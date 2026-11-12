# 08 · Télémétrie réelle

> Apprendre à lire une trace de télémétrie avec de vraies données de course, pas des schémas.

## Pourquoi

L'ingénierie compte 2 896 vidéos et la télémétrie est au cœur du parcours « Lire la télémétrie ». Les données F1 historiques sont désormais **gratuites et sans authentification** sur [OpenF1](https://openf1.org/docs) (depuis 2023), et les résultats sur [Jolpica-F1](https://docs.fastf1.dev/api_reference/jolpica.html) (depuis 1950). Aucune plateforme en français n'en fait un outil pédagogique interactif.

## Expérience

### Leçons guidées
Chaque leçon pose une question et la montre sur une vraie trace :

```
LEÇON 3 · OÙ SE GAGNE LE TEMPS ?
Monza 2024, qualifications · Pilote A contre Pilote B, meilleurs tours
┌──────────────────────────────────────────────────────────┐
│ Vitesse ─ A  ┄ B                                          │
│ 340 ┤ ───╮      ╭────────╮     ╭──                         │
│     │    ╰╮    ╭╯        ╰╮   ╭╯                           │
│ 80  ┤     ╰────╯ ①         ╰──╯ ②                          │
│ Frein ▁▁▇▇▁▁▁▁▁▁▁▁▁▁▇▇▁▁▁▁                                 │
│ Gaz   ▇▇▁▁▃▇▇▇▇▇▇▇▇▁▁▃▇▇                                   │
│ Écart ── B perd 0,12 s au freinage ①                      │
└──────────────────────────────────────────────────────────┘
① B freine 15 m plus tôt et repart plus lentement.
Question : à quoi le vois-tu sur la courbe de gaz ? [Réponse]
```

- 8 leçons au lancement : lire la vitesse, le point de freinage, la vitesse minimale en virage, la réaccélération, la comparaison de deux tours, l'usure des pneus sur un relais, l'effet de l'aspiration, la lecture des secteurs.
- Le graphique est **dessiné en SVG maison** (pas de bibliothèque de graphiques), synchronisé : survoler un point montre toutes les courbes au même endroit et, si [07](07-circuits-et-trajectoires.md) existe, la position sur le tracé.
- Chaque leçon finit par une question du [quiz](05-progression.md).

### Bac à sable
Choisir une session (2023 et après), deux pilotes et leurs meilleurs tours, puis comparer. **Données précalculées au build** pour une liste fermée de sessions, pour ne pas solliciter l'API gratuite à chaque visite.

### Sim racing : ses propres données
Un guide « Analyser sa propre télémétrie » présente des outils libres à installer (exemple : [grafana-simracing-telemetry](https://awesome.ecosyste.ms/projects/github.com%2Falexanderzobnin%2Fgrafana-simracing-telemetry) pour ACC, Assetto Corsa et iRacing). Un site web ne peut pas lire la mémoire partagée d'un jeu : pas d'intégration directe. En phase suivante, l'import d'un **CSV exporté** par ces outils pourrait réutiliser le même graphique.

## Données

- **OpenF1** `car_data` (environ 3,7 Hz : vitesse, régime, rapport, gaz, frein, DRS), `laps`, `sessions`. Base `https://api.openf1.org/v1`. Le temps réel est payant et **hors périmètre**. La disponibilité historique de `/location` est à vérifier.
- **Jolpica-F1** : résultats et temps au tour, `https://api.jolpi.ca/ergast/f1`. Mettre en cache et vérifier si une clé est requise.
- Projet **non officiel**, sans lien avec la Formule 1 : le dire en pied de page, sans logo ni marque F1.

Build : `scripts/build_telemetry.mjs` écrit `site/telemetry/{session}-{lap}.json`, rééchantillonné **par distance** (un point tous les 10 m) pour comparer deux tours point à point :

```json
{"session_key": "<session_key OpenF1>", "driver": "<numéro>", "lap": "<tour>", "lap_time_s": "<temps officiel>",
 "source": "OpenF1, données historiques", "fetched_at": "…",
 "by_distance": {"d": [0, 10, 20], "speed": [], "throttle": [], "brake": [], "gear": []}}
```

## Implémentation

| Fichier | Changement |
|---------|------------|
| `scripts/build_telemetry.mjs` | Nouveau : récupération, rééchantillonnage par distance, écart cumulé. Lancé à la main ou par une CI dédiée, pas à chaque publication |
| `site/telemetry/*.json` | Données figées, chacune de taille limitée (moins de 200 Ko) |
| `site/telemetrie.html`, `site/telemetry.js` | Nouvelle page autonome |
| `site/telemetry-lessons.json` | Leçons éditoriales : texte, sessions, repères |
| `tracks.js` (parcours « Lire la télémétrie ») | Les étapes pointent vers les leçons |

## Critères d'acceptation

- [ ] 8 leçons relues, chacune sur une vraie session citée (date, épreuve, séance).
- [ ] Les deux tours comparés sont alignés par distance ; l'écart cumulé est juste à 0,05 s près sur le tour complet, par rapport au temps officiel.
- [ ] Aucun appel à OpenF1 depuis le navigateur du visiteur.
- [ ] La mention « données non officielles » est visible ; aucune marque F1.
- [ ] Graphique lisible au toucher sur 375 px.

## Hors périmètre et risques

- Temps réel (payant), autres championnats sans données ouvertes.
- **Exactitude** : une erreur d'alignement fausserait la leçon. Écrire un test qui compare le temps reconstitué au temps officiel.
