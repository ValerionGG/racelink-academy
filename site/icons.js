/**
 * RaceLink — ligne de trajectoire, v1.
 * Original fixed geometry; no external assets, SVG input or platform logos.
 * Decorative only: the surrounding control supplies its accessible name.
 */
const drawings = Object.freeze({
  search: 'M18 11a7 7 0 1 1-14 0 7 7 0 0 1 14 0ZM20 20l-4-4',
  home: 'M3 11 12 4l9 7v9h-6v-6H9v6H3Z',
  library: 'M4 4.5h5v15H4ZM12 4.5v15M16 5l4 14.5M3 20.5h18',
  route: 'M5 21V4h11l-2 4 2 4H5',
  help: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7M12 17h.01',
  bookmark: 'M6 3h12v18l-6-4-6 4Z',
  car: 'M4 10.5 6.5 5h11l2.5 5.5M3 11l2-1h14l2 1v7H3ZM5 18v2M19 18v2M6 13.5h2M16 13.5h2',
  wrench: 'M14 3.5a5.6 5.6 0 0 0-5.3 7.4l-5 5a3 3 0 0 0 4.3 4.3l5-5a5.6 5.6 0 0 0 7.4-5.3L17 13l-4-4 3.1-3.4M6.5 17.5l.1-.1',
  steering: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM3.7 9h16.6M4 12l5 2 1.5 6M20 12l-5 2-1.5 6M13.5 12a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z',
  simracing: 'M4 3.5h16v10h-4M8 13.5H4v-10M8 20.5h8M12 18v2.5M16 14a4 4 0 1 1-8 0 4 4 0 0 1 8 0ZM8.3 12.5h7.4M12 14v3.8',
  engineering: 'M3.5 4v16.5H21M6 15.5 10 10l4 3 6-8M17 5h3v3',
  camera: 'M5 6h3l1.5-2h5L16 6h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2ZM15.5 12.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z',
  briefcase: 'M4 7h16a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1ZM9 7V4h6v3M3 13h18',
  career: 'M3.5 20h5v-5H14v-5h6.5V3.5M15.5 3.5h5v5',
  fitness: 'M3 12h4l3-7 4 14 3-7h4',
  play: 'M8 4.5 20 12 8 19.5Z',
  shorts: 'M9.5 3h5A2.5 2.5 0 0 1 17 5.5v13a2.5 2.5 0 0 1-2.5 2.5h-5A2.5 2.5 0 0 1 7 18.5v-13A2.5 2.5 0 0 1 9.5 3ZM11 10l3 2-3 2Z',
  chart: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  globe: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM12 3c-4.7 4.7-4.7 13.3 0 18M12 3c4.7 4.7 4.7 13.3 0 18M3 12h18',
  filter: 'M4 6h4M12 6h8M4 12h10M18 12h2M4 18h2M10 18h10M8 4v4h4V4ZM14 10v4h4v-4ZM6 16v4h4v-4Z',
  'arrow-right': 'M3.5 12h17M14 5.5l6.5 6.5-6.5 6.5',
  'arrow-up-right': 'M5 19 19 5M6.5 5H19v12.5',
  'chevron-down': 'M5.5 8.5 12 15l6.5-6.5',
  close: 'M5.5 5.5l13 13M18.5 5.5l-13 13',
  menu: 'M3.5 5.5h17M3.5 12h17M3.5 18.5H16',
  check: 'M4 12.5 9 17.5 20 6.5',
  clock: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM12 6.5V12l4.5 2.5',
  oil: 'M4 8.5h10v9H4ZM7 5h4M9 5v3.5M4 10.5H2v5h2M14 10l5-2 2 2-7 5M20 14.5c-.9 1.2-1.5 2-1.5 2.8a1.5 1.5 0 0 0 3 0c0-.8-.6-1.6-1.5-2.8Z',
  wheel: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM17.5 12a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0ZM12 6.5V10M7 10.3l3.3 1.1M8.8 16.5l2.1-2.9M15.2 16.5l-2.1-2.9M17 10.3l-3.3 1.1',
  shield: 'M12 3 20 6v5.5c0 4.4-3.5 7.5-8 9.5-4.5-2-8-5.1-8-9.5V6ZM8 12l2.5 2.5L16 9',
});

export const iconNames = Object.freeze(Object.keys(drawings));

export const categoryIcon = Object.freeze({
  all: 'library', driving: 'steering', pilotage: 'steering', engineering: 'engineering',
  mechanics: 'wrench', simracing: 'simracing', media: 'camera', business: 'chart',
  career: 'briefcase', fitness: 'fitness', other: 'library',
});

/** Return safe SVG markup. size is a finite number in CSS pixels, clamped 12–96. */
export function icon(name, {size = 24, className = ''} = {}) {
  const key = typeof name === 'string' && Object.hasOwn(drawings, name) ? name : 'help';
  const pixels = typeof size === 'number' && Number.isFinite(size)
    ? Math.round(Math.min(96, Math.max(12, size)) * 100) / 100 : 24;
  // No user value is interpolated as SVG geometry or unrestricted markup.
  const classes = typeof className === 'string' ? className.slice(0, 256).split(/\s+/)
    .filter(token => /^[a-zA-Z_-][a-zA-Z0-9_-]*$/.test(token)).slice(0, 8) : [];
  return `<svg class="rl-icon${classes.length ? ` ${classes.join(' ')}` : ''}" width="${pixels}" height="${pixels}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg"><path d="${drawings[key]}"/></svg>`;
}
