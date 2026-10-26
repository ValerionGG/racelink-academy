#!/usr/bin/env python3
"""Explicit, bounded ScrapeCreators client. Preview is default; no retries or billing changes.

Only SCRAPECREATORS_API_KEY, supplied explicitly by the operator, is read for
--execute. Existing campaign initialization records the verified free allowance.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

import profile_campaign as engine

API = "https://api.scrapecreators.com"
BALANCE_PATH = "/v1/account/credit-balance"
ALLOWED = {BALANCE_PATH, *(value[0] for value in engine.ENDPOINTS.values())}


class ClientError(ValueError):
    pass


class TransportError(ClientError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise TransportError("Redirect refused; the API credential was not forwarded")


def http_get(path, params, api_key, *, timeout=30):
    """One GET, fixed host/endpoints, no remote errors or authentication echoed."""
    if path not in ALLOWED or not isinstance(api_key, str) or not 10 <= len(api_key) <= 500 or any(c.isspace() for c in api_key):
        raise ClientError("Invalid endpoint or API credential format")
    query = urllib.parse.urlencode({key: str(value).lower() if type(value) is bool else value for key, value in params.items()})
    url = API + path + ("?" + query if query else "")
    request = urllib.request.Request(url, headers={"x-api-key": api_key, "Accept": "application/json",
                                                   "User-Agent": "RaceLink-Metadata-Collector/27"}, method="GET")
    deadline = time.monotonic() + timeout
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=min(timeout, 15)) as response:
            if response.geturl().split("?", 1)[0] != API + path or response.status != 200:
                raise TransportError("Unexpected API response URL or status")
            data = bytearray()
            while True:
                if time.monotonic() >= deadline:
                    raise TransportError("Response deadline exceeded; reservation retained, no retry")
                chunk = response.read1(min(64 * 1024, engine.MAX_BYTES + 1 - len(data)))
                if time.monotonic() >= deadline:
                    raise TransportError("Response deadline exceeded; reservation retained, no retry")
                data.extend(chunk)
                if not chunk or len(data) > engine.MAX_BYTES:
                    break
    except urllib.error.HTTPError as exc:
        raise TransportError(f"API HTTP {exc.code}; no retry, no remote error body persisted") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise TransportError("Request outcome uncertain; reservation retained, no retry") from None
    if len(data) > engine.MAX_BYTES or api_key.encode("utf-8") in data:
        raise TransportError("Response oversized or contains the API credential; not persisted")
    try:
        payload = json.loads(data.decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        raise TransportError("Invalid JSON response; reservation retained, no retry") from None
    if not isinstance(payload, dict):
        raise TransportError("API response is not an object")
    return payload


def bind_client(folder):
    with engine.locked(folder) as state:
        current = engine.file_hash(__file__)
        old = state.get("client_sha256")
        if old and old != current:
            raise ClientError("Network client changed; review before resuming this campaign")
        state["client_sha256"] = current
        engine.atomic(Path(folder) / "state.json", state)


def reserve_balance(folder):
    with engine.locked(folder) as state:
        if any(check["state"] == "reserved" for check in state["credit_checks"]) or any(a["state"] == "reserved" for a in state["attempts"]):
            raise ClientError("A prior request outcome is unknown; reconcile it before any new request")
        if datetime.now(timezone.utc) - engine.timestamp(state["checked_at"]) > timedelta(hours=24):
            raise ClientError("Free allowance verification expired; no API request sent")
        # Official balance example declares a one-credit charge. Reserve it too;
        # do not assume housekeeping endpoints are free or refund automatically.
        if state["free_credits"] - state["reserved_credits"] < 2:
            raise ClientError("Fewer than two verified free credits remain for balance plus page")
        check = {"seq": len(state["credit_checks"]), "state": "reserved", "reserved_at": engine.now(),
                 "endpoint": BALANCE_PATH, "reserved_credits": 1}
        state["credit_checks"].append(check)
        state["reserved_credits"] += 1
        engine.atomic(Path(folder) / "state.json", state)
        return check["seq"]


def finish_balance(folder, seq, payload):
    if not isinstance(payload, dict) or payload.get("success") not in (None, True) or payload.get("error"):
        raise ClientError("Balance lookup did not succeed; no page request sent")
    remaining = engine.integer(payload.get("creditCount"), 0, 10**9, "balance creditCount")
    charged = payload.get("credits_charged")
    if charged is not None:
        engine.integer(charged, 0, 1, "balance request charge")
    if payload.get("credits_remaining") is not None:
        remaining = min(remaining, engine.integer(payload["credits_remaining"], 0, 10**9, "remaining credits"))
    with engine.locked(folder) as state:
        engine.integer(seq, 0, len(state["credit_checks"]) - 1, "balance check")
        check = state["credit_checks"][seq]
        if check["state"] != "reserved":
            raise ClientError("Balance check is no longer pending")
        check.update(state="complete", completed_at=engine.now(), credit_count=remaining,
                     charged_credits_declared=charged, reservation_retained=1)
        state["free_credits"] = min(state["free_credits"], state["reserved_credits"] + remaining)
        engine.atomic(Path(folder) / "state.json", state)
    return remaining


def run(folder, job_key, *, execute=False, max_pages=1, interval=2, transport=http_get, api_key=None):
    folder = Path(folder).resolve()
    engine.integer(max_pages, 1, 10, "pages per invocation (1–10)")
    if type(interval) not in (int, float) or not 2 <= interval <= 30:
        raise ClientError("Interval must be between 2 and 30 seconds")
    state = engine.load_state(folder)
    job = state["jobs"].get(job_key)
    if job is None:
        raise ClientError("Unknown planned profile")
    report = {"mode": "execute" if execute else "preview", "job": job_key,
              "max_pages": max_pages, "max_reserved_credits": 2 * max_pages,
              "free_credit_cap": state["free_credits"], "already_reserved_credits": state["reserved_credits"],
              "balance_endpoint": BALANCE_PATH, "page_endpoint": engine.ENDPOINTS[job["platform"]][0],
              "page_responses_ingested": 0, "requests_sent": 0, "automatic_retries": 0,
              "out_of_pocket_usd": 0, "catalog_modified": False, "publication_count": 0,
              "note": "Only the free allowance verified during campaign init is authorized; total account balance is not a new allowance."}
    if not execute:
        return report
    if api_key is None:
        api_key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not api_key:
        raise ClientError("Set SCRAPECREATORS_API_KEY explicitly; no browser or credential-store discovery is performed")
    if not isinstance(api_key, str) or not 10 <= len(api_key) <= 500 or any(c.isspace() for c in api_key):
        raise ClientError("Invalid API credential format")
    lock = folder / ".client.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ClientError("Another client invocation is active") from None
    os.close(fd)
    try:
        bind_client(folder)
        for page_index in range(max_pages):
            state = engine.load_state(folder)
            job = state["jobs"][job_key]
            if job["state"] in {"complete", "stopped"} or len(job["attempts"]) >= job["max_pages"]:
                report["stop_reason"] = "profile_finished_stopped_or_capped"
                break
            if state["free_credits"] - state["reserved_credits"] < 2:
                report["stop_reason"] = "verified_free_credit_cap"
                break
            if page_index:
                time.sleep(interval)
            check_seq = reserve_balance(folder)
            report["requests_sent"] += 1
            balance = transport(BALANCE_PATH, {}, api_key)
            remaining = finish_balance(folder, check_seq, balance)
            if remaining < 1:
                report["stop_reason"] = "provider_reports_no_credit"
                break
            request = engine.reserve(folder, job_key)
            report["requests_sent"] += 1
            payload = transport(request["request"]["endpoint"], request["request"]["params"], api_key)
            # Validate response contract before storing native content. No errors,
            # secrets or response headers belong in the raw metadata directory.
            engine.native_page(payload, job["platform"])
            raw_bytes = engine.encoded(payload)
            if len(raw_bytes) > engine.MAX_BYTES or api_key.encode("utf-8") in raw_bytes:
                raise ClientError("Response is oversized or contains API credentials; not persisted")
            raw_dir = folder / "private-raw"
            if raw_dir.is_symlink():
                raise ClientError("Private response directory must not be a symbolic link")
            raw_dir.mkdir(exist_ok=True)
            response_file = raw_dir / f"response-{request['attempt']:04d}.json"
            with response_file.open("xb") as stream:
                stream.write(raw_bytes)
            engine.ingest(folder, request["attempt"], response_file)
            report["page_responses_ingested"] += 1
        report.update(final_state=engine.summary(engine.load_state(folder)))
        return report
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--job", required=True)
    parser.add_argument("--max-pages", default=1, type=int)
    parser.add_argument("--interval", default=2, type=float)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--execute", action="store_true")
    modes.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.folder, args.job, execute=args.execute, max_pages=args.max_pages,
                             interval=args.interval), ensure_ascii=True))
    except (ClientError, engine.CampaignError) as exc:
        parser.exit(2, "COLLECTOR: " + str(exc) + ". No automatic retry.\n")
    except (OSError, ValueError, KeyError, TypeError):
        # Do not serialize unknown exceptions; some libraries include request data.
        parser.exit(2, "COLLECTOR: execution stopped; inspect the local ledger. Unknown request outcomes retain their reservation. No automatic retry.\n")


if __name__ == "__main__":
    main()
