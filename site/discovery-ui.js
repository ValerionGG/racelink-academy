import {icon} from './icons.js';
export function createDiscoveryUI(ctx) {
  const {escape:e,t}=ctx;
  const $=s=>document.querySelector(s);
  const text=value=>typeof value==='object'&&value ? value[ctx.getUi()]||value.fr||value.en||'' : String(value||'');
  let catalog=null,visualAssets=[],intent='',latestResults=null,searchVersion=0,recommendVersion=0,timer;
  let suggestions=[],active=-1,contextTopics=[];
  $('.search-shell').insertAdjacentHTML('beforeend','<div id="search-helper" class="search-helper" hidden></div>');
  const recent=()=>{const items=ctx.storage.get('rl-search-recent',[]);return Array.isArray(items)?items.filter(x=>typeof x==='string'&&x.length<161).slice(0,5):[];};
  function remember(query){if(query?.trim()&&query.trim().length<161)ctx.storage.set('rl-search-recent',[query.trim(),...recent().filter(x=>x!==query.trim())].slice(0,5));}
  const personalKeys=['make','model','generation','year','engine','fuel_type','body_type','spec','language','duration','platform','level','license','transcript','format','content_format'];
  const hasValue=value=>value!==''&&value!==undefined&&value!==null&&value!=='all';
  const imageUrl=value=>{try{const local=typeof value==='string'&&/^\.\/assets\/[\w./-]+$/.test(value)&&!value.split('/').includes('..');const url=new URL(value,local?import.meta.url:undefined);return url.protocol==='https:'||local?url.href:'';}catch{return '';}};
  const platformName=value=>({youtube:'YouTube',dailymotion:'Dailymotion',vimeo:'Vimeo',tiktok:'TikTok',instagram:'Instagram',facebook:'Facebook',twitch:'Twitch',bilibili:'Bilibili'})[value]||value||'';
  const request=params=>new URLSearchParams(Object.entries(params).filter(([,v])=>v!==''&&v!==undefined));
  const stateContext=()=>Object.fromEntries(Object.entries(ctx.getState()).filter(([k])=>!['page','sort'].includes(k)));
  const count=n=>Number(n||0).toLocaleString(ctx.getUi());
  const dateLabel=value=>{const date=new Date(value);return Number.isNaN(date.valueOf())?'—':new Intl.DateTimeFormat(ctx.getUi(),{dateStyle:'medium'}).format(date);};
  const durationLabel=value=>{const seconds=Number(value);if(!Number.isFinite(seconds)||seconds<=0)return '';const n=Math.round(seconds);return n>=3600?`${Math.floor(n/3600)}:${String(Math.floor(n%3600/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`:`${Math.floor(n/60)}:${String(n%60).padStart(2,'0')}`;};
  function videoLanguage(video) {
    if(!video.language||video.language==='und')return t('Langue non renseignée','Language not provided','Idioma no indicado');
    const label=ctx.langName(video.language),status=String(video.language_status||'');
    if(video.language_confidence==='estimated'||/estimate|inferred/.test(status))return `${label}${t(' · estimé',' · estimated',' · estimado')}`;
    if(/not_verified|unknown/.test(status))return `${label}${t(' · à confirmer',' · unconfirmed',' · sin confirmar')}`;
    return label;
  }
  function topicButton(topic,compact=false) {
    return `<button type="button" class="${compact?'related-topic':'topic-card'}" data-discovery-topic="${e(topic.id)}" ${compact?'data-topic-context="true"':''}><span>${e(text(topic.label))}</span><small>${e(text(compact?topic.reason:topic.description))}</small><span class="topic-foot">${typeof topic.count==='number'?`${count(topic.count)} ${topic.count===1?t('ressource','resource','recurso'):t('ressources','resources','recursos')}`:t('Explorer le sujet','Explore topic','Explorar tema')} <b aria-hidden="true">↗</b></span></button>`;
  }
  function render() {
    const root=$('#discovery-hub');
    if(!catalog){root.innerHTML='';return;}
    const allTopicsOpen=root.querySelector('.all-topics')?.open||false;
    const activeTopics=catalog.topics.filter(x=>x.count>0);
    const picked=intent?activeTopics.filter(x=>x.intent===intent):activeTopics;
    const entries=[
      {id:'maintenance',category:'mechanics',label:t('Entretenir ma voiture','Maintain my car','Cuidar mi coche'),description:t('Entretien et réparations','Maintenance and repairs','Mantenimiento y reparaciones')},
      {id:'driving',category:'driving',label:t('Mieux piloter','Improve my driving','Mejorar mi pilotaje'),description:t('Freinage et trajectoires','Braking and racing lines','Frenada y trazadas')},
      {id:'simracing',category:'simracing',label:t('Régler mon simulateur','Set up my simulator','Ajustar mi simulador'),description:t('Réglages et technique','Setup and technique','Ajustes y técnica')}
    ];
    root.innerHTML=`<div class="home-intro"><h2>${t('Explorez vos sujets','Explore your interests','Explora tus temas')}</h2><button type="button" class="discovery-catalog-link" data-browse-all>${t('Tout explorer','Explore everything','Explorar todo')} ↗</button></div>
      <div class="entry-grid">${entries.map(entry=>{
        const asset=visualAssets.find(item=>item.id===entry.id),src=imageUrl(asset?.url);
        return `<button type="button" class="entry-card entry-${entry.category}" data-entry-category="${entry.category}"><span class="entry-visual">${src?`<img src="${e(src)}" alt="${e(asset?.alt||'')}" width="640" height="360" loading="lazy" decoding="async" style="object-position:${e(asset?.position||'50% 50%')}">`:''}</span><span class="entry-copy"><strong>${e(entry.label)}</strong><small>${e(entry.description)}</small><span class="entry-cta" aria-hidden="true">${icon('arrow-up-right',{size:18})}</span></span></button>`;
      }).join('')}</div>
      <details class="discovery-photo-credits"><summary>${t('Crédits photos','Photo credits','Créditos de las fotos')}</summary>${visualAssets.map(asset=>`<p><a href="${e(imageUrl(asset.sourceUrl))}" target="_blank" rel="noopener noreferrer">${e(asset.credit)}</a> · <a href="${e(imageUrl(asset.licenseUrl))}" target="_blank" rel="noopener noreferrer">${e(asset.license)}</a></p>`).join('')}<p>${t('Photos d’illustration · cadrage adapté à l’écran.','Illustrative photos · display crop adapted to the screen.','Fotos ilustrativas · encuadre adaptado a la pantalla.')}</p></details>
      <div id="editorial-picks"></div>
      <details class="all-topics" ${allTopicsOpen?'open':''}><summary>${t('Tous les sujets','All topics','Todos los temas')}</summary>
        <div class="intent-list" role="group" aria-label="${t('Filtrer les sujets par objectif','Filter topics by goal','Filtrar temas por objetivo')}"><button type="button" class="intent-choice ${intent?'':'active'}" data-intent="" aria-pressed="${!intent}"><strong>${t('Tous les objectifs','All goals','Todos los objetivos')}</strong></button>${catalog.intents.map(item=>`<button type="button" class="intent-choice ${intent===item.id?'active':''}" data-intent="${e(item.id)}" aria-pressed="${intent===item.id}"><strong>${e(text(item.label))}</strong><small>${e(text(item.description))}</small></button>`).join('')}</div>
        <div class="topic-grid">${picked.map(x=>topicButton(x)).join('')}</div><p class="discovery-scope">${t('Les sujets conservent votre véhicule, votre langue et vos autres filtres. Les nombres affichés portent sur le catalogue entier.','Topics keep your vehicle, language and other filters. Counts cover the whole catalog.','Los temas conservan vehículo, idioma y otros filtros. Los recuentos abarcan todo el catálogo.')}</p>
      </details>`;
    renderShelves();
    root.querySelectorAll('.entry-card img').forEach(img=>img.addEventListener('error',()=>{img.hidden=true;},{once:true}));
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
    const seen=new Set();
    const featured=shelves.flatMap(s=>s.items.map(item=>({item,shelf:s}))).filter(({item})=>{const id=item.video?.id||item.id||item.video_id||item.videoId;if(!id||seen.has(id)||(ctx.getState().language&&(item.video||item).language!==ctx.getState().language))return false;seen.add(id);return true;}).slice(0,6);
    if(!featured.length){root.innerHTML=`<div class="language-empty-picks">${t('Explorez les ressources dans la langue choisie.','Explore resources in your chosen language.','Explora recursos en el idioma elegido.')}<button type="button" data-browse-all>${t('Voir le catalogue','Browse the catalog','Ver el catálogo')} →</button></div>`;return;}
    const hidden=ctx.storage.get('rl-library-hide-picks',false);
    root.innerHTML=`<div class="editorial-heading"><h3>${t('La sélection RaceLink','RaceLink picks','La selección RaceLink')}</h3><button type="button" id="toggle-editorial" aria-expanded="${!hidden}" aria-controls="editorial-rails" aria-label="${hidden?t('Afficher la sélection RaceLink','Show RaceLink picks','Mostrar la selección RaceLink'):t('Masquer la sélection RaceLink','Hide RaceLink picks','Ocultar la selección RaceLink')}">${hidden?t('Afficher','Show','Mostrar'):t('Masquer','Hide','Ocultar')}</button></div>
      <div id="editorial-rails" ${hidden?'hidden':''}><div class="featured-grid">${featured.map(({item,shelf:s})=>{
        const v=item.video||item;
        const id=v.id||item.video_id||item.videoId,src=imageUrl(v.thumbnail_url||v.thumbnailUrl),duration=durationLabel(v.duration_seconds??v.durationSeconds);
        const reason=text(item.reason||item.rationale),note=text(item.evidence?.note||item.evidence)||t('Sélection sur le titre, la source et les métadonnées disponibles.','Selected using title, source and available metadata.','Selección basada en título, fuente y metadatos.');
        const basis=item.evidence?.basis==='authorized_transcript'?t('Transcription consultée','Transcript reviewed','Transcripción consultada'):item.evidence?.basis==='public_video_metadata'?t('Choix sur métadonnées','Metadata-based pick','Selección por metadatos'):'';
        const reviewed=dateLabel(item.reviewedAt||item.reviewed_at||s.reviewedAt||s.reviewed_at);
        return `<article class="editorial-video"><button class="editorial-preview" data-video="${e(id)}" type="button" aria-label="${e(t('Ouvrir : ','Open: ','Abrir: ')+v.title)}"><span class="editorial-image">${src?`<img src="${e(src)}" alt="" width="480" height="270" loading="lazy" decoding="async" referrerpolicy="no-referrer">`:`<span class="thumb-fallback">${e(platformName(v.platform))}</span>`}<span class="thumb-play" aria-hidden="true">${icon('play',{size:20})}</span>${duration?`<span class="thumb-duration" aria-label="${e(t('Durée : ','Duration: ','Duración: ')+duration)}">${e(duration)}</span>`:''}</span><strong dir="auto">${e(v.title)}</strong></button>${ctx.picks?.badge('video',id,{compact:true})||''}<small class="editorial-creator" dir="auto">${e(v.creator||t('Auteur non renseigné','Creator not provided','Autor no indicado'))}</small><small class="editorial-source">${e(platformName(v.platform))} · ${e(videoLanguage(v))}</small>${basis?`<small class="editorial-basis">${e(basis)}</small>`:''}<details><summary>${t('Pourquoi ce choix ?','Why this pick?','¿Por qué esta selección?')}</summary>${reason?`<p>${e(reason)}</p>`:''}${note!==reason?`<p>${e(note)}</p>`:''}${reviewed!=='—'?`<small>${t('Revue :','Reviewed:','Revisión:')} ${e(reviewed)}</small>`:''}</details></article>`;
      }).join('')}</div><details class="curation-policy"><summary>${t('Comment ces ressources sont choisies','How these resources are chosen','Cómo se eligen estos recursos')}</summary><p>${t('Sélections explicites, raisons documentées et date de révision. Les entrées expirées ou désactivées sont retirées. Une sélection sur métadonnées ne vaut pas visionnage complet ni validation technique.','Explicit picks, documented reasons and review dates. Expired or disabled entries are removed. Metadata selection is not a full viewing or technical validation.','Selecciones explícitas, motivos documentados y fechas de revisión. Las entradas caducadas o desactivadas se retiran. La selección por metadatos no equivale a revisión completa o validación técnica.')}</p></details></div>`;
    root.querySelectorAll('.editorial-image img').forEach(img=>img.addEventListener('error',()=>{img.hidden=true;img.parentElement.insertAdjacentHTML('afterbegin',`<span class="thumb-fallback">${t('Aperçu indisponible','Preview unavailable','Vista previa no disponible')}</span>`);},{once:true}));
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
    try{
      const [data,visuals]=await Promise.all([
        window.getCatalogJson('/aide/api/discovery'),
        fetch(new URL('./visual-assets.json?v=visual-v17b',import.meta.url)).then(response=>response.ok?response.json():null).catch(()=>null)
      ]);
      catalog=data;visualAssets=Array.isArray(visuals?.assets)?visuals.assets:[];
      ctx.picks?.setVideos(catalog.shelves||[]);render();ctx.onPicksChange?.();
    }catch{
      $('#discovery-hub').innerHTML=`<p class="small-note">${t('L’exploration par objectif est momentanément indisponible. La recherche reste accessible.','Goal browsing is temporarily unavailable. Search is still available.','La exploración por objetivos no está disponible. Puedes usar la búsqueda.')}</p>`;
    }
  }
  function closeSuggestions() {
    ++searchVersion;clearTimeout(timer);suggestions=[];active=-1;
    $('#search-suggestions').hidden=true;$('#search').setAttribute('aria-expanded','false');$('#search').removeAttribute('aria-activedescendant');
    $('#suggestion-status').textContent='';
    $('#search-helper').hidden=true;
  }
  function suggestionDetail(item) {
    if (typeof item.count === 'number') return `${count(item.count)} ${t('ressources','resources','recursos')}`;
    if (item.type === 'guide') return t('Guide RaceLink · Sources citées','RaceLink guide · Sources included','Guía RaceLink · Fuentes citadas');
    if (item.type === 'history') return t('Reprendre cette recherche','Resume this search','Retomar esta búsqueda');
    return '';
  }
  function renderSuggestions() {
    const root=$('#search-suggestions');
    root.innerHTML=suggestions.map((item,i)=>`<button type="button" role="option" tabindex="-1" id="suggestion-${i}" data-suggestion="${i}" aria-selected="${active===i}"><span class="suggestion-kind">${item.type==='history'?t('RÉCENT','RECENT','RECIENTE'):item.type==='video'?t('VIDÉO','VIDEO','VÍDEO'):item.type==='guide'?t('GUIDE','GUIDE','GUÍA'):t('SUJET','TOPIC','TEMA')}</span><span><strong dir="auto">${e((item.match_basis==='editorial_default'?'':item.completion)||text(item.label))}</strong>${item.completion&&item.match_basis!=='editorial_default'?`<small>${e(text(item.label))}</small>`:''}${item.correction?`<small class="suggestion-correction">${e(item.corrections?.length ? t('Proposition : ','Suggestion: ','Propuesta: ')+item.corrections.map(c=>`${c.from} → ${c.to}`).join(' · ') : text(item.correction))}</small>`:''}${suggestionDetail(item)?`<small>${e(suggestionDetail(item))}</small>`:''}</span><b aria-hidden="true">↗</b></button>`).join('');
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
    else if(item.type==='guide'){closeSuggestions();document.dispatchEvent(new Event('rl:search-chosen'));ctx.openGuide(item.guide_id||item.id);}
    else chooseTopic(item.id,item);
  }
  async function recommendations(results) {
    latestResults=results;
    const version=++recommendVersion,root=$('#context-discovery');
    root.hidden=true;
    const state=ctx.getState();
    const hasContext=Object.entries(stateContext()).some(([,v])=>hasValue(v));
    if(!hasContext)return;
    try {
      const response=await window.getCatalogJson(`/aide/api/recommendations?${request(stateContext())}`);
      if(version!==recommendVersion)return;
      const topics=(response.topics||[]).filter(topic=>!state.q||!results.total||topic.match_basis!=='context_filters').slice(0,4);
      contextTopics=topics;
      const precise=personalKeys.filter(k=>hasValue(state[k]));
      if(!topics.length&&results.total>0)return;
      root.innerHTML=`<div class="context-heading"><div><p class="eyebrow">${results.total?t('POUR CONTINUER','KEEP EXPLORING','PARA CONTINUAR'):t('RETROUVER UNE PISTE UTILE','FIND A USEFUL NEXT STEP','ENCONTRAR UN SIGUIENTE PASO')}</p><h3>${results.total?t('Des sujets qui prolongent votre recherche','Topics related to your search','Temas relacionados con tu búsqueda'):t('Pas de réponse précise pour le moment.','No precise match yet.','Aún no hay una coincidencia precisa.')}</h3></div></div>
        <p>${e(text(response.reason)||t('Suggestions liées aux mots de votre recherche et aux sujets du catalogue.','Suggestions based on your search words and catalog topics.','Sugerencias basadas en tu búsqueda y los temas del catálogo.'))}</p>
        ${topics.length?`<div class="related-grid">${topics.map(x=>topicButton(x,true)).join('')}</div>`:''}
        ${!results.total?`<div class="recovery-actions">${state.q?`<button type="button" data-discovery-clear-query>${t('Retirer les mots recherchés','Clear search words','Quitar palabras de búsqueda')}</button>`:''}${precise.some(k=>['make','model','generation','year','engine','fuel_type','body_type'].includes(k))?`<button type="button" data-discovery-clear-vehicle>${t('Explorer sans véhicule','Explore without a vehicle','Explorar sin vehículo')}</button>`:''}<button type="button" data-home>${t('Revenir aux objectifs','Back to goals','Volver a los objetivos')} ↗</button></div><small>${t('Ces actions élargissent la recherche uniquement si vous les choisissez. Elles ne confirment aucune compatibilité mécanique.','These actions broaden your search only when you choose them. They do not confirm mechanical compatibility.','Estas acciones amplían la búsqueda solo cuando las eliges. No confirman compatibilidad mecánica.')}</small>`:''}`;
      root.hidden=false;
    } catch {if(version===recommendVersion)root.hidden=true;}
  }
  document.addEventListener('click',event=>{
    const entry=event.target.closest('[data-entry-category]');if(entry){closeSuggestions();ctx.applySearch({...ctx.getState(),category:entry.dataset.entryCategory,page:1});return;}
    if(event.target.closest('[data-browse-all]')){closeSuggestions();ctx.applySearch({});return;}
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
