export const vehicleKeys=['make','model','generation','engine','body_type','fuel_type','year'];
export const automotiveDefaults=Object.fromEntries([...vehicleKeys,'task','system','spec'].map(key=>[key,'']));

export function createAutomotiveUI(ctx){
  const {escape:e,t,storage}=ctx;
  const $=s=>document.querySelector(s);
  let taxonomy={},guides=[],manuals=[],options={},optionVersion=0,resultFacets={};
  const fallbackTasks=[
    ['oil_change','Vidange','Oil change','Cambio de aceite'],
    ['wipers','Essuie-glaces','Wipers','Limpiaparabrisas'],
    ['wheel_change','Changer une roue','Change a wheel','Cambiar una rueda'],
    ['battery','Batterie 12 V','12 V battery','Batería de 12 V'],
    ['fuses','Fusibles','Fuses','Fusibles'],
    ['lighting','Éclairage','Lighting','Iluminación'],
    ['diagnostics','Diagnostic & OBD','Diagnostics & OBD','Diagnóstico y OBD'],
    ['service_reset','Réinitialisation entretien','Service reset','Reinicio de mantenimiento'],
    ['oil_spec','Références d’huile','Oil specifications','Especificaciones de aceite'],
    ['fuel_choice','Choisir son carburant','Choose fuel','Elegir combustible']
  ];
  const labels={
    make:['Marque','Make','Marca'],model:['Modèle','Model','Modelo'],
    generation:['Génération / série','Generation / series','Generación / serie'],
    engine:['Motorisation mentionnée','Engine mentioned','Motor mencionado'],
    body_type:['Carrosserie / type','Body type','Tipo de carrocería'],
    fuel_type:['Énergie du véhicule','Vehicle fuel / power','Energía del vehículo'],
    year:['Année','Year','Año'],task:['Intervention','Task','Intervención'],
    system:['Système','System','Sistema'],spec:['Référence mentionnée','Specification mentioned','Referencia mencionada']
  };
  function named(group,value){
    const item=(taxonomy[group]||[]).find(item=>(item.id||item.value)===value);
    const label=item?.label||item?.labels;
    if(label)return typeof label==='string'?label:label[ctx.getUi()]||label.fr||value;
    if(group==='tasks'){const row=fallbackTasks.find(row=>row[0]===value);if(row)return t(...row.slice(1));}
    return value;
  }
  function filterLabel(key,value){
    return ['task','system','body_type','fuel_type'].includes(key)?named(({task:'tasks',system:'systems',body_type:'body_types',fuel_type:'fuel_types'})[key],value):value;
  }
  function selectField(key){
    return `<div class="vehicle-field"><label for="vehicle-${key}">${e(t(...labels[key]))}</label><select id="vehicle-${key}" data-vehicle="${key}"><option value="">${t('Non précisé','Not specified','Sin especificar')}</option></select></div>`;
  }
  const root=$('#vehicle-hub');
  function render(){
    root.innerHTML=`<div class="vehicle-top"><div><p class="eyebrow">${t('L’ATELIER RACELINK','THE RACELINK WORKSHOP','EL TALLER RACELINK')}</p><h2>${t('La bonne ressource.<br>Pour votre voiture.','The right resource.<br>For your car.','El recurso adecuado.<br>Para tu coche.')}</h2></div><p>${t('Un modèle, une version, une intervention.<br>Retrouvez les gestes et les repères qui vous concernent.','A model, a version, a task.<br>Find the methods and references that matter to you.','Un modelo, una versión, una tarea.<br>Encuentra los métodos y referencias que necesitas.')}</p></div>
      <div class="vehicle-primary">${['make','model','generation'].map(selectField).join('')}<div class="vehicle-field"><label for="vehicle-year">${e(t(...labels.year))}</label><input id="vehicle-year" type="number" inputmode="numeric" min="1886" max="2100" step="1" placeholder="${t('Facultatif','Optional','Opcional')}" data-vehicle="year"></div></div>
      <details class="vehicle-advanced" ${['engine','body_type','fuel_type'].some(k=>ctx.getState()[k])?'open':''}><summary>${t('Préciser le moteur, l’énergie et la carrosserie','Specify engine, fuel and body type','Precisar motor, energía y carrocería')}</summary><div class="vehicle-secondary">${['engine','fuel_type','body_type'].map(selectField).join('')}</div></details>
      <div class="vehicle-actions"><span id="vehicle-current" role="status"></span><button type="button" id="save-vehicle">${t('Mémoriser ce véhicule','Remember this vehicle','Recordar este vehículo')}</button><button type="button" id="use-vehicle" hidden>${t('Reprendre mon véhicule','Use my saved vehicle','Usar mi vehículo guardado')}</button><button type="button" id="clear-vehicle">${t('Retirer les filtres véhicule','Clear vehicle filters','Quitar filtros de vehículo')}</button><button type="button" id="forget-vehicle" hidden>${t('Oublier mon véhicule','Forget saved vehicle','Olvidar mi vehículo')}</button></div>
      <p class="vehicle-provenance" id="vehicle-options-status">${t('Les véhicules sont repérés dans les titres ou les légendes des sources. Vérifiez la génération, le moteur et la notice avant d’appliquer une procédure.','Vehicles are identified in source titles or captions. Check the generation, engine and owner’s manual before applying a procedure.','Los vehículos se identifican en los títulos o textos de las publicaciones. Comprueba generación, motor y manual antes de aplicar un procedimiento.')}</p>
      <div class="workshop-needs"><strong>${t('Que voulez-vous faire ?','What would you like to do?','¿Qué quieres hacer?')}</strong><div id="maintenance-shortcuts"></div></div>
      <div class="workshop-refine"><div class="vehicle-field"><label for="maintenance-task">${e(t(...labels.task))}</label><select id="maintenance-task" data-maintenance="task"></select></div><div class="vehicle-field"><label for="maintenance-system">${e(t(...labels.system))}</label><select id="maintenance-system" data-maintenance="system"></select></div><form class="vehicle-field specification-form" id="specification-form"><label for="maintenance-spec">${t('Huile, norme ou carburant','Oil, standard or fuel','Aceite, norma o combustible')}</label><div><input id="maintenance-spec" list="specification-options" type="search" maxlength="80" placeholder="5W-30, RN0720, VW 504 00, E10…" aria-describedby="spec-help"><button type="submit" aria-label="${t('Rechercher la référence','Search specification','Buscar referencia')}">→</button></div><datalist id="specification-options"></datalist></form></div>
      <p class="vehicle-provenance" id="spec-help">${t('Une référence trouvée dans une vidéo n’est pas une recommandation pour votre moteur. La viscosité seule ne suffit pas : vérifiez aussi l’homologation constructeur.','A specification mentioned in a video is not a recommendation for your engine. Viscosity alone is insufficient: check the manufacturer approval too.','Una referencia en un vídeo no es una recomendación para tu motor. La viscosidad no basta: comprueba la homologación del fabricante.')}</p>
      <details class="workshop-guidance"><summary>${t('Bien identifier sa voiture, son huile et son carburant','Identify your car, oil and fuel correctly','Identificar el coche, aceite y combustible')}</summary><div id="vehicle-guides"></div></details>`;
    root.querySelectorAll('[data-vehicle]').forEach(el=>el.addEventListener('change',()=>{
      if(el.type==='number'&&!el.checkValidity()){el.reportValidity();return;}
      ctx.change(el.dataset.vehicle,el.value);
    }));
    root.querySelectorAll('[data-maintenance]').forEach(el=>el.addEventListener('change',()=>ctx.change(el.dataset.maintenance,el.value)));
    $('#specification-form').addEventListener('submit',event=>{event.preventDefault();ctx.change('spec',$('#maintenance-spec').value.trim());});
    $('#maintenance-spec').addEventListener('search',event=>{if(!event.target.value)ctx.change('spec','');});
    $('#clear-vehicle').addEventListener('click',()=>ctx.patch(Object.fromEntries(vehicleKeys.map(k=>[k,'']))));
    $('#save-vehicle').addEventListener('click',()=>{
      const current=ctx.getState();
      if(!current.make){ctx.toast(t('Choisissez au moins une marque.','Choose a make first.','Elige una marca primero.'));return;}
      const saved=Object.fromEntries(vehicleKeys.map(k=>[k,current[k]||'']));
      if(storage.set('rl-library-vehicle',saved))ctx.toast(t('Véhicule mémorisé dans ce navigateur.','Vehicle saved in this browser.','Vehículo guardado en este navegador.'));
      else ctx.toast(t('Enregistrement indisponible.','Saving unavailable.','No se puede guardar.'));
      sync();
    });
    $('#use-vehicle').addEventListener('click',()=>{const saved=storage.get('rl-library-vehicle',{});ctx.patch(Object.fromEntries(vehicleKeys.map(k=>[k,String(saved[k]||'')])));});
    $('#forget-vehicle').addEventListener('click',()=>{if(storage.set('rl-library-vehicle',{})){ctx.toast(t('Véhicule mémorisé supprimé de ce navigateur.','Saved vehicle removed from this browser.','Vehículo guardado eliminado de este navegador.'));sync();}else ctx.toast(t('Suppression impossible dans ce navigateur.','Could not remove saved data.','No se pudo eliminar.'));});
    renderMaintenance();renderGuides();renderOptions();setResultFacets(resultFacets);sync();
  }
  function renderMaintenance(){
    const state=ctx.getState(),taskList=taxonomy.tasks?.length?taxonomy.tasks.map(x=>x.id):fallbackTasks.map(x=>x[0]);
    $('#maintenance-task').innerHTML=`<option value="">${t('Toutes les interventions','All tasks','Todas las intervenciones')}</option>`+taskList.map(v=>`<option value="${e(v)}">${e(named('tasks',v))}</option>`).join('');
    $('#maintenance-system').innerHTML=`<option value="">${t('Tous les systèmes','All systems','Todos los sistemas')}</option>`+(taxonomy.systems||[]).map(x=>`<option value="${e(x.id)}">${e(named('systems',x.id))}</option>`).join('');
    $('#maintenance-shortcuts').innerHTML=['oil_change','wipers','wheel_change','fuses','oil_spec','fuel_choice'].map(v=>`<button type="button" data-task-shortcut="${v}" aria-pressed="${state.task===v}">${e(named('tasks',v))}</button>`).join('');
    root.querySelectorAll('[data-task-shortcut]').forEach(button=>button.addEventListener('click',()=>ctx.change('task',ctx.getState().task===button.dataset.taskShortcut?'':button.dataset.taskShortcut)));
  }
  function renderOptions(){
    const state=ctx.getState();
    for(const key of vehicleKeys.filter(k=>k!=='year')){
      const select=$(`#vehicle-${key}`);if(!select)continue;
      const values=options[key]||[],value=state[key]||'';
      select.innerHTML=`<option value="">${t('Non précisé','Not specified','Sin especificar')}</option>`+values.map(item=>`<option value="${e(item.value)}">${e(filterLabel(key,item.value))} (${Number(item.count)||0})</option>`).join('');
      if(value&&!values.some(item=>String(item.value)===String(value)))select.insertAdjacentHTML('beforeend',`<option value="${e(value)}">${e(filterLabel(key,value))} · ${t('non repéré','not found','no encontrado')}</option>`);
      select.value=value;
      select.disabled=(key==='model'&&!state.make)||(key==='generation'&&!state.model);
    }
  }
  function sync(){
    const state=ctx.getState();
    for(const key of vehicleKeys){const el=$(`#vehicle-${key}`);if(el)el.value=state[key]||'';}
    if($('#maintenance-task'))$('#maintenance-task').value=state.task||'';
    if($('#maintenance-system'))$('#maintenance-system').value=state.system||'';
    if($('#maintenance-spec'))$('#maintenance-spec').value=state.spec||'';
    const selected=vehicleKeys.filter(k=>state[k]).map(k=>filterLabel(k,state[k]));
    if($('#vehicle-current'))$('#vehicle-current').textContent=selected.length?selected.join(' · '):t('Aucun véhicule sélectionné','No vehicle selected','Ningún vehículo seleccionado');
    for(const selector of ['#use-vehicle','#forget-vehicle'])if($(selector))$(selector).hidden=!storage.get('rl-library-vehicle',{}).make;
    root.querySelectorAll('[data-task-shortcut]').forEach(button=>button.setAttribute('aria-pressed',String(state.task===button.dataset.taskShortcut)));
  }
  async function loadOptions(){
    const version=++optionVersion,state=ctx.getState();
    const params=new URLSearchParams(Object.fromEntries(vehicleKeys.map(k=>[k,state[k]||''])));
    root.setAttribute('aria-busy','true');
    try{
      const data=await window.getCatalogJson(`/aide/api/vehicle-options?${params}`);
      if(version!==optionVersion)return;
      options=data.options||data.facets||{};renderOptions();sync();$('#vehicle-options-status').textContent=t('Les véhicules sont repérés dans les titres ou les légendes des sources. Vérifiez la génération, le moteur et la notice avant d’appliquer une procédure.','Vehicles are identified in source titles or captions. Check the generation, engine and owner’s manual before applying a procedure.','Los vehículos se identifican en los títulos o textos de las publicaciones. Comprueba generación, motor y manual antes de aplicar un procedimiento.');
    }catch{
      if(version!==optionVersion)return;
      $('#vehicle-options-status').textContent=t('Les filtres véhicule ne sont pas disponibles. Rechargez la page ou utilisez la recherche par titre.','Vehicle filters are unavailable. Reload or use title search.','Filtros de vehículo no disponibles. Recarga o busca por título.');
    }finally{if(version===optionVersion)root.setAttribute('aria-busy','false');}
  }
  function dependentPatch(key,value){
    const patch={[key]:value};
    if(key==='make')for(const k of vehicleKeys.filter(k=>k!=='make'))patch[k]='';
    if(key==='model')for(const k of ['generation','engine','year','body_type','fuel_type'])patch[k]='';
    if(key==='generation')for(const k of ['engine','year','body_type','fuel_type'])patch[k]='';
    return patch;
  }
  function setResultFacets(facets){
    resultFacets=facets||{};
    if($('#specification-options'))$('#specification-options').innerHTML=(resultFacets.spec||[]).map(item=>`<option value="${e(item.value)}">${Number(item.count)||0} ${t('références','references','referencias')}</option>`).join('');
  }
  function sourceLinks(sources){
    return (sources||[]).filter(s=>/^https:\/\//.test(s.url)).map(s=>`<a href="${e(s.url)}" target="_blank" rel="noopener noreferrer">${e(s.title||s.label||s.make)} ↗</a>`).join('');
  }
  function renderGuides(){
    const box=$('#vehicle-guides');if(!box)return;
    box.innerHTML=`${ctx.getUi()!=='fr'?`<p class="small-note">${t('','Guidance articles are currently in French.','Las guías están disponibles en francés.')}</p>`:''}<div class="vehicle-guide-grid">${guides.map(guide=>`<article class="workshop-guide"><h3>${e(guide.title)}</h3><p>${e(guide.cardSummary||guide.intro||'')}</p><button type="button" data-guide="${e(guide.id)}">${t('Ouvrir le guide et ses sources','Open guide and sources','Abrir guía y fuentes')} <span aria-hidden="true">→</span></button></article>`).join('')}</div>${manuals.length?`<p class="detail-label">${t('TROUVER LA NOTICE DE MON VÉHICULE','FIND MY VEHICLE MANUAL','ENCONTRAR EL MANUAL DE MI VEHÍCULO')}</p><div class="manual-links">${sourceLinks(manuals)}</div>`:''}`;
  }
  function renderContext(task=ctx.getState().task){
    const hint=$('#maintenance-guide-hint');if(!hint)return;
    const guide=guides.find(g=>g.task&&g.task===task);
    hint.hidden=!guide;
    if(!guide){hint.innerHTML='';return;}
    hint.innerHTML=`<div><span class="guide-card-kind">${t('Les repères RaceLink','RaceLink guidance','Guía RaceLink')}</span><strong>${e(guide.title)}</strong><p>${e(guide.cardSummary||guide.intro)}</p></div><button type="button" data-guide="${e(guide.id)}">${t('Guide & notices constructeur','Guide & manufacturer manuals','Guía y manuales del fabricante')} <span aria-hidden="true">→</span></button>`;
  }
  function cardMarkup(video){
    const vehicles=video.automotive?.vehicles||[];
    if(!vehicles.length)return '';
    const first=vehicles[0],label=[first.make,first.model,first.generation,first.engine].filter(Boolean).join(' ');
    return `<p class="card-vehicle">${e(label)}${vehicles.length>1?` +${vehicles.length-1}`:''}<span>${t('Véhicule cité','Vehicle mentioned','Vehículo mencionado')}</span></p>`;
  }
  function detailMarkup(video){
    const data=video.automotive;if(!data)return '';
    const vehicles=data.vehicles||[],specs=data.specifications||[];
    if(!vehicles.length&&!data.tasks?.length&&!specs.length)return '';
    return `<section class="detail-vehicle"><h3>${t('Repères véhicule & entretien','Vehicle & maintenance references','Vehículo y mantenimiento')}</h3>${vehicles.length?`<ul>${vehicles.slice(0,12).map(v=>`<li><strong>${e([v.make,v.model,v.generation].filter(Boolean).join(' '))}</strong><span>${e([v.engine,filterLabel('body_type',v.body_type||''),filterLabel('fuel_type',v.fuel_type||''),v.year_from?`${v.year_from}${v.year_to&&v.year_to!==v.year_from?'–'+v.year_to:''}`:''].filter(Boolean).join(' · ')||t('Motorisation et année non précisées','Engine and year unspecified','Motor y año sin especificar'))}</span></li>`).join('')}</ul>`:''}${data.tasks?.length?`<p>${data.tasks.map(task=>e(named('tasks',task))).join(' · ')}</p>`:''}${specs.length?`<p><strong>${t('Références citées :','Specifications mentioned:','Referencias mencionadas:')}</strong> ${specs.map(s=>e(s.value)).join(' · ')}</p>`:''}<p class="small-note">${t('Informations repérées dans le titre ou la légende source, sans validation de compatibilité. Vérifiez votre version et la notice constructeur ; une référence d’huile ou de carburant citée ici n’est pas une prescription.','Information identified in the source title or caption, without fitment validation. Check your exact version and owner’s manual; an oil or fuel specification here is not a recommendation.','Datos identificados en el título o texto de la publicación, sin validar compatibilidad. Comprueba versión y manual; una referencia de aceite o combustible no es una recomendación.')}</p></section>`;
  }
  async function load(){
    const [tax,guidance]=await Promise.allSettled([
      fetch('/racelink-academy/automotive-taxonomy.json').then(r=>r.ok?r.json():Promise.reject()),
      fetch('/racelink-academy/vehicle-guides.json?v=guide-v16b').then(r=>r.ok?r.json():Promise.reject())
    ]);
    if(tax.status==='fulfilled')taxonomy=tax.value;
    if(guidance.status==='fulfilled'){guides=[...(guidance.value.identification?[guidance.value.identification]:[]),...(guidance.value.guides||[])];manuals=guidance.value.manuals||[];ctx.picks?.setResources(guides.filter(g=>g.recommendation).map(g=>({kind:'guide',id:g.id,...g.recommendation})));}
    renderMaintenance();renderGuides();sync();renderContext();await loadOptions();
  }
  return {render,sync,load,loadOptions,setResultFacets,renderContext,dependentPatch,filterLabel,cardMarkup,detailMarkup};
}
