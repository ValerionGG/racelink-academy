import {poster} from './paddock-home.js?v=4';
const norm=x=>String(x||'').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
const $=q=>document.querySelector(q);
const form=$('#finder'),params=new URLSearchParams(location.search);
const ui=['en','es'].includes(params.get('ui'))?params.get('ui'):'fr';
document.documentElement.lang=ui;
const tr=(fr,en,es)=>({fr,en,es})[ui];
const both=tr('TikTok et Instagram','TikTok and Instagram','TikTok e Instagram');
const labels={both,lede:tr('Les vidéos auto des créateurs, classées par voiture et par sujet.','Car videos from creators, by vehicle and topic.','Vídeos de automoción de creadores, por coche y tema.'),source:tr('Plateforme','Platform','Plataforma'),language:tr('Langue des métadonnées','Metadata language','Idioma de los metadatos'),topic:tr('Sujet','Topic','Tema'),model:tr('Modèle cité','Model mentioned','Modelo mencionado'),q:tr('Que cherchez-vous ?','What are you looking for?','¿Qué buscas?'),reset:tr('Tout effacer','Clear all','Borrar todo'),more:tr('Afficher la suite','Show more','Mostrar más'),photo:tr('Crédits photo','Photo credits','Créditos de foto'),hint:tr('Une voiture citée dans une vidéo ne garantit pas la compatibilité avec votre version.','A model mentioned in a video does not establish compatibility with your version.','Que un vídeo mencione un modelo no garantiza compatibilidad con tu versión.')};
document.querySelectorAll('[data-copy]').forEach(x=>{x.textContent=labels[x.dataset.copy]});
$('#back').href=ui==='fr'?'./':'./?ui='+ui;
form.elements.q.placeholder=tr('Golf, vidange, diagnostic…','Golf, oil change, diagnostics…','Golf, cambio de aceite, diagnóstico…');
const display=new Intl.DisplayNames([ui],{type:'language'});
const editorFr=tr('Présentation de l’éditeur en français','Publisher’s French description','Presentación del editor en francés');
const lang=x=>x==='ed-fr'?editorFr:x==='und'?tr('Non confirmée','Unconfirmed','No confirmado'):display.of(x)||x;
const brand=p=>p==='instagram'?'Instagram':'TikTok';
const cats={mechanics:tr('Mécanique','Mechanics','Mecánica'),driving:tr('Conduite et pilotage','Driving','Conducción'),engineering:tr('Ingénierie','Engineering','Ingeniería'),simracing:'Sim racing',safety:tr('Sécurité','Safety','Seguridad')};
const cat=k=>cats[k]||k.replaceAll('_',' ');
const el=(tag,txt,cls)=>{const x=document.createElement(tag);if(txt!==undefined)x.textContent=txt;if(cls)x.className=cls;return x};
let rows=[],tasks={},limit=24;
const st={q:(params.get('q')||'').slice(0,160),p:params.get('p')||'',l:params.has('l')?params.get('l'):'fr',v:params.get('v')||'',s:params.get('s')||''};
function task(id){return tasks[id]?.[ui]||id.replaceAll('_',' ')}
function filter(r,skip=''){
  if(skip!=='p'&&st.p&&r.p!==st.p || skip!=='l'&&st.l&&(st.l==='ed-fr'?!r.editorFr:r.l!==st.l)) return false;
  if(skip!=='v'&&st.v&&!r.models.has(st.v) || skip!=='s'&&st.s&&!r.s.includes(st.s))return false;
  return !st.q||norm(st.q).split(' ').every(w=>r.words.includes(w));
}
function options(key,all,values,defaultText){
  const select=form.elements[key],counts=new Map();
  for(const r of rows)if(filter(r,key))for(const id of values(r))counts.set(id,(counts.get(id)||0)+1);
  const blank=new Option(defaultText,'');
  select.replaceChildren(blank);
  for(const [id,label] of all)if(counts.has(id)||id===st[key])select.add(new Option(label+' · '+(counts.get(id)||0),id));
  if(st[key]&&![...select.options].some(o=>o.value===st[key]))select.add(new Option(st[key]+' · 0',st[key]));
  select.value=st[key];
}
let languages=[],models=[],topics=[];
function draw(){
  options('p',[['tiktok','TikTok'],['instagram','Instagram']],r=>[r.p],both);
  options('l',languages,r=>r.editorFr?[r.l,'ed-fr']:[r.l],tr('Toutes les langues','All languages','Todos los idiomas'));
  options('v',models,r=>r.models.keys(),tr('Tous les modèles','All models','Todos los modelos'));
  options('s',topics,r=>r.s,tr('Tous les sujets','All topics','Todos los temas'));
  const found=rows.filter(r=>filter(r));const number=found.length.toLocaleString(ui);
  $('#status').textContent=number+' '+tr(found.length===1?'vidéo':'vidéos',found.length===1?'video':'videos',found.length===1?'vídeo':'vídeos');
  const frag=document.createDocumentFragment();
  for(const r of found.slice(0,limit)){
    const a=el('article'), h=el('h3'), detail=el('a',r.t);detail.href='./?'+new URLSearchParams({video:r.id,...(ui!=='fr'?{ui}:{})});
    detail.dir='auto';h.append(detail);const shot=el('img');shot.src='./assets/photos/'+poster(r)+'.jpg';shot.alt='';shot.loading='lazy';a.append(shot,el('span',brand(r.p),'plat'),h,el('p',[brand(r.p),r.a,r.l==='und'?tr('Langue non confirmée','Language unconfirmed','Idioma sin confirmar'):lang(r.l),r.editorFr?editorFr:''].filter(Boolean).join(' · ')));
    const tags=el('p',undefined,'tags');const labels=[...new Set([...r.vehicles,...r.s.map(task)])].slice(0,5);
    if(!labels.length&&r.c)labels.push(cat(r.c));for(const label of labels)tags.append(el('span',label));a.append(tags);
    const native=el('a',tr('Voir sur ','Watch on ','Ver en ')+brand(r.p)+' ↗','native');native.href=r.u;native.target='_blank';native.rel='noopener noreferrer';a.append(native);frag.append(a)
  }
  if(!found.length)frag.append(el('p',tr('Aucune fiche avec ces critères. Retirez un critère ou essayez toutes les langues.','No matches. Remove a filter or try all languages.','No hay resultados. Quita un filtro o prueba todos los idiomas.')));
  $('#list').replaceChildren(frag);$('#more').hidden=limit>=found.length;
}
function sync(){
  const url=new URL(location.href);url.search='';
  if(ui!=='fr')url.searchParams.set('ui',ui);
  for(const [k,v] of Object.entries(st))if(v||k==='l')url.searchParams.set(k,v);
  history.replaceState(null,'',url);
}
function sort(map){return [...map].sort((a,b)=>a[1].localeCompare(b[1],ui,{sensitivity:'base'}))}
let ready=false;
form.addEventListener('submit',e=>e.preventDefault());
form.addEventListener('change',e=>{if(!ready||!['p','l','v','s'].includes(e.target.name))return;st[e.target.name]=e.target.value;limit=24;draw();sync()});
form.elements.q.addEventListener('input',()=>{if(!ready)return;st.q=form.elements.q.value;limit=24;draw();sync()});
$('#reset').onclick=()=>{if(!ready)return;Object.keys(st).forEach(k=>st[k]='');form.elements.q.value='';limit=24;draw();sync();form.elements.q.focus()};
$('#more').onclick=()=>{const old=limit;limit+=24;draw();$('#list').children[old]?.querySelector('h3 a')?.focus()};
async function start(){
 try{
  const res=await fetch('./social-index.json');if(!res.ok)throw Error();const d=await res.json();if(d.version!==1||!Array.isArray(d.items))throw Error();
  tasks=d.tasks;const m=new Map(),l=new Map(),s=new Map();rows=d.items.map(r=>{
    // Only link to a canonical public post. Ignore untrusted or malformed destinations.
    const u=new URL(r.u);if(u.protocol!=='https:'||!['tiktok','instagram'].includes(r.p)||!['www.'+r.p+'.com',r.p+'.com'].includes(u.host)||u.username||u.password)throw Error();
    const models=new Map();r.v.forEach(([make,model])=>{if(model){const label=[make,model].filter(Boolean).join(' ');models.set(norm(label),label);if(!m.has(norm(label)))m.set(norm(label),label)}});
    const vehicles=r.v.map(v=>v.filter(Boolean).join(' ')).filter(Boolean);
    l.set(r.l,lang(r.l));if(r.editorFr)l.set('ed-fr',editorFr);r.s.forEach(k=>s.set(k,task(k)));return {...r,models,vehicles,words:norm([r.t,r.a,...vehicles,...r.s.map(task),cat(r.c)].join(' '))}
  });
  models=sort(m);languages=sort(l);topics=sort(s);ready=true;form.elements.q.value=st.q;draw();
 }catch{$('#status').textContent=tr('Impossible de charger le catalogue social.','The social catalogue could not be loaded.','No se pudo cargar el catálogo social.');const back=el('a',tr('Ouvrir la bibliothèque','Open the library','Abrir la biblioteca'));back.href='./?browse=1';$('#list').replaceChildren(back)}
}
start();
