// The catalogue owns committed state. This module only stages the filter sheet.
// No request, URL, language inference or vehicle compatibility is produced here.
export const FILTER_KEYS=Object.freeze(['category','platform','level','duration','content_format','domain','transcript','license','language','make','model','generation','engine','year','fuel_type','body_type','task','system','spec']);
const PANEL_KEYS=new Set(['category','platform','level','duration','content_format','domain','transcript','license']);

export function createFilterDraft({getState,onApply}) {
  let baseline=null,patch={};
  const active=()=>baseline!==null;
  const value=x=>x??'';
  function begin(){if(!active()){baseline={...getState()};patch={};}return read();}
  function read(){return {...getState(),...patch};}
  function set(key,next){
    if(!active()||!FILTER_KEYS.includes(key))return false;
    if(value(next)===value(baseline[key]))delete patch[key];else patch[key]=value(next);
    return true;
  }
  function reset(){if(!active())return;for(const key of FILTER_KEYS)set(key,'');}
  function cancel(){baseline=null;patch={};}
  function apply(){
    if(!active())return false;
    const changes={...patch},before=baseline;
    cancel();
    if(!Object.keys(changes).length)return false;
    try{onApply(changes);}catch(error){baseline=before;patch=changes;throw error;}
    return true;
  }
  return {begin,read,set,reset,cancel,apply,isActive:active,isDirty:()=>Object.keys(patch).length>0,changes:()=>({...patch})};
}

export function createFilterStudio({root,t,getState,onApply,onDraftChange=()=>{}}) {
  const $=selector=>root.querySelector(selector);
  const $$=selector=>[...root.querySelectorAll(selector)];
  const draft=createFilterDraft({getState,onApply});
  const topics=$('.filter-topics');
  const firstSection=$('.filter-section');
  if(topics){if(firstSection&&topics!==firstSection)root.insertBefore(topics,firstSection);topics.open=true;}
  const platformSection=$('[data-filter-copy="source"]')?.closest('.filter-section');
  const preferences=$('[data-filter-copy="preferences"]')?.closest('.filter-section');
  if(platformSection&&preferences)root.insertBefore(platformSection,preferences);
  root.classList.add('filter-studio');
  const notice=root.ownerDocument.createElement('p');
  notice.id='filter-draft-note';notice.className='filter-draft-note';notice.setAttribute('role','status');notice.hidden=true;
  root.append(notice);
  function labelGroup(selector,id,text){
    const title=$(selector);if(!title)return;
    title.id=id;title.textContent=text;
    const group=title.closest('.filter-section');
    if(group){group.setAttribute('aria-labelledby',id);group.dataset.filterGroup=id.replace('filter-','').replace('-title','');}
  }
  function update(){
    root.setAttribute('aria-label',t('Filtres du catalogue','Catalog filters','Filtros del catálogo'));
    root.classList.toggle('has-filter-draft',draft.isActive());
    labelGroup('[data-filter-copy="topic"]','filter-topic-title',t('Sujet','Topic','Tema'));
    labelGroup('[data-filter-copy="source"]','filter-platform-title',t('Plateforme','Platform','Plataforma'));
    labelGroup('[data-filter-copy="preferences"]','filter-preferences-title',t('Type, niveau et durée','Type, level and duration','Tipo, nivel y duración'));
    const sourceHint=$('[data-filter-copy="sourceHint"]');
    if(sourceHint){sourceHint.id='filter-platform-hint';sourceHint.textContent=t('Le site où regarder la ressource : YouTube, TikTok, Instagram…','Where to watch the resource: YouTube, TikTok, Instagram…','Dónde ver el recurso: YouTube, TikTok, Instagram…');}
    const platforms=$('#platform-choices');
    if(platforms){platforms.setAttribute('aria-labelledby','filter-platform-title');platforms.setAttribute('aria-describedby','filter-platform-hint');}
    const categories=$('#category-filters');
    if(categories){categories.setAttribute('role','group');categories.setAttribute('aria-labelledby','filter-topic-title');}
    const type=$('#content_format'),explanation=$('.filter-explainer');
    if(type&&explanation){explanation.id='filter-type-explanation';type.setAttribute('aria-describedby',explanation.id);}
    const reset=$('#reset-filters');
    if(reset){reset.setAttribute('aria-label',t('Effacer les critères, y compris la langue et le véhicule','Clear criteria, including language and vehicle','Borrar criterios, incluidos idioma y vehículo'));}
    const state=draft.isActive()?draft.read():getState();
    for(const key of PANEL_KEYS){
      const control=$(`#${key}`);if(!control)continue;
      if(key==='license'||key==='transcript')control.checked=Boolean(state[key]);else control.value=state[key]||'';
    }
    for(const [selector,key,attribute] of [['[data-category]','category','category'],['[data-platform-choice]','platform','platformChoice']]){
      $$(selector).forEach(button=>{const selected=button.dataset[attribute]===(state[key]||'');button.setAttribute('aria-pressed',String(selected));button.classList.toggle('active',selected);});
    }
    notice.hidden=!draft.isActive();
    notice.textContent=draft.isDirty()?t('Modifications non appliquées. Fermer annule vos changements.','Changes not applied. Closing discards your changes.','Cambios sin aplicar. Cerrar descarta los cambios.'):t('Choisissez vos critères, puis appliquez les filtres.','Choose your criteria, then apply the filters.','Elige los criterios y aplica los filtros.');
  }
  function changed(){update();onDraftChange();}
  function captureClick(event){
    if(!draft.isActive())return;
    const button=event.target.closest('button');if(!button||!root.contains(button))return;
    if(button.id==='reset-filters')draft.reset();
    else if(button.hasAttribute('data-category'))draft.set('category',button.dataset.category);
    else if(button.hasAttribute('data-platform-choice'))draft.set('platform',button.dataset.platformChoice);
    else return;
    event.preventDefault();event.stopPropagation();changed();
  }
  function captureChange(event){
    if(!draft.isActive()||!PANEL_KEYS.has(event.target.id))return;
    const {id,value,checked}=event.target;
    draft.set(id,id==='transcript'?(checked?'available':''):id==='license'?(checked?'open':''):value);
    event.stopPropagation();changed();
  }
  root.addEventListener('click',captureClick,true);
  root.addEventListener('change',captureChange,true);
  update();
  return {
    update,isDraftActive:draft.isActive,hasPendingChanges:draft.isDirty,
    beginDraft(){draft.begin();changed();},
    cancelDraft(){draft.cancel();changed();},
    applyDraft(){const applied=draft.apply();changed();return applied;},
    // Capture before facet buttons are replaced, including the desktop sidebar.
    captureFocus(){
      const focused=root.ownerDocument.activeElement;
      if(!focused||!root.contains(focused))return ()=>{};
      const attribute=focused.hasAttribute('data-category')?'category':focused.hasAttribute('data-platform-choice')?'platformChoice':null;
      if(!attribute)return ()=>{};
      const value=focused.dataset[attribute];
      return ()=>$$('[data-category],[data-platform-choice]').find(button=>button.dataset[attribute]===value)?.focus({preventScroll:true});
    },
    destroy(){root.removeEventListener('click',captureClick,true);root.removeEventListener('change',captureChange,true);notice.remove();draft.cancel();}
  };
}
