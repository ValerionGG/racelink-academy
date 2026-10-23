# RaceLink Academy

Version finale **v14c**, commit [f39bfee](https://github.com/ValerionGG/racelink-academy/commit/f39bfee), publiée et contrôlée. Les observations sont détaillées dans [VALIDATION.md](research/ui-redesign-2026-10-23/VALIDATION.md).

## Register

product

## Users

Public débutant à professionnel. Une personne cherche une réponse pratique sur son téléphone près de sa voiture, ou explore sur ordinateur un sujet de mécanique, pilotage, simulation ou métier. Contexte confirmé par les demandes utilisateur et le catalogue existant.

## Product Purpose

Trouver rapidement une ressource utile, comprendre sa source et ses limites, puis la consulter. La recherche, ses suggestions et les critères exacts du véhicule sont le parcours principal. Les parcours et la découverte sont des entrées secondaires.

## Brand Personality

Claire, pratique, passionnée. V14 publiée le 23 octobre 2026, commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4) : filiation avec le site officiel RaceLink réellement inspecté, noir/rouge/blanc, corps Onest et courts accents Orbitron. Surfaces de lecture neutres, accueil noir compact avec recherche blanche, photos non teintées et légendes lisibles hors image. Onze couvertures de guides en SVG original noir/argent/rouge ; miniatures des vidéos conservées. Langage accessible avant vocabulaire technique. Les décisions courantes figurent dans [DESIGN.md](DESIGN.md), les contrôles réels et l’état de la retouche v14c dans [VALIDATION.md](research/ui-redesign-2026-10-23/VALIDATION.md).

## Anti-references

La précédente version empilait objectifs, thèmes, sélections et formulaire avant les résultats. Éviter ce parcours signalé comme compliqué, les affiches vertes rejetées par l’utilisateur, les teintes générales qui masquent les images, les libellés ambigus, les compteurs décoratifs et les badges donnant une impression de validation technique. Les références Pinterest et MotionSite ne justifient pas de transformer la bibliothèque en page promotionnelle ou d’ajouter des animations permanentes.

## Design Principles

- Une question mène directement à ses résultats.
- Distinguer le sujet, le format de ressource et la plateforme.
- Montrer les images pertinentes et créditer les auteurs.
- Séparer les illustrations de navigation, les couvertures éditoriales et les miniatures réelles des vidéos.
- Utiliser le mouvement pour confirmer une action, avec une alternative réduite ; conserver le contexte de recherche.
- Révéler les paramètres mécaniques détaillés à la demande.
- Conserver les précisions de la recherche ; ne jamais fabriquer une compatibilité.

## Accessibility & Inclusion

Conserver les contrôles HTML natifs, labels persistants, navigation au clavier, focus visible et alternative aux animations déjà présents. Français, anglais et espagnol pour l’interface ; langues de contenu séparées. Des parcours v14 ont été vérifiés via CUA sur desktop et dans un iframe mobile de 390 px ; consulter [le rapport](research/ui-redesign-2026-10-23/VALIDATION.md) pour leur périmètre. Ne pas généraliser ces essais à toutes les tailles ou à la retouche suivante. Aucun audit WCAG exhaustif ni test sur appareil physique n’est revendiqué.
