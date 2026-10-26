"""Offline contract tests; fixtures are synthetic and never exported to the app."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import vehicle_reference as vr


def fixture():
    return {"Count": 2, "Message": "Results returned successfully", "SearchCriteria": "Make:Example; ModelYear:2024",
            "Results": [{"Make_ID": 100, "Make_Name": "EXAMPLE", "Model_ID": 200, "Model_Name": "Example A"},
                        {"Make_ID": 101, "Make_Name": "EXAMPLE MOTORS", "Model_ID": 201, "Model_Name": "Example B"}]}


def raw(value=None):
    return json.dumps(fixture() if value is None else value).encode()


class FakeResponse:
    def __init__(self, body=None, status=200, headers=None):
        self.body = raw() if body is None else body
        self.status = status
        self.headers = {"Content-Type": "application/json; charset=utf-8", **(headers or {})}
        self.reads = []

    def getheader(self, name):
        return self.headers.get(name)

    def read(self, size):
        self.reads.append(size)
        return self.body[:size]


class FakeConnection:
    def __init__(self, response):
        self.response, self.requests, self.closed = response, [], False

    def request(self, *args, **kwargs):
        self.requests.append((args, kwargs))

    def getresponse(self):
        return self.response

    def close(self):
        self.closed = True


class VehicleReferenceTests(unittest.TestCase):
    def setUp(self):
        self.plan = vr.make_plan("Example", 2024)

    def test_unicode_make_and_endpoint_encoding(self):
        plan = vr.make_plan("  Citroën   Automobiles ", 2024)
        self.assertEqual(plan["make"], "Citroën Automobiles")
        self.assertIn("Citro%C3%ABn%20Automobiles/modelyear/2024?format=json", plan["url"])
        self.assertEqual(plan["max_requests"], 1)

    def test_rejects_wildcard_path_controls_and_invalid_year(self):
        for make in ("*", "a", "12", "Honda/../../", "Honda?x=1", "Renault\n", "x" * 81, None, "Honda%"):
            with self.subTest(make=make), self.assertRaises(vr.ReferenceError):
                vr.make_plan(make, 2024)
        for year in (1995, 2028, True, "2024", 2024.5):
            with self.subTest(year=year), self.assertRaises(vr.ReferenceError):
                vr.make_plan("Honda", year, current_year=2026)
        self.assertEqual(vr.make_plan("Honda", 1996, current_year=2026)["model_year"], 1996)
        self.assertEqual(vr.make_plan("Honda", 2027, current_year=2026)["model_year"], 2027)

    def test_preserves_source_ids_names_and_partial_matches(self):
        result = vr.parse_response(raw(), self.plan)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["models"][0], {"make_id": 100, "model_id": 200, "make_name": "EXAMPLE",
                         "model_name": "Example A", "requested_model_year": 2024, "exact_make_name_match": True})
        self.assertFalse(result["models"][1]["exact_make_name_match"])
        self.assertEqual(result["models"][1]["make_id"], 101)

    def test_rejects_false_counts_invalid_shape_and_api_errors(self):
        samples = [[], {"Results": []}, {**fixture(), "Count": 3}, {**fixture(), "Count": True},
                   {**fixture(), "Count": "2"}, {**fixture(), "Message": None},
                   {**fixture(), "ErrorCode": "1"}, {**fixture(), "ErrorMessage": "failure"}]
        for sample in samples:
            with self.subTest(sample=sample), self.assertRaises(vr.ReferenceError):
                vr.parse_response(raw(sample), self.plan)
        for data in (b"<html>error</html>", b"\xff", b"x" * (vr.MAX_BYTES + 1)):
            with self.assertRaises(vr.ReferenceError):
                vr.parse_response(data, self.plan)

    def test_rejects_invalid_model_fields_and_duplicate_identity(self):
        for field, value in (("Make_ID", True), ("Model_ID", "200"), ("Model_ID", -1),
                             ("Make_Name", ""), ("Model_Name", "broken\nname"), ("Model_Name", None)):
            sample = fixture()
            sample["Results"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(vr.ReferenceError):
                vr.parse_response(raw(sample), self.plan)
        sample = fixture()
        sample["Results"][1] = deepcopy(sample["Results"][0])
        with self.assertRaises(vr.ReferenceError):
            vr.parse_response(raw(sample), self.plan)

    def test_valid_empty_response_does_not_invent_models(self):
        result = vr.parse_response(raw({"Count": 0, "Message": "No results found", "SearchCriteria": "Make:Example", "Results": []}), self.plan)
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["models"], [])

    def test_http_has_one_request_and_no_secret_or_redirect_headers(self):
        response = FakeResponse()
        connection = FakeConnection(response)
        construction = []
        def factory(*args, **kwargs):
            construction.append((args, kwargs))
            return connection
        self.assertEqual(vr.fetch_one(self.plan, timeout=12, connection_factory=factory), raw())
        self.assertEqual(len(connection.requests), 1)
        self.assertEqual(construction[0][0], (vr.HOST,))
        self.assertEqual(construction[0][1]["timeout"], 12)
        args, kwargs = connection.requests[0]
        self.assertEqual(args[0], "GET")
        self.assertEqual(set(kwargs["headers"]), {"Accept", "Accept-Encoding", "User-Agent"})
        self.assertEqual(response.reads, [vr.MAX_BYTES + 1])
        self.assertTrue(connection.closed)

    def test_redirect_errors_and_oversize_are_stopped_without_retry(self):
        for status, headers, body in ((302, {"Location": "https://elsewhere.invalid"}, b""),
                                      (429, {}, b""), (200, {"Content-Type": "text/html"}, b""),
                                      (200, {"Content-Length": str(vr.MAX_BYTES + 1)}, b""),
                                      (200, {"Content-Encoding": "gzip"}, b""),
                                      (200, {"Content-Length": "100"}, b"{}"),
                                      (200, {}, b"x" * (vr.MAX_BYTES + 1))):
            connection = FakeConnection(FakeResponse(body, status, headers))
            with self.subTest(status=status, headers=headers), self.assertRaises(vr.ReferenceError):
                vr.fetch_one(self.plan, connection_factory=lambda *a, **k: connection)
            self.assertEqual(len(connection.requests), 1)
            self.assertTrue(connection.closed)

    def test_fixed_endpoint_cannot_be_replaced_and_timeout_is_bounded(self):
        with self.assertRaises(vr.ReferenceError):
            vr.fetch_one({**self.plan, "url": "https://example.invalid"})
        for timeout in (0, 61, float("nan"), True):
            with self.subTest(timeout=timeout), self.assertRaises(vr.ReferenceError):
                vr.fetch_one(self.plan, timeout=timeout)

    def test_preview_does_not_request_or_write(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "untouched"
            with patch.object(vr, "execute", side_effect=AssertionError("Must not execute")), redirect_stdout(io.StringIO()) as buffer:
                code = vr.main(["--make", "Honda", "--year", "2024", "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(buffer.getvalue())["requests"], 0)
            self.assertFalse(output.exists())

    def test_cache_keeps_raw_source_sha_date_scope_and_reuses_without_request(self):
        calls = []
        def fetcher(plan, **kwargs):
            calls.append(plan)
            return raw()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            first = vr.execute(self.plan, output, fetcher=fetcher)
            report = first["report"]
            self.assertEqual((output / "response.json").read_bytes(), raw())
            self.assertEqual(report["source"]["sha256"], vr.sha(raw()))
            self.assertEqual(report["source"]["url"], self.plan["url"])
            self.assertTrue(report["source"]["retrieved_at"].endswith("+00:00"))
            self.assertEqual(report["scope"]["jurisdiction"], "US")
            self.assertFalse(report["scope"]["proves_vehicle_compatibility"])
            self.assertFalse(report["scope"]["contains_service_procedures"])
            self.assertFalse(report["scope"]["contains_engine_oil_or_fuel_specifications"])
            second = vr.execute(self.plan, output, fetcher=fetcher)
            self.assertEqual(second["mode"], "cache")
            self.assertEqual(second["requests"], 0)
            self.assertEqual(len(calls), 1)

    def test_mismatched_request_never_overwrites_completed_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            vr.execute(self.plan, output, fetcher=lambda *a, **k: raw())
            before = {p.name: p.read_bytes() for p in output.iterdir()}
            with self.assertRaises(vr.ReferenceError):
                vr.execute(vr.make_plan("Other", 2024), output, fetcher=lambda *a, **k: self.fail("Unexpected request"))
            self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})

    def test_corrupt_or_partial_cache_never_fetches(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "response.json").write_bytes(b"partial")
            with self.assertRaises(vr.ReferenceError):
                vr.execute(self.plan, output, fetcher=lambda *a, **k: self.fail("Unexpected request"))
        for field, value in (("url", "https://example.invalid"), ("retrieved_at", "2026-10-26")):
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                report = vr.execute(self.plan, output, fetcher=lambda *a, **k: raw())["report"]
                report["source"][field] = value
                (output / "reference.json").write_bytes(vr.json_bytes(report))
                with self.subTest(field=field), self.assertRaises(vr.ReferenceError):
                    vr.execute(self.plan, output, fetcher=lambda *a, **k: self.fail("Unexpected request"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            vr.execute(self.plan, output, fetcher=lambda *a, **k: raw())
            (output / "response.json").write_bytes(b"changed")
            with self.assertRaises(vr.ReferenceError):
                vr.execute(self.plan, output, fetcher=lambda *a, **k: self.fail("Unexpected request"))

    def test_failed_response_leaves_no_completion_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with self.assertRaises(vr.ReferenceError):
                vr.execute(self.plan, output, fetcher=lambda *a, **k: b"not json")
            self.assertEqual(list(output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
