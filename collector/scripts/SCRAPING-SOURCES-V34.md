# Outils de collecte examinés — 28 octobre 2026

La recherche distingue une bibliothèque logicielle, un accès opérationnel à une plateforme et un quota réellement disponible. Installer davantage de scrapers ne garantit pas un accès à TikTok ou Instagram.

| Voie | Usage concret | État vérifié dans cette session | Coût / limite |
|---|---|---|---|
| PeerTube + SepiaSearch | Recherche publique, suivi de chaînes pédagogiques ; titres, descriptions, langue et licence déclarées | **Collecteur livré**, 8 appels, 95 lignes, 1 nouvelle référence retenue après revue et déduplication | Aucun compte, paiement ou quota acheté ; cadence bornée et arrêt sur limitation |
| Firecrawl | Extraire le texte structuré de pages publiques pour enrichir les informations et sources | **Un essai anonyme réussi**, HTTP 200, `success:true`, 1 580 caractères sur une page de documentation publique, `creditsUsed=1` | Aucun compte connecté/solde observé. Démonstration sans clé documentée ; aucun lot lancé |
| Scrapy | Grandes files de pages publiques, déduplication persistante, reprise et adaptation du débit | Documentation examinée ; non installé et non exécuté dans cette livraison | Logiciel libre local ; coûts éventuels d’hébergement distincts ; aucun accès social fourni |
| Crawlee | Files persistantes HTTP, parsing HTML/JSON, stockage local | Documentation examinée ; non installé et non exécuté | Bibliothèque libre ; cloud Apify distinct. Aucun nouveau crédit Apify acquis ni protection contournée |
| gallery-dl | Métadonnées de publications via `--dump-json` / `--simulate` | Documentation examinée ; non exécuté sur les réseaux sociaux | Logiciel libre. Instagram et TikTok sont documentés avec cookies ; ce n’est pas une solution anonyme prouvée ici |
| Wikimedia Commons API | Illustrations et médias techniques avec descriptions, attribution et licences par fichier | Documentation examinée ; non exécutée dans ce pilote | API publique ; droits à vérifier par fichier. Ne remplace pas un catalogue de tutos automobiles |

Le [collecteur PeerTube](PEERTUBE-COLLECTOR.md) est la nouvelle intégration réellement livrée. Les réponses brutes et journaux de collecte restent privés. Les prochaines vagues doivent éviter les mêmes chaînes déjà terminées et vérifier les anciennes identités avant import.

## Accès sociaux

Le diagnostic Agent Reach a observé `yt-dlp` actif pour YouTube. Pour Facebook et Instagram, OpenCLI est installé mais aucune extension de navigateur connectée n’a été détectée ; leur `active_backend` reste nul. Aucun cookie ni secret n’a été lu. La route Bilibili Search API est signalée accessible par le diagnostic, sans collecte supplémentaire effectuée dans cette livraison. [Agent Reach](https://github.com/Panniantong/agent-reach)

La documentation TikTok Research API exige un projet approuvé et des identifiants. Sa FAQ exclut les créateurs, annonceurs et utilisateurs commerciaux de ce programme : il ne faut donc pas présenter ce programme comme un accès de collecte libre acquis pour RaceLink. La documentation Meta Content Library a renvoyé une page demandant une connexion ; aucune capacité n’a été confirmée. [Démarrage TikTok](https://developers.tiktok.com/docs/en/research-api-get-started), [FAQ TikTok](https://developers.tiktok.com/docs/en/research-api-faq), [Meta Content Library](https://developers.facebook.com/docs/content-library-and-api/)

## Références et réserves sur Firecrawl

Les docs actuelles annoncent une première requête `/v2/scrape` sans clé. L’essai n’a transmis qu’une URL de documentation publique déjà consultée : `https://docs.joinpeertube.org/use/search`, avec `formats=["markdown"]`. Il n’a créé ni compte, ni abonnement, ni connexion à un réseau social et n’a référencé aucune vidéo. Le plugin Firecrawl a été trouvé mais n’est pas installé.

La page de tarifs affiche 1 000 crédits mensuels gratuits, sans carte. **Cette annonce n’est pas un solde obtenu.** Les coûts varient par format : 1 crédit pour une page simple, 4 supplémentaires pour certains formats structurés. Aucun budget payant ou recharge n’est autorisé. Avant une campagne authentifiée, observer son solde et ses limites, réserver chaque lot et conserver tout appel incertain ; l’essai anonyme n’autorise pas de supposer une capacité de collecte massive. [Documentation Firecrawl](https://docs.firecrawl.dev/introduction), [tarifs Firecrawl](https://www.firecrawl.dev/pricing)

## Références des autres outils

- **Scrapy** : persistance `JOBDIR`, filtre de doublons et état de reprise ; AutoThrottle ajuste le débit sans accélérer sur les erreurs. Ces fonctions aident à gérer les pages accessibles, elles ne fournissent pas de données sociales à elles seules. [Reprise](https://docs.scrapy.org/en/latest/topics/jobs.html), [AutoThrottle](https://docs.scrapy.org/en/latest/topics/autothrottle.html)
- **Crawlee** : files persistantes, HTTP, stockage, gestion d’erreurs. Les fonctions de proxy/empreintes/navigateur de la bibliothèque ne sont pas employées ici. [Documentation officielle](https://crawlee.dev/js/docs/introduction), [dépôt](https://github.com/apify/crawlee)
- **gallery-dl** : la documentation expose `--dump-json`, `--simulate`, bornes de résultats et temporisations. La maintenance a déménagé vers Codeberg ; les anciennes étoiles GitHub ne suffisent pas à juger la viabilité d’un extracteur. [Options](https://gdl-org.github.io/docs/options.html), [sites et authentification](https://gdl-org.github.io/docs/supportedsites.html), [annonce dans le dépôt](https://github.com/mikf/gallery-dl)
- **Wikimedia** : recherche et métadonnées étendues des fichiers (`imageinfo/extmetadata`) pour attribution et illustration ; aucune langue audio ou recommandation constructeur n’en découle. [Recherche MediaWiki](https://www.mediawiki.org/wiki/API:Search), [métadonnées Commons](https://commons.wikimedia.org/wiki/Commons:API/MediaWiki)

Les nombres de vidéos reçues, retenues, importées et réellement publiées doivent toujours être rapportés séparément. Cette documentation décrit l’état du pilote, pas le résultat d’une publication ultérieure.
