# Contrat de référence — RaceLink V18

23 octobre 2026. Méthode appliquée : [OpenDesign `reference-design-contract`](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/skills/reference-design-contract/SKILL.md), installé à révision fixe. Ce contrat adapte son workflow à la demande : un document court et le `DESIGN.md` existant, sans imposer neuf nouvelles rubriques ni produire une charte concurrente.

**But :** permettre à une personne, notamment sur téléphone près de sa voiture, de trouver une ressource, comprendre son sujet et sa provenance, puis revenir à sa recherche. La direction est photographique, pratique et familière : grandes images réelles, surfaces de lecture claires, navigation noire et accents rouges RaceLink. Le moteur, le thème et la langue ne sont jamais déduits de l'apparence d'une image.

## Preuves et frontières

| Référence | Base réellement disponible | Conserver | Adapter | Ne pas reprendre |
|---|---|---|---|---|
| RaceLink actuel | `PRODUCT.md`, corps de `DESIGN.md` et `public/product-ui.css` lus ; source observée, pas nouveau test visuel | Onest/Orbitron, couleurs, grandes photos, contexte de recherche | Langue du contenu toujours visible sur mobile ; hiérarchie des badges | Les anciennes petites vignettes et affiches à pictogrammes rejetées |
| Site RaceLink et MotionSite | Inspection et captures documentées par l'agent principal dans `research/visual-direction-2026-10-23/` ; preuve antérieure attribuée | Matière mécanique, contraste, présence photographique | Composition adaptée à la consultation d'une bibliothèque | Actifs, logos tiers, code, affirmations et animations supposées |
| Analyses BMW M / Airbnb de VoltAgent | Sections du texte consultées ; interprétations de VoltAgent | Image importante, titre sous l'image, colonne mobile, recherche structurante | Grille calculée après le rail et les marges | Charte de marque copiée, polices propriétaires, notes ou compteurs inventés |
| Google DESIGN.md | Spécification alpha lue et valeurs CSS existantes relevées | Valeurs structurées, rôles, variantes | Frontmatter ajouté sans réécrire le corps | Migration Tailwind ou nouveau thème sans besoin |

## Décisions à préserver

- **Photographies.** Guides avec couverture réelle et crédit ; vidéos avec leur propre miniature. Cadre 16:9 large, sujet utile préservé, titre en dessous. Aucune recoloration systématique ni photo de stock présentée comme image d'une vidéo. Une miniature absente reste un état explicite.
- **Mobile.** Une colonne de résultats, titres 20–21 px selon la largeur existante. La recherche et le réglage « langue du contenu » restent repérables à 320 et 390 px. Le réglage de langue d'interface demeure distinct. Le panneau de recherche conserve le choix de langue et les critères actifs.
- **Navigation.** Rail desktop avec liens ou boutons HTML natifs ; barre inférieure mobile avec libellés et état actif. Ne pas transformer la navigation en canvas ou en gestes invisibles. Les dialogues gardent fermeture clavier et retour du focus.
- **Badges.** Un libellé décrit le format ou la sélection, sans ressembler à une certification technique. « Proposé par RaceLink » doit rester lisible, ne pas masquer le sujet et donner accès à sa raison et sa preuve. Aucune durée, langue déclarée ou note fabriquée.
- **Mouvement.** Valeurs existantes seulement : pression 150 ms avec courbe actuelle ; transition des boutons 180 ms. L'absence d'animation avec `prefers-reduced-motion` reste prioritaire. Aucun effet Canvas UI nécessaire.

## Contrôle de la première version modifiée

À vérifier sur le rendu réel, sans présenter cette liste comme des tests déjà passés :

1. À 320/390 px, image pleine largeur, titre lisible et aucune découpe du geste essentiel ; pas de défilement horizontal du document.
2. Recherche et langue du contenu trouvables sans deviner une icône ; choix conservé après suggestion, fiche, retour et navigation.
3. Au clavier, rail et barre mobile utilisables, focus visible ; chaque dialogue rend le focus au déclencheur ou à la destination attendue.
4. Badge, source et auteur lisibles avec texte agrandi ; pas de chevauchement sur image, pas de fausse validation technique.
5. À 1280 px, grille tenant compte du rail : minimum utile existant de 330 px par carte, sans forcer trois petites colonnes. Les états vide, erreur et image absente restent distincts.

Le document expose les exigences ; il ne garantit pas leur satisfaction. Aucun nouveau navigateur ou appareil physique n'a été testé pendant cette application documentaire.

## Handoff et limites du skill

Lire `PRODUCT.md`, le `DESIGN.md` enrichi, puis ce contrat avant toute modification. Éditer la source CSS produit et les modules concernés dans le périmètre assigné ; ne pas modifier le bundle généré à la main. Démontrer une vue bibliothèque mobile et desktop avant de généraliser.

Les trois références `craft` d'OpenDesign ont été lues séparément et archivées. Codex n'exécute pas leur injection automatique OpenDesign. Leurs prescriptions arbitraires — plafond de deux accents, interdiction du noir pur, règles typographiques universelles et seuils simplifiés — ne remplacent ni le brief RaceLink ni les exigences d'accessibilité. L'exemple HTML du skill est une démonstration, pas un thème à recopier. Le workflow et sa checklist sont installés ; aucun daemon OpenDesign, moteur GPU ou script de skill n'est lancé.
