# RaceLink Academy — Cinéma V21

**Version `cinema-v21` publiée et vérifiée le 23 octobre 2026.** [Ouvrir la refonte](https://valeriongg.github.io/racelink-academy/?release=cinema-v21&build=065ab48) · [Validation et limites](research/cinema-v21/VALIDATION.md) · [Design](DESIGN.md) · [Décisions](research/cinema-v21/DESIGN-DECISIONS.md).

## Register

product

## Users

Une personne explore la mécanique, prépare une intervention près de sa voiture, découvre le pilotage ou règle un simulateur. Elle peut aussi arriver avec une question précise. Elle doit comprendre le sujet, la source et la langue avant d’ouvrir une ressource, puis retrouver sa recherche.

Années, moteurs, niveaux, langues ou transcriptions inconnus ne sont pas inventés. Un véhicule cité ne constitue pas une compatibilité établie.

## Product Purpose

**V21 refond l’accueil, les collections, les résultats et les lecteurs dans une direction cinéma.** Elle remplace l’accueil papier V19. Le parcours associe une découverte par grandes photos à une recherche par question, langue et véhicule.

L’accueil présente une grande photographie d’atelier, un guide à découvrir, six guides pratiques en couvertures verticales, trois univers photographiques et des sélections vidéo réelles. Les six guides mis en avant ne remplacent pas l’accès aux onze guides existants. Les données et leurs preuves restent distinctes de la mise en scène.

## Brand Personality

Une bibliothèque automobile éditoriale : fond encre `#101112`, surfaces `#191b1f`, texte clair et rouge RaceLink `#e3263f`. **Onest** sert la lecture, **Barlow Condensed** donne une échelle forte aux titres, **Orbitron** conserve le rôle de signature.

Les photos de navigation sont des illustrations créditées, séparées des véritables miniatures vidéo. Aucune photo n’est une preuve de procédure ou de compatibilité.

## Design Principles

- **Séparer découverte et réponse.** L’accueil organise les collections ; la recherche retire cette scène pour comparer les résultats.
- **Faire comprendre par l’image et le texte.** Guides d’accueil en 3:4, miniatures vidéo en 16:9, titres et provenance accessibles sans survol.
- **Garder la question et son contexte.** Formulaire unique ; langue, voiture, filtres et retours de fiche suivent le même état.
- **Attribuer les informations.** Description source, texte éditorial et transcription conservent leur provenance.
- **Révéler les détails progressivement.** Filtres dans un panneau ; interprétation des résultats et preuves à la demande.
- **Éviter la fausse personnalisation.** Pas de popularité, certification, progression ou recommandation personnelle déduite de l’esthétique streaming.

## Core Experience

**Découverte.** `service.jpg` compose l’accueil avec un grand titre Barlow Condensed, l’accès à la bibliothèque et à la voiture, puis la recherche. Une entrée distincte ouvre le guide de préparation d’une vidange. Six guides essentiels sont mis en avant ; Mécanique, Pilotage et Sim racing conduisent aux catégories existantes. Les sélections vidéo respectent leurs données et états éditoriaux.

**Recherche et contexte.** Le formulaire unique passe entre accueil, résultats desktop et feuille mobile. La langue du contenu reste indépendante de la langue FR/EN/ES du site. Formats Tout/Vidéos/Guides, voiture et filtres restent accessibles. La scène d’accueil est masquée en mode résultats.

**Filtres.** Un panneau natif commun présente préférences de contenu, plateformes, sujets et critères avancés. Il devient plein écran sur mobile. Les changements agissent immédiatement ; « Voir N résultats » ferme le panneau sans prétendre appliquer un brouillon. Chargement et indisponibilité ne sont pas un total confirmé.

**Résultats.** Grille sombre : trois colonnes à 1280 px, deux à 1100 px et moins, une à 760 px et moins ; quatre à partir de 1600 px dans le CSS courant. Les cartes associent miniature, titre, sujet, langue, aperçu disponible, auteur et plateforme. « Comprendre ces résultats » regroupe interprétation et guide conseillé. Les mentions de véhicule restent des mentions.

**Vidéo.** Lecteur sombre avec média dominant, titre, auteur et informations disponibles. Lecture intégrée sur action lorsqu’elle est possible ; lien source explicite. Contenu, transcription et notes gardent leurs zones. Une transcription absente conserve son état d’absence. Sur téléphone, le dialogue occupe l’écran disponible.

**Guide.** Le lecteur distingue le document RaceLink, ses prérequis, sa méthode générale et les notices constructeur. Les onze guides et vingt et une références existants sont conservés avec leurs véhicules, éditions et limites. Les commandes sont traduites ; les textes documentaires français restent identifiés. Le cadrage vertical de l’accueil ne change pas leur portée.

## Accessibility & Inclusion

Champs, boutons, dialogues et disclosures natifs restent les fondations. La source prévoit focus visible, commandes de rangées, états de chargement, mouvement réduit et zones sûres mobiles. Les images ne remplacent pas les labels.

**Ces dispositions ne valent pas validation V21.** Les parcours question → langue → suggestion → filtre → fiche → retour, les largeurs 320/390/768/1280, les contrastes, titres longs, images absentes et retours de focus restent à vérifier sur la nouvelle composition. Les preuves d’une version précédente ne sont pas transférées à celle-ci. Aucun audit exhaustif d’accessibilité n’est revendiqué ici.

## Content, Sources & Rights

Cette refonte n’ajoute pas de vidéos, procédures, transcriptions ou compatibilités. Descriptions natives, extraits indexés et textes autorisés gardent leur provenance. L’accès public reste distinct d’une licence libre.

Les photographies, auteurs et licences figurent dans [le manifeste photo](public/photo-sources.json) et [les crédits](public/photo-credits.html). Le VIN illustré a été modifié par son auteur. Le recadrage ne prouve pas un geste correctement exécuté.

MasterClass, le guide Netflix Tudum et Domestika ont été vus par l’agent racine en captures ; aucune connexion à un compte Netflix n’est impliquée. Leurs principes sont adaptés ; leurs médias ne sont pas incorporés à l’application. La [recherche GitHub](research/cinema-v21/prompt-research.md) documente les instructions lues et leurs limites.

## Anti-references, Evidence & History

Écartés : simple recoloration de V20, sidebar permanente de filtres, deuxième formulaire, modale intermédiaire, photos uniformément teintées, résumés fabriqués et lecture automatique.

Le brief proposait un accueil entièrement centré sur une ressource. La réalisation l’adapte en une photographie d’univers avec une entrée séparée vers un guide réel : différence explicitée dans les [décisions](research/cinema-v21/DESIGN-DECISIONS.md). Les tests, la revue du rendu et la publication sont consignés dans la validation V21.

Historique : [produit V20 archivé](research/product-redesign-v20/PRODUCT-snapshot-v20.md), [design V20 archivé](research/product-redesign-v20/DESIGN-snapshot-v20.md), [validation V20](research/product-redesign-v20/VALIDATION.md). RaceLink, MotionSite et Flowith restent des [références historiques V17](research/visual-direction-2026-10-23/design-contract.md), sans nouvelle visite revendiquée. L’intégration au domaine Focus reste distincte d’une publication GitHub Pages.
