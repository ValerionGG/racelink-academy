"""Preview one prepared Apify batch; --start explicitly permits one capped run.

No scheduler, automatic retries, cookie loading, or publication. A pending receipt
blocks resubmission after an uncertain network outcome to prevent duplicate fees.
Plans restricted to free credits can be previewed, but cannot be executed until
account credit verification is implemented.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

BASE = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = BASE/'collection/social-acquisition/plan.json'
ACTORS = {'clockworks/tiktok-scraper', 'apify/instagram-reel-scraper', 'apify/instagram-scraper'}
INPUT_FIELDS = {
    'clockworks/tiktok-scraper': {
        'shouldDownloadVideos','shouldDownloadCovers','shouldDownloadSlideshowImages',
        'shouldDownloadAvatars','shouldDownloadMusicCovers','downloadSubtitlesOptions',
        'aiVideoDescription','aiVideoSummary','commentsPerPost','maxFollowersPerProfile',
        'maxFollowingPerProfile','scrapeRelatedVideos','scrapeAdditionalAuthorMeta',
        'profiles','resultsPerPage','profileScrapeSections','profileSorting',
        'searchQueries','searchSection'},
    'apify/instagram-reel-scraper': {
        'username','resultsLimit','includeSharesCount','includeTranscript',
        'includeDownloadedVideo','onlyPostsNewerThan','skipPinnedPosts','skipTrialReels'},
    'apify/instagram-scraper': {
        'search','searchType','searchLimit','resultsType','resultsLimit','addParentData',
        'directUrls','onlyPostsNewerThan'},
}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('API redirect refused; inspect the endpoint before retrying.')

def prepared_request(plan_path, batch_id):
    plan_path = Path(plan_path).resolve()
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    matches = [job for job in plan['jobs'] if job['id'] == batch_id]
    if len(matches) != 1 or not re.fullmatch(r'[a-z0-9-]+', batch_id):
        raise ValueError('Unknown or ambiguous batch ID')
    job = matches[0]
    if job['actor'] not in ACTORS:
        raise ValueError('Actor is outside the reviewed set')
    source = (plan_path.parent/job['input_file']).resolve()
    if not source.is_relative_to(plan_path.parent):
        raise ValueError('Input must stay inside the plan directory')
    body = source.read_bytes()
    if hashlib.sha256(body).hexdigest() != job['input_sha256']:
        raise ValueError('Input changed after plan review; rebuild and review the plan')
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError('Actor input must be a JSON object')
    # This launcher accepts only reviewed public metadata inputs. Matching a new
    # hash alone must not enable credentials, stories or a comments-only crawl.
    if job['actor'] == 'apify/instagram-scraper' and payload.get('resultsType', 'posts') not in {'posts','reels','details'}:
        raise ValueError('Only public post, reel or profile metadata is allowed; no comments or stories')
    unknown_fields = set(payload) - INPUT_FIELDS[job['actor']]
    if unknown_fields:
        raise ValueError('Unreviewed input fields are not allowed: '+', '.join(sorted(unknown_fields)))
    if payload.get('profileScrapeSections', ['videos']) != ['videos']:
        raise ValueError('Only public profile videos are part of this plan')
    for key in ('directUrls','username'):
        targets = payload.get(key, [])
        if not isinstance(targets, list):
            raise ValueError(key+' must be a list of public profile or media references')
        for target in targets:
            if isinstance(target, str) and target.startswith(('http://','https://')):
                parsed = urllib.parse.urlsplit(target)
                first_path = parsed.path.strip('/').split('/')[0].lower()
                if first_path in {'stories','direct','accounts'} or parsed.username or parsed.password:
                    raise ValueError('Private, login or story URLs are not part of this plan')
    # Deny paid enrichment and media requests even if an input hash is edited.
    forbidden = ['includeTranscript','includeDownloadedVideo','includeSharesCount',
        'shouldDownloadVideos','shouldDownloadCovers','shouldDownloadSlideshowImages',
        'shouldDownloadAvatars','shouldDownloadMusicCovers','aiVideoDescription','aiVideoSummary',
        'commentsPerPost','topLevelCommentsPerPost','maxRepliesPerComment',
        'maxFollowersPerProfile','maxFollowingPerProfile']
    if any(payload.get(key) for key in forbidden):
        raise ValueError('Media, comments or paid enrichments are not part of this plan')
    if payload.get('downloadSubtitlesOptions', 'NEVER_DOWNLOAD_SUBTITLES') != 'NEVER_DOWNLOAD_SUBTITLES':
        raise ValueError('Subtitle acquisition needs a separate reviewed workflow')
    cap = float(job['request']['query']['maxTotalChargeUsd'])
    if not math.isfinite(cap) or not 0 < cap <= 1:
        raise ValueError('Each reviewed batch must have a positive charge cap at most 1 USD')
    query = urllib.parse.urlencode({'maxTotalChargeUsd':cap,'timeout':600,'restartOnError':'false'})
    url = 'https://api.apify.com/v2/actors/'+job['actor'].replace('/','~')+'/runs?'+query
    preview = {'batch':batch_id,'actor':job['actor'],'maximum_charge_usd':cap,
        'result_upper_target':job['result_upper_target'],'method':'POST','url':url,
        'input_sha256':job['input_sha256'],'input':payload,'executed':False}
    policy = plan.get('spending_policy', {})
    if not isinstance(policy, dict):
        raise ValueError('spending_policy must be a JSON object')
    if policy.get('mode') == 'free_credits_only':
        preview['spending_policy_mode'] = 'free_credits_only'
        preview['execution_blocked_reason'] = 'free_credit_verification_not_implemented'
    return preview, body

def submit(plan_path, batch_id, receipts_dir, budget_usd):
    preview, body = prepared_request(plan_path, batch_id)
    # A declared budget or a manifest attestation cannot establish that credits
    # are free. Fail before reading credentials, creating receipts or requesting
    # an Actor run; there is deliberately no override for this policy.
    if preview.get('spending_policy_mode') == 'free_credits_only':
        raise ValueError('Free-credit verification is not implemented; execution of '
                         'free_credits_only plans is blocked. --budget-usd cannot override this policy.')
    if not math.isfinite(budget_usd) or budget_usd < preview['maximum_charge_usd']:
        raise ValueError('Explicit budget must cover the batch charge cap')
    token = os.environ.get('APIFY_TOKEN')
    if not token:
        raise ValueError('APIFY_TOKEN missing. Configure it locally; never paste it in chat or commit it.')
    receipts = Path(receipts_dir).resolve()
    receipts.mkdir(parents=True, exist_ok=True)
    receipt = receipts/(batch_id+'.json')
    state = {key:value for key,value in preview.items() if key != 'input'}
    state.update(status='submission_pending', submitted_at=datetime.now(timezone.utc).isoformat())
    # Exclusive create: never automatically retry a potentially charged POST.
    with receipt.open('x', encoding='utf-8') as output:
        json.dump(state, output, ensure_ascii=False, indent=2)
    request = urllib.request.Request(preview['url'], data=body, method='POST', headers={
        'Authorization':'Bearer '+token,'Content-Type':'application/json',
        'User-Agent':'racelink-educational-acquisition/1.0'})
    try:
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(request, timeout=45) as response:
            data = json.load(response)['data']
        if not data.get('id'):
            raise ValueError('Missing run ID in API response')
        state.update(executed=True,status=data.get('status','UNKNOWN'),run_id=data['id'],
            dataset_id=data.get('defaultDatasetId'),
            run_url='https://console.apify.com/actors/runs/'+data['id'])
    except Exception:
        state.update(status='outcome_unknown_do_not_resubmit',
            recovery='Check Apify Runs before any new submission; this receipt intentionally blocks a retry.')
        receipt.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        raise RuntimeError('Run outcome not confirmed. Inspect the receipt and Apify Runs; no automatic retry.') from None
    receipt.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    return state

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,default=DEFAULT_PLAN)
    parser.add_argument('--batch',required=True)
    parser.add_argument('--start',action='store_true',help='Start exactly one potentially charged run')
    parser.add_argument('--budget-usd',type=float)
    parser.add_argument('--receipts',type=Path)
    args = parser.parse_args()
    try:
        if args.start:
            if args.budget_usd is None or args.receipts is None:
                parser.error('--start requires --budget-usd and --receipts')
            result = submit(args.plan,args.batch,args.receipts,args.budget_usd)
        else:
            result,_ = prepared_request(args.plan,args.batch)
        print(json.dumps(result,ensure_ascii=True,indent=2))
    except (ValueError,RuntimeError,FileExistsError) as exc:
        parser.exit(2,str(exc)+'\n')

if __name__ == '__main__':
    main()
