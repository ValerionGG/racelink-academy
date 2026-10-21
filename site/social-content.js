// Presentation only: original source text never becomes executable markup.
export function socialContentMarkup(video, {escape, t}) {
  const hashtags = Array.isArray(video.hashtags) ? video.hashtags.filter(x => typeof x === 'string') : [];
  const original = typeof video.source_title === 'string' ? video.source_title : '';
  const caption = typeof video.source_caption === 'string' ? video.source_caption : '';
  const revised = video.title_basis === 'editorial_rewrite';
  const tags = hashtags.length ? `<section class="social-hashtags" aria-label="${t('Hashtags de la source','Source hashtags','Hashtags de la fuente')}"><h3>${t('Hashtags de la source','Source hashtags','Hashtags de la fuente')}</h3><div class="hashtag-list">${hashtags.map(tag=>`<span dir="auto">${escape(tag)}</span>`).join('')}</div></section>` : '';
  const source = original || caption ? `<details class="social-source"><summary>${t('Voir le texte d’origine','View original text','Ver texto original')}</summary>${revised?`<p class="small-note">${t('Le titre a été reformulé pour faciliter la lecture, à partir des informations de la source.','The title was rewritten for readability using source information.','El título se reformuló para facilitar la lectura con información de la fuente.')}</p>`:''}${original?`<h4>${t('Titre avant mise en forme','Title before formatting','Título antes del formato')}</h4><p dir="auto">${escape(original)}</p>`:''}${caption&&caption!==original?`<h4>${t('Légende source','Source caption','Texto de la fuente')}</h4><p dir="auto">${escape(caption)}</p>`:''}</details>` : '';
  return tags + source;
}
