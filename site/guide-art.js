import {icon} from './icons.js';

// Editorial diagrams, not maintenance schematics. Every path is fixed locally;
// no source caption, URL, technical value or user input becomes SVG markup.
const topics = Object.freeze({
  identification: {label:['Identification','Identification','Identificación'], icon:'car'},
  oil_spec: {label:['Huile moteur','Engine oil','Aceite del motor'], icon:'oil'},
  oil_change: {label:['Vidange','Oil change','Cambio de aceite'], icon:'oil'},
  fuel_choice: {label:['Carburant','Fuel','Combustible'], drawing:'fuel'},
  wipers: {label:['Essuie-glaces','Wipers','Limpiaparabrisas'], drawing:'wipers'},
  wheel_change: {label:['Roues','Wheels','Ruedas'], icon:'wheel'},
  battery: {label:['Batterie','Battery','Batería'], drawing:'battery'},
  fuses: {label:['Fusibles','Fuses','Fusibles'], drawing:'fuse'},
  lighting: {label:['Éclairage','Lighting','Iluminación'], drawing:'light'},
  diagnostics: {label:['Diagnostic','Diagnostics','Diagnóstico'], drawing:'diagnostics'},
  service_reset: {label:['Entretien','Maintenance','Mantenimiento'], icon:'wrench'},
  general: {label:['Repères pratiques','Practical reference','Referencia práctica'], icon:'library'},
});

const ids = Object.freeze({
  'vehicle-identification':'identification',
  'guide-oil-spec':'oil_spec',
  'guide-oil-change':'oil_change',
  'guide-fuel-choice':'fuel_choice',
  'guide-wipers':'wipers',
  'guide-wheel-change':'wheel_change',
  'guide-battery':'battery',
  'guide-fuses':'fuses',
  'guide-lighting':'lighting',
  'guide-diagnostics':'diagnostics',
  'guide-service-reset':'service_reset',
});

const drawings = Object.freeze({
  fuel:'M5 21V4h10v17M3 21h14M7.5 7h5v5h-5ZM15 8h2l3 3v6a1.5 1.5 0 0 0 3 0v-5l-3-4M20 8v3h3',
  wipers:'M3 18 5.5 5h13L21 18ZM6 14l6-5 6 5M6 18l6-9 6 9M4 14h2M18 14h2',
  battery:'M3 7h18v13H3ZM6 7V4h3v3M15 7V4h3v3M6 12h4M8 10v4M15 12h3',
  fuse:'M7 3h10v13H7ZM8 16v5M16 16v5M9.5 6v3l5 3v2M9.5 6h5M9.5 14h5',
  light:'M13 5C6 5 3 8 3 12s3 7 10 7V5ZM17 6h4M17 10h5M17 14h5M17 18h4',
  diagnostics:'M4 3h16v14H4ZM7 6h10v6H7ZM8 17v3h8v-3M12 20v2M9 9h2M14 9h1',
});

const firstLanguage = fr => fr;

function topicKey(resource) {
  const guide = resource?.guide || resource || {};
  for (const value of [resource?.id, guide.id]) {
    if (typeof value === 'string' && Object.hasOwn(ids, value)) return ids[value];
  }
  for (const value of [guide.task, resource?.task]) {
    if (typeof value === 'string' && Object.hasOwn(topics, value)) return value;
  }
  return 'general';
}

/** A short subject label only; the full canonical title stays outside the art. */
export function guideTopic(resource, {t = firstLanguage} = {}) {
  const key = topicKey(resource);
  return {key, label:t(...topics[key].label)};
}

/** Safe decorative artwork; all geometry is selected from the fixed tables. */
export function guideArt(resource) {
  const topic = topics[topicKey(resource)];
  const subject = topic.icon
    ? icon(topic.icon, {size:72})
    : `<svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="${drawings[topic.drawing]}"/></svg>`;
  return `<span class="guide-art" aria-hidden="true"><svg class="guide-art-icon" viewBox="0 0 240 144" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><g stroke="currentColor" stroke-width="1" opacity=".18"><path d="M30 46V26h20M190 26h20v20M30 98v20h20M190 118h20V98M30 72h35M175 72h35M120 18v12M120 114v12"/><circle cx="120" cy="72" r="50" stroke-dasharray="2 7"/></g><g transform="translate(84 36)">${subject}</g><g stroke="var(--red, #ff1735)" stroke-width="2"><path d="M30 118h24M186 26h24"/></g><circle cx="30" cy="72" r="3" fill="var(--red, #ff1735)"/></svg></span>`;
}
