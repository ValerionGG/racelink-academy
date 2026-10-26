#!/usr/bin/env python3
"""Offline Bright Data JSON -> bounded PUBLIC_EXPORT for editorial quarantine.

No network, credentials, media download, database access or automatic publication.
Raw exports remain local; only allowlisted post metadata is written to the output.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import ipaddress
import json
import math
from pathlib import Path
import re
from urllib.parse import parse_qsl, unquote, urlsplit

DATASETS = {"gd_lu702nij2f790tmv9h": "tiktok", "gd_m7n5v2gq296pex2f5m": "tiktok", "gd_lyclm20il4r5helnj": "instagram"}
MAX_BYTES = 32 * 1024 * 1024
MAX_ROWS = 5000


class ExportError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def text(value, limit=20000):
    if value is None:
        return ""
    if not isinstance(value, str) or len(value) > limit:
        raise ExportError("invalid_text")
    inspected = html.unescape(unquote(value))
    for candidate in re.findall(r"https?://[^\s<>\"']+", inspected, re.I):
        try:
            parsed = urlsplit(candidate)
            keys = {re.sub(r"[-_]", "", name.lower()) for name, _ in parse_qsl(parsed.query)}
            if parsed.username or parsed.password or keys & {"accesstoken", "apikey", "token", "secret", "key", "auth", "authorization", "password", "credential", "session", "sessionid", "oauth"}:
                raise ExportError("sensitive_source_text")
        except ValueError:
            raise ExportError("sensitive_source_text") from None
    return value


def flag(value):
    if value is None or value == "":
        return False
    if isinstance(value, bool):
        return value
    if type(value) in (int, float) and value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.lower() in {"true", "1", "false", "0"}:
        return value.lower() in {"true", "1"}
    raise ExportError("invalid_flag")


def redact_contacts(value):
    value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[contact retiré]", value)
    return re.sub(r"(?<!\w)(?:\+33|0)[1-9](?:[ .-]?\d{2}){4}(?!\d)", "[contact retiré]", value)


def permalink(value, platform):
    value = text(value, 2000)
    try:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or parsed.hostname not in {platform + ".com", "www." + platform + ".com"} or parsed.username or parsed.password or parsed.port:
            raise ExportError("invalid_permalink")
    except ValueError:
        raise ExportError("invalid_permalink") from None
    if platform == "tiktok":
        match = re.fullmatch(r"/@([A-Za-z0-9._]{1,30})/video/(\d{10,30})/?", parsed.path)
        if match:
            return "tiktok:" + match[2], f"https://www.tiktok.com/@{match[1]}/video/{match[2]}", match[1]
    else:
        match = re.fullmatch(r"/(?:(?P<author>[A-Za-z0-9._]{1,30})/)?(?:reel|reels)/(?P<code>[A-Za-z0-9_-]{5,64})/?", parsed.path)
        if match:
            return "instagram:" + match["code"], f"https://www.instagram.com/reel/{match['code']}/", match["author"] or ""
    raise ExportError("invalid_permalink")


def date(value, platform):
    if value in (None, ""):
        return ""
    if platform == "tiktok" and type(value) in (int, float) and math.isfinite(value):
        try:
            return datetime.fromtimestamp(value, timezone.utc).isoformat()
        except (ValueError, OverflowError, OSError):
            raise ExportError("invalid_date") from None
    if isinstance(value, str):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return ""  # A vague/relative date does not become a publication date.
        if result.tzinfo is not None:
            return result.isoformat()
    return ""


def convert(row, platform):
    if not isinstance(row, dict):
        raise ExportError("invalid_row")
    if row.get("error") or row.get("error_code"):
        raise ExportError("provider_error")
    if any(flag(row.get(key)) for key in ("is_private", "isPrivate", "private")):
        raise ExportError("private_source")
    if str(row.get("availability", "")).lower() in {"private", "premium_only", "subscriber_only", "needs_auth"}:
        raise ExportError("restricted_source")
    for field in ("is_video", "isVideo"):
        if row.get(field) not in (None, "") and not flag(row[field]):
            raise ExportError("explicit_nonvideo_source")
    if any(flag(row.get(field)) for field in ("is_photo", "isPhoto", "is_story", "isStory")):
        raise ExportError("photo_or_story_source")
    identifier, url, handle = permalink(row.get("url"), platform)
    if platform == "tiktok":
        if row.get("post_id") not in (None, "") and str(row["post_id"]) != identifier.split(":", 1)[1]:
            raise ExportError("contradictory_id")
        if str(row.get("post_type", "")).lower() != "video" or row.get("carousel_images"):
            raise ExportError("video_not_established")
        # Empirical Fast API: profile_username is a display name (e.g. GBRNR),
        # while account_id and profile_url carry the actual @handle.
        creator = handle
        account_id = text(row.get("account_id"), 100)
        if account_id and account_id.lower() != handle.lower():
            raise ExportError("contradictory_creator")
        profile_url = text(row.get("profile_url"), 2000)
        if profile_url:
            try:
                profile = urlsplit(profile_url)
                profile_match = re.fullmatch(r"/@([A-Za-z0-9._]{1,30})/?", profile.path)
                if profile.scheme != "https" or profile.hostname not in {"tiktok.com", "www.tiktok.com"} or profile.username or profile.password or profile.port or not profile_match or profile_match[1].lower() != handle.lower():
                    raise ExportError("contradictory_creator")
            except ValueError:
                raise ExportError("contradictory_creator") from None
        display_name = redact_contacts(text(row.get("profile_username"), 100))
        published_at = date(row.get("create_time"), platform)
        sponsored = bool(row.get("commerce_info")) or flag(row.get("is_ad"))
    else:
        if row.get("shortcode") not in (None, "") and row["shortcode"] != identifier.split(":", 1)[1]:
            raise ExportError("contradictory_id")
        if str(row.get("product_type", "")).lower() not in {"clips", "reels", "reel"}:
            raise ExportError("video_not_established")
        creator = text(row.get("user_posted"), 100)
        if creator and not re.fullmatch(r"[A-Za-z0-9._]{1,30}", creator):
            raise ExportError("invalid_creator")
        if handle and creator and handle.lower() != creator.lower():
            raise ExportError("contradictory_creator")
        creator = creator or handle
        published_at = date(row.get("date_posted"), platform)
        sponsored = flag(row.get("is_paid_partnership")) or flag(row.get("is_ad"))
    caption = text(row.get("description"))
    if not caption.strip():
        raise ExportError("missing_source_caption")
    hashtags = row.get("hashtags") or []
    if not isinstance(hashtags, list) or len(hashtags) > 100 or any(not isinstance(t, str) or len(t) > 100 for t in hashtags):
        raise ExportError("invalid_hashtags")
    normalized_tags = []
    normalization_count = 0
    for tag in hashtags:
        text(tag, 100)
        if tag and not re.fullmatch(r"#?\w{1,100}", tag, re.UNICODE):
            # Fast API occasionally includes a trailing emoji or space-delimited
            # prose in a native hashtag. Only recover the exact hashtag token
            # when that complete source value also occurs after # in the caption.
            # Never invent a compound tag, copy URLs, or discard the caption.
            token = re.match(r"#?(\w{1,100})(?=\W|$)", tag, re.UNICODE)
            if not token or not re.search(r"(?<!\w)#" + re.escape(tag.lstrip("#")), caption) or "://" in tag:
                raise ExportError("invalid_hashtags")
            normalized_tags.append(token[1])
            normalization_count += 1
        elif tag:
            normalized_tags.append(tag.lstrip("#"))
    safe_caption = redact_contacts(caption)
    result = {"url": url, "caption": safe_caption, "creator": creator,
              "hashtags": list(dict.fromkeys(normalized_tags)),
              "media_type": "VIDEO", "is_video": True, "isSponsored": sponsored,
              "source_contact_redacted": safe_caption != caption}
    if normalization_count:
        result["source_hashtag_normalization_count"] = normalization_count
    if platform == "tiktok" and display_name:
        result["creator_display_name"] = display_name
    thumbnail = safe_thumbnail(row.get("preview_image") if platform == "tiktok" else row.get("thumbnail"))
    if thumbnail:
        result["thumbnail_url"] = thumbnail
    if published_at:
        result["published_at"] = published_at
    duration = row.get("video_duration") if platform == "tiktok" else None
    if type(duration) in (int, float) and math.isfinite(duration) and 0 < duration < 24 * 3600:
        result["duration_seconds"] = duration
    # No source title exists in these contracts: keep caption, title and tags distinct.
    # No comments, author bio, tokens, signed media/subtitle links or contacts are copied.
    return identifier, result


def safe_thumbnail(value):
    """Keep ordinary public HTTPS preview URLs; signed/session URLs stay out."""
    if not isinstance(value, str) or len(value) > 2000:
        return ""
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or not host or "." not in host or host.lower().endswith((".local", ".localhost")) or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
            return ""
        try:
            if not ipaddress.ip_address(host).is_global:
                return ""
        except ValueError:
            pass
        if re.search(r"[\s\x00-\x1f]", value):
            return ""
        return value
    except ValueError:
        return ""


def export(source, target, dataset_id, snapshot_id, captured_at):
    if dataset_id not in DATASETS or not re.fullmatch(r"sd_[A-Za-z0-9_-]{5,100}", snapshot_id):
        raise ExportError("invalid_dataset_or_snapshot")
    try:
        capture = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
        if capture.tzinfo is None:
            raise ValueError()
    except ValueError:
        raise ExportError("captured_at_requires_timezone") from None
    source, target = Path(source).resolve(), Path(target).resolve()
    if not source.is_file() or source.is_symlink():
        raise ExportError("expected_regular_source_file")
    with source.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ExportError("source_exceeds_32_mib")
    try:
        rows = json.loads(data.decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        raise ExportError("invalid_json") from None
    if not isinstance(rows, list) or len(rows) > MAX_ROWS:
        raise ExportError("expected_array_at_most_5000_rows")
    converted, provenance, rejected, duplicates, seen = [], [], Counter(), 0, set()
    ids = Counter()
    for number, row in enumerate(rows, 1):
        try:
            identifier, result = convert(row, DATASETS[dataset_id])
        except ExportError as exc:
            rejected[str(exc)] += 1
            continue
        key = (identifier, digest(encoded(result)))
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        ids[identifier] += 1
        converted.append(result)
        provenance.append({"id": identifier, "source_row_number": number,
                           "source_row_sha256": digest(encoded(row)), "mapped_row_sha256": key[1]})
    if not converted:
        raise ExportError("no_captioned_video_rows_to_export")
    page = encoded(converted)
    if len(page) > MAX_BYTES:
        raise ExportError("mapped_page_exceeds_32_mib")
    manifest = {"version": 1, "kind": "PUBLIC_EXPORT", "source": {
        "name": "Bright Data " + DATASETS[dataset_id] + " captioned metadata",
        "kind": "provider_export", "source_url": "https://brightdata.com/products/web-scraper",
        "evidence_reference": f"dataset={dataset_id}; snapshot={snapshot_id}; raw_sha256={digest(data)}",
        "captured_at": capture.isoformat()}, "pages": [{"file": "posts.json", "sha256": digest(page),
                                                          "format": "json", "schema": "generic"}]}
    report = {"adapter_version": "28.0.0", "dataset_id": dataset_id, "snapshot_id": snapshot_id,
              "raw_sha256": digest(data), "raw_rows": len(rows), "exported_rows": len(converted),
              "unique_post_ids": len(ids), "exact_metadata_duplicates": duplicates,
              "conflicting_id_variants_retained": sum(n - 1 for n in ids.values()),
              "rejected": dict(rejected), "row_provenance": provenance,
              "publication_count": 0, "database_modified": False, "network_requests": 0,
              "status": "editorial_quarantine", "audio_verified": False,
              "transcriptions_created": 0, "rights_verified": False}
    # Exclusive new directory prevents accidental reuse/overwrite of prior evidence.
    target.mkdir(parents=True, exist_ok=False)
    (target / "posts.json").write_bytes(page)
    (target / "manifest.json").write_bytes(encoded(manifest))
    (target / "conversion-report.json").write_bytes(encoded(report))
    return {key: value for key, value in report.items() if key != "row_provenance"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dataset-id", choices=DATASETS, required=True)
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--captured-at", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.source, args.output, args.dataset_id, args.snapshot_id, args.captured_at), ensure_ascii=False, indent=2))
    except (ExportError, OSError) as exc:
        parser.exit(1, f"Export refused: {exc}\n")


if __name__ == "__main__":
    main()
