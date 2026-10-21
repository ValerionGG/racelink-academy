#!/usr/bin/env python3
"""Prepare bounded, hash-verified local social exports; never fetch or write a DB.

The source's declared origin is preserved, not independently authenticated.
Output is compatible with bulk_ingest.apply_prepared and its explicit approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import datetime as dt
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from scripts.bulk_ingest import adapt, atomic_json, digest, file_digest, identity, short
from server import ValidationError, normalize_item, utcnow

VERSION = "1.0.0"
MAX_PAGE_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_LINE_BYTES = 2 * 1024 * 1024
SCHEMAS = {"generic", "meta_graph", "tiktok_display"}
SOURCE_KINDS = {"creator_export", "authorized_api_export", "provider_export", "public_dataset", "indexed_export"}
PAGE_KEYS = {"file", "sha256", "format", "schema"}
SOURCE_KEYS = {"name", "kind", "source_url", "evidence_reference", "captured_at"}
SENSITIVE_NAME = re.compile(r"(?:token|cookie|password|credential|secret|oauth|session)", re.I)


def text(value, maximum=20000):
    if value is None:
        return ""
    if not isinstance(value, str) or len(value) > maximum:
        raise ValidationError("Expected bounded text metadata")
    return value


def true_flag(value):
    if value is None or value == "":
        return False
    if isinstance(value, (bool, int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in {"true", "1", "yes", "false", "0", "no"}:
        return value.strip().lower() in {"true", "1", "yes"}
    raise ValidationError("Restriction flags must be boolean or explicit 0/1, true/false, yes/no")


def load_manifest(path):
    path = Path(path).resolve()
    if path.stat().st_size > 1024 * 1024:
        raise ValidationError("Manifest exceeds 1 MiB")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict) or set(value) != {"version", "kind", "source", "pages"} or \
            value["version"] != 1 or isinstance(value["version"], bool) or value["kind"] != "PUBLIC_EXPORT":
        raise ValidationError("Expected strict PUBLIC_EXPORT manifest version 1")
    source = value["source"]
    if (not isinstance(source, dict) or set(source) != SOURCE_KEYS or not isinstance(source["kind"], str)
            or source["kind"] not in SOURCE_KINDS):
        raise ValidationError("Invalid source declaration")
    for key in SOURCE_KEYS:
        if not text(source[key], 1000).strip() or any(ord(c) < 32 for c in source[key]):
            raise ValidationError("Source declaration requires nonempty single-line text")
    url = urlsplit(source["source_url"])
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment or url.port:
        raise ValidationError("Source reference must be HTTPS without credentials, query, port or fragment")
    try:
        timestamp = dt.datetime.fromisoformat(source["captured_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError()
    except ValueError as exc:
        raise ValidationError("captured_at requires a timezone-aware ISO timestamp") from exc
    pages = value["pages"]
    if not isinstance(pages, list) or not 1 <= len(pages) <= 1000:
        raise ValidationError("Manifest requires 1–1000 bounded local pages")
    seen, total_bytes, resolved = set(), 0, []
    for page in pages:
        if not isinstance(page, dict) or set(page) != PAGE_KEYS:
            raise ValidationError("Unexpected page fields")
        filename = text(page["file"], 300)
        relative = Path(filename)
        if not filename or "\\" in filename or relative.is_absolute() or ":" in filename or \
                any(p in {".", ".."} or p.startswith(".") for p in filename.split("/")) or SENSITIVE_NAME.search(filename):
            raise ValidationError("Page must be a non-sensitive relative file within the manifest directory")
        target = (path.parent / relative).resolve()
        if not target.is_relative_to(path.parent) or not target.is_file() or target in seen:
            raise ValidationError("Page escapes manifest directory, is absent, or is duplicated")
        if not isinstance(page["format"], str) or not isinstance(page["schema"], str) or \
                page["format"] not in {"json", "jsonl", "csv"} or page["schema"] not in SCHEMAS or \
                target.suffix.lower() not in {"." + page["format"], ".ndjson" if page["format"] == "jsonl" else ""}:
            raise ValidationError("Unsupported page format or schema")
        if not isinstance(page["sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", page["sha256"]):
            raise ValidationError("Each page requires its SHA256")
        size = target.stat().st_size
        total_bytes += size
        if size > MAX_PAGE_BYTES or total_bytes > MAX_TOTAL_BYTES:
            raise ValidationError("Page exceeds 32 MiB or manifest exceeds 512 MiB")
        if file_digest(target) != page["sha256"]:
            raise ValidationError("Source page hash mismatch")
        seen.add(target)
        resolved.append(target)
    return value, resolved


def page_rows(path, page):
    if page["format"] == "csv":
        previous = csv.field_size_limit(MAX_LINE_BYTES)
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                    raise ValidationError("CSV headers must be present and unique")
                for row in reader:
                    if None in row:
                        raise ValidationError("CSV row has unexpected extra columns")
                    yield row
        finally:
            csv.field_size_limit(previous)
        return
    if page["format"] == "jsonl":
        with path.open("rb") as stream:
            for line in iter(lambda: stream.readline(MAX_LINE_BYTES + 1), b""):
                if len(line) > MAX_LINE_BYTES:
                    raise ValidationError("JSONL row exceeds 2 MiB")
                if line.strip():
                    yield json.loads(line.decode("utf-8-sig"))
        return
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(value, dict):
        if page["schema"] == "meta_graph":
            value = value.get("data")
        elif page["schema"] == "tiktok_display":
            value = value.get("data", {}).get("videos") if isinstance(value.get("data"), dict) else None
        else:
            value = next((value[key] for key in ("items", "videos", "entries") if isinstance(value.get(key), list)), None)
    if not isinstance(value, list):
        raise ValidationError("JSON page must contain the declared schema's list")
    yield from value


def map_row(row, schema, indexed=False):
    if not isinstance(row, dict):
        raise ValidationError("Source row must be an object")
    if schema == "meta_graph":
        fields = {"url": "permalink", "caption": "caption", "title": "title", "ownerUsername": "username",
                  "type": "media_type", "timestamp": "timestamp", "thumbnail": "thumbnail_url"}
    elif schema == "tiktok_display":
        fields = {"url": "share_url", "caption": "video_description", "title": "title", "uploader": "creator",
                  "timestamp": "create_time", "duration": "duration", "thumbnail": "cover_image_url"}
    else:
        fields = {"url": "url", "title": "title", "caption": "caption", "uploader": "creator",
                  "type": "media_type", "published_at": "published_at", "duration": "duration_seconds",
                  "thumbnail": "thumbnail_url"}
    mapped = {dest: row[src] for dest, src in fields.items() if row.get(src) not in (None, "")}
    for key in ("url", "title", "caption", "uploader", "ownerUsername", "type", "thumbnail", "published_at"):
        if key in mapped:
            mapped[key] = text(mapped[key])
    if indexed:
        mapped.pop("caption", None)  # Search-result bodies are never assumed to be a source caption.
    tags = row.get("hashtags", [])
    if isinstance(tags, str):
        try:
            tags = json.loads(tags) if tags.strip() else []
        except json.JSONDecodeError as exc:
            raise ValidationError("CSV hashtags must be a JSON array") from exc
    if not isinstance(tags, list) or len(tags) > 100 or any(not isinstance(t, str) or len(t) > 100 for t in tags):
        raise ValidationError("Hashtags require a bounded list of strings")
    mapped["hashtags"] = tags
    if any(true_flag(row.get(key)) for key in ("private", "is_private", "isPrivate")):
        mapped["isPrivate"] = True
    if str(row.get("availability", "")).lower() in {"private", "premium_only", "subscriber_only", "needs_auth"}:
        mapped["availability"] = str(row["availability"]).lower()
    for key in ("is_video", "isVideo"):
        if key in row and row[key] is not None and row[key] != "" and not true_flag(row[key]):
            raise ValidationError("Source explicitly declares non-video media; permalink cannot override it")
    if any(true_flag(row.get(key)) for key in ("sponsored", "is_ad", "isAd", "paidPartnership", "isSponsored")):
        mapped["isSponsored"] = True
    for src, dest in (("is_video", "isVideo"), ("isVideo", "isVideo"), ("is_story", "isStory"), ("is_photo", "isPhoto")):
        if true_flag(row.get(src)):
            mapped[dest] = True
    # No arbitrary description, language, query, comments, media bytes/URLs,
    # tokens or nested author profile are forwarded. Missing creator stays empty.
    return mapped, fields


def convert(row, page, source, row_number):
    indexed = source["kind"] == "indexed_export"
    mapped, field_map = map_row(row, page["schema"], indexed)
    identifier, _, platform = identity(mapped.get("url", ""))
    if platform not in {"tiktok", "instagram"}:
        raise ValidationError("PUBLIC_EXPORT currently supports Instagram and TikTok video identities only")
    expected = {"meta_graph": "instagram", "tiktok_display": "tiktok"}.get(page["schema"])
    if expected and platform != expected:
        raise ValidationError("Native export schema does not match the source platform")
    if page["schema"] == "tiktok_display" and row.get("id") and str(row["id"]) != identifier.split(":", 1)[1]:
        raise ValidationError("Native TikTok video ID differs from share_url identity")
    record, decision = adapt(mapped, "apify-" + platform, source_label=page["file"], index=row_number)
    scope = "indexed_export_title_only" if indexed else "exported_metadata_not_independently_verified"
    record["verification_scope"] = scope
    record["language_status"] = "inferred_from_exported_source_text" if record["language"] != "und" else "unknown_audio_language"
    record["audio_language_verified"] = False
    record["language_evidence"]["scope"] = scope
    record["provenance"].update(adapter="public_export", adapter_version=VERSION,
        schema_adapter=page["schema"], source_record_sha256=digest(row), mapped_record_sha256=digest(mapped),
        mapped_fields=field_map, source_page_sha256=page["sha256"])
    record["public_export_provenance"] = {"kind": "PUBLIC_EXPORT", "source": source,
        "source_declaration_verified": False, "page": page["file"], "page_sha256": page["sha256"],
        "row_number": row_number, "row_sha256": digest(row), "schema": page["schema"],
        "caption_used": bool(mapped.get("caption")), "indexed_body_excluded": indexed,
        "audio_verified": False, "media_downloaded": False, "reuse_permission_established": False}
    if indexed:
        record["description_basis"] = "indexed_title_only_no_verified_caption"
        record["category_status"] = "inferred_from_indexed_title_rules"
        record["content_format_status"] = "inferred_from_indexed_title_rules"
        record["publication_date_status"] = "indexed_metadata_unverified" if record.get("published_at") else "unknown"
        record["thumbnail_status"] = "indexed_metadata_unverified" if record.get("thumbnail_url") else "unknown"
        record["provenance"]["title_basis"] = "source_index_title"
        decision["basis"] = "indexed_title_rules_not_video_review"
    social = record.get("social_content", {})
    if social:
        social["source_metadata"]["record"]["provenance"] = dict(record["provenance"])
        social["source_metadata"]["record"]["verification_scope"] = scope
        social["normalization"]["verification_scope"] = scope
        if indexed:
            social["normalization"]["indexed_body_excluded"] = True
            social["field_provenance"]["title"]["basis"] = "source_index_title"
            social["field_provenance"]["description"]["basis"] = "indexed_body_excluded"
    reasons = list(decision["reasons"])
    if social.get("needs_title_review"):
        reasons.append("source_title_needs_editorial_review")
    if true_flag(row.get("is_aigc")) or true_flag(row.get("is_ai_generated")):
        reasons.append("source_declares_ai_generated_content_review_required")
    decision = {**decision, "status": "quarantine" if reasons else "candidate", "reasons": reasons}
    record["bulk_qualification"] = decision
    normalize_item(record)
    return {"id": identifier, "record": record, "reasons": reasons,
            "evidence": {"page": page["file"], "row_number": row_number, "row_sha256": digest(row)}}


def prepare_public_export(manifest, output, *, max_records=5000, resume=False):
    if isinstance(max_records, bool) or not isinstance(max_records, int) or not 1 <= max_records <= 100000:
        raise ValidationError("max-records must be 1–100000")
    declaration, paths = load_manifest(manifest)
    output = Path(output).resolve()
    source_root = Path(manifest).resolve().parent
    if output == source_root or source_root.is_relative_to(output):
        raise ValidationError("Output must be separate from the source root")
    run_hash = digest({"manifest": declaration, "max_records": max_records, "adapter_version": VERSION})
    checkpoint = {"run_sha256": run_hash, "pages": []}
    if output.exists() and any(output.iterdir()):
        if not resume or not (output / "checkpoint.json").is_file():
            raise ValidationError("Use an empty output directory or --resume")
        checkpoint = json.loads((output / "checkpoint.json").read_text(encoding="utf-8"))
        if checkpoint.get("run_sha256") != run_hash:
            raise ValidationError("Resume requires identical manifest, bounds and adapter version")
        for index, cached in enumerate(checkpoint.get("pages", [])):
            if cached.get("file") != f"normalized-page-{index:04d}.json" or \
                    file_digest(output / cached["file"]) != cached.get("sha256"):
                raise ValidationError("Normalized page cache hash mismatch")
    output.mkdir(parents=True, exist_ok=True)
    all_rows, truncated = [], False
    for page_index, (page, path) in enumerate(zip(declaration["pages"], paths)):
        if page_index < len(checkpoint["pages"]):
            cached = json.loads((output / checkpoint["pages"][page_index]["file"]).read_text(encoding="utf-8"))
        else:
            cached = []
            for row_number, row in enumerate(page_rows(path, page), 1):
                if len(all_rows) + len(cached) >= max_records:
                    truncated = True
                    break
                try:
                    entry = convert(row, page, declaration["source"], row_number)
                except (ValidationError, ValueError, TypeError) as exc:
                    identifier = None
                    if isinstance(row, dict):
                        url = row.get({"meta_graph": "permalink", "tiktok_display": "share_url", "generic": "url"}[page["schema"]])
                        try:
                            identifier = identity(url)[0]
                        except (ValidationError, ValueError, TypeError):
                            pass
                    entry = {"id": identifier, "record": None, "reasons": [short(str(exc), 250)],
                             "evidence": {"page": page["file"], "row_number": row_number, "row_sha256": digest(row)}}
                cached.append(entry)
            cache_file = f"normalized-page-{page_index:04d}.json"
            atomic_json(output / cache_file, cached)
            checkpoint["pages"].append({"file": cache_file, "sha256": file_digest(output / cache_file),
                                        "truncated_at_bound": truncated})
            checkpoint["truncated_at_bound"] = truncated
            atomic_json(output / "checkpoint.json", checkpoint)
        all_rows.extend(cached)
        if checkpoint["pages"][page_index].get("truncated_at_bound") or truncated:
            truncated = True
            break
    grouped, quarantine, accepted = {}, [], []
    for entry in all_rows:
        if entry["id"]:
            grouped.setdefault(entry["id"], []).append(entry)
        else:
            quarantine.append(entry)
    for identifier, variants in grouped.items():
        reasons = list(dict.fromkeys(r for variant in variants for r in variant["reasons"]))
        records = [variant["record"] for variant in variants if variant["record"]]
        record = max(records, key=lambda r: len(r["description"]), default=None)
        evidence = [variant["evidence"] for variant in variants]
        if record:
            record["public_export_variants"] = evidence
        if reasons or record is None:
            quarantine.append({"id": identifier, "reasons": reasons or ["missing_usable_record"],
                               "record": record, "source_variants": evidence})
        else:
            accepted.append(record)
    atomic_json(output / "accepted.json", accepted)
    with (output / "quarantine.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for entry in quarantine:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    accepted_hash = file_digest(output / "accepted.json")
    report = {"adapter": "public_export", "adapter_version": VERSION, "mode": "dry_run",
              "created_at": utcnow(), "network_requests": 0, "database_modified": False,
              "source_records": len(all_rows), "unique_media_identities": len(grouped),
              "duplicates_in_batch": sum(len(v) - 1 for v in grouped.values()),
              "accepted_candidates": len(accepted), "quarantined": len(quarantine),
              "truncated_at_bound": truncated, "declared_pages": len(paths), "processed_pages": len(checkpoint["pages"]),
              "accepted_sha256": accepted_hash, "quarantine_sha256": file_digest(output / "quarantine.jsonl"),
              "manifest_sha256": file_digest(manifest), "run_sha256": run_hash,
              "candidate_platforms": dict(Counter(r["platform"] for r in accepted)),
              "candidate_languages": dict(Counter(r["language"] for r in accepted)),
              "rights": "unknown", "audio_language_verified": False,
              "source_authorization": "declared_in_manifest_not_verified_by_adapter"}
    atomic_json(output / "report.json", report)
    atomic_json(output / "approval.template.json", {"accepted_sha256": accepted_hash,
        "approved_ids": [], "reviewer": "", "reason": "", "note": "Review source authority, teaching evidence and exact IDs before existing bulk apply."})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-records", type=int, default=5000)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare_public_export(args.manifest, args.output,
            max_records=args.max_records, resume=args.resume), ensure_ascii=False, indent=2))
    except (ValidationError, ValueError, OSError) as exc:
        parser.exit(2, f"PUBLIC_EXPORT: {exc}\n")


if __name__ == "__main__":
    main()
