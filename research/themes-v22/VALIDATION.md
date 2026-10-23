# Validation — thèmes V22

[Version publique](https://valeriongg.github.io/racelink-academy/?release=themes-v22&build=9985987) · [Commit 9985987](https://github.com/ValerionGG/racelink-academy/commit/99859870e3fa785367d0112d99cebbe32c893324) · [Workflow réussi](https://github.com/ValerionGG/racelink-academy/actions/runs/40016757865).

## Preuves distinctes

- **109 contrats applicatifs** : [rapport agrégé](validation-results.json).
- **36 tests du thème** : [rapport](theme-checks.json), source SHA-256 `cfdce63a386789cf225e1120bafa39571376c8b11a00fb00a664ae0d29e4bb27`. Total unique hors navigateur : **145** ; les tests de thème déjà présents dans l’agrégat ne sont pas additionnés deux fois.
- **14 scénarios/observations navigateur** : [verdicts et portée](browser-checks.json), fenêtres simulées de 320, 390, 768, 1280, 1440 px. Le rapport identifie le commit vérifié ; il reste l’autorité sur les étapes effectivement réalisées.
- **19 fichiers publics** : [réponses HTTP et comparaison d’octets](public-assets-check.json), exactement identiques à leurs fichiers du dépôt pour le commit indiqué. Les 18 fichiers d’interface sont également comparés aux sources et à l’export local, en tenant compte du préfixe de publication.
- **12 photos** : [inventaire et empreintes](assets-baseline.json), octets recontrôlés dans source, export local et site Git.
- **Catalogue inchangé** : [empreintes](catalogue-integrity.json), comparaison avec la référence V21 ; 36,901 vidéos et 11 guides selon le contrôle public.

Le catalogue local et le catalogue publié conservent leurs octets et leurs empreintes propres : leurs dates de génération diffèrent. Tous les champs pédagogiques sont comparés égaux ; seule la propriété `generated_at` est exclue de cette comparaison JSON. Dans `config.json`, seule l’empreinte `catalog_sha256` diffère et désigne le JSON correspondant. Chaque archive gzip se décompresse exactement vers son propre JSON. Le rapport HTTP ne prétend donc pas que les deux fichiers de configuration ont des octets identiques.

## Portée

Clair et Sombre concernent accueil, collections photographiques, résultats, contrôles, menus, véhicule et lecteurs. Le choix est enregistré lorsqu’un stockage local est disponible. Sans choix explicite, le système détermine le thème ; les deux commandes visibles sont Clair et Sombre. La langue de contenu et la recherche restent indépendantes du thème.

Les tests isolés utilisent des doubles DOM et ne prouvent pas le rendu. Les captures sont des fenêtres de navigateur simulées, pas un appareil physique. Aucun audit WCAG exhaustif, lecteur d’écran, contrôle de chaque combinaison de langue/contenu ou validation de lecture de chaque vidéo externe n’est revendiqué. Les preuves historiques ne sont pas transformées en tests V22. Aucune donnée pédagogique, procédure, transcription ou compatibilité n’a été ajoutée par cette livraison.

## Captures

[Accueil clair mobile](home-light-mobile.png) · [Accueil sombre mobile](home-dark-mobile.png) · [Résultats guides clairs](guide-results-light-mobile.png) · [Filtres clairs](filters-light-mobile.png) · [Sources du guide en clair](guide-sources-light-mobile.png).

## Historique et paquet

Les documents remplacés sont conservés dans [history-before-v22](history-before-v22/). Les rapports V21 restent dans [cinema-v21](../cinema-v21/VALIDATION.md). Ce finaliseur n’exécute ni build, ni export, ni test, ni commit, ni publication, ni création du ZIP. Le paquet doit contenir ce rapport et `assets-baseline.json` ; le contrôle et la création du ZIP restent une étape distincte.
