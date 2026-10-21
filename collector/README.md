# RaceLink — préparation des exports de créateurs

Python 3.10+ ; aucune dépendance externe. L’adaptateur `PUBLIC_EXPORT` lit uniquement des fichiers locaux JSON/JSONL/CSV déjà obtenus auprès d’une source autorisée. Aucune collecte réseau, aucun média téléchargé et aucune DB fournie.

```powershell
python scripts/public_export.py --help
python scripts/public_export.py chemin/manifest.json --output work/lot-5000 --max-records 5000
python scripts/public_export.py chemin/manifest.json --output work/lot-5000 --max-records 5000 --resume
python -m unittest tests_public_export -v
```

Voir [PUBLIC_EXPORT.md](PUBLIC_EXPORT.md) pour le manifeste, les schémas Meta Graph/TikTok Display, les champs génériques, les preuves, la quarantaine et les limites. Les résultats sont des **candidats à relire**. Les sorties sont compatibles avec le mécanisme d’approbation explicite de `bulk_ingest.py` ; aucun contenu n’est importé automatiquement.

`server.py`, `automotive.py`, `schema.sql` et les modules de `scripts/` sont les dépendances locales du validateur. Leur présence ne lance aucun serveur et ne crée aucune base. Les tests utilisent uniquement des fichiers temporaires et un jeu synthétique de 1 500 entrées.

L’ancien outil `bulk_ingest.py` inclut aussi un lecteur de dataset Apify existant ; ce chemin est distinct et n’est jamais appelé par `PUBLIC_EXPORT`. Ne transmettez aucun token dans les exports ou manifestes.

## Références publiées sur les sites des créateurs

Le collecteur distinct `scripts/creator_site_collect.py` lit des pages explicitement choisies sur les domaines autorisés des créateurs/éditeurs. Il conserve liens sociaux, libellés et SHA des pages ; aucun accès Instagram/TikTok natif, média ou import DB. Il respecte robots, arrête l’hôte sur refus, refuse réseaux privés et redirections, et borne les requêtes. Les labels/contextes ne deviennent jamais des légendes vidéo.

Voir [CREATOR_SITES.md](CREATOR_SITES.md) pour les modes hors ligne/en ligne, les limites, la déduplication et le raccordement `indexed_export` à `PUBLIC_EXPORT`.

```powershell
python scripts/creator_site_collect.py --help
python -m unittest discover -s tests -p test_creator_site_collect.py -v
```
