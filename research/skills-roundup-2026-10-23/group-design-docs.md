# Awesome DESIGN.md, Google DESIGN.md, OpenDesign et Canvas UI

Vérification du 23 octobre 2026. Métadonnées des dépôts relevées vers 16:02 UTC. Route utilisée : Agent Reach → GitHub CLI (`gh search` et `gh api`), complétée par la consultation de pages primaires. À la suite de la recherche, installation ciblée d'un skill par le helper officiel et application documentaire autorisées ; aucun code de skill exécuté, aucune modification du frontend ou publication.

**Pour RaceLink, la combinaison utile est : une spécification visuelle commune, des principes de composition photographique et un contrat de revue explicite.** Ces quatre ressources ne sont pas quatre skills interchangeables. Leur popularité ne prouve ni leur qualité, ni leur adéquation à notre bibliothèque HTML/CSS/JS.

## Identités vérifiées

| Nom demandé et ressource identifiée | Étoiles constatées le 23/10 | Dernier commit de la branche par défaut | Nature et licence | Décision pour RaceLink |
|---|---:|---|---|---|
| [Awesome DESIGN.md — VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md), site déclaré `getdesign.md` | 123 114 | 14/10/2026, `3b605329240c` | Collection d'analyses de systèmes visuels ; MIT ; aucun `SKILL.md` dans l'arbre examiné | Consulter des références ciblées, sans installer la collection comme un skill |
| [DESIGN.md — google-labs-code/design.md](https://github.com/google-labs-code/design.md), documentation Google Stitch | 28 498 | 16/10/2026, `6e5da5382f41e` | Spécification de format et CLI ; Apache-2.0 | Retenir le format et la séparation valeurs/règles ; le CLI est facultatif |
| [OpenDesign — nexu-io/open-design](https://github.com/nexu-io/open-design), site déclaré `open-design.ai` | 103 544 | 22/10/2026, `e03d5c23f308` | Application de conception et catalogue de skills ; Apache-2.0 à la racine, licences propres conservées pour les composants tiers | Lire un workflow précis ; ne pas ajouter toute l'application à RaceLink |
| [Canvas UI — DavidHDev/canvas-ui](https://github.com/DavidHDev/canvas-ui), site déclaré `canvasui.dev` | 5 070 | 03/10/2026, `a04a99b23529` | Bibliothèque d'effets WebGL/WebGPU ; **MIT + condition Commons Clause**, pas MIT seul ; aucun `SKILL.md` | Pas de dépendance pour les cartes, la recherche ou les procédures |

Les noms, descriptions, domaines et README concordent pour ces projets. **Le rattachement exact des cartes « Open Design » et « Canvas UI » de la capture reste non confirmé faute de domaine/auteur lisible dans mon sous-travail.** Il existe notamment des homonymes Mozilla OpenDesign, Alibaba canvas-ui et CanvasUI pour interfaces 3D. Les identités ci-dessus sont vérifiées ; leur correspondance à ces deux cartes reste une hypothèse explicite.

Les SHA complets, réponses API, arbres non tronqués, dates et empreintes des fichiers sont conservés dans `group-design-docs-manifest.json` et `sources-design-docs/`. Les dates de commit du tableau ne sont pas les dates de dernière activité de toutes les branches.

## Ce que les documents apportent réellement

### 1. Awesome DESIGN.md : laisser les photographies porter la composition

Les sections composition, composants, responsive et limites des analyses [BMW M](https://github.com/VoltAgent/awesome-design-md/blob/3b605329240ce735b510037cca322f1831fdd7f8/design-md/bmw-m/DESIGN.md) et [Airbnb](https://github.com/VoltAgent/awesome-design-md/blob/3b605329240ce735b510037cca322f1831fdd7f8/design-md/airbnb/DESIGN.md) ont été consultées. BMW M décrit des photographies occupant toute la largeur de leur carte, un texte placé en dessous et une réduction du nombre de colonnes sur mobile. Airbnb sépare le visuel réutilisable du bloc de métadonnées et fait cohabiter la recherche avec une grille photographique.

Application proposée : conserver les vraies photos des guides et les miniatures propres aux vidéos ; garder le titre et les informations utiles sous l'image ; laisser la recherche atteindre directement les résultats. Le choix du nombre de colonnes doit partir de l'espace restant après la sidebar. Le `PRODUCT.md` actuel prévoit déjà une largeur utile d'environ 330 px par carte, deux colonnes à 1280 px dans le cadre actuel et une seule sur mobile : ce contrat local prime sur une grille copiée du document BMW.

Ces textes sont **des analyses publiées par VoltAgent, pas des chartes officielles de BMW ou Airbnb**. Leur licence MIT ne donne pas de droits sur les photographies, logos ou polices des marques. Certaines recommandations sont très propres à une marque, et le document BMW déclare des lacunes sur les interactions. On ne reprend donc ni ses actifs, ni ses prescriptions typographiques, ni sa consigne de ne pas documenter le survol : RaceLink doit conserver ses états clavier, focus et erreur.

### 2. Google DESIGN.md : rendre les décisions persistantes et contrôlables

La [spécification complète](https://github.com/google-labs-code/design.md/blob/6e5da5382f41edbba9d73b2c62f33f32e9971f15/docs/spec.md) a été lue. Elle distingue des valeurs de design structurées en YAML, qui font autorité, et une explication Markdown de leur emploi. Elle décrit couleurs, typographie, espacement, formes, composants et variantes d'état. Le format est encore **alpha**. Les sections inconnues sont conservées ; les doublons de rubriques ou de clés YAML sont des erreurs.

Application proposée : enrichir le `DESIGN.md` déjà présent, sans créer une seconde charte concurrente. Documenter des valeurs sémantiques pour fond de lecture, texte, accent RaceLink, focus, espacement et rayon ; préciser les règles des images et les variantes mobile. Dans notre app sans framework, on peut les reporter dans les variables CSS existantes. Les exports annoncés par le CLI concernent notamment Tailwind/DTCG ; ils ne justifient pas une migration technique. Le lint des valeurs ou des contrastes ne remplace pas une observation du rendu à 320 et 390 px. [README du projet](https://github.com/google-labs-code/design.md/blob/6e5da5382f41edbba9d73b2c62f33f32e9971f15/README.md).

Les quatre `SKILL.md` internes de ce dépôt concernent son développement — CLI, Ink, TDD, contrats de services — et ne sont pas des skills de direction artistique à installer pour cette tâche.

### 3. OpenDesign : transformer une référence en décisions vérifiables

Le [vrai skill `reference-design-contract`](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/skills/reference-design-contract/SKILL.md) et sa [checklist](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/skills/reference-design-contract/references/checklist.md) ont été lus intégralement. Ils demandent de distinguer observations, informations fournies et inférences ; de noter ce que l'on conserve, transforme et exclut d'une référence ; puis de transmettre une direction unique avec critères d'acceptation. Cela convient directement aux références RaceLink et MotionSite sans copier leurs actifs.

Deux limites importantes ont été vérifiées :

- [`design-review`](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/skills/design-review/SKILL.md) et [`design-md`](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/skills/design-md/SKILL.md) sont des fiches de catalogue renvoyant à un autre dépôt, **pas les workflows complets**. Le lien amont `google-labs-code/skills` de cette dernière a répondu 404 lors du contrôle GitHub ; aucune installation ne peut être présentée comme vérifiée à partir de ce lien.
- Le skill de contrat impose neuf titres OpenDesign, tandis que le [protocole actuel](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/docs/skills-protocol.md) précise que ces neuf titres ne sont plus le schéma obligatoire des paquets. Ils diffèrent aussi du format Google. Retenir la méthode de décision, puis choisir **un seul** format de document. Ne pas imposer simultanément les trois conventions.

**Installation ciblée effectuée à la demande de l'utilisateur**, par le helper officiel `skill-installer`, chemin `skills/reference-design-contract`, au SHA audité `e03d5c23f308c39f4de7c057568df66c29a84385`, méthode téléchargement et sans écrasement. Destination : `C:/Users/Nad/.codex/skills/reference-design-contract/`. Le dossier contient le skill, une checklist, un exemple HTML et la licence Apache-2.0 racine préservée ; aucun script. Le `SKILL.md` installé est identique au texte audité, SHA-256 `56d5e0c077263cd30f586ffa763fec5caebdee2821fa9653e86c3376b937e222`.

Ses références `od.craft.requires` dépendent de trois fichiers externes au dossier (`craft/typography.md`, `craft/color.md`, `craft/anti-ai-slop.md`) : elles ont été lues intégralement et archivées. Une installation Codex ne reproduit pas leur injection par OpenDesign. Leurs règles stylistiques arbitraires ne remplacent pas le brief ni l'accessibilité. La méthode du workflow est appliquée dans `reference-contract.md`, avec adaptation explicite de ses sorties pour préserver le document RaceLink existant. Aucun launcher OpenDesign ou commande de son README n'a été exécuté. Le nouveau skill sera disponible dans le catalogue de l'agent au prochain tour.

### 4. Canvas UI : des effets facultatifs, pas la structure du produit

Les textes sources des pages [Installation](https://canvasui.dev/docs/installation) et [Rendering](https://canvasui.dev/docs/rendering) ont été lus, avec leur version épinglée dans les preuves. La variante vanilla existe, mais elle est distribuée en TypeScript. Certains effets utilisent l'API expérimentale HTML-in-canvas : les documents prévoient un drapeau de navigateur ou un origin trial propre au domaine, et un retour au HTML normal sans support. Les constructions WebGPU ajoutent une dépendance ; leurs promesses de compatibilité n'ont pas été testées ici sur appareils.

La [licence exacte](https://github.com/DavidHDev/canvas-ui/blob/a04a99b235299ee79a123a16ccb2e6cf9da74b6b/LICENSE.md) autorise l'intégration dans une application en conservant les mentions, mais interdit la vente, sous-licence ou redistribution des composants eux-mêmes, y compris en bundle ou portage. Le champ GitHub retournait `NOASSERTION` : le texte de licence a donc été consulté plutôt que d'en déduire un MIT standard.

Pour RaceLink, aucune déformation GPU sur les miniatures, les textes de procédure ou les commandes de recherche. Un éventuel effet décoratif isolé devrait préserver le HTML, le zoom, le focus et la réduction des animations, et démontrer son intérêt sur mobile. Ce n'est pas nécessaire pour obtenir de grandes images lisibles.

## Handoff opérationnel

1. **Conserver la charte RaceLink courante** et y inscrire les contraintes qui viennent de l'utilisateur : photos réelles, images généreuses, mobile à une colonne, lecture claire, noir/rouge/blanc et continuité de la recherche.
2. **Spécifier trois composants photographiques distincts** : entrée de catégorie, guide éditorial avec crédit, vidéo avec sa propre miniature. Le cadre ne doit pas faire passer une photo d'illustration pour une image extraite de la vidéo.
3. **Évaluer le cadrage au cas par cas.** Préserver l'objet utile — roue, batterie, moteur — et ne pas assombrir uniformément toutes les images pour y superposer des titres. Les titres restent en dessous.
4. **Construire un contrat de revue observable**, inspiré d'OpenDesign : image lisible, titre compréhensible, source accessible, recherche immédiatement utilisable, filtres conservés, cibles tactiles confortables, focus visible et absence de débordement à 320/390 px. Ces points sont des critères proposés, pas des tests déjà effectués dans cette recherche.
5. **Utiliser les dépendances existantes.** Aucune nécessité démontrée d'installer OpenDesign, Canvas UI ou un nouveau CLI. Les documents servent à améliorer la cohérence et la revue, pas à remplacer l'architecture HTML/CSS/JS.

## Portée des preuves

22 fichiers de documentation, skill, exemple ou licence sont archivés avec SHA-256, en plus des métadonnées GitHub et arbres de fichiers des quatre dépôts. Ont été lus intégralement : spécification Google, les trois skills OpenDesign cités, checklist de contrat, trois références craft, exemple HTML du contrat, licence Canvas et textes de ses deux pages techniques. Les README et analyses volumineuses ont été lus par sections ciblées ; aucune revue exhaustive de leurs codes n'est revendiquée. Cette étude ne comporte ni inspection visuelle de leurs démos ni test de RaceLink.

## Bilan appliqué / écarté

| Ressource | Consulté | Appliqué | Écarté ou limité |
|---|---|---|---|
| Awesome DESIGN.md | README, licence, analyses BMW M et Airbnb ciblées | Principes de cadrage, titre sous l'image et colonnes dans `reference-contract.md` | Copie des marques/actifs et installation comme skill |
| Google DESIGN.md | README et spécification alpha complète | Frontmatter structuré ajouté à `../../DESIGN.md`, valeurs issues exclusivement du CSS produit | Aucun CLI téléchargé/exécuté ; aucune réécriture du corps ou migration Tailwind |
| OpenDesign | Workflow complet de contrat, checklist, exemple, trois références craft ; deux fiches de catalogue | Skill installé au SHA audité et contrat RaceLink court rédigé | Application/daemon, fiches incomplètes, automatisation d'injection et règles stylistiques contraires au brief |
| Canvas UI | README, licence exacte, documentation installation/rendu | Limite explicite dans le contrat : le contenu demeure du HTML natif et lisible | Aucune installation, aucun moteur GPU ou effet sur les photos de procédure |

Le frontmatter a été analysé avec le parseur YAML déjà disponible. Les propriétés de composant supplémentaires pour le mouvement et le focus utilisent l'extension autorisée par la spécification Google ; son CLI pourrait émettre des avertissements pour ces noms. Aucun succès du lint officiel n'est revendiqué. Le corps de `DESIGN.md` a été préservé **octet pour octet** lors de l'ajout : SHA-256 avant/après `6e793037d8413645bc30b15b29d7dbcf5bfb8685d017dfa3e0a4126eceebe774`. Preuve : `sources-design-docs/racelink-frontmatter-check.json`.
