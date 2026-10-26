"""Offline contract tests. All social examples below are synthetic test fixtures.

No fixture may be sent to the catalogue or represented as a collected video.
"""
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import monocrawl_collect as m


def plan(transport="mcp", budget=6):
    return {"version": 1, "free_credits": 10, "budget_credits": budget, "checked_at": m.now(),
            "auto_reload": False, "overage": False, "out_of_pocket_usd": 0,
            "transport": transport, "key_credit_limit": budget if transport == "rest" else None,
            "jobs": [{"id": "clio", "platform": "tiktok", "query": "Comment changer le filtre à air Clio", "region": "FR", "max_pages": 3},
                     {"id": "freins", "platform": "instagram", "query": "Comment changer les plaquettes de frein", "region": None, "max_pages": 3}]}


def payload(platform="tiktok", cursor=None, request_id="fixture-receipt-1", charge=None):
    url = "https://www.tiktok.com/@fixturemechanic/video/7350000000000000002" if platform == "tiktok" else "https://www.instagram.com/reel/FixtureDemo1/"
    return {"success": True, "platform": platform, "endpoint": m.ENDPOINTS[platform][0],
            "request_id": request_id, "credits_used": m.ENDPOINTS[platform][1] if charge is None else charge,
            "credits_remaining": 8, "cached": False,
            "data": {"items": [{"id": "7350000000000000002", "url": url,
                "caption": "Comment changer le filtre à air sur votre Renault Clio. #mecanique #Clio",
                "author": {"handle": "fixturemechanic", "name": "Fixture mechanic"},
                "created_at": "2026-01-01T10:00:00Z", "duration_s": 35,
                "region": "FR", "music": {"duration_s": 999, "title": "English music"}}],
                "cursor": cursor, "has_more": cursor is not None}}


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name) / "campaign"

    def tearDown(self):
        self.tmp.cleanup()

    def init(self, **kwargs):
        p = plan(**kwargs)
        m.init(self.folder, p)
        return p

    def state(self):
        return m.read(self.folder / "state.json")

    def test_preview_sends_no_request_or_environment_read(self):
        self.init(transport="rest")
        with patch.dict(m.os.environ, {}, clear=True), patch.object(m, "http_get", side_effect=AssertionError("network")):
            result = m.run(self.folder, "clio")
        self.assertEqual(result["requests_sent"], 0)
        self.assertEqual(self.state()["attempts"], [])

    def test_no_budget_beyond_observed_free(self):
        p = plan()
        p["free_credits"] = 2
        with self.assertRaises(m.CollectorError): m.init(self.folder, p)

    def test_paid_controls_refused(self):
        for key in ("auto_reload", "overage", "out_of_pocket_usd"):
            p = plan(); p[key] = 1
            with self.subTest(key=key), self.assertRaises(m.CollectorError): m.valid_plan(p)

    def test_stale_and_future_observation_refused(self):
        for delta in (timedelta(days=-2), timedelta(days=1)):
            p = plan(); p["checked_at"] = (datetime.now(timezone.utc) + delta).isoformat()
            with self.subTest(delta=delta), self.assertRaises(m.CollectorError): m.valid_plan(p)

    def test_rest_requires_dedicated_key_cap(self):
        for value in (None, 7, False):
            p = plan("rest"); p["key_credit_limit"] = value
            with self.subTest(value=value), self.assertRaises(m.CollectorError): m.valid_plan(p)

    def test_no_reset(self):
        self.init()
        with self.assertRaises(m.CollectorError): self.init()

    def test_no_arbitrary_platform_or_region(self):
        p = plan(); p["jobs"][0]["platform"] = "private"
        with self.assertRaises(m.CollectorError): m.valid_plan(p)
        p = plan(); p["jobs"][1]["region"] = "FR"
        with self.assertRaises(m.CollectorError): m.valid_plan(p)

    def test_exact_cursor_and_filters_no_invented_page(self):
        self.init()
        first = m.reserve(self.folder, "clio")
        token = "opaque=French+/cursor:1"
        m.accept(self.folder, 0, payload(cursor=token))
        second = m.reserve(self.folder, "clio")
        self.assertEqual(second["mcp"]["params"], {**first["mcp"]["params"], "cursor": token})
        self.assertNotEqual(first["mcp"]["idempotency_key"], second["mcp"]["idempotency_key"])

    def test_pending_reservation_blocks_every_job(self):
        self.init(); m.reserve(self.folder, "clio")
        with self.assertRaises(m.CollectorError): m.reserve(self.folder, "freins")

    def test_receipt_counted_once(self):
        self.init(); m.reserve(self.folder, "clio"); m.accept(self.folder, 0, payload())
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, payload())
        self.assertEqual(self.state()["spent_credits"], 2)

    def test_receipt_replay_different_job_pauses(self):
        self.init(); m.reserve(self.folder, "clio"); m.accept(self.folder, 0, payload())
        m.reserve(self.folder, "freins")
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 1, payload("instagram"))
        self.assertTrue(self.state()["paused"])

    def test_unknown_charge_retained_and_paused(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(); p["credits_used"] = None
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, p)
        self.assertEqual(self.state()["attempts"][0]["state"], "reserved")
        self.assertTrue((self.folder / "response-000000.json").is_file())
        self.assertTrue(self.state()["paused"])

    def test_charge_above_ceiling_pauses(self):
        self.init(); m.reserve(self.folder, "clio")
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, payload(charge=3))
        self.assertTrue(self.state()["paused"])

    def test_no_synthetic_live_result(self):
        for flag in ("sandbox", "synthetic", "pending_reconciliation"):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory() as temp:
                m.init(temp, plan()); m.reserve(temp, "clio")
                p = payload(); p[flag] = True
                with self.assertRaises(m.CollectorError): m.accept(temp, 0, p)
                self.assertFalse((Path(temp) / "review-000000.json").exists())

    def test_missing_or_wrong_platform_is_not_accepted(self):
        self.init(); m.reserve(self.folder, "clio")
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, payload("instagram"))

    def test_zero_credit_cache_receipt_does_not_create_budget(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(charge=0); p["credits_remaining"] = 1000; p["cached"] = True
        m.accept(self.folder, 0, p)
        self.assertEqual(self.state()["spent_credits"], 0)
        self.assertEqual(self.state()["plan"]["budget_credits"], 6)

    def test_source_caption_hashtags_and_language_scope(self):
        self.init(); m.reserve(self.folder, "clio"); m.accept(self.folder, 0, payload())
        result = m.read(self.folder / "review-000000.json")
        record = result["records"][0]["record"]
        self.assertNotIn("#", record["title"])
        self.assertNotIn("#", record["description"])
        self.assertIn("#Clio", record["social_content"]["hashtags"])
        self.assertEqual(record["social_content"]["original_caption"], payload()["data"]["items"][0]["caption"])
        self.assertEqual(record["provenance"]["adapter"], "monocrawl")
        self.assertFalse(record["audio_language_verified"])
        self.assertEqual(record["transcript_status"], "not_checked")
        self.assertEqual(record["duration_seconds"], 35)
        self.assertEqual(result["imported"], 0)

    def test_private_image_or_missing_url_held(self):
        for patching in ({"is_private": True}, {"is_photo": True}, {"url": None}, {"type": "carousel"}):
            p = payload(); p["data"]["items"][0].update(patching)
            with self.subTest(patching=patching), self.assertRaises((ValueError, TypeError)):
                m.map_item(p["data"]["items"][0], "tiktok", {"collected_at": m.now()}, 0)

    def test_repeated_cursor_stops(self):
        self.init(); m.reserve(self.folder, "clio"); m.accept(self.folder, 0, payload(cursor="same"))
        m.reserve(self.folder, "clio"); m.accept(self.folder, 1, payload(cursor="same", request_id="fixture-receipt-2"))
        self.assertTrue(self.state()["jobs"]["clio"]["finished"])

    def test_missing_cursor_is_not_constructed(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(); p["data"].pop("cursor"); p["data"]["has_more"] = True
        m.accept(self.folder, 0, p)
        self.assertTrue(self.state()["jobs"]["clio"]["finished"])

    def test_plan_mutation_detected(self):
        self.init(); state = self.state(); state["plan"]["budget_credits"] = 10
        m.atomic(self.folder / "state.json", state)
        with self.assertRaises(m.CollectorError): m.preview(self.folder, "clio")

    def test_secret_payload_not_persisted(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(); p["leak"] = "mn_testcredential000000"
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, p)
        self.assertFalse((self.folder / "response-000000.json").exists())

    def test_http_allowlist_and_no_sample_params(self):
        with self.assertRaises(m.CollectorError): m.http_get("/v1/credits/buy", {}, "mn_fixturecredential")
        with self.assertRaises(m.CollectorError): m.http_get(m.ENDPOINTS["tiktok"][0], {"query": "q", "judgments": "off", "sandbox": "true"}, "mn_fixturecredential")

    def test_mcp_cannot_accidentally_call_rest(self):
        self.init()
        with self.assertRaises(m.CollectorError): m.run(self.folder, "clio", execute=True, api_key="mn_fixturecredential")

    def test_http_failure_once_blocks_resume(self):
        self.init(transport="rest")
        calls = []
        def failing(*args): calls.append(args[:2]); raise OSError("fixture timeout")
        with self.assertRaises(m.CollectorError): m.run(self.folder, "clio", execute=True, max_pages=3, api_key="mn_fixturecredential", transport=failing)
        self.assertEqual(len(calls), 1)
        self.assertTrue(self.state()["paused"])
        self.assertEqual(self.state()["attempts"][0]["state"], "reserved")
        with self.assertRaises(m.CollectorError): m.run(self.folder, "clio", execute=True, api_key="mn_fixturecredential", transport=failing)
        self.assertEqual(len(calls), 1)

    def test_credential_absent_does_not_reserve(self):
        self.init(transport="rest")
        with patch.dict(m.os.environ, {}, clear=True), self.assertRaises(m.CollectorError):
            m.run(self.folder, "clio", execute=True)
        self.assertEqual(self.state()["attempts"], [])

    def test_three_pages_maximum(self):
        self.init()
        with self.assertRaises(m.CollectorError): m.run(self.folder, "clio", max_pages=4)

    def test_budget_exhaustion(self):
        self.init(budget=2); m.reserve(self.folder, "clio"); m.accept(self.folder, 0, payload(cursor="next"))
        with self.assertRaises(m.CollectorError): m.reserve(self.folder, "clio")

    def test_valid_rest_stops_when_source_stops(self):
        self.init(transport="rest")
        calls = []
        def transport(path, params, key):
            calls.append((path, params)); return payload()
        result = m.run(self.folder, "clio", execute=True, max_pages=3, api_key="mn_fixturecredential", transport=transport)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["receipts"][0]["candidate_count"], 1)
        self.assertEqual(self.state()["spent_credits"], 2)
        self.assertNotIn("mn_fixturecredential", (self.folder / "state.json").read_text())

    def test_partial_real_response_preserved_and_stops(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(cursor="next"); p["data"].update(partial=True, window_stop_reason="deadline", _warnings=["Fixture source window incomplete"])
        result = m.accept(self.folder, 0, p)
        self.assertTrue(result["paused"])
        self.assertEqual(m.read(self.folder / "review-000000.json")["warnings"]["data"], p["data"]["_warnings"])

    def test_redirect_refused(self):
        with self.assertRaises(m.CollectorError):
            m.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://other.example/")

    def test_network_body_never_returned_on_http_429(self):
        self.init(transport="rest")
        def blocked(*args): raise m.CollectorError("HTTP 429")
        with self.assertRaises(m.CollectorError):
            m.run(self.folder, "clio", execute=True, api_key="mn_fixturecredential", transport=blocked)
        self.assertTrue(self.state()["paused"])
        self.assertFalse(list(self.folder.glob("response-*.json")))

    def test_nested_pending_receipt_stays_reserved_without_candidates(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(cursor="next"); p["data"].update(window_stop_reason="receipt_pending", partial=True)
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, p)
        self.assertEqual(self.state()["attempts"][0]["state"], "reserved")
        self.assertEqual(self.state()["spent_credits"], 0)
        self.assertFalse((self.folder / "review-000000.json").exists())

    def test_empty_page_stops_without_constructing_next_call(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(cursor="next", charge=0); p["data"]["items"] = []
        result = m.accept(self.folder, 0, p)
        self.assertEqual(result["candidate_count"], 0)
        self.assertTrue(self.state()["jobs"]["clio"]["finished"])
        with self.assertRaises(m.CollectorError): m.reserve(self.folder, "clio")

    def test_remaining_one_credit_blocks_two_credit_request(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(cursor="next"); p["credits_remaining"] = 1
        m.accept(self.folder, 0, p)
        with self.assertRaises(m.CollectorError): m.reserve(self.folder, "clio")
        self.assertEqual(m.reserve(self.folder, "freins")["mcp"]["max_credits"], 1)

    def test_observed_key_cap_also_bounds_local_reservations(self):
        p = plan("rest"); p["key_credit_limit"] = 1
        m.init(self.folder, p)
        with self.assertRaises(m.CollectorError): m.reserve(self.folder, "clio")

    def test_malformed_partial_is_not_silently_ignored(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(cursor="next"); p["data"]["partial"] = "true"
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, p)
        self.assertFalse((self.folder / "review-000000.json").exists())

    def test_nested_privacy_or_explicit_nonvideo_refused(self):
        for changes in ({"author": {"handle": "fixturemechanic", "is_private": True}}, {"is_video": False}):
            p = payload(); p["data"]["items"][0].update(changes)
            with self.subTest(changes=changes), self.assertRaises(m.CollectorError):
                m.map_item(p["data"]["items"][0], "tiktok", {"collected_at": m.now()}, 0)

    def test_native_title_and_native_numeric_hashtag_preserved(self):
        p = payload()
        item = p["data"]["items"][0]
        item.update(title="Changer les plaquettes #freins", caption="Explication du freinage. #5008 #mecanique", hashtags=["#5008", "#freins"])
        record, _ = m.map_item(item, "tiktok", {"collected_at": m.now()}, 0)
        self.assertEqual(record["title"], "Changer les plaquettes")
        self.assertEqual(record["description"], "Explication du freinage.")
        self.assertIn("#5008", record["social_content"]["hashtags"])
        self.assertEqual(record["social_content"]["original_title"], item["title"])
        self.assertEqual(record["social_content"]["original_caption"], item["caption"])

    def test_failed_zero_charge_envelope_does_not_become_empty_success(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(charge=0); p.update(success=False, error={"type": "RATE_LIMITED", "status": 429})
        p["data"]["items"] = []
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, p)
        self.assertEqual(self.state()["attempts"][0]["state"], "reserved")
        self.assertTrue(self.state()["paused"])
        self.assertFalse((self.folder / "review-000000.json").exists())

    def test_unsettled_receipt_no_data_is_preserved_for_reconciliation(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(); p.update(credits_used=None, pending_reconciliation=True); p.pop("data")
        with self.assertRaises(m.CollectorError): m.accept(self.folder, 0, p)
        self.assertTrue((self.folder / "response-000000.json").exists())
        self.assertEqual(self.state()["attempts"][0]["state"], "reserved")
        with self.assertRaises(m.CollectorError): m.reserve(self.folder, "freins")

    def test_partial_known_charge_keeps_caption_but_no_automatic_continuation(self):
        self.init(); m.reserve(self.folder, "clio")
        p = payload(cursor="next"); p["data"]["partial"] = True
        m.accept(self.folder, 0, p)
        self.assertEqual(self.state()["attempts"][0]["state"], "complete")
        self.assertEqual(self.state()["spent_credits"], 2)
        self.assertTrue(self.state()["paused"])
        with self.assertRaises(m.CollectorError): m.reserve(self.folder, "clio")


if __name__ == "__main__":
    unittest.main()
