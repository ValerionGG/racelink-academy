// Shared Paddock navigation for the pages that live outside the main application.
const ui = ['en', 'es'].includes(new URLSearchParams(location.search).get('ui')) ? new URLSearchParams(location.search).get('ui') : 'fr';
const t = (fr, en, es) => ({fr, en, es})[ui];
const suffix = ui === 'fr' ? '' : `ui=${ui}`;
const link = (path, query = '') => { const search = [query, suffix].filter(Boolean).join('&'); return search ? `${path}?${search}` : path; };
const page = document.documentElement.dataset.annex;
const items = [
  [link('./'), t('Accueil', 'Home', 'Inicio'), ''],
  [link('./', 'browse=1&language=fr'), t('Bibliothèque', 'Library', 'Biblioteca'), ''],
  [link('./', 'view=paths'), t('Parcours', 'Paths', 'Itinerarios'), ''],
  [link('./formats-courts.html'), t('Formats courts', 'Short videos', 'Vídeos cortos'), 'social'],
  [link('./vehicules.html'), t('Voitures', 'Cars', 'Coches'), 'atlas,clio,3d'],
  [link('./', 'view=faq'), t('Aide & FAQ', 'Help & FAQ', 'Ayuda y FAQ'), ''],
];
const current = sections => sections.split(',').includes(page) ? ' aria-current="page"' : '';
const bar = document.createElement('div');
bar.className = 'pd-bar';
bar.innerHTML = `<a class="pd-brand" href="${link('./')}" aria-label="RaceLink Academy"><svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#e8141f"/><path d="M9 23V9h8.5a4.5 4.5 0 0 1 1.4 8.8L23 23h-4.6l-3.6-5H13v5Zm4-8.6h4.2a1.6 1.6 0 0 0 0-3.2H13Z" fill="#fff"/></svg><span>RACELINK<small>ACADEMY</small></span></a>
  <nav aria-label="${t('Navigation principale', 'Main navigation', 'Navegación principal')}">${items.map(([href, label, sections]) => `<a href="${href}"${current(sections)}>${label}</a>`).join('')}</nav>
  <div class="pd-bar-theme" data-theme-controls role="group"><button type="button" data-theme-choice="light"><span data-theme-label></span></button><button type="button" data-theme-choice="dark"><span data-theme-label></span></button></div>`;
document.body.prepend(bar);
const tabs = document.createElement('nav');
tabs.className = 'pd-tabs';
tabs.setAttribute('aria-label', t('Navigation mobile', 'Mobile navigation', 'Navegación móvil'));
tabs.innerHTML = [items[0], items[1], items[2], items[3], items[5]].map(([href, label, sections]) => `<a href="${href}"${current(sections)}>${label.split(' ')[0]}</a>`).join('');
document.body.append(tabs);
window.RaceLinkTheme?.refresh();
