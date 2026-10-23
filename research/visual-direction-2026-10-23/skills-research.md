# Skills et direction visuelle pour une bibliothèque à grandes images

Recherche du **23 octobre 2026, 13:29–13:31 UTC**, complétée par une **installation demandée à 13:41 UTC**. Route de recherche : **Agent Reach → GitHub CLI (`gh`)**, puis API officielle GitHub. Le diagnostic Agent Reach ne certifie pas la connexion GitHub ; les recherches et lectures publiques ont effectivement réussi. L'installation a ensuite utilisé le helper local officiel de Codex, après lecture de son code. Aucun moteur de génération, script des skills téléchargés ou navigateur n'a été lancé.

**Recommandation : une direction photographique forte, conduite par Impeccable et Frontend Design ; Taste comme contrelecture des images, UI UX Pro Max pour les contrôles techniques.** Les guides et vidéos doivent retrouver des images dominantes, avec leur titre lisible dessous. La recherche reste un outil immédiatement disponible. Le brief récent rejette explicitement les cartes compactes : la phrase contraire encore présente dans `PRODUCT.md` est désormais un historique dépassé, pas une contrainte à conserver.

## Comparaison vérifiée

Les étoiles ci-dessous appartiennent aux dépôts entiers. Elles indiquent leur diffusion, **pas la qualité du résultat ni une validation utilisateur**. La date est celle du dernier commit de la branche par défaut, pas nécessairement celle du fichier étudié. Les six dépôts de skills ne sont pas archivés.

| Skill exact consulté | Étoiles au relevé | Dernier commit UTC | Licence vérifiée | Contribution et décision RaceLink |
|---|---:|---|---|---|
| [Impeccable 4.7](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/SKILL.md) | 85 277 | 23/10/2026 | Apache-2.0 | Méthode principale : le brief prévaut, une refonte peut remplacer la composition rejetée tout en conservant fonctions et contenu. Comparer des écrans réellement différents, puis regarder le rendu. Copie locale installée distincte de cette version amont ; aucun remplacement effectué. |
| [Frontend Design, Anthropic](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md) | 183 188 | 09/10/2026 | Apache-2.0, fichier propre au skill | Direction artistique : partir du sujet automobile et donner un rôle dominant à un élément réel. Utile pour des photos expressives et une typographie lisible sans ajouter de décor. Copie locale installée, différente du texte amont consulté. |
| [Taste v2](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/SKILL.md) | 101 426 | 20/10/2026 | MIT | Contrelecture : cadrage, dimensions des images, légendes hors photographie, données réelles. Sa branche « app screens » convient au catalogue ; son scénario promotionnel ne doit pas dicter les résultats de recherche. Désormais installé au SHA audité ; scripts non exécutés. |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/d14efff8ed1faa4187f004f79926f428c8074ec7/.claude/skills/ui-ux-pro-max/SKILL.md) | 139 255 | 23/10/2026 | MIT | Contrôle ciblé : réserver l'espace des images, chargement différé, textes alternatifs, clavier, cibles tactiles et retour de navigation. Ne pas laisser un thème généré remplacer la marque RaceLink. Désormais installé au SHA audité ; moteur Python non exécuté. |
| [Hallmark 2.0](https://github.com/Nutlope/hallmark/blob/7ec868225c6caa040558c321ee0fefa0e73f83a8/skills/hallmark/SKILL.md) | 31 083 | 22/10/2026 | MIT | Intérêt : inventaire des vrais matériaux avant composition, priorité au sujet. Non retenu comme workflow : impose thèmes, empreintes CSS et règles promotionnelles ; son entrée réserve la refonte existante à une invocation explicite. Consulté, non installé et non appliqué. |
| [Frontend Design Prompts — miroir X-T-E-R](https://github.com/X-T-E-R/design-prompts-skill/blob/4f81ca29289dd0e5105f9d1768bf98bbb18b592b/SKILL.md) | 3 | 23/04/2026 | Aucune licence de réutilisation amont établie par ce miroir | Catalogue de directions issues de DesignPrompts.dev. Ce n'est pas le dépôt officiel démontré du site. Utile pour comprendre l'approche de comparaison de thèmes ; non retenu comme dépendance ni comme source à recopier. Consulté, non installé et non utilisé dans l'app. |

Les README et les fichiers de skill de ces six candidats ont été récupérés au SHA du relevé. Impeccable, Frontend Design, UI UX Pro Max, Hallmark et Design Prompts ont été relus intégralement ; Taste a été relu avec ses sections pertinentes sur les images et l'écran produit. L'étude revendiquée par Taste sur les écrans de travail porte sur 23 captures desktop ; elle ne prouve pas l'efficacité mobile de ses règles. [Référence app screens](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/references/app-screens.md).

Autre piste examinée : [Superdesign Prompts](https://github.com/superdesigndev/superdesign-prompts/tree/6c60906945208df5aa2187f19f8ddfe9b2948aa0), **32 étoiles**, dernier commit du **03/08/2026**. Il s'agit surtout d'une bibliothèque de prompts avec aperçus, distincte de son outil d'exécution. Le code est MIT et les prompts sont placés sous [CC0 dans LICENSE-DATA](https://github.com/superdesigndev/superdesign-prompts/blob/6c60906945208df5aa2187f19f8ddfe9b2948aa0/LICENSE-DATA). README consulté ; aucun aperçu visuel n'a été évalué ici, aucun prompt n'est recommandé sur la seule note annoncée par l'éditeur. Non installé, non utilisé.

## Ce que nous retenons pour les grandes images

Le [mode Operate d'Impeccable](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-operate.md) garde les commandes familières et fait porter l'identité par la typographie, la couleur, la densité et un élément distinctif. Pour RaceLink, cet élément peut être la qualité photographique et son échelle ; il n'exige ni cockpit fictif ni décor mécanique autour des contrôles.

La [référence Imagery de Taste](https://github.com/Leonxlnx/taste-skill/blob/6010f91a9935f1c167dfc500fb1a475681892e6b/skills/taste-skill/references/imagery.md) distingue les galeries et archives des cartes promotionnelles. Cadrage cohérent, légendes sous l'image et photographies créditées sont directement utiles. Ses statistiques de sites de galerie restent l'étude de l'auteur, pas une recette démontrée pour notre bibliothèque.

Les propositions suivantes sont des **décisions RaceLink à vérifier dans le rendu**, pas des obligations universelles des skills :

- **Résultats desktop :** essayer trois colonnes de grandes vignettes plutôt qu'une suite de petits aperçus. Photo ou miniature au-dessus, titre en dessous, quelques informations de décision seulement. Garder les preuves et limites détaillées dans la fiche accessible.
- **Résultats mobile :** une colonne, image occupant la largeur utile, titre complet lisible et zones tactiles distinctes. Les codes moteur, modèles et années ne doivent pas disparaître pour respecter artificiellement deux lignes.
- **Deux familles d'images :** miniature réelle pour la vidéo ; photographie éditoriale créditée pour le guide. Une photo de banque ne doit jamais remplacer la miniature d'une vidéo en donnant l'impression d'en être une image.
- **Cadrage explicite :** format paysage cohérent pour la grille ; conserver l'objet et le geste utiles. Pour une source verticale, décider du cadrage après inspection ou l'afficher sans couper les éléments techniques. Pas de filtre sombre général ni texte technique superposé à une photo chargée.
- **Découverte :** une sélection photographique dominante et des thèmes utiles, sans repousser l'accès à la recherche sous plusieurs écrans promotionnels. La grille complète reste stable et prévisible.
- **Mouvement :** retour d'action pour ouverture de fiche, sauvegarde ou filtre. Pas de lecture automatique de tutoriels, de défilement captif ou d'animations imposées pour atteindre un quota stylistique. Respecter le mode de réduction des mouvements.

## Workflow recommandé

1. **Fixer le brief à jour.** Grandes images, noir/rouge/blanc RaceLink, titres hors photo, accès direct à la recherche, contenu et provenance inchangés. Les anciens choix de compacité sont des contre-exemples.
2. **Comparer deux compositions avec les mêmes ressources.** Une bibliothèque photographique régulière et une découverte plus éditoriale. Utiliser les vraies couvertures déjà présentes, un titre long, un format vertical et une ressource sans image. Ne pas comparer des maquettes remplies de contenus différents.
3. **Choisir d'abord l'échelle et la hiérarchie.** Taille visible des photographies, titre, commande de recherche, filtres. Puis seulement affiner espacement, bordures, couleurs et transitions. Conserver un seul document de décisions, pas plusieurs systèmes de design concurrents.
4. **Vérifier sur rendu autorisé.** Largeurs desktop et 320/390 px ; image chargée et absente ; recherche → filtre → fiche → retour ; état actif, focus et langue. Mesurer le poids des images et réserver leurs dimensions. Un test de code réussi ne démontre pas la qualité visuelle.

MotionSite peut fournir des références de composition ou de mouvement à inspecter dans la mission visuelle parallèle ; ce rapport n'en revendique aucune visite. Aucun de ces skills ne remplace le modèle actif ni ne garantit un résultat « équivalent à Opus 5.5 ». Ils fournissent des consignes et des méthodes de vérification, dont le résultat doit être jugé sur les écrans obtenus.

## Statut et preuves

- **Effectivement appliqué à cette recherche :** Agent Reach, route GitHub/gh. Le moteur de recherche web a uniquement aidé à distinguer les dépôts homonymes de Design Prompts.
- **Installés et lus localement :** Impeccable et Frontend Design préexistants, puis Taste et UI UX Pro Max ajoutés sur demande. Les copies locales des deux premiers restent distinctes de l'amont. Interface Design est également présent mais n'a pas été relu ni réappliqué dans ce complément.
- **Consultés comme sources :** les six skills du tableau. Les workflows de génération, les scripts d'actifs et les inspecteurs navigateur n'ont pas été exécutés. L'installation des deux skills ci-dessous ne constitue pas un test fonctionnel de leurs moteurs.
- **Aucun changement :** application, CSS, base et dépôt Git. La recherche a ajouté ses preuves ; l'installation a ajouté deux nouveaux dossiers de skills, sans écraser de dossier existant.

`manifest.json` conserve étoiles, dates, SHA, URL de chaque fichier et empreinte SHA-256 ; `sources/` conserve les métadonnées de l'API et les textes lus. Le [miroir Design Prompts décrit lui-même son statut non officiel et l'incertitude de licence](https://github.com/X-T-E-R/design-prompts-skill/blob/4f81ca29289dd0e5105f9d1768bf98bbb18b592b/SOURCE.md). Cette réserve concerne ce miroir, pas une conclusion générale sur tous les prompts de design.

Le contrôle de version Agent Reach annonce **1.6.0 disponible**, contre **1.5.0 installé**. Aucune mise à jour lancée ; ce résultat n'est pas nécessaire à la refonte.

## Installation demandée et vérifiée

Le workflow [skill-installer local](C:/Users/Nad/.codex/skills/.system/skill-installer/SKILL.md) a été suivi. Son helper `install-skill-from-github.py` et `github_utils.py` ont été lus avant exécution. Le mode `download`, les deux SHA explicites et la destination `C:/Users/Nad/.codex/skills` empêchent ici le recours à une branche mouvante ou à un checkout Git. Les dossiers de destination étaient absents ; le helper refuse les écrasements. Il télécharge l'archive GitHub officielle et copie le dossier demandé, sans lancer son contenu.

| Skill installé | Fichier d'entrée exact | Révision figée | Contrôle après copie |
|---|---|---|---|
| Taste, nom déclaré `design-taste-frontend` | [SKILL.md](C:/Users/Nad/.codex/skills/taste-skill/SKILL.md) | `6010f91a9935f1c167dfc500fb1a475681892e6b` | 39 fichiers, 2 420 861 octets, aucun lien symbolique |
| UI UX Pro Max, nom déclaré `ui-ux-pro-max` | [SKILL.md](C:/Users/Nad/.codex/skills/ui-ux-pro-max/SKILL.md) | `d14efff8ed1faa4187f004f79926f428c8074ec7` | 74 fichiers, 3 584 054 octets, aucun lien symbolique |

Les deux `SKILL.md` ont été relus intégralement après sélection de la version. Leurs empreintes correspondent exactement aux preuves auditées :

- Taste : `d955dae4ba8ab2d994f4bb06b4bf412a1d9875433a8597939c391f4bae91dd7a`.
- UI UX Pro Max : `ea087c341bfb5b23195c7302027268ede86da802554c18a5c4896a6017b439f9`.

Les licences MIT des racines des dépôts, absentes des sous-dossiers installés par le helper, ont été copiées sans modification dans chaque dossier sous `LICENSE`. Aucun fichier amont n'a été réécrit. Les skills seront disponibles dans le catalogue au **prochain tour**.

Limites à conserver pour leur utilisation :

- Taste possède des parcours distincts pour page et application. Ses quotas de mouvement et règles de galerie ne doivent pas remplacer le brief RaceLink. Son inspecteur demande Node 22+ et un navigateur Chromium ; il n'a pas été exécuté et ne remplace pas la route CUA autorisée dans cette session.
- Taste annonce lui-même que la bibliothèque de scènes n'est pas encore livrée ; `library/scenes.json` et les démonstrations correspondantes ne sont pas dans cette révision. Le code de lecture prévoit leur absence. Ne pas promettre ces scènes comme une capacité testée.
- Le texte UI UX Pro Max emploie un chemin d'exemple Claude, `${CLAUDE_PLUGIN_ROOT}/.claude/...`. Dans Codex, le chemin local réel du moteur est `C:/Users/Nad/.codex/skills/ui-ux-pro-max/scripts/search.py`. Le fichier n'a pas été modifié et ce moteur n'a pas été exécuté ; il faudrait adapter l'invocation, pas inventer une variable Claude.
- L'installation conserve scripts, données et références pour un usage ultérieur. Elle ne certifie ni l'ensemble de leur code ni leurs résultats ; aucun score de design, audit visuel ou résultat de recherche produit par ces scripts n'est revendiqué.
