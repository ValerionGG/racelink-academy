"""Offline tests: no network, no catalogue writes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import peertube_collect as p

UUID = '4cba1a01-23d9-4de5-ac6d-427425eb393c'


def video(**changes):
    row = {'uuid': UUID, 'url': 'https://tube.example.org/videos/watch/' + UUID,
           'name': 'Vidange moteur', 'description': None, 'privacy': {'id': 1},
           'nsfw': False, 'isLive': False, 'tags': [], 'language': {'id': 'fr'},
           'licence': {'id': None, 'label': 'Unknown'}}
    row.update(changes)
    return row


class CollectorTests(unittest.TestCase):
    def test_plan_rejects_unknown_fields(self):
        with self.assertRaises(ValueError):
            p.validate_plan({'jobs': [{'query': 'vidange', 'proxy': 'x'}]})

    def test_plan_bounds(self):
        for limit in (0, 101, True):
            with self.assertRaises(ValueError):
                p.validate_plan({'jobs': [{'query': 'vidange', 'limit': limit}]})

    def test_plan_total_budget(self):
        with self.assertRaises(ValueError):
            p.validate_plan({'jobs': [{'query': 'frein', 'limit': 60}, {'query': 'vidange', 'limit': 60}]})

    def test_duplicate_jobs(self):
        with self.assertRaises(ValueError):
            p.validate_plan({'jobs': [{'query': 'Vidange'}, {'query': 'vidange'}]})

    def test_query_encoded_not_command(self):
        jobs = p.validate_plan({'jobs': [{'query': 'moteur & filtre', 'language': 'fr', 'limit': 35}]})
        self.assertIn('search=moteur+%26+filtre', p.request_url(jobs[0]))
        self.assertIn('count=10', p.request_url(jobs[0], 25))

    def test_channel_only_allows_reviewed_hosts(self):
        with self.assertRaises(ValueError):
            p.validate_plan({'jobs': [{'channel': 'https://arbitrary.example.org/video-channels/car'}]})
        jobs = p.validate_plan({'jobs': [{'channel': 'https://tube-enseignement-professionnel.apps.education.fr/video-channels/lycee_guynemer', 'limit': 35}]})
        self.assertIn('/api/v1/video-channels/lycee_guynemer/videos?count=10&start=25', p.request_url(jobs[0], 25))

    def test_channel_query_mix_rejected(self):
        with self.assertRaises(ValueError):
            p.validate_plan({'jobs': [{'channel': 'https://peertube.lyceeconnecte.fr/video-channels/mecanique23', 'query': 'moteur'}]})

    def test_missing_description_stays_missing(self):
        r = p.normalize(video(), {})
        self.assertIsNone(r['description'])
        self.assertIsNone(r['transcript'])
        self.assertEqual([], r['vehicleEvidence'])
        self.assertFalse(r['licenceVerified'])

    def test_hashtags_not_title(self):
        r = p.normalize(video(description='Cours #moteur #auto #auto'), {})
        self.assertEqual(['moteur', 'auto'], r['hashtags'])
        self.assertEqual('Vidange moteur', r['title'])
        self.assertEqual('Cours #moteur #auto #auto', r['description'])

    def test_visibility_requires_explicit_public(self):
        for privacy in ({'id': 2}, None, {}):
            with self.assertRaises(ValueError):
                p.normalize(video(privacy=privacy), {})

    def test_live_sensitive_unknown_excluded(self):
        for fields in ({'nsfw': True}, {'nsfw': None}, {'isLive': True}, {'isLive': None}):
            with self.assertRaises(ValueError):
                p.normalize(video(**fields), {})

    def test_identity_attested_by_url(self):
        with self.assertRaises(ValueError):
            p.normalize(video(url='https://tube.example.org/videos/watch/not-the-uuid'), {})

    def test_unsafe_urls_rejected(self):
        for url in ('http://tube.example.org/x', 'https://127.0.0.1/x', 'https://localhost/x',
                    'https://a:pw@tube.example.org/x', 'https://tube.example.org:8443/x',
                    'https://tube.example.org/x?token=abc', 'https://tube.example.org/x#fragment'):
            with self.assertRaises(ValueError):
                p.safe_url(url)

    def test_native_proof_unchanged(self):
        row = video()
        before = copy.deepcopy(row)
        r = p.normalize(row, {'sha256': 'test'})
        self.assertEqual(before, row)
        self.assertEqual(p.sha(row), r['nativeRecordSha256'])
        self.assertEqual('platform_declared_not_audio_verified', r['languageEvidence'])

    def test_native_thumbnail_path_resolved_on_approved_host(self):
        row = video(url='https://tube-enseignement-professionnel.apps.education.fr/videos/watch/' + UUID,
                    thumbnailPath='/lazy-static/thumbnails/image.jpg')
        r = p.normalize(row, {})
        self.assertEqual('https://tube-enseignement-professionnel.apps.education.fr/lazy-static/thumbnails/image.jpg', r['thumbnailUrl'])

    def test_thumbnail_path_cannot_switch_host(self):
        row = video(url='https://tube-enseignement-professionnel.apps.education.fr/videos/watch/' + UUID,
                    thumbnailPath='//unreviewed.example.org/image.jpg')
        self.assertIsNone(p.normalize(row, {})['thumbnailUrl'])

    def test_active_lock_prevents_parallel_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'collector.lock').write_text('active')
            jobs = p.validate_plan({'jobs': [{'query': 'vidange'}]})
            with self.assertRaises(ValueError):
                p.collect(jobs, tmp)

    def test_resume_does_not_replay_completed_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            def fetch(url, path, timeout):
                calls.append(url)
                body = json.dumps({'data': [video()], 'total': 1}).encode()
                path.write_bytes(body)
                return json.loads(body), p.sha(body)
            jobs = p.validate_plan({'jobs': [{'query': 'vidange'}]})
            first = p.collect(jobs, tmp, fetcher=fetch, sleeper=lambda _: None)
            second = p.collect(jobs, tmp, resume=True, fetcher=fetch, sleeper=lambda _: None)
            self.assertEqual(1, len(calls))
            self.assertEqual(first['rawResults'], second['rawResults'])
            self.assertEqual(0, second['imported'])

    def test_limited_source_never_auto_retries(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            def fetch(url, path, timeout):
                calls.append(url)
                raise RuntimeError('HTTP 429')
            jobs = p.validate_plan({'jobs': [{'query': 'vidange'}]})
            with self.assertRaises(RuntimeError):
                p.collect(jobs, tmp, fetcher=fetch)
            with self.assertRaises(ValueError):
                p.collect(jobs, tmp, resume=True, fetcher=fetch)
            self.assertEqual(1, len(calls))

    def test_changed_evidence_blocks_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fetch(url, path, timeout):
                body = b'{"data": []}'
                path.write_bytes(body)
                return json.loads(body), p.sha(body)
            jobs = p.validate_plan({'jobs': [{'query': 'vidange'}]})
            p.collect(jobs, tmp, fetcher=fetch)
            (Path(tmp) / 'raw/job-00-offset-0000.json').write_text('{"data": [1]}')
            with self.assertRaises(ValueError):
                p.collect(jobs, tmp, resume=True, fetcher=fetch)

    def test_duplicate_and_invalid_result_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fetch(url, path, timeout):
                body = json.dumps({'data': [video(), video(), video(privacy={'id': 2})]}).encode()
                path.write_bytes(body)
                return json.loads(body), p.sha(body)
            jobs = p.validate_plan({'jobs': [{'query': 'vidange'}]})
            r = p.collect(jobs, tmp, fetcher=fetch)
            self.assertEqual((3, 1, 1, 1), (r['rawResults'], r['distinctCandidates'], r['duplicateRows'], r['invalidRows']))


if __name__ == '__main__':
    unittest.main()
