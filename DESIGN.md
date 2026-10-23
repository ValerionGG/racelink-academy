# Interface RaceLink Academy

Version courante **visual-v17c**, commit [9b7dbfc](https://github.com/ValerionGG/racelink-academy/commit/9b7dbfcd6ca2924149220eac772e5f9e8fb5cc06), publiée. Grandes photos réelles, titres sous les images, une colonne mobile et grille adaptée à la largeur disponible. Accueil photographique avec recherche à la jonction de l’image. [Voir l’application](https://valeriongg.github.io/racelink-academy/?release=visual-v17c) · [Validation et limites](research/visual-direction-2026-10-23/VALIDATION.md) · [Skills comparés et ajoutés](research/visual-direction-2026-10-23/skills-research.md).

Le contexte durable reste dans [PRODUCT.md](PRODUCT.md). Les règles V17 ci-dessous remplacent la compacité des vignettes et le masquage du grand visuel sur téléphone. Le lecteur partagé, la recherche sans seconde couche fixe et les **21 références constructeur dans 11 guides** sont conservés. Les validations des versions antérieures restent des preuves historiques ; elles ne valident pas cette nouvelle composition.

## Intention

Un espace de consultation et d’apprentissage automobile : chercher une réponse, comprendre sa source, la consulter et retrouver son contexte. La recherche, le véhicule facultatif et la langue du contenu dominent le parcours. Les sélections et parcours aident à découvrir ; ils ne sont pas une étape obligatoire avant les résultats.

L’identité RaceLink repose sur la marque RL, le noir, le rouge et le blanc, avec de grandes images de terrain qui expliquent le sujet. La photographie donne envie d’explorer ; le titre précise le geste et la recherche reste immédiatement accessible. La navigation reste familière ; aucun instrument de cockpit ou indicateur de progression décoratif n’est nécessaire.

## Système visuel V17

| Rôle | Direction retenue | Usage |
|---|---|---|
| Police de lecture | Onest, puis polices système | Corps, contrôles, titres de ressources et descriptions. |
| Accent typographique | Orbitron | Courts labels de marque ; éviter les longs titres techniques et les paragraphes dans cette police. |
| Canvas | `#fafafa` | Fond de lecture clair et neutre. |
| Surface | `#ffffff` | En-tête, champs, panneaux et surfaces de lecture. |
| Encre | `#18191b` | Texte principal. |
| Texte secondaire | `#606166` | Auteur, source, descriptions et informations secondaires. |
| Séparateur | `#e1e1e3` | Limites de groupes et de surfaces. |
| Rouge officiel décoratif | `#ff2330` | Traits, accents et éléments de marque ; le blanc en petit texte sur ce rouge n’atteint pas 4,5:1. |
| Rouge d’action contrasté | `#c82038` comme référence à préserver ou équivalent vérifié | Action principale, focus et repères actifs ; blanc sur ce rouge ≈ 5,65:1. |
| Rouge léger | `#fff0f2` | Fond des contrôles sélectionnés. |
| Navigation et hero sombres | Encre `#101012`, proche du site officiel `#0a0a0a` / `#0f0f0f` | Sidebar et traitement local du hero photographique ; recherche blanche et texte clair contrasté. |
| Rayon de référence | `14px` | Surfaces arrondies ; composants de 8 à 16 px selon leur taille. |
| Couvertures | `16 / 9`, pleine largeur de carte | Images au-dessus du titre, y compris sur téléphone. |
| Titres des ressources | `20–21px` | Onest, contraste fort, espace suffisant pour le sujet et l’opération. |
| Grille de résultats | Minimum utile de `330px` par carte | Deux colonnes à 1280 px dans le cadre applicatif actuel ; trois seulement lorsque l’espace utile devient très large. |

L’inspection CUA du site officiel a montré Onest sur le corps et Orbitron 800 sur son h1. Cette preuve de rendu prime sur la simple présence de classes Rajdhani dans le HTML. La V17 conserve Onest pour la lecture et réserve Orbitron aux accents. Manrope appartient à la première refonte du 23 octobre. Les images et miniatures ne reçoivent pas de filtre vert, ni de recoloration rouge systématique.

Le site officiel utilise également noir, halo rouge, navigation arrondie et bouton blanc. L’Academy en retient la famille visuelle avec un hero mécanique photographique et des surfaces de lecture claires. Les grandes images remplacent la densification rejetée ; elles ne justifient pas une introduction qui retarderait la recherche, ni la reprise des niveaux et compteurs promotionnels du site officiel.

`public/product-ui.css` est le point d’édition du système produit. `public/app-ui.css` est généré par `scripts/build_ui.py`, avec des couches `legacy` puis `product` ; ne pas corriger le bundle à la main. Cette priorité de styles évite de faire dépendre la nouvelle identité de l’ordre accidentel des anciennes feuilles.

## Structure et navigation

**Ordinateur.** Cadre applicatif avec en-tête, sidebar sombre et contenu sur canvas neutre. La navigation principale est Accueil / Bibliothèque / Parcours / Enregistrés. Sujets, véhicule facultatif, aide et lien Focus restent accessibles dans la sidebar. Les changements de marque n’ajoutent pas une deuxième navigation de destinations. Les dimensions et ruptures exactes sont définies dans le CSS et doivent être contrôlées sur le rendu final.

**Téléphone, jusqu’à 760 px.** La sidebar disparaît. La barre inférieure conserve **Accueil / Rechercher / Parcours / Enregistrés**, avec icône, texte, état actif et marge de sécurité du téléphone. Le hero photographique reste présent ; la recherche est placée à la jonction de son bord inférieur et du contenu clair. Les détails et les panneaux occupent l’écran selon le système de dialogues existant. Les recouvrements, la hauteur utile et la visibilité immédiate du champ restent à contrôler au navigateur pour V17.

**Accueil.** Grande photographie mécanique, phrase courte, noir/blanc/rouge et champ blanc à la jonction de l’image. Langue des vidéos et exemples accessibles. Trois entrées photographiques larges : Entretenir ma voiture / Mieux piloter / Régler mon simulateur. Photos non teintées et légendes séparées. Puis « La sélection RaceLink », fondée sur les données existantes. Les autres sujets restent dépliables. La recherche doit être utilisable dès le premier écran ; aucun carrousel ne tourne automatiquement. Cette priorité concerne l’accès à la commande, pas la réduction des images en vignettes.

**Bibliothèque.** Recherche modifiable, contexte langue et véhicule, formats Tout / Vidéos / Guides, filtres et résultats. Le véhicule se précise progressivement ; les champs non renseignés restent inconnus. La langue du site et la langue du contenu sont deux réglages distincts. Les critères ne doivent pas être supprimés silencieusement lors d’une suggestion ou d’un retour.

## Ressources, cartes et fiches

Les cartes vidéo montrent la miniature réelle consignée, un titre descriptif, l’auteur et la plateforme. Une miniature manquante reçoit un fond neutre. Les sélections affichent une durée uniquement connue, le statut de langue et la base du choix ; la raison, la preuve et la date de revue restent dépliables. Les badges de sélection sont sobres, sans dominante verte ni fausse certification.

Les portes de découverte et les onze guides utilisent des photographies réelles non teintées, accompagnées d’une légende hors image. Les crédits donnent l’auteur, la source et la licence. Ces couvertures ne deviennent jamais des miniatures de vidéos, ni des preuves de véhicule ou de compatibilité. Les grandes icônes décoratives sur fond uni sont exclues ; seuls les pictogrammes fonctionnels restent dans les contrôles.

Sur téléphone, les résultats et guides sont en une colonne : **photo 16:9 sur toute la largeur de la carte, puis titre et informations en dessous**. Les petites vignettes latérales de la version précédente sont abandonnées. Les titres utilisent 20–21 px ; ne pas diminuer cette taille pour accroître artificiellement la densité. Les sujets, opérations et précisions de véhicule établies doivent rester lisibles.

Sur ordinateur, la largeur de la grille se calcule après la sidebar, les filtres et les marges. Le minimum utile de 330 px par carte produit deux colonnes à 1280 px dans le cadre actuel. Trois colonnes sont réservées à une zone réellement très large, compatible avec ces dimensions et les espacements. Sous 1 000 px utiles, ne pas forcer trois colonnes. Ces règles sont constatées dans la source CSS ; leurs dimensions rendues et leurs ruptures restent à vérifier visuellement pour V17.

Le sujet réel doit survivre au recadrage. Pour une source verticale, ne pas couper un outil ou un geste essentiel pour remplir le cadre. Une photo de guide générique ne devient pas la miniature d’une vidéo particulière. La hiérarchie reste image → titre → auteur/source → langue/durée connues → action ; la provenance détaillée reste accessible.

La fiche conserve titre, auteur, plateforme, action vers la source, enregistrement et informations détaillées. Sur mobile, elle utilise un dialogue natif plein écran ; elle n’a pas été convertie en une nouvelle route. Résumé, légende native, extrait indexé et transcription doivent conserver leurs noms et niveaux de preuve. Une mention de modèle ou d’huile n’est jamais une compatibilité certifiée. Une sélection éditoriale n’est ni un visionnage complet ni une validation technique.

## Interaction et accessibilité

Labels persistants, contrôles natifs, focus visible et navigation clavier sont des invariants. Garder des cibles d’au moins 44 px pour les commandes prioritaires et une recherche à 16 px sur téléphone ; contrôler l’ensemble plutôt que supposer que ces règles couvrent toutes les cibles. Les animations non essentielles doivent disparaître avec `prefers-reduced-motion`.

Le mouvement confirme une action : accent de carte, ouverture courte de panneau, état enregistré. Pas de parallaxe, de curseur magnétique ni d’entrée en cascade de tous les résultats. Les durées et amplitudes du [contrat visuel](research/visual-direction-2026-10-23/design-contract.md) sont des choix RaceLink. Les aperçus MotionSite ont été inspectés visuellement, mais leurs captures ne prouvent ni la durée de leurs animations ni leurs performances.

Chargement, aucun résultat, erreur et indisponibilité d’aperçu restent distincts. Un filtre actif à zéro reste lisible et supprimable. Le retour d’une fiche doit conserver la recherche et son contexte. Une ouverture de guide depuis une suggestion ne doit pas réouvrir la recherche à sa fermeture.

La V17 a été poussée ; sa vérification au navigateur est en cours. Contrôler le rendu aux petites largeurs, les grandes photos et titres, la recherche visible au premier écran, le texte agrandi, le clavier, les dialogues, les résultats vides, le retour navigateur, l’enregistrement et les contrastes. Il s’agit d’un protocole de validation, pas d’une liste de tests déclarés réussis.

## Sources et preuve de validation

La méthode principale est [Impeccable — Operate](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-operate.md), complétée par [Read](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-read.md) pour les fiches et [Interface Design](https://github.com/Dammyjay93/interface-design/blob/2f9be3206855bcb2d1d0af262c8bae25cba6658d/.claude/skills/interface-design/SKILL.md) pour la cohérence des composants.

Les principes de recherche et de préparation sont documentés par [iFixit](https://about.ifixit.com/Wiki/Parts_of_a_Guide_Page), [AUTODOC Club](https://club.autodoc.co.uk/manuals), [Skillshare](https://help.skillshare.com/hc/en-us/articles/16267180286221-Search-FAQ), [Linear](https://linear.app/docs/search) et [Raycast](https://manual.raycast.com/search-bar). [La référence Dribbble de Parthik Kalsariya](https://dribbble.com/shots/26306305-Modern-Mobile-UI-for-Online-Learning-Platform) a été réellement inspectée visuellement par l’agent principal. Aucun actif tiers de cette référence n’a été repris dans l’app.

La direction de marque est fondée sur une inspection CUA réelle du [site RaceLink officiel](https://racelink-app.co/) par l’agent principal : page noire, halo rouge, titre rouge, navigation arrondie, appel à l’action blanc, téléphone sombre et polices calculées. Les aperçus publics **Driven Hero – High-Tech Section** et **Hyperion V12 – Automotive Hypercar Template** de [MotionSite](https://www.motionsite.ai/) ont également été réellement inspectés : [capture Driven](research/visual-direction-2026-10-23/motionsite-driven.png), [capture Hyperion](research/visual-direction-2026-10-23/motionsite-hyperion.png), [capture RaceLink](research/visual-direction-2026-10-23/racelink-reference.png). Ils apportent la présence de la matière mécanique et le contraste noir/blanc/rouge, pas un code ou des images à recopier. Les recherches Pinterest demeurent indexées ou refusées selon le lien ; aucune inspection visuelle non réalisée n’est revendiquée.

Une **génération texte réelle dans Flowith avec Claude Opus 5.5 affiché et sélectionné** a fourni deux compositions. Le brief public, la réponse et les décisions sont archivés dans [flowith-opus-5-5.md](research/visual-direction-2026-10-23/flowith-opus-5-5.md). La proposition « Atelier » a été adaptée : grandes couvertures, titres sous image et recherche à la jonction du hero, mais fond de lecture clair, dimensions tenant compte de la sidebar et recherche du catalogue dans le flux. Aucun code généré n’a été déployé automatiquement. La réponse précise qu’elle n’a pas ouvert les références ; ce n’est ni une observation de sites ni un test de RaceLink.

La nouvelle recherche est regroupée dans le [contrat visuel](research/visual-direction-2026-10-23/design-contract.md), les [références visuelles](research/visual-direction-2026-10-23/visual-references.md), le [rapport de skills](research/visual-direction-2026-10-23/skills-research.md) et l’[inventaire des moteurs de design](research/visual-direction-2026-10-23/design-engines.md). Les recommandations antérieures de compacité ou de titres plus petits cèdent aux règles V17 du présent document.

Les recherches documentaires et l’inspection de références restent distinguées des tests de l’application. **Aucun résultat visuel V17 n’est déclaré acquis à ce stade.** Les contrôles passés de la v14 à 1280 × 720 et dans un iframe de 390 px, ainsi que ceux des photos et du lecteur de guides, sont archivés dans leurs rapports : [V14](research/ui-redesign-2026-10-23/VALIDATION.md), [photo-v15](research/photo-covers-2026-10-23/VALIDATION.md), [guide-v16b](research/official-guides-2026-10-23/VALIDATION.md). Ils ne garantissent pas les ruptures, le focus, la visibilité de la recherche ou l’absence de débordement après la refonte V17. Aucun audit WCAG complet ou essai sur téléphone physique n’est revendiqué.

## Historique — ne constitue pas la direction courante

Avant le 23 octobre 2026 : Barlow/Barlow Condensed, canvas ivoire, composition éditoriale avec grand visuel automobile. Première refonte du 23 octobre : Manrope, canvas gris neutre, sidebar desktop et hiérarchie compacte.

**V14**, commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4), a introduit Onest/Orbitron, noir/rouge/blanc et légendes séparées après le retour sur les affiches vertes. **photo-v15**, commit [ad0cc50](https://github.com/ValerionGG/racelink-academy/commit/ad0cc50), a remplacé les couvertures de guides à pictogrammes par des photographies créditées. **guide-v16b**, commit [5e60fab](https://github.com/ValerionGG/racelink-academy/commit/5e60fab4c231976a15af0439c816cefc0dbce3d7), a ajouté le lecteur partagé et les références constructeur.

Les petites vignettes latérales, le hero masqué sur mobile et les cartes compactes de ces étapes ont été rejetés puis remplacés par **visual-v17**. Le [benchmark préalable](research/ui-redesign-2026-10-23/benchmark-mobile.md), la [direction de marque V14](research/ui-redesign-2026-10-23/brand-direction.md) et les [décisions de première refonte](research/ui-redesign-2026-10-23/DECISIONS.md) conservent leur état historique. La direction courante est celle du présent document, avec contrôle visuel V17 encore en cours.
