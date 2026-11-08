---
version: paddock-2
name: RaceLink Academy
description: Paddock design. Dark by default, one saturated red for action, display type at large scale, photography first.
---

# RaceLink Academy : design Paddock

L'Academy reprend l'identité de racelink-app.co : noir, rouge d'action, lime pour la progression, or pour les niveaux, ton de paddock.

- **Maquette validée** : [`docs/design/paddock-prototype.html`](docs/design/paddock-prototype.html)
- **Audit et benchmark** : [`docs/design/etude-refonte.html`](docs/design/etude-refonte.html)
- **Captures** : [`docs/design/screens/`](docs/design/screens/)

## Principes

1. **L'Academy d'abord.** Sujets, guides, bibliothèque, parcours et aide sont le cœur. La voiture et la 3D sont un bonus.
2. **Une seule couleur forte.** Le rouge sert l'action et l'état sélectionné. La lime marque la progression, l'or les niveaux.
3. **La typographie porte l'identité.** Titres très larges en capitales, libellés en mono, jamais de grand titre en police de texte.
4. **La photo avant le décor.** Pas de dégradé décoratif ni de panneau vide : une vidéo sans vignette reçoit une photo liée à son sujet.
5. **Le français d'abord**, les autres langues à un clic.

## Jetons

Définis dans `site/paddock-ui.css`. Les composants historiques héritent des jetons `--rl-*`.

| Rôle | Jeton | Sombre | Clair |
|---|---|---|---|
| Fond | `--rl-canvas` | `#070708` | `#ecebe6` |
| Surface | `--rl-surface` | `#111114` | `#ffffff` |
| Surface relevée | `--rl-surface-raised` | `#18181d` | `#f6f5f1` |
| Texte | `--rl-ink` | `#f4f4f6` | `#0e0f12` |
| Texte secondaire | `--rl-muted` | `#a7a9b2` | `#4f5259` |
| Filet | `--rl-line` | `#26262c` | `#d8d6cf` |
| Action | `--rl-action` | `#e8141f` | `#d9141f` |
| Accent texte | `--rl-accent-text` | `#ff5a64` | `#b50f19` |
| Progression | `--pd-lime` | `#b5f23d` | `#4c8a00` |
| Niveau | `--pd-gold` | `#e7b94a` | `#8c650c` |

Le thème sombre est le réglage par défaut (`site/theme.js`). Le choix du visiteur est conservé dans `localStorage`, clé `rl-academy-theme`.

## Typographie

| Usage | Police | Réglage |
|---|---|---|
| Titres | Archivo (`--pd-display`) | graisse 800 à 900, `font-stretch:125%`, capitales |
| Texte | Onest (`--pd-body`) | 400 à 700 |
| Libellés, durées, compteurs | Geist Mono (`--pd-mono`) | 11 px, capitales, `letter-spacing:.14em` à `.16em` |

## Écrans

| Écran | Fichier principal | Éléments |
|---|---|---|
| Accueil | `site/index.html`, `site/paddock-home.js` | bandeau, console de recherche, 8 sujets, guides, sélection, parcours, formats courts, bonus, FAQ |
| Bibliothèque | `site/paddock-pages.css`, `site/app.js` | en-tête et compteur, rangée de sujets, filtres fixes, cartes, « Quelle Clio ? » |
| Fiche vidéo | `site/resource-detail.js` | plein écran, lecteur, panneau fixe, « À regarder ensuite » |
| Fiche guide | `site/guide-ui.js` | photo en tête, plan fixe, étapes numérotées, liste à cocher, notices |
| Parcours | `site/app.js` (`renderPaths`) | tuiles numérotées, secteurs de progression, étapes |
| Aide | `site/app.js` (`renderFaq`) | filtres par catégorie, recherche, questions |
| Pages autonomes | `site/paddock-annex.css`, `site/paddock-chrome.js` | navigation commune, jetons de chaque page redéfinis |

## Règles techniques

`site/app-ui.css` est généré par `python3 scripts/build_ui.py` : couches `legacy`, `product`, puis `paddock` (`paddock-ui.css` et `paddock-pages.css`). Ne pas le modifier à la main.

Trois effets ont bloqué le navigateur et ont été retirés. Ne pas les réintroduire :

- `text-wrap:balance` sur les titres en Archivo très large ;
- `backdrop-filter` sur l'en-tête et la console, au-dessus du bandeau animé ;
- `filter:blur()` de grande taille en arrière-plan de la fiche.

Le mouvement se limite à `transform` et `opacity`, et respecte `prefers-reduced-motion`. Les cibles tactiles font au moins 44 px.

Ne jamais inventer de durée, de chapitre, d'étape ou de compteur : un champ absent de la source n'est pas affiché.
