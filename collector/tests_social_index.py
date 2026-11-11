"""Offline contract for the compact social finder export."""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from scripts.export_social_index import build


class SocialIndexTests(unittest.TestCase):
    def test_export_preserves_metadata_domain_and_publisher_language_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "catalog.sqlite3"
            with closing(sqlite3.connect(database)) as conn, conn:
                conn.executescript("""
                    CREATE TABLE videos (id TEXT PRIMARY KEY, platform TEXT, title TEXT, creator TEXT,
                      language TEXT, category TEXT, domain_scope TEXT, url TEXT, metadata_json TEXT,
                      verification_scope TEXT, verified_at TEXT, published_at TEXT);
                    CREATE TABLE video_vehicles (video_id TEXT, make TEXT, model TEXT, generation TEXT,
                      engine TEXT, position INTEGER);
                    CREATE TABLE video_tasks (video_id TEXT, task TEXT);
                """)
                conn.executemany("INSERT INTO videos VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", [
                    ("tiktok:1", "tiktok", "Freinage moto", "Auteur", "fr", "driving", "motorsport",
                     "https://tiktok.com/@a/video/1", "{}", "metadata", "2026-11-08", None),
                    ("instagram:2", "instagram", "Entretien", "Atelier", "und", "mechanics", "automotive_adjacent",
                     "https://instagram.com/reel/2", json.dumps({"publisher_context_language": "fr"}),
                     "publisher_embedded_post", "2026-11-07", None),
                    ("youtube:3", "youtube", "Karting", "Auteur", "fr", "driving", "motorsport",
                     "https://youtu.be/3", "{}", "metadata", "2026-11-09", None),
                ])
                conn.execute("INSERT INTO video_vehicles VALUES (?,?,?,?,?,?)",
                             ("instagram:2", "Renault", "Clio", "V", "", 0))
                conn.execute("INSERT INTO video_tasks VALUES (?,?)", ("instagram:2", "oil_change"))
            exported = build(database, {"tasks": [{"id": "oil_change", "label": {"fr": "Vidange"}}]})
            self.assertEqual([row["id"] for row in exported["items"]], ["tiktok:1", "instagram:2"])
            moto, car = exported["items"]
            self.assertEqual(moto["d"], "motorsport")
            self.assertEqual(car["d"], "automotive_adjacent")
            self.assertEqual(moto["l"], "fr")
            self.assertNotIn("editorFr", moto)
            self.assertEqual(car["l"], "und")
            self.assertTrue(car["editorFr"])
            self.assertEqual(car["v"], [["Renault", "Clio", "V", ""]])
            self.assertEqual(car["s"], ["oil_change"])
            self.assertEqual(exported["tasks"]["oil_change"], {"fr": "Vidange"})


if __name__ == "__main__":
    unittest.main()
