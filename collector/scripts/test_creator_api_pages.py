import json
from pathlib import Path
import tempfile
import unittest

from creator_api_pages import plan, run, unpack


class CreatorPages(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out=Path(self.tmp.name)
        self.p=plan("tiktok","garage.fr",max_pages=250)

    def page(self, cursor, more):
        post="7340000000000000"+str(cursor).zfill(3)
        return {"error":{"code":"ok"},"data":{"has_more":more,"cursor":cursor,"videos":[{
            "id":post,"title":"Identifier un filtre","video_description":"Exemple de test",
            "share_url":f"https://www.tiktok.com/@Garage.fr/video/{post}?ref=unneeded"}]}}

    def test_resume_and_offline_prepare(self):
        from public_export import prepare_public_export
        cursors=[]
        def get(p,c,t):
            cursors.append(c)
            return self.page(24,True) if c is None else self.page(12,False)
        self.assertEqual(run(self.p,self.out,"dummy",1,get)["pages"],1)
        self.assertTrue(run(self.p,self.out,"dummy",1,get)["complete"])
        self.assertEqual(cursors,[None,24])
        self.assertTrue(run(self.p,self.out,"dummy",1,lambda *_:self.fail())["complete"])
        result=prepare_public_export(self.out/"manifest.json", self.out/"prepared")
        self.assertEqual(result["unique_media_identities"],2)
        self.assertNotIn("ref=unneeded",(self.out/"page-0001.json").read_text())

    def test_throttle_no_resume(self):
        def stop(*_): raise TimeoutError()
        with self.assertRaises(TimeoutError): run(self.p,self.out,"dummy",1,stop)
        with self.assertRaises(FileExistsError): run(self.p,self.out,"dummy",1,lambda *_:self.fail())

    def test_changed_page_not_replayed(self):
        run(self.p,self.out,"dummy",1,lambda *_:self.page(12,True))
        (self.out/"page-0001.json").write_text("{}")
        with self.assertRaisesRegex(ValueError,"checkpoint mismatch"): run(self.p,self.out,"dummy",1,lambda *_:self.fail())

    def test_repeating_cursor_stops(self):
        with self.assertRaisesRegex(ValueError,"Repeated cursor"):
            run(self.p,self.out,"dummy",2,lambda *_:self.page(12,True),lambda _:None)
        self.assertTrue((self.out/"in-flight").exists())

    def test_instagram_no_next_url_token_or_photos(self):
        p=plan("instagram","example",account="123456",version="v23.0")
        data={"data":[{"media_type":"IMAGE"},{"id":"1111","username":"example","media_type":"VIDEO","media_product_type":"REELS",
                "permalink":"https://www.instagram.com/reel/ABCD/?ref=example","caption":"Titre","private_extra":"omit"}],
                "paging":{"next":"https://example.invalid/?access_token=should-never-appear","cursors":{"after":"YXh4"}}}
        r=run(p,self.out,"dummy",1,lambda *_:data)
        self.assertEqual((r["source_records"],r["video_rows"]),(2,1))
        for f in self.out.iterdir():
            self.assertNotRegex(f.read_text(),r"should-never-appear|private_extra|ref=example")

    def test_reject_missing_identity(self):
        data=self.page(1,False)
        data["data"]["videos"][0]["id"]="wrong"
        with self.assertRaises(ValueError): unpack(self.p,data)
