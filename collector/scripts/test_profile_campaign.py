"""Synthetic fixtures only; no API, account, browser or production DB access."""
import json
from pathlib import Path
import tempfile
import time
import unittest
import sys

import profile_campaign as engine

APP = next(candidate for parent in Path(__file__).resolve().parents
           for candidate in (parent / "outputs/focus-academy", parent)
           if (candidate / "scripts/social_metadata.py").is_file())
sys.path.insert(0, str(APP))


def tiktok(number=1, **extra):
    return {"aweme_id": str(7100000000000000000 + number), "aweme_type": 0,
            "author": {"unique_id": "fixture", "secret": 0}, "video": {"duration": 42000},
            "desc": "Comment remplacer les essuie-glaces ? #Peugeot #308 #Auto", **extra}


def instagram(number=1, **extra):
    return {"code": f"Fixture_{number:02d}", "user": {"username": "fixture", "is_private": False},
            "media_type": 2, "caption": {"text": "Comment vérifier le niveau d’huile ? #Entretien"}, **extra}


def page(rows, platform="tiktok", more=False, next_cursor=None, remaining=99, **extra):
    payload = {"success": True, "credits_charged": 1, "credits_remaining": remaining}
    if platform == "tiktok":
        payload.update(aweme_list=rows, has_more=int(more), max_cursor=next_cursor)
    else:
        payload.update(items=rows, more_available=more, next_max_id=next_cursor, status="ok")
    return {**payload, **extra}


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.campaign = self.root / "campaign"
        self.plan = {"version": 1, "free_credits": 4, "checked_at": engine.now(),
                     "auto_recharge": False, "out_of_pocket_usd": 0,
                     "profiles": [{"platform": p, "handle": "fixture", "max_pages": 4, "region": "FR"}
                                  for p in ("tiktok", "instagram")]}
        engine.init(self.campaign, self.plan, APP)

    def tearDown(self):
        # Windows indexing can briefly retain a just-written temporary directory.
        for attempt in range(5):
            try:
                self.temp.cleanup()
                break
            except OSError as exc:
                if getattr(exc, "winerror", None) not in {32, 145} or attempt == 4:
                    raise
                time.sleep(.05 * 2 ** attempt)

    def save(self, payload, name="response.json"):
        path = self.root / name
        path.write_bytes(engine.encoded(payload))
        return path

    def ingest(self, payload, platform="tiktok"):
        reservation = engine.reserve(self.campaign, platform + ":fixture")
        path = self.save(payload, f"response-{reservation['attempt']}.json")
        return engine.ingest(self.campaign, reservation["attempt"], path)

    def review(self):
        output = self.root / "review"
        report = engine.export_review(self.campaign, output)
        lines = (output / "quarantine.jsonl").read_text(encoding="utf-8").splitlines()
        return report, [json.loads(line) for line in lines], output

    def test_reserve_before_request_unknown_outcome_stops_duplicate_requests(self):
        request = engine.reserve(self.campaign, "tiktok:fixture")
        self.assertFalse(request["network_executed"])
        with self.assertRaises(engine.CampaignError):
            engine.reserve(self.campaign, "instagram:fixture")
        state = engine.load_state(self.campaign)
        self.assertEqual(state["reserved_credits"], 1)
        self.assertEqual(state["attempts"][0]["state"], "reserved")

    def test_pagination_uses_real_cursor_even_after_empty_page(self):
        self.ingest(page([], more=True, next_cursor=1738435195000))
        request = engine.reserve(self.campaign, "tiktok:fixture")["request"]
        self.assertEqual(request["params"]["max_cursor"], "1738435195000")
        self.assertEqual(request["params"]["region"], "FR")
        self.assertFalse(request["params"]["include_pinned"])
        self.assertEqual(request["endpoint"], "/v3/tiktok/profile/videos")

    def test_cursor_cycle_stops_without_claiming_complete(self):
        self.ingest(page([tiktok()], more=True, next_cursor="123"))
        result = self.ingest(page([tiktok(2)], more=True, next_cursor="123"))
        self.assertTrue(result["cursor_cycle_stopped"])
        self.assertEqual(result["jobs"]["tiktok:fixture"]["state"], "stopped")
        with self.assertRaises(engine.CampaignError):
            engine.reserve(self.campaign, "tiktok:fixture")

    def test_idempotent_ingest_does_not_spend_or_recount(self):
        request = engine.reserve(self.campaign, "tiktok:fixture")
        source = self.save(page([tiktok()]))
        engine.ingest(self.campaign, request["attempt"], source)
        result = engine.ingest(self.campaign, request["attempt"], source)
        self.assertTrue(result["idempotent_replay"])
        self.assertEqual(result["rows"], 1)
        self.assertEqual(result["reserved_credits"], 1)
        source.write_bytes(engine.encoded(page([tiktok(2)])))
        with self.assertRaises(engine.CampaignError):
            engine.ingest(self.campaign, request["attempt"], source)

    def test_native_instagram_caption_and_pagination_mapping(self):
        self.ingest(page([instagram()], "instagram", more=True, next_cursor="3600_12"), "instagram")
        request = engine.reserve(self.campaign, "instagram:fixture")["request"]
        self.assertEqual(request["params"]["next_max_id"], "3600_12")
        self.assertEqual(request["endpoint"], "/v2/instagram/user/posts")
        _, rows, _ = self.review()
        variant = rows[0]["variants"][0]
        self.assertEqual(variant["id"], "instagram:Fixture_01")
        self.assertEqual(variant["display"]["title"], "Comment vérifier le niveau d’huile ?")

    def test_title_description_hashtags_are_distinct_and_vehicle_unknown(self):
        self.ingest(page([tiktok()]))
        report, rows, output = self.review()
        variant = rows[0]["variants"][0]
        self.assertEqual(variant["display"]["title"], "Comment remplacer les essuie-glaces ?")
        self.assertEqual(variant["display"]["hashtags"], ["#Peugeot", "#Auto"])
        self.assertIn("#308", variant["display"]["description"])  # Existing helper preserves numeric references.
        self.assertEqual(variant["vehicle_compatibility"], [])
        self.assertFalse(variant["audio_language_verified"])
        self.assertEqual(report["accepted_for_publication"], 0)
        self.assertFalse((output / "accepted.json").exists())
        self.assertFalse((output / "approval.json").exists())

    def test_dedup_preserves_different_captions_and_all_evidence(self):
        self.ingest(page([tiktok(), tiktok()], more=True, next_cursor="123"))
        self.ingest(page([tiktok(desc="Autre légende qui contredit la première.")]))
        report, rows, _ = self.review()
        self.assertEqual(report["unique_identities"], 1)
        self.assertEqual(report["repeated_identity_observations"], 2)
        self.assertEqual(rows[0]["distinct_metadata_variants"], 2)
        self.assertTrue(rows[0]["conflicting_variants"])
        self.assertEqual(len(rows[0]["variants"][0]["all_evidence"]), 2)

    def test_private_variant_cannot_disappear_behind_public_variant(self):
        self.ingest(page([tiktok(), tiktok(author={"unique_id": "fixture", "secret": 1}, desc="PRIVATE CAPTION")]))
        _, rows, output = self.review()
        self.assertIn("private_source", rows[0]["reasons"])
        exported = (output / "tiktok/publications.json").read_text(encoding="utf-8")
        self.assertNotIn("PRIVATE CAPTION", exported)
        self.assertIn('"isPrivate": true', exported)

    def test_root_private_instagram_declaration_propagates(self):
        self.ingest(page([instagram()], "instagram", user={"is_private": True}), "instagram")
        _, rows, _ = self.review()
        self.assertIn("private_source", rows[0]["reasons"])
        self.assertEqual(rows[0]["variants"][0]["record"]["caption"], "")

    def test_images_and_carousels_are_quarantined_not_videos(self):
        self.ingest(page([tiktok(image_post_info={"images": [{"x": 1}]})]))
        self.ingest(page([instagram(media_type=8)], "instagram"), "instagram")
        _, rows, _ = self.review()
        self.assertTrue(all(not item["variants"][0]["record"]["is_video"] for item in rows))

    def test_comments_contacts_profiles_and_media_not_copied(self):
        row = tiktok(comments=[{"text": "PRIVATE_COMMENT"}], access_token="SECRET",
                     transcript="NOT_A_REAL_TRANSCRIPT", download_url="https://example.org/VIDEO.mp4")
        row["author"]["email"] = "NOT_NEEDED@example.org"
        self.ingest(page([row]))
        _, _, output = self.review()
        all_text = "".join(p.read_text(encoding="utf-8") for p in output.rglob("*") if p.is_file())
        for value in ("PRIVATE_COMMENT", "SECRET", "NOT_A_REAL_TRANSCRIPT", "VIDEO.mp4", "NOT_NEEDED"):
            self.assertNotIn(value, all_text)

    def test_singular_native_ad_flag_and_caption_contacts_are_preserved_as_restrictions(self):
        self.ingest(page([tiktok(is_ad=True, desc="Comment réparer ? Contact test@example.org 06 12 34 56 78")]))
        _, rows, output = self.review()
        record = rows[0]["variants"][0]["record"]
        self.assertTrue(record["isSponsored"])
        self.assertTrue(record["source_contact_redacted"])
        self.assertNotIn("test@example.org", record["caption"])
        self.assertNotIn("06 12 34 56 78", record["caption"])
        self.assertIn("commercial_context_requires_review", rows[0]["reasons"])

    def test_profile_never_supplies_missing_publication_identity(self):
        self.ingest(page([{"desc": "Comment réparer un moteur ?", "aweme_type": 0}]))
        report, rows, _ = self.review()
        self.assertEqual(report["invalid_rows"], 1)
        self.assertEqual(rows, [])

    def test_response_access_message_stops_with_reservation_intact(self):
        request = engine.reserve(self.campaign, "tiktok:fixture")
        with self.assertRaises(engine.CampaignError):
            engine.ingest(self.campaign, request["attempt"], self.save(page([], message="Login required")))
        self.assertEqual(engine.load_state(self.campaign)["attempts"][0]["state"], "reserved")

    def test_lower_balance_tightens_cap_and_never_refunds_failed_request(self):
        self.ingest(page([tiktok()], remaining=0))
        with self.assertRaises(engine.CampaignError):
            engine.reserve(self.campaign, "instagram:fixture")
        state = engine.load_state(self.campaign)
        self.assertEqual(state["free_credits"], 1)

    def test_stop_retains_credit_and_profile_is_not_retried(self):
        request = engine.reserve(self.campaign, "tiktok:fixture")
        result = engine.stop(self.campaign, request["attempt"], "uncertain_outcome")
        self.assertEqual(result["reserved_credits"], 1)
        with self.assertRaises(engine.CampaignError):
            engine.reserve(self.campaign, "tiktok:fixture")
        engine.reserve(self.campaign, "instagram:fixture")

    def test_saved_page_tampering_blocks_resume(self):
        self.ingest(page([tiktok()]))
        (self.campaign / "page-0000.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(engine.CampaignError):
            engine.reserve(self.campaign, "instagram:fixture")

    def test_free_only_plan_rejects_recharge_paid_and_stale(self):
        for changes in ({"auto_recharge": True}, {"out_of_pocket_usd": 1}, {"free_credits": 101}, {"checked_at": "2000-01-01T00:00:00Z"}):
            with self.subTest(changes=changes), self.assertRaises(engine.CampaignError):
                engine.init(self.root / "other", {**self.plan, **changes}, APP)

    def test_public_export_schema_is_compatible_but_approves_nothing(self):
        self.ingest(page([tiktok()]))
        _, _, output = self.review()
        from scripts.public_export import load_manifest
        declaration, paths = load_manifest(output / "tiktok/manifest.json")
        self.assertEqual(declaration["kind"], "PUBLIC_EXPORT")
        self.assertEqual(len(paths), 1)

    def external(self, rows, kind="provider_export"):
        source = self.root / "external"
        source.mkdir(exist_ok=True)
        engine.atomic(source / "posts.json", rows)
        manifest = {"version": 1, "kind": "PUBLIC_EXPORT", "source": {
            "name": "SYNTHETIC SECOND PROVIDER", "kind": kind, "source_url": "https://example.org/export",
            "evidence_reference": "Synthetic test metadata, no real export", "captured_at": engine.now()},
            "pages": [{"file": "posts.json", "format": "json", "schema": "generic",
                       "sha256": engine.file_hash(source / "posts.json")}]}
        engine.atomic(source / "manifest.json", manifest)
        return source / "manifest.json"

    def test_second_provider_same_identity_is_one_review_with_proofs(self):
        self.ingest(page([tiktok()]))
        manifest = self.external([{"url": "https://www.tiktok.com/@fixture/video/7100000000000000001",
                                  "caption": "Légende différente provenant du second fournisseur.", "media_type": "VIDEO"}])
        engine.attach_export(self.campaign, manifest)
        replay = engine.attach_export(self.campaign, manifest)
        self.assertTrue(replay["idempotent_replay"])
        report, rows, _ = self.review()
        self.assertEqual(report["unique_identities"], 1)
        self.assertEqual(rows[0]["observations"], 2)
        self.assertTrue(rows[0]["conflicting_variants"])

    def test_invalid_external_variant_keeps_identity_and_restricts_export(self):
        self.ingest(page([tiktok()]))
        manifest = self.external([{"url": "https://www.tiktok.com/@fixture/video/7100000000000000001",
                                  "caption": "This is an image", "is_video": False}])
        engine.attach_export(self.campaign, manifest)
        _, rows, output = self.review()
        self.assertEqual(rows[0]["observations"], 2)
        self.assertIn("invalid_external_metadata_variant", rows[0]["reasons"])
        self.assertIn('"is_video": false', (output / "tiktok/publications.json").read_text())

    def test_indexed_export_is_not_promoted_to_native_caption(self):
        manifest = self.external([{"url": "https://www.tiktok.com/@fixture/video/7100000000000000001",
                                  "caption": "Mixed comments from a search index"}], "indexed_export")
        with self.assertRaises(engine.CampaignError):
            engine.attach_export(self.campaign, manifest)

    def test_changed_external_page_is_rejected_before_ledger_write(self):
        manifest = self.external([{"url": "https://www.tiktok.com/@fixture/video/7100000000000000001"}])
        (manifest.parent / "posts.json").write_text("[]", encoding="utf-8")
        from server import ValidationError
        with self.assertRaises(ValidationError):
            engine.attach_export(self.campaign, manifest)
        self.assertEqual(engine.load_state(self.campaign)["external_exports"], [])


if __name__ == "__main__":
    unittest.main()
