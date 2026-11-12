# Évolutions de RaceLink Academy

Ce dossier décrit les prochains chantiers. Chaque fichier est une spec prête à développer : le besoin, l'écran, les données, les fichiers à modifier et les critères d'acceptation.

Point de départ : le site en ligne au commit `6f49918` (12 novembre 2026), avec 50 520 vidéos, 11 guides RaceLink, 15 systèmes et 40 interventions classés, la page [Comprendre ta voiture](../../site/comprendre.html) et un niveau sur chaque carte.

## L'idée directrice

Aujourd'hui, RaceLink Academy aide à **trouver** une vidéo. L'objectif est d'aider à **réussir** : savoir si l'intervention est à sa portée, la préparer, la faire pas à pas, et progresser d'une fois sur l'autre. Côté piste, il s'agit de passer de « regarder un pilote » à « comprendre ce qu'il fait », avec de vraies données.

## Les chantiers

| # | Chantier | Ce que l'utilisateur y gagne | Impact | Effort | Phase |
|---|----------|------------------------------|--------|--------|-------|
| 09 | [Socle : catalogue plus léger](09-socle-catalogue.md) | Une recherche qui répond en moins d'une seconde, même sur mobile | Fort | M | 1 |
| 01 | [Fiche intervention](01-fiche-intervention.md) | Savoir avant de commencer : difficulté, durée, outils, risques | Fort | M | 1 |
| 02 | [Symptômes et codes défaut](02-symptomes-et-codes.md) | Partir de « ça fait un bruit » ou de « P0300 », pas d'un nom de pièce | Fort | M | 1 |
| 04 | [Mode atelier](04-mode-atelier.md) | Suivre une vidéo étape par étape, les mains sales, écran toujours allumé | Fort | M | 1 |
| 03 | [Ma voiture](03-ma-voiture.md) | Ses rappels constructeur, son carnet d'entretien et ses tutos réunis | Fort | L | 2 |
| 05 | [Progression](05-progression.md) | Des parcours qui se terminent, des quiz, des révisions espacées | Moyen | M | 2 |
| 06 | [Confiance et qualité](06-confiance-et-qualite.md) | Savoir quelles vidéos ont vraiment aidé d'autres personnes | Fort | M à L | 2 |
| 07 | [Circuits et trajectoires](07-circuits-et-trajectoires.md) | Voir la trajectoire idéale virage par virage, liée aux vidéos | Exceptionnel | L | 3 |
| 08 | [Télémétrie réelle](08-telemetrie.md) | Apprendre à lire une trace avec de vraies données de course | Exceptionnel | L | 3 |

Effort : S = quelques jours, M = une à deux semaines, L = plus de deux semaines, pour un développeur.

**Phase 1** : rendre le cœur rapide et utile pour une intervention mécanique.
**Phase 2** : faire revenir l'utilisateur (sa voiture, sa progression, la confiance).
**Phase 3** : les fonctions que personne d'autre ne propose gratuitement, côté piste.

## Règles communes

Elles valent pour toutes les specs. Les décliner, pas les contourner.

1. **Données réelles uniquement.** Ne jamais inventer une durée, un chapitre, un niveau ou un chiffre. Une valeur estimée s'affiche comme estimée, avec sa méthode (exemple : le niveau « estimé d'après l'intervention »).
2. **Licence vérifiée avant intégration.** Chaque source passe par [sources.md](sources.md). Une source marquée « à vérifier » ne part pas en production avant que sa licence soit lue à la source.
3. **Pas de compte utilisateur.** Tout ce qui est personnel reste dans le navigateur (`localStorage`, IndexedDB), avec un export JSON. Si une fonction a besoin d'un serveur, la spec le dit et liste les options.
4. **Site statique.** GitHub Pages, sans backend. Les données externes sont récupérées **au moment du build** (CI), pas à chaque visite, sauf mention contraire.
5. **Sécurité d'abord.** Freins, direction, airbags, haute tension, levage : toujours un avertissement visible et l'orientation vers un professionnel en cas de doute.
6. **Trois langues d'interface** (fr, en, es) via `t(fr, en, es)`. Contenu français d'abord.
7. **Design Paddock.** Jetons `--rl-*` et `--pd-*`, polices Archivo, Onest et Geist Mono ; voir [DESIGN.md](../../DESIGN.md). Pas de `backdrop-filter`, de gros `filter: blur()` ni de `text-wrap: balance` sur les titres : ils ont déjà figé le navigateur.
8. **Accessibilité.** Tout ce qui se clique se fait aussi au clavier ; cible tactile d'au moins 44 px ; `prefers-reduced-motion` respecté.

## Format d'une spec

Chaque fichier suit le même plan :

- **Pourquoi** : le problème, avec les chiffres réels du catalogue.
- **Expérience** : le parcours et une maquette d'écran.
- **Données** : d'où elles viennent, leur format, leur licence.
- **Implémentation** : les fichiers du dépôt à créer ou modifier.
- **Critères d'acceptation** : ce qui doit être vrai pour considérer le chantier fini.
- **Hors périmètre et risques.**

Les maquettes d'écran sont des croquis : leurs noms, dates, kilométrages et compteurs servent d'illustration et ne sont pas des données. Les chiffres cités dans le texte des specs, eux, viennent du catalogue au 12 novembre 2026.

## Décisions à prendre avant de démarrer

| Sujet | Question | Spec |
|-------|----------|------|
| Retours des utilisateurs | Quel petit service héberger pour les votes « ça m'a aidé » (aucun serveur aujourd'hui) ? | [06](06-confiance-et-qualite.md) |
| Logos de marques | Les afficher dans les filtres ? Ce sont des marques déposées. | [03](03-ma-voiture.md) |
| Données F1 | OpenF1 et Jolpica sont non officiels ; accepter de les citer comme source ? | [08](08-telemetrie.md) |
| Circuits | Accepter une source sous LGPL-3.0 (à confirmer) pour les tracés ? | [07](07-circuits-et-trajectoires.md) |
