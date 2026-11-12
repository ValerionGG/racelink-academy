# 09 · Socle : un catalogue plus léger

> Une recherche qui répond en moins d'une seconde, même sur un téléphone moyen.

## Pourquoi

Tout le catalogue tient dans un seul `site/catalog/catalog.json` : 77 Mo sur GitHub, dont la limite est de 100 Mo par fichier, et 7,3 Mo compressé. Le Web Worker le télécharge et le prépare entier avant la première recherche hors accueil :
- environ **5 s** de préparation mesurées sous Node sur un PC (`prepareCatalog`) ;
- sur mobile et dans un onglet en arrière-plan, plusieurs dizaines de secondes ont été observées ;
- l'instantané d'accueil (`home-snapshot.json`, 23 réponses) masque le problème sur l'accueil seulement.

Le catalogue grossit chaque jour avec l'automatisation de collecte : le mur des 100 Mo arrivera. C'est le **prérequis** des chantiers 01 à 08, qui ajoutent tous des routes.

## Cible

| Mesure | Aujourd'hui | Cible |
|--------|-------------|-------|
| Première recherche, mobile 4G | dizaines de secondes | < 1,5 s |
| Données téléchargées pour une recherche | 7,3 Mo compressés | < 500 Ko |
| Plus gros fichier du dépôt | 77 Mo | < 25 Mo |

## Options

| Option | Principe | Pour | Contre |
|--------|----------|------|--------|
| A. Index plus fragments | Un index léger (id, titre, langue, catégorie, tâches, véhicules, niveau, durée) découpé par langue, plus les fiches détaillées en fragments de 500 vidéos | Garde le moteur actuel (`searchResources`) presque intact | L'index français fait encore plusieurs Mo |
| B. Index de recherche statique, par exemple [Pagefind](https://pagefind.app) | Index découpé en petits morceaux, chargés à la demande | Conçu pour les sites statiques ; filtres et multilingue | Pagefind indexe des pages HTML : il faudrait générer une page par vidéo ou ruser ; moteur de pertinence à refaire |
| C. SQLite dans le navigateur par requêtes HTTP partielles (sql.js-httpvfs) | La base SQLite existe déjà ; le navigateur ne lit que les pages utiles | Requêtes SQL complètes ; un seul format pour le dev et le site | GitHub Pages et les requêtes partielles sont à valider ; plus complexe |

**Recommandation : A** d'abord, parce que c'est le plus petit changement qui atteint la cible. Prototyper C en parallèle sur une branche : c'est la piste d'avenir si la base dépasse 100 000 vidéos.

## Plan A en détail

```
site/catalog/
  index/fr.json      ← champs de recherche seulement, vidéos en français
  index/en.json …    ← une par langue ; « und » regroupe les inconnues
  index/all.json     ← facettes et compteurs globaux
  items/000.json …   ← fiches complètes, 500 par fichier, par hachage stable de l'id
  config.json        ← ajoute index_sha256 et le nombre de fragments
```

- Le worker charge `index/{langue}.json` au démarrage, puis les autres langues seulement si le filtre « Toutes » est choisi.
- La fiche d'une vidéo charge son fragment `items/NNN.json` à l'ouverture.
- Les estimations (niveau, etc.) sont **calculées au build** et non plus dans `prepareCatalog`, ce qui supprime l'essentiel des 5 s.
- `catalog.json` reste produit pour le zip du développeur et les exports, mais n'est plus servi au site : le sortir de `site/`.

## Implémentation

| Fichier | Changement |
|---------|------------|
| `collector/scripts/export_static.py` | Écrit l'index par langue et les fragments ; applique les estimations |
| `site/catalog-worker.js` | Chargement par langue et par fragment ; `prepareCatalog` réduit à l'indexation |
| `site/catalog-client.js` | Transmet la langue demandée au worker |
| `scripts/build_home_snapshot.mjs` | Lit le nouvel index |
| `.gitignore`, `README.md` | Nouveau découpage, et `catalog.json` hors de `site/` |
| `collector/tests_paddock_search.mjs` | Mêmes résultats avant et après sur 50 requêtes de référence |

## Critères d'acceptation

- [ ] Les 50 requêtes de référence (vidange, plaquettes, Clio, sim racing…) renvoient le même total et les mêmes 20 premiers résultats qu'avant.
- [ ] Première recherche en français en moins de 1,5 s sur un Android moyen, profil 4G de Chrome DevTools.
- [ ] Aucun fichier de plus de 25 Mo dans le dépôt.
- [ ] La page Comprendre et l'instantané d'accueil fonctionnent sans changement visible.

## Risques

- La pertinence change si des champs disparaissent de l'index : garder tous ceux qu'utilise `searchResources`.
- L'automatisation Codex quotidienne écrit dans `site/catalog/` : adapter son script **avant** de livrer, sinon elle recrée l'ancien fichier.
