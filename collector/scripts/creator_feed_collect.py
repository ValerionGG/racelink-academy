"""Read visible Instagram cards on an approved publisher's website. Python 3.10+."""
import argparse
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import socket
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler, Request
from urllib.robotparser import RobotFileParser

AGENT = 'RaceLinkAcademyReferenceBot/1.0'
MAX_BYTES = 3_000_000
MAX_CARDS = 30

def permalink(url):
    try:
        parts = urlsplit(url)
        if (parts.scheme != 'https' or parts.hostname not in ('www.instagram.com','instagram.com')
                or parts.username or parts.password or parts.port):
            return None
    except ValueError:
        return None
    path = re.fullmatch(r'/(?:[\w.]+/)?(reel|p|tv)/([A-Za-z0-9_-]{7,16})/?',parts.path)
    if path:
        return 'instagram:'+path[2], 'https://www.instagram.com/'+path[1]+'/'+path[2]+'/'

class Cards(HTMLParser):
    """Keep captions inside the enclosing public card and ignore ordinary profile links."""
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.card = None
        self.records = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get('class') or '').split()
        if tag == 'div':
            self.depth += 1
            if 'sbi_item' in classes:
                kinds = [c[9:] for c in classes if c.startswith('sbi_type_')]
                self.card = {'depth':self.depth, 'media_type':kinds[0] if len(kinds)==1 else 'unknown',
                             'links':{}, 'caption':'', 'caption_truncated':False}
        if self.card is None:
            return
        if tag=='a':
            result=permalink(attrs.get('href') or '')
            if result:
                self.card['links'][result[0]]=result[1]
        if tag=='img':
            alt = (attrs.get('alt') or '').strip()
            if len(alt)>len(self.card['caption']):
                self.card['caption']=alt[:2200]
                self.card['caption_truncated']=len(alt)>2200

    def handle_endtag(self,tag):
        if tag!='div':
            return
        if self.card and self.card['depth']==self.depth:
            card=self.card
            if len(card['links'])==1 and len(self.records)<MAX_CARDS:
                identity,url=next(iter(card['links'].items()))
                caption=card['caption']
                if re.fullmatch(r'(?:Publication|Post) [0-9]+ Instagram',caption, re.I):
                    caption=''
                self.records.append({'id':identity,'url':url,'media_type':card['media_type'],
                                     'publisher_caption':caption,'caption_truncated':card['caption_truncated']})
            self.card=None
        self.depth=max(0,self.depth-1)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args):
        raise ValueError('redirect_stopped')

def read_http(url,cap):
    opener=build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(Request(url,headers={'User-Agent':AGENT,'Accept-Encoding':'identity'}),timeout=12) as response:
            body=response.read(cap+1)
            if len(body)>cap:
                raise ValueError('response_over_limit')
            return response.status,response.headers.get_content_type(),body
    except HTTPError as err:
        return err.code,'',b''

def wildcard_exclusion(lines,path):
    """Conservatively honour matching wildcard exclusions even on older Python."""
    for line in lines:
        name,sep,rule=line.partition('#')[0].partition(':')
        if not sep or name.strip().lower()!='disallow':
            continue
        rule=rule.strip()
        if '*' not in rule and not rule.endswith('$'):
            continue
        anchored=rule.endswith('$')
        expr=re.escape(rule[:-1] if anchored else rule).replace(r'\*','.*')
        if re.match(expr+('$' if anchored else ''),path):
            return True
    return False

def page_cards(job):
    url=job['url']
    host=urlsplit(url).hostname
    addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('nonpublic_host')
    status,ct,body=read_http('https://'+host+'/robots.txt',500_000)
    if status==200:
        if ct=='text/html' or b'<html' in body[:2000].lower():
            raise ValueError('robots_returned_html')
        rules=RobotFileParser()
        lines=body.decode('utf-8','replace').splitlines()
        rules.parse(lines)
        if not rules.can_fetch(AGENT,url) or wildcard_exclusion(lines,urlsplit(url).path or '/'):
            raise ValueError('robots_disallow')
        delay=max(rules.crawl_delay(AGENT) or 0,1)
        rate=rules.request_rate(AGENT)
        if rate:
            delay=max(delay,rate.seconds/rate.requests)
        if delay>15:
            raise ValueError('defer_for_crawl_delay')
        time.sleep(delay)
    elif status not in (404,410):
        raise ValueError('robots_unavailable_http_'+str(status))
    status,ct,body=read_http(url,MAX_BYTES)
    if status!=200 or ct!='text/html':
        raise ValueError('publisher_unavailable_http_'+str(status))
    parser=Cards()
    parser.feed(body.decode('utf-8','replace'))
    return {'source_sha256':hashlib.sha256(body).hexdigest(),'cards':parser.records}

def plan_jobs(config):
    jobs=config['jobs']
    if not isinstance(jobs,list) or not 1<=len(jobs)<=20:
        raise ValueError('expected_1_to_20_jobs')
    hosts=set()
    for job in jobs:
        u=urlsplit(job['url'])
        host=u.hostname or ''
        if (not job.get('creator') or u.scheme!='https' or u.username or u.password or u.port
                or u.fragment or u.query or '.' not in host or not re.fullmatch(r'[a-z0-9.\-]+',host)):
            raise ValueError('invalid_publisher')
        if host in hosts or any(host==d or host.endswith('.'+d) for d in ('instagram.com','facebook.com','tiktok.com')):
            raise ValueError('only_distinct_publisher_hosts')
        hosts.add(host)
    return jobs

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path)
    parser.add_argument('--job',type=int,required=True,help='Zero-based index, one publisher per call')
    parser.add_argument('--checkpoint',type=Path)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    raw=args.plan.read_bytes()
    jobs=plan_jobs(json.loads(raw.decode('utf-8-sig')))
    if not 0<=args.job<len(jobs):
        parser.error('job outside plan')
    job=jobs[args.job]
    report={'plan_sha256':hashlib.sha256(raw).hexdigest(),'job':args.job,**job,'max_cards':MAX_CARDS}
    if not args.execute:
        print(json.dumps(report,ensure_ascii=False))
        return
    if not args.checkpoint:
        parser.error('--execute requires --checkpoint')
    root=args.checkpoint.resolve()
    root.mkdir(parents=True,exist_ok=True)
    pin=root/'plan.sha256'
    if not pin.exists():
        try:
            with pin.open('x') as f:
                f.write(report['plan_sha256'])
        except FileExistsError:
            pass
    if pin.read_text()!=report['plan_sha256']:
        raise SystemExit('checkpoint belongs to another plan')
    marker=root/(str(args.job)+'.started.json')
    result=root/(str(args.job)+'.result.json')
    if marker.exists() or result.exists():
        raise SystemExit('already attempted; read the result or reconcile a missing receipt')
    with marker.open('x',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False)
    try:
        report.update(page_cards(job))
        report['status']='observed'
    except (OSError,ValueError) as e:
        report.update(status='paused',reason=str(e)[:150])
    report['review_status']='unreviewed'
    tmp=result.with_suffix('.tmp')
    tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(result)
    print(report['status'],len(report.get('cards',[])))

if __name__=='__main__':
    main()
