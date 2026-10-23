# Recherche de prompts et brief V21 — RaceLink cinéma

23 octobre 2026. Recherche documentaire GitHub via Agent Reach et `gh`, sans installation, exécution de code externe, modification frontend ou publication. Ce document définit une direction à réaliser ; il ne valide aucun rendu V21.

## Décision proposée

Repenser ensemble **l’accueil, les cartes, la recherche et la fiche**. La référence au streaming apporte une découverte par programmes et une place dominante à l’image. La référence à l’éducation apporte le sujet, le niveau de preuve, la langue et la prochaine action. Assombrir V20 sans changer ces quatre compositions ne répondrait pas à la demande.

La combinaison utile est : **frontend-design pour une composition propre au sujet, Impeccable pour un brief contraint, UI UX Pro Max pour les différences entre streaming et apprentissage, Taste pour la force du contenu réel, baseline-ui pour les interactions**. Aucun dépôt ne fournit à lui seul une preuve de réussite pour RaceLink.

## Méthode et sources vérifiées

Les routes locales `agent-reach/SKILL.md`, `references/dev.md` et `references/search.md` ont été lues. La route utilisée est le CLI GitHub officiel : recherche de dépôts et de code, métadonnées de dépôt, lecture des fichiers sources par l’API GitHub. Exa n’a pas été utilisé.

Requêtes effectuées : `frontend-design`, `design skill`, `netflix education prompt`, `education design prompt`, ainsi que `Netflix path:SKILL.md`. Les trois dernières n’ont pas retourné de résultat dans ces recherches ciblées. Cela ne prouve pas l’absence de prompts spécialisés ailleurs. Les dépôts primaires connus ont ensuite été vérifiés directement.

Les étoiles ci-dessous sont un instantané du 23 octobre 2026 ; elles concernent le **dépôt entier**, et ne constituent pas une validation de qualité ou d’accessibilité.

| Source primaire | Étoiles | Dernier push déclaré par GitHub, UTC | Licence | Lecture utile |
|---|---:|---|---|---|
| [Anthropic Skills](https://github.com/anthropics/skills) | 183 253 | 9 octobre 2026, 18:45 | Apache-2.0 pour `frontend-design`, vérifiée dans son fichier de licence ; licence racine non renseignée dans l’API | `SKILL.md` complet |
| [Impeccable](https://github.com/pbakaus/impeccable) | 85 425 | 23 octobre 2026, 19:10 | Apache-2.0 | Références `shape.md` et `bolder.md` complètes |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 139 373 | 23 octobre 2026, 10:06 | MIT | `SKILL.md` complet et entrées E-learning / Video Streaming de `products.csv` |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill) | 101 552 | 20 octobre 2026, 22:04 | MIT | Passages ciblés du skill et de `app-screens.md` |
| [UI Skills — baseline-ui](https://github.com/ibelick/ui-skills) | 10 104 | 20 octobre 2026, 21:11 | MIT | `baseline-ui/SKILL.md` complet |
| [Huashu Design](https://github.com/alchaincyf/huashu-design) | 25 892 | 23 octobre 2026, 15:32 | MIT | `cinematic-patterns.md` complet, recette écartée pour cette application |

Les liens de fichiers ci-dessous figent les versions réellement examinées. Aucune copie de ces skills n’a été installée pendant cette recherche. Aucun script de génération de design n’a été lancé.

## Ce que les instructions changent concrètement

### 1. Frontend-design : partir du sujet, pas d’un gabarit

Le [fichier Anthropic](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md) privilégie une identité issue du matériau réel, une structure qui exprime l’information, puis une confrontation entre l’intention et le rendu. Il déconseille la décoration qui ne porte aucun sens. Sa [licence propre](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/LICENSE.txt) est Apache-2.0.

**Application :** remplacer le hero générique par une véritable sélection RaceLink identifiable : image, sujet précis, auteur et action. Le visiteur doit déjà rencontrer une ressource dans l’accueil, pas seulement une promesse d’apprentissage. Réserver la mise en scène la plus forte à cette sélection, puis rendre les rayons faciles à parcourir.

**Exemple :** « Comprendre le moteur, texte à l’appui » est déjà une collection réelle de `discovery-catalog.json`. Une ressource de cette collection peut former le programme principal si sa miniature convient. Son titre, sa durée et sa transcription doivent venir de l’enregistrement, sans les déduire du thème du rayon.

La liste de styles déconseillés du skill n’annule pas la marque demandée : le rouge et le noir RaceLink restent intentionnels. Pas de migration de police pour donner artificiellement l’impression d’une nouveauté.

### 2. Impeccable : définir le travail avant d’amplifier le style

[Shape](https://github.com/pbakaus/impeccable/blob/b29942e5d98b3182d0346dd205f48fbd424fdbe8/.agents/skills/impeccable/reference/shape.md) demande de préciser le besoin, le contenu réel, les états, les limites et l’organisation des interactions. [Bolder](https://github.com/pbakaus/impeccable/blob/b29942e5d98b3182d0346dd205f48fbd424fdbe8/.agents/skills/impeccable/reference/bolder.md) invite à renforcer un choix structurant sans ajouter du bruit partout ; il distingue l’amplification d’un système existant d’une direction réellement nouvelle.

**Application :** V21 doit avoir trois vues conçues séparément : découverte, recherche, lecture. Le hero n’est pas un simple composant ajouté au-dessus de V20. En recherche, il disparaît pour laisser place aux résultats. Dans la fiche, le lecteur devient la zone dominante.

**Vérification :** comparer des captures V20/V21 avec les textes floutés mentalement. Si les mêmes grands rectangles, la même densité et la même succession de blocs demeurent, la composition n’a pas été refondue. Ce contrôle est une recommandation de revue, pas un test effectué ici.

### 3. UI UX Pro Max : séparer découverte vidéo et progression pédagogique

Le [skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/d14efff8ed1faa4187f004f79926f428c8074ec7/.claude/skills/ui-ux-pro-max/SKILL.md) et ses [données produits](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/d14efff8ed1faa4187f004f79926f428c8074ec7/.claude/skills/ui-ux-pro-max/data/products.csv) distinguent les écrans de streaming, fondés sur les visuels et la découverte, des plateformes de cours, fondées sur des parcours et une progression.

**Application :** emprunter au streaming les grandes couvertures, la hiérarchie des programmes et les rangées thématiques. Emprunter à l’éducation les prérequis, l’objectif, la langue, la présence éventuelle d’un texte et les références constructeur.

**À écarter :** le vert de progression, la gamification, les badges de cours terminés, les certificats, « Reprendre » ou les recommandations personnelles sans données correspondantes. La ligne E-learning propose des choix visuels génériques qui ne conviennent pas à la demande RaceLink. La ligne streaming ne justifie ni une animation permanente ni une vidéo automatique.

### 4. Taste : remplacer les petits ornements par un contenu plus fort

Les passages examinés du [skill Taste](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/SKILL.md) défendent un matériau réel, une image dominante et une composition liée au produit. La référence [App screens](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/references/app-screens.md) distingue ses observations desktop de ses règles mobiles proposées : elle ne constitue donc pas une étude empirique des téléphones.

**Application :** une grande miniature informative vaut mieux qu’une accumulation d’étiquettes et de petits pictogrammes. Garder la langue, l’auteur et la provenance à proximité du titre. Retirer un badge ne suffit pas : l’espace gagné doit profiter à l’image, au titre et à la compréhension du contenu.

**Exemple :** une carte vidéo montre sa véritable miniature en 16:9, un titre lisible et deux lignes maximum de contexte attribué lorsqu’il existe. Une photo d’illustration de mécanique ne devient jamais la miniature prétendue d’une vidéo.

### 5. Baseline-ui : garder une interface utilisable sans survol

[Baseline-ui](https://github.com/ibelick/ui-skills/blob/55363c305097d4c84487bd5f323d29b3f067bf72/skills/baseline-ui/SKILL.md) apporte des garde-fous sur les labels, le focus, les zones sûres mobiles, les états vides, les couches et le mouvement réduit. Ses prescriptions de bibliothèques React/Tailwind ne s’appliquent pas à cette application JavaScript native.

**Application :** les cartes ne doivent pas nécessiter un survol pour révéler leur titre ou leur action. Les rangées gardent leur défilement natif et leurs boutons clavier. La recherche mobile conserve son texte lorsqu’une langue est choisie ; son panneau respecte la hauteur disponible et la zone sûre inférieure. Le focus revient à l’origine après fermeture d’une fiche.

### 6. Un résultat « cinematic » qui n’est pas une solution streaming

La référence [Cinematic patterns de Huashu](https://github.com/alchaincyf/huashu-design/blob/4fc7bfdbd5ec3fa2d43ce7a6433de60976a5e4b1/references/cinematic-patterns.md) décrit surtout une démonstration animée de processus, avec scènes, son et effets. Ce n’est pas un parcours de recherche pédagogique.

**Écarté :** intro scénarisée, musique, effets sonores et overlays de démonstration qui retarderaient la recherche. Le seul principe transférable est que le contenu utile doit exister sans lancement de l’animation. Le mot « cinéma » dans un fichier n’est pas un critère suffisant pour adopter sa recette.

## Prompt V21 prêt à utiliser

> Concevez et implémentez une véritable nouvelle composition RaceLink Academy, inspirée de la découverte des plateformes vidéo et de la clarté des plateformes d’apprentissage. La marque reste RaceLink : rouge, noir, blanc, Onest pour la lecture et accents Orbitron mesurés. Ne copiez aucun logo, visuel ou élément propriétaire Netflix. Le résultat doit ressembler à une bibliothèque éditoriale de mécanique et de sport automobile, pas à un tableau de bord SaaS.
>
> **Résultat attendu :** un accueil, des résultats, des cartes et une fiche visiblement différents de V20. Une simple modification de couleurs, de rayons ou d’arrondis ne suffit pas. Utilisez des grandes photos réelles et les miniatures réellement associées aux vidéos. Les illustrations de navigation restent distinctes des miniatures et conservent leurs crédits.
>
> **Accueil — découvrir des programmes.** Construisez une scène principale sombre autour d’une ressource ou sélection éditoriale réelle. L’image est dominante ; le titre et l’auteur sont identifiables ; le contenu n’est pas couvert par un long slogan. Une action principale ouvre la fiche. La recherche demeure accessible dès le premier écran, sans intro et sans lecture automatique. Utilisez un seul formulaire existant, pas une copie dans le hero. Enchaînez avec des rangées larges qui expriment des besoins réels : « À découvrir en français », « Deux repères pour aborder un virage », « Commencer en simulation », « Comprendre le moteur, texte à l’appui ». Résolvez les éléments de ces collections depuis les données ; ne créez pas de nouveaux titres, auteurs, durées ou statuts.
>
> **Cartes — comprendre avant d’ouvrir.** Grandes images en 16:9, titre lisible de 20–22 px lorsque la place le permet, source/auteur et langue visibles. Montrez la durée uniquement lorsqu’elle est connue. Le contexte explique une utilité réelle ; s’il provient du titre ou de la description, ne le présentez pas comme un résumé de visionnage. La raison de sélection reste accessible. L’action « Voir la fiche » est claire sans être répétée en plusieurs couches. Les guides sont identifiés comme guides, sans symbole de lecture trompeur. Aucun titre ou bouton essentiel ne dépend du survol.
>
> **Recherche — comparer.** Quand une question est lancée, retirez la scène éditoriale. Gardez une ligne de contexte courte : question, voiture, langue, puis accès aux filtres existants. Les résultats utilisent une grille de grandes cartes, deux colonnes à une largeur desktop utile modérée, une colonne sur téléphone ; les résultats ciblés ne deviennent pas un carrousel. Les critères actifs et le nombre réel de résultats sont faciles à lire. Aucun bloc explicatif ne repousse systématiquement la première image sous plusieurs écrans. Les filtres avancés restent dans leur panneau, sans duplication de contrôles.
>
> **Fiche — lire et comprendre.** Donnez au média la place dominante. Le titre, l’auteur et la provenance sont lisibles avant lecture. Distinguez explicitement lecture intégrée disponible et ouverture sur la plateforme. Les zones « En bref », transcription disponible, mentions véhicule et références se lisent sans empilement d’encadrés concurrents. Conservez les limites de compatibilité. Les notices constructeur restent rattachées à leur véhicule et à leur édition ; RaceLink n’est pas présenté comme leur auteur. La fermeture restitue le contexte, la position et le focus du parcours.
>
> **Direction graphique.** Utilisez un fond cinéma encre, des surfaces sombres sobres et un texte clair fortement contrasté. Réservez le rouge RaceLink aux actions et repères. Les couleurs des images donnent de la variété ; n’appliquez pas de teinte verte ou rouge uniforme aux photographies. La nouveauté vient de la taille, de la composition et du rythme éditorial, pas d’ombres lumineuses, de badges inventés ou d’une multitude d’animations. Gardez le lecteur et les textes longs confortables ; mesurez les contrastes au lieu de les supposer.
>
> **Téléphone et accessibilité.** Concevez à 320 et 390 px avant d’étendre à 768 et 1280 px. Une carte doit rester assez large pour comprendre son sujet. Le débordement horizontal est limité aux rangées volontaires, jamais au document. Gardez des cibles d’environ 44 px, des labels explicites et un focus visible. Les boutons de rangées restent utilisables au clavier et gèrent les extrémités. Respectez `prefers-reduced-motion`. Les transitions éventuelles sont brèves et fonctionnelles ; aucune information ne dépend de l’animation. Le changement de langue ne doit pas perdre la saisie.
>
> **Données et architecture.** Réutilisez les contrats d’événements, paramètres URL, filtres, guides, favoris et lecteurs documentés dans `integration-plan.md`. Ne changez pas de framework pour cette refonte. Ne fabriquez pas de popularité, progression, notes, épisodes, disponibilité, recommandation personnelle ou preuve de transcription. Aucun « Reprendre » sans historique fiable. Les contenus absents ont un état explicite, pas une donnée de remplacement trompeuse.
>
> **Livraison et critique.** Fournissez des captures comparables de l’accueil, de la recherche et de la fiche sur ordinateur et téléphone. Évaluez la différence structurelle avec V20, la visibilité de la recherche, la taille réelle des images, la compréhension de la provenance, le clavier et les retours de focus. Vérifiez aussi un titre long, zéro résultat, une image absente et une transcription indisponible. Distinguez les captures inspectées, les contrôles automatisés et les comportements réellement testés.

## Critères de réception proposés

| Intention | Changement observable | Vérification à effectuer après implémentation |
|---|---|---|
| Un vrai changement de composition | Scène de contenu, rayons éditoriaux, grille de comparaison et lecteur dominant ont des rôles distincts | Comparer les trois surfaces V20/V21 aux mêmes dimensions |
| Une découverte plus visuelle | Grandes miniatures réelles ; moins de petits cadres et d’étiquettes | Titre et sujet compréhensibles à 320/390 px, sans survol |
| Une recherche immédiate | Accès visible, contexte question/voiture/langue conservé | Saisie → langue → suggestions → filtre → fiche → retour |
| Une pédagogie honnête | Source, langue, utilité et niveau de preuve lisibles | Échantillon vidéo avec/sans description, transcription et durée |
| Une interface cinéma accessible | Texte contrasté, focus visible, mouvement non obligatoire | Contrastes mesurés, clavier, mouvement réduit, débordements |
| Une refonte sans régression du catalogue | Données et contrats conservés | Suites prévues dans [la préparation technique](integration-plan.md), puis navigateur réel |

## Limites de cette recherche

Cette mission n’a pas utilisé de navigateur et n’a pas évalué visuellement les références Netflix, MasterClass ou Domestika. Les captures de ces produits présentes dans ce dossier relèvent du travail de la racine et de sa documentation. Ce rapport examine des instructions et transforme leurs principes en proposition ; il ne prétend ni avoir suivi un cours, ni avoir visionné une vidéo, ni avoir validé une nouvelle interface.

Le contrôle de mise à jour Agent Reach a indiqué v1.5.0 installée et v1.6.0 disponible. Aucune mise à jour n’a été effectuée ; ce point n’a pas empêché les recherches GitHub en lecture seule.
