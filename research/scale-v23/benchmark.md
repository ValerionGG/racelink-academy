# Acquisition RaceLink : atteindre 100 000 à 300 000 références sans fabriquer le catalogue

Relevé du **24 octobre 2026**. Recherche documentaire primaire, lecture GitHub via `gh` et diagnostic Agent Reach. Aucun achat, inscription, connexion sociale, cookie, média, import ou modification de la base. Les chiffres de collecte parallèle sont attribués à leurs manifestes ; cette recherche n'a pas relancé ces collecteurs.

## Résultat final de la campagne parallèle

La tâche principale a constaté **430 nouvelles références intégrées**, portant le catalogue à **37 331 références**. Parmi ces ajouts, **194 portent un français déclaré par la plateforme ou inféré du texte source** ; ce nombre ne confirme pas la langue audio. Ces opérations d'intégration sont celles de la tâche principale, distinctes de la présente recherche documentaire.

| Collecte terminée | Occurrences avant dédoublonnage | Identités découvertes |
|---|---:|---:|
| Dailymotion et PeerTube | 16 524 | 13 493 |
| Découverte sociale Exa, 96 requêtes terminées | 2 763 | 1 822 |
| Total des identités découvertes | — | **15 315** |

Les **15 315 identités découvertes ne sont pas 15 315 tutoriels retenus**. Les références hors sujet, publicitaires, ambiguës, déjà présentes ou insuffisamment prouvées ont été écartées avant l'intégration. Le [rapport des plateformes ouvertes](OPEN-PLATFORMS.md) décrit le lot final de 304 candidats, dont 291 nouvelles identités ; la [revue sociale finale](social-final-review-notes.json) documente les décisions sur les 280 candidats issus des règles automatiques. Aucun de ces compteurs ne doit être confondu avec un visionnage ou une certification technique.

## Décision proposée : trois voies, dans cet ordre

1. **Exploiter les catalogues de créateurs déjà accessibles** : YouTube via le backend `yt-dlp` existant, puis API Data officielle dès qu'une clé est configurée ; Dailymotion **API historique** par auteur ; Exa pour découvrir de nouveaux liens et auteurs. C'est la voie immédiatement opérationnelle. Mesurer les références nouvelles retenues, pas les résultats de recherche.
2. **Préparer un seul pilote Apify ciblé**, après la connexion demandée par la racine et un budget explicite : TikTok + Instagram Reels, éventuellement Facebook. Pas de multiplication des fournisseurs ni des comptes sociaux. Les limites/refus déjà observés ne deviennent pas une autorisation de contourner l'accès. Une liste de créateurs et un échantillon contractuellement utilisable doivent précéder l'expansion.
3. **Constituer des flux de créateurs autorisés** pour les métadonnées et légendes : export volontaire, TikTok Display, Instagram professionnel, Pages Facebook, Vimeo public. C'est la voie la plus contrôlable pour des mises à jour durables et des preuves de texte ; elle exige des partenaires ou des applications autorisées. Elle n'apporte pas aujourd'hui 100 000 publications sociales françaises.

**Ne pas acheter un catalogue généraliste de 100 000 lignes sur la seule promesse de volume.** Le pilote Instagram public audité le 21 octobre a donné zéro candidat utile sur le sample réellement reçu ; les recherches Dailymotion actuelles montrent aussi un fort bruit. Le débit technique n'est pas le facteur limitant principal : la pertinence, les doublons, le français démontré et les droits le sont.

## Accès réellement constatés

| Voie | État au 24 octobre | Ce que cet état permet d'affirmer |
|---|---|---|
| Agent Reach → YouTube | `doctor --json` : `active_backend=yt-dlp`, statut `ok` | Outil disponible ; aucune promesse d'exhaustivité ni de débit illimité. |
| GitHub `gh` | Plusieurs GET réels réussis sur dépôts et fichiers | Métadonnées et licences vérifiées ; aucune mutation. |
| Dailymotion historique `/videos` et listes d'auteurs | Collecte terminée : **162 pages HTTP 200**, 15 438 lignes Dailymotion | Route publique utilisée sans authentification. Avec PeerTube : 13 493 identités découvertes et 304 candidats finaux, dont 290 Dailymotion et 14 PeerTube. [Rapport final](OPEN-PLATFORMS.md). |
| Dailymotion v2 `/v2/profiles/xiy/videos` | Une sonde sur l'exemple documenté : **401**, arrêt | Cette version n'est pas démontrée anonyme dans cet environnement. Ne pas généraliser cet échec à l'API historique. [Preuve](proofs/dailymotion-public-access.json). |
| Exa | Doctor ne teste pas le service ; **96 requêtes réelles terminées par la tâche principale**, 2 763 occurrences et 1 822 identités | L'ancien quota 429 du 21 octobre n'est plus l'état courant. Les titres indexés restent distincts des légendes natives et de l'audio. Aucun appel Exa lancé par cette recherche. |
| OpenCLI Instagram/Facebook | Extension installée mais non connectée, `active_backend=null` | Aucun catalogue de comptes sociaux disponible par cette route. |
| Apify | Console déconnectée, vérifiée par la racine | Connexion demandée à l'utilisateur ; aucun Actor lancé pour cette recherche. |
| Clés API | Racine : absence des variables Apify, TikHub, Bright Data, YouTube, Firecrawl ; valeurs non lues | Aucun de ces accès payants/officiels n'est prêt à lancer ici. Ce constat n'est pas une inspection des autres stockages de secrets. |
| vidIQ | Racine : 4 crédits ; recherche IG/TT annoncée à 5 | Ne finance pas même une recherche concernée ; Instagram profile reels coûte aussi 5 crédits, limite 12 résultats sans pagination (métadonnées outil confirmées par la racine). Ce n’est pas une voie de masse même après recharge. |

Agent Reach local reste en 1.5 ; contrôle de mise à jour : 1.6 disponible, sans installation. Le routeur n'accorde ni quota fournisseur, ni accès privé, ni licence vidéo. [Source Agent Reach](https://github.com/Panniantong/Agent-Reach).

## Quotas officiels : ce qui change réellement le dimensionnement

### YouTube : énumérer des chaînes, ne pas dépendre exclusivement de la recherche

La [table officielle actuelle](https://developers.google.com/youtube/data/determine_quota_cost), mise à jour le 15 octobre 2026, prévoit **100 appels `search.list` par jour dans un quota séparé**, et **10 000 unités/jour** pour les autres opérations. Les listes de chaînes, playlists et vidéos coûtent 1 unité. L'ancienne formule «search coûte 100 unités du même budget» n'est plus celle de cette page.

[`playlistItems.list`](https://developers.google.com/youtube/data/reference/rest/v3/playlistItems/list) retourne jusqu'à 50 éléments par page. Avec une liste de chaînes/identifiants déjà connue, hypothèse de pages pleines puis enrichissement des IDs par lots de 50 : environ **4 000 appels pour 100k** ou **12 000 pour 300k**, plus résolution des chaînes et reprises. Ce sont des minima de calcul, pas une durée garantie ni un stock confirmé. Un projet au quota par défaut peut donc dimensionner 100k en un quota journalier, 300k sur au moins deux ; les pages courtes augmentent le coût. [`videos.list`](https://developers.google.com/youtube/data/reference/rest/v3/videos/list).

La clé API de projet manque encore. À long terme, prévoir une mise à jour/suppression des données API selon la politique des 30 jours, l'attribution YouTube et les contraintes de stockage et de données dérivées. Une base permanente copiée une fois ne satisfait pas ce contrat ; une licence Creative Commons doit être lue sur chaque vidéo, pas déduite de la chaîne. [Conditions développeur](https://developers.google.com/youtube/terms/developer-policies).

### Dailymotion : distinguer deux contrats

L'API historique documente les ressources publiques et les listes, et la collecte parallèle prouve son fonctionnement actuel. Ses listes sont limitées à 100 éléments/page dans la collecte. [Référence historique](https://developers.dailymotion.com/v0/reference/perform-an-api-call).

La [documentation v2 des grands catalogues](https://developers.dailymotion.com/docs/browse-large-video-catalog) indique 100 par page, 10 pages puis partition temporelle. Elle affirme que les données publiques ne nécessitent pas d'authentification, mais son exemple inclut un jeton ; la sonde anonyme a renvoyé 401. Ne pas migrer automatiquement le collecteur qui fonctionne. Aucun quota global garanti ni tarif par ligne n'a été établi ici. Les séries par auteur sont préférables à une recherche large où «freinage» et «pilotage» ramènent actualité, aviation et divertissement.

### TikTok, Instagram, Facebook, Vimeo : accès officiel ciblé

| Service | Portée utile | Quota / volume documentaire | Accès à obtenir |
|---|---|---|---|
| [TikTok Display : vidéo/list](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-list) | Vidéos publiques **du créateur qui autorise l'application** |20/page : 5 000 pages pour 100k, 15 000 pour 300k si tous les catalogues existent ; [limite 600 requêtes/min](https://developers.tiktok.com/docs/en/tiktok-api-v2-rate-limit) | Application approuvée, OAuth et `video.list`, créateurs volontaires. Pas une recherche de tout TikTok. |
| [TikTok Research FAQ](https://developers.tiktok.com/docs/en/research-api-faq) | Recherche publique approuvée |1 000 requêtes et 100 000 records/jour | **Écarté** : chercheurs admissibles et projet approuvé ; créateurs, annonceurs, usages commerciaux explicitement inéligibles. Ne pas présenter RaceLink comme projet académique. |
| [Instagram API, collection officielle Meta](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api) | Comptes professionnels et fonctionnalités documentées BusinessDiscovery/hashtags | Pagination par curseur ; pas de quota universel prouvé par les pages consultées | App, jeton, compte professionnel et permissions adaptées. Les comptes grand public ne sont pas couverts par ce parcours. |
| [Facebook Pages API](https://developers.facebook.com/docs/pages-api/getting-started/) | Pages autorisées et accès public soumis aux permissions/features Meta | Documentation directe 429 lors de cette recherche : chiffres non vérifiés, aucun quota inventé | Page/application/permissions ; accès tiers à confirmer avec Meta. Un compte Facebook connecté n'est pas une permission globale. |
| [Vimeo API](https://help.vimeo.com/hc/en-us/articles/12427702473105-API-technical-and-developer-prerequisites) | Métadonnées publiques, listes de créateurs | API accessible sans abonnement payant requis ; [429 et arrêt documentés](https://help.vimeo.com/hc/en-us/articles/12427783954065-Rate-limits), plafond exact dépendant de l'accès | App et [jeton public](https://help.vimeo.com/hc/en-us/articles/12427789081745-How-to-generate-a-personal-access-token), même pour données publiques. Pas encore configuré. |

Aucune de ces API de métadonnées ne vaut accès universel aux sous-titres ou licence de retranscription/republication. Une légende originale peut démontrer la langue du **texte**, pas la langue parlée.

## Coûts comparables pour 100k et 300k lignes brutes

USD, hors taxes, revue éditoriale et infrastructure RaceLink. Les lignes doivent encore être dédupliquées et qualifiées. Tarifs vérifiés le 24 octobre dans les métadonnées publiques des Actors ; aucun run créé. [Snapshot intégral et empreintes](proofs/apify-public-prices.json).

| Apify Actor | Starter/Bronze par 1k | 100k brutes | 300k brutes | Scale/Silver : 100k / 300k, avec minimum mensuel 199 $ |
|---|---:|---:|---:|---:|
| [TikTok Scraper](https://apify.com/clockworks/tiktok-scraper) |3,00 $ |300 $ |900 $ |230 $ /690 $ |
| [Instagram Reel Scraper](https://apify.com/apify/instagram-reel-scraper) |2,30 $ |230 $ |690 $ |199 $ /420 $ |
| [Facebook Posts Scraper](https://apify.com/apify/facebook-posts-scraper) |4,00 $ |400 $ |1 200 $ |250 $ /750 $ |

Starter coûte 19 $/mois **incluant 19 $ de consommation**, Scale 199 $ incluant 199 $ : ne pas additionner le prépayé deux fois. Les totaux de la table supposent une consommation sur un mois et uniquement l'événement principal. Ajouter 0,001 $ par démarrage pour ces Actors, éventuels stockage/événements et options. Free fournit 5 $/mois et des tarifs unitaires supérieurs ; ce n'est pas un forfait 100k. [Plans Apify](https://apify.com/pricing).

La transcription est un budget distinct : au palier Bronze, IG/TT affichent 0,041 $ par **minute commencée et par vidéo**. 100k clips d'au plus 1 minute ajoutent donc 4 100 $, 300k ajoutent 12 300 $, avant contrôle de qualité et droits. Ne pas activer vidéo/audio, transcription, commentaires, popularité ou filtres payants sans besoin concret. Facebook Posts peut facturer des posts texte/photo finalement exclus : son prix par tutoriel vidéo sera supérieur.

Pour un mélange de 100k lignes **hypothétique**, 50 000 YouTube + 20 000 TikTok + 20 000 Instagram + 5 000 Facebook + 3 000 Dailymotion + 2 000 Vimeo : consommation Apify Bronze **126 $**, et **378 $** pour trois fois ce mélange. Le calcul ne garantit pas ces stocks ni leur langue. Ce calcul facture uniquement les lignes Apify. Il n’est pas un devis complet des autres voies : yt-dlp n’utilise pas le quota officiel YouTube ; les coûts d’infrastructure et les éventuelles conditions des API restent séparés. Le coût de découverte, de revue et de maintien reste séparé.

### Alternatives évaluées, pas de comptes à multiplier

| Offre | Prix public et calcul | Décision RaceLink |
|---|---|---|
| [TikHub](https://tikhub.io/faq) |0,001–0,01 $/requête réussie selon endpoint ; 10 RPS par défaut. 100k appels individuels : 100–1 000 $, 300k : 300–3 000 $, avant remises progressives. Les pages peuvent contenir plusieurs posts : **pas de prix fiable par référence** sans essai. Dataset TikTok annoncé 2 $/1k dans la tranche 100k–500k, minimum 150 $ : 200 $/100k, 600 $/ 300k si filtre et licence conviennent. | Compte/clé/solde absents. Pas retenu en parallèle d'Apify sans avantage mesuré. Ses conditions renvoient la responsabilité de l'usage des données à l'utilisateur ; SDK Apache ≠ licence des vidéos. |
| [Bright Data Reels](https://brightdata.com/products/datasets/instagram/reels) |109,5 millions de lignes annoncés globalement ; jusqu'à 0,0025 $/ligne, minimum 250 $. Exemple 100k = 250 $, 300k = 750 $ à ce taux, devis filtré requis. | Préférer un export déjà constitué avec licence explicite à une nouvelle extraction. Le total global n'établit aucune quantité FR auto. Aucun contrat/compte actif ni licence de republication validés ici. |
| [Exa](https://exa.ai/pricing) | Auto Search : 7 $/1 000 requêtes jusqu'à 10 résultats, Lite : 4 $ ; 1 $/1 000 requêtes par résultat supplémentaire au-delà de 10. En théorie, 10 000 requêtes pleines donnent 100k **occurrences**, soit 70 $ Auto ou 40 $ Lite ; 300k occurrences coûtent 210 $/120 $, sans déduplication. Contents : 1 $/1 000 pages/type en supplément. | **Déjà actif via la racine.** Excellent pour découverte, pas preuve de légende native ni inventaire exhaustif. Le coût facturé de la route MCP dépend de son compte ; ces tarifs API ne prouvent pas son solde. |

Les tarifs fournisseurs ne comprennent pas une autorisation des titulaires de contenus. Aucun service n'a été utilisé pour contourner un refus natif Instagram/TikTok. L'achat éventuel reste une décision séparée, sur un échantillon précis et un contrat revu.

## Rendement : budgeter les références retenues

Définir `p = nouvelles identités pertinentes et utilisables / lignes facturées`. Il inclut doublons, hors-sujet, publicités, posts non vidéo, français seulement supposé et preuves insuffisantes. Pour un objectif **nouveau** de 100k ou 300k :

| Hypothèse de rendement, non mesurée | Lignes pour 100k retenues | Lignes pour 300k retenues | Coût IG Bronze correspondant |
|---|---:|---:|---:|
|60 % : créateurs très ciblés |166 667 |500 000 |383,33 $ /1 150 $ |
|30 % : sources mixtes |333 334 |1 000 000 |766,67 $ /2 300 $ |
|10 % : recherche large |1 000 000 |3 000 000 |2 300 $ /6 900 $ |

Le lot final Dailymotion/PeerTube contient **304 candidats sur 13 493 identités découvertes**, dont 291 identités nouvelles après déduplication contre le catalogue. Il remplace les comptes lexicaux provisoires : ne pas extrapoler un rendement de 60 % à cette recherche large. [Méthode et exclusions finales](OPEN-PLATFORMS.md). Le sample [Bright Data publié sur GitHub](https://github.com/luminati-io/Instagram-Reels-dataset-samples), audité localement le 21 octobre, contenait 1 000 lignes réelles malgré 6 850 annoncées ; 30 légendes présélectionnées relues, zéro candidat admissible. Ce n'est ni une mesure exhaustive de toutes les langues, ni le taux du catalogue payant filtré, mais cela réfute l'idée qu'un gros échantillon généraliste suffit.

La revue humaine de 100k fiches à 20 secondes chacune représenterait 556 heures ; 300k, 1 667 heures. Estimation de charge, pas temps mesuré. La méthode scalable est une qualification automatique conservatrice, des preuves traçables et des échantillons stratifiés ; le badge de sélection éditoriale reste réservé aux fiches effectivement relues.

## Réservoirs pédagogiques et français : preuves de volume, pas extrapolation commerciale

| Source primaire | Signal utile | Limite de volume / droits |
|---|---|---|
| [AUTODOC Club FR](https://club.auto-doc.fr/) |3 714 tutoriels vidéo annoncés, 21 839 PDF séparément ; modèles et opérations explicites. | Déjà très représenté dans RaceLink. Ne pas additionner PDF, variantes et langues comme nouvelles vidéos uniques ; comparer IDs. |
| [SKF vidéothèque FR](https://automotive.skf.com/eur/fr/tech-center/video-library) |618 vidéos affichées, listes de lecture par langue et tutoriels d'installation. | Catalogue multilingue avec promotions et événements, **pas 618 FR pédagogiques**. Très bon vivier de créateurs/playlistIDs, pas une licence libre. |
| [Valeo TechAssist FR](https://www.valeoservice.fr/fr/techassist) | Vidéos de diagnostic et montage, durées et titres précis ; capteurs, embrayage, freinage, climatisation. | Le chiffre 70 000 concerne les **pièces**, pas les tutoriels. Pas de volume vidéo global établi. |
| [HELLA TechWorld](https://www.hella.com/techworld/en/) | Plus de 1 500 conseils de réparation annoncés, sujets électriques/ADAS et vidéos de support. |1 500 conseils ne signifie pas 1 500 vidéos. Prioriser les pages techniques FR et leur vidéo effectivement liée. |
| [Atelier Oscaro](https://www.oscaro.com/fr/atelier/) | Communauté d'auteurs et centaines de tutos par marque/modèle ; section vidéo distincte. | Quantité vidéo exacte non publiée ici ; pédagogie et contenu commercial coexistent. |
| [HPA](https://www.hpacademy.com/) | Câblage motorsport, ECU, moteur, suspension, pilotage ; cours et modules structurés. | Nombreux contenus payants. Collecter uniquement les références réellement publiques, pas les cours verrouillés. |
| [HowTo100M, Inria](https://www.di.ens.fr/willow/research/howto100m/) |1,2 million de vidéos YouTube, 136 millions de segments annoncés, intention pédagogique ; catégories auto présentes dans les ressources du projet. | Dataset 2019, non spécialisé FR. Ni disponibilité actuelle des IDs ni licence de republication des légendes établie sur la page consultée. Source de recherche éventuelle, **pas import automatique**. |
| [Sample Reels officiel BrightData sur GitHub](https://github.com/luminati-io/Instagram-Reels-dataset-samples) | Schéma URL/auteur/légende et fichier public déjà audité. | Licence du dépôt non détectée ; rendement local nul, voir plus haut. Pas de nouvelle collecte de ce sample. |

Pour la priorité FR, constituer une liste de créateurs attestés par leur propre site/chaîne, puis classer **chaque titre/légende**. Région France, nom de créateur, langue de requête ou hashtag FR ne prouvent ni langue du texte ni audio. Les portails officiels ci-dessus servent de seeds vérifiables, pas de liste de comptes sociaux inventée.

## GitHub : outils effectivement examinés

Étoiles et dates UTC au 24 octobre 2026, figées dans [github-repositories.json](proofs/github-repositories.json). Des étoiles ne prouvent ni droit d'accès ni qualité éditoriale.

| Dépôt | Étoiles / dernière poussée | Licence / conclusion |
|---|---|---|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) |201 149 /23 octobre | Unlicense. Retenu pour le pipeline metadata YouTube existant. Le [code Instagram](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/instagram.py) marque toujours `InstagramUserIE._WORKING=False` : ne pas vendre une collecte de profilIG exhaustive. |
| [Instaloader](https://github.com/instaloader/instaloader) |13 662 /23 octobre | MIT. Outil maintenu, mais disponibilité de profils publics/session/rate-limits dépendante d'Instagram ; aucun accès autorisé nouveau ici. Pas de remplacement automatique après refus. |
| [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) |67 961 /15 octobre | Licence personnalisée **Non-Commercial Learning 1.1**, limite l'usage à l'étude/recherche et exclut le crawling à grande échelle ; autorisation écrite pour usage commercial. Support principal Douyin/XHS/Bilibili/etc, pas une preuve d'accès TikTok international/IG. **Écarté.** |
| [TikHub Python SDK](https://github.com/TikHub/TikHub-API-Python-SDK) |923 /3 octobre | Apache 2.0. SDK client d'un service à clé, pas acquisition gratuite autonome. |
| [Apify Python client](https://github.com/apify/apify-client-python) |104 /23 octobre | Apache 2.0. Bon client pour consommer un dataset autorisé et tracer coût/statut. Pas installé/exécuté. |
| [Agent Reach](https://github.com/Panniantong/Agent-Reach) |101 418 /23 octobre | MIT. Routeur utilisé ; diagnostics conservateurs. Ne résout pas quotas/licences. |

README/licences utiles sont archivés dans `proofs/`. Aucun code externe exécuté ni dépendance installée.

## Prochain lot concret et seuils d'arrêt

1. Les lots Dailymotion/PeerTube et Exa de cette campagne sont terminés et relus ; leur intégration a été réalisée séparément par la tâche principale. Conserver les comptes bruts, uniques, nouveaux, retenus, français du texte et audio inconnu, ainsi que les empreintes. Cette recherche n'a réalisé aucun import.
2. Après connexion Apify, vérifier tarif effectif, solde et provenance de la liste ciblée. Le plan effectivement préparé contient **14 collectes bornées : 10 TikTok × 60 publications maximum et 4 Instagram × 100**, soit une cible supérieure cumulée de **1 000 publications brutes**. Le fichier `apify-french-pilot/plan.json` porte le statut **`prepared_not_executed`** : aucun résultat de ce pilote n'est compté dans les 430 ajouts. Ne pas traiter des profils ou URLs au refus d'accès non résolu. Les exports volontaires peuvent alimenter le même pilote sans extraction.
3. Les plafonds préparés totalisent **5 $ maximum** : 10 runs TikTok plafonnés chacun à 0,30 $ et 4 runs Instagram à 0,50 $, métadonnées seules. Vérifier ces limites au lancement, borner la durée et ne pas renouveler automatiquement. Les Actors sont `PAY_PER_EVENT` : utiliser **`maxTotalChargeUsd`** ; ne pas se reposer sur `maxItems`, documenté pour `PAY_PER_RESULT`. [Contrat Run Actor](https://docs.apify.com/api/v2/actors-runs-post). La limite de publications doit aussi être portée par le schéma propre à chaque Actor. Un plafond n'est ni une dépense déjà engagée, ni une garantie de 1 000 tutoriels utiles.
4. Évaluer le lot sur 100 fiches stratifiées par créateur/plateforme/langue. Rejeter procédures manifestement dangereuses, clips purement publicitaires, sport-spectacle, vélo/moto classés voiture et langue déduite du seul profil. Exiger des preuves avant adaptation véhicule.
5. Étendre par 5k puis 20k uniquement si le rendement net, la diversité et le coût par référence utile sont acceptables. Si la longue traîne épuise le stock pédagogique, arrêter plutôt que remplacer les tutoriels par de l'actualité ou des doublons.

**Estimation honnête :** 100k références multilingues à dominante YouTube est une cible technique plausible à tester par inventaire, pas un stock déjà démontré. 100k tutoriels **FR TikTok/Instagram** n'est établi par aucune source consultée. 300k requiert un réservoir beaucoup plus large et des droits/accès soutenables ; ni un quota 100k/jour ni un tarif 0,0025 $/ligne ne le démontrent.

Les accès requis, la preuve actuelle et les conditions de passage à l'étape suivante sont structurés dans [access-required.json](access-required.json). La liste des comptes manquants n'est pas une demande d'en créer plusieurs ni de multiplier des comptes pour contourner des quotas.
