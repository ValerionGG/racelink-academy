// Precomputes the catalogue answers the home page needs, so it renders before the full catalogue loads.
// The site falls back to the catalogue worker for any other request, or if the digest does not match.
import fs from 'node:fs';

const root = new URL('../site/', import.meta.url);
const read = path => JSON.parse(fs.readFileSync(new URL(path, root), 'utf8'));
const worker = await import(new URL('catalog-worker.js', root));
const catalog = worker.prepareCatalog(read('catalog/catalog.json'));
catalog.discovery = read('discovery-catalog.json');

const FEATURED = encodeURIComponent('youtube:-1amcyQPvL4');
const homeList = 'make=&model=&generation=&engine=&body_type=&fuel_type=&year=&task=&system=&spec=&q=&category=&discipline=&domain=&level=&language=fr&platform=&format=all&content_format=&duration=&transcript=&license=&sort=relevance&page=1&per_page=18';
const preview = 'q=vidange+clio&language=fr&category=mechanics&per_page=3';
const urls = [
  '/aide/api/stats', '/aide/api/discovery', `/aide/api/videos/${FEATURED}`,
  '/aide/api/resources?language=fr&per_page=1', `/aide/api/resources?${preview}`, `/aide/api/resources?${homeList}`,
  '/aide/api/vehicle-options?make=&model=&generation=&engine=&body_type=&fuel_type=&year=',
  '/aide/api/recommendations?language=fr&format=all',
];

function answer(path) {
  const url = new URL(path, 'https://snapshot.invalid/');
  const route = decodeURIComponent(url.pathname).replace(/^.*\/api\//, '/api/');
  if (route === '/api/stats') return worker.catalogStats(catalog);
  if (route === '/api/resources') return worker.searchResources(catalog, url.searchParams);
  if (route === '/api/discovery') return worker.discoveryCatalog(catalog, url.searchParams);
  if (route === '/api/vehicle-options') return worker.vehicleOptions(catalog, url.searchParams);
  if (route === '/api/recommendations') return worker.recommendCatalog(catalog, url.searchParams);
  if (route.startsWith('/api/resources/guide/')) return worker.guideDetail(catalog, route.slice('/api/resources/guide/'.length));
  if (route.startsWith('/api/videos/')) return worker.videoDetail(catalog, route.slice('/api/videos/'.length));
  throw new Error(`No snapshot route for ${path}`);
}

const responses = Object.fromEntries(urls.map(path => [path, answer(path)]));
for (const {value} of responses[`/aide/api/resources?${preview}`].facets.generation) {
  const path = `/aide/api/resources?${preview}&generation=${encodeURIComponent(value)}`;
  responses[path] = answer(path);
}
for (const guide of catalog.guides) {
  const path = `/aide/api/resources/guide/${encodeURIComponent(guide.id)}`;
  responses[path] = answer(path);
}

const {catalog_sha256} = read('catalog/config.json');
const output = JSON.stringify({catalog_sha256, responses});
fs.writeFileSync(new URL('catalog/home-snapshot.json', root), output);
console.log(`home-snapshot.json: ${Object.keys(responses).length} responses, ${Math.round(output.length / 1024)} KB`);
