// Search recovery is always an explicit choice. Counts come from the catalogue
// response; neither compatibility nor audio language is inferred here.
const excludedKeys=new Set(['q','page','sort']);
const vehicleKeys=new Set(['make','model','generation','engine','year','fuel_type','body_type']);
export function usableSearchAssistance(response) {
  const seen=new Set();
  const candidates=response?.search_assistance?.suggestions;
  return (Array.isArray(candidates)?candidates:[]).filter(item=>{
    if(item?.type!=='query'||typeof item.query!=='string'||!item.query.trim()||!Number.isInteger(item.count)||item.count<1)return false;
    const key=item.query.trim().toLocaleLowerCase();
    if(seen.has(key))return false;
    seen.add(key);return true;
  }).slice(0,3);
}

export function searchSuggestionPatch(state,item) {
  const next={...state};
  const vehicleConflict=[...vehicleKeys].some(key=>state[key]&&typeof item.filters?.[key]==='string'&&item.filters[key]&&String(state[key]).toLocaleLowerCase()!==item.filters[key].toLocaleLowerCase());
  for(const [key,value] of Object.entries(item.filters||{})){
    if(!Object.hasOwn(state,key)||excludedKeys.has(key)||typeof value!=='string')continue;
    if(vehicleConflict&&vehicleKeys.has(key))continue;
    // Explicit user criteria take priority over inferred proposal context.
    if(!state[key]||(key==='format'&&state[key]==='all'))next[key]=value;
  }
  return {...next,q:typeof item.query==='string'&&item.query.trim()?item.query.trim():state.q,page:1};
}

export function searchAssistanceMarkup(items,{escape:e,t,ui}) {
  if(!items.length)return '';
  const text=value=>typeof value==='object'&&value?value[ui]||value.fr||value.en||'':String(value||'');
  return `<div class="search-assistance-heading"><h2>${t('Une piste pour votre question','A useful search to try','Una pista para tu pregunta')}</h2><p>${t('Essayez ces termes du catalogue. Vos critères restent actifs.','Try these catalog terms. Your filters stay active.','Prueba estos términos del catálogo. Tus filtros siguen activos.')}</p></div><div class="search-assistance-options">${items.map((item,index)=>`<button type="button" data-search-assist="${index}"><span><strong dir="auto">${e(item.query)}</strong>${text(item.reason)?`<small>${e(text(item.reason))}</small>`:''}</span><span class="assistance-count">${item.count.toLocaleString(ui)} ${t(item.count===1?'résultat':'résultats',item.count===1?'result':'results',item.count===1?'resultado':'resultados')} <b aria-hidden="true">→</b></span></button>`).join('')}</div>`;
}
