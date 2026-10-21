# PUBLIC_EXPORT — exports sociaux locaux

Le nouvel adaptateur prépare des vidéos Instagram et TikTok à partir de fichiers déjà obtenus légalement auprès d’un créateur, d’une API autorisée ou d’un fournisseur. Il ne recherche rien sur les plateformes, ne fait aucune requête réseau et ne modifie aucune base. Un export peut contenir plusieurs milliers de lignes ; cette capacité ne garantit ni leur disponibilité, ni leur pertinence pédagogique.

## Préparer jusqu’à 5 000 références

Python 3.10+ et sa bibliothèque standard suffisent. Depuis la racine `collector/` du paquet autonome, ou `outputs/focus-academy/` :

```powershell
python scripts/public_export.py chemin/manifest.json --output work/lot-5000 --max-records 5000
python scripts/public_export.py chemin/manifest.json --output work/lot-5000 --max-records 5000 --resume
python -m unittest tests_public_export -v
```

La reprise exige le même manifeste, les mêmes limites, la même version de l’adaptateur et les mêmes empreintes de toutes les pages et caches. Les pages JSON normalisées servent uniquement à reprendre cette préparation. Aucun jeton ni fichier d’authentification n’est nécessaire.

Exemple de manifeste **à compléter avec une empreinte réelle**, placé à côté de ses pages :

```json
{
  "version": 1,
  "kind": "PUBLIC_EXPORT",
  "source": {
    "name": "Nom de l’éditeur ou du créateur",
    "kind": "authorized_api_export",
    "source_url": "https://example.org/creator-export",
    "evidence_reference": "Référence de l’autorisation et du lot, sans identifiants secrets",
    "captured_at": "2026-10-21T12:00:00Z"
  },
  "pages": [
    {"file": "page-001.json", "sha256": "REMPLACER_PAR_64_CARACTERES_HEXADECIMAUX", "format": "json", "schema": "meta_graph"}
  ]
}
```

Calcul d’une empreinte : `(Get-FileHash chemin/page-001.json -Algorithm SHA256).Hash.ToLower()`.

Le manifeste accepte exactement les champs montrés. `source.kind` vaut `creator_export`, `authorized_api_export`, `provider_export`, `public_dataset` ou `indexed_export`. Cette déclaration doit être documentée par la personne qui fournit le lot ; l’adaptateur ne la certifie pas. La référence HTTPS ne contient ni paramètres, ni fragment, ni identifiants. Elle est archivée, jamais appelée.

## Formats et champs

| Schéma | Conteneur JSON | Champs source utilisés |
|---|---|---|
| `meta_graph` | `{"data": [...]}` | `permalink`, `caption`, `title` si présent, `username`, `media_type`, `timestamp`, `thumbnail_url` |
| `tiktok_display` | `{"data": {"videos": [...]}}` | `share_url`, `title`, `video_description`, `create_time`, `duration`, `cover_image_url` ; `creator` seulement s’il est fourni explicitement |
| `generic` | tableau, ou `items` / `videos` / `entries` | `url`, `title`, `caption`, `creator`, `media_type`, `published_at`, `duration_seconds`, `thumbnail_url`, `hashtags` |

JSONL contient un objet par ligne physique. CSV utilise les mêmes noms de colonnes ; la colonne optionnelle `hashtags` contient un tableau JSON, par exemple `["#mécanique","#Auto"]`. Les légendes multilignes doivent être échappées selon CSV. Les lettres Unicode, les signes diacritiques et les séparateurs U+2028 sont conservés dans les preuves.

Une légende `caption` doit appartenir au média cible. Un résumé de moteur de recherche, des commentaires ou des recommandations de posts voisins ne sont pas des légendes. Pour des titres de liens trouvés dans un index ou sur un site éditeur, utiliser `indexed_export` : le corps `caption` est ignoré et la provenance reste indexée. Un titre tronqué ou une légende sans première phrase complète passe en revue ; aucun titre n’est inventé.

`private`, `is_private`, `isPrivate`, `availability`, `sponsored`, `is_ad`, `isAd`, `paidPartnership`, `isSponsored`, `is_video`, `isVideo`, `is_story`, `is_photo`, `is_aigc` et `is_ai_generated` sont des signaux de restriction ou de revue quand présents. Les booléens acceptent aussi les nombres 0/1 et les textes `true`/`false`, `1`/`0`, `yes`/`no` ; une autre valeur non vide demande une revue. Une indication explicite `is_video=false` ou `isVideo=0` impose une quarantaine, même si l’URL contient `/reel/` ou qu’une autre variante annonce une vidéo. Les autres champs sont ignorés. Les champs génériques `language`, les termes de recherche, les commentaires, les profils détaillés, les transcriptions, les vidéos et les jetons ne sont jamais propagés. Seule une estimation prudente du français à partir du texte source peut être produite ; l’audio reste non vérifié. Les liens de miniature restent de simples métadonnées, sans téléchargement.

## Sortie et revue

- `accepted.json` : candidats pédagogiques, pas une sélection approuvée.
- `quarantine.jsonl` : raisons, empreintes et fiche normalisée lorsqu’elle existe.
- `report.json` : comptes, bornes, dédoublonnage et empreintes.
- `approval.template.json` : liste d’approbation vide, liée à l’empreinte du lot.
- `checkpoint.json` et `normalized-page-*.json` : reprise locale vérifiée.

Les identités sont dédupliquées par URL canonique/ID média, y compris si l’auteur d’une URL TikTok change. Une variante privée, publicitaire ou insuffisamment étayée maintient toute l’identité en quarantaine ; aucun doublon défavorable ne disparaît. `provenance.adapter=public_export` et `schema_adapter` conserve le schéma natif. `public_export_provenance` relie chaque ligne à la page, son SHA256 et celui de l’objet source. Titres, légendes originales et hashtags séparés restent dans `social_content`. Aucun statut de visionnage, de langue audio ou de libre réutilisation n’est créé.

Les fichiers normalisés sont compatibles avec l’application existante, qui compare les identités à une base existante. Cette commande est une simulation :

```powershell
python scripts/bulk_ingest.py apply work/lot-5000 --db chemin/base-existante.sqlite3
```

L’écriture exige séparément `--execute` et un manifeste d’approbation explicite lié à l’empreinte, avec les IDs exacts, un relecteur et une justification. Aucune de ces écritures n’a été exécutée pour cette livraison.

Limites : 1–1 000 pages ; 32 MiB par page ; 512 MiB au total ; 2 MiB par ligne JSONL/champ CSV ; 1–100 000 lignes traitées selon `--max-records`. Les chemins absolus, traversées, liens vers un fichier extérieur, noms de fichiers d’identifiants et empreintes incohérentes sont refusés. Les pointeurs `paging.next`, curseurs API ou champs `has_more` ne sont jamais suivis : fournir explicitement les pages déjà exportées. Le rapport ne prétend pas que l’export représente tout le compte créateur.

## Voies d’acquisition réellement documentées

TikTok Display fournit les publications publiques du compte qui a autorisé l’application, avec une pagination par curseur et 20 éléments au maximum par page. Atteindre 5 000 entrées demanderait au moins 250 pages si les comptes autorisés possèdent suffisamment de vidéos ; ce n’est pas une recherche globale. Les champs `title`, `video_description`, `share_url` et `create_time` sont documentés ; les miniatures expirent. [API List Videos](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-list), [Video Object](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-object).

Le SDK officiel Meta expose `IGUser.get_media()` et les champs `IGMedia` utilisés ici. Il constitue une voie d’intégration pour un accès API autorisé, pas un moyen de récupérer sans autorisation tous les comptes Instagram. [SDK Meta](https://github.com/facebook/facebook-python-business-sdk), [IGUser](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/iguser.py), [IGMedia](https://github.com/facebook/facebook-python-business-sdk/blob/main/facebook_business/adobjects/igmedia.py).

Le SDK officiel TikTok Business exige une application, l’autorisation et l’authentification ; ce n’est pas une nouvelle source universelle gratuite. [SDK officiel](https://github.com/tiktok/tiktok-business-api-sdk). Les bibliothèques [TikTok-Api](https://github.com/davidteather/TikTok-Api) et [Instaloader](https://github.com/instaloader/instaloader) documentent des sessions/cookies ou proxys selon les usages ; elles ne sont ni installées ni appelées ici. [yt-dlp](https://github.com/yt-dlp/yt-dlp) reste disponible dans le collecteur existant pour les voies autorisées ; aucun nouvel appel natif Instagram/TikTok bloqué n’a été tenté.

Validation de capacité : 1 500 enregistrements **synthétiques**, cinq pages temporaires, dédoublonnage, reprise et normalisation testés. Aucun de ces enregistrements ne rejoint le catalogue. **Nouvelles vidéos acquises par ce nouvel adaptateur : 0.**
