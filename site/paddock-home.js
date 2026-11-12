// Home sections of the Paddock design. Counts come from the catalogue; links use the shared search parameters.
import {tracks} from './tracks.js';

const LARGE = [
  ['mechanics', './assets/photos/service.jpg', ['Mécanique','Mechanics','Mecánica'], ['Entretien et réparations.','Maintenance and repairs.','Mantenimiento y reparaciones.']],
  ['driving', './clio-v/photos/clio-cockpit.webp', ['Pilotage','Driving','Pilotaje'], ['Trajectoire et maîtrise.','Racing line and control.','Trazada y control.']],
  ['simracing', './assets/photos/simracing.jpg', ['Sim racing','Sim racing','Sim racing'], ['Réglages et pratique.','Setup and practice.','Ajustes y práctica.']],
  ['engineering', './assets/photos/diagnostics.jpg', ['Ingénierie','Engineering','Ingeniería'], ['Data et technique.','Data and technique.','Datos y técnica.']],
];
const SMALL = [
  ['media', ['Photo & vidéo','Photo & video','Foto y vídeo'], ['Raconter la course.','Tell the story of racing.','Contar la carrera.'], '<rect x="3" y="6" width="18" height="13" rx="2"/><circle cx="12" cy="12.5" r="3.5"/><path d="M8 6l1.5-2h5L16 6"/>'],
  ['business', ['Business','Business','Negocio'], ['Sponsoring et projets.','Sponsorship and projects.','Patrocinio y proyectos.'], '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'],
  ['career', ['Métiers','Careers','Profesiones'], ['Trouver sa voie.','Find your path.','Encontrar tu camino.'], '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V4h6v3M3 13h18"/>'],
  ['fitness', ['Préparation','Preparation','Preparación'], ['Le pilote aussi progresse.','Drivers train too.','El piloto también progresa.'], '<path d="M3 12h4l3-7 4 14 3-7h4"/>'],
];
const PATHS = [['mechanics',['Mécanique','Mechanics','Mecánica']],['driving',['Pilotage','Driving','Pilotaje']],['simracing',['Sim racing','Sim racing','Sim racing']],['engineering',['Ingénierie','Engineering','Ingeniería']]];
const DISCIPLINES = [
  ['motorcycle', ['Moto','Motorcycle','Moto']],
  ['karting', ['Karting','Karting','Karting']],
  ['drift', ['Drift','Drift','Drift']],
  ['motorsport', ['Motorsport','Motorsport','Automovilismo']],
  ['simracing', ['Sim racing','Sim racing','Sim racing']],
  ['racelink', ['Guides RaceLink','RaceLink guides','Guías RaceLink']],
];

// A new discipline starts a fresh search, retaining only the visitor's languages.
export function disciplineHref(id, language = 'fr', ui = 'fr') {
  if (!DISCIPLINES.some(([value]) => value === id)) throw new TypeError('Unknown discipline');
  const params = new URLSearchParams({browse:'1'});
  if (id === 'racelink') { params.set('format', 'guide'); params.set('platform', 'racelink'); }
  else params.set('discipline', id);
  if (language) params.set('language', language);
  if (ui && ui !== 'fr') params.set('ui', ui);
  return `?${params}`;
}
const POSTERS = [[/oil|huile|vidange/,'oil'],[/wiper|essuie/,'wipers'],[/wheel|tire|tyre|pneu/,'wheel'],[/batter/,'battery'],[/fuse|fusible/,'fuses'],[/light|bulb|lamp|phare/,'lighting'],[/fuel|carburant/,'fuel'],[/diag|obd|code|warning|voyant/,'diagnostics']];
const SHORTS_SHOWN = 14, PER_POSTER = 2, FEATURED_VIDEO = 'youtube:-1amcyQPvL4';

const IMAGE = key => key.includes('/') ? key : `./assets/photos/${key}.jpg`;
const CLIO = name => `./clio-v/photos/${name}.webp`;
const POOLS = {oil:['oil',CLIO('clio-engine')], diagnostics:['diagnostics',CLIO('clio-cockpit')], driving:['driving',CLIO('clio-cockpit')], wheel:['wheel',CLIO('clio-rear')],
  service:['service','identification',CLIO('clio-engine'),CLIO('clio-bleu')], simracing:['simracing']};
export const poster = item => {
  const subject = `${(item.s || []).join(' ')} ${item.t || ''}`.toLowerCase();
  const key = POSTERS.find(([pattern]) => pattern.test(subject))?.[1] || (item.c === 'driving' ? 'driving' : item.c === 'simracing' ? 'simracing' : 'service');
  const pool = POOLS[key] || [key];
  let hash = 0;
  for (const char of String(item.id || item.t || '')) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return IMAGE(pool[hash % pool.length]);
};
const PATH_TITLES = {mechanics:['Comprendre sa voiture','Understand your car','Entender tu coche'], driving:['Freiner plus tard','Brake later','Frenar más tarde'], simracing:['Régler son simulateur','Set up your simulator','Ajustar tu simulador'], engineering:['Lire la télémétrie','Read telemetry','Leer la telemetría']};
const CLOCK = '\\d{1,2}:\\d{2}(?::\\d{2})?';
const CHAPTER = new RegExp(`(${CLOCK})\\s*[-–—:)\\]]?\\s*([^\\n]*?)(?=\\s*${CLOCK}\\s*[-–—:)\\]]?\\s|\\n|$)`, 'g');
// Chapters published by the author in the video description. Nothing is inferred.
const LEVELS = {
  beginner: [1, 'Débutant', 'Beginner', 'Principiante'],
  intermediate: [2, 'Intermédiaire', 'Intermediate', 'Intermedio'],
  advanced: [3, 'Avancé', 'Advanced', 'Avanzado'],
  all: [0, 'Tous niveaux', 'All levels', 'Todos los niveles'],
};
export function levelBadge(item, t) {
  const bars = '<span class="pd-level" aria-hidden="true"><i></i><i></i><i></i></span>';
  const level = String(item.level_status || '').includes('unknown') ? null : LEVELS[item.level];
  if (!level) return `<span class="pd-card-level none" title="${t('Niveau non évalué', 'Level not assessed', 'Nivel sin evaluar')}">${bars}</span>`;
  const [rank, ...names] = level, label = t(...names);
  const hint = String(item.level_status || '').startsWith('estimated_from') ? t('Niveau estimé d’après l’intervention', 'Level estimated from the job', 'Nivel estimado según la intervención') : label;
  return `<span class="pd-card-level" data-l="${rank}" title="${hint}">${bars}${label}</span>`;
}
// The RaceLink guides are all first-step jobs, except reading a fault diagnosis.
export const guideBadge = (guide, t) => levelBadge({level: guide.task === 'diagnostics' ? 'intermediate' : 'beginner', level_status: 'estimated_from_task'}, t);
export function parseChapters(description) {
  const chapters = [];
  for (const [, clock, label] of String(description || '').matchAll(CHAPTER)) {
    const seconds = clock.split(':').reduce((total, part) => total * 60 + Number(part), 0), title = label.replace(/^[\s\-–—:|•]+/u, '').trim();
    if (title.length > 1 && (!chapters.length || seconds > chapters.at(-1).seconds)) chapters.push({clock, seconds, title: title.slice(0, 90)});
  }
  return chapters.length >= 3 ? chapters : [];
}
// ponytail: a few posters repeat by topic; live thumbnails expire, replace when the collector stores durable ones.
export function pickShorts(items, limit = SHORTS_SHOWN, perPoster = PER_POSTER) {
  const french = items.filter(item => item.l === 'fr' && item.t);
  const seen = new Map(), picked = [];
  for (const item of french) {
    const key = poster(item), used = seen.get(key) || 0;
    if (used >= perPoster) continue;
    seen.set(key, used + 1); picked.push({...item, poster:key});
    if (picked.length === limit) break;
  }
  return picked;
}

export function createPaddockHome({$, escape, t, getUi, getContentLanguage, getJson, cardMarkup, setImageFallback, catName, fmtDuration, storage}) {
  let stats = null, frenchCounts = {}, shorts = [], faq = [], taskNames = {}, previewGeneration = '', previewChoices = [], socialTotals = null, featured = null;
  const previewFilters = {language:'fr', category:'mechanics', level:'', transcript:'', license:'', platform:''};
  const pick = values => t(...values);
  const number = value => Number(value || 0).toLocaleString(getUi());
  const count = id => stats?.facets?.category?.find(entry => entry.value === id)?.count || 0;
  const progress = () => { try { return JSON.parse(localStorage.getItem('rl-library-progress') || '{}'); } catch { return {}; } };
  const contentLanguage = () => typeof getContentLanguage === 'function' ? getContentLanguage() : new URLSearchParams(location.search).get('language') ?? (location.search ? '' : 'fr');
  function disciplines() {
    document.querySelectorAll('[data-discipline-nav]').forEach(nav => {
      nav.setAttribute('aria-label', t('Disciplines et guides RaceLink','Disciplines and RaceLink guides','Disciplinas y guías RaceLink'));
      nav.innerHTML = DISCIPLINES.map(([id, name]) => `<a data-discipline-link="${id}" class="${id === 'racelink' ? 'pd-discipline-guide' : ''}" href="${escape(disciplineHref(id, contentLanguage(), getUi()))}">${escape(pick(name))}${id === 'racelink' ? '<span aria-hidden="true">→</span>' : ''}</a>`).join('');
    });
  }
  function refreshDisciplineLink(event) {
    const link = event.target.closest?.('a[data-discipline-link]');
    if (link) link.setAttribute('href', disciplineHref(link.dataset.disciplineLink, contentLanguage(), getUi()));
  }

  function ticker() {
    const language = stats?.facets?.language?.find(entry => entry.value === 'fr')?.count, platform = id => stats?.facets?.platform?.find(entry => entry.value === id)?.count || 0;
    const text = [`<span><i>●</i> ${t('Catalogue','Catalogue','Catálogo')} · <b>${number(stats?.total_videos)}</b> ${t('vidéos','videos','vídeos')}</span>`,
      `<span><b>${number(language)}</b> ${t('en français','in French','en francés')}</span>`,
      ...LARGE.map(([id,,name]) => `<span>${escape(pick(name))} <b>${number(count(id))}</b></span>`),
      `<span><b>${number(platform('tiktok'))}</b> TikTok · <b>${number(platform('instagram'))}</b> Instagram</span>`,
      `<span><b>11</b> ${t('guides RaceLink','RaceLink guides','guías RaceLink')}</span>`, `<span><b>8</b> ${t('parcours guidés','guided paths','itinerarios')}</span>`].join('');
    $('#pd-ticker').innerHTML = text + text;
  }
  function subjects() {
    const badge = id => stats ? `<span class="pd-subject-count">${number(count(id))}</span>` : '';
    const fr = id => frenchCounts[id] ? `<span class="pd-fr">${number(frenchCounts[id])} ${t('en français','in French','en francés')}</span>` : '';
    if (stats) $('#pd-subjects-kick').textContent = `8 ${t('sujets','topics','temas')} · ${number(stats.total_videos)} ${t('vidéos','videos','vídeos')}`;
    $('#pd-subjects-grid').innerHTML = LARGE.map(([id, src, name, hint]) => `<button type="button" class="pd-subject pd-subject-photo" data-entry-category="${id}"><img src="${src}" alt="" loading="lazy" decoding="async">${badge(id)}<strong>${escape(pick(name))}</strong><small>${escape(pick(hint))}</small>${fr(id)}</button>`).join('') +
      SMALL.map(([id, name, hint, path]) => `<button type="button" class="pd-subject" data-entry-category="${id}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">${path}</svg>${badge(id)}<strong>${escape(pick(name))}</strong><small>${escape(pick(hint))}</small></button>`).join('');
  }
  function shortsRail() {
    const root = $('#pd-shorts-rail');
    root.closest('section').hidden = !shorts.length;
    if (socialTotals) { $('#pd-shorts-kick').textContent = `TikTok · Instagram · ${number(socialTotals.french)} ${t('en français','in French','en francés')}`; $('#pd-shorts-all').textContent = `${t('Voir les','See all','Ver los')} ${number(socialTotals.total)} →`; }
    root.innerHTML = shorts.map(item => {
      const topic = taskNames[item.s?.[0]]?.[getUi()] || (item.c ? catName(item.c) : ''), author = String(item.a || '').replace(/^@/, '');
      return `<article class="pd-short"><button type="button" data-video="${escape(item.id)}" aria-label="${escape(item.t)}"><img src="${item.poster}" alt="" loading="lazy" decoding="async"><span class="pd-short-top"><span class="pd-plat">${item.p === 'instagram' ? 'INSTA' : 'TIKTOK'}</span><span class="pd-plat">FR</span></span><span class="pd-short-copy">${topic ? `<span class="pd-short-tag">${escape(topic)}</span>` : ''}<strong dir="auto">${escape(item.t)}</strong><small dir="auto"><i aria-hidden="true">${escape(author.charAt(0).toUpperCase())}</i>${escape(author)}</small></span></button></article>`;
    }).join('');
  }
  function paths() {
    const done = progress();
    $('#pd-paths-grid').innerHTML = PATHS.map(([id, name]) => {
      const steps = tracks[id] || [], finished = steps.filter((_, index) => done[`${id}:${index}`]).length;
      const state = finished ? t(`Étape ${Math.min(finished + 1, steps.length)}/${steps.length}`,`Step ${Math.min(finished + 1, steps.length)}/${steps.length}`,`Paso ${Math.min(finished + 1, steps.length)}/${steps.length}`) : t('À commencer','Not started','Sin empezar');
      return `<button type="button" class="pd-path" data-path="${id}"><span class="pd-path-kind">${escape(pick(name))}</span><strong>${escape(pick(PATH_TITLES[id] || name))}</strong><span class="pd-sectors" aria-hidden="true">${steps.map((_, index) => `<i class="${done[`${id}:${index}`] ? 'on' : ''}"></i>`).join('')}</span><small><span>${steps.length} ${t('étapes','steps','pasos')}</span><span>${state}</span></small></button>`;
    }).join('');
  }
  function help() {
    const counts = new Map();
    faq.forEach(item => { if (item.category) counts.set(item.category, 1); });
    $('#pd-help-kick').textContent = `${t('Aide & FAQ','Help & FAQ','Ayuda y FAQ')}${faq.length ? ` · ${faq.length} questions` : ''}`;
    $('#pd-help-cats').innerHTML = [...counts.keys()].map(name => `<button type="button" data-view="faq">${escape(name)}</button>`).join('');
    const root = $('#pd-faq');
    root.innerHTML = faq.slice(0, 6).map(item => `<details id="pd-faq-${escape(item.id)}"><summary><span><small>${escape(item.category || '')}</small>${escape(item.question)}</span></summary><p>${escape(item.answer)}</p></details>`).join('');
  }
  function copy() {
    const labels = {
      kick:t('La bibliothèque ouverte du sport auto','The open library of motorsport','La biblioteca abierta del motor'),
      headline:t('Du garage<br><span>à la</span> piste.','From garage<br><span>to</span> track.','Del taller<br><span>a la</span> pista.'),
      intro:t('Mécanique, pilotage, sim racing, ingénierie, métiers. Les meilleurs tutos du web, triés et expliqués, en français d’abord.','Mechanics, driving, sim racing, engineering, careers. The best tutorials on the web, sorted and explained.','Mecánica, pilotaje, sim racing, ingeniería, profesiones. Los mejores tutoriales de la web, ordenados y explicados.'),
      videos:t('tutos vidéo','video tutorials','tutoriales'),guides:t('guides RaceLink','RaceLink guides','guías RaceLink'),paths:t('parcours','learning paths','itinerarios'),
      subject:t('Sujet','Topic','Tema'),allSubjects:t('Tous les sujets','All topics','Todos los temas'),car:t('Ma voiture','My car','Mi coche'),optional:t('Ajouter','Add','Añadir'),
      subjectsKick:t('8 sujets','8 topics','8 temas'),subjectsTitle:t('Choisis ton sujet','Pick your topic','Elige tu tema'),library:t('Toute la bibliothèque →','The whole library →','Toda la biblioteca →'),
      disciplineTitle:t('Explorer par discipline','Explore by discipline','Explorar por disciplina'),
      shortsKick:t('TikTok · Instagram','TikTok · Instagram','TikTok · Instagram'),shortsTitle:t('Formats courts','Short videos','Vídeos cortos'),shortsHint:t('Une astuce en moins d’une minute, dans son format d’origine.','A tip in under a minute, in its original format.','Un consejo en menos de un minuto, en su formato original.'),shortsAll:t('Tout voir →','See all →','Ver todo →'),
      pathsKick:t('8 parcours guidés','8 guided paths','8 itinerarios'),pathsTitle:t('Apprends étape par étape','Learn step by step','Aprende paso a paso'),pathsAll:t('Tous les parcours →','All paths →','Todos los itinerarios →'),
      bonusKick:t('En plus','Going further','Además'),bonusTitle:t('Ta voiture, en détail','Your car, in detail','Tu coche, en detalle'),bonusHint:t('Des tutos ciblés sur ton modèle, un atlas des voitures courantes et un atelier 3D.','Tutorials for your model, an atlas of common cars and a 3D workshop.','Tutoriales para tu modelo, un atlas de coches comunes y un taller 3D.'),
      carTitle:t('Des tutos pour ta voiture','Tutorials for your car','Tutoriales para tu coche'),carHint:t('Marque, modèle, génération, moteur : la bibliothèque se cale sur ta voiture.','Make, model, generation, engine: the library adapts to your car.','Marca, modelo, generación, motor: la biblioteca se adapta a tu coche.'),
      atlasHint:t('Photos, habitacles, versions et visites 360° constructeur.','Photos, interiors, versions and manufacturer 360° tours.','Fotos, interiores, versiones y visitas 360° del fabricante.'),
      workshopTitle:t('Comprendre ta voiture','Understand your car','Entiende tu coche'),workshopHint:t('Chaque système expliqué, avec les bons tutos.','Every system explained, with the right tutorials.','Cada sistema explicado, con los tutoriales adecuados.'),
      footLearn:t('Apprendre','Learn','Aprender'),footLibrary:t('Bibliothèque','Library','Biblioteca'),footCar:t('Ta voiture','Your car','Tu coche'),footAtlas:t('Atlas des voitures','Car atlas','Atlas de coches'),footWorkshop:t('Comprendre ta voiture','Understand your car','Entiende tu coche'),
      navTopics:t('Sujets','Topics','Temas'),goLabel:t('Chercher','Search','Buscar'),askLabel:t('Qu’est-ce que tu veux apprendre ?','What do you want to learn?','¿Qué quieres aprender?'),carOptional:t('Ma voiture · optionnel','My car · optional','Mi coche · opcional'),chipTelemetry:t('Lire la télémétrie','Read telemetry','Leer la telemetría'),chipCareer:t('Devenir mécanicien','Become a mechanic','Ser mecánico'),tabSearch:t('Chercher','Search','Buscar'),tabShorts:t('Courts','Shorts','Cortos'),tabHelp:t('Aide','Help','Ayuda'),academy:t('Masterclass Focus ↗','Focus Masterclass ↗','Masterclass Focus ↗'),
      previewKick:t('Bibliothèque','Library','Biblioteca'),previewTitle:t('Trouve le bon tuto','Find the right tutorial','Encuentra el tutorial'),previewHint:t('Les filtres restent visibles, chaque critère se retire d’un clic, et la recherche comprend les modèles de voiture.','Filters stay visible, each one clears in a click, and search understands car models.','Los filtros siguen visibles, cada criterio se quita con un clic y la búsqueda entiende los modelos de coche.'),
      ficheKick:t('La fiche tuto','The tutorial page','La ficha'),ficheTitle:t('Comprendre<br>avant de regarder','Understand before you watch','Entender antes de ver'),ficheHint:t('Chapitres, transcription, tes notes et la source, sur la même page. Tu sais ce qu’il y a dans la vidéo avant de l’ouvrir.','Chapters, transcript, your notes and the source on one page. You know what is in a video before opening it.','Capítulos, transcripción, tus notas y la fuente en la misma página. Sabes qué hay en el vídeo antes de abrirlo.'),
      faqAll:t('Toute l’aide →','All help →','Toda la ayuda →'),
    };
    document.querySelectorAll('[data-pd]').forEach(el => { const value = labels[el.dataset.pd]; if (value) el.innerHTML = value; });
  }
  const PREVIEW_KEYS = ['language', 'category', 'level', 'transcript', 'license', 'platform'];
  const FILTER_VALUES = {language:'fr', level:'beginner', transcript:'available', license:'open'};
  function filterLabel(key, value) {
    if (key === 'category') return catName(value);
    if (key === 'platform') return platformLabel(value);
    return {language:t('Français','French','Francés'), level:t('Débutant','Beginner','Principiante'), transcript:t('Avec transcription','With transcript','Con transcripción'), license:t('Licence libre','Open licence','Licencia libre')}[key];
  }
  const platformLabel = value => ({youtube:'YouTube', tiktok:'TikTok', instagram:'Instagram', dailymotion:'Dailymotion', vimeo:'Vimeo', facebook:'Facebook', racelink:'RaceLink'})[value] || value;
  async function libraryPreview() {
    const root = $('#pd-lib-preview');
    const fields = {q:'vidange clio'};
    PREVIEW_KEYS.forEach(key => { if (previewFilters[key]) fields[key] = previewFilters[key]; });
    fields.per_page = '3';
    if (previewGeneration) fields.generation = previewGeneration;
    const data = await getJson(`/aide/api/resources?${new URLSearchParams(fields)}`);
    if (!previewGeneration) previewChoices = data.facets?.generation || [];
    const rows = (key, label, entries, name) => `<div class="pd-lib-facet"><span class="pd-label">${label}</span>${entries.slice(0, 3).map(entry => `<button type="button" data-preview-set="${key}" data-value="${escape(entry.value)}" class="${previewFilters[key] === entry.value ? 'on' : ''}">${escape(name(entry.value))}<small>${number(entry.count)}</small></button>`).join('')}</div>`;
    const toggle = key => `<button type="button" class="pd-toggle ${previewFilters[key] ? 'on' : ''}" data-preview-toggle="${key}" aria-pressed="${Boolean(previewFilters[key])}"><span>${filterLabel(key)}</span><i></i></button>`;
    const chips = PREVIEW_KEYS.filter(key => previewFilters[key]).map(key => `<button type="button" class="pd-chip-x" data-preview-clear="${key}">${escape(filterLabel(key, previewFilters[key]))}</button>`).join('');
    const tabs = [[t('Tout','All','Todo'), data.total], [t('Vidéos','Videos','Vídeos'), data.total_videos], [t('Guides','Guides','Guías'), data.total_guides], [t('Formats courts','Short videos','Vídeos cortos'), (data.facets?.platform || []).filter(entry => ['tiktok','instagram'].includes(entry.value)).reduce((sum, entry) => sum + entry.count, 0)]];
    root.innerHTML = `<aside class="pd-lib-side">${rows('category', t('Sujet','Topic','Tema'), data.facets?.category || [], catName)}${rows('platform', t('Plateforme','Platform','Plataforma'), data.facets?.platform || [], platformLabel)}<div class="pd-lib-facet"><span class="pd-label">${t('Contenu','Content','Contenido')}</span>${['language','level','transcript','license'].map(toggle).join('')}</div><button type="button" class="pd-more" data-query="vidange clio">${t('Toute la recherche →','Full search →','Búsqueda completa →')}</button></aside>
      <div class="pd-lib-main"><div class="pd-lib-top"><h3>« vidange clio »</h3><span class="pd-label">${t('Tri : pertinence','Sort: relevance','Orden: relevancia')}</span></div>
      <div class="pd-lib-tabs">${tabs.map(([label, count], index) => `<span class="${index ? '' : 'on'}">${label}<small>${number(count)}</small></span>`).join('')}</div>
      ${chips ? `<div class="pd-lib-chips"><span class="pd-label">${t('Critères','Filters','Criterios')}</span>${chips}</div>` : ''}
      ${previewChoices.length > 1 ? `<div class="generation-choices"><span>${t('Quelle Clio ?','Which Clio?','¿Qué Clio?')}</span>${[{value:'', label:t('Toutes','All','Todas')}, ...previewChoices.map(choice => ({...choice, label:choice.value}))].map(choice => `<button type="button" data-preview-generation="${escape(choice.value)}" aria-pressed="${previewGeneration === choice.value}">${escape(choice.label)}${choice.count ? ` <small>${choice.count}</small>` : ''}</button>`).join('')}</div>` : ''}
      <div class="video-grid pd-lib-grid">${(data.items || []).length ? data.items.map(cardMarkup).join('') : `<div class="empty"><strong>${t('Aucun résultat','No results','Sin resultados')}</strong><p>${t('Retire un critère pour élargir.','Remove a filter to widen the search.','Quita un criterio para ampliar.')}</p></div>`}</div></div>`;
    setImageFallback(root);
  }
  function previewClick(event) {
    const set = event.target.closest('[data-preview-set]'), toggle = event.target.closest('[data-preview-toggle]'), clear = event.target.closest('[data-preview-clear]'), generation = event.target.closest('[data-preview-generation]');
    if (set) previewFilters[set.dataset.previewSet] = previewFilters[set.dataset.previewSet] === set.dataset.value ? '' : set.dataset.value;
    else if (toggle) previewFilters[toggle.dataset.previewToggle] = previewFilters[toggle.dataset.previewToggle] ? '' : FILTER_VALUES[toggle.dataset.previewToggle];
    else if (clear) previewFilters[clear.dataset.previewClear] = '';
    else if (generation) previewGeneration = generation.dataset.previewGeneration;
    else return;
    if (!generation) previewGeneration = '';
    libraryPreview().catch(() => {});
  }
  function ficheTab(name) {
    document.querySelectorAll('[data-fiche-tab]').forEach(tab => tab.setAttribute('aria-selected', String(tab.dataset.ficheTab === name)));
    document.querySelectorAll('[data-fiche-pane]').forEach(pane => { pane.hidden = pane.dataset.fichePane !== name; });
  }
  async function fichePreview() {
    const root = $('#pd-fiche-preview');
    const result = await getJson(`/aide/api/videos/${encodeURIComponent(FEATURED_VIDEO)}`);
    const video = result.video || result.item || result, all = parseChapters(video.description), chapters = all.slice(0, 6);
    if (!video?.id || !chapters.length) return;
    featured = video;
    const tabs = [['chapters',t('Chapitres','Chapters','Capítulos')],['transcript',t('Transcription','Transcript','Transcripción')],['notes',t('Mes notes','My notes','Mis notas')],['source',t('Source','Source','Fuente')]];
    const specs = [[t('Durée','Duration','Duración'),fmtDuration(video.duration_seconds)],[t('Niveau','Level','Nivel'),t('Débutant','Beginner','Principiante')],[t('Sujet','Topic','Tema'),catName(video.category)],[t('Chapitres','Chapters','Capítulos'),String(all.length)]];
    const url = new URL(location.href); url.search = ''; url.hash = ''; url.searchParams.set('video', video.id);
    root.innerHTML = `<div class="pd-player" style="background-image:url('${escape(String(video.thumbnail_url || '').replace(/'/g, '%27'))}')"><button type="button" class="pd-big-play" data-video="${escape(video.id)}" aria-label="${t('Regarder ici','Watch here','Ver aquí')}"><svg viewBox="0 0 10 12" aria-hidden="true"><path d="M0 0l10 6-10 6z"/></svg></button><div class="pd-player-cap"><strong dir="auto">${escape(video.title)}</strong><span dir="auto">${escape(video.creator || '')} · YouTube · ${fmtDuration(video.duration_seconds)} · ${t('Français','French','Francés')}</span></div></div>
      <div class="pd-fiche-side"><div class="pd-fiche-tabs" role="tablist">${tabs.map(([key,label],i) => `<button type="button" role="tab" data-fiche-tab="${key}" aria-selected="${!i}">${label}</button>`).join('')}</div>
      <div class="pd-specs">${specs.map(([label,value]) => `<div><span class="pd-label">${label}</span><b>${escape(value)}</b></div>`).join('')}</div>
      <div data-fiche-pane="chapters"><ol class="pd-chapters-list">${chapters.map(chapter => `<li><button type="button" data-video="${escape(video.id)}"><b>${escape(chapter.clock)}</b><span dir="auto">${escape(chapter.title)}</span></button></li>`).join('')}</ol></div>
      <div data-fiche-pane="transcript" hidden><p class="pd-fiche-note">${t('L’auteur n’a pas publié de transcription pour cette vidéo. Le filtre « Avec transcription » de la bibliothèque liste celles qui en ont une.','The author has not published a transcript for this video. The library’s “With transcript” filter lists those that have one.','El autor no ha publicado una transcripción de este vídeo. El filtro «Con transcripción» de la biblioteca muestra los que la tienen.')}</p></div>
      <div data-fiche-pane="notes" hidden><label class="pd-label" for="pd-fiche-notes">${t('Gardées sur cet appareil','Kept on this device','Guardadas en este dispositivo')}</label><textarea id="pd-fiche-notes" class="pd-notes" placeholder="${t('Ce que tu veux retenir…','What you want to remember…','Lo que quieres recordar…')}">${escape(storage.get(`rl-note-${video.id}`, '') || '')}</textarea></div>
      <div data-fiche-pane="source" hidden><p class="pd-fiche-note">${t('Vidéo publique de','Public video by','Vídeo público de')} ${escape(video.creator || '')}, ${t('référencée par RaceLink. Elle reste chez son auteur.','indexed by RaceLink. It stays with its author.','referenciado por RaceLink. Sigue en manos de su autor.')}</p></div>
      <div class="pd-fiche-acts"><button type="button" class="on" data-video="${escape(video.id)}">▶ ${t('Regarder ici','Watch here','Ver aquí')}</button><button type="button" data-save="${escape(video.id)}">${t('Enregistrer','Save','Guardar')}</button><button type="button" data-pd-copy="${escape(url.href)}">${t('Copier le lien','Copy link','Copiar enlace')}</button></div></div>`;
    root.closest('section').hidden = false;
  }
  function ficheEvents(event) {
    const tab = event.target.closest('[data-fiche-tab]'); if (tab) ficheTab(tab.dataset.ficheTab);
    const copy = event.target.closest('[data-pd-copy]');
    if (copy) navigator.clipboard?.writeText(copy.dataset.pdCopy).then(() => { copy.textContent = t('Lien copié ✓','Link copied ✓','Enlace copiado ✓'); }).catch(() => {});
  }
  function render() { copy(); if (stats) ticker(); disciplines(); subjects(); shortsRail(); paths(); help(); }
  // Static content appears at once; the counts follow when the catalogue is ready.
  function load() {
    render();
    // Refresh before navigation, including keyboard activation and opening in a new tab.
    for (const type of ['click', 'pointerdown', 'focusin', 'contextmenu']) document.addEventListener(type, refreshDisciplineLink);
    // The manifest is tiny, so the total shows before the catalogue finishes loading.
    fetch('./export-manifest.json').then(r => r.ok ? r.json() : Promise.reject()).then(data => { const total = $('#catalog-total'); if (total.textContent === '…' && data.videos) total.textContent = number(data.videos); }).catch(() => {});
    fetch('./social-index.json').then(r => r.ok ? r.json() : Promise.reject()).then(data => { taskNames = data.tasks || {}; socialTotals = {total:(data.items || []).length, french:(data.items || []).filter(item => item.l === 'fr').length}; shorts = pickShorts(Array.isArray(data.items) ? data.items : []); shortsRail(); }).catch(() => {});
    libraryPreview().catch(() => {}); fichePreview().catch(() => {});
    $('#pd-lib-preview').addEventListener('click', previewClick);
    $('#pd-fiche-preview').addEventListener('click', ficheEvents);
    $('#pd-fiche-preview').addEventListener('input', event => { if (event.target.id === 'pd-fiche-notes') storage.set(`rl-note-${featured.id}`, event.target.value); });
    getJson('/aide/api/resources?language=fr&per_page=1').then(data => { frenchCounts = Object.fromEntries((data.facets?.category || []).map(entry => [entry.value, entry.count])); subjects(); }).catch(() => {});
  }
  return {load, render, featured: id => featured?.id === id ? featured : null, setStats(value) { stats = value; render(); }, setFaq(value) { faq = value; help(); }};
}
