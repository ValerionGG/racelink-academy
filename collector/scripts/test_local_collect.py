"""Local collector tests: temporary metadata only, no network or live database."""
from pathlib import Path
import json
import os
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts.local_collect import (BASE_FLAGS, collect, collect_exa, error_status, exa_command,
    exa_entries, job_key, normalize_yt, process, provenance, stop_process, validate_plan, yt_command)
from scripts.bulk_ingest import adapt, prepare
from server import ValidationError
from tests_bulk_ingest import cleanup_temporary


def video(platform="youtube", number=1):
    urls = {"youtube": f"https://www.youtube.com/watch?v=sample{number:05}",
            "instagram": f"https://www.instagram.com/reel/Sample{number:05}/",
            "tiktok": f"https://www.tiktok.com/@testfixture/video/{1000000000000000000+number}"}
    return {"kind":"video", "value":urls[platform], "limit":1}


def metadata(permalink, **extra):
    return {"webpage_url":permalink, "title":"How to replace car wipers — synthetic test",
            "description":"Step by step car wiper replacement", "uploader":"Synthetic author",
            "thumbnail":"https://images.example.org/cover.jpg?signature=public",
            "upload_date":"20261021", **extra}


class PlanTests(unittest.TestCase):
    def test_unknown_flags_credentials_local_hosts_profiles_and_unbounded_plans_fail(self):
        invalid = [[{**video(), "cookies":"private"}], [video() | {"limit":2}],
            [video() | {"value":"https://127.0.0.1/video"}],
            [video() | {"value":"https://secret:password@youtube.com/watch?v=sample00001"}],
            [{"kind":"youtube_channel","value":"https://youtube.com/@garage?token=private"}],
            [{"kind":"video","value":"https://instagram.com/garage/"}],
            [{"kind":"exa_search","value":"tuto","limit":11}],
            [{"kind":"youtube_search","value":"tuto\n--cookies", "limit":1}],
            [{"kind":"youtube_search","value":f"query {i}","limit":500} for i in range(21)]]
        for plan in invalid:
            with self.subTest(plan=plan[:1]), self.assertRaises((ValidationError, ValueError)):
                validate_plan(plan)

    def test_exact_duplicate_jobs_are_collapsed(self):
        self.assertEqual(len(validate_plan([video(),video()])), 1)
        self.assertEqual(validate_plan([{"kind":"youtube_channel","value":"https://youtube.com/@garage/videos","limit":4}])[0]["platform"], "youtube")

    def test_fixed_subprocess_arguments_disable_external_configuration_and_media(self):
        job = validate_plan([{"kind":"youtube_search","value":"wipers & $(secret)","limit":3}])[0]
        cmd = yt_command("yt-dlp",job)
        self.assertEqual(cmd[-2], "--")
        self.assertEqual(cmd[-1], "ytsearch3:wipers & $(secret)")
        for flag in ("--ignore-config", "--no-plugin-dirs", "--no-remote-components", "--simulate", "--skip-download",
                     "--no-cookies", "--no-cookies-from-browser", "--no-cache-dir"):
            self.assertIn(flag,cmd)
        self.assertNotIn("--write-comments",cmd)
        self.assertIn("--flat-playlist",cmd)

    def test_exa_uses_only_public_endpoint_without_key_or_oauth(self):
        job = validate_plan([{"kind":"exa_search","value":"public car tutorials", "limit":2}])[0]
        cmd = exa_command(["node","existing-mcporter.js"],job)
        self.assertIn("https://mcp.exa.ai/mcp",cmd)
        self.assertIn("--no-oauth",cmd)
        self.assertNotIn("--header",cmd)
        self.assertNotIn("--persist",cmd)
        self.assertEqual(json.loads(cmd[cmd.index("--args")+1])["numResults"],2)

    def test_advanced_search_validates_bounded_filters_without_changing_legacy_jobs(self):
        legacy={"kind":"exa_search","value":"tuto","limit":2}
        self.assertEqual(validate_plan([legacy])[0],legacy|{"platform":"web_index"})
        base={"kind":"exa_search_advanced","value":"vidange","limit":50,
              "include_domains":["instagram.com","tiktok.com"],"include_text":["vidange"],"user_location":"FR"}
        job=validate_plan([base])[0]
        cmd=exa_command(["node","mcporter.js"],job)
        self.assertIn("https://mcp.exa.ai/mcp?tools=web_search_advanced_exa",cmd)
        args=json.loads(cmd[cmd.index("--args")+1])
        self.assertEqual(args["includeText"],["vidange"])
        self.assertEqual(args["userLocation"],"FR")
        self.assertFalse(args["enableSummary"])
        self.assertIn("--no-oauth",cmd)
        self.assertEqual(provenance(job,"exa-public-mcp")["evidence_scope"],"indexed_search_metadata")
        for extra in ({"limit":51},{"include_domains":["internal.example"]},{"include_text":"vidange"},
                      {"include_text":["x\nsecret"]},{"user_location":"French"},{"cookies":"private"}):
            with self.subTest(extra=extra),self.assertRaises(ValidationError):
                validate_plan([base|extra])
        with self.assertRaises(ValidationError):
            validate_plan([legacy|{"user_location":"FR"}])

    def test_tiktok_execution_uses_the_upstream_supported_www_host(self):
        job=validate_plan([video("tiktok")])[0]
        self.assertTrue(yt_command("yt-dlp",job)[-1].startswith("https://www.tiktok.com/@"))
        self.assertTrue(job["value"].startswith("https://tiktok.com/@"))

    def test_http_access_blocks_accept_standard_status_wording(self):
        for message in ("HTTP 429 Too Many Requests", "HTTP 403 Forbidden", "HTTP Error 429",
                        "Forbidden", "Too Many Requests", "HTTP status 403"):
            self.assertEqual(error_status(message),"access_blocked")

    def test_instagram_auth_blocks_stop_without_misclassifying_generic_help(self):
        for message in ("Instagram API is not granting access",
                        "empty media response; this resource requires a logged-in session",
                        "Only available to logged-in users",
                        "Authentication is required to access this page"):
            self.assertEqual(error_status(message),"access_blocked")
        self.assertEqual(error_status("Use --help for documentation about logged-in session options"),
                         "extractor_failed")

    def test_keyless_process_isolates_existing_credentials_and_configuration(self):
        captured={}
        class Completed:
            returncode=0
            def poll(self): return 0
        def popen(command, **kwargs):
            captured.update(command=command,env=kwargs["env"])
            self.assertFalse(kwargs["shell"])
            self.assertNotIn("EXA_API_KEY",kwargs["env"])
            config=Path(kwargs["env"]["MCPORTER_CONFIG"])
            self.assertEqual(json.loads(config.read_text()),{"mcpServers":{},"imports":[]})
            self.assertTrue(command[command.index("--name")+1].startswith("focus-keyless-"))
            self.assertTrue(Path(kwargs["env"]["XDG_DATA_HOME"]).is_relative_to(config.parent))
            kwargs["stdout"].write(b'{}')
            return Completed()
        job=validate_plan([{"kind":"exa_search","value":"car wipers","limit":1}])[0]
        with patch.dict(os.environ,{"EXA_API_KEY":"fake-secret","MCPORTER_CONFIG":"existing-private-config"}), \
             patch("scripts.local_collect.subprocess.Popen",side_effect=popen):
            self.assertEqual(process(exa_command(["node","mcporter.js"],job))["stdout"],"{}")
            advanced=exa_command(["node","mcporter.js"],job)
            advanced[advanced.index("https://mcp.exa.ai/mcp")]="https://mcp.exa.ai/mcp?tools=web_search_advanced_exa"
            self.assertEqual(process(advanced)["stdout"],"{}")
            self.assertEqual(os.environ["MCPORTER_CONFIG"],"existing-private-config")

    @unittest.skipUnless(os.name == "nt", "Windows launcher process tree")
    def test_windows_timeout_stops_only_the_created_process_tree_without_shell(self):
        calls=[]
        class Child:
            pid=123456789
            def poll(self): return None
            def kill(self): calls.append("kill")
            def wait(self,timeout): calls.append(("wait",timeout))
        with patch("scripts.local_collect.subprocess.run") as terminate:
            stop_process(Child())
        command=terminate.call_args.args[0]
        self.assertEqual(command[1:],["/PID","123456789","/T","/F"])
        self.assertFalse(terminate.call_args.kwargs["shell"])
        self.assertEqual(calls,["kill",("wait",5)])


class ShutdownTests(unittest.TestCase):
    """Real local child, no network: interruption must finish the child before unlock."""
    def check_interruption(self, exception):
        children = []
        original = subprocess.Popen
        def track(*args, **kwargs):
            child = original(*args, **kwargs)
            children.append(child)
            return child
        alive = False
        try:
            with self.assertRaises(exception):
                with patch("scripts.local_collect.subprocess.Popen", side_effect=track), \
                     patch("scripts.local_collect.time.sleep", side_effect=exception("synthetic interruption")):
                    process([sys.executable, "-c", "import time; time.sleep(30)"], timeout=5)
            self.assertTrue(children)
            alive = children[0].poll() is None
        finally:
            if children and children[0].poll() is None:
                stop_process(children[0])
        self.assertFalse(alive, "Transport returned while its own child was still alive")

    def test_keyboard_interrupt_terminates_real_owned_child_and_preserves_exception(self):
        self.check_interruption(KeyboardInterrupt)

    def test_system_exit_terminates_real_owned_child_and_preserves_exception(self):
        self.check_interruption(SystemExit)


class MappingTests(unittest.TestCase):
    def test_social_ytdlp_export_is_bulk_compatible_with_honest_provenance(self):
        for platform in ("youtube","instagram","tiktok"):
            job = validate_plan([video(platform)])[0]
            raw = metadata(job["value"], url="https://cdn.example.org/private-media.mp4", language="fr-FR",
                           subtitles={"fr":[{"text":"not authorized"}]}, comments=[{"text":"personal"}])
            record = normalize_yt(raw,job,"test-version")
            self.assertEqual(record["url"],record["webpage_url"])
            self.assertNotIn("subtitles",record)
            self.assertNotIn("comments",record)
            item, decision = adapt(record)
            self.assertEqual(decision["status"],"candidate")
            self.assertEqual(item["provenance"]["adapter"],"yt-dlp")
            self.assertEqual(item["collection_provenance"]["evidence_scope"],"public_video_metadata")
            self.assertEqual(item["thumbnail_url"],raw["thumbnail"])
            self.assertEqual(item["published_at"],"2026-10-21")
            self.assertNotIn("transcript",item)

    def test_flat_search_never_guesses_french_from_query(self):
        job = validate_plan([{"kind":"youtube_search","value":"tutoriel voiture francais","limit":2}])[0]
        record = normalize_yt({"id":"sample00001","title":"How to replace car wipers"},job,"test")
        item,_ = adapt(record)
        self.assertEqual(item["language"],"und")
        self.assertEqual(item["verification_scope"],"public_listing_metadata")

    def test_generic_instagram_extractor_title_keeps_original_caption_provenance(self):
        job=validate_plan([video("instagram")])[0]
        record=normalize_yt(metadata(job["value"],title="Video by test",description="How to replace car wipers\nSource tags"),job,"test")
        item,_=adapt(record)
        self.assertEqual(item["title"],"How to replace car wipers")
        self.assertEqual(item["collection_provenance"]["extractor_title"],"Video by test")
        self.assertEqual(item["collection_provenance"]["title_basis"],"first_line_of_source_caption")

    def test_output_identity_or_platform_change_is_rejected(self):
        job=validate_plan([video()])[0]
        with self.assertRaises(ValidationError):
            normalize_yt(metadata(video(number=2)["value"]),job,"test")
        with self.assertRaises(ValidationError):
            normalize_yt(metadata(video("instagram")["value"]),job,"test")

    def test_indexed_results_remain_indexed_and_language_unknown(self):
        job=validate_plan([{"kind":"exa_search","value":"French wiper tutorial","limit":2}])[0]
        payload={"content":[{"type":"text","text":"Title: How to replace car wipers\nURL: https://instagram.com/reel/Sample00001/\nPublished: N/A\nAuthor: N/A\nHighlights:\nA car wiper tutorial.\n\n---\n\nTitle: Garage profile\nURL: https://instagram.com/garage/\nAuthor: N/A\nHighlights:\nA profile."}]}
        result=collect_exa(job,["node","mcporter"],runner=lambda *_:{"returncode":0,"stdout":json.dumps(payload),"stderr":""})
        self.assertEqual(len(result["records"]),1)
        self.assertEqual(result["rejected_non_video_links"],1)
        item,_=adapt(result["records"][0])
        self.assertEqual(item["language"],"und")
        self.assertEqual(item["verification_scope"],"indexed_search_metadata")
        self.assertEqual(item["provenance"]["adapter"],"exa-public-mcp")
        self.assertEqual(item["creator"],"")
        self.assertIsNone(item["verified_at"])

    def test_unrecognized_exa_text_does_not_invent_results(self):
        self.assertEqual(list(exa_entries({"content":[{"type":"text","text":"A very useful tutorial may exist."}]})),[])
        payload={"structuredContent":{"results":[{"url":video()["value"],"title":"Car wiper tutorial","highlights":["One","Two"]}]}}
        self.assertEqual(list(exa_entries(payload))[0]["description"],"One Two")

    def test_advanced_json_inside_mcp_text_keeps_real_fields_and_index_scope(self):
        job=validate_plan([{"kind":"exa_search_advanced","value":"tutoriel français","limit":2,
            "include_text":["vidange"],"user_location":"FR"}])[0]
        row={"url":video("instagram")["value"],"title":"How to replace car wipers",
             "text":"Related videos: vidange en français", "author":"Source author",
             "image":"https://images.example.org/cover.jpg?signature=public%2Bvalue",
             "publishedDate":"2026-10-25T10:00:00Z"}
        for notices in (None,["A search restriction was relaxed"]):
            with self.subTest(notices=notices):
                data={"results":[row]}
                if notices is not None:
                    data["notices"]=notices
                payload={"content":[{"type":"text","text":json.dumps(data)}]}
                result=collect_exa(job,["node","mcporter"],runner=lambda *_:{"returncode":0,"stdout":json.dumps(payload),"stderr":""})
                self.assertEqual(result["status"],"ok")
                self.assertEqual(len(result["records"]),1)
                collected=result["records"][0]
                self.assertEqual(collected["title"],row["title"])
                self.assertEqual(collected["uploader"],row["author"])
                self.assertEqual(collected["thumbnail"],row["image"])
                self.assertEqual(collected["published_at"],row["publishedDate"])
                item,_=adapt(collected)
                self.assertEqual(item["language"],"und")
                self.assertEqual(item["description"],"")
                self.assertEqual(item["verification_scope"],"indexed_search_metadata")
                self.assertIsNone(item["verified_at"])

    def test_structured_root_and_text_json_exa_variants_have_same_rows_without_duplicates(self):
        row={"url":video()["value"],"title":"Car wiper tutorial","highlights":["One","Two"]}
        data={"results":[row]}
        variants=(data,{"structuredContent":data},
                  {"content":[{"type":"text","text":json.dumps(data)}]},
                  {"structuredContent":data,"content":[{"type":"text","text":json.dumps(data)}]})
        expected=list(exa_entries(data))
        self.assertEqual(len(expected),1)
        for payload in variants:
            self.assertEqual(list(exa_entries(payload)),expected)
        self.assertEqual(list(exa_entries({"structuredContent":{"results":[]},
            "content":[{"type":"text","text":json.dumps(data)}]})),[])

    def test_unknown_or_malformed_json_exa_content_is_not_a_result(self):
        for text in ('{"results":', '{"results":"not a list"}',
                     '{"notices":["A tutorial exists"]}', '[{"title":"A tutorial"}]'):
            with self.subTest(text=text):
                self.assertEqual(list(exa_entries({"content":[{"type":"text","text":text}]})),[])
        self.assertEqual(list(exa_entries([])),[])
        self.assertEqual(list(exa_entries({"content":[{"type":"text","text":None}]})),[])

    def test_modern_json_exa_collection_keeps_permalink_filter_and_result_bound(self):
        job=validate_plan([{"kind":"exa_search_advanced","value":"vidange","limit":2}])[0]
        rows=[{"url":"https://instagram.com/garage/","title":"Garage profile"},
              {"url":video("instagram")["value"],"title":"How to replace car wipers"},
              {"url":video("instagram",2)["value"],"title":"Beyond the requested bound"}]
        payload={"content":[{"type":"text","text":json.dumps({"results":rows})}]}
        result=collect_exa(job,["node","mcporter"],runner=lambda *_:{"returncode":0,"stdout":json.dumps(payload),"stderr":""})
        self.assertEqual(len(result["records"]),1)
        self.assertEqual(result["rejected_non_video_links"],1)
        self.assertEqual(result["records"][0]["id"],"Sample00001")

    def test_advanced_index_images_dates_and_filters_keep_index_provenance(self):
        job=validate_plan([{"kind":"exa_search_advanced","value":"tutoriel français","limit":25,
            "include_text":["vidange"],"user_location":"FR"}])[0]
        signed="https://images.example.org/image.jpg?signature=public%2Bvalue&expires=12345"
        payload={"results":[{"url":"https://instagram.com/source_author/reel/Sample00001/",
            "title":"How to replace car wipers | Instagram","text":"Related posts: vidange en français",
            "image":signed,"publishedDate":"2026-10-01T10:00:00Z"}]}
        result=collect_exa(job,["node","mcporter"],runner=lambda *_:{"returncode":0,"stdout":json.dumps(payload),"stderr":""})
        item,decision=adapt(result["records"][0])
        self.assertEqual(decision["status"],"candidate")
        self.assertEqual(item["thumbnail_url"],signed)
        self.assertEqual(item["thumbnail_status"],"indexed_metadata_unverified")
        self.assertEqual(item["publication_date_status"],"indexed_metadata_unverified")
        self.assertTrue(item["published_at"].startswith("2026-10-01"))
        self.assertEqual(item["creator"],"")
        self.assertEqual(item["language"],"und")
        self.assertEqual(item["description"],"")
        self.assertEqual(item["collection_provenance"]["search_filters"]["user_location"],"FR")
        self.assertIsNone(item["verified_at"])


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="focus-local-collector-test-")
        self.addCleanup(cleanup_temporary,self.tmp)
        self.root=Path(self.tmp.name)
        self.calls=[]

    def runner(self, command, timeout):
        self.calls.append(command)
        if "--version" in command:
            return {"returncode":0,"stdout":"test-version","stderr":""}
        target=command[-1]
        return {"returncode":0,"stdout":json.dumps(metadata(target)),"stderr":""}

    def test_preview_has_no_network_or_files(self):
        output=self.root/"new"
        result=collect(validate_plan([video()]),output,runner=lambda *_:self.fail("Preview executed a command"))
        self.assertEqual(result["mode"],"dry_run")
        self.assertFalse(output.exists())

    def test_resume_uses_verified_cache_without_repeating_network(self):
        output=self.root/"run"
        jobs=validate_plan([video(),video(number=2)])
        first=collect(jobs,output,execute=True,max_jobs=1,yt_dlp="fake",runner=self.runner,sleeper=lambda _:None)
        self.assertEqual(first["pending_jobs"],1)
        second=collect(jobs,output,execute=True,resume=True,yt_dlp="fake",runner=self.runner,sleeper=lambda _:None)
        self.assertEqual(second["unique_records"],2)
        self.assertEqual(len([c for c in self.calls if "--version" not in c]),2)
        final=collect(jobs,output,execute=True,resume=True,runner=lambda *_:self.fail("Cache repeated network"),sleeper=lambda _:None)
        self.assertEqual(final["jobs_attempted_this_run"],0)
        self.assertFalse(final["database_modified"])
        prepared=prepare([output/"records.jsonl"],self.root/"prepared",db=None)
        self.assertEqual(prepared["accepted_candidates"],2)

    def test_tampered_cache_or_changed_plan_blocks_resume(self):
        output=self.root/"run"
        jobs=validate_plan([video()])
        collect(jobs,output,execute=True,yt_dlp="fake",runner=self.runner,sleeper=lambda _:None)
        with self.assertRaises(ValidationError):
            collect(validate_plan([video(number=2)]),output,execute=True,resume=True,runner=self.runner)
        (output/"cache"/f"{job_key(jobs[0])}.json").write_text("{}")
        with self.assertRaises(ValidationError):
            collect(jobs,output,execute=True,resume=True,runner=self.runner)

    def test_access_block_pauses_same_platform_and_is_cached(self):
        output=self.root/"run"
        jobs=validate_plan([video("tiktok"),video("tiktok",2)])
        def blocked(command,timeout):
            self.calls.append(command)
            return {"returncode":0,"stdout":"test","stderr":""} if "--version" in command else \
                   {"returncode":1,"stdout":"","stderr":"HTTP Error 403: login required"}
        result=collect(jobs,output,execute=True,yt_dlp="fake",runner=blocked,sleeper=lambda _:None)
        self.assertEqual([r["status"] for r in result["results"]],["access_blocked","paused_after_access_block"])
        self.assertEqual(len([c for c in self.calls if "--version" not in c]),1)
        again=collect(jobs,output,execute=True,resume=True,runner=lambda *_:self.fail("Blocked request retried"),sleeper=lambda _:None)
        self.assertEqual(again["jobs_attempted_this_run"],0)

    def test_exa_rate_limit_pauses_remaining_searches_for_transport_and_mcp_errors(self):
        jobs=validate_plan([{"kind":"exa_search","value":query,"limit":1} for query in ("car wipers","oil change")])
        errors=[{"returncode":1,"stdout":"","stderr":"HTTP Error 429: rate limit"},
                {"returncode":0,"stdout":json.dumps({"isError":True,"content":[{"type":"text","text":"HTTP Error 403: login required"}]}),"stderr":""}]
        for index,error in enumerate(errors):
            with self.subTest(index=index), patch("scripts.local_collect.exa_prefix",return_value=["node","mcporter"]) as prefix:
                calls=[]
                def runner(*args):
                    calls.append(args)
                    return error
                result=collect(jobs,self.root/f"exa-{index}",execute=True,runner=runner,sleeper=lambda _:None)
                self.assertEqual([row["status"] for row in result["results"]],["access_blocked","paused_after_access_block"])
                self.assertEqual(len(calls),1)
                self.assertEqual(prefix.call_count,1)

    def test_duplicate_listing_and_detail_keep_more_direct_evidence(self):
        output=self.root/"run"
        jobs=validate_plan([{"kind":"youtube_search","value":"car wipers","limit":1},video()])
        def runner(command,timeout):
            if "--version" in command:
                return {"returncode":0,"stdout":"test","stderr":""}
            data=metadata(video()["value"])
            if command[-1].startswith("ytsearch"):
                data={"entries":[data]}
            else:
                data["language"]="fr-FR"
            return {"returncode":0,"stdout":json.dumps(data),"stderr":""}
        result=collect(jobs,output,execute=True,yt_dlp="fake",runner=runner,sleeper=lambda _:None)
        self.assertEqual(result["duplicate_records"],1)
        record=json.loads((output/"records.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(record["_collection"]["evidence_scope"],"public_video_metadata")
        self.assertEqual(record["language"],"fr-FR")

    def test_advanced_rate_limit_pauses_basic_search_and_resume_does_not_retry(self):
        jobs=validate_plan([{"kind":"exa_search_advanced","value":"vidange","limit":25},
                           {"kind":"exa_search","value":"car wipers","limit":2}])
        output=self.root/"advanced-blocked"
        calls=[]
        def runner(command,timeout):
            calls.append(command)
            return {"returncode":1,"stdout":"","stderr":"HTTP 429 Too Many Requests"}
        with patch("scripts.local_collect.exa_prefix",return_value=["node","mcporter"]):
            result=collect(jobs,output,execute=True,yt_dlp="unused",runner=runner,sleeper=lambda _:None)
            self.assertEqual([r["status"] for r in result["results"]],["access_blocked","paused_after_access_block"])
            self.assertEqual(len(calls),1)
            self.assertNotIn("--version",calls[0])
            collect(jobs,output,execute=True,resume=True,runner=lambda *_:self.fail("Blocked cache retried"),sleeper=lambda _:None)


if __name__=="__main__":
    unittest.main()
