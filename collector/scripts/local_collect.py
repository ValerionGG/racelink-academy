#!/usr/bin/env python3
"""Metadata-only local collection; no subscription, cookies, media or database writes.

Uses an installed yt-dlp executable and, optionally, the public Exa MCP via an
installed mcporter. A JSON plan is previewed unless --execute is explicit.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from urllib.parse import urlsplit, urlunsplit

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from scripts.bulk_ingest import (atomic_json, digest, file_digest, identity, project_source, short)
from server import ValidationError, utcnow

VERSION = "1.0.1"
EXA_KINDS = {"exa_search", "exa_search_advanced"}
KINDS = {"video", "youtube_search", "youtube_channel", *EXA_KINDS}
MAX_PROCESS_BYTES = 32 * 1024 * 1024
BASE_FLAGS = ["--ignore-config", "--no-plugin-dirs", "--no-remote-components",
    "--no-cookies", "--no-cookies-from-browser", "--no-cache-dir", "--simulate", "--skip-download",
    "--no-write-subs", "--no-write-auto-subs", "--no-write-thumbnail", "--no-write-info-json",
    "--no-progress", "--retries", "0", "--extractor-retries", "0", "--socket-timeout", "12",
    "--sleep-requests", "1", "--proxy", "", "--dump-single-json"]


def validate_plan(value):
    jobs = value.get("jobs") if isinstance(value, dict) else value
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 200:
        raise ValidationError("A plan requires 1–200 jobs")
    validated, seen, budget = [], set(), 0
    for index, job in enumerate(jobs):
        extra_keys = {"include_domains", "include_text", "user_location"}
        if not isinstance(job, dict) or set(job) - ({"kind", "value", "limit"} |
                (extra_keys if job.get("kind") == "exa_search_advanced" else set())):
            raise ValidationError(f"Job {index}: unsupported plan fields")
        kind, text = job.get("kind"), job.get("value")
        if kind not in KINDS or not isinstance(text, str) or not 1 <= len(text.strip()) <= 1000 or \
            any(ord(c) < 32 for c in text):
            raise ValidationError(f"Job {index}: invalid kind or value")
        text = text.strip()
        limit = job.get("limit", 1 if kind == "video" else 5)
        maximum = 50 if kind == "exa_search_advanced" else 10 if kind == "exa_search" else 500
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= maximum:
            raise ValidationError(f"Job {index}: limit must be 1–{maximum}")
        if kind == "video":
            _, text, platform = identity(text)
            if limit != 1:
                raise ValidationError("Direct video jobs must have limit=1")
        elif kind == "youtube_channel":
            parsed = urlsplit(text)
            if parsed.scheme != "https" or parsed.hostname not in {"www.youtube.com", "youtube.com"} or \
                parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.port or \
                not re.fullmatch(r"/(?:@[A-Za-z0-9_.-]{1,100}|channel/UC[A-Za-z0-9_-]{22})(?:/videos|/shorts)?/?", parsed.path):
                raise ValidationError("Use a public https YouTube channel/@handle URL; no custom parameters")
            text = urlunsplit(("https", "www.youtube.com", parsed.path.rstrip("/"), "", ""))
            platform = "youtube"
        else:
            platform = "youtube" if kind == "youtube_search" else "web_index"
        clean = {"kind": kind, "value": text, "limit": limit, "platform": platform}
        if kind == "exa_search_advanced":
            domains = job.get("include_domains", ["instagram.com", "tiktok.com"])
            terms = job.get("include_text", [])
            location = job.get("user_location", "")
            if not isinstance(domains, list) or not 1 <= len(domains) <= 3 or any(
                    not isinstance(d, str) or d not in {"instagram.com", "tiktok.com", "youtube.com"} for d in domains):
                raise ValidationError("Advanced domains must be Instagram, TikTok or YouTube")
            if not isinstance(terms, list) or len(terms) > 5 or any(not isinstance(t, str) or
                    not 1 <= len(t.strip()) <= 100 or any(ord(c) < 32 for c in t) for t in terms):
                raise ValidationError("Advanced include_text allows at most five short source phrases")
            if not isinstance(location, str) or (location and not re.fullmatch(r"[A-Z]{2}", location)):
                raise ValidationError("Advanced user_location must be a two-letter uppercase country code")
            clean.update(include_domains=sorted(set(domains)), include_text=list(dict.fromkeys(t.strip() for t in terms)),
                         user_location=location)
        key = digest(clean)
        if key not in seen:
            seen.add(key)
            validated.append(clean)
            budget += limit
    if budget > 10000:
        raise ValidationError("A plan is limited to 10000 requested metadata records; split into bounded plans")
    return validated


def yt_command(executable, job):
    command = [str(executable), *BASE_FLAGS]
    if job["kind"] in {"youtube_search", "youtube_channel"}:
        command += ["--flat-playlist", "--playlist-end", str(job["limit"])]
    else:
        command += ["--no-playlist", "--ignore-no-formats-error"]
    target = f"ytsearch{job['limit']}:{job['value']}" if job["kind"] == "youtube_search" else job["value"]
    if job["platform"] == "tiktok":
        # The installed upstream TikTok extractor requires the public www host;
        # the catalog's canonical identity deliberately omits that cosmetic prefix.
        parsed = urlsplit(target)
        target = urlunsplit(("https", "www.tiktok.com", parsed.path, "", ""))
    # End options explicitly. Input strings are never sent to a shell.
    return [*command, "--", target]


def stop_process(child):
    if os.name == "nt":
        # Python's Windows .exe launchers may leave a child Python process after
        # kill(). Bound the whole tree that this collector just created.
        taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/taskkill.exe"
        try:
            subprocess.run([str(taskkill), "/PID", str(child.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                shell=False, timeout=5, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except (OSError, subprocess.TimeoutExpired):
            pass
    if child.poll() is None:
        child.kill()
    child.wait(timeout=5)


def process(command, timeout=45):
    env = {k:v for k,v in os.environ.items() if not re.search(
        r"(?:TOKEN|COOKIE|PASSWORD|SECRET|API_KEY|AUTHORIZATION|PROXY)", k, re.I)}
    env["PYTHONIOENCODING"] = "utf-8"
    env["NO_COLOR"] = "1"
    with tempfile.TemporaryDirectory(prefix="focus-metadata-process-") as directory:
        if any(urlsplit(str(part)).scheme == "https" and urlsplit(str(part)).hostname == "mcp.exa.ai"
               and urlsplit(str(part)).path == "/mcp" for part in command if str(part).startswith("https://")):
            # --no-oauth alone can still reuse cached tokens. Isolate configuration,
            # imports and auth/cache stores, and use a fresh server identity so a
            # pre-existing user's paid Exa connection cannot be selected implicitly.
            config = Path(directory) / "mcporter.json"
            atomic_json(config, {"mcpServers": {}, "imports": []})
            env["MCPORTER_CONFIG"] = str(config)
            env["MCPORTER_OAUTH_NO_BROWSER"] = "1"
            for key in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
                env[key] = str(Path(directory) / key.lower())
            command = list(command)
            command[command.index("--name") + 1] = "focus-keyless-" + uuid.uuid4().hex
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            try:
                child = subprocess.Popen(command, stdout=out, stderr=err, stdin=subprocess.DEVNULL,
                    cwd=directory, env=env, shell=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            except OSError:
                return {"returncode": -1, "stdout": "", "stderr": "Required executable is unavailable", "status": "dependency_unavailable"}
            deadline = time.monotonic() + timeout
            status = None
            while child.poll() is None:
                if time.monotonic() > deadline:
                    status = "timeout"
                elif os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size > MAX_PROCESS_BYTES:
                    status = "output_limit"
                if status:
                    stop_process(child)
                    break
                time.sleep(.05)
            if os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size > MAX_PROCESS_BYTES:
                status = "output_limit"
            if status:
                return {"returncode": child.returncode, "stdout": "", "stderr": status, "status": status}
            out.seek(0)
            err.seek(0)
            return {"returncode": child.returncode,
                "stdout": out.read(MAX_PROCESS_BYTES).decode("utf-8", errors="replace"),
                "stderr": err.read(16384).decode("utf-8", errors="replace")}


def error_status(stderr):
    text = stderr.lower()
    auth_context = ("logged-in" in text or "logged in" in text) and any(
        token in text for token in ("empty media response","necessary","required","requires","only available","must be"))
    if auth_context or re.search(r"\b(?:http(?: error)?\s*)?(?:403|429)\b", text) or any(token in text for token in (
            "login", "log in", "sign in", "captcha", "forbidden", "too many requests",
            "not granting access", "authentication required", "authentication is required",
            "rate limit", "not available in your country")):
        return "access_blocked"
    if "unsupported url" in text:
        return "unsupported_url"
    return "extractor_failed"


def sanitized_error(text):
    # Preserve actionable platform errors, never signed URLs or credential-like values.
    text = re.sub(r"https?://\S+", "[source URL]", text)
    text = re.sub(r"(?i)(token|cookie|password|secret|authorization)\s*[:=]\s*\S+", r"\1=[redacted]", text)
    return short(text, 1200)


def provenance(job, provider, version=None):
    result = {"collector": "local_collect", "collector_version": VERSION, "provider": provider,
        "job_kind": job["kind"], "source": job["value"], "collected_at": utcnow(),
        "extractor_version": version,
        "evidence_scope": "indexed_search_metadata" if provider == "exa-public-mcp" else
            "public_video_metadata" if job["kind"] == "video" else "public_listing_metadata",
        "authenticated": False, "media_downloaded": False, "audio_language_verified": False}
    if job["kind"] == "exa_search_advanced":
        result["search_filters"] = {key: job.get(key) for key in ("include_domains", "include_text", "user_location")}
    return result


def flatten_yt(value):
    if isinstance(value, dict) and isinstance(value.get("entries"), list):
        for entry in value["entries"]:
            if isinstance(entry, dict):
                yield entry
    elif isinstance(value, dict):
        yield value


def normalize_yt(raw, job, version):
    record = project_source(raw)
    permalink = raw.get("webpage_url") or raw.get("original_url") or raw.get("url")
    if not permalink and job["kind"] == "video":
        permalink = job["value"]
    try:
        media_id, url, platform = identity(permalink)
    except (ValidationError, TypeError, ValueError):
        if job["platform"] == "youtube" and re.fullmatch(r"[A-Za-z0-9_-]{11}", str(raw.get("id", ""))):
            media_id, url, platform = identity("https://www.youtube.com/watch?v=" + raw["id"])
        else:
            raise ValidationError("Extractor did not return a public media permalink")
    if platform != job["platform"]:
        raise ValidationError("Extractor output changed source platform")
    if job["kind"] == "video" and identity(job["value"])[0] != media_id:
        raise ValidationError("Extractor output changed media identity")
    record["webpage_url"] = url
    record["url"] = url  # Drop yt-dlp's CDN media URL.
    record["_collection"] = provenance(job, "yt-dlp", version)
    if platform == "instagram":
        record["isVideo"] = True
        if re.fullmatch(r"Video by .+", str(record.get("title", ""))) and record.get("description"):
            record["_collection"]["extractor_title"] = record["title"]
            record["_collection"]["title_basis"] = "first_line_of_source_caption"
            record["title"] = short(record["description"].splitlines()[0], 480)
    if not record.get("title") and not record.get("description"):
        raise ValidationError("Extractor returned no source title or description")
    return record


def collect_yt(job, executable, version, *, runner=process, timeout=45):
    result = runner(yt_command(executable, job), timeout)
    if result.get("status"):
        return {"status": result["status"], "records": [], "error": sanitized_error(result["stderr"])}
    try:
        value = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {"status": error_status(result["stderr"]), "records": [], "error": sanitized_error(result["stderr"] or "No JSON metadata returned")}
    records, failures = [], []
    for raw in list(flatten_yt(value))[:job["limit"]]:
        try:
            records.append(normalize_yt(raw, job, version))
        except (ValidationError, ValueError) as exc:
            failures.append(str(exc))
    status = "ok" if records and not failures and result["returncode"] == 0 else "partial" if records else error_status(result["stderr"])
    return {"status": status, "records": records, "rejected_metadata": failures,
            "error": sanitized_error(result["stderr"]) if result["returncode"] else None}


def exa_prefix(explicit=None):
    if explicit:
        path = Path(explicit)
        if not path.is_file() or path.suffix != ".js":
            raise ValidationError("mcporter-js must identify an already installed JavaScript CLI")
        return [shutil.which("node") or "node", str(path.resolve())]
    command = shutil.which("mcporter")
    if not command:
        raise ValidationError("mcporter is not installed; Exa discovery is optional")
    path = Path(command)
    if path.suffix.lower() in {".cmd", ".ps1", ".bat"}:
        script = path.parent / "node_modules/mcporter/dist/cli.js"
        if not script.is_file():
            raise ValidationError("Specify existing --mcporter-js; shell wrappers are not executed")
        return [shutil.which("node") or "node", str(script)]
    return [command]


def exa_command(prefix, job):
    args = {"query": job["value"], "numResults": job["limit"], "objective":
        "Find direct public educational video permalinks on YouTube, Instagram or TikTok. "
        "Return source titles and short indexed excerpts. Exclude profiles, ads and private pages. "
        "Do not infer audio language or provide transcripts."}
    tool, endpoint = "web_search_exa", "https://mcp.exa.ai/mcp"
    if job["kind"] == "exa_search_advanced":
        tool = "web_search_advanced_exa"
        endpoint += "?tools=" + tool
        args = {"query": job["value"], "numResults": job["limit"], "type": "auto",
                "includeDomains": job["include_domains"], "textMaxCharacters": 1200, "enableSummary": False}
        if job.get("include_text"):
            args["includeText"] = job["include_text"]
        if job.get("user_location"):
            args["userLocation"] = job["user_location"]
    # Explicit public endpoint: no API key, saved connector, actor or OAuth flow.
    return [*prefix, "call", "--http-url", endpoint, "--name", "focus-exa-public",
        "--tool", tool, "--args", json.dumps(args, ensure_ascii=False),
        "--output", "json", "--timeout", "25000", "--no-oauth"]


def exa_entries(payload):
    def mapped_entries(entries):
        for entry in entries:
            if isinstance(entry, dict):
                highlights = entry.get("highlights", entry.get("text", ""))
                yield {"url": entry.get("url"), "title": entry.get("title"),
                       "description": " ".join(x for x in highlights if isinstance(x, str)) if isinstance(highlights, list) else highlights,
                       "author": entry.get("author"), "thumbnail": entry.get("image") or entry.get("thumbnail"),
                       "published_at": entry.get("publishedDate")}
    if not isinstance(payload, dict):
        return
    for structured in (payload.get("structuredContent"), payload):
        if isinstance(structured, dict) and isinstance(structured.get("results"), list):
            yield from mapped_entries(structured["results"])
            return  # Structured results are authoritative; do not duplicate text.
    for part in payload.get("content", []) if isinstance(payload, dict) else []:
        if not isinstance(part, dict) or part.get("type") != "text":
            continue
        text = part.get("text", "")
        if not isinstance(text, str):
            continue
        # Current advanced MCP serializes its results object into content[].text
        # without structuredContent. Parse only that documented results list;
        # notices, prose, fenced examples and arbitrary nested JSON are not rows.
        if text.lstrip().startswith(("{", "[")):
            try:
                decoded = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(decoded, dict) and isinstance(decoded.get("results"), list):
                yield from mapped_entries(decoded["results"])
                return
            continue
        # Preserve the earlier plain-text response format for basic searches.
        for block in re.split(r"\n---\n", text):
            found = re.search(r"(?:^|\n)Title:\s*(.*?)\nURL:\s*(https?://\S+)", block, re.S)
            if not found:
                continue
            author = re.search(r"(?:^|\n)Author:\s*([^\n]+)", block)
            highlights = re.search(r"(?:^|\n)Highlights:\s*(.*)", block, re.S)
            yield {"url": found[2], "title": found[1].strip(),
                   "description": highlights[1] if highlights else "",
                   "author": author[1] if author else None}


def collect_exa(job, prefix, *, runner=process, timeout=45):
    result = runner(exa_command(prefix, job), timeout)
    if result.get("status") or result["returncode"]:
        status = result.get("status") or ("access_blocked" if error_status(result.get("stderr", "")) == "access_blocked" else "search_unavailable")
        return {"status": status, "records": [],
                "error": sanitized_error(result.get("stderr", "Search failed"))}
    try:
        payload = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {"status": "search_unavailable", "records": [], "error": "Search did not return parseable JSON"}
    if payload.get("isError"):
        message = " ".join(str(part.get("text", "")) for part in payload.get("content", []) if isinstance(part, dict))
        status = "access_blocked" if error_status(message) == "access_blocked" else "search_unavailable"
        return {"status": status, "records": [], "error": "Search service returned an access block" if status == "access_blocked" else "Search service returned an error"}
    records, rejected = [], 0
    for source in list(exa_entries(payload))[:job["limit"]]:
        try:
            media_id, url, platform = identity(source.get("url"))
        except (ValidationError, ValueError, TypeError):
            rejected += 1
            continue
        if not source.get("title"):
            rejected += 1
            continue
        creator = source.get("author")
        record = {"id": media_id.split(":", 1)[1], "url": url, "webpage_url": url,
            "title": short(source["title"], 480), "description": short(source.get("description"), 1200),
            "uploader": "" if creator in {None, "N/A", "Unknown"} else short(creator, 300),
            "language": "und", "language_status": "unknown_audio_language",
            "_collection": provenance(job, "exa-public-mcp")}
        # Index metadata stays attributed to the index. Adaptation validates these
        # values; a signed public thumbnail URL is stored without downloading it.
        for key in ("thumbnail", "published_at"):
            if isinstance(source.get(key), str):
                record[key] = source[key]
        # Only direct reels/tv or TikTok /video URLs evidence a video format from
        # the index. An Instagram /p post remains unqualified unless verified later.
        if platform == "instagram" and re.search(r"/(?:reel|reels|tv)/", url):
            record["isVideo"] = True
        records.append(record)
    return {"status": "ok" if records else "empty_or_unrecognized_results", "records": records,
            "rejected_non_video_links": rejected, "error": None}


def job_key(job):
    return digest({"collector_version": VERSION, "job": job})


def collect(jobs, output, *, execute=False, resume=False, max_jobs=10, interval=2,
            timeout=45, yt_dlp=None, mcporter_js=None, runner=process, sleeper=time.sleep):
    if not 1 <= max_jobs <= 200 or not 1 <= interval <= 30 or not 10 <= timeout <= 120:
        raise ValidationError("Bound max-jobs 1–200, interval 1–30 seconds and timeout 10–120 seconds")
    plan_hash = digest(jobs)
    preview = {"mode": "execute" if execute else "dry_run", "jobs": len(jobs),
        "requested_records_bound": sum(j["limit"] for j in jobs), "max_jobs_this_run": max_jobs,
        "plan_sha256": plan_hash, "database_modified": False, "cookies_used": False,
        "media_downloaded": False, "actor_started": False}
    if not execute:
        return preview
    output = Path(output)
    if output.exists() and any(output.iterdir()) and not resume:
        raise ValidationError("Use a new output directory, or --resume with the identical plan")
    output.mkdir(parents=True, exist_ok=True)
    lock = output / ".collector.lock"
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValidationError("Collection directory is locked; verify no process is running before removing stale lock") from None
    os.close(handle)
    try:
        state_path = output / "checkpoint.json"
        state = json.loads(state_path.read_text(encoding="utf-8")) if resume else {
            "version": VERSION, "plan_sha256": plan_hash, "jobs": {}, "created_at": utcnow()}
        if state.get("plan_sha256") != plan_hash:
            raise ValidationError("Resume requires the identical normalized plan")
        caches = output / "cache"
        caches.mkdir(exist_ok=True)
        for key, entry in state["jobs"].items():
            if key not in {job_key(job) for job in jobs} or file_digest(caches / f"{key}.json") != entry["sha256"]:
                raise ValidationError("Cache differs from checkpoint; do not reuse altered evidence")
        atomic_json(state_path, state)
        exe = yt_dlp or shutil.which("yt-dlp")
        if exe and Path(exe).suffix.lower() in {".cmd", ".bat", ".ps1"}:
            raise ValidationError("Use the installed yt-dlp executable, not a shell wrapper")
        version = None
        if exe and any(j["kind"] not in EXA_KINDS and job_key(j) not in state["jobs"] for j in jobs):
            v = runner([str(exe), "--ignore-config", "--no-plugin-dirs", "--no-remote-components", "--version"], min(timeout, 10))
            version = short(v.get("stdout", "").strip(), 100) if v.get("returncode") == 0 else None
        paused, attempted = set(), 0
        for job in jobs:
            key = job_key(job)
            if key in state["jobs"]:
                if state["jobs"][key]["status"] == "access_blocked":
                    paused.add(job["platform"])
                continue
            if attempted >= max_jobs:
                break
            if job["platform"] in paused:
                result = {"status": "paused_after_access_block", "records": [], "error": "Earlier public request was blocked; no automatic bypass or retry"}
            else:
                attempted += 1
                sleeper(interval)
                if job["kind"] in EXA_KINDS:
                    try:
                        prefix = exa_prefix(mcporter_js)
                        result = collect_exa(job, prefix, runner=runner, timeout=timeout)
                    except ValidationError as exc:
                        result = {"status": "dependency_unavailable", "records": [], "error": str(exc)}
                elif exe:
                    result = collect_yt(job, exe, version, runner=runner, timeout=timeout)
                else:
                    result = {"status": "dependency_unavailable", "records": [], "error": "yt-dlp is not installed; no installation attempted"}
            if result["status"] == "access_blocked":
                paused.add(job["platform"])
            cache = {"job": job, "completed_at": utcnow(), **result}
            cache_path = caches / f"{key}.json"
            atomic_json(cache_path, cache)
            state["jobs"][key] = {"sha256": file_digest(cache_path), "status": result["status"], "records": len(result["records"])}
            atomic_json(state_path, state)
        unique, total, statuses = {}, 0, []
        rank = {"public_video_metadata": 2, "public_listing_metadata": 1, "indexed_search_metadata": 0}
        for job in jobs:
            key = job_key(job)
            if key not in state["jobs"]:
                statuses.append({"job": job, "status": "pending", "records": 0})
                continue
            cache = json.loads((caches / f"{key}.json").read_text(encoding="utf-8"))
            statuses.append({"job": job, "status": cache["status"], "records": len(cache["records"]), "error": cache.get("error")})
            for record in cache["records"]:
                total += 1
                media_id, _, _ = identity(record["webpage_url"])
                old = unique.get(media_id)
                if old is None or rank[record["_collection"]["evidence_scope"]] > rank[old["_collection"]["evidence_scope"]]:
                    unique[media_id] = record
        temporary = output / "records.jsonl.tmp"
        with temporary.open("w", encoding="utf-8") as stream:
            for record in unique.values():
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        os.replace(temporary, output / "records.jsonl")
        report = {**preview, "completed_at": utcnow(), "yt_dlp_version": version,
            "jobs_attempted_this_run": attempted, "completed_jobs": len(state["jobs"]),
            "pending_jobs": len(jobs) - len(state["jobs"]), "source_records": total,
            "unique_records": len(unique), "duplicate_records": total - len(unique),
            "records_sha256": file_digest(output / "records.jsonl"), "results": statuses,
            "qualification": "Metadata candidates only. Run bulk_ingest prepare; no record was imported."}
        atomic_json(output / "report.json", report)
        return report
    finally:
        lock.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-jobs", type=int, default=10)
    parser.add_argument("--interval", type=float, default=2)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--yt-dlp", type=Path, help="Already installed yt-dlp executable")
    parser.add_argument("--mcporter-js", type=Path, help="Already installed mcporter/dist/cli.js, optional")
    args = parser.parse_args(argv)
    try:
        if args.plan.stat().st_size > 1024 * 1024:
            raise ValidationError("Plan exceeds 1 MiB")
        jobs = validate_plan(json.loads(args.plan.read_text(encoding="utf-8-sig")))
        report = collect(jobs, args.output, execute=args.execute, resume=args.resume,
            max_jobs=args.max_jobs, interval=args.interval, timeout=args.timeout,
            yt_dlp=args.yt_dlp, mcporter_js=args.mcporter_js)
        print(json.dumps(report, ensure_ascii=True))
        return 0
    except (ValidationError, OSError, ValueError, TypeError) as exc:
        print(json.dumps({"error": short(str(exc), 400)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
