#!/usr/bin/env python3
"""Bounded public Dailymotion metadata collection; preview by default.

Python standard library only. No media, cookies, credentials, browser or DB.
Legacy public API documented at developers.dailymotion.com/v0/reference/perform-an-api-call.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

VERSION = '1.0.0'
PROVIDER = 'dailymotion-public-api-legacy'
MAX_BYTES = 8 * 1024 * 1024
PAUSE_CODES = {401, 403, 429}
FIELDS = 'id,title,description,url,language,duration,owner,owner.screenname,owner.url,thumbnail_url,created_time,private,published'
QUERIES = [
    'vidange moteur', 'changer filtre huile', 'changer filtre air voiture', 'filtre gazole remplacement',
    'courroie distribution remplacement', 'chaine distribution moteur', 'changer plaquettes frein', 'changer disques frein',
    'purge frein voiture', 'amortisseur voiture remplacement', 'bougies allumage remplacement', 'bougies prechauffage remplacement',
    'alternateur voiture remplacement', 'demarreur voiture remplacement', 'batterie voiture remplacement', 'fusible voiture diagnostic',
    'diagnostic OBD voiture', 'injecteur diesel remplacement', 'vanne EGR nettoyage', 'filtre particules nettoyage',
    'turbo moteur fonctionnement', 'refroidissement moteur thermostat', 'changer essuie glace', 'changer roue secours',
    'rotule direction remplacement', 'embrayage voiture remplacement', 'cardan voiture remplacement', 'roulement roue remplacement',
    'huile moteur viscosite', 'moteur quatre temps fonctionnement', 'boite vitesses fonctionnement', 'differentiel automobile fonctionnement',
    'pilotage freinage degressif', 'pilotage trajectoire circuit', 'karting conseils pilotage', 'stage pilotage technique',
    'simracing reglage volant', 'assetto corsa tutoriel', 'iracing tutorial', 'sim racing setup guide',
    'car oil change tutorial', 'brake pads replacement tutorial', 'engine cooling system explained', 'suspension geometry explained',
    'cambio aceite motor tutorial', 'cambiar pastillas freno', 'motor steuerkette wechseln', 'bremsbelage wechseln anleitung',
    'vidange Clio dci', 'Peugeot HDI tutoriel', 'Renault entretien tutoriel', 'Volkswagen TDI filtre remplacement',
    'moteur hybride fonctionnement', 'voiture electrique diagnostic', 'capteur ABS remplacement', 'courroie accessoires remplacement',
    'biellette barre stabilisatrice remplacement', 'liquide refroidissement vidange', 'nettoyer climatisation voiture', 'reglage geometrie voiture',
]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def plan_hash(plan):
    return sha(json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def write_json(path, value):
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temp, path)


def page_url(plan, query_index, page):
    return 'https://api.dailymotion.com/videos?' + urlencode({
        'fields': FIELDS, 'search': plan['queries'][query_index],
        'limit': plan['page_size'], 'page': page, 'sort': 'relevance'})


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Reader:
    def __init__(self, interval, timeout, *, opener=None, sleep=time.sleep, clock=time.monotonic):
        # No environment proxy, cookie jar, OAuth cache or authentication handler.
        self.opener = opener or build_opener(ProxyHandler({}), NoRedirect())
        self.interval, self.timeout, self.sleep, self.clock = interval, timeout, sleep, clock
        self.last = None

    def get(self, url):
        if self.last is not None:
            delay = self.interval - (self.clock() - self.last)
            if delay > 0:
                self.sleep(delay)
        self.last = self.clock()
        request = Request(url, headers={'User-Agent': f'RaceLink-Academy-Metadata/{VERSION}',
                                        'Accept': 'application/json'}, method='GET')
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                body = response.read(MAX_BYTES + 1)
                entry = {'status': response.status, 'retry_after': response.headers.get('Retry-After')}
                if len(body) > MAX_BYTES:
                    return {**entry, 'body': {}, 'error': 'response_too_large'}
                try:
                    data = json.loads(body.decode('utf-8'))
                except (UnicodeError, json.JSONDecodeError):
                    return {**entry, 'body': {}, 'error': 'not_json'}
                if not isinstance(data, dict) or not isinstance(data.get('list'), list) or not isinstance(data.get('has_more'), bool):
                    return {**entry, 'body': {}, 'error': 'invalid_api_shape'}
                if not all(isinstance(row, dict) for row in data['list']):
                    return {**entry, 'body': {}, 'error': 'invalid_video_record'}
                # Keep only requested publication fields, never unexpected stream/media data.
                allowed = set(FIELDS.split(','))
                projected = {key: data[key] for key in ('page', 'limit', 'total', 'has_more') if key in data}
                projected['list'] = [{key: val for key, val in row.items() if key in allowed} for row in data['list']]
                return {**entry, 'body': projected}
        except HTTPError as error:
            retry_after = error.headers.get('Retry-After') if error.headers else None
            error.close()
            return {'status': error.code, 'retry_after': retry_after, 'body': {}, 'error': 'http_error'}
        except (URLError, TimeoutError, OSError):
            return {'status': 0, 'body': {}, 'error': 'network_error'}


@contextmanager
def output_lock(output):
    output.mkdir(parents=True, exist_ok=True)
    lock = output / '.collector.lock'
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def next_cursor(plan, query_index, page, entry):
    body = entry.get('body', {})
    if (body.get('has_more') is True and len(body.get('list', [])) == plan['page_size']
            and page < plan['pages_per_query']):
        return query_index, page + 1
    return query_index + 1, 1


def validate_entry(entry, plan, query_index, page):
    if not isinstance(entry, dict) or entry.get('provider') != PROVIDER or entry.get('url') != page_url(plan, query_index, page):
        raise ValueError('Cached page identity differs from the plan')
    if type(entry.get('status')) is not int or not isinstance(entry.get('body'), dict):
        raise ValueError('Malformed cached page')
    if entry['status'] == 200 and not entry.get('error'):
        body = entry['body']
        if not isinstance(body.get('list'), list) or type(body.get('has_more')) is not bool or len(body['list']) > plan['page_size']:
            raise ValueError('Cached pagination shape differs from the plan')


def collect(plan, output, *, resume=False, reader=None):
    """Explicit execution entry point; CLI calls it only after --execute."""
    output = Path(output).resolve()
    network_requests = 0
    with output_lock(output):
        checkpoint_path = output / 'checkpoint.json'
        pause = output / 'dailymotion-paused.json'
        fingerprint = plan_hash(plan)
        if checkpoint_path.exists():
            if not resume:
                raise ValueError('Output already contains a collection; use --resume with the same plan')
            state = json.loads(checkpoint_path.read_text(encoding='utf-8'))
            if state.get('plan_sha256') != fingerprint:
                raise ValueError('Resume requires the same queries, limits and interval')
            qi, page = 0, 1
            for item in state['pages']:
                url = page_url(plan, qi, page)
                filename = sha(url.encode())[:20] + '.json'
                path = output / 'raw' / filename
                if item.get('file') != filename or sha(path.read_bytes()) != item.get('sha256'):
                    raise ValueError('A checkpoint cache page is missing or changed')
                entry = json.loads(path.read_text(encoding='utf-8'))
                validate_entry(entry, plan, qi, page)
                qi, page = next_cursor(plan, qi, page, entry)
            if (qi, page) != (state['next_query_index'], state['next_page']):
                raise ValueError('Checkpoint cursor does not match its cache pages')
        else:
            if any(p.name != '.collector.lock' for p in output.iterdir()):
                raise ValueError('A new collection needs an empty output directory')
            state = {'version': VERSION, 'plan_sha256': fingerprint, 'created_at': now(),
                     'next_query_index': 0, 'next_page': 1, 'pages': [], 'complete': False,
                     'paused': False, 'failed': False}
            write_json(output / 'plan.json', plan)
            (output / 'raw').mkdir()
            write_json(checkpoint_path, state)
        if pause.exists() or state.get('paused') or state.get('failed'):
            return {**state, 'paused': pause.exists() or bool(state.get('paused')), 'complete': False,
                    'network_requests_this_run': 0, 'mode': 'execute', 'database_modified': False}
        while state['next_query_index'] < len(plan['queries']):
            if pause.exists():
                state['paused'] = True
                break
            qi, page = state['next_query_index'], state['next_page']
            url = page_url(plan, qi, page)
            path = output / 'raw' / (sha(url.encode())[:20] + '.json')
            cached = path.exists()
            if cached:
                entry = json.loads(path.read_text(encoding='utf-8'))
            else:
                reader = reader or Reader(plan['minimum_request_interval_seconds'], plan['timeout_seconds'])
                result = reader.get(url)
                network_requests += 1
                entry = {**result, 'provider': PROVIDER, 'retrieved_at': now(), 'url': url,
                         'query': plan['queries'][qi], 'page': page}
                write_json(path, entry)
            validate_entry(entry, plan, qi, page)
            state['pages'].append({'file': path.name, 'sha256': sha(path.read_bytes()), 'status': entry['status'],
                                   'query_index': qi, 'page': page, 'received': len(entry['body'].get('list', [])),
                                   'reused_after_checkpoint': cached})
            state['next_query_index'], state['next_page'] = next_cursor(plan, qi, page, entry)
            state['updated_at'] = now()
            if entry['status'] in PAUSE_CODES:
                state['paused'] = True
                write_json(pause, {'observed_at': now(), 'status': entry['status'],
                                  'retry_after': entry.get('retry_after'), 'evidence': 'raw/' + path.name,
                                  'reason': 'access_or_rate_limit_no_automatic_retry'})
            elif entry['status'] != 200 or entry.get('error'):
                state['failed'] = True
            state['complete'] = (state['next_query_index'] == len(plan['queries'])
                                 and not state['paused'] and not state['failed'])
            write_json(checkpoint_path, state)
            if state['paused'] or state['failed']:
                break
        report = {**state, 'mode': 'execute', 'network_requests_this_run': network_requests,
                  'raw_rows': sum(p['received'] for p in state['pages']), 'database_modified': False,
                  'media_downloaded': False, 'authenticated': False}
        write_json(output / 'report.json', report)
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--query', action='append', help='Repeat for custom queries, at most 60')
    parser.add_argument('--start', type=int)
    parser.add_argument('--count', type=int)
    parser.add_argument('--pages', type=int, default=2)
    parser.add_argument('--page-size', type=int, default=100)
    parser.add_argument('--interval', type=float, default=1.5)
    parser.add_argument('--timeout', type=float, default=25)
    args = parser.parse_args(argv)
    if not 1 <= args.pages <= 10 or not 1 <= args.page_size <= 100:
        parser.error('--pages must be 1–10 and --page-size 1–100')
    if not math.isfinite(args.interval) or not 1.5 <= args.interval <= 60 or not math.isfinite(args.timeout) or not 5 <= args.timeout <= 120:
        parser.error('--interval must be 1.5–60 seconds and --timeout 5–120 seconds')
    if args.query:
        if args.start is not None or args.count is not None:
            parser.error('--query cannot be combined with --start/--count')
        queries = [q.strip() for q in args.query]
        if len(queries) > 60 or any(not q or len(q) > 200 or any(ord(c) < 32 for c in q) for q in queries):
            parser.error('Provide 1–60 nonempty queries of at most 200 characters without controls')
        if len(set(queries)) != len(queries):
            parser.error('Duplicate queries are not allowed')
    else:
        start = 0 if args.start is None else args.start
        count = 40 if args.count is None else args.count
        if not 0 <= start < len(QUERIES) or not 1 <= count <= 60 or start + count > len(QUERIES):
            parser.error('--start/--count must select an existing range in the 60-query plan')
        queries = QUERIES[start:start + count]
    plan = {'version': VERSION, 'provider': PROVIDER, 'queries': queries,
            'pages_per_query': args.pages, 'page_size': args.page_size,
            'minimum_request_interval_seconds': args.interval, 'timeout_seconds': args.timeout,
            'maximum_requests': len(queries) * args.pages, 'media_downloaded': False, 'authenticated': False}
    if not args.execute:
        print(json.dumps({'mode': 'preview', 'output': str(args.output), 'writes': False, 'network_requests': 0, 'plan': plan}, ensure_ascii=True))
        return 0
    try:
        result = collect(plan, args.output, resume=args.resume)
        print(json.dumps(result, ensure_ascii=True))
        return 3 if result.get('paused') or result.get('failed') else 0
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'COLLECT_DAILYMOTION: {type(error).__name__}: {str(error)}\n')


if __name__ == '__main__':
    raise SystemExit(main())
