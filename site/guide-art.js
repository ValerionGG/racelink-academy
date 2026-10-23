import {GUIDE_PHOTOS} from './guide-photos.js?v=themes-v22';

// Topic labels and photo selection stay independent of a guide's canonical title.
const topics = Object.freeze({
  identification: {label:['Identification','Identification','Identificación']},
  oil_spec: {label:['Huile moteur','Engine oil','Aceite del motor']},
  oil_change: {label:['Vidange','Oil change','Cambio de aceite']},
  fuel_choice: {label:['Carburant','Fuel','Combustible']},
  wipers: {label:['Essuie-glaces','Wipers','Limpiaparabrisas']},
  wheel_change: {label:['Roues','Wheels','Ruedas']},
  battery: {label:['Batterie','Battery','Batería']},
  fuses: {label:['Fusibles','Fusibles','Fusibles']},
  lighting: {label:['Éclairage','Lighting','Iluminación']},
  diagnostics: {label:['Diagnostic','Diagnostics','Diagnóstico']},
  service_reset: {label:['Entretien','Maintenance','Mantenimiento']},
  general: {label:['Repères pratiques','Practical reference','Referencia práctica']},
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

/** Editorial photo metadata; the registry owns source and licensing evidence. */
export function guidePhoto(resource) {
  return GUIDE_PHOTOS[topicKey(resource)] || GUIDE_PHOTOS.general || null;
}
