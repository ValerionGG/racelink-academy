#!/usr/bin/env python3
"""Bounded Bright Data Web Scraper client. Preview by default; no auth setup.

Only BRIGHTDATA_API_KEY is read. A fresh UI free-credit ledger is mandatory.
POST reservations survive failures; POST is never retried. GET collection is separate.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "28.0.0"
API = "https://api.brightdata.com"
MAX_BYTES = 32 * 1024 * 1024
MAX_CREDITS = 4000
MARGIN = 1000
DATASETS = {
    "gd_lyclm20il4r5helnj": {"platform": "instagram", "discover_by": "url", "country": "country_code"},
    "gd_lu702nij2f790tmv9h": {"platform": "tiktok", "discover_by": "profile_url", "country": "country"},
    "gd_m7n5v2gq296pex2f5m": {"platform": "tiktok", "discover_by": None, "country": None},
}
SAFE_FIELDS = {
    "instagram": {"url", "post_id", "shortcode", "user_posted", "description", "hashtags", "date_posted",
                  "product_type", "length", "thumbnail", "is_paid_partnership", "is_ad", "is_private", "isPrivate", "private", "availability",
                  "is_video", "isVideo", "is_photo", "isPhoto", "is_story", "isStory"},
    "tiktok": {"url", "post_id", "profile_username", "profile_url", "account_id", "description", "hashtags", "create_time", "post_type",
               "video_duration", "preview_image", "is_ad", "is_private", "isPrivate", "private", "availability",
               "is_video", "isVideo", "is_photo", "isPhoto", "is_story", "isStory"},
}


class ClientError(ValueError):
    pass


class TransportError(ClientError):
    pass


def now():
    return datetime.now(timezone.utc)


def stamp():
    return now().isoformat().replace("+00:00", "Z")


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ClientError("Invalid " + label)
    return value


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed
    except (ValueError, AttributeError):
        raise ClientError("Expected a timezone-aware observation timestamp") from None


def read(path, max_bytes=MAX_BYTES):
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ClientError("Expected a regular local JSON file")
    with path.open("rb") as stream:
        data = stream.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ClientError("JSON file exceeds its bound")
    try:
        return json.loads(data.decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        raise ClientError("Invalid local JSON") from None


def atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    if path.is_symlink() or temporary.is_symlink():
        raise ClientError("Symlink output refused")
    with temporary.open("wb") as stream:
        stream.write(encoded(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


@contextmanager
def locked(folder):
    """OS lock is released on crash; durable reserved state is never reset."""
    folder = Path(folder).resolve()
    if not folder.is_dir() or (folder / "state.lock").is_symlink():
        raise ClientError("Expected an initialized campaign directory")
    with (folder / "state.lock").open("a+b") as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ClientError("Campaign is busy; no concurrent requests") from None
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def job_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", value):
        raise ClientError("Invalid job ID")
    return value


def snapshot(value):
    if not isinstance(value, str) or not re.fullmatch(r"sd_[A-Za-z0-9_-]{5,100}", value):
        raise ClientError("Invalid snapshot ID")
    return value


def validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != {"id", "dataset_id", "limit_per_input", "inputs"}:
        raise ClientError("Expected only id, dataset_id, limit_per_input and inputs")
    job_id(plan["id"])
    if plan["dataset_id"] not in DATASETS:
        raise ClientError("Only validated Instagram reels and TikTok profile contracts are enabled")
    spec = DATASETS[plan["dataset_id"]]
    limit = integer(plan["limit_per_input"], 1, 1000, "per-profile limit")
    if not isinstance(plan["inputs"], list) or not 1 <= len(plan["inputs"]) <= 40:
        raise ClientError("Provide 1–40 explicit public profiles")
    normalized, profiles = [], set()
    for row in plan["inputs"]:
        allowed = {"url", "num_of_posts", "start_date", "end_date"} | ({spec["country"]} if spec["country"] else set())
        if not isinstance(row, dict) or not {"url", "num_of_posts"} <= set(row) <= allowed:
            raise ClientError("Unexpected profile input fields")
        integer(row["num_of_posts"], 1, limit, "num_of_posts (must not exceed per-input limit)")
        try:
            url = urllib.parse.urlsplit(row["url"])
            if url.scheme != "https" or url.hostname not in {spec["platform"] + ".com", "www." + spec["platform"] + ".com"} or url.port or url.username or url.password or url.query or url.fragment:
                raise ValueError()
        except (ValueError, AttributeError, TypeError):
            raise ClientError("Expected a public HTTPS profile URL without query or credentials") from None
        pattern = r"/@([A-Za-z0-9._]{1,30})/?" if spec["platform"] == "tiktok" else r"/([A-Za-z0-9._]{1,30})/?"
        match = re.fullmatch(pattern, url.path)
        if not match or match[1].lower() in {"reel", "reels", "p", "explore", "accounts", "about", "login"}:
            raise ClientError("Expected a profile URL, not a post or search route")
        handle = match[1]
        if handle.lower() in profiles:
            raise ClientError("Duplicate profile input")
        profiles.add(handle.lower())
        canonical = f"https://www.{spec['platform']}.com/" + ("@" if spec["platform"] == "tiktok" else "") + handle + ("/" if spec["platform"] == "instagram" else "")
        country = row.get(spec["country"], "") if spec["country"] else ""
        if not isinstance(country, str) or not re.fullmatch(r"(?:[A-Z]{2})?", country):
            raise ClientError("Country must be empty or an explicit two-letter code")
        dates = {}
        for field in ("start_date", "end_date"):
            value = row.get(field, "")
            if value:
                try:
                    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                        raise ValueError()
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    raise ClientError("Date bounds must be empty or YYYY-MM-DD") from None
            elif value != "":
                raise ClientError("Date bounds must be strings")
            dates[field] = value
        if dates["start_date"] and dates["end_date"] and dates["start_date"] > dates["end_date"]:
            raise ClientError("Inverted date bounds")
        normalized.append({"url": canonical, "num_of_posts": row["num_of_posts"], **({spec["country"]: country} if spec["country"] else {}), **dates})
    reserve = len(normalized) * limit
    integer(reserve, 1, MAX_CREDITS, "batch reservation (maximum 4000)")
    result = {"id": plan["id"], "dataset_id": plan["dataset_id"], "limit_per_input": limit, "inputs": normalized}
    return result, reserve


def financial_batch(batch):
    normalized, reserve = validate_plan({key: batch[key] for key in ("id", "dataset_id", "limit_per_input", "inputs")})
    if integer(batch.get("reserved_credits"), 1, MAX_CREDITS, "external reservation") < reserve:
        raise ClientError("External UI reservation is below its maximum result count")
    return {**normalized, "reserved_credits": batch["reserved_credits"]}


def observation(path, *, fresh=True):
    value = read(path, 1024 * 1024)
    if not isinstance(value, dict) or value.get("version") != 1 or value.get("provider") != "brightdata":
        raise ClientError("Expected Bright Data UI free-credit ledger version 1")
    if type(value.get("payment_methods")) is not int or value.get("payment_methods") != 0 or type(value.get("out_of_pocket_usd")) not in (int, float) or value.get("out_of_pocket_usd") != 0:
        raise ClientError("Only a verified no-card, zero-payment account is enabled")
    if value.get("auto_recharge") not in (None, False):
        raise ClientError("Auto recharge must not be enabled")
    free = integer(value.get("free_credits_observed"), 0, 5000, "observed monthly free credits")
    integer(value.get("campaign_cap"), 1, MAX_CREDITS, "campaign cap")
    integer(value.get("safety_margin"), MARGIN, 5000, "safety margin")
    age = now() - timestamp(value.get("checked_at"))
    if fresh and not timedelta(0) <= age <= timedelta(hours=24):
        raise ClientError("Verify monthly free credits in the UI within the last 24 hours")
    batches = value.get("batches")
    if not isinstance(batches, list) or len(batches) > 1000:
        raise ClientError("Invalid external batch ledger")
    baseline = {}
    for batch in batches:
        if not isinstance(batch, dict):
            raise ClientError("Invalid external batch")
        try:
            financial = financial_batch(batch)
        except KeyError:
            raise ClientError("Incomplete external batch") from None
        if financial["id"] in baseline:
            raise ClientError("Duplicate external batch ID")
        if batch.get("snapshot_id"):
            snapshot(batch["snapshot_id"])
        baseline[financial["id"]] = financial
    total = sum(b["reserved_credits"] for b in baseline.values())
    cap = min(value["campaign_cap"], free - value["safety_margin"])
    if total > MAX_CREDITS:
        raise ClientError("External reservations already exceed 4000")
    return value, baseline, total, cap


def code_hash():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def init(folder, ledger):
    folder, ledger = Path(folder).resolve(), Path(ledger).resolve()
    observed, baseline, total, cap = observation(ledger)
    if cap < total or cap < 1:
        raise ClientError("Observed free credits cannot cover the margin and existing reservations")
    folder.mkdir(parents=True, exist_ok=True)
    with locked(folder):
        if (folder / "state.json").exists():
            raise ClientError("Campaign exists; free-credit reservations cannot be reset")
        if any(p.name != "state.lock" for p in folder.iterdir()):
            raise ClientError("Initialize an empty campaign directory")
        state = {"version": VERSION, "client_sha256": code_hash(), "created_at": stamp(),
                 "ui_ledger": str(ledger), "period": timestamp(observed["checked_at"]).strftime("%Y-%m"),
                 "campaign_cap": min(cap, MAX_CREDITS), "external_baseline": baseline, "jobs": {},
                 "out_of_pocket_usd": 0, "catalog_modified": False}
        atomic(folder / "state.json", state)
    return {"status": "initialized", "external_reserved": total, "effective_cap": cap, "network_requests": 0}


def load(folder):
    state = read(Path(folder) / "state.json", 4 * 1024 * 1024)
    if not isinstance(state, dict) or state.get("version") != VERSION or state.get("client_sha256") != code_hash():
        raise ClientError("Client changed or campaign invalid; review before resuming")
    if not isinstance(state.get("jobs"), dict) or len(state["jobs"]) > 1000:
        raise ClientError("Invalid job ledger")
    integer(state.get("campaign_cap"), 1, MAX_CREDITS, "saved campaign cap")
    for name, job in state["jobs"].items():
        job_id(name)
        if not isinstance(job, dict):
            raise ClientError("Invalid job")
        plan, maximum = validate_plan(job.get("plan"))
        if name != plan["id"] or plan != job["plan"] or job.get("max_records") != maximum:
            raise ClientError("Saved plan or maximum was altered")
        integer(job.get("reserved_credits"), maximum, MAX_CREDITS, "saved reservation")
        integer(job.get("get_requests"), 0, 1000000, "GET request count")
        if job.get("budget_origin") not in {"api", "ui"} or job.get("status") not in {"reserved", "uncertain", "submitted", "ready", "failed", "complete", "over_cap"}:
            raise ClientError("Invalid saved job status or origin")
        if job.get("status") in {"submitted", "ready", "failed", "complete", "over_cap"}:
            snapshot(job.get("snapshot_id"))
        if job.get("status") == "complete" and job.get("file") != job["snapshot_id"] + ".json":
            raise ClientError("Invalid completed snapshot filename")
    return state


def budget(state, *, fresh=True, allow_unknown=False):
    observed, baseline, external, cap = observation(state["ui_ledger"], fresh=fresh)
    if timestamp(observed["checked_at"]).strftime("%Y-%m") != state["period"]:
        raise ClientError("Monthly period changed; existing reservations are not reset")
    if any(baseline.get(key) != old for key, old in state["external_baseline"].items()):
        raise ClientError("External UI reservations were removed or altered")
    for name, job in state["jobs"].items():
        if job["budget_origin"] == "ui" and baseline.get(name) != {**job["plan"], "reserved_credits": job["reserved_credits"]}:
            raise ClientError("An adopted UI job no longer matches its external reservation")
    if not allow_unknown and any(not b.get("snapshot_id") and b.get("status") != "rejected_customer_inactive" for b in observed["batches"]):
        raise ClientError("An external UI request lacks its snapshot; reconcile it before a new POST")
    internal = sum(job["reserved_credits"] for job in state["jobs"].values() if job["budget_origin"] == "api")
    return external + internal, min(cap, state["campaign_cap"], MAX_CREDITS), baseline, observed


def api_key():
    value = os.environ.get("BRIGHTDATA_API_KEY")
    if not isinstance(value, str) or not 10 <= len(value) <= 500 or any(c.isspace() for c in value):
        raise ClientError("Set BRIGHTDATA_API_KEY explicitly; no credential-store or browser discovery is performed")
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise TransportError("Redirect refused; credential was not forwarded")


def http(method, path, params, payload, key, *, timeout=30):
    """One bounded HTTPS call. No retries, redirects, proxies or auth setup."""
    if method == "POST":
        if path != "/datasets/v3/trigger":
            raise ClientError("POST endpoint refused")
    elif method == "GET":
        if not re.fullmatch(r"/datasets/v3/(?:progress|snapshot)/sd_[A-Za-z0-9_-]{5,100}", path):
            raise ClientError("GET endpoint refused")
    else:
        raise ClientError("HTTP method refused")
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    request = urllib.request.Request(url, data=encoded(payload) if payload is not None else None,
                                    headers={"Authorization": "Bearer " + key, "Accept": "application/json", "Content-Type": "application/json",
                                             "User-Agent": "RaceLink-Metadata-Collector/28"}, method=method)
    deadline = time.monotonic() + timeout
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect()).open(request, timeout=min(timeout, 15)) as response:
            if response.status != 200 or response.geturl() != url:
                raise TransportError("Unexpected HTTP status or response URL")
            data = bytearray()
            while True:
                if time.monotonic() >= deadline:
                    raise TransportError("Response deadline exceeded; no retry")
                chunk = response.read1(min(64 * 1024, MAX_BYTES + 1 - len(data)))
                if time.monotonic() >= deadline:
                    raise TransportError("Response deadline exceeded; no retry")
                data.extend(chunk)
                if not chunk or len(data) > MAX_BYTES:
                    break
    except urllib.error.HTTPError as exc:
        raise TransportError(f"API HTTP {exc.code}; no retry or remote error body persisted") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise TransportError("Request outcome uncertain; no retry") from None
    if len(data) > MAX_BYTES or key.encode() in data:
        raise TransportError("Response too large or contains API credential; not persisted")
    try:
        return json.loads(data.decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        raise TransportError("Invalid JSON response; no retry") from None


def request_plan(plan):
    spec = DATASETS[plan["dataset_id"]]
    params = {"dataset_id": plan["dataset_id"], "notify": "false", "include_errors": "true"}
    if spec["discover_by"]:
        params.update(type="discover_new", discover_by=spec["discover_by"], limit_per_input=plan["limit_per_input"])
    return {"method": "POST", "path": "/datasets/v3/trigger", "params": params,
        "body": {"input": plan["inputs"], "limit_per_input": plan["limit_per_input"]}}


def fingerprint(plan):
    inputs = [{**row, "url": row["url"].lower()} for row in plan["inputs"]]
    return sha({**{key: value for key, value in plan.items() if key not in {"id", "inputs"}},
                "inputs": sorted(inputs, key=lambda row: row["url"])})


def safe_reply(reply, key):
    try:
        data = encoded(reply)
    except (ValueError, TypeError):
        raise ClientError("Invalid JSON payload") from None
    if len(data) > MAX_BYTES or key.encode() in data:
        raise ClientError("Response too large or contains API credential; not persisted")


def trigger(folder, plan, *, execute=False, transport=http):
    folder = Path(folder).resolve()
    plan, reserve = validate_plan(plan)
    with locked(folder):
        state = load(folder)
        if plan["id"] in state["jobs"]:
            job = state["jobs"][plan["id"]]
            if job["plan"] != plan:
                raise ClientError("Job ID already binds different inputs")
            return {"status": job["status"], "snapshot_id": job.get("snapshot_id"), "requests_sent": 0,
                    "note": "Existing job returned; POST never replayed"}
        used, cap, baseline, _ = budget(state)
        if any(j["status"] in {"reserved", "uncertain", "over_cap"} for j in state["jobs"].values()):
            raise ClientError("A prior POST is uncertain or exceeded its cap; reconcile before new work")
        all_plans = [j["plan"] for j in state["jobs"].values()] + [{k: v for k, v in item.items() if k != "reserved_credits"} for item in baseline.values()]
        if any(fingerprint(item) == fingerprint(plan) for item in all_plans):
            raise ClientError("Identical profile batch already reserved; use its existing snapshot")
        if used + reserve > cap:
            raise ClientError("Batch exceeds verified free-credit cap or 1000-credit margin")
        request = request_plan(plan)
        if not execute:
            return {"mode": "preview", "request": request, "reserved_for_batch": reserve, "already_reserved": used,
                    "effective_cap": cap, "requests_sent": 0, "out_of_pocket_usd": 0}
        key = api_key()
        job = {"plan": plan, "budget_origin": "api", "reserved_credits": reserve, "max_records": reserve,
               "status": "reserved", "reserved_at": stamp(), "snapshot_id": None, "get_requests": 0}
        state["jobs"][plan["id"]] = job
        state["external_baseline"] = baseline
        atomic(folder / "state.json", state)  # Flush reservation BEFORE the only POST.
        try:
            reply = transport(request["method"], request["path"], request["params"], request["body"], key)
            safe_reply(reply, key)
            if not isinstance(reply, dict) or reply.get("error"):
                raise ClientError("Trigger response did not provide a successful snapshot")
            snap = snapshot(reply.get("snapshot_id"))
            if any(other.get("snapshot_id") == snap for name, other in state["jobs"].items() if name != plan["id"]):
                raise ClientError("Provider returned an already-bound snapshot")
        except Exception:
            job.update(status="uncertain", last_error="post_outcome_requires_reconciliation")
            atomic(folder / "state.json", state)
            raise ClientError("POST outcome uncertain; reservation retained, no retry. Reconcile snapshot in UI.") from None
        job.update(status="submitted", snapshot_id=snap, submitted_at=stamp())
        atomic(folder / "state.json", state)
        return {"status": "submitted", "snapshot_id": snap, "reserved_credits": reserve, "requests_sent": 1}


def adopt_ui(folder, batch_id):
    folder = Path(folder).resolve()
    job_id(batch_id)
    with locked(folder):
        state = load(folder)
        _, _, baseline, observed = budget(state, fresh=False, allow_unknown=True)
        batch = next((b for b in observed["batches"] if b["id"] == batch_id), None)
        if batch is None:
            raise ClientError("Unknown UI batch")
        snap = snapshot(batch.get("snapshot_id"))
        plan, maximum = validate_plan({k: batch[k] for k in ("id", "dataset_id", "limit_per_input", "inputs")})
        if batch_id in state["jobs"]:
            old = state["jobs"][batch_id]
            if old["plan"] != plan or old["snapshot_id"] != snap or old["budget_origin"] != "ui":
                raise ClientError("UI adoption conflicts with existing job")
            return {"status": old["status"], "requests_sent": 0}
        if any(j.get("snapshot_id") == snap for j in state["jobs"].values()):
            raise ClientError("Snapshot already belongs to another job")
        state["jobs"][batch_id] = {"plan": plan, "budget_origin": "ui", "reserved_credits": batch["reserved_credits"],
                                   "max_records": maximum, "status": "submitted", "snapshot_id": snap,
                                   "adopted_at": stamp(), "get_requests": 0}
        state["external_baseline"] = baseline
        atomic(folder / "state.json", state)
        return {"status": "adopted", "snapshot_id": snap, "extra_reserved_credits": 0, "requests_sent": 0}


def reconcile(folder, name, snap, evidence):
    folder, evidence = Path(folder).resolve(), Path(evidence).resolve()
    job_id(name)
    snapshot(snap)
    if not evidence.is_file() or evidence.is_symlink() or evidence.stat().st_size > MAX_BYTES:
        raise ClientError("Provide a bounded local UI/API evidence file for the snapshot")
    evidence_hash = hashlib.sha256(evidence.read_bytes()).hexdigest()
    with locked(folder):
        state = load(folder)
        job = state["jobs"].get(name)
        if not job or job["status"] not in {"reserved", "uncertain"} or job["budget_origin"] != "api":
            raise ClientError("Only an unresolved API POST can be reconciled")
        if any(j.get("snapshot_id") == snap for j in state["jobs"].values()):
            raise ClientError("Snapshot already belongs to a job")
        job.update(snapshot_id=snap, status="submitted", reconciled_at=stamp(), reconciliation_evidence_sha256=evidence_hash)
        atomic(folder / "state.json", state)
        return {"status": "reconciled", "snapshot_id": snap, "requests_sent": 0, "reservation_released": False}


def project_rows(rows, dataset_id):
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        raise ClientError("Snapshot must contain a JSON array of objects")
    platform = DATASETS[dataset_id]["platform"]
    projected = []
    for row in rows:
        if row.get("error") or row.get("error_code"):
            projected.append({"error": "provider_error"})
            continue
        safe = {k: v for k, v in row.items() if k in SAFE_FIELDS[platform]}
        if platform == "tiktok":
            # Preserve presence of slideshow/commerce markers, not their nested URLs/tokens.
            if row.get("carousel_images"):
                safe["carousel_images"] = ["source_declares_carousel"]
            if row.get("commerce_info"):
                safe["commerce_info"] = "source_declares_commercial_context"
        projected.append(safe)
    return projected


def collect(folder, name, *, execute=False, transport=http):
    folder = Path(folder).resolve()
    job_id(name)
    with locked(folder):
        state = load(folder)
        job = state["jobs"].get(name)
        if not job:
            raise ClientError("Unknown job")
        snap = snapshot(job.get("snapshot_id"))
        if job["status"] == "complete":
            page = folder / job["file"]
            if page.is_symlink() or not page.is_file() or hashlib.sha256(page.read_bytes()).hexdigest() != job["sha256"]:
                raise ClientError("Completed snapshot file is missing or changed")
            return {"status": "complete", "file": str(page), "rows": job["rows"], "requests_sent": 0}
        if job["status"] not in {"submitted", "ready"}:
            raise ClientError("Snapshot is not eligible for collection")
        if not execute:
            return {"mode": "preview", "snapshot_id": snap, "maximum_get_requests": 2, "requests_sent": 0}
        key = api_key()
        job["get_requests"] += 1
        atomic(folder / "state.json", state)
        try:
            progress = transport("GET", "/datasets/v3/progress/" + snap, {}, None, key)
            safe_reply(progress, key)
            if not isinstance(progress, dict) or progress.get("snapshot_id") not in (None, snap):
                raise ClientError("Invalid progress response")
            status = progress.get("status")
            if status in {"starting", "building", "running", "pending", "collecting"}:
                job.update(status="submitted", last_progress=status, last_checked_at=stamp())
                atomic(folder / "state.json", state)
                return {"status": status, "snapshot_id": snap, "requests_sent": 1, "retry_post": False}
            if status in {"failed", "canceled", "cancelled"}:
                job.update(status="failed", last_progress=status, last_checked_at=stamp())
                atomic(folder / "state.json", state)
                return {"status": "failed", "requests_sent": 1, "reservation_released": False}
            if status != "ready" or progress.get("error"):
                raise ClientError("Unrecognized progress status")
            job.update(status="ready", last_progress="ready", last_checked_at=stamp())
            job["get_requests"] += 1
            atomic(folder / "state.json", state)
            rows = transport("GET", "/datasets/v3/snapshot/" + snap, {"format": "json"}, None, key)
            safe_reply(rows, key)
            if not isinstance(rows, list):
                raise ClientError("Snapshot response is not a JSON array")
            if len(rows) > job["max_records"]:
                job.update(status="over_cap", returned_rows=len(rows))
                atomic(folder / "state.json", state)
                raise ClientError("Provider exceeded reserved result cap; no additional POST allowed")
            safe = project_rows(rows, job["plan"]["dataset_id"])
        except Exception:
            # Safe GET may be invoked again later; never repeat or refund the POST.
            job["last_error"] = "get_failed_or_invalid_response"
            atomic(folder / "state.json", state)
            raise ClientError("Collection GET failed or response invalid; no automatic retry, POST reservation retained") from None
        file = snap + ".json"
        page = folder / file
        atomic(page, safe)
        job.update(status="complete", file=file, sha256=hashlib.sha256(page.read_bytes()).hexdigest(),
                   source_response_sha256=sha(rows), rows=len(safe), completed_at=stamp(),
                   metadata_allowlist_applied=True, raw_media_downloaded=False)
        atomic(folder / "state.json", state)
        return {"status": "complete", "file": str(page), "rows": len(safe), "requests_sent": 2,
                "metadata_allowlist_applied": True, "catalog_modified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init_parser = sub.add_parser("init")
    init_parser.add_argument("folder", type=Path)
    init_parser.add_argument("--ui-ledger", type=Path, required=True)
    trigger_parser = sub.add_parser("trigger")
    trigger_parser.add_argument("folder", type=Path)
    trigger_parser.add_argument("--plan", type=Path, required=True)
    trigger_parser.add_argument("--execute", action="store_true")
    collect_parser = sub.add_parser("collect")
    collect_parser.add_argument("folder", type=Path)
    collect_parser.add_argument("--job", required=True)
    collect_parser.add_argument("--execute", action="store_true")
    adopt_parser = sub.add_parser("adopt-ui")
    adopt_parser.add_argument("folder", type=Path)
    adopt_parser.add_argument("--job", required=True)
    reconcile_parser = sub.add_parser("reconcile-snapshot")
    reconcile_parser.add_argument("folder", type=Path)
    reconcile_parser.add_argument("--job", required=True)
    reconcile_parser.add_argument("--snapshot", required=True)
    reconcile_parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = init(args.folder, args.ui_ledger)
        elif args.command == "trigger":
            result = trigger(args.folder, read(args.plan, 1024 * 1024), execute=args.execute)
        elif args.command == "collect":
            result = collect(args.folder, args.job, execute=args.execute)
        elif args.command == "adopt-ui":
            result = adopt_ui(args.folder, args.job)
        else:
            result = reconcile(args.folder, args.job, args.snapshot, args.evidence)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ClientError, OSError, KeyError) as exc:
        parser.exit(1, f"Bright Data collector: {exc}\n")


if __name__ == "__main__":
    main()
