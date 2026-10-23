# RaceLink Academy — décisions de refonte du 23 octobre 2026

Version finale v14c publiée et vérifiée : [rapport de validation](VALIDATION.md). Les étapes ci-dessous conservent les versions observées.

La refonte transforme l’accueil et la bibliothèque en un espace de consultation plus compact : **navigation persistante, recherche, contexte véhicule/langue, résultats et fiche source**. La **v14 a été publiée**, commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4), puis observée dans le navigateur. Elle suit l’identité officielle RaceLink, réellement inspectée : Onest, accents Orbitron, noir/rouge/blanc. Le catalogue reste inchangé. La retouche v14c de compacité mobile et de couleurs des badges conserve un état de validation séparé dans [VALIDATION.md](VALIDATION.md).

## Ce qui est effectivement codé

| Surface | Réalisation observée dans les sources | Pourquoi |
|---|---|---|
| Cadre desktop | En-tête noir, sidebar sombre, contenu gris neutre ; navigation Accueil, Bibliothèque, Parcours, Enregistrés. | Séparer les destinations de l’application des filtres de résultats. |
| Typographie | Onest pour le corps, les contrôles et les titres ; courts accents Orbitron. | Relier la bibliothèque au site officiel tout en gardant une lecture facile des procédures. |
| Couleurs | Canvas gris neutre, surfaces blanches, navigation et accueil noirs ; rouge officiel `#ff2330` en accent, rouge `#c82038` pour des actions contrastées. | Conserver la marque sans recolorer les photos ni surcharger les commandes. |
| Accueil | Zone noire compacte, champ blanc, langue de contenu et trois entrées illustrées avec photos non teintées et légendes séparées. | Faire de l’accueil une entrée dans le catalogue. Le visuel reste secondaire. |
| Découverte | « Explorez vos sujets » ; Entretenir ma voiture / Mieux piloter / Régler mon simulateur ; autres sujets dépliables. | Rendre les entrées compréhensibles sans supprimer les disciplines existantes. |
| Sélection | « La sélection RaceLink », miniatures réelles, auteur, plateforme, langue et durée connue ; raisons et preuve en détails. | Aider à choisir tout en montrant ce qui a réellement été consulté. |
| Guides | Onze couvertures SVG originales noir/argent/rouge, distinctes des miniatures vidéo. | Identifier le sujet et le format sans remplacer les images des créateurs. |
| Bibliothèque | Recherche, ligne de contexte langue/véhicule, formats Tout/Vidéos/Guides, filtres et liste. | Distinguer la tâche, le type de ressource et sa plateforme. |
| Résultats mobile | Une colonne, miniature latérale, titre et auteur ; enregistrement accessible sur la carte. | Réduire le défilement et permettre la comparaison de titres précis. |
| Navigation mobile | Accueil / Rechercher / Parcours / Enregistrés, pictogrammes et texte, zone de sécurité inférieure. | Quatre destinations stables sans demander un apprentissage de menus cachés. |
| Fiche mobile | Dialogue natif plein écran, avec source, enregistrement, informations et onglets existants. | Réutiliser les contrats de lecture ; aucune nouvelle route de fiche n’est revendiquée. |
| Styles | `product-ui.css` définit la couche produit ; `app-ui.css` est un bundle généré avec couches `legacy` puis `product`. | Préserver les fonctions existantes tout en donnant une priorité explicite à la nouvelle présentation. |

Les fichiers applicatifs inspectés comprennent `public/index.html`, `public/product-ui.css` et `public/discovery-ui.js`. Le manifeste conserve les empreintes historiques de la première étude, explicitement distinctes de la publication v14. Les contrôles du déploiement courant et du navigateur figurent dans [VALIDATION.md](VALIDATION.md). Une empreinte seule ne prouve pas le bon fonctionnement.

## Arbitrages entre la recherche et la réalisation

Le benchmark proposait Barlow et le canvas ivoire ; la première refonte a ensuite utilisé Manrope et un fond gris neutre. Après le retour sur les affiches vertes, **la v14 publiée adopte Onest, des accents Orbitron, un accueil noir compact et des photos non teintées**. La preuve visuelle et les styles calculés du site officiel ont guidé ce choix. [DESIGN.md](../../DESIGN.md) constitue la référence canonique ; le benchmark conserve ses hypothèses comme étude préalable. [brand-direction.md](brand-direction.md) retrace ce dernier arbitrage.

Le benchmark proposait le libellé « Explorer » pour la première destination mobile. Le code conserve **Accueil**, suivi de Rechercher, Parcours et Enregistrés. Les sélections défilent horizontalement sur mobile ; les résultats de recherche restent une liste verticale. Une fiche plein écran est réalisée avec le dialogue existant, sans introduire un routage distinct.

La distinction entre véhicule connu et simple mention reste essentielle. Ni un filtre appliqué, ni une image automobile, ni une mise en avant ne créent une compatibilité mécanique. Les niveaux, langues et transcriptions conservent leurs statuts réels. L’esthétique ne justifie aucun compteur fictif, progression inventée, faux visionnage ou nouveau badge de validation.

## Ce que les références ont apporté

| Référence primaire | Principe retenu | Limite |
|---|---|---|
| [iFixit — Parts of a Guide Page](https://about.ifixit.com/Wiki/Parts_of_a_Guide_Page) | Comprendre le périmètre et les prérequis avant une intervention. | RaceLink référence des sources externes ; il ne reconstruit pas de procédure complète à partir d’un titre. |
| [AUTODOC Club — Manuals](https://club.autodoc.co.uk/manuals) | Associer véhicule et intervention sans perdre les accès par sujet. | Une mention extraite n’équivaut pas au système de compatibilité d’un producteur de manuel. |
| [Skillshare — Search FAQ](https://help.skillshare.com/hc/en-us/articles/16267180286221-Search-FAQ) | Facettes explicites, langues et types de ressources distincts. | Les mécanismes documentés n’ont pas été testés dans son application mobile par les agents. |
| [YouTube — Transcriptions](https://support.google.com/youtube/answer/15930243?hl=fr) | Lire ou atteindre un passage lorsque le texte et les horodatages existent. | Aucune transcription ne doit être promise pour toutes les ressources. |
| [Linear — Search](https://linear.app/docs/search) et [Raycast — Search Bar](https://manual.raycast.com/search-bar) | Recherche directe, action principale claire, contexte et retours cohérents. | Références d’interactions documentées, pas modèles de commandes desktop à copier sur téléphone. |
| [Dribbble — Parthik Kalsariya](https://dribbble.com/shots/26306305-Modern-Mobile-UI-for-Online-Learning-Platform) | Référence de conception mobile, recherche, catégories et navigation inférieure. | Image réellement inspectée par l’agent principal ; concept de portfolio, sans mesure indépendante d’efficacité. Aucun actif copié. |
| [Behance — Gorsel Kutman, Lingua Attack](https://www.behance.net/gallery/115613205/E-learning-mobile-app-UX-Case-Study) | Complexité progressive et distinction tâche/configuration. | Texte consulté par l’agent de recherche ; image non inspectée. Étude publiée en 2021. |

La référence [Pinterest recherchée](https://www.pinterest.com/pin/simple-elearning-app-ui-design--30680841204302881/) a renvoyé 403. Son titre était indexé, mais son auteur et sa composition n’ont pas été confirmés ; elle ne fonde aucune décision visuelle. Les refus et indisponibilités n’ont pas été contournés.

## Skills : une méthode principale, des contrôles ciblés

[Impeccable 4.7](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/SKILL.md) est la référence principale, avec [Operate](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-operate.md) pour la bibliothèque et [Read](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-read.md) pour les fiches. [Interface Design](https://github.com/Dammyjay93/interface-design/blob/2f9be3206855bcb2d1d0af262c8bae25cba6658d/.claude/skills/interface-design/SKILL.md) complète les composants ; [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28327f2f214d31bbd7555ed0c012a5df6484ed96/.claude/skills/ui-ux-pro-max/SKILL.md) et [Emil](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/emil-design-eng/SKILL.md) servent à la contrelecture UX et à la finition. [Taste](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/SKILL.md) et [Anthropic Frontend Design](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md) complètent la comparaison.

Le [rapport des skills](skills-report.md) détaille l’adéquation, les licences et les limites. [skills-comparison.json](skills-comparison.json) conserve les étoiles, dates, SHA et URL au moment de la recherche. Les étoiles portent sur les dépôts complets ; elles ne mesurent pas la qualité d’usage de RaceLink. Aucun launcher, script distant ni installation de ces dépôts n’a été exécuté dans cette recherche.

## État précis de la validation

| Travail | État au moment de cette note |
|---|---|
| Lecture de PRODUCT.md, HTML et CSS actuels | Réalisée pour documenter le code. |
| Recherche des produits et portfolios | Sources primaires textuelles consultées ; dix références documentées avec leur niveau de preuve. |
| Recherche GitHub | Six dépôts comparés par la route Agent Reach / `gh`, métadonnées et textes inspectés à SHA fixé. |
| Sources visuelles | RaceLink officiel et référence Dribbble inspectés via CUA par l’agent principal ; les autres niveaux de preuve restent documentés source par source. |
| Baseline publique | Inspectée par l’agent principal à 1280 × 720 ; capture réelle conservée dans le dossier de travail. |
| Référence Dribbble ci-dessus | Image réelle inspectée par l’agent principal via CUA. |
| Syntaxe de discovery-ui.js | Vérifiée par `node --check` après sa modification ; logique de recherche/événements/API inchangée dans ce patch. |
| V14 publiée `d4cdda4` | Accueil à 1280 × 720 et iframe mobile de 390 px réellement observés via CUA ; onze guides visibles, recherche et filtres testés. |
| Guide carburants | Ouverture/fermeture avec focus restauré. |
| Recherche mobile | Langue française puis « vidange Clio 3 » : deux vidéos, suggestions visibles ; Entrée restaure le focus sur la commande de modification de recherche. |
| Filtre YouTube | Requête et français conservés, retour du focus au titre des résultats. |
| Débordement mobile | `scrollWidth = clientWidth = 375` dans l’iframe de 390 px. |
| Retouche v14c | Compacité mobile et retrait du vert résiduel ; validation finale suivie séparément dans [VALIDATION.md](VALIDATION.md). |
| Audit WCAG exhaustif ou appareil physique | Non effectué et non revendiqué. |

Les scénarios ci-dessus décrivent uniquement les essais réels de la v14 ; ils ne constituent pas un audit de tous les états. Les contrôles complémentaires à 320/430/768 px sont consignés pour v14b/v14c dans le rapport final. Les captures, les détails des parcours et les dernières vérifications se trouvent dans [VALIDATION.md](VALIDATION.md), qui fait foi pour la retouche suivante.

## Contenu du dossier

- [benchmark-mobile.md](benchmark-mobile.md) : étude préalable des parcours, observations et recommandations ; ses hypothèses non retenues sont signalées.
- [skills-report.md](skills-report.md) : comparaison argumentée de six sources GitHub.
- [skills-comparison.json](skills-comparison.json) : métadonnées des dépôts et fichiers de référence, avec URL publiques et empreintes ; aucun script amont inclus.
- [source-manifest.json](source-manifest.json) : preuves documentaires, restrictions, observation visuelle rapportée par l’agent principal, sources et empreintes du code inspecté.
- [brand-direction.md](brand-direction.md) : filiation avec RaceLink officiel, cartes et mouvement, preuves Pinterest/MotionSite et limites.
- [VALIDATION.md](VALIDATION.md) : publication et scénarios réellement contrôlés.
- [../../DESIGN.md](../../DESIGN.md) : référence visuelle actuelle.

Le dossier ne recopie pas l’intégralité des skills, leurs sources ou les fichiers de travail. Les liens directs permettent de retrouver les références à la révision étudiée.
