# Collecte sociale V25 — pilote Apify limité aux crédits gratuits

État vérifié le 26 octobre 2026 : ce paquet est prêt à être prévisualisé et testé. Aucun compte n'a été créé, aucun appel authentifié n'a été effectué, aucun Actor n'a été lancé et aucun crédit n'a été consommé par cette recherche. Les vérifications réseau réalisées ont uniquement lu les fiches et schémas publics des fournisseurs. Le rendement réel TikTok/Instagram reste donc à mesurer.

## Livrable exécutable

`launch_free_pilot.py` est autonome dans ce dossier avec `verify_apify_free_credits.py`, les deux fiches d'acteurs, leurs schémas et `pilot/`. Il ne modifie pas l'ancien `start_social_batch.py`, dont la garde `free_credits_only` reste intacte. Python 3.10+ et le paquet local `jsonschema` sont nécessaires ; aucun outil ne s'installe automatiquement.

Depuis ce dossier, aperçu entièrement hors ligne, sans lecture de jeton :

```powershell
python -B -X utf8 launch_free_pilot.py
python -B -X utf8 launch_free_pilot.py --batch fr-tiktok-06
python -B -X utf8 verify_apify_free_credits.py
```

Après authentification, un opérateur configure explicitement `APIFY_TOKEN` dans son environnement local, sans le transmettre dans une conversation, une URL, un fichier de projet ou l'historique des commandes. La connexion OAuth du navigateur ne configure pas automatiquement cette variable. Le programme ne cherche jamais de jeton dans un navigateur, un fichier de configuration, un coffre ou d'autres variables.

Lecture facultative du budget, puis lancement explicite d'un profil :

```powershell
python -B -X utf8 verify_apify_free_credits.py --execute --run-cap-usd 0.50
python -B -X utf8 launch_free_pilot.py --batch fr-tiktok-06 --execute
python -B -X utf8 launch_free_pilot.py --batch fr-instagram-01 --execute
```

Ces commandes d'exécution sont documentées, **pas exécutées** pendant la préparation. Le launcher refait lui-même tous les contrôles ; un rapport de budget sauvegardé ne peut pas servir de permission permanente. Le paquet n’installe aucun ordonnanceur ; un éventuel suivi autorisé doit appeler explicitement la CLI et repasser les contrôles à chaque invocation. Sans `--execute`, aucun réseau ni lancement. Sans `APIFY_TOKEN`, `--execute` s'arrête avant tout réseau et toute création d'état.

La commande sans `--batch`, avec `--execute`, sélectionne les deux profils pilotes et les traite séquentiellement. Elle s'arrête si le premier est encore actif, échoue ou ne retourne aucun élément. Plusieurs `--batch` sont possibles ; jamais de parallélisme.

## Contrôles avant chaque nouveau run

1. Vérifier le hash du fichier d'entrée, un seul profil public, les plafonds de résultats, et la désactivation explicite des vidéos, images, commentaires, abonnés, transcriptions et options d'enrichissement.
2. Relire anonymement la fiche de l'Actor : identité publique, permissions, build revu, tarification courante et plafond minimum. Refuser un changement de build, de prix ou de schéma. Valider l'entrée contre le schéma public actuel, sans résolution de références externes.
3. Lire le plan et le budget du compte par trois GET. Exiger `FREE`, plan actif, prix de base zéro, `isPaying=false`, cycle courant cohérent, et **zéro Actor actif**. Les champs manquants ou incohérents bloquent.
4. Limiter l'allocation à la plus petite valeur entre 5 USD, les crédits mensuels du plan et la limite mensuelle du compte. Prendre la plus grande consommation entre les deux vues API. Réserver 0,25 USD supplémentaires et conserver les réservations des runs antérieurs du cycle, même terminés, pour couvrir les retards de facturation.
5. Écrire un reçu durable **avant** l'unique POST. Envoyer `maxTotalChargeUsd=0.50`, `timeout=600`, `restartOnError=false`, et le numéro de build revu. Le chemin POST correspond au contrat OpenAPI : `/v2/acts/{owner}~{actor}/runs`. Aucun retry automatique du POST.

Il n'existe aucune modification de forfait, abonnement, recharge, limite globale de facturation ou paiement dans le code. Un compte payant est refusé, même s'il possède des crédits promotionnels. Les crédits supplémentaires achetés et toute allocation au-delà de 5 USD sont ignorés.

Le verrou local sérialise les commandes de ce paquet ; il ne peut pas empêcher un humain ou un autre outil de démarrer un run ailleurs après la lecture du budget. Le contrôle des runs actifs est donc renouvelé juste avant chaque POST, et le plafond serveur ainsi que le blocage du dépassement du plan Free restent nécessaires. Les API utilisées donnent une estimation prudente des crédits de plan restants, pas un relevé séparant chaque crédit gratuit d'un portefeuille acheté.

Avec 5 USD encore intacts, la réservation conservatrice autorise au plus **neuf plafonds de 0,50 USD dans le cycle**, même si les coûts finaux sont inférieurs. Les 14 lots du plan ne constituent donc pas une autorisation de dépenser 7 USD. Ne pas effacer les reçus pour libérer artificiellement des crédits.

## Suivi, reprise et revue

Les reçus et pages d'export sont créés uniquement en exécution dans `pilot/runtime/`. Ils restent locaux et ne doivent pas être publiés. Un cycle de suivi fait au maximum 12 GET de statut, espacés de 10 secondes ; le run serveur reste plafonné à 600 secondes. `--polls` peut réduire le nombre de lectures.

Pour reprendre un run connu, sans jamais le relancer :

```powershell
python -B -X utf8 launch_free_pilot.py --batch fr-tiktok-06 --execute --resume
```

Une reprise demande exactement un lot. Si le POST est incertain ou si le reçu ne contient pas de run confirmé, tout nouveau démarrage est bloqué. Un opérateur doit consulter Apify Runs et réconcilier le reçu ; ne pas supprimer le reçu ni créer un nouvel identifiant pour contourner ce contrôle. Un verrou persistant après crash doit aussi être inspecté avant suppression manuelle.

Les datasets sont lus par pages de 50, avec un plafond total égal à la cible du lot. Les pages conservent le texte source utile et ses hashtags, IDs, liens de publications, compte auteur public et compteurs ; elles excluent les URLs de fichiers vidéo, commentaires, biographies et objets de profil. Les contacts e-mail et numéros français trouvés dans un texte sont masqués. Le texte source peut donc être signalé comme tronqué ou expurgé, sans être présenté comme une copie intégrale. Chaque page porte provenance, offset, hash et portée `public_post_metadata_for_review`.

Les déclarations de contenu privé, réservé aux abonnés, sponsorisé, photo/carrousel, story ou généré par IA sont conservées pour la revue. Les encodages booléens 0/1 et texte true/false/yes/no sont normalisés strictement ; une valeur inconnue bloque l’export au lieu de devenir une vidéo publique par défaut.

Les miniatures publiquement fournies par l'Actor sont conservées comme **URLs d'images**, sans téléchargement : HTTPS, domaines CDN des plateformes, absence de credentials, exclusion des formats vidéo. Les signatures publiques d'image nécessaires à l'affichage sont conservées et peuvent expirer. Les champs `displayUrl`, `thumbnailUrl`, `thumbnail`, `cover`, `videoMeta.coverUrl` et `videoMeta.cover` sont examinés. Une miniature absente ou expirée doit garder l'état prévu par l'interface, sans inventer une image de la vidéo.

Chaque export terminé produit aussi `manifest.json` au format existant **PUBLIC_EXPORT / generic**, lisible par `scripts/public_export.py` : `url`, légende native dans `caption`, créateur dans `creator`, durée dans `duration_seconds`, miniature dans `thumbnail_url`, hashtags séparés. Le champ `title` n'est renseigné que si le fournisseur fournit un vrai champ titre ; le traitement éditorial existant peut ensuite dériver un titre court de la légende. Les aliases `uploader` et `duration` rendent également les pages compatibles avec `bulk_ingest` pour une revue directe. La reprise vérifie les hashes des pages déjà exportées, leurs offsets et le manifeste ; une page supprimée ou changée bloque la reprise au lieu d'annoncer un succès.

**Aucune page n'est importée en base ni publiée automatiquement.** `exported_count` compte des lignes brutes pour revue, pas des tutoriels validés. Les publications peuvent être supprimées, hors sujet, non francophones ou dupliquées. Aucune transcription ni langue audio n'est acquise, et les licences vidéo restent inconnues. Un run échoué peut avoir des résultats partiels utiles : son statut est conservé et la séquence s'arrête.

## Plan de profils et extension

| Lot | Source publique à qualifier | Cible brute maximale | Étape |
| --- | --- | ---: | --- |
| fr-tiktok-06 | TikTok `maclede12` | 60 | Pilote |
| fr-instagram-01 | Instagram `norautofr` | 100 | Pilote |
| fr-tiktok-01 | TikTok `opermis7` | 60 | Extension |
| fr-tiktok-02 | TikTok `wurthfrance` | 60 | Extension |
| fr-tiktok-03 | TikTok `lemoniteurlyonnais` | 60 | Extension |
| fr-tiktok-04 | TikTok `diagnosticauto` | 60 | Extension |
| fr-tiktok-05 | TikTok `code.simplifie` | 60 | Extension |
| fr-tiktok-07 | TikTok `vsm.cfa` | 60 | Extension |
| fr-tiktok-08 | TikTok `garage.amt42` | 60 | Extension |
| fr-tiktok-09 | TikTok `astucesautomobiles` | 60 | Extension |
| fr-tiktok-10 | TikTok `reparationsfaciles` | 60 | Extension |
| fr-instagram-02 | Instagram `glb_evan` | 100 | Extension |
| fr-instagram-03 | Instagram `autodoc` | 100 | Extension |
| fr-instagram-04 | Instagram `atelier_mecanique_tlemcen` | 100 | Extension |

Les graines viennent du plan antérieur et de ses URLs de preuve ; elles ne prouvent ni une disponibilité actuelle ni une langue française. La portée des 14 lots est **1 000 publications brutes au maximum**, pas 1 000 tutoriels français nouveaux. Le pilote initial en vise au plus 160.

Après la revue des pilotes, une extension doit être explicitement sélectionnée :

```powershell
python -B -X utf8 launch_free_pilot.py --batch fr-tiktok-04 --extend-after-review
python -B -X utf8 launch_free_pilot.py --batch fr-tiktok-04 --extend-after-review --execute
```

Qualification recommandée : dédupliquer par plateforme et ID, séparer titre éditorial court / description / hashtags, reconnaître la langue depuis la légende en indiquant `inferred_from_source_caption_text`, classer le sujet automobile attesté, puis extraire marque, modèle et moteur uniquement lorsqu'ils figurent dans la publication. Ne jamais inférer une procédure exacte, une motorisation ou une homologation depuis le nom du créateur. Mettre à part la promotion, le divertissement et les fiches sans geste ou explication utiles. Mesurer par profil le nombre nouveau, le taux de tutoriels automobiles, la part FR et le coût par élément accepté avant d'élargir.

## Prix et limites vérifiés

| Actor | Build revu | Événement Free | Démarrage | Minimum du plafond de run |
| --- | --- | ---: | ---: | ---: |
| `clockworks/tiktok-scraper` | 0.0.620 | 0,0037 USD / résultat | 0,001 USD | **0,50 USD** |
| `apify/instagram-reel-scraper` | 0.0.618 | 0,0026 USD / reel | 0,001 USD | 0,0073 USD |

Le précédent plafond TikTok de 0,30 USD n'est plus accepté par la tarification publique actuelle. Les deux lots V25 utilisent 0,50 USD maximum. Les fiches de prix indiquent les frais plateforme inclus pour ces Actors ; le plafond `maxTotalChargeUsd` couvre tous les modèles selon la documentation actuelle. L'estimation de base des 1 000 cibles est 3,274 USD, mais ce n'est ni un devis ni la somme autorisée par la garde de réservations.

`maxItems` n'est pas employé comme garde financière : ce paramètre concerne la facturation par résultat, alors que ces deux Actors sont facturés par événement. Les entrées `resultsPerPage` et `resultsLimit` portent sur chaque profil.

Alternative vérifiée et rejetée pour la grande échelle gratuite : API Dojo `tiktok-profile-scraper` affiche 0,30 USD / 1 000 et un calcul de 16 666 posts Free sur sa page prix, mais **son README limite les comptes gratuits à cinq runs par mois de dix éléments**, soit au plus 50 éléments de démonstration. `data-slayer/instagram-posts` affiche 0,0025 USD par résultat et 0,002 USD au démarrage, un faible gain contre un schéma beaucoup plus large ; aucun run de cet acteur n'a été testé.

Une API gratuite ou un dépôt GitHub ne supprime pas les quotas des services. Les recherches V24 ont déjà invalidé la route de datasets massifs comme remplacement commercial fiable : licences non commerciales / recherche seulement, duplication extrême, très faible rendement automobile FR. Voir `work/free-v24/dataset-research/README.md` dans le projet source.

## MCP et sources primaires

Le MCP officiel peut utiliser OAuth à `https://mcp.apify.com`. Aucun MCP Apify n'est connecté dans ce paquet. Les quatre outils de découverte `search-actors`, `fetch-actor-details`, `search-apify-docs`, `fetch-apify-docs` sont accessibles sans compte via la configuration de découverte décrite dans la documentation. `call-actor` exige une authentification ; ses bornes passent dans `callOptions`, pas dans l'entrée du scraper. Ne pas déléguer la vérification du plan à un Actor générique : `/users/me` omet les informations de plan depuis un contexte Actor.

- [Tarifs Apify et comportement du plan Free](https://apify.com/pricing)
- [Facturation du compte](https://docs.apify.com/account/billing)
- [Compte et plan — GET users/me](https://docs.apify.com/api/v2/users-me-get) — la réponse contient aussi des données sensibles, notamment un mot de passe proxy ; le vérificateur les élimine avant tout retour, affichage ou écriture.
- [Limites et consommation courante](https://docs.apify.com/api/v2/users-me-limits-get)
- [Consommation mensuelle](https://docs.apify.com/api/v2/users-me-usage-monthly-get)
- [Paramètres du lancement et plafond total](https://docs.apify.com/api/v2/actors-runs-post)
- [Lecture du statut d'un run](https://docs.apify.com/api/v2/actor-run-get)
- [Pagination et sélection de champs de dataset](https://docs.apify.com/api/v2/dataset-items-get)
- [Schéma OpenAPI public d'un build](https://docs.apify.com/api/v2/actor-openapi-json-get)
- [Tarification Clockworks TikTok](https://apify.com/clockworks/tiktok-scraper/pricing)
- [Tarification Apify Instagram Reels](https://apify.com/apify/instagram-reel-scraper/pricing)
- [Fiche publique TikTok API](https://api.apify.com/v2/acts/clockworks~tiktok-scraper)
- [Fiche publique Instagram API](https://api.apify.com/v2/acts/apify~instagram-reel-scraper)
- [Contrat TikTok OpenAPI public](https://api.apify.com/v2/actors/clockworks~tiktok-scraper/builds/default/openapi.json)
- [Contrat Instagram OpenAPI public](https://api.apify.com/v2/actors/apify~instagram-reel-scraper/builds/default/openapi.json)
- [MCP officiel](https://docs.apify.com/mcp)
- [API Dojo : conditions de démonstration](https://apify.com/apidojo/tiktok-profile-scraper)
- [API Dojo : prix affichés](https://apify.com/apidojo/tiktok-profile-scraper/pricing)
- [Data Slayer : prix](https://apify.com/data-slayer/instagram-posts/pricing)

## Vérification locale et distribution

```powershell
python -B -X utf8 -m unittest discover -s . -p 'test_*.py' -v
```

44 tests hors ligne couvrent notamment la projection des secrets, compte payant, budget insuffisant, run concurrent, schéma/prix/build modifiés, hash changé, seul POST autorisé, reçu avant POST, issue inconnue, reprise GET seule, pagination reprise, pages manquantes ou modifiées, compatibilité du manifeste, miniatures publiques, arrêt sur échec ou résultat vide, verrou local et réservations persistantes. Les 14 entrées sont également validées contre les schémas publics sauvegardés.

Deux revues indépendantes ont également validé 22 contrôles de compatibilité complète des exports et 38 cas de restrictions via le véritable adaptateur PUBLIC_EXPORT. Le rapport de la seconde est fourni dans `independent-review.json` ; son script de reproduction dépend de l’application et reste dans `work/scale-v25/research/provider-independent-review-checks.py`, hors du paquet autonome.

Le manifeste `artifact-sha256.json` permet de contrôler les fichiers distribués. Les fiches sauvegardées sont des projections de réponses anonymes publiques, sans `deploymentKey` ni données inutiles. Ne distribuer ni `pilot/runtime/`, ni jeton, ni fichier `.env`. Le paquet doit être copié entier pour conserver les chemins relatifs de ses fixtures et entrées.
