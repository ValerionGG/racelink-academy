# RaceLink Academy

Bibliothèque ouverte de tutoriels auto et motorsport : 50 520 vidéos référencées, dont 10 632 en français, et 11 guides.

**Site en ligne : <https://valeriongg.github.io/racelink-academy/>**

## Reprendre le projet

Site statique sans framework ni dépendance à installer. Le catalogue est chargé puis interrogé dans le navigateur par un Web Worker.

### Lancer en local

Les ressources utilisent le chemin absolu `/racelink-academy/` : il faut servir `site/` sous ce préfixe.

```bash
mkdir -p /tmp/rl && ln -s "$PWD/site" /tmp/rl/racelink-academy
python3 -m http.server 8420 --directory /tmp/rl
```

Puis ouvrir <http://localhost:8420/racelink-academy/>.

### Où modifier quoi

| Sujet | Fichiers |
|---|---|
| Design de l'application | `site/paddock-ui.css` (jetons, accueil), `site/paddock-pages.css` (bibliothèque, fiches, menus) |
| Feuille de style finale | `site/app-ui.css` est générée : `python3 scripts/build_ui.py` après toute modification de CSS |
| Application | `site/app.js`, `site/paddock-home.js` (sections de l'accueil), `site/resource-card.js`, `site/resource-detail.js`, `site/guide-ui.js` |
| Recherche et classement | `site/catalog-worker.js`, tests : `node --test collector/tests_paddock_search.mjs` |
| Pages autonomes | `site/vehicules.html`, `site/clio-5-2025.html`, `site/3d.html`, `site/formats-courts.html`, habillées par `site/paddock-annex.css` et `site/paddock-chrome.js` |
| Données publiées | `site/catalog/catalog.json` et sa version `.gz`, `site/social-index.json` |
| Collecte et ingestion | `collector/`, dernier lot : `collector/collection/tutos-v43/` |

Après une modification d'un fichier JS ou CSS, augmenter son paramètre `?v=` là où il est chargé.

### Publier

Un push sur `main` déploie le site sur GitHub Pages (`.github/workflows/pages.yml`). `scripts/build_pages.sh` génère au passage `catalog/home-snapshot.json`, qui permet d'afficher l'accueil sans attendre le catalogue, et une copie du site sous `/v2/`.

### Base de données

La base SQLite complète (50 520 vidéos, voitures, tâches, transcriptions) est publiée avec la release [`data-2026-11-08`](https://github.com/ValerionGG/racelink-academy/releases/tag/data-2026-11-08), car elle dépasse la taille permise dans le dépôt. Les traces de collecte internes en ont été retirées. Schéma : `collector/schema.sql`.

```bash
curl -LO https://github.com/ValerionGG/racelink-academy/releases/download/data-2026-11-08/racelink-catalog.sqlite3.gz
gunzip racelink-catalog.sqlite3.gz
```

Pour régénérer le catalogue public depuis cette base :

```bash
cd collector
python3 scripts/export_static.py --db ../racelink-catalog.sqlite3 --output /tmp/rl-export --base-path /racelink-academy/ --flat
cp /tmp/rl-export/catalog/catalog.json /tmp/rl-export/catalog/catalog.json.gz /tmp/rl-export/catalog/config.json ../site/catalog/
cp /tmp/rl-export/catalog/transcripts/*.json ../site/catalog/transcripts/
cp /tmp/rl-export/social-index.json /tmp/rl-export/export-manifest.json ../site/
cd .. && python3 scripts/report_stats.py
```

Sous Git Bash (Windows), préfixer la commande d'export par `MSYS2_ARG_CONV_EXCL="*"`.

### Documentation

- [`docs/CHIFFRES.md`](docs/CHIFFRES.md) : chiffres détaillés, générés depuis le catalogue
- [`DESIGN.md`](DESIGN.md) : système de design, jetons et règles
- [`PRODUCT.md`](PRODUCT.md) : produit et parcours
- [`docs/design/`](docs/design/) : maquette, audit et captures d'écran

### À savoir

- **Publication automatique** : une automatisation Codex quotidienne pousse aussi des mises à jour du catalogue sur `main`. Faire `git pull --rebase` avant de pousser.
- **Taille du catalogue** : `catalog.json` pèse 77 Mo sur GitHub, dont la limite par fichier est de 100 Mo. Il ralentit aussi le premier chargement : c'est le prochain chantier technique.
- **Vignettes TikTok et Instagram** : leurs URL expirent. Une photo liée au sujet les remplace.

## Pages

[**Atlas automobile · 9 dossiers France 2025**](https://valeriongg.github.io/racelink-academy/vehicules.html)

71 combinaisons finition–moteur sourcées, 21 photographies créditées et trois visites constructeur extérieur/habitacle intégrées. Les vues manquantes, gammes partielles et différences de millésime sont indiquées par voiture. [Détail de la couverture V41](https://github.com/ValerionGG/racelink-academy/blob/main/research/atlas-v41/README.md).

[**Atlas Renault Clio V · France 2025**](https://valeriongg.github.io/racelink-academy/clio-5-2025.html) · [Skill RaceLink Vehicle Showroom](https://github.com/ValerionGG/racelink-academy/blob/main/skills/racelink-vehicle-showroom/SKILL.md)

Photos de la phase 2, visite Renault extérieur/intérieur, projections locales, équipements et 14 combinaisons de finition et de moteur au tarif français du 1er juillet 2025.

[TikTok et Instagram par voiture et par sujet](https://valeriongg.github.io/racelink-academy/formats-courts.html) · [Atelier 3D WikiSpeed SGT01](https://valeriongg.github.io/racelink-academy/3d.html) · [Bibliothèque](https://valeriongg.github.io/racelink-academy/)

[Bilan, sources et contrôles de cette livraison](https://github.com/ValerionGG/racelink-academy/blob/main/research/social3d-v38/README.md) · [Collecte des comptes autorisés](https://github.com/ValerionGG/racelink-academy/blob/main/collector/scripts/CREATOR-API-PAGES.md) · [Skill CAO automobile](https://github.com/ValerionGG/racelink-academy/blob/main/skills/racelink-vehicle-atlas/SKILL.md)

GitHub Pages héberge cette version indépendamment du domaine Focus. Le catalogue conserve ses onze guides et ses références constructeur.
