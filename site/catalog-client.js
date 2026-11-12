/* Same contract locally through Python or in a static preview through a Web Worker. */
(() => {
  "use strict";
  const script = document.currentScript;
  const base = new URL("./", script ? script.src : window.location.href);
  let modePromise, workerPromise, worker;
  let sequence = 0;
  const pending = new Map();

  async function resolveMode() {
    if (!modePromise) {
      modePromise = fetch(new URL("catalog/config.json", base), {cache: "no-store"})
        .then(response => response.ok ? response.json() : {mode: "api"})
        .catch(() => ({mode: "api"}));
    }
    return modePromise;
  }

  function workerRequest(message) {
    return new Promise((resolve, reject) => {
      const id = ++sequence;
      const timeout = setTimeout(() => {
        pending.delete(id);
        reject(new Error("Le catalogue met trop de temps à répondre."));
      }, message.type === "init" ? 120000 : 60000);
      pending.set(id, {resolve, reject, timeout});
      worker.postMessage({id, ...message});
    });
  }

  async function ensureWorker(mode) {
    if (!workerPromise) {
      workerPromise = (async () => {
        if (!window.Worker) throw new Error("Ce navigateur ne prend pas en charge la recherche locale.");
        worker = new Worker(new URL("catalog-worker.js?v=themes-v48", base), {type: "module"});
        worker.onmessage = event => {
          const entry = pending.get(event.data.id);
          if (!entry) return;
          pending.delete(event.data.id);
          clearTimeout(entry.timeout);
          event.data.error ? entry.reject(new Error(event.data.error)) : entry.resolve(event.data.result);
        };
        worker.onerror = () => {
          for (const entry of pending.values()) {
            clearTimeout(entry.timeout);
            entry.reject(new Error("Impossible de charger le moteur du catalogue."));
          }
          pending.clear();
        };
        const catalogUrl = new URL("catalog/" + (mode.catalog || "catalog.json"), base);
        const gzipUrl = mode.compression === "gzip" && mode.compressed_catalog
          ? new URL("catalog/" + mode.compressed_catalog, base) : null;
        // Config is revalidated on every visit; the digest avoids a stale
        // browser/CDN response when a new catalog has just been published.
        if (mode.catalog_sha256) {
          catalogUrl.searchParams.set("v", mode.catalog_sha256);
          if (gzipUrl) gzipUrl.searchParams.set("v", mode.catalog_sha256);
        }
        await workerRequest({
          type: "init", catalogUrl: catalogUrl.href,
          ...(gzipUrl ? {catalogGzipUrl: gzipUrl.href} : {}),
        });
      })();
    }
    return workerPromise;
  }

  let snapshotPromise, warmed = false;
  // Precomputed answers let the home page appear before the full catalogue has loaded.
  function loadSnapshot(mode) {
    if (!snapshotPromise) {
      const url = new URL("catalog/home-snapshot.json", base);
      if (mode.catalog_sha256) url.searchParams.set("v", mode.catalog_sha256);
      snapshotPromise = fetch(url)
        .then(response => response.ok ? response.json() : null)
        .then(data => data && data.catalog_sha256 === mode.catalog_sha256 ? data.responses : null)
        .catch(() => null);
    }
    return snapshotPromise;
  }

  window.getCatalogJson = async function getCatalogJson(path) {
    const mode = await resolveMode();
    if (mode.mode === "static") {
      const responses = await loadSnapshot(mode);
      if (responses && Object.hasOwn(responses, String(path))) {
        if (!warmed) { warmed = true; setTimeout(() => ensureWorker(mode).catch(() => {}), 2500); }
        return structuredClone(responses[String(path)]);
      }
      await ensureWorker(mode);
      return workerRequest({type: "request", path: String(path)});
    }
    const response = await fetch(path);
    if (!response.ok) throw new Error(`Catalogue HTTP ${response.status}`);
    return response.json();
  };
  window.getCatalogMode = async () => (await resolveMode()).mode;
})();
