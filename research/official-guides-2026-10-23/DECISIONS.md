# Guides officiels et lecture mobile — décisions du 23 octobre 2026

La capture mobile transmise montrait deux problèmes concrets : la recherche persistante s’ajoutait à l’en-tête noir et passait devant le compteur et le tri ; les guides occupaient de longues cartes verticales avant de laisser apparaître les ressources suivantes. Cette itération réduit ces obstacles et rend les documents constructeur accessibles depuis le même lecteur que la méthode RaceLink.

## Une liste mobile plus lisible

La barre recherche/filtres du catalogue revient dans le flux de la page. L’en-tête reste la seule couche persistante en haut ; la navigation basse conserve l’accès à la recherche. Le compteur, le tri et les critères ne doivent plus passer sous une seconde barre fixe. Les contrôles existants sont conservés : aucune duplication de formulaire ni de filtre mobile.

Les guides gardent les photographies réelles de la direction visuelle RaceLink, mais adoptent une composition compacte sur téléphone : vignette, titre lisible, résumé court et accès au guide. Le titre n’est pas imprimé une seconde fois sur l’image. La photo reste une illustration, avec crédit et licence consultables dans le lecteur ; elle ne prouve ni une procédure ni la compatibilité d’un véhicule.

Chaque guide reçoit un `cardSummary` de 77 à 105 caractères. Ce texte présente l’utilité de la fiche sans remplacer son introduction complète. La liste normalisée utilise ce résumé comme `description`, tandis que le lecteur conserve `guide.intro` et les étapes originales.

## Un lecteur partagé, deux niveaux d’information

La bibliothèque, les raccourcis de contexte et l’atelier ouvrent désormais le même lecteur par l’identifiant du guide. L’atelier montre un aperçu et un bouton d’ouverture, au lieu de maintenir une seconde version complète de l’article dans un bloc dépliable. Cela évite des contenus et des interactions divergents entre les deux accès.

Le lecteur distingue explicitement :

- **La méthode RaceLink** : les informations à réunir, les questions à poser et les contrôles à effectuer pour retrouver une procédure applicable. Ce sont des repères éditoriaux généraux.
- **Les références constructeur directes** : des sections de notices ou de documentation effectivement consultées, avec constructeur, modèle/version, édition ou période connue, section concernée, date de vérification et limites.
- **Les autres sources et portails** : documents de référence et portes d’entrée pour trouver sa propre notice. Un portail de sélection n’est pas présenté comme une procédure déjà vérifiée pour le véhicule de l’utilisateur.

Les liens directs ouvrent le document d’origine. Le compteur de références constructeur est distinct du nombre total de sources : `source_count` compte toutes les sources validées, tandis que la présentation des références constructeur utilise leur type documenté. La disponibilité d’une page publique n’ajoute aucun droit de réutilisation de son contenu.

## Enrichissement documentaire

Les deux lots de recherche ajoutent **21 entrées de source** aux **11 guides** existants. Le fichier de guides contient maintenant **45 liens sourcés au total**, répartis entre ces fiches ; ce chiffre ne désigne pas 45 documents distincts.

Le [lot A](sources-a.json) couvre huile, préparation de vidange, carburant, essuie-glaces et changement de roue. Le [lot B](sources-b.json) couvre identification, diagnostic, batterie, fusibles, éclairage et rappel d’entretien. Les métadonnées `vehicleScope`, `section`, `summary`, `evidenceNote`, `verifiedAt` et les limites disponibles sont conservées. Les exemples ne créent aucune application véhicule dans les filtres du catalogue.

Les limites sont déterminantes :

- **Vidange** : les sources vérifiées expliquent la préparation, le contrôle du niveau, l’appoint et les documents à retrouver. Aucune procédure constructeur gratuite complète, avec dépose du filtre, bouchon, joint et couples pour un moteur identifié, n’a été validée dans ce lot. Le guide ne promet pas cette couverture.
- **Batterie Tesla** : la procédure de remplacement citée concerne une batterie basse tension plomb-acide en **Amérique du Nord**. La langue française de la page ne la rend pas applicable à une voiture française, ni aux batteries lithium-ion ou de traction.
- **Diagnostic OBD** : la référence Volvo XC90 2025 décrit la prise et les conditions de connexion ; elle ne fournit pas un effacement universel des défauts.
- **Notices et PDF** : les périodes affichées sont conservées sans inventer d’année ou de génération. Les sections PDF Peugeot ont été lues dans le texte extrait ; leurs figures n’ont pas été inspectées visuellement. Le téléchargement PDF Renault non vérifié n’est pas devenu une source validée.

Les [détails de fusion](guide-enrichment-report.json) et la [vérification du lot B](verification-b.md) documentent ces choix.

## Références de design

Les skills **Impeccable** et **Frontend Design** ont été appliqués à cette itération. Impeccable sert à distinguer les besoins d’une interface de recherche de ceux d’une surface de lecture : hiérarchie des commandes, densité utile, focus et séparation entre méthode et sources. Frontend Design soutient une direction RaceLink cohérente, avec photographies, typographie et contrastes maîtrisés, sans remplacer les interactions familières par du décor.

Les sources GitHub consultées sont [pbakaus/impeccable](https://github.com/pbakaus/impeccable) et [Frontend Design dans anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design). Le relevé de cette itération, au **23 octobre 2026**, comptait respectivement **85 258** et **183 187 étoiles**. Ces valeurs sont une photographie datée des dépôts entiers, pas une mesure propre à chaque skill ni un critère unique de sélection. La pertinence des recommandations pour cette interface et leur cohérence avec les contraintes existantes priment.

## Périmètre des données et vérification

Les **36 901 vidéos restent inchangées**. Aucun import, enrichissement ou déplacement de leurs données n’a été effectué pour cette évolution des guides. L’empreinte déterministe de toutes les lignes vidéo, comparée avant et après l’enrichissement avec accès SQLite en lecture seule, est identique : `e86b6c26d4a604292dcbc0674d4b8a09a02bc20124b69a3813bcb5da078920eb`.

Les contrats de guides, la conservation des champs dans le Worker et l’export temporaire sans changement des vidéos sont consignés dans [validation-results.json](validation-results.json). Les autres contrôles automatisés sont répertoriés dans [tests.json](tests.json). Cette note ne conclut pas à une validation visuelle ou navigateur finale ; les résultats correspondants doivent être consignés séparément une fois ces contrôles terminés.
