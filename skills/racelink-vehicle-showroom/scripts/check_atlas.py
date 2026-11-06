"""Check an atlas registry and local photo files; never certifies visual accuracy.
Usage: python check_atlas.py public/atlas/models.json public/
"""
import json,sys
from pathlib import Path
from urllib.parse import urlparse

def check(registry,public):
    public=public.resolve();models=json.loads(registry.read_text(encoding='utf-8'));errors=[];coverage=[];seen=set()
    def require(condition,message):
        if not condition:errors.append(message)
    for m in models:
        mid=m.get('id');require(mid and mid not in seen,f'Duplicate/missing model: {mid}');seen.add(mid)
        require(all(m.get(k) for k in ['make','model','generation','year','market','availability_date','availability_scope']),f'{mid}: missing identity/scope')
        require(m.get('availability_status') in ['verified','partial_verified'],f'{mid}: unreviewed availability')
        require(isinstance(m.get('availability_complete'),bool),f'{mid}: missing complete/partial flag')
        engines={e['id'] for e in m.get('engines',[])}
        require(len(engines)==len(m.get('engines',[])),f'{mid}: duplicate engine IDs')
        trims=set()
        for t in m.get('trims',[]):
            require(t['id'] not in trims,f'{mid}: duplicate trim');trims.add(t['id'])
            require(t.get('engines') and set(t['engines'])<=engines,f'{mid}/{t["id"]}: invalid engine relation')
            require(urlparse(t.get('source','')).scheme=='https',f'{mid}: trim source missing')
        for e in m.get('engines',[]):require(urlparse(e.get('source','')).scheme=='https',f'{mid}: engine source missing')
        for p in m.get('photos',[]):
            require(all(p.get(k) for k in ['src','title','alt','caption','view','author','date','source','license','licenseUrl','changes','width','height']),f'{mid}: incomplete photo provenance')
            require(p.get('exactBodyMatch',True),f'{mid}: another body used as this vehicle')
            target=(public/p['src']).resolve()
            require(target.is_relative_to(public) and target.is_file(),f'{mid}: missing/unsafe photo path')
            require(p['view'] in ['exterior','interior','engine','cargo','underbody','detail'],f'{mid}: invalid view')
            require(urlparse(p['source']).scheme=='https' and urlparse(p['licenseUrl']).scheme=='https',f'{mid}: insecure photo provenance URL')
        for viewer in m.get('immersive',[]):
            require(viewer.get('kind') in ['oem','artist'],f'{mid}: invalid viewer kind')
            require(all(viewer.get(k) for k in ['embedUrl','url','modelScope','note','checkedAt']),f'{mid}: missing viewer scope')
            require(viewer.get('verified',{}).get('render') and viewer.get('verified',{}).get('controls'),f'{mid}: viewer not tested')
            require(urlparse(viewer['embedUrl']).scheme=='https',f'{mid}: insecure viewer')
            require(not any(k in viewer for k in ['evidence','verificationOrigin','mobileVerification']),f'{mid}: private evidence in public registry')
        coverage.append({'id':mid,'photos':len(m.get('photos',[])),'missing_photo_views':[v for v in ['exterior','interior'] if not any(p['view']==v for p in m.get('photos',[]))],'viewers':len(m.get('immersive',[])),'pairs':sum(len(t['engines']) for t in m.get('trims',[])),'complete_availability':m.get('availability_complete')})
    return {'status':'failed' if errors else 'passed','models':len(models),'photos':sum(m['photos'] for m in coverage),'pairs':sum(m['pairs'] for m in coverage),'coverage':coverage,'errors':errors,'scope':'Structure, provenance fields and local file presence only. Visual identity and the behaviour of remote viewers require separate review.'}
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit(__doc__)
    report=check(Path(sys.argv[1]),Path(sys.argv[2]));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(bool(report['errors']))
