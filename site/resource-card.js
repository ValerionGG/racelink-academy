// A photograph, one opening action, and the source. Evidence lives in the reader.
// Pure rendering: no request, storage, or mutation of the source record.
import {sourceLabel} from './source-label.js?v=discovery-v34';
export function resourceCard(video,c){
  const {escape:e,t,glyph,safeUrl,platformName,languageLabel,estimatedLanguage,fmtDuration}=c;
  const id=e(video.id),image=safeUrl(video.thumbnail_url,true);
  const title=typeof video.title==='string'&&video.title.trim()?video.title:t('Ressource vidéo','Video resource','Recurso de vídeo');
  const author=(typeof video.creator==='string'?video.creator.trim():'')||t('Auteur non renseigné','Creator not specified','Autor no indicado');
  const language=languageLabel(video.language)+(estimatedLanguage(video)?t(' · estimé',' · estimated',' · estimado'):'');
  const saved=Boolean(c.isSaved);
  const duration=Number(video.duration_seconds)>0?fmtDuration(video.duration_seconds):'';
  const source=sourceLabel(video,platformName);
  return `<article class="video-card resource-card">
    <h3 class="resource-card-heading"><button type="button" class="resource-card-open" data-video="${id}" aria-label="${e(t('Ouvrir : ','Open: ','Abrir: ')+title)}">
      <span class="thumbnail resource-photo">${image?`<img src="${e(image)}" alt="" width="640" height="360" loading="lazy" decoding="async" referrerpolicy="no-referrer">`:`<span class="thumb-fallback">${e(source)}<small>${e(t('Aperçu non fourni par la source','No preview supplied by the source','Vista previa no disponible en la fuente'))}</small></span>`}<span class="resource-format" aria-hidden="true">${e(t('Vidéo','Video','Vídeo'))}</span>${duration?`<span class="thumb-duration">${e(duration)}</span>`:''}</span>
      <span class="resource-card-title" dir="auto">${e(title)}</span>
    </button></h3>
    <p class="resource-card-source"><span class="resource-card-creator" dir="auto" title="${e(author)}">${e(author)}</span><span class="resource-card-platform">${e(source)}</span><span class="resource-card-language">${e(language)}</span></p>
    <button type="button" class="save-card${saved?' saved':''}" data-save="${id}" aria-label="${e(saved?t('Retirer de ma sélection','Remove from collection','Quitar de mi selección'):t('Enregistrer la vidéo','Save video','Guardar vídeo'))}" aria-pressed="${saved}">${glyph('bookmark',{size:20})}</button>
  </article>`;
}
