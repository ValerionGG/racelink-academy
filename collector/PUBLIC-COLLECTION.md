# Référencer des vidéos publiques sans crédit payant

Cette voie utilise les collecteurs déjà présents dans `scripts/` : `local_collect.py` pour YouTube via yt-dlp, et `collect_dailymotion.py` pour les métadonnées publiques Dailymotion. Elle ne requiert ni compte fournisseur ni crédit de collecte. La version V29 l’a exécutée avec yt-dlp 2026.08.19, sans cookie et sans téléchargement vidéo, audio ou sous-titre.

## 1. Définir une recherche bornée

Créer un fichier `plan.json` avec des sujets précis, distincts des campagnes terminées :

```json
{"jobs":[{"kind":"youtube_search","value":"remplacer filtre habitacle voiture tutoriel français","limit":50}]}
```

Depuis le dossier du collecteur, prévisualiser puis exécuter dans un nouveau dossier :

```powershell
python -B -X utf8 scripts/local_collect.py plan.json --output collection/nouveau-lot
python -B -X utf8 scripts/local_collect.py plan.json --output collection/nouveau-lot --execute --max-jobs 1 --interval 2 --timeout 90
```

Le premier appel est une prévisualisation. Le second collecte uniquement les métadonnées. Conserver le plan, les caches et le checkpoint. Une reprise utilise le même plan et le même dossier avec `--resume`; ne pas recréer un dossier pour rejouer des travaux terminés. À toute limitation d’accès, suspendre cette source.

Pour Dailymotion, un exemple borné :

```powershell
python -B -X utf8 scripts/collect_dailymotion.py --output collection/nouveau-dm --query "changer filtre habitacle voiture" --pages 1 --page-size 50
python -B -X utf8 scripts/collect_dailymotion.py --output collection/nouveau-dm --query "changer filtre habitacle voiture" --pages 1 --page-size 50 --execute
```

Ce collecteur conserve les réponses et leurs empreintes; il s’arrête sur une restriction d’accès ou de débit. Les requêtes génériques Dailymotion peuvent retourner beaucoup de publicité et de hors-sujet : leur volume brut ne mesure pas la qualité du catalogue.

## 2. Préparer et relire les nouvelles fiches

Pour les résultats YouTube :

```powershell
python -B -X utf8 scripts/bulk_ingest.py prepare collection/nouveau-lot/records.jsonl --output collection/nouveau-lot-revue --db data/catalog.sqlite3
```

Cette étape lit la base pour comparer les identités; elle ne l’écrit pas. Relire chaque nouvelle candidature et les quarantaines pertinentes : objectif pédagogique précis, cohérence du titre et du texte, langue du texte, véhicule et sujet réellement mentionnés. Les créneaux, démarrages en côte et autres leçons de conduite peuvent nécessiter une revue manuelle lorsque les règles générales ne reconnaissent pas le sujet.

Séparer titre, description, hashtags et liens avec `social_metadata.py`. Conserver les textes originaux et la provenance. Ne pas compléter une description absente ou tronquée avec des étapes supposées. Les listings YouTube peuvent être partiels ou localisés automatiquement : ils ne prouvent ni une légende complète ni la langue audio. Dailymotion expose une langue déclarative par la plateforme, également distincte d’une vérification audio.

Classer selon le sujet et le véhicule documentés, sans déduire une compatibilité à partir d’un seul hashtag. Écarter promotions sans leçon, promesses universelles, contradictions et contenus hors sujet. Une référence publique n’implique pas une licence libre ni une procédure officiellement certifiée. Aucun transcript n’est créé par cette voie.

## 3. Importer et publier avec contrôle

Dédupliquer contre la base actuelle et les lots précédents. Sceller les candidats relus par SHA-256 et produire une approbation contenant les seuls identifiants retenus. Sauvegarder SQLite, importer sous contrôle strict, puis vérifier que seules les nouvelles fiches approuvées ont été ajoutées et qu’aucune ancienne ligne n’a changé.

`bulk_ingest.apply` accepte YouTube, TikTok et Instagram. **Dailymotion et Vimeo nécessitent une normalisation et un import strict adaptés**, avec les mêmes contrôles de source, sauvegarde et différence de base; ne pas leur attribuer artificiellement une autre plateforme pour contourner cette limite.

Après export, vérifier les comptes par plateforme/langue, la recherche, les fiches publiées et la version du paquet local. Distinguer dans le bilan lignes reçues, vidéos distinctes, nouvelles fiches retenues et fiches effectivement publiées. Les processus yt-dlp peuvent effectuer plusieurs appels internes : ne pas présenter leur nombre comme un compte exact de requêtes HTTP.

Documentation : [Agent Reach](https://github.com/Panniantong/agent-reach), [yt-dlp](https://github.com/yt-dlp/yt-dlp#usage-and-options), [API Dailymotion](https://developers.dailymotion.com/v0/reference/perform-an-api-call), [champs Dailymotion](https://developers.dailymotion.com/v0/reference/video-fields).

## Voie PeerTube ajoutée en V34

`scripts/peertube_collect.py` recherche SepiaSearch et liste les chaînes pédagogiques explicitement autorisées dans son plan. Prévisualisation par défaut, plafond, délai, checkpoint avant requête, arrêt sur limitation ; aucune vidéo téléchargée. Voir [le guide](scripts/PEERTUBE-COLLECTOR.md).

Une référence PeerTube conserve sa vraie URL et son identité. Le schéma courant la range dans `platform=other`, avec `provider=peertube` et un libellé PeerTube dans sa fiche. Ce n’est pas une vidéo YouTube. L’import est distinct de la collecte, exige revue, preuve native, déduplication globale, sauvegarde et scellé des seuls nouveaux identifiants. Les checkpoints V34 sont terminés ; ne pas les rejouer.
