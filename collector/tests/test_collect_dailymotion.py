import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

SOURCE = next(p/'scripts/collect_dailymotion.py' for p in Path(__file__).resolve().parents if (p/'scripts/collect_dailymotion.py').is_file())
spec = importlib.util.spec_from_file_location('collect_dailymotion', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FakeReader:
    def __init__(self, responses): self.responses, self.calls = list(responses), []
    def get(self, url):
        self.calls.append(url)
        if not self.responses: raise AssertionError('Unexpected network request')
        return self.responses.pop(0)


def response(count=2, more=False, status=200):
    return {'status': status, 'body': {'list': [{'id': f'x{i}', 'title': 'Changer un filtre moteur'} for i in range(count)], 'has_more': more}}


def plan():
    return {'version': mod.VERSION, 'provider': mod.PROVIDER, 'queries': ['vidange moteur', 'freins voiture'],
            'pages_per_query': 2, 'page_size': 2, 'minimum_request_interval_seconds': 1.5,
            'timeout_seconds': 25, 'maximum_requests': 4, 'media_downloaded': False, 'authenticated': False}


class CollectorTests(unittest.TestCase):
    def test_preview_neither_writes_nor_creates_reader(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(mod, 'Reader', side_effect=AssertionError('network')):
            output = Path(folder) / 'absent'
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(mod.main(['--output', str(output), '--query', 'vidange moteur']), 0)
            self.assertFalse(output.exists())
            self.assertEqual(json.loads(stdout.getvalue())['network_requests'], 0)

    def test_output_is_required(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            mod.main([])
        self.assertEqual(error.exception.code, 2)

    def test_parser_rejects_invalid_limits_without_writing(self):
        invalid = [['--pages', '0'], ['--pages', '11'], ['--page-size', '101'], ['--interval', 'nan'],
                   ['--timeout', 'inf'], ['--start', '-1'], ['--start', '59', '--count', '2'],
                   ['--query', ''], ['--query', 'a', '--query', 'a'], ['--query', 'a', '--count', '1']]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'absent'
            for args in invalid:
                with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    mod.main(['--output', str(output), *args])
                self.assertEqual(error.exception.code, 2)
                self.assertFalse(output.exists())

    def test_bounded_pagination_and_resume_zero_network(self):
        with tempfile.TemporaryDirectory() as folder:
            reader = FakeReader([response(more=True), response(more=True), response(count=1, more=True)])
            first = mod.collect(plan(), folder, reader=reader)
            self.assertEqual(len(reader.calls), 3)
            self.assertTrue(first['complete'])
            self.assertEqual(first['raw_rows'], 5)
            second = mod.collect(plan(), folder, resume=True, reader=FakeReader([]))
            self.assertEqual(second['network_requests_this_run'], 0)
            self.assertEqual(second['raw_rows'], 5)

    def test_resume_requires_same_plan(self):
        with tempfile.TemporaryDirectory() as folder:
            mod.collect(plan(), folder, reader=FakeReader([response(), response()]))
            changed = {**plan(), 'page_size': 1}
            with self.assertRaisesRegex(ValueError, 'same queries'):
                mod.collect(changed, folder, resume=True, reader=FakeReader([]))

    def test_existing_output_requires_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            mod.collect(plan(), folder, reader=FakeReader([response(), response()]))
            with self.assertRaisesRegex(ValueError, '--resume'):
                mod.collect(plan(), folder, reader=FakeReader([]))

    def test_hash_change_refuses_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            result = mod.collect(plan(), folder, reader=FakeReader([response(), response()]))
            path = Path(folder) / 'raw' / result['pages'][0]['file']
            path.write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'missing or changed'):
                mod.collect(plan(), folder, resume=True, reader=FakeReader([]))

    def test_cache_after_interruption_is_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            real_write = mod.write_json
            def crash(path, value):
                if path.name == 'checkpoint.json' and value.get('pages'):
                    raise OSError('simulated interruption after cache write')
                real_write(path, value)
            with patch.object(mod, 'write_json', side_effect=crash), self.assertRaises(OSError):
                mod.collect(plan(), folder, reader=FakeReader([response()]))
            reader = FakeReader([response()])
            result = mod.collect(plan(), folder, resume=True, reader=reader)
            self.assertEqual(len(reader.calls), 1)
            self.assertTrue(result['pages'][0]['reused_after_checkpoint'])
            self.assertTrue(result['complete'])

    def test_refusals_stop_all_jobs_and_persist(self):
        for code in (401, 403, 429):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as folder:
                reader = FakeReader([{'status': code, 'body': {}, 'retry_after': '60'}])
                result = mod.collect(plan(), folder, reader=reader)
                self.assertEqual(len(reader.calls), 1)
                self.assertTrue(result['paused'])
                self.assertFalse(result['complete'])
                pause = json.loads((Path(folder) / 'dailymotion-paused.json').read_text(encoding='utf-8'))
                self.assertEqual(pause['status'], code)
                self.assertEqual(pause['retry_after'], '60')
                self.assertEqual(mod.collect(plan(), folder, resume=True, reader=FakeReader([]))['network_requests_this_run'], 0)

    def test_existing_pause_stops_without_network(self):
        with tempfile.TemporaryDirectory() as folder:
            result = mod.collect(plan(), folder, reader=FakeReader([response(), response()]))
            mod.write_json(Path(folder) / 'dailymotion-paused.json', {'status': 429})
            again = mod.collect(plan(), folder, resume=True, reader=FakeReader([]))
            self.assertEqual(again['network_requests_this_run'], 0)
            self.assertTrue(again['paused'])
            self.assertFalse(again['complete'])

    def test_network_failure_not_retried(self):
        with tempfile.TemporaryDirectory() as folder:
            reader = FakeReader([{'status': 0, 'body': {}, 'error': 'network_error'}])
            result = mod.collect(plan(), folder, reader=reader)
            self.assertTrue(result['failed'])
            self.assertEqual(len(reader.calls), 1)
            self.assertEqual(mod.collect(plan(), folder, resume=True, reader=FakeReader([]))['network_requests_this_run'], 0)

    def test_lock_blocks_second_writer(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / '.collector.lock').write_text('busy')
            with self.assertRaises(FileExistsError):
                mod.collect(plan(), folder, reader=FakeReader([]))

    def test_transport_redirect_is_not_followed(self):
        self.assertIsNone(mod.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.invalid'))

    def test_transport_projection_excludes_media_and_profile_data(self):
        class Http:
            status = 200
            headers = {}
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, bound):
                return json.dumps({'has_more': False, 'list': [{'id': 'x1', 'title': 'Titre',
                    'stream_hls_url': 'https://media.invalid/video.m3u8', 'comments': ['ignored']}]}).encode()
        class Opener:
            def open(self, request, timeout):
                self.request = request
                return Http()
        opener = Opener()
        result = mod.Reader(1.5, 25, opener=opener).get('https://api.dailymotion.com/videos')
        self.assertEqual(result['body']['list'], [{'id': 'x1', 'title': 'Titre'}])
        self.assertNotIn('Authorization', opener.request.headers)
        self.assertNotIn('Cookie', opener.request.headers)

    def test_transport_uses_no_environment_proxy_or_cookies(self):
        with patch.object(mod, 'build_opener') as factory:
            mod.Reader(1.5, 25)
            args = factory.call_args.args
            self.assertEqual(args[0].proxies, {})
            self.assertIsInstance(args[1], mod.NoRedirect)


if __name__ == '__main__': unittest.main(verbosity=2)
