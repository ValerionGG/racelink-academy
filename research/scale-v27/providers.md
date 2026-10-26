# Collecte sociale V27 — fournisseurs réellement exploitables

Vérification du 26 octobre 2026. Recherche avec Agent Reach (Exa et GitHub CLI), documentation primaire et schémas publics. Aucun compte créé, appel authentifié, installation, cookie ou lancement de collecte dans cette sous-tâche. Les volumes ci-dessous sont des capacités brutes annoncées, pas des tutoriels acquis.

## Décision

**Bright Data est le meilleur prochain essai : 5 000 références brutes par mois dans un compte ordinaire gratuit, sans carte.** Ce n'est plus uniquement une offre de proxy ou un MCP de lecture de pages : les scrapers sociaux de profils et de découverte sont couverts. Le contrôle du compte réel reste à faire avant toute collecte. [Offre sociale](https://brightdata.com/products/web-scraper/social-media-scrape), [conditions du quota](https://docs.brightdata.com/general/account/billing-and-pricing/free-tier).

| Fournisseur | Allocation gratuite vérifiée | Rendement pertinent | Décision |
| --- | --- | --- | --- |
| Bright Data | 5 000 crédits/mois, sans carte ; pool partagé avec SERP, Unlocker, MCP, Studio, Browser | Web Scraper : un crédit par référence livrée ; TikTok profils/recherche, Instagram reels par profil | Priorité 1 : lots plafonnés, compte non approvisionné |
| EnsembleData | 50 unités/jour pendant **7 jours**, sans carte | TikTok recherche : jusqu'à 20 résultats/unité ; Instagram : une unité/reel | Priorité 2 : découverte TikTok, 45 pages/jour maximum proposées |
| ScrapeCreators | 100 crédits initiaux, sans carte ; bonus conditionnels distincts | TikTok et Instagram posts : un crédit/page, plusieurs publications possibles | Priorité 3 : profils déjà qualifiés ; mesurer le nombre réel par page |
| SociaVault | 50 crédits initiaux, sans carte, sans expiration annoncée | Routes de listes TikTok/Instagram ; quantité réelle par page non garantie | Secours, pas une base de collecte permanente |
| Apify actuel | Allocation déjà consommée et neuf réservations du cycle V26 | 981 publications exportées, 300 ajouts publiés | Ne pas recréer des comptes ou des jobs pour réutiliser le même essai |

Sources : [EnsembleData tarifs](https://ensembledata.com/pricing), [durée exacte de l'essai TikTok](https://ensembledata.com/tiktok-api), [ScrapeCreators](https://scrapecreators.com/), [SociaVault](https://sociavault.com/pricing). Le rendement pédagogique et la part française restent à mesurer pour chaque profil. Aucun de ces fournisseurs ne démontre à lui seul 100 000 tutoriels gratuits et francophones.

## Flux Bright Data concret

Le quota est renouvelé le premier du mois, sans report. Sans fonds déposés, l'épuisement provoque un arrêt ; avec des fonds, la facturation peut continuer. Ne déposer aucun fonds, ne pas activer auto-recharge et constater le solde du quota dans Billing Overview. MCP et API ne donnent pas deux enveloppes séparées. [Documentation du compte gratuit](https://docs.brightdata.com/general/account/billing-and-pricing/free-tier).

Les schémas JSON publics ont été téléchargés et conservés dans `provider-docs/`. Identifiants vérifiés, non devinés :

| Objet | dataset_id | Méthode de découverte | Entrées utiles |
| --- | --- | --- | --- |
| TikTok Posts | `gd_lu702nij2f790tmv9h` | `discover_by_profile_url` | `url`, `num_of_posts`, `posts_to_not_include`, `start_date`, `end_date`, `post_type`, `country`, `include_pinned_post`, `sort_by` |
| TikTok Posts | identique | `discover_by_keyword` | `search_keyword`, `num_of_posts`, `posts_to_not_include`, `country` |
| Instagram Reels | `gd_lyclm20il4r5helnj` | `discover_by_url` | `url`, `num_of_posts`, `posts_to_not_include`, `start_date`, `end_date`, `all_reels`, `country_code` |

[Schémas TikTok](https://docs.brightdata.com/scrapers/tiktok.com.json), [schémas Instagram](https://docs.brightdata.com/scrapers/instagram.com.json).

Séquence API à construire/tester :

1. Enregistrer un job et sa réservation locale avant le lancement ; clé fournie explicitement via variable d'environnement, jamais cherchée dans un navigateur ou un dépôt.
2. `POST https://api.brightdata.com/datasets/v3/trigger` avec `dataset_id`, `type=discover_new`, le `discover_by` correspondant, `limit_per_input`, `limit_multiple_results`, `include_errors=true`. Pour les noms des modes, suivre l'exemple généré par la Console pour le scraper sélectionné ; ne pas inventer des valeurs à partir du libellé humain.
3. Corps JSON avec `input` et bornes par profil. Pilote conseillé : deux profils, 50 résultats chacun, limite totale 100. Réserver ces 100 crédits même si le rendement est moindre, jusqu'au rapprochement du compte.
4. Persister le `snapshot_id` retourné. Si le POST est incertain, retrouver le job existant ; ne pas soumettre de nouveau.
5. `GET /datasets/v3/progress/{snapshot_id}` jusqu'à `ready`, puis `GET /datasets/v3/snapshot/{snapshot_id}?format=json`. Reprise de ces GET seulement, pas répétition du POST. Sur 429, ralentir/arrêter selon `Retry-After`.
6. Filtrer les champs utiles via `custom_output_fields` puis projection locale ; garder les indicateurs de type/confidentialité/promotion disponibles. Ne pas publier biographie, contacts, commentaires ou URL vidéo brute.

[Contrat async et paramètres de limites](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests), [suivi et téléchargement](https://docs.brightdata.com/products/scrapers/scrapers-library/async-requests). Le plafond total limite les résultats ; la sûreté financière dépend aussi du compte gratuit non approvisionné. Ce flux est documenté, pas encore lancé par cette recherche.

Proposition de campagne après pilote : 30 profils éducatifs × 100 publications + 80 recherches ciblées × 20 = 4 600 références maximum, 400 crédits de marge commune. Tester d'abord le rendement ; arrêter un profil s'il produit surtout des légendes vides. Réserver une part majoritaire à Instagram, car EnsembleData est plus économique pour découvrir TikTok.

## EnsembleData : différence importante entre tarif résumé et vrai endpoint

Le schéma [OpenAPI actuel](https://ensembledata.com/apis/openapi.json) précise :

- `/tt/keyword/search` : une unité, jusqu'à 20 posts ; paramètres `name`, `cursor`, `country=FR`, `sorting`, `period`, `match_exactly=false`, `get_author_stats=false`. Reprendre `nextCursor`, sans supposer qu'il est un numéro de page.
- `/tt/user/posts` par username : **1 + depth** unités pour jusqu'à 10 × depth posts. La page marketing simplifie ce coût. La variante `/tt/user/posts-from-secuid` coûte depth unités si l'identifiant public est déjà connu.
- `/instagram/user/reels` : coût égal au nombre de reels ; rendement gratuit faible.
- `/customer/get-used-units` : lecture de consommation sans coût, avec une date. Le token est un paramètre de l'API : les logs doivent systématiquement expurger les URLs authentifiées.

45 recherches/jour × 20 × 7 donnent un plafond de travail de **6 300 résultats bruts** et 5 unités/jour de marge. Ce calcul n'est ni une disponibilité garantie ni une estimation de nouvelles fiches. La fin de l'essai doit être inscrite dans l'ordonnanceur ; aucun abonnement après l'essai.

## ScrapeCreators : bon coût par page, skill partiellement périmé

Skill officiel trouvé : [ScrapeCreators/social-media-research-skills](https://github.com/ScrapeCreators/social-media-research-skills), fichier [scrapecreators-api/SKILL.md](https://github.com/ScrapeCreators/social-media-research-skills/blob/main/skills/scrapecreators-api/SKILL.md). Lu comme documentation, non installé.

Utiliser `/v3/tiktok/profile/videos` avec `handle`, `region=FR`, `max_cursor` et arrêt sur `has_more=false` ; une page réussie coûte un crédit, même vide. La taille n'est pas garantie, et une pagination complète peut omettre des posts. [Contrat TikTok](https://docs.scrapecreators.com/v3/tiktok/profile/videos/).

Pour Instagram, privilégier `/v2/instagram/user/posts` et `next_max_id` : les légendes sont nécessaires au classement. `/v1/instagram/user/reels` **n'inclut pas les légendes**, ce qui obligerait à multiplier les appels de détail. [Posts](https://docs.scrapecreators.com/v2/instagram/user/posts/), [reels](https://docs.scrapecreators.com/v1/instagram/user/reels/).

Le skill cite encore `/v1/credit/balance` ; la spécification actuelle donne `/v1/account/credit-balance`. Toujours suivre le schéma, conserver `credits_charged`, `credits_remaining`, le curseur et un hash de page. [OpenAPI](https://docs.scrapecreators.com/openapi.json).

Les bonus allant jusqu'à 7 000 crédits exigent notamment réponses marketing, étoile GitHub ou avis G2. Ils ne font pas partie des 100 crédits garantis. Ne pas publier un avis ou une recommandation au nom de l'utilisateur pour les obtenir. Garder auto-recharge désactivé. [Offre](https://scrapecreators.com/), [conditions](https://scrapecreators.com/terms).

## SociaVault et code ouvert : utilité et limites réelles

SociaVault expose `/v1/scrape/tiktok/videos` et `/v1/scrape/instagram/reels`, clé `X-API-Key`, pagination. Ses 50 crédits servent à un contrôle de secours ; ils ne sont pas renouvelés mensuellement dans l'offre publiée. [TikTok](https://docs.sociavault.com/api-reference/tiktok/videos), [Instagram](https://docs.sociavault.com/api-reference/instagram/reels), [tarifs](https://sociavault.com/pricing).

Les conditions consultées ne fournissent pas d'autorisation de multiplier les essais d'une même personne. La recherche ne propose donc pas de duplication de comptes, d'alias temporaires ou de rotation d'identités. Un compte légitime par fournisseur distinct suffit à tester ces alternatives.

| Dépôt GitHub | Constat du 26 octobre 2026 | Utilité réelle |
| --- | --- | --- |
| [davidteather/TikTok-Api](https://github.com/davidteather/TikTok-Api) | 6 716 étoiles ; dernier push 24 août 2026 | Modèles de données utiles ; nécessite navigateur/session msToken, erreurs de réponse vide encore signalées. N'apporte aucun quota gratuit géré |
| [instaloader/instaloader](https://github.com/instaloader/instaloader) | 13 688 étoiles ; push ce jour | Outil entretenu ; accès et limites Instagram restent présents, ne remplace pas une source stable garantie |
| [drawrowfly/tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper) | 5 232 étoiles mais dernier push 19 mai 2023 | Nombre d'étoiles trompeur pour la maintenabilité ; pas retenu |

Agent Reach local : v1.5.0 ; doctor détecte OpenCLI sans extension connectée pour Instagram/Facebook. Le test Exa a réellement réussi. L'annonce v1.6.0 indique aussi Instagram non validé sur la machine de publication à cause du rate limit : une mise à jour n'est pas une promesse de collecte massive. Aucune mise à jour lancée. [Mise à jour officielle](https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md).

## Intégration éditoriale

Les fournisseurs alimentent une même file de candidats : dédoublonnage plateforme/ID contre le catalogue et les exclusions V26, revue de chaque légende, titres séparés des hashtags, voiture/moteur uniquement si explicitement cités, statut langue estimée depuis le texte et licence inconnue. Un résultat de recherche n'est pas une procédure vérifiée. Le nouveau moteur utile est cette chaîne commune avec curseurs, reprise, budgets et rendements par créateur, pas une multiplication de scrapers non suivis.
