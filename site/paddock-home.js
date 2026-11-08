// Home sections of the Paddock design. Counts come from the catalogue; navigation stays delegated to app.js.
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
const POSTERS = [[/oil|huile|vidange/,'oil'],[/wiper|essuie/,'wipers'],[/wheel|tire|tyre|pneu/,'wheel'],[/batter/,'battery'],[/fuse|fusible/,'fuses'],[/light|bulb|lamp|phare/,'lighting'],[/fuel|carburant/,'fuel'],[/diag|obd|code|warning|voyant/,'diagnostics']];
const SHORTS_SHOWN = 14, PER_POSTER = 2;

export const poster = item => {
  const subject = `${(item.s || []).join(' ')} ${item.t}`.toLowerCase();
  return POSTERS.find(([pattern]) => pattern.test(subject))?.[1] || (item.c === 'driving' ? 'driving' : 'service');
};
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

export function createPaddockHome({$, escape, t, getUi, getJson}) {
  let stats = null, frenchCounts = {}, shorts = [], faq = [];
  const pick = values => t(...values);
  const number = value => Number(value || 0).toLocaleString(getUi());
  const count = id => stats?.facets?.category?.find(entry => entry.value === id)?.count || 0;
  const progress = () => { try { return JSON.parse(localStorage.getItem('rl-library-progress') || '{}'); } catch { return {}; } };

  function ticker() {
    const entries = [[stats?.total_videos, t('vidéos','videos','vídeos')],...LARGE.map(([id,,name]) => [count(id), pick(name)]),
      [stats?.facets?.platform?.find(p => p.value === 'tiktok')?.count, 'TikTok'],[stats?.facets?.platform?.find(p => p.value === 'instagram')?.count, 'Instagram']].filter(([n]) => n);
    const text = entries.map(([n, label]) => `<span>${escape(label)} <b>${number(n)}</b></span>`).join('');
    $('#pd-ticker').innerHTML = text + text;
  }
  function subjects() {
    const badge = id => stats ? `<span class="pd-subject-count">${number(count(id))}</span>` : '';
    const fr = id => frenchCounts[id] ? `<span class="pd-fr">${number(frenchCounts[id])} ${t('en français','in French','en francés')}</span>` : '';
    $('#pd-subjects-grid').innerHTML = LARGE.map(([id, src, name, hint]) => `<button type="button" class="pd-subject pd-subject-photo" data-entry-category="${id}"><img src="${src}" alt="" loading="lazy" decoding="async">${badge(id)}<strong>${escape(pick(name))}</strong><small>${escape(pick(hint))}</small>${fr(id)}</button>`).join('') +
      SMALL.map(([id, name, hint, path]) => `<button type="button" class="pd-subject" data-entry-category="${id}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">${path}</svg>${badge(id)}<strong>${escape(pick(name))}</strong><small>${escape(pick(hint))}</small></button>`).join('');
  }
  function shortsRail() {
    const root = $('#pd-shorts-rail');
    root.closest('section').hidden = !shorts.length;
    root.innerHTML = shorts.map(item => `<article class="pd-short"><button type="button" data-video="${escape(item.id)}" aria-label="${escape(item.t)}"><img src="./assets/photos/${item.poster}.jpg" alt="" loading="lazy" decoding="async"><span class="pd-plat">${item.p === 'instagram' ? 'Instagram' : 'TikTok'}</span><span class="pd-short-copy"><strong dir="auto">${escape(item.t)}</strong><small dir="auto">${escape(item.a || '')}</small></span></button></article>`).join('');
  }
  function paths() {
    const done = progress();
    $('#pd-paths-grid').innerHTML = PATHS.map(([id, name]) => {
      const steps = tracks[id] || [], finished = steps.filter((_, index) => done[`${id}:${index}`]).length;
      const state = finished ? t(`Étape ${Math.min(finished + 1, steps.length)}/${steps.length}`,`Step ${Math.min(finished + 1, steps.length)}/${steps.length}`,`Paso ${Math.min(finished + 1, steps.length)}/${steps.length}`) : t('À commencer','Not started','Sin empezar');
      return `<button type="button" class="pd-path" data-path="${id}"><span class="pd-path-kind">${escape(pick(name))}</span><strong>${escape(pick(steps[0]?.title || name))}</strong><span class="pd-sectors" aria-hidden="true">${steps.map((_, index) => `<i class="${done[`${id}:${index}`] ? 'on' : ''}"></i>`).join('')}</span><small><span>${steps.length} ${t('étapes','steps','pasos')}</span><span>${state}</span></small></button>`;
    }).join('');
  }
  function help() {
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
      subjectsKick:t('8 univers','8 worlds','8 mundos'),subjectsTitle:t('Choisis ton sujet','Pick your topic','Elige tu tema'),library:t('Toute la bibliothèque →','The whole library →','Toda la biblioteca →'),
      shortsKick:t('TikTok · Instagram','TikTok · Instagram','TikTok · Instagram'),shortsTitle:t('Formats courts','Short videos','Vídeos cortos'),shortsHint:t('Une astuce en moins d’une minute, dans son format d’origine.','A tip in under a minute, in its original format.','Un consejo en menos de un minuto, en su formato original.'),shortsAll:t('Tout voir →','See all →','Ver todo →'),
      pathsKick:t('8 parcours guidés','8 guided paths','8 itinerarios'),pathsTitle:t('Apprends étape par étape','Learn step by step','Aprende paso a paso'),pathsAll:t('Tous les parcours →','All paths →','Todos los itinerarios →'),
      bonusKick:t('En plus','Going further','Además'),bonusTitle:t('Ta voiture, en détail','Your car, in detail','Tu coche, en detalle'),bonusHint:t('Des tutos ciblés sur ton modèle, un atlas des voitures courantes et un atelier 3D.','Tutorials for your model, an atlas of common cars and a 3D workshop.','Tutoriales para tu modelo, un atlas de coches comunes y un taller 3D.'),
      carTitle:t('Des tutos pour ta voiture','Tutorials for your car','Tutoriales para tu coche'),carHint:t('Marque, modèle, génération, moteur : la bibliothèque se cale sur ta voiture.','Make, model, generation, engine: the library adapts to your car.','Marca, modelo, generación, motor: la biblioteca se adapta a tu coche.'),
      atlasHint:t('Photos, habitacles, versions et visites 360° constructeur.','Photos, interiors, versions and manufacturer 360° tours.','Fotos, interiores, versiones y visitas 360° del fabricante.'),
      workshopHint:t('Un châssis ouvert à démonter pièce par pièce.','An open chassis to take apart piece by piece.','Un chasis abierto para desmontar pieza a pieza.'),
      footLearn:t('Apprendre','Learn','Aprender'),footLibrary:t('Bibliothèque','Library','Biblioteca'),footCar:t('Ta voiture','Your car','Tu coche'),footAtlas:t('Atlas des voitures','Car atlas','Atlas de coches'),footWorkshop:t('Atelier 3D','3D workshop','Taller 3D'),
      faqAll:t('Toute l’aide →','All help →','Toda la ayuda →'),
    };
    document.querySelectorAll('[data-pd]').forEach(el => { const value = labels[el.dataset.pd]; if (value) el.innerHTML = value; });
  }
  function render() { copy(); if (stats) ticker(); subjects(); shortsRail(); paths(); help(); }
  // Static content appears at once; the counts follow when the catalogue is ready.
  function load() {
    render();
    fetch('./social-index.json').then(r => r.ok ? r.json() : Promise.reject()).then(data => { shorts = pickShorts(Array.isArray(data.items) ? data.items : []); shortsRail(); }).catch(() => {});
    getJson('/aide/api/resources?language=fr&per_page=1').then(data => { frenchCounts = Object.fromEntries((data.facets?.category || []).map(entry => [entry.value, entry.count])); subjects(); }).catch(() => {});
  }
  return {load, render, setStats(value) { stats = value; render(); }, setFaq(value) { faq = value; help(); }};
}
