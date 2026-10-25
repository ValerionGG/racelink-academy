# Collecteur public Agent Reach / Exa

Le collecteur 1.0.1 lit les réponses JSON modernes du MCP Exa et les anciens formats. Il collecte des liens et métadonnées indexées ; aucune connexion sociale, clé, dépense Apify, vidéo ou transcription n'est requise. Installer au préalable Python, Node et mcporter via leurs sources officielles.

Depuis `collector/`, aperçu sans réseau :

```powershell
python scripts/local_collect.py collection/public-french-v24/plan.json --output collection-results/v24
```

Collecte explicitement bornée, avec reprise :

```powershell
python scripts/local_collect.py collection/public-french-v24/plan.json --output collection-results/v24 --execute --max-jobs 2 --interval 2
python scripts/local_collect.py collection/public-french-v24/plan.json --output collection-results/v24 --execute --resume --max-jobs 46 --interval 2
```

Conserver tous les fichiers du cache et leurs empreintes pour la qualification, pas uniquement `records.jsonl` dédoublonné : une variante négative peut empêcher l'import. Les résultats ne sont jamais importés automatiquement. La requête française ne prouve ni la langue d'un résultat ni celle de l'audio. Les quotas du service public peuvent interrompre la collecte.

Validation hors réseau : `python -B -m unittest scripts.test_local_collect -v` (28 tests).
