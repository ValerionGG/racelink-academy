import {guidePhoto,guideTopic} from './guide-art.js?v=themes-v22';
import {createGuideSources,isManufacturerReference} from './guide-sources.js?v=themes-v22';

export function createGuideUI({escape:e,t,picks,safeUrl}) {
  let version=0;
  const $=s=>document.querySelector(s),sourcesUI=createGuideSources({escape:e,safeUrl});
  const list=value=>Array.isArray(value)?value:[];
  const official=sources=>list(sources).filter(source=>source&&isManufacturerReference(source)&&safeUrl(source.url));
  const referenceLabel=count=>count===1?t('référence constructeur','manufacturer reference','referencia del fabricante'):t('références constructeur','manufacturer references','referencias del fabricante');
  function photoSource(value){
    if(typeof value!=='string')return '';
    if(/^(?:\/aide\/|\.\/)?(?:assets|images)\/[\w./-]+$/.test(value)&&!value.split('/').includes('..'))return value;
    return safeUrl(value,true);
  }
  function photoPosition(value){
    const position=typeof value==='string'?value.trim():'';
    return /^(?:left|right|top|bottom|center|\d+(?:\.\d+)?%)(?:\s+(?:left|right|top|bottom|center|\d+(?:\.\d+)?%))?$/.test(position)?position:'50% 50%';
  }
  function photoCredit(photo){
    const source=safeUrl(photo.sourceUrl),license=safeUrl(photo.licenseUrl);
    return `<details class="guide-photo-credit"><summary>${t('Crédit photo','Photo credit','Crédito de la foto')}</summary><p>${source?`<a href="${e(source)}" target="_blank" rel="noopener noreferrer">${e(photo.credit||t('Source photo','Photo source','Fuente de la foto'))}</a>`:e(photo.credit||'')}${license?` · <a href="${e(license)}" target="_blank" rel="noopener noreferrer">${e(photo.license||'')}</a>`:''}</p><p>${t('Photo d’illustration · cadrage adapté à l’écran.','Illustrative photo · crop adapted to the screen.','Foto ilustrativa · encuadre adaptado a la pantalla.')}</p></details>`;
  }
  function card(resource){
    const topic=guideTopic(resource,{t}),photo=guidePhoto(resource),src=photoSource(photo?.src),g=resource.guide||resource;
    const id=resource.id||g.id,title=resource.title||g.title||'',references=official(g.sources||resource.sources),first=references[0];
    const preview=g.cardSummary||resource.description||g.intro||'';
    return `<article class="video-card guide-card guide-card-v20">
      <button class="guide-cover" data-guide="${e(id)}" data-guide-topic="${e(topic.key)}" aria-label="${e(t('Lire : ','Read: ','Leer: ')+title)}">${src?`<img class="guide-photo" src="${e(src)}" alt="${e(photo.alt||'')}" lang="fr" width="640" height="360" loading="lazy" decoding="async" style="object-position:${e(photoPosition(photo.position))}">`:`<span class="guide-photo-unavailable">${t('Illustration indisponible','Image unavailable','Imagen no disponible')}</span>`}</button>
      <div class="guide-card-body">
        <div class="guide-card-labels"><p class="guide-card-kind">${t('Guide pratique','Practical guide','Guía práctica')}<span aria-hidden="true"> / </span><span>${e(topic.label)}</span></p><span class="guide-language" aria-label="${t('Contenu en français','Content in French','Contenido en francés')}">FR</span></div>
        <h3><button class="title-button" data-guide="${e(id)}" lang="fr">${e(title)}</button></h3>
        ${preview?`<p class="card-excerpt" lang="fr">${e(preview)}</p>`:''}
        ${first?`<div class="guide-card-source"><span class="guide-card-source-label">${t('Exemple de référence','Example reference','Ejemplo de referencia')} · ${e(first.publisher||'Source')}</span><a href="${e(safeUrl(first.url))}" target="_blank" rel="noopener noreferrer" lang="fr">${e(first.title)} <span aria-hidden="true">↗</span></a><button class="guide-reference-count" data-guide="${e(id)}" data-guide-section="sources">${t('Voir les sources et leur portée','View sources and scope','Ver fuentes y alcance')}<span>${references.length} ${referenceLabel(references.length)}</span></button></div>`:''}
      </div>
      <div class="guide-card-footer">${picks.badge('guide',id,{compact:true})}<button class="guide-read" data-guide="${e(id)}">${t('Lire le guide','Read guide','Leer guía')} <span aria-hidden="true">→</span></button></div>
    </article>`;
  }
  function jump(section){
    if(!['prerequisites','method','sources','videos'].includes(section))return;
    const target=$(`#guide-${section}`);if(!target)return;
    target.focus({preventScroll:true});target.scrollIntoView({block:'start',behavior:'instant'});
  }
  function prerequisites(g){
    const fields=list(g.fields),checklist=list(g.checklist);
    if(!fields.length&&!checklist.length)return '';
    return `<section class="guide-prerequisites" aria-labelledby="guide-prerequisites"><h3 id="guide-prerequisites" tabindex="-1">${t('Avant de commencer','Before you start','Antes de empezar')}</h3>
      ${fields.length?`<h4>${t('Informations à réunir','Information to gather','Información que reunir')}</h4><ul class="guide-checklist guide-field-list" lang="fr">${fields.map(field=>`<li>${e(field.label||'')}</li>`).join('')}</ul>`:''}
      ${checklist.length?`${fields.length?`<h4>${t('Points à vérifier','Points to check','Puntos que comprobar')}</h4>`:''}<ul class="guide-checklist" lang="fr">${checklist.map(item=>`<li>${e(item)}</li>`).join('')}</ul>`:''}
    </section>`;
  }
  function reader(resource,id){
    const g=resource.guide||resource,photo=guidePhoto(resource),src=photoSource(photo?.src),topic=guideTopic(resource,{t});
    const sources=list(g.sources),references=official(sources),others=sources.filter(source=>source&&!isManufacturerReference(source));
    const steps=list(g.steps),videos=list(g.relatedVideos),hasPrerequisites=list(g.fields).length||list(g.checklist).length;
    return `<article class="guide-reader guide-reader-v20">
      <header class="guide-reader-hero">
        <div class="guide-reader-heading"><p class="guide-card-kind">${e(topic.label)} · ${t('Guide RaceLink','RaceLink guide','Guía RaceLink')}</p><h2 id="dialog-title" tabindex="-1" lang="fr">${e(g.title||resource.title||'')}</h2>
          ${g.cardSummary?`<p class="guide-overview" lang="fr">${e(g.cardSummary)}</p>`:''}
          <p class="guide-content-language">${t('Ce guide et ses sources sont présentés en français.','This guide and its source descriptions are in French.','Esta guía y las descripciones de sus fuentes están en francés.')}</p>
          <div class="guide-reader-meta">${picks.badge('guide',id,{compact:true})}<span>${steps.length} ${t('repères de méthode','method points','puntos del método')}</span><button data-guide-jump="sources">${references.length} ${referenceLabel(references.length)} <span aria-hidden="true">↓</span></button></div>
        </div>
        ${src?`<figure class="guide-reader-figure"><img class="guide-reader-photo" src="${e(src)}" alt="${e(photo.alt||'')}" lang="fr" width="960" height="640" decoding="async" style="object-position:${e(photoPosition(photo.position))}"><figcaption>${photoCredit(photo)}</figcaption></figure>`:''}
      </header>
      <div class="guide-scope"><p>${t('Méthode générale RaceLink. Les notices ci-dessous concernent les versions indiquées : vérifiez le modèle, le moteur et l’édition de votre véhicule avant toute intervention.','General RaceLink method. The manuals below apply to the versions stated: check your vehicle model, engine and manual edition before any work.','Método general RaceLink. Los manuales siguientes corresponden a las versiones indicadas: comprueba el modelo, el motor y la edición del manual de tu vehículo antes de intervenir.')}</p>${g.missingDetailsMessage?`<p lang="fr">${e(g.missingDetailsMessage)}</p>`:''}</div>
      <div class="guide-reader-layout">
        <nav class="guide-plan guide-jumps" aria-label="${t('Plan du guide','Guide contents','Contenido de la guía')}"><p>${t('Dans ce guide','In this guide','En esta guía')}</p>
          ${hasPrerequisites?`<button data-guide-jump="prerequisites">${t('Avant de commencer','Before you start','Antes de empezar')} <span aria-hidden="true">↓</span></button>`:''}
          <button data-guide-jump="method">${t('La méthode','The method','El método')} <span aria-hidden="true">↓</span></button>
          <button data-guide-jump="sources">${t('Notices constructeur','Manufacturer manuals','Manuales del fabricante')} <span aria-hidden="true">↓</span></button>
          ${videos.length?`<button data-guide-jump="videos">${t('Continuer en vidéo','Continue with video','Continuar en vídeo')} <span aria-hidden="true">↓</span></button>`:''}
        </nav>
        <div class="guide-reader-main">
          ${prerequisites(g)}
          <section class="guide-method" aria-labelledby="guide-method"><h3 id="guide-method" tabindex="-1">${t('La méthode RaceLink','The RaceLink method','El método RaceLink')}</h3>${g.intro?`<p class="guide-lead" lang="fr">${e(g.intro)}</p>`:''}<ol class="guide-steps" lang="fr">${steps.map(step=>`<li>${e(typeof step==='string'?step:step.text||'')}</li>`).join('')}</ol></section>
          <section class="guide-references" aria-labelledby="guide-sources"><div class="guide-section-heading"><h3 id="guide-sources" tabindex="-1">${t('Notices & références constructeur','Manufacturer manuals & references','Manuales y referencias del fabricante')}</h3><span>${references.length} ${referenceLabel(references.length)}</span></div><p class="guide-sources-intro">${t('Ouvrez la page d’origine pour suivre les indications du constructeur. Le véhicule concerné figure sous chaque lien.','Open the original page to follow the manufacturer’s instructions. The relevant vehicle is stated under each link.','Abre la página original para seguir las indicaciones del fabricante. El vehículo correspondiente aparece bajo cada enlace.')}</p>
            <div class="guide-source-list" lang="fr">${sourcesUI.render(references)}</div>
            ${!references.length?`<p class="guide-sources-empty">${t('Aucune procédure constructeur directe n’est documentée pour ce guide. Consultez les autres références ci-dessous.','No direct manufacturer procedure is documented for this guide. See the other references below.','No hay un procedimiento directo del fabricante documentado para esta guía. Consulta las demás referencias.')}</p>`:''}
            ${others.length?`<details class="guide-other-sources"><summary>${t('Autres sources & portails de notices','Other sources & manual portals','Otras fuentes y portales de manuales')}</summary><div lang="fr">${sourcesUI.render(others)}</div></details>`:''}
          </section>
          ${videos.length?`<section class="guide-related" aria-labelledby="guide-videos"><h3 id="guide-videos" tabindex="-1">${t('Pour continuer en vidéo','Continue with video','Para continuar en vídeo')}</h3><div class="guide-related-videos">${videos.map(video=>`<button data-video="${e(video.id)}" lang="fr">${e(video.title)} <span aria-hidden="true">↗</span></button>`).join('')}</div></section>`:''}
        </div>
      </div>
      <footer class="guide-reader-footer">${picks.note('guide',id)}</footer>
    </article>`;
  }
  async function open(id,section){
    const current=++version,dialog=$('#video-dialog');
    if(!dialog.open)dialog.showModal();
    dialog.classList.add('guide-dialog');dialog.scrollTop=0;
    const header=`<div class="detail-header"><span>RaceLink · ${t('Guide pratique','Practical guide','Guía práctica')}</span><button data-close aria-label="${t('Fermer','Close','Cerrar')}">×</button></div>`;
    $('#video-detail').innerHTML=`${header}<div class="guide-loading" role="status"><span>${t('Chargement du guide…','Loading guide…','Cargando guía…')}</span><div class="guide-loading-photo" aria-hidden="true"></div></div>`;
    try {
      const {resource}=await window.getCatalogJson(`/aide/api/resources/guide/${encodeURIComponent(id)}`);
      if(current!==version||!dialog.open)return;
      if(!resource)throw new Error('Missing guide resource');
      $('#video-detail').innerHTML=`${header}${reader(resource,id)}`;
      dialog.scrollTop=0;
      if(section==='sources')jump('sources');else $('#dialog-title').focus({preventScroll:true});
    }catch{
      if(current===version&&dialog.open){
        $('#video-detail').innerHTML=`${header}<div class="guide-reader"><h2 id="dialog-title" tabindex="-1">${t('Guide indisponible','Guide unavailable','Guía no disponible')}</h2><p>${t('Fermez cette fiche puis réessayez.','Close this panel and retry.','Cierra esta ficha y vuelve a intentarlo.')}</p></div>`;
        $('#dialog-title').focus({preventScroll:true});
      }
    }
  }
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-guide-jump]');if(button)jump(button.dataset.guideJump);
    if(event.target.closest('[data-video],[data-close]')){++version;$('#video-dialog').classList.remove('guide-dialog');}
  });
  $('#video-dialog').addEventListener('close',()=>{++version;$('#video-dialog').classList.remove('guide-dialog');});
  return {card,open};
}
