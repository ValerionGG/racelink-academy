"""Persistent, bounded public-Exa discovery queue. No accounts, media or catalog writes.

The cursor advances over explicit search jobs, not over fictional Exa result pages.
All variants are retained for offline reconciliation. No candidate is published.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import uuid

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from scripts import local_collect as collector
from scripts import bulk_ingest as bulk
from scripts import scale_ingest
from server import ValidationError, utcnow

VERSION = "1.0.1"
APPLICATION_ID = 0x524C5131
GOOD = {"ok", "empty_or_unrecognized_results"}
STOP_FILE = "stop-request.json"


def collector_hash():
    return bulk.file_digest(Path(collector.__file__))


@contextmanager
def queue(directory, *, create=False):
    folder = Path(directory).resolve()
    if not folder.exists():
        if not create:
            raise ValidationError("Queue does not exist; run init first")
        folder.mkdir(parents=True)
    database = folder / "queue.sqlite3"
    lock = folder / ".queue.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValidationError("Queue is locked. Verify its process has stopped before removing a stale .queue.lock") from None
    os.write(fd, str(os.getpid()).encode("ascii"))
    os.close(fd)
    conn = None
    try:
        if database.exists():
            probe = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
            try:
                if probe.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
                    raise ValidationError("Not a social-queue database")
            finally:
                probe.close()
        elif not create or any(p.name != lock.name for p in folder.iterdir()):
            raise ValidationError("init requires an empty directory; other databases are never opened for writing")
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA synchronous=FULL")
        yield conn, folder
    finally:
        if conn is not None:
            conn.close()
        lock.unlink(missing_ok=True)


def get_meta(conn, key):
    row = conn.execute("SELECT value FROM metadata WHERE key=?", (key,)).fetchone()
    return json.loads(row[0]) if row else None


def put_meta(conn, key, value):
    conn.execute("INSERT OR REPLACE INTO metadata VALUES(?,?)", (key, json.dumps(value, ensure_ascii=False)))


def init(directory, *, request_cap=1000, daily_cap=100, result_cap=50000, interval=2):
    if any(type(x) is not int for x in (request_cap, daily_cap, result_cap)) or not (
            1 <= request_cap <= 100000 and 1 <= daily_cap <= request_cap and 1 <= result_cap <= 5000000):
        raise ValidationError("Explicit caps: requests 1–100000; daily <= total; requested rows 1–5000000")
    if not 2 <= interval <= 30:
        raise ValidationError("Minimum interval must be 2–30 seconds")
    with queue(directory, create=True) as (conn, folder):
        if conn.execute("PRAGMA application_id").fetchone()[0]:
            raise ValidationError("Queue already initialized; caps cannot be reset by init")
        conn.executescript(f"""
            PRAGMA application_id={APPLICATION_ID};
            CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE jobs(seq INTEGER PRIMARY KEY,job_key TEXT UNIQUE NOT NULL,job_json TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'pending',created_at TEXT NOT NULL);
            CREATE TABLE attempts(seq INTEGER PRIMARY KEY,job_seq INTEGER NOT NULL,started_at TEXT NOT NULL,
                utc_day TEXT NOT NULL,requested_rows INTEGER NOT NULL,state TEXT NOT NULL,
                response_json TEXT,response_sha256 TEXT,error TEXT);
            CREATE TABLE variants(seq INTEGER PRIMARY KEY,attempt_seq INTEGER NOT NULL,ordinal INTEGER NOT NULL,
                media_id TEXT NOT NULL,raw_sha256 TEXT NOT NULL,raw_json TEXT NOT NULL,
                UNIQUE(attempt_seq,ordinal));
            CREATE INDEX variants_identity ON variants(media_id,seq);
            CREATE INDEX attempts_day ON attempts(utc_day);
            CREATE TABLE events(seq INTEGER PRIMARY KEY,created_at TEXT NOT NULL,kind TEXT NOT NULL,detail TEXT NOT NULL);
        """)
        for key, value in {"version": VERSION, "queue_id": uuid.uuid4().hex, "created_at": utcnow(),
                "collector_sha256": collector_hash(), "request_cap": request_cap, "daily_cap": daily_cap,
                "collector_history": [{"sha256": collector_hash(), "version": collector.VERSION,
                                       "after_attempt": 0, "recorded_at": utcnow()}],
                "result_cap": result_cap, "interval": interval, "pause": None, "last_request_epoch": 0}.items():
            put_meta(conn, key, value)
        conn.commit()
        return summary(conn)


def summary(conn):
    states = dict(conn.execute("SELECT state,count(*) FROM jobs GROUP BY state"))
    attempts = conn.execute("SELECT count(*),coalesce(sum(requested_rows),0) FROM attempts").fetchone()
    total, unique = conn.execute("SELECT count(*),count(DISTINCT media_id) FROM variants").fetchone()
    next_job = conn.execute("SELECT min(seq) FROM jobs WHERE state='pending'").fetchone()[0]
    return {"tool": "social_queue", "version": VERSION, "queue_id": get_meta(conn, "queue_id"),
            "collector_binding_sha256": get_meta(conn, "collector_sha256"),
            "jobs": states, "next_job_cursor": next_job, "requests_reserved": attempts[0],
            "requested_rows_reserved": attempts[1], "source_variants": total, "unique_identities": unique,
            "duplicate_identity_variants": total - unique, "pause": get_meta(conn, "pause"),
            "caps": {key: get_meta(conn, key) for key in ("request_cap", "daily_cap", "result_cap")},
            "provider": "exa-public-mcp", "authenticated": False, "paid_actor_started": False,
            "catalog_modified": False, "candidate_publication": False,
            "pagination": "job cursor only; provider exposes no result-page cursor in this adapter"}


def status(directory):
    # Monitoring must remain available while the writer holds its long-lived
    # process lock. SQLite supplies one consistent read transaction; mode=ro
    # prevents creating a missing database or writing to the catalog by mistake.
    database = Path(directory).resolve() / "queue.sqlite3"
    if not database.is_file():
        raise ValidationError("Queue database does not exist")
    conn = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=2)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        if conn.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
            raise ValidationError("Not a social-queue database")
        conn.execute("BEGIN")
        return summary(conn)
    finally:
        conn.close()


def enqueue(directory, plans):
    jobs = []
    for plan in plans:
        path = Path(plan)
        if path.stat().st_size > 4 * 1024 * 1024:
            raise ValidationError("Plan exceeds 4 MiB")
        for job in collector.validate_plan(json.loads(path.read_text(encoding="utf-8"))):
            if job["kind"] not in collector.EXA_KINDS:
                raise ValidationError("This queue accepts public Exa search only, never native platform or paid actor jobs")
            jobs.append(job)
    if not jobs or len(jobs) > 20000:
        raise ValidationError("Enqueue 1–20000 validated jobs; each source plan remains bounded to 200")
    with queue(directory) as (conn, _):
        before = conn.total_changes
        for job in jobs:
            conn.execute("INSERT OR IGNORE INTO jobs(job_key,job_json,created_at) VALUES(?,?,?)",
                         (bulk.digest(job), json.dumps(job, ensure_ascii=False), utcnow()))
        added = conn.total_changes - before
        conn.commit()
        return {**summary(conn), "jobs_added": added, "duplicate_jobs_skipped": len(jobs) - added}


def reviewed_reason(reason):
    if not isinstance(reason, str) or not 10 <= len(reason.strip()) <= 500:
        raise ValidationError("Record a 10–500 character reason; never include credentials")
    return reason.strip()


def request_stop(directory, reason):
    """Set a cooperative stop without taking the running collector's writer lock."""
    reason = reviewed_reason(reason)
    info = status(directory)  # Read-only marker validation; does not create a queue.
    path = Path(directory).resolve() / STOP_FILE
    request = {"queue_id": info["queue_id"], "requested_at": utcnow(), "reason": reason}
    try:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(request, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        return {"stop_requested": True, "already_requested": True, "network_requests": 0}
    # The runner treats even a partially written/malformed stop file as a stop.
    return {"stop_requested": True, "already_requested": False, "network_requests": 0,
            "effect": "Current call may finish; a new-version runner stops before the next reservation"}


def stop_requested(conn, folder):
    path = folder / STOP_FILE
    if not path.exists():
        return False
    request = None
    try:
        if path.stat().st_size <= 4096:
            request = json.loads(path.read_text(encoding="utf-8"))
        valid = isinstance(request, dict) and request.get("queue_id") == get_meta(conn, "queue_id")
    except (OSError, UnicodeError, json.JSONDecodeError):
        valid = False
    detail = {"reason": "cooperative_stop" if valid else "invalid_stop_request", "at": utcnow(),
              "request": request if valid else None}
    put_meta(conn, "pause", detail)
    conn.execute("INSERT INTO events(created_at,kind,detail) VALUES(?,?,?)",
                 (utcnow(), "cooperative_stop", json.dumps(detail, ensure_ascii=False)))
    conn.commit()
    return True


def rebind_collector(directory, expected_old_hash, reason):
    """Explicit local code migration; never resets state, quotas, or old evidence."""
    reason = reviewed_reason(reason)
    if not isinstance(expected_old_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_old_hash):
        raise ValidationError("expected-old-hash must be the exact previous SHA256")
    with queue(directory) as (conn, _):  # Exclusive lock; refuses an active runner.
        old_hash = get_meta(conn, "collector_sha256")
        if old_hash != expected_old_hash:
            raise ValidationError("Collector binding changed or wrong previous SHA256; no migration made")
        if conn.execute("SELECT 1 FROM jobs WHERE state='running' LIMIT 1").fetchone() or conn.execute(
                "SELECT 1 FROM attempts WHERE state='reserved' LIMIT 1").fetchone():
            raise ValidationError("Resolve running/uncertain reservations before rebinding the collector")
        new_hash = collector_hash()
        if new_hash == old_hash:
            raise ValidationError("Collector hash is unchanged; no migration is needed")
        cursor = conn.execute("SELECT coalesce(max(seq),0) FROM attempts").fetchone()[0]
        history = get_meta(conn, "collector_history") or [{"sha256": old_hash,
            "version": "not_recorded_in_legacy_queue", "after_attempt": 0}]
        migration = {"old_sha256": old_hash, "new_sha256": new_hash, "reason": reason,
                     "after_attempt": cursor, "at": utcnow(), "new_collector_version": collector.VERSION}
        history.append({"sha256": new_hash, "version": collector.VERSION,
                        "after_attempt": cursor, "recorded_at": migration["at"]})
        put_meta(conn, "collector_history", history)
        put_meta(conn, "collector_sha256", new_hash)
        conn.execute("INSERT INTO events(created_at,kind,detail) VALUES(?,?,?)",
                     (migration["at"], "collector_rebound", json.dumps(migration, ensure_ascii=False)))
        conn.commit()
        return {**summary(conn), "migration": migration,
                "preserved": ["attempts", "request reservations", "quotas", "jobs", "variants", "pause"]}


def run(directory, *, execute=False, max_jobs=10, max_seconds=600, timeout=45, mcporter_js=None,
        runner=collector.process, sleeper=time.sleep, clock=time.time):
    if type(max_jobs) is not int or not 1 <= max_jobs <= 200 or not 10 <= max_seconds <= 3600 or not 10 <= timeout <= 120:
        raise ValidationError("Bound a run to 1–200 jobs, 10–3600 seconds and 10–120 seconds per call")
    with queue(directory) as (conn, folder):
        if get_meta(conn, "collector_sha256") != collector_hash():
            raise ValidationError("Collector changed; use a new queue or explicit audited rebind-collector")
        info = summary(conn)
        if not execute:
            return {**info, "mode": "preview", "max_jobs_this_run": max_jobs, "network_requests": 0}
        if info["pause"]:
            return {**info, "mode": "paused", "network_requests_this_run": 0}
        if conn.execute("SELECT 1 FROM jobs WHERE state='running' LIMIT 1").fetchone():
            # The durable reservation already consumed quota. Never silently repeat
            # a request whose response was lost between the network and the commit.
            put_meta(conn, "pause", {"reason": "uncertain_interrupted_request", "at": utcnow()})
            conn.commit()
            return {**summary(conn), "mode": "paused", "network_requests_this_run": 0}
        if stop_requested(conn, folder):
            return {**summary(conn), "mode": "paused", "network_requests_this_run": 0}
        # Resolve existing runtime before consuming a request reservation.
        prefix = collector.exa_prefix(mcporter_js)
        deadline = clock() + max_seconds
        attempted, stop_reason = 0, "run_limit"
        while attempted < max_jobs:
            if stop_requested(conn, folder):
                stop_reason = "cooperative_stop"
                break
            job_row = conn.execute("SELECT * FROM jobs WHERE state='pending' ORDER BY seq LIMIT 1").fetchone()
            if not job_row:
                stop_reason = "queue_complete"
                break
            job = json.loads(job_row["job_json"])
            now = clock()
            day = datetime.fromtimestamp(now, timezone.utc).date().isoformat()
            used = conn.execute("SELECT count(*),coalesce(sum(requested_rows),0) FROM attempts").fetchone()
            daily = conn.execute("SELECT count(*) FROM attempts WHERE utc_day=?", (day,)).fetchone()[0]
            if used[0] >= get_meta(conn, "request_cap") or used[1] + job["limit"] > get_meta(conn, "result_cap"):
                stop_reason = "lifetime_cap"
                break
            if daily >= get_meta(conn, "daily_cap"):
                stop_reason = "daily_cap"
                break
            delay = max(0, get_meta(conn, "last_request_epoch") + get_meta(conn, "interval") - now)
            if now + delay + timeout > deadline:
                stop_reason = "time_budget"
                break
            if delay:
                sleeper(delay)
            if stop_requested(conn, folder):
                stop_reason = "cooperative_stop"
                break
            # Reserve atomically before calling the subprocess. Even a crash cannot
            # reset this cumulative budget or accidentally publish a partial result.
            started = clock()
            day = datetime.fromtimestamp(started, timezone.utc).date().isoformat()
            cursor = conn.execute("INSERT INTO attempts(job_seq,started_at,utc_day,requested_rows,state) VALUES(?,?,?,?,?)",
                                  (job_row["seq"], utcnow(), day, job["limit"], "reserved"))
            attempt = cursor.lastrowid
            conn.execute("UPDATE jobs SET state='running' WHERE seq=?", (job_row["seq"],))
            put_meta(conn, "last_request_epoch", started)
            conn.commit()
            attempted += 1
            try:
                result = collector.collect_exa(job, prefix, runner=runner, timeout=timeout)
            except Exception:
                # Do not serialize arbitrary exception text: it can contain secrets
                # from a dependency. Resume diagnoses this durable uncertain state.
                put_meta(conn, "pause", {"reason": "uncertain_collector_exception", "at": utcnow()})
                conn.commit()
                raise ValidationError("Collector raised an exception; reservation retained, queue paused") from None
            encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
            result_hash = bulk.digest(result)
            error = collector.sanitized_error(result.get("error") or "")
            state = "done" if result["status"] in GOOD else "failed"
            for index, raw in enumerate(result.get("records", [])):
                identity, _, _ = bulk.identity(raw.get("webpage_url") or raw.get("url"))
                conn.execute("INSERT INTO variants(attempt_seq,ordinal,media_id,raw_sha256,raw_json) VALUES(?,?,?,?,?)",
                             (attempt, index, identity, bulk.digest(raw), json.dumps(raw, ensure_ascii=False)))
            conn.execute("UPDATE attempts SET state=?,response_json=?,response_sha256=?,error=? WHERE seq=?",
                         (result["status"], encoded, result_hash, error, attempt))
            conn.execute("UPDATE jobs SET state=? WHERE seq=?", (state, job_row["seq"]))
            if state == "failed":
                put_meta(conn, "pause", {"reason": result["status"], "at": utcnow(), "attempt": attempt,
                          "instruction": "Inspect service availability; no automatic retry or bypass"})
            conn.commit()
            if state == "failed":
                stop_reason = result["status"]
                break
        report = {**summary(conn), "mode": "execute", "network_requests_this_run": attempted, "stop_reason": stop_reason}
        bulk.atomic_json(folder / "last-run.json", report)
        return report


def resume_after_review(directory, reason, *, retry_job=None):
    reason = reviewed_reason(reason)
    with queue(directory) as (conn, folder):
        if not get_meta(conn, "pause"):
            raise ValidationError("Queue is not paused")
        if retry_job is not None:
            row = conn.execute("SELECT state FROM jobs WHERE seq=?", (retry_job,)).fetchone()
            if not row or row[0] not in {"failed", "running"}:
                raise ValidationError("Only the explicitly selected failed/uncertain job can be retried")
        conn.execute("UPDATE jobs SET state='uncertain' WHERE state='running'")
        conn.execute("UPDATE attempts SET state='outcome_unknown' WHERE state='reserved'")
        if retry_job is not None:
            conn.execute("UPDATE jobs SET state='pending' WHERE seq=?", (retry_job,))
        conn.execute("INSERT INTO events(created_at,kind,detail) VALUES(?,?,?)",
                     (utcnow(), "resume_after_review", json.dumps({"reason": reason.strip(), "retry_job": retry_job})))
        # Remove the consumed marker before committing resume. A stop requested
        # concurrently after this unlink remains present for the next run.
        (folder / STOP_FILE).unlink(missing_ok=True)
        put_meta(conn, "pause", None)
        conn.commit()
        return summary(conn)


def snapshot(directory, output):
    target = Path(output).resolve()
    with queue(directory) as (conn, folder):
        if target == folder or target.is_relative_to(folder) or folder.is_relative_to(target):
            raise ValidationError("Snapshot must be separate from the queue directory")
        if target.exists():
            raise ValidationError("Use a new immutable snapshot directory")
        if conn.execute("SELECT 1 FROM jobs WHERE state='running' LIMIT 1").fetchone():
            raise ValidationError("Resolve the uncertain request before producing a review snapshot")
        for attempt in conn.execute("SELECT response_json,response_sha256 FROM attempts WHERE response_json IS NOT NULL"):
            if bulk.digest(json.loads(attempt[0])) != attempt[1]:
                raise ValidationError("Stored response evidence changed")
        if not conn.execute("SELECT 1 FROM variants LIMIT 1").fetchone():
            raise ValidationError("No source variants to prepare")
        target.mkdir(parents=True)
        raw_path = target / "source-variants.jsonl"
        try:
            with raw_path.open("x", encoding="utf-8", newline="\n") as stream:
                for row in conn.execute("SELECT raw_json,raw_sha256 FROM variants ORDER BY seq"):
                    if bulk.digest(json.loads(row[0])) != row[1]:
                        raise ValidationError("Stored variant evidence changed")
                    stream.write(row[0] + "\n")
            manifest = {**summary(conn), "created_at": utcnow(), "source_file": raw_path.name,
                        "source_sha256": bulk.file_digest(raw_path), "collector_sha256": get_meta(conn, "collector_sha256"),
                        "collector_sha256_scope": "current binding; historical attempts use collector_history epochs",
                        "collector_history": get_meta(conn, "collector_history") or [{
                            "sha256": get_meta(conn, "collector_sha256"), "after_attempt": 0,
                            "version": "not_recorded_in_legacy_queue"}],
                        "snapshot_variant_cursor": conn.execute("SELECT max(seq) FROM variants").fetchone()[0],
                        "complete_collection": not conn.execute("SELECT 1 FROM jobs WHERE state!='done' LIMIT 1").fetchone(),
                        "review_required": True, "import_authorized": False,
                        "warning": "Later snapshots may add conflicting evidence; no automatic approval transfer"}
            bulk.atomic_json(target / "manifest.json", manifest)
            return manifest
        except BaseException:
            # Incomplete directories are deliberately left without a valid manifest.
            raise


def prepare(snapshot_dir, output, *, max_records=25000, batch_size=1000, max_batches=10):
    snapshot_dir, output = Path(snapshot_dir).resolve(), Path(output).resolve()
    manifest = json.loads((snapshot_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("source_file") != "source-variants.jsonl" or manifest.get("tool") != "social_queue":
        raise ValidationError("Use a social-queue snapshot manifest")
    source = snapshot_dir / manifest["source_file"]
    if bulk.file_digest(source) != manifest["source_sha256"]:
        raise ValidationError("Snapshot source changed; preparation refused")
    if output == snapshot_dir or output.is_relative_to(snapshot_dir) or snapshot_dir.is_relative_to(output):
        raise ValidationError("Review output must be separate from immutable evidence")
    staged = scale_ingest.stage([source], output / "stage", max_records=max_records, resume=True)
    if not staged["complete"]:
        return {"mode": "staging_only", "complete": False, "stage": staged, "next_action": "Repeat identical prepare command"}
    reviewed = scale_ingest.prepare(output / "stage", output / "review", batch_size=batch_size,
                                    max_batches=max_batches, resume=True)
    return {"mode": "review_only", "complete": reviewed["complete"], "stage": staged, "review": reviewed,
            "approval": "Empty approval templates only. No publication or catalog import is implemented."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("init"); create.add_argument("--queue", required=True, type=Path)
    create.add_argument("--request-cap", type=int, default=1000); create.add_argument("--daily-cap", type=int, default=100)
    create.add_argument("--result-cap", type=int, default=50000); create.add_argument("--interval", type=float, default=2)
    add = sub.add_parser("enqueue"); add.add_argument("--queue", required=True, type=Path); add.add_argument("plans", nargs="+", type=Path)
    execute = sub.add_parser("run"); execute.add_argument("--queue", required=True, type=Path)
    execute.add_argument("--execute", action="store_true"); execute.add_argument("--max-jobs", type=int, default=10)
    execute.add_argument("--max-seconds", type=int, default=600); execute.add_argument("--timeout", type=int, default=45)
    execute.add_argument("--mcporter-js", type=Path)
    inspect = sub.add_parser("status"); inspect.add_argument("--queue", required=True, type=Path)
    stop = sub.add_parser("request-stop"); stop.add_argument("--queue", required=True, type=Path)
    stop.add_argument("--reason", required=True)
    bind = sub.add_parser("rebind-collector"); bind.add_argument("--queue", required=True, type=Path)
    bind.add_argument("--expected-old-hash", required=True); bind.add_argument("--reason", required=True)
    resume = sub.add_parser("resume-after-review"); resume.add_argument("--queue", required=True, type=Path)
    resume.add_argument("--reason", required=True); resume.add_argument("--retry-job", type=int)
    snap = sub.add_parser("snapshot"); snap.add_argument("--queue", required=True, type=Path); snap.add_argument("--output", required=True, type=Path)
    prep = sub.add_parser("prepare"); prep.add_argument("--snapshot", required=True, type=Path); prep.add_argument("--output", required=True, type=Path)
    prep.add_argument("--max-records", type=int, default=25000); prep.add_argument("--batch-size", type=int, default=1000)
    prep.add_argument("--max-batches", type=int, default=10)
    args = vars(parser.parse_args(argv)); command = args.pop("command")
    if "queue" in args: args["directory"] = args.pop("queue")
    if "snapshot" in args: args["snapshot_dir"] = args.pop("snapshot")
    functions = {"init": init, "enqueue": enqueue, "run": run, "status": status,
                 "request-stop": request_stop, "rebind-collector": rebind_collector,
                 "resume-after-review": resume_after_review, "snapshot": snapshot, "prepare": prepare}
    try:
        print(json.dumps(functions[command](**args), ensure_ascii=True))
    except (ValidationError, OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        parser.exit(2, "SOCIAL_QUEUE: " + str(exc).encode("ascii", "backslashreplace").decode() + "\n")


if __name__ == "__main__":
    main()
