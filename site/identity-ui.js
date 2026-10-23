import {icon, categoryIcon} from './icons.js';

// Navigation is a native dialog: focus containment, Escape and focus return
// remain provided by the browser. Links reuse the existing catalog actions.
export function createIdentityUI({t, openSearch, getView, isBrowsing, getState = () => ({})}) {
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
      heroEyebrow: t('À portée de main','Within reach','A tu alcance'),
      heroCaption: t('Comprendre votre voiture.','Understand your car.','Comprende tu coche.'),
      heroAction: t('Explorer la mécanique','Explore mechanics','Explorar la mecánica'),
      heroNote: t('MÉCANIQUE · PILOTAGE · SIM RACING','MECHANICS · DRIVING · SIM RACING','MECÁNICA · PILOTAJE · SIM RACING')
    };
    const productLabels = {
      context: t('Votre espace pour apprendre','Your learning space','Tu espacio para aprender'),
      search: labels.search,
      topics: t('Vos sujets','Your topics','Tus temas'),
      mechanics: t('Mécanique','Mechanics','Mecánica'),
      driving: t('Pilotage','Driving','Pilotaje'),
      allTopics: t('Tous les sujets','All topics','Todos los temas'),
      myCar: t('Mon véhicule','My vehicle','Mi vehículo'),
      carHint: t('Des tutos plus précis','More relevant tutorials','Tutoriales más precisos'),
      greeting: t('LA PASSION S’APPREND.','PASSION IS SOMETHING YOU LEARN.','LA PASIÓN SE APRENDE.')
    };
    document.querySelectorAll('[data-identity-text]').forEach(el => {el.textContent = labels[el.dataset.identityText] || '';});
    document.querySelectorAll('[data-product-text]').forEach(el => {
      if(productLabels[el.dataset.productText]!==undefined)el.textContent=productLabels[el.dataset.productText];
    });
    // The main hero question and introduction remain owned by app translations.
    $('.app-sidebar')?.setAttribute('aria-label',t('Espace d’apprentissage','Learning space','Espacio de aprendizaje'));
    $('.desktop-nav')?.setAttribute('aria-label',t('Navigation principale','Main navigation','Navegación principal'));
    $('.header-search')?.setAttribute('aria-label',labels.search);
    $('.sidebar-section nav')?.setAttribute('aria-label',t('Sujets','Topics','Temas'));
    $('.mobile-nav')?.setAttribute('aria-label',t('Navigation mobile','Mobile navigation','Navegación móvil'));
    $('.academy-scene')?.setAttribute('aria-label',t('Explorer la mécanique','Explore mechanics','Explorar la mecánica'));
    triggers.forEach(el => el.setAttribute('aria-label',t('Explorer tous les sujets','Explore all topics','Explorar todos los temas')));
    dialog.innerHTML = `<header class="navigation-heading"><div><p class="eyebrow">RACELINK / ACADEMY</p><h2 id="navigation-title">${t('Votre prochaine découverte.','Your next discovery.','Tu próximo descubrimiento.')}</h2></div><button type="button" class="icon-button" data-close-navigation aria-label="${t('Fermer le menu','Close menu','Cerrar el menú')}">${icon('close')}</button></header>
      <div class="navigation-body"><div class="navigation-categories"><p class="menu-label">${t('EXPLORER PAR SUJET','EXPLORE BY TOPIC','EXPLORAR POR TEMA')}</p><nav aria-label="${t('Sujets de la bibliothèque','Library topics','Temas de la biblioteca')}">${categories.map(([id,fr,en,es,df,de,ds])=>`<button type="button" class="menu-topic" data-entry-category="${id}"><span class="menu-topic-icon">${icon(categoryIcon[id])}</span><span><strong>${t(fr,en,es)}</strong><small>${t(df,de,ds)}</small></span>${icon('arrow-up-right',{size:18,className:'menu-arrow'})}</button>`).join('')}</nav></div>
      <aside class="navigation-shortcuts"><p class="menu-label">${t('À VOTRE RYTHME','AT YOUR PACE','A TU RITMO')}</p><button data-browse-all>${icon('library')}<span>${t('Tous les tutoriels','All tutorials','Todos los tutoriales')}</span>${icon('arrow-right',{size:18})}</button><button data-view="paths">${icon('route')}<span>${t('Parcours guidés','Learning paths','Itinerarios guiados')}</span>${icon('arrow-right',{size:18})}</button><button data-view="saved">${icon('bookmark')}<span>${t('Ma sélection','My collection','Mi selección')}</span>${icon('arrow-right',{size:18})}</button><button data-view="faq">${icon('help')}<span>${t('Aide & questions','Help & questions','Ayuda y preguntas')}</span>${icon('arrow-right',{size:18})}</button><p class="menu-note">${t('Une question précise ? Cherchez un geste, un modèle de voiture ou une référence.','A specific question? Search for a task, a car model or a specification.','¿Una pregunta concreta? Busca una tarea, un modelo o una referencia.')}</p><button class="menu-search" data-open-search>${icon('search')}<span>${t('Lancer une recherche','Start a search','Iniciar una búsqueda')}</span></button></aside></div>`;
    hydrate();sync();
  }
  function sync() {
    const view = getView(), results = view === 'explore' && isBrowsing(), category = getState().category;
    function markCurrent(el, active, value = 'page') {
      el.classList.toggle('active', active);
      if(active)el.setAttribute('aria-current',value);else el.removeAttribute('aria-current');
    }
    // View links can live in the sidebar, header, mobile bar or topic dialog.
    // Home and the filtered library share a view, but are distinct destinations.
    document.querySelectorAll('[data-view]').forEach(el=>{
      markCurrent(el,el.dataset.view===view&&(view!=='explore'||!results));
    });
    document.querySelectorAll('[data-library-nav],[data-browse-all],.mobile-nav [data-open-search]').forEach(el=>{
      markCurrent(el,results);
    });
    document.querySelectorAll('[data-entry-category]').forEach(el=>{
      markCurrent(el,results&&el.dataset.entryCategory===category,'true');
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
    const action=event.target.closest('[data-open-search],[data-open-vehicle],[data-entry-category],[data-browse-all],[data-view]');
    if(!action)return;
    const fromMenu=dialog.contains(action);
    if(fromMenu)dialog.close();
    if(action.hasAttribute('data-open-search'))openSearch();
    if(action.hasAttribute('data-open-vehicle'))document.dispatchEvent(new Event('rl:open-vehicle'));
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
