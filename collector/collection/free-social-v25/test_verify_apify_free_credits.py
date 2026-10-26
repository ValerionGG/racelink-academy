import contextlib, io, json, tempfile, unittest, urllib.error
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
import datetime as dt
import verify_apify_free_credits as probe

NOW=dt.datetime(2026,10,26,12,tzinfo=dt.timezone.utc)

def source():
    cycle={'startAt':'2026-10-01T00:00:00Z','endAt':'2026-10-31T23:59:59Z'}
    return {'account':{'plan':{'tier':'FREE','isEnabled':True,'monthlyBasePriceUsd':0,'monthlyUsageCreditsUsd':5},'isPaying':False,
                       'email':'DO_NOT_COPY@example.test','proxy':{'password':'NEVER_PRINT_THIS'},'id':'PRIVATE_ID'},
            'limits':{'monthlyUsageCycle':cycle,'limits':{'maxMonthlyUsageUsd':5},'current':{'monthlyUsageUsd':1.2,'activeActorJobCount':0}},
            'usage':{'usageCycle':dict(cycle),'totalUsageCreditsUsdAfterVolumeDiscount':1.3}}

def snapshot(d=None):
    return {k:probe.project(k,v) for k,v in (d or source()).items()}

class BudgetTests(unittest.TestCase):
    def test_projection_excludes_account_secrets(self):
        encoded=json.dumps(snapshot())
        for text in ['DO_NOT_COPY','NEVER_PRINT_THIS','PRIVATE_ID','email','proxy','password']:
            self.assertNotIn(text,encoded)
    def test_conservative_remaining_and_never_authorizes(self):
        r=probe.assess(snapshot(),now=NOW)
        self.assertEqual(r['available_for_next_run_usd'],3.45)
        self.assertTrue(r['eligible_for_operator_review'])
        self.assertFalse(r['execution_authorized'])
        self.assertTrue(r['execution_guard_enabled'])
    def test_paid_account_is_blocked(self):
        for field,value in [('tier','BRONZE'),('monthlyBasePriceUsd',19),('isEnabled',False)]:
            d=source();d['account']['plan'][field]=value
            self.assertFalse(probe.assess(snapshot(d),now=NOW)['eligible_for_operator_review'])
        d=source();d['account']['isPaying']=True
        self.assertFalse(probe.assess(snapshot(d),now=NOW)['eligible_for_operator_review'])
    def test_missing_plan_is_blocked(self):
        d=source();del d['account']['plan']
        with self.assertRaises(probe.BudgetError):snapshot(d)
    def test_never_counts_credits_above_five(self):
        d=source();d['account']['plan']['monthlyUsageCreditsUsd']=50;d['limits']['limits']['maxMonthlyUsageUsd']=100
        self.assertEqual(probe.assess(snapshot(d),now=NOW)['conservative_allowance_usd'],5)
    def test_small_account_limit_is_respected(self):
        d=source();d['limits']['limits']['maxMonthlyUsageUsd']=1.5
        self.assertFalse(probe.assess(snapshot(d),now=NOW)['eligible_for_operator_review'])
    def test_usage_uses_larger_observation(self):
        d=source();d['limits']['current']['monthlyUsageUsd']=4.7
        self.assertEqual(probe.assess(snapshot(d),now=NOW)['available_for_next_run_usd'],0.05)
    def test_active_run_blocks(self):
        d=source();d['limits']['current']['activeActorJobCount']=1
        self.assertIn('other_actor_jobs_are_active',probe.assess(snapshot(d),now=NOW)['reasons'])
    def test_cycle_mismatch_blocks(self):
        d=source();d['usage']['usageCycle']['startAt']='2026-09-01T00:00:00Z'
        self.assertIn('usage_cycle_mismatch',probe.assess(snapshot(d),now=NOW)['reasons'])
    def test_old_cycle_blocks(self):
        self.assertIn('usage_cycle_is_not_current',probe.assess(snapshot(),now=NOW.replace(year=2027))['reasons'])
    def test_invalid_numbers_fail_closed(self):
        for value in [True,None,'5',float('nan'),float('inf'),-1]:
            d=source();d['account']['plan']['monthlyUsageCreditsUsd']=value
            with self.assertRaises(probe.BudgetError):snapshot(d)
    def test_preview_reads_no_credentials_and_makes_no_requests(self):
        def locale_only(key,*args):
            self.assertIn(key,{'LANGUAGE','LC_ALL','LC_MESSAGES','LANG'})
            return None
        with patch.object(probe.os.environ,'get',side_effect=locale_only),patch.object(probe,'fetch_projected',side_effect=AssertionError('network')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(probe.main([]),0)
    def test_no_token_means_no_network_or_file(self):
        with tempfile.TemporaryDirectory() as td,patch.object(probe.os.environ,'get',return_value='') as get,patch.object(probe,'fetch_projected',side_effect=AssertionError('network')),contextlib.redirect_stdout(io.StringIO()):
            target=Path(td)/'report.json';self.assertEqual(probe.main(['--execute','--output',str(target)]),2)
            self.assertFalse(target.exists())
            self.assertEqual([c for c in get.call_args_list if c.args[0]=='APIFY_TOKEN'],[unittest.mock.call('APIFY_TOKEN','')])
            self.assertTrue(all(c.args[0] in {'LANGUAGE','LC_ALL','LC_MESSAGES','LANG','APIFY_TOKEN'} for c in get.call_args_list))
    def test_http_error_body_never_printed(self):
        error=urllib.error.HTTPError('https://api.apify.com/v2/users/me',401,'SECRET_VALUE',{},io.BytesIO(b'NEVER_PRINT_THIS'))
        def failed(*args,**kwargs):raise error
        with self.assertRaises(probe.BudgetError) as raised:probe.fetch_projected('account','FAKE_TOKEN',opener=failed)
        self.assertEqual(str(raised.exception),'Budget endpoint HTTP 401')
    def test_get_only_and_filtered_response(self):
        class Response(io.BytesIO):status=200
        def fake(request,timeout):
            self.assertEqual(request.get_method(),'GET');self.assertEqual(request.full_url,probe.ENDPOINTS['account'])
            self.assertEqual(request.get_header('Authorization'),'Bearer FAKE_TOKEN')
            return Response(json.dumps({'data':source()['account']}).encode())
        result=probe.fetch_projected('account','FAKE_TOKEN',opener=fake)
        self.assertNotIn('NEVER_PRINT_THIS',json.dumps(result))
    def test_redirects_are_refused(self):
        self.assertIsNone(probe.NoRedirect().redirect_request(None,None,302,'',{},'https://other.test/'))

if __name__=='__main__':unittest.main()
