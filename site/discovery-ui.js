export function createDiscoveryUI(ctx) {
  const {escape:e,t}=ctx;
  const $=s=>document.querySelector(s);
  const text=value=>typeof value==='object'&&value ? value[ctx.getUi()]||value.fr||value.en||'' : String(value||'');
  let catalog=null,intent='',latestResults=null,searchVersion=0,recommendVersion=0,timer;
  let suggestions=[],active=-1,contextTopics=[];
  $('.search-shell').insertAdjacentHTML('beforeend','<div id="search-helper" class="search-helper" hidden></div>');
  const recent=()=>{const items=ctx.storage.get('rl-search-recent',[]);return Array.isArray(items)?items.filter(x=>typeof x==='string'&&x.length<161).slice(0,5):[];};
  function remember(query){if(query?.trim()&&query.trim().length<161)ctx.storage.set('rl-search-recent',[query.trim(),...recent().filter(x=>x!==query.trim())].slice(0,5));}
  const icons={maintain:'↻',solve:'⌕',drive:'↗',understand:'⌁',sim:'⊕',career:'◇'};
  const personalKeys=['make','model','generation','year','engine','fuel_type','body_type','spec','language','duration','platform','level','license','transcript'];
  const request=params=>new URLSearchParams(Object.entries(params).filter(([,v])=>v!==''&&v!==undefined));
  const stateContext=()=>Object.fromEntries(Object.entries(ctx.getState()).filter(([k])=>!['page','sort'].includes(k)));
  const count=n=>Number(n||0).toLocaleString(ctx.getUi());
  const dateLabel=value=>{const date=new Date(value);return Number.isNaN(date.valueOf())?'—':new Intl.DateTimeFormat(ctx.getUi(),{dateStyle:'medium'}).format(date);};
  function topicButton(topic,compact=false) {
    return `<button type="button" class="${compact?'related-topic':'topic-card'}" data-discovery-topic="${e(topic.id)}" ${compact?'data-topic-context="true"':''}><span>${e(text(topic.label))}</span><small>${e(text(compact?topic.reason:topic.description))}</small><span class="topic-foot">${typeof topic.count==='number'?`${count(topic.count)} ${t('ressources','resources','recursos')}`:t('Explorer le sujet','Explore topic','Explorar tema')} <b aria-hidden="true">↗</b></span></button>`;
  }
  function render() {
    const root=$('#discovery-hub');
    if(!catalog){root.innerHTML='';return;}
    const activeTopics=catalog.topics.filter(x=>x.count>0);
    const picked=intent?activeTopics.filter(x=>x.intent===intent):catalog.intents.map(i=>activeTopics.find(x=>x.intent===i.id)).filter(Boolean);
    root.innerHTML=`<div class="discovery-heading"><div><p class="eyebrow">${t('UN BESOIN. UN POINT DE DÉPART.','A NEED. A PLACE TO START.','UNA NECESIDAD. UN PUNTO DE PARTIDA.')}</p><h2>${t('Qu’avez-vous envie de faire ?','What would you like to do?','¿Qué quieres hacer?')}</h2></div><a class="discovery-catalog-link" href="#catalog-heading">${t('Voir tout le catalogue','Browse the whole catalog','Ver todo el catálogo')} ↘</a></div>
      <div class="intent-list" role="group" aria-label="${t('Choisir un objectif','Choose a goal','Elegir un objetivo')}">${catalog.intents.map((item,i)=>`<button type="button" class="intent-choice ${intent===item.id?'active':''}" data-intent="${e(item.id)}" aria-pressed="${intent===item.id}"><span class="intent-index">0${i+1} <i aria-hidden="true">${icons[item.id]||'↗'}</i></span><strong>${e(text(item.label))}</strong><small>${e(text(item.description))}</small></button>`).join('')}</div>
      <div class="topics-heading"><strong>${intent?e(text(catalog.intents.find(x=>x.id===intent)?.label)):t('Six portes d’entrée pour commencer','Six starting points','Seis puntos de partida')}</strong><span>${intent?`<button type="button" data-intent="">${t('Tous les objectifs','All goals','Todos los objetivos')} ↗</button>`:t('Choisissez un objectif pour découvrir tous ses sujets.','Choose a goal to see all its topics.','Elige un objetivo para ver todos sus temas.')}</span></div>
      <div class="topic-grid">${picked.map(x=>topicButton(x)).join('')}</div><p class="discovery-scope">${t('Comptages sur le catalogue entier. À l’ouverture d’un sujet, votre véhicule, votre langue et vos autres filtres personnels sont conservés.','Counts cover the whole catalog. Opening a topic keeps your vehicle, language and other personal filters.','Los recuentos abarcan todo el catálogo. Al abrir un tema se conservan vehículo, idioma y otros filtros personales.')}</p>
      <div id="editorial-picks"></div>`;
    renderShelves();
    root.querySelectorAll('[data-intent]').forEach(button=>button.addEventListener('click',()=>{
      intent=button.dataset.intent;render();
      root.querySelector(`[data-intent="${intent}"]`)?.focus({preventScroll:true});
    }));
  }
  function renderShelves() {
    const root=$('#editorial-picks');
    if(!root||!catalog)return;
    const shelves=(catalog.shelves||[]).filter(s=>s.items?.length);
    if(!shelves.length){root.innerHTML='';return;}
    const hidden=ctx.storage.get('rl-library-hide-picks',false);
    root.innerHTML=`<div class="editorial-heading"><div><p class="eyebrow">${t('LE CHOIX RACELINK','RACELINK PICKS','SELECCIÓN RACELINK')}</p><h3>${t('Des ressources pour commencer.','Useful starting points.','Puntos de partida útiles.')}</h3></div><button type="button" id="toggle-editorial" aria-expanded="${!hidden}" aria-controls="editorial-rails">${hidden?t('Afficher les sélections','Show picks','Mostrar selecciones'):t('Masquer les sélections','Hide picks','Ocultar selecciones')}</button></div>
      <div id="editorial-rails" ${hidden?'hidden':''}><div class="editorial-grid">${shelves.map((s,i)=>`<section class="editorial-shelf shelf-${i%3}"><div class="shelf-title"><span>0${i+1}</span><h4>${e(text(s.label||s.title))}</h4></div><p>${e(text(s.description))}</p>${s.items.map(item=>{
        const v=item.video||item;
        return `<article class="editorial-video">${ctx.picks?.badge('video',v.id||item.video_id||item.videoId,{compact:true})||''}<button data-video="${e(v.id||item.video_id||item.videoId)}" type="button"><span aria-hidden="true">↗</span><strong dir="auto">${e(v.title)}</strong></button><small>${e(v.creator)} · ${e(ctx.langName(v.language))}${/estimate|inferred/.test(v.language_status||'')?' *':''}</small><p>${e(text(item.reason||item.rationale))}</p><details><summary>${t('Pourquoi cette sélection ?','Why this pick?','¿Por qué esta selección?')}</summary><p>${e(text(item.evidence?.note||item.evidence)||t('Sélection sur le titre, la source et les métadonnées disponibles.','Selected using title, source and available metadata.','Selección basada en título, fuente y metadatos.'))}</p><small>${t('Revue :','Reviewed:','Revisión:')} ${e(dateLabel(item.reviewedAt||item.reviewed_at||s.reviewedAt||s.reviewed_at))}</small></details></article>`;
      }).join('')}</section>`).join('')}</div><details class="curation-policy"><summary>${t('Comment les mises en avant sont contrôlées','How featured picks are controlled','Cómo se controlan las selecciones')}</summary><p>${t('Sélections explicites, raisons documentées et date de révision. Les entrées expirées ou désactivées sont retirées des mises en avant. Aucun classement par popularité supposée, aucune lecture automatique. Une sélection sur métadonnées ne vaut pas visionnage complet ni validation technique.','Explicit picks, documented reasons and review dates. Expired or disabled entries are removed from featured picks. No assumed popularity ranking and no autoplay. Metadata selection is not a full viewing or technical validation.','Selecciones explícitas, motivos documentados y fechas de revisión. Las entradas caducadas o desactivadas se retiran. Sin popularidad supuesta ni reproducción automática. La selección por metadatos no equivale a revisión completa o validación técnica.')}</p></details></div>`;
    $('#toggle-editorial').addEventListener('click',()=>{ctx.storage.set('rl-library-hide-picks',!hidden);renderShelves();$('#toggle-editorial').focus();});
  }
  function chooseTopic(id,resolved) {
    const topic=resolved||catalog?.topics.find(x=>x.id===id);
    if(!topic)return;
    remember(topic.query);
    closeSuggestions();
    const keep=Object.fromEntries(personalKeys.map(k=>[k,ctx.getState()[k]||'']));
    ctx.applySearch({...keep,...topic.filters,q:topic.query||''});
  }
  async function load() {
    try{catalog=await window.getCatalogJson('/aide/api/discovery');ctx.picks?.setVideos(catalog.shelves||[]);render();ctx.onPicksChange?.();}catch{
      $('#discovery-hub').innerHTML=`<p class="small-note">${t('L’exploration par objectif est momentanément indisponible. La recherche reste accessible.','Goal browsing is temporarily unavailable. Search is still available.','La exploración por objetivos no está disponible. Puedes usar la búsqueda.')}</p>`;
    }
  }
  function closeSuggestions() {
    ++searchVersion;clearTimeout(timer);suggestions=[];active=-1;
    $('#search-suggestions').hidden=true;$('#search').setAttribute('aria-expanded','false');$('#search').removeAttribute('aria-activedescendant');
    $('#suggestion-status').textContent='';
    $('#search-helper').hidden=true;
  }
  function renderSuggestions() {
    const root=$('#search-suggestions');
    root.innerHTML=suggestions.map((item,i)=>`<button type="button" role="option" tabindex="-1" id="suggestion-${i}" data-suggestion="${i}" aria-selected="${active===i}"><span class="suggestion-kind">${item.type==='history'?t('RÉCENT','RECENT','RECIENTE'):item.type==='video'?t('VIDÉO','VIDEO','VÍDEO'):t('SUJET','TOPIC','TEMA')}</span><span><strong dir="auto">${e((item.match_basis==='editorial_default'?'':item.completion)||text(item.label))}</strong>${item.completion&&item.match_basis!=='editorial_default'?`<small>${e(text(item.label))}</small>`:''}${item.correction?`<small class="suggestion-correction">${e(item.corrections?.length ? t('Proposition : ','Suggestion: ','Propuesta: ')+item.corrections.map(c=>`${c.from} → ${c.to}`).join(' · ') : text(item.correction))}</small>`:''}<small>${e(item.correction?'':text(item.reason))}${typeof item.count==='number'?`${item.correction?'':' · '}${count(item.count)} ${t('ressources','resources','recursos')}`:''}</small></span><b aria-hidden="true">↗</b></button>`).join('');
    root.hidden=!suggestions.length;$('#search').setAttribute('aria-expanded',String(suggestions.length>0));
    if(active>=0)$('#search').setAttribute('aria-activedescendant',`suggestion-${active}`);else $('#search').removeAttribute('aria-activedescendant');
    $('#suggestion-status').textContent=suggestions.length?`${suggestions.length} ${t('suggestions disponibles. Flèches pour parcourir, Entrée pour choisir.','suggestions available. Use arrows to navigate and Enter to choose.','sugerencias. Usa las flechas y pulsa Intro para elegir.')}`:'';
    const hasRecent=suggestions.some(x=>x.type==='history');
    $('#search-helper').innerHTML=`<span>${suggestions.length?t('Suggestions liées à votre recherche.','Suggestions related to your search.','Sugerencias relacionadas con tu búsqueda.'):t('Pas de suggestion précise. Lancez votre recherche avec Entrée.','No precise suggestion. Press Enter to search.','Sin sugerencias precisas. Pulsa Intro para buscar.')}</span>${hasRecent?`<button type="button" data-clear-recent>${t('Effacer l’historique','Clear history','Borrar historial')}</button>`:''}`;
    $('#search-helper').hidden=false;
  }
  async function suggest() {
    const version=++searchVersion,q=$('#search').value.trim();
    $('#search-helper').textContent=t('Recherche de suggestions…','Finding suggestions…','Buscando sugerencias…');$('#search-helper').hidden=false;
    try {
      const response=await window.getCatalogJson(`/aide/api/suggestions?${request({...stateContext(),q,ui:ctx.getUi()})}`);
      if(version!==searchVersion||document.activeElement!==$('#search'))return;
      const history=q?[]:recent().slice(0,2).map(query=>({type:'history',query,label:query,reason:t('Sur cet appareil uniquement','On this device only','Solo en este dispositivo')}));
      suggestions=[...history,...(response.suggestions||[])].slice(0,6);active=-1;renderSuggestions();
    } catch {if(version===searchVersion)closeSuggestions();}
  }
  function chooseSuggestion(index) {
    const item=suggestions[index];if(!item)return;
    if(item.type==='history'){remember(item.query);closeSuggestions();ctx.applySearch({...ctx.getState(),q:item.query,page:1});}
    else if(item.type==='video'){closeSuggestions();document.dispatchEvent(new Event('rl:search-chosen'));ctx.openVideo(item.video_id||item.id);}
    else chooseTopic(item.id,item);
  }
  async function recommendations(results) {
    latestResults=results;
    const version=++recommendVersion,root=$('#context-discovery');
    root.hidden=true;
    const state=ctx.getState();
    const hasContext=Object.entries(stateContext()).some(([,v])=>v);
    if(!hasContext)return;
    try {
      const response=await window.getCatalogJson(`/aide/api/recommendations?${request(stateContext())}`);
      if(version!==recommendVersion)return;
      const topics=(response.topics||[]).slice(0,4);
      contextTopics=topics;
      const precise=personalKeys.filter(k=>state[k]);
      if(!topics.length&&results.total>0)return;
      root.innerHTML=`<div class="context-heading"><div><p class="eyebrow">${results.total?t('POUR CONTINUER','KEEP EXPLORING','PARA CONTINUAR'):t('RETROUVER UNE PISTE UTILE','FIND A USEFUL NEXT STEP','ENCONTRAR UN SIGUIENTE PASO')}</p><h3>${results.total?t('Des sujets qui prolongent votre recherche','Topics related to your search','Temas relacionados con tu búsqueda'):t('Pas de réponse précise pour le moment.','No precise match yet.','Aún no hay una coincidencia precisa.')}</h3></div></div>
        <p>${e(text(response.reason)||t('Suggestions liées aux mots de votre recherche et aux sujets du catalogue.','Suggestions based on your search words and catalog topics.','Sugerencias basadas en tu búsqueda y los temas del catálogo.'))}</p>
        ${topics.length?`<div class="related-grid">${topics.map(x=>topicButton(x,true)).join('')}</div>`:''}
        ${!results.total?`<div class="recovery-actions">${state.q?`<button type="button" data-discovery-clear-query>${t('Retirer les mots recherchés','Clear search words','Quitar palabras de búsqueda')}</button>`:''}${precise.some(k=>['make','model','generation','year','engine','fuel_type','body_type'].includes(k))?`<button type="button" data-discovery-clear-vehicle>${t('Explorer sans véhicule','Explore without a vehicle','Explorar sin vehículo')}</button>`:''}<a href="#discovery-hub">${t('Revenir aux objectifs','Back to goals','Volver a los objetivos')} ↗</a></div><small>${t('Ces actions élargissent la recherche uniquement si vous les choisissez. Elles ne confirment aucune compatibilité mécanique.','These actions broaden your search only when you choose them. They do not confirm mechanical compatibility.','Estas acciones amplían la búsqueda solo cuando las eliges. No confirman compatibilidad mecánica.')}</small>`:''}`;
      root.hidden=false;
    } catch {if(version===recommendVersion)root.hidden=true;}
  }
  document.addEventListener('click',event=>{
    if(event.target.closest('[data-clear-recent]')){ctx.storage.set('rl-search-recent',[]);$('#search').focus();suggest();return;}
    const topic=event.target.closest('[data-discovery-topic]');if(topic){chooseTopic(topic.dataset.discoveryTopic,topic.hasAttribute('data-topic-context')?contextTopics.find(x=>x.id===topic.dataset.discoveryTopic):undefined);return;}
    const option=event.target.closest('[data-suggestion]');if(option){chooseSuggestion(Number(option.dataset.suggestion));return;}
    if(event.target.closest('[data-discovery-clear-query]'))ctx.clearFilter('q');
    if(event.target.closest('[data-discovery-clear-vehicle]'))ctx.clearVehicle();
    if(!event.target.closest('.search-shell'))closeSuggestions();
  });
  $('#search').addEventListener('input',()=>{closeSuggestions();timer=setTimeout(suggest,180);});
  $('#search').addEventListener('focus',()=>{clearTimeout(timer);timer=setTimeout(suggest,100);});
  $('#search').addEventListener('keydown',event=>{
    if(event.key==='Escape'){if(suggestions.length){event.preventDefault();event.stopPropagation();}closeSuggestions();return;}
    if(!suggestions.length)return;
    if(['ArrowDown','ArrowUp'].includes(event.key)){
      event.preventDefault();active=active<0?(event.key==='ArrowDown'?0:suggestions.length-1):(active+(event.key==='ArrowDown'?1:-1)+suggestions.length)%suggestions.length;renderSuggestions();
      $(`#suggestion-${active}`)?.scrollIntoView({block:'nearest'});
    }else if(event.key==='Enter'&&active>=0){event.preventDefault();chooseSuggestion(active);}
  });
  $('.search-shell').addEventListener('focusout',event=>{if(!$('.search-shell').contains(event.relatedTarget))closeSuggestions();});
  $('#search-suggestions').addEventListener('mousedown',event=>event.preventDefault());
  $('#search-form').addEventListener('submit',()=>{remember($('#search').value);closeSuggestions();});
  document.addEventListener('rl:close-suggestions',closeSuggestions);
  return {load,render,recommendations,closeSuggestions,beginSearch(){++recommendVersion;$('#context-discovery').hidden=true;},refresh(){render();if(latestResults)recommendations(latestResults);}};
}
