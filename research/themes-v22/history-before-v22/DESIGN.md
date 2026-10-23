---
version: alpha
name: RaceLink Academy
description: Cinema V21 published; application contracts, public files and responsive browser scenarios checked.
colors:
  primary: "#e3263f"
  brand: "#e3263f"
  canvas: "#101112"
  surface: "#191b1f"
  surface-raised: "#23262b"
  on-surface: "#f5f5f2"
  muted: "#a9acb4"
  border: "#34363d"
  accent-soft: "#321920"
  focus: "#ff6379"
  reader-canvas: "#141518"
typography:
  body:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 15px
    lineHeight: 1.6
  display:
    fontFamily: "Barlow Condensed, Impact, sans-serif"
    fontWeight: 700
  brand:
    fontFamily: "Orbitron, Onest, system-ui, sans-serif"
    fontSize: 13px
    fontWeight: 800
  hero:
    fontFamily: "Barlow Condensed, Impact, sans-serif"
    fontSize: "clamp(72px, 7.6vw, 112px)"
    fontWeight: 700
    lineHeight: 0.88
    letterSpacing: -0.01em
rounded:
  surface: 10px
  resource-photo: 8px
  search: 8px
  compact-control: 6px
  reader: 12px
spacing:
  desktop-page-inline: 56px
  tablet-page-inline: 32px
  mobile-page-inline: 20px
  compact-page-inline: 16px
  resource-columns: 24px
  resource-rows: 32px
  resource-gap-mobile: 28px
components:
  masthead:
    height: 80px
  masthead-mobile:
    height: 66px
  guide-home-cover:
    aspectRatio: "3 / 4"
  video-photo:
    aspectRatio: "16 / 9"
  universe-photo:
    aspectRatio: 1.8
  universe-photo-mobile:
    aspectRatio: 1.45
  guide-reader-photo:
    aspectRatio: "16 / 7"
  guide-reader-photo-mobile:
    aspectRatio: "16 / 10"
  focus-ring:
    color: "{colors.focus}"
    outlineWidth: 3px
    outlineOffset: 4px
  video-reader:
    maxWidth: 1360px
  reader-mobile:
    height: 100dvh
    rounded: 0px
  reduced-motion:
    animation: none
    transition: none
    scrollBehavior: auto
---

# Interface RaceLink Academy — Cinéma V21

**Direction `cinema-v21`, 23 octobre 2026 : implémentée dans les sources, validation en cours.** Aucune publication ni réussite de tests V21 n’est déclarée ici. [Produit](PRODUCT.md) · [Décisions et références](research/cinema-v21/DESIGN-DECISIONS.md) · [Contrats d’intégration](research/cinema-v21/integration-plan.md).

Les neuf sections documentent la direction courante. Le frontmatter conserve le format documentaire alpha existant ; aucun lint officiel n’est revendiqué. Les valeurs proviennent de `public/product-ui.css` et des sources de la nouvelle composition.

## 1. Visual Theme & Atmosphere

Une bibliothèque automobile cinéma : photographie d’atelier en grand format, titres condensés, couvertures de guides, univers photographiques et sélections vidéo réelles. Le noir, le blanc et le rouge composent toute l’expérience, y compris résultats et lecteurs.

V21 remplace l’accueil papier V19 et les résultats blancs V20. La découverte s’organise en collections ; la recherche retire cette scène et laisse une grille de comparaison. Les grandes images servent le sujet, sans intro ni lecture automatique.

## 2. Color

| Rôle | Valeur déclarée | Usage |
|---|---|---|
| Fond | `#101112` | Accueil et résultats |
| Surface | `#191b1f` | Commandes et surfaces secondaires |
| Surface relevée | `#23262b` | Hiérarchie locale |
| Texte principal | `#f5f5f2` | Lecture sur fond sombre |
| Texte secondaire | `#a9acb4` | Métadonnées et aides |
| Séparation | `#34363d` | Bordures et filets |
| Rouge RaceLink | `#e3263f` | Actions et repères |
| Rouge atténué | `#321920` | États secondaires |
| Focus général | `#ff6379` | Contour de clavier |
| Fond du lecteur | `#141518` | Dialogue vidéo et guide |

Les lecteurs possèdent des variantes locales, dont `#adb0b8` pour le texte secondaire et un focus clair. Le dégradé d’accueil protège le texte sans colorer uniformément les photographies. Une mention de voiture n’emploie pas un statut de compatibilité.

Les contrastes calculés pour V20 ne s’appliquent pas à cette palette. Ces valeurs ne valent ni mesure ni audit de conformité V21.

## 3. Typography

**Onest** porte texte, titres de cartes et commandes. **Barlow Condensed** porte le grand titre d’accueil et les titres éditoriaux/lecteurs. **Orbitron** reste la signature. Les trois familles sont chargées depuis Google Fonts avec `display=swap` et des replis système.

Le hero desktop utilise `clamp(72px, 7.6vw, 112px)` en graisse 700, ligne 0,88 ; les règles mobiles réduisent cette échelle, jusqu’à 56 px sous 360 px. Les titres vidéo de résultats sont à 18 px, 17 px sous 360 px. La fiche vidéo utilise 36 px sur mobile, 32 px sous 360 px ; le guide 40 puis 36 px. Le texte de lecture vise 16 px avec une ligne confortable.

Les labels restent plus petits que le contenu. Leur lisibilité, le texte agrandi, les titres longs et toutes les langues doivent être examinés dans le rendu ; la lecture du CSS seule ne les valide pas.

## 4. Spacing & Grid

L’enveloppe générale atteint 1560 px avec 56 px de marges internes desktop, 32 px sous 1100 px, 20 px sous 760 px et 16 px sous 360 px. La scène d’accueil prend la largeur de la page.

Les résultats prévoient **trois colonnes à 1280 px**, deux à 1100 px et moins, une à 760 px et moins, puis quatre à partir de 1600 px. Écarts de base : 24 px entre colonnes, 32 px entre rangées ; 28 px entre cartes sur mobile. Ce sont des règles de source, pas des captures validées.

Les six guides d’accueil ont une couverture 3:4 ; les trois univers emploient un cadrage large ; les vidéos conservent le 16:9. Les collections défilent horizontalement dans leur zone. Le ratio 3:4 n’est pas appliqué au catalogue entier ni au lecteur.

Le dialogue lecteur déclare actuellement un maximum de **1360 px**, limité par la fenêtre ; sous 760 px, vidéo et guide occupent `100dvh`, sans bordure ni rayon. Recherche et filtres deviennent aussi plein écran sur téléphone.

## 5. Layout & Composition

**Accueil.** `service.jpg` forme la scène photographique. Titre et actions se superposent à sa partie sombre. Une entrée distincte ouvre le guide de préparation d’une vidange. Recherche et choix de langue suivent ; aucun second formulaire n’est créé.

**Collections.** Six guides essentiels : huile, carburant, roue, essuie-glaces, batterie et diagnostic. Trois univers : Mécanique, Pilotage, Sim racing. Les sélections vidéo suivent les données et statuts existants. Le contexte et les ressources disponibles gouvernent les éléments affichés, sans faux contenus pour compléter une rangée.

**Résultats.** Le mode recherche masque hero et collections. Question, langue, voiture et Filtres précèdent formats, total, tri et grille. L’interprétation et le guide conseillé restent dans « Comprendre ces résultats » ; les conflits de véhicule conservent leur information explicite.

**Navigation.** En-tête sombre et navigation mobile à quatre entrées. Les sujets sont accessibles par univers et menu ; `.app-sidebar` est masquée. L’unique formulaire et l’unique ensemble de filtres changent d’emplacement selon le contexte.

## 6. Components

**Guide d’accueil.** Photo en 3:4, titre canonique, résumé existant, type Guide pratique, langue française et sources disponibles. L’affiche est le traitement d’un document, pas une vidéo jouable ni une notice officielle RaceLink.

**Carte vidéo.** Miniature originale en 16:9, durée connue uniquement, titre, sujet, langue et informations attribuées. Description absente ne signifie pas résumé à inventer. Auteur, plateforme, état linguistique et ouverture ne dépendent pas du survol. Enregistrer reste une action distincte.

**Fiche vidéo.** Lecteur sombre, titre condensé, média et contenu répartis sur grand écran, puis une colonne sous 1080 px. La miniature reste contenue dans la zone média. Lecture intégrée sur demande lorsqu’elle est disponible ; lien source explicite. Contenu, transcription, notes et preuves conservent leurs rôles.

**Lecteur guide.** Photo 16:7 desktop et 16:10 mobile, titre, synthèse, prérequis, méthode et notices distinctes. Le plan et les références restent dans le dialogue. Chaque notice garde véhicule, période, section et limites ; la photo n’établit aucune compatibilité. Le français documentaire reste signalé lorsque les commandes changent de langue.

**Filtres.** Panneau natif commun, plein écran mobile. Ordre : niveau/durée/type, plateformes, sujets, puis texte et droits. Les changements sont immédiats ; le pied ferme le panneau avec le total courant ou son état de chargement. Aucun faux mode brouillon.

## 7. Motion & Interaction

Les rangées utilisent le défilement natif et des commandes précédent/suivant. Les transitions de couleur et de photo ne deviennent pas une étape du parcours. Aucun lancement automatique de vidéo ; les actions restent accessibles sans survol.

Le CSS contient `prefers-reduced-motion` pour retirer animations, transitions et défilement doux. Les dialogues natifs, labels, identifiants et événements existants sont conservés. Focus général : contour 3 px, décalage 4 px ; les lecteurs ont leur contour clair spécifique.

Ces dispositions restent à éprouver sur V21 : extrémités/redimensionnement des rangées, fermeture des dialogues, recherche avec langue, suggestions, filtres et restitution du focus. Aucune certification d’accessibilité ni exécution de ces parcours n’est déclarée ici.

## 8. Voice & Brand

Nommer le sujet et la matière disponible. Une sélection ne certifie pas toutes les procédures ; un titre public n’est pas un visionnage ; une transcription absente reste absente. Langues estimées, licences et véhicules cités conservent leur degré de preuve.

Photos et licences : [manifeste](public/photo-sources.json), [crédits](public/photo-credits.html). Le VIN illustré a été modifié par son auteur. La scène d’accueil illustre l’atelier ; elle n’est pas une capture attribuée au guide.

Les [décisions V21](research/cinema-v21/DESIGN-DECISIONS.md) distinguent les captures vues de MasterClass, du guide Netflix Tudum et de Domestika. Tudum montre une interface TV dans un article ; aucun compte Netflix n’a été utilisé. La [recherche GitHub](research/cinema-v21/prompt-research.md) donne les fichiers, versions et principes retenus. Leurs prescriptions ne remplacent pas la marque ou le produit.

## 9. Anti-patterns

Ne pas reproduire l’accueil clair V19 ni considérer V21 comme une simple couche sombre. Ne pas copier les médias des références, inventer popularité/progression, teinter uniformément les images, ajouter une intro, une sidebar de filtres permanente, un second formulaire ou une modale avant la fiche.

`public/product-ui.css` demeure la couche visuelle produit, compilée par `scripts/build_ui.py`. Les collections réutilisent les actions du catalogue ; la refonte ne change pas le sens des paramètres, guides, transcriptions et preuves.

**Statut : V21 publiée et vérifiée.** [Périmètre des contrôles](research/cinema-v21/VALIDATION.md). Le [plan d’intégration](research/cinema-v21/integration-plan.md) sépare source, contrats, export, captures et navigateur réel. Les contrôles V20 ne valent pas validation V21.

Historique : [design V20](research/product-redesign-v20/DESIGN-snapshot-v20.md), [produit V20](research/product-redesign-v20/PRODUCT-snapshot-v20.md), [validation V20](research/product-redesign-v20/VALIDATION.md), [V19](research/graphic-redesign-v19/VALIDATION.md), [V18](research/skills-roundup-2026-10-23/README.md). MotionSite et Flowith restent des [références historiques V17](research/visual-direction-2026-10-23/design-contract.md), sans nouvelle utilisation revendiquée.
