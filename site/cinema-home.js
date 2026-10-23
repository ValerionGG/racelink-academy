import {GUIDE_PHOTOS} from './guide-photos.js?v=themes-v22';
import {icon} from './icons.js';
import {attachRailNavigation} from './rail-navigation.js?v=themes-v22';

// Composition only: the catalogue and photo registries remain the sources of truth.
const ESSENTIALS = ['oil_spec', 'fuel_choice', 'wheel_change', 'wipers', 'battery', 'diagnostics'];
const UNIVERSES = [
  {id:'maintenance', category:'mechanics', title:['Mécanique','Mechanics','Mecánica'], description:['Comprendre, entretenir, réparer.','Understand, maintain, repair.','Comprender, mantener, reparar.']},
  {id:'driving', category:'driving', title:['Pilotage','Driving','Pilotaje'], description:['Freinage, trajectoires et technique.','Braking, racing lines and technique.','Frenada, trazadas y técnica.']},
  {id:'simracing', category:'simracing', title:['Sim racing','Sim racing','Sim racing'], description:['Réglages, matériel et sensations.','Setup, equipment and feel.','Ajustes, equipo y sensaciones.']},
];
const array = value => Array.isArray(value) ? value : [];
const escape = value => String(value ?? '').replace(/[&<>"']/g, character =>
  ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'})[character]);
const languageCode = value => typeof value === 'string' ? value.toLowerCase().split(/[-_]/)[0] : '';
const platformName = value => ({youtube:'YouTube', dailymotion:'Dailymotion', vimeo:'Vimeo', tiktok:'TikTok', instagram:'Instagram', facebook:'Facebook', twitch:'Twitch', bilibili:'Bilibili'})[value] || String(value || '');

function safeUrl(value, localImage = false) {
  if (typeof value !== 'string' || !value.trim()) return '';
  const local = localImage && /^\.\/assets\/[\w./-]+$/.test(value) && !value.split('/').includes('..');
  try {
    const url = new URL(value, local ? import.meta.url : undefined);
    return (local || url.protocol === 'https:') && !url.username && !url.password ? url.href : '';
  } catch { return ''; }
}
function position(value) {
  return typeof value === 'string' && /^(?:left|right|top|bottom|center|\d+(?:\.\d+)?%)(?:\s+(?:left|right|top|bottom|center|\d+(?:\.\d+)?%))?$/.test(value.trim()) ? value.trim() : '50% 50%';
}
function duration(value) {
  const seconds = Number(value);
  if (!Number.isFinite(seconds) || seconds <= 0) return '';
  const n = Math.round(seconds);
  return n >= 3600 ? `${Math.floor(n / 3600)}:${String(Math.floor(n % 3600 / 60)).padStart(2, '0')}:${String(n % 60).padStart(2, '0')}` : `${Math.floor(n / 60)}:${String(n % 60).padStart(2, '0')}`;
}
function active(record, parent, now) {
  const reviewed = Date.parse(record?.reviewedAt ?? record?.reviewed_at ?? parent?.reviewedAt ?? parent?.reviewed_at);
  const expires = Date.parse(record?.expiresAt ?? record?.expires_at ?? parent?.expiresAt ?? parent?.expires_at);
  return (record?.enabled ?? parent?.enabled) === true && parent?.enabled === true &&
    Number.isFinite(reviewed) && Number.isFinite(expires) && reviewed <= now && now < expires && reviewed < expires;
}

/**
 * root: dedicated element. Navigation remains delegated to the existing app.
 * load(): fetch data once, render, return readiness. render(): reread UI/content language.
 * getJson is the existing API function; local registries use ordinary static JSON fetches.
 */
export function createCinemaHome(ctx) {
  const root = ctx.root;
  if (!root || typeof root.querySelectorAll !== 'function') throw new TypeError('cinema-home requires a root element');
  const locale = () => ['fr', 'en', 'es'].includes(ctx.getUi?.()) ? ctx.getUi() : 'fr';
  const t = (fr, en, es) => typeof ctx.t === 'function' ? ctx.t(fr, en, es) : ({fr, en, es})[locale()];
  const text = value => typeof value === 'string' ? value : value && typeof value === 'object' ? String(value[locale()] || value.fr || value.en || value.es || '') : '';
  const selectedLanguage = () => { const code = languageCode(ctx.getState?.().language); return code === 'all' ? '' : code; };
  const matchesLanguage = value => !selectedLanguage() || languageCode(value) === selectedLanguage();
  const languageLabel = video => {
    if (!video.language || video.language === 'und') return t('Langue non renseignée','Language not provided','Idioma no indicado');
    const label = ctx.langName?.(video.language) || video.language;
    if (video.language_confidence === 'estimated' || /estimate|inferred/.test(String(video.language_status || ''))) return `${label} · ${t('estimé','estimated','estimado')}`;
    if (/not_verified|unknown/.test(String(video.language_status || ''))) return `${label} · ${t('à confirmer','unconfirmed','sin confirmar')}`;
    return label;
  };
  let data = null, guideData = null, visuals = [], loading = null, disposed = false, detach = [];
  const cleanupRails = () => { detach.forEach(fn => fn()); detach = []; };

  function image(photo, className = '', isVideo = false) {
    const src = safeUrl(photo?.src || photo?.url, true);
    return `<span class="cinema-image ${className}"><span class="cinema-image-fallback" aria-hidden="true">${escape(t('Aperçu indisponible','Preview unavailable','Vista previa no disponible'))}</span>${src ? `<img src="${escape(src)}" alt="" width="${isVideo ? 640 : 960}" height="${isVideo ? 360 : 640}" loading="lazy" decoding="async" referrerpolicy="no-referrer" style="object-position:${position(photo?.position)}">` : ''}</span>`;
  }
  function controls(id) {
    return `<nav class="cinema-controls" data-cinema-controls="${id}" aria-label="${escape(t('Parcourir la collection','Browse the collection','Explorar la colección'))}" hidden><span data-rail-position></span><button type="button" data-rail-previous aria-controls="${id}" aria-label="${escape(t('Carte précédente','Previous card','Tarjeta anterior'))}">${icon('arrow-right', {size:20})}</button><button type="button" data-rail-next aria-controls="${id}" aria-label="${escape(t('Carte suivante','Next card','Tarjeta siguiente'))}">${icon('arrow-right', {size:20})}</button></nav>`;
  }
  function heading(id, title, action, label) {
    return `<div class="cinema-section-heading"><h2 id="${id}">${escape(title)}</h2><button type="button" class="cinema-browse" ${action}>${escape(label)} ${icon('arrow-right', {size:18})}</button></div>`;
  }
  function guideCard(guide) {
    const photo = GUIDE_PHOTOS[guide.task];
    const publishers = [...new Set(array(guide.sources).filter(source => ['manufacturer_procedure','manufacturer_specification'].includes(source?.sourceType) && safeUrl(source.url)).map(source => source.publisher).filter(Boolean))];
    const badge = ctx.picks?.badge('guide', guide.id, {compact:true}) || '';
    return `<article class="cinema-card cinema-guide"><h3><button type="button" class="cinema-card-open" data-guide="${escape(guide.id)}">${image(photo, 'cinema-poster')}<span class="cinema-card-copy"><span class="cinema-kind">${escape(t('Guide pratique','Practical guide','Guía práctica'))}<span>FR</span></span><span class="cinema-card-title" lang="fr">${escape(guide.title)}</span></span></button></h3>${guide.cardSummary ? `<p class="cinema-card-description" lang="fr">${escape(guide.cardSummary)}</p>` : ''}${publishers.length ? `<p class="cinema-card-source">${escape(t('Sources : ','Sources: ','Fuentes: ')+publishers.join(' · '))}</p>` : ''}${badge ? `<div class="cinema-card-pick">${badge}</div>` : ''}</article>`;
  }
  function universeCard(entry, asset) {
    return `<article class="cinema-universe"><h3><button type="button" class="cinema-universe-open" data-entry-category="${entry.category}">${image(asset, 'cinema-landscape')}<span class="cinema-universe-copy"><span><span class="cinema-universe-title">${escape(t(...entry.title))}</span><span class="cinema-universe-description">${escape(t(...entry.description))}</span></span>${icon('arrow-up-right', {size:24})}</span></button></h3></article>`;
  }
  function selectedVideos() {
    const now = Date.now(), seen = new Set(), videos = [];
    for (const shelf of array(data?.shelves)) {
      if (!active(shelf, shelf, now)) continue;
      for (const item of array(shelf.items)) {
        const video = item?.video;
        if (!active(item, shelf, now) || !video?.id || !video.title || video.review_status !== 'editorial_selection' ||
            (item.videoId && item.videoId !== video.id) || seen.has(video.id) || !matchesLanguage(video.language)) continue;
        seen.add(video.id); videos.push({video, item, shelf});
      }
    }
    return videos.slice(0, 12);
  }
  function videoCard({video, item, shelf}) {
    const length = duration(video.duration_seconds ?? video.durationSeconds);
    const reason = text(item.reason), evidence = text(item.evidence?.note);
    const reviewed = Date.parse(item.reviewedAt ?? item.reviewed_at ?? shelf.reviewedAt ?? shelf.reviewed_at);
    const date = Number.isFinite(reviewed) ? new Intl.DateTimeFormat(locale(), {dateStyle:'medium', timeZone:'UTC'}).format(reviewed) : '';
    const basis = item.evidence?.basis === 'authorized_transcript' ? t('Transcription consultée','Transcript reviewed','Transcripción consultada') : t('Sélection sur métadonnées','Metadata-based selection','Selección por metadatos');
    return `<article class="cinema-card cinema-video"><h3><button type="button" class="cinema-card-open" data-video="${escape(video.id)}"><span class="cinema-video-visual">${image({src:video.thumbnail_url || video.thumbnailUrl}, 'cinema-thumbnail', true)}<span class="cinema-play" aria-hidden="true">${icon('play', {size:22})}</span>${length ? `<span class="cinema-duration">${escape(length)}</span>` : ''}</span><span class="cinema-card-copy"><span class="cinema-kind">${escape(platformName(video.platform))}<span>${escape(languageLabel(video))}</span></span><span class="cinema-card-title" dir="auto">${escape(video.title)}</span></span></button></h3><p class="cinema-card-creator" dir="auto">${escape(String(video.creator || '').trim() || t('Auteur non renseigné','Creator not provided','Autor no indicado'))}</p>${ctx.picks?.badge('video', video.id, {compact:true}) || ''}<details class="cinema-reason"><summary>${escape(t('Pourquoi ce choix ?','Why this pick?','¿Por qué esta selección?'))}</summary>${reason ? `<p>${escape(reason)}</p>` : ''}<p>${escape(basis)}${evidence ? ` · ${escape(evidence)}` : ''}</p>${date ? `<small>${escape(t('Revu le ','Reviewed ','Revisado ')+date)}</small>` : ''}</details></article>`;
  }
  function credits(photos) {
    const unique = [...new Map(photos.filter(Boolean).map(photo => [photo.sourceUrl, photo])).values()];
    if (!unique.length) return '';
    return `<details class="cinema-credits"><summary>${escape(t('Crédits des photographies','Photography credits','Créditos de las fotografías'))}</summary><p>${escape(t('Photos d’illustration, recadrées à l’affichage. Les vignettes vidéo proviennent des sources du catalogue.','Illustrative photographs, cropped for display. Video thumbnails come from catalogue sources.','Fotografías ilustrativas, recortadas en pantalla. Las miniaturas proceden de las fuentes del catálogo.'))}</p><ul>${unique.map(photo => { const source = safeUrl(photo.sourceUrl), license = safeUrl(photo.licenseUrl); return `<li>${source ? `<a href="${escape(source)}" target="_blank" rel="noopener noreferrer">${escape(photo.credit || t('Source','Source','Fuente'))}</a>` : escape(photo.credit || '')}${license ? ` · <a href="${escape(license)}" target="_blank" rel="noopener noreferrer">${escape(photo.license || t('Licence','License','Licencia'))}</a>` : ''}</li>`; }).join('')}</ul></details>`;
  }
  function render() {
    if (disposed) return {ready:false, guides:0, videos:0};
    cleanupRails();
    const allGuides = ESSENTIALS.map(task => array(guideData?.guides).find(guide => guide?.task === task && guide.id && guide.title)).filter(Boolean);
    const guides = allGuides.filter(guide => matchesLanguage(guide.language || guideData?.language));
    const universes = UNIVERSES.map(entry => ({entry, asset:visuals.find(asset => asset?.id === entry.id && safeUrl(asset.url, true))})).filter(({asset}) => asset);
    const videos = selectedVideos();
    const ready = Boolean(allGuides.length || universes.length || data);
    root.classList.add('cinema-home');
    if (!ready) { root.innerHTML = ''; return {ready:false, guides:0, videos:0}; }
    root.innerHTML = `${allGuides.length ? `<section class="cinema-section cinema-essentials" aria-labelledby="cinema-essentials-title">${heading('cinema-essentials-title', t('Les essentiels pour votre voiture','Essentials for your car','Lo esencial para tu coche'), 'data-browse-guides', t('Tous les guides','All guides','Todas las guías'))}${guides.length ? `<div class="cinema-rail cinema-guide-rail" id="cinema-essentials-rail">${guides.map(guideCard).join('')}</div>${controls('cinema-essentials-rail')}` : `<p class="cinema-empty">${escape(t('Ces guides sont disponibles en français. Aucun guide de cette collection dans la langue choisie.','These guides are available in French. This collection has no guide in your selected language.','Estas guías están disponibles en francés. Esta colección no tiene guías en el idioma elegido.'))}</p>`}<p class="cinema-scope">${escape(t('Des repères généraux, à rapprocher de la notice de votre version.','General guidance to use alongside the manual for your exact version.','Orientaciones generales que debes contrastar con el manual de tu versión exacta.'))}</p></section>` : ''}
      ${universes.length ? `<section class="cinema-section cinema-passions" aria-labelledby="cinema-passions-title">${heading('cinema-passions-title', t('Explorez votre passion','Explore your passion','Explora tu pasión'), 'data-browse-all', t('Toute la bibliothèque','The whole library','Toda la biblioteca'))}<div class="cinema-rail cinema-universe-rail" id="cinema-passions-rail">${universes.map(({entry, asset}) => universeCard(entry, asset)).join('')}</div>${controls('cinema-passions-rail')}</section>` : ''}
      ${data ? `<section class="cinema-section cinema-practice" aria-labelledby="cinema-practice-title">${heading('cinema-practice-title', t('Pour passer à la pratique','Put it into practice','Para pasar a la práctica'), 'data-browse-all', t('Explorer le catalogue','Explore the catalogue','Explorar el catálogo'))}${videos.length ? `<div class="cinema-rail cinema-video-rail" id="cinema-practice-rail">${videos.map(videoCard).join('')}</div>${controls('cinema-practice-rail')}<p class="cinema-scope">${escape(t('Des sélections documentées. Elles ne constituent pas une validation technique.','Documented selections. They do not constitute technical validation.','Selecciones documentadas. No constituyen una validación técnica.'))}</p>` : `<p class="cinema-empty">${escape(t('Aucune sélection éditoriale active dans la langue choisie. Le catalogue reste accessible.','No active editorial selection in your chosen language. The catalogue is still available.','No hay una selección editorial activa en el idioma elegido. El catálogo sigue disponible.'))}</p>`}</section>` : ''}
      ${credits([...guides.map(guide => GUIDE_PHOTOS[guide.task]), ...universes.map(({asset}) => asset)])}`;
    root.querySelectorAll('[data-cinema-controls]').forEach(control => {
      const rail = root.querySelector(`#${control.dataset.cinemaControls}`);
      detach.push(attachRailNavigation(rail, control));
    });
    root.querySelectorAll('.cinema-image img').forEach(img => img.addEventListener('error', () => { img.hidden = true; }, {once:true}));
    return {ready, guides:guides.length, videos:videos.length};
  }
  async function load() {
    if (disposed) return {ready:false, guides:0, videos:0};
    if (loading) return loading;
    const staticJson = async file => {
      const response = await fetch(new URL(`./${file}?v=themes-v22`, import.meta.url));
      if (!response.ok) throw new Error('Static collection unavailable');
      return response.json();
    };
    const getJson = ctx.getJson || (path => window.getCatalogJson(path));
    loading = Promise.allSettled([
      Promise.resolve().then(() => getJson('/aide/api/discovery')),
      staticJson('vehicle-guides.json'), staticJson('visual-assets.json'),
    ]).then(results => {
      if (disposed) return {ready:false, guides:0, videos:0};
      if (results[0].status === 'fulfilled' && Array.isArray(results[0].value?.shelves)) data = results[0].value;
      if (results[1].status === 'fulfilled') guideData = results[1].value;
      if (results[2].status === 'fulfilled') visuals = array(results[2].value?.assets);
      return render();
    });
    return loading;
  }
  return {load, render, destroy() { disposed = true; cleanupRails(); root.innerHTML = ''; }};
}
