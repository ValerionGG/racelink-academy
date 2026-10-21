import {icon, categoryIcon} from './icons.js';

// Navigation is a native dialog: focus containment, Escape and focus return
// remain provided by the browser. Links reuse the existing catalog actions.
export function createIdentityUI({t, openSearch, getView, isBrowsing}) {
  const $ = selector => document.querySelector(selector);
  const categories = [
    ['mechanics','Mécanique','Mechanics','Mecánica','Entretien & réparations','Maintenance & repairs','Mantenimiento y reparaciones'],
    ['driving','Pilotage','Driving','Pilotaje','Trajectoire & maîtrise','Lines & car control','Trazada y control'],
    ['simracing','Sim racing','Sim racing','Sim racing','Réglages & pratique','Setup & practice','Ajustes y práctica'],
    ['engineering','Ingénierie','Engineering','Ingeniería','Data & technique','Data & technology','Datos y técnica'],
    ['media','Photo & vidéo','Photo & video','Foto y vídeo','Raconter la course','Tell the racing story','Contar la carrera'],
    ['business','Business','Business','Negocio','Sponsoring & projets','Sponsorship & projects','Patrocinio y proyectos'],
    ['career','Métiers','Careers','Profesiones','Trouver sa voie','Find your path','Encuentra tu camino'],
    ['fitness','Préparation','Preparation','Preparación','Le pilote aussi progresse','Build driver readiness','Preparación del piloto']
  ];
  document.body.insertAdjacentHTML('beforeend', '<dialog id="navigation-dialog" class="navigation-dialog" aria-labelledby="navigation-title"></dialog>');
  const dialog = $('#navigation-dialog');
  const triggers = [...document.querySelectorAll('[data-open-navigation]')];
  function hydrate() {
    document.querySelectorAll('[data-icon]').forEach(el => {el.innerHTML = icon(el.dataset.icon);});
  }
  function update() {
    const labels = {
      browse: t('Explorer','Explore','Explorar'), library: t('Bibliothèque','Library','Biblioteca'),
      search: t('Rechercher','Search','Buscar'), menu: t('Menu','Menu','Menú'),
      heroEyebrow: t('APPRENDRE. COMPRENDRE. PRATIQUER.','LEARN. UNDERSTAND. PRACTISE.','APRENDE. COMPRENDE. PRACTICA.'),
      heroCaption: t('Le savoir prend le volant.','Knowledge takes the wheel.','El saber toma el volante.'),
      heroAction: t('Entrer dans l’atelier','Enter the workshop','Entrar en el taller'),
      heroNote: t('MÉCANIQUE · PILOTAGE · SIM RACING','MECHANICS · DRIVING · SIM RACING','MECÁNICA · PILOTAJE · SIM RACING')
    };
    document.querySelectorAll('[data-identity-text]').forEach(el => {el.textContent = labels[el.dataset.identityText] || '';});
    $('.academy-scene')?.setAttribute('aria-label',t('Explorer la mécanique','Explore mechanics','Explorar la mecánica'));
    triggers.forEach(el => el.setAttribute('aria-label',t('Explorer tous les sujets','Explore all topics','Explorar todos los temas')));
    dialog.innerHTML = `<header class="navigation-heading"><div><p class="eyebrow">RACELINK / ACADEMY</p><h2 id="navigation-title">${t('Votre prochaine découverte.','Your next discovery.','Tu próximo descubrimiento.')}</h2></div><button type="button" class="icon-button" data-close-navigation aria-label="${t('Fermer le menu','Close menu','Cerrar el menú')}">${icon('close')}</button></header>
      <div class="navigation-body"><div class="navigation-categories"><p class="menu-label">${t('EXPLORER PAR SUJET','EXPLORE BY TOPIC','EXPLORAR POR TEMA')}</p><nav aria-label="${t('Sujets de la bibliothèque','Library topics','Temas de la biblioteca')}">${categories.map(([id,fr,en,es,df,de,ds])=>`<button type="button" class="menu-topic" data-entry-category="${id}"><span class="menu-topic-icon">${icon(categoryIcon[id])}</span><span><strong>${t(fr,en,es)}</strong><small>${t(df,de,ds)}</small></span>${icon('arrow-up-right',{size:18,className:'menu-arrow'})}</button>`).join('')}</nav></div>
      <aside class="navigation-shortcuts"><p class="menu-label">${t('À VOTRE RYTHME','AT YOUR PACE','A TU RITMO')}</p><button data-browse-all>${icon('library')}<span>${t('Tous les tutoriels','All tutorials','Todos los tutoriales')}</span>${icon('arrow-right',{size:18})}</button><button data-view="paths">${icon('route')}<span>${t('Parcours guidés','Learning paths','Itinerarios guiados')}</span>${icon('arrow-right',{size:18})}</button><button data-view="saved">${icon('bookmark')}<span>${t('Ma sélection','My collection','Mi selección')}</span>${icon('arrow-right',{size:18})}</button><button data-view="faq">${icon('help')}<span>${t('Aide & questions','Help & questions','Ayuda y preguntas')}</span>${icon('arrow-right',{size:18})}</button><p class="menu-note">${t('Une question précise ? Cherchez un geste, un modèle de voiture ou une référence.','A specific question? Search for a task, a car model or a specification.','¿Una pregunta concreta? Busca una tarea, un modelo o una referencia.')}</p><button class="menu-search" data-open-search>${icon('search')}<span>${t('Lancer une recherche','Start a search','Iniciar una búsqueda')}</span></button></aside></div>`;
    hydrate();sync();
  }
  function sync() {
    const view = getView(), results = view === 'explore' && isBrowsing();
    document.querySelectorAll('.desktop-nav [data-view="explore"],.mobile-nav [data-view="explore"]').forEach(el=>{
      el.classList.toggle('active',view==='explore'&&!results);
      if(view==='explore'&&!results)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-library-nav],.mobile-nav [data-open-search]').forEach(el=>{
      el.classList.toggle('active',results);
      if(results)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');
    });
  }
  triggers.forEach(el=>el.addEventListener('click',()=>{
    update();document.dispatchEvent(new Event('rl:close-suggestions'));
    dialog.showModal();document.body.classList.add('navigation-open');
    triggers.forEach(button=>button.setAttribute('aria-expanded','true'));
  }));
  dialog.addEventListener('close',()=>{document.body.classList.remove('navigation-open');triggers.forEach(el=>el.setAttribute('aria-expanded','false'));});
  dialog.addEventListener('click',event=>{
    if(event.target.closest('[data-close-navigation]'))dialog.close();
    if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}
  });
  document.addEventListener('click',event=>{
    const action=event.target.closest('[data-open-search],[data-entry-category],[data-browse-all],[data-view]');
    if(!action)return;
    const fromMenu=dialog.contains(action);
    if(fromMenu)dialog.close();
    if(action.hasAttribute('data-open-search'))openSearch();
    requestAnimationFrame(()=>{
      sync();
      if(fromMenu&&(action.hasAttribute('data-entry-category')||action.hasAttribute('data-browse-all'))){
        const heading=$('#catalog-heading');heading.tabIndex=-1;heading.focus({preventScroll:true});
      }
    });
  },true);
  update();
  return {update,sync};
}
