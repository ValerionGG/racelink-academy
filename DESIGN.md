---
version: alpha
name: RaceLink Academy
description: V30 library workspace, photographic content, light and dark themes.
---

# RaceLink Academy — Design V30

## Ajustements de recherche V34

La recherche commence par la question réellement saisie. Les suggestions de reformulation explicites présentent une expression du catalogue, une courte raison et un compte calculé dans le contexte des critères conservés. Aucun changement silencieux de véhicule, plateforme ou langue. Les propositions sont séparées des résultats réellement trouvés et des ressources pouvant être ouvertes directement.

Le résumé des critères comprend maintenant la langue et le format ; chaque bouton porte un libellé de suppression explicite. Les contrôles de langue occupent une ligne complète sur mobile et le français reste visible. Le panneau mobile/tablette place la langue en premier, distingue sujet et plateforme, et dispose d’actions Annuler/Appliquer persistantes. Une modification du brouillon affiche son nombre de critères, pas le nombre de résultats de la recherche précédente.

`public/search-workspace.css` contient ces composants et adaptations, avec les jetons `--rl-*` existants ; `scripts/build_ui.py` l’intègre au bundle. Le cadrage photographique V30 reste intact. Boutons de recherche et de filtres : cibles minimales de 44 px, sélecteurs mobiles de 48 px, pied du panneau tenant compte de la zone sûre. Les règles ont été relues à 320–430 px et pour la transition tablette 761–1000 px ; cela ne constitue pas une inspection du rendu.

Références : [Baymard, critères appliqués](https://baymard.com/research-articles/how-to-design-applied-filters), [Baymard, suggestions](https://baymard.com/research-articles/autocomplete-design), [Udemy, recherche et filtres](https://support.udemy.com/hc/en-us/sections/206458408-Purchasing-a-course), [Coursera, langue d’interface distincte du contenu](https://www.coursera.support/s/article/learner-000001029?language=en_US). Aucun asset de ces plateformes n’a été copié. Skills lus : Impeccable (registre produit) et Interface Design.

Validation V34 : 12 contrats UI de récupération/critères, 17 filtres, 10 interactions de recherche/Échap et 17 de navigation, soit 56 contrôles. Les tests utilisent des modules réels, des doubles DOM ciblés et certains gestionnaires de l’application extraits sans modification. Ils ne couvrent pas le bootstrap complet, le rendu CSS, le clavier tactile ou un lecteur d’écran. Le navigateur n’étant pas disponible dans la session, aucune capture V34 ni validation visuelle mobile n’est annoncée ; les preuves antérieures restent datées de leur propre version.

Une bibliothèque à utiliser au quotidien : recherche au premier écran, navigation persistante sur ordinateur et grandes photographies. Le rouge sert les actions et les états sélectionnés. Les modes clair et sombre couvrent les mêmes fonctions.

## Structure

L’accueil commence par une question et le champ de recherche. Une photographie ouvre un guide réel ; le panneau adjacent mène au choix du véhicule. Les rangées montrent des gestes du quotidien, des univers et des sélections éditoriales documentées. Aucun chiffre de progression, popularité ou personnalisation fictif.

Sur ordinateur, un rail gauche contient les quatre destinations principales. La recherche affiche ses filtres à côté de la grille lorsque la largeur le permet. Les groupes sont Sujet, Plateforme, Type/niveau/durée, Texte et droits ; le format et la langue restent visibles au-dessus. Sur mobile, les critères du panneau sont un brouillon : fermer annule, appliquer lance une recherche. Aucun compteur n’est présenté comme le total d’un brouillon non exécuté.

## Cartes et lecture

Les cartes vidéo ont une photographie 16:9, un seul bouton photo+titre, la source, la langue et la sauvegarde. Les guides suivent la même hiérarchie avec un accès aux références constructeur. Les extraits longs, métadonnées et preuves se lisent dans la fiche. La vidéo précède son titre dans le lecteur, avec les détails à droite sur grand écran et dans un flux unique sur mobile. Les références de guide gardent leur portée et leurs limites.

## Système

Onest porte le texte et les titres, Orbitron reste limité à la signature. `product-ui.css` conserve les rôles sémantiques `--rl-*` et les composants existants ; `studio-ui.css` définit la nouvelle structure, `resource-ui.css` les cartes et lecteurs vidéo. `scripts/build_ui.py` construit l’unique entrée `app-ui.css`. Ne pas modifier le fichier généré directement.

Focus visible, dialogues natifs, libellés FR/EN/ES, préférences de thème persistées et mouvement réduit sont conservés. Les contrôles automatiques ne remplacent pas une inspection du rendu.

## Références et validation

[Sources et observations de design](public/design-sources.md) : deux maquettes inspectées, documentation réelle des plateformes, limites Pinterest/Behance/MotionSite précisées. Aucune image de maquette tierce n’est utilisée comme asset produit. Photographies existantes créditées dans `public/photo-sources.json`.

La validation V30 est séparée des anciennes preuves : `research/studio-v30/VALIDATION.md`. Le navigateur intégré n’a pas permis d’inspecter cette version ; aucun contrôle visuel mobile/desktop V30 n’est donc revendiqué. Les anciennes captures V22 ne constituent pas une preuve du nouveau rendu.
