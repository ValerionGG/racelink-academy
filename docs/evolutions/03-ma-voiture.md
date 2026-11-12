# 03 · Ma voiture

> Une page qui ne parle que de ta voiture : ses rappels, son entretien, ses tutos.

## Pourquoi

« Mon véhicule » existe déjà : on mémorise marque, modèle, génération et moteur (`automotive-ui.js`, bouton « Mémoriser ce véhicule »). Mais cela ne sert qu'à filtrer. Il manque ce qui fait revenir : un rappel constructeur, une vidange qui approche, l'historique de ce qu'on a fait.

## Expérience

```
┌──────────────────────────────────────────────────────────────┐
│ MA VOITURE                                       [Modifier]  │
│ Renault Clio V · 1.0 TCe 90 · 2021                            │
│ 42 tutos pour ce modèle · 3 guides · notice ↗                │
├──────────────────────────────┬───────────────────────────────┤
│ ⚠ RAPPELS CONSTRUCTEUR       │ CARNET D'ENTRETIEN            │
│ 1 rappel publié qui peut     │ 12/09/2026 · 61 200 km        │
│ concerner ce modèle.         │   Vidange + filtre à huile    │
│ « Défaut de… » · 03/2026 ↗   │ 02/04/2026 · 55 900 km        │
│ À confirmer avec ton VIN     │   Plaquettes avant            │
│ auprès du constructeur.      │ [+ Ajouter une intervention]  │
│ Source : RappelConso         │                               │
├──────────────────────────────┴───────────────────────────────┤
│ À SURVEILLER (d'après TES intervalles)                       │
│ Vidange : prochaine vers 76 200 km (intervalle saisi 15 000) │
├──────────────────────────────────────────────────────────────┤
│ LES TUTOS DE TA VOITURE   [Freinage] [Entretien] [Électricité]│
└──────────────────────────────────────────────────────────────┘
```

### Rappels constructeur
- **France** : [RappelConso V2](https://www.data.gouv.fr/datasets/rappelconso-v2-rappels-de-produits/), catégorie « Automobiles, motos, scooters ». La correspondance porte sur la marque et le modèle, en texte. Elle est donc **approximative** : l'écran dit « peut concerner » et renvoie au constructeur avec le VIN.
- **Modèles vendus aux États-Unis** : [NHTSA Recalls](https://www.nhtsa.gov/node/102181) par marque, modèle et année, en option.
- Récupération **au build**, chaque jour avec la CI, dans `site/catalog/recalls.json`. Aucun appel externe depuis le navigateur.

### Carnet d'entretien
- Entrées saisies par l'utilisateur : date, kilométrage, intervention (liste des tâches), note. Stockage local, **export et import JSON**.
- « À surveiller » ne calcule qu'à partir d'**intervalles saisis par l'utilisateur**, idéalement recopiés de sa notice. Aucun intervalle constructeur n'est inventé.
- Chaque ligne du carnet renvoie à la fiche intervention et aux vidéos de son modèle.

### Identité de la voiture
- Photo libre du modèle via **Wikidata et Wikimedia Commons**, avec l'auteur et la licence affichés. Repli : le visuel actuel par sujet.
- Consommation et CO₂ pour les modèles récents via **ADEME Car Labelling**, quand la correspondance est sûre.
- **VIN** : facultatif. Il sert à aider la vérification d'un rappel. Décodage local du code constructeur (WMI, trois premiers caractères) et de l'année (10ᵉ caractère). Le VIN ne quitte jamais le navigateur.

### Plusieurs voitures
Jusqu'à 5 véhicules, pour un foyer, une voiture de piste ou une moto, puisque les disciplines moto, karting et drift existent maintenant.

## Données

```json
// site/catalog/recalls.json (build)
{"generated_at": "…", "source": "RappelConso V2 (DGCCRF), Licence Ouverte 2.0", "recalls": [
  {"id": "…", "make": "Renault", "model_text": "Clio", "date": "2026-03-…", "title": "…", "risk": "…", "url": "…"}
]}

// localStorage « rl-garage » (navigateur, exportable)
{"version": 1, "cars": [{"id": "c1", "make": "Renault", "model": "Clio", "generation": "V", "engine": "1.0 TCe 90", "year": 2021,
  "intervals": {"oil_change": {"km": 15000, "months": 12}},
  "log": [{"date": "2026-09-12", "km": 61200, "task": "oil_change", "note": ""}]}]}
```

## Implémentation

| Fichier | Changement |
|---------|------------|
| `collector/scripts/fetch_recalls.py` | Nouveau : RappelConso (et NHTSA en option), avec normalisation des marques sur la liste du catalogue |
| `.github/workflows/pages.yml`, `scripts/build_pages.sh` | Étape de récupération ; si la source tombe, garder le dernier fichier sans bloquer la publication |
| `site/garage.js`, `site/garage.html` ou vue `./?view=garage` | Nouveau |
| `site/automotive-ui.js` | Le véhicule mémorisé devient le premier véhicule du garage (migration de la clé existante) |
| `scripts/build_car_photos.mjs` | Nouveau : requête SPARQL sur les modèles présents dans le catalogue ; licence de chaque photo via `imageinfo` ; écrit `site/catalog/car-photos.json` |

## Critères d'acceptation

- [ ] Un rappel ne s'affiche jamais sans sa date, sa source et le lien officiel.
- [ ] La formulation est toujours « peut concerner », avec l'invitation à vérifier par le VIN.
- [ ] Le carnet survit au rechargement ; l'export puis l'import restaurent les mêmes données.
- [ ] Aucun intervalle d'entretien affiché qui n'ait été saisi par l'utilisateur.
- [ ] Toute photo affiche son auteur et sa licence.
- [ ] Le VIN n'apparaît dans aucune requête réseau (à vérifier dans l'onglet Réseau).

## Hors périmètre et risques

- **Plaque d'immatriculation : non.** Le fichier SIV n'est pas ouvert.
- **Logos de marques** : décision produit en attente (marques déposées). Sans décision, on garde le nom en texte.
- Correspondance de modèle fragile (« Clio » contre « CLIO V Société ») : écrire des tests sur des cas réels.
