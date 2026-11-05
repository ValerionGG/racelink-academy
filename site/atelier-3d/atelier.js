import {families,language,partName,text,t} from './copy.js';

const $ = id=>document.getElementById(id);
const family=$('family'), part=$('part'), start=$('start'), poster=$('poster'), stage=$('stage');
const explode=$('explode'), tools=$('tools'), status=$('status');
let workshop=null, loading=false, inventory=[], exploded=false, failed=false;

document.documentElement.lang=language;
document.title='WikiSpeed SGT01 · '+text.workshop+' · RaceLink Academy';
document.querySelectorAll('[data-t]').forEach(el=>{el.textContent=text[el.dataset.t];});
document.querySelector('.skip').textContent=t('Aller au contenu','Skip to content','Saltar al contenido');
$('viewer').setAttribute('aria-label',text.canvas);
$('zoom-in').setAttribute('aria-label',text.zoomIn);
$('zoom-out').setAttribute('aria-label',text.zoomOut);
document.querySelectorAll('a[href="./"]').forEach(el=>{
  el.href=language==='fr'?'./':'./?ui='+language;
});
window.RaceLinkTheme?.updateThemeLabels(language);
const overview=new Option(text.all,'all');
family.replaceChildren(overview,...Object.entries(families).map(([key,[name]])=>new Option(name,key)));
family.disabled=false;
start.hidden=false;
status.textContent=text.initial;
function chosenSolid() {
  return part.value==='' || family.value==='all' ? null : Number(part.value);
}
function itemsForFamily() {
  return inventory.filter(record=>record[1]===family.value);
}
function populateParts() {
  const items=itemsForFamily();
  const options=items.map(([id,,name,parent])=>{
    const label=partName(name || parent);
    return {key:id,label};
  }).sort((a,b)=>a.label.localeCompare(b.label,language,{numeric:true}) || a.key-b.key);
  const choices=options.map(({key,label})=> new Option(label+' · '+String(key+1),String(key)));
  part.replaceChildren(new Option(text.pieceAll,''),...choices);
  $('part-field').hidden=items.length===0;
}
function sync() {
  const key=family.value,group=families[key],index=chosenSolid();
  const selected=index===null?null:inventory.find(([id])=>id===index);
  const source=selected && (selected[2] || selected[3]);
  $('stage-name').textContent=(workshop && selected) ? partName(source) : (group?.[0] || text.all);
  $('selection-title').textContent=selected?partName(source):group?.[0] || text.overview;
  $('selection-copy').textContent=selected ?
    (source?text.inGroup+' · '+group[0]:text.unnamed) : group?.[2] || text.description;
  $('selection-count').textContent=selected ? text.solid+' '+(index+1)+' / 271' : group ?
    group[1]+' '+text.solids : '271 '+text.solids+' · 8 '+text.families;
  $('native').hidden=!source;
  $('native').textContent=source ? text.geometry+' · '+source : '';
  const asset=key==='all'?'sgt01':key;
  poster.src=new URL('./'+asset+'.webp',import.meta.url).href;
  poster.alt=text.viewOf+' · WikiSpeed SGT01 · '+(group?.[0] || text.all);
  const inventoryList=$('inventory-list');
  const rows=group && inventory.length ?
    [...new Set(itemsForFamily().map(([, , name,parent])=>partName(name||parent)))].sort((a,b)=>a.localeCompare(b,language)) :
    Object.values(families).map(([name,count])=>name+' · '+count);
  inventoryList.replaceChildren(...rows.map(label=>{
    const li=document.createElement('li');
    li.textContent=label;
    return li;
  }));
  $('part-list').hidden=!!group && inventory.length===0;
  explode.disabled=selected!==null;
  if (explode.disabled) exploded=false;
  explode.setAttribute('aria-pressed',String(exploded));
  workshop?.select(key,index,exploded);
  const url=new URL(location.href);
  if (key==='all') url.searchParams.delete('ensemble'); else url.searchParams.set('ensemble',key);
  if (index===null) url.searchParams.delete('piece'); else url.searchParams.set('piece',String(index));
  history.replaceState(null,'',url);
}
function fallback() {
  workshop?.dispose();
  workshop=null;failed=true;
  poster.hidden=false;tools.hidden=true;start.hidden=false;start.disabled=false;
  start.querySelector('[data-t]').textContent=text.loadingFailure;
  status.textContent=text.fallback;
  sync();
}
async function activate(focusCanvas) {
  if (workshop || loading) return;
  loading=true;start.disabled=true;status.textContent=text.loading;
  try {
    const {createWorkshop}=await import('./model.js');
    workshop=await createWorkshop(stage,text.canvas,fallback);
    failed=false;start.hidden=true;poster.hidden=true;tools.hidden=false;status.textContent=text.ready;
    sync();
    if (focusCanvas) workshop.focus();
  } catch {fallback();}
  finally {loading=false;start.disabled=false;}
}
const params=new URLSearchParams(location.search);
if (Object.hasOwn(families,params.get('ensemble'))) family.value=params.get('ensemble');
populateParts();sync();
start.addEventListener('click',()=>activate(true));
family.addEventListener('change',()=>{
  exploded=false;populateParts();sync();
  if (!workshop&&!failed&&!loading) status.textContent=text.initial;
});
part.addEventListener('change',()=>{
  exploded=false;sync();
  if (chosenSolid()!==null&&!workshop&&!failed) activate(false);
});
explode.addEventListener('click',()=>{
  exploded=!exploded;
  explode.setAttribute('aria-pressed',String(exploded));
  workshop?.select(family.value,chosenSolid(),exploded);
});
$('angle').addEventListener('change',event=>workshop?.angle(event.target.value));
$('reset').addEventListener('click',()=>workshop?.fit());
$('zoom-in').addEventListener('click',()=>workshop?.zoom(1.24));
$('zoom-out').addEventListener('click',()=>workshop?.zoom(1/1.24));
try {
  const response=await fetch(new URL('./parts.json',import.meta.url));
  if (!response.ok) throw new Error('inventory');
  const rows=await response.json();
  if (rows.length!==271 || new Set(rows.map(([id])=>id)).size!==271) throw new Error('inventory');
  inventory=rows;
  populateParts();
  const wanted=params.get('piece');
  if (wanted!==null && itemsForFamily().some(([id])=>String(id)===wanted)) part.value=wanted;
  sync();
  if (chosenSolid()!==null) activate(false);
} catch {
  // Family colours, descriptions, previews and counts are available without the detailed index.
  populateParts();sync();
}
