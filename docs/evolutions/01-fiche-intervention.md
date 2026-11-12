# 01 · Fiche intervention

> Savoir, avant d'ouvrir la vidéo, si l'intervention est à sa portée.

## Pourquoi

Le catalogue classe 31 343 vidéos sur 40 interventions (`automotive.tasks`), mais la fiche vidéo ne dit rien de l'intervention elle-même : ni les outils, ni les risques, ni la durée habituelle. L'utilisateur le découvre au milieu de la vidéo, voiture sur cric.

[iFixit](https://www.ifixit.com/Info/Licensing) a imposé un format que tout le monde comprend : difficulté, durée, outils, pièces, puis les étapes. On reprend ce format, pas son contenu (licence CC BY-NC-SA, voir [sources.md](sources.md)).

## Expérience

Une **fiche intervention** par tâche (exemple : « Plaquettes de frein »), accessible :
- depuis chaque fiche vidéo dont la tâche est connue (bloc « Avant de commencer ») ;
- depuis la page [Comprendre ta voiture](../../site/comprendre.html), en cliquant une intervention ;
- par URL : `./?intervention=brake_pads`.

```
┌──────────────────────────────────────────────────────────────┐
│ FREINAGE · INTERVENTION                                      │
│ Remplacer les plaquettes de frein                            │
│ ▂▄▆ Intermédiaire   ⏱ 45 à 90 min   🔧 6 outils   ⚠ Sécurité │
├───────────────────────────────┬──────────────────────────────┤
│ AVANT DE COMMENCER            │ ⚠ ORGANE DE SÉCURITÉ         │
│ ☐ Cric + chandelles           │ Freins : en cas de doute,    │
│ ☐ Clé dynamométrique          │ fais contrôler par un pro.   │
│ ☐ Repousse-piston             │ Ne jamais travailler sous    │
│ ☐ Clé à douille 13 à 19       │ une voiture tenue par le     │
│ PIÈCES                        │ seul cric.                   │
│ · Jeu de plaquettes (essieu)  │                              │
│ · Nettoyant frein             │ Ta notice : couples de       │
│                               │ serrage et référence.  ↗     │
├───────────────────────────────┴──────────────────────────────┤
│ LES MEILLEURES VIDÉOS · 1 017 en français      [Ma voiture ▾]│
│ [carte] [carte] [carte] [carte]                              │
│ ÉTAPES TYPES  1 Desserrer  2 Lever  3 Déposer l'étrier …     │
└──────────────────────────────────────────────────────────────┘
```

- La **durée** est une fourchette éditoriale, affichée « indicative ». Elle n'est jamais présentée comme mesurée.
- Les **outils** sont une liste à cocher, gardée dans le navigateur pour cette intervention.
- Le bloc **Sécurité** est obligatoire pour les systèmes `braking`, `steering`, `suspension`, ainsi que pour les airbags, la haute tension et le levage. Il n'est jamais repliable.
- **Véhicule électrique ou hybride** (`fuel_type` = `electric` ou `hybrid`) : bandeau haute tension, qui renvoie vers un professionnel habilité. Pour les secours, mentionner l'application Euro Rescue, en lien seulement.
- Les **étapes types** sont un résumé générique en 4 à 8 lignes, rédigé par RaceLink. Elles servent aussi de squelette au [mode atelier](04-mode-atelier.md).

## Données

Nouveau fichier éditorial `site/task-sheets.json`, une entrée par tâche de `automotive-taxonomy.json` :

```json
{
  "version": "1.0.0",
  "tasks": {
    "brake_pads": {
      "difficulty": "intermediate",
      "duration_min": [45, 90],
      "safety": ["braking", "lifting"],
      "tools": [{"fr": "Cric et chandelles", "en": "Jack and axle stands", "es": "Gato y borriquetas"}],
      "parts": [{"fr": "Jeu de plaquettes (par essieu)", "en": "Pad set (per axle)", "es": "Juego de pastillas (por eje)"}],
      "steps": [{"fr": "Desserrer les roues au sol", "en": "Loosen the wheels on the ground", "es": "Aflojar las ruedas en el suelo"}],
      "reviewed_by": "RaceLink", "reviewed_at": "2026-11-20"
    }
  },
  "safety": {
    "braking": {"fr": "Organe de sécurité. En cas de doute, fais contrôler par un professionnel.", "en": "…", "es": "…"},
    "lifting": {"fr": "Ne jamais travailler sous une voiture tenue par le seul cric : utilise des chandelles.", "en": "…", "es": "…"},
    "high_voltage": {"fr": "Circuit haute tension : intervention réservée à un professionnel habilité.", "en": "…", "es": "…"}
  }
}
```

- `difficulty` reprend les niveaux du site. Il **remplace** la table `taskLevels` de `catalog-worker.js`, pour que la carte et la fiche ne se contredisent jamais.
- Tant qu'une fiche n'a pas `reviewed_at`, elle ne s'affiche pas. Mieux vaut pas de fiche qu'une fiche fausse.
- Rédaction : commencer par les 10 tâches les plus fournies (`brake_pads` 3 455 vidéos, `shock_absorbers` 3 170, `brake_discs` 2 225, `oil_change` 2 006, `air_filter` 1 930, `belts` 1 576, `cabin_filter` 1 531, `oil_filter` 1 530, `stabilizer_links` 1 415, `wheel_bearing` 1 287).

## Implémentation

| Fichier | Changement |
|---------|------------|
| `site/task-sheets.json` | Nouveau, éditorial |
| `site/catalog-worker.js` | `estimateLevel()` lit `difficulty` dans les fiches, chargées à l'init comme `discovery-catalog.json` ; nouvelle route `/api/interventions/{task}` qui renvoie la fiche, le total de vidéos et les 8 meilleures |
| `site/intervention.js` | Nouveau module de rendu de la fiche, sur le modèle de `guide-ui.js` |
| `site/resource-detail.js` | Bloc « Avant de commencer » (difficulté, durée, 3 premiers outils, sécurité) avec un lien vers la fiche |
| `site/comprendre.js` | Les interventions du panneau mènent à la fiche, plus à la recherche brute |
| `scripts/build_home_snapshot.mjs` | Pré-calcule les fiches dans l'instantané pour un affichage immédiat |
| `collector/tests_paddock_search.mjs` | Test : la difficulté de la fiche fixe le niveau estimé |

## Critères d'acceptation

- [ ] Les 10 tâches prioritaires ont une fiche relue, en fr, en et es.
- [ ] Une vidéo de tâche connue affiche « Avant de commencer » sur sa fiche.
- [ ] Le niveau affiché sur la carte et dans la fiche est le même pour une même tâche.
- [ ] Le bloc sécurité est visible sans clic pour freinage, direction, suspension, levage et haute tension.
- [ ] La durée porte la mention « indicative ».
- [ ] La liste d'outils cochée est retrouvée après rechargement de la page.
- [ ] Navigable au clavier ; cases d'au moins 44 px.

## Hors périmètre et risques

- **Couples de serrage et références de pièces : jamais génériques.** Ils dépendent du véhicule. On renvoie vers la notice, que l'atlas propose déjà pour plusieurs modèles.
- **Responsabilité.** La fiche n'est pas une procédure constructeur ; une mention le dit en pied de fiche.
