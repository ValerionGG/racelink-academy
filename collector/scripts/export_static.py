#!/usr/bin/env python3
"""Export a self-contained public preview with a worker-backed catalog."""
import argparse
import gzip
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import BASE, DEFAULT_DB, PUBLIC, connect, folded, serialize_video, stats, utcnow, load_guides
from scripts.export_social_index import build as build_social_index


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def export_static(db_path, output, base_path="/aide/", *, flat=False):
    output = Path(output).resolve()
    if output == BASE or output.is_relative_to(PUBLIC) or PUBLIC.is_relative_to(output):
        raise ValueError("Export to a separate directory outside the source project")
    if not re.fullmatch(r"/(?:[A-Za-z0-9_-]+/)*", base_path):
        raise ValueError("base-path must look like /aide/")
    # A project host such as GitHub Pages adds its own URL prefix. A flat
    # artifact therefore uses base_path for URLs, without duplicating it on disk.
    web_root = output if flat else output / base_path.strip("/")
    web_root.mkdir(parents=True, exist_ok=True)
    for source in PUBLIC.rglob("*"):
        relative = source.relative_to(PUBLIC)
        if "catalog" in relative.parts or "__pycache__" in relative.parts:
            continue
        if source.is_file():
            destination = web_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if base_path != "/aide/" and source.suffix in {".html", ".js", ".css", ".json"}:
                # Decode raw bytes so unrelated files retain their line endings
                # and can be verified against the source by checksum.
                content = source.read_bytes().decode("utf-8")
                # /aide/api/ remains the virtual API contract understood by the
                # Worker. Other literal references must use the deployed prefix.
                content = re.sub(
                    r"""(['"`])/aide/(?!api/)""",
                    lambda match: match[1] + base_path,
                    content,
                )
                destination.write_bytes(content.encode("utf-8"))
            else:
                shutil.copy2(source, destination)
    entries, transcript_count = [], 0
    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM videos ORDER BY id").fetchall()
        for row in rows:
            item = serialize_video(row)
            for redundant in ("durationSeconds", "thumbnailUrl", "verifiedAt", "reviewStatus",
                              "languageStatus", "levelStatus", "transcriptStatus", "created_at",
                              "updated_at", "source_description", "learning_outcomes", "summary_basis",
                              "summary_language", "summary_quality_note", "contentFormat"):
                item.pop(redundant, None)
            item = {key: value for key, value in item.items() if value is not None and value != ""}
            # Only public search text; no original import metadata, internal paths, or credentials.
            if row["transcript_text"] or row["source_questions_text"]:
                item["_search"] = folded(" ".join([
                    row["title"], row["creator"], row["description"],
                    " ".join(json.loads(row["tags"])), row["transcript_text"], row["source_questions_text"],
                ]))
            if row["transcript_text"]:
                name = hashlib.sha256(row["id"].encode()).hexdigest()[:24] + ".json"
                item["_transcript_file"] = name
                transcript = serialize_video(row, detail=True)["transcript"]
                for internal in ("permission_reference", "source_vtt", "source_sha256"):
                    transcript.pop(internal, None)
                transcript["permission"] = (
                    "Creative Commons Attribution (CC BY) — licence déclarée sur YouTube"
                    if transcript["permission_basis"] == "creative-commons"
                    else transcript["permission_basis"])
                write_json(web_root / "catalog" / "transcripts" / name, transcript)
                transcript_count += 1
            entries.append(item)
    guides = load_guides(PUBLIC)
    write_json(web_root / "social-index.json", build_social_index(db_path, json.loads((PUBLIC / "automotive-taxonomy.json").read_bytes())))
    payload = {"version": 2, "generated_at": utcnow(), "stats": stats(db_path), "items": entries, "guides": guides}
    write_json(web_root / "catalog" / "catalog.json", payload)
    catalog_bytes = (web_root / "catalog" / "catalog.json").read_bytes()
    compressed_bytes = gzip.compress(catalog_bytes, compresslevel=9, mtime=0)
    (web_root / "catalog" / "catalog.json.gz").write_bytes(compressed_bytes)
    catalog_sha256 = hashlib.sha256(catalog_bytes).hexdigest()
    write_json(web_root / "catalog" / "config.json", {
        "mode": "static", "catalog": "catalog.json", "version": 2,
        "compressed_catalog": "catalog.json.gz", "compression": "gzip",
        "catalog_sha256": catalog_sha256,
    })
    if base_path != "/" and not flat:
        (output / "index.html").write_text(
            '<!doctype html><html lang="fr"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta http-equiv="refresh" content="0;url={base_path}">'
            f'<title>Focus Académie</title><a href="{base_path}">Ouvrir Focus Académie</a></html>',
            encoding="utf-8")
        (output / "_redirects").write_text(
            f"/ {base_path} 302\n{base_path.rstrip('/')} {base_path} 301\n", encoding="utf-8")
    (output / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        f"{base_path}catalog/*\n  Cache-Control: public, max-age=300\n",
        encoding="utf-8")
    manifest = {
        "mode": "static", "base_path": base_path, "flat_layout": flat, "videos": len(entries),
        "guides": len(guides), "images": 0, "total_resources": len(entries) + len(guides),
        "transcripts": transcript_count,
        "catalog_bytes": len(catalog_bytes),
        "catalog_gzip_bytes": len(compressed_bytes),
        "catalog_sha256": catalog_sha256,
        "generated_at": payload["generated_at"],
        "contains_synthetic_records": False,
        "search_engine": "Browser Web Worker, normalized word-prefix matching and bounded glossary",
        "backend_secrets_required": False,
    }
    write_json(output / "export-manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-path", default="/aide/")
    parser.add_argument("--flat", action="store_true",
                        help="Write the site at the output root; base-path is only its public URL prefix")
    args = parser.parse_args()
    print(json.dumps(export_static(args.db, args.output, args.base_path, flat=args.flat), indent=2))
