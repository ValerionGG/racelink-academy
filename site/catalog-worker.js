/* No DOM, network trackers, external libraries, or generated content. */
export const normalize = value => String(value ?? "").normalize("NFKD")
  .replace(/\p{M}/gu, "").toLowerCase().trim();
const wordsOf = value => normalize(value).match(/[\p{L}\p{N}]+/gu) || [];
const stopwords = new Set(`comment pourquoi quand quelle quelles quels quel est sont je tu on nous vous il elle ils elles
le la les un une des de du d l a au aux en et ou pour par avec sans dans sur que qui ce cet cette
how why when what which can could do does did i you we they the a an to of for with without in on and is are my your
como por que cuando cual cuales puedo podemos el la los las un una de del al en con sin para`.split(/\s+/));
const contexts = new Set("roue roues wheel wheels voiture voitures car cars coche coches rueda ruedas".split(" "));
const topics = [
  ["braking", "frein freins freiner freinage brake brakes braking frenar frenado frenada", ["frein", "brak", "fren"]],
  ["locking", "bloquer blocage bloque bloquage lock locking lockup bloquear bloqueo", ["bloqu", "blocage", "lock"]],
  ["telemetry", "telemetrie telemetry telemetria", ["telemetr"]],
  ["setup", "reglage reglages regler setup setups tuning ajuste ajustes configurar", ["regl", "setup", "tuning", "ajust"]],
  ["tyres", "pneu pneus pneumatiques tyre tyres tire tires neumatico neumaticos", ["pneu", "tyre", "tire", "neumatic"]],
  ["sponsorship", "sponsor sponsors sponsoring sponsorship sponsorships patrocinio", ["sponsor", "patrocini"]],
  ["oversteer", "survirage oversteer oversteering sobreviraje", ["survir", "oversteer", "sobrevir"]],
  ["understeer", "sousvirage understeer understeering subviraje", ["sous virage", "sousvir", "understeer", "subvir"]],
  ["trajectory", "trajectoire trajectoires trazada trazadas", ["trajectoir", "racing line", "trazad"]],
].map(([name, aliases, terms]) => ({name, aliases: new Set(aliases.split(" ")), terms}));
const compareTitle = (a, b) => {
  const left = a.title.toLowerCase(), right = b.title.toLowerCase();
  return (left < right ? -1 : left > right ? 1 : 0) || a.id.localeCompare(b.id);
};
const selection = item => ["editorial_selection", "curated", "verified"].includes(item.review_status);
const clean = item => Object.fromEntries(Object.entries(item).filter(([key]) => !key.startsWith("_")));
const vehicleFields = ["make", "model", "generation", "engine", "body_type", "fuel_type"];
const vehicleFilters = [...vehicleFields, "year"];
const validFilter = value => value != null && value !== "" && !["all", "any", "*"].includes(String(value));
const specKey = value => normalize(value).replace(/[^a-z0-9]/g, "");
const contentFormats = {tutorial: "tutorial", tutorial_candidate: "tutorial", demonstration: "demonstration",
  telemetry_demonstration: "demonstration", course: "course", course_candidate: "course", lecture: "course",
  stream: "stream", training_stream_candidate: "stream", unspecified: "unspecified"};
const taskPhrases = {
  oil_change: ["vidange", "oil change", "change oil", "cambio de aceite", "cambiar aceite"],
  oil_filter: ["filtre a huile", "oil filter", "filtro de aceite"],
  cabin_filter: ["filtre habitacle", "filtre d habitacle", "filtre de cabine", "cabin filter", "pollen filter", "filtro habitaculo"],
  air_filter: ["filtre a air", "air filter", "filtro de aire"],
  fuel_filter: ["filtre a carburant", "filtre a gasoil", "fuel filter", "filtro de combustible"],
  wipers: ["essuie glaces", "essuie glace", "wipers", "wiper", "limpiaparabrisas"],
  wheel_change: ["changer une roue", "changer la roue", "changement de roue", "wheel change", "change wheel", "cambiar rueda"],
  key_battery: ["pile de cle", "pile cle", "key battery", "key fob battery", "pila llave"],
  battery: ["batterie", "battery", "bateria"],
  brake_pads: ["plaquettes de frein", "plaquettes frein", "brake pads", "pastillas de freno"],
  brake_discs: ["disques de frein", "disques frein", "brake discs", "brake rotors", "discos de freno"],
  wheel_bearing: ["roulement de roue", "roulement roue", "wheel bearing", "rodamiento de rueda"],
  spark_plugs: ["bougies d allumage", "bougies allumage", "spark plugs", "bujias"],
  glow_plugs: ["bougies de prechauffage", "glow plugs"],
  fuses: ["fusibles", "fusible", "fuses", "fuse"],
  lighting: ["ampoule", "ampoules", "phare", "phares", "headlight", "bulb", "bombilla"],
  diagnostics: ["diagnostic", "diagnostics", "obd", "code defaut"],
  service_reset: ["service reset", "reset service", "remise a zero entretien", "reset entretien"],
  oil_spec: ["quelle huile", "which oil", "oil viscosity", "viscosite huile", "que aceite"],
  fuel_choice: ["quel carburant", "which fuel", "que combustible", "choix carburant"],
};
const automotiveStopwords = new Set([...stopwords, ...`faire faireune changer change changing remplacer replace replacing mettre ajouter remplir trouver
savoir comment tutorial tuto tutoriel guide video ma mon mes sa son ses voiture vehicule auto car vehicle coche mi su como hacer comment bien`.split(/\s+/)]);
const romanGenerations = {i: "1", ii: "2", iii: "3", iv: "4", v: "5", vi: "6", vii: "7", viii: "8", ix: "9", x: "10"};
const phrasePattern = value => new RegExp("(?<![\\p{L}\\p{N}_])" +
  wordsOf(value).join("[^\\p{L}\\p{N}]*") + "(?![\\p{L}\\p{N}_])", "gu");
const phraseFound = (text, value) => phrasePattern(value).test(text);
const emptyAutomotive = () => ({vehicles: [], tasks: [], systems: [], specifications: [], status: "not_extracted"});
function languageConfidence(language, status = "unknown") {
  if (["und", "mul"].includes(language) || status.startsWith("unknown")) return "unknown";
  if (["platform_metadata", "platform_declared", "original_audio_metadata"].includes(status)) return "platform_declared";
  if (["caption_track", "original_caption_track", "original_automatic_caption_track", "source_caption_metadata"].includes(status)) return "source_caption_track";
  return /^(inferred|estimated)/.test(status) ? "estimated" : "unknown";
}

export function prepareCatalog(payload) {
  const unique = new Map();
  for (const raw of payload.items || []) {
    if (!unique.has(raw.id)) {
      const item = {...raw};
      if (item.language_status === "inferred_from_discovery_query") {
        item.language = "und";
        item.language_status = "unknown_query_only";
      }
      item.language_tag = item.language_tag || item.language || "und";
      item.language = String(item.language || "und").toLowerCase().replaceAll("_", "-").split("-")[0];
      item.language_confidence = languageConfidence(item.language, item.language_status);
      item.resource_type = "video";
      item.pedagogical_format = contentFormats[item.content_format || item.contentFormat] || "unspecified";
      item.format_status = item.format_status || (item.pedagogical_format === "unspecified" ? "not_classified" : "metadata_candidate");
      const searchWords = wordsOf(item._search || [
        item.title, item.creator, item.description, ...(item.tags || []),
        ...(item.source_questions || []).flatMap(question => [question.question, question.excerpt]),
      ].join(" "));
      item._tokens = [...new Set(searchWords)];
      item._titleTokens = wordsOf(item.title);
      item._creatorTokens = wordsOf(item.creator);
      item._tagTokens = wordsOf((item.tags || []).join(" "));
      item._search = searchWords.join(" ");
      item.automotive = item.automotive || emptyAutomotive();
      item._vehicles = item.automotive.vehicles.map(vehicle => ({...vehicle,
        _keys: Object.fromEntries(vehicleFields.map(field => [field, normalize(vehicle[field])]))}));
      item._specs = item.automotive.specifications.map(spec => specKey(spec.value));
      unique.set(item.id, item);
    }
  }
  const items = [...unique.values()];
  const applications = new Map(), specifications = new Set();
  for (const item of items) {
    for (const vehicle of item._vehicles) {
      if (vehicle.make || vehicle.model) applications.set(
        JSON.stringify([vehicle.make, vehicle.model, vehicle.generation, vehicle.engine]), vehicle);
    }
    for (const spec of item.automotive.specifications) specifications.add(spec.value);
  }
  return {items, byId: unique, stats: payload.stats || {},
    applications: [...applications.values()], specifications: [...specifications], guides: payload.guides || [],
    discovery: payload.discovery || {version: 1, intents: [], topics: [], shelves: []}, _discoveryCounts: new Map()};
}

function param(params, key, fallback = "") {
  const value = params instanceof URLSearchParams ? params.get(key) : params[key];
  return value == null ? fallback : String(Array.isArray(value) ? value[0] : value);
}

function numberParam(params, name, fallback, maximum) {
  const value = param(params, name, String(fallback));
  if (!/^\d{1,8}$/.test(value) || Number(value) < 1 || Number(value) > maximum)
    throw new Error(`Paramètre ${name} invalide`);
  return Number(value);
}

function termMatch(tokens, text, term) {
  return term.includes(" ") ? text.includes(term) : tokens.some(word => word.startsWith(term));
}

function matches(item, groups) {
  return groups.every(group => group.some(term => termMatch(item._tokens, item._search, term)));
}

function educationalCandidates(query, words) {
  const groups = [], concepts = [], unknown = [];
  for (const word of words.filter(word => !stopwords.has(word))) {
    if (contexts.has(word)) continue;
    const topic = topics.find(topic => topic.aliases.has(word));
    if (topic) {
      if (!concepts.includes(topic.name)) {
        concepts.push(topic.name);
        groups.push(topic.terms);
      }
    } else {
      unknown.push(word);
      groups.push([word]);
    }
  }
  const candidates = concepts.length && groups.length ? [{groups, mode: "glossary", topics: concepts}] : [];
  const question = query.includes("?") || ["comment", "pourquoi", "how", "why", "como", "can", "could"].includes(words[0]);
  if (question && !unknown.length && concepts.length === 2 && concepts.includes("braking") && concepts.includes("locking")) {
    candidates.push({groups: [topics.find(topic => topic.name === "braking").terms],
      mode: "related_topics", topics: ["braking"]});
  }
  return candidates;
}

function facet(items, field, transform = value => value) {
  const counts = new Map();
  for (const item of items) {
    const value = transform(item[field]);
    counts.set(value, (counts.get(value) || 0) + 1);
  }
  return [...counts].map(([value, count]) => ({value, count}))
    .sort((a, b) => b.count - a.count || String(a.value).localeCompare(String(b.value)));
}

function automotiveFacet(items, field) {
  const counts = new Map();
  for (const item of items) {
    const values = field === "spec" ? item.automotive.specifications.map(spec => spec.value)
      : item.automotive[field === "task" ? "tasks" : "systems"];
    for (const value of new Set(values)) counts.set(value, (counts.get(value) || 0) + 1);
  }
  return [...counts].map(([value, count]) => ({value, count}))
    .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value));
}

function selectedVehicle(params) {
  const result = {};
  for (const key of vehicleFilters) {
    const value = param(params, key).trim();
    if (!validFilter(value)) continue;
    if (value.length > 150) throw new Error(`Filtre ${key} trop long`);
    if (key === "year") {
      if (!/^\d{4}$/.test(value) || Number(value) < 1886 || Number(value) > 2100)
        throw new Error("Année véhicule invalide");
      result[key] = Number(value);
    } else result[key] = value;
  }
  return result;
}

function vehicleMatches(vehicle, filters) {
  return Object.entries(filters).every(([field, value]) => {
    if (field !== "year") return vehicle._keys[field] === normalize(value);
    const low = vehicle.year_from ?? vehicle.year_to;
    const high = vehicle.year_to ?? vehicle.year_from;
    return low != null && high != null && value >= low && value <= high;
  });
}

export function vehicleOptions(catalog, params = {}) {
  const selected = selectedVehicle(params), options = {}, matchingVideos = new Set();
  let matchingApplications = 0;
  for (const item of catalog.items) for (const vehicle of item._vehicles) {
    if (vehicleMatches(vehicle, selected)) { matchingApplications++; matchingVideos.add(item.id); }
  }
  for (const field of vehicleFilters) {
    const filters = Object.fromEntries(Object.entries(selected).filter(([key]) =>
      field === "make" ? false : field === "model" ? key === "make" :
      field === "generation" ? ["make", "model"].includes(key) : key !== field));
    const counts = new Map();
    for (const item of catalog.items) for (const vehicle of item._vehicles) {
      if (!vehicleMatches(vehicle, filters)) continue;
      const values = [];
      if (field === "year") {
        const low = vehicle.year_from ?? vehicle.year_to, high = vehicle.year_to ?? vehicle.year_from;
        if (low != null && high != null) for (let year = low; year <= high; year++) values.push(String(year));
      } else if (vehicle._keys[field]) values.push(vehicle[field]);
      for (const value of values) {
        const key = normalize(value);
        if (!counts.has(key)) counts.set(key, {value, ids: new Set()});
        const group = counts.get(key);
        if (value < group.value) group.value = value;
        group.ids.add(item.id);
      }
    }
    options[field] = [...counts.values()].map(({value, ids}) => ({value, count: ids.size}))
      .sort((a, b) => a.value.toLowerCase() < b.value.toLowerCase() ? -1 : a.value.toLowerCase() > b.value.toLowerCase() ? 1 : 0);
  }
  return {options, facets: options, total_videos: matchingVideos.size, matching_applications: matchingApplications,
    selected, evidence_scope: "title_mention", compatibility_verified: false};
}

export function inferAutomotive(catalog, q, params = {}) {
  const result = {vehicle: {}, task: null, spec: null, residual: q, conflicts: []};
  if (!q) return result;
  let remaining = normalize(q);
  const consume = value => { remaining = remaining.replace(phrasePattern(value), " "); };
  const aliases = {"Volkswagen": ["vw"], "Mercedes-Benz": ["mercedes", "mercedes benz"]};
  const applications = catalog.applications;
  const makes = [...new Set(applications.map(item => item.make).filter(Boolean))]
    .sort((a, b) => b.length - a.length)
    .filter(make => [make, ...(aliases[make] || [])].some(value => phraseFound(remaining, value)));
  if (makes.length === 1) {
    result.vehicle.make = makes[0];
    for (const value of [makes[0], ...(aliases[makes[0]] || [])]) consume(value);
  }
  let scope = applications.filter(item => !result.vehicle.make || item.make === result.vehicle.make);
  let modelMentions = [];
  const compactRemaining = wordsOf(remaining).join("");
  for (const model of [...new Set(scope.map(item => item.model).filter(Boolean))].sort((a, b) => b.length - a.length)) {
    if (!compactRemaining.includes(wordsOf(model).join(""))) continue;
    if (/^\d+$/.test(model) && !(result.vehicle.make || param(params, "make"))) continue;
    const rows = scope.filter(item => item.model === model), combined = [];
    for (const generation of new Set(rows.map(item => item.generation).filter(Boolean))) {
      for (const alias of [generation, romanGenerations[normalize(generation)]].filter(Boolean)) {
        const phrase = model + " " + alias;
        if (new RegExp(phrasePattern(phrase).source + "(?![.,]\\d)", "u").test(remaining)) combined.push({generation, phrase});
      }
    }
    if (combined.length) {
      const generations = [...new Set(combined.map(item => item.generation))];
      modelMentions.push({model, generation: generations.length === 1 ? generations[0] : null,
        phrases: combined.map(item => item.phrase)});
    } else if (phraseFound(remaining, model)) {
      const explicit = remaining.match(new RegExp(phrasePattern(model).source +
        "\\s+(?:mk\\s*)?(viii|vii|iii|vi|iv|ix|ii|v|x|i|10|[1-9])(?=$|[\\s(),/?])", "u"));
      if (explicit) {
        const generation = Object.entries(romanGenerations).find(([, number]) => number === explicit[1])?.[0] || explicit[1];
        modelMentions.push({model, generation: generation.toUpperCase(), phrases: [explicit[0]]});
      } else modelMentions.push({model, generation: null, phrases: [model]});
    }
  }
  if (modelMentions.length) {
    const longest = Math.max(...modelMentions.map(item => item.model.length));
    modelMentions = modelMentions.filter(item => item.model.length === longest);
  }
  if (modelMentions.length === 1) {
    const {model, generation, phrases} = modelMentions[0];
    result.vehicle.model = model;
    if (generation) result.vehicle.generation = generation;
    phrases.forEach(consume);
    scope = scope.filter(item => item.model === model);
    const modelMakes = [...new Set(scope.map(item => item.make).filter(Boolean))];
    if (modelMakes.length === 1 && !result.vehicle.make) result.vehicle.make = modelMakes[0];
  } else if (param(params, "model")) scope = scope.filter(item => normalize(item.model) === normalize(param(params, "model")));
  if (result.vehicle.model || param(params, "model")) {
    const engines = [...new Set(scope.map(item => item.engine).filter(Boolean))].filter(engine => phraseFound(remaining, engine));
    if (engines.length === 1) { result.vehicle.engine = engines[0]; consume(engines[0]); }
    else if (!engines.length) {
      const engine = remaining.match(/(?<![\p{L}\p{N}_])[0-8][.,]\d(?:\s*(?:l|litre|liter))?(?:\s*(?:tdi|hdi|cdti|cdi|dci|tdci|tsi|tfsi|gdi|mpi|vtec|ecoboost|jtd|d4d|d-4d|16v|8v|v[468]))?(?![\p{L}\p{N}_])/u);
      if (engine) { result.vehicle.engine = engine[0].toUpperCase().replace(",", ".").replace(/\s+/g, " "); consume(engine[0]); }
    }
    const years = [...new Set(remaining.match(/(?<![\p{L}\p{N}_])(?:19|20)\d{2}(?![\p{L}\p{N}_])/gu) || [])];
    if (years.length === 1) { result.vehicle.year = years[0]; consume(years[0]); }
  }
  for (const [task, phrases] of Object.entries(taskPhrases)) {
    const found = phrases.filter(phrase => phraseFound(remaining, phrase));
    if (found.length) {
      result.task = task;
      found.filter(alias => alias !== "obd").forEach(consume);
      break;
    }
  }
  const specs = catalog.specifications.filter(value => phraseFound(remaining, value) &&
    !(result.vehicle.make === "BMW" && specKey(value) === "e85" &&
      !/\b(?:fuel|carburant|ethanol|essence|combustible)\b/.test(remaining)));
  if (specs.length && new Set(specs.map(specKey)).size === 1) { result.spec = specs[0]; consume(specs[0]); }
  if (!result.spec) {
    const grade = remaining.match(/(?<![\p{L}\p{N}_])(\d{1,2})[\s-]*w[\s-]*(\d{2})(?![\p{L}\p{N}_])/u);
    if (grade) { result.spec = grade[1] + "W-" + grade[2]; consume(result.spec); }
  }
  for (const [field, value] of Object.entries(result.vehicle)) {
    const selected = param(params, field);
    if (selected && normalize(selected) !== normalize(value)) result.conflicts.push({field, selected, mentioned: value});
  }
  for (const field of ["task", "spec"]) {
    const selected = param(params, field), value = result[field];
    const equal = field === "spec" ? specKey(selected) === specKey(value) : selected === value;
    if (selected && value && !equal) result.conflicts.push({field, selected, mentioned: value});
  }
  if (Object.keys(result.vehicle).length || result.task || result.spec) {
    const ignored = new Set([...automotiveStopwords, ...(result.task === "oil_change" || result.spec ? ["huile", "oil", "aceite"] : [])]);
    result.residual = wordsOf(remaining).filter(word => !ignored.has(word)).join(" ");
  }
  return result;
}

export function searchCatalog(catalog, params = {}, options = {}) {
  const page = numberParam(params, "page", 1, 1000000);
  const perPage = numberParam(params, "per_page", 24, 100);
  const q = param(params, "q").trim();
  if (q.length > 300) throw new Error("Recherche limitée à 300 caractères");
  const resourceFormat = param(params, "format", "all") || "all", contentFormat = param(params, "content_format");
  if (!["all", "video", "guide", "image"].includes(resourceFormat)) throw new Error("Format de ressource invalide");
  if (validFilter(contentFormat) && !Object.values(contentFormats).includes(contentFormat)) throw new Error("Format pédagogique invalide");
  const interpretation = inferAutomotive(catalog, q, params);
  const effective = Object.fromEntries(vehicleFilters.map(key => [key, param(params, key)]));
  for (const [key, value] of Object.entries(interpretation.vehicle)) if (!effective[key]) effective[key] = value;
  const vehicle = selectedVehicle(effective);
  const task = param(params, "task") || interpretation.task;
  const system = param(params, "system");
  const spec = param(params, "spec") || interpretation.spec;
  for (const [key, value] of Object.entries({task, system, spec}))
    if (value && value.length > 150) throw new Error(`Filtre ${key} trop long`);
  const residual = interpretation.residual;
  const queryWords = wordsOf(residual).slice(0, 20);
  const sort = param(params, "sort", "relevance");
  if (!["relevance", "newest", "title", "duration"].includes(sort)) throw new Error("Tri invalide");
  const filters = ["category", "level", "language", "platform", "license"].map(key => [key, param(params, key)]);
  const duration = param(params, "duration"), transcript = param(params, "transcript"), domain = param(params, "domain");
  if (duration && !["all", "any", "short", "medium", "long"].includes(duration)) throw new Error("Durée invalide");
  if (transcript && !["all", "any", "available", "true", "1", "missing", "unavailable", "false", "0"].includes(transcript))
    throw new Error("Filtre transcription invalide");
  if (domain && !["all", "any", "motorsport", "automotive_adjacent"].includes(domain)) throw new Error("Contexte invalide");
  const idsValue = param(params, "ids"), ids = idsValue ? [...new Set(idsValue.split(","))] : null;
  if (ids && (ids.length > 100 || ids.some(id => !/^[A-Za-z0-9_:-]{1,100}$/.test(id)))) throw new Error("Identifiants invalides");
  const valid = value => value && !["all", "any", "*"].includes(value);
  const filtered = catalog.items.filter(item => {
    if (!["all", "video"].includes(resourceFormat)) return false;
    if (validFilter(contentFormat) && item.pedagogical_format !== contentFormat) return false;
    if (interpretation.conflicts.length) return false;
    if (Object.keys(vehicle).length && !item._vehicles.some(application => vehicleMatches(application, vehicle))) return false;
    if (validFilter(task) && !item.automotive.tasks.includes(task)) return false;
    if (validFilter(system) && !item.automotive.systems.includes(system)) return false;
    if (validFilter(spec) && !item._specs.includes(specKey(spec))) return false;
    for (const [key, value] of filters) {
      if (!valid(value)) continue;
      if (key === "license" && value === "open") {
        if (!["creative-commons", "public-domain"].includes(item.license)) return false;
      } else if (item[key] !== value.toLowerCase()) return false;
    }
    if (ids && !ids.includes(item.id)) return false;
    if (valid(domain) && item.domain_scope !== domain) return false;
    if (valid(duration)) {
      if (item.duration_seconds == null) return false;
      if (duration === "short" && item.duration_seconds >= 600) return false;
      if (duration === "medium" && (item.duration_seconds < 600 || item.duration_seconds >= 1800)) return false;
      if (duration === "long" && item.duration_seconds < 1800) return false;
    }
    if (valid(transcript)) {
      const wanted = ["available", "true", "1"].includes(transcript);
      if (Boolean(item.has_transcript) !== wanted) return false;
    }
    return true;
  });
  let groups = queryWords.map(word => [word]);
  let results = residual ? (queryWords.length ? filtered.filter(item => matches(item, groups)) : []) : filtered;
  let searchMode = Object.keys(interpretation.vehicle).length || interpretation.task || interpretation.spec ? "structured" : "literal";
  let expandedTopics = [];
  if (queryWords.length && !results.length) {
    for (const candidate of educationalCandidates(residual, queryWords)) {
      const expanded = filtered.filter(item => matches(item, candidate.groups));
      if (expanded.length) {
        results = expanded; groups = candidate.groups;
        searchMode = candidate.mode; expandedTopics = candidate.topics;
        break;
      }
    }
  }
  if (options.countOnly) return {total: results.length};
  const facets = Object.fromEntries(["category", "level", "language", "platform", "license"]
    .map(key => [key, facet(results, key)]));
  facets.transcript = facet(results, "has_transcript", value => value ? "available" : "missing");
  facets.domain = facet(results, "domain_scope");
  facets.content_format = facet(results, "pedagogical_format");
  facets.format = [{value: "video", count: results.length}];
  for (const field of ["task", "system", "spec"]) facets[field] = automotiveFacet(results, field);
  const score = item => groups.reduce((sum, group) => sum +
    (group.some(term => termMatch(item._titleTokens, normalize(item.title), term)) ? 5 : 0) +
    (group.some(term => termMatch(item._creatorTokens, normalize(item.creator), term)) ? 1.5 : 0) +
    (group.some(term => termMatch(item._tagTokens, normalize((item.tags || []).join(" ")), term)) ? 2 : 0), 0);
  const sorted = [...results];
  if (sort === "newest") sorted.sort((a, b) => {
    const left = a.published_at || "", right = b.published_at || "";
    return (left > right ? -1 : left < right ? 1 : 0) || a.id.localeCompare(b.id);
  });
  else if (sort === "duration") sorted.sort((a, b) =>
    (a.duration_seconds ?? Infinity) - (b.duration_seconds ?? Infinity) || a.id.localeCompare(b.id));
  else if (sort === "relevance") {
    if (queryWords.length) {
      const scores = new Map(sorted.map(item => [item.id, score(item)]));
      sorted.sort((a, b) => scores.get(b.id) - scores.get(a.id) || compareTitle(a, b));
    } else sorted.sort((a, b) => Number(selection(b)) - Number(selection(a)) || compareTitle(a, b));
  } else sorted.sort(compareTitle);
  const offset = options.offset ?? (page - 1) * perPage;
  return {items: sorted.slice(offset, offset + perPage).map(clean), total: results.length,
    page, per_page: perPage, pages: Math.ceil(results.length / perPage), facets, query: q, sort,
    search_mode: searchMode, expanded_topics: expandedTopics, engine: "static-prefix",
    inferred_vehicle: interpretation.vehicle, inferred_task: interpretation.task, inferred_spec: interpretation.spec,
    interpreted_fields: {vehicle: interpretation.vehicle, task: interpretation.task, spec: interpretation.spec},
    interpretation_conflicts: interpretation.conflicts, query_residual: residual};
}

export function catalogStats(catalog) {
  const items = catalog.items;
  const languageGroups = new Map(), languageSummary = new Map();
  for (const item of items) {
    const status = item.language_status || "unknown", language = item.language || "und";
    const key = JSON.stringify([language, status]);
    const group = languageGroups.get(key) || {language, status, count: 0};
    group.count++; languageGroups.set(key, group);
    const entry = languageSummary.get(language) || {language, total: 0, platform_declared: 0,
      source_caption_track: 0, estimated: 0, unknown: 0};
    entry.total++; entry[languageConfidence(language, status)]++; languageSummary.set(language, entry);
  }
  const facets = Object.fromEntries(["category", "language", "platform", "level", "license"]
    .map(key => [key, facet(items, key)]));
  facets.domain = facet(items, "domain_scope");
  facets.content_format = facet(items, "pedagogical_format");
  facets.format = [{value: "video", count: items.length}, {value: "guide", count: catalog.guides.length}, {value: "image", count: 0}];
  for (const field of ["task", "system", "spec"]) facets[field] = automotiveFacet(items, field);
  return {...catalog.stats, total_videos: items.length, total_guides: catalog.guides.length,
    total_images: 0, total_resources: items.length + catalog.guides.length,
    language_status_counts: [...languageGroups.values()].sort((a, b) =>
      a.language.localeCompare(b.language) || a.status.localeCompare(b.status)),
    language_summary: [...languageSummary.values()].sort((a, b) => b.total - a.total || a.language.localeCompare(b.language)),
    platforms: new Set(items.map(item => item.platform)).size,
    languages: new Set(items.map(item => item.language).filter(value => !["und", "mul"].includes(value))).size,
    categories: new Set(items.map(item => item.category)).size,
    with_transcript: items.filter(item => item.has_transcript).length,
    with_source_questions: items.filter(item => item.source_questions?.length).length,
    total_source_questions: items.reduce((total, item) => total + (item.source_questions?.length || 0), 0),
    with_vehicle_mentions: items.filter(item => item._vehicles.length).length,
    selected_videos: items.filter(item => item.review_status === "editorial_selection").length,
    verified_videos: items.filter(item => item.content_verified).length,
    reusable_videos: items.filter(item => ["creative-commons", "public-domain", "permission"].includes(item.license)).length,
    facets, engine: "static-prefix"};
}

export function videoDetail(catalog, id) {
  const item = catalog.byId.get(id);
  if (!item) return null;
  const related = catalog.items.filter(other => other.category === item.category && other.id !== id)
    .sort((a, b) => Number(b.language === item.language) - Number(a.language === item.language) || compareTitle(a, b))
    .slice(0, 6).map(clean);
  return {...clean(item), transcript: null, related};
}

function matchingGuides(catalog, params, interpretation) {
  if (interpretation.conflicts.length || Object.keys(interpretation.vehicle).length || interpretation.spec ||
      [...vehicleFilters, "spec", "system", "duration", "content_format"].some(key => validFilter(param(params, key)))) return [];
  const task = param(params, "task") || interpretation.task;
  const terms = wordsOf(interpretation.residual).filter(word => !automotiveStopwords.has(word));
  return catalog.guides.filter(guide => {
    if (validFilter(task) && guide.task !== task) return false;
    for (const [key, column] of [["language", "language"], ["platform", "platform"], ["category", "category"],
      ["level", "level"], ["license", "license"], ["domain", "domain_scope"]])
      if (validFilter(param(params, key)) && param(params, key) !== String(guide[column] || "")) return false;
    if (["available", "true", "1"].includes(param(params, "transcript"))) return false;
    if (param(params, "ids") && !param(params, "ids").split(",").includes(guide.id)) return false;
    const original = guide.guide || {};
    const text = ["title", "intro", "summary", "steps", "checklist", "fields", "missingDetailsMessage"]
      .map(key => discoveryText(original[key])).join(" ") + " " + (taskPhrases[guide.task] || []).join(" ");
    const words = wordsOf(text);
    return terms.every(term => words.some(word => word.startsWith(term)));
  }).sort(compareTitle);
}

export function searchResources(catalog, params = {}, options = {}) {
  const kind = param(params, "format", "all") || "all";
  if (!["all", "video", "guide", "image"].includes(kind)) throw new Error("Format de ressource invalide");
  const videoParams = Object.fromEntries(Object.entries(params instanceof URLSearchParams ? Object.fromEntries(params) : params)
    .filter(([key]) => key !== "format"));
  const interpretation = inferAutomotive(catalog, param(params, "q").trim(), params);
  const guides = matchingGuides(catalog, params, interpretation);
  const page = numberParam(params, "page", 1, 1000000), size = numberParam(params, "per_page", 24, 100);
  const start = (page - 1) * size, offset = kind === "all" ? Math.max(0, start - guides.length) : start;
  const videos = searchCatalog(catalog, videoParams, {countOnly: options.countOnly, offset});
  const total = (["all", "video"].includes(kind) ? videos.total : 0) + (["all", "guide"].includes(kind) ? guides.length : 0);
  if (options.countOnly) return {total};
  const items = ["all", "guide"].includes(kind) ? guides.slice(start, start + size) : [];
  if (["all", "video"].includes(kind)) items.push(...videos.items.slice(0, size - items.length));
  const facets = Object.fromEntries(Object.entries(videos.facets).map(([key, values]) =>
    [key, ["all", "video"].includes(kind) ? [...values] : []]));
  if (["all", "guide"].includes(kind)) {
    for (const [name, column] of [["category", "category"], ["level", "level"], ["language", "language"],
      ["platform", "platform"], ["license", "license"], ["domain", "domain_scope"], ["task", "task"], ["transcript", "transcript_status"]]) {
      const counts = new Map((facets[name] || []).map(item => [item.value, item.count]));
      for (const guide of guides) {
        const value = name === "transcript" ? "missing" : guide[column];
        if (value) counts.set(value, (counts.get(value) || 0) + 1);
      }
      facets[name] = [...counts].map(([value, count]) => ({value, count}))
        .sort((a, b) => b.count - a.count || (a.value < b.value ? -1 : a.value > b.value ? 1 : 0));
    }
  }
  facets.format = [{value: "video", count: videos.total}, {value: "guide", count: guides.length}, {value: "image", count: 0}];
  return {...videos, items, total, pages: Math.ceil(total / size), facets, format: kind,
    total_videos: videos.total, total_guides: guides.length, total_images: 0,
    ordering: "guides_first_then_videos", compatibility_verified: false};
}

export function guideDetail(catalog, id) {
  const resource = catalog.guides.find(guide => guide.id === id);
  return resource ? {resource} : null;
}

const discoveryFilters = [...vehicleFilters, "task", "system", "spec", "category", "level",
  "language", "platform", "license", "duration", "transcript", "domain", "ids", "format", "content_format"];
const discoveryContext = params => Object.fromEntries(discoveryFilters.map(key => [key, param(params, key)])
  .filter(([, value]) => validFilter(value)));
const discoveryText = value => value && typeof value === "object"
  ? Object.values(value).map(discoveryText).join(" ") : String(value || "");

function mergeTopicContext(topic, context) {
  const merged = {...context};
  for (const [key, value] of Object.entries(discoveryContext(topic.filters || {}))) {
    if (key in merged && (key === "spec" ? specKey(merged[key]) !== specKey(value) : normalize(merged[key]) !== normalize(value)))
      return null;
    merged[key] = value;
  }
  return merged;
}

function discoveryCount(catalog, params) {
  const key = JSON.stringify(Object.entries(params).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0));
  if (!catalog._discoveryCounts.has(key)) {
    if (catalog._discoveryCounts.size >= 512) catalog._discoveryCounts.delete(catalog._discoveryCounts.keys().next().value);
    catalog._discoveryCounts.set(key, searchResources(catalog, params, {countOnly: true}).total);
  }
  return catalog._discoveryCounts.get(key);
}

function discoveryTopics(catalog, config, context) {
  return (config.topics || []).slice(0, 100).filter(topic => topic && topic.enabled !== false).map(topic => {
    const filters = mergeTopicContext(topic, context);
    return {...topic, count: filters === null ? 0 : discoveryCount(catalog, {...filters, q: String(topic.query || "")}),
      filters: filters || {...context}, context_conflict: filters === null};
  });
}

function activeEditorialDates(item, shelf, now) {
  if (shelf.enabled !== true || item.enabled === false) return false;
  const reviewed = String(item.reviewedAt || shelf.reviewedAt || "");
  const expires = String(item.expiresAt || shelf.expiresAt || "");
  const zoned = value => /(?:Z|[+-]\d{2}:\d{2})$/.test(value);
  return zoned(reviewed) && zoned(expires) && Date.parse(reviewed) <= now && now < Date.parse(expires);
}

function discoveryShelves(catalog, config, context, now = Date.now()) {
  return (config.shelves || []).slice(0, 20).filter(Boolean).map(shelf => {
    const seen = new Set();
    const items = (shelf.items || []).slice(0, 12).filter(entry => {
      if (!entry || !activeEditorialDates(entry, shelf, now)) return false;
      const id = String(entry.videoId || ""), item = catalog.byId.get(id);
      if (!/^[A-Za-z0-9_:-]{1,100}$/.test(id) || seen.has(id) || item?.review_status !== "editorial_selection") return false;
      if (context.ids && !context.ids.split(",").includes(id)) return false;
      if (!discoveryCount(catalog, {...context, ids: id})) return false;
      seen.add(id);
      return true;
    }).map(entry => ({...entry, video: clean(catalog.byId.get(entry.videoId))}));
    return {...shelf, items};
  }).filter(shelf => shelf.items.length);
}

export function discoveryCatalog(catalog, params = {}, config = catalog.discovery, now = Date.now()) {
  const context = discoveryContext(params);
  return {version: config.version || 1, intents: (config.intents || []).slice(0, 20),
    topics: discoveryTopics(catalog, config, context), shelves: discoveryShelves(catalog, config, context, now),
    context, generated_at: new Date(now).toISOString(), policy: "explicit_filters_preserved"};
}

function oneTopicEdit(left, right) {
  if (left === right || Math.abs(left.length - right.length) > 1) return false;
  if (left.length === right.length) {
    const different = [...left].flatMap((letter, i) => letter !== right[i] ? [i] : []);
    return different.length === 1 || (different.length === 2 && different[1] === different[0] + 1 &&
      left[different[0]] === right[different[1]] && left[different[1]] === right[different[0]]);
  }
  const [shorter, longer] = left.length < right.length ? [left, right] : [right, left];
  let index = 0;
  while (index < shorter.length && shorter[index] === longer[index]) index++;
  return shorter.slice(index) === longer.slice(index + 1);
}

function topicPrediction(topic, query, context = {}) {
  const phrases = [
    ...(topic.aliases || []).filter(alias => typeof alias === "string").map(alias => [alias, 12, true]),
    ...(taskPhrases[topic.filters?.task] || []).map(alias => [alias, 14, true]),
    [discoveryText(topic.query), 8, false], [discoveryText(topic.label), 4, false],
  ];
  const terms = new Map();
  for (const [phrase, weight, editable] of phrases) {
    for (const match of phrase.matchAll(/[\p{L}\p{N}]+/gu)) {
      const word = normalize(match[0]);
      if (word.length < 3) continue;
      if (!terms.has(word) || weight > terms.get(word).weight)
        terms.set(word, {text: match[0], weight, editable: editable && /^\p{L}+$/u.test(word) &&
          !(match[0] === match[0].toUpperCase() && word.length <= 5)});
    }
  }
  const protectedWords = new Set([...vehicleFilters, "spec"].flatMap(key => wordsOf(context[key] || "")));
  const matches = [];
  let score = 0;
  for (const token of query.matchAll(/[\p{L}\p{N}]+/gu)) {
    const word = normalize(token[0]);
    if (automotiveStopwords.has(word) || protectedWords.has(word)) continue;
    const immutable = !/^\p{L}+$/u.test(word) || (token[0] === token[0].toUpperCase() && word.length <= 5);
    let target = word, kind = "exact";
    if (!terms.has(word)) {
      let candidates = immutable || word.length < 3 ? [] :
        [...terms.keys()].filter(term => terms.get(term).editable && term.startsWith(word));
      if (candidates.length) {
        candidates.sort((a, b) => terms.get(b).weight - terms.get(a).weight || a.length - b.length || (a < b ? -1 : a > b ? 1 : 0));
        target = candidates[0]; kind = "prefix";
      } else {
        candidates = immutable || word.length < 4 ? [] :
          [...terms.keys()].filter(term => terms.get(term).editable && term.length >= 4 && oneTopicEdit(word, term));
        if (candidates.length !== 1) continue;
        target = candidates[0]; kind = "typo";
      }
    }
    const value = terms.get(target);
    score += {exact: 24, prefix: 12, typo: 4}[kind] + value.weight;
    let replacement = kind === "exact" ? token[0] : value.text;
    if (token[0][0] === token[0][0].toUpperCase() && kind !== "exact")
      replacement = replacement[0].toUpperCase() + replacement.slice(1);
    matches.push({start: token.index, end: token.index + token[0].length, from: token[0], to: replacement, kind, term: target});
  }
  if (!matches.length || matches.filter(item => item.kind === "typo").length > 1) return null;
  for (const [phrase, weight] of phrases)
    if (wordsOf(phrase).length > 1 && phraseFound(normalize(query), phrase)) score += 30 + weight;
  const variant = replacements => {
    let completion = query;
    for (const item of [...replacements].reverse())
      completion = completion.slice(0, item.start) + item.to + completion.slice(item.end);
    const corrections = replacements.filter(item => item.from !== item.to).map(({from, to, kind}) => ({from, to, kind}));
    return {completion, corrections, match_basis: corrections.some(item => item.kind === "typo") ? "topic_typo" :
      corrections.length ? "prefix_completion" : "exact_terms"};
  };
  const variants = [variant(matches)];
  if (matches.length === 1) {
    const matched = matches[0];
    for (const [phrase, , editable] of [...phrases].sort((a, b) => b[1] - a[1])) {
      const words = wordsOf(phrase);
      if (!editable || words.length < 2 || words.length > 4 || !words.includes(matched.term)) continue;
      if (words.some(word => protectedWords.has(word) || /\d/.test(word))) continue;
      const candidate = variant([{...matched, to: phrase, kind: matched.kind === "typo" ? "typo" : "prefix"}]);
      if (!variants.some(item => item.completion === candidate.completion)) variants.push(candidate);
      if (variants.length >= 4) break;
    }
  }
  return {score, variants};
}

function topicScore(topic, query) {
  return topicPrediction(topic, query)?.score || 0;
}

export function suggestCatalog(catalog, params = {}, config = catalog.discovery) {
  const query = param(params, "q").trim();
  if (query.length > 300) throw new Error("Recherche limitée à 300 caractères");
  if (query && query.length < 2) return {query, suggestions: [], limit: 6};
  const context = discoveryContext(params), interpretation = inferAutomotive(catalog, query, params);
  if (interpretation.conflicts.length) return {query, suggestions: [], limit: 6, context, interpretation_conflicts: interpretation.conflicts};
  for (const [key, value] of Object.entries(interpretation.vehicle)) if (!(key in context)) context[key] = String(value);
  if (interpretation.spec && !context.spec) context.spec = interpretation.spec;
  const ranked = [];
  for (const [index, topic] of (config.topics || []).slice(0, 100).entries()) {
    if (!topic || typeof topic !== "object" || topic.enabled === false) continue;
    const filters = mergeTopicContext(topic, context);
    if (!filters) continue;
    const prediction = query ? topicPrediction(topic, query, context) : {
      score: 0, variants: [{completion: String(topic.query || ""), corrections: [], match_basis: "editorial_default"}]};
    if (prediction) ranked.push({topic, index, filters, ...prediction});
  }
  const defaults = config.defaultTopicIds || [];
  const editorialOrder = entry => !query && defaults.includes(entry.topic.id)
    ? defaults.indexOf(entry.topic.id) : defaults.length + entry.index;
  ranked.sort((a, b) => b.score - a.score || editorialOrder(a) - editorialOrder(b) || a.index - b.index);
  const items = [];
  for (const {topic, filters, variants} of ranked) {
    for (const prediction of variants) {
      const completion = prediction.completion;
      if (completion.length > 300) continue;
      const count = discoveryCount(catalog, {...filters, q: completion});
      if (!count) continue;
      const correction = prediction.match_basis === "topic_typo" ? {
        fr: "Petite faute possible dans un terme du sujet ; correction proposée.",
        en: "Possible small typo in a topic term; correction suggested.",
        es: "Posible errata en un término del tema; corrección sugerida."} : null;
      items.push({type: "topic", id: topic.id, label: topic.label || topic.id,
        query: completion, filters, count, ...prediction, correction, reason: correction || {
          fr: query ? "Question conservée ; seuls les mots du sujet sont complétés." : "Point de départ éditorial.",
          en: query ? "Question preserved; only topic words are completed." : "Editorial starting point.",
          es: query ? "Pregunta conservada; solo se completan los términos del tema." : "Punto de partida editorial."}});
      break;
    }
    if (items.length >= (query ? 3 : 5)) break;
  }
  if (query && items.length < 6 && ["all", "guide"].includes(context.format || "all")) {
    const found = searchResources(catalog, {...context, format: "guide", q: query, per_page: String(6 - items.length)});
    items.push(...found.items.map(guide => ({type: "guide", resource_type: "guide", id: guide.id,
      label: guide.title, query, filters: context, reason: {
        fr: "Guide RaceLink avec sources citées, correspondant à la recherche.",
        en: "RaceLink guide with cited sources matching the search.",
        es: "Guía RaceLink con fuentes citadas que coincide con la búsqueda."}})));
  }
  if (query && items.length < 6) {
    const result = searchCatalog(catalog, {...context, q: query, per_page: String(6 - items.length), sort: "title"});
    items.push(...result.items.map(item => ({type: "video", id: item.id, video_id: item.id, label: item.title, query,
      filters: context, reason: {fr: "Titre présent dans le catalogue, correspondant à la recherche et aux filtres.",
        en: "Existing catalog title matching the search and filters.",
        es: "Título existente que coincide con la búsqueda y los filtros."}})));
  }
  return {query, suggestions: items.slice(0, 6), limit: 6, policy: "existing_topics_and_titles", context};
}

export function recommendCatalog(catalog, params = {}, config = catalog.discovery, now = Date.now()) {
  const context = discoveryContext(params);
  let query = param(params, "q").trim(), inferredCategory = null;
  if (query.length > 300) throw new Error("Recherche limitée à 300 caractères");
  const interpretation = inferAutomotive(catalog, query, params);
  for (const [key, value] of Object.entries(interpretation.vehicle)) if (!(key in context)) context[key] = String(value);
  if (interpretation.spec && !context.spec) context.spec = interpretation.spec;
  const videoId = param(params, "video_id");
  if (videoId) {
    if (!/^[A-Za-z0-9_:-]{1,100}$/.test(videoId)) throw new Error("Identifiant vidéo invalide");
    const item = catalog.byId.get(videoId);
    if (item) {
      query = query || item.title;
      if (!context.category) context.category = inferredCategory = item.category;
    }
  }
  const sameFilters = filters => Object.keys(filters).length === Object.keys(context).length &&
    Object.entries(filters).every(([key, value]) => context[key] === value);
  let topics = discoveryTopics(catalog, config, context).filter(topic => topic.count > 0 && !interpretation.conflicts.length &&
    !(sameFilters(topic.filters) && normalize(topic.query || "") === normalize(query)));
  const related = topics.filter(topic => topicScore(topic, query) > 0 ||
    (interpretation.task && topic.filters.task === interpretation.task));
  if (query && (interpretation.task || (config.topics || []).some(topic => topicScore(topic, query) > 0))) topics = related;
  const defaults = config.defaultTopicIds || [], positions = new Map(topics.map((topic, index) => [topic.id, index]));
  const order = topic => defaults.includes(topic.id) ? defaults.indexOf(topic.id) : defaults.length + positions.get(topic.id);
  topics.sort((a, b) => topicScore(b, query) - topicScore(a, query) || order(a) - order(b));
  const ranked = [], usedIntents = new Set();
  for (const topic of topics) {
    const intent = topic.intentId || topic.intent || topic.id;
    if (topicScore(topic, query) > 0 || !usedIntents.has(intent)) { ranked.push(topic); usedIntents.add(intent); }
  }
  ranked.push(...topics.filter(topic => !ranked.includes(topic)));
  const selected = ranked.slice(0, 4).map(topic => {
    const lexical = topicScore(topic, query) > 0;
    return {...topic, match_basis: lexical ? "lexical_and_filters" : "context_filters",
      reason: {fr: lexical ? "Mots en commun et filtres conservés." : "Sujet disponible avec ces filtres.",
        en: lexical ? "Shared words and preserved filters." : "Topic available with these filters.",
        es: lexical ? "Palabras comunes y filtros conservados." : "Tema disponible con estos filtros."}};
  });
  return {topics: selected, shelves: interpretation.conflicts.length ? [] : discoveryShelves(catalog, config, context, now),
    context: {filters: context, query, video_id: videoId || null, inferred_category: inferredCategory},
    reason: {fr: "Propositions de sujets à ouvrir ; la recherche actuelle reste inchangée.",
      en: "Topic suggestions to open; the current search remains unchanged.",
      es: "Temas sugeridos para abrir; la búsqueda actual no cambia."},
    policy: "explicit_filters_preserved", interpretation_conflicts: interpretation.conflicts};
}

export async function loadCatalogPayload(catalogUrl, catalogGzipUrl, fetcher = fetch,
  Decompressor = globalThis.DecompressionStream) {
  if (catalogGzipUrl && typeof Decompressor === "function") {
    try {
      const compressed = await fetcher(catalogGzipUrl);
      if (!compressed.ok) throw new Error("Catalogue compressé indisponible");
      const buffer = await compressed.arrayBuffer(), bytes = new Uint8Array(buffer);
      // Some hosts set Content-Encoding and transparently decode the response.
      const body = bytes[0] === 0x1f && bytes[1] === 0x8b
        ? new Blob([buffer]).stream().pipeThrough(new Decompressor("gzip")) : buffer;
      return await new Response(body).json();
    } catch {
      // The ordinary JSON is the portable fallback; never requires a polyfill.
    }
  }
  const response = await fetcher(catalogUrl);
  if (!response.ok) throw new Error("Catalogue statique introuvable");
  return response.json();
}

let loadedCatalog, catalogLocation;
if (typeof self !== "undefined" && typeof self.postMessage === "function" && typeof document === "undefined") {
  self.onmessage = async event => {
    const {id, type, path, catalogUrl, catalogGzipUrl} = event.data;
    try {
      let result;
      if (type === "init") {
        catalogLocation = new URL(catalogUrl);
        const [payload, discoveryResponse] = await Promise.all([
          loadCatalogPayload(catalogLocation, catalogGzipUrl),
          fetch(new URL("../discovery-catalog.json", catalogLocation))
        ]);
        loadedCatalog = prepareCatalog(payload);
        if (discoveryResponse.ok) loadedCatalog.discovery = await discoveryResponse.json();
        result = {ready: true, total: loadedCatalog.items.length};
      } else {
        if (!loadedCatalog) throw new Error("Catalogue pas encore chargé");
        const url = new URL(path, catalogLocation);
        const route = decodeURIComponent(url.pathname).replace(/^.*\/api\//, "/api/");
        if (route === "/api/stats") result = catalogStats(loadedCatalog);
        else if (route === "/api/resources" || route === "/api/resources/") result = searchResources(loadedCatalog, url.searchParams);
        else if (route.startsWith("/api/resources/guide/")) {
          result = guideDetail(loadedCatalog, route.slice("/api/resources/guide/".length));
          if (!result) throw new Error("Guide introuvable");
        }
        else if (route === "/api/discovery") result = discoveryCatalog(loadedCatalog, url.searchParams);
        else if (route === "/api/suggestions") result = suggestCatalog(loadedCatalog, url.searchParams);
        else if (route === "/api/recommendations") result = recommendCatalog(loadedCatalog, url.searchParams);
        else if (route === "/api/vehicle-options") result = vehicleOptions(loadedCatalog, url.searchParams);
        else if (route === "/api/videos" || route === "/api/videos/") result = searchCatalog(loadedCatalog, url.searchParams);
        else if (route === "/api/health") result = {status: "ok", service: "focus-academy-static"};
        else if (route.startsWith("/api/videos/")) {
          const videoId = route.slice("/api/videos/".length);
          result = videoDetail(loadedCatalog, videoId);
          if (!result) throw new Error("Vidéo introuvable");
          const file = loadedCatalog.byId.get(videoId)._transcript_file;
          if (file) {
            if (!/^[a-f0-9]{24}\.json$/.test(file)) throw new Error("Référence transcription invalide");
            const response = await fetch(new URL("transcripts/" + file, catalogLocation));
            if (!response.ok) throw new Error("Transcription indisponible");
            result.transcript = await response.json();
          }
        } else throw new Error("Route catalogue inconnue");
      }
      self.postMessage({id, result});
    } catch (error) {
      self.postMessage({id, error: error.message || "Erreur du catalogue"});
    }
  };
}
