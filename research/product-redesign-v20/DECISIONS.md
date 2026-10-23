# V20 — Décisions de recherche et de consultation

23 octobre 2026 · `workshop-v20`. **Publication finale et vérifications ciblées terminées.** [Version publique](https://valeriongg.github.io/racelink-academy/?release=workshop-v20). Référence finale publiée [`17ea9abab52b9028b5863db61e6537dd939a3be7`](https://github.com/ValerionGG/racelink-academy/commit/17ea9abab52b9028b5863db61e6537dd939a3be7), [workflow 39997940444](https://github.com/ValerionGG/racelink-academy/actions/runs/39997940444). Interactions contrôlées sur `5a48d1f`, contrôle HTTP et deux finitions CSS vérifiés sur `17ea9ab`. La [validation](VALIDATION.md) garde la portée de chaque contrôle.

## Périmètre et problème

La demande porte sur une refonte profonde des cartes, fiches, recherche et filtres. L'accueil photographique V19 ne constitue pas le chantier de cette itération. Le [rapport UX](search-ux.md), dont la source de travail est `work/redesign-v20/search-ux.md`, part de captures V19 réellement inspectées : sur mobile, de nombreuses rangées de contexte et d'explication précédaient la première photo de résultat. Les filtres commençaient par les disciplines avant les préférences utiles ; les fiches demandaient de parcourir un bloc média avant de comprendre le sujet.

Le rapport distingue ses observations de code, ses lectures de sources primaires et ses propositions. Son benchmark iFixit, AUTODOC Club et aide YouTube ne prétend pas être une visite visuelle complète de ces plateformes. Sa copie stable `search-ux.md` accompagne cette note ; la [contrelecture du rendu](visual-review.md) est un document séparé.

## Décisions appliquées

| Décision | Réalisation source | Utilité et limite |
|---|---|---|
| Un contexte court | Recherche, langue, voiture et bouton Filtres dans l'en-tête des résultats ; question/langue retirées des puces répétitives. | Réduire la hauteur avant les ressources sans confondre langue du site et du contenu. |
| Un seul panneau de filtres | Contrôles existants déplacés dans le même dialogue natif desktop/mobile ; préférences, plateformes, sujets repliés et groupe avancé. | Pas de sidebar permanente ni de copie de formulaire. Changements immédiats ; le bouton « Voir N résultats » ferme le panneau. |
| Des explications à la demande | Interprétation et guide conseillé sous « Comprendre ces résultats ». Un conflit de véhicule ouvre l'élément. | Préserver la portée du résultat sans imposer tout le contexte à chaque recherche. |
| Une carte qui renseigne | Grande image 16:9, sujet/langue, titre, description existante attribuée, auteur/plateforme et actions distinctes. | La préfiche est la carte elle-même. Aucun écran intermédiaire ni résumé issu d'un visionnage supposé. |
| Un lecteur vidéo organisé | Titre/auteur en haut ; média et repères à gauche, contenu/transcription/notes à droite sur grand écran. | La lecture externe attend l'action. Provenance, droits et questions restent accessibles dans des disclosures. |
| Un guide structuré par usage | Photo, résumé existant, plan, prérequis avant méthode, puis notices constructeur distinctes. Première référence nommée sur la carte. | Le guide reste une méthode générale. Chaque source conserve modèle, période, limites et attribution. |
| Une grille ample | Deux colonnes desktop, une colonne mobile, y compris catalogue de guides seuls. | Le sélecteur historique plus spécifique des guides a été repris dans les règles V20. Les captures montrent les grandes cartes sur ordinateur et mobile. |

## Écarts assumés à la proposition initiale

- Sur mobile, la fiche vidéo est **titre/auteur → média et repères → contenu**. Le rapport proposait un aperçu descriptif avant le média ; cet ordre n'est pas implémenté et n'est pas revendiqué.
- L'onglet Transcription reste visible quand le texte manque, avec un état explicite. Le rapport proposait de moins mettre en avant cet onglet vide.
- Les sujets sont repliés dans leur ensemble ; une séparation automatique « sujets disponibles / autres sujets à zéro » n'est pas présentée comme acquise.
- Les propositions de sorties ciblées du zéro résultat — retirer seulement l'année, le moteur ou un terme — restent distinctes du comportement actuel de réinitialisation. La documentation n'annonce pas ces nouveaux raccourcis.
- La cible de première image à environ 320–360 px du haut à 390 × 844, proposée dans le rapport de composition, n'est pas atteinte dans l'état mesuré : la première ressource commence à **406,75 px** et reste visible. Cette mesure vaut pour le scénario consigné, pas pour toute recherche ; la cible n'est pas une règle WCAG.

## Rôle réel des skills

| Ressource | Usage dans cette itération |
|---|---|
| [Impeccable — SKILL.md](C:/Users/Nad/.codex/skills/impeccable/SKILL.md) et [registre produit](C:/Users/Nad/.codex/skills/impeccable/reference/product.md) | Lus et appliqués : familiarité des commandes, hiérarchie de tâche, dévoilement progressif, typographie de lecture, états explicites. Le script de contexte local a trouvé PRODUCT.md et DESIGN.md existants ; aucune nouvelle palette automatique n'a été générée. |
| [Frontend Design — SKILL.md](C:/Users/Nad/.codex/skills/frontend-design/SKILL.md) | Lu et appliqué à l'architecture visuelle, à la typographie et à la composition des grandes cartes. Son usage ne remplace pas la vérification du rendu et des interactions. |
| [Reference Design Contract](https://github.com/nexu-io/open-design/blob/e03d5c23f308c39f4de7c057568df66c29a84385/skills/reference-design-contract/SKILL.md) | Cadre documentaire installé antérieurement ; les neuf sections de DESIGN.md restent utilisées. Aucune nouvelle installation ni nouvelle visite de référence revendiquée. |
| Google DESIGN.md | Frontmatter structuré conservé et synchronisé avec les valeurs effectives V20 ; le format alpha et ses limites sont maintenus. Aucun lint officiel réussi n'est annoncé. |
| Taste, UI UX Pro Max et autres ressources V18 | Ressources auditées/installées lors d'itérations précédentes. Aucun nouvel appel de leur moteur ou script n'est revendiqué ici. Leur présence n'est pas présentée comme une validation du produit. |

Les références RaceLink/MotionSite et la consultation Flowith/Claude Opus 5.5 restent historiques. Cette V20 n'ajoute ni consultation externe de ce moteur ni collecte de photos. Les méthodes de design n'autorisent pas à inventer des faits sur les ressources.

## Contrat de contenu et d'intégration

`resource-card.js` réutilise la description existante avec une longueur bornée et un libellé de provenance. `resource-detail.js` rend la fiche et conserve les actions de lecture, enregistrement, partage et onglets de l'application. `guide-ui.js` conserve `data-guide`, `data-guide-section`, `data-video`, `#dialog-title`, `#guide-method` et `#guide-sources`, et ajoute des cibles de plan pour les prérequis et vidéos associées.

Les contrôles de recherche et filtres gardent leur identité DOM. Les paramètres de véhicule sont des mentions ou des choix explicites, jamais une recommandation automatique de pièce, huile ou carburant. Les textes français des guides et de leurs preuves restent signalés ; seules les commandes sont localisées en FR/EN/ES. Les crédits photo et raisons des badges restent disponibles.

Les fragments CSS de travail sont intégrés à l'unique `public/product-ui.css`, après les règles héritées adaptées ; ils ne doivent pas être chargés comme feuilles concurrentes. Le bundle est produit par `scripts/build_ui.py`.

## Vérification et limites

Les [tests des cartes](card-checks.json), [tests du lecteur](detail-checks.json), [navigation](navigation-checks.json), [recherche et filtres](search-filter-checks.json), [contrat HTML](html-contract-checks.json) et [export](export-checks.json) totalisent **109 contrôles locaux réussis** dans le [récapitulatif](validation-results.json). Leurs dates, empreintes et limites restent propres à chaque suite ; les **14 contrôles HTML/bundle** ont été relancés sur le CSS final. Le [catalogue est inchangé](catalogue-integrity.json) ; le contrôle public final sur `17ea9ab` a confirmé **17 fichiers HTTP 200 conformes au dépôt** dans [public-assets-check.json](public-assets-check.json).

La [revue navigateur public](browser-checks.json) consigne **18 scénarios** à 320/390/768/1280 px : filtres et focus de plateforme, suggestions avec flèches/Entrée, réinitialisation conservant question et format, fiche et retour du focus, guide et navigation vers les notices. Une [contrelecture indépendante de treize captures](visual-review.md) n'a pas identifié de correctif nécessaire dans les états examinés ; cette inspection d'images ne prouve pas les fonctions.

Le dernier correctif `17ea9ab` ajuste seulement le fond des sujets associés et masque le signe « + » du bouton voiture à 320 px pour conserver son libellé complet. Ces deux états finaux ont été contrôlés : fond blanc et « Ma voiture » sans ellipse. Les interactions restent documentées sur `5a48d1f` ; les parcours complets ne sont pas déclarés rejoués sur le commit final. Aucun appareil physique, texte agrandi/zoom système, réglage OS de mouvement réduit, lecteur d'écran ou audit WCAG exhaustif n'a été testé. Les sources constructeur externes n'ont pas été revérifiées pendant cette passe UI. La [validation V19d](../graphic-redesign-v19/VALIDATION.md) reste une preuve historique séparée.
