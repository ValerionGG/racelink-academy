---
version: alpha
name: RaceLink Academy
description: V19d published and verified within the documented browser and source-check scope.
colors:
  primary: "#bb1830"
  brand: "#ff2330"
  canvas: "#f5f5f4"
  surface: "#ffffff"
  on-surface: "#17181a"
  muted: "#5e6065"
  border: "#dedfdf"
  accent-soft: "#fff0f2"
  neutral-soft: "#ececed"
  shell: "#111214"
  shell-muted: "#b4b5b8"
typography:
  body:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 15px
    lineHeight: 1.6
  brand:
    fontFamily: "Orbitron, Onest, system-ui, sans-serif"
    fontSize: 14px
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: 0px
  hero:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 62px
    fontWeight: 650
    lineHeight: 1.04
    letterSpacing: -0.04em
  hero-mobile:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 43px
    fontWeight: 650
    lineHeight: 1.05
    letterSpacing: -1.6px
  hero-compact:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 37px
    fontWeight: 650
    lineHeight: 1.05
    letterSpacing: -1.3px
  video-title:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 22px
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: -0.55px
  guide-title:
    fontFamily: "Onest, system-ui, sans-serif"
    fontSize: 23px
    fontWeight: 650
    lineHeight: 1.3
    letterSpacing: -0.4px
rounded:
  surface: 12px
  resource-photo: 10px
  search: 9px
  compact-control: 6px
  guide-control: 9px
  brand-mark: 9px
  dialog: 18px
spacing:
  desktop-page-inline: 48px
  mobile-page-inline: 20px
  compact-page-inline: 16px
  hero-columns: 52px
  resource-columns: 28px
  resource-rows: 40px
  guide-reader-columns: 36px
components:
  masthead:
    height: 80px
    backgroundColor: "{colors.shell}"
  masthead-mobile:
    height: 70px
    backgroundColor: "{colors.shell}"
  resource-photo:
    rounded: "{rounded.resource-photo}"
    aspectRatio: "16 / 9"
  topic-photo:
    rounded: "{rounded.resource-photo}"
    aspectRatio: "4 / 3"
  hero-photo-mobile:
    rounded: "{rounded.resource-photo}"
    aspectRatio: "16 / 10"
  guide-reader-photo:
    height: 280px
    rounded: "{rounded.resource-photo}"
  guide-reader-photo-mobile:
    aspectRatio: "16 / 9"
    rounded: "{rounded.resource-photo}"
  focus-ring:
    color: "{colors.primary}"
    outlineWidth: 3px
    outlineOffset: 4px
  press-motion:
    transitionDuration: 150ms
    transitionTimingFunction: "cubic-bezier(.23,1,.32,1)"
  control-motion:
    transitionDuration: 180ms
    transitionTimingFunction: ease
  discovery-photo-motion:
    transitionDuration: 400ms
    transitionTimingFunction: "cubic-bezier(.23,1,.32,1)"
  guide-photo-motion:
    transitionDuration: 300ms
    transitionTimingFunction: ease
  reduced-motion:
    animation: none
    transition: none
    scrollBehavior: auto
---

# Interface RaceLink Academy — Atelier V19d

**Version `atelier-v19d` publiée et vérifiée, 23 octobre 2026.** [Ouvrir RaceLink Academy](https://valeriongg.github.io/racelink-academy/?release=atelier-v19d). Commit de code [`850e57869e9ad9219c054000c8e7b46718835a25`](https://github.com/ValerionGG/racelink-academy/commit/850e57869e9ad9219c054000c8e7b46718835a25), [workflow de publication 39993178520 réussi](https://github.com/ValerionGG/racelink-academy/actions/runs/39993178520). La [validation détaillée](research/graphic-redesign-v19/VALIDATION.md) distingue les observations V19, V19b, V19c et V19d et leurs limites.

Les neuf sections suivent le workflow [Reference Design Contract](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/skills/reference-design-contract/SKILL.md). Le frontmatter reprend les valeurs réellement déclarées dans `public/product-ui.css`, selon la syntaxe alpha Google DESIGN.md ; les propriétés de composant additionnelles sont des extensions permises, sans succès du lint officiel revendiqué. [Contrat préparatoire V19](research/graphic-redesign-v19/design-contract.md) · [Handoff et inventaire](research/graphic-redesign-v19/implementation-handoff.md) · [Contexte produit](PRODUCT.md).

## 1. Visual Theme & Atmosphere

Une bibliothèque automobile photographique, claire et pratique. Le nouvel accueil juxtapose une zone de lecture/recherche à gauche et un gros plan mécanique réel à droite. Le header noir horizontal et le rouge d'action ancrent la marque ; le papier clair accueille les titres et les informations utiles. Les photos donnent de la présence au geste, les titres expliquent la ressource.

V19 recompose V18 : **aucune sidebar fixe** ; navigation principale dans le header, barre de sujets horizontale secondaire dans le flux. Le catalogue et les lecteurs conservent les fonctions existantes. La recherche, la langue du contenu et les précisions du véhicule priment sur les éléments promotionnels.

## 2. Color

| Rôle réel | Valeur V19 | Usage |
|---|---|---|
| Papier | `#f5f5f4` | Fond principal |
| Surface | `#ffffff` | Recherche, contrôles et lecteurs |
| Encre | `#17181a` | Texte principal |
| Secondaire | `#5e6065` | Sources, aides et descriptions |
| Séparation | `#dedfdf` | Filets et bordures |
| Action | `#bb1830` | Actions, liens actifs et focus |
| Marque | `#ff2330` | Repère de marque et trait de navigation |
| Action légère | `#fff0f2` | États sélectionnés |
| Surface neutre secondaire | `#ececed` | Fond secondaire |
| Header et bandeau guide | `#111214` | Zones sombres |
| Secondaire sur sombre | `#b4b5b8` | Repères secondaires |

Ces valeurs effectives remplacent les propositions initiales `#121314` et `#c82038` du contrat préparatoire. Les rapports conservent la trace de cette proposition ; la présente charte décrit la source courante.

Contrastes calculés à partir des valeurs, sans audit du rendu : encre/papier **16,29:1**, secondaire/papier **5,77:1**, blanc/action **6,39:1**, action/papier **5,86:1**, blanc/header **18,74:1**. Blanc/rouge de marque reste **3,79:1** : ne pas y placer du petit texte blanc. Les images ne reçoivent pas de teinte rouge ou verte globale.

## 3. Typography

**Onest** porte lecture, titres et commandes ; **Orbitron** est réservé à la marque. `index.html` charge Onest 400/500/600/700/800 et Orbitron 600/700/800 via Google Fonts avec `display=swap`. Aucun fichier de fonte local n'est livré dans `public/assets` ; le repli Onest → système → sans-serif doit rester utilisable. Les graisses indiquées ci-dessous sont celles du CSS, pas des mesures de police rendue.

| Élément | Source V19 |
|---|---|
| Corps de base | 15 px / 1,6 |
| Titre d'accueil | 62 px / 1,04 ; graisse 650 |
| Accueil entre 761 et 1100 px | 48 px |
| Accueil jusqu'à 760 px | 43 px / 1,05 |
| Accueil jusqu'à 360 px | 37 px / 1,05 |
| Accueil à partir de 1600 px | 72 px |
| Titre de vidéo | 22 px / 1,35 ; 20 px dans la rupture tablette, 21 px jusqu'à 360 px |
| Titre de guide | 23 px / 1,3 ; 21 px jusqu'à 360 px |
| Titre du lecteur guide | 40 px desktop ; 31 px mobile |
| Suggestions mobiles | Type 12 px, titre 16 px, complément 13 px |

Les titres des cartes gardent le geste, le sujet et les précisions établies. Les observations couvrent notamment l'accueil français final, l'anglais sur tablette V19c et l'espagnol à 320 px V19b ; elles ne constituent pas une revue exhaustive de tous les titres et langues. Le texte agrandi et le zoom système n'ont pas été testés. Certains badges de la source restent à 10–11 px : ne pas les décrire tous comme des badges de 12–13 px ni déduire un audit de lisibilité exhaustif.

## 4. Spacing & Grid

Le conteneur principal a un maximum de **1440 px**, avec 48 px de marge intérieure desktop, 30 px entre 761 et 1100 px, 20 px mobile et 16 px jusqu'à 360 px. Le contenu ne réserve plus de largeur à une sidebar de navigation.

Le catalogue conserve des **filtres latéraux de 205 px**, séparés des résultats par 36 px. La grille vidéo emploie `auto-fill` avec minimum 340 px et espacements de 28 px horizontal / 40 px vertical. La grille ne contenant que des guides utilise un minimum de 330 px. À 1280 px, le calcul CSS donne deux colonnes généreuses ; le nombre de colonnes dépend de l'espace après filtres et marges. Entre 761 et 1100 px, filtres 170 px, écart 26 px et minimum vidéo 270 px. À 760 px et moins, filtres dans le dialogue et résultats en une colonne avec écart de 36 px.

Les catégories et sélections ont trois colonnes desktop ; les sélections passent à deux dans la rupture tablette. Sur mobile, les catégories restent en rail à environ 88 % de largeur par carte, les sélections à 92 %, avec commandes natives. Jusqu'à 360 px, les deux rails utilisent 92 %. Les captures et mesures publiées couvrent les écrans décrits dans la validation, sans vérifier toutes les combinaisons de contenu et de largeur.

## 5. Layout & Composition

**Navigation.** Header noir sticky de **80 px desktop / 70 px mobile**. Accueil, Bibliothèque, Parcours et Enregistrés sont dans sa navigation principale sur ordinateur. La classe historique `.app-sidebar` désigne désormais une **barre de sujets horizontale statique de 60 px**, avec véhicule et aide ; ce n'est plus une colonne fixe. Elle disparaît jusqu'à 760 px. Sur téléphone, la barre basse conserve Accueil / Rechercher / Parcours / Enregistrés et la zone de sécurité du système.

**Accueil.** Colonnes `1fr / 1.05fr`, écart de 52 px : titre et recherche à gauche, `assets/photos/oil.jpg` à droite. La photo montre un versement d'huile, sans prouver une spécification de lubrifiant. Son minimum desktop est 440 px de haut ; elle garde une action blanche en bas pour explorer la mécanique. Le titre et le texte d'introduction restent hors photo. Sur mobile, ordre DOM et visuel : texte → recherche/langue → photographie. **Le hero mobile implémenté est en 16:10**, tandis que les ressources restent en 16:9 ; cela remplace le ratio proposé dans le brief.

**Découverte.** Trois portes photographiques en **4:3**, légendes sous les images. Puis un bandeau sombre « Les bons gestes. Les bonnes sources. » associe **`wheel.jpg`** à un accès direct aux guides : image de roue réelle et texte côte à côte sur desktop, empilés sur mobile. La sélection éditoriale et les autres sujets suivent, sans fausses notes ni compteurs décoratifs.

**Catalogue.** Le mode résultats masque hero et découverte. Recherche modifiable, langue, véhicule, formats et critères actifs précèdent les grandes cartes. Les filtres latéraux appartiennent au catalogue seulement. Sur mobile, recherche et filtres sont des commandes dans le flux, sans deuxième couche fixe au-dessus des résultats.

## 6. Components

**Cartes.** Couvertures vidéo et guide 16:9, rayon final de 10 px, titre en dessous ; auteurs, plateforme et langue disponible restent lisibles. Aperçu manquant explicite. Une photo de guide ne remplace jamais la miniature d'une vidéo. Le badge « Proposé par RaceLink » renvoie à une raison et une preuve ; il ne signifie ni visionnage intégral ni validation technique.

**Recherche mobile.** Un seul formulaire est déplacé dans le dialogue natif ; aucun identifiant dupliqué. Champ et sélecteur de langue à 16 px, fermeture 44 px, suggestions séparant format, titre et provenance. Changer la langue doit conserver saisie et critères, actualiser les suggestions et garder la feuille ouverte. La langue de l'interface demeure indépendante. Les guides restent accessibles directement et dans leur onglet.

**Lecteur guide.** Les onze guides partagent un dialogue natif, avec **photo réelle entre titre et introduction** : hauteur 280 px desktop, cadre 16:9 mobile. Méthode RaceLink, informations à réunir et sources constructeur restent séparées. Les 21 références constructeur précisent leur véhicule, édition/période, section, date et limites. L'accès depuis une carte peut rejoindre directement les sources. Les autres portails et références sont secondaires, identifiés comme tels.

**Parcours V19d.** Les huit entrées deviennent des lignes éditoriales séparées par des filets, sans blocs d'icônes visibles ni fonds de carte. Sur ordinateur, chaque ligne aligne titre, description et action « Découvrir le parcours » ; le titre mesure 27 px, la description 15 px et l'action conserve une hauteur minimale de 44 px. Sur mobile, ces trois éléments s'empilent, avec titre de 25 px et description de 14 px. Le bouton natif occupe toujours toute la ligne ; le pictogramme historique reste dans le DOM mais son conteneur est masqué. L'accès aux quatre étapes et au suivi personnel reste inchangé, sans certification.

**Lecteurs et vues secondaires.** Les vidéos, parcours, enregistrés, véhicule et FAQ utilisent le même système clair. La FAQ conserve sa recherche et ses accordéons natifs. Les dialogues deviennent plein écran sur mobile. Les sources, légendes, extraits indexés, résumés et transcriptions gardent leur nom et leur niveau de preuve.

## 7. Motion & Interaction

Valeurs déclarées : pression des flèches 150 ms, courbe `cubic-bezier(.23,1,.32,1)` ; couleurs des boutons 180 ms. Le hero et les catégories ont une transition photo de 400 ms, les couvertures de guides 300 ms. Sur périphérique avec survol, le zoom atteint **1,025**, sans déplacement de la carte. Ces valeurs effectives remplacent les durées seulement proposées dans les contrats antérieurs.

Sous `prefers-reduced-motion`, animations et transitions non essentielles disparaissent ; le rail choisit un défilement instantané. Pas d'autoplay, parallaxe, défilement détourné ou cascade retardant les résultats. Les commandes de rail gardent le focus à leur limite avec `aria-disabled` ; leur disparition responsive doit rendre le focus à une carte visible.

Focus : contour rouge de 3 px, décalage de 4 px. Conserver contrôles natifs, labels, clavier, retour du focus et contexte de recherche. Le raccourci de recherche ne doit pas interférer avec un dialogue ouvert. Les contrôles effectués incluent les suggestions au clavier sur V19/V19b et le focus du lecteur et des sources de guide sur V19c ; ils ne couvrent pas toutes les interactions au clavier.

## 8. Voice & Brand

Un ton précis et accueillant : nommer un geste, une question ou un sujet, sans fausse promesse. Une mention de véhicule n'est pas une compatibilité ; une estimation de langue n'est pas une langue déclarée par la plateforme. Une méthode générale RaceLink n'est pas une procédure constructeur certifiée.

Les douze photographies locales et leurs conditions figurent dans [le manifeste](public/photo-sources.json) et [les crédits](public/photo-credits.html). Les images Pexels, Unsplash, CC BY, CC BY-SA et domaine public conservent chacune leurs conditions ; leur licence n'est pas celle du code. Les photos d'illustration ne prouvent ni véhicule compatible ni procédure sûre. Le numéro de la photo d'identification Audi a été modifié par son auteur.

La filiation RaceLink/MotionSite vient des **inspections V17 historiques**, documentées dans [les références](research/visual-direction-2026-10-23/design-contract.md). La consultation Flowith avec Claude Opus 5.5 appartient également à V17 : [preuve et limites](research/visual-direction-2026-10-23/flowith-opus-5-5.md). Aucune nouvelle visite de ces références ni génération n'est revendiquée pour V19. Les [douze ressources de design V18](research/skills-roundup-2026-10-23/README.md) apportent méthodes et contrôle ; leurs conventions ne remplacent pas le brief.

## 9. Anti-patterns

Exclure petites vignettes latérales sur mobile, affiches à pictogrammes, teinte uniforme des photographies, longs titres Orbitron, introduction promotionnelle avant la recherche, effets GPU sur le contenu et validation technique implicite. Ne pas réintroduire la sidebar fixe ou trois petites colonnes à 1280 px avec les filtres actuels.

`public/product-ui.css` reste la source visuelle ; `scripts/build_ui.py` génère `app-ui.css` en couches legacy puis product. Ne pas corriger le bundle à la main ni empiler de nouvelles feuilles. Préserver les priorités de visibilité des vues, des dialogues et du mode résultats.

**État : V19d publiée et vérifiée dans le périmètre documenté.** Les [observations navigateur](research/graphic-redesign-v19/browser-checks.json) et le [contrôle des fichiers publics](research/graphic-redesign-v19/public-assets-check.json) complètent la [validation](research/graphic-redesign-v19/VALIDATION.md).

- **V19/V19b :** recherche en français, suggestions au clavier, filtre YouTube et correction du hero dans les résultats mobiles.
- **V19c :** guides photographiques, accès aux sources et focus, parcours en lignes sur ordinateur et mobile, accueil anglais sur tablette. Ces cas n'ont pas tous été rejoués sur V19d.
- **V19d :** accueil français à 390 et 1280 px ; menu à 320 px repositionné à l'origine `(0, 0)` ; onglets sans débordement interne avec `clientWidth = scrollWidth = 273 px`.
- **Contrôles automatisés :** 14 tests HTML et 6 tests d'export sur V19d ; 17 tests de navigation sur V19c. Les 15 fichiers publics contrôlés répondent HTTP 200 et correspondent aux octets du dépôt.

Les tailles mobiles sont des fenêtres émulées, pas des appareils physiques. Aucun test de texte agrandi ou de zoom système, de réglage OS de mouvement réduit, de lecteur d'écran ni audit WCAG exhaustif n'a été réalisé. Toutes les pages et tailles n'ont pas été rejouées sur V19d, dont le correctif final porte sur deux règles CSS et les marqueurs de cache. Les liens constructeur avaient été vérifiés lors de la recherche de sources ; leur contenu externe n'a pas été revérifié pendant cette passe UI.

Historique séparé : [V14](research/ui-redesign-2026-10-23/VALIDATION.md), [photos V15](research/photo-covers-2026-10-23/VALIDATION.md), [guides V16](research/official-guides-2026-10-23/VALIDATION.md), [V17](research/visual-direction-2026-10-23/VALIDATION.md), [V18](research/skills-roundup-2026-10-23/VALIDATION.md). Ces preuves ne valident pas automatiquement la nouvelle composition.
