"""Offline integration tests; all metadata is synthetic and only temporary queues are written."""
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts import social_queue as q
from scripts import local_collect
from server import ValidationError


def job(number=1, limit=2):
    return {"kind": "exa_search_advanced", "value": f"comment changer essuie glace voiture {number}",
            "limit": limit, "include_domains": ["instagram.com", "tiktok.com"],
            "include_text": ["voiture"], "user_location": "FR"}


def result(number=1, title="How to replace car wipers — synthetic fixture", url=None):
    return {"url": url or f"https://www.instagram.com/reel/Fixture{number:05}/",
            "title": title, "text": "Composite snippet must not become a verified caption."}


def response(*entries):
    return {"returncode": 0, "stderr": "", "stdout": json.dumps({"content": [
        {"type": "text", "text": json.dumps({"results": list(entries)})}]})}


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.cleanup_temp)
        self.root = Path(self.temp.name)
        self.directory = self.root / "queue"
        self.prefix = patch.object(local_collect, "exa_prefix", return_value=["synthetic-mcporter"])
        self.prefix.start(); self.addCleanup(self.prefix.stop)
        self.calls = []

    def cleanup_temp(self):
        # Windows indexers can briefly keep an already-closed temp directory busy.
        # Retry only this test's TemporaryDirectory, never arbitrary input paths.
        for attempt in range(5):
            try:
                self.temp.cleanup()
                return
            except OSError:
                if attempt == 4: raise
                time.sleep(.1 * (attempt + 1))

    def setup_queue(self, jobs=None, **caps):
        q.init(self.directory, **caps)
        p = self.root / "plan.json"
        p.write_text(json.dumps({"jobs": jobs or [job()]}), encoding="utf-8")
        return q.enqueue(self.directory, [p])

    def run_queue(self, data=None, **kwargs):
        def runner(command, timeout):
            self.calls.append(command)
            return data if data is not None else response(result(len(self.calls)))
        return q.run(self.directory, execute=True, runner=runner, sleeper=lambda _: None,
                     clock=lambda: 1793000000, **kwargs)

    def test_preview_never_resolves_runtime_or_calls_network(self):
        self.setup_queue()
        with patch.object(local_collect, "exa_prefix", side_effect=AssertionError("runtime touched")):
            report = q.run(self.directory)
        self.assertEqual(report["network_requests"], 0)
        self.assertEqual(report["requests_reserved"], 0)

    def test_duplicate_jobs_collapse_across_enqueue_calls(self):
        first = self.setup_queue([job(), job()])
        self.assertEqual(first["jobs_added"], 1)
        second = q.enqueue(self.directory, [self.root / "plan.json"])
        self.assertEqual(second["jobs_added"], 0)
        self.assertEqual(second["duplicate_jobs_skipped"], 1)

    def test_native_platform_and_paid_fields_are_refused(self):
        q.init(self.directory)
        for value in ({"kind": "video", "value": "https://www.tiktok.com/@fixture/video/1234567890123456789"},
                      job() | {"token": "synthetic"}, job() | {"actor": "paid"}):
            p = self.root / "bad.json"; p.write_text(json.dumps([value]), encoding="utf-8")
            with self.assertRaises(ValidationError): q.enqueue(self.directory, [p])
        self.assertEqual(q.status(self.directory)["jobs"], {})

    def test_foreign_database_is_not_modified(self):
        self.directory.mkdir()
        db = self.directory / "queue.sqlite3"
        c = sqlite3.connect(db); c.execute("CREATE TABLE private_data(x)"); c.close()
        before = db.read_bytes()
        with self.assertRaises(ValidationError): q.init(self.directory)
        self.assertEqual(before, db.read_bytes())

    def test_caps_cannot_be_reset_and_lock_refuses_concurrent_run(self):
        self.setup_queue()
        with self.assertRaises(ValidationError): q.init(self.directory)
        (self.directory / ".queue.lock").write_text("fixture")
        with self.assertRaises(ValidationError): self.run_queue()
        self.assertEqual(self.calls, [])

    def test_readonly_status_works_during_writer_lock_and_cannot_create_database(self):
        self.setup_queue()
        database = self.directory / "queue.sqlite3"
        with q.queue(self.directory):
            before = database.read_bytes()
            self.assertEqual(q.status(self.directory)["jobs"], {"pending": 1})
            self.assertEqual(before, database.read_bytes())
        missing = self.root / "does-not-exist"
        with self.assertRaises(ValidationError): q.status(missing)
        self.assertFalse(missing.exists())

    def test_lifetime_quota_survives_multiple_runs(self):
        self.setup_queue([job(1), job(2), job(3)], request_cap=2, daily_cap=2)
        self.run_queue(max_jobs=1)
        report = self.run_queue(max_jobs=10)
        self.assertEqual(report["stop_reason"], "lifetime_cap")
        self.assertEqual(report["requests_reserved"], 2)
        self.assertEqual(report["jobs"]["pending"], 1)
        self.assertEqual(len(self.calls), 2)

    def test_daily_quota_is_utc_and_next_day_resumes_remaining_job(self):
        self.setup_queue([job(1), job(2)], request_cap=3, daily_cap=1)
        report = self.run_queue()
        self.assertEqual(report["stop_reason"], "daily_cap")
        report = q.run(self.directory, execute=True, clock=lambda: 1793086400,
                       sleeper=lambda _: None, runner=lambda *_: response(result(2)))
        self.assertEqual(report["requests_reserved"], 2)
        self.assertEqual(report["jobs"], {"done": 2})

    def test_requested_row_cap_applies_before_call_not_to_actual_yield(self):
        self.setup_queue([job(1, 50), job(2, 50)], result_cap=60)
        report = self.run_queue(data=response())
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(report["requested_rows_reserved"], 50)
        self.assertEqual(report["source_variants"], 0)

    def test_time_budget_and_dependency_failure_spend_no_request(self):
        self.setup_queue()
        self.assertEqual(self.run_queue(max_seconds=10)["stop_reason"], "time_budget")
        with patch.object(local_collect, "exa_prefix", side_effect=ValidationError("missing runtime")):
            with self.assertRaises(ValidationError): self.run_queue()
        self.assertEqual(q.status(self.directory)["requests_reserved"], 0)

    def test_403_429_pause_survives_run_and_never_automatically_retries(self):
        self.setup_queue([job(1), job(2)])
        report = self.run_queue(data={"returncode": 1, "stdout": "", "stderr": "HTTP 429 Too Many Requests"})
        self.assertEqual(report["pause"]["reason"], "access_blocked")
        report = self.run_queue()
        self.assertEqual(report["network_requests_this_run"], 0)
        self.assertEqual(len(self.calls), 1)
        resumed = q.resume_after_review(self.directory, "Synthetic test: service access restored")
        self.assertEqual(resumed["jobs"], {"failed": 1, "pending": 1})
        self.run_queue()
        self.assertEqual(len(self.calls), 2)

    def test_explicit_retry_consumes_another_reservation(self):
        self.setup_queue()
        self.run_queue(data={"returncode": 1, "stdout": "", "stderr": "HTTP 403 Forbidden"})
        q.resume_after_review(self.directory, "Synthetic test: restored service confirmed", retry_job=1)
        report = self.run_queue()
        self.assertEqual(report["requests_reserved"], 2)
        self.assertEqual(report["jobs"], {"done": 1})

    def test_crash_after_reservation_never_loses_quota_or_repeats_automatically(self):
        self.setup_queue([job(1), job(2)])
        def crash(*_): raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            q.run(self.directory, execute=True, runner=crash, clock=lambda: 1793000000)
        report = self.run_queue()
        self.assertEqual(report["requests_reserved"], 1)
        self.assertEqual(report["pause"]["reason"], "uncertain_interrupted_request")
        self.assertEqual(len(self.calls), 0)
        with self.assertRaises(ValidationError): q.snapshot(self.directory, self.root / "invalid-snapshot")
        q.resume_after_review(self.directory, "Synthetic test: skipped uncertain request")
        self.run_queue()
        self.assertEqual(q.status(self.directory)["jobs"], {"done": 1, "uncertain": 1})

    def test_exception_is_paused_without_leaking_error_text(self):
        self.setup_queue()
        def crash(*_): raise RuntimeError("SECRET_FIXTURE_must_not_leak")
        with self.assertRaises(ValidationError) as caught:
            q.run(self.directory, execute=True, runner=crash)
        self.assertNotIn("SECRET_FIXTURE", str(caught.exception))
        self.assertNotIn("SECRET_FIXTURE", (self.directory / "queue.sqlite3").read_bytes().decode("utf-8", "ignore"))
        self.assertEqual(q.status(self.directory)["requests_reserved"], 1)

    def test_unknown_response_halts_instead_of_making_empty_success_claim(self):
        self.setup_queue([job(1), job(2)])
        self.run_queue(data={"returncode": 1, "stdout": "", "stderr": "Transient server error"})
        self.assertEqual(len(self.calls), 1)
        self.assertIsNotNone(q.status(self.directory)["pause"])

    def test_same_identity_variants_are_preserved_and_unicode_is_one_jsonl_line(self):
        self.setup_queue([job(1), job(2)])
        self.run_queue(data=response(result(1, "Comment changer les essuie-glaces de voiture\u2028Étapes")))
        report = q.status(self.directory)
        self.assertEqual(report["source_variants"], 2)
        self.assertEqual(report["unique_identities"], 1)
        snap = self.root / "snapshot"
        manifest = q.snapshot(self.directory, snap)
        with (snap / "source-variants.jsonl").open(encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream]
        self.assertEqual(len(rows), 2)
        self.assertFalse(manifest["import_authorized"])
        self.assertEqual(rows[0]["_collection"]["evidence_scope"], "indexed_search_metadata")
        self.assertFalse(rows[0]["_collection"]["audio_language_verified"])

    def test_snapshot_is_immutable_and_append_requires_new_snapshot(self):
        self.setup_queue([job(1), job(2)])
        self.run_queue(max_jobs=1)
        snap = self.root / "snapshot"; before = q.snapshot(self.directory, snap)
        original = (snap / "source-variants.jsonl").read_bytes()
        self.run_queue()
        with self.assertRaises(ValidationError): q.snapshot(self.directory, snap)
        self.assertEqual(original, (snap / "source-variants.jsonl").read_bytes())
        self.assertFalse(before["complete_collection"])
        self.assertTrue(q.snapshot(self.directory, self.root / "snapshot2")["complete_collection"])

    def test_changed_response_or_source_evidence_is_refused(self):
        self.setup_queue(); self.run_queue()
        with q.queue(self.directory) as (conn, _):
            conn.execute("UPDATE attempts SET response_sha256='tampered'"); conn.commit()
        with self.assertRaises(ValidationError): q.snapshot(self.directory, self.root / "snapshot")

    def test_prepare_is_bounded_resumable_and_approval_is_empty(self):
        self.setup_queue([job(1), job(2)]); self.run_queue()
        snap = self.root / "snapshot"; q.snapshot(self.directory, snap)
        first = q.prepare(snap, self.root / "prepared", max_records=1, batch_size=1, max_batches=1)
        self.assertFalse(first["complete"])
        second = q.prepare(snap, self.root / "prepared", max_records=1, batch_size=1, max_batches=1)
        self.assertFalse(second["complete"])
        third = q.prepare(snap, self.root / "prepared", max_records=1, batch_size=1, max_batches=1)
        self.assertTrue(third["complete"])
        packets = list((self.root / "prepared/review").glob("batch-*/approval.template.json"))
        self.assertEqual(len(packets), 2)
        for packet in packets: self.assertEqual(json.loads(packet.read_text())["approved_ids"], [])
        accepted = json.loads((packets[0].parent / "accepted.json").read_text(encoding="utf-8"))
        self.assertEqual(accepted[0]["description"], "")
        self.assertEqual(accepted[0]["review_status"], "candidate")
        self.assertFalse(accepted[0]["transcriptImported"])

    def test_later_promo_variant_is_not_discarded_by_identity_dedupe(self):
        self.setup_queue([job(1), job(2)])
        self.run_queue(max_jobs=1, data=response(result(1)))
        self.run_queue(data=response(result(1, "Buy car wipers now! Discount code SALE, link in bio, sponsored")))
        snap = self.root / "snapshot"; q.snapshot(self.directory, snap)
        report = q.prepare(snap, self.root / "prepared")
        self.assertEqual(report["review"]["source_records"], 2)
        self.assertEqual(report["review"]["accepted_candidates"], 0)
        self.assertEqual(report["review"]["quarantined"], 1)

    def test_snapshot_hash_and_engine_change_are_fail_closed(self):
        self.setup_queue(); self.run_queue()
        snap = self.root / "snapshot"; q.snapshot(self.directory, snap)
        with (snap / "source-variants.jsonl").open("a", encoding="utf-8") as stream: stream.write("{}\n")
        with self.assertRaises(ValidationError): q.prepare(snap, self.root / "prepared")
        with patch.object(q, "collector_hash", return_value="new engine"):
            with self.assertRaises(ValidationError): self.run_queue()

    def test_stop_request_before_run_prevents_runtime_resolution_and_reservation(self):
        self.setup_queue()
        q.request_stop(self.directory, "Synthetic test: operator requested a pause")
        with patch.object(local_collect, "exa_prefix", side_effect=AssertionError("runtime touched")):
            report = q.run(self.directory, execute=True)
        self.assertEqual(report["pause"]["reason"], "cooperative_stop")
        self.assertEqual(report["requests_reserved"], 0)
        self.assertTrue(q.request_stop(self.directory, "Synthetic test: duplicate stop")["already_requested"])
        q.resume_after_review(self.directory, "Synthetic test: operator resumes collection")
        self.assertFalse((self.directory / q.STOP_FILE).exists())
        self.assertEqual(self.run_queue()["jobs"], {"done": 1})

    def test_cooperative_stop_during_call_retains_result_and_skips_next_request(self):
        self.setup_queue([job(1), job(2)])
        def runner(*_):
            q.request_stop(self.directory, "Synthetic test: pause while response is pending")
            return response(result())
        report = q.run(self.directory, execute=True, runner=runner)
        self.assertEqual(report["network_requests_this_run"], 1)
        self.assertEqual(report["source_variants"], 1)
        self.assertEqual(report["jobs"], {"done": 1, "pending": 1})
        self.assertEqual(report["pause"]["reason"], "cooperative_stop")

    def test_stop_request_during_rate_delay_prevents_second_reservation(self):
        self.setup_queue([job(1), job(2)])
        def sleeper(_): q.request_stop(self.directory, "Synthetic test: pause during rate delay")
        report = q.run(self.directory, execute=True, runner=lambda *_: response(result()),
                       clock=lambda: 1793000000, sleeper=sleeper)
        self.assertEqual(report["requests_reserved"], 1)
        self.assertEqual(report["jobs"]["pending"], 1)

    def test_invalid_stop_file_fails_closed(self):
        self.setup_queue()
        (self.directory / q.STOP_FILE).write_text('{"queue_id":', encoding="utf-8")
        report = self.run_queue()
        self.assertEqual(report["pause"]["reason"], "invalid_stop_request")
        self.assertEqual(self.calls, [])

    def test_rebind_refuses_lock_wrong_hash_and_unresolved_request(self):
        self.setup_queue()
        old = q.collector_hash()
        with q.queue(self.directory):
            with self.assertRaises(ValidationError):
                q.rebind_collector(self.directory, old, "Synthetic test: reviewed safe code change")
        with patch.object(q, "collector_hash", return_value="a" * 64):
            with self.assertRaises(ValidationError):
                q.rebind_collector(self.directory, "b" * 64, "Synthetic test: wrong prior hash")
            with q.queue(self.directory) as (conn, _):
                conn.execute("UPDATE jobs SET state='running'"); conn.commit()
            with self.assertRaises(ValidationError):
                q.rebind_collector(self.directory, old, "Synthetic test: unresolved job")
        self.assertEqual(q.status(self.directory)["collector_binding_sha256"], old)

    def test_rebind_preserves_quotas_jobs_evidence_and_audits_epochs(self):
        self.setup_queue([job(1), job(2)])
        self.run_queue(max_jobs=1)
        old = q.collector_hash()
        with q.queue(self.directory) as (conn, _):
            before = {table: [tuple(r) for r in conn.execute("SELECT * FROM " + table)]
                      for table in ("jobs", "attempts", "variants")}
            old_caps = {key: q.get_meta(conn, key) for key in ("request_cap", "daily_cap", "result_cap")}
        with patch.object(q, "collector_hash", return_value="a" * 64):
            migrated = q.rebind_collector(self.directory, old, "Synthetic test: reviewed transport cleanup")
            self.assertEqual(migrated["requests_reserved"], 1)
            with q.queue(self.directory) as (conn, _):
                for table, rows in before.items():
                    self.assertEqual(rows, [tuple(r) for r in conn.execute("SELECT * FROM " + table)])
                self.assertEqual(old_caps, {key: q.get_meta(conn, key) for key in old_caps})
                event = json.loads(conn.execute("SELECT detail FROM events WHERE kind='collector_rebound'").fetchone()[0])
                self.assertEqual(event["old_sha256"], old)
                self.assertEqual(event["new_sha256"], "a" * 64)
                self.assertEqual(event["after_attempt"], 1)
            self.run_queue()
            manifest = q.snapshot(self.directory, self.root / "snapshot")
        self.assertEqual(manifest["collector_history"][0]["sha256"], old)
        self.assertEqual(manifest["collector_history"][-1]["after_attempt"], 1)
        self.assertEqual(manifest["requests_reserved"], 2)

    def test_rebind_legacy_queue_keeps_old_epoch_and_existing_pause(self):
        self.setup_queue()
        old = q.collector_hash()
        with q.queue(self.directory) as (conn, _):
            conn.execute("DELETE FROM metadata WHERE key='collector_history'")
            q.put_meta(conn, "pause", {"reason": "access_blocked"}); conn.commit()
        with patch.object(q, "collector_hash", return_value="c" * 64):
            report = q.rebind_collector(self.directory, old, "Synthetic test: reviewed legacy migration")
            self.assertEqual(report["pause"], {"reason": "access_blocked"})
            with q.queue(self.directory) as (conn, _):
                self.assertEqual(q.get_meta(conn, "collector_history")[0]["sha256"], old)
                self.assertEqual(q.get_meta(conn, "collector_history")[0]["after_attempt"], 0)


if __name__ == "__main__": unittest.main()
