# Interface RaceLink Academy

Version courante **photo-v15**, commit [ad0cc50](https://github.com/ValerionGG/racelink-academy/commit/ad0cc50), publiée. Les couvertures des **11 guides** et les entrées de l’accueil utilisent **12 photographies réelles**. Titres sous les images, crédits accessibles, pictogrammes décoratifs retirés. [Voir la version](https://valeriongg.github.io/racelink-academy/?release=photo-v15) · [Validation et limites](research/photo-covers-2026-10-23/VALIDATION.md).

Fondation de marque antérieure, **v14 publiée le 23 octobre 2026**, commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4). Elle remplace la direction Manrope et les affiches vertes après le retour utilisateur et l’inspection réelle de [racelink-app.co](https://racelink-app.co/). L’accueil et plusieurs parcours de la v14 ont été vérifiés via CUA ; leur périmètre précis figure dans [VALIDATION.md](research/ui-redesign-2026-10-23/VALIDATION.md). La retouche v14c de compacité mobile et des badges fait l’objet d’une validation séparée. Le contexte durable reste dans [PRODUCT.md](PRODUCT.md), les preuves et arbitrages dans [brand-direction.md](research/ui-redesign-2026-10-23/brand-direction.md) et [DECISIONS.md](research/ui-redesign-2026-10-23/DECISIONS.md).

## Intention

Un espace de consultation et d’apprentissage automobile : chercher une réponse, comprendre sa source, la consulter et retrouver son contexte. La recherche, le véhicule facultatif et la langue du contenu dominent le parcours. Les sélections et parcours aident à découvrir ; ils ne sont pas une étape obligatoire avant les résultats.

L’identité RaceLink repose sur la marque RL, le noir, le rouge et le blanc, avec des images de terrain qui expliquent le sujet. La navigation reste familière ; aucun instrument de cockpit ou indicateur de progression décoratif n’est nécessaire. La recherche demeure plus importante que l’affiche.

## Système visuel v14 retenu

| Rôle | Direction retenue | Usage |
|---|---|---|
| Police de lecture | Onest, puis polices système | Corps, contrôles, titres de ressources et descriptions. |
| Accent typographique | Orbitron | Courts labels de marque ; éviter les longs titres techniques et les paragraphes dans cette police. |
| Canvas | `#f5f5f5` | Fond de lecture neutre. |
| Surface | `#ffffff` | En-tête, champs, panneaux et surfaces de lecture. |
| Encre | `#18191b` | Texte principal. |
| Texte secondaire | `#606166` | Auteur, source, descriptions et informations secondaires. |
| Séparateur | `#e1e1e3` | Limites de groupes et de surfaces. |
| Rouge officiel décoratif | `#ff2330` | Traits, accents et éléments de marque ; le blanc en petit texte sur ce rouge n’atteint pas 4,5:1. |
| Rouge d’action contrasté | `#c82038` comme référence à préserver ou équivalent vérifié | Action principale, focus et repères actifs ; blanc sur ce rouge ≈ 5,65:1. |
| Rouge léger | `#fff0f2` | Fond des contrôles sélectionnés. |
| Navigation et accueil sombres | Encre `#101012`, proche du site officiel `#0a0a0a` / `#0f0f0f` | Sidebar et zone d’accueil compacte ; recherche blanche et texte clair contrasté. |
| Rayon de référence | `14px` | Surfaces arrondies ; composants de 8 à 16 px selon leur taille. |

L’inspection CUA du site officiel a montré Onest sur le corps et Orbitron 800 sur son h1. Cette preuve de rendu prime sur la simple présence de classes Rajdhani dans le HTML. La v14 applique Onest à la lecture et réserve Orbitron aux accents. Manrope appartient à la première refonte du 23 octobre. Les images et miniatures ne reçoivent pas de filtre vert, ni de recoloration rouge systématique.

Le site officiel utilise également noir, halo rouge, navigation arrondie et bouton blanc. L’Academy en retient la famille visuelle, avec une densité adaptée à la recherche. Elle ne reproduit pas les grands effets promotionnels, les niveaux ou les compteurs de la page d’accueil officielle.

`public/product-ui.css` est le point d’édition du système produit. `public/app-ui.css` est généré par `scripts/build_ui.py`, avec des couches `legacy` puis `product` ; ne pas corriger le bundle à la main. Cette priorité de styles évite de faire dépendre la nouvelle identité de l’ordre accidentel des anciennes feuilles.

## Structure et navigation

**Ordinateur.** Cadre applicatif avec en-tête, sidebar sombre et contenu sur canvas neutre. La navigation principale est Accueil / Bibliothèque / Parcours / Enregistrés. Sujets, véhicule facultatif, aide et lien Focus restent accessibles dans la sidebar. Les changements de marque n’ajoutent pas une deuxième navigation de destinations. Les dimensions et ruptures exactes sont définies dans le CSS et doivent être contrôlées sur le rendu final.

**Téléphone, jusqu’à 760 px.** La sidebar disparaît. La barre inférieure conserve **Accueil / Rechercher / Parcours / Enregistrés**, avec icône, texte, état actif et marge de sécurité du téléphone. Le grand visuel de l’accueil est masqué ; le champ de recherche reste prioritaire. Les détails et les panneaux occupent l’écran selon le système de dialogues existant.

**Accueil.** Zone noire compacte, question courte et champ blanc clairement prioritaire ; langue des vidéos et exemples accessibles. Trois entrées illustrées : Entretenir ma voiture / Mieux piloter / Régler mon simulateur. Photos non teintées et légendes blanches séparées. Puis « La sélection RaceLink », fondée sur les données existantes. Les autres sujets restent dépliables. Sur mobile, aucune grande affiche ne doit repousser la recherche et les trois choix ; aucun carrousel ne tourne automatiquement. La liste des résultats reste verticale.

**Bibliothèque.** Recherche modifiable, contexte langue et véhicule, formats Tout / Vidéos / Guides, filtres et résultats. Le véhicule se précise progressivement ; les champs non renseignés restent inconnus. La langue du site et la langue du contenu sont deux réglages distincts. Les critères ne doivent pas être supprimés silencieusement lors d’une suggestion ou d’un retour.

## Ressources, cartes et fiches

Les cartes vidéo montrent la miniature réelle consignée, un titre descriptif, l’auteur et la plateforme. Une miniature manquante reçoit un fond neutre. Les sélections affichent une durée uniquement connue, le statut de langue et la base du choix ; la raison, la preuve et la date de revue restent dépliables. Les badges de sélection sont sobres, sans dominante verte ni fausse certification.

Les portes de découverte et les onze guides utilisent des photographies réelles non teintées, accompagnées d’une légende hors image. Les crédits donnent l’auteur, la source et la licence. Ces couvertures ne deviennent jamais des miniatures de vidéos, ni des preuves de véhicule ou de compatibilité. Les grandes icônes décoratives sur fond uni sont exclues ; seuls les pictogrammes fonctionnels restent dans les contrôles.

Sur téléphone, les résultats vidéo sont en une colonne : image à gauche, titre et informations à droite. Les guides disposent d’une carte propre. Sur ordinateur, les vidéos forment une grille et les filtres occupent une colonne contextuelle distincte de la sidebar de navigation.

La fiche conserve titre, auteur, plateforme, action vers la source, enregistrement et informations détaillées. Sur mobile, elle utilise un dialogue natif plein écran ; elle n’a pas été convertie en une nouvelle route. Résumé, légende native, extrait indexé et transcription doivent conserver leurs noms et niveaux de preuve. Une mention de modèle ou d’huile n’est jamais une compatibilité certifiée. Une sélection éditoriale n’est ni un visionnage complet ni une validation technique.

## Interaction et accessibilité

Labels persistants, contrôles natifs, focus visible et navigation clavier sont des invariants. Garder des cibles d’au moins 44 px pour les commandes prioritaires et une recherche à 16 px sur téléphone ; contrôler l’ensemble plutôt que supposer que ces règles couvrent toutes les cibles. Les animations non essentielles doivent disparaître avec `prefers-reduced-motion`.

Le mouvement confirme une action : accent de carte, ouverture courte de panneau, état enregistré. Pas de parallaxe, de curseur magnétique ni d’entrée en cascade de tous les résultats. Les durées proposées dans [brand-direction.md](research/ui-redesign-2026-10-23/brand-direction.md) sont des choix RaceLink ; aucune animation MotionSite n’a été observée ou mesurée.

Chargement, aucun résultat, erreur et indisponibilité d’aperçu restent distincts. Un filtre actif à zéro reste lisible et supprimable. Le retour d’une fiche doit conserver la recherche et son contexte. Une ouverture de guide depuis une suggestion ne doit pas réouvrir la recherche à sa fermeture.

Avant publication, vérifier le rendu aux petites largeurs, les longs titres FR/EN/ES, le texte agrandi, le clavier, les dialogues, les résultats vides, le retour navigateur, l’enregistrement et les contrastes. Il s’agit d’un protocole de validation, pas d’une liste de tests déclarés réussis.

## Sources et preuve de validation

La méthode principale est [Impeccable — Operate](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-operate.md), complétée par [Read](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-read.md) pour les fiches et [Interface Design](https://github.com/Dammyjay93/interface-design/blob/2f9be3206855bcb2d1d0af262c8bae25cba6658d/.claude/skills/interface-design/SKILL.md) pour la cohérence des composants.

Les principes de recherche et de préparation sont documentés par [iFixit](https://about.ifixit.com/Wiki/Parts_of_a_Guide_Page), [AUTODOC Club](https://club.autodoc.co.uk/manuals), [Skillshare](https://help.skillshare.com/hc/en-us/articles/16267180286221-Search-FAQ), [Linear](https://linear.app/docs/search) et [Raycast](https://manual.raycast.com/search-bar). [La référence Dribbble de Parthik Kalsariya](https://dribbble.com/shots/26306305-Modern-Mobile-UI-for-Online-Learning-Platform) a été réellement inspectée visuellement par l’agent principal. Aucun actif tiers de cette référence n’a été repris dans l’app.

La direction de marque est désormais fondée sur une inspection CUA réelle du [site RaceLink officiel](https://racelink-app.co/) par l’agent principal : page noire, halo rouge, titre rouge, navigation arrondie, appel à l’action blanc, téléphone sombre et polices calculées. Les recherches [Pinterest](https://uk.pinterest.com/pin/motorsport-project-app-design--155655730846334439/) restent indexées uniquement, avec refus d’ouverture ; la galerie [MotionSite](https://www.motionsite.ai/) est documentée par son index officiel, pas par des animations inspectées. Aucun refus n’a été contourné ni actif copié.

Les recherches documentaires et l’inspection de références restent distinguées des tests de l’application. La v14 publiée a été observée via CUA à 1280 × 720 et dans un iframe de 390 px ; onze guides, retour du focus après fermeture, recherche française, suggestions et conservation des critères ont été contrôlés. Le document mobile mesurait 375 px utiles et 375 px défilables. Voir [VALIDATION.md](research/ui-redesign-2026-10-23/VALIDATION.md) pour les étapes, captures et limites, ainsi que la dernière validation v14c consignée. Aucun test v14 à 320/430/768 px, audit WCAG complet ou essai sur téléphone physique n’est déduit de ces contrôles.

## Historique

Avant le 23 octobre 2026 : Barlow/Barlow Condensed, canvas ivoire, composition éditoriale avec grand visuel automobile. Première refonte du 23 octobre : Manrope, canvas gris neutre, sidebar desktop et hiérarchie compacte. Après le retour sur les affiches vertes : direction v14 Onest/Orbitron, noir/rouge/blanc, cartes photo avec légende séparée et couvertures de guides noir/argent/rouge. Le [benchmark préalable](research/ui-redesign-2026-10-23/benchmark-mobile.md) et les [décisions de première refonte](research/ui-redesign-2026-10-23/DECISIONS.md) conservent leur état historique ; la direction courante est celle du présent document.
