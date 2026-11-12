# 02 · Symptômes et codes défaut

> Partir de ce qu'on entend, sent ou lit sur le tableau de bord, pas du nom d'une pièce qu'on ne connaît pas.

## Pourquoi

Personne ne cherche « silentbloc de barre stabilisatrice ». On cherche « ça claque à l'avant sur les dos d'âne ». Le moteur de recherche reconnaît déjà des synonymes de tâches (`catalog-worker.js`, table vers la ligne 44, et `inferred_task`), mais seulement des noms de pièces. Le catalogue a 1 114 vidéos de diagnostic (`diagnostics`) et 615 sur les capteurs, sans point d'entrée pour un débutant.

## Expérience

### A. « Qu'est-ce qui se passe ? »

Une entrée sur l'accueil, à côté de la recherche : **« J'ai un symptôme »**.

```
┌────────────────────────────────────────────────────────┐
│ QU'EST-CE QUE TU REMARQUES ?                           │
│ [🔊 Un bruit] [💡 Un voyant] [🫨 Une vibration]       │
│ [👃 Une odeur] [💧 Une fuite] [🚗 Un comportement]     │
├────────────────────────────────────────────────────────┤
│ 🔊 Un bruit… quand ?                                   │
│ (•) En freinant   ( ) En tournant   ( ) Sur les bosses │
│ ( ) Au démarrage  ( ) En roulant, de plus en plus fort │
├────────────────────────────────────────────────────────┤
│ PISTES LES PLUS FRÉQUENTES            ⚠ Freins = sécurité│
│ 1 Plaquettes usées (témoin d'usure)   → fiche · 3 455 │
│ 2 Disques voilés ou usés              → fiche · 2 225 │
│ 3 Étrier grippé                       → fiche ·   457 │
│ Ce sont des pistes, pas un diagnostic. Un doute sur    │
│ les freins : garage, sans attendre.                    │
└────────────────────────────────────────────────────────┘
```

Deux questions au plus, puis des **pistes** qui mènent aux [fiches intervention](01-fiche-intervention.md) et aux vidéos. Le mot « diagnostic » n'est jamais promis.

### B. Code défaut OBD

Champ « Code défaut » (exemple : `P0301`) dans la recherche, et une page `./?code=P0301` :

```
P0301 · Raté d'allumage détecté, cylindre 1
Système : Allumage et préchauffage        Source : OBDex (générique)
Ce que ça veut dire · Causes fréquentes · Ce qu'on peut vérifier soi-même
[Vidéos : bougies d'allumage · 860]  [Lire un diagnostic OBD (guide)]
```

- La recherche reconnaît le motif `^[PCBU][0-9A-F]{4}$`.
- Seuls les codes **génériques** (`P0xxx`, `P2xxx`…) ont une définition. Pour un code constructeur, la page le dit et renvoie au guide « Comprendre un diagnostic OBD ».

### C. Préparer le contrôle technique (France)

Une liste « Avant le contrôle technique » : éclairage, essuie-glaces, pneus, freins, fuites, voyants. Chaque point mène à sa fiche. Il n'existe **pas de jeu ouvert des défaillances** (voir [sources.md](sources.md)) : la liste est éditoriale et s'appuie sur la réglementation publique, sans statistiques inventées.

## Données

`site/symptoms.json`, éditorial, relu :

```json
{
  "version": "1.0.0",
  "families": ["noise", "warning_light", "vibration", "smell", "leak", "behaviour"],
  "symptoms": [{
    "id": "noise_braking",
    "family": "noise",
    "label": {"fr": "Un bruit en freinant", "en": "A noise when braking", "es": "Un ruido al frenar"},
    "words": {"fr": ["grince en freinant", "couine frein", "bruit freinage"], "en": ["squeal when braking"], "es": ["chirrido al frenar"]},
    "leads": [{"task": "brake_pads", "why": {"fr": "Le témoin d'usure frotte sur le disque.", "en": "…", "es": "…"}}],
    "safety": "braking"
  }]
}
```

`site/obd-codes.json` est produit au build à partir d'OBDex, après vérification de sa licence, en ne gardant que les codes génériques (`code`, `description_en`, `system`). Les descriptions françaises et espagnoles sont **traduites et relues** pour les 200 codes les plus courants, puis signalées comme traduction. Le reste reste en anglais, avec une mention.

## Implémentation

| Fichier | Changement |
|---------|------------|
| `site/symptoms.json`, `site/obd-codes.json` | Nouveaux |
| `collector/scripts/build_obd_codes.py` | Télécharge OBDex à une révision figée, filtre et rattache chaque code à un système (P03xx vers `ignition`, etc.) |
| `site/catalog-worker.js` | `interpretQuery()` reconnaît un code défaut et les mots de `symptoms.json` ; routes `/api/symptoms` et `/api/codes/{code}` |
| `site/symptoms-ui.js` | Nouveau : l'assistant en deux questions |
| `site/index.html`, `site/paddock-home.js` | Entrée « J'ai un symptôme » sous la recherche |
| `collector/tests_symptoms.mjs` | La requête « ça grince quand je freine » propose `brake_pads` ; `P0301` renvoie `ignition` |

## Critères d'acceptation

- [ ] 30 symptômes relus au lancement, couvrant les 6 familles.
- [ ] Chaque piste mène à une fiche ou à une recherche filtrée non vide.
- [ ] Les mots « diagnostic certain » ou « c'est forcément » n'apparaissent nulle part.
- [ ] Un code défaut générique affiche sa définition et sa source ; un code inconnu affiche un message utile, sans page vide.
- [ ] Bandeau sécurité pour tout symptôme qui touche freins, direction, airbag, odeur de brûlé, fumée ou liquide de frein.

## Hors périmètre et risques

- Pas de lecture OBD en direct (Bluetooth ELM327) dans cette phase. Web Bluetooth n'existe ni sur Safari ni sur iOS : à étudier plus tard.
- **Risque majeur : rassurer à tort.** Chaque écran rappelle que ce sont des pistes.
