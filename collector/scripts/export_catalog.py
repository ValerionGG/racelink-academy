#!/usr/bin/env python3
"""Export actual catalog metadata for a static deployment (never synthetic data)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import DEFAULT_DB, connect, serialize_video

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
parser.add_argument("--db", type=Path, default=DEFAULT_DB)
args = parser.parse_args()
with connect(args.db) as conn:
    videos = [serialize_video(row, detail=True)
              for row in conn.execute("SELECT * FROM videos ORDER BY title,id")]
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"exported": len(videos), "output": str(args.output)}, ensure_ascii=False))
