// Called by tests_search_assistance.py with isolated fixture data over stdin.
import fs from 'node:fs';
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const source = fs.readFileSync(new URL('./public/catalog-worker.js', import.meta.url), 'utf8');
const {prepareCatalog, queryAssistance, searchResources, suggestCatalog} =
  await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const catalog = prepareCatalog(data.payload);
catalog.discovery = data.config;
process.stdout.write(JSON.stringify(data.params.map(params => ({
  search: searchResources(catalog, params), assist: queryAssistance(catalog, params).suggestions,
  suggest: suggestCatalog(catalog, params).suggestions,
}))));
