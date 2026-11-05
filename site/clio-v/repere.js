const manualOrigin = 'https://www.user-manual.renault.com';
const vehicle = '/fr/content/clio/getting-know-your-vehicle/';
const engineAccess = '/fr/content/clio/maintenance/accessing-engine-levels/';
const videos = '/fr/notice/13326/videos';

const topics = [
  {
    page: vehicle + 'driving-position/poste-de-conduite-direction-gauche',
    title: 'Se repérer au volant',
    preview: 'Sur le plan Renault à 24 repères, le n° 6 désigne la manette des essuie-glaces, le n° 8 l’écran central et le n° 22 la commande du capot.',
    actions: [
      ['Voir les 24 commandes'],
      ['Repérer la commande du capot', engineAccess + 'capot-moteur'],
    ],
  },
  {
    page: vehicle + 'e-tech-full-hybrid-vehicle-hev/presentation',
    title: 'Situer les batteries de l’hybride',
    preview: 'Sur l’E-Tech 145, la batterie de traction se trouve sous le plancher arrière et la batterie de 12 V dans le coffre. Le dessin situe aussi les deux moteurs.',
    actions: [
      ['Voir le schéma hybride'],
      ['Suivre les flux d’énergie', vehicle + 'e-tech-full-hybrid-vehicle-hev/fonctionnement'],
    ],
  },
  {
    page: vehicle + 'lpg-vehicle/presentation',
    title: 'Lire la jauge GPL',
    preview: 'Sur l’Eco-G 100, les témoins du sélecteur distinguent le GPL de l’essence. Renault illustre ces témoins et le remplissage du réservoir GPL.',
    actions: [
      ['Identifier les témoins'],
      ['Voir le remplissage GPL', vehicle + 'lpg-vehicle/reservoir-gpl'],
    ],
  },
  {
    page: '/fr/content/clio/maintenance/acces-moteur-niveaux',
    title: 'Retrouver la jauge d’huile',
    preview: 'Les dessins de la notice distinguent les jauges et les bouchons selon le moteur. La qualité d’huile à utiliser figure dans le document d’entretien de votre voiture.',
    actions: [
      ['Voir les jauges et les niveaux', engineAccess + 'huile-moteur'],
      ['Repérer les autres réservoirs', engineAccess + 'niveaux-filtres'],
    ],
  },
  {
    page: videos,
    title: 'Voir un geste en vidéo',
    preview: 'Renault présente 28 démonstrations pour cette édition de la notice. Choisissez un geste pour accéder directement à sa vidéo.',
    actions: [
      ['Utiliser le kit de gonflage', videos + '#video-teaser-content-143322'],
      ['Contrôler les liquides', videos + '#video-teaser-content-143323'],
      ['Les 28 démonstrations'],
    ],
  },
];

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}

/** Render inside a labelled page section. Links open the matching official guide. */
export function renderOfficialSystems(root, data) {
  if (!root) return;
  root.replaceChildren();
  if (data?.model !== 'Renault Clio V phase 2') return;

  const edition = data.date_editions?.find(item => item.id === '13326');
  if (!edition) return;
  const title = element('h2', 'Où se trouve cette commande ?');
  const period = element('p', 'Schémas et vidéos Renault pour la Clio 5 du 17 mars au 14 septembre 2025. Les commandes visibles dépendent de la finition et des options.');
  const otherEditions = element('a', 'Choisir une autre période');
  otherEditions.href = '#notices';
  period.append(' ', otherEditions);

  const cards = element('div', '', 'manuals');
  for (const topic of topics) {
    const card = element('article');
    const links = element('div', '', 'source-links');
    for (const [label, path = topic.page] of topic.actions) {
      const link = element('a', label);
      link.href = new URL(path, manualOrigin).href;
      links.append(link);
    }
    card.append(element('h3', topic.title), element('p', topic.preview), links);
    cards.append(card);
  }
  root.append(title, period, cards);
}
