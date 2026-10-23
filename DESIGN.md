---
version: alpha
name: RaceLink Academy
description: V22 light and dark themes; scoped evidence is in the validation report.
---

# RaceLink Academy — Design V22

**Version `themes-v22` publiée ; contrôles ciblés documentés.** [Ouvrir](https://valeriongg.github.io/racelink-academy/?release=themes-v22&build=9985987) · [Validation et limites](research/themes-v22/VALIDATION.md).

## Direction

Même composition photographique, deux systèmes de lecture complets. Barlow Condensed porte les grands titres, Onest le texte et les commandes, Orbitron la signature. Les grandes images et leur cadrage sont conservés ; les cartes utilisent surfaces, bordures légères, rayons de 12 px et texte espacé.

## Thèmes et couleurs

Les rôles `--rl-canvas`, `surface`, `field`, `ink`, `muted`, `line`, `action`, `on-action`, `focus` et leurs variantes gouvernent l’ensemble de l’application. Clair emploie un fond gris très clair et des surfaces blanches ; Sombre emploie une encre profonde et des surfaces anthracite. Le rouge garde le rôle d’action. La source effective est `public/product-ui.css` ; les valeurs fixes d’anciennes versions ne sont plus des directives courantes.

Les rôles `media-bg`, `media-ink` et `media-muted` restent indépendants : durée, bouton sur image et zone vidéo conservent leur lisibilité. Le texte sur action utilise `on-action`, jamais la couleur de texte courant inversée. `color-scheme`, la préférence locale et la métadonnée de couleur suivent le thème.

## Surfaces et interaction

Six guides d’accueil en 3:4, trois univers photographiques, miniatures vidéo en 16:9. Résultats comparables, lecteur ample et dialogues plein écran mobile. Le thème ne modifie ni dimensions des images, ni données, ni ordre du parcours. Les filtres, champs de véhicule, suggestions, plan de guide, notices, notes et états vides doivent suivre les mêmes rôles.

Les commandes conservent focus visible, labels, états sélectionnés et dialogues natifs. Les rangées défilent dans leur propre zone. Les transitions sont limitées et retirées pour le mouvement réduit. La présence de règles CSS ne remplace pas les [contrôles et leurs limites](research/themes-v22/VALIDATION.md).

## Provenance et histoire

Photos réelles créditées, miniatures d’origine distinctes des illustrations. Aucune certification technique n’est déduite du design. [Principes cinéma et références](research/cinema-v21/DESIGN-DECISIONS.md), [recherche de prompts](research/cinema-v21/prompt-research.md) et [ancien design archivé](research/themes-v22/history-before-v22/DESIGN.md). Les prescriptions « interface uniquement sombre » ne s’appliquent plus à V22.
