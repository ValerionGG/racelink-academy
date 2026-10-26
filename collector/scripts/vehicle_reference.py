#!/usr/bin/env python3
"""Preview or cache one official NHTSA vPIC make/year lookup; standard library only.

This produces reference metadata for review, never vehicle compatibility advice.
No VIN, credentials, proxy, redirect, media, database or application writes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
import json
import os
from pathlib import Path
import ssl
import unicodedata
from urllib.parse import quote, urlsplit

VERSION = "1.0.0"
HOST = "vpic.nhtsa.dot.gov"
DOCS = "https://vpic.nhtsa.dot.gov/api/"
MAX_BYTES = 8 * 1024 * 1024
SCOPE = {
    "authority": "NHTSA vPIC",
    "jurisdiction": "US",
    "coverage": "Manufacturer submissions to the US NHTSA; not a complete French or worldwide vehicle register.",
    "make_matching": "API LIKE search; requested make may match multiple makes.",
    "purpose": "Candidate make/model/year vocabulary for human review.",
    "proves_vehicle_compatibility": False,
    "contains_service_procedures": False,
    "contains_engine_oil_or_fuel_specifications": False,
    "vin_requested": False,
}


class ReferenceError(ValueError):
    """A request, response or existing cache cannot be safely used."""


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def normalized_name(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def make_plan(make: str, year: int, *, current_year: int | None = None) -> dict:
    """Validate a bounded name lookup; reject wildcard and path/query syntax."""
    if not isinstance(make, str) or any(unicodedata.category(c).startswith("C") for c in make):
        raise ReferenceError("Make must be a readable name without control characters")
    make = " ".join(unicodedata.normalize("NFC", make).split())
    allowed_punctuation = " -'’&.()"
    if not 2 <= len(make) <= 80 or not any(c.isalpha() for c in make):
        raise ReferenceError("Make must contain letters and be 2–80 characters long")
    if any(unicodedata.category(c)[0] not in "LNM" and c not in allowed_punctuation for c in make):
        raise ReferenceError("Make contains unsupported punctuation or wildcard characters")
    latest = (current_year if current_year is not None else dt.date.today().year) + 1
    if type(year) is not int or not 1996 <= year <= latest:
        raise ReferenceError(f"Model year must be an integer between 1996 and {latest}")
    url = f"https://{HOST}/api/vehicles/GetModelsForMakeYear/make/{quote(make, safe='')}/modelyear/{year}?format=json"
    return {"provider": "nhtsa-vpic", "endpoint": "GetModelsForMakeYear", "make": make,
            "model_year": year, "url": url, "method": "GET", "max_requests": 1,
            "max_response_bytes": MAX_BYTES, "documentation_url": DOCS}


def plan_sha(plan: dict) -> str:
    return sha(json_bytes(plan))


def parse_response(raw: bytes, plan: dict) -> dict:
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ReferenceError("Response exceeds the 8 MiB limit or is not bytes")
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReferenceError("Response is not UTF-8 JSON") from exc
    if not isinstance(data, dict) or not isinstance(data.get("Results"), list):
        raise ReferenceError("Expected an API object containing Results")
    rows = data["Results"]
    if type(data.get("Count")) is not int or data["Count"] != len(rows):
        raise ReferenceError("API Count is not an integer matching Results")
    if not isinstance(data.get("Message"), str) or not isinstance(data.get("SearchCriteria"), str):
        raise ReferenceError("Missing API Message or SearchCriteria")
    if data.get("ErrorCode") not in (None, 0, "0") or data.get("ErrorMessage"):
        raise ReferenceError("API reported an error")
    models, seen = [], set()
    for row in rows:
        if not isinstance(row, dict):
            raise ReferenceError("Invalid model record")
        for field in ("Make_ID", "Model_ID"):
            if type(row.get(field)) is not int or row[field] <= 0:
                raise ReferenceError(f"Invalid positive integer {field}")
        for field in ("Make_Name", "Model_Name"):
            value = row.get(field)
            if (not isinstance(value, str) or not value.strip() or len(value) > 200
                    or any(unicodedata.category(c).startswith("C") for c in value)):
                raise ReferenceError(f"Invalid {field}")
        identity = (row["Make_ID"], row["Model_ID"])
        if identity in seen:
            raise ReferenceError("Duplicate make/model identifiers in API response")
        seen.add(identity)
        models.append({"make_id": row["Make_ID"], "model_id": row["Model_ID"],
                       "make_name": row["Make_Name"], "model_name": row["Model_Name"],
                       "requested_model_year": plan["model_year"],
                       "exact_make_name_match": normalized_name(row["Make_Name"]) == normalized_name(plan["make"])})
    return {"count": len(models), "models": models, "api_message": data["Message"],
            "api_search_criteria": data["SearchCriteria"]}


def fetch_one(plan: dict, *, timeout: float = 20, connection_factory=None) -> bytes:
    """Exactly one HTTPS GET. http.client never follows redirects or uses env proxies."""
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 1 <= timeout <= 60:
        raise ReferenceError("Timeout must be between 1 and 60 seconds")
    expected = make_plan(plan.get("make"), plan.get("model_year"))
    if plan != expected:
        raise ReferenceError("Request does not match the fixed NHTSA endpoint")
    factory = connection_factory or http.client.HTTPSConnection
    connection = factory(HOST, timeout=timeout, context=ssl.create_default_context())
    try:
        target = urlsplit(plan["url"])
        connection.request("GET", target.path + "?" + target.query,
                           headers={"Accept": "application/json", "Accept-Encoding": "identity",
                                    "User-Agent": f"RaceLink-VehicleReference/{VERSION}"})
        response = connection.getresponse()
        if response.status != 200:
            raise ReferenceError(f"HTTP {response.status}; stopped without redirect or retry")
        content_type = (response.getheader("Content-Type") or "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ReferenceError("API response is not application/json")
        if (response.getheader("Content-Encoding") or "identity").lower() != "identity":
            raise ReferenceError("Unexpected content encoding")
        length = response.getheader("Content-Length")
        if length is not None and (not length.isdigit() or int(length) > MAX_BYTES):
            raise ReferenceError("Invalid or excessive Content-Length")
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ReferenceError("Response exceeds the 8 MiB limit")
        if length is not None and len(raw) != int(length):
            raise ReferenceError("Incomplete API response")
        return raw
    except (OSError, http.client.HTTPException) as exc:
        raise ReferenceError("NHTSA request failed; stopped without retry") from exc
    finally:
        connection.close()


def read_cache(output: Path, plan: dict) -> dict | None:
    report_path = output / "reference.json"
    if not report_path.exists():
        return None
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        raw = (output / "response.json").read_bytes()
        if (report.get("status") != "completed" or report.get("request") != plan
                or report.get("request_sha256") != plan_sha(plan)):
            raise ReferenceError("Existing completed output belongs to a different request")
        source = report.get("source", {})
        if source.get("sha256") != sha(raw):
            raise ReferenceError("Cached source hash does not match")
        if (source.get("url") != plan["url"] or source.get("bytes") != len(raw)
                or source.get("http_status") != 200 or source.get("raw_file") != "response.json"):
            raise ReferenceError("Cached provenance does not match its request")
        try:
            retrieved_at = dt.datetime.fromisoformat(source["retrieved_at"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ReferenceError("Cached retrieval date is invalid") from exc
        if retrieved_at.utcoffset() != dt.timedelta(0):
            raise ReferenceError("Cached retrieval date must include UTC timezone")
        if report.get("result") != parse_response(raw, plan) or report.get("scope") != SCOPE:
            raise ReferenceError("Cached normalized metadata does not match its source")
        return report
    except (OSError, UnicodeError, json.JSONDecodeError, AttributeError) as exc:
        raise ReferenceError("Existing output is incomplete or invalid; use a new directory") from exc


def execute(plan: dict, output: Path, *, timeout: float = 20, fetcher=fetch_one) -> dict:
    """Reuse verified completed cache. Never replace different or partial output."""
    if not isinstance(output, Path):
        output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    lock = output / ".reference.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ReferenceError("Output directory is locked by another operation") from exc
    os.close(descriptor)
    try:
        cached = read_cache(output, plan)
        if cached is not None:
            return {"mode": "cache", "requests": 0, "report": cached}
        if any(p.name != lock.name for p in output.iterdir()):
            raise ReferenceError("Output directory contains unfinished or unrelated files; use a new directory")
        raw = fetcher(plan, timeout=timeout)
        result = parse_response(raw, plan)
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
        report = {"version": VERSION, "status": "completed", "request": plan,
                  "request_sha256": plan_sha(plan), "scope": SCOPE, "result": result,
                  "source": {"url": plan["url"], "retrieved_at": timestamp, "sha256": sha(raw),
                             "bytes": len(raw), "http_status": 200, "raw_file": "response.json"}}
        # The manifest is the completion marker; interruption leaves an unreplayable partial cache.
        with (output / "response.json").open("xb") as stream:
            stream.write(raw)
        with (output / "reference.json").open("xb") as stream:
            stream.write(json_bytes(report))
        return {"mode": "fetched", "requests": 1, "report": report}
    finally:
        lock.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--make", required=True, help="Full or partial make name; no wildcard")
    parser.add_argument("--year", type=int, required=True, help="Model year, 1996 to current year + 1")
    parser.add_argument("--output", type=Path, required=True, help="Explicit dedicated output directory")
    parser.add_argument("--execute", action="store_true", help="Perform at most one GET; otherwise only show the plan")
    parser.add_argument("--timeout", type=float, default=20, help="Socket timeout in seconds, 1–60")
    args = parser.parse_args(argv)
    try:
        plan = make_plan(args.make, args.year)
        if not 1 <= args.timeout <= 60:
            raise ReferenceError("Timeout must be between 1 and 60 seconds")
        if not args.execute:
            print(json.dumps({"mode": "preview", "requests": 0, "writes": 0,
                              "output": str(args.output.resolve()), "request": plan, "scope": SCOPE}, ensure_ascii=False, indent=2))
        else:
            outcome = execute(plan, args.output, timeout=args.timeout)
            print(json.dumps({"mode": outcome["mode"], "requests": outcome["requests"],
                              "models": outcome["report"]["result"]["count"],
                              "output": str(args.output.resolve()), "scope": SCOPE}, ensure_ascii=False, indent=2))
        return 0
    except (ReferenceError, OSError) as exc:
        print(json.dumps({"status": "stopped", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
