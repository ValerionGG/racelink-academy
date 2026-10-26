# Campagnes de profils, pagination et preuves V27

Le module `profile_campaign.py` complète les collecteurs existants. Il ne collecte pas lui-même : aucun accès réseau, navigateur, secret ou base de données. Il réserve les requêtes gratuites, mémorise les curseurs des réponses réellement obtenues et produit une quarantaine commune aux fournisseurs. Les 100 000 lignes constituent une borne locale, **pas un volume acquis ou promis**.

Le client séparé `scrapecreators_collect.py` peut ensuite exécuter la campagne avec une clé fournie explicitement. Son mode par défaut est un aperçu sans réseau. L'exécution réseau de ce client n'a pas été testée sur un compte réel ; les tests utilisent un transport factice.

## Ce qui existait et ce qui manque

- `social_queue.py` organise les requêtes Exa, sans curseur de pagination natif des profils. Le réutiliser ne révèle pas les anciennes publications d'un créateur.
- `bulk_ingest.py` et `public_export.py` savent préparer, dédoublonner et appliquer un paquet approuvé. Ils ne conduisent pas les campagnes par profil. Leur mécanisme d'approbation reste celui de l'application.
- Le lanceur Apify V25 sait paginer un dataset obtenu, sous ses propres plafonds. Il ne transforme pas les pages d'un dataset en nouvelles pages d'un profil.
- `browser_social_capture.py` préserve les observations de l'interface. Les alt de grille ne sont pas des légendes.
- V27 apporte un registre de pages par profil, des réservations avant requête et une réconciliation entre fournisseurs qui garde toutes les variantes. Il réutilise `social_metadata.py` et les schémas PUBLIC_EXPORT, au lieu d'inventer un second nettoyage ou une seconde procédure d'import.

## Contrats réellement consultés

Documentation primaire consultée le 26 octobre 2026 :

- [TikTok Profile Videos](https://docs.scrapecreators.com/v3/tiktok/profile/videos/) : `GET /v3/tiktok/profile/videos`, tableau `aweme_list`, pagination `has_more` / `max_cursor`. Conserver région, tri et option pinned pendant la pagination. Une page réussie peut être vide et reste facturable 1 crédit ; une pagination terminée ne garantit pas l'exhaustivité de TikTok.
- [Instagram Posts](https://docs.scrapecreators.com/v2/instagram/user/posts/) : `GET /v2/instagram/user/posts`, tableau `items`, `more_available` / `next_max_id`. La légende est `caption.text`, un média vidéo est déclaré avec `media_type = 2`. Les messages d'accès doivent être lus même avec HTTP 200.
- [Offre Instagram](https://scrapecreators.com/instagram-api) : 100 crédits d'essai annoncés sans carte. L'annonce ne prouve pas le solde d'un compte. L'endpoint reels exclut les légendes ; utiliser posts pour cette collecte.
- [Skills officiels ScrapeCreators](https://github.com/ScrapeCreators/social-media-research-skills) : référence de workflow, pas installation ni autorisation d'achat.

La tâche principale doit constater le solde courant, l'absence de recharge automatique et le caractère gratuit des crédits. L'endpoint de solde actuel identifié dans la recherche du parent est `/v1/account/credit-balance` ; ce module ne l'appelle pas et ne contient pas l'ancien `/v1/credit/balance`.

## Démarrage après vérification effective du compte

Préparer un fichier privé `plan.json` avec exactement ce schéma. Remplacer l'heure et le nombre de crédits par les valeurs réellement vérifiées ; l'exemple est volontairement périmé et n'est pas exécutable tel quel.

```json
{
  "version": 1,
  "free_credits": 100,
  "checked_at": "2000-01-01T00:00:00Z",
  "auto_recharge": false,
  "out_of_pocket_usd": 0,
  "profiles": [
    {"platform": "tiktok", "handle": "maclede12", "max_pages": 5, "region": "FR"},
    {"platform": "instagram", "handle": "norautofr", "max_pages": 5, "region": "FR"}
  ]
}
```

Depuis ce dossier (`focus-academy` dans le ZIP, `collector` dans GitHub) :

```powershell
python -B -X utf8 scripts/profile_campaign.py init collection/runtime/profile-v27/campaign --plan collection/runtime/profile-v27/plan.json --app .
python -B -X utf8 scripts/profile_campaign.py reserve collection/runtime/profile-v27/campaign --job tiktok:maclede12
```

La réservation est persistée **avant** la requête externe. La sortie fournit un numéro `attempt`, l'endpoint et les paramètres exacts ; aucun en-tête d'authentification n'est produit. L'opérateur fait au maximum une requête avec ce plan, conserve sa réponse JSON native en privé, puis :

```powershell
python -B -X utf8 scripts/profile_campaign.py ingest collection/runtime/profile-v27/campaign --attempt 0 --response collection/runtime/profile-v27/raw/response-0.json
python -B -X utf8 scripts/profile_campaign.py status collection/runtime/profile-v27/campaign
```

Une réponse rejouée avec les mêmes octets ne recompte rien. Un résultat absent, un format inconnu, un message d'accès ou un changement d'octets bloque la poursuite. Une boucle de curseur stoppe le profil. Une page vide suit `has_more`, elle ne devient pas arbitrairement une fin. Les réservations restent consommées après un échec, même si le fournisseur dit ne pas avoir facturé. Le solde observé peut diminuer le plafond, jamais l'augmenter.

En cas d'échec constaté, consigner le motif sans erreur distante ni secret :

```powershell
python -B -X utf8 scripts/profile_campaign.py stop collection/runtime/profile-v27/campaign --attempt 0 --reason uncertain_outcome
```

Les raisons acceptées sont `access_restricted`, `rate_limited`, `quota_exhausted`, `request_failed`, `uncertain_outcome`. Le profil reste arrêté et aucun retry n'est effectué.

## Client automatique, uniquement avec les crédits gratuits vérifiés

Ne pas réserver manuellement une page avant de lancer ce client : il gère ses propres réservations. Fournir `SCRAPECREATORS_API_KEY` par l'environnement depuis un gestionnaire local ou une configuration privée ; ne pas mettre la clé dans le plan, une commande enregistrée, Git, le chat ou un log. Le client ne cherche aucun secret dans le navigateur.

```powershell
python -B -X utf8 scripts/scrapecreators_collect.py collection/runtime/profile-v27/campaign --job tiktok:maclede12 --max-pages 5 --dry-run
python -B -X utf8 scripts/scrapecreators_collect.py collection/runtime/profile-v27/campaign --job tiktok:maclede12 --max-pages 5 --execute
```

Chaque cycle réserve d'abord un crédit pour `GET /v1/account/credit-balance`, car l'exemple OpenAPI de cette route indique lui-même `credits_charged: 1` ; son coût gratuit n'est pas supposé. Le champ de solde est `creditCount`. Le client vérifie le solde puis réserve un deuxième crédit pour la page. Un essai confirmé de 100 crédits permet donc **au maximum 50 cycles réservés** avec cette marge conservatrice, et non 100 pages garanties. Le solde total ne peut jamais augmenter le plafond de crédits gratuits constaté au démarrage.

La borne est de 1 à 10 pages par invocation, avec 2 secondes minimum entre cycles. Aucun retry automatique, redirection HTTP, abonnement, recharge ou endpoint de paiement. Les issues de requête incertaines restent réservées et bloquent la poursuite. Le mode aperçu n'accède pas à l'environnement des secrets. Les réponses natives sont conservées dans `campaign/private-raw/` ; ce dossier et le registre de campagne doivent rester privés. L'ingestion locale produit ensuite la projection minimale et la revue.

Les réponses sont limitées à 32 MiB, lues par blocs `read1` avec une échéance monotone de 30 secondes et un timeout socket de 15 secondes. Cela interrompt un corps qui arrive au compte-gouttes ; une lecture bloquée peut dépasser l'échéance d'au plus son timeout socket. L'ouverture HTTPS et la lecture initiale des en-têtes utilisent le timeout de la bibliothèque : ce n'est pas une garantie de durée totale stricte contre un serveur qui distille les en-têtes. Toute interruption doit conserver la réservation, sans relance automatique.

## Réconcilier les autres fournisseurs

Un export d'Apify, de créateur ou de fournisseur déjà projeté par son adaptateur peut rejoindre la même revue :

```powershell
python -B -X utf8 scripts/profile_campaign.py attach-export collection/runtime/profile-v27/campaign --manifest work/apify-v26/provider-export/manifest.json
```

Le chemin est indicatif : fournir un manifeste existant. Les pages et leur SHA256 sont contrôlés par `public_export.load_manifest`. Les schémas déjà supportés (`generic`, `meta_graph`, `tiktok_display`) sont réutilisés. Les JSON natifs Bright Data ou Apify ne sont **pas** rebaptisés `generic` sans mapping examiné. Les index Exa restent dans leur propre workflow : ce registre refuse `indexed_export` pour ne pas promouvoir des commentaires ou extraits composites en légendes natives.

Les pièces jointes ne déduisent aucune consommation fournisseur : le compte de crédits de ce registre concerne seulement les requêtes ScrapeCreators réservées ici. Pour les autres fournisseurs, conserver leur reçu et leur propre garde de budget. Aucune dépense ni reprise fournisseur n'est déclenchée par l'attachement.

## Revue et intégration

```powershell
python -B -X utf8 scripts/profile_campaign.py review collection/runtime/profile-v27/campaign --output collection/runtime/profile-v27/review-01
```

Le dossier neuf contient :

- `quarantine.jsonl` : une identité par ligne, toutes ses variantes, les titres/descriptions/hashtags séparés et les SHA256 des réponses/pages/lignes sources ;
- `invalid-rows.json` : les preuves des entrées non projetables, sans commentaires ni contenu arbitraire ;
- `tiktok/manifest.json` et `instagram/manifest.json` quand présents : format PUBLIC_EXPORT compatible avec l'outil existant, **pour préparation et revue uniquement** ;
- `report.json` : nombre de lignes, identités uniques, répétitions et contradictions. `accepted_for_publication` reste toujours zéro.

Les légendes privées sont effacées de la projection. Images, carrousels, diaporamas, partenariats, accès restreints et incohérences sont signalés. Une variante restrictive ne disparaît pas derrière une autre version plus propre. Aucun moteur, véhicule, langue audio, niveau, procédure ou licence n'est confirmé par ce registre. Les mentions de véhicules en hashtags restent dans leurs champs de texte ; `vehicle_compatibility` reste vide. Une légende n'est ni une vidéo regardée ni une transcription.

Après lecture des variantes, utiliser le workflow `SOCIAL_INGESTION.md` pour préparer un paquet révisé et ses approbations exactes. Ne pas appliquer directement un `accepted.json` que le préparateur pourrait produire par ses seuls heuristiques. Ce registre ne crée aucun fichier `accepted.json` ou `approval.json`, ne modifie pas le catalogue et ne publie rien.

## Validation

```powershell
python -B -X utf8 -m unittest discover -s scripts -p "test_*.py" -v
```

Les fixtures sont synthétiques et temporaires. La suite contrôle les réservations, erreurs, reprises, boucles et pages vides, les limites, les métadonnées privées ou non vidéo, les hashtags, les variantes, la compatibilité du manifeste et les empreintes. Aucun test ne nécessite un compte ou un appel réseau.
