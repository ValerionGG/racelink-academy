// Source labels describe the document, never certify a vehicle's compatibility.
export const isManufacturerReference = source =>
  ['manufacturer_procedure','manufacturer_specification'].includes(source.sourceType) &&
  /^https:\/\//.test(source.url || '') && Boolean(source.vehicleScope && source.verifiedAt);

export function createGuideSources({escape:e,safeUrl}) {
  const labels={manufacturer_procedure:'Notice constructeur',manufacturer_specification:'Spécification constructeur',manual_portal:'Portail de notices'};
  function render(sources=[]) {
    return sources.filter(s=>safeUrl(s.url)).map(s=>{
      const date=/^\d{4}-\d{2}-\d{2}(?:T|$)/.test(s.verifiedAt||'')?s.verifiedAt.slice(0,10).split('-').reverse().join('/') : '';
      return `<article class="official-source"><p class="source-kind">${e(s.publisher||'Source')} · ${e(labels[s.sourceType]||'Référence documentaire')}</p><a class="official-source-link" href="${e(safeUrl(s.url))}" target="_blank" rel="noopener noreferrer"><strong>${e(s.title)}</strong><span aria-hidden="true">↗</span></a><p class="source-vehicle">${e(s.vehicleScope||s.scope||'Véhicule et édition à sélectionner sur le site constructeur.')}</p>${s.section?`<p class="source-section">Section : ${e(s.section)}</p>`:''}${s.summary||s.evidenceNote||s.limits?`<details class="source-evidence"><summary>Contenu et portée de la source</summary>${s.summary?`<p>${e(s.summary)}</p>`:''}${s.limits?`<p><strong>Portée :</strong> ${e(s.limits)}</p>`:''}${s.evidenceNote?`<p>${e(s.evidenceNote)}</p>`:''}${date?`<p class="source-date">Page consultée le ${e(date)}.</p>`:''}</details>`:''}</article>`;
    }).join('');
  }
  return {render};
}
