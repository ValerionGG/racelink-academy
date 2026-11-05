"""Acquire bounded, creator-authorized public video metadata for public_export.py.

No global search, media, cookies, retries, client secrets or publication.
Preview is offline; a creator-specific token is read only during --execute.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

TT = "https://open.tiktokapis.com/v2/video/list/"
IG = "https://graph.instagram.com"
FIELDS = {
    "tiktok": "id,title,video_description,share_url,create_time,duration",
    "instagram": "id,username,caption,media_type,media_product_type,permalink,timestamp",
}
def check(condition, message):
    if not condition:
        raise ValueError(message)

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def write(path, obj):
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def plan(platform, handle, account=None, version=None, max_pages=5):
    check(platform in FIELDS and re.fullmatch(r"[a-zA-Z0-9_.]{1,30}", handle or ""), "Invalid platform/creator")
    check(isinstance(max_pages, int) and 1 <= max_pages <= 250, "Limit must be 1–250 pages")
    if platform == "instagram":
        check(re.fullmatch(r"[0-9]{3,30}", account or "") and re.fullmatch(r"v[0-9]{1,2}\.0", version or ""), "Provide the authorized Instagram user ID and supported Graph version")
    else:
        check(not account and not version, "Graph settings apply only to Instagram")
    return dict(platform=platform, handle=handle.lower(), account=account, version=version, max_pages=max_pages, page_size=20)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

def fetch(p, cursor, token):
    fields = FIELDS[p["platform"]]
    if p["platform"] == "tiktok":
        url = TT + "?" + urlencode({"fields": fields})
        body = json.dumps({"max_count": 20, **({"cursor": cursor} if cursor is not None else {})}).encode()
    else:
        url = f"{IG}/{p['version']}/{p['account']}/media?" + urlencode({"limit":20, "fields":fields, **({"after": cursor} if cursor is not None else {})})
        body = None
    req = Request(url, data=body, headers={"Authorization":"Bearer " + token, "Content-Type":"application/json","Accept":"application/json"})
    with build_opener(NoRedirect).open(req, timeout=20) as r:
        payload = r.read(2_000_001)
        check(len(payload) <= 2_000_000, "Response exceeded page budget")
        return json.loads(payload)

def unpack(p, result):
    tt = p["platform"] == "tiktok"
    check(isinstance(result,dict), "Invalid response")
    if tt:
        check(result.get("error",{}).get("code") == "ok", "TikTok did not confirm success")
        d = result["data"]
        rows, more, cursor = d["videos"], d["has_more"], d.get("cursor")
        check(isinstance(more,bool) and (not more or type(cursor) is int and cursor > 0), "Invalid TikTok cursor")
    else:
        check("error" not in result, "Instagram returned an API error")
        rows, paging = result["data"], result.get("paging",{})
        more = bool(paging.get("next"))
        cursor = paging.get("cursors",{}).get("after")
        check(not more or isinstance(cursor,str) and re.fullmatch(r"[\w=/+.-]{1,2048}",cursor,re.ASCII), "Missing/invalid Instagram cursor")
    check(isinstance(rows,list) and len(rows)<=20, "Invalid page size")
    media = []
    for row in rows:
        check(isinstance(row,dict), "Invalid media row")
        if not tt and (row.get("media_type") != "VIDEO" or row.get("media_product_type") != "REELS"):
            continue
        raw = row["share_url" if tt else "permalink"]
        u = urlsplit(raw)
        check(u.scheme=="https" and u.netloc.lower() in ({"www.tiktok.com","tiktok.com"} if tt else {"www.instagram.com","instagram.com"}), "Unexpected public permalink domain")
        path = u.path.rstrip("/")
        if tt:
            match = re.fullmatch(r"/@([\w.]+)/video/([0-9]{10,25})",path,re.ASCII)
            check(match and match[1].lower()==p["handle"] and match[2]==str(row["id"]), "Creator or TikTok ID mismatch")
            url = "https://www.tiktok.com" + path
        else:
            check(str(row.get("username","")).lower()==p["handle"] and re.fullmatch(r"/(?:reel|p)/[a-zA-Z0-9_-]+",path), "Creator or Reel permalink mismatch")
            url = "https://www.instagram.com" + path + "/"
        entry = {k:row[k] for k in FIELDS[p["platform"]].split(",") if k in row}
        entry["share_url" if tt else "permalink"] = url
        if tt:
            entry["creator"]=p["handle"]
        media.append(entry)
    return ({"data":{"videos":media}} if tt else {"data":media}), cursor if more else None, len(rows), len(media)

def run(p, out, token, pages_per_run, get=fetch, sleep=time.sleep):
    check(1<=pages_per_run<=10,"One invocation can request at most 10 pages")
    check(token and not any(c.isspace() for c in token), "A dedicated authorized creator token is required in the process environment")
    out.mkdir(parents=True, exist_ok=True)
    cp = out/"checkpoint.json"
    # Exclusive marker also prevents two processes from fetching the same cursor.
    lock = out/"in-flight"
    with lock.open("x",encoding="utf-8") as f:
        f.write(now())
    attempted = False
    try:
        s=json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else dict(plan=p,created=now(),pages=[],cursors=[],cursor=None,done=False,observed=0,videos=0)
        check(s["plan"]==p, "Plan changed; cannot resume")
        for i,item in enumerate(s["pages"],1):
            check(item["file"]==f"page-{i:04}.json" and sha(out/item["file"])==item["sha256"],"Page checkpoint mismatch")
        for _ in range(pages_per_run):
            if s["done"] or len(s["pages"]) >= p["max_pages"]: break
            name=f"page-{len(s['pages'])+1:04}.json"
            path=out/name
            check(not path.exists(),"Unreconciled existing page")
            attempted=True
            result=get(p,s["cursor"],token)
            safe,cursor,observed,nvideos=unpack(p,result)
            check(cursor is None or cursor not in s["cursors"],"Repeated cursor; source suspended")
            write(path,safe)
            s["pages"].append(dict(file=name,sha256=sha(path),format="json",schema="tiktok_display" if p["platform"]=="tiktok" else "meta_graph"))
            s.update(cursor=cursor,done=cursor is None,observed=s["observed"]+observed,videos=s["videos"]+nvideos)
            if cursor is not None: s["cursors"].append(cursor)
            write(cp,s)
            attempted=False
            if cursor is not None and len(s["pages"])<p["max_pages"] and _+1<pages_per_run: sleep(1)
        host="https://www.tiktok.com/@" if p["platform"]=="tiktok" else "https://www.instagram.com/"
        source=dict(name=p["handle"],kind="authorized_api_export",source_url=host+p["handle"],evidence_reference="Authorized account API response; creator matched to its native post metadata",captured_at=s["created"])
        write(out/"manifest.json",dict(version=1,kind="PUBLIC_EXPORT",source=source,pages=s["pages"]))
        return dict(pages=len(s["pages"]),source_records=s["observed"],video_rows=s["videos"],complete=s["done"],cap_reached=len(s["pages"])==p["max_pages"],imported=0)
    finally:
        if not attempted: lock.unlink()

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platform",choices=FIELDS)
    parser.add_argument("handle")
    parser.add_argument("--account-id")
    parser.add_argument("--graph-version")
    parser.add_argument("--max-pages",type=int,default=5)
    parser.add_argument("--pages-per-run",type=int,default=2)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--execute",action="store_true")
    a=parser.parse_args()
    try:
        p=plan(a.platform,a.handle,a.account_id,a.graph_version,a.max_pages)
        if a.execute:
            check(a.output,"--output is required")
            result=run(p,a.output,os.environ.get("RACELINK_"+a.platform.upper()+"_CREATOR_TOKEN"),a.pages_per_run)
        else:
            result=dict(preview=p,max_source_rows=20*a.max_pages,network_requests=0)
        print(json.dumps(result))
    except Exception as e:
        # HTTP exceptions may contain upstream URLs; never display provider bodies or headers.
        parser.exit(2,"Collection stopped: "+(str(e) if type(e) is ValueError else type(e).__name__)+"\n")
