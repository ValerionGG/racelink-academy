# Audit public-apis pour RaceLink — 26 octobre 2026

Lecture seule : aucune importation, modification UI, inscription ou dépense. Deux tests HTTP publics ponctuels, sans authentification ; aucun média téléchargé.

## Apport du dépôt

[public-apis/public-apis](https://github.com/public-apis/public-apis) est un annuaire, pas un accès unifié aux services. Les rubriques Social, Vehicle et Video ont été parcourues. Leur présence ne certifie ni disponibilité, ni gratuité intégrale, ni droits de réutilisation. Les cinq candidats ci-dessous ont été vérifiés auprès de leurs éditeurs.

## Cinq candidats

| Candidat | Apport concret | Accès et limites constatées | Décision |
|---|---|---|---|
| Dailymotion | Recherche réelle de vidéos, titres, descriptions et langues déclarées ; utile au français | La documentation legacy montre les listes publiques et annonce la v2. Pas de nouveau test réseau dans cet audit. Le collecteur existant utilise déjà cet accès, pagination, cache et arrêt sur 401/403/429. | Réutiliser `collect_dailymotion.py`, ne pas créer un doublon. Vérifier les checkpoints avant campagne. |
| NHTSA vPIC | Marques, modèles, identification VIN et spécifications déclarées | Service public sans inscription ; contrôle de trafic. Test Peugeot HTTP 200 : 8 modèles seulement, 504/505/405/604 et quatre scooters. La FAQ confirme une couverture des véhicules enregistrés pour usage/importation/vente US. Aucune procédure de vidange ni référence d'huile homologuée. | Source complémentaire d'identité véhicule, jamais remplacement du référentiel France ni preuve de compatibilité d'une réparation. |
| Bluesky | Recherche de publications par texte, langue et domaine, donc découverte possible de liens vers tutoriels | Le schéma expose `lang`, `domain`, pagination 1–100 ; cursor non exhaustif. Test standard `q=vidange&lang=fr&limit=5` sur `public.api.bsky.app` → 403. Arrêt, aucune variation de casse/route/identité. | Non exploitable sans résoudre l'accès officiel. Un texte Bluesky décrivant une vidéo n'est pas sa légende native. |
| TikTok Display / Embed | Display liste les vidéos du créateur qui autorise l'application. oEmbed enrichit une URL déjà connue | Display exige application approuvée, Login Kit, scopes et consentement du compte. oEmbed ne découvre aucune URL. La documentation du 22 octobre annonce la dépréciation d'Embed Videos au profit d'Embed Player. | Ne pas compter cela comme accès à tout TikTok. Vérifier l'intégration lecteur lors d'une prochaine modification ciblée. |
| Monocrawl | Nouveau fournisseur/MCP/skill listé ; découverte TikTok par mots-clés, Instagram Reels par mots-clés et lectures de comptes | Le README annonce 1 000 crédits/mois, mais tarification ET docs actuelles indiquent **150 crédits initiaux**, sans carte. Recherche TikTok 2 crédits, Reels Instagram 1 crédit ; chaque page coûte. Couverture de recherche Instagram incomplète et parfois retardée. Aucun compte créé et aucun crédit consommé. | Candidat pilote borné après constat du solde réel, pas solution gratuite démontrée pour 100 000 vidéos. Ne jamais importer les exemples `/sandbox`. |

Sources primaires :

- Dailymotion : [appels legacy](https://developers.dailymotion.com/v0/reference/perform-an-api-call), [migration v2](https://developers.dailymotion.com/docs/migrating-from-legacy-api-to-api-v2).
- NHTSA : [API](https://vpic.nhtsa.dot.gov/api/), [FAQ périmètre et gratuité](https://vpic.nhtsa.dot.gov/api/home/index/faq).
- Bluesky : [hôtes et authentification](https://bsky.network/docs/api-directory/), [schéma searchPosts](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/searchPosts.json).
- TikTok : [Display API](https://developers.tiktok.com/docs/en/display-api-overview), [prérequis](https://developers.tiktok.com/docs/en/display-api-get-started), [oEmbed et dépréciation](https://developers.tiktok.com/docs/en/embed-videos).
- Monocrawl : [MCP et skill](https://github.com/monocrawl/monocrawl-mcp), [tarifs actuels](https://www.monocrawl.com/pricing), [TikTok](https://www.monocrawl.com/docs/platforms/tiktok), [recherche Reels](https://www.monocrawl.com/docs/endpoints/instagram/search-reels).

## Réemploi du code déjà présent

Fichiers inspectés : `scripts/collect_dailymotion.py`, `OPEN-COLLECTOR.md`, `local_collect.py`, `creator_site_collect.py`, plus recherche ciblée dans les adaptateurs d'import et de fournisseurs.

- `local_collect.py` : recherche/chaînes YouTube, discovery via index, métadonnées séparées et validation. Ne pas refaire ce pipeline.
- `creator_site_collect.py` : extraction de permaliens sociaux sur pages d'éditeurs explicitement sélectionnées, file de revue ; ne visite pas TikTok/Instagram.
- `profile_campaign.py`, `scrapecreators_collect.py`, `brightdata_collect.py` : pagination et contrôles de crédits déjà disponibles pour les fournisseurs existants.
- Un éventuel adaptateur Monocrawl devrait produire une **file de revue** compatible avec ces contrats : URL stable, identifiant chaîne, titre natif, description, hashtags, langue déclarée, fournisseur/date et preuve du résultat réel. Aucun remplacement automatique des langues audio ou des procédures officielles par une inférence.

## Tests ponctuels observés

1. `GET https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=vidange&lang=fr&limit=5` : HTTP 403 ; arrêt sans retry.
2. `GET https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/Peugeot?format=json` : HTTP 200, Count=8, modèles 505, 405, 604, 504, Speedfight2, Vivacity, Looxor, Trekker.

Recommandation immédiate : réutiliser les collecteurs publics éprouvés ; conserver Monocrawl dans la liste des pilotes à solde gratuit vérifié. Le dépôt apporte surtout une nouvelle piste sociale vérifiable et une source officielle d'identification, pas un déblocage gratuit de centaines de milliers de tutoriels.

## Utilisation dans le projet

Le registre machine [collection/public-api-sources.json](collection/public-api-sources.json) distingue les sources intégrées, consultatives, suspendues et non configurées. Il ne déclenche aucun appel. Le [référentiel véhicule](VEHICLE-REFERENCE.md) est séparé des filtres et des procédures constructeur.

## Contrôle du nouvel outil

Le 26 octobre 2026, `vehicle_reference.py` a reçu 79 entrées pour Honda, année-modèle 2024, en un GET HTTP 200. Toutes catégories de véhicules confondues, pas uniquement des voitures. Les 14 tests hors réseau passent. Les réponses brutes restent privées ; rien n’a été importé dans le catalogue vidéo ni dans les filtres.

## Suite V32 : adaptateur Monocrawl

Le [collecteur borné](scripts/MONOCRAWL-COLLECTOR.md) est maintenant livré avec 42 tests hors réseau. Il prépare les recherches TikTok et Instagram, réserve leur plafond avant appel et sépare les réponses brutes des candidats à relire. Le MCP officiel est privilégié. Un résultat ou un coût incertain suspend la campagne ; aucune nouvelle tentative automatique ne consomme le crédit à l'aveugle.

L'outil est prêt mais le compte n'est pas connecté : aucun solde gratuit n'a été observé, aucun appel authentifié n'a été exécuté et aucun ajout TikTok/Instagram ne provient de ce connecteur. Les exemples et tests ne sont jamais des vidéos acquises.
