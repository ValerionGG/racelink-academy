"""Fake transport only. No real provider/account/API credentials are used."""
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock

import profile_campaign as engine
import scrapecreators_collect as client
from test_profile_campaign import APP, tiktok, page


class FakeTransport:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def __call__(self, endpoint, params, api_key):
        self.calls.append((endpoint, dict(params)))
        reply = next(self.replies)
        if isinstance(reply, Exception):
            raise reply
        return reply


def balance(remaining):
    return {"success": True, "creditCount": remaining, "credits_remaining": remaining, "credits_charged": 1}


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.campaign = self.root / "campaign"
        engine.init(self.campaign, {"version": 1, "free_credits": 4, "checked_at": engine.now(),
                    "auto_recharge": False, "out_of_pocket_usd": 0,
                    "profiles": [{"platform": "tiktok", "handle": "fixture", "max_pages": 4, "region": "FR"}]}, APP)
        self.key = "SYNTHETIC-API-KEY-FOR-TESTS"

    def tearDown(self):
        for attempt in range(5):
            try:
                self.temp.cleanup()
                break
            except OSError as exc:
                if getattr(exc, "winerror", None) not in {32, 145} or attempt == 4:
                    raise
                time.sleep(.05 * 2 ** attempt)

    def call(self, transport, **options):
        with patch.object(client.time, "sleep"):
            return client.run(self.campaign, "tiktok:fixture", transport=transport,
                              api_key=self.key, **options)

    def test_default_preview_never_reads_key_or_calls_network_or_reserves(self):
        fake = FakeTransport([])
        before = engine.file_hash(self.campaign / "state.json")
        with patch.dict(os.environ, {}, clear=True):
            result = client.run(self.campaign, "tiktok:fixture", transport=fake)
        self.assertEqual(result["mode"], "preview")
        self.assertEqual(fake.calls, [])
        self.assertEqual(engine.file_hash(self.campaign / "state.json"), before)

    def test_missing_key_stops_before_any_request(self):
        fake = FakeTransport([])
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(client.ClientError):
            client.run(self.campaign, "tiktok:fixture", execute=True, transport=fake)
        self.assertEqual(fake.calls, [])

    def test_two_pages_reserve_balance_plus_page_each_time(self):
        fake = FakeTransport([balance(3), page([tiktok()], more=True, next_cursor="123", remaining=2),
                              balance(1), page([tiktok(2)], remaining=0)])
        result = self.call(fake, execute=True, max_pages=2)
        self.assertEqual(result["page_responses_ingested"], 2)
        self.assertEqual(result["requests_sent"], 4)
        self.assertEqual(result["final_state"]["reserved_credits"], 4)
        self.assertEqual([item[0] for item in fake.calls], [client.BALANCE_PATH, "/v3/tiktok/profile/videos"] * 2)
        self.assertEqual(fake.calls[3][1]["max_cursor"], "123")
        self.assertEqual(result["publication_count"], 0)

    def test_credit_cap_stops_before_third_page_or_balance(self):
        fake = FakeTransport([balance(1000), page([tiktok()], more=True, next_cursor="1", remaining=999),
                              balance(998), page([tiktok(2)], more=True, next_cursor="2", remaining=997)])
        result = self.call(fake, execute=True, max_pages=10)
        self.assertEqual(len(fake.calls), 4)
        self.assertEqual(result["stop_reason"], "verified_free_credit_cap")
        self.assertEqual(result["final_state"]["free_credit_cap"], 4)  # Total/paid balance never expands free allowance.

    def test_zero_balance_stops_before_page(self):
        fake = FakeTransport([balance(0)])
        result = self.call(fake, execute=True)
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(result["page_responses_ingested"], 0)
        self.assertEqual(result["final_state"]["reserved_credits"], 1)

    def test_balance_timeout_has_no_auto_retry_and_blocks_next_invocation(self):
        fake = FakeTransport([client.TransportError("Uncertain request outcome")])
        with self.assertRaises(client.TransportError):
            self.call(fake, execute=True)
        state = engine.load_state(self.campaign)
        self.assertEqual(state["credit_checks"][0]["state"], "reserved")
        self.assertEqual(state["reserved_credits"], 1)
        self.assertEqual(len(fake.calls), 1)
        again = FakeTransport([])
        with self.assertRaises(client.ClientError):
            self.call(again, execute=True)
        self.assertEqual(again.calls, [])

    def test_page_timeout_retains_both_reservations_and_does_not_retry(self):
        fake = FakeTransport([balance(3), client.TransportError("Uncertain page outcome")])
        with self.assertRaises(client.TransportError):
            self.call(fake, execute=True)
        state = engine.load_state(self.campaign)
        self.assertEqual(state["reserved_credits"], 2)
        self.assertEqual(state["attempts"][0]["state"], "reserved")
        self.assertEqual(len(fake.calls), 2)
        self.assertFalse((self.campaign / "private-raw").exists())

    def test_nonstandard_balance_or_unexpected_charge_blocks_page(self):
        for reply in ({"credits_remaining": 100}, {"creditCount": 100, "credits_charged": 2}):
            with self.subTest(reply=reply):
                folder = self.root / str(len(list(self.root.iterdir())))
                plan = {"version": 1, "free_credits": 2, "checked_at": engine.now(), "auto_recharge": False,
                        "out_of_pocket_usd": 0, "profiles": [{"platform": "tiktok", "handle": "fixture", "max_pages": 1, "region": "FR"}]}
                engine.init(folder, plan, APP)
                fake = FakeTransport([reply])
                with self.assertRaises((client.ClientError, engine.CampaignError)):
                    client.run(folder, "tiktok:fixture", execute=True, transport=fake, api_key=self.key)
                self.assertEqual(len(fake.calls), 1)

    def test_credential_echo_is_never_written(self):
        fake = FakeTransport([balance(3), page([tiktok(desc=self.key)], remaining=2)])
        with self.assertRaises(client.ClientError):
            self.call(fake, execute=True)
        self.assertFalse((self.campaign / "private-raw").exists())
        self.assertNotIn(self.key, (self.campaign / "state.json").read_text())

    def test_error_response_is_not_written_even_if_success_true(self):
        fake = FakeTransport([balance(3), {"success": True, "credits_charged": 0, "credits_remaining": 3,
                                          "error": "forbidden", "message": "Profile is age restricted"}])
        with self.assertRaises(engine.CampaignError):
            self.call(fake, execute=True)
        self.assertFalse((self.campaign / "private-raw").exists())

    def test_error_without_message_is_not_accepted_as_a_successful_page(self):
        fake = FakeTransport([balance(3), page([tiktok()], error="forbidden")])
        with self.assertRaises(engine.CampaignError):
            self.call(fake, execute=True)
        self.assertFalse((self.campaign / "private-raw").exists())

    def test_slow_trickle_body_stops_at_monotonic_deadline(self):
        response = MagicMock()
        response.status = 200
        response.geturl.return_value = client.API + client.BALANCE_PATH
        response.read1.return_value = b"{"
        response.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(client.urllib.request, "build_opener", return_value=opener), \
                patch.object(client.time, "monotonic", side_effect=[0, 1, 31]), \
                self.assertRaises(client.TransportError):
            client.http_get(client.BALANCE_PATH, {}, self.key)
        self.assertEqual(response.read1.call_count, 1)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 15)

    def test_redirect_handler_refuses_to_forward_api_key(self):
        with self.assertRaises(client.TransportError):
            client.NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://other.example")

    def test_unallowlisted_endpoint_fails_before_transport(self):
        with self.assertRaises(client.ClientError):
            client.http_get("/v1/billing/charge", {}, self.key)


if __name__ == "__main__":
    unittest.main()
