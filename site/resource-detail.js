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

/** Media first; existing IDs, one tab panel and delegated actions remain intact. */
import {sourceLabel} from './source-label.js?v=discovery-v34';
export function renderResourceDetail(resource, helpers) {
  const c = context(helpers), {e,t} = c;
  const source = c.safeUrl(resource.url), image = c.safeUrl(resource.thumbnail_url || resource.thumbnailUrl, true);
  const canEmbed = Boolean(source && c.embedUrl?.(resource)), isSaved = Boolean(c.isSaved);
  const platform = sourceLabel(resource,c.platformName) || t('la source','the source','la fuente');
  const author = text(resource.creator).trim() || t('Auteur non renseigné','Creator not provided','Autor no indicado');
  const sourceLink = (label,className='') => source ? `<a class="${className}" href="${e(source)}" target="_blank" rel="noopener noreferrer">${e(label)} <span aria-hidden="true">↗</span></a>` : '';
  const levelKnown = resource.level && !['all','unknown'].includes(resource.level) && !String(resource.level_status).includes('unknown');
  const facts = [Number(resource.duration_seconds)>0 ? c.fmtDuration(resource.duration_seconds) : '', c.langName(resource.language)+(c.estimatedLanguage(resource)?t(' · estimée',' · estimated',' · estimado'):''), levelKnown ? c.levelName(resource.level) : ''].filter(Boolean);
  const tabs = [['about',t('Détails','Details','Detalles')],['transcript',t('Transcription','Transcript','Transcripción')],['notes',t('Mes notes','My notes','Mis notas')]];
  return `<article class="resource-workspace" data-resource-kind="video">
    <header class="detail-header resource-toolbar">
      <button type="button" class="resource-back" data-close aria-label="${e(t('Fermer la fiche','Close resource','Cerrar ficha'))}"><span aria-hidden="true">←</span> ${e(t('Retour','Back','Volver'))}</button>
      <span class="resource-location">${e(c.catName(resource.category))}</span>
    </header>
    <div class="resource-body">
      <section class="resource-media" aria-label="${e(t('Vidéo et repères','Video and key details','Vídeo y datos principales'))}">
        <div class="player resource-player" id="player">
          <div class="resource-preview"><div class="resource-preview-empty"><span>${e(platform)}</span><p>${e(t('Aperçu indisponible','Preview unavailable','Vista previa no disponible'))}</p></div>${image?`<img src="${e(image)}" alt="" width="960" height="540" decoding="async" referrerpolicy="no-referrer">`:''}</div>
          <div class="player-prompt resource-watch"><div class="resource-watch-actions">${canEmbed?`<button type="button" data-play class="resource-watch-primary"><span aria-hidden="true">▶</span> ${e(t('Regarder ici','Watch here','Ver aquí'))}</button>`:sourceLink(t(`Voir sur ${platform}`,`Watch on ${platform}`,`Ver en ${platform}`),'resource-watch-primary')}${!source?`<p>${e(t('Lien source indisponible','Source link unavailable','Enlace de origen no disponible'))}</p>`:''}</div></div>
        </div>
        <header class="resource-heading">
          <p class="resource-kind">${e(t('Vidéo','Video','Vídeo'))}<span aria-hidden="true"> · </span>${sourceLink(platform,'resource-source-link')||e(platform)}</p>
          <h2 id="dialog-title" dir="auto">${e(text(resource.title)||t('Ressource vidéo','Video resource','Recurso de vídeo'))}</h2>
          <p class="resource-author" dir="auto">${e(author)}</p>
          <ul class="resource-quick-facts" aria-label="${e(t('Informations de la source','Source information','Información de la fuente'))}">${facts.map(fact=>`<li>${e(fact)}</li>`).join('')}</ul>
          <div class="detail-actions resource-utilities">
            <button type="button" data-save="${e(resource.id)}" class="${isSaved?'saved':''}" aria-pressed="${isSaved}" aria-label="${e(isSaved?t('Retirer de ma sélection','Remove from collection','Quitar de mi selección'):t('Enregistrer la vidéo','Save video','Guardar vídeo'))}">${e(isSaved?t('Enregistré ✓','Saved ✓','Guardado ✓'):t('Enregistrer','Save','Guardar'))}</button>
            <button type="button" data-share${source?'':' disabled'}>${e(t('Copier le lien','Copy link','Copiar enlace'))}</button>
          </div>
          ${source?`<p class="resource-playback-note">${e(canEmbed?t('Le lecteur externe se charge à votre demande et peut utiliser des cookies.','The external player loads when you choose and may use cookies.','El reproductor externo se carga cuando lo eliges y puede utilizar cookies.'):t('La vidéo s’ouvre chez son auteur, dans un nouvel onglet.','The video opens at its source in a new tab.','El vídeo se abre en su fuente, en una pestaña nueva.'))}</p>`:''}
          <div id="detail-racelink-pick" class="detail-racelink-pick resource-pick" hidden></div>
        </header>
      </section>
      <section class="detail-side resource-reading" aria-label="${e(t('Lire et retenir','Read and learn','Leer y aprender'))}">
        <div class="detail-tabs resource-tabs" role="tablist" aria-label="${e(t('Contenu de la fiche','Resource contents','Contenido de la ficha'))}">${tabs.map(([key,label],i)=>`<button type="button" role="tab" id="tab-${key}" data-tab="${key}" aria-controls="detail-panel" aria-selected="${i===0}" tabindex="${i===0?'0':'-1'}"${i===0?' class="active"':''}>${e(label)}</button>`).join('')}</div>
        <div class="detail-panel resource-panel" id="detail-panel" role="tabpanel" aria-labelledby="tab-about" tabindex="0">${renderResourceOverview(resource,helpers)}</div>
      </section>
    </div>
  </article>`;
}

/** Use for the existing setDetailTab('about') branch; other tab handlers stay intact. */
export function renderResourceOverview(resource, helpers) {
  const c = context(helpers), {e,t} = c;
  const transcriptBased = (resource.summary_basis || resource.summaryBasis) === 'authorized_transcript';
  const reviewed = ['curated','editorial_review','editorial_selection','verified'].includes(resource.review_status);
  const listing = String(resource.verification_scope || '').includes('listing') || String(resource.description_basis || '').includes('listing_excerpt');
  const editorial = ['editorial_summary','existing_editorial_description'].includes(resource.description_type);
  const descriptionLabel = transcriptBased ? t('Résumé de la transcription','Transcript summary','Resumen de la transcripción')
    : editorial ? t('Présentation éditoriale','Editorial overview','Presentación editorial')
    : listing ? t('Extrait de la source','Source excerpt','Extracto de la fuente')
    : resource.description_type === 'source_caption_without_social_tokens' ? t('Légende de la source','Source caption','Texto de la fuente')
    : t('Description de la source','Source description','Descripción de la fuente');
  const description = text(resource.description).trim();
  const longDescription = description.length > 480;
  const excerpt = longDescription ? description.slice(0,360).replace(/\s+\S*$/u,'').trimEnd() + '…' : description;
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
  const levelKnown = resource.level && !['all','unknown'].includes(resource.level) && !String(resource.level_status).includes('unknown');
  const transcriptText = typeof resource.transcript === 'string' ? resource.transcript : resource.transcript?.text || resource.transcript?.content;
  const hasTranscript = Boolean(resource.has_transcript && text(transcriptText).trim());
  const fields = [
    [t('Durée','Duration','Duración'),c.fmtDuration(resource.duration_seconds)],
    [t('Langue','Language','Idioma'),c.langName(resource.language)+(c.estimatedLanguage(resource)?t(' · estimée',' · estimated',' · estimado'):'')],
    [t('Niveau indicatif','Estimated level','Nivel estimado'),levelKnown?c.levelName(resource.level):t('Non confirmé','Unconfirmed','Sin confirmar')],
    [t('Licence de réutilisation','Reuse license','Licencia de reutilización'),c.licenseName(resource.license)],
    [t('Référence contrôlée le','Reference checked on','Referencia comprobada el'),text(resource.verified_at)||t('Date non renseignée','Date not provided','Fecha no indicada')]
  ];
  return `<section class="resource-overview"><div class="resource-description"><h3>${e(descriptionLabel)}</h3><p class="social-description" dir="auto">${e(excerpt || t('Aucun descriptif disponible. Ouvrez la source pour découvrir le contenu.','No description is available. Open the source to explore the content.','No hay descripción disponible. Abre la fuente para conocer el contenido.'))}</p>${longDescription?`<details class="resource-disclosure resource-full-description"><summary>${e(t('Afficher tout le texte disponible','Show all available text','Mostrar todo el texto disponible'))}</summary><p class="social-description" dir="auto">${e(description)}</p></details>`:''}</div>
    ${telemetry?`<p class="resource-context-note">${e(t('Tour avec télémétrie : observez les données et les gestes à l’écran. Une explication orale n’est pas garantie.','Lap with telemetry: study the on-screen data and driving inputs. Spoken instruction is not guaranteed.','Vuelta con telemetría: observa los datos y movimientos en pantalla. No se garantiza una explicación oral.'))}</p>`:''}
    ${points.length?`<section class="resource-concepts"><h3>${e(t('Points abordés','Topics covered','Temas tratados'))}</h3><ul class="detail-points">${points.map(point=>`<li>${e(point)}</li>`).join('')}</ul></section>`:''}
    ${automotive?`<details class="resource-disclosure resource-vehicle-context" open><summary>${e(t('Véhicule et entretien','Vehicle and maintenance','Vehículo y mantenimiento'))}</summary>${automotive}</details>`:''}
    ${social?`<details class="resource-disclosure resource-source-text"><summary>${e(t('Texte et hashtags de la source','Source text and hashtags','Texto y hashtags de la fuente'))}</summary>${social}</details>`:''}
    ${questions.length?`<details class="resource-disclosure comment-questions"><summary>${e(t('Questions dans les commentaires','Questions in the comments','Preguntas en los comentarios'))}</summary><p>${e(t('Questions reformulées en français à partir de commentaires publics consultés. Elles ne valident pas les réponses de la vidéo.','Questions paraphrased in French from public comments. They do not validate the answers in the video.','Preguntas reformuladas en francés a partir de comentarios públicos. No validan las respuestas del vídeo.'))}</p>${questionMarkup}</details>`:''}
    <details class="resource-disclosure resource-provenance"><summary>${e(t('Source, droits et méthode','Source, rights and method','Fuente, derechos y método'))}</summary><p>${e(provenance)}</p><dl class="resource-source-facts">${fields.map(([label,value])=>`<div><dt>${e(label)}</dt><dd>${e(value)}</dd></div>`).join('')}</dl><p class="resource-transcript-state">${e(hasTranscript?t('Une transcription est disponible dans cette fiche.','A transcript is available in this resource.','Esta ficha incluye una transcripción.'):t('Aucune transcription enregistrée ici. Les sous-titres peuvent être disponibles à la source.','No transcript is stored here. Captions may be available at the source.','No hay una transcripción guardada aquí. La fuente puede ofrecer subtítulos.'))}</p>${reference?`<a class="resource-original-link" href="${e(reference)}" target="_blank" rel="noopener noreferrer">${e(t('Consulter la référence d’origine','See the original reference','Ver referencia original'))} ↗</a>`:''}</details>
  </section>`;
}
