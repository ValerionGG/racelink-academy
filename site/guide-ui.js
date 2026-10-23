import {guidePhoto,guideTopic} from './guide-art.js?v=skills-v18b';
import {createGuideSources,isManufacturerReference} from './guide-sources.js?v=skills-v18b';

export function createGuideUI({escape:e,t,picks,safeUrl}) {
  let version=0;
  const $=s=>document.querySelector(s),sourcesUI=createGuideSources({escape:e,safeUrl});
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
    return `<details class="guide-photo-credit"><summary>${t('Crédit photo','Photo credit','Crédito de la foto')}</summary><p>${source?`<a href="${e(source)}" target="_blank" rel="noopener noreferrer">${e(photo.credit||'Source photo')}</a>`:e(photo.credit||'')}${license?` · <a href="${e(license)}" target="_blank" rel="noopener noreferrer">${e(photo.license)}</a>`:''}</p><p>Photo d’illustration · cadrage adapté à l’écran.</p></details>`;
  }
  function card(resource){
    const topic=guideTopic(resource,{t}),photo=guidePhoto(resource),src=photoSource(photo?.src),g=resource.guide||resource;
    const count=(resource.sources||g.sources||[]).filter(isManufacturerReference).length;
    return `<article class="video-card guide-card"><button class="guide-cover" data-guide="${e(resource.id)}" data-guide-topic="${e(topic.key)}" aria-label="${e(t('Lire : ','Read: ','Leer: ')+resource.title)}">${src?`<img class="guide-photo" src="${e(src)}" alt="${e(photo.alt||'')}" width="640" height="360" loading="lazy" decoding="async" style="object-position:${e(photoPosition(photo.position))}">`:''}</button><div class="guide-card-body"><p class="guide-card-kind">${t('Guide pratique','Practical guide','Guía práctica')} <span>· FR</span></p><h3><button class="title-button" data-guide="${e(resource.id)}">${e(resource.title)}</button></h3><p class="card-excerpt">${e(g.cardSummary||resource.description)}</p>${count?`<button class="guide-reference-count" data-guide="${e(resource.id)}" data-guide-section="sources">${count} ${count===1?t('référence constructeur','manufacturer reference','referencia del fabricante'):t('références constructeur','manufacturer references','referencias del fabricante')} <span aria-hidden="true">↗</span></button>`:''}</div><div class="guide-card-footer">${picks.badge('guide',resource.id,{compact:true})}<button class="guide-read" data-guide="${e(resource.id)}">${t('Ouvrir le guide','Open guide','Abrir guía')} <span aria-hidden="true">→</span></button></div></article>`;
  }
  function jump(section){
    const target=$(`#guide-${section}`);if(!target)return;
    target.focus({preventScroll:true});target.scrollIntoView({block:'start',behavior:'instant'});
  }
  async function open(id,section){
    const current=++version,dialog=$('#video-dialog');
    if(!dialog.open)dialog.showModal();
    dialog.classList.add('guide-dialog');dialog.scrollTop=0;
    const header=`<div class="detail-header"><span>RACELINK · ${t('GUIDE PRATIQUE','PRACTICAL GUIDE','GUÍA PRÁCTICA')}</span><button data-close aria-label="${t('Fermer','Close','Cerrar')}">×</button></div>`;
    $('#video-detail').innerHTML=`${header}<div class="empty" role="status">${t('Chargement du guide…','Loading guide…','Cargando guía…')}</div>`;
    try {
      const {resource}=await window.getCatalogJson(`/aide/api/resources/guide/${encodeURIComponent(id)}`);
      if(current!==version||!dialog.open)return;
      const g=resource.guide,photo=guidePhoto(resource),count=(g.sources||[]).filter(isManufacturerReference).length;
      $('#video-detail').innerHTML=`${header}<article class="guide-reader" lang="fr"><header class="guide-reader-heading"><p class="guide-card-kind">Les repères RaceLink · Lecture en français</p><h2 id="dialog-title" tabindex="-1">${e(g.title)}</h2><p class="guide-lead">${e(g.intro)}</p><div class="guide-reader-meta">${picks.badge('guide',id,{compact:true})}<span>${count} référence${count===1?'':'s'} constructeur</span></div><p class="guide-scope">Méthode générale RaceLink. Les notices ci-dessous concernent les versions indiquées : vérifiez le modèle, le moteur et l’édition de votre véhicule avant toute intervention.</p><nav class="guide-jumps" aria-label="Dans ce guide"><button data-guide-jump="method">La méthode <span>↓</span></button><button data-guide-jump="sources">Notices constructeur <span>↓</span></button></nav></header><div class="guide-reader-layout"><section class="guide-method"><h3 id="guide-method" tabindex="-1">La méthode</h3><ol class="guide-steps">${(g.steps||[]).map(step=>`<li>${e(typeof step==='string'?step:step.text)}</li>`).join('')}</ol>${g.fields?.length?`<h3>Informations à réunir</h3><ul class="guide-checklist">${g.fields.map(f=>`<li>${e(f.label)}</li>`).join('')}</ul>`:''}${g.checklist?.length?`<h3>Avant de commencer</h3><ul class="guide-checklist">${g.checklist.map(x=>`<li>${e(x)}</li>`).join('')}</ul>`:''}${g.relatedVideos?.length?`<h3>Pour continuer en vidéo</h3><div class="guide-related-videos">${g.relatedVideos.map(v=>`<button data-video="${e(v.id)}">${e(v.title)} <span>↗</span></button>`).join('')}</div>`:''}</section><aside class="guide-references" aria-labelledby="guide-sources"><h3 id="guide-sources" tabindex="-1">Notices & références constructeur</h3><p class="guide-sources-intro">Ouvrez la page d’origine pour suivre les indications du constructeur. Le véhicule concerné figure sous chaque lien.</p><div class="guide-source-list">${sourcesUI.render((g.sources||[]).filter(isManufacturerReference))}${(g.sources||[]).some(s=>!isManufacturerReference(s))?`<details class="guide-other-sources"><summary>Autres sources & portails de notices</summary>${sourcesUI.render((g.sources||[]).filter(s=>!isManufacturerReference(s)))}</details>`:''}</div></aside></div><footer class="guide-reader-footer">${picks.note('guide',id)}${photo?photoCredit(photo):''}</footer></article>`;
      dialog.scrollTop=0;
      if(section==='sources')jump('sources');else $('#dialog-title').focus({preventScroll:true});
    }catch{if(current===version&&dialog.open)$('#video-detail').innerHTML=`${header}<div class="guide-reader"><h2 id="dialog-title">${t('Guide indisponible','Guide unavailable','Guía no disponible')}</h2><p>${t('Fermez cette fiche puis réessayez.','Close this panel and retry.','Cierra esta ficha y vuelve a intentarlo.')}</p></div>`;}
  }
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-guide-jump]');if(button)jump(button.dataset.guideJump);
    if(event.target.closest('[data-video],[data-close]')){++version;$('#video-dialog').classList.remove('guide-dialog');}
  });
  $('#video-dialog').addEventListener('close',()=>{++version;$('#video-dialog').classList.remove('guide-dialog');});
  return {card,open};
}
