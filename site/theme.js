/* RaceLink Academy themes-v22. Classic synchronous script: load before CSS. */
(function initRaceLinkTheme(window, document) {
  'use strict';
  if (window.RaceLinkTheme) return;

  const KEY = 'rl-academy-theme';
  const root = document.documentElement;
  const validTheme = value => value === 'light' || value === 'dark';
  const labels = {
    fr: {group:'Apparence', light:'Clair', dark:'Sombre', lightTitle:'Thème clair', darkTitle:'Thème sombre'},
    en: {group:'Appearance', light:'Light', dark:'Dark', lightTitle:'Light theme', darkTitle:'Dark theme'},
    es: {group:'Apariencia', light:'Claro', dark:'Oscuro', lightTitle:'Tema claro', darkTitle:'Tema oscuro'},
  };
  let storage = null, media = null, explicit = null, current = null;
  let locale = 'fr';
  try { storage = window.localStorage; } catch { /* Restricted browser storage. */ }
  try { const saved = storage?.getItem(KEY); if (validTheme(saved)) explicit = saved; } catch { /* Use system preference. */ }
  try { media = window.matchMedia?.('(prefers-color-scheme: dark)') || null; } catch { /* Light is the accessible fallback. */ }

  function getState() {
    return {theme:current, preference:explicit, followsSystem:explicit === null};
  }

  function syncThemeColor() {
    document.querySelectorAll('meta[name="theme-color"]').forEach(meta => {
      meta.setAttribute('content', current === 'dark' ? '#101112' : '#f5f6f8');
    });
  }

  function refreshControls() {
    const copy = labels[locale];
    document.querySelectorAll('[data-theme-controls]').forEach(group => {
      group.setAttribute('aria-label', copy.group);
    });
    document.querySelectorAll('[data-theme-choice]').forEach(button => {
      const theme = button.dataset.themeChoice;
      if (!validTheme(theme)) return;
      button.setAttribute('aria-pressed', String(theme === current));
      button.setAttribute('aria-label', copy[`${theme}Title`]);
      button.setAttribute('title', copy[`${theme}Title`]);
      const label = button.querySelector('[data-theme-label]');
      if (label && label.textContent !== copy[theme]) label.textContent = copy[theme];
    });
  }

  function updateThemeLabels(ui = root.lang) {
    const code = String(ui || '').toLowerCase().split(/[-_]/)[0];
    locale = Object.prototype.hasOwnProperty.call(labels, code) ? code : 'fr';
    refreshControls();
  }

  function applyTheme() {
    const theme = explicit || (media?.matches ? 'dark' : 'light');
    const changed = current !== theme;
    current = theme;
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    syncThemeColor();
    refreshControls();
    if (changed && typeof window.CustomEvent === 'function') {
      document.dispatchEvent(new window.CustomEvent('rl:theme-change', {detail:getState()}));
    }
  }

  function setTheme(theme) {
    if (!validTheme(theme)) return false;
    explicit = theme;
    try { storage?.setItem(KEY, theme); } catch { /* Choice still applies for this page. */ }
    applyTheme();
    return true;
  }

  // Initial application is synchronous, before DOMContentLoaded and before CSS.
  applyTheme();
  window.RaceLinkTheme = Object.freeze({setTheme, getState, updateThemeLabels, refresh:refreshControls});

  document.addEventListener('click', event => {
    const button = event.target?.closest?.('[data-theme-choice]');
    if (!button || button.disabled || button.getAttribute('aria-disabled') === 'true') return;
    if (setTheme(button.dataset.themeChoice)) event.preventDefault();
  });
  const systemChanged = () => { if (explicit === null) applyTheme(); };
  if (media) {
    if (typeof media.addEventListener === 'function') media.addEventListener('change', systemChanged);
    else if (typeof media.addListener === 'function') media.addListener(systemChanged);
  }
  window.addEventListener('storage', event => {
    if (event.key !== KEY && event.key !== null) return;
    if (event.storageArea && storage && event.storageArea !== storage) return;
    explicit = validTheme(event.newValue) ? event.newValue : null;
    applyTheme();
  });

  function syncLabels() { updateThemeLabels(root.lang); syncThemeColor(); }
  // Only new theme controls or the interface language trigger DOM refreshes.
  // Catalogue card rendering therefore does not repeatedly visit all controls.
  if (typeof window.MutationObserver === 'function') {
    new window.MutationObserver(records => {
      if (records.some(record => record.type === 'attributes' && record.target === root && record.attributeName === 'lang')) {
        syncLabels();
      } else if (records.some(record => record.type === 'childList' && [...record.addedNodes].some(node =>
        node.nodeType === 1 && (node.matches?.('[data-theme-controls],[data-theme-choice]') || node.querySelector?.('[data-theme-controls],[data-theme-choice]'))
      ))) refreshControls();
    }).observe(root, {attributes:true, attributeFilter:['lang'], childList:true, subtree:true});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', syncLabels, {once:true});
  syncLabels();
})(window, document);
