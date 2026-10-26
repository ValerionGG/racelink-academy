// The same search and filter controls are reused in native mobile dialogs.
export function createMobileUI({t,getState,getTotal,isLoading,onExplore,filterStudio}) {
  const $=s=>document.querySelector(s);
  const mobile=matchMedia('(max-width:760px)');
  const shell=$('.search-shell'),filters=$('#filters');
  const searchAnchor=document.createComment('search home'),filterAnchor=document.createComment('filters home');
  shell.before(searchAnchor);filters.before(filterAnchor);
  document.body.insertAdjacentHTML('beforeend',`
    <dialog id="search-dialog" class="search-dialog" aria-labelledby="mobile-search-title">
      <header class="sheet-heading"><div><span class="eyebrow">RACELINK ACADEMY</span><h2 id="mobile-search-title"></h2></div><button type="button" data-sheet-close="search" aria-label="Fermer">×</button></header>
      <div class="mobile-search-body"></div><p class="mobile-search-help"></p>
    </dialog>
    <dialog id="filters-dialog" class="filters-dialog" aria-labelledby="mobile-filter-title">
      <header class="sheet-heading"><h2 id="mobile-filter-title"></h2><button type="button" data-sheet-close="filters" aria-label="Fermer">×</button></header>
      <div class="mobile-filter-body"></div>
      <footer class="sheet-footer"><button type="button" id="mobile-vehicle"></button><button type="button" id="show-filter-results"></button></footer>
    </dialog>`);
  const searchDialog=$('#search-dialog'),filterDialog=$('#filters-dialog'),resourceDialog=$('#video-dialog');
  let filterFocus=null,suppressSearchFocus=false;
  function lock(){document.body.classList.toggle('sheet-open',searchDialog.open||filterDialog.open);}
  function focusAfterSearch(){
    if(resourceDialog?.open||filterDialog.open)return;
    const results=document.body.classList.contains('results-mode');
    const target=results?(mobile.matches?$('#edit-search'):$('#catalog-heading')):$('.hero h1');
    if(!target)return;
    if(target!==$('#edit-search'))target.tabIndex=-1;
    target.focus({preventScroll:true});
  }
  function closeSearch(){
    if(!searchDialog.open)return;
    // Native dialog focus restoration runs before its queued close event. Move
    // focus now, so a guide opened immediately afterwards never remembers the
    // search input as its return target.
    suppressSearchFocus=true;$('#search').blur();searchDialog.close();
    restoreSearch();focusAfterSearch();
  }
  function openSearch(){
    if(resourceDialog?.open||filterDialog.open)return;
    const input=$('#search');
    const draft={value:input.value,start:input.selectionStart,end:input.selectionEnd,direction:input.selectionDirection};
    suppressSearchFocus=false;
    // Opening search is navigation, not a new query: preserve draft text and
    // selection even if the view callback synchronizes committed filter state.
    onExplore();
    input.value=draft.value;
    restoreSearch();
    if(mobile.matches){
      if(!searchDialog.open){$('.mobile-search-body').append(shell);searchDialog.showModal();lock();}
    }else{input.scrollIntoView({block:'center',behavior:'smooth'});}
    input.focus({preventScroll:true});
    if(draft.start!==null&&draft.end!==null)input.setSelectionRange(draft.start,draft.end,draft.direction||'none');
  }
  function openFilters(){
    if(filterDialog.open)return;
    if(mobile.matches)filterStudio?.beginDraft();
    $('.mobile-filter-body').append(filters);
    filterDialog.showModal();$('#mobile-filters').setAttribute('aria-expanded','true');lock();update();
  }
  function restoreSearch(){if(!searchDialog.open){const slot=!mobile.matches&&document.body.classList.contains('results-mode')?$('#results-search-desktop'):null;if(slot){if(shell.parentElement!==slot)slot.append(shell);}else if(searchAnchor.nextSibling!==shell)searchAnchor.after(shell);}}
  function update(){
    restoreSearch();
    filterStudio?.update();
    const state=getState(),total=getTotal();
    $('#mobile-search-title').textContent=t('Rechercher un tuto','Find a tutorial','Buscar un tutorial');
    $('#mobile-filter-title').textContent=t('Affiner les résultats','Refine results','Afinar resultados');
    $('.mobile-search-help').textContent=t('Essayez « vidange Clio 3 », « huile 5W-30 » ou « freinage dégressif ». Ajoutez votre modèle pour préciser les résultats.','Try “oil change Clio 3”, “oil 5W-30” or “trail braking”. Add your model to refine the results.','Prueba « cambio aceite Clio 3 », « aceite 5W-30 » o « trail braking ». Añade tu modelo para afinar los resultados.');
    $('#edit-search-label').textContent=state.q||t('Rechercher un tuto, une question…','Search a tutorial, a question…','Busca un tutorial, una pregunta…');
    const number=Object.entries(state).filter(([k,v])=>v&&!['q','page','sort','format','language','make','model','generation','engine','year','fuel_type','body_type'].includes(k)).length;
    $('#mobile-filters').innerHTML=`${t('Filtres','Filters','Filtros')}${number?` <b>${number}</b>`:''}`;
    $('#mobile-vehicle').textContent=t('Préciser ma voiture ↗','Specify my car ↗','Precisar mi coche ↗');
    $('#show-filter-results').textContent=total===null?(isLoading()?t('Recherche en cours…','Searching…','Buscando…'):t('Catalogue indisponible','Catalog unavailable','Catálogo no disponible')):`${t('Voir','Show','Ver')} ${Number(total).toLocaleString(document.documentElement.lang)} ${total===1?t('résultat','result','resultado'):t('résultats','results','resultados')} →`;
    $('#show-filter-results').disabled=total===null;
    if(filterStudio?.hasPendingChanges()){
      $('#show-filter-results').textContent=t('Appliquer les filtres','Apply filters','Aplicar filtros');
      $('#show-filter-results').disabled=false;
      $('#mobile-vehicle').textContent=t('Appliquer et préciser ma voiture ↗','Apply and specify my car ↗','Aplicar y precisar mi coche ↗');
    }
    document.querySelectorAll('[data-sheet-close]').forEach(b=>b.setAttribute('aria-label',t('Fermer','Close','Cerrar')));
  }
  $('#edit-search').addEventListener('click',openSearch);
  $('#search').addEventListener('focus',()=>{if(mobile.matches&&!suppressSearchFocus&&!resourceDialog?.open&&!filterDialog.open&&!searchDialog.open&&!searchDialog.contains($('#search')))openSearch();});
  $('#mobile-filters').addEventListener('click',openFilters);
  searchDialog.addEventListener('cancel',()=>{suppressSearchFocus=true;});
  searchDialog.addEventListener('close',()=>{
    // A new explicit open may precede an older queued close event.
    if(searchDialog.open)return;
    suppressSearchFocus=true;$('#search').blur();restoreSearch();lock();
    focusAfterSearch();
    // Keep the guard for the entire handoff: closing the resource can restore
    // browser focus before its own close listener has had a chance to run.
    if(!resourceDialog?.open)suppressSearchFocus=false;
    document.dispatchEvent(new Event('rl:close-suggestions'));
  });
  resourceDialog?.addEventListener('close',()=>{
    if(resourceDialog.open||!suppressSearchFocus)return;
    restoreSearch();focusAfterSearch();suppressSearchFocus=false;
  });
  filterDialog.addEventListener('close',()=>{if(filterDialog.open)return;filterStudio?.cancelDraft();filterAnchor.after(filters);$('#mobile-filters').setAttribute('aria-expanded','false');lock();(filterFocus||$('#mobile-filters')).focus({preventScroll:true});filterFocus=null;});
  document.querySelectorAll('[data-sheet-close]').forEach(b=>b.addEventListener('click',()=>b.dataset.sheetClose==='search'?closeSearch():filterDialog.close()));
  $('#show-filter-results').addEventListener('click',()=>{filterStudio?.applyDraft();filterFocus=$('#catalog-heading');filterFocus.tabIndex=-1;filterDialog.close();$('#catalog-heading').scrollIntoView({behavior:'smooth'});});
  $('#mobile-vehicle').addEventListener('click',()=>{filterStudio?.applyDraft();filterFocus=$('#vehicle-make');$('#vehicle-disclosure').open=true;filterDialog.close();$('#vehicle-disclosure').scrollIntoView({behavior:'smooth'});});
  document.addEventListener('rl:search-chosen',closeSearch);
  for(const dialog of [searchDialog,filterDialog])dialog.addEventListener('click',event=>{
    if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom){if(dialog===searchDialog)closeSearch();else dialog.close();}}
  });
  mobile.addEventListener('change',()=>{if(!mobile.matches){closeSearch();}restoreSearch();});
  return {update,openSearch,closeSearch,openFilters};
}
