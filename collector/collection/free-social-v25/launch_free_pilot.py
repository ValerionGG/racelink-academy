#!/usr/bin/env python3
"""Preview by default; explicitly execute bounded Apify Free-plan profile batches.

No login discovery, subscriptions, billing changes, media downloads, automatic
POST retries, or database writes. Results are public post metadata for review.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import datetime as dt
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

import verify_apify_free_credits as budget

HERE = Path(__file__).resolve().parent
PLAN = HERE / 'pilot' / 'plan.json'
STATE = HERE / 'pilot' / 'runtime'
UI_RECONCILIATION_FLAG = HERE / 'UI_RUNS_UNRECONCILED'
API = 'https://api.apify.com/v2/'
CAP = Decimal('0.50')
MAX_BYTES = 4 * 1024 * 1024
TERMINAL = {'SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED'}
STATUSES = TERMINAL | {'READY', 'RUNNING', 'TIMING-OUT', 'ABORTING'}
ACTORS = {
    'clockworks/tiktok-scraper': {'platform': 'tiktok', 'event': 'result',
        'price': Decimal('0.0037'), 'memory': 4096,
        'false': ['shouldDownloadVideos', 'shouldDownloadCovers', 'shouldDownloadSlideshowImages',
                  'shouldDownloadAvatars', 'shouldDownloadMusicCovers', 'aiVideoDescription',
                  'aiVideoSummary', 'scrapeRelatedVideos', 'scrapeAdditionalAuthorMeta'],
        'zero': ['commentsPerPost', 'maxFollowersPerProfile', 'maxFollowingPerProfile']},
    'apify/instagram-reel-scraper': {'platform': 'instagram', 'event': 'reel',
        'price': Decimal('0.0026'), 'memory': 1024,
        'false': ['includeSharesCount', 'includeTranscript', 'includeDownloadedVideo'], 'zero': []},
}
# Apify's dataset `fields` selects top-level keys only; nested paths are ignored.
# These two objects stay in memory and safe_post_metadata persists only approved
# leaves (public creator handle, duration and image URL), never full profiles.
# Contract: https://docs.apify.com/storage/dataset
DATASET_FIELDS = ('id,text,caption,title,url,webVideoUrl,shortCode,timestamp,createTimeISO,'
    'createTime,hashtags,videoDuration,videoMeta,authorMeta,ownerUsername,'
    'diggCount,shareCount,commentCount,playCount,videoViewCount,videoPlayCount,likesCount,commentsCount,'
    'displayUrl,thumbnailUrl,thumbnail,cover,type,isVideo,isSlideshow,isPhoto,'
    'isSponsored,isAd,paidPartnership,isPaidPartnership,isPrivate,private,is_private,availability,'
    'is_video,is_photo,is_slideshow,isStory,is_story,isAIGC,isAiGenerated,is_aigc,is_ai_generated')


class PilotError(Exception):
    """Messages are fixed diagnostics, never remote error bodies or credentials."""


def now():
    return dt.datetime.now(dt.timezone.utc)


def require_ui_runs_reconciled():
    # Explicit local operator flag: never inspect browser state or external ledgers.
    # Its contents are unnecessary and may contain private operator annotations.
    if UI_RECONCILIATION_FLAG.exists() or UI_RECONCILIATION_FLAG.is_symlink():
        raise PilotError('UI runs are not reconciled; new starts are blocked by UI_RUNS_UNRECONCILED')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def save(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        with path.open('xb') as output:
            output.write(encoded(value))
            output.flush()
            os.fsync(output.fileno())
    else:
        temporary = path.with_suffix(path.suffix + '.tmp')
        with temporary.open('wb') as output:
            output.write(encoded(value))
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(path)


def load(path):
    if path.stat().st_size > MAX_BYTES:
        raise PilotError('Local configuration or receipt exceeds the size limit')
    return json.loads(path.read_text(encoding='utf-8'))


def api_json(path, token=None, method='GET', body=None):
    # Callers supply only fixed endpoint templates and validated IDs.
    if not re.fullmatch(r'[A-Za-z0-9~_/.,?=&%+:-]+', path) or path.startswith('/'):
        raise PilotError('Unreviewed API path')
    if method not in {'GET', 'POST'} or (method == 'POST' and not re.fullmatch(r'acts/[A-Za-z0-9~_-]+/runs\?.+', path)):
        raise PilotError('Unreviewed API operation')
    headers = {'Accept': 'application/json', 'User-Agent': 'RacelinkFreePilot/1.0'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if body is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(API + path, method=method, data=body, headers=headers)
    try:
        with budget.SAFE_OPENER(req, timeout=25) as response:
            if response.status not in {200, 201}:
                raise PilotError('Apify returned a non-success status')
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise PilotError('Apify response exceeds 4 MiB; no retry')
        return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise PilotError('Apify HTTP ' + str(exc.code) + '; no automatic retry') from None
    except (urllib.error.URLError, OSError, TimeoutError):
        raise PilotError('Apify network failure; no automatic retry') from None
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise PilotError('Apify returned invalid JSON') from None


def selected_jobs(plan_path, batches=None, allow_extension=False):
    plan_path = Path(plan_path).resolve()
    plan = load(plan_path)
    policy = plan['spending_policy']
    if (policy.get('mode') != 'free_credits_only' or policy.get('max_out_of_pocket_usd') != 0
        or policy.get('paid_balance_allowed') is not False or policy.get('subscriptions_allowed') is not False
        or policy.get('top_up_allowed') is not False or policy.get('explicit_cli_live_guard') is not True):
        raise PilotError('Plan does not enforce the reviewed free-credits-only policy')
    ids = batches or plan['pilot']['initial_jobs']
    if not ids or len(ids) > 14 or len(set(ids)) != len(ids):
        raise PilotError('Select one to fourteen distinct prepared batches')
    jobs = []
    for batch in ids:
        if not re.fullmatch(r'fr-(?:tiktok|instagram)-[0-9]{2}', batch):
            raise PilotError('Invalid batch ID')
        matches = [job for job in plan['jobs'] if job['id'] == batch]
        if len(matches) != 1:
            raise PilotError('Unknown or ambiguous batch')
        job = dict(matches[0])
        actor = job['actor']
        if actor not in ACTORS:
            raise PilotError('Actor outside the two reviewed providers')
        if job['stage'] != 'pilot' and not allow_extension:
            raise PilotError('Review pilot yield first; extension requires --extend-after-review')
        if Decimal(str(job['request']['query']['maxTotalChargeUsd'])) != CAP:
            raise PilotError('Every batch must have the fixed 0.50 USD maximum charge')
        path = (plan_path.parent / job['input_file']).resolve()
        if not path.is_relative_to(plan_path.parent):
            raise PilotError('Input must remain inside the pilot directory')
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != job['input_sha256']:
            raise PilotError('Input hash differs from the reviewed plan')
        payload = json.loads(body)
        review_input(actor, payload, job['result_upper_target'])
        if not re.fullmatch(r'\d+\.\d+\.\d+', job['reviewed_build']):
            raise PilotError('Reviewed build number missing')
        job.update(input=payload, body=body)
        jobs.append(job)
    return plan, jobs


def review_input(actor, payload, target):
    config = ACTORS[actor]
    if isinstance(target, bool) or not isinstance(target, int) or not 1 <= target <= 100:
        raise PilotError('A batch may target at most 100 public posts')
    if not isinstance(payload, dict):
        raise PilotError('Actor input must be an object')
    expected = set(config['false'] + config['zero'])
    for field in config['false']:
        if payload.get(field) is not False:
            raise PilotError('Media, comments and enrichment options must be explicitly disabled')
    for field in config['zero']:
        if type(payload.get(field)) is not int or payload[field] != 0:
            raise PilotError('Follower and comment counts must be explicitly zero')
    if config['platform'] == 'tiktok':
        expected.update(['profiles', 'resultsPerPage', 'profileScrapeSections', 'profileSorting', 'downloadSubtitlesOptions'])
        profiles = payload.get('profiles')
        valid = (payload.get('resultsPerPage') == target and payload.get('profileScrapeSections') == ['videos']
                 and payload.get('profileSorting') == 'latest'
                 and payload.get('downloadSubtitlesOptions') == 'NEVER_DOWNLOAD_SUBTITLES')
    else:
        expected.update(['username', 'resultsLimit'])
        profiles = payload.get('username')
        valid = payload.get('resultsLimit') == target
    if (set(payload) != expected or not valid or not isinstance(profiles, list) or len(profiles) != 1
        or not isinstance(profiles[0], str) or not re.fullmatch(r'[a-zA-Z0-9_.]{1,40}', profiles[0])):
        raise PilotError('Only one reviewed public profile and bounded metadata input are allowed')


def public_actor_review(job):
    actor = job['actor'].replace('/', '~')
    data = api_json('acts/' + actor).get('data', {})
    baseline = load(HERE / (actor + '.json'))['data']
    if (data.get('id') != baseline['id'] or data.get('isPublic') is not True
        or data.get('isDeprecated') is True or data.get('actorPermissionLevel') != baseline.get('actorPermissionLevel')):
        raise PilotError('Actor identity, visibility or permissions changed')
    latest = data.get('taggedBuilds', {}).get('latest', {})
    if latest.get('buildNumber') != job['reviewed_build']:
        raise PilotError('Actor build changed; re-review its public schema before execution')
    def active_price(source):
        prices = []
        for price in source.get('pricingInfos', []):
            started = price.get('startedAt')
            if started and dt.datetime.fromisoformat(started.replace('Z', '+00:00')) <= now():
                prices.append(price)
        if not prices:
            raise PilotError('No current public pricing information')
        return max(prices, key=lambda item: item['startedAt'])
    price, prior = active_price(data), active_price(baseline)
    if price.get('pricingModel') != 'PAY_PER_EVENT' or price.get('pricingPerEvent') != prior.get('pricingPerEvent'):
        raise PilotError('Provider event pricing changed; no automatic repricing')
    minimum = budget.number(price.get('minimalMaxTotalChargeUsd'), 'minimalMaxTotalChargeUsd')
    if minimum > CAP:
        raise PilotError('Provider minimum charge cap exceeds 0.50 USD')
    events = price['pricingPerEvent']['actorChargeEvents']
    config = ACTORS[job['actor']]
    unit = budget.number(events[config['event']]['eventTieredPricingUsd']['FREE']['tieredEventPriceUsd'], 'result_event')
    startup = budget.number(events['actor-start']['eventTieredPricingUsd']['FREE']['tieredEventPriceUsd'], 'startup_event')
    if unit > config['price'] or startup > Decimal('0.001'):
        raise PilotError('Base event prices exceed the reviewed ceilings')
    schema_doc = api_json('actors/' + actor + '/builds/default/openapi.json')
    schema = schema_doc['components']['schemas']['inputSchema']
    local_schema = load(HERE / (actor + '-input-schema.json'))
    if digest(schema) != digest(local_schema):
        raise PilotError('Public input schema changed; re-review required')
    def no_external_refs(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {'$ref', '$dynamicRef'} and (not isinstance(child, str) or not child.startswith('#')):
                    raise PilotError('External schema references are disabled')
                no_external_refs(child)
        elif isinstance(value, list):
            for child in value:
                no_external_refs(child)
    no_external_refs(schema)
    try:
        import jsonschema
        validator = jsonschema.validators.validator_for(schema)
        validator.check_schema(schema)
        validator(schema).validate(job['input'])
    except ImportError:
        raise PilotError('Install the local jsonschema dependency before execution') from None
    except Exception:
        raise PilotError('Actor input failed current public schema validation') from None
    return {'actor_id': data['id'], 'build': job['reviewed_build'], 'schema_sha256': digest(schema),
            'pricing_sha256': digest(price['pricingPerEvent']), 'minimum_cap_usd': float(minimum),
            'result_event_usd': float(unit), 'startup_event_usd': float(startup),
            'estimated_base_cost_usd': float(startup + unit * job['result_upper_target'])}


@contextmanager
def exclusive_runtime(state_dir):
    state_dir.mkdir(parents=True, exist_ok=True)
    lock = state_dir / 'launcher.lock'
    try:
        save(lock, {'created_at': now().isoformat(), 'purpose': 'sequential free pilot'}, exclusive=True)
    except FileExistsError:
        raise PilotError('Another launcher or an unreconciled crash lock exists; do not launch concurrently') from None
    try:
        yield
    finally:
        lock.unlink()


def budget_before_start(token, state_dir):
    fields = {key: budget.fetch_projected(key, token) for key in budget.ENDPOINTS}
    report = budget.assess(fields, CAP)
    if not report['eligible_for_operator_review']:
        raise PilotError('Free-plan budget check blocked: ' + ', '.join(report['reasons']))
    cycle = fields['limits']['cycle']
    effective = Decimal(str(report['observed_usage_usd']))
    for receipt_path in state_dir.glob('fr-*.json'):
        receipt = load(receipt_path)
        if receipt.get('status') in {'submission_pending', 'outcome_unknown_do_not_resubmit'}:
            raise PilotError('An uncertain previous start must be reconciled before any new batch')
        if receipt.get('cycle') == cycle:
            effective = max(effective, budget.number(receipt.get('reserved_effective_usage_after_start_usd'), 'reserved_usage'))
    available = Decimal(str(report['conservative_allowance_usd'])) - budget.RESERVE_USD - effective
    if available < CAP:
        raise PilotError('Conservative persistent run reservations leave less than 0.50 USD of free allowance')
    report.update(persistent_effective_usage_usd=float(effective),
                  available_after_persistent_reservations_usd=float(available))
    return report


def validate_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9]{10,40}', value):
        raise PilotError('Invalid run or dataset ID')
    return value


def project_run(data, expected_actor_id, expected_run_id=None):
    if not isinstance(data, dict) or data.get('actId') != expected_actor_id:
        raise PilotError('Run actor identity does not match the reviewed Actor')
    run_id = validate_id(data.get('id'))
    if expected_run_id and run_id != expected_run_id:
        raise PilotError('Run ID changed')
    status = data.get('status')
    if status not in STATUSES:
        raise PilotError('Unknown run status')
    options = data.get('options', {})
    if budget.number(options.get('maxTotalChargeUsd'), 'run_charge_cap') > CAP:
        raise PilotError('Returned run cap exceeds the reviewed ceiling')
    result = {'run_id': run_id, 'run_status': status,
              'dataset_id': validate_id(data.get('defaultDatasetId'))}
    if data.get('usageTotalUsd') is not None:
        result['reported_usage_total_usd'] = float(budget.number(data['usageTotalUsd'], 'usageTotalUsd'))
    return result


def safe_thumbnail(value, platform):
    if not isinstance(value, str) or not 1 <= len(value) <= 5000:
        return None
    try:
        parsed = urllib.parse.urlsplit(value)
        host = (parsed.hostname or '').lower()
        allowed = {'instagram': ('cdninstagram.com', 'fbcdn.net', 'instagram.com'),
                   'tiktok': ('tiktokcdn.com', 'tiktokcdn-eu.com', 'tiktokcdn-us.com', 'tiktok.com',
                              'byteoversea.com', 'ibytedtos.com', 'ibyteimg.com', 'byteimg.com', 'muscdn.com')}
        if (parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port
            or not any(host == domain or host.endswith('.' + domain) for domain in allowed[platform])):
            return None
        if re.search(r'\.(?:mp4|webm|m3u8|mpd|mov|m4a)(?:$|[~/])', parsed.path, re.I):
            return None
        keys = [key.lower() for key, value in urllib.parse.parse_qsl(parsed.query)]
        if any(re.search(r'token|password|credential|authorization|cookie|session|secret|api[-_]?key', key) for key in keys):
            return None
        if any(ord(char) < 33 for char in value):
            return None
        return urllib.parse.urlunsplit(('https', host, parsed.path, parsed.query, ''))
    except ValueError:
        return None


def metadata_flag(value):
    """Unknown restriction encodings must not become an assertion of public video."""
    if value is None or value == '':
        return None
    if type(value) is bool:
        return value
    if type(value) in {int, float} and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {'true', '1', 'yes'}:
            return True
        if text in {'false', '0', 'no'}:
            return False
    raise PilotError('Unknown source restriction flag encoding; review required before export')


def safe_post_metadata(row, platform):
    """Keep original useful post fields, discard nested profiles/media/comments."""
    if not isinstance(row, dict):
        raise PilotError('Dataset item must be an object')
    result = {}
    for key in ('id', 'shortCode', 'createTimeISO', 'timestamp'):
        value = row.get(key)
        if isinstance(value, (str, int)) and not isinstance(value, bool):
            result[key] = str(value)[:200]
    for key in ('text', 'caption', 'title'):
        if isinstance(row.get(key), str):
            # Retain source wording, except contact strings unnecessary for tutorials.
            value = row[key][:12000]
            value = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[contact retiré]', value)
            value = re.sub(r'(?<!\w)(?:\+33|0)[1-9](?:[ .-]?\d{2}){4}(?!\d)', '[contact retiré]', value)
            result[key] = value
            if value != row[key]:
                result['source_text_trimmed_or_contact_redacted'] = True
    for key in ('url', 'webVideoUrl'):
        value = row.get(key)
        if isinstance(value, str):
            parsed = urllib.parse.urlsplit(value)
            host = parsed.hostname or ''
            if (parsed.scheme == 'https' and not parsed.username and not parsed.password
                and ((platform == 'tiktok' and host in {'www.tiktok.com', 'tiktok.com'}
                      and re.fullmatch(r'/@[\w.]+/video/\d+/?', parsed.path))
                     or (platform == 'instagram' and host in {'www.instagram.com', 'instagram.com'}
                         and re.fullmatch(r'/(?:p|reel|reels)/[A-Za-z0-9_-]+/?', parsed.path)))):
                result[key] = urllib.parse.urlunsplit(('https', host, parsed.path, '', ''))
    profile = (row.get('ownerUsername') if platform == 'instagram' else
               row.get('authorMeta', {}).get('name') if isinstance(row.get('authorMeta'), dict) else row.get('authorMeta.name'))
    if isinstance(profile, str) and re.fullmatch(r'[\w.]{1,40}', profile):
        result['source_creator_handle'] = profile
        result['creator'] = profile  # PUBLIC_EXPORT generic schema.
        result['uploader'] = profile  # Direct bulk_ingest adapter.
        if platform == 'instagram':
            result['ownerUsername'] = profile
    tags = row.get('hashtags', [])
    if isinstance(tags, list):
        result['hashtags'] = [tag.lstrip('#') for item in tags[:100]
            for tag in [item if isinstance(item, str) else item.get('name') if isinstance(item, dict) else None]
            if isinstance(tag, str) and re.fullmatch(r'#?[\w]{1,100}', tag)]
    for key in ('createTime', 'videoDuration', 'diggCount', 'shareCount', 'commentCount',
                'playCount', 'videoViewCount', 'videoPlayCount', 'likesCount', 'commentsCount'):
        value = row.get(key)
        if type(value) in {int, float} and 0 <= value <= 10**16:
            result[key] = value
    if isinstance(row.get('videoMeta'), dict) and type(row['videoMeta'].get('duration')) in {int, float}:
        value = row['videoMeta']['duration']
        if 0 <= value <= 100000:
            result['duration_seconds'] = value
    elif type(row.get('videoDuration')) in {int, float} and 0 <= row['videoDuration'] <= 100000:
        result['duration_seconds'] = row['videoDuration']
    elif type(row.get('videoMeta.duration')) in {int, float} and 0 <= row['videoMeta.duration'] <= 100000:
        result['duration_seconds'] = row['videoMeta.duration']
    if 'duration_seconds' in result:
        result['duration'] = result['duration_seconds']
    if not result.get('url') and result.get('webVideoUrl'):
        result['url'] = result['webVideoUrl']
    if not result.get('caption') and result.get('text'):
        result['caption'] = result['text']
    if result.get('caption'):
        result['caption_status'] = 'provider_exported_source_caption_not_independently_verified'
    if result.get('createTimeISO') or result.get('timestamp'):
        result['published_at'] = result.get('createTimeISO') or result.get('timestamp')
    nested = row.get('videoMeta') if isinstance(row.get('videoMeta'), dict) else {}
    for key, value in [(key, row.get(key)) for key in ('displayUrl', 'thumbnailUrl', 'thumbnail', 'cover')] + [
            ('videoMeta.coverUrl', nested.get('coverUrl') or row.get('videoMeta.coverUrl')),
            ('videoMeta.cover', nested.get('cover') or row.get('videoMeta.cover'))]:
        thumbnail = safe_thumbnail(value, platform)
        if thumbnail:
            result.update(thumbnail_url=thumbnail, thumbnail=thumbnail, thumbnail_source_field=key,
                          thumbnail_status='provider_public_image_url_may_expire_not_downloaded')
            break
    groups = {'isPrivate': ('isPrivate', 'private', 'is_private', 'authorMeta.privateAccount'),
              'isSponsored': ('isSponsored', 'isAd', 'paidPartnership', 'isPaidPartnership'),
              'isPhoto': ('isPhoto', 'is_photo', 'isSlideshow', 'is_slideshow'),
              'isStory': ('isStory', 'is_story'),
              'is_aigc': ('isAIGC', 'isAiGenerated', 'is_aigc', 'is_ai_generated')}
    for destination, keys in groups.items():
        values = [metadata_flag(row[key]) for key in keys if key in row]
        author = row.get('authorMeta')
        if destination == 'isPrivate' and isinstance(author, dict) and 'privateAccount' in author:
            values.append(metadata_flag(author['privateAccount']))
        values = [value for value in values if value is not None]
        if values:
            result[destination] = any(values)  # A restrictive declaration wins a contradictory one.
    video_values = [metadata_flag(row[key]) for key in ('isVideo', 'is_video') if key in row]
    video_values = [value for value in video_values if value is not None]
    if video_values:
        result['is_video'] = all(video_values)  # Explicit non-video must never disappear.
        result['isVideo'] = result['is_video']
    availability = row.get('availability')
    if availability not in (None, ''):
        if not isinstance(availability, str) or availability.lower() not in {
                'public', 'unlisted', 'private', 'premium_only', 'subscriber_only', 'needs_auth'}:
            raise PilotError('Unknown source availability declaration; review required')
        result['availability'] = availability.lower()
    media_type = row.get('type')
    known_types = {'VIDEO': 'VIDEO', 'GRAPHVIDEO': 'VIDEO', 'REEL': 'VIDEO', 'REELS': 'VIDEO',
                   'IMAGE': 'IMAGE', 'PHOTO': 'IMAGE', 'GRAPHIMAGE': 'IMAGE', 'SLIDESHOW': 'IMAGE',
                   'CAROUSEL': 'CAROUSEL', 'SIDECAR': 'SIDECAR', 'GRAPHSIDECAR': 'SIDECAR', 'STORY': 'STORY'}
    if media_type not in (None, ''):
        if not isinstance(media_type, str) or media_type.upper() not in known_types:
            raise PilotError('Unknown source media type; review required before export')
        media_type = known_types[media_type.upper()]
    if media_type == 'STORY':
        result['isStory'] = True
    if 'isStory' in result:
        result['is_story'] = result['isStory']  # PUBLIC_EXPORT generic accepts this source alias.
    if result.get('isPhoto') is True:
        result.update(is_video=False, is_photo=True, media_type='IMAGE')
    elif media_type in {'IMAGE', 'CAROUSEL', 'SIDECAR'}:
        result.update(is_video=False, media_type=media_type)
    elif result.get('is_video') is False:
        result['is_video'] = False
    else:
        result['media_type'] = 'VIDEO'  # Two reviewed Actors are public video/reel collectors.
    return result


def verify_export_progress(state, state_dir):
    offset = state.get('exported_offset', 0)
    maximum = state['result_upper_target']
    pages = state.get('export_pages', [])
    if type(offset) is not int or not 0 <= offset <= maximum or not isinstance(pages, list) or len(pages) > 3:
        raise PilotError('Invalid persisted export progress')
    expected = 0
    export_dir = state_dir / 'review' / state['batch']
    for entry in pages:
        if (not isinstance(entry, dict) or not re.fullmatch(r'page-\d{6}\.json', str(entry.get('file', '')))
            or entry.get('offset') != expected or type(entry.get('count')) is not int or not 0 <= entry['count'] <= 50):
            raise PilotError('Invalid persisted export page sequence')
        path = export_dir / entry['file']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry.get('sha256'):
            raise PilotError('Export page missing or changed; restore evidence before resume')
        page = load(path)
        if (not isinstance(page.get('items'), list) or len(page['items']) != entry['count']
            or page.get('provenance', {}).get('offset') != expected
            or page.get('sha256_items') != digest(page['items'])):
            raise PilotError('Export page contents do not match the recorded progress')
        expected += entry['count']
    if expected != offset:
        raise PilotError('Export offset lacks matching hashed pages')
    if state.get('status') == 'finished_for_review':
        path = export_dir / 'manifest.json'
        if (state.get('exported_count') != offset or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != state.get('public_export_manifest_sha256')):
            raise PilotError('Completed export manifest missing or changed; no successful resume')


def export_dataset(state, receipt_path, token, state_dir):
    run_id, dataset_id = validate_id(state['run_id']), validate_id(state['dataset_id'])
    export_dir = state_dir / 'review' / state['batch']
    maximum = state['result_upper_target']
    verify_export_progress(state, state_dir)
    offset = state.get('exported_offset', 0)
    while offset < maximum:
        limit = min(50, maximum - offset)
        query = urllib.parse.urlencode({'format': 'json', 'offset': offset, 'limit': limit,
                                       'fields': DATASET_FIELDS, 'clean': 'false'})
        rows = api_json('datasets/' + dataset_id + '/items?' + query, token)
        if not isinstance(rows, list) or len(rows) > limit:
            raise PilotError('Unexpected dataset page shape or page size')
        projected = [safe_post_metadata(row, state['platform']) for row in rows]
        page = {'provenance': {'provider': 'apify', 'actor': state['actor'], 'run_id': run_id,
                'dataset_id': dataset_id, 'offset': offset, 'limit': limit, 'fetched_at': now().isoformat(),
                'scope': 'public_post_metadata_for_review', 'video_license': 'unknown',
                'transcript_obtained': False, 'availability_rechecked_on_platform': False},
                'items': projected, 'sha256_items': digest(projected)}
        page_path = export_dir / ('page-' + str(offset).zfill(6) + '.json')
        save(page_path, page)
        state.setdefault('export_pages', []).append({'file': page_path.name,
            'sha256': hashlib.sha256(page_path.read_bytes()).hexdigest(), 'offset': offset, 'count': len(rows)})
        offset += len(rows)
        state.update(exported_offset=offset, export_status='partial_metadata_for_review')
        save(receipt_path, state)
        if len(rows) < limit:
            break
    manifest = {'version': 1, 'kind': 'PUBLIC_EXPORT', 'source': {
        'name': 'Apify public ' + state['platform'] + ' video metadata', 'kind': 'provider_export',
        'source_url': 'https://apify.com/' + state['actor'], 'captured_at': now().isoformat(),
        'evidence_reference': 'Apify run ' + run_id + '; hashed source pages; native caption supplied by provider; audio and licence unverified'},
        'pages': [{'file': page['file'], 'sha256': page['sha256'], 'format': 'json', 'schema': 'generic'}
                  for page in state.get('export_pages', [])]}
    save(export_dir / 'manifest.json', manifest)
    state.update(export_status='bounded_metadata_for_review', status='finished_for_review',
                 exported_count=offset, export_upper_limit=maximum,
                 export_may_be_truncated_at_target=(offset == maximum), database_written=False,
                 public_export_manifest='review/' + state['batch'] + '/manifest.json',
                 public_export_manifest_sha256=hashlib.sha256((export_dir / 'manifest.json').read_bytes()).hexdigest())
    save(receipt_path, state)
    return state


def finish_or_wait(state, receipt_path, token, state_dir, polls=12, interval=10):
    if not 1 <= polls <= 12 or not 0 <= interval <= 30:
        raise PilotError('Polling is bounded to twelve requests with at most 30 seconds between requests')
    for attempt in range(polls):
        if state['run_status'] in TERMINAL:
            return export_dataset(state, receipt_path, token, state_dir)
        if attempt:
            time.sleep(interval)
        response = api_json('actor-runs/' + validate_id(state['run_id']), token)
        state.update(project_run(response.get('data'), state['provider_review']['actor_id'], state['run_id']))
        state.update(status='run_observed', last_observed_at=now().isoformat())
        save(receipt_path, state)
    if state['run_status'] in TERMINAL:
        return export_dataset(state, receipt_path, token, state_dir)
    state.update(status='poll_window_finished_resume_required',
                 next_action='Use the same batch with --execute --resume; this never creates another run.')
    save(receipt_path, state)
    return state


def launch_one(job, token, state_dir=STATE, resume=False, polls=12, interval=10):
    receipt_path = state_dir / (job['id'] + '.json')
    if receipt_path.exists():
        state = load(receipt_path)
        if not resume:
            raise PilotError('Batch already has a receipt; use --resume to read the existing run, never resubmit')
        if not state.get('run_id') or state.get('status') in {'submission_pending', 'outcome_unknown_do_not_resubmit'}:
            raise PilotError('Start outcome is uncertain; reconcile Apify Runs manually, no automatic repost')
        if (state.get('input_sha256') != job['input_sha256'] or state.get('actor') != job['actor']
            or state.get('batch') != job['id'] or state.get('platform') != ACTORS[job['actor']]['platform']
            or state.get('result_upper_target') != job['result_upper_target']):
            raise PilotError('Receipt identity does not match the prepared batch')
        verify_export_progress(state, state_dir)
        if state.get('status') == 'finished_for_review':
            return state
        return finish_or_wait(state, receipt_path, token, state_dir, polls, interval)
    if resume:
        raise PilotError('No receipt exists to resume; --resume never starts a run')
    require_ui_runs_reconciled()
    provider = public_actor_review(job)
    # This is the last network check before POST: fresh Free plan + idle account.
    report = budget_before_start(token, state_dir)
    require_ui_runs_reconciled()  # Recheck if the UI operator flagged activity during live reads.
    query = urllib.parse.urlencode({'maxTotalChargeUsd': '0.50', 'timeout': 600,
        'memory': ACTORS[job['actor']]['memory'], 'restartOnError': 'false', 'build': job['reviewed_build']})
    state = {'batch': job['id'], 'actor': job['actor'], 'platform': ACTORS[job['actor']]['platform'],
        'input_sha256': job['input_sha256'], 'result_upper_target': job['result_upper_target'],
        'maximum_charge_usd': .5, 'cycle': report['budget_fields']['limits']['cycle'],
        'reserved_effective_usage_after_start_usd': float(Decimal(str(report['persistent_effective_usage_usd'])) + CAP),
        'budget_check': report, 'provider_review': provider, 'status': 'submission_pending',
        'submitted_at': now().isoformat(), 'execution_mode': 'explicit_cli_free_credits_only'}
    save(receipt_path, state, exclusive=True)  # Durable before the sole POST.
    try:
        response = api_json('acts/' + job['actor'].replace('/', '~') + '/runs?' + query,
                            token, method='POST', body=job['body'])
        state.update(project_run(response.get('data'), provider['actor_id']))
        state['status'] = 'run_observed'
        save(receipt_path, state)
    except Exception:
        state.update(status='outcome_unknown_do_not_resubmit',
            next_action='Inspect Apify Runs and reconcile this receipt. Never delete it to retry.')
        save(receipt_path, state)
        raise PilotError('Start outcome is uncertain; durable receipt blocks all further new runs') from None
    return finish_or_wait(state, receipt_path, token, state_dir, polls, interval)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', action='append', help='Repeat for sequential batches; default: the two pilot profiles')
    parser.add_argument('--execute', action='store_true', help='Explicitly allow capped starts after all live Free-plan guards pass')
    parser.add_argument('--resume', action='store_true', help='Read/poll/export an existing receipt; never POST')
    parser.add_argument('--extend-after-review', action='store_true', help='Acknowledge review of pilot relevance before selecting extension profiles')
    parser.add_argument('--polls', type=int, default=12)
    args = parser.parse_args(argv)
    try:
        plan, jobs = selected_jobs(PLAN, args.batch, args.extend_after_review)
        if not 1 <= args.polls <= 12:
            raise PilotError('Select one to twelve status polls')
        if args.resume and len(jobs) != 1:
            raise PilotError('Resume exactly one named batch')
        if not args.execute:
            print(json.dumps({'mode': 'offline_preview', 'network_called': False, 'credential_read': False,
                'execution_guard_enabled': True, 'maximum_charge_per_run_usd': .5,
                'reserve_usd': .25, 'batches': [{key: value for key, value in job.items() if key != 'body'} for job in jobs],
                'next_action': 'Only --execute can request starts, after live Free-plan/budget/provider checks.'}, indent=2))
            return 0
        if not args.resume:
            require_ui_runs_reconciled()  # Before credential access, network and runtime writes.
        token = os.environ.get('APIFY_TOKEN', '').strip()
        if not token:
            raise PilotError('APIFY_TOKEN not configured; no network or run requested')
        if len(token) > 4096 or any(ord(char) < 33 or ord(char) > 126 for char in token):
            raise PilotError('Invalid APIFY_TOKEN format; no network or run requested')
        with exclusive_runtime(STATE):
            for job in jobs:
                state = launch_one(job, token, STATE, args.resume, args.polls)
                print(json.dumps({key: state.get(key) for key in ('batch', 'status', 'run_status', 'run_id',
                    'dataset_id', 'exported_count', 'maximum_charge_usd', 'export_status')}, indent=2))
                if state['status'] != 'finished_for_review':
                    return 3  # Never launch the next profile while this one is pending.
                if state.get('run_status') != 'SUCCEEDED' or not state.get('exported_count'):
                    return 3  # Inspect a failed or empty pilot before spending on another profile.
        return 0
    except (PilotError, budget.BudgetError) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc), 'database_written': False}))
        return 2
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        print(json.dumps({'status': 'blocked', 'reason': 'Invalid local configuration, receipt or API response; no automatic retry'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
