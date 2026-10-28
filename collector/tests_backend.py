import http.client
import datetime as dt
import copy
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from server import (ValidationError, canonical_url, connect, get_video, import_items,
                    import_transcript, initialize, make_server, parse_vtt, search, stats, web_url,
                    import_automotive_enrichment, vehicle_options, discovery, suggestions, recommendations,
                    normalize_guides, search_resources)
from automotive import extract_automotive


def sample(index, **kwargs):
    return {
        "id": f"sample_{index}",
        "url": f"https://example.org/videos/{index}",
        "title": f"Vidéo télémétrie {index}",
        "description": "Comprendre le freinage et les réglages.",
        "language": "fr", "category": "engineering", "level": "beginner",
        **kwargs,
    }

def vehicle(make="Renault", model="Clio", generation="III", **kwargs):
    return {"make": make, "model": model, "generation": generation, "engine": "",
            "body_type": "", "fuel_type": "", "year_from": None, "year_to": None,
            "evidence": "TEST FIXTURE ONLY — explicit vehicle mention", "status": "title_mention", **kwargs}


def automotive(vehicles=None, tasks=None, systems=None, specs=None):
    return {"vehicles": vehicles or [], "tasks": tasks or [], "systems": systems or [],
            "specifications": specs or [], "status": "metadata_extraction"}

def discovery_fixture():
    topic = lambda ident, intent, label, filters, query="": {
        "id": ident, "intentId": intent, "label": {"fr": label, "en": label, "es": label},
        "aliases": [label], "filters": filters, "query": query}
    return {"version": 1, "intents": [{"id": "maintain"}, {"id": "drive"}],
            "defaultTopicIds": ["braking", "oil-change"],
            "topics": [
                topic("oil-change", "maintain", "Vidange oil change cambio aceite", {"task": "oil_change"}),
                topic("oil-grade", "maintain", "Huile oil aceite", {"task": "oil_spec"}),
                topic("braking", "drive", "Freinage braking", {"category": "driving"}),
            ],
            "shelves": [{"id": "selection", "enabled": True, "reviewedAt": "2026-10-01T00:00:00Z",
                         "expiresAt": "2026-11-01T00:00:00Z",
                         "items": [{"videoId": "sample_1"}, {"videoId": "sample_2"}, {"videoId": "missing"}]}]}


def guide_fixture():
    return {"language": "fr", "updatedAt": "2026-10-20", "guides": [
        {"id": "guide-oil", "title": "Préparer une vidange", "intro": "Comprendre une huile 5W30.",
         "task": "oil_change", "steps": ["Lire la notice."],
         "sources": [{"title": "Renault — exemple Clio", "url": "https://example.org/manual", "publisher": "Renault"}]},
        {"id": "guide-wipers", "title": "Comprendre les essuie-glaces", "task": "wipers",
         "sources": [{"title": "Source de méthode", "url": "https://example.org/wipers"}]},
    ]}


def cleanup_temp(temp):
    # Windows file indexing can briefly retain a directory after SQLite closes it.
    for attempt in range(5):
        try:
            temp.cleanup()
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.05 * (attempt + 1))


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = initialize(Path(self.temp.name) / "test.sqlite3")

    def tearDown(self):
        cleanup_temp(self.temp)

    def test_caption_vehicle_evidence_survives_index_search_and_detail(self):
        proof = "TEST FIXTURE ONLY — Volkswagen T-Roc : remplacement du filtre."
        mention = vehicle("Volkswagen", "T-Roc", "", status="caption_mention", evidence=proof)
        import_items(self.db, [sample(1, title="Remplacer le filtre", description=proof,
                                     automotive=automotive([mention]))], strict=True)
        with connect(self.db) as conn:
            row = conn.execute("SELECT status,evidence FROM video_vehicles WHERE video_id='sample_1'").fetchone()
            self.assertEqual((row["status"], row["evidence"]), ("caption_mention", proof))
        result = search(self.db, {"make": "Volkswagen", "model": "T-Roc"})
        self.assertEqual(result["total"], 1)
        for item in (result["items"][0], get_video(self.db, "sample_1")):
            self.assertEqual(item["automotive"]["vehicles"], [mention])
        self.assertEqual(search(self.db, {"make": "Volkswagen", "engine": "1.6 TDI"})["total"], 0)
        options = vehicle_options(self.db, {"make": "Volkswagen"})
        self.assertEqual(options["evidence_scope"], "title_or_caption_mention")
        self.assertFalse(options["compatibility_verified"])

    def test_caption_vehicle_requires_nonempty_text_evidence(self):
        for evidence in (None, "", "  ", True, {"caption": "VW T-Roc"}):
            with self.subTest(evidence=evidence), self.assertRaises(ValidationError):
                import_items(self.db, [sample(1, automotive=automotive([
                    vehicle(status="caption_mention", evidence=evidence)]))], strict=True)
        self.assertEqual(search(self.db, {})["total"], 0)

    def test_unicode_accents_multilingual(self):
        import_items(self.db, [sample(1), sample(2, title="日本語 ブレーキング", language="ja"),
                               sample(3, title="تعلم القيادة", language="ar")], strict=True)
        self.assertEqual(search(self.db, {"q": "telemetrie"})["total"], 1)
        self.assertEqual(search(self.db, {"q": "télémétrie"})["total"], 1)
        self.assertEqual(search(self.db, {"q": "日本語"})["total"], 1)
        self.assertEqual(search(self.db, {"q": "القيادة"})["total"], 1)

    def test_social_permalink_aliases_enrich_one_media_identity(self):
        pairs = [
            ("https://www.instagram.com/p/AbCd12/", "https://www.instagram.com/reel/AbCd12/"),
            ("https://www.facebook.com/watch/?v=123456", "https://www.facebook.com/page/videos/a-title/123456/"),
            ("https://www.instagram.com/reel/AbCd34/", "https://www.instagram.com/source.name/reel/AbCd34/"),
        ]
        for index, (original, alias) in enumerate(pairs):
            import_items(self.db, [sample(index, url=original, review_status="editorial_selection")], strict=True)
            result = import_items(self.db, [sample(index + 10, url=alias)], strict=True)
            self.assertEqual((result["inserted"], result["updated"]), (0, 1))
            item = get_video(self.db, f"sample_{index}")
            self.assertEqual(item["url"], canonical_url(original)[0])
            self.assertEqual(item["review_status"], "editorial_selection")
        self.assertEqual(stats(self.db)["total_videos"], 3)

    def test_source_questions_are_searchable_but_not_transcripts_or_answers(self):
        question = {"question_fr": "Compatible Paccar ?", "excerpt": "Can this scan Paccar?",
            "source_url": "https://example.org/comment/1", "retrieved_at": "2026-10-20T00:00:00Z",
            "author": "not-to-expose"}
        import_items(self.db, [sample(1, comments={"questions": [question]})], strict=True)
        result = search(self.db, {"q": "Paccar"})
        self.assertEqual(result["total"], 1)
        item = get_video(self.db, "sample_1")
        self.assertFalse(item["has_transcript"])
        self.assertIsNone(item["transcript"])
        self.assertEqual(item["source_questions"][0]["answer_status"], "not_verified")
        self.assertNotIn("author", item["source_questions"][0])
        self.assertNotIn("source_questions_text", item)
        import_items(self.db, [sample(1)], strict=True)
        self.assertEqual(search(self.db, {"q": "Paccar"})["total"], 1)
        question["question_fr"], question["excerpt"] = "Compatible Zedtron ?", "Zedtron?"
        import_items(self.db, [sample(1, comments={"questions": [question]})], strict=True)
        self.assertEqual(search(self.db, {"q": "Paccar"})["total"], 0)
        self.assertEqual(search(self.db, {"q": "Zedtron"})["total"], 1)
        self.assertEqual(stats(self.db)["total_source_questions"], 1)

    def test_fts_migration_retains_existing_content_and_new_questions(self):
        import_items(self.db, [sample(1)], strict=True)
        with connect(self.db) as conn:
            for trigger in ("videos_ai", "videos_ad", "videos_au"):
                conn.execute(f"DROP TRIGGER {trigger}")
            conn.execute("DROP TABLE videos_fts")
            conn.execute("CREATE VIRTUAL TABLE videos_fts USING fts5(title,creator,description,tags,transcript_text,"
                         "content='videos',content_rowid='rowid',tokenize='unicode61 remove_diacritics 2')")
        initialize(self.db)
        self.assertEqual(search(self.db, {"q": "télémétrie"})["total"], 1)
        import_items(self.db, [sample(2)], strict=True)
        self.assertEqual(search(self.db, {"q": "telemetrie"})["total"], 2)

    def test_pagination_facets_and_filter(self):
        import_items(self.db, [sample(i, language="en" if i % 2 else "fr") for i in range(31)])
        one = search(self.db, {"page": "1", "per_page": "7"})
        two = search(self.db, {"page": "2", "per_page": "7"})
        self.assertEqual(one["total"], 31)
        self.assertEqual(one["pages"], 5)
        self.assertFalse({v["id"] for v in one["items"]} & {v["id"] for v in two["items"]})
        filtered = search(self.db, {"language": "en", "per_page": "100"})
        self.assertEqual(filtered["total"], 15)
        self.assertEqual(filtered["facets"]["language"], [{"value": "en", "count": 15}])
        self.assertEqual(search(self.db, {"page": "100"})["items"], [])

    def test_discovery_query_language_is_not_a_video_language_and_evidence_can_improve(self):
        import_items(self.db, [sample(1, title="English metadata title", language="fr",
            language_status="inferred_from_discovery_query", review_status="editorial_selection")], strict=True)
        item = get_video(self.db, "sample_1")
        self.assertEqual(item["language"], "und")
        self.assertEqual(item["language_confidence"], "unknown")
        self.assertEqual(search(self.db, {"language": "fr"})["total"], 0)
        with connect(self.db) as conn:
            metadata = json.loads(conn.execute('SELECT metadata_json FROM videos').fetchone()[0])
            self.assertEqual(metadata["discovery_language_hint"], "fr")
        import_items(self.db, [sample(1, language="fr-FR", language_status="platform_metadata")], strict=True)
        item = get_video(self.db, "sample_1")
        self.assertEqual(item["review_status"], "editorial_selection")
        self.assertEqual(item["language"], "fr")
        self.assertEqual(item["language_tag"], "fr-fr")
        self.assertEqual(item["language_confidence"], "platform_declared")
        import_items(self.db, [sample(1, language="en", language_status="inferred_from_channel_not_verified")], strict=True)
        self.assertEqual(get_video(self.db, "sample_1")["language"], "fr")
        self.assertEqual(stats(self.db)["language_summary"], [{"language": "fr", "total": 1,
            "platform_declared": 1, "source_caption_track": 0, "estimated": 0, "unknown": 0}])
        import_items(self.db, [sample(2, language="fr-FR", language_status="inferred_from_channel_not_verified",
            review_status="editorial_selection")], strict=True)
        import_items(self.db, [sample(2, language="en", language_status="platform_metadata")], strict=True)
        self.assertEqual(get_video(self.db, "sample_2")["language_tag"], "en")

    def test_explicit_language_filter_keeps_estimates_separate_from_unknown(self):
        import_items(self.db, [sample(1, language="fr", language_status="inferred_from_public_caption"),
            sample(2, language="en", language_status="caption_track"),
            sample(3, language="fr", language_status="inferred_from_discovery_query")], strict=True)
        self.assertEqual(search(self.db, {"language": "FR"})["total"], 1)
        self.assertEqual(search(self.db, {"language": "und"})["total"], 1)
        self.assertEqual(search_resources(self.db, {"language": "en"}, guides=[])["total"], 1)

    def test_compound_clio_title_is_found_without_fabricating_missing_engine(self):
        titles = ['Vidange CLIO3 1.5 DCI', 'Vidange Clio 3', 'Vidange Monclio3', 'Vidange 208']
        import_items(self.db, [sample(index, title=title, automotive=extract_automotive(title))
            for index,title in enumerate(titles)], strict=True)
        for query in ['vidange clio 3', 'vidange clio3']:
            result = search(self.db, {'q':query})
            self.assertEqual({item['id'] for item in result['items']}, {'sample_0','sample_1'})
            self.assertTrue(all(item['automotive']['vehicles'][0]['status']=='inferred_from_unambiguous_model'
                for item in result['items']))
        self.assertEqual(search(self.db, {'q':'vidange clio3 1.5 DCI'})['total'], 1)
        self.assertEqual(search(self.db, {'q':'vidange clio3 1.8 DCI'})['total'], 0)
        self.assertEqual(search(self.db, {'q':'vidange 208'})['inferred_vehicle'], {})

    def test_injection_and_bounds(self):
        import_items(self.db, [sample(1)])
        for query in ["' OR 1=1; DROP TABLE videos;--", '":*", NEAR(x) OR y', ":", "***"]:
            search(self.db, {"q": query})
        search(self.db, {"language": "' OR 1=1 --"})
        self.assertEqual(stats(self.db)["total_videos"], 1)
        for params in [{"page": "0"}, {"page": "-2"}, {"per_page": "101"},
                       {"sort": "title;DELETE"}, {"q": "a" * 301}, {"duration": "banana"}]:
            with self.assertRaises(ValidationError):
                search(self.db, params)

    def test_canonical_dedupe_and_idempotent_update(self):
        one = sample(1, url="https://youtu.be/abcdefghijk?si=abc", title="Old title")
        two = sample(2, url="https://www.youtube.com/watch?v=abcdefghijk&utm_source=x",
                     title="New title")
        self.assertEqual(import_items(self.db, [one])["inserted"], 1)
        self.assertEqual(import_items(self.db, [two])["updated"], 1)
        self.assertEqual(stats(self.db)["total_videos"], 1)
        self.assertEqual(search(self.db, {"q": "New"})["items"][0]["id"], "sample_1")
        self.assertEqual(search(self.db, {"q": "Old"})["total"], 0)

    def test_unknown_rights_and_transcript_permissions(self):
        result = import_items(self.db, [
            sample(1, license="public"),
            sample(2, license="creative-commons"),
            sample(3, transcript={"text": "A fake unlicensed transcript"}),
        ])
        self.assertEqual(result["inserted"], 1)
        self.assertEqual(result["rejected"], 2)
        item = get_video(self.db, "sample_1")
        self.assertEqual(item["license"], "unknown")
        self.assertIsNone(item["transcript"])
        self.assertEqual(stats(self.db)["verified_videos"], 0)

    def test_authorized_vtt_search_and_metadata_refresh(self):
        import_items(self.db, [sample(1)], strict=True)
        vtt = Path(self.temp.name) / "captions.vtt"
        vtt.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n"
                       "<v Alice>Contrepoids aérodynamique</v>\n\n"
                       "00:00:02.000 --> 00:00:03.000\nContrepoids aérodynamique\n",
                       encoding="utf-8")
        import_transcript(self.db, "sample_1", vtt, "fr", "https://example.org/captions",
                          "creator-permission", "Written consent test fixture only")
        self.assertEqual(search(self.db, {"q": "contrepoids", "transcript": "available"})["total"], 1)
        transcript = get_video(self.db, "sample_1")["transcript"]
        self.assertEqual(transcript["text"], "Contrepoids aérodynamique")
        self.assertEqual(transcript["segments"][0]["start"], 0)
        self.assertEqual(transcript["segments"][0]["end"], 2)
        self.assertIn("creator-permission", transcript["permission"])
        import_items(self.db, [sample(1, title="New metadata")])
        self.assertEqual(stats(self.db)["with_transcript"], 1)
        self.assertEqual(search(self.db, {"q": "aerodynamique"})["total"], 1)
        self.assertEqual(get_video(self.db, "sample_1")["transcript"]["segments"][0]["end"], 2)

    def test_strict_import_rollback(self):
        with self.assertRaises(ValidationError):
            import_items(self.db, [sample(1), {"title": "Missing URL"}], strict=True)
        self.assertEqual(stats(self.db)["total_videos"], 0)

    def test_url_safety(self):
        for value in ["javascript:alert(1)", "file:///C:/private", "http://127.0.0.1/x",
                      "http://192.168.1.10/x", "https://localhost/x",
                      "https://user:password@example.org/x", "https://example.org:8000/x"]:
            with self.assertRaises(ValidationError, msg=value):
                web_url(value)
        self.assertEqual(canonical_url("https://youtu.be/abcdefghijk")[0],
                         "https://www.youtube.com/watch?v=abcdefghijk")
        self.assertEqual(canonical_url("https://vimeo.com/12345678/abc123")[0],
                         "https://vimeo.com/12345678?h=abc123")

    def test_metadata_status_is_not_content_verification(self):
        import_items(self.db, [
            sample(1, reviewStatus="curated", verificationScope="public_search_metadata"),
            sample(2, reviewStatus="verified", verificationScope="editorial_review"),
        ])
        self.assertFalse(get_video(self.db, "sample_1")["content_verified"])
        self.assertEqual(stats(self.db)["verified_videos"], 1)

    def test_no_unknown_duration_fabrication(self):
        import_items(self.db, [sample(1), sample(2, durationSeconds=180),
                               sample(3, durationSeconds=800), sample(4, durationSeconds=2000)])
        self.assertIsNone(get_video(self.db, "sample_1")["duration_seconds"])
        for duration in ["short", "medium", "long"]:
            self.assertEqual(search(self.db, {"duration": duration})["total"], 1)

    def test_open_license_filter_and_saved_ids(self):
        import_items(self.db, [
            sample(1, license="creative-commons", license_url="https://creativecommons.org/licenses/by/4.0/"),
            sample(2, license="public-domain", license_url="https://example.org/rights"),
            sample(3, license="permission", license_url="https://example.org/permission"),
            sample(4),
        ])
        self.assertEqual(search(self.db, {"license": "open"})["total"], 2)
        ids = search(self.db, {"ids": "sample_1,sample_3"})["items"]
        self.assertEqual({row["id"] for row in ids}, {"sample_1", "sample_3"})
        with self.assertRaises(ValidationError):
            search(self.db, {"ids": "' OR 1=1 --"})

    def test_question_glossary_and_precise_terms(self):
        import_items(self.db, [
            sample(1, title="Braking without locking wheels", description="", language="en"),
            sample(2, title="Freinage progressif", description=""),
        ])
        result = search(self.db, {"q": "Comment freiner sans bloquer les roues ?"})
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["id"], "sample_1")
        self.assertEqual(result["search_mode"], "glossary")
        self.assertEqual(search(self.db, {"q": "Comment freiner SennaZX927 ?"})["total"], 0)
        literal = search(self.db, {"q": "Freinage"})
        self.assertEqual(literal["search_mode"], "literal")
        self.assertEqual(literal["total"], 1)

    def test_related_questions_are_labeled(self):
        import_items(self.db, [sample(1, title="Freinage progressif", description="")])
        result = search(self.db, {"q": "Comment freiner sans bloquer les roues ?"})
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["search_mode"], "related_topics")

    def test_discovery_refresh_does_not_downgrade_review_and_rights(self):
        import_items(self.db, [sample(
            1, title="Qualified title", review_status="editorial_selection",
            verification_scope="public_video_metadata", license="creative-commons",
            license_url="https://creativecommons.org/licenses/by/4.0/",
            duration_seconds=800, language_status="platform_metadata",
        )], strict=True)
        import_items(self.db, [sample(
            1, title="Unqualified search title", language="de",
            review_status="candidate", verification_scope="public_search_metadata",
        )], strict=True)
        item = get_video(self.db, "sample_1")
        self.assertEqual(item["title"], "Qualified title")
        self.assertEqual(item["license"], "creative-commons")
        self.assertEqual(item["review_status"], "editorial_selection")
        self.assertEqual(item["language"], "fr")
        self.assertEqual(item["duration_seconds"], 800)

    def test_motorsport_and_adjacent_domains_are_distinct(self):
        import_items(self.db, [sample(1), sample(2, domainScope="automotive_adjacent",
                                                    level_slug="unknown")], strict=True)
        motorsport = search(self.db, {"domain": "motorsport"})
        automotive = search(self.db, {"domain": "automotive_adjacent"})
        self.assertEqual([v["id"] for v in motorsport["items"]], ["sample_1"])
        self.assertEqual([v["id"] for v in automotive["items"]], ["sample_2"])
        self.assertEqual(automotive["items"][0]["level"], "unknown")
        self.assertEqual(search(self.db, {"level": "unknown"})["total"], 1)
        self.assertEqual(automotive["facets"]["domain"], [{"value": "automotive_adjacent", "count": 1}])
        self.assertEqual(len(stats(self.db)["facets"]["domain"]), 2)
        with self.assertRaises(ValidationError):
            search(self.db, {"domain": "invalid"})

    def test_vehicle_filters_require_one_same_application(self):
        import_items(self.db, [
            sample(1, automotive=automotive([
                vehicle(engine="1.5 dCi", year_from=2005, year_to=2009),
                vehicle("Volkswagen", "Golf", "IV", engine="1.9 TDI", year_from=2000, year_to=2002)])),
            sample(2, automotive=automotive([vehicle()])),
        ], strict=True)
        self.assertEqual(search(self.db, {"make": "Renault", "engine": "1.9 TDI"})["total"], 0)
        self.assertEqual(search(self.db, {"make": "Renault", "year": "2001"})["total"], 0)
        self.assertEqual(search(self.db, {"model": "Clio", "generation": "IV"})["total"], 0)
        self.assertEqual(search(self.db, {"make": "Renault", "engine": "1.5 dCi", "year": "2007"})["total"], 1)
        self.assertEqual(search(self.db, {"model": "Clio"})["total"], 2)
        self.assertEqual(search(self.db, {"model": "Clio", "fuel_type": "diesel"})["total"], 0)

    def test_year_missing_and_single_endpoint_are_not_open_ranges(self):
        import_items(self.db, [
            sample(1, automotive=automotive([vehicle(year_from=2007)])),
            sample(2, automotive=automotive([vehicle(year_to=2009)])),
            sample(3, automotive=automotive([vehicle()])),
        ], strict=True)
        self.assertEqual(search(self.db, {"year": "2007"})["total"], 1)
        self.assertEqual(search(self.db, {"year": "2009"})["total"], 1)
        self.assertEqual(search(self.db, {"year": "2008"})["total"], 0)
        self.assertEqual(vehicle_options(self.db, {})["options"]["year"],
                         [{"value": "2007", "count": 1}, {"value": "2009", "count": 1}])
        for value in ["1850", "2101", "200x", "20"]:
            with self.assertRaises(ValidationError):
                search(self.db, {"year": value})

    def test_vehicle_options_hierarchy_ignores_task_language_and_query(self):
        import_items(self.db, [
            sample(1, automotive=automotive([vehicle(), vehicle()])),
            sample(2, automotive=automotive([vehicle(generation="IV")])),
            sample(3, automotive=automotive([vehicle("Renault", "Megane", "II")])),
            sample(4, automotive=automotive([vehicle("Peugeot", "308", "II")])),
        ], strict=True)
        selected = {"make": "Renault", "model": "Clio", "generation": "III"}
        clean_options = vehicle_options(self.db, selected)
        options = vehicle_options(self.db, {**selected, "task": "missing", "language": "ja", "q": "nonsense"})
        self.assertEqual(options, clean_options)
        self.assertEqual(options["total_videos"], 1)
        self.assertEqual(options["matching_applications"], 1)
        self.assertEqual({v["value"] for v in options["options"]["make"]}, {"Renault", "Peugeot"})
        self.assertEqual({v["value"] for v in options["options"]["model"]}, {"Clio", "Megane"})
        self.assertEqual({v["value"] for v in options["options"]["generation"]}, {"III", "IV"})

    def test_specifications_are_exact_mentions_not_compatibility(self):
        specs = lambda value: [{"kind": "oil_viscosity", "value": value, "evidence": value + " TEST ONLY",
                                "status": "title_mention"}]
        import_items(self.db, [
            sample(1, automotive=automotive(specs=specs("5W-30"))),
            sample(2, automotive=automotive(specs=specs("5W-40"))),
            sample(3, title="5W30 appears only as ordinary text"),
        ], strict=True)
        for value in ["5w30", "5W-30", "5W 30"]:
            self.assertEqual(search(self.db, {"spec": value})["total"], 1)
        self.assertEqual(search(self.db, {"spec": "5w3"})["total"], 0)
        self.assertEqual(search(self.db, {"spec": "5w30", "make": "Renault"})["total"], 0)
        result = search(self.db, {"q": "huile 5W30"})
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["inferred_spec"], "5W-30")

    def test_natural_vehicle_task_question_keeps_generation_engine_and_unknown_words(self):
        import_items(self.db, [
            sample(1, title="Oil and filter change", description="", automotive=automotive(
                [vehicle(engine="1.5 dCi")], ["oil_change"], ["lubrication"])),
            sample(2, title="Other oil change", description="", automotive=automotive(
                [vehicle(generation="IV", engine="1.2")], ["oil_change"])),
            sample(3, title="Cabin filter replacement", description="", automotive=automotive(
                [vehicle("Volkswagen", "Golf", "V")], ["cabin_filter"])),
        ], strict=True)
        for query in ["comment faire une vidange Clio 3", "oil change Clio III", "cambio de aceite Clio 3"]:
            result = search(self.db, {"q": query})
            self.assertEqual(result["total"], 1, query)
            self.assertEqual(result["inferred_vehicle"]["generation"], "III")
            self.assertEqual(result["search_mode"], "structured")
        result = search(self.db, {"q": "vidange Clio 3 1.5dCi"})
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["inferred_vehicle"]["engine"], "1.5 dCi")
        self.assertEqual(search(self.db, {"q": "vidange Clio 3 ZX99unmentioned"})["total"], 0)
        self.assertEqual(search(self.db, {"q": "filtre habitacle Golf 5"})["total"], 1)
        conflict = search(self.db, {"q": "vidange Clio 3", "generation": "IV"})
        self.assertEqual(conflict["total"], 0)
        self.assertEqual(conflict["interpretation_conflicts"][0]["field"], "generation")

    def test_automotive_enrichment_is_idempotent_and_preserved_during_refresh(self):
        import_items(self.db, [sample(1, review_status="editorial_selection")], strict=True)
        payload = {"sample_1": automotive([vehicle()], ["oil_change"], ["lubrication"])}
        self.assertEqual(import_automotive_enrichment(self.db, payload)["updated"], 1)
        self.assertEqual(import_automotive_enrichment(self.db, payload)["updated"], 1)
        import_items(self.db, [sample(1, review_status="candidate")], strict=True)
        self.assertEqual(search(self.db, {"model": "Clio", "task": "oil_change"})["total"], 1)
        self.assertEqual(stats(self.db)["with_vehicle_mentions"], 1)
        with connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM video_vehicles").fetchone()[0], 1)
        bad = {"sample_1": automotive([vehicle(year_from=2010, year_to=2000)])}
        self.assertEqual(len(import_automotive_enrichment(self.db, bad)["rejected"]), 1)
        self.assertEqual(search(self.db, {"model": "Clio"})["total"], 1)

    def test_unindexed_explicit_generation_or_engine_never_becomes_loose_full_text(self):
        import_items(self.db, [sample(1, title="Clio III tutorial in 7 steps 1.8 dCi",
                                      automotive=automotive([vehicle()], ["oil_change"]))], strict=True)
        generation = search(self.db, {"q": "vidange Clio 7"})
        self.assertEqual(generation["total"], 0)
        self.assertEqual(generation["inferred_vehicle"]["generation"], "VII")
        engine = search(self.db, {"q": "vidange Clio 3 1.8 dCi"})
        self.assertEqual(engine["total"], 0)
        self.assertEqual(engine["inferred_vehicle"]["engine"], "1.8 DCI")

    def seed_discovery(self):
        spec = lambda value: [{"kind": "oil_viscosity", "value": value, "evidence": "TEST ONLY " + value,
                               "status": "title_mention"}]
        import_items(self.db, [
            sample(1, title="Vidange huile tutoriel", category="mechanics", review_status="editorial_selection",
                   automotive=automotive([vehicle()], ["oil_change", "oil_spec"], specs=spec("5W-30"))),
            sample(2, title="Vidange huile autre véhicule", category="mechanics",
                   automotive=automotive([vehicle("Peugeot", "308", "II")], ["oil_change", "oil_spec"], specs=spec("5W-40"))),
            sample(3, title="Freinage débutant", category="driving"),
        ], strict=True)

    def test_discovery_counts_and_expiring_qualified_shelves(self):
        self.seed_discovery()
        config = discovery_fixture()
        now = dt.datetime(2026, 10, 20, tzinfo=dt.timezone.utc)
        result = discovery(self.db, {}, config=config, now=now)
        self.assertEqual({x["id"]: x["count"] for x in result["topics"]},
                         {"oil-change": 2, "oil-grade": 2, "braking": 1})
        self.assertEqual([x["video"]["id"] for x in result["shelves"][0]["items"]], ["sample_1"])
        self.assertEqual(discovery(self.db, {"make": "Peugeot"}, config=config, now=now)["shelves"], [])
        self.assertEqual(discovery(self.db, {"ids": "sample_2"}, config=config, now=now)["shelves"], [])
        self.assertEqual(discovery(self.db, {}, config=config,
                                   now=dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc))["shelves"], [])
        disabled = copy.deepcopy(config)
        disabled["shelves"][0]["enabled"] = False
        self.assertEqual(discovery(self.db, {}, config=disabled, now=now)["shelves"], [])

    def test_suggestions_are_real_bounded_multilingual_and_keep_specs(self):
        self.seed_discovery()
        config = discovery_fixture()
        defaults = suggestions(self.db, {}, config=config)["suggestions"]
        self.assertEqual([item["id"] for item in defaults[:2]], ["braking", "oil-change"])
        for q in ["vidan", "oil", "aceit"]:
            result = suggestions(self.db, {"q": q}, config=config)
            self.assertLessEqual(len(result["suggestions"]), 6)
            self.assertTrue(any(item["type"] == "topic" for item in result["suggestions"]))
            for item in result["suggestions"]:
                if item["type"] == "video":
                    self.assertEqual(get_video(self.db, item["video_id"])["title"], item["label"])
        result = suggestions(self.db, {"q": "huile 5W30"}, config=config)
        self.assertEqual(result["context"]["spec"], "5W-30")
        self.assertTrue(result["suggestions"])
        self.assertTrue(all(item["filters"]["spec"] == "5W-30" for item in result["suggestions"]))
        self.assertEqual(suggestions(self.db, {"q": "x"}, config=config)["suggestions"], [])
        self.assertEqual(suggestions(self.db, {"q": "Clio", "make": "Peugeot"}, config=config)["suggestions"], [])

    def test_video_suggestions_preserve_catalog_source_and_language_evidence(self):
        import_items(self.db, [
            sample(1, title="MetadataProbe A", creator="Atelier Électricité & diagnostic",
                   platform="youtube", language="fr-FR", language_status="platform_metadata"),
            sample(2, title="MetadataProbe B", creator="Mécanique source", platform="instagram",
                   language="fr", language_status="inferred_from_public_caption"),
            sample(3, title="MetadataProbe C", creator="", platform="tiktok",
                   language="fr", language_status="inferred_from_discovery_query"),
        ], strict=True)
        params = {"q": "MetadataProbe", "format": "video"}
        found = suggestions(self.db, params, config={"topics": []})["suggestions"]
        expected = search(self.db, {**params, "sort": "title", "per_page": "6"})["items"]
        self.assertEqual([item["id"] for item in found], [item["id"] for item in expected])
        self.assertEqual(len(found), 3)
        fields = ("creator", "platform", "language", "language_status", "language_confidence")
        for suggestion, item in zip(found, expected):
            self.assertEqual(suggestion["type"], "video")
            self.assertEqual({key: suggestion[key] for key in fields}, {key: item[key] for key in fields})
            self.assertNotIn("metadata_json", suggestion)
        self.assertEqual([item["language_confidence"] for item in found],
                         ["platform_declared", "estimated", "unknown"])
        self.assertEqual(found[2]["language"], "und")
        self.assertEqual(found[2]["creator"], "")

    def test_recommendations_preserve_vehicle_and_skip_identical_routes(self):
        self.seed_discovery()
        config = discovery_fixture()
        result = recommendations(self.db, {"q": "unknownword Clio 3"}, config=config)
        self.assertTrue(result["topics"])
        for topic in result["topics"]:
            self.assertEqual(topic["filters"]["make"], "Renault")
            self.assertEqual(topic["filters"]["generation"], "III")
            self.assertEqual(topic["count"], 1)
            self.assertEqual(topic["match_basis"], "context_filters")
        same = recommendations(self.db, {"task": "oil_change"}, config=config)
        self.assertNotIn("oil-change", [topic["id"] for topic in same["topics"]])
        defaults = recommendations(self.db, {"q": "nonsense"}, config=config)
        self.assertGreaterEqual(len({topic["intentId"] for topic in defaults["topics"][:2]}), 2)
        contradictory = recommendations(self.db, {"q": "Clio 3", "generation": "IV"}, config=config)
        self.assertEqual(contradictory["topics"], [])
        self.assertEqual(contradictory["shelves"], [])
        focused = recommendations(self.db, {"q": "freinage"}, config=config)
        self.assertEqual([topic["id"] for topic in focused["topics"]], ["braking"])
        empty_precise = recommendations(self.db, {"q": "freinage", "spec": "5W30"}, config=config)
        self.assertEqual(empty_precise["topics"], [])

    def test_predictions_complete_only_topic_words_and_preserve_the_whole_question(self):
        self.seed_discovery()
        import_items(self.db, [sample(10, title="Vidange Clio III 1.5 dCi 2008 huile 5W30",
            category="mechanics", automotive=automotive(
                [vehicle(engine="1.5 dCi", year_from=2008, year_to=2008)], ["oil_change"],
                specs=[{"kind": "oil_viscosity", "value": "5W-30", "evidence": "5W30",
                        "status": "title_mention"}]))], strict=True)
        config = discovery_fixture()
        query = "Comment faire une vidan Clio 3 1.5 dCi 2008 avec 5W30 ?"
        result = suggestions(self.db, {"q": query, "language": "fr"}, config=config)
        topic = next(item for item in result["suggestions"] if item["id"] == "oil-change")
        self.assertEqual(topic["completion"], query.replace("vidan", "vidange"))
        self.assertEqual(topic["query"], topic["completion"])
        self.assertEqual(topic["match_basis"], "prefix_completion")
        self.assertEqual(topic["corrections"], [{"from": "vidan", "to": "vidange", "kind": "prefix"}])
        self.assertIsNone(topic["correction"])
        self.assertEqual(topic["filters"]["engine"], "1.5 dCi")
        self.assertEqual(topic["filters"]["spec"], "5W-30")
        self.assertEqual(topic["filters"]["language"], "fr")
        self.assertEqual(topic["count"], 1)
        self.assertEqual(search(self.db, {**topic["filters"], "q": topic["query"]})["total"], topic["count"])
        for suffix in ("Cliio 3", "Clio 3 1.8 dCi", "Clio 3 5W3O", "Clio 3 2099"):
            self.assertEqual(suggestions(self.db, {"q": "vidan " + suffix}, config=config)["suggestions"], [],
                             "A precise unsupported identifier must not be corrected or dropped: " + suffix)

    def test_predictions_label_a_single_topical_typo_and_rank_multiword_intent(self):
        self.seed_discovery()
        config = discovery_fixture()
        query = "comment faire une vidnage Clio 3 ?"
        result = suggestions(self.db, {"q": query}, config=config)
        topic = next(item for item in result["suggestions"] if item["id"] == "oil-change")
        self.assertEqual(topic["query"], query.replace("vidnage", "vidange"))
        self.assertEqual(topic["match_basis"], "topic_typo")
        self.assertEqual(topic["corrections"], [{"from": "vidnage", "to": "vidange", "kind": "typo"}])
        self.assertTrue(topic["correction"]["fr"])
        multiple = suggestions(self.db, {"q": "how to oil cha"}, config=config)["suggestions"]
        self.assertEqual(multiple[0]["id"], "oil-change")
        self.assertEqual(multiple[0]["completion"], "how to oil change")
        self.assertLessEqual(len(multiple), 6)
        self.assertEqual(suggestions(self.db, {"q": query, "task": "wipers"}, config=config)["suggestions"], [])

    def test_prediction_typo_tolerance_never_repairs_a_technical_standard(self):
        import_items(self.db, [sample(1, title="Huile ACEA C3", automotive=automotive(
            tasks=["oil_spec"], specs=[{"kind": "oil_standard", "value": "ACEA C3",
                                      "evidence": "ACEA C3", "status": "title_mention"}]))], strict=True)
        config = discovery_fixture()
        config["topics"][1]["aliases"].append("ACEA")
        self.assertTrue(suggestions(self.db, {"q": "huile ACEA C3"}, config=config)["suggestions"])
        for item in suggestions(self.db, {"q": "huile ace C3"}, config=config)["suggestions"]:
            self.assertEqual(item["query"], "huile ace C3")
            self.assertFalse(item.get("corrections"))
        for query in ("huile aceaa C3", "huile ACEA C4"):
            self.assertEqual(suggestions(self.db, {"q": query}, config=config)["suggestions"], [], query)

    def test_discovery_cache_observes_import_updates_and_obd_stays_precise(self):
        self.seed_discovery()
        config = discovery_fixture()
        initial = discovery(self.db, {}, config=config)["topics"][0]["count"]
        import_items(self.db, [sample(4, automotive=automotive(tasks=["oil_change"])),
                               sample(5, title="OBD scan", automotive=automotive(tasks=["diagnostics"])),
                               sample(6, title="Generic diagnosis", automotive=automotive(tasks=["diagnostics"]))], strict=True)
        self.assertEqual(discovery(self.db, {}, config=config)["topics"][0]["count"], initial + 1)
        self.assertEqual(search(self.db, {"q": "OBD", "task": "diagnostics"})["total"], 1)

    def test_pedagogical_formats_are_independent_from_platform_and_preserved_on_refresh(self):
        formats = ["tutorial_candidate", "telemetry_demonstration", "course_candidate", "training_stream_candidate", "unspecified"]
        import_items(self.db, [sample(i + 1, title="Freinage format " + str(i), content_format=value)
                               for i, value in enumerate(formats)], strict=True)
        for value in ("tutorial", "demonstration", "course", "stream", "unspecified"):
            result = search(self.db, {"q": "freinage", "content_format": value, "platform": "other"})
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["items"][0]["pedagogical_format"], value)
            self.assertEqual(result["facets"]["content_format"], [{"value": value, "count": 1}])
        import_items(self.db, [sample(1, title="Actualisation sans forme pédagogique")], strict=True)
        self.assertEqual(get_video(self.db, "sample_1")["pedagogical_format"], "tutorial")
        self.assertEqual(search(self.db, {"format": "guide"})["total"], 0)
        with self.assertRaises(ValidationError):
            search(self.db, {"content_format": "tutorial; DROP TABLE videos"})

    def test_unified_resources_have_stable_mixed_pagination_and_real_sources(self):
        guides = normalize_guides(guide_fixture())
        import_items(self.db, [sample(i) for i in range(1, 6)], strict=True)
        items = []
        for page in range(1, 5):
            result = search_resources(self.db, {"page": str(page), "per_page": "2", "sort": "title"}, guides=guides)
            self.assertEqual(result["total"], 7)
            self.assertEqual(result["total_images"], 0)
            items.extend(result["items"])
        self.assertEqual(len({(item["resource_type"], item["id"]) for item in items}), 7)
        self.assertEqual([item["resource_type"] for item in items[:2]], ["guide", "guide"])
        self.assertTrue(items[0]["sources"][0]["url"].startswith("https://"))
        self.assertIn("sources", items[0]["guide"])
        self.assertEqual(search_resources(self.db, {"format": "image"}, guides=guides)["items"], [])
        guide_only = search_resources(self.db, {"format": "guide"}, guides=guides)
        self.assertEqual(guide_only["total"], 2)
        self.assertEqual(guide_only["facets"]["platform"], [{"value": "racelink", "count": 2}])

    def test_general_guides_never_satisfy_vehicle_specs_rights_or_video_format(self):
        self.seed_discovery()
        guides = normalize_guides(guide_fixture())
        for params in ({"make": "Renault"}, {"q": "vidange Clio 3"}, {"spec": "5W30"},
                       {"q": "huile 5W30"}, {"content_format": "tutorial"}, {"platform": "youtube"},
                       {"language": "en"}, {"license": "open"}, {"transcript": "available"}):
            self.assertEqual(search_resources(self.db, {**params, "format": "guide"}, guides=guides)["total"], 0, params)
        result = search_resources(self.db, {"format": "guide", "q": "how to change oil"}, guides=guides)
        self.assertEqual([item["id"] for item in result["items"]], ["guide-oil"])
        self.assertFalse(result["items"][0]["compatibility_verified"])
        invalid = guide_fixture()
        invalid["guides"][0]["sources"][0]["url"] = "http://127.0.0.1/private"
        self.assertEqual(len(normalize_guides(invalid)), 1)

    def test_guide_suggestions_and_topic_routes_preserve_resource_constraints(self):
        self.seed_discovery()
        config = discovery_fixture()
        config["_guides"] = normalize_guides(guide_fixture())
        result = suggestions(self.db, {"q": "vidange", "format": "guide", "platform": "racelink"}, config=config)
        self.assertTrue(any(item["type"] == "guide" for item in result["suggestions"]))
        self.assertFalse(any(item["type"] == "video" for item in result["suggestions"]))
        for item in result["suggestions"]:
            self.assertEqual(item["filters"]["format"], "guide")
            self.assertEqual(item["filters"]["platform"], "racelink")
        topic = next(item for item in result["suggestions"] if item["type"] == "topic")
        self.assertEqual(topic["count"], 1)


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.db = initialize(root / "test.sqlite3")
        import_items(cls.db, [sample(1)])
        cls.public = root / "public"
        cls.public.mkdir()
        (cls.public / "index.html").write_text("<h1>TEST ONLY</h1>", encoding="utf-8")
        (root / "secret.txt").write_text("PRIVATE TEST SENTINEL", encoding="utf-8")
        (cls.public / "vehicle-guides.json").write_text(json.dumps(guide_fixture()), encoding="utf-8")
        cls.server = make_server(cls.db, port=0, public_path=cls.public)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cleanup_temp(cls.temp)

    def request(self, path, method="GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        conn.request(method, path)
        response = conn.getresponse()
        result = response.status, response.read(), dict(response.getheaders())
        conn.close()
        return result

    def test_routes_and_integration_prefix(self):
        for route in ["/", "/aide", "/aide/", "/api/videos", "/aide/api/videos",
                      "/api/videos/sample_1", "/api/stats", "/api/health",
                      "/api/vehicle-options", "/aide/api/vehicle-options",
                      "/api/discovery", "/api/suggestions", "/aide/api/recommendations",
                      "/api/resources", "/aide/api/resources?format=guide", "/api/resources/guide/guide-oil"]:
            self.assertEqual(self.request(route)[0], 200, route)
        self.assertEqual(self.request("/api/videos/missing")[0], 404)
        self.assertEqual(self.request("/api/resources/guide/missing")[0], 404)
        resource = json.loads(self.request("/api/resources/guide/guide-oil")[1])["resource"]
        self.assertEqual(resource["guide"]["steps"], ["Lire la notice."])
        self.assertEqual(resource["resource_type"], "guide")
        self.assertEqual(self.request("/api/undefined")[0], 404)
        self.assertEqual(self.request("/api/videos", "POST")[0], 405)

    def test_traversal_and_server_files(self):
        for route in ["/../secret.txt", "/%2e%2e/secret.txt", "/aide/../secret.txt",
                      "/%5c..%5csecret.txt", "/server.py", "/schema.sql",
                      "/%00", "/data/catalog.sqlite3"]:
            status, data, headers = self.request(route)
            self.assertIn(status, {400, 403, 404}, route)
            self.assertNotIn(b"PRIVATE TEST SENTINEL", data)

    def test_head_and_api_validation(self):
        status, data, headers = self.request("/api/videos", "HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(data, b"")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(self.request("/api/videos?page=-1")[0], 400)
        self.assertEqual(self.request("/api/videos?" + "&".join(f"x{i}=1" for i in range(40)))[0], 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
