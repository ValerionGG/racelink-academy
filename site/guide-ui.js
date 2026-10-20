// Guide resources share the library search, while keeping their original sources.
export function createGuideUI({escape:e,t,picks,safeUrl}) {
  let version=0;
  const $=s=>document.querySelector(s);
  function card(resource){
    return `<article class="video-card guide-card"><button class="guide-cover" data-guide="${e(resource.id)}" aria-label="${e(t('Lire : ','Read: ','Leer: ')+resource.title)}"><span class="guide-cover-label">RACELINK · ${t('GUIDE','GUIDE','GUÍA')}</span><span class="guide-cover-symbol" aria-hidden="true">↳</span><span>${t('Comprendre, étape par étape.','Understand, step by step.','Entender, paso a paso.')}</span>${picks.badge('guide',resource.id,{overlay:true})}</button><div class="card-heading"><h3><button class="title-button" data-guide="${e(resource.id)}">${e(resource.title)}</button></h3></div><p class="creator">RaceLink · ${t('Lecture en français','Written in French','Lectura en francés')}</p><p class="card-excerpt">${e(resource.description)}</p><button class="guide-read" data-guide="${e(resource.id)}">${t('Lire le guide','Read guide','Leer guía')} ↗</button></article>`;
  }
  async function open(id){
    const current=++version,dialog=$('#video-dialog');
    if(!dialog.open)dialog.showModal();
    $('#video-detail').innerHTML=`<div class="detail-header"><span>RACELINK · GUIDE</span><button data-close aria-label="${t('Fermer','Close','Cerrar')}">×</button></div><div class="empty">${t('Chargement du guide…','Loading guide…','Cargando guía…')}</div>`;
    try {
      const {resource}=await window.getCatalogJson(`/aide/api/resources/guide/${encodeURIComponent(id)}`);
      if(current!==version||!dialog.open)return;
      const g=resource.guide;
      $('#video-detail').innerHTML=`<div class="detail-header"><span>RACELINK · ${t('GUIDE PRATIQUE','PRACTICAL GUIDE','GUÍA PRÁCTICA')}</span><button data-close aria-label="${t('Fermer','Close','Cerrar')}">×</button></div><article class="guide-reader" lang="fr">${picks.badge('guide',id)}<h2 id="dialog-title">${e(g.title)}</h2><p class="guide-lead">${e(g.intro)}</p>${picks.note('guide',id)}<h3>La démarche</h3><ol class="guide-steps">${(g.steps||[]).map(step=>`<li>${e(step)}</li>`).join('')}</ol>${g.fields?.length?`<h3>Informations à réunir</h3><ul>${g.fields.map(f=>`<li>${e(f.label)}</li>`).join('')}</ul>`:''}${g.checklist?.length?`<h3>Avant de commencer</h3><ul class="guide-checklist">${g.checklist.map(x=>`<li>${e(x)}</li>`).join('')}</ul>`:''}<p class="guide-scope">Ce guide explique une méthode générale. Les références et opérations doivent être confirmées dans la notice correspondant à votre véhicule et à son moteur.</p><h3>Sources pour vérifier</h3><div class="guide-source-list">${(g.sources||[]).filter(s=>safeUrl(s.url)).map(s=>`<a href="${e(safeUrl(s.url))}" target="_blank" rel="noopener noreferrer"><strong>${e(s.title)} ↗</strong><span>${e(s.scope||s.publisher)}</span></a>`).join('')}</div>${g.relatedVideos?.length?`<h3>Pour continuer en vidéo</h3><div class="guide-related-videos">${g.relatedVideos.map(v=>`<button data-video="${e(v.id)}">${e(v.title)} <span>↗</span></button>`).join('')}</div>`:''}</article>`;
    }catch{if(current===version&&dialog.open)$('#video-detail').innerHTML=`<div class="detail-header"><span>RACELINK · GUIDE</span><button data-close aria-label="${t('Fermer','Close','Cerrar')}">×</button></div><div class="guide-reader"><h2 id="dialog-title">${t('Guide indisponible','Guide unavailable','Guía no disponible')}</h2><p>${t('Fermez cette fiche puis réessayez.','Close this panel and retry.','Cierra esta ficha y vuelve a intentarlo.')}</p></div>`;}
  }
  document.addEventListener('click',event=>{if(event.target.closest('[data-video],[data-close]'))++version;});
  $('#video-dialog').addEventListener('close',()=>++version);
  return {card,open};
}
