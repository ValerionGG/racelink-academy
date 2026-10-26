#!/usr/bin/env python3
"""Convert bounded local CUA observations into reviewable PUBLIC_EXPORT snapshots.

Offline only: no browser, network, cookies, media downloads or database access.
Grid alt text never becomes a caption or a title. All source declarations remain
human/agent observations, not an independent authentication of their truth.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
import uuid

VERSION = "1.0.0"
MAX_BYTES = 2 * 1024 * 1024
MAX_CAPTURES = 200
MAX_ITEMS = 50
ACCESS = {"public", "login_required", "rate_limited", "server_error", "private", "unavailable"}
TOP_KEYS = {"version", "kind", "source_url", "captured_at", "surface", "access", "items"}
ITEM_KEYS = {"url", "media_kind", "creator", "visible_title", "grid_alt", "grid_text",
             "caption", "caption_status", "published_at", "evidence_note"}


class CaptureError(ValueError):
    pass


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def engine_hash():
    return digest_bytes(Path(__file__).read_bytes())


def bounded_text(value, cap=20000):
    if not isinstance(value, str) or len(value) > cap or any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise CaptureError("Expected bounded visible text without control characters")
    # Deliberately refuse token-like URL values; do not save authentication or CDN links.
    if re.search(r"https?://\S*[?&](?:token|access_token|signature|sig|auth|key|oh|oe)=", value, re.I):
        raise CaptureError("Signed/credential-like URL found in visible text; project only publication metadata")
    return value


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", value):
        raise CaptureError("Timestamp requires ISO date, time, seconds and timezone")
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CaptureError("Invalid timestamp") from exc
    if date < datetime(2010, 1, 1, tzinfo=timezone.utc) or date > datetime.now(timezone.utc) + timedelta(minutes=10):
        raise CaptureError("Timestamp is outside plausible observation bounds")
    return date.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def date_key(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def source_url(value, *, media=False):
    bounded_text(value, 500)
    if any(c.isspace() for c in value) or "\\" in value or "%" in value:
        raise CaptureError("Use an unencoded public profile or publication URL")
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError as exc:
        raise CaptureError("Malformed URL") from exc
    if url.scheme != "https" or url.username or url.password or port or url.query or url.fragment:
        raise CaptureError("Use HTTPS without credentials, query, fragment or port")
    if url.hostname in {"instagram.com", "www.instagram.com"}:
        platform = "instagram"
        match = re.fullmatch(r"/(?:(?P<creator>[A-Za-z0-9._]{1,30})/)?(?P<type>reel|reels|p)/(?P<id>[A-Za-z0-9_-]{5,64})/?", url.path)
        if match:
            kind = "reel" if match["type"] in {"reel", "reels"} else "p"
            return platform, f"https://www.instagram.com/{kind}/{match['id']}/", f"instagram:{match['id']}"
        if not media and re.fullmatch(r"/[A-Za-z0-9._]{1,30}/?", url.path) and url.path.strip("/") not in {"accounts", "direct", "explore", "stories", "reels", "reel", "p"}:
            return platform, "https://www.instagram.com/" + url.path.strip("/") + "/", None
    elif url.hostname in {"tiktok.com", "www.tiktok.com"}:
        platform = "tiktok"
        match = re.fullmatch(r"/@(?P<creator>[A-Za-z0-9._]{1,30})/video/(?P<id>\d{10,30})/?", url.path)
        if match:
            return platform, f"https://www.tiktok.com/@{match['creator']}/video/{match['id']}", f"tiktok:{match['id']}"
        if not media and re.fullmatch(r"/@[A-Za-z0-9._]{1,30}/?", url.path):
            return platform, "https://www.tiktok.com" + url.path.rstrip("/"), None
    raise CaptureError("Only explicit Instagram/TikTok profile or publication URLs are accepted")


def legacy_grid(value):
    """Project the observed V25 grid shape; image src is discarded, never fetched."""
    if set(value) != {"source", "kind", "captured_at", "items"} or value["kind"] != "visible_dom_grid":
        raise CaptureError("Invalid legacy CUA grid shape")
    if not isinstance(value["items"], list) or len(value["items"]) > MAX_ITEMS:
        raise CaptureError("A grid capture accepts at most 50 items")
    items = []
    for row in value["items"]:
        if not isinstance(row, dict) or set(row) != {"url", "text", "images"}:
            raise CaptureError("Legacy grid row has unknown fields")
        if not isinstance(row["images"], list) or len(row["images"]) > 5:
            raise CaptureError("Grid image references must be a bounded list")
        alts = []
        for image in row["images"]:
            if not isinstance(image, dict) or set(image) != {"alt", "src"}:
                raise CaptureError("Only alt/src legacy image fields are recognized")
            alts.append(bounded_text(image["alt"], 2000))
        items.append({"url": row["url"], "media_kind": "unknown", "grid_text": row["text"],
                      "grid_alt": "\n".join(alts), "caption_status": "unavailable"})
    return {"version": 1, "kind": "CUA_SOCIAL_CAPTURE", "source_url": value["source"],
            "captured_at": value["captured_at"], "surface": "profile_grid", "access": "public", "items": items}


def validate_capture(value):
    if isinstance(value, dict) and value.get("kind") == "visible_dom_grid":
        value = legacy_grid(value)
    if not isinstance(value, dict) or set(value) != TOP_KEYS or type(value["version"]) is not int or value["version"] != 1 or value["kind"] != "CUA_SOCIAL_CAPTURE":
        raise CaptureError("Expected strict CUA_SOCIAL_CAPTURE version 1")
    platform, url, page_id = source_url(value["source_url"])
    captured_at = timestamp(value["captured_at"])
    surface, access = value["surface"], value["access"]
    if surface not in {"profile_grid", "post_detail"} or access not in ACCESS:
        raise CaptureError("Unknown surface/access classification")
    if (surface == "post_detail") != bool(page_id):
        raise CaptureError("Surface must match profile URL or individual publication URL")
    if not isinstance(value["items"], list) or len(value["items"]) > (1 if surface == "post_detail" else MAX_ITEMS):
        raise CaptureError("At most 50 grid items or one detail item per capture")
    if access != "public" and value["items"]:
        raise CaptureError("Blocked/private captures record an empty item list, never hidden content")
    items = []
    for row in value["items"]:
        if not isinstance(row, dict) or set(row) - ITEM_KEYS or not {"url", "media_kind", "caption_status"} <= set(row):
            raise CaptureError("Unknown/missing item fields; raw page state and comments are forbidden")
        item_platform, permalink, identifier = source_url(row["url"], media=True)
        if item_platform != platform or (page_id and identifier != page_id):
            raise CaptureError("Item platform/identity differs from the observed page")
        if row["media_kind"] not in {"video", "image", "carousel", "unknown"} or row["caption_status"] not in {"complete", "partial", "unavailable"}:
            raise CaptureError("Invalid media kind or caption status")
        clean = {key: bounded_text(val, 20000 if key == "caption" else 2000) for key, val in row.items() if key not in {"url", "media_kind", "caption_status"}}
        if clean.get("published_at"):
            clean["published_at"] = timestamp(clean["published_at"])
            if date_key(clean["published_at"]) > date_key(captured_at):
                raise CaptureError("Publication date is later than capture")
        if surface == "profile_grid" and (clean.get("caption") or clean.get("visible_title") or row["caption_status"] != "unavailable"):
            raise CaptureError("Grid text/alt cannot be a native caption or title")
        if surface == "post_detail" and (clean.get("grid_alt") or clean.get("grid_text")):
            raise CaptureError("Keep grid observations separate from detail observations")
        if row["caption_status"] in {"complete", "partial"} and not clean.get("caption", "").strip():
            raise CaptureError("Caption status requires actually observed text")
        if row["caption_status"] == "unavailable" and clean.get("caption"):
            raise CaptureError("Unavailable captions must be empty")
        items.append({**clean, "url": permalink, "observed_url": row["url"], "id": identifier, "media_kind": row["media_kind"], "caption_status": row["caption_status"]})
    return {**value, "source_url": url, "observed_source_url": value["source_url"], "captured_at": captured_at, "platform": platform, "items": items}


def load_capture(path):
    path = Path(path).resolve()
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise CaptureError("Each capture must be an existing JSON file at most 2 MiB")
    raw = path.read_bytes()
    return {"path": str(path), "sha256": digest_bytes(raw), "capture": validate_capture(json.loads(raw.decode("utf-8-sig")))}


def aggregate(sources):
    grouped, stops, private_ids = {}, [], set()
    for source in sources:
        capture = source["capture"]
        if capture["access"] != "public":
            stops.append({"platform": capture["platform"], "url": capture["source_url"], "at": capture["captured_at"], "reason": capture["access"]})
            if capture["access"] == "private":
                private_id = source_url(capture["source_url"])[2]
                if private_id:
                    private_ids.add(private_id)
        for item in capture["items"]:
            proof = {"capture_sha256": source["sha256"], "source_url": capture["source_url"], "observed_source_url": capture["observed_source_url"], "captured_at": capture["captured_at"],
                     "surface": capture["surface"], "access": capture["access"], "item": item}
            grouped.setdefault(item["id"], []).append(proof)
    exports, pending, excluded = {"instagram": [], "tiktok": []}, [], []
    for identifier, variants in grouped.items():
        latest = max(variants, key=lambda v: date_key(v["captured_at"]))
        details = [v for v in variants if v["surface"] == "post_detail" and v["item"]["media_kind"] == "video" and v["item"]["caption_status"] == "complete"]
        known_kinds = {v["item"]["media_kind"] for v in variants} - {"unknown"}
        if identifier in private_ids or known_kinds & {"image", "carousel"}:
            excluded.append({"id": identifier, "url": latest["item"]["url"], "reason": "private_observation" if identifier in private_ids else "non_video_or_conflicting_media_observation", "observations": len(variants)})
        elif len({(v["item"]["caption"], v["item"].get("visible_title", "")) for v in details}) > 1:
            pending.append({"id": identifier, "url": latest["item"]["url"], "status": "divergent_complete_captions_require_review",
                            "observations": variants, "caption_verified": False, "audio_language_verified": False})
        elif details:
            chosen = max(details, key=lambda v: date_key(v["captured_at"]))
            item = chosen["item"]
            record = {"url": item["url"], "caption": item["caption"], "title": item.get("visible_title", ""),
                      "creator": item.get("creator", ""), "media_type": "VIDEO", "is_video": True,
                      "browser_capture": {"method": "CUA_visible_public_detail", "native_caption_observed": True,
                          "audio_language_verified": False, "media_watched": False, "license_verified": False,
                          "source_declaration_independently_verified": False, "selected_evidence": chosen,
                          "all_evidence": variants}}
            if item.get("published_at"):
                record["published_at"] = item["published_at"]
            exports[identifier.split(":", 1)[0]].append(record)
        else:
            pending.append({"id": identifier, "url": latest["item"]["url"], "status": "needs_public_video_detail_and_complete_caption",
                            "observations": variants, "caption_verified": False, "audio_language_verified": False})
    return exports, pending, excluded, stops


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(encode(value))
    os.replace(temporary, path)


def convert(inputs, output, *, execute=False, resume=False):
    if not 1 <= len(inputs) <= MAX_CAPTURES:
        raise CaptureError("Supply 1–200 explicit local capture paths")
    output = Path(output).resolve()
    checkpoint_path = output / "checkpoint.json"
    initial_checkpoint_hash = digest_bytes(checkpoint_path.read_bytes()) if checkpoint_path.is_file() else None
    previous, entries = [], {}
    if output.exists() and any(output.iterdir()):
        if not resume or not (output / "checkpoint.json").is_file():
            raise CaptureError("Use a new output directory or --resume with a valid checkpoint")
        state = json.loads((output / "checkpoint.json").read_text(encoding="utf-8"))
        if state.get("tool") != "browser_social_capture" or state.get("version") != VERSION or state.get("engine_sha256") != engine_hash():
            raise CaptureError("Incompatible checkpoint")
        for entry in state["sources"]:
            path = Path(entry["path"])
            if digest_bytes(path.read_bytes()) != entry["sha256"]:
                raise CaptureError("Previously captured source bytes changed")
            previous.append(load_capture(path))
        for file, expected in state["artifacts"].items():
            target = (output / file).resolve()
            if not target.is_relative_to(output) or digest_bytes(target.read_bytes()) != expected:
                raise CaptureError("Output evidence changed since checkpoint")
    loaded = previous + [load_capture(path) for path in inputs]
    for entry in loaded:
        if Path(entry["path"]).is_relative_to(output):
            raise CaptureError("Input captures must be outside output")
        old = entries.get(entry["path"])
        if old and old["sha256"] != entry["sha256"]:
            raise CaptureError("Source changed within the capture batch")
        entries[entry["path"]] = entry
    if len(entries) > MAX_CAPTURES:
        raise CaptureError("Campaign limit 200 captures; seal it and start a separate review batch")
    # Same capture bytes supplied under another name count only once.
    sources = list({entry["sha256"]: entry for entry in entries.values()}.values())
    exports, pending, excluded, stops = aggregate(sources)
    report = {"tool": "browser_social_capture", "version": VERSION, "mode": "execute" if execute else "preview",
              "captures": len(sources), "observations": sum(len(s["capture"]["items"]) for s in sources),
              "unique_identities": sum(map(len, exports.values())) + len(pending) + len(excluded),
              "detail_records_for_review": {key: len(rows) for key, rows in exports.items()},
              "needs_detail": len(pending), "excluded": len(excluded), "observed_stops": stops,
              "network_requests": 0, "database_modified": False, "publication_authorized": False,
              "warning": "Caption observation is not a transcript, technical validation, reuse licence or verified audio language."}
    if not execute:
        return report
    output.mkdir(parents=True, exist_ok=True)
    lock = output / ".capture.lock"
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise CaptureError("Output is locked; do not run concurrent conversions") from exc
    os.close(handle)
    try:
        current_hash = digest_bytes(checkpoint_path.read_bytes()) if checkpoint_path.is_file() else None
        if current_hash != initial_checkpoint_hash:
            raise CaptureError("Checkpoint changed during validation; rerun against the new completed snapshot")
        # Do not overwrite an earlier snapshot. A crash may leave an unreferenced
        # snapshot, but only the atomic checkpoint declares a completed conversion.
        snapshot = output / "snapshots" / uuid.uuid4().hex
        snapshot.mkdir(parents=True)
        evidence = [{"source_sha256": s["sha256"], "capture": s["capture"]} for s in sources]
        atomic(snapshot / "observations.json", evidence)
        atomic(snapshot / "needs-detail.json", pending)
        atomic(snapshot / "excluded.json", excluded)
        manifests = []
        for platform, records in exports.items():
            if not records:
                continue
            folder = snapshot / platform
            atomic(folder / "publications.json", records)
            page_hash = digest_bytes((folder / "publications.json").read_bytes())
            when = max((row["browser_capture"]["selected_evidence"]["captured_at"] for row in records), key=date_key)
            manifest = {"version": 1, "kind": "PUBLIC_EXPORT", "source": {
                "name": "CUA public visible publication detail", "kind": "provider_export",
                "source_url": f"https://www.{platform}.com/", "captured_at": when,
                "evidence_reference": "Visible CUA observations; browser_capture in publications.json; no independent source authentication"},
                "pages": [{"file": "publications.json", "format": "json", "schema": "generic", "sha256": page_hash}]}
            atomic(folder / "manifest.json", manifest)
            manifests.append((folder / "manifest.json").relative_to(output).as_posix())
        report.update(snapshot=snapshot.relative_to(output).as_posix(), public_export_manifests=manifests)
        atomic(snapshot / "report.json", report)
        artifacts = {p.relative_to(output).as_posix(): digest_bytes(p.read_bytes()) for p in snapshot.rglob("*") if p.is_file()}
        if previous:
            artifacts = {**state["artifacts"], **artifacts}
        atomic(output / "checkpoint.json", {"tool": "browser_social_capture", "version": VERSION,
            "engine_sha256": engine_hash(),
            "sources": [{"path": e["path"], "sha256": e["sha256"]} for e in entries.values()], "artifacts": artifacts,
            "latest_snapshot": snapshot.relative_to(output).as_posix()})
        return report
    finally:
        lock.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(convert(args.captures, args.output, execute=args.execute, resume=args.resume), ensure_ascii=True))
    except (CaptureError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, "BROWSER_CAPTURE: " + str(exc).encode("ascii", "backslashreplace").decode() + "\n")


if __name__ == "__main__":
    main()
