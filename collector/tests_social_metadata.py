"""Offline tests; no database, network, source mutation or generated captions."""
import copy
import json
from pathlib import Path
import unittest

from scripts.social_metadata import normalize_social_metadata as normalize


class SocialMetadataTests(unittest.TestCase):
    def test_editorial_type_aliases_are_not_source_captions(self):
        for field in ("description_basis", "description_type", "descriptionType"):
            row={"title":"Original title", "description":"Note éditoriale &amp; disponibilité à vérifier.",
                 "caption":"Foreign source caption. #Source",field:"editorial_summary"}
            result=normalize(row)
            self.assertEqual(result["description"],"Note éditoriale & disponibilité à vérifier.")
            self.assertEqual(result["field_provenance"]["description"]["basis"],"existing_editorial_description")
            self.assertEqual(result["source_metadata"]["record"][field],"editorial_summary")
            self.assertEqual(result["source_metadata"]["record"]["description"],row["description"])
            self.assertEqual(result["hashtags"],["#Source"])
            self.assertIn("caption",result["field_provenance"]["hashtags"]["fields"])
            self.assertEqual(result["field_provenance"]["description"]["field"],"description")

    def test_html_entities_are_decoded_outside_signed_links_only(self):
        link="https://images.example/cover?token=a%2Bb&amp;expires=123#cover"
        row={"title":"Moteur &amp; huile OBD2", "description":"L&#39;huile &amp; filtre. "+link}
        result=normalize(row)
        self.assertEqual(result["title"],"Moteur & huile OBD2")
        self.assertEqual(result["description"],"L'huile & filtre.")
        self.assertEqual(result["links"],[link])
        self.assertEqual(result["source_metadata"]["record"]["description"],row["description"])

    def test_already_separated_tokens_and_source_url_are_preserved(self):
        row={"title":"Titre", "description":"Description", "url":"https://www.instagram.com/reel/Example/",
             "hashtags":["#Auto","#auto","#école","#126"], "mentions":["@garage.fr"],
             "links":["https://example.org/?sig=x%2By&amp;a=1"],"description_type":"source_caption"}
        result=normalize(row)
        self.assertEqual(result["hashtags"],["#Auto","#école","#126"])
        self.assertEqual(result["mentions"],row["mentions"])
        self.assertEqual(result["links"],row["links"])
        for field in ("url","hashtags","mentions","links","description_type"):
            self.assertEqual(result["source_metadata"]["record"][field],row[field])
        self.assertEqual(normalize(result),result)

    def test_arabic_and_japanese_sentence_boundaries(self):
        for caption,expected in (("كيف نفحص ضغط الإطارات؟ اتبع تعليمات الشركة.","كيف نفحص ضغط الإطارات؟"),
                                 ("タイヤ空気圧を確認する方法。車両の指定値を確認してください。","タイヤ空気圧を確認する方法。")):
            result=normalize({"caption":caption})
            self.assertEqual(result["title"],expected)
            self.assertFalse(result["needs_title_review"])

    def test_native_titles_are_not_shortened_or_rewritten(self):
        title="Honda Accord VI (1997–2002) : prise OBD2, moteur 1.6L et huile VW 507.00"
        self.assertEqual(normalize({"title":title,"description":title})["title"],title)
        long_title=title*4
        result=normalize({"title":long_title})
        self.assertEqual(result["title"],long_title)
        self.assertTrue(result["needs_title_review"])

    def test_caption_first_complete_sentence_does_not_cut_specs_or_years(self):
        caption="Contrôler le moteur 1.6L, la prise OBD2 et l’huile VW 507.00 (1997–2002). Voici la suite. #Auto"
        result=normalize({"caption":caption})
        self.assertEqual(result["title"],caption.split(" Voici")[0])
        self.assertEqual(result["hashtags"],["#Auto"])
        self.assertIn("Voici la suite.",result["description"])

    def test_unterminated_or_truncated_caption_needs_review_without_invention(self):
        for caption in ("Comment changer le filtre sur votre voiture", "Comment changer le filtre sur votre...",
                        "Encore une idée… À suivre.", "X"*200+". Suite."):
            result=normalize({"caption":caption})
            self.assertEqual(result["title"],caption)
            self.assertTrue(result["needs_title_review"])
            self.assertEqual(result["field_provenance"]["title"]["basis"],"source_text_pending_title_review")
            self.assertEqual(result["source_metadata"]["record"]["caption"],caption)

    def test_heading_is_preserved_instead_of_salutation(self):
        caption="🚗 **Comprendre le Blocage de la Géométrie Variable des Turbos Diesel** 🚗 Salut tout le monde !\n### Fonctionnement\nExplication."
        result=normalize({"caption":caption})
        self.assertEqual(result["title"],"Comprendre le Blocage de la Géométrie Variable des Turbos Diesel")
        self.assertEqual(result["hashtags"],[])
        self.assertEqual(normalize({"caption":"## Réparer le moteur 1.6L\nLa suite."})["title"],"Réparer le moteur 1.6L")

    def test_unicode_hashtags_dedupe_keep_original_case_and_marks(self):
        text="Un tuto. #Auto #auto #école #e\u0301cole #fypシ #fypシ゚viral #日本語 #العربية #foryoupage #foryoupage"
        result=normalize({"caption":text})
        self.assertEqual(result["hashtags"],["#Auto","#école","#fypシ","#fypシ゚viral","#日本語","#العربية","#foryoupage"])
        self.assertEqual(result["description"],"Un tuto.")
        self.assertEqual(result["source_metadata"]["record"]["caption"],text)

    def test_adjacent_hashtag_keeps_native_model_and_handles_do_not_become_emails(self):
        result=normalize({"title":"Tutorial BMW 5 Series#carwiperblade #wipers",
                          "description":"Merci @Garage.FR et @garage.fr ; mail: help@example.com"})
        self.assertEqual(result["title"],"Tutorial BMW 5 Series")
        self.assertEqual(result["hashtags"],["#carwiperblade","#wipers"])
        self.assertEqual(result["mentions"],["@Garage.FR"])
        self.assertIn("help@example.com",result["description"])

    def test_numbers_csharp_and_url_fragments_are_not_hashtags(self):
        text="C# ; Cra 52 #61 - 108 Medellín ; #126 / 365 ; #123 ; docs.html#intro ; https://example.org/path#chapter #Auto"
        result=normalize({"title":text})
        self.assertEqual(result["hashtags"],["#Auto"])
        self.assertEqual(result["links"],["https://example.org/path#chapter"])
        for token in ("C#","#61","#126","#123","docs.html#intro"):
            self.assertIn(token,result["title"])

    def test_text_after_hashtag_is_not_discarded(self):
        caption="Quel ordre pour brancher ou débrancher une batterie 12V ? #automobile Moyen mnémotechnique:\nOn commence par le -"
        result=normalize({"caption":caption})
        self.assertEqual(result["title"],"Quel ordre pour brancher ou débrancher une batterie 12V ?")
        self.assertIn("Moyen mnémotechnique:",result["description"])
        self.assertIn("On commence par le -",result["description"])

    def test_native_numeric_vehicle_hashtags_are_separated_without_source_loss(self):
        caption="Où trouver la prise OBD2 de la Peugeot 1007 ? #peugeot #1007 #5008"
        row={"caption":caption,"hashtags":["peugeot","1007","#5008"]}
        before=copy.deepcopy(row)
        result=normalize(row)
        self.assertEqual(result["description"],"Où trouver la prise OBD2 de la Peugeot 1007 ?")
        self.assertEqual(result["hashtags"],["#peugeot","#1007","#5008"])
        self.assertEqual(result["source_metadata"]["record"]["caption"],caption)
        self.assertEqual(row,before)
        self.assertEqual(normalize(result),result)

    def test_only_explicit_native_numeric_hashtags_are_removed(self):
        row={"caption":"Référence #126 / 365 ; Fiat 500. #500 #___","hashtags":["500"]}
        result=normalize(row)
        self.assertEqual(result["hashtags"],["#500"])
        self.assertIn("#126 / 365",result["description"])
        self.assertIn("#___",result["description"])
        self.assertNotIn("#500",result["description"])

    def test_numeric_native_hashtags_do_not_strip_url_fragments(self):
        result=normalize({"caption":"Fiat 500. https://example.org/#500 #500","hashtags":["500","＃500"]})
        self.assertEqual(result["links"],["https://example.org/#500"])
        self.assertEqual(result["hashtags"],["#500"])
        self.assertEqual(result["description"],"Fiat 500.")

    def test_numeric_caption_tag_in_contiguous_cluster_with_incomplete_native_tags(self):
        caption="Prise OBD2 Peugeot 308 CC. #peugeot #308 #308cc #peugeot308cabrio"
        result=normalize({"caption":caption,"hashtags":["peugeot308cabrio"]})
        self.assertEqual(result["description"],"Prise OBD2 Peugeot 308 CC.")
        self.assertEqual(result["hashtags"],["#peugeot","#308","#308cc","#peugeot308cabrio"])
        self.assertEqual(result["source_metadata"]["record"]["caption"],caption)
        self.assertEqual(normalize({"caption":"Fiat 500. #500 #fiat"})["hashtags"],["#500","#fiat"])

    def test_numeric_hashtag_cluster_does_not_consume_separated_reference_or_url(self):
        for caption in ("#auto Référence #126 /365", "#auto #126 /365", "https://example.org/#auto #126"):
            result=normalize({"caption":caption})
            self.assertIn("#126",result["description"])
            self.assertNotIn("#126",result["hashtags"])

    def test_urls_preserve_signatures_fragments_and_distinct_case(self):
        text="Voir https://img.example/cover.jpg?sig=a%2Bb&x=3#image et https://img.example/cover.jpg?sig=a%2Bb&x=3#image."
        result=normalize({"title":"Source", "description":text})
        self.assertEqual(result["links"],["https://img.example/cover.jpg?sig=a%2Bb&x=3#image"])
        self.assertEqual(result["hashtags"],[])

    def test_exa_composite_bodies_cannot_supply_description_or_tokens(self):
        row={"title":"Tutoriel huile 5W30 #Huile", "description":"Other creator: #freins @Other https://other.example/ - français audio!",
             "_collection":{"provider":"exa-public-mcp","evidence_scope":"public_video_metadata"}}
        result=normalize(row)
        self.assertEqual(result["description"],"")
        self.assertEqual(result["hashtags"],["#Huile"])
        self.assertEqual(result["mentions"],[])
        self.assertEqual(result["links"],[])
        self.assertEqual(result["source_metadata"]["record"]["description"],row["description"])
        self.assertFalse(result["normalization"]["language_inferred"])

    def test_existing_editorial_summary_is_distinguished_from_source_caption(self):
        row={"title":"How to change wipers", "description":"La légende annonce une méthode.",
             "description_basis":"public_title_or_caption_only","verification_scope":"indexed_caption_metadata"}
        result=normalize(row)
        self.assertEqual(result["title"],row["title"])
        self.assertEqual(result["description"],row["description"])
        self.assertEqual(result["field_provenance"]["description"]["basis"],"existing_editorial_description")

    def test_editorial_description_does_not_replace_foreign_native_title_or_become_new_title(self):
        row={"title":"How to replace the oil filter", "caption":"How to replace the oil filter. #Oil",
            "description":"Le titre présente le remplacement du filtre.",
            "description_basis":"public_title_or_caption_only","verification_scope":"indexed_caption_metadata"}
        result=normalize(row)
        self.assertEqual(result["title"],row["title"])
        self.assertEqual(result["description"],row["description"])
        self.assertNotIn("#Oil",result["hashtags"])
        del row["title"]
        result=normalize(row)
        self.assertEqual(result["title"],"")
        self.assertTrue(result["needs_title_review"])

    def test_token_only_caption_does_not_invent_a_subject(self):
        result=normalize({"caption":"#Auto @Garage https://example.org"})
        self.assertEqual(result["title"],"")
        self.assertTrue(result["needs_title_review"])

    def test_catalogue_metadata_json_and_source_text_are_preserved_without_mutation(self):
        meta={"title":"Titre d’origine","description":"Légende complète. #Source","provenance":{"title_basis":"first_line_of_source_caption"}}
        raw=json.dumps(meta,ensure_ascii=False,indent=3)
        row={"title":"Légende complète. #Source","description":meta["description"],"metadata_json":raw}
        before=copy.deepcopy(row)
        result=normalize(row)
        self.assertEqual(row,before)
        self.assertEqual(result["source_metadata"]["metadata_json"],raw)
        self.assertEqual(result["source_metadata"]["metadata"]["title"],"Titre d’origine")
        self.assertEqual(result["title"],"Légende complète.")

    def test_truncated_caption_title_does_not_invent_a_partial_hashtag(self):
        row={"title":"Remplacer les essuie-glaces. #Volks", "description":"Remplacer les essuie-glaces. #Volkswagen #Auto",
             "provenance":{"title_basis":"exact_truncated_prefix_of_direct_caption_first_line"},
             "verification_scope":"public_video_metadata"}
        result=normalize(row)
        self.assertEqual(result["title"],"Remplacer les essuie-glaces.")
        self.assertEqual(result["hashtags"],["#Volkswagen","#Auto"])
        self.assertEqual(result["field_provenance"]["title"]["field"],"description")

    def test_idempotence_and_documented_editorial_override(self):
        row={"caption":"Comment changer votre... #auto"}
        first=normalize(row)
        self.assertEqual(normalize(first),first)
        override={"title":"Vérifier les essuie-glaces","basis":"Titre choisi après lecture de la légende source complète."}
        second=normalize(first,override)
        self.assertEqual(second["source_metadata"],first["source_metadata"])
        self.assertEqual(second["title"],override["title"])
        self.assertFalse(second["needs_title_review"])
        self.assertEqual(normalize(second),second)
        self.assertEqual(second["normalization"]["title_override"],override)

    def test_override_requires_basis_and_is_never_interpreted_as_markup_or_code(self):
        for bad in ("Title",{}, {"title":"T"},{"title":"T","basis":""},{"title":"T\nS","basis":"source"}):
            with self.assertRaises(ValueError):normalize({},bad)
        title='<img src=x onerror="alert(1)">'
        result=normalize({}, {"title":title,"basis":"User-supplied literal string, caller must escape HTML"})
        self.assertEqual(result["title"],title)

    def test_malformed_json_and_unicode_line_separators_do_not_lose_original(self):
        row={"caption":"Première phrase.\u2028Suite.\u2029Fin.","metadata_json":"{invalid"}
        result=normalize(row)
        self.assertTrue(result["normalization"]["metadata_json_parse_failed"])
        self.assertEqual(result["source_metadata"]["record"]["caption"],row["caption"])
        self.assertEqual(result["source_metadata"]["metadata_json"],"{invalid")

    def test_abbreviations_do_not_cut_first_sentence(self):
        result=normalize({"caption":"Dr. Martin vérifie le moteur 1.6L et la norme VW 507.00. Ensuite il explique."})
        self.assertEqual(result["title"],"Dr. Martin vérifie le moteur 1.6L et la norme VW 507.00.")

    def test_optional_real_snapshot_is_lossless_and_idempotent(self):
        snapshot=Path(__file__).resolve().parents[2]/'work/social-metadata-2026-10-21/input-snapshot.json'
        if not snapshot.exists():self.skipTest("Optional local research snapshot is not part of the reusable module")
        rows=json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual(len(rows),237)
        for row in rows:
            with self.subTest(id=row["id"]):
                before=copy.deepcopy(row)
                result=normalize(row)
                self.assertEqual(normalize(result),result)
                self.assertEqual(row,before)
                self.assertEqual(result["source_metadata"]["record"]["title"],row["title"])
                self.assertEqual(result["source_metadata"]["metadata_json"],row["metadata_json"])
                if row["verification_scope"]=="indexed_search_metadata":
                    self.assertEqual(result["description"],"")


if __name__ == "__main__":
    unittest.main()
