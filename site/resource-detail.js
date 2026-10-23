/**
 * Video reading workspace. Pure markup: the application retains player, tab,
 * save, share, close and transcript handlers. No request, storage or DOM mutation.
 * Only socialMarkup/automotiveMarkup may return trusted application markup;
 * every value read from the resource itself is escaped here.
 */
const text = value => typeof value === 'string' ? value : '';

function context(helpers) {
  const {escape: e, t, safeUrl} = helpers;
  if (typeof e !== 'function' || typeof t !== 'function' || typeof safeUrl !== 'function') {
    throw new TypeError('resource-detail requires escape, t and safeUrl helpers');
  }
  return {
    ...helpers, e, t, safeUrl,
    catName: helpers.catName || (value => value || t('Non précisé','Not specified','Sin especificar')),
    levelName: helpers.levelName || (value => value),
    langName: helpers.langName || (value => value && value !== 'und' ? value : t('Non confirmée','Unconfirmed','Sin confirmar')),
    licenseName: helpers.licenseName || (() => t('Non confirmée','Unconfirmed','Sin confirmar')),
    platformName: helpers.platformName || (value => value || t('la source','the source','la fuente')),
    fmtDuration: helpers.fmtDuration || (() => t('Durée inconnue','Duration unknown','Duración desconocida')),
    estimatedLanguage: helpers.estimatedLanguage || (() => false),
  };
}

/** All existing detail IDs and data actions are preserved exactly once. */
export function renderResourceDetail(resource, helpers) {
  const c = context(helpers), {e, t} = c;
  const source = c.safeUrl(resource.url);
  const image = c.safeUrl(resource.thumbnail_url || resource.thumbnailUrl, true);
  const canEmbed = Boolean(source && c.embedUrl?.(resource));
  const isSaved = Boolean(c.isSaved);
  const platform = c.platformName(resource.platform) || t('la source','the source','la fuente');
  const author = text(resource.creator).trim() || t('Auteur non renseigné','Creator not provided','Autor no indicado');
  const language = c.langName(resource.language);
  const estimated = c.estimatedLanguage(resource);
  const levelUnknown = !resource.level || ['all','unknown'].includes(resource.level) || String(resource.level_status).includes('unknown');
  const level = levelUnknown ? t('Non confirmé','Unconfirmed','Sin confirmar') : c.levelName(resource.level);
  const transcriptText = typeof resource.transcript === 'string' ? resource.transcript : resource.transcript?.text || resource.transcript?.content;
  const hasTranscript = Boolean(resource.has_transcript && text(transcriptText).trim());
  const watch = t(`Regarder sur ${platform}`,`Watch on ${platform}`,`Ver en ${platform}`);
  const sourceLink = (label, className = '') => source
    ? `<a class="${className}" href="${e(source)}" target="_blank" rel="noopener noreferrer">${e(label)} <span aria-hidden="true">↗</span></a>` : '';
  const tabs = [
    ['about',t('Contenu','Overview','Contenido')],
    ['transcript',t('Transcription','Transcript','Transcripción')],
    ['notes',t('Mes notes','My notes','Mis notas')],
  ];
  return `<article class="resource-workspace" data-resource-kind="video">
    <header class="detail-header resource-toolbar">
      <span class="resource-location">${e(t('La bibliothèque','The library','La biblioteca'))}<span aria-hidden="true"> / </span>${e(c.catName(resource.category))}</span>
      <button type="button" data-close aria-label="${e(t('Fermer la fiche','Close resource','Cerrar ficha'))}"><span aria-hidden="true">×</span></button>
    </header>
    <header class="resource-heading">
      <p class="resource-kind">${e(t('Vidéo','Video','Vídeo'))}<span aria-hidden="true"> · </span>${e(platform)}</p>
      <h2 id="dialog-title" dir="auto">${e(text(resource.title) || t('Ressource vidéo','Video resource','Recurso de vídeo'))}</h2>
      <div class="resource-byline"><p dir="auto">${e(author)}</p><div class="detail-actions resource-utilities">
        <button type="button" data-save="${e(resource.id)}" class="${isSaved?'saved':''}" aria-pressed="${isSaved}" aria-label="${e(isSaved?t('Retirer de ma sélection','Remove from collection','Quitar de mi selección'):t('Enregistrer la vidéo','Save video','Guardar vídeo'))}">${e(isSaved?t('Enregistré ✓','Saved ✓','Guardado ✓'):t('Enregistrer','Save','Guardar'))}</button>
        <button type="button" data-share${source?'':' disabled'}>${e(t('Copier le lien','Copy link','Copiar enlace'))}</button>
      </div></div>
    </header>
    <div class="resource-body">
      <section class="resource-media" aria-label="${e(t('Vidéo et repères','Video and key details','Vídeo y datos principales'))}">
        <div class="player resource-player" id="player">
          <div class="resource-preview"><div class="resource-preview-empty"><span>${e(platform)}</span><p>${e(t('Aperçu indisponible','Preview unavailable','Vista previa no disponible'))}</p></div>${image?`<img src="${e(image)}" alt="" width="960" height="540" decoding="async" referrerpolicy="no-referrer">`:''}</div>
          <div class="player-prompt resource-watch">
            <div class="resource-watch-actions">${canEmbed?`<button type="button" data-play class="resource-watch-primary"><span aria-hidden="true">▶</span> ${e(t('Regarder ici','Watch here','Ver aquí'))}</button>${sourceLink(t(`Sur ${platform}`,`On ${platform}`,`En ${platform}`),'resource-watch-source')}`:sourceLink(watch,'resource-watch-primary')}${!source?`<p>${e(t('Lien source indisponible','Source link unavailable','Enlace de origen no disponible'))}</p>`:''}</div>
            ${source?`<p class="resource-playback-note">${e(canEmbed?t('Le lecteur externe se charge à votre demande et peut utiliser des cookies.','The external player loads when you choose and may use cookies.','El reproductor externo se carga cuando lo eliges y puede utilizar cookies.'):t('La vidéo s’ouvre chez son auteur, dans un nouvel onglet.','The video opens at its source in a new tab.','El vídeo se abre en su fuente, en una pestaña nueva.'))}</p>`:''}
          </div>
        </div>
        <dl class="resource-facts">
          <div><dt>${e(t('Durée','Duration','Duración'))}</dt><dd>${e(c.fmtDuration(resource.duration_seconds))}</dd></div>
          <div><dt>${e(t('Langue','Language','Idioma'))}</dt><dd>${e(language)}${estimated?`<span class="resource-estimate">${e(t('estimée','estimated','estimado'))}</span>`:''}</dd></div>
          <div><dt>${e(t('Niveau indicatif','Estimated level','Nivel estimado'))}</dt><dd>${e(level)}</dd></div>
        </dl>
        <p class="resource-transcript-state">${e(hasTranscript?t('Une transcription est disponible dans cette fiche.','A transcript is available in this resource.','Esta ficha incluye una transcripción.'):t('Aucune transcription enregistrée ici. Les sous-titres peuvent être disponibles à la source.','No transcript is stored here. Captions may be available at the source.','No hay una transcripción guardada aquí. La fuente puede ofrecer subtítulos.'))}</p>
        <div id="detail-racelink-pick" class="detail-racelink-pick resource-pick" hidden></div>
      </section>
      <section class="detail-side resource-reading" aria-label="${e(t('Lire et retenir','Read and learn','Leer y aprender'))}">
        <div class="detail-tabs resource-tabs" role="tablist" aria-label="${e(t('Contenu de la fiche','Resource contents','Contenido de la ficha'))}">${tabs.map(([key,label],i)=>`<button type="button" role="tab" id="tab-${key}" data-tab="${key}" aria-controls="detail-panel" aria-selected="${i===0}" tabindex="${i===0?'0':'-1'}"${i===0?' class="active"':''}>${e(label)}</button>`).join('')}</div>
        <div class="detail-panel resource-panel" id="detail-panel" role="tabpanel" aria-labelledby="tab-about" tabindex="0">${renderResourceOverview(resource, helpers)}</div>
      </section>
    </div>
  </article>`;
}

/** Use for the existing setDetailTab('about') branch; other tab handlers stay intact. */
export function renderResourceOverview(resource, helpers) {
  const c = context(helpers), {e,t} = c;
  const transcriptBased = (resource.summary_basis || resource.summaryBasis) === 'authorized_transcript';
  const reviewed = ['curated','editorial_review','editorial_selection','verified'].includes(resource.review_status);
  const descriptionLabel = resource.description_type === 'existing_editorial_description'
    ? t('Présentation éditoriale','Editorial overview','Presentación editorial')
    : resource.description_type === 'source_caption_without_social_tokens'
      ? t('Légende de la source','Source caption','Texto de la fuente')
      : t('Dans cette ressource','In this resource','En este recurso');
  const rawPoints = resource.learning_points || resource.learningPoints;
  const points = Array.isArray(rawPoints) ? rawPoints.filter(point => typeof point === 'string' && point.trim()) : [];
  const questions = Array.isArray(resource.source_questions) ? resource.source_questions.filter(q => q && typeof q.question === 'string') : [];
  const automotive = c.automotiveMarkup?.(resource) || '';
  const social = c.socialMarkup?.(resource) || '';
  const provenance = transcriptBased
    ? t('Résumé français établi à partir de la transcription de la source. Les pistes automatiques peuvent contenir des erreurs ; les éléments uniquement visuels ne sont pas couverts.','French summary based on the source transcript. Automatic captions may contain errors; visual-only information is not covered.','Resumen en francés basado en la transcripción. Los subtítulos automáticos pueden contener errores; no cubre información solo visual.')
    : reviewed
      ? t('Choix effectué à partir des métadonnées publiques. Le contenu intégral n’a pas été audité.','Selected using public metadata. The full content has not been audited.','Seleccionado a partir de metadatos públicos. No se ha auditado el contenido completo.')
      : t('Le titre et les informations publiques ont permis ce référencement. La pertinence pédagogique reste à confirmer.','Indexed from the title and public information. Its teaching value still needs confirmation.','Indexado a partir del título y de información pública. Su valor didáctico aún debe confirmarse.');
  const reference = c.safeUrl(resource.source_url || resource.url);
  const telemetry = (resource.content_format || resource.contentFormat) === 'telemetry_demonstration';
  const questionMarkup = questions.map(question => {
    const href = c.safeUrl(question.source_url);
    const link = href ? `<a href="${e(href)}" target="_blank" rel="noopener noreferrer">${e(t('Voir le contexte','View context','Ver contexto'))} ↗</a>` : '';
    return `<blockquote>${e(question.question)}</blockquote>${link}`;
  }).join('');
  return `<section class="resource-overview"><h3>${e(descriptionLabel)}</h3><p class="social-description" dir="auto">${e(text(resource.description) || t('Aucun descriptif disponible. Ouvrez la source pour découvrir le contenu.','No description is available. Open the source to explore the content.','No hay descripción disponible. Abre la fuente para conocer el contenido.'))}</p>
    ${telemetry?`<p class="resource-context-note">${e(t('Tour avec télémétrie : observez les données et les gestes à l’écran. Une explication orale n’est pas garantie.','Lap with telemetry: study the on-screen data and driving inputs. Spoken instruction is not guaranteed.','Vuelta con telemetría: observa los datos y movimientos en pantalla. No se garantiza una explicación oral.'))}</p>`:''}
    ${points.length?`<section class="resource-concepts"><h3>${e(t('Points abordés','Topics covered','Temas tratados'))}</h3><ul class="detail-points">${points.map(point=>`<li>${e(point)}</li>`).join('')}</ul></section>`:''}
    ${automotive?`<details class="resource-disclosure"><summary>${e(t('Véhicules et repères cités','Vehicles and specifications mentioned','Vehículos y referencias mencionados'))}</summary>${automotive}</details>`:''}
    ${questions.length?`<details class="resource-disclosure comment-questions"><summary>${e(t('Questions dans les commentaires','Questions in the comments','Preguntas en los comentarios'))}</summary><p>${e(t('Questions reformulées en français à partir de commentaires publics consultés. Elles ne valident pas les réponses de la vidéo.','Questions paraphrased in French from public comments. They do not validate the answers in the video.','Preguntas reformuladas en francés a partir de comentarios públicos. No validan las respuestas del vídeo.'))}</p>${questionMarkup}</details>`:''}
    <details class="resource-disclosure resource-provenance"><summary>${e(t('Source, droits et méthode','Source, rights and method','Fuente, derechos y método'))}</summary><p>${e(provenance)}</p><dl class="resource-source-facts"><div><dt>${e(t('Licence de réutilisation','Reuse license','Licencia de reutilización'))}</dt><dd>${e(c.licenseName(resource.license))}</dd></div><div><dt>${e(t('Référence contrôlée le','Reference checked on','Referencia comprobada el'))}</dt><dd>${e(text(resource.verified_at) || t('Date non renseignée','Date not provided','Fecha no indicada'))}</dd></div></dl>${reference?`<a class="resource-original-link" href="${e(reference)}" target="_blank" rel="noopener noreferrer">${e(t('Consulter la référence d’origine','See the original reference','Ver referencia original'))} ↗</a>`:''}${social}</details>
  </section>`;
}
