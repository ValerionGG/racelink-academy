# V21 — décisions de design

23 octobre 2026 · Direction `cinema-v21`.

**État de ce document : choix de conception et présence dans les sources. Il ne déclare ni validation visuelle V21, ni résultats de tests, ni publication.**

## Intention

Transformer la bibliothèque en un espace de découverte visuelle, avec une identité RaceLink noire, blanche et rouge. La refonte concerne l’accueil, les collections, les résultats et les lecteurs. Elle distingue deux usages : explorer un sujet et trouver une réponse précise avec sa voiture et sa langue.

## Références réellement observées

Les pages ci-dessous ont été ouvertes et vues par l’agent racine dans le navigateur. Les trois captures ont aussi été examinées localement pour ce document. Les observations décrivent les zones visibles, sans extrapoler les parcours non visités.

| Source primaire et preuve | Observation visible | Reprise / adaptation RaceLink |
|---|---|---|
| [MasterClass — accueil](https://www.masterclass.com/) · [capture](reference-masterclass.png) | Fond noir, titre très condensé de grande taille, portraits dominants, recherche dans la navigation et choix par intention. | Fond sombre, titre **Barlow Condensed**, photographie dominante et entrées par sujet. Les portraits de célébrités sont remplacés par des scènes automobiles pertinentes. Aucun discours d’autorité ou résultat pédagogique n’est déduit du style. |
| [Netflix Tudum — guide du nouvel accueil](https://www.netflix.com/tudum/articles/netflix-new-homepage-layout-user-guide) · [capture](reference-netflix.png) | L’article montre une interface TV avec une rangée de grandes couvertures, une sélection mise en avant et des informations associées. | Collections visuelles horizontales, distinction entre guide principal et autres ressources, surfaces sombres cohérentes. **Il s’agit d’une illustration dans un article, pas d’un compte Netflix manipulé.** Pas de reprise des classements, saisons, récompenses ou personnalisation sans données RaceLink. |
| [Domestika — cours](https://www.domestika.org/en/courses) · [capture](reference-domestika.png) | Recherche dans l’en-tête ; cartes montrant image, titre, auteur et informations pédagogiques. Une colonne de catégories et des éléments commerciaux sont également visibles. | Cartes informatives et repérage du sujet, de la langue et de la source. Les filtres restent regroupés dans un panneau RaceLink. Prix, urgence commerciale, compte à rebours et notes ne sont pas reproduits. La fenêtre cookies masque une partie de la capture : aucun constat n’est tiré de cette zone. |

Ces références apportent des principes de composition. Leurs images, marques et contenus ne sont pas incorporés à l’application.

## Choix présents dans l’implémentation

- **Une scène d’accueil photographique.** `service.jpg` donne une échelle humaine à la mécanique. Un dégradé sombre rend le texte lisible sans appliquer une teinte uniforme à toute la photographie. Cette image illustre l’univers : elle n’est pas présentée comme une capture du guide mis en avant.
- **Une typographie à rôles distincts.** Barlow Condensed porte les grands titres éditoriaux ; Onest conserve la lecture et les commandes ; Orbitron reste lié à la signature de marque. La nouveauté porte sur la composition et l’échelle, pas sur un remplacement général des textes par une police décorative.
- **Des guides comme couvertures 3:4.** Les photos des guides deviennent des affiches éditoriales. Les vidéos conservent leurs miniatures réelles en 16:9 : le traitement cinéma ne transforme pas tous les médias en posters verticaux.
- **Des univers photographiques et des sélections réelles.** Les entrées par sujet sont visuelles. Les sélections vidéo utilisent les identités et informations disponibles du catalogue, avec leur raison de sélection et leur provenance ; elles ne simulent pas un classement de popularité.
- **Une recherche distincte de l’accueil.** Les résultats utilisent une grille sombre ; la scène d’accueil disparaît dans ce mode. Question, langue, véhicule et filtres restent des commandes du parcours existant. Sur mobile, les filtres occupent un panneau plein écran.
- **Des lecteurs dans la même direction sombre.** Média, titre, source et informations de compréhension forment une hiérarchie commune. Les guides restent des documents, les notices restent attribuées à leurs constructeurs et la transcription n’est proposée que lorsqu’elle existe.

Le fond principal déclaré dans les sources est `#101112`, le texte principal `#f5f5f2` et l’accent rouge `#e3263f`. Ces valeurs décrivent l’implémentation ; ce document ne leur attribue pas une conformité de contraste non mesurée ici.

## Apport des prompts et skills

La [recherche GitHub et le brief V21](prompt-research.md) documentent les fichiers réellement lus, leurs versions, licences et étoiles au jour de la recherche. Les contributions retenues sont : composition issue du sujet avec **frontend-design**, définition des états et du périmètre avec **Impeccable**, distinction streaming/apprentissage avec **UI UX Pro Max**, force des images réelles avec **Taste**, garde-fous d’interaction avec **baseline-ui**.

Le brief est une intention, pas un journal d’exécution. En particulier, son idée d’un accueil entièrement centré sur une ressource a été **adaptée** : la réalisation utilise une grande photographie d’univers et une entrée séparée vers un guide réel. La recette de démonstration animée de Huashu a été écartée. Aucun skill n’a fourni un code de plateforme prêt à copier.

## Vérifications à venir et limites

Les contrats à préserver et le plan de vérification figurent dans [integration-plan.md](integration-plan.md). La revue V21 devra notamment vérifier le cadrage des couvertures 3:4, l’accès immédiat à la recherche sur téléphone, la lisibilité des titres longs, le clavier dans les rangées, les retours de focus, les filtres et le mouvement réduit.

Les captures de référence sont des preuves d’inspiration, **pas des preuves du rendu RaceLink**. La lecture de `index.html` et `product-ui.css` confirme les choix déclarés ci-dessus, pas leur bon fonctionnement dans tous les états. Les résultats de validation et l’éventuelle publication doivent être consignés séparément après réalisation.
