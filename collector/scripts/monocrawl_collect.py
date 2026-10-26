#!/usr/bin/env python3
"""Bounded Monocrawl public-search collector. Preview is default; no DB writes.

The same reservation can be fulfilled through the official MCP or this REST
client. No automatic retry, sample mode, account creation, or billing mutation.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

import bulk_ingest

VERSION = "1.0.0"
API = "https://www.monocrawl.com"
ENDPOINTS = {"tiktok": ("/v1/tiktok/search", 2),
             "instagram": ("/v1/instagram/search-reels", 1)}
MAX_BYTES = 8 * 1024 * 1024
MAX_PAGES_PER_WAVE = 3


class CollectorError(ValueError):
    pass


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def number(value, minimum, maximum, label, integer=False):
    if type(value) not in ((int,) if integer else (int, float)) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise CollectorError("Invalid " + label)
    return value


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed
    except (ValueError, AttributeError):
        raise CollectorError("Expected timezone-aware checked_at") from None


def read(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_BYTES:
        raise CollectorError("Expected regular JSON file at most 8 MiB")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded(value))
    os.replace(temporary, path)


def safe_text(value, limit, label):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
        raise CollectorError("Invalid " + label)
    # Never accept credentials in a plan, query, cursor or receipt identifier.
    if re.search(r"\bmn_[A-Za-z0-9_-]{8,}", value):
        raise CollectorError("Credential-like value refused")
    return value


def valid_plan(plan):
    fields = {"version", "free_credits", "budget_credits", "checked_at", "auto_reload", "overage",
              "out_of_pocket_usd", "transport", "key_credit_limit", "jobs"}
    if not isinstance(plan, dict) or set(plan) != fields or type(plan.get("version")) is not int or plan["version"] != 1:
        raise CollectorError("Unexpected plan fields")
    number(plan["free_credits"], 1, 10000, "observed free credits", True)
    number(plan["budget_credits"], 1, min(plan["free_credits"], 100), "bounded pilot budget", True)
    age = datetime.now(timezone.utc) - timestamp(plan["checked_at"])
    if not timedelta(0) <= age <= timedelta(hours=24):
        raise CollectorError("Free allowance and billing controls must be observed within 24 hours")
    if plan["auto_reload"] is not False or plan["overage"] is not False or plan["out_of_pocket_usd"] != 0:
        raise CollectorError("Only observed free allowance with reload and overage disabled")
    if plan["transport"] not in {"mcp", "rest"}:
        raise CollectorError("Transport must be mcp or rest")
    if plan["transport"] == "rest":
        number(plan["key_credit_limit"], 1, plan["budget_credits"], "observed dedicated key credit limit", True)
    elif plan["key_credit_limit"] is not None:
        number(plan["key_credit_limit"], 1, plan["budget_credits"], "key credit limit", True)
    jobs = plan["jobs"]
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 50:
        raise CollectorError("Expected 1–50 explicit search jobs")
    seen = set()
    for job in jobs:
        if not isinstance(job, dict) or set(job) != {"id", "platform", "query", "region", "max_pages"}:
            raise CollectorError("Unexpected job fields")
        if not isinstance(job["id"], str) or not re.fullmatch(r"[a-z0-9-]{1,60}", job["id"]) or job["id"] in seen:
            raise CollectorError("Invalid or duplicate job id")
        seen.add(job["id"])
        if job["platform"] not in ENDPOINTS:
            raise CollectorError("Only TikTok and Instagram public search allowed")
        safe_text(job["query"], 250, "query")
        if job["region"] is not None and (job["platform"] != "tiktok" or not re.fullmatch(r"[A-Z]{2}", str(job["region"]))):
            raise CollectorError("Region is only a two-letter TikTok request location, not language")
        number(job["max_pages"], 1, 20, "job max_pages", True)
    return plan


def init(folder, plan):
    valid_plan(plan)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    if any(folder.iterdir()):
        raise CollectorError("Use an empty campaign directory; do not reset a spent ledger")
    state = {"version": VERSION, "plan": plan, "plan_sha256": digest(plan), "created_at": now(),
             "attempts": [], "spent_credits": 0, "paused": False,
             "jobs": {j["id"]: {"cursor": None, "pages": 0, "finished": False} for j in plan["jobs"]}}
    atomic(folder / "state.json", state)
    return {"initialized": True, "budget_credits": plan["budget_credits"], "requests_sent": 0}


@contextmanager
def locked(folder):
    folder = Path(folder)
    lock = folder / ".lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise CollectorError("Campaign locked; inspect existing process, do not start another") from None
    os.close(fd)
    try:
        state = read(folder / "state.json")
        if state.get("version") != VERSION or digest(state["plan"]) != state.get("plan_sha256"):
            raise CollectorError("Campaign plan or version changed")
        yield state
    finally:
        lock.unlink(missing_ok=True)


def request_for(state, job_id):
    valid_plan(state["plan"])
    job = next((j for j in state["plan"]["jobs"] if j["id"] == job_id), None)
    if not job:
        raise CollectorError("Unknown planned job")
    progress = state["jobs"][job_id]
    if state["paused"] or any(a["state"] == "reserved" for a in state["attempts"]):
        raise CollectorError("Prior outcome unresolved or campaign paused; no retry")
    if progress["finished"] or progress["pages"] >= job["max_pages"]:
        raise CollectorError("Job finished or page limit reached")
    path, price = ENDPOINTS[job["platform"]]
    limit = min(state["plan"]["budget_credits"], state["plan"]["key_credit_limit"] or state["plan"]["budget_credits"])
    if state["spent_credits"] + price > limit:
        raise CollectorError("Observed free-credit pilot budget exhausted")
    # A later balance can reduce available funds, never enlarge the authorization.
    completed = [a for a in state["attempts"] if a["state"] == "complete"]
    if completed and price > completed[-1]["credits_remaining"]:
        raise CollectorError("Last receipt reports fewer credits than this request requires")
    params = {"query": job["query"], "judgments": "off"}
    if job["region"] is not None:
        params["region"] = job["region"]
    if progress["cursor"] is not None:
        params["cursor"] = progress["cursor"]
    return {"job": job_id, "platform": job["platform"], "endpoint": path, "params": params,
            "max_credits": price, "page": progress["pages"] + 1}


def preview(folder, job_id):
    with locked(folder) as state:
        request = request_for(state, job_id)
        return {"mode": "preview", "requests_sent": 0, "request": request,
                "spent_credits": state["spent_credits"], "budget_credits": state["plan"]["budget_credits"],
                "catalog_modified": False, "publication_count": 0}


def reserve(folder, job_id):
    with locked(folder) as state:
        request = request_for(state, job_id)
        attempt = {"seq": len(state["attempts"]), "state": "reserved", "reserved_at": now(),
                   "idempotency_key": "racelink-" + uuid.uuid4().hex, **request}
        state["attempts"].append(attempt)
        atomic(Path(folder) / "state.json", state)
        return {"reservation": attempt["seq"], "rest": {"path": request["endpoint"], "params": request["params"]},
                "mcp": {"platform": request["platform"], "endpoint": request["endpoint"].split("/", 3)[3],
                        "params": request["params"], "max_credits": request["max_credits"],
                        "idempotency_key": attempt["idempotency_key"]}}


def map_item(item, platform, receipt, index):
    if not isinstance(item, dict):
        raise CollectorError("Non-object record")
    if any(item.get(k) is True for k in ("is_private", "private", "is_slideshow", "is_photo", "is_story")):
        raise CollectorError("Private or non-video result refused")
    if item.get("type") in {"image", "photo", "carousel", "sidecar"}:
        raise CollectorError("Non-video result refused")
    if item.get("is_video") is False:
        raise CollectorError("Source explicitly marks a non-video record")
    author = item.get("author") if isinstance(item.get("author"), dict) else {}
    if any(author.get(k) is True for k in ("is_private", "private", "privateAccount")):
        raise CollectorError("Source author is private")
    # Supply only fields with a documented source meaning to the existing schema
    # adapter. Music duration, region and has_audio never establish video language.
    mapped = {"url": item.get("url"), "caption": item.get("caption"), "title": item.get("title"),
              "duration": item.get("duration_s"), "published_at": item.get("created_at"),
              "isAd": item.get("is_ad"), "isPaidPartnership": item.get("is_paid_partnership")}
    mapped["author"] = {"uniqueId": author.get("handle"), "nickname": author.get("name")}
    if platform == "instagram":
        mapped.update(ownerUsername=author.get("handle"), ownerFullName=author.get("name"),
                      productType=item.get("product_type"))
    if isinstance(item.get("hashtags"), list):
        mapped["hashtags"] = [v for v in item["hashtags"] if isinstance(v, str)]
    record, decision = bulk_ingest.adapt(mapped, "apify-" + platform, source_label="monocrawl-search", index=index)
    record["provenance"].update(adapter="monocrawl", adapter_version=VERSION,
                                source_record_sha256=digest(item), response_receipt=receipt)
    record["collection_provenance"] = {"provider": "monocrawl", "collector": "monocrawl_collect",
        "collector_version": VERSION, "evidence_scope": "public_search_metadata", "media_downloaded": False,
        "audio_language_verified": False, "collected_at": receipt["collected_at"]}
    record["verification_scope"] = "public_search_metadata"
    record["review_status"] = "candidate"
    return record, decision


def accept(folder, seq, payload, *, api_key=None):
    """Settle one real receipt, preserve raw envelope privately, stage candidates.

    This does not import candidates, invent compatibility or certify audio.
    """
    raw = encoded(payload)
    if len(raw) > MAX_BYTES or (api_key and api_key.encode("utf-8") in raw) or re.search(rb"\bmn_[A-Za-z0-9_-]{12,}", raw):
        raise CollectorError("Oversized or credential-bearing payload refused")
    folder = Path(folder)
    with locked(folder) as state:
        number(seq, 0, len(state["attempts"]) - 1, "reservation", True)
        attempt = state["attempts"][seq]
        if attempt["state"] != "reserved":
            raise CollectorError("Reservation already accepted; never count a replay twice")
        filename = f"response-{seq:06d}.json"
        raw_path = folder / filename
        if raw_path.exists() and raw_path.read_bytes() != raw:
            raise CollectorError("Different payload for an existing reservation")
        raw_path.write_bytes(raw)
        attempt.update(response_file=filename, response_sha256=hashlib.sha256(raw).hexdigest())
        try:
            if not isinstance(payload, dict) or payload.get("success") is not True or payload.get("error"):
                raise CollectorError("Source request did not succeed")
            if payload.get("platform") != attempt["platform"] or payload.get("endpoint") != attempt["endpoint"]:
                raise CollectorError("Response endpoint does not match reservation")
            if any(payload.get(k) not in (None, False) for k in ("sandbox", "synthetic", "is_sample", "pending_reconciliation")):
                raise CollectorError("Sample or unresolved accounting response refused")
            if payload.get("mode") in {"sandbox", "sample", "dry_run"} or payload.get("dry_run") is True:
                raise CollectorError("Preview/sample is not a real response")
            charged = number(payload.get("credits_used"), 0, attempt["max_credits"], "settled credits_used")
            remaining = number(payload.get("credits_remaining"), 0, 10**12, "credits_remaining")
            request_id = safe_text(payload.get("request_id"), 200, "request_id")
            if any(a.get("request_id") == request_id for a in state["attempts"] if a["seq"] != seq):
                raise CollectorError("Historical receipt replayed under another reservation")
            data = payload.get("data")
            if not isinstance(data, dict) or not isinstance(data.get("items"), list) or len(data["items"]) > 1000:
                raise CollectorError("Expected bounded data.items; stored MCP results require complete free retrieval first")
            if data.get("window_stop_reason") == "receipt_pending" or data.get("pending_reconciliation") not in (None, False):
                raise CollectorError("Nested receipt remains pending despite a provisional numeric charge")
            if data.get("partial") is not None and type(data["partial"]) is not bool:
                raise CollectorError("Invalid partial flag")
            next_cursor = data.get("cursor")
            if next_cursor is not None:
                safe_text(next_cursor, 4096, "opaque response cursor")
            if data.get("has_more") is not None and type(data["has_more"]) is not bool:
                raise CollectorError("Invalid has_more")
        except (CollectorError, TypeError, ValueError):
            state["paused"] = True
            attempt["stop_reason"] = "invalid_or_unsettled_receipt"
            atomic(folder / "state.json", state)
            raise CollectorError("Receipt preserved, reservation retained, campaign paused; inspect before continuing") from None
        receipt = {"request_id": request_id, "response_sha256": attempt["response_sha256"],
                   "endpoint": attempt["endpoint"], "collected_at": now()}
        records, rejected = [], []
        for index, item in enumerate(data["items"]):
            try:
                record, decision = map_item(item, attempt["platform"], receipt, index)
                records.append({"record": record, "qualification": decision})
            except (CollectorError, ValueError, TypeError):
                rejected.append({"index": index, "source_record_sha256": digest(item), "reason": "invalid_or_unusable_video_metadata"})
        atomic(folder / f"review-{seq:06d}.json", {"version": VERSION, "receipt": receipt,
            "requires_editorial_review": True, "records": records, "rejected": rejected,
            "warnings": {"envelope": payload.get("warnings"), "data": data.get("_warnings")}, "partial": data.get("partial"),
            "window_stop_reason": data.get("window_stop_reason"), "imported": 0})
        attempt.update(state="complete", completed_at=now(), credits_used=charged,
                       credits_remaining=remaining, request_id=request_id, candidate_count=len(records), rejected_count=len(rejected))
        state["spent_credits"] += charged
        progress = state["jobs"][attempt["job"]]
        previous = [a.get("params", {}).get("cursor") for a in state["attempts"] if a["job"] == attempt["job"]]
        progress.update(pages=progress["pages"] + 1, cursor=next_cursor,
                        finished=(not data["items"] or next_cursor is None or data.get("has_more") is False or next_cursor in previous))
        if not data["items"]:
            progress["stop_reason"] = "empty_page_no_completeness_claim"
        if data.get("partial") is True or data.get("window_stop_reason") in {"funding_limit", "receipt_pending", "source_unavailable", "invalid_source_page"}:
            state["paused"] = True
        if remaining < min(cost for _, cost in ENDPOINTS.values()):
            state["paused"] = True
        atomic(folder / "state.json", state)
        return {"accepted": True, "credits_used": charged, "candidate_count": len(records),
                "rejected_count": len(rejected), "catalog_modified": False, "publication_count": 0,
                "next_cursor_available": next_cursor is not None, "paused": state["paused"]}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CollectorError("Redirect refused; credential not forwarded")


def http_get(path, params, api_key):
    if path not in {e[0] for e in ENDPOINTS.values()} or not re.fullmatch(r"mn_[A-Za-z0-9_-]{8,500}", api_key or ""):
        raise CollectorError("Invalid allowlisted endpoint or environment credential")
    if not isinstance(params, dict) or not {"query", "judgments"} <= set(params) or set(params) - {"query", "judgments", "region", "cursor"} or params["judgments"] != "off":
        raise CollectorError("Only fixed public-search parameters allowed")
    safe_text(params["query"], 250, "query")
    if "cursor" in params:
        safe_text(params["cursor"], 4096, "opaque cursor")
    if "region" in params and (path != ENDPOINTS["tiktok"][0] or not re.fullmatch(r"[A-Z]{2}", str(params["region"]))):
        raise CollectorError("Invalid region")
    url = API + path + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"x-api-key": api_key, "Accept": "application/json",
                                     "User-Agent": "RaceLink-Metadata-Collector/32"})
    deadline = time.monotonic() + 60
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=15) as response:
            if response.status != 200 or response.geturl().split("?", 1)[0] != API + path:
                raise CollectorError("Unexpected HTTP outcome")
            raw = bytearray()
            while len(raw) <= MAX_BYTES:
                if time.monotonic() > deadline:
                    raise CollectorError("Response deadline exceeded; reservation retained")
                chunk = response.read1(min(65536, MAX_BYTES + 1 - len(raw)))
                raw.extend(chunk)
                if not chunk:
                    break
    except urllib.error.HTTPError as exc:
        raise CollectorError(f"HTTP {exc.code}; paused without retry or saving remote error body") from None
    except (OSError, TimeoutError, urllib.error.URLError):
        raise CollectorError("Transport outcome unknown; reservation retained, no retry") from None
    if len(raw) > MAX_BYTES or api_key.encode() in raw:
        raise CollectorError("Payload too large or credential-bearing")
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        raise CollectorError("Invalid JSON; reservation retained") from None


def run(folder, job_id, *, execute=False, max_pages=1, transport=http_get, api_key=None):
    number(max_pages, 1, MAX_PAGES_PER_WAVE, "pages per wave", True)
    report = preview(folder, job_id)
    report["max_pages"] = max_pages
    if not execute:
        return report
    state = read(Path(folder) / "state.json")
    if state["plan"]["transport"] != "rest":
        raise CollectorError("MCP campaign: reserve, call official tool, then accept its full envelope")
    api_key = api_key or os.environ.get("MONOCRAWL_API_KEY")
    if not isinstance(api_key, str) or not re.fullmatch(r"mn_[A-Za-z0-9_-]{8,500}", api_key):
        raise CollectorError("MONOCRAWL_API_KEY must be supplied explicitly in the environment")
    report.update(mode="execute", receipts=[])
    for page in range(max_pages):
        if page:
            time.sleep(2)
        reservation = reserve(folder, job_id)
        report["requests_sent"] += 1
        try:
            request = reservation["rest"]
            payload = transport(request["path"], request["params"], api_key)
            report["receipts"].append(accept(folder, reservation["reservation"], payload, api_key=api_key))
        except Exception:
            with locked(folder) as state:
                state["paused"] = True
                atomic(Path(folder) / "state.json", state)
            raise CollectorError("Request stopped; ledger retains the reservation. No automatic retry.") from None
        state = read(Path(folder) / "state.json")
        if state["paused"] or state["jobs"][job_id]["finished"] or state["jobs"][job_id]["pages"] >= next(j["max_pages"] for j in state["plan"]["jobs"] if j["id"] == job_id):
            break
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init")
    p.add_argument("--plan", required=True)
    p.add_argument("--directory", required=True)
    for command in ("preview", "reserve", "run", "accept"):
        p = sub.add_parser(command)
        p.add_argument("--directory", required=True)
        if command == "accept":
            p.add_argument("--reservation", type=int, required=True)
            p.add_argument("--response", required=True)
        else:
            p.add_argument("--job", required=True)
        if command == "run":
            p.add_argument("--execute", action="store_true")
            p.add_argument("--max-pages", type=int, default=1)
    args = parser.parse_args()
    try:
        if args.command == "init": result = init(args.directory, read(args.plan))
        elif args.command == "accept": result = accept(args.directory, args.reservation, read(args.response))
        elif args.command == "run": result = run(args.directory, args.job, execute=args.execute, max_pages=args.max_pages)
        else: result = globals()[args.command](args.directory, args.job)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (CollectorError, OSError, ValueError, KeyError, TypeError):
        parser.exit(2, "COLLECTOR: stopped. Inspect local ledger; unresolved outcomes remain reserved. No retry or billing change.\n")


if __name__ == "__main__":
    main()
