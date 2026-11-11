"""Build the light social finder from the canonical public fields; no remote requests."""
from collections import defaultdict
import json
from pathlib import Path
import sqlite3
from contextlib import closing

APP=Path(__file__).resolve().parents[1]

def build(db, taxonomy):
    with closing(sqlite3.connect(Path(db).resolve().as_uri()+"?mode=ro",uri=True)) as c:
        c.execute("begin")
        where=" platform IN ('tiktok','instagram')"
        vehicles=defaultdict(list); tasks=defaultdict(list)
        for key,make,model,generation,engine in c.execute("SELECT v.video_id,v.make,v.model,v.generation,v.engine FROM video_vehicles v JOIN videos r ON v.video_id=r.id WHERE"+where+" ORDER BY v.video_id,v.position"):
            if make or model or generation or engine: vehicles[key].append([make,model,generation,engine])
        for key,task in c.execute("SELECT v.video_id,v.task FROM video_tasks v JOIN videos r ON v.video_id=r.id WHERE"+where+" ORDER BY v.video_id,v.task"):
            tasks[key].append(task)
        data=[dict(id=k,p=p,t=t,a=a,l=l,c=cat,d=domain,v=vehicles[k],s=tasks[k],u=url,**({'editorFr':True} if pl=='fr' and scope in {'publisher_embedded_post','publisher_post_oembed_identity'} else {})) for k,p,t,a,l,cat,domain,url,pl,scope in
              c.execute("SELECT id,platform,title,creator,language,category,domain_scope,url,json_extract(metadata_json,'$.publisher_context_language'),verification_scope FROM videos WHERE"+where+" ORDER BY verified_at DESC,published_at DESC,id")]
    return dict(version=1,tasks={e['id']:e['label'] for e in taxonomy['tasks']},items=data)

if __name__=='__main__':
    catalog=build(APP/'data/catalog.sqlite3',json.loads((APP/'public/automotive-taxonomy.json').read_bytes()))
    path=APP/'public/social-index.json'
    path.write_bytes(json.dumps(catalog,ensure_ascii=False,separators=(',',':')).encode())
    print(json.dumps(dict(items=len(catalog['items']),bytes=path.stat().st_size)))
