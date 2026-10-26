# Passer de la collecte aux références publiées

Ces commandes partent de ce dossier : `focus-academy` dans le ZIP, ou `collector` dans le dépôt. Aucun export brut, registre de compte ou dossier `collection/runtime/` ne doit être publié.

## Préparer sans modifier la base

Après une collecte réellement terminée :

```powershell
python -B -X utf8 scripts/profile_campaign.py review collection/runtime/profile-v27/campaign --output collection/runtime/profile-v27/review-01
python -B -X utf8 scripts/public_export.py collection/runtime/profile-v27/review-01/tiktok/manifest.json --output collection/runtime/profile-v27/prepared-tiktok --max-records 5000
python -B -X utf8 scripts/review_social_batch.py collection/runtime/profile-v27/prepared-tiktok --output collection/runtime/profile-v27/editorial-tiktok --batch-size 100
```

Utiliser le manifeste Instagram à la place pour ce réseau. Il n'existe que si des publications ont été reçues. Le dossier de sortie doit être neuf ; une reprise exige les mêmes sources et empreintes.

## Relire les preuves avant approbation

Relire la légende complète, les variantes et les exclusions antérieures. Retenir les explications pédagogiques précises ; garder en attente une légende insuffisante ; exclure publicités pures, humour, images/carrousels et contenu privé. Un hashtag, un pays de recherche ou une bio ne prouve ni compatibilité avec un moteur, ni langue audio.

Conserver les citations et la provenance des corrections. Séparer titre, description et hashtags. Garder la légende dans `social_content.original_caption` pour son affichage. Le classement reste candidat, la licence inconnue et la transcription absente sans preuve distincte. Le badge RaceLink et la validation d'une procédure ne découlent pas de l'import.

Ne pas modifier un `accepted.json` scellé. Une correction demande un nouveau paquet et de nouvelles empreintes, liés à la source. Remplir `approval.template.json` avec les seules identités relues et retenues et le hash du paquet exact ; enregistrer la décision dans `approval.json`.

## Vérifier, sauvegarder puis importer

```powershell
python -B -X utf8 scripts/bulk_ingest.py apply collection/runtime/profile-v27/prepared-tiktok --db data/catalog.sqlite3 --approval collection/runtime/profile-v27/prepared-tiktok/approval.json
```

Cette commande est un aperçu. Contrôler `database_modified=false`, les nouveautés, doublons et éventuelles mises à jour. Pour une campagne d'ajouts, sélectionner uniquement les nouvelles identités.

Avant exécution, sauvegarder SQLite avec son API de sauvegarde afin d'inclure le journal WAL. Après cette sauvegarde, la même commande avec `--execute` importe le paquet approuvé. Vérifier delta exact, intégrité, recherche et préservation des anciennes lignes. Exporter le site, contrôler les fichiers effectivement servis et reconstruire le ZIP. Des milliers de résultats bruts ne constituent pas automatiquement des milliers de tutoriels utiles.
