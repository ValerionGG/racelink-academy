---
version: alpha
name: RaceLink Academy
description: V20 published and checked; interaction checks and final CSS verification retain their respective scopes.
colors:
  primary: "#bb1830"
  brand: "#ff2330"
  canvas: "#f5f5f4"
  results-canvas: "#f0f1f3"
  surface: "#ffffff"
  on-surface: "#17181a"
  muted: "#5e6065"
  border: "#dedfdf"
  accent-soft: "#fff0f2"
  neutral-soft: "#ececed"
  shell: "#111214"
  shell-muted: "#b4b5b8"
typography:
  body:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 15px
    lineHeight: 1.6
  brand:
    fontFamily: "Orbitron, Onest, system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: 0px
  hero:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 62px
    fontWeight: 650
    lineHeight: 1.04
    letterSpacing: -0.04em
  hero-mobile:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 43px
    fontWeight: 650
    lineHeight: 1.05
    letterSpacing: -1.6px
  hero-compact:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 37px
    fontWeight: 650
    lineHeight: 1.05
    letterSpacing: -1.3px
  video-title:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 24px
    fontWeight: 650
    lineHeight: 1.3
    letterSpacing: -0.5px
  guide-title:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 25px
    fontWeight: 650
    lineHeight: 1.3
    letterSpacing: -0.55px
rounded:
  surface: 12px
  resource-photo: 0px
  resource-surface: 16px
  video-surface-mobile: 12px
  guide-reader-photo: 10px
  guide-reader-photo-mobile: 8px
  search: 12px
  compact-control: 6px
  guide-control: 9px
  brand-mark: 9px
  dialog: 18px
spacing:
  desktop-page-inline: 48px
  mobile-page-inline: 20px
  compact-page-inline: 16px
  catalog-compact-page-inline: 12px
  hero-columns: 52px
  resource-columns: 28px
  resource-rows: 28px
  resource-gap-mobile: 22px
  guide-reader-columns: 40px
components:
  masthead:
    height: 80px
    backgroundColor: "{colors.shell}"
  masthead-mobile:
    height: 70px
    backgroundColor: "{colors.shell}"
  resource-photo:
    rounded: "{rounded.resource-photo}"
    aspectRatio: "16 / 9"
  topic-photo:
    rounded: "{rounded.guide-reader-photo}"
    aspectRatio: "4 / 3"
  hero-photo-mobile:
    rounded: "{rounded.guide-reader-photo}"
    aspectRatio: "16 / 10"
  guide-reader-photo:
    aspectRatio: "4 / 3"
    rounded: "{rounded.guide-reader-photo}"
  guide-reader-photo-mobile:
    aspectRatio: "16 / 10"
    rounded: "{rounded.guide-reader-photo-mobile}"
  focus-ring:
    color: "{colors.primary}"
    outlineWidth: 3px
    outlineOffset: 4px
  press-motion:
    transitionDuration: 150ms
    transitionTimingFunction: "cubic-bezier(.23,1,.32,1)"
  control-motion:
    transitionDuration: 180ms
    transitionTimingFunction: ease
  discovery-photo-motion:
    transitionDuration: 400ms
    transitionTimingFunction: "cubic-bezier(.23,1,.32,1)"
  guide-photo-motion:
    transition: none
  video-photo-motion:
    transitionDuration: 200ms
    transitionTimingFunction: ease
  video-reader-motion:
    transitionDuration: 160ms
    transitionTimingFunction: ease
  filter-panel:
    width: 580px
    rounded: 0px
  video-reader:
    maxWidth: 1240px
  guide-reader:
    maxWidth: 1180px
  reduced-motion:
    animation: none
    transition: none
    scrollBehavior: auto
---

# Interface RaceLink Academy — Workshop V20

**Version `workshop-v20` publiée et vérifiée, 23 octobre 2026.** [Ouvrir RaceLink Academy](https://valeriongg.github.io/racelink-academy/?release=workshop-v20). Référence finale publiée : [`17ea9abab52b9028b5863db61e6537dd939a3be7`](https://github.com/ValerionGG/racelink-academy/commit/17ea9abab52b9028b5863db61e6537dd939a3be7), [workflow 39997940444](https://github.com/ValerionGG/racelink-academy/actions/runs/39997940444). Les interactions ont été contrôlées sur [`5a48d1f`](https://github.com/ValerionGG/racelink-academy/commit/5a48d1fc2eebd0728079b79666e276f00ae43043) ; le contrôle HTTP et les deux finitions CSS ont été vérifiés sur `17ea9ab` : fond blanc des sujets associés et libellé « Ma voiture » complet à 320 px. [Validation détaillée](research/product-redesign-v20/VALIDATION.md).

Cette itération refond **la recherche, les filtres, les cartes et les lecteurs**. L'accueil photographique V19 est conservé. [Décisions et portée V20](research/product-redesign-v20/DECISIONS.md) · [Contexte produit](PRODUCT.md). Les neuf sections documentaires restent celles de Reference Design Contract ; le frontmatter suit le format alpha Google DESIGN.md et les valeurs du code, sans lint officiel revendiqué.

## 1. Visual Theme & Atmosphere

Une bibliothèque de travail qui aide à comparer avant d'ouvrir. Les résultats reposent sur un fond gris clair, des cartes blanches à grandes photos, un contexte de recherche compact et des lecteurs organisés autour du sujet et de la source.

La hiérarchie change à l'intérieur du produit : plus de colonne permanente de filtres, moins de rangées explicatives avant la première ressource, un aperçu attribué sur la carte et des détails de preuve accessibles progressivement. La marque noir/blanc/rouge, l'accueil `oil.jpg`, les portes photographiques, le bandeau guides `wheel.jpg` et les parcours en lignes sont hérités de V19, sans nouvelle refonte de ces surfaces.

## 2. Color

| Rôle | Valeur effective | Usage |
|---|---|---|
| Accueil | `#f5f5f4` | Papier conservé |
| Résultats | `#f0f1f3` | Fond du mode résultats V20 |
| Surface | `#ffffff` | Cartes, filtres et lecteurs |
| Encre | `#17181a` | Texte principal |
| Secondaire | `#5e6065` | Aides et provenance |
| Séparation de base | `#dedfdf` | Filets |
| Action | `#bb1830` | Liens, actions principales et focus |
| Marque | `#ff2330` | Repère de marque |
| Action légère | `#fff0f2` | Sélection et enregistrement |
| Header | `#111214` | Navigation conservée |

Les composants V20 emploient aussi des bordures grises locales, notamment `#d8dbe1` pour la carte vidéo et `#c8cacf` pour les contrôles. La carte guide conserve la séparation de base. Ne pas transformer les mentions de véhicule en couleur de succès : une citation n'est pas une compatibilité.

Contrastes calculés sur les tokens de base : encre/papier 16,29:1, secondaire/papier 5,77:1 et blanc/action 6,39:1. Blanc/rouge de marque reste 3,79:1 : éviter le petit texte blanc sur ce rouge. Ces calculs ne constituent pas un audit complet des nouveaux composants.

## 3. Typography

Onest porte titres, texte et commandes ; Orbitron reste limité à la marque. Google Fonts fournit Onest 400/500/600/700/800 et Orbitron 600/700/800 avec `display=swap`, sans nouvelle fonte locale. Repli système conservé.

| Élément V20 | Desktop | Mobile ≤760 px |
|---|---|---|
| Titre de carte vidéo | 24 px / 1,3 | 21 px / 1,35 ; 20 px ≤360 |
| Titre de carte guide | 25 px / 1,3 | 24 px ; 23 px ≤360 |
| Aperçu vidéo | 14 px / 1,65 | 13 px / 1,65 |
| Aperçu guide | 15 px / 1,65 | 15 px |
| Titre de fiche vidéo | 32 px / 1,22 | 25 px / 1,3 ; 23 px ≤360 |
| Titre de lecteur guide | 36 px / 1,18 | 31 px / 1,2 ; 28 px ≤360 |
| Texte de lecture vidéo | 15 px / 1,8 | 15 px |
| Méthode du guide | 16 px / 1,75 | 16 px |

Le titre d'accueil hérité reste à 62 px desktop, 43 px mobile et 37 px compact. Certains libellés secondaires de cartes sont encore à 10–12 px ; ne pas affirmer une lisibilité universelle sans contrôle. Les contenus longs, l'agrandissement du texte et toutes les variantes linguistiques ne sont pas validés par la seule lecture du CSS.

## 4. Spacing & Grid

Le catalogue utilise un maximum de **1380 px**, contre 1440 px pour les surfaces générales. La grille de résultats, y compris lorsqu'elle ne contient que des guides, prévoit **deux colonnes desktop**, sans filtre latéral, puis **une colonne à 760 px et moins**. Écart desktop de 28 px, mobile de 22 px. Les captures V20 montrent les grandes cartes sur ordinateur et mobile ; elles ne couvrent pas toutes les combinaisons de contenu et de largeur.

Les cartes vidéo ont une bordure et un rayon de 16 px, réduit à 12 px sur mobile ; les cartes guides gardent 16 px. La grande couverture 16:9 occupe la largeur du cadre. Le corps vidéo a 20 px verticaux / 22 px latéraux desktop, puis 16 px mobile ; celui du guide a 20 px, puis 18 px latéraux mobile.

Le panneau de filtres occupe au maximum 580 px à droite sur ordinateur, toute la largeur sur téléphone. Il contient l'unique exemplaire des contrôles, déplacé dans un dialogue natif. Les lecteurs vidéo et guide ont respectivement un maximum de 1240 et 1180 px ; ils deviennent plein écran sur mobile.

## 5. Layout & Composition

**Recherche.** Le formulaire unique passe de l'accueil à l'emplacement des résultats desktop ou à la feuille mobile. Le contexte visible associe langue, voiture et bouton Filtres. La langue du contenu demeure distincte de la langue de l'interface. La voiture s'ouvre à la demande dans son panneau ; sa valeur courte reste dans le contrôle.

**Filtres.** Aucune sidebar permanente. Le même panneau sert aux deux tailles d'écran, dans cet ordre : niveau/durée/type de vidéo, plateformes, sujets repliés, puis contexte/transcription/licence dans le groupe avancé. Les changements sont immédiats ; « Voir N résultats » ferme le panneau, sans prétendre appliquer un brouillon. Le compteur dépend de la dernière réponse terminée ; chargement et indisponibilité ont leurs états propres.

**Résultats.** Formats Tout/Vidéos/Guides, total, tri et critères supplémentaires précèdent les cartes. Question et langue ne sont plus répétées en puces. L'interprétation et le guide conseillé sont regroupés dans « Comprendre ces résultats », repliable ; un conflit entre véhicule cité et sélection ouvre cet élément et affiche l'avertissement. Le comportement de recherche élargie ne doit pas être confondu avec une garantie de pertinence.

**Accueil et navigation.** L'accueil, le header noir 80/70 px et les parcours en lignes V19 sont conservés. La classe historique `.app-sidebar` reste une barre de sujets horizontale dans le flux ; elle n'est pas une sidebar fixe. L'objectif V20 est d'améliorer le trajet question → comparaison → lecture, pas de présenter un nouvel écran promotionnel.

## 6. Components

**Carte vidéo.** Grande miniature réelle, durée si renseignée, sujet et langue, titre, aperçu, contexte automobile disponible, auteur/plateforme et accès à la fiche. `resource-card.js` extrait au plus environ 220 caractères de la description existante, retire les URL/hashtags de cet aperçu et l'attribue : « Aperçu éditorial » pour les types éditoriaux, « Dans le descriptif » autrement. Une description absente ne produit pas de résumé inventé. La langue estimée reste marquée ; miniature absente, auteur inconnu et disponibilité de transcription ont des états explicites. Enregistrer est une action distincte.

**Carte guide.** Même présence photographique, type/sujet et contenu français annoncés, titre canonique et résumé existant. La première référence constructeur est nommée et ouvrable depuis la carte ; un second accès rejoint l'ensemble des sources et leur portée. Les badges reposent sur la sélection réelle, jamais sur la seule mise en forme.

**Fiche vidéo.** Titre et auteur au-dessus du contenu, enregistrement et copie du lien à proximité. Desktop : média à gauche, lecture à droite. Sous 1000 px : une colonne. **Sur mobile, l'ordre effectif est titre/auteur → média et repères → contenu**, différent de la proposition initiale qui plaçait l'aperçu avant le média. La lecture intégrée se charge seulement sur action quand elle est disponible ; sinon l'action ouvre la plateforme source. Durée, langue, niveau indicatif et présence du texte restent explicites. Onglets Contenu / Transcription / Mes notes ; les sections véhicule, questions et source/droits/méthode sont repliables. L'onglet Transcription reste présent même sans texte et décrit cette absence.

**Lecteur guide.** En-tête partagé entre titre/synthèse et photo 4:3 desktop, empilé avec photo 16:10 mobile. Plan latéral desktop, plan dans le flux mobile. Prérequis et informations à réunir précèdent la méthode ; les notices constructeur forment une section distincte. Les textes de portée, limites, dates, autres portails et crédits restent consultables. Onze guides et vingt et une références constructeur sont conservés, sans nouvelle procédure. La navigation est FR/EN/ES ; le contenu documentaire français reste identifié par `lang="fr"` et une mention visible.

## 7. Motion & Interaction

Les interactions emploient les commandes natives existantes. Les états de recherche, filtres, sauvegarde et dialogue appartiennent toujours à l'application ; les nouveaux modules de carte/fiche rendent leur présentation. Les titres, descriptions, métadonnées et liens sont échappés ou filtrés ; seuls les fragments de l'application explicitement prévus sont acceptés comme HTML.

Transitions vidéo : carte 180 ms, photo 200 ms avec zoom 1,025 au survol ; lecteur 160 ms. La nouvelle photo de guide n'a pas de zoom. Les règles de mouvement réduit suppriment les transitions non essentielles ; leur comportement avec un réglage OS réel reste à tester.

Focus de base : contour rouge 3 px, décalage 4 px. Le plan guide déplace le focus vers un titre de section ; les dialogues conservent leurs identifiants et actions existants. Les retours entre recherche, filtres et lecteur doivent préserver les critères et éviter la réouverture involontaire de la recherche. La validation de ces enchaînements est séparée de la syntaxe.

## 8. Voice & Brand

Nommer le sujet et la matière disponible sans promettre visionnage, certification ou compatibilité. Une description source n'est pas une synthèse du visionnage ; une transcription absente ne devient pas disponible parce qu'une fiche est bien présentée. Les mentions de langue, niveau et véhicule gardent leur degré de certitude.

Les douze photographies locales, auteurs et licences restent dans [le manifeste](public/photo-sources.json) et [les crédits](public/photo-credits.html) : Pexels, Unsplash, CC BY, CC BY-SA ou domaine public selon l'image. La photo n'est pas une preuve technique ; le VIN illustré a été modifié par son auteur. Aucune nouvelle image ou collecte n'est revendiquée pour cette refonte.

RaceLink/MotionSite et Flowith/Claude Opus 5.5 restent des [références historiques V17](research/visual-direction-2026-10-23/design-contract.md), avec [portée documentée](research/visual-direction-2026-10-23/flowith-opus-5-5.md). Impeccable, registre produit, guide la V20 ; les rôles effectifs des ressources et les écarts au benchmark sont consignés dans [DECISIONS.md](research/product-redesign-v20/DECISIONS.md).

## 9. Anti-patterns

Ne pas remettre une colonne de filtres permanente, une seconde modale avant la fiche, des résumés inventés, des affiches à pictogrammes ou des badges de compatibilité. Ne pas réduire les photos pour compenser des contrôles redondants.

`public/product-ui.css` reste la source visuelle unique, compilée par `scripts/build_ui.py` dans le bundle à couches. Les fragments de travail V20 sont des matériaux d'intégration, pas des feuilles à charger en parallèle. Préserver les règles de visibilité des vues, des dialogues et du mode résultats.

**État : V20 publiée au commit final `17ea9ab`, avec des vérifications ciblées documentées.** La [validation](research/product-redesign-v20/VALIDATION.md) distingue les différentes preuves :

- [109 contrôles locaux réussis](research/product-redesign-v20/validation-results.json), selon les sources et dates consignées : navigation, HTML, export, recherche/filtres, cartes et lecteur. Les 14 contrôles HTML/bundle ont été relancés sur le CSS final. Ils ne sont pas des tests de rendu.
- [17 fichiers publics contrôlés](research/product-redesign-v20/public-assets-check.json), HTTP 200 et octets conformes au dépôt au commit final `17ea9ab` ; [catalogue inchangé](research/product-redesign-v20/catalogue-integrity.json).
- [Parcours navigateur public](research/product-redesign-v20/browser-checks.json) à 320/390/768/1280 px : filtres et focus de plateforme, suggestions avec flèches/Entrée, réinitialisation conservant question et format, fiche vidéo et retour du focus, guide et navigation vers les notices.
- [Contrelecture indépendante de 13 captures](research/product-redesign-v20/visual-review.md), distincte de ces essais fonctionnels. Elle n'a pas identifié de correctif visuel nécessaire dans les états examinés.

Le [rapport navigateur](research/product-redesign-v20/browser-checks.json) consigne 18 scénarios, en distinguant les interactions sur `5a48d1f` des deux finitions CSS contrôlées sur `17ea9ab` ; les parcours complets ne sont pas déclarés rejoués sur ce dernier commit. Aucun téléphone physique, texte agrandi/zoom système, réglage OS de mouvement réduit, lecteur d'écran ou audit WCAG exhaustif n'a été testé. Les sources externes constructeur n'ont pas été revérifiées pendant cette passe UI.

Historique séparé : [V19d](research/graphic-redesign-v19/VALIDATION.md), [V18](research/skills-roundup-2026-10-23/README.md), [guides V16](research/official-guides-2026-10-23/VALIDATION.md), [photos V15](research/photo-covers-2026-10-23/VALIDATION.md). La validation d'une version précédente ne remplace pas celle des nouvelles surfaces.
