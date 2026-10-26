"""Offline fixtures only; no browser, HTTP, catalogue or database access."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import browser_social_capture as capture
from scripts import public_export


IG = "https://www.instagram.com/reel/Fixture0001/"
TT = "https://www.tiktok.com/@fixture/video/1234567890123456789"
WHEN = "2026-01-01T12:00:00Z"


def fixture(surface="post_detail", url=IG, **item_changes):
    row = {"url": url, "media_kind": "video", "caption_status": "complete",
           "caption": "Fixture — Comment changer les essuie-glaces de voiture. #entretien", "creator": "Créateur test"}
    if surface == "profile_grid":
        row = {"url": url, "media_kind": "unknown", "caption_status": "unavailable", "grid_alt": "Photo fixture de voiture"}
    row.update(item_changes)
    return {"version": 1, "kind": "CUA_SOCIAL_CAPTURE", "captured_at": WHEN,
            "source_url": url if surface == "post_detail" else "https://www.instagram.com/fixture/",
            "surface": surface, "access": "public", "items": [row]}


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.cleanup_temp)
        self.root = Path(self.temp.name)
        self.out = self.root / "out"
        self.number = 0

    def cleanup_temp(self):
        # Windows indexing can briefly retain just-created temporary directories.
        # Retry only this test's own TemporaryDirectory, never a supplied path.
        for attempt in range(5):
            try:
                self.temp.cleanup()
                return
            except OSError:
                if attempt == 4:
                    raise
                time.sleep(.1 * (attempt + 1))

    def write(self, value):
        self.number += 1
        path = self.root / f"capture-{self.number}.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def rows(self, report, platform="instagram"):
        return json.loads((self.out / report["snapshot"] / platform / "publications.json").read_text(encoding="utf-8"))

    def test_preview_creates_no_output(self):
        result = capture.convert([self.write(fixture())], self.out)
        self.assertEqual(result["detail_records_for_review"]["instagram"], 1)
        self.assertFalse(self.out.exists())
        self.assertEqual(result["network_requests"], 0)

    def test_grid_never_becomes_caption_or_export(self):
        result = capture.convert([self.write(fixture("profile_grid"))], self.out, execute=True)
        self.assertEqual(result["needs_detail"], 1)
        self.assertEqual(result["public_export_manifests"], [])
        self.assertFalse((self.out / result["snapshot"] / "instagram").exists())

    def test_grid_caption_or_native_title_is_rejected(self):
        for change in ({"caption": "Copied grid alt", "caption_status": "complete"}, {"visible_title": "Title from image alt"}):
            with self.subTest(change=change), self.assertRaises(capture.CaptureError):
                capture.validate_capture(fixture("profile_grid", **change))

    def test_legacy_grid_drops_cdn_src_without_fetching(self):
        value = {"source": "https://www.instagram.com/fixture/", "kind": "visible_dom_grid", "captured_at": WHEN,
                 "items": [{"url": IG, "text": "", "images": [{"alt": "Photo voiture", "src": "https://cdn.invalid/private?token=SYNTHETIC"}]}]}
        result = capture.convert([self.write(value)], self.out, execute=True)
        evidence = (self.out / result["snapshot"] / "observations.json").read_text(encoding="utf-8")
        self.assertNotIn("SYNTHETIC", evidence)
        self.assertNotIn("cdn.invalid", evidence)
        self.assertEqual(result["needs_detail"], 1)

    def test_public_export_manifest_is_compatible(self):
        result = capture.convert([self.write(fixture())], self.out, execute=True)
        path = self.out / result["public_export_manifests"][0]
        declaration, pages = public_export.load_manifest(path)
        row = next(public_export.page_rows(pages[0], declaration["pages"][0]))
        prepared = public_export.convert(row, declaration["pages"][0], declaration["source"], 1)
        self.assertTrue(prepared["record"]["public_export_provenance"]["caption_used"])
        self.assertEqual(prepared["record"]["verification_scope"], "exported_metadata_not_independently_verified")
        self.assertFalse(prepared["record"]["audio_language_verified"])

    def test_tiktok_caption_unicode_and_native_title_are_preserved(self):
        text = "交換の説明。\nفحص كهرباء السيارة #ميكانيك\u2028Fiat 1.6 — partie 2"
        result = capture.convert([self.write(fixture(url=TT, caption=text, visible_title="Fiat 1.6 — partie 2"))], self.out, execute=True)
        row = self.rows(result, "tiktok")[0]
        self.assertEqual(row["caption"], text)
        self.assertEqual(row["title"], "Fiat 1.6 — partie 2")
        self.assertNotIn("language", row)

    def test_partial_caption_remains_pending(self):
        report = capture.convert([self.write(fixture(caption_status="partial"))], self.out)
        self.assertEqual(report["needs_detail"], 1)
        self.assertEqual(report["detail_records_for_review"]["instagram"], 0)

    def test_login_block_is_empty_event(self):
        value = fixture(); value.update(access="login_required", items=[])
        report = capture.convert([self.write(value)], self.out, execute=True)
        self.assertEqual(report["unique_identities"], 0)
        self.assertEqual(report["observed_stops"][0]["reason"], "login_required")
        value["items"] = fixture()["items"]
        with self.assertRaises(capture.CaptureError): capture.validate_capture(value)

    def test_private_observation_blocks_existing_public_variant(self):
        private = fixture(); private.update(access="private", items=[])
        report = capture.convert([self.write(fixture()), self.write(private)], self.out)
        self.assertEqual(report["excluded"], 1)
        self.assertEqual(report["detail_records_for_review"]["instagram"], 0)

    def test_image_or_carousel_contradiction_blocks_video_variant(self):
        for kind in ("image", "carousel"):
            with self.subTest(kind=kind):
                report = capture.convert([self.write(fixture()), self.write(fixture("profile_grid", media_kind=kind))], self.out)
                self.assertEqual(report["excluded"], 1)

    def test_identity_deduplicates_author_prefixed_reel_url(self):
        other = fixture(url="https://www.instagram.com/fixture/reel/Fixture0001/")
        report = capture.convert([self.write(fixture()), self.write(other)], self.out, execute=True)
        self.assertEqual(report["unique_identities"], 1)
        self.assertEqual(len(self.rows(report)[0]["browser_capture"]["all_evidence"]), 2)
        self.assertEqual(self.rows(report)[0]["browser_capture"]["all_evidence"][1]["observed_source_url"], other["source_url"])

    def test_duplicate_capture_bytes_not_double_counted(self):
        report = capture.convert([self.write(fixture()), self.write(fixture())], self.out)
        self.assertEqual(report["captures"], 1)
        self.assertEqual(report["observations"], 1)

    def test_resume_adds_detail_without_mutating_old_snapshot(self):
        grid = self.write(fixture("profile_grid"))
        first = capture.convert([grid], self.out, execute=True)
        path = self.out / first["snapshot"] / "needs-detail.json"
        original = path.read_bytes()
        second = capture.convert([self.write(fixture())], self.out, execute=True, resume=True)
        self.assertEqual(second["needs_detail"], 0)
        self.assertEqual(second["unique_identities"], 1)
        self.assertEqual(path.read_bytes(), original)

    def test_changed_source_or_export_refuses_resume(self):
        source = self.write(fixture())
        report = capture.convert([source], self.out, execute=True)
        path = self.out / report["snapshot"] / "instagram/publications.json"
        path.write_text("[]", encoding="utf-8")
        with self.assertRaises(capture.CaptureError): capture.convert([source], self.out, resume=True)

    def test_changed_input_refuses_resume(self):
        source = self.write(fixture())
        capture.convert([source], self.out, execute=True)
        source.write_text(json.dumps(fixture(caption="Changed source")), encoding="utf-8")
        with self.assertRaises(capture.CaptureError): capture.convert([source], self.out, resume=True)

    def test_strict_url_and_timestamp(self):
        for url in ("javascript:alert(1)", "https://instagram.com.evil/reel/Fixture0001/", IG+"?token=secret", "https://user:secret@www.instagram.com/reel/Fixture0001/", "https://www.instagram.com:443/reel/Fixture0001/", "https://www.instagram.com/stories/fixture/123/", "https://127.0.0.1/reel/Fixture0001/"):
            with self.subTest(url=url), self.assertRaises(capture.CaptureError): capture.source_url(url)
        for value in ("2026-01-01", "2026-01-01T12:00:00", "9999-01-01T12:00:00Z", "2026-99-99T12:00:00Z"):
            with self.subTest(value=value), self.assertRaises(capture.CaptureError): capture.timestamp(value)

    def test_detail_identity_must_match_source_page(self):
        value = fixture(); value["items"][0]["url"] = "https://www.instagram.com/reel/Different01/"
        with self.assertRaises(capture.CaptureError): capture.validate_capture(value)

    def test_unknown_fields_and_media_urls_are_refused(self):
        for key in ("comments", "cookies", "hidden_state", "video_url", "thumbnail_url", "language"):
            with self.subTest(key=key), self.assertRaises(capture.CaptureError): capture.validate_capture(fixture(**{key: "value"}))

    def test_fifty_item_and_two_hundred_capture_bounds(self):
        value = fixture("profile_grid"); value["items"] *= 51
        with self.assertRaises(capture.CaptureError): capture.validate_capture(value)
        with self.assertRaises(capture.CaptureError): capture.convert([Path("unused")]*201, self.out)

    def test_actual_time_order_not_iso_lexicographic_order(self):
        older = fixture()
        newer = fixture()
        newer["captured_at"] = "2026-01-01T12:00:00.1Z"
        report = capture.convert([self.write(older), self.write(newer)], self.out, execute=True)
        self.assertEqual(self.rows(report)[0]["browser_capture"]["selected_evidence"]["captured_at"], "2026-01-01T12:00:00.100000Z")

    def test_conflicting_complete_caption_is_not_silently_discarded(self):
        report = capture.convert([self.write(fixture()), self.write(fixture(caption="Buy now sponsored fixture"))], self.out)
        self.assertEqual(report["needs_detail"], 1)
        self.assertEqual(report["detail_records_for_review"]["instagram"], 0)

    def test_signed_url_text_is_rejected(self):
        with self.assertRaises(capture.CaptureError): capture.validate_capture(fixture(caption="https://cdn.invalid/file?token=secret"))

    def test_lock_prevents_execute(self):
        source = self.write(fixture())
        capture.convert([source], self.out, execute=True)
        (self.out / ".capture.lock").write_text("fixture")
        with self.assertRaises(capture.CaptureError): capture.convert([source], self.out, execute=True, resume=True)

    def test_changed_helper_refuses_reinterpretation_on_resume(self):
        source = self.write(fixture())
        capture.convert([source], self.out, execute=True)
        with patch.object(capture, "engine_hash", return_value="changed-helper"):
            with self.assertRaises(capture.CaptureError): capture.convert([source], self.out, resume=True)


if __name__ == "__main__":
    unittest.main()
