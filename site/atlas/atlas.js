import {matchCars,carHref,fuelTest} from './search.js?v=41';
const $=s=>document.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl=value=>{try{const u=new URL(value,location.href);return ['https:','http:'].includes(u.protocol)?u.href:'';}catch{return '';}};
const link=(url,label,cls='')=>`<a class="${esc(cls)}" href="${esc(safeUrl(url))}" target="_blank" rel="noopener noreferrer">${esc(label)} ↗</a>`;
const date=value=>value?new Intl.DateTimeFormat('fr-FR',{dateStyle:'long',timeZone:'UTC'}).format(new Date(value)):'Date non documentée';
let models=[], current=null, make='', query='', only3d=false, view='exterieur', photoIndex=0, sourceIndex=0, trimId='', motorId='', lastFocus=null, fuelIntent='', browseReturn=null;
const available3d=m=>(m.immersive||[]).some(s=>s.verified?.render&&s.verified?.controls);
const sources=m=>(m.immersive||[]).filter(s=>s.verified?.render&&s.verified?.controls);
function writeUrl(replace=true){
  const p=new URLSearchParams();
  if(current){p.set('voiture',current.id);p.set('annee',String(current.year));if(view!=='exterieur')p.set('vue',view);if(trimId)p.set('finition',trimId);if(motorId)p.set('moteur',motorId);if(photoIndex)p.set('photo',String(photoIndex));if(sourceIndex)p.set('lecteur',String(sourceIndex));if(fuelIntent)p.set('energie',fuelIntent);}
  else {if(query)p.set('q',query);if(make)p.set('marque',make);if(only3d)p.set('3d','1');}
  history[replace?'replaceState':'pushState']({},'',location.pathname+(p.size?'?'+p:''));
  $('#copy').href=location.href;
}
function renderBrowse(){
  current=null;$('#media').replaceChildren();$('#browse').hidden=false;$('#detail').hidden=true;
  const hits=matchCars(models,query,{make},{allowEmpty:true}).filter(x=>!only3d||available3d(x.model));
  $('#car-grid').innerHTML=hits.map(hit=>{
    const m=hit.model,p=m.photos?.find(p=>p.view==='exterior');
    return `<a class="car-card" href="${esc(carHref(hit))}" data-car="${m.id}"><div class="car-image">${p?`<img src="${esc(p.src)}" alt="${esc(p.alt)}" width="600" height="390" loading="lazy">`:'<span class="photo-pending">Sandero berline<br><small>Dossier constructeur · photo à documenter</small></span>'}${available3d(m)?'<span class="card-badge">VISITE INTÉGRÉE</span>':''}</div><span class="card-arrow" aria-hidden="true">↗</span><p class="card-make">${esc(m.make)}</p><h2>${esc(m.model)} ${esc(m.generation)}</h2><p class="card-spec">France · ${m.year} · ${m.trims.length} finitions documentées${m.availability_status==='partial_verified'?'<br>Sélection partielle':''}</p></a>`;
  }).join('');
  $('#car-grid').setAttribute('aria-busy','false');$('#no-cars').hidden=hits.length>0;
  $('#result-status').textContent=`${hits.length} ${hits.length===1?'modèle':'modèles'}${query?' pour « '+query+' »':''}`;
  $('#makes').innerHTML=['Toutes',...new Set(models.map(m=>m.make))].map(m=>`<button type="button" data-make="${m==='Toutes'?'':esc(m)}" aria-pressed="${(m==='Toutes'&&!make)||m===make}">${esc(m)}</button>`).join('');
  document.title='Les voitures, en détail · RaceLink Academy';
}
function readRoute(focus=false){
  const p=new URLSearchParams(location.search),id=p.get('voiture');
  query=p.get('q')||'';make=p.get('marque')||'';only3d=p.get('3d')==='1';$('#car-query').value=query;$('#only3d').checked=only3d;
  if(!id){renderBrowse();return;}
  const m=models.find(m=>m.id===id);
  if(!m||p.has('annee')&&p.get('annee')!==String(m.year)){
    query=m?`${m.make} ${m.model} ${p.get('annee')}`:id;$('#car-query').value=query;make='';only3d=false;$('#only3d').checked=false;renderBrowse();$('#result-status').textContent='Cette voiture ou cette année ne dispose pas encore de dossier.';return;
  }
  current=m;view=['exterieur','habitacle','details','3d'].includes(p.get('vue'))?p.get('vue'):'exterieur';
  photoIndex=Math.max(0,Number.parseInt(p.get('photo'),10)||0);sourceIndex=Math.max(0,Number.parseInt(p.get('lecteur'),10)||0);
  trimId=p.get('finition')||'';motorId=p.get('moteur')||'';fuelIntent=(p.get('energie')||'').slice(0,60);
  renderDetail();if(focus)$('#car-title').focus({preventScroll:true});
}
function renderDetail(){
  $('#browse').hidden=true;$('#detail').hidden=false;$('#car-make').textContent=current.make;
  $('#car-title').textContent=`${current.model} ${current.generation}`;
  $('#car-generation').textContent=`${current.phase||'Génération '+current.generation} · dossier France ${current.year}`;
  document.title=`${current.make} ${current.model} ${current.generation} ${current.year} · RaceLink Academy`;
  $('#threed-badge').textContent=available3d(current)?'':'à documenter';
  $('[data-view="details"]').hidden=!current.photos.some(p=>!['exterior','interior'].includes(p.view));
  renderVersions(true);renderMedia();renderReferences();writeUrl();
}
function renderVersions(initial=false){
  const oldTrim=trimId,oldMotor=motorId;
  let trim=current.trims.find(t=>t.id===trimId);
  if(!trim&&motorId)trim=current.trims.find(t=>t.engines.includes(motorId));
  trim=trim||current.trims[0];trimId=trim?.id||'';
  const engines=current.engines.filter(e=>trim?.engines.includes(e.id));
  let motor=engines.find(e=>e.id===motorId)||engines[0];motorId=motor?.id||'';
  $('#trim').innerHTML=current.trims.length?current.trims.map(t=>`<option value="${esc(t.id)}" ${t.id===trimId?'selected':''}>${esc(t.label)}</option>`).join(''):'<option>Versions non documentées</option>';
  $('#motor').innerHTML=engines.length?engines.map(e=>`<option value="${esc(e.id)}" ${e.id===motorId?'selected':''}>${esc(e.label)}</option>`).join(''):'<option>Motorisation à confirmer</option>';
  $('#trim').disabled=!current.trims.length;$('#motor').disabled=!engines.length;
  const sourceDate=current.availability_date_precision==='month'?new Intl.DateTimeFormat('fr-FR',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(current.availability_date)):date(current.availability_date);
  const datePrefix=current.availability_date_precision==='month'?(/^[aeiouyâàéèêîïôùû]/i.test(sourceDate)?'d’':'de '):'du ';
  $('#version-date').textContent=`France · source ${datePrefix}${sourceDate}${current.availability_status==='partial_verified'?' · sélection partielle':''}`;
  let message='';
  if(initial&&(oldTrim&&oldTrim!==trimId||oldMotor&&oldMotor!==motorId))message='Cette combinaison n’est pas documentée. La version affichée ci-dessous est une autre combinaison, indiquée par les sélecteurs.';
  else if(!initial&&oldMotor&&oldMotor!==motorId)message=`${motor?.label||'La motorisation affichée'} remplace la précédente : elle est documentée pour cette finition.`;
  else if(fuelIntent&&motor&&fuelIntent.split(' + ').every(f=>['hybrid','hybride','electrique','electric','diesel','gazole','gpl','essence'].includes(f)&&fuelTest(motor,f)))message=`Recherche « ${fuelIntent.replace(/\bhybrid\b/g,'hybride').replace(/\belectrique\b|\belectric\b/g,'électrique')} » : ${trim?.label} / ${motor?.label} est une combinaison correspondante. Vous pouvez comparer les autres versions avec les sélecteurs.`;
  else if(fuelIntent){message='Le critère d’énergie du lien ne correspond pas à la version affichée. Il a été retiré ; vérifiez les sélecteurs ci-dessous.';fuelIntent='';}
  else if(current.availability_status==='partial_verified')message='Seules les versions attestées par les sources ci-dessous sont proposées. Cette liste est partielle.';
  $('#version-message').textContent=message;$('#version-message').hidden=!message;
  const fields=[['Énergie',motor?.fuel],['Transmission',motor?.gearbox],['Cylindrée',motor?.capacity_cm3?`${motor.capacity_cm3.toLocaleString('fr-FR')} cm³`:null],['Coffre (VDA)',motor?.boot_dm3_vda?`${motor.boot_dm3_vda} dm³`:null],['Longueur',current.dimensions_mm?.length?`${(current.dimensions_mm.length/1000).toLocaleString('fr-FR')} m`:null],['Empattement',current.dimensions_mm?.wheelbase?`${(current.dimensions_mm.wheelbase/1000).toLocaleString('fr-FR')} m`:null]];
  $('#motor-facts').innerHTML=fields.filter(([,v])=>v).map(([name,value])=>`<div><dt>${esc(name)}</dt><dd>${esc(value)}</dd></div>`).join('');
  const dimensions={length:'Longueur',width_without_mirrors:'Largeur hors rétroviseurs',width_folded_mirrors:'Largeur, rétroviseurs repliés',width_open_mirrors:'Largeur, rétroviseurs déployés',height:'Hauteur',height_with_roof_bars:'Hauteur avec barres de toit',height_with_boot_open:'Hauteur, hayon ouvert',wheelbase:'Empattement',front_overhang:'Porte-à-faux avant',rear_overhang:'Porte-à-faux arrière'};
  $('#dimensions-details').hidden=!current.dimensions_mm;$('#dimensions-details').open=false;
  $('#dimension-facts').innerHTML=Object.entries(current.dimensions_mm||{}).filter(([k])=>dimensions[k]).map(([k,v])=>`<div><dt>${dimensions[k]}</dt><dd>${Number(v).toLocaleString('fr-FR')} mm</dd></div>`).join('');
  $('#dimensions-note').textContent=current.dimensions_scope||'Cotes de la documentation constructeur liée ci-dessous.';
  $('#version-links').innerHTML=[trim?.source?link(trim.source,'Source de cette combinaison'):'',motor?.source&&motor.source!==trim?.source?link(motor.source,'Caractéristiques constructeur'):''].join('');
}
function currentPhotos(){return (current.photos||[]).filter(p=>view==='details'?!['exterior','interior'].includes(p.view):p.view===(view==='habitacle'?'interior':'exterior'));}
function renderMedia(){
  document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
  $('#media').replaceChildren();$('#media').classList.remove('viewer-active','expanded');$('#thumbnails').replaceChildren();$('#photo-provenance').hidden=true;$('#enlarge').hidden=true;$('#immersion-status').hidden=true;$('#viewer-scope').hidden=true;$('#expand-stage').hidden=true;
  if(view==='3d'){renderImmersion();return;}
  const photos=currentPhotos();if(photoIndex>=photos.length)photoIndex=0;
  const photo=photos[photoIndex];
  if(!photo){
    const inside=view==='habitacle',immersive=sources(current).find(s=>!inside||s.verified.interior);
    const reference=current.official_links.find(l=>['presentation','brochure'].includes(l.kind))||current.official_links.find(l=>l.kind==='manual');
    $('#media').innerHTML=`<div class="load3d"><h3>${inside?'Explorer l’habitacle':'Explorer la carrosserie'}</h3><p>Aucune photographie redistribuable de cette vue n’est intégrée à ce dossier.</p>${immersive?'<button class="action" data-open-3d>Ouvrir la visite intégrée →</button>':reference?link(reference.url,reference.kind==='manual'?'Ouvrir la documentation constructeur':'Voir les vues du constructeur','action'):''}</div>`;
    $('#media-name').textContent='Vue photographique non disponible';$('#media-note').textContent='Les documents constructeur ci-dessous complètent cette fiche.';return;
  }
  $('#media').innerHTML=`<img src="${esc(photo.src)}" alt="${esc(photo.alt)}" width="${photo.width||1600}" height="${photo.height||1000}" fetchpriority="high">`;
  $('#media-name').textContent=photo.title;$('#media-note').textContent=`${photo.caption||''} · Photo du ${date(photo.date)}`;
  $('#photo-provenance').hidden=false;$('#enlarge').hidden=false;
  $('#credit').innerHTML=`${esc(photo.author)} · ${link(photo.licenseUrl,photo.license)} · ${link(photo.source,'Photo originale')}<br>${esc(photo.changes||'')}`;
  $('#thumbnails').innerHTML=photos.map((p,i)=>`<button aria-label="${esc(p.title)}" aria-pressed="${i===photoIndex}" data-photo="${i}"><img src="${esc(p.src)}" alt="" width="94" height="52" loading="lazy">${esc(p.title)}</button>`).join('');
}
function renderImmersion(){
  const list=sources(current);if(sourceIndex>=list.length)sourceIndex=0;
  const source=list[sourceIndex],poster=current.photos?.find(p=>p.view==='exterior');
  $('#media-name').textContent=source?.label||'Pas encore de visite vérifiée pour ce modèle';
  $('#media-note').textContent=source?`${source.kind==='oem'?'Configurateur constructeur':'Maquette d’auteur'} · ${source.market||source.author||''}`:'Aucune maquette générique n’est utilisée à sa place.';
  if(!source){$('#media').innerHTML=`<div class="load3d"><h3>Les vues disponibles.</h3><p>${esc(current.immersive_unavailable_reason||'Aucun lecteur détaillé intégrable n’est vérifié pour cette génération.')}</p><button class="action" data-open-photos>Voir les photographies →</button></div>`;return;}
  $('#viewer-scope').hidden=false;$('#viewer-scope').textContent=`Vue montrée : ${source.modelScope} ${source.kind==='oem'?'Les sélecteurs RaceLink ne changent pas cette visite.':''}`;
  $('#expand-stage').hidden=false;$('#expand-stage').disabled=true;$('#expand-stage').textContent=document.fullscreenEnabled?'Plein écran ↗':'Agrandir le lecteur';
  $('#media').innerHTML=`${poster?`<img class="loader-photo" src="${esc(poster.src)}" alt="">`:''}<div class="load3d"><h3>${source.kind==='oem'?'La visite constructeur.':'Le modèle en volume.'}</h3><p>${esc(source.modelScope||source.label)}</p><button class="action" id="load-viewer">Explorer ${source.kind==='oem'?'la visite':'en 3D'} →</button><p>${source.kind==='oem'?'Dans le lecteur, ouvrez 360° puis le volant pour entrer à bord.':'Faites tourner la maquette et zoomez sur la carrosserie.'}</p><p>Chargement du site tiers à votre demande.</p></div>`;
  $('#immersion-status').hidden=false;
  $('#immersion-status').innerHTML=`${list.length>1?`<label for="viewer-source">Choisir le lecteur</label><select id="viewer-source">${list.map((s,i)=>`<option value="${i}" ${i===sourceIndex?'selected':''}>${esc(s.label)}</option>`).join('')}</select>`:''}<p>${esc(source.note||'')} ${source.verified.interior?'Habitacle exploré lors du contrôle.':'La vue intérieure de ce lecteur n’a pas été confirmée.'}</p><p>${source.kind==='artist'?`Auteur : ${esc(source.author)}${source.license?' · '+link(source.licenseUrl,source.license):''}. `:''}Vues et commandes vérifiées le ${date(source.checkedAt?.slice(0,10))}. ${link(source.url,'Ouvrir le lecteur sur son site')}</p>`;
  $('#viewer-source')?.addEventListener('change',e=>{sourceIndex=Number(e.target.value);renderMedia();writeUrl();});
  $('#load-viewer').addEventListener('click',()=>{
    const allowed=['https://sketchfab.com','https://www.renault.ma','https://www.dacia.ma','https://www.renault.fr','https://www.dacia.fr','https://www.peugeot.fr','https://www.citroen.fr','https://www.toyota.fr'];
    if(!allowed.includes(new URL(source.embedUrl).origin))return;
    const iframe=document.createElement('iframe');iframe.src=source.embedUrl;iframe.title=source.label+' — '+(source.modelScope||'');iframe.allow='fullscreen; xr-spatial-tracking';iframe.allowFullscreen=true;iframe.referrerPolicy='strict-origin-when-cross-origin';$('#media').replaceChildren(iframe);$('#media').classList.add('viewer-active');$('#expand-stage').disabled=false;iframe.focus();
  });
}
function renderReferences(){
  const links=[...(current.official_links||[]),...(current.related_models||[]).map(m=>({label:m.label,url:'./vehicules.html?voiture='+m.id+'&annee=2025',scope:'Carrosserie et versions documentées dans un dossier distinct.'}))];
  $('#official-links').innerHTML=links.map(l=>`<a class="official-card" href="${esc(safeUrl(l.url))}" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">↗</span><strong>${esc(l.label)}</strong><p>${esc(l.scope||'Source constructeur')}</p></a>`).join('')+`<a class="official-card" href="./?q=${encodeURIComponent(current.make+' '+current.model)}"><span aria-hidden="true">↗</span><strong>Trouver un tutoriel</strong><p>Ouvrir la bibliothèque pour ce modèle. Vérifiez la génération et le moteur de chaque vidéo.</p></a>`;
  const labels={tariff:'Tarif et finitions',technical:'Caractéristiques techniques',dimensions:'Dimensions',engines:'Motorisations',engine_detail:'Détail motorisations',engine_thermal:'Moteurs thermiques',trims:'Équipements par finition',colours:'Couleurs',brochure:'Brochure',commercial:'Modèles professionnels',sixth_gen:'Génération suivante'};
  $('#dossier-sources').innerHTML=`<p>${esc(current.availability_scope)}</p>${current.dimensions_scope?`<p>Dimensions : ${esc(current.dimensions_scope)}</p>`:''}<ul>${Object.entries(current.sources||{}).map(([key,value])=>`<li>${String(value).startsWith('https://')?link(value,labels[key]||key):esc(value)}</li>`).join('')}</ul><p>${esc(current.popularity?.scope||'')} ${current.popularity?link(current.popularity.source,'Classement PFA 2025')+' : rang '+current.popularity.rank+'.':''} ${esc(current.popularity?.note||'')}</p>`;
}
$('#finder').addEventListener('submit',e=>{e.preventDefault();query=$('#car-query').value.trim();renderBrowse();writeUrl(false);});
$('#car-query').addEventListener('input',()=>{query=$('#car-query').value;renderBrowse();writeUrl();});
$('#car-query').addEventListener('keydown',e=>{if(e.key==='Escape')e.preventDefault();});
$('#only3d').addEventListener('change',e=>{only3d=e.target.checked;renderBrowse();writeUrl();});
$('#makes').addEventListener('click',e=>{const b=e.target.closest('[data-make]');if(b){make=b.dataset.make;renderBrowse();writeUrl();[...$('#makes').querySelectorAll('button')].find(x=>x.dataset.make===make)?.focus();}});
$('#clear').addEventListener('click',()=>{query='';make='';only3d=false;$('#car-query').value='';$('#only3d').checked=false;renderBrowse();writeUrl();$('#car-query').focus();});
$('#car-grid').addEventListener('click',e=>{const card=e.target.closest('[data-car]');if(!card||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();lastFocus=card.dataset.car;browseReturn={query,make,only3d};history.pushState({},'',card.href);readRoute(true);window.scrollTo({top:0,behavior:'instant'});});
$('#back').addEventListener('click',()=>{if(browseReturn){({query,make,only3d}=browseReturn);$('#car-query').value=query;$('#only3d').checked=only3d;}renderBrowse();writeUrl(false);document.querySelector(`[data-car="${lastFocus}"]`)?.focus();});
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{view=b.dataset.view;photoIndex=0;$('#media').classList.remove('expanded','viewer-active');renderMedia();writeUrl();}));
$('#media').addEventListener('click',e=>{if(e.target.closest('[data-open-3d]')){view='3d';sourceIndex=Math.max(0,sources(current).findIndex(s=>s.verified.interior));renderMedia();writeUrl();}if(e.target.closest('[data-open-photos]')){view='exterieur';renderMedia();writeUrl();}});
$('#thumbnails').addEventListener('click',e=>{const b=e.target.closest('[data-photo]');if(b){photoIndex=Number(b.dataset.photo);renderMedia();writeUrl();$('#thumbnails').querySelector(`[data-photo="${photoIndex}"]`)?.focus();}});
$('#trim').addEventListener('change',e=>{trimId=e.target.value;fuelIntent='';renderVersions();writeUrl();});
$('#motor').addEventListener('change',e=>{motorId=e.target.value;fuelIntent='';renderVersions();writeUrl();});
$('#enlarge').addEventListener('click',()=>{const p=currentPhotos()[photoIndex];if(!p)return;$('#dialog-image').src=p.src;$('#dialog-image').alt=p.alt;$('#dialog-credit').textContent=`${p.caption} · ${p.author} · ${p.license}`;$('#photo-dialog').showModal();});
$('#close-photo').addEventListener('click',()=>$('#photo-dialog').close());
$('#expand-stage').addEventListener('click',async()=>{if(document.fullscreenEnabled&&$('#media').requestFullscreen){try{await $('#media').requestFullscreen();return;}catch{/* Use an expanded inline view when fullscreen is unavailable. */}}const active=$('#media').classList.toggle('expanded');$('#expand-stage').textContent=active?'Réduire le lecteur':'Agrandir le lecteur';});
$('#copy').addEventListener('click',async e=>{if(!navigator.share&&!navigator.clipboard)return;e.preventDefault();try{if(navigator.share)await navigator.share({title:document.title,url:location.href});else{await navigator.clipboard.writeText(location.href);$('#copy').textContent='Lien copié ✓';setTimeout(()=>$('#copy').textContent='Partager cette vue ↗',2500);}}catch{/* The actual link remains available. */}});
window.addEventListener('popstate',()=>readRoute(true));
try{
  const response=await fetch(new URL('./models.json?v=41',import.meta.url));if(!response.ok)throw Error('registry');models=await response.json();
  $('#coverage').textContent=`${models.length} modèles · France 2025 · ${models.filter(available3d).length} visites intégrées`;
  $('#market-scope').innerHTML=`${models.length} dossiers représentant huit familles parmi les dix premières lignes du classement français des immatriculations de voitures neuves 2025. Sandero et Stepway sont distinguées. Ce classement ne mesure pas le parc roulant. ${link(models[0].popularity.source,'Source PFA / AAA DATA')}`;
  readRoute();
}catch{ $('#car-grid').setAttribute('aria-busy','false');$('#result-status').textContent='Le chargement des dossiers a échoué. Rechargez la page pour réessayer.';}
