# Validation de l’identité RaceLink — 23 octobre 2026

## Version et périmètre

Code final `f39bfee` (brand-v14c), publié sur GitHub Pages. La première exécution a échoué dans le service Deploy (« try again later »). Sa relance a rencontré deux artefacts « github-pages » ; une nouvelle exécution, 39931846704, a réussi sans changement du code. Le manifeste conserve cette conclusion finale. Catalogue identique : 36 901 vidéos, 11 guides ; aucune nouvelle vidéo ajoutée.

## Contrôles exécutés

- 6 tests d’export statique, 14 contrats HTML/imports/styles : réussis.
- 16 scénarios de navigation dans un DOM simulé : réussis ; voir `navigation-checks.json`. Ils ne remplacent pas un navigateur.
- 6 contrôles des sélections éditoriales et 7 contrôles des champs sociaux : réussis.
- Syntaxe de app.js, guide-ui.js et guide-art.js vérifiée ; les modules mobile/identity/discovery avaient déjà été vérifiés lors de la refonte précédente.
- 10 fichiers HTTP 200 comparés aux fichiers du dépôt après normalisation LF/CRLF. Catalogue gzip décompressé : SHA-256 identique au catalogue public précédent, voir `public-assets-check.json`.

## Observations réelles dans le navigateur intégré

Accueil desktop à 1280 × 720 et aperçus dans un iframe public de 320, 390, 430 et 768 px. Les largeurs utiles sont respectivement 305, 375, 415 et 753 px à cause de la barre de défilement. La largeur défilable égale la largeur utile sur ces accueils. Desktop : 1265 px utiles et défilables. Aucun téléphone physique testé.

Sur v14 : la liste affiche 11 couvertures distinctes, un guide carburant s’ouvre avec ses sources, puis sa fermeture restaure le focus sur la couverture. Le hero est masqué en mode résultats. Sur mobile, la langue française puis « vidange Clio 3 » produisent deux suggestions vidéo et deux résultats ; Entrée ferme le dialogue et rend le focus au bouton de recherche. Le filtre YouTube garde la requête et le français, puis revient au titre du catalogue.

Sur v14b : contrôle visuel de l’accueil et mesures de débordement aux quatre largeurs ; le bloc d’accueil à 390 px passe de 464,6 à 348,4 px. La correction finale v14c conserve les langues sur une ligne pleine à 320 px, avec libellé visible, sans raccourci français redondant. La capture 320 finale et le marqueur de version sont contrôlés après publication.

Les captures `brand-desktop.png`, `brand-mobile.png`, `brand-mobile-320.png`, `brand-mobile-430.png`, `brand-tablet.png` et `brand-guides.png` sont de vraies captures du site public. Le rapport `browser-checks.json` distingue les commits observés.

## Limites

Pas d’audit WCAG exhaustif, test de lecteur d’écran, test sur appareil physique ou mesure de performance réseau revendiqué. Le mouvement réduit est prévu dans le CSS et vérifié statiquement ; son émulation navigateur n’a pas été testée. Les photos de cours Focus servent aux entrées éditoriales ; les miniatures des vidéos restent celles de leurs sources.

Le localhost a été refusé par l’outil navigateur et n’a pas été retenté. La vérification a utilisé le site public autorisé. Pinterest a été recherché, mais ses pins retenus n’étaient pas inspectables ; MotionSite est documenté sur son index officiel sans prétendre avoir observé ses animations. RaceLink officiel et une référence Dribbble ont réellement été inspectés.
