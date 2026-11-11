/* Browsing disciplines are metadata matches, not verified vehicle applications.
 * Motorcycle/karting/drift use the displayed title only. Descriptions, creators
 * and tags are deliberately excluded: promotional footers can name unrelated
 * disciplines. Motorsport and sim racing reuse existing editorial fields.
 * Full catalog fields and compact social-index aliases share the same rules.
 */
export const DISCIPLINES = Object.freeze([
  {id: "motorcycle", label: {fr: "Moto", en: "Motorcycling", es: "Moto"}},
  {id: "karting", label: {fr: "Karting", en: "Karting", es: "Karting"}},
  {id: "drift", label: {fr: "Drift", en: "Drifting", es: "Drift"}},
  {id: "motorsport", label: {fr: "Sport automobile", en: "Motorsport", es: "Automovilismo"}},
  {id: "simracing", label: {fr: "Sim racing", en: "Sim racing", es: "Sim racing"}},
].map(item => Object.freeze({...item, label: Object.freeze(item.label)})));

const titleTerms = {
  motorcycle: new Set("moto motos motocycle motocycles motocyclette motocyclettes motorcycle motorcycles motorcycling motorrad motorrader motocicleta motocicletas motocross supermoto superbike motogp".split(" ")),
  karting: new Set("kart karts karting gokart gokarts".split(" ")),
  drift: new Set("drift drifts drifting".split(" ")),
};
const field = (item, full, compact) => typeof item?.[full] === "string"
  ? item[full] : typeof item?.[compact] === "string" ? item[compact] : "";
const titleTokens = item => field(item, "title", "t").normalize("NFKD")
  .replace(/\p{M}/gu, "").toLowerCase().match(/[\p{L}\p{N}]+/gu) || [];
const matched = (item, id, tokens) => {
  if (id === "motorsport") return field(item, "domain_scope", "d") === "motorsport";
  if (id === "simracing") return field(item, "category", "c") === "simracing";
  return Boolean(titleTerms[id] && tokens.some(token => titleTerms[id].has(token)));
};

export function disciplineMatches(item, id) {
  if (!DISCIPLINES.some(discipline => discipline.id === id)) return false;
  return matched(item, id, titleTerms[id] ? titleTokens(item) : []);
}

export function disciplineIds(item) {
  const tokens = titleTokens(item);
  return DISCIPLINES.filter(({id}) => matched(item, id, tokens)).map(({id}) => id);
}
