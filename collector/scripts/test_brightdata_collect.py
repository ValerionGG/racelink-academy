from copy import deepcopy
from datetime import timedelta
import hashlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import brightdata_collect as client

KEY = "offline-testing-key-never-real"
IG = "gd_lyclm20il4r5helnj"
TT = "gd_lu702nij2f790tmv9h"


def plan(name="ig-batch-1", limit=50, handles=("mechanic",)):
    return {"id": name, "dataset_id": IG, "limit_per_input": limit,
            "inputs": [{"url": "https://www.instagram.com/" + handle + "/", "num_of_posts": limit} for handle in handles]}


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.folder = self.root / "campaign"
        self.ledger = self.root / "ui-ledger.json"
        self.observation = {"version": 1, "provider": "brightdata", "checked_at": client.stamp(),
                            "free_credits_observed": 5000, "payment_methods": 0, "out_of_pocket_usd": 0,
                            "campaign_cap": 4000, "safety_margin": 1000, "batches": []}
        self.write_observation()
        client.init(self.folder, self.ledger)
        self.env = patch.dict("os.environ", {"BRIGHTDATA_API_KEY": KEY})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        # Windows occasionally reports a transient nonempty directory immediately
        # after closing flushed files. Only retry cleanup of this exact owned temp.
        for attempt in range(5):
            try:
                self.temp.cleanup()
                break
            except OSError as error:
                if getattr(error, "winerror", None) not in (5, 32, 145) or attempt == 4:
                    raise
                time.sleep(0.05)

    def write_observation(self):
        self.ledger.write_bytes(client.encoded(self.observation))

    def state(self):
        return client.load(self.folder)

    def submit(self, item=None, snap="sd_offlinetest01"):
        item = item or plan()
        return client.trigger(self.folder, item, execute=True, transport=lambda *args: {"snapshot_id": snap})

    def add_ui(self, snap="sd_uiexample01"):
        item = plan("ig-pilot-01", 50, ("francoisgbrnr", "maclede12"))
        self.observation["batches"].append({**item, "reserved_credits": 100, "snapshot_id": snap, "status": "reserved_before_ui_submit"})
        self.write_observation()

    def test_preview_no_request_or_reservation(self):
        with patch.dict("os.environ", {}, clear=True):
            result = client.trigger(self.folder, plan(), transport=lambda *args: self.fail("Network called"))
        self.assertEqual(result["requests_sent"], 0)
        self.assertEqual(result["reserved_for_batch"], 50)
        self.assertEqual(self.state()["jobs"], {})

    def test_exact_validated_instagram_contract(self):
        result = client.trigger(self.folder, plan(limit=50, handles=("francoisgbrnr", "maclede12")))
        request = result["request"]
        self.assertEqual(request["params"], {"dataset_id": IG, "notify": "false", "include_errors": "true", "type": "discover_new", "discover_by": "url", "limit_per_input": 50})
        self.assertEqual(request["body"]["limit_per_input"], 50)
        self.assertEqual(request["body"]["input"][0], {"url": "https://www.instagram.com/francoisgbrnr/", "num_of_posts": 50, "country_code": "", "start_date": "", "end_date": ""})

    def test_tiktok_only_profile_contract(self):
        item = {"id": "tt-1", "dataset_id": TT, "limit_per_input": 10, "inputs": [{"url": "https://www.tiktok.com/@maclede12", "num_of_posts": 10, "country": "FR"}]}
        result = client.trigger(self.folder, item)
        self.assertEqual(result["request"]["params"]["discover_by"], "profile_url")
        self.assertNotIn("language", result["request"]["body"]["input"][0])

    def test_tiktok_fast_contract_has_no_discovery_query(self):
        item = {"id": "tt-fast-1", "dataset_id": "gd_m7n5v2gq296pex2f5m", "limit_per_input": 25,
                "inputs": [{"url": "https://www.tiktok.com/@francoisgbrnr/", "num_of_posts": 25},
                           {"url": "https://www.tiktok.com/@klavkarr/", "num_of_posts": 25}]}
        result = client.trigger(self.folder, item)
        self.assertEqual(result["request"]["params"], {"dataset_id": "gd_m7n5v2gq296pex2f5m", "notify": "false", "include_errors": "true"})
        self.assertEqual(result["request"]["body"]["limit_per_input"], 25)
        self.assertEqual(result["reserved_for_batch"], 50)
        self.assertNotIn("country", result["request"]["body"]["input"][0])
        self.assertNotIn("type", result["request"]["params"])
        self.assertNotIn("limit_per_input", result["request"]["params"])

    def test_documented_inactive_account_rejection_still_reserves_credits(self):
        self.add_ui(None)
        self.observation["batches"][0]["status"] = "rejected_customer_inactive"
        self.write_observation()
        result = client.trigger(self.folder, plan())
        self.assertEqual(result["already_reserved"], 100)

    def test_reservation_flushed_before_single_post(self):
        calls = []
        def transport(*args):
            state = self.state()
            self.assertEqual(state["jobs"]["ig-batch-1"]["status"], "reserved")
            self.assertEqual(state["jobs"]["ig-batch-1"]["reserved_credits"], 50)
            calls.append(args)
            return {"snapshot_id": "sd_offlinetest01"}
        client.trigger(self.folder, plan(), execute=True, transport=transport)
        result = client.trigger(self.folder, plan(), execute=True, transport=transport)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["requests_sent"], 0)

    def test_missing_key_no_reservation(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(client.ClientError):
            client.trigger(self.folder, plan(), execute=True)
        self.assertEqual(self.state()["jobs"], {})

    def test_post_error_retains_reservation_and_never_retries(self):
        def fail(*args):
            raise TimeoutError("remote secret")
        with self.assertRaisesRegex(client.ClientError, "POST outcome uncertain") as error:
            client.trigger(self.folder, plan(), execute=True, transport=fail)
        self.assertNotIn("remote secret", str(error.exception))
        self.assertEqual(self.state()["jobs"]["ig-batch-1"]["reserved_credits"], 50)
        result = client.trigger(self.folder, plan(), execute=True, transport=lambda *args: self.fail("POST replayed"))
        self.assertEqual(result["status"], "uncertain")
        with self.assertRaisesRegex(client.ClientError, "prior POST"):
            client.trigger(self.folder, plan("other", handles=("othermechanic",)), execute=True)

    def test_invalid_snapshot_is_uncertain(self):
        with self.assertRaises(client.ClientError):
            client.trigger(self.folder, plan(), execute=True, transport=lambda *args: {"snapshot_id": "https://unexpected.test"})
        self.assertEqual(self.state()["jobs"]["ig-batch-1"]["status"], "uncertain")

    def test_secret_response_is_not_persisted(self):
        with self.assertRaises(client.ClientError):
            client.trigger(self.folder, plan(), execute=True, transport=lambda *args: {"snapshot_id": "sd_offlinetest01", "secret": KEY})
        self.assertNotIn(KEY, (self.folder / "state.json").read_text())

    def test_ui_pending_blocks_new_post(self):
        self.add_ui(None)
        with self.assertRaisesRegex(client.ClientError, "lacks its snapshot"):
            client.trigger(self.folder, plan())

    def test_ui_reservations_count_and_adopt_is_not_double_billed(self):
        self.add_ui()
        client.adopt_ui(self.folder, "ig-pilot-01")
        result = client.trigger(self.folder, plan())
        self.assertEqual(result["already_reserved"], 100)
        self.assertEqual(client.adopt_ui(self.folder, "ig-pilot-01")["requests_sent"], 0)

    def test_external_reservation_cannot_disappear(self):
        self.add_ui()
        client.adopt_ui(self.folder, "ig-pilot-01")
        self.observation["batches"] = []
        self.write_observation()
        with self.assertRaisesRegex(client.ClientError, "removed or altered"):
            client.trigger(self.folder, plan())

    def test_4000_cap_includes_existing_ui_batch(self):
        self.add_ui()
        with self.assertRaisesRegex(client.ClientError, "free-credit cap"):
            client.trigger(self.folder, plan(limit=1000, handles=("a", "b", "c", "d")))

    def test_free_credits_are_not_dollar_balance(self):
        self.observation["free_credits_observed"] = 1020
        self.observation["balance"] = 100000
        self.write_observation()
        with self.assertRaisesRegex(client.ClientError, "free-credit cap"):
            client.trigger(self.folder, plan(limit=50))

    def test_expired_future_card_and_recharge_observation_refused(self):
        original = deepcopy(self.observation)
        values = [{"checked_at": (client.now() - timedelta(hours=25)).isoformat()},
                  {"checked_at": (client.now() + timedelta(hours=1)).isoformat()},
                  {"payment_methods": 1}, {"auto_recharge": True}]
        for fields in values:
            self.observation = {**original, **fields}
            self.write_observation()
            with self.assertRaises(client.ClientError):
                client.trigger(self.folder, plan())

    def test_invalid_profiles_and_unbounded_options_refused(self):
        for url in ("https://evil.test/mecanique", "http://www.instagram.com/mecanique/", "https://www.instagram.com/p/ABC/", "https://www.instagram.com/mecanique/?token=x", "https://name:secret@www.instagram.com/mecanique/"):
            item = plan(); item["inputs"][0]["url"] = url
            with self.assertRaises(client.ClientError):
                client.validate_plan(item)
        for values in ({"num_of_posts": 51}, {"all_reels": True}, {"country_code": "French"}, {"start_date": "yesterday"}):
            item = plan(); item["inputs"][0].update(values)
            with self.assertRaises(client.ClientError):
                client.validate_plan(item)

    def test_same_profiles_reordered_or_renamed_do_not_repeat(self):
        self.submit(plan(handles=("garage1", "garage2")))
        with self.assertRaisesRegex(client.ClientError, "Identical profile batch"):
            client.trigger(self.folder, plan("another-id", handles=("GARAGE2", "garage1")))

    def test_job_cannot_change_inputs(self):
        self.submit()
        with self.assertRaisesRegex(client.ClientError, "binds different"):
            client.trigger(self.folder, plan(handles=("other",)))

    def test_collect_preview_is_read_only(self):
        self.submit()
        before = (self.folder / "state.json").read_bytes()
        result = client.collect(self.folder, "ig-batch-1")
        self.assertEqual(result["requests_sent"], 0)
        self.assertEqual(before, (self.folder / "state.json").read_bytes())

    def test_progress_running_one_get_no_download(self):
        self.submit()
        calls = []
        def transport(*args):
            calls.append(args)
            return {"status": "running", "snapshot_id": "sd_offlinetest01"}
        result = client.collect(self.folder, "ig-batch-1", execute=True, transport=transport)
        self.assertEqual(result["status"], "running")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "GET")

    def test_collect_projection_and_repeat_without_network(self):
        self.submit()
        rows = [{"url": "https://www.instagram.com/reel/ABCDE12/", "shortcode": "ABCDE12", "description": "Changer une roue", "product_type": "clips", "user_posted": "garage", "video_url": "https://cdn.test/download?token=private", "top_comments": [{"email": "private@example.test"}], "tt_chain_token": "sensitive"}]
        replies = iter([{"status": "ready"}, rows])
        result = client.collect(self.folder, "ig-batch-1", execute=True, transport=lambda *args: next(replies))
        output = json.loads(Path(result["file"]).read_text())
        self.assertNotIn("video_url", output[0])
        self.assertNotIn("top_comments", output[0])
        self.assertNotIn("tt_chain_token", output[0])
        self.assertEqual(client.collect(self.folder, "ig-batch-1", execute=True, transport=lambda *args: self.fail("GET replayed"))["requests_sent"], 0)
        Path(result["file"]).write_text("[]")
        with self.assertRaisesRegex(client.ClientError, "missing or changed"):
            client.collect(self.folder, "ig-batch-1")

    def test_download_failure_allows_safe_get_resume_only(self):
        self.submit()
        replies = iter([{"status": "ready"}, {"message": "remote private error"}])
        with self.assertRaises(client.ClientError):
            client.collect(self.folder, "ig-batch-1", execute=True, transport=lambda *args: next(replies))
        self.assertEqual(self.state()["jobs"]["ig-batch-1"]["status"], "ready")
        self.assertNotIn("remote private error", (self.folder / "state.json").read_text())
        replies = iter([{"status": "ready"}, []])
        result = client.collect(self.folder, "ig-batch-1", execute=True, transport=lambda *args: next(replies))
        self.assertEqual(result["status"], "complete")

    def test_over_cap_download_blocks_new_posts(self):
        self.submit(plan(limit=1))
        replies = iter([{"status": "ready"}, [{"url": "a"}, {"url": "b"}]])
        with self.assertRaises(client.ClientError):
            client.collect(self.folder, "ig-batch-1", execute=True, transport=lambda *args: next(replies))
        self.assertEqual(self.state()["jobs"]["ig-batch-1"]["status"], "over_cap")
        with self.assertRaisesRegex(client.ClientError, "exceeded its cap"):
            client.trigger(self.folder, plan("new", handles=("someone",)))

    def test_failed_job_retains_reservation(self):
        self.submit()
        result = client.collect(self.folder, "ig-batch-1", execute=True, transport=lambda *args: {"status": "failed", "error": "private remote message"})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(self.state()["jobs"]["ig-batch-1"]["reserved_credits"], 50)

    def test_snapshot_reconciliation_requires_evidence_and_preserves_credit(self):
        with self.assertRaises(client.ClientError):
            client.trigger(self.folder, plan(), execute=True, transport=lambda *args: {})
        proof = self.root / "ui-proof.json"
        proof.write_text('{"snapshot":"sd_reconciled01"}')
        result = client.reconcile(self.folder, "ig-batch-1", "sd_reconciled01", proof)
        self.assertFalse(result["reservation_released"])
        self.assertEqual(self.state()["jobs"]["ig-batch-1"]["reserved_credits"], 50)

    def test_os_lock_prevents_concurrent_operation(self):
        with client.locked(self.folder):
            with self.assertRaisesRegex(client.ClientError, "busy"):
                client.trigger(self.folder, plan())

    def test_reservation_write_failure_sends_no_request(self):
        with patch.object(client, "atomic", side_effect=OSError("disk full")), self.assertRaises(OSError):
            client.trigger(self.folder, plan(), execute=True, transport=lambda *args: self.fail("POST before durable reserve"))
        self.assertEqual(self.state()["jobs"], {})

    def test_post_result_write_failure_never_replays_post(self):
        original = client.atomic
        writes = []
        def atomic(path, value):
            writes.append(path)
            if len(writes) == 2:
                raise OSError("simulated crash after response")
            return original(path, value)
        with patch.object(client, "atomic", side_effect=atomic), self.assertRaises(OSError):
            self.submit()
        self.assertEqual(self.state()["jobs"]["ig-batch-1"]["status"], "reserved")
        result = client.trigger(self.folder, plan(), execute=True, transport=lambda *args: self.fail("POST replayed after crash"))
        self.assertEqual(result["requests_sent"], 0)

    def test_tampered_saved_reservation_refused(self):
        self.submit()
        state = self.state(); state["jobs"]["ig-batch-1"]["reserved_credits"] = 0
        client.atomic(self.folder / "state.json", state)
        with self.assertRaisesRegex(client.ClientError, "saved reservation"):
            client.trigger(self.folder, plan("new", handles=("someone",)))

    def test_redirect_and_unknown_endpoints_refused(self):
        with self.assertRaisesRegex(client.TransportError, "Redirect refused"):
            client.NoRedirect().redirect_request(None, None, 302, "", {}, "https://another.test")
        with self.assertRaisesRegex(client.ClientError, "POST endpoint refused"):
            client.http("POST", "/zone", {}, {}, KEY)
        with self.assertRaisesRegex(client.ClientError, "GET endpoint refused"):
            client.http("GET", "/customer/balance", {}, None, KEY)

    def test_http_transport_pins_host_headers_and_json(self):
        class Response(io.BytesIO):
            status = 200
            def geturl(self):
                return client.API + "/datasets/v3/progress/sd_offlinetest01"
        class Opener:
            request = None
            def open(self, request, **kwargs):
                self.request = request
                return Response(b'{"status":"ready"}')
        opener = Opener()
        with patch.object(client.urllib.request, "build_opener", return_value=opener):
            result = client.http("GET", "/datasets/v3/progress/sd_offlinetest01", {}, None, KEY)
        self.assertEqual(result, {"status": "ready"})
        self.assertEqual(opener.request.get_header("Authorization"), "Bearer " + KEY)
        self.assertEqual(opener.request.full_url, client.API + "/datasets/v3/progress/sd_offlinetest01")

    def test_http_oversized_response_and_key_echo_refused(self):
        class Response(io.BytesIO):
            status = 200
            def geturl(self):
                return client.API + "/datasets/v3/progress/sd_offlinetest01"
        class Opener:
            def __init__(self, body):
                self.body = body
            def open(self, *args, **kwargs):
                return Response(self.body)
        for data, cap in [(b"x" * 130, 128), (client.encoded({"key": KEY}), 2048)]:
            with patch.object(client.urllib.request, "build_opener", return_value=Opener(data)), patch.object(client, "MAX_BYTES", cap):
                with self.assertRaisesRegex(client.TransportError, "too large or contains API credential"):
                    client.http("GET", "/datasets/v3/progress/sd_offlinetest01", {}, None, KEY)

    def test_http_transport_does_not_retry_or_log_remote_error(self):
        class Opener:
            calls = 0
            def open(self, *args, **kwargs):
                self.calls += 1
                raise client.urllib.error.HTTPError(client.API + "/datasets/v3/trigger", 429, "private message", {}, io.BytesIO(b"secret remote body"))
        opener = Opener()
        with patch.object(client.urllib.request, "build_opener", return_value=opener):
            with self.assertRaisesRegex(client.TransportError, "HTTP 429") as error:
                client.http("POST", "/datasets/v3/trigger", {}, {"input": []}, KEY)
        self.assertEqual(opener.calls, 1)
        self.assertNotIn("private", str(error.exception))
        self.assertNotIn("secret", str(error.exception))


if __name__ == "__main__":
    unittest.main()
