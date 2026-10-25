# Voies gratuites utiles — vérification du 25 octobre 2026

La voie immédiatement exploitable est le collecteur Exa déjà installé, avec une qualification des **titres sources** français et des liens de créateurs. La recherche GitHub n’a pas établi de nouvelle bibliothèque capable de fournir massivement Instagram/TikTok/Facebook de façon fiable, anonyme, sans navigateur ni contournement. Aucun paquet installé, compte connecté, média téléchargé ou catalogue modifié pendant cet audit.

## Correction réellement livrée

Le [serveur Exa officiel](https://github.com/exa-labs/exa-mcp-server/blob/main/src/tools/webSearchAdvanced.ts) sérialise les résultats dans `content[].text`. Son [helper de notices](https://github.com/exa-labs/exa-mcp-server/blob/main/src/tools/searchNotes.ts) désactive actuellement `structuredContent` par défaut. `local_collect.exa_entries()` attendait uniquement les objets structurés ou l’ancien texte `Title: / URL:` : une réponse moderne valide pouvait donc sembler vide.

`scripts/local_collect.py` **1.0.1** accepte désormais ce JSON textuel, conserve les formats antérieurs, ignore les JSON malformés et évite les doublons lorsque les mêmes données apparaissent sous plusieurs formats. Les limites, l’arrêt sur blocage et le statut de métadonnées indexées sont conservés. La version renouvelle les clés de cache ; ne pas effacer ni réécrire les anciennes preuves. Prendre un nouveau dossier de sortie.

Validation : **28 tests sur 28**, dont quatre nouveaux tests ciblés, intégralement hors réseau. Commande depuis `outputs/focus-academy` : `python -B -m unittest scripts.test_local_collect -v`. Empreintes et portée dans [parser-validation.json](parser-validation.json).

## Précision française : réglages utiles, sans nouvelle promesse

L’API officielle définit `includeText` comme une conjonction : **toutes** les chaînes doivent apparaître dans le résultat. Ce n’est pas un filtre de titre ni une preuve de langue audio. `userLocation: FR` cible une géographie. Source exacte et empreinte GitHub conservées dans [github-findings.json](github-findings.json).

- Faire une requête par intervention et par plateforme, avec un seul terme français distinctif (`vidange`, `essuie-glaces`, `plaquettes`, `fusible`, `embrayage`, `CarPlay`) ; mettre les formulations pédagogiques dans la requête. Éviter `includeText: ["tutoriel", "vidange", "Clio"]` pour une recherche générale : cela exige les trois termes.
- Après collecte, exiger le sujet dans le titre nettoyé réel, ou dans une légende directe déjà vérifiée. Un corps indexé contenant des recommandations ne qualifie jamais le média cible. Conserver le titre source original et la provenance avant toute correction éditoriale.
- Mettre en revue les titres génériques et les mentions qui ne figurent que dans les hashtags ; exclure annonces, incidents isolés, clips de spectacle et résultats sans geste expliqué. Les notices Exa peuvent signaler une restriction relâchée : les arguments envoyés ne constituent donc jamais une preuve que chaque résultat respecte le filtre.
- Le plan racine `work/free-v24/social-plan.json` est prêt pour des probes bornées. Limites actuelles du collecteur : 50 résultats demandés/requête avancée, 200 jobs/plan, 10 000 résultats demandés/plan. Le quota gratuit réel peut interrompre la collecte bien avant ; aucun volume utile garanti.

## GitHub : options examinées

| Source primaire | Constat actuel | Décision pour ce tour |
|---|---|---|
| [TikTok-Api](https://github.com/davidteather/TikTok-Api) | Bibliothèque non officielle ; quickstart Playwright et `ms_token`, documentation des réponses vides liées au blocage. | Incompatible avec le périmètre sans navigateur/cookies. Aucun essai natif. |
| [tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper) | Slogan sans login, mais exemples de flux demandant une session ; signatures/proxies proposés dans le README. | Ne pas traiter le slogan comme une preuve de disponibilité anonyme. |
| [Instaloader](https://github.com/instaloader/instaloader) | Export de métadonnées et reprise possibles, mais [limitations 401/429 signalées](https://github.com/instaloader/instaloader/issues/2786). | Pas une solution vérifiée aux restrictions déjà rencontrées. |
| [facebook-scraper](https://github.com/kevinzg/facebook-scraper) | Annonce des pages publiques sans clé ; dernier push observé le 22 juin 2024, recours possible aux cookies documenté. | Pas de garantie actuelle de collecte massive anonyme ; pas installé. |
| [ProxiTok](https://github.com/pablouser1/ProxiTok) | Frontend tiers, flux RSS de comptes/tags, requêtes TikTok effectuées côté serveur. | Pas retenu comme détour aux restrictions natives ; disponibilité des instances non testée. |
| [Bright Data Instagram Scraper](https://github.com/brightdata/instagram-scraper) | Dépôt fournisseur récent ; requiert une connexion ou clé fournisseur, même sans login Instagram. | Option gratuite conditionnelle, pas disponible anonymement ici. |

La [documentation Bright Data](https://docs.brightdata.com/general/account/billing-and-pricing/free-tier) annonce 5 000 crédits mensuels pour les nouveaux comptes, sans carte ; les appels s’arrêtent à épuisement si aucun fonds n’est déposé. Avec un solde payé, la consommation continue sur ce solde. Cela nécessite donc un compte et un contrôle effectif du crédit, sans dépôt ni recharge. Le README demande `auto_create_zones=False`. Aucun appel fournisseur exécuté ; ne pas présenter ces crédits comme déjà disponibles ni comme 5 000 tutoriels qualifiés.

## APIs et exports : frontières exactes

La [doc TikTok Embed Videos, actualisée le 22 octobre](https://developers.tiktok.com/docs/en/embed-videos) annonce une dépréciation prochaine au profit d’Embed Player. Son exemple oEmbed actuel expose un player et un identifiant, pas le titre, l’auteur ou la miniature. Ce n’est donc pas une nouvelle API garantie de légendes ni un moteur de découverte. Aucune requête native TikTok effectuée.

[Vimeo oEmbed](https://help.vimeo.com/hc/en-us/articles/12427681730577-Overview-Developer-Tools) documente toujours nom, description, miniature et embed d’une vidéo connue. C’est une voie d’enrichissement par URL publique, pas une recherche paginée. La lecture de la documentation Meta oEmbed a été refusée/limitée ; aucune disponibilité anonyme Meta n’est revendiquée.

**Correction de périmètre local :** `public_export.py` n’accepte actuellement que les identités Instagram et TikTok, avec schémas `generic`, `meta_graph`, `tiktok_display`. `bulk_ingest.identity()` ne connaît que YouTube/Instagram/TikTok. Facebook et Vimeo sont acceptés par le modèle du serveur, mais pas par ces adaptateurs. Un export créateur Facebook/Vimeo demanderait un adaptateur explicite vers les fiches normalisées, avec sa preuve et sa revue, sans le maquiller en export Apify.

Le collecteur existant `creator_site_collect.py` peut exploiter des pages éditeur explicites, sans accéder à Instagram/TikTok. Les liens et leur contexte restent des preuves éditoriales du site, jamais des légendes natives. C’est utilisable dès maintenant sur les pages déjà archivées ; les exports IG/TT fournis par un créateur restent importables via `PUBLIC_EXPORT` après revue.

Agent Reach installé : 1.5.0 ; `check-update` annonce 1.6.0. Mise à jour non effectuée. Elle ne résout pas à elle seule les limites Instagram : les notes amont indiquent que cette plateforme n’a pas été validée lors de la sortie pour cause de limitation.
