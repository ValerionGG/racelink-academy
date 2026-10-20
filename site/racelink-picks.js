/* Explicit editorial picks. No network requests, ratings, or certification claims. */
export function createRaceLinkPicks({escape, t, getUi}) {
  const allowedKinds = new Set(["video", "guide", "image"]);
  const picks = new Map();
  const fallbackEscape = value => String(value ?? "").replace(/[&<>"']/g, character =>
    ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[character]);
  const e = typeof escape === "function" ? value => escape(String(value ?? "")) : fallbackEscape;
  const locale = () => ["fr", "en", "es"].includes(getUi?.()) ? getUi() : "fr";
  const tr = (fr, en, es) => typeof t === "function" ? t(fr, en, es) : ({fr, en, es})[locale()];
  const localized = value => typeof value === "string" ? value : value && typeof value === "object"
    ? String(value[locale()] || value.fr || value.en || value.es || "") : "";
  const copyText = value => typeof value === "string" ? value : value && typeof value === "object"
    ? Object.fromEntries(["fr", "en", "es"].filter(key => typeof value[key] === "string").map(key => [key, value[key]]))
    : "";
  const keyOf = (kind, id) => allowedKinds.has(kind) && typeof id === "string" && id.trim() && id.length <= 300
    ? `${kind}:${id}` : null;

  function timestamp(value) {
    if (typeof value !== "string") return NaN;
    const match = value.match(/^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d{1,3})?)?(Z|[+-]\d{2}:\d{2}))?$/);
    if (!match) return NaN;
    const [, y, m, d, h, min, sec, zone] = match;
    const year = Number(y), month = Number(m), day = Number(d);
    const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
    const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if (month < 1 || month > 12 || day < 1 || day > days[month - 1] ||
        (h && Number(h) > 23) || (min && Number(min) > 59) || (sec && Number(sec) > 59)) return NaN;
    if (zone && zone !== "Z" && (Number(zone.slice(1, 3)) > 23 || Number(zone.slice(4)) > 59)) return NaN;
    return Date.parse(value);
  }

  function add(kind, id, record, parent = {}, author = "") {
    const key = keyOf(kind, id);
    if (!key || !record || typeof record !== "object") return;
    const enabled = (record.enabled ?? parent.enabled) === true &&
      (kind !== "video" || parent.enabled === true);
    const reviewedAt = record.reviewedAt ?? parent.reviewedAt;
    const expiresAt = record.expiresAt ?? parent.expiresAt;
    const reviewed = timestamp(reviewedAt), expires = timestamp(expiresAt);
    if (!enabled || !Number.isFinite(reviewed) || !Number.isFinite(expires) || reviewed >= expires) return;
    const evidence = record.evidence && typeof record.evidence === "object" ? record.evidence : {};
    const pick = {kind, id, enabled, reviewed, expires, reviewedAt, expiresAt,
      reason: copyText(record.reason), basis: typeof evidence.basis === "string" ? evidence.basis : "",
      evidenceNote: copyText(evidence.note), author: copyText(author),
      attribution: copyText(record.attribution)};
    if (!picks.has(key)) picks.set(key, []);
    picks.get(key).push(pick);
  }

  function clear(kinds) {
    for (const [key, values] of picks) if (kinds.includes(values[0]?.kind)) picks.delete(key);
  }

  function setVideos(shelves) {
    clear(["video"]);
    for (const shelf of Array.isArray(shelves) ? shelves : []) {
      if (!shelf || shelf.enabled !== true) continue;
      for (const item of Array.isArray(shelf.items) ? shelf.items : []) {
        const video = item?.video;
        if (!video || video.review_status !== "editorial_selection") continue;
        if (item.videoId && item.videoId !== video.id) continue;
        add("video", video.id, item, shelf, video.creator);
      }
    }
  }

  function setResources(resources) {
    clear(["guide", "image"]);
    for (const item of Array.isArray(resources) ? resources : []) {
      if (!item || !["guide", "image"].includes(item.kind)) continue;
      add(item.kind, item.id, item, {}, item.creator || item.author);
    }
  }

  function current(kind, id) {
    const key = keyOf(kind, id);
    if (!key) return null;
    const now = Date.now();
    return (picks.get(key) || []).filter(pick => pick.enabled && pick.reviewed <= now && now < pick.expires)
      .sort((left, right) => right.reviewed - left.reviewed)[0] || null;
  }

  const has = (kind, id) => Boolean(current(kind, id));
  const label = () => tr("Proposé par RaceLink", "Suggested by RaceLink", "Propuesto por RaceLink");

  function badge(kind, id, {overlay = false, compact = false} = {}) {
    if (!has(kind, id)) return "";
    const classes = ["racelink-pick", overlay ? "racelink-pick--overlay" : "", compact ? "racelink-pick--compact" : ""]
      .filter(Boolean).join(" ");
    return `<span class="${classes}" data-pick-kind="${e(kind)}" data-pick-id="${e(id)}"><span class="racelink-pick-mark" aria-hidden="true">RL</span><span>${e(label())}</span></span>`;
  }

  function basisLabel(basis) {
    const labels = {
      public_video_metadata: ["Revue des métadonnées publiques", "Public metadata review", "Revisión de metadatos públicos"],
      authorized_transcript: ["Revue d’une transcription source autorisée", "Authorized source transcript review", "Revisión de una transcripción original autorizada"],
      official_sources: ["Revue à partir de sources officielles", "Review using official sources", "Revisión con fuentes oficiales"],
      editorial_review: ["Revue éditoriale", "Editorial review", "Revisión editorial"],
      public_image_metadata: ["Revue des métadonnées de l’image", "Image metadata review", "Revisión de metadatos de la imagen"],
      generated_illustration: ["Illustration éditoriale", "Editorial illustration", "Ilustración editorial"],
    };
    return labels[basis] ? tr(...labels[basis]) : basis ||
      tr("Base de revue non précisée", "Review basis not specified", "Base de revisión no especificada");
  }

  function note(kind, id) {
    const pick = current(kind, id);
    if (!pick) return "";
    const date = value => new Intl.DateTimeFormat(locale(), {dateStyle: "medium", timeZone: "UTC"}).format(value);
    const reason = localized(pick.reason) || tr("Ressource incluse dans la sélection éditoriale RaceLink.",
      "Resource included in RaceLink’s editorial selection.", "Recurso incluido en la selección editorial de RaceLink.");
    const evidence = localized(pick.evidenceNote);
    const author = localized(pick.attribution) || localized(pick.author);
    const credit = author
      ? `${tr("Attribution :", "Attribution:", "Atribución:")} ${author}`
      : tr("Attribution : consulter la source d’origine.", "Attribution: see the original source.", "Atribución: consulta la fuente original.");
    return `<details class="racelink-pick-note" data-pick-kind="${e(kind)}" data-pick-id="${e(id)}"><summary>${e(tr("Pourquoi RaceLink le propose ?", "Why does RaceLink suggest this?", "¿Por qué lo propone RaceLink?"))}</summary><p class="racelink-pick-reason">${e(reason)}</p><p>${e(basisLabel(pick.basis))}${evidence ? ` — ${e(evidence)}` : ""}</p><small>${e(tr("Revu le", "Reviewed", "Revisado"))} ${e(date(pick.reviewed))} · ${e(tr("À réexaminer avant le", "Review again before", "Revisar antes del"))} ${e(date(pick.expires))}</small><p class="racelink-pick-attribution">${e(credit)}</p></details>`;
  }

  return {setVideos, setResources, has, badge, note};
}
