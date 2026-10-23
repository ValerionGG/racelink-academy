# RaceLink Academy — Workshop V20

> Archive documentaire V20. Le contenu historique est conservé ; seuls les liens relatifs ont été adaptés à ce dossier. La direction courante se trouve dans [PRODUCT.md](../../PRODUCT.md) et [DESIGN.md](../../DESIGN.md).

**Version `workshop-v20` publiée et vérifiée, 23 octobre 2026.** [Ouvrir RaceLink Academy](https://valeriongg.github.io/racelink-academy/?release=workshop-v20). Référence finale publiée [`17ea9abab52b9028b5863db61e6537dd939a3be7`](https://github.com/ValerionGG/racelink-academy/commit/17ea9abab52b9028b5863db61e6537dd939a3be7), [workflow 39997940444](https://github.com/ValerionGG/racelink-academy/actions/runs/39997940444). Les interactions ont été contrôlées sur [`5a48d1f`](https://github.com/ValerionGG/racelink-academy/commit/5a48d1fc2eebd0728079b79666e276f00ae43043), puis le contrôle HTTP et les deux finitions CSS sur `17ea9ab`. [Validation](../../research/product-redesign-v20/VALIDATION.md) · [Design courant](DESIGN-snapshot-v20.md) · [Décisions V20](../../research/product-redesign-v20/DECISIONS.md).

## Register

product

## Users

Une personne compare des ressources près de sa voiture sur téléphone, ou prépare sur ordinateur une intervention, une séance de pilotage ou de simulation. Elle doit comprendre le sujet, la langue et l'origine avant d'ouvrir. Année, moteur, niveau ou langue inconnus ne sont pas déduits pour remplir l'interface.

## Product Purpose

Poser une question, préciser éventuellement langue et véhicule, comparer des vidéos ou guides, puis consulter en conservant le contexte de recherche. **La V20 refond recherche, filtres, cartes et lecteurs ; l'accueil photographique V19 est conservé.**

La carte sert de premier aperçu utile, sans écran intermédiaire supplémentaire. Le lecteur distingue ce qui est consultable ici, ce qui s'ouvre chez l'auteur et les preuves disponibles.

## Brand Personality

Une bibliothèque automobile concrète, à grandes photos, lisible et précise. Onest porte l'interface, Orbitron la marque. L'accueil papier `#f5f5f4` et le header `#111214` restent ; les résultats prennent un fond `#f0f1f3`, des surfaces blanches et le rouge d'action `#bb1830`.

La refonte répond à la tâche : elle retire la sidebar de filtres, rapproche les paramètres utiles de la question et nomme l'origine des aperçus. Les images réelles gardent leurs auteurs, leur sujet et leurs limites.

## Design Principles

- **La question avant la classification.** Recherche visible, langue et voiture en contrôles courts ; sujets et critères détaillés à la demande.
- **Comparer sur de grandes images.** Deux colonnes desktop et une colonne mobile, y compris pour les guides seuls. Couvertures 16:9, titre et description dans le corps de carte.
- **Attribuer l'aperçu.** Description source ou résumé éditorial existant, avec son libellé ; aucune étape ni promesse pédagogique inventée.
- **Révéler les détails au bon endroit.** Interprétation et guide conseillé dans un élément repliable ; conflit de véhicule rendu visible.
- **Préserver le contexte.** Question, langue et critères restent le contrat commun des suggestions, filtres et retours de fiche.
- **Garder les inconnues honnêtes.** Langue estimée, auteur absent, niveau indicatif et transcription absente sont nommés sans certification implicite.

## Core Experience

**Recherche et contexte.** Un seul formulaire est déplacé entre accueil, emplacement desktop des résultats et dialogue mobile. Le contrôle de voiture ouvre le panneau existant ; la langue du contenu reste indépendante de la langue FR/EN/ES du site. Les formats Tout/Vidéos/Guides restent visibles.

**Filtres.** Un panneau natif partagé desktop/mobile remplace la colonne permanente. Il présente préférences de contenu, plateformes, sujets repliés et critères avancés. Les filtres modifient immédiatement les résultats ; le pied « Voir N résultats » ferme le panneau et utilise le total courant, ou un état de chargement/indisponibilité. Le badge du bouton compte les critères supplémentaires, sans recompter question, langue et principaux champs véhicule.

**Résultats.** Total, tri et critères supplémentaires restent compacts. « Comprendre ces résultats » rassemble interprétation et guide conseillé ; un conflit de véhicule ouvre la zone. Les cartes affichent sujet, langue, titre, aperçu attribué, auteur et plateforme. Un véhicule cité ne devient pas une compatibilité.

**Vidéo.** Titre/auteur en haut, média et lecture côte à côte sur grand écran. Sur mobile, titre/auteur puis média puis contenu : l'aperçu avant média proposé dans le rapport UX n'est pas l'ordre actuellement implémenté. Lecture externe sur demande, ou lien vers la plateforme si l'intégration n'est pas disponible. Contenu, transcription et notes restent séparés ; source, droits, légende d'origine et autres détails sont accessibles dans leurs sections.

**Guide.** Carte photo avec sujet, résumé existant et référence constructeur nommée. Lecteur avec photo, plan, prérequis, méthode et notices distinctes. Les onze guides et vingt et une références constructeur sont conservés ; chaque notice garde son véhicule, sa période et ses limites. Les contrôles sont traduits, les textes documentaires français restent signalés. Aucun moteur ou produit compatible n'est déduit de la couverture.

## Accessibility & Inclusion

Dialogues, boutons, champs et disclosures natifs, labels et focus explicites restent les invariants. Les nouveaux modules conservent les IDs et actions de recherche, lecture, sauvegarde, partage, transcription et navigation vers les sources. Les images sont grandes sans remplacer les textes.

Les parcours publics ont été vérifiés à 320/390/768/1280 px : filtres, focus de plateforme, suggestions avec flèches/Entrée, réinitialisation conservant question et format, fiche vidéo et retour du focus, guide et accès aux notices. La [contrelecture des captures](../../research/product-redesign-v20/visual-review.md) est distincte de ces essais fonctionnels. Les [109 contrôles locaux](../../research/product-redesign-v20/validation-results.json) ne constituent pas un audit d'accessibilité complet.

Aucun téléphone physique, texte agrandi/zoom système, réglage OS de mouvement réduit, lecteur d'écran ou audit WCAG exhaustif n'a été testé. Les observations portent sur des fenêtres émulées et des états ciblés ; toutes les cibles ne sont pas documentées comme atteignant 44 px. Les parcours complets ne sont pas déclarés rejoués après les deux finitions CSS de `17ea9ab`.

## Content, Sources & Rights

La refonte n'ajoute ni procédure, ni vidéo, ni transcription. Aperçus éditoriaux, descriptions natives, extraits indexés et textes autorisés gardent leur provenance. Les droits de réutilisation restent distincts du simple accès public.

Les douze JPG locaux, leurs sources et leurs licences restent dans [le manifeste photo](../../public/photo-sources.json) et [les crédits](../../public/photo-credits.html). Le nouveau cadrage ne prouve ni véhicule compatible ni geste correctement exécuté. Le VIN illustré a été modifié par son auteur.

Les raisons des sélections RaceLink, les licences, les limites de notices et les références d'origine restent accessibles. Onest et Orbitron continuent d'être chargées via Google Fonts avec repli système.

## Anti-references, Evidence & History

Rejetés : nouvelles rangées d'explication avant chaque résultat, colonne de filtres permanente, double formulaire, modale intermédiaire, résumés fabriqués, sources cachées et petites vignettes de substitution.

Le rapport UX et les [décisions V20](../../research/product-redesign-v20/DECISIONS.md) relient les changements aux problèmes observés dans V19. Les idées non implémentées ne deviennent pas des fonctions acquises : l'ordre mobile de la fiche vidéo, les sorties détaillées de zéro résultat et les propositions de masquage des sujets sans résultat doivent être distingués du code réel.

Les références RaceLink/MotionSite et Flowith/Claude Opus 5.5 sont des [observations historiques V17](../../research/visual-direction-2026-10-23/design-contract.md), sans nouvelle visite revendiquée. Les [ressources de design V18](../../research/skills-roundup-2026-10-23/README.md) restent documentées ; Impeccable produit est appliqué à cette itération.

**État V20 : publiée au commit final `17ea9ab`, vérifications ciblées terminées.** Les dix-sept fichiers publics correspondent à ce commit et le catalogue reste inchangé. Le fond blanc des sujets associés et le libellé « Ma voiture » complet à 320 px ont été contrôlés après le dernier correctif. Les 18 scénarios navigateur et les 109 contrôles locaux conservent leur périmètre et leur commit propres ; les 14 contrôles HTML/bundle ont été relancés sur le CSS final. La [validation V20](../../research/product-redesign-v20/VALIDATION.md) détaille cette portée. La [validation V19d](../../research/graphic-redesign-v19/VALIDATION.md) reste historique. L'intégration dans le domaine Focus est distincte d'une publication GitHub Pages.
