"""PUBLIC_EXPORT fixtures are synthetic and temporary; all tests run offline."""
import csv
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts.public_export import (convert, load_manifest, map_row, prepare_public_export)
from scripts.bulk_ingest import digest, file_digest, apply_prepared
from server import ValidationError, initialize


def video(number=1, **extra):
    return {"url": f"https://www.tiktok.com/@fixture/video/{7100000000000000000 + number}",
            "title": "Comment remplacer les essuie-glaces de votre voiture ?",
            "caption": "Étapes pour remplacer les essuie-glaces. #Auto #mécanique #Auto",
            "creator": "Synthetic test creator", "media_type": "VIDEO", **extra}


class PublicExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.output = self.root / "prepared"

    def tearDown(self):
        for attempt in range(4):
            try:
                self.temp.cleanup()
                break
            except OSError as exc:
                if getattr(exc, "winerror", None) not in {32, 145} or attempt == 3:
                    raise
                time.sleep(.05 * 2 ** attempt)

    def manifest(self, pages, *, kind="creator_export"):
        declaration = {"version": 1, "kind": "PUBLIC_EXPORT", "source": {
            "name": "SYNTHETIC TEST FIXTURE", "kind": kind, "source_url": "https://example.org/creator",
            "evidence_reference": "SYNTHETIC TEST — no actual authorization claimed",
            "captured_at": "2026-10-21T00:00:00Z"}, "pages": []}
        for i, (fmt, schema, rows) in enumerate(pages):
            path = self.source / f"page-{i:03}.{fmt}"
            if fmt == "csv":
                with path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
            elif fmt == "jsonl":
                path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
            else:
                path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            declaration["pages"].append({"file": path.name, "sha256": file_digest(path), "format": fmt, "schema": schema})
        path = self.source / "manifest.json"
        path.write_text(json.dumps(declaration), encoding="utf-8")
        return path

    def read(self, name="accepted.json"):
        return json.loads((self.output / name).read_text(encoding="utf-8"))

    def test_native_meta_graph_and_tiktok_display_fields_and_provenance(self):
        meta = {"id": "123456", "permalink": "https://www.instagram.com/reel/Fixture_01/",
                "caption": "Comment remplacer vos essuie-glaces ? #Auto #école", "media_type": "VIDEO",
                "username": "source_creator", "timestamp": "2026-10-20T12:00:00Z"}
        tiktok = {"id": "7100000000000000001", "share_url": video()["url"], "title": video()["title"],
                  "video_description": video()["caption"], "create_time": 1792497600,
                  "cover_image_url": "https://cdn.example.org/cover.jpg?signature=a%2Bb", "duration": 60}
        path = self.manifest([("json", "meta_graph", {"data": [meta], "paging": {"next": "DO_NOT_FETCH"}}),
                              ("json", "tiktok_display", {"data": {"videos": [tiktok], "has_more": True, "cursor": 10}})], kind="authorized_api_export")
        report = prepare_public_export(path, self.output)
        self.assertEqual(report["accepted_candidates"], 2)
        records = {r["platform"]: r for r in self.read()}
        self.assertEqual(records["instagram"]["creator"], "source_creator")
        self.assertEqual(records["tiktok"]["creator"], "")
        self.assertEqual(records["instagram"]["social_content"]["original_caption"], meta["caption"])
        self.assertEqual(records["tiktok"]["social_content"]["original_title"], tiktok["title"])
        self.assertEqual(records["tiktok"]["thumbnail_url"], tiktok["cover_image_url"])
        self.assertEqual(records["tiktok"]["provenance"]["source_record_sha256"], digest(tiktok))
        self.assertEqual(records["tiktok"]["provenance"]["schema_adapter"], "tiktok_display")
        self.assertNotIn("apify", json.dumps(records).lower())
        self.assertEqual(report["network_requests"], 0)

    def test_languages_media_tokens_comments_are_not_promoted_or_copied(self):
        row = video(title="How to replace car wipers", caption="Follow the fitting steps. #Wipers",
                    language="fr", audio_language="fr", search_query="tutoriel français",
                    comments=[{"text": "PRIVATE_COMMENT", "username": "PRIVATE_USER"}],
                    access_token="SECRET_TOKEN", media_url="https://cdn.example.org/SECRET_VIDEO.mp4",
                    transcription="FAKE_TRANSCRIPT", license="CC BY")
        path = self.manifest([("json", "generic", [row])])
        prepare_public_export(path, self.output)
        record = self.read()[0]
        self.assertEqual(record["language"], "und")
        self.assertFalse(record["audio_language_verified"])
        self.assertEqual(record["license"], "unknown")
        self.assertFalse(record["transcriptImported"])
        text = "".join(p.read_text(encoding="utf-8") for p in self.output.glob("*.json*"))
        for value in ("SECRET_TOKEN", "PRIVATE_COMMENT", "PRIVATE_USER", "SECRET_VIDEO", "FAKE_TRANSCRIPT"):
            self.assertNotIn(value, text)

    def test_index_body_does_not_create_a_lesson_or_language(self):
        row = video(title="A day at the garage", caption=video()["caption"])
        path = self.manifest([("json", "generic", [row])], kind="indexed_export")
        result = prepare_public_export(path, self.output)
        self.assertEqual(result["accepted_candidates"], 0)
        self.assertEqual(result["quarantined"], 1)
        entry = json.loads((self.output / "quarantine.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(entry["record"]["language"], "und")
        self.assertEqual(entry["record"]["description"], "")
        self.assertEqual(entry["record"]["social_content"]["original_caption"], "")

    def test_indexed_export_never_claims_native_title_or_confirmed_dates(self):
        path = self.manifest([("json", "generic", [video(published_at="2026-10-20", language="fr",
            thumbnail_url="https://cdn.example.org/image.jpg?signature=abc")])], kind="indexed_export")
        result = prepare_public_export(path, self.output)
        self.assertEqual(result["accepted_candidates"], 1)
        record = self.read()[0]
        social = record["social_content"]
        self.assertEqual(social["field_provenance"]["title"]["basis"], "source_index_title")
        self.assertEqual(social["source_metadata"]["record"]["provenance"]["title_basis"], "source_index_title")
        self.assertEqual(record["category_status"], "inferred_from_indexed_title_rules")
        self.assertEqual(record["publication_date_status"], "indexed_metadata_unverified")
        self.assertEqual(record["thumbnail_status"], "indexed_metadata_unverified")
        self.assertFalse(record["audio_language_verified"])
        self.assertNotIn("platform_metadata", record["language_status"])
        serialized = json.dumps(record)
        self.assertNotIn("apify", serialized)
        self.assertNotIn("source_native_title", serialized)

    def test_dedup_private_and_promotional_variants_cannot_disappear(self):
        path = self.manifest([("json", "generic", [video(), video(private=True), video(2), video(2, sponsored=True), video(3), video(3)])])
        report = prepare_public_export(path, self.output)
        self.assertEqual(report["unique_media_identities"], 3)
        self.assertEqual(report["duplicates_in_batch"], 3)
        self.assertEqual(report["accepted_candidates"], 1)
        self.assertEqual(report["quarantined"], 2)
        self.assertEqual(len(self.read()[0]["public_export_variants"]), 2)

    def test_csv_native_title_unicode_hashtags_and_separator_survive(self):
        caption = "Étapes de montage.\u2028Respectez la notice. #fypシ゚viral #école #Auto"
        row = video(caption=caption, hashtags=json.dumps(["#école", "#Auto", "#Auto"]))
        path = self.manifest([("csv", "generic", [row])])
        prepare_public_export(path, self.output)
        social = self.read()[0]["social_content"]
        self.assertEqual(social["original_caption"], caption)
        self.assertEqual(social["hashtags"], ["#fypシ゚viral", "#école", "#Auto"])

    def test_jsonl_unicode_line_separator_is_not_a_physical_row(self):
        path = self.manifest([("jsonl", "generic", [video(caption="Étapes.\u2028Vérifiez la notice."), video(2)])])
        self.assertEqual(prepare_public_export(path, self.output)["source_records"], 2)

    def test_missing_title_and_fragment_caption_need_review(self):
        path = self.manifest([("json", "generic", [video(title="", caption=""),
            video(2, title="", caption="Remplacer les essuie-glaces voiture sans ponctuation"),
            video(3, title="", caption="Comment remplacer les essuie-glaces ? Consultez la notice.")])])
        report = prepare_public_export(path, self.output)
        self.assertEqual(report["accepted_candidates"], 1)
        self.assertEqual(report["quarantined"], 2)
        self.assertEqual(self.read()[0]["title"], "Comment remplacer les essuie-glaces ?")

    def test_resume_preserves_outputs_and_detects_tampered_cache_or_input(self):
        path = self.manifest([("jsonl", "generic", [video(1)]), ("jsonl", "generic", [video(2), video(3)])])
        report = prepare_public_export(path, self.output, max_records=2)
        self.assertTrue(report["truncated_at_bound"])
        self.assertEqual(prepare_public_export(path, self.output, max_records=2, resume=True)["accepted_sha256"], report["accepted_sha256"])
        with self.assertRaises(ValidationError):
            prepare_public_export(path, self.output, max_records=3, resume=True)
        cache = self.output / "normalized-page-0000.json"
        cache.write_text("[]", encoding="utf-8")
        with self.assertRaises(ValidationError):
            prepare_public_export(path, self.output, max_records=2, resume=True)
        (self.source / "page-000.jsonl").write_text("[]", encoding="utf-8")
        with self.assertRaises(ValidationError):
            load_manifest(path)

    def test_manifest_blocks_traversal_absolute_paths_secrets_unknown_fields_and_token_urls(self):
        path = self.manifest([("json", "generic", [video()])])
        original = json.loads(path.read_text(encoding="utf-8"))
        for filename in ("../page.json", "C:/secret.json", ".hidden.json", "tokens.json", "pages/../../secret.json"):
            changed = json.loads(json.dumps(original))
            changed["pages"][0]["file"] = filename
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.subTest(filename=filename), self.assertRaises(ValidationError):
                load_manifest(path)
        for field in ("headers", "cookies", "token"):
            changed = {**original, field: "secret"}
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.subTest(field=field), self.assertRaises(ValidationError):
                load_manifest(path)
        original["source"]["source_url"] = "https://example.org/export?access_token=SECRET"
        path.write_text(json.dumps(original), encoding="utf-8")
        with self.assertRaises(ValidationError):
            load_manifest(path)

    def test_media_type_negative_and_ai_flag_require_review(self):
        path = self.manifest([("json", "generic", [video(media_type="IMAGE"), video(2, is_aigc=True)])])
        report = prepare_public_export(path, self.output)
        self.assertEqual(report["accepted_candidates"], 0)
        self.assertEqual(report["quarantined"], 2)

    def test_numeric_restrictions_and_ai_alias_never_lose_negative_evidence(self):
        flags = ("private", "is_private", "isPrivate", "sponsored", "is_ad", "isAd", "isSponsored",
                 "is_photo", "is_story", "is_aigc", "is_ai_generated")
        rows = [video(index + 1, **{flag: 1}) for index, flag in enumerate(flags)]
        rows += [video(50, private=2), video(51, sponsored=1.0), video(52, private=0, sponsored="false")]
        path = self.manifest([("json", "generic", rows)])
        report = prepare_public_export(path, self.output)
        self.assertEqual(report["accepted_candidates"], 1)
        self.assertEqual(report["quarantined"], len(rows) - 1)

    def test_explicit_non_video_flag_overrides_reel_path_and_positive_duplicate(self):
        values = (False, 0, 0.0, "false", "0", "no")
        rows = []
        for key in ("is_video", "isVideo"):
            for value in values:
                number = len(rows)
                url = f"https://www.instagram.com/reel/Fixture_{number:03}/"
                rows.extend([video(url=url), video(url=url, **{key: value})])
        rows.extend([video(url="https://www.instagram.com/reel/Fixture_conflict/", is_video=True, isVideo=False),
                     video(url="https://www.instagram.com/reel/Fixture_positive/", isVideo=1)])
        path = self.manifest([("json", "generic", rows)])
        report = prepare_public_export(path, self.output)
        self.assertEqual(report["accepted_candidates"], 1)
        self.assertEqual(report["quarantined"], 13)
        self.assertEqual(report["duplicates_in_batch"], 12)
        self.assertEqual(self.read()[0]["id"], "instagram:Fixture_positive")

    def test_native_schema_and_media_identity_must_agree(self):
        path = self.manifest([
            ("json", "meta_graph", {"data": [{"permalink": video()["url"], "caption": video()["caption"], "media_type": "VIDEO"}]}),
            ("json", "tiktok_display", {"data": {"videos": [{"share_url": video(2)["url"],
                "id": "7100000000000000099", "title": video()["title"]}]}})])
        result = prepare_public_export(path, self.output)
        self.assertEqual(result["accepted_candidates"], 0)
        self.assertEqual(result["quarantined"], 2)

    def test_explicit_bounds_duplicate_pages_and_invalid_json_fail_closed(self):
        path = self.manifest([("json", "generic", [video()])])
        for bound in (True, 0, -1, 100001):
            with self.subTest(bound=bound), self.assertRaises(ValidationError):
                prepare_public_export(path, self.output, max_records=bound)
        with patch("scripts.public_export.MAX_PAGE_BYTES", 1), self.assertRaises(ValidationError):
            load_manifest(path)
        original = json.loads(path.read_text(encoding="utf-8"))
        changed = {**original, "pages": original["pages"] * 2}
        path.write_text(json.dumps(changed), encoding="utf-8")
        with self.assertRaises(ValidationError):
            load_manifest(path)
        path.write_text(json.dumps(original), encoding="utf-8")
        raw = self.source / original["pages"][0]["file"]
        raw.write_text("BROKEN_JSON", encoding="utf-8")
        original["pages"][0]["sha256"] = file_digest(raw)
        path.write_text(json.dumps(original), encoding="utf-8")
        with self.assertRaises(ValueError):
            prepare_public_export(path, self.output)
        self.assertFalse((self.output / "accepted.json").exists())

    def test_capacity_1500_unique_synthetic_records_across_pages(self):
        pages = [("jsonl", "generic", [video(i) for i in range(start, start + 300)]) for start in range(1, 1501, 300)]
        path = self.manifest(pages)
        report = prepare_public_export(path, self.output, max_records=5000)
        self.assertEqual(report["source_records"], 1500)
        self.assertEqual(report["accepted_candidates"], 1500)
        self.assertFalse(report["truncated_at_bound"])
        self.assertEqual(report["processed_pages"], 5)
        self.assertEqual(len({r["id"] for r in self.read()}), 1500)

    def test_compatible_with_existing_apply_dry_run_and_explicit_approval_guard(self):
        path = self.manifest([("json", "generic", [video()])])
        prepare_public_export(path, self.output)
        database = initialize(self.root / "isolated.sqlite3")
        before = file_digest(database)
        result = apply_prepared(self.output, db=database)
        self.assertEqual(result["new"], 1)
        self.assertFalse(result["database_modified"])
        self.assertEqual(file_digest(database), before)
        with self.assertRaises(ValidationError):
            apply_prepared(self.output, db=database, execute=True)


if __name__ == "__main__":
    unittest.main()
