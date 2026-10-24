# Préparation massive de métadonnées — V23

Outil figé : `outputs/focus-academy/scripts/scale_ingest.py` (1.0.2). Il prépare des lots hors réseau ; il n'acquiert aucune vidéo et n'écrit pas dans le catalogue. Les paquets restent des candidats à relire.

## 1. Enregistrer un snapshot immuable

Depuis `outputs/focus-academy`, ce pilote utilise le fichier réel partiel du 24 octobre. Pour la collecte finale, choisir le fichier final **contenant toutes les variantes vérifiées** et de nouveaux répertoires `social-final-stage` / `social-final-review`. Ne pas remplacer le fichier d'un stage existant.

```powershell
python scripts/scale_ingest.py stage ../../work/scale-v23/social-partial.jsonl --stage ../../work/scale-v23/social-pilot-stage --max-records 25000
```

Si la réponse indique `complete: false`, reprendre exactement les mêmes entrées :

```powershell
python scripts/scale_ingest.py stage ../../work/scale-v23/social-partial.jsonl --stage ../../work/scale-v23/social-pilot-stage --max-records 25000 --resume
```

Plusieurs fichiers sont acceptés comme arguments avant `--stage`. Les variantes de fichiers différents sont rapprochées par identité média. Les sources déjà terminées sont sautées à la reprise. Le SHA256 du fichier entier et la version des modules de qualification sont vérifiés ; changer une source ou le moteur impose un nouveau stage.

## 2. Préparer des paquets bornés

Toutes les sources prévues doivent être enregistrées et complètes avant la première préparation, qui scelle la campagne :

```powershell
python scripts/scale_ingest.py prepare --stage ../../work/scale-v23/social-pilot-stage --output ../../work/scale-v23/social-pilot-review --batch-size 1000 --max-batches 10
python scripts/scale_ingest.py prepare --stage ../../work/scale-v23/social-pilot-stage --output ../../work/scale-v23/social-pilot-review --batch-size 1000 --max-batches 10 --resume
```

Répéter la seconde commande jusqu'à `complete: true`. `report.json` global donne les comptes ; `checkpoint.json` lie les paquets, leurs empreintes et la couverture des lignes. Aucun paquet n'est publié. Une interruption rejoue seulement le paquet non confirmé.

## 3. Relire et approuver les identités exactes

Chaque `batch-000000`, puis `batch-000001`, etc., contient :

- `accepted.json` : candidats issus des règles de métadonnées, sans attestation de visionnage ;
- `quarantine.jsonl` : motifs contradictoires, manque de preuve ou données rejetées ;
- `report.json` : empreinte du fichier accepté, comptes, sources et version du moteur ;
- `approval.template.json` : liste d'approbation vide.

Examiner titre/légende, preuve et statut de langue, domaine pédagogique, modèle/moteur réellement cités et exclusions antérieures. Une panne seule, une publicité ou un spectacle de conduite ne devient pas un tutoriel parce qu'il contient un mot technique. Une légende Exa composite ne prouve pas le sujet du média cible. La revue peut conserver moins d'IDs, mais ne doit pas contourner une quarantaine sans nouvelle preuve.

Copier le modèle **hors du paquet**, pour ne pas modifier les fichiers vérifiés par le checkpoint :

```powershell
Copy-Item -LiteralPath ../../work/scale-v23/social-pilot-review/batch-000000/approval.template.json -Destination ../../work/scale-v23/social-pilot-approval-000000.json
```

Renseigner manuellement dans cette copie `approved_ids` (liste exacte non vide), `reviewer` et `reason`, en conservant `accepted_sha256`. Ne pas sélectionner automatiquement tous les candidats. Toute correction de données requiert un nouveau paquet de revue et une nouvelle empreinte ; ne pas éditer silencieusement `accepted.json`.

## 4. Simuler puis appliquer le lot relu

Les exemples suivants supposent une base existante choisie par le responsable de l'intégration. Adapter `C:/chemin/catalogue.sqlite3` au chemin autorisé. La simulation ouvre cette base en lecture seule et identifie nouveautés et références existantes :

```powershell
python scripts/bulk_ingest.py apply ../../work/scale-v23/social-pilot-review/batch-000000 --db C:/chemin/catalogue.sqlite3 --approval ../../work/scale-v23/social-pilot-approval-000000.json
```

Après revue du résultat, sauvegarde de la base et autorisation de l'intégration, seule cette variante écrit les IDs approuvés dans une transaction stricte :

```powershell
python scripts/bulk_ingest.py apply ../../work/scale-v23/social-pilot-review/batch-000000 --db C:/chemin/catalogue.sqlite3 --approval ../../work/scale-v23/social-pilot-approval-000000.json --execute
```

L'application reste une étape séparée par paquet ; elle vérifie empreinte, identité canonique, statut candidat et schéma serveur. `scale_ingest` ne propose aucune commande `apply`. Une preuve négative ultérieure demande une nouvelle campagne de maintenance : ce pipeline ne retire pas automatiquement un contenu déjà publié.

## Entrées compatibles et limites

Un objet brut par ligne physique **JSONL/NDJSON**, maximum 2 MiB par ligne. Fournisseur `auto` par défaut, ou les valeurs de `--provider` affichées par l'aide. Schémas actuels : yt-dlp YouTube/Instagram/TikTok et exports Apify Instagram/TikTok déjà acquis ; les enregistrements Agent Reach/Exa issus de `local_collect` conservent leur `_collection.provider='exa-public-mcp'` et leur preuve indexée. Il n'y a pas de nouvel appel Apify dans cet outil.

Champs utiles reconnus par les adaptateurs existants :

| Objet | Exemples de champs bruts |
|---|---|
| Identité | `url`, `webVideoUrl`, `webpage_url`, `id`, `shortCode` |
| Texte natif | `title`, `caption`, `text`, `desc`, `description` |
| Auteur | `authorMeta.name`, `ownerUsername`, `channel`, `uploader` |
| Langue déclarée | `language`, `defaultAudioLanguage`, `captionLanguage`, avec origine conservée |
| Publication / vignette | `createTimeISO`, `timestamp`, `upload_date`, `thumbnail`, `displayUrl`, `videoMeta.coverUrl` |
| Contraintes | indicateurs privé, publicité, contenu non vidéo et disponibilités explicitement présents |
| Collecte | `_collection` dans le schéma existant de `local_collect`, notamment fournisseur, date et preuve indexée/directe |

Les descriptions d'index ne sont pas assimilées à des légendes natives. Aucune langue audio n'est inventée depuis une requête ; titre, légende et langue audio restent distincts. Les hashtags sont séparés par `social_metadata` sans fabriquer de compatibilité automobile. Commentaires complets, jetons, cookies, sous-titres et fichiers médias ne sont pas propagés. Le SHA256 du record brut permet de retrouver sa preuve dans le snapshot conservé séparément.

Ne pas envoyer les fichiers `accepted.json` déjà normalisés par `public_export` ou un autre adaptateur. Ne pas envoyer un conteneur `items`/`entries`/`latestPosts` : aplatir avec une procédure qui conserve les contraintes du parent. **Dailymotion, Facebook, Vimeo et PeerTube ne sont pas pris en charge ici** ; leurs records normalisés suivent la voie serveur séparée sous revue. Ne pas changer leur plateforme pour les faire passer.

Le stage ne compare pas le catalogue ; la simulation `bulk_ingest apply` le fait. Fournir toutes les variantes des caches vérifiés, car une sortie déjà dédupliquée peut omettre une preuve défavorable. Une campagne scellée refuse de nouveaux fichiers. Les exclusions entre campagnes doivent être conservées par le responsable éditorial.

## Vérification et capacité mesurée

Depuis la racine du workspace : `python work/scale-v23/test_scale_ingest.py` — **23/23 tests**. Depuis l'application : `python -m unittest tests_bulk_ingest tests_social_metadata tests_public_export -q` — **97/97 régressions**. La version 1.0.2 vérifie le hash même après erreur JSON/Unicode ou dépassement de taille et invalide définitivement un stage dont une source a changé pendant la lecture, y compris après restauration du fichier original. Une nouvelle campagne est alors obligatoire ; l'outil ne réhabilite pas les commits partiels.

La mesure de capacité ci-dessous a été exécutée sur la version 1.0.1 (voir son SHA dans le rapport), avant le correctif du chemin d’erreur 1.0.2. `python work/scale-v23/benchmark_scale.py` mesure des données synthétiques dans une base temporaire supprimée ensuite : **100 301 lignes, 100 200 identités, 101 paquets, 116,343 s, pic mémoire 66 764 800 octets**, sur cette machine. Cela prouve une capacité de préparation, pas une acquisition de 100 200 vidéos réelles. Résultats : `benchmark-results.json` et `validation-results.json`. Architecture détaillée : `BACKEND-AUDIT.md`.

## Vérifier l'export final avant publication

Le snapshot `baseline-identities.json` contient les 36 901 identités et empreintes des fiches publiques avant import. Il est lié à `baseline.json`, sans ouverture de la base. `publication-approved.json` doit contenir exactement les records normalisés nouveaux réellement retenus, en tableau JSON ; les enregistrements existants n'en font pas partie.

Depuis la racine du workspace, après génération et synchronisation des exports :

```powershell
python work/scale-v23/verify_release.py verify --expected-records work/scale-v23/publication-approved.json
```

Par défaut, le contrôle lit `outputs/focus-academy-static/aide` et `work/racelink-academy-git/site`, puis écrit `work/scale-v23/release-checks.json`. Il exige les mêmes octets de catalogue JSON/gzip dans les deux exports : deux générations avec des dates différentes doivent être synchronisées avant le contrôle. Les options `--local`, `--git` et `--output` permettent de vérifier d'autres dossiers explicitement.

Contrôles : empreintes du catalogue/config/manifeste et gzip, IDs/URLs canoniques/identités média uniques, préservation de la baseline, ensemble exact des ajouts approuvés, total baseline + vrais nouveaux, statistiques, guides inchangés, projection des véhicules/tâches approuvés et preuve textuelle des mentions. Le rapport donne les IDs réels derrière les nouvelles applications véhicule et les interventions. Il ne confirme ni compatibilité constructeur ni exactitude d'un tutoriel non visionné.

Un scan limité détecte des champs de secrets évidents, paramètres d'authentification et chemins locaux dans les **nouvelles fiches publiques**. Il rapporte les emplacements/règles sans imprimer une valeur suspecte ; il ne prouve pas l'absence exhaustive de secrets. Aucun coffre de secrets, variable d'environnement, réseau ou catalogue SQLite n'est lu.

Test reproductible : `python work/scale-v23/test_verify_release.py` — **13/13 tests**. Le rapport `verify-release-baseline-smoke.json` est seulement un smoke test de la baseline sur un même export fourni deux fois, pas une validation finale ni une comparaison indépendante des deux versions finales.

## Version livrée et campagne déjà préparée

Le moteur livré est en version **1.0.2**, SHA256 `3397e81cb786f1917831dce274344ab859253e5a7ee7842948657373de5a2427`. Les paquets social-final-v2 ont été préparés avec **1.0.1** sur un snapshot immuable, sans erreur de lecture. Leurs preuves et empreintes restent celles de cette exécution ; ils ne sont pas réattribués à 1.0.2. La comparaison stage-revision-comparison.json conserve la comparaison précédente des contenus/provenances.
