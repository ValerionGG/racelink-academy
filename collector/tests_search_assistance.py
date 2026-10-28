"""Opt-in query recovery, precise vehicle constraints, and API/Worker parity.

All inserted records are isolated test fixtures. No live catalog is changed.
"""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from server import (initialize, import_items, connect, serialize_video, discovery_config,
                    search, search_resources, suggestions, query_assistance)
from tests_backend import sample, vehicle, automotive, cleanup_temp


class SearchAssistanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.temp.name) / 'fixture.sqlite3'
        initialize(cls.db)
        cls.config = {**discovery_config(), '_guides': []}
        records = [
            sample(1, title='Remplacer les essuie-glaces Clio IV', description='',
                   automotive=automotive([vehicle(generation='IV', engine='1.2 TCE', year_from=2018, year_to=2018)], ['wipers'])),
            sample(2, title='Comprendre la climatisation Clio IV', description='',
                   url='https://www.tiktok.com/@test_fixture/video/7000000000000000002',
                   automotive=automotive([vehicle(generation='IV')], [], ['hvac'])),
            sample(3, title='Climatisation Clio IV English fixture', description='', language='en',
                   url='https://www.tiktok.com/@test_fixture/video/7000000000000000003',
                   automotive=automotive([vehicle(generation='IV')])),
            sample(4, title='Pile de clé Clio V', description='',
                   automotive=automotive([vehicle(generation='V')], ['key_battery'])),
            sample(5, title='Legacy lowercase model fixture', description='',
                   automotive=automotive([vehicle(make='', model='clio', generation='3')])),
            sample(6, title='Vidange Clio III', description='',
                   automotive=automotive([vehicle(generation='III', engine='1.5 DCI')], ['oil_change'])),
            sample(7, title='Comprendre une climatisation', description='',
                   url='https://www.instagram.com/reel/TestFixture7/'),
        ]
        import_items(cls.db, records, strict=True)

    @classmethod
    def tearDownClass(cls):
        cleanup_temp(cls.temp)

    def assistance(self, params):
        return query_assistance(self.db, params, config=self.config)['suggestions']

    def test_symptom_is_an_opt_in_topic_not_a_diagnosis_or_automatic_rewrite(self):
        params = {'q': 'ma clim ne fait plus de froid', 'language': 'fr', 'platform': 'tiktok'}
        result = search_resources(self.db, params, guides=[])
        self.assertEqual(result['query'], params['q'])
        self.assertEqual(result['total'], 0)
        recovery = result['search_assistance']['suggestions'][0]
        self.assertEqual(recovery['query'], 'climatisation')
        self.assertEqual(recovery['match_basis'], 'symptom_vocabulary')
        self.assertEqual(recovery['count'], 1)
        self.assertEqual(recovery['filters'], {'language': 'fr', 'platform': 'tiktok'})
        self.assertIn('pas un diagnostic', recovery['reason']['fr'])
        clicked = search_resources(self.db, {**recovery['filters'], 'q': recovery['query']}, guides=[])
        self.assertEqual(clicked['total'], recovery['count'])
        self.assertEqual([item['id'] for item in clicked['items']], ['sample_2'])

    def test_case_variants_do_not_erase_explicit_model_generation(self):
        result = search(self.db, {'q': 'pile de ma clé Clio 5', 'language': 'fr'})
        self.assertEqual(result['inferred_vehicle'], {'model': 'Clio', 'generation': 'V', 'make': 'Renault'})
        self.assertEqual(result['inferred_task'], 'key_battery')
        self.assertEqual([item['id'] for item in result['items']], ['sample_4'])
        for query in ['vidange Clio 3', 'vidange clio3']:
            result = search(self.db, {'q': query})
            self.assertEqual(result['inferred_vehicle']['generation'], 'III')
            self.assertEqual([item['id'] for item in result['items']], ['sample_6'])

    def test_typo_recovery_keeps_entire_vehicle_engine_year_and_extra_words(self):
        params = {'q': 'essuie glasse Clio 4 1.2 TCE 2018', 'language': 'fr'}
        item = self.assistance(params)[0]
        self.assertEqual(item['query'], 'essuie-glaces Clio 4 1.2 TCE 2018')
        self.assertEqual(item['count'], 1)
        for key, value in {'make': 'Renault', 'model': 'Clio', 'generation': 'IV', 'engine': '1.2 TCE', 'year': '2018', 'language': 'fr'}.items():
            self.assertEqual(item['filters'][key], value)
        self.assertEqual(self.assistance({**params, 'q': params['q'] + ' zeppelin'}), [])

    def test_recovery_never_relaxes_incompatible_or_empty_filters(self):
        for params in [
            {'q': 'ma clim ne fait plus de froid', 'language': 'ja'},
            {'q': 'ma clim ne fait plus de froid', 'platform': 'vimeo'},
            {'q': 'ma clim ne fait plus de froid', 'format': 'image'},
            {'q': 'essuie glasse Clio 4', 'make': 'Peugeot'},
            {'q': 'essuie glasse Clio 4', 'generation': 'V'},
            {'q': 'essuie glasse Clio 4 1.3 TCE'},
            {'q': 'essuie glasse Clio 4 2019'},
            {'q': 'essuie glasse Clio 4', 'spec': '5W-30'},
            {'q': 'essuie glasse Clio 4', 'task': 'oil_change'},
            {'q': 'ma clim ne fait plus de froid', 'ids': 'sample_6'},
        ]:
            with self.subTest(params=params):
                self.assertEqual(self.assistance(params), [])

    def test_no_fuzzy_vehicle_or_technical_reference_repair(self):
        for query in ['essuie glasse Cluo 4', 'essuie glasse Clio 40', 'essuie glasse Clio 4 ACEA C3',
                      'essuie glasse Clio 4 RN071O', 'essuie glasse Clio 4 5W3', 'xyzzy qwerty', '']:
            with self.subTest(query=query):
                self.assertEqual(self.assistance({'q': query}), [])

    def test_predictive_search_exposes_counted_symptom_proposal(self):
        params = {'q': 'ma clim ne fait plus de froid Clio 4', 'language': 'fr'}
        found = suggestions(self.db, params, config=self.config)['suggestions']
        proposal = next(item for item in found if item['type'] == 'query')
        self.assertEqual(proposal['count'], 1)
        self.assertEqual(proposal['filters']['generation'], 'IV')
        self.assertEqual(len(found), 1)

    def test_source_provider_requires_explicit_peertube_metadata(self):
        with connect(self.db) as conn:
            row = dict(conn.execute('SELECT * FROM videos LIMIT 1').fetchone())
        for provider in ['peertube', 'PeerTube', 'youtube', None]:
            metadata = json.loads(row['metadata_json'])
            metadata['provider'] = provider
            item = serialize_video({**row, 'metadata_json': json.dumps(metadata)})
            self.assertEqual(item.get('source_provider'), 'peertube' if provider == 'peertube' else None)

    def test_python_worker_parity_on_recovery_and_precise_model_case(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node is required for cross-engine parity')
        with connect(self.db) as conn:
            payload = {'items': [serialize_video(row) for row in conn.execute('SELECT * FROM videos')]}
        params = [
            {'q': 'ma clim ne fait plus de froid', 'language': 'fr'},
            {'q': 'ma clim ne fait plus de froid', 'language': 'fr', 'platform': 'tiktok'},
            {'q': 'ma clim ne fait plus de froid Clio 4', 'language': 'fr'},
            {'q': 'essuie glasse Clio 4 1.2 TCE 2018', 'language': 'fr'},
            {'q': 'essuie glasse Clio 4', 'generation': 'V'},
            {'q': 'essuie glasse Clio 4 5W3'},
            {'q': 'pile de ma clé Clio 5', 'language': 'fr'},
            {'q': 'vidange Clio 3'}, {'q': 'vidange clio3'},
            {'q': 'ma clim ne fait plus de froid', 'format': 'image'},
        ]
        data = {'payload': payload, 'config': self.config, 'params': params}
        runner = Path(__file__).with_name('tests_search_assistance.mjs')
        proc = subprocess.run([node, str(runner)], input=json.dumps(data, ensure_ascii=False),
                              text=True, encoding='utf-8', capture_output=True, check=True)
        actual = json.loads(proc.stdout)
        for query, result in zip(params, actual):
            with self.subTest(params=query):
                expected = search_resources(self.db, query, guides=[])
                for key in ['total', 'inferred_vehicle', 'inferred_task', 'inferred_spec', 'query_residual', 'interpretation_conflicts', 'search_assistance']:
                    self.assertEqual(result['search'][key], expected[key], key)
                self.assertEqual(result['assist'], self.assistance(query))
                self.assertEqual(result['suggest'], suggestions(self.db, query, config=self.config)['suggestions'])


if __name__ == '__main__':
    unittest.main()
