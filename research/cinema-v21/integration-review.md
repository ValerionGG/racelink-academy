# Revue d’intégration V21

Revue du 23 octobre 2026, sur les sources marquées `cinema-v21`. Aucun fichier applicatif, bundle, catalogue ou dépôt Git n’a été modifié par cette validation.

## Résultat reproductible

Commande depuis la racine du workspace :

```powershell
python work/redesign-v21/run-contracts.py all
```

Les **109 contrôles passent** : navigation 17, HTML/bundle 14, export sur fixture 6, recherche/filtres 13, cartes 52, lecteur vidéo 7. Les rapports sont dans ce dossier, avec leurs empreintes et leur portée. Après la correction CSS décrite ci-dessous, les suites navigation (17) et HTML/bundle (14) ont été relancées avec succès.

Le runner adapte uniquement les attentes de version et un contrat de texte devenu obsolète : les huit clés `data-product-text` de V20 deviennent les sept clés exactes de V21. Le message d’accueil appartient désormais au dictionnaire `data-cinema-copy`. Aucun comportement de navigation ou de filtrage n’a été supprimé des tests. Les rapports des anciennes versions sont conservés ; une première écriture du test de cartes dans le dossier V20 a été restaurée à l’identique depuis l’archive livrée, puis la redirection asynchrone des rapports a été corrigée dans le runner V21.

## Défaut trouvé et corrigé par l’intégration

La règle initiale `.results-mode .hero` avait la même spécificité que `.hero.wrap` dans la media query mobile, placée ensuite. Le `display:block` mobile pouvait donc réafficher le grand visuel au-dessus des résultats. La source courante utilise maintenant `.results-mode .hero.wrap` dans `public/product-ui.css`, ce qui l’emporte sur la règle mobile. Cette constatation est une analyse de cascade CSS, pas un contrôle visuel dans un navigateur.

## Contrats vérifiés en lecture seule

- `app.js` crée `cinemaHome` avant l’exécution asynchrone du rappel `onPicksChange`. Le chargement de découverte initialise les sélections RaceLink, puis l’accueil utilise ces mêmes données ; aucun accès prématuré à la constante n’a été constaté.
- `cinemaHome.load()` utilise les endpoints et registres existants. L’ancienne découverte reste disponible si le nouvel accueil ne devient pas prêt ; les résultats masquent le nouvel accueil.
- La langue d’interface et la langue du contenu demeurent distinctes. Les guides français ne sont pas présentés comme traduits ; les sélections vidéo respectent la langue de contenu choisie et leurs dates d’activation.
- Le formulaire et le panneau de filtres restent uniques. Le déplacement du formulaire dans `.home-finder` conserve l’ancre utilisée par `mobile-ui.js`, ainsi que la cible `#results-search-desktop`.
- Les quatre vues principales, les dialogues natifs, leurs cibles de focus et les attributs de navigation déléguée restent présents. Le lien du grand visuel ouvre bien le guide existant `guide-oil-change`.
- Dans `cinema-home.js`, les titres, auteurs et explications sont échappés ; les images locales sont limitées à `./assets/`, les liens externes à HTTPS, les crédits restent séparés de la sélection éditoriale. Les dates invalides, futures ou expirées excluent les sélections. Aucun défaut concret supplémentaire n’a été trouvé dans cette revue.

## Limites

Les contrôles exécutés utilisent des doubles DOM, des assertions de structure et un export sur base temporaire de test. Ils ne prouvent pas le rendu, le contraste de chaque état, les gestes tactiles, la lecture par technologie d’assistance ou le comportement sur appareil physique. La validation visuelle et les scénarios dans le navigateur restent à réaliser par l’intégration principale. Les 20 contrôles du module d’accueil fournis séparément par son auteur ne sont pas inclus dans le total de 109.
