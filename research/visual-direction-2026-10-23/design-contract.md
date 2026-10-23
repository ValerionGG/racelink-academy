# Contrat visuel — RaceLink Academy

**Direction arrêtée le 23 octobre 2026 : une bibliothèque d’apprentissage portée par de grandes photographies réelles, une recherche immédiatement accessible et l’identité noire, blanche et rouge de RaceLink.** Les images doivent permettre de reconnaître le geste, le véhicule ou la discipline avant de lire. Le titre explique ensuite ce que la ressource permet d’apprendre.

Ce contrat remplace les propositions antérieures de titres à 17–19 px, de petites images latérales sur mobile ou de trois colonnes de cartes dans une zone étroite. Les valeurs ci-dessous sont des choix pour RaceLink, pas des mesures relevées sur les références. Il s’agit d’un brief et d’une grille de critique après implémentation ; aucune validation du nouveau rendu n’est annoncée ici.

## 1. Composition et place des images

### Résultats et guides

- **Mobile : une colonne, photographie sur toute la largeur de la carte, au-dessus du titre.** « Plein cadre » désigne la largeur utile disponible, avec les marges de page ; une vignette placée à gauche du texte ne satisfait pas ce contrat.
- **Format cible : 16:9**, commun aux photographies de guides, couvertures de catégories et miniatures horizontales. À 390 px avec deux marges de 16 px, cela représente environ 358 × 201 px d’image. Ce calcul illustre le volume visuel attendu, sans imposer une marge unique à tous les écrans.
- **Desktop : deux colonnes lorsque la largeur utile de la grille est inférieure à 1 000 px.** La largeur utile exclut la navigation, les filtres latéraux et les marges. Ne pas choisir le nombre de colonnes à partir de la largeur totale de l’écran. Une colonne reste nécessaire lorsqu’il n’y a plus assez d’espace pour deux cartes lisibles.
- À partir de 1 000 px utiles, trois colonnes deviennent possibles si les images restent généreuses et les titres lisibles ; ce n’est pas une obligation. Conserver deux colonnes est préférable à réduire systématiquement les couvertures.
- **Titres : 19 à 22 px**, interligne d’environ 1,25–1,35, graisse lisible. Utiliser Onest pour les titres de ressources et le texte courant. Réserver Orbitron aux accents de marque et aux courts repères, sans transformer les longs titres techniques en affiches typographiques.
- Le titre suit l’image sur une surface claire. Donner assez de lignes au sujet, à l’opération et au véhicule lorsqu’ils sont établis ; le lecteur doit pouvoir distinguer deux procédures proches. Ne pas faire disparaître la génération ou l’opération derrière une troncature prématurée.
- Prévoir 16–24 px entre les cartes et un rythme régulier entre image, titre et métadonnées. Préserver cette respiration avant de chercher à montrer davantage de fiches dans le premier écran.

Pour les vidéos verticales, conserver le sujet utile dans le cadre et vérifier le recadrage. Si une coupe masque un outil ou un geste essentiel, préférer une présentation qui conserve l’image complète. Une couverture ne doit pas devenir une photographie de remplacement présentée comme une image réelle de cette vidéo.

### Catégories photographiques

Les trois portes **Entretien**, **Pilotage** et **Sim racing** doivent être de grandes cartes photographiques reconnaissables, avec un libellé court. Montrer un atelier et une intervention, une situation de pilotage, puis un poste de simulation réel. Ne pas substituer trois fonds abstraits ou trois versions de la même photo.

Sur téléphone, chaque carte occupe la largeur utile disponible. Sur desktop, elles peuvent partager une rangée si chaque photographie garde une place suffisante. Le libellé reste accessible sans survol ; chaque catégorie est un lien ou un bouton identifiable au clavier. La recherche demeure prioritaire dans l’ordre de la page.

## 2. Hero mécanique, recherche immédiate

Le premier écran associe **une photographie mécanique forte**, une base noire, du blanc et un accent rouge RaceLink. Le cadrage doit montrer une matière, une pièce ou une intervention réelle : moteur, outillage en action ou atelier. Une photo autorisée et précisément attribuée suffit ; aucune illustration synthétique, grille de pictogrammes ou jauge décorative ne remplace cette matière.

Retenir de Driven la présence du sujet et le contraste entre image sombre et titre clair. Retenir de HPA le lien direct entre univers mécanique et apprentissage. Appliquer ces principes à un en-tête utile :

1. Une courte phrase d’intention, par exemple **« Apprenez le bon geste. »**, suivie si nécessaire d’une seule ligne explicative.
2. Un **champ de recherche blanc, large et immédiatement utilisable**, avec une aide concrète comme « Vidange Clio 3, freinage, réglage volant… ».
3. Des accès courts aux catégories ; les notices, filtres et détails ne doivent pas former une deuxième introduction.

Sur mobile, viser un bloc photographique d’environ 240–320 px, à ajuster au contenu et au zoom texte. La vraie contrainte est que le champ de recherche apparaisse entièrement dans le premier écran à 390 × 844, sans défilement ni animation préalable. Sur desktop, le champ doit rester immédiatement visible à 1280 × 720. Ces deux critères restent à tester, pas à présumer.

Le texte et le champ sont de vrais éléments HTML. Appliquer un assombrissement local seulement là où le contraste du texte l’exige ; conserver le sujet visible et les couleurs naturelles des photographies de cartes. Le rouge marque les actions et l’état actif, avec un contraste mesuré ; il ne recouvre pas toutes les images.

## 3. Informations qui accompagnent la photo

Ordre de lecture d’une fiche : **image → titre → auteur et source → langue et durée connues → action**. Le type « Guide » ou « Vidéo » reste identifiable. Les filtres et les badges secondaires ne doivent pas concurrencer la photo ni produire une rangée de pastilles plus longue que le titre.

Conserver les distinctions déjà nécessaires au produit : langue de l’interface et langue du contenu, sélection éditoriale et simple référencement, source constructeur et guide RaceLink, mention de véhicule et compatibilité établie. Les détails de provenance peuvent être regroupés dans une zone secondaire, mais le périmètre d’une notice constructeur reste lisible dans le lecteur.

Un état de filtre actif doit être visible, supprimable et conservé lors d’une ouverture puis fermeture de ressource. Aucun changement esthétique ne doit réinitialiser la recherche, la langue, le véhicule ou le retour à la liste.

## 4. Mouvement fonctionnel

Proposer des transitions sobres de 160–200 ms pour l’état d’un bouton, l’ouverture d’une zone ou un léger retour visuel sur une carte. Une mise à l’échelle maximale d’environ 1,02 peut accompagner le survol d’une photo sur desktop si elle ne coupe pas le sujet. Le focus clavier doit être visible indépendamment de cet effet.

La recherche et les liens fonctionnent dès leur affichage. Pas d’introduction bloquante, de carrousel automatique, de vidéo de fond imposée ou de défilement détourné. Désactiver les transformations et transitions non nécessaires lorsque la réduction des animations est demandée. Les captures MotionSite sont des preuves de composition, **pas une preuve des mouvements ou performances de ces templates**.

## 5. Matrice référence → changement → vérification

| Référence et niveau de preuve | Changement retenu pour RaceLink | Vérification après implémentation |
|---|---|---|
| **[MotionSite](https://www.motionsite.ai/), « Driven Hero – High-Tech Section »**. Aperçu public réellement inspecté ; [capture](motionsite-driven.png) relue. Pièce mécanique diagonale très présente, noir et gris, texte blanc contrasté. | Hero photographique mécanique, sujet identifiable et titre bref. Recomposer avec une photographie autorisée propre au projet ; ne pas copier le texte, le composant ou l’image du template. | Le sujet mécanique reste lisible à 390 et 1280 px. Le champ de recherche est visible au premier écran. Le hero n’occupe pas toute la hauteur utile au détriment de la bibliothèque. |
| **[MotionSite](https://www.motionsite.ai/), « Hyperion V12 – Automotive Hypercar Template »**. Aperçu public réellement inspecté ; [capture](motionsite-hyperion.png) relue. Noir, grands contrastes blanc/rouge et hiérarchie automobile affirmée. | Accent rouge pour action et navigation, fond noir dans la zone de marque, hiérarchie forte. Les cartes de statistiques de l’aperçu ne deviennent pas des compteurs décoratifs de cours. | Une action principale est identifiable ; textes et commandes conservent leur contraste. Aucun faux chiffre, niveau ou indicateur de progression. |
| **[RaceLink officiel](https://racelink-app.co/)**. Inspection réelle par l’agent principal ; [capture](racelink-reference.png) relue. Univers noir/rouge, mot-clé rouge, navigation sombre ; Onest et Orbitron constatées lors de l’inspection précédente. | Continuité de marque dans le hero et la navigation. Onest pour les ressources, Orbitron pour quelques accents courts. Photos de cartes sur surfaces claires. | La parenté RaceLink est visible sans reproduire la page promotionnelle. Un titre long de tutoriel reste facile à lire et le rouge n’altère pas les photographies. |
| **[HPA — Automotive Training Courses](https://www.hpacademy.com/courses/)**. Page primaire lue en texte lors de la recherche ; pas de nouvelle inspection visuelle revendiquée. Catégories de formation automobile explicites. | Les grandes photos conduisent à des sujets d’apprentissage précis : mécanique, réglage, pilotage. L’intention pédagogique prime sur la promotion. | Chaque entrée mène à un catalogue pertinent ; le titre indique un sujet ou un geste, pas seulement une ambiance automobile. |
| **[AUTODOC Club — manuels](https://club.auto-doc.fr/manuals)**. Page primaire lue en texte : accès par véhicule et pièce, procédures nommées. | Garder l’opération et le véhicule lisibles sous les grandes photos ; rendre les filtres accessibles sans les imposer à chaque visite. | Deux vidéos d’opérations ou de générations différentes se distinguent sans ouverture. Aucun véhicule non prouvé ajouté à un titre. |
| **[Dribbble — Photography Studio Course Landing Page](https://dribbble.com/shots/27667979-Photography-Studio-Course-Landing-Page-Design), Rangan Mohanta Dibosh**. Description de l’auteur lue ; pixels non inspectés dans cette recherche. | Référence secondaire pour l’intention éditoriale photographique. Les dimensions et comportements proviennent du présent contrat, pas de cette page. | Pas d’argument « observé sur Dribbble » pour une disposition ou animation non vue. Comparer le résultat aux critères mesurables ci-dessus. |
| **[Pinterest — Online courses landing page](https://in.pinterest.com/pin/752030837806028791/)**. Titre indexé ; accès direct refusé, aucune inspection visuelle. | Piste documentaire conservée, aucun détail visuel adopté sur cette seule base. | Ne pas attribuer à ce pin une mise en page, un auteur ou une animation non vérifiés. |

Les captures MotionSite montrent les aperçus à l’intérieur de leur galerie. Elles ne prouvent ni l’accès au code du template, ni ses droits de réutilisation, ni son comportement mobile. Les références sont des principes de composition ; leurs actifs ne sont pas les actifs du site.

## 6. Critique à effectuer sur le résultat

Avant de valider, produire des captures de l’accueil, des résultats et d’un guide à **390 px et 1280 px**, puis contrôler l’adaptation à 320 px et 768 px. Ces vérifications sont à réaliser après implémentation.

1. **L’image a-t-elle réellement repris sa place ?** Rejeter un résultat mobile qui ressemble encore à une liste avec petite vignette latérale. Mesurer le cadre et vérifier le 16:9, le sujet et la netteté.
2. **Les cartes respirent-elles dans la largeur disponible ?** Relever la largeur réelle de la grille. En dessous de 1 000 px utiles sur desktop, trois colonnes constituent un écart au contrat.
3. **Lit-on le titre sans effort ?** Vérifier les 19–22 px calculés, un titre technique long, un véhicule/génération et une langue étrangère. Tester l’agrandissement du texte sans masquer l’action.
4. **Peut-on chercher immédiatement ?** À froid, le champ reste visible et utilisable avant l’image et les animations. Vérifier aussi le retour depuis une ressource et la présence du clavier mobile.
5. **Les photos disent-elles vrai ?** Contrôler chaque sujet, source et recadrage. Une prise OBD ne doit pas être remplacée par une vidange ; une photo générique ne prétend pas montrer une vidéo particulière.
6. **La marque reste-t-elle au service de la lecture ?** Critiquer les halos, textes Orbitron longs ou aplats rouges qui réduisent la lisibilité. Tester contrastes, focus et états actifs, sans se fier à l’impression visuelle seule.
7. **Les interactions existantes restent-elles intactes ?** Recherche avec langue et véhicule, suggestion au clavier, ouverture/fermeture du guide, lien de notice, retour à la liste et focus restauré. Vérifier l’absence de recouvrement par la navigation mobile et de défilement horizontal involontaire.
8. **Le mouvement aide-t-il vraiment ?** Tester la préférence de réduction des animations. Une interface dépendant d’un effet pour révéler ses commandes doit être corrigée.

La validation finale doit consigner les dimensions, captures et interactions réellement vérifiées, ainsi que les écarts encore présents. Le présent document ne les déclare pas réussis.

## Documents associés

- [Références visuelles et niveaux de preuve](visual-references.md) — recherche antérieure ; les choix dimensionnels du présent contrat prévalent.
- [Recherche de skills de design](skills-research.md).
- [Moteurs et outils disponibles](design-engines.md) — inventaire de capacités, distinct d’une évaluation visuelle du résultat.
