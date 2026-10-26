import json
from pathlib import Path
import tempfile
import unittest

import brightdata_export as adapter


def tiktok(**values):
    return {"url": "https://www.tiktok.com/@mechanic/video/7123456789012345678?tracking=x", "post_id": "7123456789012345678",
            "profile_username": "mechanic", "description": "Comment faire la vidange ? #vidange", "hashtags": ["#vidange"],
            "post_type": "video", "video_duration": 20, **values}


def instagram(**values):
    return {"url": "https://www.instagram.com/reel/AbCd1234/", "shortcode": "AbCd1234", "user_posted": "garage",
            "description": "Changer un essuie-glace", "product_type": "clips", **values}


class ExportTests(unittest.TestCase):
    def test_caption_not_used_as_title(self):
        identifier, row = adapter.convert(tiktok(), "tiktok")
        self.assertEqual(identifier, "tiktok:7123456789012345678")
        self.assertNotIn("title", row)
        self.assertNotIn("?", row["url"])
        self.assertEqual(row["hashtags"], ["vidange"])
        self.assertEqual(row["duration_seconds"], 20)

    def test_reel_projection_drops_sensitive_and_download_data(self):
        _, row = adapter.convert(instagram(video_url="https://cdn.test/file.mp4?token=secret", top_comments=["email@example.test"], token="secret"), "instagram")
        self.assertNotIn("video_url", row)
        self.assertNotIn("top_comments", row)
        self.assertNotIn("token", row)

    def test_creator_and_id_contradictions(self):
        for values in ({"post_id": "9999999999999"}, {"account_id": "someoneelse"}, {"profile_url": "https://www.tiktok.com/@someoneelse"}):
            with self.assertRaises(adapter.ExportError):
                adapter.convert(tiktok(**values), "tiktok")
        with self.assertRaises(adapter.ExportError):
            adapter.convert(instagram(shortcode="Other000"), "instagram")

    def test_private_and_restricted_not_exported(self):
        for values in ({"is_private": True}, {"availability": "needs_auth"}):
            with self.assertRaises(adapter.ExportError):
                adapter.convert(tiktok(**values), "tiktok")

    def test_discovery_only_and_photo_not_video(self):
        for values in ({"post_type": "image"}, {"post_type": ""}, {"carousel_images": ["x"]}):
            with self.assertRaises(adapter.ExportError):
                adapter.convert(tiktok(**values), "tiktok")
        with self.assertRaises(adapter.ExportError):
            adapter.convert(instagram(product_type=""), "instagram")

    def test_missing_caption_rejected(self):
        with self.assertRaisesRegex(adapter.ExportError, "missing_source_caption"):
            adapter.convert(tiktok(description=""), "tiktok")

    def test_contact_redaction(self):
        _, row = adapter.convert(tiktok(description="Vidange : contact@garage.fr 06 12 34 56 78"), "tiktok")
        self.assertNotIn("@garage", row["caption"])
        self.assertNotIn("06 12", row["caption"])
        self.assertTrue(row["source_contact_redacted"])

    def test_no_language_inferred_from_country(self):
        _, row = adapter.convert(tiktok(country="FR", region="FR"), "tiktok")
        self.assertNotIn("language", row)

    def test_display_name_is_not_mistaken_for_handle(self):
        _, row = adapter.convert(tiktok(profile_username="Garage Mécanique", account_id="mechanic", profile_url="https://www.tiktok.com/@mechanic"), "tiktok")
        self.assertEqual(row["creator"], "mechanic")
        self.assertEqual(row["creator_display_name"], "Garage Mécanique")

    def test_explicit_media_contradictions_rejected(self):
        for values in ({"is_video": False}, {"isVideo": False}, {"isPhoto": True}, {"is_story": True}):
            with self.assertRaises(adapter.ExportError):
                adapter.convert(instagram(**values), "instagram")

    def test_api_key_and_hashtag_urls_refused(self):
        for values in ({"description": "https://example.test?api_key=secret"}, {"description": "https://example.test?api%5Fkey=secret"},
                       {"hashtags": ["https://example.test/?token=secret"]}):
            with self.assertRaises(adapter.ExportError):
                adapter.convert(instagram(**values), "instagram")

    def test_safe_thumbnail_preserved_and_signed_private_urls_omitted(self):
        _, row = adapter.convert(instagram(thumbnail="https://cdn.example.test/preview.jpg"), "instagram")
        self.assertEqual(row["thumbnail_url"], "https://cdn.example.test/preview.jpg")
        for value in ("https://cdn.example.test/a.jpg?token=private", "https://127.0.0.1/a.jpg", "http://cdn.example.test/a.jpg"):
            _, row = adapter.convert(instagram(thumbnail=value), "instagram")
            self.assertNotIn("thumbnail_url", row)

    def test_empirical_native_emoji_hashtag_uses_caption_token(self):
        caption = "Prise OBD2 Volkswagen Beetle #volkswagenbeetle🚘"
        _, row = adapter.convert(tiktok(description=caption, hashtags=["volkswagenbeetle🚘"]), "tiktok")
        self.assertEqual(row["hashtags"], ["volkswagenbeetle"])
        self.assertEqual(row["caption"], caption)
        self.assertEqual(row["source_hashtag_normalization_count"], 1)

    def test_empirical_native_space_hashtag_does_not_invent_compound(self):
        _, row = adapter.convert(tiktok(description="Prise OBD2 Seat Leon #seat #seat leon #leon", hashtags=["seat", "seat leon", "leon"]), "tiktok")
        self.assertEqual(row["hashtags"], ["seat", "leon"])

    def test_malformed_hashtag_requires_exact_caption_evidence(self):
        for tag in ("seat leon", "volkswagenbeetle🚘", "https://example.test?api_key=secret"):
            with self.assertRaises(adapter.ExportError):
                adapter.convert(tiktok(hashtags=[tag]), "tiktok")

    def test_sponsored_kept_flagged_for_review(self):
        _, row = adapter.convert(instagram(is_paid_partnership=True), "instagram")
        self.assertTrue(row["isSponsored"])

    def test_error_body_rejected(self):
        with self.assertRaisesRegex(adapter.ExportError, "provider_error"):
            adapter.convert(tiktok(error="Secret remote message"), "tiktok")

    def test_sensitive_caption_not_written(self):
        with self.assertRaisesRegex(adapter.ExportError, "sensitive_source_text"):
            adapter.convert(tiktok(description="https://example.test?token=secret"), "tiktok")

    def test_manifest_hash_duplicates_variants_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            raw = folder / "raw.json"
            raw.write_text(json.dumps([tiktok(), tiktok(), tiktok(description="Autre légende"), tiktok(error="private secret")]), encoding="utf-8")
            target = folder / "public"
            report = adapter.export(raw, target, "gd_lu702nij2f790tmv9h", "sd_example123", "2026-10-26T12:00:00Z")
            self.assertEqual(report["exported_rows"], 2)
            self.assertEqual(report["exact_metadata_duplicates"], 1)
            self.assertEqual(report["conflicting_id_variants_retained"], 1)
            self.assertEqual(report["publication_count"], 0)
            manifest = json.loads((target / "manifest.json").read_text())
            self.assertEqual(manifest["pages"][0]["sha256"], adapter.digest((target / "posts.json").read_bytes()))
            self.assertNotIn("private secret", (target / "conversion-report.json").read_text())
            with self.assertRaises(FileExistsError):
                adapter.export(raw, target, "gd_lu702nij2f790tmv9h", "sd_example123", "2026-10-26T12:00:00Z")

    def test_invalid_source_shape_and_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            raw = Path(folder) / "raw.json"
            raw.write_text("{}")
            with self.assertRaisesRegex(adapter.ExportError, "expected_array"):
                adapter.export(raw, Path(folder) / "out", "gd_lu702nij2f790tmv9h", "sd_example123", "2026-10-26T12:00:00Z")
            with self.assertRaisesRegex(adapter.ExportError, "invalid_dataset_or_snapshot"):
                adapter.export(raw, Path(folder) / "out", "gd_lu702nij2f790tmv9h", "https://secret", "2026-10-26T12:00:00Z")


if __name__ == "__main__":
    unittest.main()
