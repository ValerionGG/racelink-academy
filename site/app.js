import {createCinemaHome} from './cinema-home.js?v=collection-v24';
import {icon as glyph, categoryIcon} from './icons.js';
import {createIdentityUI} from './identity-ui.js?v=themes-v22';
import {tracks} from './tracks.js';
import {createAutomotiveUI,automotiveDefaults,vehicleKeys} from './automotive-ui.js?v=themes-v22';
import {createDiscoveryUI} from './discovery-ui.js?v=collection-v24';
import {createRaceLinkPicks} from './racelink-picks.js';
import {createMobileUI} from './mobile-ui.js?v=themes-v22&rev=2';
import {createGuideUI} from './guide-ui.js?v=themes-v22';
import {socialContentMarkup} from './social-content.js';
import {renderResourceDetail,renderResourceOverview} from './resource-detail.js?v=themes-v22';
import {resourceCard} from './resource-card.js?v=themes-v22';
const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => [...root.querySelectorAll(s)];
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const normalize = s => String(s || '').normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase();
const storage = {get(key, fallback) {try {return JSON.parse(localStorage.getItem(key)) ?? fallback;} catch {return fallback;}}, set(key, value) {try {localStorage.setItem(key, JSON.stringify(value));return true;} catch {return false;}}};
let ui = storage.get('rl-library-language','fr');
if (!['fr','en','es'].includes(ui)) ui = 'fr';
const dictionaries = {
  en: {brandSub:'KNOWLEDGE MAKES THE DIFFERENCE.',explore:'Explore',paths:'Learning paths',help:'Help & FAQ',saved:'My collection',academy:'Masterclasses ↗',openLibrary:'THE OPEN MOTORSPORT LIBRARY',headline:'ONE QUESTION.<br>ONE INSIGHT.<br><span>ONE LAP AHEAD.</span>',intro:'From your first braking point to professional precision.<br>Paddock knowledge, brought together for you.',try:'Explore',startHere:'START HERE',pathLabel:'LEARNING PATH · DRIVING',featureTitle:'YOUR NEXT CORNER<br>STARTS HERE.',featureCta:'Explore the fundamentals',references:'videos indexed',accessNote:'Public sources · Credited creators · Direct access',method:'Our approach ↗',findAnswer:'THE RIGHT KNOWLEDGE, AT THE RIGHT TIME',catalogTitle:'Find your own racing line.',filters:'Filters',refine:'Refine your search',reset:'Clear',discipline:'DISCIPLINE',level:'LEVEL',language:'VIDEO LANGUAGE',platform:'PLATFORM',duration:'AVAILABLE TIME',withTranscript:'With transcript',freeLicense:'Confirmed open license',filterNote:'Every step forward starts with a good question.',catalogDisclosure:'Listings are based on public metadata. Teaching quality, language and level still need confirmation for videos marked “To review”.',notAlone:'LOOKING FOR A STARTING POINT?',helpTitle:'Learning starts<br>with asking questions.',faqQuick1:'How do I read a transcript?',faqQuick2:'What if the video is in another language?',faqQuick3:'Explore all help topics',footer:'Share the passion. Share the knowledge.'},
  es: {brandSub:'EL SABER MARCA LA DIFERENCIA.',explore:'Explorar',paths:'Itinerarios',help:'Ayuda y FAQ',saved:'Mi selección',academy:'Clases magistrales ↗',openLibrary:'LA BIBLIOTECA ABIERTA DEL AUTOMOVILISMO',headline:'UNA PREGUNTA.<br>UNA NUEVA IDEA.<br><span>UNA VUELTA POR DELANTE.</span>',intro:'De la primera frenada a la precisión profesional.<br>El conocimiento del paddock, reunido para ti.',try:'Explora',startHere:'EMPIEZA AQUÍ',pathLabel:'ITINERARIO · PILOTAJE',featureTitle:'TU PRÓXIMA CURVA<br>EMPIEZA AQUÍ.',featureCta:'Explora los fundamentos',references:'vídeos referenciados',accessNote:'Fuentes públicas · Autores acreditados · Acceso directo',method:'Nuestro método ↗',findAnswer:'EL CONOCIMIENTO QUE NECESITAS',catalogTitle:'Encuentra tu propia trazada.',filters:'Filtros',refine:'Afinar la búsqueda',reset:'Borrar',discipline:'DISCIPLINA',level:'NIVEL',language:'IDIOMA DEL VÍDEO',platform:'PLATAFORMA',duration:'TIEMPO DISPONIBLE',withTranscript:'Con transcripción',freeLicense:'Licencia libre confirmada',filterNote:'Cada avance empieza con una buena pregunta.',catalogDisclosure:'Las referencias se basan en metadatos públicos. La calidad didáctica, el idioma y el nivel requieren confirmación en los vídeos marcados «Por revisar».',notAlone:'¿BUSCAS UN PUNTO DE PARTIDA?',helpTitle:'Aprender empieza<br>haciendo preguntas.',faqQuick1:'¿Cómo leer una transcripción?',faqQuick2:'¿Y si el vídeo está en otro idioma?',faqQuick3:'Ver toda la ayuda',footer:'La pasión se comparte. El conocimiento también.'}
};
Object.assign(dictionaries.en,{explore:'Home',openLibrary:'YOUR NEXT STEP STARTS HERE',headline:'A question?<br><span>Find out how.</span>',intro:'Maintain your car, improve on track or in a simulator. <br>Videos and guides to put knowledge into practice.',catalogTitle:'Find your answer.',discipline:'TOPIC',language:'LANGUAGE'});
Object.assign(dictionaries.es,{explore:'Inicio',openLibrary:'TU PRÓXIMO PASO EMPIEZA AQUÍ',headline:'¿Una pregunta?<br><span>Descubre cómo.</span>',intro:'Cuida tu coche, mejora en pista o en simulación. <br>Vídeos y guías para pasar a la práctica.',catalogTitle:'Encuentra tu respuesta.',discipline:'TEMA',language:'IDIOMA'});
Object.assign(dictionaries.en,{brandSub:'Your automotive library',saved:'Saved',headline:'The passion.<br><span>The know-how.</span>',intro:'Maintain, drive, improve. Videos and guides to turn curiosity into skills.',catalogTitle:'Find the right tutorial',discipline:'Topic',level:'Level',platform:'Platform',duration:'Duration'});
Object.assign(dictionaries.es,{brandSub:'Tu biblioteca del automóvil',saved:'Guardados',headline:'La pasión.<br><span>El saber hacer.</span>',intro:'Cuidar, pilotar, progresar. Vídeos y guías para aprender a hacerlo bien.',catalogTitle:'Encuentra el tutorial adecuado',discipline:'Tema',level:'Nivel',platform:'Plataforma',duration:'Duración'});
Object.assign(dictionaries.en,{headline:'CARS.<br><span>LEARN BY DOING.</span>',intro:'From your first service to your next corner. <br>Videos and guides to put knowledge into practice.',catalogTitle:'Find your next discovery.'});
Object.assign(dictionaries.es,{headline:'EL AUTOMÓVIL.<br><span>SE APRENDE.</span>',intro:'Del primer mantenimiento a la próxima curva. <br>Vídeos y guías para pasar a la práctica.',catalogTitle:'Tu próximo descubrimiento.'});
const originalText = Object.fromEntries($$('[data-i18n]').map(el => [el.dataset.i18n,el.innerHTML]));
const t = (fr,en,es) => ui === 'en' ? en : ui === 'es' ? es : fr;
const categories = [
  ['driving','◉','Pilotage','Driving','Pilotaje','Vision, trajectoire et freinage. Les bases qui changent chaque tour.'],
  ['engineering','⌁','Ingénierie','Engineering','Ingeniería','Lire la data, comprendre les pneus et prendre de meilleures décisions.'],
  ['mechanics','⚒','Mécanique','Mechanics','Mecánica','Comprendre la voiture, ses réglages et ses composants.'],
  ['simracing','⊕','Sim racing','Sim racing','Sim racing','Du premier setup à une pratique plus précise sur simulateur.'],
  ['media','▣','Média','Media','Medios','Raconter la course, de la prise de vue au montage.'],
  ['business','↗','Business','Business','Negocio','Sponsoring, partenariats et économie du sport automobile.'],
  ['career','◇','Carrière','Careers','Carrera','Découvrir les métiers et les compétences du paddock.'],
  ['fitness','⌇','Physique','Fitness','Preparación física','Préparation et compréhension des exigences du pilote.']
];
const catName = value => {const c = categories.find(c => c[0] === value);return c ? t(c[2],c[3],c[4]) : value;};
const levelName = value => ({beginner:t('Débutant','Beginner','Principiante'),intermediate:t('Intermédiaire','Intermediate','Intermedio'),advanced:t('Avancé / Pro','Advanced / Pro','Avanzado / Pro'),all:t('Tous niveaux','All levels','Todos los niveles'),unknown:t('À qualifier','To review','Por revisar')})[value] || value;
const platformName = value => ({youtube:'YouTube',dailymotion:'Dailymotion',vimeo:'Vimeo',tiktok:'TikTok',instagram:'Instagram',facebook:'Facebook',twitch:'Twitch',bilibili:'Bilibili',racelink:'RaceLink',other:ui==='en'?'Other sources':ui==='es'?'Otras fuentes':'Autres sources'})[value] || value;
const licenseName = value => value==='creative-commons'?'Creative Commons · CC BY':value==='public-domain'?t('Domaine public','Public domain','Dominio público'):value==='permission'?t('Autorisation de l’auteur','Creator permission','Permiso del autor'):t('Non confirmée','Unconfirmed','Sin confirmar');
function readingSegments(raw){
  const groups=[];
  for(const cue of raw){
    const text=String(cue.text||'').trim();if(!text)continue;
    const previous=groups.at(-1);
    if(previous&&Number(cue.start)-previous.start<25&&previous.text.length<650){
      if(previous.lastText!==text)previous.text+=` ${text}`;
      previous.lastText=text;
    }else groups.push({start:Number(cue.start)||0,text,lastText:text});
  }
  return groups;
}
const langName = value => {if (!value || value === 'und') return t('Non confirmée','Unconfirmed','Sin confirmar');try{return new Intl.DisplayNames([ui],{type:'language'}).of(value);}catch{return value;}};
const languageLabel = value => {const label=langName(value);return label.charAt(0).toLocaleUpperCase(ui)+label.slice(1);};
const estimatedLanguage = video => video.language_confidence==='estimated'||/estimate|inferred/.test(String(video.language_status||''));
const fmtDuration = seconds => {if (!seconds) return t('Durée inconnue','Duration unknown','Duración desconocida');const n=Math.round(seconds);return n>=3600 ? `${Math.floor(n/3600)}:${String(Math.floor(n%3600/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}` : `${Math.floor(n/60)}:${String(n%60).padStart(2,'0')}`;};
const safeUrl = (value, image = false) => {try{const u = new URL(value);return u.protocol === 'https:' || (!image && u.protocol === 'http:' && ['localhost','127.0.0.1'].includes(u.hostname)) ? u.href : '';}catch{return '';}};
const readSaved = () => storage.get('rl-library-saved',{});let saved = readSaved();
let state = {...automotiveDefaults,q:'',category:'',domain:'',level:'',language:'',platform:'',format:'all',content_format:'',duration:'',transcript:'',license:'',sort:'relevance',page:1};
let browsing=false;
let view='explore',stats=null,loadedItems=[],detail=null,requestVersion=0,detailVersion=0,toastTimer=null,lastTotal=null,activeTrack='';
let faqItems = [];
const seedFaq = [
  {id:'method',question:'Comment les vidéos sont-elles sélectionnées ?',answer:'Le catalogue rassemble des références trouvées dans les métadonnées publiques des plateformes. « À qualifier » signifie que le contenu a été repéré mais que sa pertinence pédagogique reste à vérifier. Une sélection éditoriale repose sur le titre, la source et le descriptif ; elle ne constitue pas une certification du contenu.'},
  {id:'transcripts',question:'Comment lire une transcription ?',answer:'Ouvrez une fiche puis l’onglet « Transcription ». Un texte n’est affiché que s’il a effectivement été obtenu avec une permission de réutilisation enregistrée. Les sous-titres disponibles chez l’auteur sont signalés séparément. Si le texte est absent, le lien vers la source permet de vérifier les sous-titres du lecteur d’origine.'},
  {id:'language',question:'Comment trouver des vidéos en français ou dans une autre langue ?',answer:'Sous la recherche, choisissez une langue ou ouvrez « Vidéos en français ». Ce choix reste visible dans les résultats et se conserve lorsque vous explorez un sujet. « Site FR » change seulement la langue de l’interface. La langue des vidéos provient des métadonnées de la plateforme, des pistes de sous-titres ou d’une estimation signalée à partir du titre, de la description et de la source. Une simple requête en français ne prouve pas la langue parlée. Les traductions et sous-titres supplémentaires dépendent du lecteur d’origine.'},
  {id:'public',question:'Public, gratuit et libre : quelle différence ?',answer:'Une vidéo accessible publiquement peut rester protégée par le droit d’auteur. Le catalogue renvoie vers sa source et ne prétend pas qu’elle est libre de réutilisation. Le filtre « Licence libre confirmée » nécessite une licence explicite enregistrée. Des restrictions régionales, une connexion ou une suppression peuvent changer l’accès.'},
  {id:'saved',question:'Où sont enregistrés mes favoris et mes notes ?',answer:'Votre sélection et vos notes restent dans ce navigateur, sur cet appareil. Aucun compte n’est nécessaire pour les utiliser. Si vous effacez les données du navigateur, elles seront perdues. Elles ne sont pas synchronisées avec votre compte Focus.'},
  {id:'focus',question:'Comment retrouver mes masterclass Focus ?',answer:'Le lien « Les masterclass » ouvre Focus et ses cours, mentors, groupes et agenda. La bibliothèque est un complément de ressources publiques. Les abonnements et achats restent gérés dans Focus.'}
];

const raceLinkPicks=createRaceLinkPicks({escape,t,getUi:()=>ui});
const guideUI=createGuideUI({escape,t,picks:raceLinkPicks,safeUrl});
const openGuide=(id,section)=>{++detailVersion;detail=null;guideUI.open(id,section);};
const automotiveUI=createAutomotiveUI({
  escape,t,storage,picks:raceLinkPicks,getState:()=>state,getUi:()=>ui,change:setFilter,toast:showToast,
  patch(patch){browsing=true;state={...state,...patch,page:1};syncControls();syncUrl();automotiveUI.loadOptions();loadVideos();}
});
const discoveryUI=createDiscoveryUI({
  escape,t,storage,picks:raceLinkPicks,getState:()=>state,getUi:()=>ui,langName,openVideo,openGuide,
  onPicksChange(){
    cinemaHome.render();
    const grid=$('#video-grid');
    if(loadedItems.length&&grid.getAttribute('aria-busy')!=='true'){grid.innerHTML=loadedItems.map(cardMarkup).join('');setImageFallback(grid);}
    if(view==='saved')renderSaved();
    if(detail&&$('#video-dialog').open)renderDetailPick();
  },
  clearFilter:key=>setFilter(key,''),
  clearVehicle(){vehicleKeys.forEach(key=>state[key]='');syncControls();syncUrl();automotiveUI.loadOptions();loadVideos();},
  applySearch(patch){
    document.dispatchEvent(new Event('rl:search-chosen'));
    browsing=true;state={...automotiveDefaults,q:'',category:'',domain:'',level:'',language:state.language,platform:'',format:'all',content_format:'',duration:'',transcript:'',license:'',sort:'relevance',page:1,...patch};
    changeView('explore',false);syncControls();syncUrl(true);automotiveUI.loadOptions();loadVideos();
    $('#catalog-heading').scrollIntoView({behavior:'smooth'});
  }
});
const cinemaHome=createCinemaHome({root:$('#cinema-home'),escape,t,getUi:()=>ui,getState:()=>state,langName,picks:raceLinkPicks,getJson:url=>window.getCatalogJson(url)});
function translateCinema(){
  const labels={heroLabel:t('LE SAVOIR SE TRANSMET.','KNOWLEDGE IS MEANT TO BE SHARED.','EL SABER SE COMPARTE.'),explore:t('Explorer les tutos','Explore tutorials','Explorar tutoriales'),vehicle:t('Pour ma voiture','For my car','Para mi coche'),featured:t('LE GUIDE À DÉCOUVRIR','A GUIDE TO EXPLORE','UNA GUÍA POR DESCUBRIR'),featuredTitle:t('Avant votre première vidange.','Before your first oil change.','Antes de tu primer cambio de aceite.'),featuredAction:t('Préparer l’intervention →','Prepare the task →','Preparar la intervención →'),heroCaption:t('MÉCANIQUE · PILOTAGE · SIM RACING','MECHANICS · DRIVING · SIM RACING','MECÁNICA · PILOTAJE · SIM RACING'),finderEyebrow:t('VOTRE PROCHAINE DÉCOUVERTE','YOUR NEXT DISCOVERY','TU PRÓXIMO DESCUBRIMIENTO'),finderTitle:t('Qu’avez-vous envie d’apprendre ?','What would you like to learn?','¿Qué te gustaría aprender?')};
  $$('[data-cinema-copy]').forEach(el=>{el.textContent=labels[el.dataset.cinemaCopy]||'';});
  cinemaHome.render();
}
const mobileUI=createMobileUI({t,getState:()=>state,getTotal:()=>lastTotal,isLoading:()=>$('#video-grid').getAttribute('aria-busy')==='true',onExplore:()=>{if(view!=='explore')changeView('explore');}});

function showToast(message){$('#toast').textContent=message;$('#toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),3000);}
const identityUI=createIdentityUI({t,openSearch:()=>mobileUI.openSearch(),getView:()=>view,isBrowsing:()=>browsing,getState:()=>state});
function updateSavedCount(){$('#saved-count').textContent=Object.keys(saved).length;}
function syncUrl(push=false){
  const u=new URL(location.href);u.search='';if(!browsing)u.hash='';
  if(browsing)u.searchParams.set('browse','1');else if(state.language)u.searchParams.set('browse','0');
  if(view!=='explore')u.searchParams.set('view',view);
  if(view==='paths'&&activeTrack)u.searchParams.set('track',activeTrack);
  for(const [key,value] of Object.entries(state))if(value&&!(key==='page'&&value===1)&&!(key==='sort'&&value==='relevance')&&!(key==='format'&&value==='all'))u.searchParams.set(key,value);
  if(ui!=='fr')u.searchParams.set('ui',ui);
  history[push?'pushState':'replaceState']({},'',u);
}
function restoreUrl(){
  const p=new URLSearchParams(location.search);
  for(const key of Object.keys(state))state[key]=p.get(key)||(key==='page'?1:key==='sort'?'relevance':key==='format'?'all':'');
  browsing=p.has('browse')?p.get('browse')!=='0':Object.entries(state).some(([k,v])=>v&&!['page','sort'].includes(k)&&!(k==='format'&&v==='all'));
  state.page=Math.max(1,Number(state.page)||1);
  if(['fr','en','es'].includes(p.get('ui')))ui=p.get('ui');
  view=['paths','faq','saved'].includes(p.get('view'))?p.get('view'):'explore';
  activeTrack=tracks[p.get('track')]?p.get('track'):'';
}
function syncControls(){
  document.body.classList.toggle('results-mode',browsing);
  $('#explore-view .catalog').hidden=!browsing;
  $$('#format-tabs button').forEach(b=>b.setAttribute('aria-pressed',String((state.format||'all')===b.dataset.format)));
  $('.results-back').textContent=t('← Accueil','← Home','← Inicio');
  $('.advanced-filters>summary').textContent=t('Disponibilité du texte et droits','Text availability and rights','Disponibilidad de texto y derechos');
  $('#search').value=state.q;
  for(const key of ['level','language','platform','duration','sort','domain','content_format'])$(`#${key}`).value=state[key]||'';
  $('#home-language').value=state.language||'';
  $$('[data-content-language]').forEach(button=>button.setAttribute('aria-pressed',String(state.language===button.dataset.contentLanguage)));
  $('#transcript').checked=Boolean(state.transcript);$('#license').checked=Boolean(state.license);automotiveUI.sync();
  const selectedVehicle=vehicleKeys.map(key=>state[key]).filter(Boolean);
  $('#vehicle-disclosure-value').textContent=selectedVehicle.length?selectedVehicle.join(' · '):t('Marque, moteur, huile, intervention…','Make, engine, oil, task…','Marca, motor, aceite, tarea…');
  if(location.hash==='#vehicle-hub')$('#vehicle-disclosure').open=true;
  updateLibrary();mobileUI.update();
}
function updateLibrary(){
  $('#vehicle-trigger-label').textContent=[state.make,state.model].filter(Boolean).join(' ')||t('Ma voiture','My car','Mi coche');
  $('.library-vehicle').classList.toggle('has-vehicle',Boolean(state.make));
  $('.vehicle-apply').textContent=t('Voir les résultats →','Show results →','Ver resultados →');
  $('#result-explanation-label').textContent=t('Comprendre ces résultats','Understand these results','Entender estos resultados');
  $('#library-context-caption').textContent=state.category?catName(state.category):t('À regarder, à lire, à comprendre.','Watch, read, understand.','Ver, leer, comprender.');
  const labels={topic:t('Quel sujet ?','Which topic?','¿Qué tema?'),source:t('Où regarder ?','Where to watch?','¿Dónde verlo?'),sourceHint:t('Choisissez la plateforme qui publie la vidéo.','Choose the platform publishing the video.','Elige la plataforma que publica el vídeo.'),preferences:t('Quel contenu vous convient ?','What works for you?','¿Qué contenido prefieres?')};
  $$('[data-filter-copy]').forEach(el=>el.textContent=labels[el.dataset.filterCopy]);
  $('#reset-filters').textContent=t('Effacer les critères','Clear filters','Borrar filtros');
  $('.filter-heading strong').textContent=t('Vos critères','Your preferences','Tus criterios');
}
function applyTranslations(){
  document.documentElement.lang=ui;$('#ui-language').value=ui;
  $('#ui-language').setAttribute('aria-label',t('Langue de l’interface','Website language','Idioma del sitio'));
  $('#interface-language-label').textContent=t('Site','Site','Sitio');
  $('label[for="home-language"]').textContent=t('Langue des vidéos','Video language','Idioma de los vídeos');
  $('label[for="language"]').textContent=t('Langue','Language','Idioma');
  $('.language-shortcuts').setAttribute('aria-label',t('Choix rapide de langue','Quick language choice','Selección rápida de idioma'));
  $('.language-shortcuts [data-content-language="fr"]').textContent=t('Français','French','Francés');
  $('.language-shortcuts [data-content-language=""]').textContent=t('Toutes','All','Todos');
  $('#content-language-note').textContent=t('La langue peut être estimée à partir du titre et de la source.','Language may be estimated from the title and source.','El idioma puede estimarse a partir del título y la fuente.');
  $$('[data-i18n]').forEach(el=>{el.innerHTML=ui==='fr'?originalText[el.dataset.i18n]:dictionaries[ui]?.[el.dataset.i18n]||originalText[el.dataset.i18n];});
  $('#search').placeholder=t('Un sujet, un modèle…','A topic, a car model…','Un tema, un modelo…');
  $('#search').setAttribute('aria-label',t('Rechercher des tutoriels','Search tutorials','Buscar tutoriales'));
  $('#search-form button').setAttribute('aria-label',t('Lancer la recherche','Search','Buscar'));
  $('.results-toolbar label .sr-only').textContent=t('Trier les résultats','Sort results','Ordenar resultados');
  $('label[for="domain"]').textContent=t('CONTEXTE','CONTEXT','CONTEXTO');
  $('label[for="content_format"]').textContent=t('TYPE DE VIDÉO','VIDEO TYPE','TIPO DE VÍDEO');
  $('.filter-explainer').textContent=t('Tutoriel, démonstration, cours ou direct. Classement selon les informations disponibles.','Tutorial, demonstration, course or stream. Classification uses available information.','Tutorial, demostración, curso o directo. Clasificación según la información disponible.');
  $('#format-tabs').setAttribute('aria-label',t('Format de la ressource','Resource format','Formato del recurso'));
  $('.hero h1').tabIndex=-1;
  $('.suggestions [data-query="vidange"]').textContent=t('Faire une vidange','Change engine oil','Cambiar el aceite');
  $('.suggestions [data-query="freinage"]').textContent=t('Mieux freiner','Improve braking','Mejorar la frenada');
  $('.suggestions [data-query="sim racing"]').textContent=t('Régler mon simulateur','Set up my simulator','Ajustar mi simulador');
  $('#domain').innerHTML=[['',t('Tous les contextes','All contexts','Todos los contextos')],['motorsport',t('Motorsport & fondamentaux','Motorsport & fundamentals','Automovilismo y fundamentos')],['automotive_adjacent',t('Auto & compétences complémentaires','Automotive & related skills','Automóvil y competencias complementarias')]].map(([v,l])=>`<option value="${v}">${l}</option>`).join('');
  $('#level').innerHTML=`<option value="">${t('Tous les niveaux','All levels','Todos los niveles')}</option>${['beginner','intermediate','advanced'].map(x=>`<option value="${x}">${levelName(x)}</option>`).join('')}`;
  $('#duration').innerHTML=[['',t('Toutes les durées','Any duration','Cualquier duración')],['short',t('Moins de 10 min','Under 10 min','Menos de 10 min')],['medium','10–30 min'],['long',t('Plus de 30 min','Over 30 min','Más de 30 min')]].map(([v,l])=>`<option value="${v}">${l}</option>`).join('');
  $('#sort').innerHTML=[['relevance',t('Pertinence','Relevance','Relevancia')],['newest',t('Les plus récentes','Newest first','Más recientes')],['duration',t('Les plus courtes','Shortest first','Más cortos')],['title',t('Titre A → Z','Title A → Z','Título A → Z')]].map(([v,l])=>`<option value="${v}">${l}</option>`).join('');
  automotiveUI.render();
  discoveryUI.refresh();
  $('#vehicle-disclosure-label').textContent=t('Affiner pour votre voiture','Refine for your car','Afinar para tu coche');
  $('.workshop-jump').textContent=t('Mon véhicule & entretien ↘','My vehicle & maintenance ↘','Mi vehículo y mantenimiento ↘');
  renderFacets();syncControls();renderPaths();renderFaq();renderSaved();renderStats();identityUI.update();translateCinema();
}
function renderStats(){
  if(!stats)return;
  $('#catalog-total').textContent=Number(stats.total_videos||0).toLocaleString(ui);
  const count=typeof stats.languages==='number'?stats.languages:Array.isArray(stats.languages)?stats.languages.length:Object.keys(stats.languages||{}).length;
  const domains=stats.facets?.domain||[];
  const core=domains.find(d=>d.value==='motorsport')?.count,auto=domains.find(d=>d.value==='automotive_adjacent')?.count;
  if(core!==undefined&&auto!==undefined)$('#scope-totals').textContent=`${Number(core).toLocaleString(ui)} motorsport · ${Number(auto).toLocaleString(ui)} ${t('mécanique auto','automotive mechanics','mecánica auto')}`;
  $('#language-total').textContent=`${count} ${t('langues repérées','languages identified','idiomas identificados')}`;
  renderLanguages();
}
let facets={};
function renderLanguages(){
  // Keep the global choices even when the current query has no matching language.
  const values=[...new Set(['fr','en',...(stats?.facets?.language||[]).map(f=>f.value),...(facets.language||[]).map(f=>f.value),state.language].filter(Boolean))];
  values.sort((a,b)=>a==='fr'?-1:b==='fr'?1:a==='und'?1:b==='und'?-1:languageLabel(a).localeCompare(languageLabel(b),ui));
  const options=`<option value="">${t('Toutes les langues','All languages','Todos los idiomas')}</option>${values.map(value=>`<option value="${escape(value)}">${escape(languageLabel(value))}</option>`).join('')}`;
  for(const id of ['language','home-language']){const select=$(`#${id}`);select.innerHTML=options;select.value=state.language||'';}
  const frenchCount=(stats?.facets?.language||[]).find(f=>f.value==='fr')?.count;
  $('#french-videos').innerHTML=`${t('Vidéos en français','Videos in French','Vídeos en francés')}${frenchCount===undefined?'':` <small>${Number(frenchCount).toLocaleString(ui)}</small>`} <span aria-hidden="true">→</span>`;
}
function renderFacets(){
  const previousFocus=document.activeElement;
  const focusChoice=previousFocus?.hasAttribute('data-platform-choice')?['platformChoice',previousFocus.dataset.platformChoice]:previousFocus?.hasAttribute('data-category')?['category',previousFocus.dataset.category]:null;
  identityUI.sync();
  automotiveUI.setResultFacets(facets);
  const categoriesFacet=facets.category||[];
  $('#category-filters').innerHTML=[['','⌘',t('Tout explorer','Explore everything','Explorar todo')],...categories.map(c=>[c[0],c[1],catName(c[0])])].map(([id,icon,name])=>{
    const count=id?(categoriesFacet.find(f=>f.value===id)?.count??0):(lastTotal??stats?.total_videos);
    return `<button class="category-button ${state.category===id?'active':''}" data-category="${id}" aria-pressed="${state.category===id}"><span class="cat-icon" aria-hidden="true">${glyph(categoryIcon[id]||'library',{size:20})}</span>${escape(name)}<span class="cat-count">${count??'—'}</span></button>`;
  }).join('');
  renderLanguages();
  const platforms=['youtube','dailymotion','vimeo','tiktok','instagram','facebook','twitch','bilibili','racelink','other'].filter(v=>v===state.platform||(facets.platform||[]).some(f=>f.value===v&&f.count>0));
  $('#platform').innerHTML=`<option value="">${t('Toutes les plateformes','All platforms','Todas las plataformas')}</option>${platforms.map(value=>`<option value="${value}">${platformName(value)} (${(facets.platform||[]).find(f=>f.value===value)?.count||0})</option>`).join('')}`;
  $('#platform').value=state.platform;
  $('#platform-choices').innerHTML=[['',t('Toutes','All','Todas')],...platforms.map(value=>[value,platformName(value)])].map(([value,label])=>`<button type="button" data-platform-choice="${escape(value)}" aria-pressed="${state.platform===value}">${escape(label)}${value?`<span>${Number((facets.platform||[]).find(f=>f.value===value)?.count||0).toLocaleString(ui)}</span>`:''}</button>`).join('');
  const types={tutorial:t('Tutoriel','Tutorial','Tutorial'),demonstration:t('Démonstration','Demonstration','Demostración'),course:t('Cours','Course','Curso'),stream:t('Direct / replay','Stream / replay','Directo / repetición'),unspecified:t('Type à confirmer','Unconfirmed type','Tipo sin confirmar')};
  $('#content_format').innerHTML=`<option value="">${t('Tous les types','All types','Todos los tipos')}</option>${Object.entries(types).map(([v,l])=>`<option value="${v}">${l} (${(facets.content_format||[]).find(f=>f.value===v)?.count||0})</option>`).join('')}`;
  $('#content_format').value=state.content_format;
  if(focusChoice&&$('#filters-dialog')?.open){const selector=focusChoice[0]==='platformChoice'?'[data-platform-choice]':'[data-category]';$$(selector).find(button=>button.dataset[focusChoice[0]]===focusChoice[1])?.focus({preventScroll:true});}
  $$('#format-tabs button').forEach(button=>{const v=button.dataset.format,label=v==='all'?t('Tout','All','Todo'):v==='video'?t('Vidéos','Videos','Vídeos'):t('Guides','Guides','Guías');const n=v==='all'?(facets.format||[]).reduce((sum,x)=>sum+x.count,0):(facets.format||[]).find(f=>f.value===v)?.count;button.innerHTML=`${glyph(v==='video'?'play':v==='guide'?'library':'filter',{size:18})}${label}${n===undefined?'':` <span>${Number(n).toLocaleString(ui)}</span>`}`;});
}
function cardMarkup(video){
  if(video.resource_type==='guide')return guideUI.card(video);
  return resourceCard(video,{escape,t,glyph,safeUrl,catName,platformName,languageLabel,estimatedLanguage,fmtDuration,isSaved:Boolean(saved[video.id]),badge:raceLinkPicks.badge('video',video.id,{compact:true}),automotiveMarkup:automotiveUI.cardMarkup(video)});
}
function setImageFallback(root){
  $$('img',root).forEach(img=>img.addEventListener('error',()=>{img.style.display='none';const parent=img.parentElement;if(parent.classList.contains('thumbnail'))parent.insertAdjacentHTML('afterbegin','<span class="thumb-fallback">RACELINK</span>');},{once:true}));
}
function renderDetailPick(){
  const slot=$('#detail-racelink-pick');
  if(slot&&detail){slot.innerHTML=raceLinkPicks.badge('video',detail.id)+raceLinkPicks.note('video',detail.id);slot.hidden=!raceLinkPicks.has('video',detail.id);}
}
async function loadVideos(){
  const version=++requestVersion;
  discoveryUI.beginSearch();
  const params=new URLSearchParams({...state,per_page:18});
  const grid=$('#video-grid');grid.setAttribute('aria-busy','true');grid.inert=true;
  lastTotal=null;
  mobileUI.update();
  $('#results-status').textContent=t('Recherche en cours…','Searching…','Buscando…');
  if(!loadedItems.length)grid.innerHTML=Array.from({length:6},()=>'<div class="skeleton" aria-hidden="true"></div>').join('');
  try{
    const data=await window.getCatalogJson(`/aide/api/resources?${params}`);if(version!==requestVersion)return;
    loadedItems=data.items||[];
    if(data.facets)facets=data.facets;
    const n=Number(data.total)||0;
    lastTotal=n;renderFacets();renderActiveFilters();automotiveUI.renderContext(data.inferred_task||state.task);
    $('#search-mode').hidden=!data.search_mode||data.search_mode==='literal';
    $('#search-mode').textContent=data.search_mode==='related_topics'?t('Résultats liés à votre question : les termes techniques associés ont été utilisés.','Results related to your question: associated technical terms were used.','Resultados relacionados: se han utilizado términos técnicos asociados.'):t('Recherche élargie avec des équivalents techniques français, anglais et espagnols.','Search expanded using French, English and Spanish technical equivalents.','Búsqueda ampliada con equivalentes técnicos en francés, inglés y español.');
    const understood=[...Object.values(data.inferred_vehicle||{}),data.inferred_task?automotiveUI.filterLabel('task',data.inferred_task):'',data.inferred_spec||''].filter(Boolean);
    if(understood.length){$('#search-mode').hidden=false;$('#search-mode').textContent=t('Votre recherche a été comprise comme : ','Your search was interpreted as: ','Tu búsqueda se interpretó como: ')+understood.join(' · ');}
    if(data.interpretation_conflicts?.length){$('.result-explanation').open=true;$('#search-mode').hidden=false;$('#search-mode').textContent+=t(' Le véhicule cité diffère de votre sélection. Vérifiez les filtres.',' The vehicle mentioned differs from your selection. Check the filters.',' El vehículo mencionado difiere de tu selección. Comprueba los filtros.');}
    $('#results-status').innerHTML=`<strong>${n.toLocaleString(ui)}</strong> ${n===1?t('ressource trouvée','resource found','recurso encontrado'):t('ressources trouvées','resources found','recursos encontrados')}`;
    grid.innerHTML=loadedItems.length?loadedItems.map(cardMarkup).join(''):`<div class="empty"><strong>${t('Une autre trajectoire ?','Try another racing line?','¿Otra trazada?')}</strong><p>${vehicleKeys.some(key=>state[key])?t('Aucune correspondance explicite pour cette version et ces critères. Le moteur ou l’année peut manquer dans le titre ou la légende source. Retirer un filtre élargit les résultats, sans confirmer leur compatibilité.','No explicit match for this version and these filters. Source titles or captions may omit the engine or year. Removing a filter broadens results without confirming compatibility.','No hay coincidencia explícita para esta versión. El título o texto de la publicación puede omitir motor o año. Quitar un filtro amplía resultados sin confirmar compatibilidad.'):t('Aucun résultat avec ces critères. Essayez un mot plus simple ou retirez un filtre.','No results match these filters. Try a simpler term or remove a filter.','No hay resultados con estos filtros. Prueba otro término o elimina un filtro.')}</p><button data-reset>${t('Repartir de zéro','Reset search','Restablecer búsqueda')}</button></div>`;
    setImageFallback(grid);
    discoveryUI.recommendations(data);
    const pages=data.pages||Math.ceil(n/18)||1;
    $('#pagination').innerHTML=n?`<button data-page="${Math.max(1,state.page-1)}" ${state.page<=1?'disabled':''}>← ${t('Précédent','Previous','Anterior')}</button><span>${t('Page','Page','Página')} ${state.page} / ${pages}</span><button data-page="${state.page+1}" ${state.page>=pages?'disabled':''}>${t('Suivant','Next','Siguiente')} →</button>`:'';
  }catch(error){
    if(version!==requestVersion)return;
    $('#results-status').textContent=t('Catalogue indisponible','Catalog unavailable','Catálogo no disponible');
    grid.innerHTML=`<div class="empty"><strong>${t('La connexion au catalogue a échoué.','Could not connect to the catalog.','No se pudo conectar al catálogo.')}</strong><p>${t('Lancez le serveur local indiqué dans le guide puis réessayez.','Start the local server described in the guide, then retry.','Inicia el servidor local descrito en la guía e inténtalo de nuevo.')}</p><button data-retry>${t('Réessayer','Retry','Reintentar')}</button></div>`;
  }finally{if(version===requestVersion){grid.setAttribute('aria-busy','false');grid.inert=false;mobileUI.update();}}
}
function renderActiveFilters(){
  $('#active-filters').innerHTML=Object.entries(state).filter(([key,val])=>val&&!['q','language','sort','page','format'].includes(key)).map(([key,value])=>{
    const label=[...vehicleKeys,'task','system','spec'].includes(key)?automotiveUI.filterLabel(key,value):key==='format'?(value==='guide'?t('Guides','Guides','Guías'):t('Vidéos','Videos','Vídeos')):key==='content_format'?$('#content_format').selectedOptions[0]?.textContent: key==='category'?catName(value):key==='domain'?(value==='motorsport'?'Motorsport':t('Auto & compétences complémentaires','Automotive & related skills','Automóvil y competencias complementarias')):key==='level'?levelName(value):key==='language'?langName(value):key==='platform'?platformName(value):key==='transcript'?t('Transcription','Transcript','Transcripción'):key==='license'?t('Licence libre','Open license','Licencia libre'):value;
    return `<button data-remove="${key}" aria-label="${escape(t('Retirer le filtre ','Remove filter ','Quitar filtro ')+label)}">${escape(label)} ×</button>`;
  }).join('');
}
function setFilter(key,value){browsing=true;if(key==='format'&&!value)value='all';Object.assign(state,automotiveUI.dependentPatch(key,value));state.page=1;syncControls();syncUrl();if(vehicleKeys.includes(key))automotiveUI.loadOptions();loadVideos();}
function chooseContentLanguage(value,videoOnly=false){
  const fromHome=!browsing;
  state.q=$('#search').value.trim();
  if(videoOnly)state.format='video';
  discoveryUI.closeSuggestions();
  if($('#search-dialog')?.open){
    setFilter('language',value);
    $('#search').focus({preventScroll:true});
    discoveryUI.refreshSuggestions();
    return;
  }
  document.dispatchEvent(new Event('rl:search-chosen'));
  setFilter('language',value);const heading=$('#catalog-heading');
  if(fromHome){heading.tabIndex=-1;heading.focus({preventScroll:true});}
  heading.scrollIntoView({behavior:'smooth'});
}
function reset(){browsing=true;state={...automotiveDefaults,q:'',category:'',domain:'',level:'',language:'',platform:'',format:'all',content_format:'',duration:'',transcript:'',license:'',sort:'relevance',page:1};syncControls();syncUrl();automotiveUI.loadOptions();loadVideos();}
function goHome(){state={...automotiveDefaults,q:'',category:'',domain:'',level:'',language:state.language,platform:'',format:'all',content_format:'',duration:'',transcript:'',license:'',sort:'relevance',page:1};browsing=false;$('#vehicle-disclosure').open=false;discoveryUI.refresh();cinemaHome.render();changeView('explore');syncControls();automotiveUI.loadOptions();loadVideos();window.scrollTo({top:0,behavior:'instant'});}
function changeView(next,push=true){
  view=next;$$('main>section').forEach(el=>el.hidden=el.id!==`${next}-view`);
  $$('[data-view]').forEach(el=>{el.classList.toggle('active',el.dataset.view===next);if(el.dataset.view===next)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
  identityUI.sync();if(next==='saved')renderSaved();if(next==='faq')renderFaq();if(next==='paths')renderPaths();
  if(push){syncUrl(true);window.scrollTo({top:0,behavior:'instant'});$('#main').focus({preventScroll:true});}
}
function renderPaths(){
  if(activeTrack&&tracks[activeTrack]){
    const progress=storage.get('rl-library-progress',{}),steps=tracks[activeTrack];
    const done=steps.filter((_,i)=>progress[`${activeTrack}:${i}`]).length;
    $('#paths-view').innerHTML=`<button class="track-back" data-all-tracks>← ${t('Tous les parcours','All learning paths','Todos los itinerarios')}</button><p class="eyebrow">${t('PARCOURS GUIDÉ · 4 ÉTAPES','GUIDED PATH · 4 STEPS','ITINERARIO · 4 PASOS')}</p><h1>${escape(catName(activeTrack)).toUpperCase()}<br><span class="track-accent">${t('UN REPÈRE À LA FOIS.','ONE STEP AT A TIME.','PASO A PASO.')}</span></h1><p class="lead">${t('Explorez les ressources, notez ce que vous retenez, puis marquez l’étape comprise. Ce suivi personnel ne délivre pas de certification.','Explore resources, take notes, then mark a step understood. This personal tracker does not award certification.','Explora recursos, toma notas y marca los pasos comprendidos. Este seguimiento no otorga certificación.')}</p><div class="track-progress"><span>${done} / 4 ${t('étapes comprises','steps understood','pasos comprendidos')}</span><progress max="4" value="${done}" aria-label="${t('Progression personnelle','Personal progress','Progreso personal')}"></progress></div><div class="track-steps">${steps.map((step,i)=>`<article class="track-step ${progress[`${activeTrack}:${i}`]?'done':''}"><span class="step-number">0${i+1}</span><div><h2>${escape(t(...step.title))}</h2><p>${escape(t(...step.goal))}</p><div class="step-actions"><button data-step-query="${escape(step.query)}" data-step-category="${activeTrack}">${t('Trouver les tutoriels','Find tutorials','Buscar tutoriales')} ↗</button><button class="step-done" data-complete-step="${activeTrack}:${i}" aria-pressed="${Boolean(progress[`${activeTrack}:${i}`])}">${progress[`${activeTrack}:${i}`]?t('Compris ✓','Understood ✓','Comprendido ✓'):t('Marquer comme compris','Mark as understood','Marcar como comprendido')}</button></div></div></article>`).join('')}</div>`;
    return;
  }
  $('#paths-view').innerHTML=`<p class="eyebrow">${t('UN POINT DE DÉPART POUR CHAQUE AMBITION','A STARTING POINT FOR EVERY AMBITION','UN PUNTO DE PARTIDA PARA CADA AMBICIÓN')}</p><h1>${t('Apprenez, étape par étape.','Learn, step by step.','Aprende, paso a paso.')}</h1><p class="lead">${t('Huit portes d’entrée pour explorer le motorsport. Choisissez une discipline, puis adaptez les ressources à votre niveau.','Eight ways into motorsport. Pick a discipline, then filter the resources to your level.','Ocho puertas al automovilismo. Elige una disciplina y filtra los recursos según tu nivel.')}</p><div class="path-grid">${categories.map((c,i)=>`<button class="path-card" data-path="${c[0]}">${['mechanics','driving','simracing'].includes(c[0])?`<img class="path-photo" src="./assets/photos/${c[0]==='mechanics'?'service':c[0]}.jpg" alt="" width="960" height="640" loading="lazy">`:''}<span class="path-top"><span class="path-number">0${i+1} / RACELINK</span></span><h2>${escape(catName(c[0]))}</h2><p>${ui==='fr'?c[5]:t('',`Explore tutorials, methods and explanations in ${catName(c[0]).toLowerCase()}.`,`Explora tutoriales, métodos y explicaciones de ${catName(c[0]).toLowerCase()}.`)}</p><span class="path-bottom">${t('Découvrir le parcours','Explore this path','Descubrir el itinerario')}<span>↗</span></span></button>`).join('')}</div>`;
}
function renderFaq(openId){
  const merged=[...seedFaq,...faqItems.filter(x=>!seedFaq.some(s=>s.question===x.question))];
  $('#faq-view').innerHTML=`<p class="eyebrow">${t('LE STAND DES BONNES RÉPONSES','YOUR PIT STOP FOR ANSWERS','TU PARADA PARA ENCONTRAR RESPUESTAS')}</p><h1>${t('Comment peut-on vous aider ?','How can we help?','¿Cómo podemos ayudarte?' )}</h1><p class="lead">${t('Recherche, langues, transcriptions et premiers pas. Retrouvez les réponses aux questions qui vous ralentissent.','Search, languages, transcripts and first steps. Help articles are currently written in French.','Búsqueda, idiomas, transcripciones y primeros pasos. Los artículos de ayuda están disponibles en francés.')}</p><div class="faq-layout"><aside class="faq-side"><strong>RACELINK ACADEMY</strong><p>${t('Apprendre à votre rythme, comprendre vos sources et retrouver facilement ce qui vous aide.','Learn at your pace, understand your sources and find what helps you.','Aprende a tu ritmo, conoce tus fuentes y encuentra lo que te ayuda.')}</p></aside><div><input class="faq-search" id="faq-search" type="search" placeholder="${t('Rechercher dans l’aide…','Search help articles…','Buscar en la ayuda…')}" aria-label="${t('Rechercher dans l’aide','Search help','Buscar ayuda')}"><div id="faq-list">${merged.map(f=>`<details class="faq-item" id="faq-${escape(f.id)}" ${f.id===openId?'open':''}><summary>${escape(f.question)}</summary><p>${escape(f.answer)}</p>${f.sources?.length?`<div class="faq-sources">${f.sources.filter(source=>safeUrl(source.url)).map(source=>`<a href="${escape(safeUrl(source.url))}" target="_blank" rel="noopener noreferrer">${escape(source.title)} ↗</a>`).join('')}</div>`:''}</details>`).join('')}</div><p id="faq-empty" hidden>${t('Aucune réponse trouvée.','No answers found.','No se encontraron respuestas.')}</p></div></div>`;
  $('#faq-search').addEventListener('input',event=>{const q=normalize(event.target.value);let count=0;$$('.faq-item').forEach(el=>{el.hidden=!normalize(el.textContent).includes(q);if(!el.hidden)count++;});$('#faq-empty').hidden=count>0;});
}
function renderSaved(){
  const items=Object.values(saved);
  $('#saved-view').innerHTML=`<p class="eyebrow">${t('VOTRE CARNET DE PROGRESSION','YOUR LEARNING NOTEBOOK','TU CUADERNO DE APRENDIZAJE')}</p><h1>${t('Vos ressources enregistrées','Your saved resources','Tus recursos guardados')}</h1><p class="lead">${t('Vos ressources enregistrées dans ce navigateur. Revenez quand c’est le bon moment.','Resources saved in this browser. Return when the time is right.','Recursos guardados en este navegador. Vuelve cuando quieras.')}</p><div class="video-grid saved-grid">${items.length?items.map(cardMarkup).join(''):`<div class="empty"><strong>${t('Votre prochaine découverte vous attend.','Your next discovery awaits.','Tu próximo descubrimiento te espera.')}</strong><p>${t('Enregistrez une vidéo avec le marque-page pour la retrouver ici.','Save a video using its bookmark to find it here.','Guarda un vídeo con el marcador para encontrarlo aquí.')}</p><button data-view="explore">${t('Explorer le catalogue','Explore the catalog','Explorar el catálogo')}</button></div>`}</div>`;
  setImageFallback($('#saved-view'));
}
function toggleSave(id){
  if(saved[id])delete saved[id];else{const video=loadedItems.find(v=>v.id===id)||(detail?.id===id?detail:null);if(!video)return;saved[id]=video;}
  if(!storage.set('rl-library-saved',saved))showToast(t('Sauvegarde indisponible dans ce navigateur.','Saving is unavailable in this browser.','No se puede guardar en este navegador.'));
  else showToast(saved[id]?t('Ajouté à votre sélection','Added to your collection','Añadido a tu selección'):t('Retiré de votre sélection','Removed from your collection','Quitado de tu selección'));
  updateSavedCount();
  $$('[data-save]').filter(el=>el.dataset.save===id).forEach(el=>{el.classList.toggle('saved',Boolean(saved[id]));el.setAttribute('aria-pressed',String(Boolean(saved[id])));el.setAttribute('aria-label',saved[id]?t('Retirer de ma sélection','Remove from collection','Quitar de mi selección'):t('Enregistrer la vidéo','Save video','Guardar vídeo'));if(el.classList.contains('save-card'))el.innerHTML=glyph('bookmark',{size:21});else el.textContent=saved[id]?t('Enregistré ✓','Saved ✓','Guardado ✓'):t('Enregistrer','Save','Guardar');});
  if(view==='saved')renderSaved();
}
function embedUrl(video,time=0){
  const source=safeUrl(video.url);if(!source)return '';
  const u=new URL(source);let id='';
  if(video.platform==='youtube'&&(['youtube.com','www.youtube.com','m.youtube.com','youtu.be'].includes(u.hostname))){id=u.hostname==='youtu.be'?u.pathname.slice(1):u.searchParams.get('v')||u.pathname.split('/').pop();if(!/^[\w-]{11}$/.test(id))return '';return `https://www.youtube-nocookie.com/embed/${id}?start=${Math.floor(time)}&rel=0`;}
  if(video.platform==='vimeo'&&['vimeo.com','www.vimeo.com'].includes(u.hostname)){id=u.pathname.split('/').filter(Boolean).pop();if(/^\d+$/.test(id))return `https://player.vimeo.com/video/${id}#t=${Math.floor(time)}s`;}
  if(video.platform==='dailymotion'&&['www.dailymotion.com','dailymotion.com'].includes(u.hostname)){id=u.pathname.match(/\/video\/([a-zA-Z0-9]+)/)?.[1];if(id)return `https://www.dailymotion.com/embed/video/${id}?start=${Math.floor(time)}`;}
  return '';
}
function loadPlayer(time=0){
  if(!detail)return;const embed=embedUrl(detail,time);
  if(!embed)return;
  $('#player').innerHTML=`<iframe src="${escape(embed)}" title="${escape(detail.title)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>`;
}
function resourceDetailContext(){return {escape,t,safeUrl,embedUrl,catName,levelName,platformName,langName,estimatedLanguage,licenseName,fmtDuration,isSaved:Boolean(saved[detail.id]),socialMarkup:video=>socialContentMarkup(video,{escape,t}),automotiveMarkup:video=>automotiveUI.detailMarkup(video)};}
async function openVideo(id){
  const version=++detailVersion;const dialog=$('#video-dialog');
  if(!dialog.open)dialog.showModal();
  $('#video-detail').innerHTML=`<div class="detail-header"><span>RACELINK ACADEMY</span><button data-close aria-label="${t('Fermer','Close','Cerrar')}">×</button></div><div class="empty"><p>${t('Chargement de la ressource…','Loading resource…','Cargando recurso…')}</p></div>`;
  try{
    const result=await window.getCatalogJson(`/aide/api/videos/${encodeURIComponent(id)}`);if(version!==detailVersion||!dialog.open)return;detail=result.video||result.item||result;
    $('#video-detail').innerHTML=renderResourceDetail(detail,resourceDetailContext());
    renderDetailPick();setDetailTab('about');setImageFallback($('#video-detail'));$('#dialog-title').tabIndex=-1;$('#dialog-title').focus({preventScroll:true});
  }catch{
    if(version!==detailVersion)return;
    $('#video-detail').insertAdjacentHTML('beforeend',`<div class="empty"><p>${t('Cette ressource ne peut pas être chargée. Fermez la fiche et réessayez.','This resource could not be loaded. Close this panel and retry.','No se pudo cargar este recurso. Cierra la ficha y vuelve a intentarlo.')}</p></div>`);
  }
}
function setDetailTab(name){
  $$('.detail-tabs button').forEach(el=>{const active=el.dataset.tab===name;el.classList.toggle('active',active);el.setAttribute('aria-selected',String(active));el.tabIndex=active?0:-1;});
  const panel=$('#detail-panel');panel.setAttribute('aria-labelledby',`tab-${name}`);
  if(name==='about'){
    panel.innerHTML=renderResourceOverview(detail,resourceDetailContext());
  }else if(name==='notes'){
    const note=storage.get(`rl-note-${detail.id}`,'');
    panel.innerHTML=`<h3>${t('Gardez le déclic.','Capture the insight.','Guarda la idea.')}</h3><textarea class="notes-area" id="video-notes" aria-label="${t('Notes personnelles','Personal notes','Notas personales')}" placeholder="${t('Une idée à tester, une notion à revoir…','An idea to try, a concept to revisit…','Una idea para probar, un concepto para repasar…')}">${escape(note)}</textarea><p class="small-note" id="notes-status">${t('Notes privées, enregistrées automatiquement dans ce navigateur.','Private notes, saved automatically in this browser.','Notas privadas guardadas automáticamente en este navegador.')}</p>`;
    $('#video-notes').addEventListener('input',e=>{if(!storage.set(`rl-note-${detail.id}`,e.target.value))$('#notes-status').textContent=t('Enregistrement impossible. Copiez vos notes pour les conserver.','Could not save. Copy your notes to keep them.','No se pudo guardar. Copia tus notas para conservarlas.');});
  }else{
    const transcript=detail.transcript;
    const text=typeof transcript==='string'?transcript:transcript?.text||transcript?.content||'';
    if(!detail.has_transcript||!text){
      panel.innerHTML=`<div class="transcript-empty"><strong>${t('Le texte n’est pas encore disponible.','The text is not available yet.','El texto aún no está disponible.')}</strong><p>${t('Aucune transcription réutilisable n’est enregistrée pour cette vidéo. Des sous-titres peuvent être proposés directement par son auteur ou dans le lecteur de la plateforme.','No reusable transcript is stored for this video. Captions may be available from its creator or in the platform player.','No hay una transcripción reutilizable guardada para este vídeo. Su autor o el reproductor pueden ofrecer subtítulos.')}</p><a href="${escape(safeUrl(detail.url))}" target="_blank" rel="noopener noreferrer">${t('Vérifier les sous-titres à la source','Check captions at the source','Consultar subtítulos en la fuente')} ↗</a></div><p class="small-note">${t('Un résumé n’est jamais présenté comme une transcription.','A summary is never presented as a transcript.','Un resumen nunca se presenta como una transcripción.')}</p>`;
    }else{
      const cues=readingSegments(transcript.segments||transcript.cues||[]);
      panel.innerHTML=`<p class="small-note transcript-quality">${escape(String(transcript.kind).includes('automatic')?t('Transcription automatique · erreurs possibles','Automatic transcript · errors may occur','Transcripción automática · posibles errores'):t('Sous-titres publiés par la source','Captions published by the source','Subtítulos publicados por la fuente'))}</p><input class="transcript-search" id="transcript-search" type="search" placeholder="${t('Trouver un mot dans la transcription','Find a word in the transcript','Buscar una palabra en la transcripción')}" aria-label="${t('Rechercher dans la transcription','Search transcript','Buscar en la transcripción')}"><p class="small-note" id="transcript-match-status" role="status"></p><div class="transcript-text" id="transcript-text">${cues.length?cues.map(c=>`<div class="cue"><button data-seek="${Number(c.start)||0}">${Math.floor((Number(c.start)||0)/60)}:${String(Math.floor((Number(c.start)||0)%60)).padStart(2,'0')}</button><p>${escape(c.text)}</p></div>`).join(''):escape(text)}</div><p class="source-info">${t('Langue :','Language:','Idioma:')} ${escape(langName(detail.transcript_language||detail.language))}<br>© ${escape(detail.creator)} · ${escape(licenseName(detail.license))}<br>${t('Sous-titres regroupés pour la lecture, sans traduction.','Captions grouped for reading, without translation.','Subtítulos agrupados para la lectura, sin traducción.')}<br><a href="${escape(safeUrl(transcript.source_url||detail.url))}" target="_blank" rel="noopener noreferrer">${t('Source originale','Original source','Fuente original')} ↗</a> · ${transcript.license_url?`<a href="${escape(safeUrl(transcript.license_url))}" target="_blank" rel="noopener noreferrer">${t('Licence et attribution','License and attribution','Licencia y atribución')} ↗</a>`:''}</p>`;
      $('#transcript-search').addEventListener('input',e=>{const query=normalize(e.target.value);let count=0;if(cues.length)$$('.cue').forEach(c=>{c.hidden=!normalize(c.textContent).includes(query);if(!c.hidden)count++;});else{$('#transcript-text').textContent=query?text.split('\n').filter(l=>normalize(l).includes(query)).join('\n'):text;count=$('#transcript-text').textContent?1:0;}$('#transcript-match-status').textContent=query?`${count} ${t('passages trouvés','passages found','pasajes encontrados')}`:'';});
    }
  }
}
document.addEventListener('click',async event=>{
  const el=event.target.closest('button,a');if(!el)return;
  if(el.hasAttribute('data-home')){goHome();}
  else if(el.dataset.view){event.preventDefault();if(el.dataset.view==='explore')goHome();else changeView(el.dataset.view);}
  else if(el.hasAttribute('data-content-language'))chooseContentLanguage(el.dataset.contentLanguage,el.id==='french-videos');
  else if(el.hasAttribute('data-format'))setFilter('format',el.dataset.format);
  else if(el.hasAttribute('data-guide'))openGuide(el.dataset.guide,el.dataset.guideSection);
  else if(el.hasAttribute('data-query')){changeView('explore');setFilter('q',el.dataset.query);$('#catalog-heading').scrollIntoView({behavior:'smooth'});}
  else if(el.hasAttribute('data-category'))setFilter('category',el.dataset.category);
  else if(el.hasAttribute('data-path')){activeTrack=el.dataset.path;changeView('paths');}
  else if(el.hasAttribute('data-all-tracks')){activeTrack='';renderPaths();syncUrl(true);}
  else if(el.hasAttribute('data-step-query')){browsing=true;changeView('explore');state={...automotiveDefaults,q:el.dataset.stepQuery,category:el.dataset.stepCategory,domain:'',level:'',language:state.language,platform:'',format:'all',content_format:'',duration:'',transcript:'',license:'',sort:'relevance',page:1};syncControls();syncUrl();automotiveUI.loadOptions();loadVideos();$('#catalog-heading').scrollIntoView({behavior:'smooth'});}
  else if(el.hasAttribute('data-complete-step')){const key=el.dataset.completeStep,p=storage.get('rl-library-progress',{});p[key]=!p[key];storage.set('rl-library-progress',p);renderPaths();$$('[data-complete-step]').find(button=>button.dataset.completeStep===key)?.focus({preventScroll:true});}
  else if(el.hasAttribute('data-platform-choice'))setFilter('platform',el.dataset.platformChoice);
  else if(el.hasAttribute('data-close-vehicle')){$('#vehicle-disclosure').open=false;$('#catalog-heading').focus({preventScroll:true});}
  else if(el.hasAttribute('data-remove'))setFilter(el.dataset.remove,'');
  else if(el.hasAttribute('data-reset'))reset();
  else if(el.hasAttribute('data-retry'))loadVideos();
  else if(el.hasAttribute('data-page')){state.page=Number(el.dataset.page);syncUrl();await loadVideos();$('#catalog-heading').scrollIntoView({behavior:'smooth'});}
  else if(el.hasAttribute('data-video'))openVideo(el.dataset.video);
  else if(el.hasAttribute('data-save'))toggleSave(el.dataset.save);
  else if(el.hasAttribute('data-close'))$('#video-dialog').close();
  else if(el.hasAttribute('data-play'))loadPlayer();
  else if(el.hasAttribute('data-seek'))loadPlayer(Number(el.dataset.seek));
  else if(el.hasAttribute('data-tab'))setDetailTab(el.dataset.tab);
  else if(el.hasAttribute('data-faq')){changeView('faq');renderFaq(el.dataset.faq);$(`#faq-${el.dataset.faq}`)?.scrollIntoView({behavior:'smooth',block:'center'});}
  else if(el.hasAttribute('data-share')){try{await navigator.clipboard.writeText(detail.url);showToast(t('Lien source copié','Source link copied','Enlace de origen copiado'));}catch{showToast(t('Utilisez le bouton Voir la source pour copier l’adresse.','Use View source to copy its address.','Usa Ver fuente para copiar la dirección.'));}}
});
$('#search-form').addEventListener('submit',e=>{e.preventDefault();const query=$('#search').value.trim();document.dispatchEvent(new Event('rl:search-chosen'));if(view!=='explore')changeView('explore',false);setFilter('q',query);$('#catalog-heading').scrollIntoView({behavior:'smooth'});});
for(const key of ['level','platform','duration','sort','domain','content_format'])$(`#${key}`).addEventListener('change',e=>setFilter(key,e.target.value));
$('#language').addEventListener('change',e=>chooseContentLanguage(e.target.value));
$('#home-language').addEventListener('change',e=>chooseContentLanguage(e.target.value,true));
$('#transcript').addEventListener('change',e=>setFilter('transcript',e.target.checked?'available':''));
$('#license').addEventListener('change',e=>setFilter('license',e.target.checked?'open':''));
$('#reset-filters').addEventListener('click',()=>{const query=state.q,format=state.format;state={...automotiveDefaults,q:query,category:'',domain:'',level:'',language:'',platform:'',format,content_format:'',duration:'',transcript:'',license:'',sort:state.sort,page:1};syncControls();syncUrl();automotiveUI.loadOptions();loadVideos();});
$('#method-link').addEventListener('click',e=>{e.preventDefault();changeView('faq');renderFaq('method');});
function openVehicle(){
  browsing=true;changeView('explore',false);syncControls();syncUrl(true);loadVideos();
  $('#vehicle-disclosure').open=true;$('#vehicle-disclosure').scrollIntoView({behavior:'smooth',block:'start'});
  $('#vehicle-make')?.focus({preventScroll:true});
}
$('.workshop-jump').addEventListener('click',e=>{e.preventDefault();openVehicle();});
document.addEventListener('rl:open-vehicle',openVehicle);
$('#ui-language').addEventListener('change',e=>{ui=e.target.value;storage.set('rl-library-language',ui);applyTranslations();syncUrl();loadVideos();});
$('#video-dialog').addEventListener('close',()=>{++detailVersion;$('#video-detail').innerHTML='';detail=null;});
$('#video-dialog').addEventListener('click',e=>{if(e.target===$('#video-dialog')){const rect=e.target.getBoundingClientRect();if(e.clientX<rect.left||e.clientX>rect.right||e.clientY<rect.top||e.clientY>rect.bottom)e.target.close();}});
document.addEventListener('keydown',e=>{
  if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName)&&!document.querySelector('dialog[open]')){e.preventDefault();mobileUI.openSearch();}
  if(e.target.closest('.detail-tabs')&&['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();const tabs=$$('[role=tab]');const idx=tabs.indexOf(e.target);const next=e.key==='Home'?0:e.key==='End'?tabs.length-1:(idx+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;tabs[next].focus();setDetailTab(tabs[next].dataset.tab);}
});
window.addEventListener('popstate',()=>{restoreUrl();applyTranslations();changeView(view,false);automotiveUI.loadOptions();loadVideos();});
async function init(){
  restoreUrl();applyTranslations();changeView(view,false);updateSavedCount();
  const discoveryLoad=discoveryUI.load();
  const [statsResult,faqResult,vehicleFaqResult]=await Promise.allSettled([window.getCatalogJson('/aide/api/stats'),fetch('/racelink-academy/faq.json').then(r=>r.ok?r.json():Promise.reject()),fetch('/racelink-academy/vehicle-faq.json').then(r=>r.ok?r.json():Promise.reject()),automotiveUI.load()]);
  if(statsResult.status==='fulfilled'){stats=statsResult.value;renderStats();}
  if(faqResult.status==='fulfilled')faqItems=faqResult.value.items||faqResult.value;
  if(vehicleFaqResult.status==='fulfilled')faqItems.push(...(vehicleFaqResult.value.items||vehicleFaqResult.value));
  if(view==='faq')renderFaq();
  await loadVideos();
  await discoveryLoad;
  const cinemaResult=await cinemaHome.load();
  document.body.classList.toggle('cinema-ready',Boolean(cinemaResult?.ready));
  if(new URLSearchParams(location.search).has('video'))openVideo(new URLSearchParams(location.search).get('video'));
}
init();
