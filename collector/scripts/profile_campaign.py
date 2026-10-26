#!/usr/bin/env python3
"""Offline profile-page campaign ledger and metadata quarantine, never an API client.

Reserve a free-credit page before an external UI/API operator makes one request.
Ingest its JSON response afterwards. No credential, browser, network or DB code.
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
import sys

VERSION = "1.0.0"
MAX_BYTES = 32 * 1024 * 1024
MAX_ROWS = 100000
ENDPOINTS = {
    "tiktok": ("/v3/tiktok/profile/videos", "max_cursor"),
    "instagram": ("/v2/instagram/user/posts", "next_max_id"),
}


class CampaignError(ValueError):
    pass


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def file_hash(path):
    hash_value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hash_value.update(block)
    return hash_value.hexdigest()


def read(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_BYTES:
        raise CampaignError("Expected a regular local JSON file at most 32 MiB")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encoded(value))
    os.replace(temporary, path)


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def timestamp(value):
    if not isinstance(value, str):
        raise CampaignError("A timezone-aware timestamp is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CampaignError("Invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise CampaignError("A timezone-aware timestamp is required")
    return parsed


def integer(value, minimum, maximum, label):
    if type(value) is not int or not minimum <= value <= maximum:
        raise CampaignError(f"Invalid {label}")
    return value


def cursor(value):
    if value is None:
        return None
    if type(value) is int and value >= 0:
        value = str(value)
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_=+./:-]{1,2048}", value) or "://" in value:
        raise CampaignError("Expected an opaque cursor, never a URL or credential")
    return value


def flag(value):
    if type(value) is bool or type(value) is int and value in (0, 1):
        return bool(value)
    raise CampaignError("Unknown boolean declaration")


def init(folder, plan, app):
    folder, app = Path(folder).resolve(), Path(app).resolve()
    if folder.exists() and any(folder.iterdir()):
        raise CampaignError("Use an empty campaign directory; caps cannot be reset")
    if set(plan) != {"version", "free_credits", "checked_at", "auto_recharge", "out_of_pocket_usd", "profiles"}:
        raise CampaignError("Unexpected plan fields; never include account details or credentials")
    if plan["version"] != 1 or type(plan["version"]) is not int:
        raise CampaignError("Expected plan version 1")
    integer(plan["free_credits"], 1, 100, "free credit cap (1–100)")
    if plan["auto_recharge"] is not False or plan["out_of_pocket_usd"] != 0:
        raise CampaignError("Only free credits and disabled recharge are allowed")
    checked = timestamp(plan["checked_at"])
    if not timedelta(0) <= datetime.now(timezone.utc) - checked <= timedelta(hours=24):
        raise CampaignError("Verify free balance and recharge settings within the last 24 hours")
    profiles = plan["profiles"]
    if not isinstance(profiles, list) or not 1 <= len(profiles) <= 1000:
        raise CampaignError("Provide 1–1000 explicit public profile handles")
    jobs = {}
    for item in profiles:
        if set(item) != {"platform", "handle", "max_pages", "region"}:
            raise CampaignError("Profile fields must be platform, handle, max_pages, region")
        platform, handle = item["platform"], item["handle"]
        if platform not in ENDPOINTS or not isinstance(handle, str) or not re.fullmatch(r"[A-Za-z0-9._]{1,30}", handle):
            raise CampaignError("Invalid platform or public handle")
        integer(item["max_pages"], 1, 100, "profile page cap")
        if not isinstance(item["region"], str) or not re.fullmatch(r"[A-Z]{2}", item["region"]):
            raise CampaignError("Region requires an explicit two-letter code")
        key = platform + ":" + handle.casefold()
        if key in jobs:
            raise CampaignError("Duplicate profile in plan")
        jobs[key] = {**item, "state": "pending", "next_cursor": None, "attempts": []}
    helper = app / "scripts/social_metadata.py"
    if not helper.is_file():
        raise CampaignError("Existing social_metadata.py is required")
    state = {"tool": "profile_campaign", "version": VERSION, "engine_sha256": file_hash(__file__),
             "helper_sha256": file_hash(helper), "app": str(app), "plan_sha256": digest(plan),
             "created_at": now(), "free_credits": plan["free_credits"], "reserved_credits": 0,
             "checked_at": plan["checked_at"], "rows": 0, "jobs": jobs, "attempts": [], "external_exports": [], "credit_checks": [],
             "network_requests": 0, "catalog_modified": False, "out_of_pocket_usd": 0}
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / ".campaign.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise CampaignError("Campaign initialization is already in progress") from exc
    os.close(fd)
    try:
        if (folder / "state.json").exists():
            raise CampaignError("Campaign already exists; caps cannot be reset")
        atomic(folder / "state.json", state)
    finally:
        lock.unlink(missing_ok=True)
    return summary(state)


def load_state(folder):
    state = read(Path(folder) / "state.json")
    if state.get("tool") != "profile_campaign" or state.get("version") != VERSION or state.get("engine_sha256") != file_hash(__file__):
        raise CampaignError("Campaign engine changed; do not silently resume")
    helper = Path(state["app"]) / "scripts/social_metadata.py"
    if file_hash(helper) != state["helper_sha256"]:
        raise CampaignError("Metadata helper changed; review before resuming")
    for attempt in state["attempts"]:
        if attempt["state"] == "complete":
            page = Path(folder) / attempt["file"]
            if not re.fullmatch(r"page-\d{4}\.json", attempt["file"]) or page.is_symlink() or file_hash(page) != attempt["sha256"]:
                raise CampaignError("Saved page evidence is missing or changed")
    for attachment in state["external_exports"]:
        name = attachment["file"]
        page = Path(folder) / name
        if not re.fullmatch(r"external-\d{4}\.json", name) or page.is_symlink() or file_hash(page) != attachment["sha256"]:
            raise CampaignError("Attached export evidence is missing or changed")
    return state


@contextmanager
def locked(folder):
    folder = Path(folder).resolve()
    lock = folder / ".campaign.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise CampaignError("Campaign is locked; no concurrent credit reservations") from exc
    os.close(fd)
    try:
        state = load_state(folder)
        yield state
    finally:
        lock.unlink(missing_ok=True)


def summary(state):
    return {"tool": state["tool"], "profiles": len(state["jobs"]), "free_credit_cap": state["free_credits"],
            "reserved_credits": state["reserved_credits"], "responses": sum(a["state"] == "complete" for a in state["attempts"]),
            "rows": state["rows"], "external_exports": len(state["external_exports"]), "network_requests_by_registry": 0, "catalog_modified": False,
            "credit_checks_reserved": len(state["credit_checks"]),
            "out_of_pocket_usd": 0, "all_metadata_requires_review": True,
            "jobs": {key: {"state": item["state"], "pages_reserved": len(item["attempts"]),
                           "max_pages": item["max_pages"]} for key, item in state["jobs"].items()}}


def reserve(folder, job_key):
    with locked(folder) as state:
        if any(check["state"] == "reserved" for check in state["credit_checks"]):
            raise CampaignError("A balance check outcome is unknown; reconcile before any page")
        if any(a["state"] == "reserved" for a in state["attempts"]):
            raise CampaignError("An earlier request outcome is unknown; never retry automatically")
        if state["reserved_credits"] >= state["free_credits"]:
            raise CampaignError("Free credit reservation cap reached")
        if datetime.now(timezone.utc) - timestamp(state["checked_at"]) > timedelta(hours=24):
            raise CampaignError("Free balance observation expired; reconcile before a new campaign")
        job = state["jobs"].get(job_key)
        if not job or job["state"] in {"complete", "stopped"} or len(job["attempts"]) >= job["max_pages"]:
            raise CampaignError("Profile is unknown, stopped, complete or at its page cap")
        endpoint, cursor_field = ENDPOINTS[job["platform"]]
        params = {"handle": job["handle"], "trim": False}
        if job["platform"] == "tiktok":
            params.update(region=job["region"], sort_by="latest", include_pinned=False)
        if job["next_cursor"] is not None:
            params[cursor_field] = job["next_cursor"]
        attempt = {"seq": len(state["attempts"]), "job": job_key, "state": "reserved", "reserved_at": now(),
                   "request_cursor": job["next_cursor"], "reserved_credits": 1,
                   "request": {"provider": "scrapecreators", "method": "GET", "endpoint": endpoint, "params": params}}
        state["attempts"].append(attempt)
        job["attempts"].append(attempt["seq"])
        job["state"] = "in_progress"
        state["reserved_credits"] += 1
        atomic(Path(folder) / "state.json", state)
        return {"attempt": attempt["seq"], "request": attempt["request"], "network_executed": False,
                "instruction": "Make at most one external request, then ingest its native JSON. Never auto-retry."}


def stop(folder, seq, reason):
    if reason not in {"access_restricted", "rate_limited", "quota_exhausted", "request_failed", "uncertain_outcome"}:
        raise CampaignError("Use a supported non-sensitive stop reason")
    with locked(folder) as state:
        integer(seq, 0, len(state["attempts"]) - 1, "attempt")
        attempt = state["attempts"][seq]
        if attempt["state"] != "reserved":
            raise CampaignError("Only an unresolved attempt can be stopped")
        attempt.update(state="stopped", reason=reason, stopped_at=now())
        state["jobs"][attempt["job"]]["state"] = "stopped"
        # Reservation is retained even when the provider may charge zero.
        atomic(Path(folder) / "state.json", state)
        return summary(state)


def text(value, limit=20000):
    if value is None:
        return ""
    if not isinstance(value, str) or len(value) > limit:
        raise CampaignError("Source text is missing or exceeds its bound")
    if re.search(r"https?://\S*[?&](?:access_token|token|secret|key|auth)=", value, re.I):
        raise CampaignError("Credential-like URL in source text")
    return value


def redact_contacts(value):
    value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[contact retiré]", value)
    return re.sub(r"(?<!\w)(?:\+33|0)[1-9](?:[ .-]?\d{2}){4}(?!\d)", "[contact retiré]", value)


def permalink(value, platform):
    from urllib.parse import urlsplit
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.hostname not in {platform + ".com", "www." + platform + ".com"} or parsed.username or parsed.password or parsed.port:
        return None
    if platform == "tiktok":
        match = re.fullmatch(r"/@([A-Za-z0-9._]{1,30})/video/(\d{10,30})/?", parsed.path)
        if match:
            return f"tiktok:{match[2]}", f"https://www.tiktok.com/@{match[1]}/video/{match[2]}"
    else:
        match = re.fullmatch(r"/(?:[A-Za-z0-9._]{1,30}/)?(p|reel|reels)/([A-Za-z0-9_-]{5,64})/?", parsed.path)
        if match:
            kind = "reel" if match[1] in {"reel", "reels"} else "p"
            return f"instagram:{match[2]}", f"https://www.instagram.com/{kind}/{match[2]}/"
    return None


def native_row(row, platform, *, root_private=False):
    if not isinstance(row, dict):
        raise CampaignError("Publication is not an object")
    reasons = ["editorial_review_required"]
    result = {}
    if platform == "tiktok":
        author = row.get("author") if isinstance(row.get("author"), dict) else {}
        handle, identifier = author.get("unique_id"), str(row.get("aweme_id", ""))
        identity = permalink(row.get("share_url"), platform)
        if not identity and isinstance(handle, str) and re.fullmatch(r"[A-Za-z0-9._]{1,30}", handle) and re.fullmatch(r"\d{10,30}", identifier):
            identity = permalink(f"https://www.tiktok.com/@{handle}/video/{identifier}", platform)
        if identity and identifier and identity[0].split(":", 1)[1] != identifier:
            raise CampaignError("TikTok source ID and permalink contradict each other")
        caption = text(row.get("desc"))
        result["creator"] = text(handle, 100)
        status = row.get("status") if isinstance(row.get("status"), dict) else {}
        private = root_private or flag(author.get("secret", False)) or status.get("private_status", 0) != 0 or flag(status.get("self_see", False))
        restricted = flag(status.get("is_delete", False)) or flag(status.get("is_prohibited", False))
        video = row.get("aweme_type") == 0 and not row.get("image_post_info") and isinstance(row.get("video"), dict)
        sponsored = flag(row.get("is_ad", False)) or flag(row.get("is_ads", False)) or bool(row.get("commerce_info")) or bool(row.get("shop_product_url"))
        result["media_type"] = "VIDEO" if video else "UNKNOWN"
        result["is_video"] = bool(video)
        if not video:
            reasons.append("video_kind_not_established_or_slideshow")
        if restricted:
            result["availability"] = "needs_auth"
            reasons.append("restricted_source")
    else:
        owner = row.get("user") if isinstance(row.get("user"), dict) else {}
        code = row.get("code")
        identity = permalink(row.get("url"), platform)
        if not identity and isinstance(code, str) and re.fullmatch(r"[A-Za-z0-9_-]{5,64}", code):
            identity = permalink(f"https://www.instagram.com/p/{code}/", platform)
        if identity and code and identity[0].split(":", 1)[1] != code:
            raise CampaignError("Instagram shortcode and permalink contradict each other")
        cap = row.get("caption")
        caption = text(cap.get("text") if isinstance(cap, dict) else cap)
        result["creator"] = text(owner.get("username"), 100)
        private = root_private or flag(owner.get("is_private", False))
        video = type(row.get("media_type")) is int and row["media_type"] == 2 and not row.get("carousel_media")
        sponsored = flag(row.get("is_paid_partnership", False)) or flag(row.get("is_ad", False))
        result.update(media_type="VIDEO" if video else "UNKNOWN", is_video=bool(video))
        if not video:
            reasons.append("video_kind_not_established_or_carousel")
    if not identity:
        raise CampaignError("No publication identity in the publication's own metadata")
    sanitized_caption = redact_contacts(caption)
    result.update(url=identity[1], caption="" if private else sanitized_caption, isPrivate=private, isSponsored=sponsored,
                  source_contact_redacted=sanitized_caption != caption)
    if private:
        reasons.append("private_source")
    if sponsored:
        reasons.append("commercial_context_requires_review")
    if not caption.strip():
        reasons.append("missing_source_caption")
    return identity[0], result, reasons


def native_page(payload, platform):
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise CampaignError("Provider did not declare success; do not persist error bodies")
    if payload.get("status") not in (None, "ok") or payload.get("status_code") not in (None, 0) or payload.get("status_msg") not in (None, "") or payload.get("message") not in (None, "") or payload.get("error") or payload.get("errorStatus"):
        raise CampaignError("Response contains an access/status message; review outside the ledger")
    list_key, more_key, cursor_key = ("aweme_list", "has_more", "max_cursor") if platform == "tiktok" else ("items", "more_available", "next_max_id")
    rows = payload.get(list_key)
    if not isinstance(rows, list) or len(rows) > 1000:
        raise CampaignError("Expected the documented list with at most 1000 source rows")
    has_more = flag(payload.get(more_key))
    next_cursor = cursor(payload.get(cursor_key)) if has_more else None
    if has_more and next_cursor is None:
        raise CampaignError("Provider indicates more pages but omitted its cursor")
    integer(payload.get("credits_charged"), 0, 1, "charged credits")
    integer(payload.get("credits_remaining"), 0, 10**9, "remaining credits")
    user = payload.get("user") if isinstance(payload.get("user"), dict) else {}
    root_private = flag(user.get("is_private", False))
    return rows, next_cursor, has_more, root_private


def ingest(folder, seq, response):
    response = Path(response).resolve()
    if not response.is_file() or response.is_symlink():
        raise CampaignError("Expected a regular response file")
    with response.open("rb") as source_stream:
        source_bytes = source_stream.read(MAX_BYTES + 1)
    if len(source_bytes) > MAX_BYTES:
        raise CampaignError("Response exceeds 32 MiB")
    payload = json.loads(source_bytes.decode("utf-8-sig"))
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    with locked(folder) as state:
        integer(seq, 0, len(state["attempts"]) - 1, "attempt")
        attempt = state["attempts"][seq]
        if attempt["state"] == "complete" and attempt["source_sha256"] == source_hash:
            return {**summary(state), "idempotent_replay": True}
        if attempt["state"] != "reserved":
            raise CampaignError("Attempt is no longer awaiting this response")
        job = state["jobs"][attempt["job"]]
        rows, next_cursor, more, private = native_page(payload, job["platform"])
        if state["rows"] + len(rows) > MAX_ROWS:
            raise CampaignError("Campaign row bound reached; response remains uncommitted")
        used = {a["request_cursor"] for a in state["attempts"] if a["job"] == attempt["job"]}
        cycle = more and next_cursor in used
        sys.path.insert(0, state["app"])
        from scripts.social_metadata import normalize_social_metadata
        projected = []
        for index, row in enumerate(rows, 1):
            evidence = {"source_response_sha256": source_hash, "source_row_sha256": digest(row), "row": index,
                        "attempt": seq, "provider": "scrapecreators", "schema": attempt["request"]["endpoint"],
                        "verification_scope": "exported_metadata_not_independently_verified"}
            try:
                identifier, record, reasons = native_row(row, job["platform"], root_private=private)
                if record.get("creator") and record["creator"].casefold() != job["handle"].casefold():
                    reasons.append("creator_differs_from_requested_profile")
                social = normalize_social_metadata({**record, "verification_scope": evidence["verification_scope"]})
                display = {key: social[key] for key in ("title", "description", "hashtags", "mentions", "links", "needs_title_review", "field_provenance")}
                projected.append({"id": identifier, "record": record, "display": display, "reasons": reasons,
                                  "evidence": evidence, "review_status": "quarantine", "vehicle_compatibility": [],
                                  "audio_language_verified": False, "transcript_status": "not_obtained", "license": "unknown"})
            except (CampaignError, ValueError, TypeError):
                projected.append({"id": None, "record": None, "reasons": ["invalid_or_incomplete_metadata"],
                                  "evidence": evidence, "review_status": "quarantine"})
        filename = f"page-{seq:04d}.json"
        page = {"version": 1, "source_sha256": source_hash, "rows": projected,
                "cursor_evidence": {"request": attempt["request_cursor"], "next": next_cursor, "has_more": more},
                "credits_charged": payload["credits_charged"], "credits_remaining": payload["credits_remaining"]}
        atomic(Path(folder) / filename, page)
        attempt.update(state="complete", completed_at=now(), file=filename, sha256=file_hash(Path(folder) / filename),
                       source_sha256=source_hash, row_count=len(rows), credits_charged=payload["credits_charged"],
                       credits_remaining=payload["credits_remaining"], has_more=more, next_cursor=next_cursor)
        state["rows"] += len(rows)
        job["next_cursor"] = next_cursor
        job["state"] = "stopped" if cycle else "pending" if more else "complete"
        if cycle:
            job["stop_reason"] = "provider_cursor_cycle"
        # A lower observed remaining balance tightens, never increases, the cap.
        state["free_credits"] = min(state["free_credits"], state["reserved_credits"] + payload["credits_remaining"])
        atomic(Path(folder) / "state.json", state)
        return {**summary(state), "idempotent_replay": False, "cursor_cycle_stopped": cycle}


def export_review(folder, output):
    output = Path(output).resolve()
    if output.exists():
        raise CampaignError("Use a fresh review directory")
    with locked(folder) as state:
        grouped, invalid = {}, []
        pages = [attempt for attempt in state["attempts"] if attempt["state"] == "complete"] + state["external_exports"]
        for entry in pages:
            page = read(Path(folder) / entry["file"])
            for row in page["rows"]:
                if row["id"] is None:
                    invalid.append(row)
                else:
                    grouped.setdefault(row["id"], []).append(row)
        output.mkdir(parents=True)
        conflicts = 0
        export_rows = {platform: [] for platform in ENDPOINTS}
        with (output / "quarantine.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
            for identifier, variants in sorted(grouped.items()):
                variants_by_hash = {}
                for variant in variants:
                    key = digest(variant["record"])
                    if key not in variants_by_hash:
                        variants_by_hash[key] = {**variant, "all_evidence": []}
                    variants_by_hash[key]["all_evidence"].append(variant["evidence"])
                    # Preserve every observation including restrictive variants.
                    export_rows[identifier.split(":", 1)[0]].append({**variant["record"],
                        "campaign_evidence": variant["evidence"], "campaign_review_status": "quarantine"})
                conflict = len(variants_by_hash) > 1
                conflicts += conflict
                entry = {"id": identifier, "review_status": "quarantine", "observations": len(variants),
                         "distinct_metadata_variants": len(variants_by_hash), "conflicting_variants": conflict,
                         "reasons": sorted({reason for variant in variants for reason in variant["reasons"]}),
                         "variants": list(variants_by_hash.values())}
                stream.write(encoded(entry).decode("utf-8"))
        atomic(output / "invalid-rows.json", invalid)
        manifests = []
        for platform, rows in export_rows.items():
            if not rows:
                continue
            platform_dir = output / platform
            platform_dir.mkdir()
            atomic(platform_dir / "publications.json", rows)
            manifest = {"version": 1, "kind": "PUBLIC_EXPORT", "source": {
                "name": "Campaign provider metadata; editorial review required",
                "kind": "provider_export", "source_url": "https://github.com/ValerionGG/racelink-academy",
                "evidence_reference": "../quarantine.jsonl contains all variants and original response/row hashes",
                "captured_at": now()}, "pages": [{"file": "publications.json", "format": "json",
                    "schema": "generic", "sha256": file_hash(platform_dir / "publications.json")}]}
            atomic(platform_dir / "manifest.json", manifest)
            manifests.append(platform + "/manifest.json")
        report = {**summary(state), "unique_identities": len(grouped), "invalid_rows": len(invalid),
                  "repeated_identity_observations": sum(len(v) - 1 for v in grouped.values()),
                  "identities_with_different_metadata": conflicts, "accepted_for_publication": 0,
                  "public_export_manifests_for_review_only": manifests,
                  "quarantine_sha256": file_hash(output / "quarantine.jsonl"), "created_at": now(),
                  "scope": "Metadata only. No media watched, transcript, audio language, vehicle fitment or licence verified."}
        atomic(output / "report.json", report)
        return report


def attach_export(folder, manifest):
    """Reuse PUBLIC_EXPORT mappings for other providers; never invent raw schemas.

    Bright Data and Apify exports must first have a reviewed, provider-specific
    projection. Native JSON is not re-labelled generic just to pass this gate.
    """
    with locked(folder) as state:
        sys.path.insert(0, state["app"])
        from scripts.public_export import load_manifest, page_rows, map_row
        from scripts.social_metadata import normalize_social_metadata
        declaration, paths = load_manifest(manifest)
        if declaration["source"]["kind"] == "indexed_export":
            raise CampaignError("Indexed excerpts stay in social_queue; this campaign requires direct exported metadata")
        snapshot_hash = digest(declaration)
        if any(item["manifest_sha256"] == snapshot_hash for item in state["external_exports"]):
            return {**summary(state), "idempotent_replay": True}
        projected = []
        source = declaration["source"]
        for page, path in zip(declaration["pages"], paths):
            for index, row in enumerate(page_rows(path, page), 1):
                if state["rows"] + len(projected) >= MAX_ROWS:
                    raise CampaignError("Campaign row cap exceeded; attachment was not committed")
                evidence = {"provider": "public_export", "provider_name": source["name"], "source_kind": source["kind"],
                            "manifest_sha256": snapshot_hash, "source_page_sha256": page["sha256"],
                            "source_row_sha256": digest(row), "row": index, "schema": page["schema"],
                            "verification_scope": "indexed_export_title_only" if source["kind"] == "indexed_export" else "exported_metadata_not_independently_verified"}
                # Retain the identity of a restricted/invalid variant so it cannot
                # disappear behind another provider's apparently clean version.
                url_key = {"generic": "url", "meta_graph": "permalink", "tiktok_display": "share_url"}[page["schema"]]
                identity = None
                if isinstance(row, dict):
                    for platform in ENDPOINTS:
                        identity = permalink(row.get(url_key), platform)
                        if identity:
                            break
                try:
                    mapped, _ = map_row(row, page["schema"], source["kind"] == "indexed_export")
                    if not identity:
                        raise CampaignError("Missing valid social publication identity")
                    record = {"url": identity[1], "title": mapped.get("title", ""), "caption": mapped.get("caption", ""),
                              "creator": mapped.get("uploader", mapped.get("ownerUsername", "")),
                              "media_type": mapped.get("type", "UNKNOWN"), "hashtags": mapped.get("hashtags", []),
                              "isPrivate": mapped.get("isPrivate", False), "isSponsored": mapped.get("isSponsored", False)}
                    for key in ("availability", "isVideo", "isPhoto", "isStory"):
                        if key in mapped:
                            record[key] = mapped[key]
                    if mapped.get("isPhoto"):
                        record["is_photo"] = True
                    if mapped.get("isStory"):
                        record["is_story"] = True
                    if record["isPrivate"]:
                        record.update(caption="", title="")
                    else:
                        record["caption"] = redact_contacts(record["caption"])
                        record["title"] = redact_contacts(record["title"])
                    social = normalize_social_metadata({**record, "verification_scope": evidence["verification_scope"]})
                    display = {key: social[key] for key in ("title", "description", "hashtags", "mentions", "links", "needs_title_review", "field_provenance")}
                    reasons = ["editorial_review_required", "external_provider_projection_requires_review"]
                    if record["isPrivate"]:
                        reasons.append("private_source")
                except (ValueError, KeyError, TypeError):
                    record = {"url": identity[1], "caption": "", "is_video": False, "media_type": "UNKNOWN"} if identity else None
                    display, reasons = {}, ["invalid_external_metadata_variant", "editorial_review_required"]
                projected.append({"id": identity[0] if identity else None, "record": record, "display": display,
                                  "reasons": reasons, "evidence": evidence, "review_status": "quarantine",
                                  "vehicle_compatibility": [], "audio_language_verified": False,
                                  "transcript_status": "not_obtained", "license": "unknown"})
        filename = f"external-{len(state['external_exports']):04d}.json"
        atomic(Path(folder) / filename, {"version": 1, "rows": projected})
        state["external_exports"].append({"file": filename, "sha256": file_hash(Path(folder) / filename),
                                          "manifest_sha256": snapshot_hash, "rows": len(projected), "attached_at": now()})
        state["rows"] += len(projected)
        atomic(Path(folder) / "state.json", state)
        return {**summary(state), "idempotent_replay": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    new = sub.add_parser("init")
    new.add_argument("folder", type=Path)
    new.add_argument("--plan", required=True, type=Path)
    new.add_argument("--app", required=True, type=Path)
    status = sub.add_parser("status")
    status.add_argument("folder", type=Path)
    request = sub.add_parser("reserve")
    request.add_argument("folder", type=Path)
    request.add_argument("--job", required=True)
    receive = sub.add_parser("ingest")
    receive.add_argument("folder", type=Path)
    receive.add_argument("--attempt", required=True, type=int)
    receive.add_argument("--response", required=True, type=Path)
    stop_cmd = sub.add_parser("stop")
    stop_cmd.add_argument("folder", type=Path)
    stop_cmd.add_argument("--attempt", required=True, type=int)
    stop_cmd.add_argument("--reason", required=True)
    export = sub.add_parser("review")
    export.add_argument("folder", type=Path)
    export.add_argument("--output", required=True, type=Path)
    attach = sub.add_parser("attach-export")
    attach.add_argument("folder", type=Path)
    attach.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.action == "init":
            result = init(args.folder, read(args.plan), args.app)
        elif args.action == "status":
            result = summary(load_state(args.folder))
        elif args.action == "reserve":
            result = reserve(args.folder, args.job)
        elif args.action == "ingest":
            result = ingest(args.folder, args.attempt, args.response)
        elif args.action == "stop":
            result = stop(args.folder, args.attempt, args.reason)
        elif args.action == "attach-export":
            result = attach_export(args.folder, args.manifest)
        else:
            result = export_review(args.folder, args.output)
        print(json.dumps(result, ensure_ascii=True))
    except (CampaignError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, "CAMPAIGN: " + str(exc).encode("ascii", "backslashreplace").decode() + "\n")


if __name__ == "__main__":
    main()
