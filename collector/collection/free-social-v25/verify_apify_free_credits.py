#!/usr/bin/env python3
"""Read-only Apify Free-plan budget probe. Never starts Actors or changes billing.

Default is offline preview. --execute reads APIFY_TOKEN only, uses GET only,
and projects sensitive API responses to a strict budget-only allowlist before
returning, printing, or writing anything. Full account responses are discarded.
"""
from __future__ import annotations
import argparse
import datetime as dt
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ENDPOINTS = {
    'account': 'https://api.apify.com/v2/users/me',
    'limits': 'https://api.apify.com/v2/users/me/limits',
    'usage': 'https://api.apify.com/v2/users/me/usage/monthly',
}
MAX_RESPONSE_BYTES = 1024 * 1024
OFFICIAL_FREE_ALLOWANCE_USD = Decimal('5.00')
RESERVE_USD = Decimal('0.25')

class BudgetError(Exception):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

SAFE_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect()).open

def number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise BudgetError('Missing or invalid numeric budget field: ' + field)
    try:
        value = Decimal(str(value))
    except InvalidOperation as exc:
        raise BudgetError('Invalid numeric budget field: ' + field) from exc
    if not value.is_finite() or value < 0:
        raise BudgetError('Invalid numeric budget field: ' + field)
    return value

def project(kind, data):
    """The only boundary at which account API data leaves the fetch function."""
    if not isinstance(data, dict):
        raise BudgetError('Invalid response data object')
    if kind == 'account':
        plan = data.get('plan')
        if not isinstance(plan, dict):
            raise BudgetError('Account plan missing; an Actor-scoped token cannot establish a Free plan')
        if not isinstance(plan.get('tier'), str) or len(plan['tier']) > 30:
            raise BudgetError('Account plan tier missing')
        if not isinstance(plan.get('isEnabled'), bool) or not isinstance(data.get('isPaying'), bool):
            raise BudgetError('Account plan status missing')
        tier = plan['tier'] if plan['tier'] in {'FREE', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND'} else 'UNKNOWN'
        return {'plan_tier': tier, 'plan_enabled': plan['isEnabled'],
                'is_paying': data['isPaying'],
                'monthly_base_price_usd': float(number(plan.get('monthlyBasePriceUsd'), 'monthlyBasePriceUsd')),
                'monthly_usage_credits_usd': float(number(plan.get('monthlyUsageCreditsUsd'), 'monthlyUsageCreditsUsd'))}
    cycle_name = 'monthlyUsageCycle' if kind == 'limits' else 'usageCycle'
    cycle = data.get(cycle_name)
    if not isinstance(cycle, dict):
        raise BudgetError('Missing usage cycle')
    dates = {}
    for field in ('startAt', 'endAt'):
        value = cycle.get(field)
        try:
            parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                raise ValueError()
        except (AttributeError, TypeError, ValueError) as exc:
            raise BudgetError('Invalid usage cycle timestamp') from exc
        dates[field] = parsed.astimezone(dt.timezone.utc).isoformat()
    out = {'cycle': dates}
    if kind == 'limits':
        limits, current = data.get('limits'), data.get('current')
        if not isinstance(limits, dict) or not isinstance(current, dict):
            raise BudgetError('Missing limits/current objects')
        out.update(max_monthly_usage_usd=float(number(limits.get('maxMonthlyUsageUsd'), 'maxMonthlyUsageUsd')),
                   current_monthly_usage_usd=float(number(current.get('monthlyUsageUsd'), 'monthlyUsageUsd')),
                   active_actor_job_count=float(number(current.get('activeActorJobCount'), 'activeActorJobCount')))
    elif kind == 'usage':
        out['usage_after_discounts_usd'] = float(number(data.get('totalUsageCreditsUsdAfterVolumeDiscount'), 'totalUsageCreditsUsdAfterVolumeDiscount'))
    else:
        raise BudgetError('Unknown projection')
    return out

def fetch_projected(kind, token, opener=None):
    opener = opener or SAFE_OPENER
    request = urllib.request.Request(ENDPOINTS[kind], method='GET', headers={
        'Authorization': 'Bearer ' + token, 'Accept': 'application/json',
        'User-Agent': 'RacelinkFreeBudgetProbe/1.0'})
    try:
        with opener(request, timeout=25) as response:
            if response.status != 200:
                raise BudgetError('Budget endpoint returned a non-success status')
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise BudgetError('Budget response exceeds 1 MiB')
        value = json.loads(body)
        return project(kind, value.get('data'))
    except urllib.error.HTTPError as exc:
        # Never read or print error bodies, request headers, account fields, or token.
        raise BudgetError('Budget endpoint HTTP ' + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise BudgetError('Budget endpoint network failure; no retry or launch') from None
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        raise BudgetError('Budget endpoint returned invalid JSON') from None

def assess(projected, requested_cap=Decimal('0.50'), now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    cap = number(requested_cap, 'requested_run_cap_usd')
    if cap <= 0:
        raise BudgetError('Requested run cap must be positive')
    account, limits, usage = (projected[k] for k in ('account', 'limits', 'usage'))
    reasons = []
    if account['plan_tier'] != 'FREE' or not account['plan_enabled'] or account['is_paying'] or account['monthly_base_price_usd'] != 0:
        reasons.append('account_is_not_verified_zero_price_free_plan')
    if limits['cycle'] != usage['cycle']:
        reasons.append('usage_cycle_mismatch')
    start = dt.datetime.fromisoformat(limits['cycle']['startAt'])
    end = dt.datetime.fromisoformat(limits['cycle']['endAt'])
    if not start <= now <= end:
        reasons.append('usage_cycle_is_not_current')
    if limits['active_actor_job_count'] != 0:
        reasons.append('other_actor_jobs_are_active')
    allowance = min(OFFICIAL_FREE_ALLOWANCE_USD, Decimal(str(account['monthly_usage_credits_usd'])), Decimal(str(limits['max_monthly_usage_usd'])))
    consumed = max(Decimal(str(limits['current_monthly_usage_usd'])), Decimal(str(usage['usage_after_discounts_usd'])))
    remaining = max(Decimal('0'), allowance - consumed)
    available = max(Decimal('0'), remaining - RESERVE_USD)
    if cap > available:
        reasons.append('insufficient_verified_free_allowance_after_reserve')
    return {'mode': 'free_credits_only', 'read_only': True, 'checked_at': now.isoformat(),
            'expires_at': (now + dt.timedelta(minutes=5)).isoformat(),
            'eligible_for_operator_review': not reasons, 'execution_authorized': False,
            'execution_guard_enabled': True, 'reasons': reasons,
            'requested_run_cap_usd': float(cap), 'conservative_allowance_usd': float(allowance),
            'observed_usage_usd': float(consumed), 'estimated_remaining_free_plan_allowance_usd': float(remaining),
            'reserve_usd': float(RESERVE_USD), 'available_for_next_run_usd': float(available),
            'budget_fields': projected,
            'limitations': ['This is a conservative plan-credit calculation, not a wallet credit ledger.',
                           'Purchased credits and promotional credits above the official 5 USD Free allowance are ignored.',
                           'Usage may settle with delay. Refresh before each sequential run; this report cannot launch or authorize a run.',
                           'A paid plan or missing billing field remains blocked; no plan change is attempted.']}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Perform three read-only GET requests using explicitly configured APIFY_TOKEN')
    parser.add_argument('--output', type=Path, help='Save only the filtered budget report')
    parser.add_argument('--run-cap-usd', default='0.50')
    args = parser.parse_args(argv)
    if not args.execute:
        print(json.dumps({'mode': 'offline_preview', 'read_only': True, 'credential_read': False,
                          'network_called': False, 'endpoints': ENDPOINTS,
                          'execution_guard_enabled': True}, indent=2))
        return 0
    # Deliberately no file/config/browser/keychain lookup, and no environment scan.
    token = os.environ.get('APIFY_TOKEN', '').strip()
    if not token:
        print(json.dumps({'status': 'blocked', 'reason': 'APIFY_TOKEN_not_configured', 'network_called': False}))
        return 2
    if len(token) > 4096 or any(ord(c) < 33 or ord(c) > 126 for c in token):
        print(json.dumps({'status': 'blocked', 'reason': 'invalid_APIFY_TOKEN_format', 'network_called': False}))
        return 2
    try:
        cap = number(Decimal(args.run_cap_usd), 'requested_run_cap_usd')
        if cap <= 0:
            raise BudgetError('Requested run cap must be positive')
        projected = {key: fetch_projected(key, token) for key in ENDPOINTS}
        report = assess(projected, cap)
    except (BudgetError, InvalidOperation) as exc:
        message = str(exc) if isinstance(exc, BudgetError) else 'Invalid requested run cap'
        print(json.dumps({'status': 'blocked', 'reason': message, 'execution_authorized': False}))
        return 2
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + '\n', encoding='utf-8')
    print(encoded)
    return 0 if report['eligible_for_operator_review'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
