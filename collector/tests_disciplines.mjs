// Run: node --test collector/tests_disciplines.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {DISCIPLINES, disciplineIds, disciplineMatches} from '../site/disciplines.js';
import {prepareCatalog, searchCatalog, searchResources, catalogStats, discoveryCatalog,
  suggestCatalog, queryAssistance, recommendCatalog} from '../site/catalog-worker.js';

test('each discipline has translated labels and unknown metadata fails closed', () => {
  assert.deepEqual(DISCIPLINES.map(item => item.id), ['motorcycle', 'karting', 'drift', 'motorsport', 'simracing']);
  for (const item of DISCIPLINES) for (const language of ['fr', 'en', 'es']) assert.ok(item.label[language]);
  for (const item of [null, undefined, {}, {title: ''}]) assert.deepEqual(disciplineIds(item), []);
  assert.equal(disciplineMatches({title: 'Moto'}, 'unknown'), false);
  assert.equal(disciplineMatches({title: 'Moto'}, '__proto__'), false);
});

test('real catalog titles use whole tokens across French, English and normalized accents', () => {
  for (const title of ['Cours de pilotage moto sur circuit', 'Motorcycle Body Position: 5 Steps',
    'MOTORRAD RENNFAHRER RICHTIG BREMSEN!', 'Motorräder: Bremsen wechseln', 'Tuto motocross'])
    assert.equal(disciplineMatches({title}, 'motorcycle'), true, title);
  for (const title of ["Les conseils d’un champion pour débuter en Kart", 'How to Trail Brake in Karting', 'Go-kart setup', 'Go karts'])
    assert.equal(disciplineMatches({title}, 'karting'), true, title);
  for (const title of ['DRIFT SCHOOL QUICK TIPS #1', 'Learning to Drift in No Hesi / Assetto Corsa: Part 2', 'Drifting tutorial'])
    assert.equal(disciplineMatches({title}, 'drift'), true, title);
});

test('prefixes, creator names, tags and promotional descriptions do not classify titles', () => {
  for (const title of ['How to Film Motorsports Like a Pro!', 'Motoröl wechseln', 'Motor replacement',
    'Motoneige entretien', 'Automoto magazine', 'motoxyz', '漢moto字'])
    assert.equal(disciplineMatches({title}, 'motorcycle'), false, title);
  assert.equal(disciplineMatches({title: 'Pièces kartable'}, 'karting'), false);
  assert.equal(disciplineMatches({title: 'Driftwood tutorial'}, 'drift'), false);
  assert.deepEqual(disciplineIds({title: 'Changer les essuie-glaces', creator: 'moto-verte', tags: ['moto', 'karting'],
    description: 'Abonnez-vous pour des vidéos moto karting drift'}), []);
});

test('structured domains and categories are explicit, compact aliases preserve full-record semantics', () => {
  const full = {title: 'Learning to Drift in Assetto Corsa', category: 'simracing', domain_scope: 'motorsport'};
  assert.deepEqual(disciplineIds(full), ['drift', 'motorsport', 'simracing']);
  assert.deepEqual(disciplineIds({t: full.title, c: full.category, d: full.domain_scope}), disciplineIds(full));
  assert.deepEqual(disciplineIds({title: 'Motorsport simracing', category: 'driving'}), []);
  assert.deepEqual(disciplineIds({title: '', t: 'moto', category: '', c: 'simracing', domain_scope: '', d: 'motorsport'}), []);
});

const item = (id, title, extra = {}) => ({id, title, creator: id, language: 'fr', platform: 'youtube',
  category: 'mechanics', domain_scope: 'automotive_adjacent', tags: [], license: 'unknown', level: 'unknown',
  automotive: {vehicles: [], tasks: [], systems: [], specifications: []}, ...extra});
const guide = (id, title, extra = {}) => ({id, title, resource_type: 'guide', platform: 'racelink', language: 'fr',
  category: 'mechanics', domain_scope: 'automotive_adjacent', guide: {title}, ...extra});
const fixture = () => prepareCatalog({items: [
  item('youtube:moto', 'Freinage moto sur circuit', {domain_scope: 'motorsport'}),
  item('youtube:car', 'Freinage voiture sur circuit', {domain_scope: 'motorsport'}),
  item('tiktok:kart', 'Tuto freinage karting', {platform: 'tiktok', domain_scope: 'motorsport'}),
  item('instagram:drift', 'Freinage drift dans Assetto Corsa', {platform: 'instagram', category: 'simracing', domain_scope: 'motorsport'}),
  item('youtube:english', 'Motorcycle braking', {language: 'en'}),
  item('youtube:noise', 'Essuie-glaces voiture', {description: 'moto karting drift'}),
], guides: [guide('guide-generic', 'Comprendre le freinage'), guide('guide-moto', 'Freinage moto')], discovery: {
  version: 1, topics: [
    {id: 'braking', label: {fr: 'Freinage'}, query: 'freinage', aliases: ['freinage'], filters: {}},
    {id: 'karts', label: {fr: 'Karting'}, query: '', filters: {discipline: 'karting'}},
  ], queryAssistance: [{id: 'brakes', kind: 'symptom', aliases: ['ralentir'], query: 'freinage'}], shelves: [],
}});
const count = (facets, id) => facets.discipline.find(item => item.value === id)?.count || 0;

test('discipline is applied before resource counts, facets and pagination, with intersections', () => {
  const catalog = fixture(), params = {discipline: 'motorcycle', language: 'fr', format: 'all', per_page: '1'};
  const first = searchResources(catalog, params);
  assert.equal(first.total, 2);
  assert.equal(first.total_guides, 1);
  assert.equal(first.total_videos, 1);
  assert.equal(first.items[0].id, 'guide-moto');
  assert.equal(count(first.facets, 'motorcycle'), 2);
  assert.equal(count(first.facets, 'motorsport'), 4);
  assert.equal(count(first.facets, 'karting'), 1);
  assert.equal(count(first.facets, 'drift'), 1);
  assert.equal(searchResources(catalog, {...params, page: '2'}).items[0].id, 'youtube:moto');
  assert.equal(searchResources(catalog, {...params, platform: 'tiktok'}).total, 0);
  assert.equal(searchResources(catalog, {...params, category: 'simracing'}).total, 0);
  assert.equal(searchResources(catalog, params, {countOnly: true}).total, first.total);
});

test('discipline options exclude their own filter and preserve query, language, platform and resource type', () => {
  const catalog = fixture();
  const params = {discipline: 'motorcycle', q: 'freinage', language: 'fr', format: 'all'};
  const result = searchResources(catalog, params);
  for (const {value, count: predicted} of result.facets.discipline)
    assert.equal(searchResources(catalog, {...params, discipline: value}, {countOnly: true}).total, predicted, value);
  const restricted = searchResources(catalog, {...params, platform: 'tiktok'});
  assert.equal(restricted.total, 0);
  assert.deepEqual(restricted.facets.discipline, [{value: 'karting', count: 1}, {value: 'motorsport', count: 1}]);
  const guides = searchResources(catalog, {...params, format: 'guide', discipline: 'drift'});
  assert.equal(guides.total, 0);
  assert.deepEqual(guides.facets.discipline, [{value: 'motorcycle', count: 1}]);
});

test('generic guides cannot enter a discipline via body text, while attested guide titles can', () => {
  const catalog = fixture();
  catalog.guides[0].guide.steps = ['An incidental example names moto and drift'];
  const guides = searchResources(catalog, {discipline: 'motorcycle', format: 'guide'});
  assert.deepEqual(guides.items.map(item => item.id), ['guide-moto']);
  assert.equal(count(guides.facets, 'motorcycle'), 1);
  assert.equal(searchResources(catalog, {discipline: 'drift', format: 'guide'}).total, 0);
  assert.equal(count(catalogStats(catalog).facets, 'motorcycle'), 3);
  assert.ok(!('_disciplines' in searchCatalog(catalog, {discipline: 'motorcycle'}).items[0]));
});

test('discovery, completions and query recovery retain discipline and count only matching records', () => {
  const catalog = fixture(), params = {discipline: 'motorcycle', language: 'fr'};
  const discovery = discoveryCatalog(catalog, params);
  assert.equal(discovery.topics.find(topic => topic.id === 'braking').count, 2);
  assert.equal(discovery.topics.find(topic => topic.id === 'karts').count, 0);
  assert.equal(discovery.topics.find(topic => topic.id === 'karts').context_conflict, true);
  for (const suggestion of suggestCatalog(catalog, {...params, q: 'freinage'}).suggestions) {
    assert.equal(suggestion.filters.discipline, 'motorcycle');
    if (suggestion.type === 'video') assert.equal(suggestion.id, 'youtube:moto');
    if (suggestion.type === 'guide') assert.equal(suggestion.id, 'guide-moto');
    if (suggestion.count != null) assert.equal(suggestion.count, 2);
  }
  const recovery = queryAssistance(catalog, {...params, q: 'ralentir'}).suggestions;
  assert.equal(recovery.length, 1);
  assert.equal(recovery[0].count, 2);
  assert.equal(recovery[0].filters.discipline, 'motorcycle');
  assert.equal(queryAssistance(catalog, {...params, q: 'ralentir', platform: 'tiktok'}).suggestions.length, 0);
  for (const topic of recommendCatalog(catalog, params).topics) assert.equal(topic.filters.discipline, 'motorcycle');
});

test('unknown API disciplines fail closed even through count and empty suggestion routes', () => {
  const catalog = fixture(), params = {discipline: 'unknown'};
  for (const run of [() => searchResources(catalog, params), () => searchResources(catalog, params, {countOnly: true}),
    () => searchCatalog(catalog, params), () => suggestCatalog(catalog, params), () => queryAssistance(catalog, params),
    () => discoveryCatalog(catalog, params), () => recommendCatalog(catalog, params)]) assert.throws(run, /Discipline invalide/);
  for (const discipline of ['', 'all', 'any', '*']) assert.equal(searchResources(catalog, {discipline}).total, 8);
});
