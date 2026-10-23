# Préparation technique V21 — cinéma

23 octobre 2026. **Préparation seulement : aucune suite V21 exécutée, aucun rendu V21 validé, aucune modification de catalogue.** Source de référence : V20 `workshop-v20`. La nouvelle direction peut remplacer la composition visuelle ; les contrats fonctionnels ci-dessous doivent rester utilisables.

## Contrats à préserver

| Surface | Contrat actuel | Risque pour une nouvelle page d’accueil |
|---|---|---|
| Vues | `#explore-view`, `#paths-view`, `#faq-view`, `#saved-view` sont les quatre `section` directement sous `main`. `changeView()` utilise `main>section`. `#main` reste une cible de focus. | Un wrapper autour des sections ou une nouvelle section directement sous `main` peut rendre le masquage des vues incorrect. Placer les rangées cinéma à l’intérieur de `#explore-view`. |
| Recherche | Une seule `.search-shell`, un seul `#search-form`, `#search` combobox, `#search-suggestions` listbox et `#suggestion-status`. `#home-language`, `#french-videos` et les labels associés sont utilisés sans garde. | Ne pas cloner le formulaire dans un hero ou un bandeau. `mobile-ui.js` déplace le nœud original et le rend à son ancre d’accueil ou à `#results-search-desktop`. Remplacer son parent après initialisation pourrait perdre cette ancre. |
| Titre d’accueil | `.hero h1` est ciblé dans `applyTranslations()` et comme retour du focus dans `mobile-ui.js`. | Conserver ce contrat ou modifier les deux consommateurs et leurs tests ensemble. Le simple changement de classe peut casser le démarrage ou le retour du focus. |
| Raccourcis d’accueil | `.suggestions [data-query="vidange"]`, `[data-query="freinage"]`, `[data-query="sim racing"]`, `.workshop-jump` et `.academy-scene` ont des consommateurs dans l’application et l’identité. | Avant suppression, rechercher tous leurs usages ; plusieurs accès sont non optionnels. Une transformation en lien éditorial doit garder une action précise. |
| Bibliothèque | `.catalog`, `#catalog-heading[tabindex="-1"]`, `.results-back`, `#results-search-desktop`, `#edit-search`, `#edit-search-label`, `.library-controls` et `#video-grid`. `body.results-mode` gouverne la distinction accueil/résultats. | Un nouveau hero à forte spécificité ne doit pas rester visible en mode résultats. Contrôler aussi le retour depuis Enregistrés/Parcours vers la recherche. |
| Filtres | Un seul `#filters`, déplacé dans `#filters-dialog` sur ordinateur comme sur mobile. `#mobile-filters`, `#reset-filters`, `#platform` masqué, `#platform-choices`, `#category-filters`, `#level`, `#duration`, `#content_format`, `#domain`, `#transcript`, `#license` restent requis. | Ne pas reconstruire une seconde copie des champs. Conserver `data-platform-choice`, `data-category`, `aria-pressed` et la restauration du focus après remplacement des facettes. |
| Contexte | `#language` concerne le contenu ; `#ui-language` concerne l’interface. `#format-tabs` et `data-format=all/video/guide` gardent leur sens. Le véhicule et les références d’huile restent des critères précis. | Les commandes home ne doivent pas effacer silencieusement langue, voiture ou référence technique. « Effacer les critères » conserve question, format et tri, contrairement à la réinitialisation complète. |
| Voiture | `#vehicle-disclosure`, `#vehicle-hub`, `#vehicle-trigger-label`, `data-open-vehicle`, `data-close-vehicle`, événement `rl:open-vehicle`. | Le panneau doit rester atteignable depuis toute vue ; sa fermeture rend le focus à `#catalog-heading`. |
| Suggestions | `data-suggestion`, groupes non sélectionnables, flèches, Entrée, Échap ; fermeture via `rl:close-suggestions` et handoff via `rl:search-chosen`. | Aucun résultat ancien ne doit remplacer une requête plus récente. Les mots exacts, modèle, moteur et spécification ne doivent pas disparaître lors d’un choix de sujet. |
| Cartes/lecteurs | `data-video`, `data-guide`, `data-save`, `data-share`, `data-close`, `data-play`, `data-tab` ; `#video-dialog`, `#video-detail`, `#dialog-title`, `#player`, `#detail-panel` et onglets existants. | Les rangées cinéma doivent réutiliser les actions réelles. Pas de bouton imbriqué, lecture automatique, résumé inventé, disponibilité ou validation technique présumée. |
| Guides | `data-guide-section`, `#guide-method`, `#guide-sources`, cibles prérequis/vidéos liées. Références constructeur et méthode générale restent distinctes. | Un traitement visuel commun aux vidéos ne doit pas transformer un guide en média jouable ni masquer les limites de ses notices. |
| État utilisateur | URL `browse/view/track/ui` et tous les paramètres de recherche ; stockage des enregistrés, notes et parcours. | Un retour accueil peut modifier la recherche selon le comportement explicite existant, mais ne doit pas effacer les données enregistrées. |

Repères V20 : `public/app.js` fonctions `syncUrl`, `restoreUrl`, `syncControls`, `applyTranslations`, `goHome`, `changeView`, `renderFacets` ; `public/mobile-ui.js` fonctions `openSearch`, `restoreSearch`, `openFilters` ; `public/discovery-ui.js` création du moteur de suggestions et rendu des sélections. Les numéros de ligne évoluent pendant la refonte : vérifier les noms plutôt que figer un ancien décalage.

## Rangées cinéma et données honnêtes

- `attachRailNavigation()` fournit déjà le défilement natif, des boutons précédent/suivant, le suivi de position, l’observation du redimensionnement et une réduction du mouvement. Son retour est un nettoyage : l’appeler avant de reconstruire une rangée pour éviter de garder plusieurs observateurs.
- `overflow-x` doit rester local à la rangée. Ses contrôles doivent disparaître lorsqu’elle ne déborde pas, sans laisser le focus sur un élément caché. Les longues cartes et titres doivent fonctionner à 320 px et au clavier.
- Les sélections suivent les identités réellement présentes, les dates et les états éditoriaux existants. Aucun succès, popularité, « épisode » ou durée ne doit être déduit du style Netflix/MasterClass.
- Les photos de navigation sont des illustrations créditées. Elles ne sont pas les vignettes originales d’une vidéo ni une preuve du contenu. Préserver les crédits et les liens de licence du registre.
- Réserver la priorité de chargement à l’image principale réellement visible ; charger les autres rangées à la demande du navigateur. Ne pas importer une bibliothèque de carrousel pour répliquer le défilement natif déjà disponible.

## Lanceur préparé

`work/redesign-v21/run-contracts.py` propose `navigation`, `html`, `export`, `search-filters`, `cards`, `detail`, `all` et `summary`. Il exige le marqueur `cinema-v21` dans l’index avant exécution et écrit uniquement ses rapports dans `outputs/focus-academy/research/cinema-v21/`.

Les sources des tests existants sont réutilisées. Pour l’export, seules les constantes de cache `workshop-v20` sont remplacées par `cinema-v21` **en mémoire** ; les adaptations sont consignées. Aucune assertion comportementale n’est supprimée. La base d’export de test est temporaire ; aucun export de production, catalogue ou paquet n’est construit. Les scripts Node redirigent exclusivement leur rapport JSON nommé, afin de préserver les historiques V18–V20.

Commandes à lancer **après le signal de fin de code** depuis l’espace de travail :

```text
python work/redesign-v21/run-contracts.py navigation
python work/redesign-v21/run-contracts.py html
python work/redesign-v21/run-contracts.py export
python work/redesign-v21/run-contracts.py search-filters
python work/redesign-v21/run-contracts.py cards
python work/redesign-v21/run-contracts.py detail
python work/redesign-v21/run-contracts.py summary
```

V20 comptait 17 + 14 + 6 + 13 + 52 + 7 = 109 contrôles. Ce nombre est une référence historique, **pas un résultat V21**. Les stubs ou attentes de texte strictement obsolètes devront être adaptés explicitement après lecture des changements voulus ; aucun test ne doit devenir permissif pour dissimuler une régression.

## Validation après intégration

1. Vérifier modules/imports et un seul formulaire de recherche ; exécuter navigation, HTML/bundle et comportements. Examiner tout nouveau besoin de stub.
2. Contrôler les lecteurs et les cartes, puis l’export temporaire pour `/aide/` et un préfixe Pages. Vérifier le marqueur sur index, CSS et modules modifiés ; le bundle doit être exactement régénéré depuis ses sources.
3. Navigateur : accueil → rangée → fiche → fermeture ; recherche depuis une autre vue ; saisie mobile conservée ; filtres plateforme et langue ; question + voiture ; reset ; guides et sources ; menu et retour du focus.
4. Mesurer 320, 390, 768 et desktop : aucun débordement du document, rangées défilantes volontaires seulement, commandes visibles sans survol, longues sources lisibles. Tester clavier, déplacement réduit et images indisponibles si la session le permet.
5. Distinguer tests DOM, examen des captures, navigateur réel et appareil physique dans le rapport. Ne pas reprendre une preuve V20 comme preuve de la nouvelle composition.

## État de préparation

Seules la syntaxe Python du lanceur et sa sortie `--help` ont été vérifiées. Les suites, l’export de test et le navigateur attendent le signal du parent. Aucune modification frontend, Git, base de production ou publication dans cette mission.
