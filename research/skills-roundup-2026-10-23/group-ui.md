# Revue UI — Hallmark, UI UX Pro Max, Impeccable et Taste Skill

23 octobre 2026. **Conserver la direction photographique V17c et améliorer les commandes qui l’accompagnent.** Les quatre ressources ne justifient ni une nouvelle palette ni une réduction des couvertures. Les priorités sont la recherche mobile avec sa langue, la lecture des métadonnées, l’accès aux guides et les commandes des rails horizontaux.

## Périmètre et preuves

Lecture de `public/product-ui.css`, `public/index.html`, `public/discovery-ui.js` et `public/guide-ui.js`, des documents PRODUCT/DESIGN et des instructions pertinentes des quatre skills. Les quatre captures V17c ont été réellement ouvertes et examinées : [accueil desktop](../visual-direction-2026-10-23/desktop-home-final.png), [guides desktop](../visual-direction-2026-10-23/desktop-guides-final.png), [accueil mobile](../visual-direction-2026-10-23/mobile-home-final.png), [guides mobile](../visual-direction-2026-10-23/mobile-guides-final.png). Version visuelle de référence : [9b7dbfc](https://github.com/ValerionGG/racelink-academy/commit/9b7dbfcd6ca2924149220eac772e5f9e8fb5cc06).

Les constats portent sur cette base. L’agent principal modifie en parallèle la recherche et la découverte ; les correctifs annoncés sont identifiés comme tels, sans prétendre les avoir testés. Aucun navigateur partagé, aucune modification du frontend, aucun changement de données ni publication dans cette mission. Ce rapport n’est pas un audit WCAG exhaustif et ne déduit pas les interactions de captures statiques.

## Identités et récence vérifiées sur GitHub

Métadonnées relues avec `gh api repos/<owner>/<repo>` et tête de `main` avec `gh api repos/<owner>/<repo>/commits/main`. Instantané du 23 octobre, vers 16:02 UTC. Les étoiles mesurent la visibilité du dépôt, pas la qualité d’un résultat RaceLink.

| Ressource | Étoiles observées | Licence du dépôt | Dernier push du dépôt / commit de `main` | Instruction primaire |
|---|---:|---|---|---|
| **[Nutlope/hallmark](https://github.com/Nutlope/hallmark)** | 31 172 | MIT | 22/10/2026 17:20 UTC · `7ec8682` | [SKILL v2.0.0](https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/SKILL.md) |
| **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)** | 139 311 | MIT | 23/10/2026 10:06 UTC · `d14efff` | [SKILL](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/d14efff8ed1faa4187f004f79926f428c8074ec7/.claude/skills/ui-ux-pro-max/SKILL.md) |
| **[pbakaus/impeccable](https://github.com/pbakaus/impeccable)** | 85 335 | Apache-2.0 | 23/10/2026 15:57 UTC · `5cb95ee` | [SKILL](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/SKILL.md) |
| **[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)** | 101 489 | MIT | 20/10/2026 22:04 UTC · `6010f91` | [SKILL, tasteskill v2](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/SKILL.md) |

Les quatre dépôts sont non archivés. `pushed_at` n’est pas la date de modification du SKILL : le push récent d’Impeccable n’a pas changé la tête de `main` vérifiée par rapport à la recherche précédente ; ce commit porte la date du 23 octobre à 00:49 UTC. Aucun remplacement automatique des trois skills déjà présents.

### Installation Hallmark

Absence de `skills/hallmark` vérifiée avant installation. Le SKILL amont a été lu et son identité v2.0.0 vérifiée. Installation effectuée avec le **Skill Installer de Codex**, depuis un commit épinglé :

```text
install-skill-from-github.py --repo Nutlope/hallmark
  --path skills/hallmark
  --ref 7ec868225c6caa040558c321ee0fefa0e73f83a8
  --method download
```

Résultat : installation réussie dans le répertoire de skills Codex de l’utilisateur, sans écrasement. Hallmark sera disponible comme skill au prochain tour. Aucune dépendance de navigateur, clé, génération d’image ou installation complémentaire n’a été lancée.

## Ce que chaque ressource apporte réellement

### Hallmark : améliorer un système existant sans le remplacer

Le [mode audit/redesign](https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/references/redesign.md) exige de garder contenu, branchements et marque ; le [mode app](https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/references/flow.md) écarte les recettes de landing page. Les [gates](https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/references/gates.md), sections 1 à 5, ont été lues.

**Application RaceLink :** rendre plus lisibles les types de suggestion et leurs titres ; garder les images et les fonctions intactes. La petite colonne « VIDÉO / GUIDE / SUJET » à 8 px n’aide pas suffisamment à choisir. La proposition utile est un type en casse normale à 11 px, un titre à 14 px minimum et un complément à 12 px, sans pictogramme ou mini-affiche supplémentaire. Conserver le même résultat d’action : vidéo vers lecteur vidéo, guide vers lecteur guide, sujet vers résultats.

**Arbitrage :** ses règles contre les murs de photos, les points médians ou les aperçus répétés ne deviennent pas des interdictions produit. Une bibliothèque vidéo repose justement sur des objets comparables et leurs images. Les données de provenance sont utiles, même si elles ressemblent à des métadonnées que le style marketing de Hallmark préfère réduire.

### UI UX Pro Max : prioriser la tâche mobile et le focus

Lecture du SKILL et de la [référence complète](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/d14efff8ed1faa4187f004f79926f428c8074ec7/.claude/skills/ui-ux-pro-max/references/quick-reference.md). La référence `pro-rules.md` a été consultée en tenant compte de son périmètre natif : les unités iOS/Android ne sont pas automatiquement des obligations web. Le contexte est du HTML/CSS et du JavaScript en modules ; aucun framework ou système visuel généré n’est nécessaire.

La recherche locale `"focus not obscured" --domain ux` a retourné des règles web pertinentes, en distinguant le minimum AA et le niveau renforcé AAA. La recherche `"horizontal scroll navigation"` était trop générale ; une seule reformulation `"carousel keyboard buttons"` n’a apporté qu’une règle générale de navigation clavier pertinente. **Le contrat de boutons de rail ci-dessous est donc une recommandation appliquée à RaceLink, pas une recette de carrousel prétendument trouvée dans la base.**

**Application RaceLink :** rendre le sélecteur de langue visible dans la feuille de recherche et conserver saisie/contexte à son changement. Pour les rails, ajouter une alternative explicite au geste de balayage et préserver le focus. Le scroll interne d’un rail n’est pas à confondre avec un débordement horizontal de toute la page.

### Impeccable : cohérence des commandes et lecture

Le script de contexte a été exécuté depuis la racine de l’application ; il a trouvé PRODUCT/DESIGN et le registre `product`. Lecture du [registre produit](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/product.md) : familiarité, états cohérents, animations qui expliquent une action et hiérarchie stable. La palette existante a été conservée ; aucun tirage de nouvelle palette.

**Application RaceLink :** la source, l’auteur et la langue doivent avoir une échelle cohérente entre résultat et sélection. Dans la base inspectée, `.editorial-video > small` descend à 10 px sur mobile, alors que l’auteur des résultats est à 13 px. Viser 12 px pour auteur/source/langue, 11–12 px pour la provenance secondaire et 14 px pour une action de lecture. Vérifier les sélecteurs effectifs : une règle générale plus spécifique peut annuler une augmentation isolée de `.editorial-creator`.

Le lecteur de guide possède déjà une distinction utile entre méthode générale et notices, ainsi que des liens vers leur périmètre. La conserver. Amélioration ultérieure bornée : dans l’état d’erreur de `guide-ui.js`, un bouton **« Réessayer »** dans le lecteur évite l’instruction actuelle « Fermez cette fiche puis réessayez ». Ce n’est pas un motif pour reconstruire le lecteur ou multiplier les dialogues.

### Taste Skill : préserver la substance photographique

Lecture du SKILL et du [chapitre complet App screens](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/references/app-screens.md). Ce chapitre distingue la lecture d’une page promotionnelle du travail dans un écran à filtres et reconnaît que ses règles mobiles sont des recommandations, issues d’une étude principalement desktop.

**Application RaceLink :** les photographies V17c et les objets du catalogue sont la substance à conserver. Les cartes de guides observées montrent correctement photo, titre, résumé et références ; les deux colonnes desktop utilisent réellement l’espace disponible. Dans l’accueil, améliorer la découverte des ressources cachées par les rails plutôt que réduire les cartes pour tout faire tenir. Proposer un accès visible **« Guides pratiques »** dans la ligne d’actions de découverte, sans ajouter une quatrième catégorie photographique ni un nouveau bloc d’introduction.

**Arbitrage :** ne pas importer sa préférence pour les petites lignes de données, la suppression des heroes d’app ou les sidebars claires. La grande photographie d’accueil, la sidebar noire et la palette RaceLink sont des choix explicites de l’utilisateur et du système existant. Les règles de pages imposant huit éléments animés ou un clip en mouvement ne s’appliquent pas à ce catalogue.

## Recommandations concrètes, par ordre d’utilité

| Priorité | Preuve dans la base inspectée | Modification recommandée | Vérification à effectuer |
|---|---|---|---|
| **1 — Langue dans la recherche mobile** | `product-ui.css`, règle `.mobile-search-body .home-language-picker { display:none }` ; l’agent principal a confirmé le problème par CUA à 390 px. | Afficher la langue au-dessus des suggestions. Un changement conserve la saisie, laisse la feuille ouverte et met à jour les suggestions. **Correctif annoncé en cours par l’agent principal.** | Saisir une question, changer la langue, parcourir puis sélectionner une suggestion ; vérifier langue, saisie et retour du focus. |
| **2 — Suggestions lisibles** | Base : `#search-suggestions strong` à 13 px, `.suggestion-kind` à 8 px ; code `renderSuggestions()` dans `discovery-ui.js`. | Type en casse normale 11 px, titre 14 px ou plus, complément lisible ; aucun petit décor supplémentaire. **Refonte de hiérarchie annoncée en cours.** | Vérifier un titre long et les types vidéo/guide/sujet à 390 px ; flèches, Entrée, Échap et lecture sans clavier. |
| **3 — Rails accessibles** | Capture d’accueil mobile : une carte complète et une partie de la suivante. CSS : `.entry-card` à 82 % et `.editorial-video` à 86 %, défilement horizontal interne. Base initiale sans boutons précédent/suivant. | Deux boutons de 44 × 44 px, noms spécifiques au rail et `aria-controls`. Déplacer d’une carte + l’espacement. Garder les grandes images. | Boutons utilisables au clavier/toucher, état aux extrémités, aucune mise au point forcée sur une carte et aucun défilement de la page entière. |
| **4 — Métadonnées des sélections** | CSS mobile `.editorial-video > small { font-size:10px }`, malgré les déclarations plus basses de `.editorial-creator`. | Auteur, source et langue à 12 px ; maintenir explicitement « estimé » ou « à confirmer » selon les données. La provenance détaillée demeure dans « Pourquoi ce choix ? ». | Contrôler la taille calculée réelle, une langue longue et un auteur long ; aucune troncature qui cache le statut linguistique. |
| **5 — Accès aux guides depuis l’accueil** | `render()` : sujets photographiques, « Tout explorer », sélection et « Tous les sujets » ; pas d’accès explicite au format guide dans cette ligne initiale. | Ajouter « Guides pratiques » près de « Tout explorer ». Réutiliser le chemin de navigation au format guide, avec l’état de langue cohérent. Un seul accès suffit. | Depuis l’accueil, obtenir la liste de guides ; conserver un retour clair et ne jamais présenter les guides généraux comme compatibles avec un véhicule par défaut. |

### Focus des rails : contrat précis

- Garder le focus sur le bouton précédent/suivant utilisé ; ne pas reconstruire le rail par `innerHTML` pour le faire défiler.
- Conserver l’ordre DOM des cartes. La tabulation vers une carte hors champ doit la rendre visible sans sauter verticalement derrière la barre basse.
- Mettre à jour les états des boutons après défilement et redimensionnement. Si un bouton atteint une extrémité en étant focalisé, conserver un focus prévisible : `aria-disabled` avec activation neutralisée est une option ; une désactivation native doit être testée pour éviter une perte de focus.
- Utiliser un défilement court seulement si les animations sont autorisées ; défilement instantané avec `prefers-reduced-motion`. Aucune rotation automatique.
- Masquer les commandes si toutes les cartes tiennent déjà dans le rail. Aucun compteur « 01/03 » nécessaire : le bord visible de la carte suivante et les boutons suffisent.

## Contrôles exécutés et interprétation

### Hallmark, analyse statique uniquement

Commande : `sloplint.mjs public/product-ui.css public/index.html public/discovery-ui.js public/guide-ui.js --scope app --json`, sans `--render`, `--before` ni `--kept`.

Le moteur a réellement analysé **2 fichiers pris en charge**, malgré les quatre chemins fournis : CSS et HTML. Il a retourné **274 FAIL, 295 REFLEX et 10 WARN**, avec rendu `off`. Les principales familles sont 293 espacements hors de son échelle, 203 couleurs/polices hors de son bloc de tokens et 59 usages de blanc absolu hors tokens. **Ce ne sont pas 274 défauts d’usage ni un verdict sur les captures.** Il s’agit majoritairement de conformité à la convention Hallmark d’un site qui utilise déjà son propre système.

Les autres alertes ont été rapprochées du code : la « double barre sticky » regroupe en-tête de page et en-tête de dialogue dans des contextes différents ; le contraste signalé à 4,27:1 concerne un contrôle désactivé ; les boutons à deux lignes sont parfois une composition intentionnelle. Aucun de ces points n’est transformé en blocage visuel sans vérification du contexte. La normalisation de tokens peut être utile ultérieurement, mais ne doit pas remplacer les cinq améliorations de parcours ci-dessus.

### Taste Skill, analyse statique uniquement

Commande : `lint.mjs --app public/product-ui.css public/index.html public/discovery-ui.js public/guide-ui.js`.

Résultat : **4 fichiers, 2 FAIL et 18 WARN**. Les deux FAIL concernent les gradients de `.scene-shade` : ce sont les voiles neutres sur photographie autorisés par le texte du skill, que le détecteur statique ne sait pas contextualiser. L’alerte `padStart(2,'0')` de `discovery-ui.js` concerne le formatage d’une durée réelle, pas une numérotation décorative. Ombres et backdrop de dialogues doivent également être distingués des décors de cartes. Aucun faux « zéro défaut » n’est annoncé.

Les inspecteurs automatiques de navigateur de ces dépôts n’ont pas été lancés : la mission est bornée au rapport et aux captures fournies, et l’agent principal contrôle les interactions dans CUA. Aucun score esthétique numérique arbitraire n’a été calculé. Les constats visibles restent : grandes images respectées, titres clairs dans les guides, recherche d’accueil visible et navigation noire/blanche/rouge cohérente. Les commandes et métadonnées mobiles constituent le meilleur prochain gain.

## Limites de la passe

L’agent principal a commencé à intégrer les contrôles de rails et la nouvelle structure de suggestions pendant cette revue. Les numéros de ligne peuvent donc évoluer ; les sélecteurs et fonctions cités sont les points de repère stables. Les recommandations ne constituent pas une validation des changements en cours. Le prochain contrôle doit porter sur les états réels de langue, de focus et de rail après leur intégration, sans repartir vers une nouvelle identité visuelle.

## Contrelecture du code V18 en cours

Lecture supplémentaire de `public/rail-navigation.js`, des changements de `discovery-ui.js` et de `product-ui.css`, sans modification de l’application. Les ajouts sont cohérents avec la direction retenue : accès « Guides pratiques », langue visible dans la feuille, suggestions avec type à 11 px et titre à 14 px (15 px dans la feuille mobile), auteur et source lisibles, commandes de rails de 44 × 44 px.

**Pas de défaut P1 identifié dans cette lecture. Un point P2 de focus doit être sécurisé ou vérifié dans le navigateur :** `update()` applique `disabled` au bouton activé lorsqu’il atteint une extrémité, et applique `controls.hidden` lorsque le rail n’a plus de débordement. Le code ne prévoit pas de restitution du focus si l’élément actif devient désactivé ou masqué. Le risque de perte du point de navigation clavier concerne notamment le dernier clic sur « suivant » et le passage mobile → desktop avec une flèche active. Le comportement navigateur exact n’a pas été observé par cet agent.

Correction ciblée recommandée : garder les commandes d’extrémité focusables avec `aria-disabled` et bloquer explicitement leur action à la limite ; lorsque le redimensionnement masque les commandes contenant le focus, le rendre à un contrôle visible de la carte correspondante. Ne pas déplacer le focus lors d’un simple défilement ou d’un redimensionnement qui laisse les commandes visibles.

Les autres points de code examinés sont cohérents :

- Les positions tiennent compte du padding du rail et sont bornées à `scrollWidth - clientWidth` ; le dernier élément est reconnu même si sa position théorique dépasse la limite réelle.
- `prefers-reduced-motion` est lu au moment du déplacement et sélectionne `instant`. La règle CSS correspondante supprime également transitions et animations.
- `ResizeObserver` relance les mesures ; un rail initialement masqué peut être mesuré à nouveau quand il redevient visible. Les commandes sont masquées lorsque tous les éléments tiennent dans la largeur.
- Les événements, le frame planifié et l’observateur sont détachés avant reconstruction. Un déplacement de rail ne remplace pas son HTML. La reconstruction de la sélection après « Masquer/Afficher » restitue explicitement le focus au bouton correspondant.

La méthode de validation est adaptée à l’environnement : **aucun navigateur lancé par Hallmark `--render`**. Les contrôles statiques ci-dessus sont complétés par l’inspection CUA de l’agent principal, séparément documentée. Cette revue n’est ni une certification Hallmark ni une validation visuelle de V18. Les prescriptions stylistiques génériques restent subordonnées au `DESIGN.md` existant et à la demande de grandes photographies.

## Contrelecture visuelle finale — V18c publiée

Les quatre captures ci-dessous ont été ouvertes et inspectées avec `view_image`, le 23 octobre 2026. **Aucun problème visuel bloquant identifié dans ces états.**

| Capture inspectée | Constat visible |
|---|---|
| [Recherche française sur mobile](search-french-mobile-final.png) | Saisie et langue des vidéos sont visibles au-dessus des suggestions. Type, titre et métadonnées ont une hiérarchie lisible ; les titres longs reviennent à la ligne. Les sources et le statut linguistique « estimé » restent visibles. |
| [Recherche à 320 px](search-320-final.png) | L’interface espagnole et les vidéos françaises sont distinguées. Le champ, le sélecteur et les suggestions tiennent dans la largeur ; les titres Clio 3 sont lisibles sans coupe latérale visible. |
| [Découverte mobile](mobile-discovery-final.png) | Grandes photos conservées, accès « Guides pratiques » identifiable, rail avec aperçu de la carte suivante et commandes précédent/suivant visibles. La barre inférieure conserve ses quatre destinations. |
| [Accueil desktop](desktop-home-final.png) | La photo d’atelier, la recherche à sa jonction, la langue et les actions restent hiérarchisées. L’accès aux guides se lit avant les catégories photographiques ; aucune collision visible avec la navigation latérale. |

Le point P2 de focus de la contrelecture précédente a été traité par l’agent principal : `aria-disabled`, gardes aux limites et restitution à une carte visible lorsque les commandes disparaissent. **Preuve fonctionnelle transmise par l’agent principal après CUA** : au dernier sujet, état 3/3, focus conservé sur « Sujet suivant », `aria-disabled="true"`, Tab vers « Crédits photos » ; après redimensionnement desktop, focus rendu à une carte. Ce contrôle n’a pas été reproduit par l’auteur de cette contrelecture visuelle.

Cette conclusion porte uniquement sur les quatre images et les observations CUA attribuées ci-dessus. Elle ne valide pas des pages ou interactions non vues et ne motive aucune nouvelle refonte.
