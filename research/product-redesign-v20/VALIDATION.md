# V20 — Recherche, cartes et lecteurs

Version **workshop-v20**, vérification du 23 octobre 2026. [Ouvrir l’application](https://valeriongg.github.io/racelink-academy/?release=workshop-v20) · [Commit public 17ea9ab](https://github.com/ValerionGG/racelink-academy/commit/17ea9abab52b9028b5863db61e6537dd939a3be7).

Les **109 contrôles automatisés passent**. Le rapport navigateur consigne **18 scénarios** sur l’application publique ; les **17 fichiers publics** contrôlés par HTTP correspondent au dépôt. Ces trois vérifications ont des périmètres distincts, détaillés ci-dessous.

## Changements vérifiés

La bibliothèque regroupe question, langue du contenu, voiture et commande de filtres. Le panneau de filtres utilise les mêmes contrôles sur ordinateur et mobile ; préférences et plateformes précèdent les sujets repliables. L’interprétation de la recherche reste accessible à la demande. Sur la capture mobile de 390 px, la première ressource commence à **406,75 px** du haut : c’est une mesure de cet état, pas une garantie pour toute recherche.

Les cartes conservent de grandes photographies et présentent titre, auteur, plateforme et langue, avec l’incertitude indiquée lorsqu’elle existe. Le lecteur vidéo commence par le titre et l’auteur, puis organise aperçu, action de lecture, repères, contenu, transcription et notes. Quand aucune transcription n’est enregistrée, il l’annonce et renvoie aux sous-titres éventuels à la source ; un résumé n’est pas présenté comme une transcription.

Les guides possèdent un plan de lecture et un accès direct aux références. La méthode générale RaceLink reste distincte des notices constructeur et de leur périmètre. Le catalogue de guides seuls a été observé sur deux colonnes à l’écran desktop, et le lecteur mobile conserve l’accès aux sources sans débordement dans les états testés.

## Contrôles automatisés

| Suite | Résultat | Ce qu’elle vérifie |
|---|---:|---|
| [Navigation](navigation-checks.json) | 17/17 | Navigation active, fermeture des dialogues, retour du focus simulé, conservation de la question et des filtres, indépendance des langues UI/contenu. |
| [HTML et bundle](html-contract-checks.json) | 14/14 | Identifiants et références ARIA, labels, imports locaux, marqueurs de cache et correspondance exacte du bundle CSS avec ses sources. |
| [Export statique](export-checks.json) | 6/6 | Préfixes `/aide/` et GitHub Pages, compression fidèle, champs publics et preuves conservés ; base temporaire uniquement. |
| [Recherche et filtres](search-filter-checks.json) | 13/13 | Effacement des critères conservant question, format et tri ; plateformes conservant le véhicule ; focus des facettes ; suggestions, corrections et réponses asynchrones obsolètes. |
| [Cartes](card-checks.json) | 52/52 | Texte et provenance échappés, URL d’image, actions, langue inconnue ou estimée, auteur absent et contrats d’intégration. |
| [Lecteur vidéo](detail-checks.json) | 7/7 | Actions et onglets conservés, FR/EN/ES, absence de faux lecteur ou transcription, provenance progressive et rendu sans mutation des données. |
| **Total** | **109/109** | [Agrégat et empreintes des sources](validation-results.json). |

Les tests de navigation et d’export ont été relancés sur la source `5a48d1f`, après l’ajout de la cible de focus `catalog-heading`. Les autres suites conservent leurs dates et empreintes propres ; elles ne sont pas présentées comme des tests navigateur du commit final. Les seuls changements d’attentes aux anciennes suites sont trois marqueurs de cache d’export, de `atelier-v19d` à `workshop-v20`.

Les [quatre précontrôles du paquet](package-preflight-checks.json), hors total de 109, vérifient les marqueurs V20 et la présence/égalité des modules de cartes et de lecteur entre source et export local. Ils ne créent pas le ZIP et ne prouvent pas sa construction finale.

## Vérification de l’application publique

Le [rapport navigateur](browser-checks.json) distingue les interactions contrôlées sur `5a48d1f` des dernières corrections CSS et de leur URL de cache contrôlées sur `17ea9ab`. Il porte sur des fenêtres de navigateur redimensionnées, dont **320, 390 et 768 px**, ainsi que des états desktop.

- Recherche mobile, suggestions au clavier, sélection de YouTube et état actif de la plateforme vérifiés. Le bouton du panneau indique alors deux résultats dans le scénario enregistré.
- « Effacer les critères » conserve `vidange` et le format `video` ; le nombre de résultats observé devient 932 pour cet état du catalogue.
- Fiche vidéo mobile et desktop ouvertes ; aperçu chargé, état sans transcription explicite et retour du focus au titre de la carte vérifiés.
- Guide mobile, navigation vers `guide-sources` et quatre liens de source présents dans le guide contrôlé. Le rapport ne revendique pas la visite de chacune de ces destinations externes.
- Panneau de filtres desktop de 580 px, recherche/tablette et états étroits de recherche, filtres et lecteur contrôlés sans débordement horizontal mesuré.
- Fermeture du panneau voiture avec retour du focus sur `catalog-heading`, libellés anglais et espagnols, puis libellé « Ma voiture » complet à 320 px vérifiés. La feuille finale chargée porte `workshop-v20&rev=2`.

La [contrelecture visuelle indépendante](visual-review.md) porte sur treize captures réellement ouvertes, sans navigateur partagé. Elle ne remplace pas ces tests d’interaction. La capture `search-320.png` montre encore un libellé tronqué ; [search-320-final.png](search-320-final.png) et le dernier scénario navigateur documentent sa correction.

Le [contrôle HTTP final](public-assets-check.json) confirme 17 réponses 200 et une égalité des fichiers avec le dépôt au commit `17ea9ab`. Cette égalité ne constitue pas, à elle seule, un test de rendu.

## Captures

| Surface | Captures |
|---|---|
| Recherche | [Avant mobile](before-search-mobile.png) · [Après mobile](after-search-mobile.png) · [Desktop](search-desktop.png) · [Tablette](search-tablet.png) · [320 px final](search-320-final.png) |
| Filtres et suggestions | [Filtres mobile](filters-mobile.png) · [Filtres desktop](filters-desktop.png) · [Filtres 320 px](filters-320.png) · [Suggestions mobile](suggestions-mobile.png) |
| Vidéo | [Fiche mobile](video-detail-mobile.png) · [Fiche desktop](video-detail-desktop.png) · [Fiche 320 px](detail-320.png) |
| Guides | [Cartes mobile](guide-cards-mobile.png) · [Cartes desktop](guide-cards-desktop.png) · [Lecteur mobile](guide-detail-mobile.png) · [Lecteur desktop](guide-detail-desktop.png) · [Sources mobile](guide-sources-mobile.png) |

Les captures illustrent les étapes décrites par les rapports ; elles ne sont pas toutes des captures du dernier commit CSS.

## Données conservées et limites

La V20 conserve **36 901 vidéos et 11 guides**. Aucun nouveau contenu, média, transcription ou élément de compatibilité véhicule n’a été ajouté par cette refonte. Le [contrôle d’intégrité](catalogue-integrity.json) confirme les dix fichiers du catalogue et de ses transcriptions inchangés. SHA256 du catalogue public : `083bc7f7e05382f189319e7e8e1a1050302d92606f16a6e0cda74212d023b544`.

Les contrôles automatisés emploient des doubles DOM ciblés ou des rendus de markup ; ils ne lancent pas tout le bootstrap de l’application ni le moteur de recherche réel. La vérification publique complète ce périmètre sur les scénarios consignés, sans test sur téléphone physique, lecteur d’écran, zoom système ou certification WCAG exhaustive. Aucun visionnage externe ni consentement aux cookies des plateformes n’a été réalisé dans cette revue. La disponibilité du contenu original et sa validité mécanique ne découlent pas des tests d’interface.

Le [document de décisions](DECISIONS.md) conserve le cadrage préparatoire et ses écarts assumés. Le présent document décrit la validation réalisée après ce cadrage.

## Reproduire les contrôles locaux

Les commandes exactes sont conservées dans [l’agrégat](validation-results.json). Depuis l’espace de travail original, les lanceurs `work/redesign-v20/run-contracts.py navigation`, `html` et `export` exécutent les suites existantes en écrivant leurs rapports dans ce dossier, sans écraser les historiques. Les scripts `test-search-filters.mjs`, `test-resource-card.mjs` et `test-resource-detail.mjs`, dans le même dossier de travail, exécutent les contrôles complémentaires. Le script `summarize-checks.py` agrège leurs résultats ; il ne réalise aucune validation navigateur ou publication.
