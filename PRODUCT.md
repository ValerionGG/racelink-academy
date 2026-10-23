# RaceLink Academy

Version courante **skills-v18c**, publiée sur [GitHub Pages](https://valeriongg.github.io/racelink-academy/?release=skills-v18c). Grandes images conservées ; recherche mobile avec langue visible, suggestions sourcées, accès aux guides et commandes des rails. [Validation et portée](research/skills-roundup-2026-10-23/VALIDATION.md).

## Register

product

## Users

Public débutant à professionnel. Une personne cherche une réponse pratique sur son téléphone près de sa voiture, ou explore sur ordinateur un sujet de mécanique, pilotage, simulation ou métier. Contexte confirmé par les demandes utilisateur et le catalogue existant.

## Product Purpose

Trouver rapidement une ressource utile, comprendre sa source et ses limites, puis la consulter. La recherche, ses suggestions et les critères exacts du véhicule sont le parcours principal. Les parcours et la découverte sont des entrées secondaires.

## Brand Personality

Claire, pratique, passionnée. La filiation avec le site officiel RaceLink réellement inspecté repose sur le noir, le rouge et le blanc, Onest pour la lecture et de courts accents Orbitron. V17 remet les grandes photos au premier plan : hero mécanique photographique, recherche blanche à sa jonction, catégories photographiques larges et titres lisibles sous les images. Les surfaces de lecture restent claires et les photos non teintées. Les onze guides conservent leurs photographies avec crédits ; les vidéos conservent leurs propres miniatures. Langage accessible avant vocabulaire technique. Les décisions courantes figurent dans [DESIGN.md](DESIGN.md).

## Anti-references

Éviter les étapes empilées avant les résultats, les affiches vertes, les grandes icônes sur fond uni et la réduction des photos en petites vignettes latérales : ces directions ont été rejetées par l’utilisateur. Ne pas rechercher la compacité au prix du sujet photographique et de la lecture. Les teintes générales qui masquent les images, les libellés ambigus, les compteurs décoratifs et les badges donnant une impression de validation technique restent exclus. Les références MotionSite ne justifient pas de repousser la recherche sous une page promotionnelle ou d’ajouter des animations permanentes.

## Design Principles

- Une question mène directement à ses résultats.
- Distinguer le sujet, le format de ressource et la plateforme.
- Montrer les images pertinentes et créditer les auteurs.
- Donner aux photos un cadre 16:9 sur toute la largeur des cartes mobiles, puis afficher le titre de 20–21 px en dessous.
- Adapter la grille à l’espace réel : deux colonnes de résultats à 1280 px avec le cadre applicatif actuel ; minimum utile de 330 px par carte, trois colonnes seulement sur un espace très large.
- Séparer les illustrations de navigation, les couvertures éditoriales et les miniatures réelles des vidéos.
- Utiliser le mouvement pour confirmer une action, avec une alternative réduite ; conserver le contexte de recherche.
- Révéler les paramètres mécaniques détaillés à la demande.
- Conserver les précisions de la recherche ; ne jamais fabriquer une compatibilité.

## Accessibility & Inclusion

Conserver les contrôles HTML natifs, labels persistants, navigation au clavier, focus visible et alternative aux animations déjà présents. Français, anglais et espagnol pour l’interface ; langues de contenu séparées. Les contrôles V18 du navigateur et leurs limites sont consignés dans research/skills-roundup-2026-10-23/VALIDATION.md.

## Guides et références constructeur — 23 octobre 2026

Sur mobile, conserver un seul en-tête fixe : la recherche en contexte reste dans le flux et la navigation basse permet de la rouvrir. Les guides se parcourent en cartes photographiques généreuses : image 16:9 sur toute la largeur, titre puis informations et accès aux références. Aucune affiche à pictogramme ne remplace la photo. Le format actif n’a pas besoin d’une seconde pastille de filtre.

Un lecteur commun dessert la bibliothèque et les repères véhicule. Séparer les étapes générales RaceLink des références constructeur : modèle, moteur lorsque connu, période/édition, marché, section, date de consultation et limites. Ne jamais déduire une compatibilité du seul intitulé d’un guide. Les liens de notices directes restent accessibles depuis les cartes ; les portails et autres références documentaires sont secondaires.

## Recherche et décisions V17

Les aperçus publics **Driven Hero** et **Hyperion V12** de [MotionSite](https://www.motionsite.ai/) ainsi que [racelink-app.co](https://racelink-app.co/) ont réellement été inspectés. Ils inspirent la présence de la matière mécanique et le contraste noir/blanc/rouge ; leurs actifs et leur code ne sont pas repris. Les captures et la matrice référence → changement → vérification figurent dans le [contrat visuel](research/visual-direction-2026-10-23/design-contract.md).

Une contre-proposition a également été obtenue réellement dans **Flowith, avec Claude Opus 5.5 affiché et sélectionné**, à partir du brief public. La composition photographique « Atelier » a été adaptée : fond de lecture clair, largeur de grille recalculée avec la sidebar et recherche du catalogue dans le flux. [Brief, réponse et décisions](research/visual-direction-2026-10-23/flowith-opus-5-5.md). Cette consultation ne constitue ni un test de l’application ni un déploiement automatique de code généré.

## Historique — directions remplacées

- **V14**, commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4) : fondation Onest/Orbitron et noir/rouge/blanc. La compacité du hero et des cartes appartient à cette étape ; elle ne constitue plus la direction courante.
- **photo-v15**, commit [ad0cc50](https://github.com/ValerionGG/racelink-academy/commit/ad0cc50) : douze photographies réelles pour l’accueil et les onze guides, avec crédits. [Validation historique](research/photo-covers-2026-10-23/VALIDATION.md).
- **guide-v16b**, commit [5e60fab](https://github.com/ValerionGG/racelink-academy/commit/5e60fab4c231976a15af0439c816cefc0dbce3d7) : lecteur partagé et 21 références constructeur dans onze guides. Les cartes compactes de cette étape sont remplacées par les grandes couvertures V17 ; le travail documentaire et les interactions utiles sont conservés. [Validation historique](research/official-guides-2026-10-23/VALIDATION.md).
