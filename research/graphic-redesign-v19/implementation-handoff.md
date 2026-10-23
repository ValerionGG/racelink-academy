# Handoff d'implémentation — RaceLink V19

À lire avant le code : [contrat V19](design-contract.md), `../../PRODUCT.md`, `../../DESIGN.md`, `../../public/photo-sources.json` et [validation V18 historique](../skills-roundup-2026-10-23/VALIDATION.md). Le contrat V19 autorise la recomposition ; le produit, les données et les niveaux de preuve restent inchangés. La modification de DESIGN/PRODUCT revient à l'agent principal.

## Exécution visuelle

1. **Refondre `public/product-ui.css` comme source unique.** Ne pas ajouter une nouvelle feuille de correctifs ni modifier `app-ui.css` à la main. Le build existant gère les couches CSS. Conserver une priorité explicite pour `[hidden]`, vues alternatives, dialogues et mode résultats.
2. **Remplacer la sidebar fixe par un header horizontal.** Quatre destinations principales, état actif, labels et boutons/liens natifs. Réutiliser les handlers `data-view`, `data-browse-all`, `data-open-search`, `data-open-navigation` et `data-open-vehicle`. Garder l'accès direct aux guides, à l'aide et aux sources, sans multiplier les destinations.
3. **Recomposer le hero.** Panneau clair à gauche pour titre/recherche/langue ; `oil.jpg` à droite, sans teinte ni texte superposé. Sur mobile, remettre réellement l'ordre texte/recherche/langue/photo, en cohérence DOM et visuel. Ne pas dupliquer `#search-form`, `#search`, `#home-language` ou les suggestions : le module mobile déplace le formulaire existant.
4. **Conserver les grands visuels partout.** Deux colonnes de résultats à 1280 px avec filtres latéraux ; une colonne mobile. Image avant le titre, métadonnées lisibles, badge sobre hors du geste. Les portes de catégories reprennent les trois photos existantes. Ne pas remplacer les miniatures vidéo par ces photos génériques.
5. **Appliquer les valeurs du contrat.** Papier `#f5f5f4`, blanc `#fff`, encre `#121314`, secondaire `#5e6065`, action `#c82038`. Onest pour la lecture ; Orbitron seulement pour la marque. Rayon proposé : 12 px sur images, 10 px sur contrôles, 16 px sur panneaux ; pas de grande carte arrondie imbriquée autour de chaque bloc.

## Inventaire réel disponible

Fichiers relevés le 23/10/2026 dans `public/assets/photos/` : **12 JPG, 1 450 046 octets au total**. Dimensions ci-dessous lues dans les fichiers locaux, pas confondues avec les originaux des fournisseurs. Sources, auteurs, limites et licences sont archivés dans `public/photo-sources.json` ; mappings actuels dans `public/guide-photos.js`.

| Fichier | Dimensions locales | Sujet / usage conseillé | Auteur et licence archivés |
|---|---|---|---|
| `oil.jpg` | 960 × 640 | **Hero V19** : versement d'huile, geste et matière au centre ; aussi guides huile | Daniel Andraski — Pexels |
| `service.jpg` | 960 × 540 | Porte Entretien ; atelier et moteur sur support, pas diagnostic particulier | Artem Podrez — Pexels |
| `driving.jpg` | 960 × 1440 | Porte Pilotage ; cockpit vertical, préserver volant et tableau de bord | Dani / shotbydani — Unsplash |
| `simracing.jpg` | 960 × 640 | Porte Sim racing ; pilotes sur simulateurs à un événement | Matti Blume — CC BY-SA 4.0 |
| `wheel.jpg` | 960 × 640 | Guide roue ; roue complète tenue devant une voiture sur pont | Andrea Piacquadio — Pexels |
| `fuel.jpg` | 960 × 720 | Guide carburant ; main et pistolet, couleur sans valeur de compatibilité | Engin Akyurt — Pexels |
| `battery.jpg` | 960 × 640 | Guide batterie ; câbles de démarrage, pas validation d'un ordre de branchement | Daniel @ bestjumpstarterreview.com — Pexels |
| `wipers.jpg` | 960 × 640 | Guide essuie-glaces ; voiture ancienne, pas fixation moderne universelle | Maria Tyutina — Pexels |
| `diagnostics.jpg` | 1280 × 853 | Guide diagnostic ; connecteur OBD, pas écran de résultat | Arp — domaine public / CC0 |
| `fuses.jpg` | 960 × 640 | Guide fusibles ; boîtier et connexions, pas plan d'affectation universel | Shixart1985 — CC BY 2.0 |
| `lighting.jpg` | 960 × 641 | Guide éclairage ; détail d'optique automobile | Nenad Stojković / Shixart1985 — CC BY 2.0 |
| `identification.jpg` | 960 × 720 | Guide identification ; plaque Audi documentaire, numéro modifié par l'auteur | Hans Haase — CC BY-SA 3.0 |

Pixels de `oil`, `service`, `driving` et `simracing` réellement relus avec `view_image` pour V19. Les autres descriptions reprennent leurs preuves locales antérieures ; aucune nouvelle visite fournisseur. Sur le hero, `oil.jpg` montre le bidon, les mains et le filet d'huile : conserver cette zone centrale. Pour le cockpit portrait, partir du cadrage existant `50% 49%`, puis contrôler le rendu ; ne pas couper le volant pour satisfaire un ratio. Ne pas inventer de recadrage jugé réussi avant observation.

**Crédits :** préserver l'accès à `photo-credits.html` et les mentions des images CC ; leur licence ne devient pas celle du code. Les images de marque ou les personnes représentées ne constituent pas un soutien à RaceLink. Aucun téléchargement ni nouvelle image requis dans ce handoff.

**Fontes :** aucun `.woff`, `.woff2` ou `.ttf` trouvé dans `public/assets`. `index.html` charge actuellement Onest **400/500/600/700/800** et Orbitron **600/700/800** via Google Fonts, avec `display=swap`. CSS : Onest → `system-ui` → `sans-serif` ; Orbitron → Onest. Réutiliser ces familles et poids, sans ajouter de police ou dépendance. Le rendu de repli doit rester lisible ; cette passe n'a pas retéléchargé les fontes ni leurs licences.

## Conditions de réception

La première livraison montre **accueil desktop + mobile, catalogue et recherche mobile**, avant généralisation aux autres vues. À 1280 px, les deux photos de résultats gardent une largeur utile d'au moins 330 px ; à 390 px, la couverture de carte reste proche de 358 × 201 px avec marges de 16 px. À 320 px, réduire les colonnes, jamais le visuel en vignette latérale. Le champ et sa langue restent visibles avant la photo d'accueil.

Rejouer : langue conservée avec saisie et véhicule ; flèches/Entrée/Échap dans les suggestions ; ouverture/fermeture vidéo et guide ; focus rendu ; lien de notice ; commandes de rails ; enregistrement ; retour navigateur ; état vide/erreur. Tester aussi agrandissement du texte et mouvement réduit. Garder les limites de preuve et le statut de langue. Les tests V18 fournissent des cas de régression, pas un certificat pour V19.

Le catalogue, l'API et les preuves de contenu n'ont pas besoin d'être modifiés pour cette refonte. Les deux documents présents sont une préparation : aucun frontend, DESIGN, PRODUCT, actif ou état Git n'a été modifié par leur auteur pendant cette mission.
