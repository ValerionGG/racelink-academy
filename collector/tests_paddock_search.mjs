// Run: node --test collector/tests_paddock_search.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareCatalog, searchResources, estimateLevel} from '../site/catalog-worker.js';

const video = (id, title, generation, extra = {}) => ({
  id: `youtube:${id}`, url: `https://youtu.be/${id}`, title, platform: 'youtube', creator: 'Atelier', language: 'fr',
  category: 'mechanics', level: 'unknown', tags: [], license: 'unknown', duration_seconds: 300, thumbnail_url: 'https://i.ytimg.com/x.jpg',
  review_status: 'candidate', domain_scope: 'automotive_adjacent', pedagogical_format: 'tutorial',
  automotive: {vehicles: [{make: 'Renault', model: 'Clio', generation, engine: '', body_type: '', fuel_type: '', year_from: null, year_to: null, evidence: title, status: 'inferred_from_unambiguous_model'}],
    tasks: ['oil_change'], systems: [], specifications: [], status: 'metadata_extraction'}, ...extra});
const guide = {id: 'guide-oil-change', title: 'Préparer une vidange', task: 'oil_change', language: 'fr', category: 'mechanics', level: 'beginner', platform: 'racelink', license: 'unknown', domain_scope: 'automotive_adjacent', resource_type: 'guide', guide: {title: 'Préparer une vidange'}};
const catalog = () => prepareCatalog({version: 1, generated_at: '2026-11-08', stats: {}, guides: [guide], items: [
  video('a', 'A vidange Clio 2', 'II', {thumbnail_url: '', duration_seconds: null, pedagogical_format: 'unspecified'}),
  video('b', 'B vidange Clio 3', 'III'),
  video('c', 'C vidange Clio 3', 'III'),
  video('d', 'C vidange  clio 3', 'III'),
  video('e', 'E vidange Clio 5', 'V'),
]});
const params = {q: 'vidange clio', format: 'all', per_page: 24};

test('a generic guide is surfaced when the car comes from the query', () => {
  const result = searchResources(catalog(), params);
  assert.equal(result.total_guides, 1);
  assert.equal(result.items[0].id, 'guide-oil-change');
});
test('an explicit vehicle filter still hides generic guides', () => {
  assert.equal(searchResources(catalog(), {...params, make: 'Renault', model: 'Clio'}).total_guides, 0);
});
test('generations are offered with counts when the model is known', () => {
  const {facets} = searchResources(catalog(), params);
  assert.deepEqual(facets.generation, [{value: 'III', count: 2}, {value: 'II', count: 1}, {value: 'V', count: 1}]);
});
test('same title from the same creator is listed once', () => {
  const titles = searchResources(catalog(), params).items.map(item => item.title).filter(title => /clio 3/i.test(title));
  assert.equal(titles.length, 2);
});
test('well-documented tutorials rank before bare listings', () => {
  const videos = searchResources(catalog(), {...params, format: 'video'}).items;
  assert.equal(videos.at(-1).id, 'youtube:a');
});

test('estimates a level only from a known job or an explicit title', () => {
  const job = (title, ...tasks) => estimateLevel({title, automotive: {tasks}});
  assert.equal(job('Clio 4', 'oil_change'), 'beginner');
  assert.equal(job('Clio 4', 'oil_change', 'brake_pads'), 'intermediate');
  assert.equal(job('Clio 4', 'belts'), 'intermediate');
  assert.equal(job('Remplacement courroie de distribution', 'belts'), 'advanced');
  assert.equal(job('Le sim racing pour débutants'), 'beginner');
  assert.equal(job('Trajectoire au Mans'), null);
  const [known, unknown] = prepareCatalog({items: [
    video('a', 'Vidange', 'V', {level: 'advanced', level_status: 'editorial_estimate'}),
    video('b', 'Vidange', 'V', {level: 'unknown', level_status: 'not_assessed'}),
  ], guides: []}).items;
  assert.deepEqual([known.level, known.level_status], ['advanced', 'editorial_estimate']);
  assert.deepEqual([unknown.level, unknown.level_status], ['beginner', 'estimated_from_task']);
});
