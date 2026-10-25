#!/usr/bin/env python3
"""Create a bounded metadata review pack; no network, database or approvals."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from scripts.bulk_ingest import MAX_INPUT_BYTES, MAX_ITEMS, VERSION, atomic_json, file_digest, short
from server import ValidationError, language_confidence, utcnow


def review_batch(prepared, output, batch_size=250):
    if not isinstance(batch_size, int) or isinstance(batch_size, bool) or not 1 <= batch_size <= 250:
        raise ValidationError("Review batches must contain 1–250 candidates")
    prepared, output = Path(prepared), Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValidationError("Use a new or empty review directory")
    report = json.loads((prepared/"report.json").read_text(encoding="utf-8"))
    for name, key in (("accepted.json", "accepted_sha256"), ("quarantine.jsonl", "quarantine_sha256")):
        path = prepared/name
        if path.stat().st_size > MAX_INPUT_BYTES:
            raise ValidationError("Prepared file exceeds 150 MiB; split source into smaller preparations")
        if file_digest(path) != report.get(key):
            raise ValidationError("Prepared file hash is absent or differs; prepare again without modifying evidence")
    records = json.loads((prepared/"accepted.json").read_text(encoding="utf-8"))
    with (prepared/"quarantine.jsonl").open(encoding="utf-8") as stream:
        quarantine = [json.loads(line) for line in stream if line.strip()]
    if not isinstance(records, list) or len(records)+len(quarantine) > MAX_ITEMS:
        raise ValidationError("Invalid or unbounded prepared records")
    ids = [r.get("id") for r in records if isinstance(r, dict)]
    if len(ids) != len(records) or not all(isinstance(i,str) and i for i in ids) or len(ids) != len(set(ids)):
        raise ValidationError("Candidate identities must be explicit and unique")
    if any(r.get("review_status") != "candidate" or r.get("bulk_qualification",{}).get("status") != "candidate" for r in records):
        raise ValidationError("Review pack accepts metadata candidates only, not editorial selections")
    groups = defaultdict(list)
    for record in records:
        key = (record["platform"], record["category_slug"], record["verification_scope"],
               record["language"].split("-")[0], language_confidence(record["language"],record["language_status"]))
        groups[key].append(record["id"])
    batches = []
    for key in sorted(groups):
        members = sorted(groups[key])
        for offset in range(0,len(members),batch_size):
            chunk = members[offset:offset+batch_size]
            sample_count = min(len(chunk), max(5, math.ceil(len(chunk)*.1)))
            sample = sorted(chunk, key=lambda identifier: hashlib.sha256(
                (report["accepted_sha256"]+"\0"+identifier).encode()).hexdigest())[:sample_count]
            batches.append({"id": f"review-{len(batches)+1:04}", "platform":key[0], "category":key[1],
                "verification_scope":key[2], "language":key[3], "language_confidence":key[4],
                "candidate_ids":chunk, "source_sample_ids":sample,
                "status":"pending_metadata_review", "approved_ids":[],
                "rule":"Review every title/caption; inspect the deterministic source sample. Any off-topic, promotional or incorrect-language sample holds this batch for full source review. Sampling does not verify every video or its technical correctness."})
    held_ids = sorted(q["id"] for q in quarantine if isinstance(q.get("id"),str))
    result = {"created_at":utcnow(), "rules_version":VERSION, "mode":"review_only",
        "database_modified":False, "network_used":False, "approved_ids":[],
        "accepted_sha256":report["accepted_sha256"], "quarantine_sha256":report["quarantine_sha256"],
        "candidate_count":len(records), "quarantine_count":len(quarantine),
        "invalid_source_records":sum(len(q.get("source_variants",[q])) for q in quarantine if q.get("record") is None),
        "held_ids":held_ids, "batch_size_bound":batch_size, "batches":batches,
        "quarantine_reasons":dict(Counter(reason for q in quarantine for reason in q.get("reasons",[]))),
        "notes":["Candidate lists are not approval manifests.",
                 "Indexed text is not direct page verification or a full-video review.",
                 "French text estimates do not confirm French audio.",
                 "Vehicle mentions in source prose are not manufacturer compatibility.",
                 "Quarantined identities require individual review and a new preparation; they are excluded from candidate IDs."]}
    output.mkdir(parents=True,exist_ok=True)
    atomic_json(output/"review-batches.json",result)
    atomic_json(output/"candidate-ids.json",sorted(ids))
    atomic_json(output/"french-candidate-ids.json",sorted(r["id"] for r in records if r["language"].split("-")[0] == "fr"))
    with (output/"candidates-review.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        fields=["id","url","title","creator","sourceDescription","platform","category_slug","language",
                "language_status","verification_scope","vehicle_mentions","language_evidence","qualification_evidence"]
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for record in sorted(records,key=lambda r:r["id"]):
            row={field:record.get(field,"") for field in fields}
            row["vehicle_mentions"]=json.dumps(record.get("automotive",{}).get("vehicles",[]),ensure_ascii=False)
            row["language_evidence"]=json.dumps(record.get("language_evidence",{}),ensure_ascii=False)
            row["qualification_evidence"]=json.dumps(record.get("bulk_qualification",{}).get("evidence",{}),ensure_ascii=False)
            # CSV cells are source text, not executable spreadsheet formulae.
            row={key:("'"+str(value) if str(value).startswith(("=","+","-","@","\t","\r")) else value) for key,value in row.items()}
            writer.writerow(row)
    return {"mode":result["mode"],"candidate_count":len(records),"quarantine_count":len(quarantine),
            "review_batches":len(batches),"approved_count":0,"database_modified":False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--batch-size",type=int,default=250)
    args=parser.parse_args(argv)
    try:
        result=review_batch(args.prepared,args.output,args.batch_size)
        print(json.dumps(result,ensure_ascii=True))
        return 0
    except (ValidationError,OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"error":short(str(exc),300)},ensure_ascii=True),file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
