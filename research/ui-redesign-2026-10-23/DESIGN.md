# Interface RaceLink Academy

Référence visuelle canonique, mise à jour le **23 octobre 2026**. Ce document décrit l’interface codée dans `public/index.html`, `public/product-ui.css` et le module de découverte, ainsi que les règles à préserver. Le contexte utilisateur durable reste dans [PRODUCT.md](PRODUCT.md). Les décisions et leurs preuves sont détaillées dans [le dossier de refonte](research/ui-redesign-2026-10-23/DECISIONS.md).

## Intention

Un espace de consultation et d’apprentissage automobile : chercher une réponse, comprendre sa source, la consulter et retrouver son contexte. La recherche, le véhicule facultatif et la langue du contenu dominent le parcours. Les sélections et parcours aident à découvrir ; ils ne sont pas une étape obligatoire avant les résultats.

L’identité RaceLink repose sur la marque RL, le rouge d’action et les illustrations automobiles existantes. La navigation reste familière ; aucun instrument de cockpit ou indicateur de progression décoratif n’est nécessaire.

## Système visuel actuel

| Rôle | Valeur source | Usage |
|---|---|---|
| Police de l’interface | Manrope, puis polices système | Corps, contrôles et titres ; `--display` renvoie à la même famille. |
| Canvas | `#f5f6f8` | Fond de lecture neutre. |
| Surface | `#ffffff` | En-tête, champs, panneaux et surfaces de lecture. |
| Encre | `#19212b` | Texte principal. |
| Texte secondaire | `#586372` | Auteur, source, descriptions et informations secondaires. |
| Séparateur | `#e1e5eb` | Limites de groupes et de surfaces. |
| Rouge RaceLink | `#c82038` | Action principale, focus et repères actifs. |
| Rouge léger | `#fff0f2` | Fond des contrôles sélectionnés. |
| Navigation sombre | `#171c25` | Sidebar desktop ; texte secondaire `#aeb7c5`. |
| Rayon de référence | `14px` | Surfaces arrondies ; composants de 8 à 16 px selon leur taille. |

Manrope remplace Barlow comme police principale. Barlow Condensed reste chargé dans le HTML pour compatibilité avec les styles hérités ; il ne définit plus les titres de la couche produit. Les images et miniatures ne reçoivent pas de filtre chromatique général.

`public/product-ui.css` est le point d’édition du système produit. `public/app-ui.css` est généré par `scripts/build_ui.py`, avec des couches `legacy` puis `product` ; ne pas corriger le bundle à la main. Cette priorité de styles évite de faire dépendre la nouvelle identité de l’ordre accidentel des anciennes feuilles.

## Structure et navigation

**Ordinateur.** En-tête blanc fixe dans le défilement, sidebar sombre de 224 px, puis contenu sur canvas gris. La navigation principale est Accueil / Bibliothèque / Parcours / Enregistrés. Sujets, véhicule facultatif, aide et lien Focus sont accessibles dans la sidebar. L’état actif utilise une surface blanche et une icône rouge. Entre 761 et 1100 px, la sidebar se réduit à 192 px.

**Téléphone, jusqu’à 760 px.** La sidebar disparaît. La barre inférieure conserve **Accueil / Rechercher / Parcours / Enregistrés**, avec icône, texte, état actif et marge de sécurité du téléphone. Le grand visuel de l’accueil est masqué ; le champ de recherche reste prioritaire. Les détails et les panneaux occupent l’écran selon le système de dialogues existant.

**Accueil.** Question courte, recherche, langue des vidéos et exemples. Trois entrées illustrées compactes : Entretenir ma voiture / Mieux piloter / Régler mon simulateur. Puis « La sélection RaceLink », fondée sur les données existantes. Les autres sujets restent dans un panneau dépliable. Sur mobile, les entrées et sélections défilent horizontalement sans rotation automatique ; la liste des résultats reste verticale.

**Bibliothèque.** Recherche modifiable, contexte langue et véhicule, formats Tout / Vidéos / Guides, filtres et résultats. Le véhicule se précise progressivement ; les champs non renseignés restent inconnus. La langue du site et la langue du contenu sont deux réglages distincts. Les critères ne doivent pas être supprimés silencieusement lors d’une suggestion ou d’un retour.

## Ressources, cartes et fiches

Les cartes montrent une miniature réelle lorsqu’elle est disponible, un titre descriptif, l’auteur et la plateforme. Une miniature manquante reçoit un fond neutre. Les sélections affichent une durée uniquement connue, le statut de langue et la base du choix ; la raison, la preuve et la date de revue restent dépliables. L’illustration d’une catégorie ne devient pas une miniature de vidéo.

Sur téléphone, les résultats vidéo sont en une colonne : image à gauche, titre et informations à droite. Les guides disposent d’une carte propre. Sur ordinateur, les vidéos forment une grille et les filtres occupent une colonne contextuelle distincte de la sidebar de navigation.

La fiche conserve titre, auteur, plateforme, action vers la source, enregistrement et informations détaillées. Sur mobile, elle utilise un dialogue natif plein écran ; elle n’a pas été convertie en une nouvelle route. Résumé, légende native, extrait indexé et transcription doivent conserver leurs noms et niveaux de preuve. Une mention de modèle ou d’huile n’est jamais une compatibilité certifiée. Une sélection éditoriale n’est ni un visionnage complet ni une validation technique.

## Interaction et accessibilité

Labels persistants, contrôles natifs, focus rouge visible et navigation clavier sont des invariants. La couche produit prévoit des cibles de 44 px pour plusieurs commandes mobiles prioritaires et un champ de recherche à 16 px sur téléphone ; cela ne constitue pas un audit de toutes les cibles tactiles. Les animations et transitions sont désactivées avec `prefers-reduced-motion`.

Chargement, aucun résultat, erreur et indisponibilité d’aperçu restent distincts. Un filtre actif à zéro reste lisible et supprimable. Le retour d’une fiche doit conserver la recherche et son contexte. Une ouverture de guide depuis une suggestion ne doit pas réouvrir la recherche à sa fermeture.

Avant publication, vérifier le rendu aux petites largeurs, les longs titres FR/EN/ES, le texte agrandi, le clavier, les dialogues, les résultats vides, le retour navigateur, l’enregistrement et les contrastes. Il s’agit d’un protocole de validation, pas d’une liste de tests déclarés réussis.

## Sources et preuve de validation

La méthode principale est [Impeccable — Operate](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-operate.md), complétée par [Read](https://github.com/pbakaus/impeccable/blob/5cb95eea9c96479f57afe0732a45470d30183326/.agents/skills/impeccable/reference/mode-read.md) pour les fiches et [Interface Design](https://github.com/Dammyjay93/interface-design/blob/2f9be3206855bcb2d1d0af262c8bae25cba6658d/.claude/skills/interface-design/SKILL.md) pour la cohérence des composants.

Les principes de recherche et de préparation sont documentés par [iFixit](https://about.ifixit.com/Wiki/Parts_of_a_Guide_Page), [AUTODOC Club](https://club.autodoc.co.uk/manuals), [Skillshare](https://help.skillshare.com/hc/en-us/articles/16267180286221-Search-FAQ), [Linear](https://linear.app/docs/search) et [Raycast](https://manual.raycast.com/search-bar). [La référence Dribbble de Parthik Kalsariya](https://dribbble.com/shots/26306305-Modern-Mobile-UI-for-Online-Learning-Platform) a été réellement inspectée visuellement par l’agent principal. Aucun actif tiers de cette référence n’a été repris dans l’app.

Les agents de recherche n’avaient pas de navigateur disponible : leurs observations produit sont documentaires. L’agent principal a inspecté la version publique antérieure à 1280 × 720 et la référence Dribbble. **Au moment de cette mise à jour, le nouveau rendu n’était pas encore visuellement validé.** Les validations ultérieures doivent être consignées avec leur date et leur périmètre ; aucun audit WCAG complet ni test sur téléphone physique n’est revendiqué ici.

## Historique

Avant le 23 octobre 2026 : Barlow/Barlow Condensed, canvas ivoire, composition éditoriale avec grand visuel automobile. La refonte conserve la marque, les contenus et la recherche, mais adopte Manrope, le canvas gris neutre, la sidebar desktop et une hiérarchie plus compacte. Le [benchmark préalable](research/ui-redesign-2026-10-23/benchmark-mobile.md) conserve ses hypothèses initiales ; le présent document décrit les choix réellement codés.
