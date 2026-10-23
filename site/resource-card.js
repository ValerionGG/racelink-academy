// A preview explains the available resource without claiming it was watched.
export function resourceCard(video,c){
  const {escape:e,t,glyph,safeUrl,catName,platformName,languageLabel,estimatedLanguage,fmtDuration}=c;
  const id=e(video.id),image=safeUrl(video.thumbnail_url,true);
  const author=typeof video.creator==='string'?video.creator.trim():'';
  const raw=String(video.description||'').replace(/https?:\/\/\S+/g,'').replace(/#[\p{L}\p{N}_]+/gu,'').replace(/\s+/g,' ').trim();
  const description=raw.length>220?raw.slice(0,217).replace(/\s+\S*$/,'')+'…':raw;
  const sourceLabel=['editorial_summary','existing_editorial_description'].includes(video.description_type)?t('Aperçu éditorial','Editorial overview','Resumen editorial'):t('Dans le descriptif','From the description','En la descripción');
  const transcript=video.has_transcript?t('Transcription disponible','Transcript available','Transcripción disponible'):video.source_captions_available?t('Sous-titres signalés à la source','Captions reported at source','Subtítulos indicados en la fuente'):t('Consulter chez l’auteur','Available from the creator','Consultar al autor');
  return `<article class="video-card resource-card">
    <button class="thumbnail resource-photo" data-video="${id}" aria-label="${e(t('Ouvrir : ','Open: ','Abrir: ')+video.title)}">${image?`<img src="${e(image)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">`:`<span class="thumb-fallback">${e(platformName(video.platform))}<small>${t('Aperçu non fourni par la source','No preview supplied by the source','Vista previa no disponible en la fuente')}</small></span>`}<span class="resource-photo-action">${t('Découvrir le contenu','Preview this resource','Descubrir el contenido')} <span aria-hidden="true">↗</span></span>${video.duration_seconds?`<span class="thumb-duration">${e(fmtDuration(video.duration_seconds))}</span>`:''}</button>
    <div class="resource-card-body"><div class="resource-kicker"><span>${e(catName(video.category))}</span><span>${e(languageLabel(video.language))}${estimatedLanguage(video)?t(' · estimé',' · estimated',' · estimado'):''}</span></div>
    <div class="card-heading"><h3 dir="auto"><button class="title-button" data-video="${id}">${e(video.title)}</button></h3><button class="save-card ${c.isSaved?'saved':''}" data-save="${id}" aria-label="${e(c.isSaved?t('Retirer de ma sélection','Remove from collection','Quitar de mi selección'):t('Enregistrer la vidéo','Save video','Guardar vídeo'))}" aria-pressed="${c.isSaved}">${glyph('bookmark',{size:20})}</button></div>
    ${description?`<div class="resource-summary"><span>${sourceLabel}</span><p dir="auto">${e(description)}</p></div>`:''}
    ${c.automotiveMarkup||''}<div class="resource-source"><span class="resource-platform">${e(platformName(video.platform))}</span><span dir="auto">${e(author||t('Auteur non renseigné','Creator not specified','Autor no indicado'))}</span></div>
    ${c.badge||''}<div class="resource-card-footer"><small>${transcript}</small><button data-video="${id}">${t('Voir la fiche','View details','Ver ficha')} <span aria-hidden="true">→</span></button></div></div></article>`;
}
