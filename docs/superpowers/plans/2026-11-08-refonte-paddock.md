# Refonte Paddock de RaceLink Academy

Maquette validée : https://claude.ai/artifact/NFX3Pp9wGe9XfF67P3jYcq (version 2).

**But.** Donner à l'Academy l'identité RaceLink et un parcours clair, sans perdre une seule fonction. L'Academy reste le cœur ; la voiture et la 3D sont un bonus.

**Architecture.** Le JavaScript, les identifiants du DOM et le catalogue restent en place. Une couche CSS `paddock` s'ajoute après `product` dans `app-ui.css`, redéfinit les jetons `--rl-*` et restyle les composants. Un module `paddock-home.js` rend les nouvelles sections de l'accueil à partir des données réelles.

**Travail isolé.** Branche `refonte-paddock` dans son propre worktree : l'automatisation Codex publie `main` depuis un autre dossier. Rien ne part en ligne sans accord.

## Fonctions à conserver

Recherche et suggestions, langue du contenu, filtres (sujet, plateforme, type, niveau, durée, transcription, licence), critères supprimables, Mon véhicule, 11 guides, sélection « Proposé par RaceLink » et « Pourquoi ce choix ? », fiche (Détails, Transcription, Mes notes, Source, Enregistrer, Copier le lien), parcours, Enregistrés, Aide & FAQ, Focus Masterclass, langues FR/EN/ES, clair/sombre, atlas, Clio, atelier 3D, crédits, méthode.

## Tâches

1. **Socle** : `site/paddock-ui.css`, couche dans `scripts/build_ui.py`, jetons clair/sombre, polices Archivo et Geist Mono, sombre par défaut (`site/theme.js`), navigation haute, plus de barre latérale.
2. **Accueil** (`site/index.html`, `site/paddock-home.js`, `site/cinema-home.js`) : bandeau « Du garage à la piste », console de recherche, 8 sujets avec comptes réels (`stats.facets.category`), 11 guides, sélection, rail 9:16, parcours, bonus véhicule/atlas/3D, aide.
3. **Recherche** (`site/catalog-worker.js`, `site/app.js`) : guides remontés quand la voiture est déduite de la requête, facette génération (« Quelle Clio ? »), doublons fusionnés, français par défaut à l'arrivée, sujets à 0 masqués.
4. **Fiche** : plus de panneau vide, hiérarchie Paddock. Chapitres et étapes seulement si la source les fournit : rien n'est inventé.
5. **Annexes** : formats courts en cartes 9:16, atlas, Clio, 3D sous le même habillage ; l'atlas transmet génération et moteur à la recherche.
6. **Contenu** : lot de nouvelles vidéos via le collecteur, en parallèle, limité à `collector/` et `site/catalog/`.

## Vérification

`node --test` sur la recherche, tests existants `collector/tests_search_*.mjs`, puis contrôle dans le navigateur : ordinateur et 390 px, clair et sombre, parcours accueil → recherche → fiche → enregistrer → parcours → aide → atlas → formats courts.

## Limites connues

Pas de recherche par plaque (API payante). Vignettes TikTok et Instagram absentes pour une partie du catalogue : une affiche par sujet les remplace.
