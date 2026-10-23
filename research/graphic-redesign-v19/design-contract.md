# Contrat graphique V19 — Atelier éditorial

23 octobre 2026, établi avant l'implémentation V19. Méthode : [reference-design-contract](C:/Users/Nad/.codex/skills/reference-design-contract/SKILL.md), avec sorties adaptées à la mission : ce contrat et le handoff, sans modifier `DESIGN.md` ni `PRODUCT.md`.

**Direction retenue : une ouverture éditoriale claire, une grande photographie de geste mécanique et une bibliothèque généreuse.** Le nouvel accueil juxtapose le texte et la recherche sur fond clair à gauche, la photo réelle `oil.jpg` à droite. L'en-tête noir devient horizontal ; la sidebar permanente disparaît. Sur téléphone, titre, recherche et langue précèdent la photo 16:9. Cette recomposition remplace le hero superposé et le cadre de navigation V18, tout en conservant ses interactions utiles.

Le public va du débutant qui consulte près de sa voiture au professionnel qui cherche une ressource précise. Le parcours principal reste chercher → choisir une source → consulter → retrouver son contexte. Les photographies montrent la matière ; elles ne prouvent aucune compatibilité ou validation technique.

## Preuves, conservation et transformation

| Référence | Niveau de preuve | Conserver | Transformer | Ne pas copier |
|---|---|---|---|---|
| Demande de refonte complète, grandes photos, noir/blanc/rouge et mobile | `provided` : demande utilisateur et cadrage confirmé par l'agent principal | Priorité photographique et accès direct à la recherche | Nouvelle composition, nouveau rythme et suppression de la sidebar fixe | Les petites vignettes, affiches vertes et pictogrammes décoratifs rejetés |
| RaceLink officiel, MotionSite Driven et Hyperion | `provided` : inspections historiques V17, [captures et matrice](../visual-direction-2026-10-23/design-contract.md) ; aucune nouvelle visite | Matière mécanique et contraste de marque | Double page claire, photographie non teintée, action pratique | Images, code, slogans, compteurs, mouvement ou performance non observés |
| RaceLink V18c | `observed` : source actuelle lue ; [validation navigateur historique](../skills-roundup-2026-10-23/VALIDATION.md) attribuée à ses auteurs | Recherche/langue, contrôles natifs, focus, filtres et sources | Header horizontal, hiérarchie de lecture et espace utile | Supposer que les tests V18 valident V19 |
| Actifs locaux et manifeste | `observed` : 12 fichiers et dimensions vérifiés ; pixels de `oil`, `service`, `driving`, `simracing` relus | Photographies existantes, auteurs, crédits et licences | Cadrage adapté à chaque place | Fausse photo de vidéo, fausse procédure ou agrandissement démesuré |

La direction est un choix RaceLink (`inferred`), pas une copie de dimensions mesurées chez MotionSite.

## Palette et typographie

| Rôle V19 | Valeur proposée | Emploi |
|---|---|---|
| Papier | `#f5f5f4` | Fond principal, chaleureux mais neutre |
| Surface | `#ffffff` | Recherche, lecteurs, panneaux et contrôles |
| Encre / bandeau | `#121314` | Titres, texte fort et header noir |
| Secondaire | `#5e6065` | Source, aide, légendes et métadonnées |
| Action | `#c82038` | Bouton principal, liens actifs et focus |
| Marque | `#ff2330` | Trait ou accent ponctuel ; pas petit texte blanc dessus |
| Séparation | `#e1e1e3` | Filets et regroupements discrets |

Contrastes calculés localement, sans prétendre auditer l'interface : encre/papier **17,05:1** ; secondaire/papier **5,77:1** ; action/blanc **5,65:1** ; action/papier **5,18:1**. Blanc/rouge de marque : **3,79:1**, insuffisant pour du petit texte ordinaire.

**Onest** porte titres, texte et commandes. **Orbitron** reste dans la marque et de très courts repères. Titre d'accueil proposé : 48–60 px desktop, 32–38 px mobile ; titres de ressources 21–24 px ; corps 15–16 px ; métadonnées et badges 12–13 px. Ces valeurs sont des objectifs V19, à vérifier avec les vrais textes FR/EN/ES. Pas de titre technique long en Orbitron, ni de réduction silencieuse des titres pour densifier.

## Composition par vue

**Accueil desktop.** Header noir de 64–72 px : marque, Accueil / Bibliothèque / Parcours / Enregistrés, puis recherche et langue du site. Les sujets, véhicule et aide restent accessibles sans menu obligatoire supplémentaire. Dans une largeur de contenu maximale d'environ 1 360 px, l'ouverture comporte deux zones : environ 44 % pour le texte/recherche, 56 % pour `oil.jpg`, séparées par un espace de 32–40 px. Titre court, une phrase, champ blanc puis langue du contenu. La photo garde le bidon, les mains et le filet d'huile ; aucun texte ne recouvre le geste. Son crédit reste accessible. Le champ doit tenir dans le premier écran à 1280 × 720.

Sous cette ouverture : trois grandes portes photographiques **Entretenir / Piloter / Simuler**, titres en dessous. `service.jpg`, `driving.jpg` et `simracing.jpg` donnent trois scènes distinctes. L'accès direct aux guides et la sélection documentée suivent, sans nouvelle séquence promotionnelle. Les rails éventuels gardent leurs commandes natives, leur compteur et leur absence d'autoplay.

**Accueil mobile.** Header allégé et navigation basse existante ; ordre DOM et visuel : titre → aide courte → recherche → langue du contenu → photo réelle 16:9 → grandes catégories. Marges 16–20 px. Recherche et langue restent entièrement visibles au premier écran à 390 × 844 et 320 × 740, sans imposer une introduction ou un défilement animé. L'image n'est pas masquée : à 390 px avec marges de 16 px, son cadre attendu est environ 358 × 201 px. Les catégories restent larges, pas des vignettes latérales.

**Catalogue.** Pas de hero entre la question et les résultats. Recherche modifiable, contexte langue/véhicule, onglets Tout / Vidéos / Guides et filtres actifs précèdent directement la liste. Filtres latéraux conservés sur desktop : deux colonnes de grandes cartes à 1280 px, trois seulement si l'espace utile après filtres et marges le permet. Sur mobile : une colonne et filtres dans le dialogue existant. Ordre des cartes : image 16:9 → type discret → titre → auteur/source/langue connue → action. Un badge de sélection se lit sans masquer l'image et n'implique aucune certification.

**Recherche mobile.** Dialogue natif clair, titre court, fermeture de 44 px ; champ à 16 px, langue des vidéos explicitement libellée, suggestions immédiatement dessous. Chaque suggestion sépare format, titre et provenance disponible. Aucun nouveau formulaire dupliqué, aucun effacement de la saisie ou des critères lors d'un changement de langue. Ne pas ajouter de photographie dans cette feuille : elle sert à trouver rapidement la prochaine ressource.

## Critères de revue et inconnues

- Vérifier accueil, résultats et recherche à **320, 390, 768 et 1280 px** après implémentation ; vérifier une largeur plus grande pour le passage à trois colonnes. Aucune validation V19 n'est acquise ici.
- Contrôler texte agrandi, titres longs, langue FR/EN/ES, focus et clavier ; aucun contrôle sous la barre basse, aucune largeur de document débordante.
- Refaire le parcours V18 : saisir « vidange Clio 3 », choisir Français, ouvrir une suggestion, fermer ; saisie, langue et contexte conservés, focus restauré, recherche non rouverte sans action.
- Ouvrir un guide et ses sources depuis accueil et catalogue ; FAQ et guides restent directement accessibles. La nouvelle navigation ne crée pas un détour obligatoire.
- Aucun autoplay, parallaxe, animation d'entrée de toute la liste ou effet GPU. Garder le mouvement bref existant et sa suppression en mouvement réduit.
- Les JPG locaux mesurent 960 px de large, sauf le diagnostic à 1280 px : netteté à contrôler sur écran dense, sans prétendre disposer d'originaux haute résolution dans l'app. Le cockpit vertical exige un cadrage attentif. Les fontes restent dépendantes de Google Fonts avec repli système.

Le premier résultat doit prouver la recomposition — header horizontal, grande image à droite, recherche claire à gauche puis avant l'image sur mobile — et la conservation du parcours de recherche. Une simple recoloration de V18 ne satisfait pas ce contrat.
