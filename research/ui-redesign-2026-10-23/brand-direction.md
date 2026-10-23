# RaceLink Academy — direction des visuels et des interactions

Version finale v14c publiée et vérifiée : [rapport de validation](VALIDATION.md). Les étapes ci-dessous conservent les versions observées.

Recherche du 23 octobre 2026, après le retour utilisateur sur les affiches vertes. **V14 publiée**, commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4) : Onest, accents Orbitron, noir/rouge/blanc, accueil noir compact avec champ blanc, photos non teintées et légendes blanches, onze couvertures de guides SVG noir/argent/rouge. Le rendu et plusieurs parcours de cette version ont été observés via CUA. La validation de la retouche v14c reste suivie séparément dans [VALIDATION.md](VALIDATION.md). Aucun fichier applicatif modifié par cette recherche documentaire.

## Direction retenue

**Faire une bibliothèque RaceLink, avec des images de terrain et une lecture nette.** Conserver la recherche, les contenus et les quatre destinations mobiles au premier plan. Remplacer le traitement vert des portes d’entrée par trois compositions distinctes, lisibles à petite taille : geste mécanique, repère de pilotage, matériel de simulation. Le rouge relie l’ensemble à la marque ; il n’a pas à recolorer les photographies.

Le résultat attendu est une application que l’on comprend rapidement : une demande, un véhicule facultatif, une langue de contenu, puis des ressources dont le titre et l’auteur sont visibles. Les affiches ne doivent pas prendre la place des vidéos ni faire croire à trois cours produits par RaceLink.

## Ce que les sources établissent

| Référence | Auteur ou éditeur | Preuve disponible le 23 octobre | Enseignement et limite |
|---|---|---|---|
| [RaceLink — site officiel](https://racelink-app.co/) | RaceLink | Texte et HTML inspectés par l’agent de recherche ; page réellement inspectée via CUA par l’agent principal, avec styles calculés du corps et du h1. | Page noire avec halo rouge, mot Motorsport rouge, navigation noire arrondie, bouton Apple blanc et téléphone sombre. Corps Onest ; h1 Orbitron 800. Reprendre cette filiation, sans transformer l’Academy en page promotionnelle ni importer de faux niveaux. |
| [MotionSite AI — galerie](https://www.motionsite.ai/) | MotionSite AI | Résultat de recherche officiel indexé ; ouverture directe précédemment indisponible pour l’agent principal. Aucune animation inspectée. | La page décrit une bibliothèque de prompts et templates, avec notamment Hyperion V12 dans Automotive et CodeYoung dans Education. C’est une piste de compositions, pas une preuve d’efficacité, de qualité du code ou de performance mobile. Aucun prompt payant acquis. |
| [MotionSite AI — blog](https://www.motionsite.ai/blog) | MotionSite AI | Texte officiel indexé. | Deux entrées datées des 18 et 19 octobre portent sur les interfaces SaaS et le glassmorphism. Cela renseigne le positionnement éditorial ; cela ne justifie pas du verre flouté partout dans une bibliothèque. |
| [Motorsport project // App design](https://uk.pinterest.com/pin/motorsport-project-app-design--155655730846334439/) | Créateur non confirmé | Titre indexé ; ouverture du pin : 403. | Piste de recherche directement liée à une application motorsport. Composition et auteur non confirmés : aucune règle visuelle n’en est déduite. |
| [Racing Car Design with Red, White, and Black Color Scheme](https://www.pinterest.com/pin/602426887636045103/) | Créateur non confirmé | Titre indexé ; ouverture indisponible. | Piste chromatique seulement, à ne pas présenter comme une image inspectée. Aucun actif repris. |
| [Red and White Racing Poster](https://es.pinterest.com/pin/red-and-white-racing-poster--707135578991960575/) | Créateur non confirmé | Titre indexé ; ouverture : 403. | Piste d’affiche sportive, sans preuve de composition ni de lisibilité mobile. Aucun autre accès essayé après le refus. |
| [Modern Mobile UI for Online Learning Platform](https://dribbble.com/shots/26306305-Modern-Mobile-UI-for-Online-Learning-Platform) | Parthik Kalsariya | Image réellement inspectée par l’agent principal via CUA lors de la recherche précédente. | Référence de hiérarchie mobile : recherche, catégories et navigation inférieure. C’est un concept de portfolio ; aucune donnée d’usage indépendante n’a été établie. |
| [Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) et [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) | W3C WAI et MDN | Documentation primaire lue. | Permettre la réduction du mouvement non essentiel. Le critère WCAG cité est de niveau AAA ; sa lecture n’est pas un audit de conformité de l’Academy. |

Pinterest a bien été recherché sur des pins individuels, au-delà d’un feed. Les titres indexés servent à retrouver des pistes, pas à inventer leur mise en page. Aucun login, CAPTCHA ou refus n’a été contourné. MotionSite n’a pas été assimilé à un autre service portant un nom proche.

## Filiation RaceLink vérifiable

Dans le HTML officiel, `#FF2330` colore un mot du titre principal et plusieurs accents. Une progression emploie un dégradé `#BC0606` vers `#FF2330`. Des surfaces utilisent `#0F0F0F`, `#0A0A0A` et du blanc translucide. Les classes `font-rajdhani` et `font-onest` sont présentes ; **le style calculé effectivement observé par l’agent principal est Onest sur le corps et Orbitron 800 sur le h1**. La présence d’une classe ne suffit donc pas à identifier la police rendue. Le vert `#A6E22E` apparaît sur un indicateur de niveau ; cette présence ponctuelle ne démontre pas que des affiches vertes doivent structurer l’Academy. [Source officielle](https://racelink-app.co/)

Choix final v14 : **Onest pour les titres de vidéos, les contrôles et la lecture ; Orbitron pour de courts labels et accents de marque.** Cette décision remplace la proposition initiale de conserver Manrope. Le canvas gris neutre et les cartes blanches restent des surfaces de lecture ; la navigation sombre et un accueil noir compact portent l’identité. Le rouge officiel convient à un trait, un pictogramme décoratif ou un aplat avec texte adapté. Il faut vérifier séparément les petits textes et les boutons : le blanc sur `#FF2330` donne environ 3,79:1, contre 5,65:1 sur `#C82038` selon le calcul sRGB. Ces ratios ne remplacent pas l’examen de tous les états.

## Diagnostic historique des affiches vertes

La lecture du code avant correction montre plusieurs sources indépendantes, pas seulement des images :

- `product-ui.css`, lignes 86–88 : fond de `.academy-scene` en `#27342f`, voile `.scene-shade` teinté vert.
- Lignes 107–109 : fonds `.entry-card` et `.entry-visual` en `#27342c`, puis voile sombre sur la totalité de la carte.
- Lignes 221–223 et 312 : badges de sélection et bloc de détail teintés vert.
- `visual-assets.json` : trois illustrations de cours Focus, dont la nature photographique ou générée n’est pas établie. Leur provenance est documentée ; elles ne sont pas les miniatures de vidéos du catalogue.

Ces lignes décrivent l’état avant correction, pas le CSS publié de la v14. Elles expliquent pourquoi remplacer seulement l’image aurait laissé une dominante verte. La v14 sépare image, titre et commande ; la retouche v14c retire les derniers verts des badges et repères de contexte. Son état de validation est indiqué dans [VALIDATION.md](VALIDATION.md).

## Brief des trois cartes

| Porte | Image à privilégier | Composition et texte | À éviter |
|---|---|---|---|
| Entretenir ma voiture | Cadrage rapproché d’un geste identifiable dans un atelier : outil, pièce et main lisibles ; décor secondaire. | Image panoramique, couleurs naturelles, légende blanche sous l’image. Titre sur deux lignes maximum ; repères courts « Entretien · Diagnostic ». | Vue générique de supercar, fumée, texte incrusté dans l’image, visuel d’une réparation risquée ou incompatible. |
| Mieux piloter | Habitacle ou regard vers une portion de circuit montrant une trajectoire ou un point de freinage identifiable. | Contraste net, détail rouge discret ; même format que les deux autres cartes. Repères « Freinage · Trajectoires ». | Photo de podium ou de voiture spectaculaire qui n’aide pas à comprendre le sujet ; fausse télémétrie. |
| Régler mon simulateur | Volant, pédalier ou poste de simulation en usage ; matériel distinct d’un cockpit réel. | Lumière neutre, geste ou réglage visible, repères « Réglages · Technique ». | Éclairage RGB dominant, écrans contenant du texte illisible, faux temps au tour. |

Les repères décrivent des familles réellement présentes, pas un engagement sur chaque ressource. Si les images sont générées pour ces portes, les traiter comme des illustrations éditoriales, sans marque ou événement inventé. Conserver les miniatures d’origine pour les vidéos ; une illustration ne doit jamais prendre leur place.

Sur desktop, trois cartes de même largeur suffisent. Sur téléphone, proposer trois lignes compactes avec une image latérale et le titre en clair permettrait de voir les trois choix sans rail caché. C’est une recommandation à comparer au rendu, pas un constat de test. Une seule zone cliquable par carte ; aucun bouton imbriqué. Aucun chiffre décoratif, faux niveau ou indicateur de progression.

## Sélections, résultats et filtres

Les sélections doivent ressembler à des ressources : miniature, durée seulement si connue, titre, auteur, plateforme et langue. Le statut de la sélection peut tenir dans un libellé discret ; sa justification reste dans « Pourquoi ce choix ». Le badge ne doit pas suggérer que toutes les vidéos ont été visionnées.

Dans les résultats, garder les titres de procédures assez longs pour conserver la pièce et le véhicule cités. Le contexte choisi doit rester lisible au-dessus de la liste, avec effacement individuel : véhicule, langue, format. La langue d’interface reste distincte de la langue des ressources. Un modèle extrait d’un titre ne devient pas une promesse de compatibilité.

Sur mobile, la recherche et les trois choix doivent apparaître avant une nouvelle grande affiche. Garder quatre destinations stables. Le panneau de filtres possède un titre, des valeurs lisibles, un effacement et une action de retour aux résultats ; le clavier ne doit pas masquer sa commande principale. Aucune nouvelle fonction n’est demandée ici : la priorité est de rendre ces actions existantes évidentes.

## Mouvement proposé : montrer un changement d’état

Ces durées sont des choix de conception proposés pour RaceLink, non des mesures de MotionSite.

| Interaction | Proposition | Mode mouvement réduit |
|---|---|---|
| Survol desktop d’une carte | Bordure/accent et déplacement de flèche de 2–3 px, environ 140 ms ; aucune information nouvelle au seul survol. | Couleur ou bordure immédiate. |
| Pression tactile | Retour visuel de fond ou de bordure ; ne pas réduire toute la page. | Retour immédiat. |
| Ouverture de filtres | Translation courte du panneau, 180–220 ms ; focus dans le panneau et position préservée à la fermeture. | Affichage immédiat, mêmes règles de focus. |
| Enregistrement | Icône et texte changent ensemble ; confirmation brève sans déplacement de carte. | Même confirmation sans interpolation. |
| Résultats d’une recherche | Mettre à jour le compte et la liste sans cascade animée ; ne pas faire rejouer l’entrée de toutes les cartes. | Identique. |

Aucun autoplay, parallaxe, curseur magnétique ou animation permanente n’est nécessaire pour trouver une procédure. Le mouvement sert la relation entre une action et sa réponse. Les règles de réduction viennent de la documentation [W3C](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) et [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion), pas d’une imitation présumée de MotionSite.

## Réalisation et vérification

La v14 publiée a été observée via CUA sur l’accueil à 1280 × 720 et dans un iframe de 390 px. Les onze guides sont visibles ; le guide carburants a été ouvert puis fermé avec restauration du focus. Sur mobile, la langue française et la requête « vidange Clio 3 » donnent deux vidéos ; les suggestions s’affichent, Entrée rend le focus à la commande de modification de recherche. Le filtre YouTube conserve la requête et le français, puis rend le focus au titre des résultats. La largeur utile et la largeur défilable du document mobile sont toutes deux de 375 px.

Ces scénarios ne constituent pas une validation de tous les états, des largeurs 320/430/768 ou d’un appareil physique. La retouche v14c compacte l’interface mobile et retire le vert résiduel des badges ; consulter [VALIDATION.md](VALIDATION.md) pour sa dernière passe et les captures. [DESIGN.md](../../DESIGN.md) formalise la direction courante ; [PRODUCT.md](../../PRODUCT.md) conserve les invariants du produit. Les durées de mouvement et la variante de trois lignes mobiles proposées plus haut restent des recommandations lorsqu’elles ne sont pas explicitement réalisées.

Méthode suivie : skill `design-inspiration`, preuves distinguées entre HTML, texte, index et image inspectée. Les recherches précédentes et les liens amont sont détaillés dans [benchmark-mobile.md](benchmark-mobile.md) et [skills-report.md](skills-report.md). Aucun actif Pinterest, Dribbble ou MotionSite n’a été copié.
