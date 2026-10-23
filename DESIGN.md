---
version: alpha
name: RaceLink Academy
description: Existing RaceLink product tokens from public/product-ui.css.
colors:
  primary: "#c82038"
  brand: "#ff2330"
  canvas: "#fafafa"
  surface: "#ffffff"
  on-surface: "#18191b"
  muted: "#606166"
  border: "#e1e1e3"
  accent-soft: "#fff0f2"
  neutral-soft: "#ededee"
  shell: "#101012"
  shell-muted: "#aaaab0"
typography:
  body:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 14px
    lineHeight: 1.55
  brand:
    fontFamily: "Orbitron, Onest, system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: 0px
  resource-title:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 21px
    lineHeight: 1.3
    letterSpacing: -0.4px
  resource-title-compact:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 20px
    lineHeight: 1.3
    letterSpacing: -0.4px
rounded:
  surface: 14px
  guide-photo: 12px
  guide-control: 9px
  brand-mark: 10px
spacing:
  desktop-page-inline: 36px
  guide-content-start: 16px
  guide-reader-columns: 36px
  guide-card-bottom: 20px
components:
  resource-photo:
    rounded: "{rounded.guide-photo}"
    aspectRatio: "16 / 9"
  focus-ring:
    color: "{colors.primary}"
    outlineWidth: 3px
    outlineOffset: 3px
  press-motion:
    transitionDuration: 150ms
    transitionTimingFunction: "cubic-bezier(.23,1,.32,1)"
  control-motion:
    transitionDuration: 180ms
    transitionTimingFunction: ease
  reduced-motion:
    animation: none
    transition: none
    scrollBehavior: auto
---

# Interface RaceLink Academy

Version **skills-v18c**, [commit e0ee228](https://github.com/ValerionGG/racelink-academy/commit/e0ee2280f8af4bd84e10e3c246f2420b13588be8). [Application](https://valeriongg.github.io/racelink-academy/?release=skills-v18c) · [Validation](research/skills-roundup-2026-10-23/VALIDATION.md) · [Les douze ressources étudiées](research/skills-roundup-2026-10-23/README.md).

## Intention et priorité

Une bibliothèque d'apprentissage automobile pour débutants et professionnels. L'action principale est de chercher une réponse, choisir une ressource dont on comprend la provenance, puis revenir à sa recherche. La langue des contenus et le véhicule sont des critères explicites. La langue du site demeure indépendante.

La direction demandée par l'utilisateur est stable : **grandes photographies réelles**, noir/blanc/rouge RaceLink, titres sous les images, lecture claire et mobile prioritaire. Les petites vignettes latérales, affiches vertes et grandes icônes décoratives sur fond uni ont été rejetées. Les nouvelles ressources de design servent cette direction.

## Système et composants

Les valeurs structurées ci-dessus suivent le format alpha Google DESIGN.md et reflètent le CSS existant. Onest porte la lecture ; Orbitron est réservé à la marque. Le rouge d'action `#c82038` sert au texte, boutons et focus ; `#ff2330` reste un accent de marque, sans petit texte blanc dessus. Fond `#fafafa`, surfaces blanches, texte `#18191b`, secondaire `#606166`.

`public/product-ui.css` est la source du système ; `scripts/build_ui.py` génère `app-ui.css` en couches legacy puis product. Ne pas modifier le bundle à la main ni empiler de nouvelles feuilles de correction. Les nouveaux comportements utilisent du HTML, du CSS et des modules JavaScript natifs.

- **Accueil :** grand visuel mécanique avec recherche blanche à la jonction de l'image, langue des vidéos et exemples. Le champ doit être utilisable au premier écran. Trois portes photographiques : entretien, pilotage, simulation. Accès Guides pratiques, puis sélection éditoriale documentée.
- **Cartes :** guide ou vidéo avec couverture 16:9 pleine largeur, titre 20–21 px et description sous l'image. Les portes de sujets restent en 16:10. Grille de résultats avec minimum utile 330 px ; deux colonnes à 1280 px dans le cadre actuel, une colonne mobile. Les sélections de l'accueil utilisent une grille adaptative avec minimum 300 px.
- **Images :** photos locales licenciées et créditées pour les guides et sujets ; miniature propre à chaque vidéo. Une photo d'illustration n'est jamais présentée comme miniature d'une vidéo. Cadrage sans recoloration uniforme ; titre hors photo. Aperçu manquant signalé explicitement.
- **Provenance :** titre, auteur, plateforme et langue connue. Une estimation de langue reste marquée. La sélection RaceLink donne accès à sa raison et à la preuve ; elle ne signifie ni visionnage intégral ni validation technique. Métadonnées de sélection à 12 px, sans masquer les limites.

## Recherche et navigation

Sur ordinateur : en-tête et sidebar noirs, contenu clair. Sur mobile jusqu'à 760 px : barre basse Accueil / Rechercher / Parcours / Enregistrés, zones de sécurité et cibles tactiles. La recherche utilise un seul formulaire déplacé dans un dialogue natif, jamais une copie avec les mêmes identifiants.

La langue des vidéos apparaît dans la feuille de recherche. Son changement conserve la saisie et les critères de voiture, actualise les suggestions et garde la feuille ouverte. Le bouton français et ce sélecteur ciblent les vidéos ; les guides restent accessibles par leur entrée et leur onglet. Le catalogue et le choix de langue d'interface restent séparés.

Les suggestions montrent un type lisible, le titre, puis la provenance disponible. Sur téléphone : type 11 px, titre 15 px et complément 12 px. Les flèches parcourent les options, Entrée ouvre la sélection, Échap ferme les suggestions puis le dialogue. Un guide ou une vidéo ouverts depuis cette recherche ne doivent pas la rouvrir à leur fermeture.

Les rails de grandes photos ont des boutons natifs de 44 px, un état de limite avec `aria-disabled`, et un compteur de position. Aucun autoplay. Aux limites, le focus reste sur la commande ; si elle disparaît au passage desktop, une carte visible du même rail récupère le focus. Le défilement natif respecte le mouvement réduit. Les observateurs sont détachés à chaque reconstruction du rail.

## Guides et références constructeur

Les onze guides partagent le même lecteur : titre, méthode générale, informations à réunir, puis notices et références. Vingt et une références constructeur précisent modèle, édition ou périmètre. L'accès depuis une carte peut rejoindre directement les sources. Le texte RaceLink n'est pas une procédure constructeur certifiée ; la compatibilité ne se déduit jamais d'une photo ou d'une simple mention de modèle.

## Mouvement, accessibilité et validation

Le mouvement confirme une action. Pression des flèches à 150 ms, transform seulement ; pas de cascade des résultats, de parallaxe, de vidéo scrubbée ni de délai de recherche. Sous `prefers-reduced-motion`, les transitions et animations non essentielles disparaissent et les rails défilent instantanément.

Focus visible, contrôles natifs, labels persistants, texte de recherche 16 px sur mobile et états chargement/vide/erreur distincts. La V18 a été contrôlée dans le navigateur de l'app à 320, 390 et 1280 px. Les parcours et captures sont détaillés dans la validation ; aucun essai sur téléphone physique ni audit WCAG exhaustif n'est revendiqué.

## Références et historique

Les douze ressources de la capture, leurs rôles et les quatre skills ajoutés sont listés dans [le rapport V18](research/skills-roundup-2026-10-23/README.md). Hallmark et Taste ont été audités statiquement ; leurs conventions ne constituent pas une certification zéro alerte. Les contraintes de marque et de grandes photos priment sur les prescriptions contradictoires de landing pages.

La direction photographique V17 s'appuie sur des inspections réelles de RaceLink et de deux aperçus MotionSite : [références](research/visual-direction-2026-10-23/visual-references.md). Une contre-proposition texte a été obtenue dans Flowith avec Claude Opus 5.5 lors de cette étape : [brief et arbitrages](research/visual-direction-2026-10-23/flowith-opus-5-5.md). Il n'y a pas eu de nouvelle génération Flowith pendant V18.

Historique : [V14](research/ui-redesign-2026-10-23/VALIDATION.md), [photos V15](research/photo-covers-2026-10-23/VALIDATION.md), [guides V16](research/official-guides-2026-10-23/VALIDATION.md), [grandes images V17](research/visual-direction-2026-10-23/VALIDATION.md). Ces preuves conservent leur portée historique.
