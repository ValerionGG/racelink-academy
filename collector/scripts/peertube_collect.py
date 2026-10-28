#!/usr/bin/env python3
"""Bounded metadata-only SepiaSearch collection. Preview by default; never imports.

No authentication, browser, proxy, media fetch, or paid endpoint. Every response
is retained privately; publication requires separate editorial review.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit
import uuid

ENDPOINT = 'https://sepiasearch.org/api/v1/search/videos'
CHANNEL_HOSTS = {'tube-enseignement-professionnel.apps.education.fr', 'peertube.lyceeconnecte.fr'}
VERSION = '1.0.0'
MAX_BYTES = 8 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(value).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def integer(value, minimum, maximum, label):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f'{label}: expected integer {minimum}–{maximum}')
    return value


def validate_plan(plan, maximum=100):
    if not isinstance(plan, dict) or set(plan) != {'jobs'}:
        raise ValueError('Plan must contain only jobs')
    jobs = plan['jobs']
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 20:
        raise ValueError('Expected 1–20 jobs')
    clean, seen = [], set()
    for item in jobs:
        if not isinstance(item, dict) or set(item) - {'query', 'channel', 'limit', 'language'}:
            raise ValueError('Unknown job field')
        if 'channel' in item:
            if set(item) - {'channel', 'limit'}:
                raise ValueError('Channel jobs only accept channel and limit')
            url = safe_url(item['channel'])
            parsed = urlsplit(url)
            if parsed.hostname not in CHANNEL_HOSTS or not re.fullmatch(r'/video-channels/[A-Za-z0-9_.-]{1,100}', parsed.path):
                raise ValueError('Channel must belong to an explicitly reviewed educational host')
            if url in seen:
                raise ValueError('Repeated channel')
            seen.add(url)
            clean.append({'channel': url, 'limit': integer(item.get('limit', 20), 1, 100, 'limit')})
            continue
        query = item.get('query')
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= 200 or any(ord(c) < 32 for c in query):
            raise ValueError('Invalid query')
        query = query.strip()
        language = item.get('language', 'fr')
        if language is not None and (not isinstance(language, str) or not re.fullmatch('[a-z]{2,3}(?:-[A-Za-z]{2,4})?', language)):
            raise ValueError('Invalid language')
        limit = integer(item.get('limit', 20), 1, 100, 'limit')
        if (query.casefold(), language) in seen:
            raise ValueError('Repeated query in plan')
        seen.add((query.casefold(), language))
        clean.append({'query': query, 'limit': limit, 'language': language})
    if sum(j['limit'] for j in clean) > maximum:
        raise ValueError('Plan exceeds maximum result budget')
    return clean


def request_url(job, start=0):
    if 'channel' in job:
        parsed = urlsplit(job['channel'])
        endpoint = 'https://' + parsed.hostname + '/api/v1' + parsed.path + '/videos'
        params = {'count': min(25, job['limit'] - start), 'start': start, 'nsfw': 'false', 'isLive': 'false', 'sort': '-publishedAt'}
        return endpoint + '?' + urlencode(params)
    params = {'search': job['query'], 'count': min(25, job['limit'] - start), 'start': start, 'nsfw': 'false', 'isLive': 'false'}
    if job['language']:
        params['languageOneOf'] = job['language']
    return ENDPOINT + '?' + urlencode(params)


def safe_url(value):
    if not isinstance(value, str) or len(value) > 2048 or any(ord(c) < 33 for c in value):
        raise ValueError('Invalid public URL')
    p = urlsplit(value)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port or p.query or p.fragment or '\\' in value:
        raise ValueError('Expected canonical HTTPS URL')
    host = p.hostname.lower()
    if '.' not in host or host.endswith(('.local', '.localhost', '.internal')):
        raise ValueError('Nonpublic host')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('IP host not accepted')
    return urlunsplit(('https', host, p.path, '', ''))


def optional_url(value):
    try:
        return safe_url(value)
    except (ValueError, TypeError):
        return None


def normalize(row, proof):
    if not isinstance(row, dict):
        raise ValueError('Result is not an object')
    if not isinstance(row.get('privacy'), dict) or row['privacy'].get('id') != 1:
        raise ValueError('Public visibility not attested')
    if row.get('nsfw') is not False or row.get('isLive') is not False:
        raise ValueError('Sensitive, live, or unknown status')
    ident = str(uuid.UUID(row.get('uuid', '')))
    url = safe_url(row.get('url'))
    path = urlsplit(url).path
    if path != '/videos/watch/' + ident and path != '/w/' + str(row.get('shortUUID', '')):
        raise ValueError('Video URL does not match native identity')
    title = row.get('name')
    if not isinstance(title, str) or not title.strip() or len(title) > 1000:
        raise ValueError('Missing/invalid title')
    description = row.get('description')
    if description is not None and not isinstance(description, str):
        raise ValueError('Invalid description')
    tags = row.get('tags') or []
    if not isinstance(tags, list) or any(not isinstance(x, str) for x in tags):
        raise ValueError('Invalid tags')
    lang = row.get('language') or {}
    channel = row.get('channel') or {}
    thumbnail = optional_url(row.get('thumbnailUrl'))
    if not thumbnail and urlsplit(url).hostname in CHANNEL_HOSTS:
        path = row.get('thumbnailPath')
        if isinstance(path, str) and re.fullmatch(r'/(?:lazy-static|static)/thumbnails/[A-Za-z0-9_.-]+', path):
            thumbnail = optional_url(urljoin(url, path))
    return {
        'identity': f'peertube:{urlsplit(url).hostname}:{ident}',
        'platform': 'peertube', 'sourceId': ident, 'url': url,
        'title': title.strip(), 'description': description,
        'hashtags': list(dict.fromkeys(re.findall(r'(?<!\w)#([\w]+)', description or '', re.UNICODE))),
        'tags': tags, 'language': lang.get('id'), 'languageEvidence': 'platform_declared_not_audio_verified',
        'durationSeconds': row.get('duration'),
        'author': channel.get('displayName') or channel.get('name'),
        'authorUrl': optional_url(channel.get('url')),
        'thumbnailUrl': thumbnail,
        'publishedAt': row.get('publishedAt'),
        'licenceDeclared': row.get('licence'), 'licenceVerified': False,
        'descriptionScope': 'search_index_excerpt_may_be_truncated',
        'transcript': None, 'vehicleEvidence': [], 'status': 'requires_editorial_review',
        'nativeRecordSha256': sha(row), 'provenance': proof,
    }


def fetch(url, raw_path, timeout=30):
    """One public GET; TLS checked, no redirect/retry, 8 MiB ceiling."""
    parsed = urlsplit(url)
    channel_endpoint = parsed.scheme == 'https' and parsed.hostname in CHANNEL_HOSTS and not parsed.username and not parsed.password and not parsed.port and not parsed.fragment and re.fullmatch(r'/api/v1/video-channels/[A-Za-z0-9_.-]{1,100}/videos', parsed.path)
    if not url.startswith(ENDPOINT + '?') and not channel_endpoint:
        raise ValueError('Only the approved search endpoint is allowed')
    curl = shutil.which('curl.exe') or shutil.which('curl')
    if not curl:
        raise RuntimeError('curl is required')
    command = [curl, '--disable', '--silent', '--show-error', '--proto', '=https',
               '--max-time', str(timeout), '--connect-timeout', '10', '--max-filesize', str(MAX_BYTES),
               '--retry', '0', '--noproxy', '*', '--user-agent', 'RaceLinkAcademyMetadata/1.0 (public educational reference pilot)',
               '--output', str(raw_path), '--write-out', '%{http_code}', url]
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout + 5, check=False)
    status = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
    if result.returncode or status != 200:
        raise RuntimeError(f'HTTP {status}; curl exit {result.returncode}. Source paused; no automatic retry.')
    body = Path(raw_path).read_bytes()
    if len(body) > MAX_BYTES:
        raise ValueError('Response exceeds size cap')
    value = json.loads(body)
    if not isinstance(value, dict) or not isinstance(value.get('data'), list):
        raise ValueError('Unexpected API response; source paused')
    return value, sha(body)


def collect(jobs, output, *, resume=False, interval=3, timeout=30, fetcher=fetch, sleeper=time.sleep):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    lock = output / 'collector.lock'
    try:
        handle = lock.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise ValueError('Another collection may be active. Review the lock; never launch a parallel replay.') from exc
    try:
        with handle:
            handle.write(now())
        return _collect(jobs, output, resume=resume, interval=interval, timeout=timeout, fetcher=fetcher, sleeper=sleeper)
    finally:
        lock.unlink()


def _collect(jobs, output, *, resume=False, interval=3, timeout=30, fetcher=fetch, sleeper=time.sleep):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    cp_path = output / 'checkpoint.json'
    plan_sha = sha(jobs)
    if cp_path.exists():
        cp = json.loads(cp_path.read_text(encoding='utf-8'))
        if not resume or cp.get('planSha256') != plan_sha:
            raise ValueError('Use --resume with the same plan and checkpoint')
        if cp.get('blocked') or any(p['status'] == 'pending' for p in cp['pages']):
            raise ValueError('Uncertain/blocked request requires review, never automatic replay')
    else:
        if resume:
            raise ValueError('No checkpoint exists to resume')
        cp = {'version': VERSION, 'createdAt': now(), 'planSha256': plan_sha, 'jobs': jobs, 'pages': [], 'blocked': False}
        save(cp_path, cp)
    for job_no, job in enumerate(jobs):
        pages = [p for p in cp['pages'] if p['job'] == job_no]
        if pages and pages[-1].get('done'):
            continue
        start = sum(p['count'] for p in pages)
        while start < job['limit']:
            if cp['pages']:
                sleeper(interval)
            url = request_url(job, start)
            name = f'job-{job_no:02d}-offset-{start:04d}.json'
            raw_path = output / 'raw' / name
            raw_path.parent.mkdir(exist_ok=True)
            page = {'job': job_no, 'offset': start, 'requestUrl': url, 'rawFile': 'raw/' + name, 'status': 'pending', 'startedAt': now()}
            cp['pages'].append(page)
            save(cp_path, cp)  # Reserve before request; an interrupted request is never silently replayed.
            try:
                value, digest = fetcher(url, raw_path, timeout)
                count = len(value['data'])
                requested = min(25, job['limit'] - start)
                if count > requested:
                    raise ValueError('Response exceeds requested result count')
                page.update(status='completed', sha256=digest, count=count, receivedAt=now(),
                            done=count < requested or start + count >= job['limit'])
                save(cp_path, cp)
                start += count
                if page['done']:
                    break
            except Exception as exc:
                page.update(status='blocked', error=str(exc), failedAt=now())
                cp['blocked'] = True
                save(cp_path, cp)
                raise
    records, rejected, duplicates, seen = [], [], [], {}
    for page in cp['pages']:
        raw = (output / page['rawFile']).read_bytes()
        if sha(raw) != page['sha256']:
            raise ValueError('Raw evidence changed')
        data = json.loads(raw)['data']
        for position, native in enumerate(data):
            proof = {k: page[k] for k in ('requestUrl', 'rawFile', 'sha256', 'receivedAt')}
            proof.update(resultIndex=position, collector='peertube_collect/' + VERSION)
            try:
                record = normalize(native, proof)
                identity = record['identity']
                if identity in seen:
                    duplicates.append({'identity': identity, 'variantConflict': seen[identity]['nativeRecordSha256'] != record['nativeRecordSha256'], 'record': record})
                else:
                    seen[identity] = record
                    records.append(record)
            except (ValueError, TypeError, AttributeError) as exc:
                rejected.append({'reason': str(exc), 'provenance': proof})
    save(output / 'records.json', records)
    save(output / 'duplicates.json', duplicates)
    save(output / 'rejected.json', rejected)
    report = {'finishedAt': now(), 'source': 'PeerTube public metadata APIs / SepiaSearch', 'requests': len(cp['pages']),
              'rawResults': sum(p['count'] for p in cp['pages']), 'distinctCandidates': len(records),
              'duplicateRows': len(duplicates), 'invalidRows': len(rejected), 'imported': 0, 'published': 0,
              'financialCost': 0, 'mediaDownloaded': False, 'planSha256': plan_sha}
    save(output / 'result.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--max-results', type=int, default=100)
    parser.add_argument('--interval', type=float, default=3)
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()
    integer(args.max_results, 1, 500, 'max-results')
    integer(args.timeout, 5, 60, 'timeout')
    if not 2 <= args.interval <= 60:
        raise ValueError('interval must be 2–60 seconds')
    jobs = validate_plan(json.loads(args.plan.read_text(encoding='utf-8-sig')), args.max_results)
    if not args.execute:
        print(json.dumps({'mode': 'preview', 'endpoint': ENDPOINT, 'maximumResults': sum(j['limit'] for j in jobs), 'jobs': jobs, 'mediaDownloaded': False}, ensure_ascii=False, indent=2))
        return
    print(json.dumps(collect(jobs, args.output, resume=args.resume, interval=args.interval, timeout=args.timeout), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
