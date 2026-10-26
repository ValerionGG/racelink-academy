import contextlib
import copy
import datetime as dt
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import launch_free_pilot as pilot


def budget_report(usage=0):
    return {'budget_fields': {'limits': {'cycle': {'startAt': '2026-10-01T00:00:00+00:00',
        'endAt': '2026-11-01T00:00:00+00:00'}}}, 'persistent_effective_usage_usd': usage}


def run_response(job, status='SUCCEEDED'):
    actor_id = pilot.load(pilot.HERE / (job['actor'].replace('/', '~') + '.json'))['data']['id']
    return {'data': {'id': 'RunId1234567890123', 'actId': actor_id, 'status': status,
        'defaultDatasetId': 'Dataset1234567890', 'options': {'maxTotalChargeUsd': .5}}}


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.state = Path(self.temp.name)
        self.ui_flag = self.state / 'UI_RUNS_UNRECONCILED'
        self.flag_patch = patch.object(pilot, 'UI_RECONCILIATION_FLAG', self.ui_flag)
        self.flag_patch.start()
        self.addCleanup(self.flag_patch.stop)
        self.plan, self.jobs = pilot.selected_jobs(pilot.PLAN)
        self.job = self.jobs[0]
        self.actor_id = pilot.load(pilot.HERE / (self.job['actor'].replace('/', '~') + '.json'))['data']['id']
        self.provider = {'actor_id': self.actor_id}

    def tearDown(self):
        # Windows may briefly retain a just-closed file during filesystem scans.
        # Retry only that scoped temporary-directory cleanup, never a test failure.
        target = Path(self.temp.name).resolve()
        self.assertEqual(Path(tempfile.gettempdir()).resolve(), target.parent)
        for attempt in range(3):
            try:
                self.temp.cleanup()
                break
            except OSError as exc:
                if getattr(exc, 'winerror', None) not in {32, 145} or attempt == 2:
                    raise
                time.sleep(.05 * (attempt + 1))

    def test_preview_no_network_no_credentials_no_state(self):
        self.ui_flag.touch()  # Offline preview remains available while UI runs are unresolved.
        def get_env(key, default=None):
            self.assertIn(key, {'LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'})
            return default
        with patch.object(pilot.os.environ, 'get', side_effect=get_env), patch.object(pilot, 'api_json') as api, \
             patch.object(pilot.budget, 'fetch_projected') as fetch, patch.object(pilot, 'STATE', self.state / 'absent'), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, pilot.main([]))
        api.assert_not_called()
        fetch.assert_not_called()
        self.assertFalse((self.state / 'absent').exists())

    def test_missing_token_has_no_network_or_state(self):
        with patch.dict(pilot.os.environ, {}, clear=True), patch.object(pilot, 'api_json') as api, \
             patch.object(pilot, 'STATE', self.state / 'absent'), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(2, pilot.main(['--execute']))
        api.assert_not_called()
        self.assertFalse((self.state / 'absent').exists())

    def test_ui_flag_blocks_execute_before_token_network_or_runtime(self):
        self.ui_flag.write_text('contents must not be read', encoding='utf-8')
        def get_env(key, default=None):
            self.assertNotEqual('APIFY_TOKEN', key)
            return default
        with patch.object(pilot.os.environ, 'get', side_effect=get_env), \
             patch.object(pilot, 'api_json') as api, patch.object(pilot.budget, 'fetch_projected') as fetch, \
             patch.object(pilot, 'STATE', self.state / 'absent'), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(2, pilot.main(['--execute']))
        self.assertIn('UI_RUNS_UNRECONCILED', output.getvalue())
        api.assert_not_called()
        fetch.assert_not_called()
        self.assertFalse((self.state / 'absent').exists())

    def test_ui_flag_blocks_direct_new_launch_without_receipt(self):
        self.ui_flag.touch()
        with patch.object(pilot, 'api_json') as api, patch.object(pilot, 'public_actor_review') as provider, \
             patch.object(pilot, 'budget_before_start') as check, \
             self.assertRaisesRegex(pilot.PilotError, 'UI_RUNS_UNRECONCILED'):
            pilot.launch_one(self.job, 'test-only', self.state)
        api.assert_not_called()
        provider.assert_not_called()
        check.assert_not_called()
        self.assertFalse((self.state / (self.job['id'] + '.json')).exists())

    def test_ui_flag_created_during_budget_read_blocks_post_and_receipt(self):
        def mark_ui(token, state_dir):
            self.ui_flag.touch()
            return budget_report()
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', side_effect=mark_ui), \
             patch.object(pilot, 'api_json') as api, \
             self.assertRaisesRegex(pilot.PilotError, 'UI_RUNS_UNRECONCILED'):
            pilot.launch_one(self.job, 'test-only', self.state)
        api.assert_not_called()
        self.assertFalse((self.state / (self.job['id'] + '.json')).exists())

    def test_input_hash_modification_blocks(self):
        directory = self.state / 'plan'
        directory.mkdir()
        plan = copy.deepcopy(self.plan)
        job = next(item for item in plan['jobs'] if item['id'] == self.job['id'])
        job['input_file'] = 'changed.json'
        (directory / 'changed.json').write_text('{}')
        pilot.save(directory / 'plan.json', plan)
        with self.assertRaisesRegex(pilot.PilotError, 'hash'):
            pilot.selected_jobs(directory / 'plan.json', [job['id']])

    def test_unknown_inputs_and_media_always_rejected(self):
        for field, value in [('shouldDownloadVideos', True), ('commentsPerPost', 1),
                             ('cookies', 'secret'), ('profiles', ['one', 'two'])]:
            payload = dict(self.job['input'])
            payload[field] = value
            with self.subTest(field=field), self.assertRaises(pilot.PilotError):
                pilot.review_input(self.job['actor'], payload, 60)

    def test_extension_requires_explicit_review_flag(self):
        with self.assertRaisesRegex(pilot.PilotError, 'Review pilot'):
            pilot.selected_jobs(pilot.PLAN, ['fr-tiktok-01'])
        self.assertEqual(1, len(pilot.selected_jobs(pilot.PLAN, ['fr-tiktok-01'], True)[1]))

    def test_current_provider_fixtures_pass_anonymously(self):
        for job in self.jobs:
            actor = job['actor'].replace('/', '~')
            def api(path, token=None):
                self.assertIsNone(token)
                return pilot.load(pilot.HERE / (actor + ('-openapi.json' if 'openapi' in path else '.json')))
            with patch.object(pilot, 'api_json', side_effect=api):
                review = pilot.public_actor_review(job)
                self.assertLessEqual(review['minimum_cap_usd'], .5)
                self.assertEqual(job['reviewed_build'], review['build'])

    def test_price_build_schema_changes_fail_closed(self):
        actor = self.job['actor'].replace('/', '~')
        for kind in ('price', 'build', 'schema', 'minimum'):
            data = pilot.load(pilot.HERE / (actor + '.json'))
            schema = pilot.load(pilot.HERE / (actor + '-openapi.json'))
            if kind == 'price':
                data['data']['pricingInfos'][-1]['pricingPerEvent']['actorChargeEvents']['result']['eventTieredPricingUsd']['FREE']['tieredEventPriceUsd'] = .5
            elif kind == 'minimum':
                data['data']['pricingInfos'][-1]['minimalMaxTotalChargeUsd'] = 1
            elif kind == 'build':
                data['data']['taggedBuilds']['latest']['buildNumber'] = '0.0.999'
            else:
                schema['components']['schemas']['inputSchema']['description'] = 'changed'
            with self.subTest(kind=kind), patch.object(pilot, 'api_json', side_effect=lambda path: schema if 'openapi' in path else data), \
                 self.assertRaises(pilot.PilotError):
                pilot.public_actor_review(self.job)

    def test_budget_failure_prevents_post_and_receipt(self):
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', side_effect=pilot.PilotError('blocked')), \
             patch.object(pilot, 'api_json') as api, self.assertRaises(pilot.PilotError):
            pilot.launch_one(self.job, 'test-only', self.state)
        api.assert_not_called()
        self.assertFalse((self.state / (self.job['id'] + '.json')).exists())

    def test_durable_receipt_before_single_post_and_safe_export(self):
        calls = []
        def api(path, token=None, method='GET', body=None):
            calls.append((path, method))
            if method == 'POST':
                receipt = pilot.load(self.state / (self.job['id'] + '.json'))
                self.assertEqual('submission_pending', receipt['status'])
                query = parse_qs(urlsplit(pilot.API + path).query)
                self.assertEqual(['0.50'], query['maxTotalChargeUsd'])
                self.assertEqual(['600'], query['timeout'])
                self.assertEqual(['false'], query['restartOnError'])
                self.assertEqual([self.job['reviewed_build']], query['build'])
                return run_response(self.job)
            self.assertIn('datasets/', path)
            return [{'id': '1234', 'text': 'Vidange moteur #auto', 'webVideoUrl': 'https://www.tiktok.com/@mechanic/video/1234?tracking=x',
                     'authorMeta': {'name': 'mechanic', 'email': 'secret@example.org', 'bio': 'private'},
                     'videoUrl': 'https://cdn.example.org/file?signature=secret', 'comments': ['secret'],
                     'hashtags': [{'name': 'auto'}]}]
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', return_value=budget_report()), \
             patch.object(pilot, 'api_json', side_effect=api):
            result = pilot.launch_one(self.job, 'test-only', self.state)
        self.assertEqual('finished_for_review', result['status'])
        self.assertEqual(1, result['exported_count'])
        self.assertEqual(1, sum(method == 'POST' for _, method in calls))
        raw = next((self.state / 'review').rglob('page-*.json')).read_text()
        self.assertNotIn('secret', raw)
        self.assertNotIn('signature', raw)
        self.assertNotIn('tracking', raw)
        self.assertIn('Vidange moteur #auto', raw)

    def test_dataset_top_level_selection_preserves_nested_metadata_and_filters_profiles(self):
        # Simulate the provider contract: nested `fields` selectors are ignored.
        # Returning unfiltered fixtures would conceal a broken dataset request.
        source = {'id': '7100000000000000001', 'text': 'Vidange moteur #auto',
            'webVideoUrl': 'https://www.tiktok.com/@mechanic/video/7100000000000000001',
            'authorMeta': {'name': 'mechanic', 'privateAccount': True, 'email': 'PROFILE_CONTACT@example.org',
                           'bio': 'PROFILE_BIO', 'avatar': 'PROFILE_AVATAR'},
            'videoMeta': {'duration': 38,
                'coverUrl': 'https://p16-sign.tiktokcdn-us.com/image.jpg',
                'playAddr': 'https://example.org/PRIVATE_MEDIA.mp4'},
            'comments': ['UNREQUESTED_COMMENT']}
        state = {'batch': self.job['id'], 'actor': self.job['actor'], 'platform': 'tiktok',
            'run_id': 'RunId1234567890123', 'dataset_id': 'Dataset1234567890',
            'result_upper_target': 60, 'run_status': 'SUCCEEDED'}
        def provider_select(path, token=None, method='GET', body=None):
            self.assertEqual('GET', method)
            selected = parse_qs(urlsplit(pilot.API + path).query)['fields'][0].split(',')
            return [{key: value for key, value in source.items() if key in selected}]
        receipt = self.state / (self.job['id'] + '.json')
        with patch.object(pilot, 'api_json', side_effect=provider_select) as api:
            result = pilot.export_dataset(state, receipt, 'test-only', self.state)
        self.assertEqual(1, api.call_count)
        self.assertEqual(1, result['exported_count'])
        page = pilot.load(next((self.state / 'review').rglob('page-*.json')))
        row = page['items'][0]
        self.assertEqual('mechanic', row['creator'])
        self.assertEqual(38, row['duration_seconds'])
        self.assertEqual(source['videoMeta']['coverUrl'], row['thumbnail_url'])
        self.assertIs(row['isPrivate'], True)
        saved = json.dumps(page)
        for excluded in ('PROFILE_CONTACT', 'PROFILE_BIO', 'PROFILE_AVATAR',
                         'PRIVATE_MEDIA', 'UNREQUESTED_COMMENT'):
            self.assertNotIn(excluded, saved)
        self.assertNotIn('authorMeta', row)
        self.assertNotIn('videoMeta', row)

    def test_uncertain_start_never_reposts(self):
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', return_value=budget_report()), \
             patch.object(pilot, 'api_json', side_effect=TimeoutError) as api:
            with self.assertRaisesRegex(pilot.PilotError, 'uncertain'):
                pilot.launch_one(self.job, 'test-only', self.state)
            with self.assertRaisesRegex(pilot.PilotError, 'uncertain'):
                pilot.launch_one(self.job, 'test-only', self.state, resume=True)
        self.assertEqual(1, api.call_count)
        receipt = pilot.load(self.state / (self.job['id'] + '.json'))
        self.assertEqual('outcome_unknown_do_not_resubmit', receipt['status'])

    def test_poll_window_then_resume_uses_get_only(self):
        response = run_response(self.job, 'RUNNING')
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', return_value=budget_report()), \
             patch.object(pilot, 'api_json', return_value=response) as api:
            result = pilot.launch_one(self.job, 'test-only', self.state, polls=1, interval=0)
        self.assertEqual('poll_window_finished_resume_required', result['status'])
        self.assertEqual(2, api.call_count)
        self.ui_flag.touch()  # Existing receipt resumes remain GET-only even during UI reconciliation.
        calls = []
        def resume_api(path, token=None, method='GET', body=None):
            calls.append(method)
            return [] if 'datasets/' in path else run_response(self.job)
        with patch.object(pilot, 'api_json', side_effect=resume_api), \
             patch.object(pilot, 'public_actor_review') as review, patch.object(pilot, 'budget_before_start') as check:
            result = pilot.launch_one(self.job, 'test-only', self.state, resume=True, polls=1, interval=0)
        self.assertEqual('finished_for_review', result['status'])
        self.assertEqual(['GET', 'GET'], calls)
        review.assert_not_called()
        check.assert_not_called()

    def test_dataset_pagination_is_bounded_and_resumable(self):
        job = self.jobs[1]
        state = {'batch': job['id'], 'actor': job['actor'], 'platform': 'instagram',
                 'run_id': 'RunId1234567890123', 'dataset_id': 'Dataset1234567890',
                 'result_upper_target': 100, 'run_status': 'SUCCEEDED'}
        receipt = self.state / (job['id'] + '.json')
        rows = [{'id': str(index), 'caption': 'tuto'} for index in range(50)]
        with patch.object(pilot, 'api_json', side_effect=[rows, pilot.PilotError('network')]) as api:
            with self.assertRaises(pilot.PilotError):
                pilot.export_dataset(state, receipt, 'test-only', self.state)
        self.assertEqual(50, pilot.load(receipt)['exported_offset'])
        with patch.object(pilot, 'api_json', return_value=rows) as api:
            result = pilot.export_dataset(pilot.load(receipt), receipt, 'test-only', self.state)
        self.assertEqual(1, api.call_count)
        self.assertIn('offset=50', api.call_args.args[0])
        self.assertEqual(100, result['exported_count'])
        self.assertTrue(result['export_may_be_truncated_at_target'])

    def test_exclusive_lock_blocks_parallel_and_releases_own_lock(self):
        with pilot.exclusive_runtime(self.state):
            with self.assertRaisesRegex(pilot.PilotError, 'lock'):
                with pilot.exclusive_runtime(self.state):
                    self.fail('parallel lock acquired')
        self.assertFalse((self.state / 'launcher.lock').exists())

    def test_persistent_cap_reservations_prevent_delayed_usage_overspend(self):
        report = {'eligible_for_operator_review': True, 'reasons': [], 'observed_usage_usd': 0,
                  'conservative_allowance_usd': 5, 'budget_fields': budget_report()['budget_fields']}
        cycle = report['budget_fields']['limits']['cycle']
        pilot.save(self.state / 'fr-tiktok-01.json', {'status': 'finished_for_review', 'cycle': cycle,
                   'reserved_effective_usage_after_start_usd': 4.5})
        fields = {'limits': {'cycle': cycle}}
        with patch.object(pilot.budget, 'fetch_projected', side_effect=lambda key, token: fields.get(key, {})), \
             patch.object(pilot.budget, 'assess', return_value=report), self.assertRaisesRegex(pilot.PilotError, 'reservations'):
            pilot.budget_before_start('test-only', self.state)

    def test_unknown_receipt_blocks_other_batches_even_after_cycle_change(self):
        report = {'eligible_for_operator_review': True, 'reasons': [], 'observed_usage_usd': 0,
                  'conservative_allowance_usd': 5, 'budget_fields': budget_report()['budget_fields']}
        pilot.save(self.state / 'fr-tiktok-01.json', {'status': 'outcome_unknown_do_not_resubmit'})
        fields = {'limits': report['budget_fields']['limits']}
        with patch.object(pilot.budget, 'fetch_projected', side_effect=lambda key, token: fields.get(key, {})), \
             patch.object(pilot.budget, 'assess', return_value=report), self.assertRaisesRegex(pilot.PilotError, 'uncertain'):
            pilot.budget_before_start('test-only', self.state)

    def test_status_response_projects_account_and_storage_secrets_out(self):
        response = run_response(self.job)['data']
        response.update(userId='private', meta={'clientIp': 'private'}, containerUrl='secret', statusMessage='secret')
        result = pilot.project_run(response, self.actor_id)
        self.assertNotIn('private', json.dumps(result))
        self.assertNotIn('secret', json.dumps(result))
        response['options']['maxTotalChargeUsd'] = 1
        with self.assertRaises(pilot.PilotError):
            pilot.project_run(response, self.actor_id)

    def test_failed_batch_exports_partial_results_for_review(self):
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', return_value=budget_report()), \
             patch.object(pilot, 'api_json', side_effect=[run_response(self.job, 'FAILED'), []]):
            result = pilot.launch_one(self.job, 'test-only', self.state)
        self.assertEqual('FAILED', result['run_status'])
        self.assertEqual('finished_for_review', result['status'])
        self.assertFalse(result['database_written'])

    def test_redaction_and_no_contacts_media_or_profile_metadata(self):
        result = pilot.safe_post_metadata({'caption': 'Contact me@example.com ou 06 12 34 56 78. Vidange',
            'displayUrl': 'cdn', 'latestComments': ['secret'], 'ownerUsername': 'norautofr',
            'profile': {'email': 'hidden'}, 'url': 'https://www.instagram.com/reel/abc/?sig=secret'}, 'instagram')
        text = json.dumps(result)
        for fragment in ('me@example.com', '06 12', 'secret', 'cdn', 'hidden'):
            self.assertNotIn(fragment, text)
        self.assertIn('Vidange', text)

    def test_transport_does_not_log_token_or_follow_redirect(self):
        class Response:
            status = 201
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, maximum): return b'{"data": {"ok": true}}'
        def opener(request, timeout):
            self.assertEqual('POST', request.method)
            self.assertEqual('Bearer test-only-token', request.get_header('Authorization'))
            self.assertNotIn('test-only-token', request.full_url)
            self.assertEqual(25, timeout)
            return Response()
        with patch.object(pilot.budget, 'SAFE_OPENER', side_effect=opener):
            self.assertTrue(pilot.api_json('acts/clockworks~tiktok-scraper/runs?maxTotalChargeUsd=0.50',
                'test-only-token', method='POST', body=b'{}')['data']['ok'])
        with self.assertRaises(pilot.PilotError):
            pilot.api_json('users/me', 'test-only-token', method='POST', body=b'{}')

    def test_multi_batch_stops_after_failed_or_empty_run(self):
        for status, count in [('FAILED', 2), ('SUCCEEDED', 0)]:
            with patch.dict(pilot.os.environ, {'APIFY_TOKEN': 'test-only-token'}), \
                 patch.object(pilot, 'STATE', self.state / status), \
                 patch.object(pilot, 'launch_one', return_value={'status': 'finished_for_review',
                     'run_status': status, 'exported_count': count}) as launch, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(3, pilot.main(['--execute']))
            self.assertEqual(1, launch.call_count)

    def test_completed_resume_refuses_missing_export_page(self):
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', return_value=budget_report()), \
             patch.object(pilot, 'api_json', side_effect=[run_response(self.job), [{'id': '123'}]]):
            pilot.launch_one(self.job, 'test-only', self.state)
        page = next((self.state / 'review').rglob('page-*.json'))
        page.unlink()
        with patch.object(pilot, 'api_json') as api, self.assertRaisesRegex(pilot.PilotError, 'missing or changed'):
            pilot.launch_one(self.job, 'test-only', self.state, resume=True)
        api.assert_not_called()

    def test_partial_resume_refuses_changed_page_or_unbacked_offset(self):
        job = self.jobs[1]
        state = {'batch': job['id'], 'actor': job['actor'], 'platform': 'instagram',
                 'run_id': 'RunId1234567890123', 'dataset_id': 'Dataset1234567890',
                 'result_upper_target': 100, 'run_status': 'SUCCEEDED'}
        receipt = self.state / (job['id'] + '.json')
        with patch.object(pilot, 'api_json', side_effect=[[{'id': str(i)} for i in range(50)], pilot.PilotError('network')]):
            with self.assertRaises(pilot.PilotError):
                pilot.export_dataset(state, receipt, 'test-only', self.state)
        saved = pilot.load(receipt)
        next((self.state / 'review').rglob('page-*.json')).write_text('{}')
        with patch.object(pilot, 'api_json') as api, self.assertRaisesRegex(pilot.PilotError, 'missing or changed'):
            pilot.export_dataset(saved, receipt, 'test-only', self.state)
        api.assert_not_called()
        with self.assertRaisesRegex(pilot.PilotError, 'offset'):
            pilot.verify_export_progress({**saved, 'export_pages': []}, self.state)

    def test_public_image_urls_preserved_without_downloading_or_credentials(self):
        image = 'https://p16-sign-va.tiktokcdn.com/public-cover.jpeg?x-expires=1999999999&x-signature=public-signature'
        row = pilot.safe_post_metadata({'text': 'Comment changer un essuie-glace #auto',
            'webVideoUrl': 'https://www.tiktok.com/@mechanic/video/7341410668551097633',
            'authorMeta': {'name': 'mechanic'}, 'videoMeta': {'duration': 38, 'coverUrl': image}}, 'tiktok')
        self.assertEqual(image, row['thumbnail_url'])
        self.assertEqual('mechanic', row['creator'])
        self.assertEqual('mechanic', row['uploader'])
        self.assertEqual(38, row['duration_seconds'])
        self.assertEqual(38, row['duration'])
        self.assertEqual(row['text'], row['caption'])
        self.assertEqual(row['url'], row['webVideoUrl'])
        self.assertNotIn('title', row)
        for value in ('https://p16.tiktokcdn.com/video.mp4', 'https://user:password@p16.tiktokcdn.com/image.jpg',
                      'http://p16.tiktokcdn.com/image.jpg', 'https://127.0.0.1/image.jpg',
                      'https://p16.tiktokcdn.com/image.jpg?access_token=secret'):
            self.assertIsNone(pilot.safe_thumbnail(value, 'tiktok'))

    def test_public_export_manifest_matches_generic_schema_and_page_hash(self):
        with patch.object(pilot, 'public_actor_review', return_value=self.provider), \
             patch.object(pilot, 'budget_before_start', return_value=budget_report()), \
             patch.object(pilot, 'api_json', side_effect=[run_response(self.job), [{'id': '123'}]]):
            result = pilot.launch_one(self.job, 'test-only', self.state)
        manifest = pilot.load(self.state / result['public_export_manifest'])
        self.assertEqual({'version', 'kind', 'source', 'pages'}, set(manifest))
        self.assertEqual('PUBLIC_EXPORT', manifest['kind'])
        self.assertEqual('generic', manifest['pages'][0]['schema'])
        self.assertEqual('provider_export', manifest['source']['kind'])
        pilot.verify_export_progress(result, self.state)

    def test_false_video_and_restrictions_survive_numeric_and_text_encodings(self):
        for value in (False, 0, 0.0, 'false', '0', 'no', ' FALSE '):
            row = pilot.safe_post_metadata({'text': 'Tuto vidange', 'isVideo': value}, 'tiktok')
            self.assertIs(row['is_video'], False)
            self.assertNotEqual('VIDEO', row.get('media_type'))
        for value in (True, 1, 1.0, 'true', '1', 'yes', ' TRUE '):
            for field, expected in (('isPhoto', 'isPhoto'), ('isSlideshow', 'isPhoto'),
                                    ('isPrivate', 'isPrivate'), ('isSponsored', 'isSponsored'),
                                    ('isAd', 'isSponsored'), ('isStory', 'isStory'), ('isAIGC', 'is_aigc')):
                with self.subTest(field=field, value=value):
                    row = pilot.safe_post_metadata({field: value}, 'tiktok')
                    self.assertIs(row[expected], True)
                    if expected == 'isPhoto':
                        self.assertIs(row['is_video'], False)

    def test_private_author_account_is_preserved_and_restrictive_alias_wins(self):
        for value in (True, 1, 'true', 'yes'):
            for source in ({'authorMeta': {'privateAccount': value}},
                           {'authorMeta.privateAccount': value}):
                with self.subTest(source=source):
                    row = pilot.safe_post_metadata({'isPrivate': False, **source}, 'tiktok')
                    self.assertIs(row['isPrivate'], True)
                    self.assertNotIn('authorMeta', row)
                    self.assertNotIn('authorMeta.privateAccount', row)
        for value in (False, 0, 'false', 'no'):
            row = pilot.safe_post_metadata({'authorMeta': {'privateAccount': value}}, 'tiktok')
            self.assertIs(row['isPrivate'], False)
            row = pilot.safe_post_metadata({'isPrivate': True,
                'authorMeta': {'privateAccount': value}}, 'tiktok')
            self.assertIs(row['isPrivate'], True)
        row = pilot.safe_post_metadata({'authorMeta.privateAccount': True,
            'authorMeta': {'privateAccount': False}}, 'tiktok')
        self.assertIs(row['isPrivate'], True)

    def test_unknown_private_author_account_encoding_is_rejected(self):
        for value in ('maybe', 2, -1, [], {}, ' '):
            for source in ({'authorMeta': {'privateAccount': value}},
                           {'authorMeta.privateAccount': value}):
                with self.subTest(source=source), self.assertRaises(pilot.PilotError):
                    pilot.safe_post_metadata(source, 'tiktok')

    def test_unknown_restriction_encoding_is_not_dropped(self):
        for field in ('isVideo', 'isPrivate', 'isSponsored', 'isStory', 'isSlideshow', 'isAIGC'):
            for value in ('maybe', 2, -1, [], {}, ' '):
                with self.subTest(field=field, value=value), self.assertRaises(pilot.PilotError):
                    pilot.safe_post_metadata({field: value}, 'tiktok')

    def test_restrictive_alias_wins_and_restricted_availability_is_kept(self):
        row = pilot.safe_post_metadata({'isPrivate': False, 'private': 'true', 'isVideo': True,
            'is_video': 0, 'availability': 'subscriber_only'}, 'instagram')
        self.assertIs(row['isPrivate'], True)
        self.assertIs(row['is_video'], False)
        self.assertEqual('subscriber_only', row['availability'])
        with self.assertRaises(pilot.PilotError):
            pilot.safe_post_metadata({'availability': 'unknown_flag'}, 'instagram')

    def test_flattened_metadata_and_explicit_media_types(self):
        row = pilot.safe_post_metadata({'authorMeta.name': 'mechanic', 'videoMeta.duration': 38,
            'videoMeta.coverUrl': 'https://p16.tiktokcdn.com/image.jpg', 'type': 'Video'}, 'tiktok')
        self.assertEqual('mechanic', row['creator'])
        self.assertEqual(38, row['duration'])
        self.assertIn('thumbnail_url', row)
        for kind in ('Slideshow', 'GraphImage', 'GraphSidecar'):
            self.assertIs(pilot.safe_post_metadata({'type': kind}, 'instagram')['is_video'], False)
        self.assertTrue(pilot.safe_post_metadata({'type': 'Story'}, 'instagram')['isStory'])
        for source in ({'type': 'Story'}, {'isStory': True}, {'is_story': 1}, {'isStory': 'true'}):
            self.assertTrue(pilot.safe_post_metadata(source, 'instagram')['is_story'])
        with self.assertRaises(pilot.PilotError):
            pilot.safe_post_metadata({'type': 'unrecognized-format'}, 'instagram')


if __name__ == '__main__':
    unittest.main()
