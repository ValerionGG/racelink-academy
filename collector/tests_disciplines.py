"""Discipline filtering against isolated fixtures; never opens the live database."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from discipline_rules import discipline_ids
from server import (ValidationError, connect, discovery, discovery_context, import_items,
                    initialize, normalize_guides, query_assistance, search, search_resources,
                    serialize_video, stats, suggestions)
from tests_backend import cleanup_temp, sample


CASES = [
    ({'title': 'Cours de pilotage moto sur circuit', 'domain_scope': 'motorsport'}, ['motorcycle', 'motorsport']),
    ({'title': 'MOTORRÄDER: Bremsen'}, ['motorcycle']),
    ({'title': 'Les conseils d’un champion pour débuter en Kart'}, ['karting']),
    ({'title': 'go-kart / gokarts'}, ['karting']),
    ({'title': 'Learning to Drift in No Hesi / Assetto Corsa', 'category': 'simracing'}, ['drift', 'simracing']),
    ({'title': 'motor Motoröl motorsports motoneige'}, []),
    ({'title': 'Vidange', 'description': 'moto kart drift', 'tags': ['moto', 'kart'], 'creator': 'moto-verte'}, []),
    ({'title': 'Cours de mécanique', 'category': 'driving'}, []),
    ({'title': '', 't': 'moto', 'domain_scope': '', 'd': 'motorsport', 'category': '', 'c': 'simracing'}, []),
    ({'title': None, 't': 'MOTO', 'domain_scope': None, 'd': 'motorsport', 'category': 0, 'c': 'simracing'}, ['motorcycle', 'motorsport', 'simracing']),
    ({'t': 'Drifting avec un kart', 'd': 'motorsport'}, ['karting', 'drift', 'motorsport']),
    ({'title': 'driftmoto kartographie', 'category': 'Simracing', 'domain_scope': 'Motorsport'}, []),
    ({}, []), (None, []),
]


class DisciplineRulesTests(unittest.TestCase):
    def test_conservative_title_and_existing_editorial_fields(self):
        for record, expected in CASES:
            with self.subTest(record=record):
                self.assertEqual(discipline_ids(record), expected)

    def test_javascript_classifier_parity(self):
        node = shutil.which('node')
        candidates = [Path(__file__).parent / 'public' / 'disciplines.js',
                      Path(__file__).parent.parent / 'site' / 'disciplines.js',
                      Path(__file__).parents[2] / 'work' / 'racelink-academy-git' / 'site' / 'disciplines.js']
        module = next((path for path in candidates if path.is_file()), None)
        if not node or not module:
            self.skipTest('Node and published discipline module required for parity')
        script = ('import {disciplineIds} from ' + json.dumps(module.resolve().as_uri()) + ';'
                  'let s="";for await(const part of process.stdin)s+=part;'
                  'process.stdout.write(JSON.stringify(JSON.parse(s).map(disciplineIds)));')
        proc = subprocess.run([node, '--input-type=module', '-e', script],
                              input=json.dumps([case[0] for case in CASES]), text=True,
                              encoding='utf-8', capture_output=True, check=True)
        self.assertEqual(json.loads(proc.stdout), [expected for _, expected in CASES])


class DisciplineApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = initialize(Path(cls.temp.name) / 'fixture.sqlite3')
        records = [
            sample(1, title='Freinage moto débutant', category='driving', description='', domain_scope='motorsport'),
            sample(2, title='Freinage moto English', language='en', category='driving', description='', domain_scope='motorsport'),
            sample(3, title='Freinage karting débutant', category='driving', description='', domain_scope='motorsport'),
            sample(4, title='Freinage Drift simulation', category='simracing', description='', domain_scope='motorsport'),
            sample(5, title='Vidange motor entretien', category='mechanics', domain_scope='automotive_adjacent',
                   description='Publicité moto kart drift', tags=['moto', 'kart', 'drift']),
            sample(6, title='Freinage moto technique', category='mechanics', description='', domain_scope='automotive_adjacent'),
            sample(7, title='Freinage télémétrie', category='engineering', description='', domain_scope='motorsport'),
        ]
        import_items(cls.db, records, strict=True)
        cls.guides = normalize_guides({'guides': [
            {'id': 'guide-moto', 'title': 'Freinage moto : lire la notice', 'language': 'fr',
             'sources': [{'url': 'https://example.org/guide', 'title': 'Test only'}]},
            {'id': 'guide-car', 'title': 'Freinage automobile', 'language': 'fr',
             'sources': [{'url': 'https://example.org/guide2', 'title': 'Test only'}]},
        ]})
        cls.config = {'version': 1, '_guides': cls.guides, 'intents': [], 'shelves': [],
            'defaultTopicIds': ['braking'], 'topics': [
                {'id': 'braking', 'label': {'fr': 'Freinage'}, 'aliases': ['freinage'], 'query': 'freinage',
                 'filters': {}, 'intentId': 'drive'},
                {'id': 'kart-only', 'label': {'fr': 'Kart'}, 'query': '', 'filters': {'discipline': 'karting'}},
            ]}

    @classmethod
    def tearDownClass(cls):
        cleanup_temp(cls.temp)

    def test_filter_before_count_pagination_and_facets(self):
        params = {'discipline': 'motorcycle', 'language': 'fr', 'per_page': '1', 'sort': 'title'}
        first = search(self.db, params)
        second = search(self.db, {**params, 'page': '2'})
        self.assertEqual(first['total'], 2)
        self.assertEqual(first['pages'], 2)
        self.assertEqual([first['items'][0]['id'], second['items'][0]['id']], ['sample_1', 'sample_6'])
        self.assertEqual(first['facets']['discipline'], [{'value': 'motorsport', 'count': 4},
            {'value': 'motorcycle', 'count': 2}, {'value': 'drift', 'count': 1},
            {'value': 'karting', 'count': 1}, {'value': 'simracing', 'count': 1}])
        self.assertEqual(first['facets']['language'], [{'value': 'fr', 'count': 2}])
        self.assertEqual(search(self.db, params, count_only=True), {'total': 2})
        self.assertEqual(search(self.db, {**params, 'category': 'engineering'})['total'], 0)
        self.assertEqual(search(self.db, {**params, 'domain': 'motorsport'})['total'], 1)

    def test_fts_parameter_order_preserves_all_filters(self):
        self.assertEqual(search(self.db, {'q': 'freinage', 'discipline': 'karting', 'language': 'fr'})['total'], 1)
        self.assertEqual(search(self.db, {'q': 'freinage', 'discipline': 'motorcycle', 'language': 'en'})['items'][0]['id'], 'sample_2')
        self.assertEqual(search(self.db, {'discipline': 'motorcycle', 'ids': 'sample_5'}, no_assistance=True)['total'], 0)

    def test_guide_selection_and_combined_offsets(self):
        params = {'discipline': 'motorcycle', 'language': 'fr', 'per_page': '1'}
        first = search_resources(self.db, params, guides=self.guides)
        second = search_resources(self.db, {**params, 'page': '2'}, guides=self.guides)
        self.assertEqual(first['total'], 3)
        self.assertEqual(first['items'][0]['id'], 'guide-moto')
        self.assertEqual(second['items'][0]['id'], 'sample_1')
        self.assertEqual(first['facets']['discipline'], [{'value': 'motorsport', 'count': 4},
            {'value': 'motorcycle', 'count': 3}, {'value': 'drift', 'count': 1},
            {'value': 'karting', 'count': 1}, {'value': 'simracing', 'count': 1}])
        only = search_resources(self.db, {**params, 'format': 'guide'}, guides=self.guides)
        self.assertEqual(only['total'], 1)
        self.assertEqual(only['facets']['discipline'], [{'value': 'motorcycle', 'count': 1}])
        self.assertEqual(search_resources(self.db, {**params, 'format': 'image'}, guides=self.guides)['total'], 0)

    def test_discipline_alternatives_exclude_only_their_own_criterion(self):
        params = {'discipline': 'motorcycle', 'q': 'freinage', 'language': 'fr'}
        result = search_resources(self.db, params, guides=self.guides)
        for option in result['facets']['discipline']:
            actual = search_resources(self.db, {**params, 'discipline': option['value']},
                                      guides=self.guides, count_only=True)
            self.assertEqual(option['count'], actual['total'])
        restricted = search_resources(self.db, {**params, 'category': 'engineering'}, guides=self.guides)
        self.assertEqual(restricted['total'], 0)
        self.assertEqual(restricted['facets']['discipline'], [{'value': 'motorsport', 'count': 1}])
        guide_only = search_resources(self.db, {**params, 'discipline': 'drift', 'format': 'guide'}, guides=self.guides)
        self.assertEqual(guide_only['total'], 0)
        self.assertEqual(guide_only['facets']['discipline'], [{'value': 'motorcycle', 'count': 1}])

    def test_context_topic_counts_and_suggestions_keep_discipline(self):
        params = {'discipline': 'motorcycle', 'language': 'fr'}
        result = discovery(self.db, params, config=self.config)
        self.assertEqual(result['context'], params)
        topics = {topic['id']: topic for topic in result['topics']}
        self.assertEqual(topics['braking']['count'], 3)
        self.assertEqual(topics['kart-only']['count'], 0)
        self.assertTrue(topics['kart-only']['context_conflict'])
        proposed = suggestions(self.db, {**params, 'q': 'frein'}, config=self.config)['suggestions']
        self.assertTrue(proposed)
        for item in proposed:
            self.assertEqual(item['filters']['discipline'], 'motorcycle')
            if 'count' in item:
                actual = search_resources(self.db, {**item['filters'], 'q': item['query']}, guides=self.guides, count_only=True)
                self.assertEqual(item['count'], actual['total'])

    def test_invalid_discipline_fails_even_for_early_return(self):
        for value in ['moto', 'MOTORCYCLE', 'unknown', 'motorcycle OR 1=1']:
            params = {'discipline': value, 'q': ''}
            for invoke in [lambda: search(self.db, params),
                           lambda: search_resources(self.db, params, guides=[]),
                           lambda: discovery_context(params),
                           lambda: suggestions(self.db, params, config=self.config),
                           lambda: query_assistance(self.db, params, config=self.config)]:
                with self.subTest(value=value), self.assertRaises(ValidationError):
                    invoke()

    def test_neutral_filters_and_search_do_not_change_rows(self):
        with connect(self.db) as conn:
            before = [tuple(row) for row in conn.execute('SELECT * FROM videos ORDER BY id')]
        total = search(self.db, {}, count_only=True)['total']
        for value in ['', 'all', 'any', '*']:
            self.assertEqual(search(self.db, {'discipline': value}, count_only=True)['total'], total)
        for discipline in ['motorcycle', 'karting', 'drift', 'motorsport', 'simracing']:
            search_resources(self.db, {'discipline': discipline}, guides=self.guides)
        with connect(self.db) as conn:
            self.assertEqual(before, [tuple(row) for row in conn.execute('SELECT * FROM videos ORDER BY id')])

    def test_stats_use_same_discipline_counts(self):
        result = stats(self.db, public_path=Path(self.temp.name))
        facets = {entry['value']: entry['count'] for entry in result['facets']['discipline']}
        self.assertEqual(facets, {'motorcycle': 3, 'karting': 1, 'drift': 1, 'motorsport': 5, 'simracing': 1})


if __name__ == '__main__':
    unittest.main()
