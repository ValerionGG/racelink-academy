# RaceLink Academy — Atelier V19d

**Version `atelier-v19d` publiée et vérifiée, 23 octobre 2026.** [Ouvrir RaceLink Academy](https://valeriongg.github.io/racelink-academy/?release=atelier-v19d). Commit de code [`850e57869e9ad9219c054000c8e7b46718835a25`](https://github.com/ValerionGG/racelink-academy/commit/850e57869e9ad9219c054000c8e7b46718835a25), [workflow de publication 39993178520 réussi](https://github.com/ValerionGG/racelink-academy/actions/runs/39993178520). La [validation détaillée](research/graphic-redesign-v19/VALIDATION.md) précise la portée des contrôles par version. Les valeurs et règles de la source courante sont dans [DESIGN.md](DESIGN.md).

## Register

product

## Users

Du débutant au professionnel : une personne cherche sur téléphone près de sa voiture, ou explore sur ordinateur un sujet de mécanique, pilotage, simulation ou métier. Elle doit pouvoir comprendre le sujet et la provenance avant d'ouvrir la ressource. Les informations inconnues de véhicule, niveau ou langue restent inconnues.

## Product Purpose

Trouver une ressource utile, comprendre sa source et ses limites, la consulter puis retrouver sa recherche. La langue des contenus et les précisions du véhicule sont explicites ; la langue du site demeure indépendante. Les parcours, sélections et sujets aident à découvrir, sans devenir une étape obligatoire.

## Brand Personality

Une bibliothèque éditoriale automobile, claire et photographique. La continuité RaceLink conserve Onest pour lire, Orbitron pour la marque, noir/blanc/rouge et des images de terrain. V19 renouvelle réellement la composition : **header horizontal sans sidebar fixe**, texte et recherche sur fond clair à gauche, gros plan `oil.jpg` à droite. Le papier devient `#f5f5f4`, l'encre `#17181a`, le header `#111214` et le rouge d'action `#bb1830`. Ces valeurs effectives remplacent les propositions préparatoires ; les observations du rendu sont consignées séparément dans la validation.

Les surfaces de lecture restent claires, les photographies naturelles et les titres hors image. La présence d'une personne, d'une marque de produit ou d'un véhicule dans une photo n'implique aucun partenariat ni recommandation.

## Design Principles

- **Chercher immédiatement.** L'accueil associe titre, recherche, langue et photographie. Sur mobile, texte/recherche/langue précèdent la photo ; l'accueil français a été contrôlé à 390 px sur V19d.
- **Donner une vraie surface aux images.** Hero mobile 16:10, portes de catégories 4:3, cartes de ressources 16:9. Les vidéos conservent leur propre miniature ; les guides ont leurs illustrations et crédits.
- **Adapter la grille à l'espace réel.** Filtres latéraux du catalogue conservés, deux colonnes généreuses à 1280 px selon le calcul source, une colonne mobile. Les catégories gardent de grandes cartes et des commandes de rail natives.
- **Lire avant de décorer.** Accueil à 62 px desktop, 43 px mobile et 37 px jusqu'à 360 px ; titres vidéo 22 px et guides 23 px hors ruptures spécifiques. Les détails exacts sont dans DESIGN.md ; les observations ne constituent pas un contrôle exhaustif de tous les titres et badges.
- **Conserver le contexte.** Langue, saisie, véhicule et filtres ne disparaissent pas lors d'une suggestion, d'une ouverture de fiche ou d'un retour.
- **Rendre les sources accessibles.** Une sélection éditoriale explique sa raison ; aucun badge ne certifie le contenu technique.

## Core Experience

**Navigation.** Header noir de 80 px sur ordinateur et 70 px sur mobile. Quatre destinations desktop : Accueil, Bibliothèque, Parcours, Enregistrés. La classe historique `.app-sidebar` devient une barre de sujets horizontale dans le flux ; elle ne réserve plus de colonne. Sur téléphone, navigation basse Accueil / Rechercher / Parcours / Enregistrés. Véhicule et FAQ restent accessibles.

**Accueil.** Recherche claire dans la colonne gauche, photo mécanique `oil.jpg` à droite, puis portes Entretien / Pilotage / Sim racing. Un nouveau bandeau photographique `wheel.jpg`, sombre et contrasté, donne accès directement aux guides. La sélection documentée suit ; pas de compteur promotionnel ou de navigation supplémentaire imposée.

**Recherche et catalogue.** Le catalogue masque le hero. Recherche, langue, voiture, formats et filtres précèdent les résultats. Sur mobile, le formulaire unique est déplacé dans un dialogue natif : langue visible, saisie et critères conservés, suggestions par format/titre/provenance. Le changement de langue ne doit pas fermer la feuille. Le site FR/EN/ES et la langue des vidéos sont deux choix distincts.

**Guides.** Onze guides et vingt et une références constructeur conservés. Le lecteur commun ajoute une photographie après le titre, puis méthode générale, informations à réunir, références et limites. Photo de 280 px de haut desktop, 16:9 mobile. Chaque notice garde son véhicule, édition ou périmètre ; les portails restent distingués des procédures directes. Aucun véhicule compatible n'est déduit d'une couverture.

**Parcours V19d.** Les huit disciplines sont présentées en lignes éditoriales, sans blocs d'icônes visibles. Sur ordinateur, titre, description et action s'alignent ; sur mobile, ils s'empilent pour rester lisibles. Chaque ligne entière est un bouton natif qui ouvre le parcours. Les quatre étapes, les ressources associées et le suivi personnel restent accessibles ; ce suivi ne délivre pas de certification.

## Accessibility & Inclusion

Contrôles HTML natifs, labels, focus visible et retour du focus restent des invariants. Les vérifications couvrent des parcours précis de recherche, de consultation des guides et de navigation, détaillés ci-dessous. Préserver les commandes de rail à leur limite et lors des changements responsive. Champ de recherche et sélecteur de langue à 16 px sur téléphone.

Le mouvement confirme l'action : pression 150 ms, couleurs des boutons 180 ms, zoom de photo 1,025 au survol avec transition 300/400 ms selon le composant. La préférence de mouvement réduit supprime les animations non essentielles ; pas d'autoplay ou de cascade d'apparition des résultats.

**Portée des vérifications.** V19/V19b : recherche française, suggestions au clavier et filtre YouTube. V19c : guides photographiques, accès aux sources et focus, parcours en lignes sur ordinateur et mobile, accueil anglais sur tablette. V19d : accueil français à 390/1280 px, menu 320 px à l'origine `(0, 0)` et onglets avec `clientWidth = scrollWidth = 273 px`. Les contrôles automatisés comptent 14 tests HTML et 6 tests d'export sur V19d, ainsi que 17 tests de navigation sur V19c. Les [observations navigateur](research/graphic-redesign-v19/browser-checks.json) et le [contrôle des fichiers publics](research/graphic-redesign-v19/public-assets-check.json) conservent les preuves.

**Limites.** Toutes les pages et tailles n'ont pas été rejouées sur V19d. Les fenêtres mobiles sont émulées : aucun appareil physique, texte agrandi ou zoom système, réglage OS de mouvement réduit, lecteur d'écran ou audit WCAG exhaustif n'a été testé. Les sources constructeur restent celles de la recherche antérieure, sans nouvelle vérification de leur contenu externe pendant la passe UI.

## Content, Sources & Rights

Les résumés éditoriaux, légendes natives, extraits indexés et transcriptions gardent des libellés distincts. Une langue estimée ne devient pas une déclaration de la plateforme. Un référencement ne signifie pas visionnage complet ; un guide général ne remplace pas la notice du véhicule.

Les **douze JPG locaux** mesurent 960 px de large, sauf le diagnostic à 1280 px. Les captures publiées montrent les cadrages des vues examinées ; elles ne couvrent pas toutes les photos à toutes les tailles. Le [manifeste photo](public/photo-sources.json) et [les crédits](public/photo-credits.html) conservent auteur, source et licence Pexels, Unsplash, CC BY, CC BY-SA ou domaine public selon l'image. Les couvertures ne sont jamais des preuves de compatibilité. Le VIN illustré a été modifié par son auteur.

Onest et Orbitron sont chargées via Google Fonts avec repli système ; aucune nouvelle fonte locale ou bibliothèque graphique n'est requise. Le catalogue, ses preuves et ses compteurs ne sont pas modifiés par cette refonte.

## Anti-references, Evidence & History

Rejetés : petites vignettes latérales, affiches vertes, grandes icônes décoratives, teinte générale des photos, longs textes promotionnels avant les résultats et fausse impression de certification. Les références MotionSite ne justifient ni une copie d'actifs ni des animations permanentes.

La filiation avec le [site RaceLink](https://racelink-app.co/) et les aperçus MotionSite Driven/Hyperion repose sur les **inspections historiques V17**, dont les [preuves et décisions](research/visual-direction-2026-10-23/design-contract.md) restent attribuées. La consultation réelle de Flowith avec Claude Opus 5.5 appartient à cette même étape : [brief et portée](research/visual-direction-2026-10-23/flowith-opus-5-5.md). Aucune nouvelle visite de ces références ni génération n'est revendiquée pour V19.

Le [contrat préparatoire V19](research/graphic-redesign-v19/design-contract.md) et [son handoff](research/graphic-redesign-v19/implementation-handoff.md) documentent le choix initial ; DESIGN.md est synchronisé avec les valeurs finalement codées, notamment le rouge `#bb1830`, le header 80/70 px et le hero mobile 16:10.

Historique : [V14](research/ui-redesign-2026-10-23/VALIDATION.md), [photos V15](research/photo-covers-2026-10-23/VALIDATION.md), [guides V16](research/official-guides-2026-10-23/VALIDATION.md), [photographie V17](research/visual-direction-2026-10-23/VALIDATION.md), [douze ressources et interactions V18](research/skills-roundup-2026-10-23/README.md). Leurs tests ne valident pas automatiquement V19. L'intégration dans le domaine Focus reste distincte d'une publication GitHub Pages.
