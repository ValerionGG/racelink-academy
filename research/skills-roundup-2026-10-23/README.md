# Les douze ressources de la capture, appliquées à RaceLink

Recherche et travail du 23 octobre 2026. [Version à consulter](https://valeriongg.github.io/racelink-academy/?release=skills-v18c).

La direction reste celle demandée : grandes photographies réelles, identité RaceLink noire/blanche/rouge, titres hors image et priorité au mobile. Cette passe améliore la recherche et la découverte, sans repartir vers une nouvelle esthétique. Les douze noms de la capture ont été examinés ; ils ne correspondent pas tous à des skills installables.

## Inventaire vérifié et rôle

Les étoiles sont celles des API GitHub consultées le 23 octobre, vers 16:02–16:04 UTC. Elles mesurent la popularité, pas la qualité du résultat.

| Ressource primaire | Étoiles | Utilisation effective dans cette passe |
|---|---:|---|
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 139 311 | Revue de la langue visible, des commandes tactiles et du focus ; recherches UX ciblées. Skill déjà installé. |
| [Awesome DESIGN.md](https://github.com/VoltAgent/awesome-design-md) | 123 114 | Lecture des analyses BMW M et Airbnb : cartes photographiques et métadonnées séparées. Ce sont des analyses tierces, pas les chartes officielles des marques. |
| [OpenDesign](https://github.com/nexu-io/open-design) | 103 544 | Skill `reference-design-contract` pour le contrat de référence : observations, adaptations et critères vérifiables. L'application OpenDesign complète n'est pas installée. |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill) | 101 489 | Chapitre App screens, audit statique et conservation des vrais objets du catalogue ; accès direct aux guides. Skill déjà installé. |
| [Impeccable](https://github.com/pbakaus/impeccable) | 85 335 | Revue produit : cohérence des tailles de texte, commandes familières et lecture. Skill déjà installé. |
| [React Bits](https://github.com/DavidHDev/react-bits) | 50 061 | Lecture de composants animés : gestion du mouvement réduit et nettoyage. Principes adaptés au défilement natif ; aucun composant React importé. |
| [Emil Kowalski Skills](https://github.com/emilkowalski/skills) | 48 965 | Audit des occasions de mouvement : retour d'appui limité aux flèches, aucun délai dans la recherche. `find-animation-opportunities` installé. |
| [Hallmark](https://github.com/Nutlope/hallmark) | 31 172 | Skill installé, audit app et hiérarchie des suggestions : type lisible, titre, provenance. Les prescriptions de landing page cèdent à la charte RaceLink. |
| [Google DESIGN.md](https://github.com/google-labs-code/design.md) | 28 498 | Frontmatter structuré ajouté au DESIGN.md existant avec les valeurs réelles de RaceLink. Aucun CLI supplémentaire. |
| [GSAP Skills](https://github.com/greensock/gsap-skills) | 16 982 | `gsap-performance` installé ; lectures DOM regroupées, animation de transform et nettoyage des observateurs. Aucun moteur GSAP ajouté. |
| [Scroll World](https://github.com/oso95/scroll-world) | 10 386 | Skill et moteur étudiés pour le cadrage mobile et le repli statique. Workflow de vidéo générée non exécuté : les photos demandées restent statiques. |
| [Canvas UI](https://github.com/DavidHDev/canvas-ui) | 5 070 | Documentation vanilla et repli HTML examinés. Recherche, photos et commandes restent en HTML accessible ; aucun effet GPU ajouté. |

La correspondance des noms Open Design, Canvas UI et Scroll World avec ces dépôts est fondée sur leur intitulé et leur description ; la capture ne fournit pas les URL. Les dépôts eux-mêmes et leurs contenus ont été vérifiés. Les trois [rapports détaillés](group-ui.md), [motion](group-motion.md) et [formats de design](group-design-docs.md) donnent versions, licences, limites et liens primaires.

## Changements livrés

- **Recherche mobile :** langue sélectionnable juste sous la saisie. Un changement conserve la question et les critères de voiture, garde la feuille ouverte et actualise les suggestions.
- **Suggestions :** types en casse normale, titres de 15 px sur mobile, compléments de 12 px. Les vidéos indiquent plateforme, langue et auteur disponibles. Une langue estimée ou non confirmée conserve cette mention.
- **Découverte :** bouton Guides pratiques vers les onze guides, avec notices constructeur accessibles dans le lecteur existant.
- **Grandes cartes :** boutons précédent/suivant sur les deux rails mobiles, compteur de position, maintien du focus aux limites et repli sur une carte quand les commandes disparaissent à l'élargissement. Pas de défilement automatique.
- **Sélection RaceLink :** auteur et source plus lisibles ; grille dimensionnée selon la place disponible. Photos et ordre des ressources conservés.
- **Mouvement :** pression de 150 ms sur les flèches, défilement natif, mouvement réduit respecté ; recherche et résultats immédiats.

Le catalogue contient toujours **36 901 vidéos et 11 guides**. Cette passe n'ajoute pas de vidéos, de transcriptions ou de preuves de compatibilité mécanique. Les **21 références constructeur déjà présentes** restent accessibles, avec leur périmètre. L'application est publiée sur GitHub Pages ; le domaine Focus n'est pas modifié.

## Installation et méthode

Quatre ajouts ciblés : Hallmark, Find Animation Opportunities, GSAP Performance et Reference Design Contract. Les versions sont épinglées dans les rapports. Les skills préexistants ont été consultés sans écrasement. Les textes installés ont été lus pour cette passe ; leur apparition dans le catalogue automatique peut nécessiter le prochain tour.

Les bibliothèques, spécifications et workflows non pertinents n'ont pas été exécutés artificiellement pour atteindre douze installations. Aucune migration React, dépendance d'animation, abonnement ou génération vidéo payante n'a été introduit. L'audit d'Emil reste une analyse ; l'implémentation découle de la demande de modification de RaceLink.

Les linters de style Hallmark et Taste ont été réellement exécutés en mode statique. Ils ne sont **pas au vert** selon toutes leurs conventions : règles de tokens, formats de labels et voiles sur photos notamment. Le rapport UI contextualise les alertes ; aucun score esthétique ou audit WCAG complet n'est revendiqué. Le contrôle final du produit passe par les tests fonctionnels et le navigateur, documentés dans [VALIDATION.md](VALIDATION.md).

Les recherches sont réalisées avec **[Agent Reach](https://github.com/Panniantong/Agent-Reach)**, route GitHub CLI, et des pages primaires. [Contrat adapté](reference-contract.md) · [Charte unique](../../DESIGN.md).
