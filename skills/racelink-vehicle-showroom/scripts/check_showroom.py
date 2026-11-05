"""Check the vehicle, trim/engine matrix, manual periods and photo credit records."""
import argparse, datetime, json, re
from pathlib import Path
from urllib.parse import urlparse

def require(value, label):
    if not value:
        raise ValueError(label)

def https(url):
    return isinstance(url, str) and urlparse(url).scheme == 'https' and bool(urlparse(url).netloc)

def check(d, photos, directory):
    day=datetime.date.fromisoformat(d['availability_date'])
    year=d['year']
    require(type(year) is int and 1885 <= year <= 9999 and d['model'] and d['market'],'Dated vehicle identity')
    if day.year != year:
        evidence=d.get('year_evidence') or {}
        require(isinstance(evidence,dict) and https(evidence.get('source')) and
                evidence.get('year') == year and isinstance(evidence.get('note'),str) and evidence['note'].strip(),
                'Provide the source and reason connecting this tariff date to the requested year')
    require(https(d['sources']['tariff']) and https(d['sources']['dimensions']),'Market and geometry sources')
    engines=[e['id'] for e in d['engines']]
    require(len(engines)==len(set(engines)) and all(e['gearbox'] and e['fuel'] for e in d['engines']),'Engine identities')
    trims=[t['id'] for t in d['trims']]
    require(trims and len(trims)==len(set(trims)),'Trim identities')
    pairs=0;covered=set()
    for t in d['trims']:
        require(t['engines'] and set(t['engines']).issubset(engines),'Unknown motor or empty trim: '+t['id'])
        require(all(type(p) is int and p>0 for p in t['engines'].values()),'Missing published price')
        pairs+=len(t['engines']);covered.update(t['engines'])
    require(covered==set(engines),'Unpriced engine in matrix')
    periods=[]
    for edition in d['date_editions']:
        a,b=(datetime.date.fromisoformat(edition[k]) for k in ('from','to'))
        require(a<=b and https(edition['guide']) and https(edition['pdf']), 'Manual date or URL')
        periods.append((a,b))
    periods.sort()
    require(periods and all(a[1]<b[0] for a,b in zip(periods,periods[1:])), 'Overlapping or missing manual periods')
    require(photos and len({p['src'] for p in photos})==len(photos),'Photo identities')
    for p in photos:
        require(re.fullmatch(r'[\w.-]+\.(webp|jpg|jpeg|png|avif)',p['src']) and (directory/p['src']).is_file(),'Missing local photo')
        require(all(p.get(k) for k in ('alt','title','caption','author','changes','license')) and all(https(p.get(k)) for k in ('source','licenseUrl')), 'Incomplete photo rights or provenance')
        datetime.date.fromisoformat(p['date'])
        require(p.get('view') in ('exterior','interior','engine','cargo','underbody','detail'), 'Unknown photo view: '+p['src'])
    require({'exterior','interior'}.issubset({p['view'] for p in photos}), 'An exterior and an interior photo are required')
    return dict(model=d['model'],market=d['market'],as_of=str(day),trims=len(trims),engines=len(engines),combinations=pairs,photos=len(photos),manual_editions=len(periods))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('dossier','photos','directory'):parser.add_argument(arg,type=Path)
    a=parser.parse_args()
    print(json.dumps(check(json.loads(a.dossier.read_text(encoding='utf-8')),json.loads(a.photos.read_text(encoding='utf-8')),a.directory),ensure_ascii=False))
