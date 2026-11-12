# Sources à intégrer

Recherche du 12 novembre 2026. **Statut** :
- **Vérifié** : l'accès et la licence ont été confirmés sur une page officielle de la source.
- **À vérifier** : l'information vient d'un tiers ou reste incomplète. Lire la licence à la source avant de mettre en production.

Les données externes se récupèrent au build (CI), se mettent en cache dans `site/catalog/` et citent leur source dans l'interface.

## Voiture : sécurité, rappels, identification

| Source | Ce qu'elle apporte | Accès | Licence | Statut | Spec |
|--------|--------------------|-------|---------|--------|------|
| [RappelConso V2](https://www.data.gouv.fr/datasets/rappelconso-v2-rappels-de-produits/) (DGCCRF) | Rappels de produits en France ; catégorie « Automobiles et moyens de déplacement », sous-catégorie « Automobiles, motos, scooters » | API Opendatasoft (Explore v2.1) sur data.economie.gouv.fr ; la V1 est remplacée fin 2025 | Licence Ouverte 2.0 selon un site tiers | À vérifier : URL de l'API, syntaxe du filtre, limite de 10 000 lignes signalée sur la V1 | [03](03-ma-voiture.md) |
| [NHTSA Recalls](https://www.nhtsa.gov/node/102181) | Rappels par marque, modèle et année : `api.nhtsa.gov/recalls/recallsByVehicle?make=&model=&modelYear=` | Gratuit, sans clé | Données publiques américaines | Vérifié pour l'accès ; utile seulement pour les modèles vendus aux États-Unis | [03](03-ma-voiture.md) |
| NHTSA vPIC (décodage VIN), via [ce guide](https://www.carwhere.com/guides/nhtsa-vin-decoder-api) | Marque, modèle et année depuis un VIN ; jusqu'à 50 VIN par appel | Gratuit, sans clé ; répond toujours HTTP 200, lire `ErrorCode` | Données publiques américaines | À vérifier : couverture des VIN européens et appel direct depuis le navigateur (CORS) | [03](03-ma-voiture.md) |
| [ADEME Car Labelling](https://www.data.gouv.fr/datasets/ademe-car-labelling) | Consommation et CO₂ des voitures neuves en France | 2 API listées sur data.gouv.fr ; seule la dernière mise à jour est exposée | Licence de data.gouv.fr | À vérifier : URL des API et fréquence (trimestrielle ou semestrielle selon les pages) | [03](03-ma-voiture.md) |
| [Euro Rescue](https://www.etsc.eu/new-app-helps-rescue-workers-extricate-vehicle-occupants/) (Euro NCAP et CTIF) | Fiches de désincarcération ISO 17840 par modèle (environ 1 550 fiches en 4 langues) | Application gratuite ; **aucune API ni donnée ouverte trouvée** | Le protocole Euro NCAP exige une autorisation écrite pour republier | Lien seulement | [01](01-fiche-intervention.md) |
| [Wikidata](https://www.wikidata.org/wiki/Q1362426) et Wikimedia Commons | Modèles de voitures (élément « modèle d'automobile », Q3231690), dates, photos | SPARQL sur query.wikidata.org ; licence de chaque photo via l'API `imageinfo` de Commons | Données Wikidata en CC0 ; photos sous licences variées, souvent CC BY ou BY-SA (attribution obligatoire) | À vérifier : modélisation des générations | [03](03-ma-voiture.md) |
| [car-brand-logos](https://cdn.jsdelivr.net/npm/car-brand-logos@1.0.0/README.md) | 184 logos SVG et PNG avec un manifeste | npm | MIT pour la structure ; **les logos restent des marques déposées** | Décision produit en attente | [03](03-ma-voiture.md) |
| Contrôle technique : [annuaire des centres](https://www.data.gouv.fr/datasets/annuaire-des-centres-de-controle-technique) et [prix](https://www.data.gouv.fr/datasets/prix-des-controles-techniques) | Centres agréés et tarifs | data.gouv.fr | Licence de data.gouv.fr | Vérifié pour l'existence. **Aucun jeu ouvert sur les défaillances** : seul le [bilan UTAC en PDF](https://www.ecologie.gouv.fr/sites/default/files/documents/bilan_vl_final.pdf) existe | [02](02-symptomes-et-codes.md) |

## Diagnostic et réparation

| Source | Ce qu'elle apporte | Accès | Licence | Statut | Spec |
|--------|--------------------|-------|---------|--------|------|
| [OBDex](https://github.com/foerbsnavi/OBDex) | 9 533 codes défaut OBD-II génériques en JSON ; codes constructeur exclus | GitHub | Le README annonce CC0 pour les données et MIT pour les outils, mais GitHub affiche « Unknown » | À vérifier : lire `LICENSE-DATA` | [02](02-symptomes-et-codes.md) |
| [dtcdb](https://awesome.ecosyste.ms/projects/github.com%2Ftodrobbins%2Fdtcdb) | Base de codes défaut en CSV | GitHub | MIT | Plan B : dernière mise à jour en 2013 | [02](02-symptomes-et-codes.md) |
| [iFixit](https://www.ifixit.com/Info/Licensing) | Guides structurés (étapes, outils, pièces, difficulté sur 5 niveaux, durée) ; API publique `https://www.ifixit.com/api/2.0/` sans clé | API publique | CC BY-NC-SA 3.0. Usage commercial sous licence, **entraînement d'IA interdit**, usage prévu : résumé et lien | Vérifié | [01](01-fiche-intervention.md) |

**iFixit sert surtout de modèle de format** : difficulté, durée, outils, pièces, étapes illustrées. On reprend la structure, pas le contenu. Un lien vers un guide iFixit reste possible avec un résumé court.

## Piste, pilotage, télémétrie

| Source | Ce qu'elle apporte | Accès | Licence | Statut | Spec |
|--------|--------------------|-------|---------|--------|------|
| [TUMFTM racetrack-database](https://gh.hhj520.top/TUMFTM/racetrack-database) | Ligne médiane, largeur de piste et trajectoire optimale pour plus de 20 circuits (F1, DTM) | GitHub (CSV) | LGPL-3.0 selon [ecosyste.ms](https://awesome.ecosyste.ms/projects/63690) | À vérifier : fichier `LICENSE` | [07](07-circuits-et-trajectoires.md) |
| [OpenF1](https://openf1.org/docs) | Télémétrie F1 : vitesse, régime, rapport, gaz, frein (`car_data`, environ 3,7 Hz), tours, pneus, météo | `https://api.openf1.org/v1`. Historique (depuis 2023) gratuit et sans authentification ; temps réel payant | Projet non officiel ; licence du dépôt à lire | À vérifier : licence et disponibilité historique de `/location` | [08](08-telemetrie.md) |
| [Jolpica-F1](https://docs.fastf1.dev/api_reference/jolpica.html) | Remplaçant d'Ergast : résultats, qualifications, tours, arrêts, depuis 1950 | `https://api.jolpi.ca/ergast/f1` ; mettre en cache | Dépôt sous Apache-2.0 | À vérifier : clé requise ou non (sources contradictoires) | [08](08-telemetrie.md) |
| [grafana-simracing-telemetry](https://awesome.ecosyste.ms/projects/github.com%2Falexanderzobnin%2Fgrafana-simracing-telemetry) et [SimTelemetry](https://1clonegithubbyxjn.1934672944.workers.dev/yuan-thomas/SimTelemetry) | Analyse de sa propre télémétrie en sim racing (Assetto Corsa, ACC, iRacing selon les outils) | Logiciels à installer | Variable | Lien et tutoriel seulement : la mémoire partagée des jeux n'est pas lisible depuis un site web | [08](08-telemetrie.md) |

## Briques techniques

| Brique | Usage | Licence | Statut | Spec |
|--------|-------|---------|--------|------|
| [Screen Wake Lock API](https://web.dev/blog/screen-wake-lock-supported-in-all-browsers) | Garder l'écran allumé en mode atelier ; Chrome 84, Firefox 126, Safari 16.4 ; HTTPS obligatoire ; le verrou peut être retiré par l'appareil | Standard web | Vérifié | [04](04-mode-atelier.md) |
| Web Speech API (`SpeechRecognition`) | Commandes vocales « suivant », « répète » | Standard web | À vérifier : support navigateur, surtout Firefox et iOS | [04](04-mode-atelier.md) |
| [YouTube IFrame Player](https://developers.google.com/youtube/player_parameters?hl=it-IT) | `start`, `end`, `enablejsapi=1`, `seekTo()` pour jouer une étape ; le départ peut tomber jusqu'à environ 2 s plus tôt (image clé) | Conditions YouTube API Services | À vérifier : règles sur l'usage des sous-titres | [04](04-mode-atelier.md) |
| [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs) | Répétition espacée (algorithme FSRS) pour les révisions | MIT | Vérifié | [05](05-progression.md) |
