// A photograph, one opening action, and the source. Evidence lives in the reader.
// Pure rendering: no request, storage, or mutation of the source record.
import {sourceLabel} from './source-label.js?v=discovery-v34';
import {poster,levelBadge} from './paddock-home.js?v=themes-v48';
export function resourceCard(video,c){
  const {escape:e,t,glyph,safeUrl,platformName,languageLabel,estimatedLanguage,fmtDuration}=c;
  const id=e(video.id),image=safeUrl(video.thumbnail_url,true);
  const title=typeof video.title==='string'&&video.title.trim()?video.title:t('Ressource vidéo','Video resource','Recurso de vídeo');
  const author=(typeof video.creator==='string'?video.creator.trim():'')||t('Auteur non renseigné','Creator not specified','Autor no indicado');
  const language=languageLabel(video.language)+(estimatedLanguage(video)?t(' · estimé',' · estimated',' · estimado'):'');
  const saved=Boolean(c.isSaved);
  const duration=Number(video.duration_seconds)>0?fmtDuration(video.duration_seconds):'';
  const source=sourceLabel(video,platformName);
  const art=poster({id:video.id,t:title,s:video.automotive?.tasks||[],c:video.category});
  const car=video.automotive?.vehicles?.find(v=>v?.model),carLabel=car?[car.model,car.generation].filter(Boolean).join(' '):'';
  return `<article class="video-card resource-card">
    <h3 class="resource-card-heading"><button type="button" class="resource-card-open" data-video="${id}" aria-label="${e(t('Ouvrir : ','Open: ','Abrir: ')+title)}">
      <span class="thumbnail resource-photo" style="background-image:url('${art}')">${image?`<img src="${e(image)}" alt="" width="640" height="360" loading="lazy" decoding="async" referrerpolicy="no-referrer">`:''}<span class="pd-card-play" aria-hidden="true"><svg viewBox="0 0 10 12"><path d="M0 0l10 6-10 6z"/></svg></span><span class="pd-card-tags"><span class="pd-card-plat">${e(source)}</span>${levelBadge(video,t)}</span><span class="pd-card-progress" aria-hidden="true"></span><span class="resource-format" aria-hidden="true">${e(t('Vidéo','Video','Vídeo'))}</span>${duration?`<span class="thumb-duration">${e(duration)}</span>`:''}</span>
      <span class="resource-card-title" dir="auto">${e(title)}</span>
    </button></h3>
    <p class="resource-card-source">${carLabel?`<span class="pd-tag" dir="auto">${e(carLabel)}</span>`:''}<span class="resource-card-creator" dir="auto" title="${e(author)}">${e(author)}</span><span class="resource-card-platform">${e(source)}</span><span class="resource-card-language">${e(language)}</span></p>
    <button type="button" class="save-card${saved?' saved':''}" data-save="${id}" aria-label="${e(saved?t('Retirer de ma sélection','Remove from collection','Quitar de mi selección'):t('Enregistrer la vidéo','Save video','Guardar vídeo'))}" aria-pressed="${saved}">${glyph('bookmark',{size:20})}</button>
  </article>`;
}
