"""All mutable fixtures and databases are temporary; no live network requests."""
from contextlib import closing
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from scripts.bulk_ingest import (ApifyReader, NoRedirect, adapt, apply_prepared, atomic_json,
    fetch_apify, file_digest, identity, prepare, project_source, source_rows)
from scripts.review_social_batch import review_batch
from server import ValidationError, import_items, initialize, normalize_item, serialize_video


def cleanup_temporary(temporary):
    # Windows scanners may briefly hold freshly written SQLite/JSON files after
    # all Python handles are closed. Retry only these transient removal errors.
    for attempt in range(4):
        try:
            temporary.cleanup()
            return
        except OSError as exc:
            if getattr(exc, "winerror", None) not in {32, 145} or attempt == 3:
                raise
            time.sleep(.05 * 2 ** attempt)


def youtube(number=1, **extra):
    return {"id": f"fixture{number:04}", "title": "How to replace car wipers — synthetic fixture",
            "channel": "Test author", "language": "fr-FR", **extra}


def tiktok(**extra):
    return {"id": "1234567890123456789", "webVideoUrl": "https://www.tiktok.com/@garage/video/1234567890123456789?utm_source=fixture",
            "text": "Comment changer les essuie-glaces de sa voiture — synthetic fixture",
            "textLanguage": "fr", "authorMeta": {"name": "garage", "nickName": "Garage test", "privateAccount": False},
            "videoMeta": {"duration": 42.8, "subtitleLinks": [{"downloadLink": "https://example.test/not-fetched"}]},
            "isSlideshow": False, "isAd": False, **extra}


def instagram(**extra):
    return {"id": "987654321000", "shortCode": "Fixture001", "url": "https://www.instagram.com/reel/Fixture001/?igshid=fixture",
            "caption": "Tutoriel : changer les essuie-glaces de voiture — synthetic fixture",
            "ownerUsername": "garage_test", "ownerFullName": "Garage test", "type": "Video", "productType": "clips",
            "paidPartnership": False, "videoDuration": 19.3, **extra}


class MappingTests(unittest.TestCase):
    def test_social_display_cleanup_runs_after_source_classification(self):
        caption="Comment changer les essuie-glaces ? Renault Clio III 1.5 dCi. #Auto #Wipers"
        raw=tiktok(text=caption, _collection={"provider":"yt-dlp","evidence_scope":"public_video_metadata"})
        record,decision=adapt(raw)
        self.assertEqual(record["title"],"Comment changer les essuie-glaces ?")
        self.assertEqual(decision["status"],"candidate")
        self.assertIn("wipers",record["automotive"]["tasks"])
        self.assertTrue(any(v["make"]=="Renault" and v["model"]=="Clio" for v in record["automotive"]["vehicles"]))
        self.assertEqual(record["social_content"]["original_caption"],caption)
        self.assertEqual(record["social_content"]["source_metadata"]["import_source_fields"]["text"],caption)
        self.assertFalse(record["audio_language_verified"])

    def test_social_exact_source_whitespace_and_search_hashtags_survive(self):
        caption="Tutoriel essuie-glaces.\n\n  #Auto\t#école #e\u0301cole #fypシ゚viral"
        record,_=adapt(instagram(caption=caption,tags=["mécanique","#AUTO"]))
        social=record["social_content"]
        self.assertEqual(social["original_caption"],caption)
        self.assertEqual(social["original_caption_status"],"exported_direct_caption_not_independently_verified")
        self.assertEqual(record["tags"],["mécanique","#AUTO","#école","#fypシ゚viral"])
        self.assertEqual(social["original_search_tags"],["mécanique","#AUTO"])
        self.assertEqual(social["added_search_hashtags"],["#école","#fypシ゚viral"])

    def test_social_editorial_summary_is_preserved_and_not_claimed_as_caption(self):
        caption="How to replace car wipers. #Wipers"
        record,_=adapt(instagram(caption=caption,description="Le titre explique une méthode &amp; ses étapes.",
                                descriptionType="editorial_summary"))
        self.assertEqual(record["description"],"Le titre explique une méthode & ses étapes.")
        self.assertEqual(record["social_content"]["original_caption"],caption)
        self.assertEqual(record["descriptionType"],"existing_editorial_description")
        self.assertEqual(record["social_content"]["hashtags"],["#Wipers"])
        raw=instagram(description="Note interne à vérifier.",description_basis="editorial_summary",title="How to replace car wipers")
        del raw["caption"]
        record,_=adapt(raw)
        self.assertEqual(record["social_content"]["original_caption"],"")

    def test_social_provisional_title_remains_nonempty(self):
        record,_=adapt(instagram(caption="Tutoriel changer les essuie-glaces de voiture #Auto"))
        self.assertEqual(record["title"],"Tutoriel changer les essuie-glaces de voiture")
        self.assertTrue(record["social_content"]["needs_title_review"])
        self.assertEqual(record["social_content"]["title_basis"],"source_cleanup")

    def test_social_source_contract_is_already_exposed_by_serializer(self):
        caption="Tutoriel remplacer les essuie-glaces. #Auto"
        record,_=adapt(instagram(caption=caption))
        public=serialize_video(normalize_item(record))
        self.assertEqual(public["hashtags"],["#Auto"])
        self.assertEqual(public["source_caption"],caption)
        self.assertEqual(public["source_title"],caption)
        self.assertEqual(public["description_type"],"source_caption_without_social_tokens")

    def test_social_cleanup_does_not_reclassify_promotion_or_other_platforms(self):
        raw=instagram(caption="How to replace car wipers? #Auto BUY NOW using promo code EXAMPLE")
        record,decision=adapt(raw)
        self.assertEqual(decision["status"],"quarantine")
        self.assertEqual(record["title"],"How to replace car wipers?")
        youtube_title="How to replace car wipers #Auto &amp; maintenance"
        record,_=adapt(youtube(title=youtube_title))
        self.assertEqual(record["title"],youtube_title)
        self.assertNotIn("social_content",record)

    def test_index_body_is_only_fingerprinted_never_imported_as_nested_audit(self):
        raw=instagram(title="Tutoriel remplacer les essuie-glaces #Auto",caption="Other user comment #Peugeot",
                      _collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"})
        record,_=adapt(raw)
        social=record["social_content"]
        self.assertEqual(social["original_caption"],"")
        self.assertEqual(social["hashtags"],["#Auto"])
        self.assertNotIn("Other user comment",json.dumps(record))
        self.assertTrue(social["normalization"]["excluded_index_body_sha256"])

    def test_live_clockworks_shape_is_metadata_only(self):
        raw = tiktok(api_token="fake-secret", transcript={"text": "Not authorized"},
            comments=[{"text": "Personal comment", "username": "hidden"}], license="creative-commons")
        record, decision = adapt(raw)
        self.assertEqual(record["id"], "tiktok:1234567890123456789")
        self.assertNotIn("?", record["url"])
        self.assertEqual(record["creator"], "Garage test")
        self.assertEqual(record["duration_seconds"], 42)
        self.assertEqual(record["language_status"], "inferred_from_exported_caption_language")
        self.assertEqual(record["language_evidence"]["field"], "textLanguage")
        self.assertFalse(record["audio_language_verified"])
        self.assertEqual(record["license"], "unknown")
        self.assertFalse(record["transcriptImported"])
        self.assertNotIn("transcript", record)
        encoded = json.dumps(record)
        for value in ("fake-secret", "Personal comment", "Not authorized", "downloadLink"):
            self.assertNotIn(value, encoded)
        self.assertEqual(decision["status"], "candidate")

    def test_instagram_reel_and_scraper_shapes(self):
        record, _ = adapt(instagram())
        self.assertEqual(record["language"], "fr")
        self.assertEqual(record["language_status"], "inferred_from_source_text")
        self.assertEqual(record["id"], "instagram:Fixture001")
        fallback = instagram()
        del fallback["url"]
        record, _ = adapt(fallback, "apify-instagram")
        self.assertEqual(record["url"], "https://instagram.com/p/Fixture001")
        no_shortcode = {k:v for k,v in fallback.items() if k != "shortCode"}
        with self.assertRaises(ValidationError):
            adapt(no_shortcode, "apify-instagram")

    def test_ytdlp_full_and_flat_do_not_guess_language(self):
        full, _ = adapt(youtube(), "yt-dlp")
        self.assertEqual(full["language"], "fr-fr")
        self.assertEqual(full["language_status"], "platform_metadata")
        flat = youtube(language=None, _type="url", ie_key="Youtube")
        unknown, _ = adapt(flat)
        self.assertEqual(unknown["language"], "und")
        queried, _ = adapt(youtube(language_status="inferred_from_discovery_query"))
        self.assertEqual(queried["language"], "und")
        self.assertEqual(queried["language_evidence"]["basis"], "query_language_ignored")
        estimated, _ = adapt(youtube(language_status="estimated_from_public_title"))
        self.assertNotEqual(estimated["language_status"], "platform_metadata")
        unknown, _ = adapt(youtube(language_status="unknown_audio_language"))
        self.assertEqual(unknown["language"], "und")

    def test_car_word_alone_does_not_classify_as_mechanics(self):
        cases = [("Car photography tutorial", "media"),
                 ("How to open a car shop business", "business"),
                 ("How to start a career as a car mechanic", "career"),
                 ("How to replace car wipers", "mechanics")]
        for title, category in cases:
            record, decision = adapt(youtube(title=title))
            self.assertEqual(record["category_slug"], category)
            self.assertEqual(decision["status"], "candidate")
        for title in ("A tutorial about my car", "Photography tutorial", "Business tips",
                      "How to replace battery", "How to replace the iPhone battery"):
            _, decision = adapt(youtube(title=title))
            self.assertEqual(decision["status"], "quarantine")

    def test_specific_maintenance_vocabulary_with_vehicle_context_is_recognized(self):
        titles = [
            "Comment changer un amortisseur arrière sur la HYUNDAI I30 CW - [TUTORIEL AUTODOC]",
            "Remplacer le roulement de roue d'une voiture",
            "Comment changer la courroie de distribution de votre Renault Clio",
            "How to replace a car cabin filter",
            "Comment purger le liquide de frein de votre voiture",
            "How to replace BMW control arms",
            "Nettoyer les injecteurs de sa voiture",
            "Comment démonter un démarreur de voiture",
            "How to adjust car headlights",
            "Comment réparer la pompe de lave-glace de votre Renault Megane",
        ]
        for title in titles:
            with self.subTest(title=title):
                record,decision=adapt(youtube(title=title,language=None))
                self.assertEqual(decision["status"],"candidate")
                self.assertEqual(record["category_slug"],"mechanics")

    def test_non_automotive_or_ambiguous_components_remain_quarantined(self):
        titles = ["Comment changer un amortisseur de vélo", "How to replace an aircraft wheel",
            "Boeing 787 wheel replacement tutorial", "How to replace a plane tire",
            "Comment changer le filtre de hotte de cuisine", "How to replace a home radiator",
            "Comment changer la rotule du genou", "How to replace a radiator",
            "How to replace an air filter", "How to replace water pump",
            "Comment changer une courroie", "Be the best version of yourself: Citroën BX"]
        for title in titles:
            with self.subTest(title=title):
                _,decision=adapt(youtube(title=title,language=None))
                self.assertEqual(decision["status"],"quarantine")

    def test_new_component_vocabulary_does_not_override_promotional_flags(self):
        for raw in (
            instagram(caption="Comment changer les amortisseurs de votre voiture #ad"),
            instagram(caption="Remplacer les rotules de voiture - code réduction"),
            tiktok(text="Comment purger les freins de votre voiture",isSponsored=True),
            youtube(title="Comment changer les filtres de sa voiture",description="Lien en bio"),
        ):
            with self.subTest(raw=raw):
                _,decision=adapt(raw)
                self.assertIn("promotional_or_sponsored_metadata",decision["reasons"])

    def test_hashtags_do_not_establish_a_vehicle_lesson_or_french_language(self):
        record,decision=adapt(instagram(caption="Comment purger les freins de votre voiture #Renault #Clio3 #BMW"))
        self.assertEqual(decision["status"],"candidate")
        self.assertEqual(record["automotive"]["vehicles"],[])
        _,decision=adapt(instagram(caption="A beautiful day #tutorial #engine #Renault"))
        self.assertEqual(decision["status"],"quarantine")
        record,_=adapt(instagram(caption="How to replace car wipers #francais #comment #changer #voiture"))
        self.assertEqual(record["language"],"und")

    def test_french_estimate_uses_only_source_text_and_retains_index_scope(self):
        collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata",
                    "source":"French tutorials Renault Clio","job_kind":"exa_search"}
        record,decision=adapt(instagram(caption="Comment changer les essuie-glaces de votre voiture",
                                       _collection=collection))
        self.assertEqual(record["language"],"fr")
        self.assertEqual(record["language_status"],"inferred_from_indexed_source_text")
        self.assertEqual(record["verification_scope"],"indexed_search_metadata")
        self.assertFalse(record["language_evidence"]["search_query_used"])
        self.assertFalse(record["audio_language_verified"])
        self.assertEqual(record["review_status"],"candidate")
        self.assertIsNone(record["verified_at"])
        self.assertNotIn("Renault",record["language_evidence"]["excerpt"])
        for caption in ("How to replace your car wipers", "Moteur", "La voiture",
                        "Comment changer les essuie-glaces: how to replace your car wipers"):
            record,_=adapt(instagram(caption=caption,language="fr",_collection=collection))
            self.assertEqual(record["language"],"und",caption)

    def test_video_language_declaration_is_not_replaced_by_french_caption_estimate(self):
        record,_=adapt(youtube(title="Comment changer les essuie-glaces de votre voiture",language="en"))
        self.assertEqual(record["language"],"en")
        self.assertEqual(record["language_status"],"platform_metadata")

    def test_index_comments_related_posts_and_navigation_cannot_qualify_target(self):
        collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}
        record,decision=adapt(instagram(title="A quick clip | Instagram",
            caption="A quick clip\n\n18 comments\nComment changer les essuie-glaces de votre Renault Clio",
            _collection=collection))
        self.assertEqual(decision["status"],"quarantine")
        self.assertEqual(record["language"],"und")
        self.assertEqual(record["automotive"]["vehicles"],[])
        self.assertNotIn("Renault",record["description"])
        self.assertEqual(record["description_basis"],"indexed_title_only_no_verified_caption")
        self.assertEqual(record["description"],"")
        record,decision=adapt(tiktok(title="VW Golf Wiper Blade Replacement Tutorial | TikTok",
            text="VW Golf Wiper Blade Replacement Tutorial\n\n...\n\nComment changer les filtres de votre Audi Q3",
            _collection=collection))
        self.assertEqual(decision["status"],"candidate")
        self.assertEqual(record["language"],"und")
        self.assertNotIn("Audi",record["description"])
        self.assertTrue(all(v["model"] != "Q3" for v in record["automotive"]["vehicles"]))
        record,decision=adapt(tiktok(title="Quick clip",text="Comment changer les essuie-glaces de votre voiture",
                                    _collection=collection))
        self.assertEqual(decision["status"],"quarantine")
        self.assertEqual(record["language"],"und")

    def test_instagram_index_wrapper_preserves_original_and_uses_only_caption_title(self):
        title="Garage Pierre | Comment changer les essuie-glaces de votre voiture #BMW | Instagram"
        record,decision=adapt(instagram(title=title,caption=title,
            _collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}))
        self.assertTrue(record["title"].startswith("Comment changer"))
        self.assertEqual(record["provenance"]["source_index_title"],title)
        self.assertEqual(record["provenance"]["qualification_text"],"indexed_title_only")
        self.assertEqual(record["language"],"fr")
        self.assertEqual(record["automotive"]["vehicles"],[])
        with self.assertRaises(ValidationError):
            adapt(instagram(title="| Instagram",_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}))

    def test_exa_cannot_claim_direct_page_proof_or_keep_a_composite_body(self):
        record,_=adapt(instagram(title="How to replace car wipers",
            caption="Comment changer les filtres de votre Renault Clio. A different recommended video.",
            _collection={"provider":"exa-public-mcp","evidence_scope":"public_video_metadata"}))
        self.assertEqual(record["verification_scope"],"indexed_search_metadata")
        self.assertEqual(record["collection_provenance"]["evidence_scope"],"indexed_search_metadata")
        self.assertEqual(record["language"],"und")
        self.assertEqual(record["description"],"")
        self.assertEqual(record["sourceDescription"],"")
        self.assertTrue(record["provenance"]["index_excerpt_omitted"])
        self.assertNotIn("Renault",json.dumps(record))

    def test_observed_social_name_and_component_homonyms_are_not_lessons(self):
        titles=["L'alternateur | Si tu utilises ChatGPT, écoute ça !!! | Instagram",
            "Garagé Paris | Advice from 33 yo Citroen: Be the best version of you! #citroen #frenchcar | Instagram",
            "Team | Just change the oil in your car and your headlights will run forever | Instagram",
            "Comment faire la vidange de votre chauffe-eau",
            "How to replace a stroller wheel", "How to replace the belt for martial arts",
            "Comment remplacer les bougies parfumées pour la maison", "Purge de la machine à café"]
        for title in titles:
            with self.subTest(title=title):
                _,decision=adapt(instagram(title=title,_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}))
                self.assertEqual(decision["status"],"quarantine")

    def test_real_french_instruction_phrases_are_recognized_as_estimates(self):
        titles=["Voici toute les étapes pour mettre de l’essence à la station essence !",
                "Quel ordre pour brancher ou débrancher une batterie 12V ? #automobile Moyen mnémotechnique",
                "Que signifie ces voyant sur ton tableau de bord ?",
                "Aujourd’hui un remplacement de pusleur d’air sur une Peugeot 307sw",
                "Comment installer CarPlay sur votre autoradio ?"]
        for title in titles:
            with self.subTest(title=title):
                record,decision=adapt(instagram(caption=title,
                    _collection={"provider":"yt-dlp","evidence_scope":"public_video_metadata"}))
                self.assertEqual(decision["status"],"candidate")
                self.assertEqual(record["language"],"fr")
                self.assertEqual(record["language_status"],"inferred_from_source_text")
                self.assertFalse(record["audio_language_verified"])
        record,_=adapt(instagram(title="Vidange moteur",_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}))
        self.assertEqual(record["language"],"fr")
        self.assertEqual(record["language_status"],"inferred_from_indexed_source_text")

    def test_connected_car_phone_exception_is_narrow_and_new_car_question_is_not_a_tour(self):
        for title in ("How do I connect my smartphone to Android Auto in my new Peugeot?",
                      "Comment connecter votre iPhone à CarPlay ?"):
            _,decision=adapt(youtube(title=title))
            self.assertEqual(decision["status"],"candidate")
        for title in ("How to replace the iPhone battery for CarPlay",
                      "How to connect CarPlay: a comparison and my new setup tour",
                      "Comment EV to get your car business guide"):
            _,decision=adapt(youtube(title=title))
            self.assertEqual(decision["status"],"quarantine")
        record,_=adapt(youtube(title="Explication du turbo à géométrie variable et du pilotage pneumatique"))
        self.assertEqual(record["category_slug"],"mechanics")

    def test_observed_technical_explanations_are_not_confused_with_driving_or_physiotherapy(self):
        record,decision=adapt(youtube(title="Comprendre le blocage de la géométrie variable des turbos diesel",
            description="Pilotage : la géométrie variable est pilotée par une commande pneumatique. Les ailettes du turbo bougent."))
        self.assertEqual(record["category_slug"],"mechanics")
        self.assertEqual(decision["status"],"candidate")
        for title,description in (("How to tell when your ignition coils are failing", ""),
            ("If engine oil is exposed to -35 degrees, does it look like grease?", "The viscosity of an oil is measured by its resistance to flow. W stands for Winter.")):
            _,decision=adapt(youtube(title=title,description=description))
            self.assertEqual(decision["status"],"candidate")
        for title in ("Tuto taping du syndrome de l’essuie-glace (SBIT)","E-Bike wheel replacement tutorial"):
            _,decision=adapt(youtube(title=title))
            self.assertIn("out_of_scope_source_context",decision["reasons"])

    def test_observed_direct_location_reverse_and_wear_indicator_questions(self):
        collection={"provider":"yt-dlp","evidence_scope":"public_video_metadata"}
        examples=[
            ("[PRISE OBD2] Où trouver le connecteur OBD2 pour votre Honda Accord VI...",
             "[PRISE OBD2] Où trouver le connecteur OBD2 pour votre Honda Accord VI (1997 - 2002) ?"),
            ("Décourez où se situe la préssion des pneumatiques sur votre véhicule!...",
             "Décourez où se situe la préssion des pneumatiques sur votre véhicule!"),
            ("Comment passer la marche arrière sur boîte manuelle (exemple Skod...",
             "Comment passer la marche arrière sur boîte manuelle (exemple Skoda Fabia 2025)"),
            ("Prochaine fois que tu regarde tes freins, regarde cet indicateur d’usure.",
             "Prochaine fois que tu regarde tes freins, regarde cet indicateur d’usure.")]
        for title,description in examples:
            with self.subTest(title=title):
                item,decision=adapt(tiktok(title=title,text=description,_collection=collection))
                self.assertEqual(decision["status"],"candidate")
                self.assertEqual(item["language"],"fr")
                self.assertFalse(item["audio_language_verified"])
        item,_=adapt(tiktok(title=examples[2][0],text=examples[2][1],_collection=collection))
        self.assertIn("Skoda Fabia 2025",item["title"])
        self.assertTrue(item["provenance"]["title_restored_from_caption"])
        self.assertEqual(item["provenance"]["source_extractor_title"],examples[2][0])
        self.assertEqual(item["provenance"]["mapped_fields"]["title"],"text")

    def test_location_requires_vehicle_context_and_cannot_override_promotions(self):
        for title in ("Where is the fuse in my washing machine?", "Où trouver le filtre de la hotte ?",
                      "Où se situe l'indicateur d'usure de mon vélo ?", "Where is the office?",
                      "Comment passer la marche arrière dans un jeu de plateau"):
            _,decision=adapt(youtube(title=title))
            self.assertEqual(decision["status"],"quarantine")
        for title in ("Where is the OBD2 connector in your vehicle?", "Where to find your car tyre pressure label"):
            _,decision=adapt(youtube(title=title))
            self.assertEqual(decision["status"],"candidate")
        _,decision=adapt(youtube(title="Où trouver la prise OBD2 de votre voiture ? #pub"))
        self.assertIn("promotional_or_sponsored_metadata",decision["reasons"])

    def test_caption_title_restoration_requires_direct_exact_prefix_and_first_line(self):
        title="Comment changer les filtres de votre voiture..."
        direct={"provider":"yt-dlp","evidence_scope":"public_video_metadata"}
        cases=[({"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"},title+" Renault Clio 3"),
               (direct,"Un autre titre\n"+title[:-3]+" Renault Clio 3"),
               (direct,"Comment changer les freins de votre voiture Renault Clio 3")]
        for collection,caption in cases:
            item,_=adapt(tiktok(title=title,text=caption,_collection=collection))
            self.assertEqual(item["title"],title)
            self.assertNotIn("title_restored_from_caption",item["provenance"])
        item,_=adapt(tiktok(title="Tuto...",text="Tuto Renault Clio 3",_collection=direct))
        self.assertEqual(item["title"],"Tuto...")

    def test_specific_french_recovery_questions_keep_vehicle_context(self):
        for title in ("Comment tester un fusible de voiture avec un multimètre", "Comment redémarrer votre voiture avec des câbles de ...",
                      "Comment utiliser la climatisation de votre voiture", "Comment personnaliser l'écran central de sa Peugeot -208 ?",
                      "comment remplir son liquide de lave-glace ...", "Refaire un faisceau électrique voiture : étape par étape",
                      "Comment tester facilement la batterie de sa voiture ?", "Comment tester facilement et rapidement un alternateur ..."):
            _,decision=adapt(instagram(title=title,_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}))
            self.assertEqual(decision["status"],"candidate",title)
        for title in ("Comment tester un fusible", "Comment utiliser la climatisation", "Refaire un faisceau électrique : étape par étape"):
            _,decision=adapt(instagram(title=title,caption="",_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}))
            self.assertEqual(decision["status"],"quarantine",title)

    def test_numeric_durations_do_not_accept_nan_negative_or_unbounded(self):
        for duration in ("NaN", "Infinity", -1, 999999, True, None):
            record, _ = adapt(youtube(duration=duration))
            self.assertIsNone(record["duration_seconds"])

    def test_promo_and_ambiguous_metadata_go_to_quarantine(self):
        cases = [youtube(title="How to replace car wipers: CODE PROMO test"),
                 youtube(title="My new car review"), youtube(title="A beautiful racing car"),
                 youtube(title="How to bake bread"), tiktok(isAd=True),
                 tiktok(hasTikTokShopProduct=True), instagram(paidPartnership=True),
                 youtube(title="How to disable the airbag in your car")]
        for raw in cases:
            with self.subTest(raw=raw):
                _, decision = adapt(raw)
                self.assertEqual(decision["status"], "quarantine")
                self.assertTrue(decision["reasons"])

    def test_non_video_private_and_unsupported_sources_rejected(self):
        cases = [instagram(type="Image"), instagram(type="Sidecar"),
                 tiktok(isSlideshow=True), tiktok(isStory=True),
                 tiktok(authorMeta={"name":"garage", "privateAccount":True}),
                 youtube(availability="private"), youtube(webpage_url="https://127.0.0.1/video"),
                 instagram(url="https://instagram.com/garage_test/"),
                 tiktok(webVideoUrl="https://vm.tiktok.com/shortlink/")]
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                adapt(raw)

    def test_stable_media_identity_ignores_permalink_aliases(self):
        self.assertEqual(identity("https://instagram.com/garage/reel/Fixture001/?igsh=x")[0],
                         identity("https://instagram.com/p/Fixture001/")[0])
        self.assertEqual(identity("https://tiktok.com/@old/video/123456")[0],
                         identity("https://tiktok.com/@new/video/123456")[0])

    def test_caption_excerpt_and_field_provenance_are_bounded(self):
        record, _ = adapt(instagram(caption="Tutoriel voiture " + "texte " * 500))
        self.assertLessEqual(len(record["title"]), 480)
        self.assertEqual(len(record["description"]), 1200)
        self.assertTrue(record["provenance"]["caption_truncated"])
        self.assertTrue(record["provenance"]["title_truncated"])
        self.assertEqual(record["provenance"]["mapped_fields"]["title"], "caption")

    def test_documented_dates_and_signed_image_metadata_survive_mapping(self):
        image_url = "https://cdn.example.org/public-cover.jpg?expires=2099999999&signature=public-cdn-signature"
        cases = [
            (tiktok(createTimeISO="2026-10-20T14:22:05Z", videoMeta={"duration":20,"coverUrl":image_url}), "2026-10-20T14:22:05+00:00", "createTimeISO"),
            (instagram(timestamp="2026-10-20T16:22:05+02:00", displayUrl=image_url), "2026-10-20T16:22:05+02:00", "timestamp"),
            (youtube(upload_date="20261020", thumbnail=image_url), "2026-10-20", "upload_date")]
        for raw, date, field in cases:
            record, _ = adapt(raw)
            self.assertEqual(record["thumbnail_url"], image_url)
            self.assertEqual(record["published_at"], date)
            self.assertEqual(record["provenance"]["mapped_fields"]["published_at"], field)

    def test_thumbnail_fallback_and_invalid_date_do_not_create_false_metadata(self):
        record, _ = adapt(youtube(upload_date="20261399", thumbnails=[{"url":"http://127.0.0.1/cover.jpg"},
            {"url":"https://images.example.org/cover.jpg?signature=public"}]))
        self.assertIsNone(record["published_at"])
        self.assertEqual(record["thumbnail_url"], "https://images.example.org/cover.jpg?signature=public")
        for thumbnail in ("http://127.0.0.1/cover.jpg", "https://secret:password@example.org/cover.jpg",
                          "https://images.example.org/cover.jpg?access_token=secret"):
            record, _ = adapt(youtube(thumbnail=thumbnail, timestamp=1792506125))
            self.assertIsNone(record["thumbnail_url"])
            self.assertTrue(record["published_at"].endswith("+00:00"))


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="focus-bulk-test-")
        self.addCleanup(cleanup_temporary, self.tmp)
        self.root = Path(self.tmp.name)
        self.db = self.root / "test.sqlite3"
        initialize(self.db)

    def source(self, records, filename="source.json"):
        path = self.root / filename
        if filename.endswith("jsonl"):
            path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        else:
            atomic_json(path, records)
        return path

    def approval(self, output, ids):
        data = json.loads((output / "approval.template.json").read_text(encoding="utf-8"))
        data.update(approved_ids=ids, reviewer="Fixture reviewer", reason="Synthetic test only")
        path = self.root / "approval.json"
        atomic_json(path, data)
        return path

    def test_nested_json_jsonl_and_profile_listings(self):
        source = self.source({"entries":[youtube(1), youtube(2)]})
        self.assertEqual(len(list(source_rows(source))), 2)
        self.assertEqual(len(list(source_rows(self.source([youtube(3), youtube(4)], "source.jsonl")))), 2)
        source = self.source({"latestPosts":[instagram()], "latestIgtvVideos":[instagram(shortCode="Fixture002")], "private":True})
        rows = list(source_rows(source))
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["isPrivate"] for row in rows))

    def test_prepare_never_writes_database_and_deduplicates(self):
        before = file_digest(self.db)
        src = self.source([instagram(), instagram(url="https://instagram.com/p/Fixture001/")])
        output = self.root / "prepared"
        result = prepare([src], output, db=self.db)
        self.assertEqual(result["accepted_candidates"], 1)
        self.assertEqual(result["duplicates_in_batch"], 1)
        self.assertEqual(result["new_media_candidates"], 1)
        self.assertEqual(file_digest(self.db), before)
        self.assertEqual(json.loads((output/"approval.template.json").read_text())["approved_ids"], [])

    def test_duplicate_promotion_cannot_hide_behind_clean_variant(self):
        src = self.source([instagram(), instagram(paidPartnership=True)])
        result = prepare([src], self.root/"prepared", db=self.db)
        self.assertEqual(result["accepted_candidates"], 0)
        self.assertEqual(result["quarantined"], 1)

    def test_direct_provenance_wins_index_excerpt_and_all_collection_proofs_survive(self):
        indexed=instagram(caption="Comment changer les essuie-glaces de votre voiture. "+"Texte de source. "*40,
            _collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata","source":"query"})
        direct=instagram(caption="Comment changer les essuie-glaces de votre voiture",
            _collection={"provider":"yt-dlp","evidence_scope":"public_video_metadata","source":"public URL"})
        output=self.root/"prepared"
        prepare([self.source([indexed,direct])],output,db=None)
        records=json.loads((output/"accepted.json").read_text(encoding="utf-8"))
        self.assertEqual(records[0]["verification_scope"],"public_video_metadata")
        self.assertEqual({entry["collection"]["evidence_scope"] for entry in records[0]["bulk_sources"]},
                         {"public_video_metadata","indexed_search_metadata"})
        report=json.loads((output/"report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["database_compared"])
        self.assertIsNone(report["new_media_candidates"])

    def test_qualified_direct_source_lifts_only_missing_index_evidence(self):
        indexed=instagram(title="A quick clip",caption="Unverified search excerpt",
            _collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"})
        direct=instagram(caption="Comment changer les essuie-glaces de votre voiture",
            _collection={"provider":"yt-dlp","evidence_scope":"public_video_metadata"})
        output=self.root/"prepared"
        result=prepare([self.source([indexed,direct])],output,db=None)
        self.assertEqual(result["accepted_candidates"],1)
        self.assertEqual(result["duplicates_in_batch"],1)
        record=json.loads((output/"accepted.json").read_text(encoding="utf-8"))[0]
        self.assertEqual(record["verification_scope"],"public_video_metadata")
        self.assertEqual({r["reason"] for r in record["bulk_reconciliation"]["ignored_missing_evidence"]},
                         {"no_explicit_learning_signal","no_supported_automotive_or_motorsport_topic"})

    def test_qualified_index_title_resolves_generic_variant_without_promoting_its_scope(self):
        provenance={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}
        generic=instagram(title="A quick clip",_collection=provenance)
        informative=instagram(title="Comment tester la batterie de sa voiture",_collection=provenance)
        output=self.root/"indexed"
        result=prepare([self.source([generic,informative])],output,db=None)
        self.assertEqual(result["accepted_candidates"],1)
        record=json.loads((output/"accepted.json").read_text(encoding="utf-8"))[0]
        self.assertEqual(record["title"],informative["title"])
        self.assertEqual(record["bulk_qualification"]["status"],"candidate")
        self.assertEqual(record["verification_scope"],"indexed_search_metadata")
        self.assertEqual(record["bulk_reconciliation"]["basis"],"qualified_index_title_over_index_missing_evidence")
        self.assertIsNone(record["verified_at"])
        for number,negative in enumerate((instagram(title="How to replace car wipers #ad",_collection=provenance),
                instagram(title="Boeing aircraft wheel replacement tutorial",_collection=provenance),
                instagram(isPrivate=True), instagram(title="A quick clip",caption="Just a clip",
                    _collection={"provider":"yt-dlp","evidence_scope":"public_video_metadata"}))):
            result=prepare([self.source([informative,negative],f"index-negative-{number}.json")],self.root/f"index-negative-{number}",db=None)
            self.assertEqual(result["accepted_candidates"],0)

    def test_direct_source_never_erases_explicit_index_or_source_negative(self):
        direct=instagram(caption="Comment changer les essuie-glaces de votre voiture",
            _collection={"provider":"yt-dlp","evidence_scope":"public_video_metadata"})
        negatives=[
            instagram(title="How to replace car wipers #ad",_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}),
            instagram(title="How to disable the airbag in your car",_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}),
            instagram(title="Boeing aircraft wheel replacement tutorial",_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}),
            instagram(title="My new car review",_collection={"provider":"exa-public-mcp","evidence_scope":"indexed_search_metadata"}),
            instagram(isPrivate=True), instagram(type="Image")]
        for number,negative in enumerate(negatives):
            with self.subTest(number=number):
                result=prepare([self.source([negative,direct],f"negative-{number}.json")],self.root/f"negative-{number}",db=None)
                self.assertEqual(result["accepted_candidates"],0)
                self.assertEqual(result["quarantined"],1)
                self.assertEqual(result["duplicates_in_batch"],1)

    def test_private_variants_share_identity_even_without_a_clean_variant(self):
        result=prepare([self.source([instagram(isPrivate=True),instagram(isPrivate=True)])],self.root/"prepared",db=None)
        self.assertEqual(result["quarantined"],1)
        self.assertEqual(result["duplicates_in_batch"],1)

    def test_regional_variants_of_same_declared_language_do_not_conflict(self):
        result=prepare([self.source([youtube(language="fr"),youtube(language="fr-FR")])],self.root/"prepared",db=None)
        self.assertEqual(result["accepted_candidates"],1)

    def test_review_batches_are_bounded_deterministic_and_never_approve(self):
        output=self.root/"prepared"
        rows=[youtube(n,title="Comment changer le filtre à huile de votre voiture",language=None,channel="=HYPERLINK(test)") for n in range(1,14)]
        rows += [youtube(20,title="Comment changer le filtre à huile de voiture #ad")]
        prepare([self.source(rows)],output,db=None)
        first=self.root/"review1"
        result=review_batch(output,first,batch_size=10)
        self.assertEqual(result["candidate_count"],13)
        self.assertEqual(result["quarantine_count"],1)
        self.assertEqual(result["approved_count"],0)
        second=self.root/"review2"
        review_batch(output,second,batch_size=10)
        a=json.loads((first/"review-batches.json").read_text())
        b=json.loads((second/"review-batches.json").read_text())
        self.assertEqual(a["batches"],b["batches"])
        self.assertEqual([len(batch["candidate_ids"]) for batch in a["batches"]],[10,3])
        self.assertEqual([len(batch["source_sample_ids"]) for batch in a["batches"]],[5,3])
        self.assertTrue(all(batch["approved_ids"] == [] for batch in a["batches"]))
        ids=json.loads((first/"candidate-ids.json").read_text())
        self.assertNotIn("youtube:fixture0020",ids)
        self.assertEqual(len(json.loads((first/"french-candidate-ids.json").read_text())),13)
        self.assertIn("'=HYPERLINK(test)",(first/"candidates-review.csv").read_text(encoding="utf-8-sig"))
        self.assertEqual(json.loads((output/"approval.template.json").read_text())["approved_ids"],[])

    def test_review_refuses_changed_quarantine_evidence_or_invalid_bounds(self):
        output=self.root/"prepared"
        prepare([self.source([youtube()])],output,db=None)
        with self.assertRaises(ValidationError):
            review_batch(output,self.root/"review",batch_size=251)
        (output/"quarantine.jsonl").write_text("{}\n")
        with self.assertRaises(ValidationError):
            review_batch(output,self.root/"review")

    def test_jsonl_review_preserves_unicode_line_separator_inside_caption(self):
        output=self.root/"prepared"
        source=self.source([youtube(title="Comment changer les essuie-glaces",description="Caption\u2028suite\u2029fin #ad")])
        prepare([source],output,db=None)
        self.assertIn("\u2028",(output/"quarantine.jsonl").read_text(encoding="utf-8"))
        result=review_batch(output,self.root/"review")
        self.assertEqual(result["quarantine_count"],1)
        self.assertEqual(result["approved_count"],0)

    def test_conflicting_language_proofs_quarantine_same_identity(self):
        src = self.source([youtube(language="fr"), youtube(language="en")])
        result = prepare([src], self.root/"prepared", db=self.db)
        self.assertEqual(result["accepted_candidates"], 0)
        self.assertEqual(result["quarantined"], 1)

    def test_bounds_are_reported_and_invalid_json_stops_preparation(self):
        src = self.source([youtube(1), youtube(2)])
        result = prepare([src], self.root/"prepared", db=self.db, max_items=1)
        self.assertTrue(result["truncated_at_bound"])
        self.assertEqual(result["source_records"], 1)
        bad = self.root/"bad.jsonl"
        bad.write_text('{"id":"test"}\nnot JSON\n')
        with self.assertRaises(ValidationError):
            prepare([bad], self.root/"badprep", db=self.db)

    def test_apply_is_dry_run_and_requires_matching_review_manifest(self):
        output = self.root/"prepared"
        prepare([self.source([youtube(1), youtube(2)])], output, db=self.db)
        before = file_digest(self.db)
        result = apply_prepared(output, db=self.db)
        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(file_digest(self.db), before)
        with self.assertRaises(ValidationError):
            apply_prepared(output, db=self.db, execute=True)
        approval = self.approval(output, ["youtube:fixture0001"])
        result = apply_prepared(output, db=self.db, approval=approval, execute=True)
        self.assertEqual(result["import"]["inserted"], 1)
        result = apply_prepared(output, db=self.db, approval=approval, execute=True)
        self.assertEqual(result["import"]["updated"], 1)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT transcript_text FROM videos").fetchone()[0], "")
        tampered = json.loads((output/"accepted.json").read_text(encoding="utf-8"))
        tampered[0]["title"] = "Changed after review"
        atomic_json(output/"accepted.json", tampered)
        with self.assertRaises(ValidationError):
            apply_prepared(output, db=self.db, approval=approval, execute=True)

    def test_tiktok_renamed_author_updates_existing_identity(self):
        old, _ = adapt(tiktok())
        old.update(id="original_tiktok_id", url="https://tiktok.com/@old/video/1234567890123456789",
                   review_status="editorial_selection", language="fr", language_status="platform_metadata")
        import_items(self.db, [old], strict=True)
        output = self.root/"prepared"
        report = prepare([self.source([tiktok()])], output, db=self.db)
        self.assertEqual(report["existing_media_to_update"], 1)
        approval = self.approval(output, ["tiktok:1234567890123456789"])
        result = apply_prepared(output, db=self.db, approval=approval, execute=True)
        self.assertEqual(result["import"]["updated"], 1)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute("SELECT id,review_status,language_status FROM videos").fetchone(),
                ("original_tiktok_id", "editorial_selection", "platform_metadata"))


class FakeDataset:
    def __init__(self, rows):
        self.rows, self.calls = rows, []
        self.modified = "2026-10-21T00:00:00Z"

    def get(self, dataset, items=False, **params):
        self.calls.append((dataset, items, params))
        if not items:
            return {"data":{"id":"abc123", "itemCount":len(self.rows), "modifiedAt":self.modified}}
        return self.rows[params["offset"]:params["offset"] + params["limit"]]


class FetchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="focus-apify-test-")
        self.addCleanup(cleanup_temporary, self.tmp)
        self.root = Path(self.tmp.name)

    def test_bounded_resume_includes_empty_rows_without_skip_or_duplicates(self):
        reader = FakeDataset([youtube(1), {}, youtube(2), youtube(3), youtube(4)])
        output = self.root/"pages"
        first = fetch_apify("abc123", output, reader=reader, page_size=2, max_items=5, max_pages=1)
        self.assertFalse(first["bounded_complete"])
        with self.assertRaises(ValidationError):
            prepare([output], self.root/"early", db=None)
        final = fetch_apify("abc123", output, reader=reader, page_size=2, max_items=5, resume=True)
        self.assertTrue(final["complete"])
        self.assertEqual([p[2]["offset"] for p in reader.calls if p[1]], [0, 2, 4])
        self.assertTrue(all(p[2]["skipEmpty"] == "false" for p in reader.calls if p[1]))
        result = prepare([output], self.root/"prepared", db=None)
        self.assertEqual(result["source_records"], 5)
        self.assertEqual(result["accepted_candidates"], 4)
        self.assertEqual(result["quarantined"], 1)

    def test_changed_dataset_and_corrupted_page_block_resume(self):
        reader = FakeDataset([youtube(1), youtube(2)])
        output = self.root/"pages"
        fetch_apify("abc123", output, reader=reader, page_size=1, max_items=2, max_pages=1)
        reader.modified = "2026-10-21T01:00:00Z"
        with self.assertRaises(ValidationError):
            fetch_apify("abc123", output, reader=reader, max_items=2, resume=True)
        reader.modified = "2026-10-21T00:00:00Z"
        (output/"page-000000000.json").write_text("[]")
        with self.assertRaises(ValidationError):
            fetch_apify("abc123", output, reader=reader, max_items=2, resume=True)

    def test_fetch_projection_removes_personal_comments_secrets_and_media(self):
        raw = instagram(latestComments=[{"text":"private sample", "ownerUsername":"person"}],
            apiToken="secret-value", audioUrl="https://example.test/audio", videoUrl="https://example.test/video?token=secret-value")
        output = self.root/"pages"
        fetch_apify("abc123", output, reader=FakeDataset([raw]), max_items=1)
        text = (output/"page-000000000.json").read_text(encoding="utf-8")
        self.assertNotIn("private sample", text)
        self.assertNotIn("secret-value", text)
        self.assertNotIn("audioUrl", text)
        self.assertNotIn("videoUrl", text)

    def test_transport_get_only_token_header_and_bounded_retry(self):
        calls, sleeps = [], []
        class Opener:
            def open(self, request, timeout):
                calls.append(request)
                if len(calls) == 1:
                    raise HTTPError(request.full_url, 429, "Rate limited", {"Retry-After":"2"}, None)
                return io.BytesIO(b'[{"id":"fixture"}]')
        reader = ApifyReader("fake-test-token", opener=Opener(), sleep=sleeps.append)
        result = reader.get("abc123", items=True, offset=0, limit=1)
        self.assertEqual(result, [{"id":"fixture"}])
        self.assertTrue(all(c.get_method() == "GET" for c in calls))
        self.assertTrue(all("fake-test-token" not in c.full_url for c in calls))
        self.assertEqual(calls[0].get_header("Authorization"), "Bearer fake-test-token")
        self.assertIn(2, sleeps)
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.test/"))
        with self.assertRaises(ValidationError):
            reader.get("../../acts/start")

    def test_http_error_never_exposes_body_or_header(self):
        class Opener:
            def open(self, request, timeout):
                raise HTTPError(request.full_url, 401, "secret-token-error", {"token":"secret"}, io.BytesIO(b'secret-body'))
        reader = ApifyReader("fake-test-token", opener=Opener(), sleep=lambda _:None)
        with self.assertRaisesRegex(ValidationError, "HTTP 401") as error:
            reader.get("abc123")
        self.assertNotIn("secret", str(error.exception))


if __name__ == "__main__":
    unittest.main()
