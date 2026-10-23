# Skills UI/UX pour la refonte de RaceLink — 23 octobre 2026

**Recommandation : Impeccable 4.7 comme méthode principale, avec Operate pour le catalogue et Read pour les guides.** Interface Design complète le système de composants ; UI UX Pro Max sert de contrôle ciblé des interactions. Emil intervient pour la finition. Taste et Anthropic sont des références de comparaison, sans empiler six directions artistiques.

Ce choix vient de leur adéquation à `outputs/focus-academy/PRODUCT.md` : trouver une ressource, comprendre sa provenance, la consulter, puis revenir à sa recherche. Le nombre d’étoiles n’est pas une mesure d’utilisabilité.

## Sources et actualité vérifiées

Route Agent Reach **GitHub / `gh`** : recherche de dépôts triée par étoiles, API officielle pour métadonnées et branche par défaut, puis README, licence et véritables `SKILL.md` récupérés au SHA observé. Horodatage des compteurs : **23 octobre 2026, 07:26 UTC**. Aucun dépôt n’est archivé. « Dernier commit » concerne la branche par défaut du dépôt, pas nécessairement le skill étudié.

| Source étudiée | Étoiles du dépôt | Dernier commit UTC | Licence du contenu étudié | Rôle conseillé |
|---|---:|---|---|---|
| [Impeccable 4.7](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/SKILL.md) | 85 134 | 23/10/2026 | Apache-2.0 | Méthode principale produit + lecture |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28327f2f214d31bbd7555ed0c012a5df6484ed96/.claude/skills/ui-ux-pro-max/SKILL.md) | 139 140 | 23/10/2026 | MIT | Référence UX ciblée |
| [Interface Design](https://github.com/Dammyjay93/interface-design/blob/2f9be3206855bcb2d1d0af262c8bae25cba6658d/.claude/skills/interface-design/SKILL.md) | 5 839 | 20/06/2026 | MIT | Composants et cohérence durable |
| [Taste v2](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/SKILL.md) | 101 283 | 20/10/2026 | MIT | Contrelecture de la composition produit |
| [Emil Design Engineering](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/emil-design-eng/SKILL.md) | 48 821 | 11/10/2026 | MIT | Toucher, clavier, mouvement et finition |
| [Anthropic Frontend Design](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md) | 183 120 | 09/10/2026 | Apache-2.0 du skill | Identité et clarté de l’expression |

Les étoiles appartiennent aux dépôts entiers, particulièrement importants chez Anthropic et Emil qui contiennent plusieurs skills. L’API du dépôt Anthropic n’indique pas de licence générale ; sa [licence propre à Frontend Design](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/LICENSE.txt) a été vérifiée. `emilkowalski/skill` redirige vers le nom canonique `emilkowalski/skills`. Les fichiers locaux gardent le nom de dossier utilisé lors de la découverte. Une date de mise à jour GitHub causée par les étoiles n’est pas présentée comme une modification de code.

## Ce que leur contenu apporte réellement

**Impeccable : la distinction la plus utile pour RaceLink.** Operate part des tâches, de la navigation, des données et des états. L’identité intervient dans la typographie, la palette, la densité et un signe distinctif, sans transformer les commandes familières en décor automobile. Read recentre les guides sur la question du lecteur, une colonne lisible et une navigation de document. Les références séparent aussi `PRODUCT.md`, contexte durable, de `DESIGN.md`, décisions visuelles. Application : la recherche domine le catalogue ; une fiche se lit clairement ; le rouge et la « ligne de trajectoire » donnent l’identité sans simuler un cockpit. [Operate](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-operate.md), [Read](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-read.md).

**Interface Design : le meilleur complément de cohérence.** Son périmètre explicite couvre les applications, outils et tableaux de bord. Il demande de relier les choix visuels à l’utilisateur et au domaine, de stabiliser les tokens et de concevoir les états de chaque contrôle. Sa priorité aux éléments HTML natifs est pertinente pour les formulaires et dialogues existants. Il est moins récemment modifié que les autres, mais mieux ajusté à cette tâche que son classement par étoiles ne le suggère. Sa mémoire `.interface-design/system.md` serait redondante ici : conserver une seule référence visuelle canonique.

**UI UX Pro Max : utile comme index de problèmes.** Son moteur propose des recherches ciblées par domaine et impose de vérifier la pertinence des résultats. La [référence UX](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28327f2f214d31bbd7555ed0c012a5df6484ed96/.claude/skills/ui-ux-pro-max/references/quick-reference.md) traite explicitement du focus masqué par une barre fixe, des étiquettes de filtres longues, du maintien des critères au retour, des recherches accessibles et de la divulgation progressive. Ces sujets correspondent aux régressions à éviter. Les palettes et styles générés depuis les tables ne constituent pas une étude des utilisateurs de RaceLink ; ne pas leur laisser remplacer la marque ou imposer une nouvelle stack. Le moteur Python n’a pas été exécuté.

**Taste : vérifier la bonne branche du workflow.** Le dépôt ne se limite plus aux pages promotionnelles : sa référence [App screens](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/references/app-screens.md) possède un parcours produit distinct. Elle pousse à vérifier le cadre de navigation, les alignements, les états et les données réelles. Elle décrit sur téléphone une navigation basse ou repliée, des filtres dans une feuille et le retour liste/détail avec position conservée. Limite explicite : l’étude annoncée porte sur 23 écrans desktop de 17 produits, sans écrans mobiles ; les recommandations téléphone sont des règles de l’auteur. Ce n’est pas une validation mobile indépendante. Les tirages de styles et les règles de galerie du parcours général sont moins adaptés à une identité RaceLink déjà choisie.

**Emil : traiter les détails après l’architecture.** Son guide aide à décider quand une animation est utile, à rendre les transitions interrompables, à distinguer survol et toucher et à respecter la réduction des mouvements. Pour RaceLink : aucune attente décorative pendant la saisie ; une feuille de filtres et un retour d’action peuvent bénéficier d’un mouvement bref. Ce skill ne définit pas à lui seul l’organisation d’un catalogue ni son classement.

**Anthropic : une direction claire et du contenu crédible.** Le skill favorise une identité liée au sujet, une typographie assumée, un petit système de tokens et une critique du résultat. Ses règles sur les faux chiffres, les cartes imbriquées et les libellés vagues rejoignent `PRODUCT.md`. Il apporte moins de procédures détaillées pour les facettes, les états persistants et les interactions mobiles : conserver son exigence de clarté, pas un second système de composition.

## Arbitrages à appliquer

- **Une source de vérité visuelle.** Consigner composants, espacements, couleurs sémantiques, typographie et états dans un seul `DESIGN.md` ; les autres skills sont des références ponctuelles.
- **Le produit décide du mouvement.** Une règle générique hostile aux transitions instantanées ne doit pas ralentir les suggestions ou les actions clavier fréquentes. L’absence d’animation peut être le bon comportement.
- **Un objectif tactile n’est pas une certification.** Retenir 44 px comme cible de confort du projet. La référence UI UX Pro Max distingue elle-même les unités natives et les critères web ; ne pas présenter toute grille d’un skill comme une preuve de conformité WCAG.
- **La densité dépend de l’usage.** Ne pas reproduire les contrôles desktop de 28–36 px observés dans Taste sur téléphone. Préserver les vrais titres longs, les codes moteur et les noms de modèles.
- **L’esthétique ne crée aucune preuve.** Une ressource indexée, une langue estimée ou une transcription autorisée doivent garder leurs distinctions. Aucun compteur décoratif, badge de validation inventé ou donnée d’exemple présentée comme réelle.

## Workflow recommandé pour cette refonte

1. **Partir du brief existant.** Utilisateurs, tâches et données sont déjà documentés. Décision de cette refonte : sidebar desktop, navigation basse mobile, recherche centrale, fiche simplifiée. Ce sont des choix produit retenus pour RaceLink, pas des obligations universelles d’un skill.
2. **Comparer deux compositions avec les mêmes vraies données.** Faire varier la densité et l’emplacement des filtres, sans changer le contenu. Tester une requête véhicule précise, un titre français long, une ressource sans vignette et un résultat sans transcription. Choisir sur la rapidité de lecture et l’action principale.
3. **Établir le contrat visuel unique.** Modes Operate/Read, tokens limités, composants natifs, règles de carte et de fiche. L’identité automobile reste perceptible ; les commandes restent immédiatement reconnaissables.
4. **Construire les états en même temps que les vues.** Chargement, erreur, aucun résultat, critères actifs, clavier, sauvegarde, retour à la liste. Une modification de catégorie ou l’ouverture d’une fiche ne doit pas perdre la requête, la langue ou les filtres.
5. **Vérifier le produit rendu dans CUA.** Largeurs 320, 390, 768 et 1440 ; zoom et textes FR/EN/ES ; focus des dialogues et de la navigation ; recherche → filtre → fiche → retour ; réduction des mouvements. Séparer les observations sur viewport simulé de tout test sur appareil réel. Les règles automatiques ou le score interne d’un skill ne remplacent pas ces preuves.

## Archives, périmètre et réutilisation

[skills-comparison.json](skills-comparison.json) rassemble les URL canoniques, compteurs, dates, licences, SHA et empreintes des fichiers consultés. [source-manifest.json](source-manifest.json) relie ces preuves à la recherche produit et au code observé. Les références sont pointées vers leur révision GitHub précise ; les textes amont, scripts, arbres Git et fichiers de travail ne sont pas recopiés dans ce livrable.

Les six README et six SKILL principaux ont été consultés par l’agent de recherche. Les références longues ont été examinées dans les sections pertinentes ; aucune vérification de tous leurs scripts ou de toutes leurs données n’est revendiquée. Aucun launcher, script distant ou installation n’a été exécuté. Impeccable 4.7 annonce un launcher pouvant télécharger un binaire au premier usage ; Taste propose des outils Node et un navigateur automatisé. Cette recherche s’est limitée à leurs textes. Les compteurs d’étoiles et l’activité sont des instantanés datés.

Les recommandations de ce rapport ne constituent pas des tests passés. [DECISIONS.md](DECISIONS.md) indique les choix réalisés ; [VALIDATION.md](VALIDATION.md) détaille les scénarios CUA exécutés sur la v14 publiée et l’état des retouches suivantes. L’inspection réelle du site officiel RaceLink et de l’image Dribbble reste distincte de ces tests de l’application.
