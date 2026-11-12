# 07 · Circuits et trajectoires

> Voir, virage par virage, où freiner, où tourner et où accélérer, puis regarder les pilotes le faire.

## Pourquoi

Le pilotage compte 2 235 vidéos et le sim racing 3 477, mais une trajectoire s'explique mal en vidéo seule. Un tracé de circuit interactif, avec la trajectoire idéale et les zones de freinage, est l'outil pédagogique qui manque partout, et RaceLink peut le proposer gratuitement.

## Expérience

Une page **Circuits** (`./circuits.html`, rangée dans le menu Pilotage), puis une page par circuit (`./circuits.html?c=spa`).

```
┌─────────────────────────────────────────────────────────────┐
│ SPA-FRANCORCHAMPS · 7,0 km · 20 virages                      │
│ ┌──────────────────────────────────┐ VIRAGE 1 · LA SOURCE   │
│ │      ╭──╮                         │ Épingle droite, lente. │
│ │  ╭───╯  ╰──── ⓵ ●freinage        │ ● Freinage : fort,     │
│ │  │          ╲   ◆corde           │   en ligne droite      │
│ │  │           ╲  ▲réaccélération  │ ◆ Corde tardive pour   │
│ │  ╰────────────╯                   │   sortir vite vers     │
│ │ trajectoire idéale ━  bord ┄      │   l'Eau Rouge          │
│ └──────────────────────────────────┘ [◀ V20]  [V2 ▶]        │
│ [Afficher la largeur] [Afficher la courbure]                 │
├─────────────────────────────────────────────────────────────┤
│ LES VIDÉOS DE CE CIRCUIT   Pilotage 34 · Sim racing 112      │
└─────────────────────────────────────────────────────────────┘
```

- Le tracé est un **SVG** dessiné à partir de la ligne médiane et des largeurs ; la trajectoire idéale est une deuxième courbe.
- Les **virages** sont détectés automatiquement là où la courbure de la trajectoire dépasse un seuil, puis **nommés et commentés éditorialement**. Pas de nom de virage tant qu'il n'est pas relu.
- Les zones « freinage », « corde » et « réaccélération » sont **dérivées de la courbure** et présentées comme indicatives : la vraie trajectoire dépend de la voiture.
- Survoler la trajectoire montre la courbure ; un clic sur un virage le centre et ouvre son commentaire.
- Les vidéos du circuit viennent du catalogue (recherche par nom de circuit dans le titre). Pour un passage précis, `start=` lance la vidéo au bon virage quand un chapitre le permet.

**Lien avec [08 · Télémétrie](08-telemetrie.md)** : sur les circuits de F1 couverts par OpenF1, superposer la vitesse réelle d'un tour rapide le long du tracé.

## Données

[TUMFTM racetrack-database](https://gh.hhj520.top/TUMFTM/racetrack-database) : plus de 20 circuits (F1, DTM), en CSV, avec ligne médiane `x, y`, largeurs gauche et droite, et trajectoire calculée par optimisation de courbure minimale. **Licence LGPL-3.0 selon un indexeur tiers : lire le fichier `LICENSE` avant tout.** Si la licence couvre les données, elle impose de garder la mention et de redistribuer les fichiers modifiés sous la même licence.

Build : `scripts/build_tracks.mjs` convertit les CSV en `site/tracks/{id}.json` simplifiés (exemple : un point tous les 5 m), avec :

```json
{"id": "spa", "name": "Spa-Francorchamps", "length_m": 7004,
 "centerline": [[x, y, wl, wr]], "raceline": [[x, y]],
 "corners": [{"index": 1, "at_m": 412, "name": null, "notes": null, "direction": "right"}],
 "source": "TUMFTM racetrack-database (LGPL-3.0)", "source_revision": "<commit>"}
```

`name` et `notes` restent `null` tant qu'ils ne sont pas relus. Un fichier éditorial `site/tracks/notes.json` les complète.

## Implémentation

| Fichier | Changement |
|---------|------------|
| `scripts/build_tracks.mjs` | Nouveau : conversion, simplification, détection des virages |
| `site/tracks/*.json`, `site/tracks/notes.json` | Données |
| `site/circuits.html`, `site/circuits.js` | Nouvelle page autonome, habillée par `paddock-annex.css` et `paddock-chrome.js`, comme `comprendre.html` |
| `site/paddock-chrome.js` | Entrée de menu |
| `docs/evolutions/sources.md` | Licence confirmée et révision figée |

## Critères d'acceptation

- [ ] 5 circuits au lancement (exemple : Spa, Monza, Silverstone, Barcelone, Nürburgring), commentés virage par virage.
- [ ] Le tracé reste lisible sur un téléphone de 375 px : zoom et déplacement au doigt, sans défilement horizontal de la page.
- [ ] Les zones de freinage et la corde portent la mention « indicatif ».
- [ ] Source, licence et révision visibles en pied de page.
- [ ] Navigation de virage en virage au clavier.

## Hors périmètre et risques

- Pas de simulation de temps au tour dans cette phase. TUMFTM publie aussi `laptime-simulation`, à étudier pour plus tard.
- **Risque de licence** : sans confirmation, ne pas publier les données. Dessiner soi-même les tracés n'est pas une option sérieuse.
