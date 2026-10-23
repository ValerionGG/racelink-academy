# Contre-proposition obtenue dans Flowith

Modèle affiché et sélectionné : Claude Opus 5.5. Une génération texte exécutée le 23 octobre 2026. Aucun code généré déployé automatiquement. Le brief public seul a été transmis.

## Brief envoyé

Tu es directeur artistique UI/UX senior. Je te demande une contre-proposition concrète, pas du code complet ni une recherche prétendument effectuée. Projet public : RaceLink Academy https://valeriongg.github.io/racelink-academy/ . Bibliothèque de tutoriels automobiles/motorsport multilingues, recherche voiture/modèle/moteur/sujet/langue, vidéos sources et guides RaceLink avec références constructeur. Marque : noir #101012, blanc #f8f8f8, rouge #c82038, Onest pour lire, Orbitron seulement marque. Le propriétaire rejette expressément les petites vignettes et les icônes sur aplats : il veut de GRANDES PHOTOGRAPHIES RÉELLES et une app premium mobile. Nous avons inspecté les previews publics MotionSite Driven Hero (photo mécanique immense, typographie sobre blanc/gris) et Hyperion V12 (noir, rouge, titres forts), et racelink-app.co (photos automobile et titres blanc/rouge). Ne prétends pas les avoir vus si tu ne les ouvres pas.
Propose deux compositions distinctes pour accueil et catalogue, compare puis choisis une direction pour apprentissage. Décris précisément une largeur mobile390 et desktop1280 : grille, taille des photos16:9, titre19–22px sous photo, metadata courte, CTA44px. Catalogue mobile 1col ; recherche immédiatement accessible, pas de hero promo sur résultats. Accueil peut avoir photo mécanique dominante, phrase courte et recherche accessible sans dépasser un écran. Garde les 4 onglets Accueil/Rechercher/Parcours/Enregistrés. Pas de données de progrès inventées, de promesses de tuto officiel quand il s'agit de synthèse RaceLink, ni de photo stock présentée comme miniature vidéo. Le lecteur distingue synthèse et liens constructeur par véhicule. Réponds en français, 800 mots maximum : 2 variantes, choix motivé, tokens et plan CSS concret, 5 erreurs à éviter. Je produirai et testerai le code ensuite. Pas de déploiement, pas d'autres actions.

## Réponse affichée

RaceLink Academy : contre-proposition DA

Je n'ai pas ouvert les références citées. Je m'appuie uniquement sur votre description et sur le brief.

Variante A : « Atelier », la photo d'abord, en colonne

Accueil 390 (viewport 390×844)

Photo mécanique pleine largeur, bord à bord, hauteur min(56svh, 470px), cadrage serré sur moteur ou freins. Un dégradé noir occupe le tiers bas.
Sur la photo, une phrase courte en Onest 28/32 (600), par exemple : « Comprendre sa voiture, dans sa langue. »
Le champ de recherche (52px) chevauche le bas de la photo de 26px et reste visible sans défilement.
En dessous, des puces de raccourcis (marque, moteur, langue) de 44px de haut.
La barre d'onglets mesure 64px plus la zone de sécurité. L'ensemble tient dans un écran.

Catalogue 390

Recherche collante en haut (52px) suivie d'une rangée de filtres défilable horizontalement (44px). Aucun hero.
Une colonne, marges de 16px, soit une largeur utile de 358px.
Chaque carte comporte :
une photo 16:9 de 358×201 ;
un badge de type en surimpression (« Vidéo source » ou « Synthèse RaceLink ») ;
le titre en 20/26, 600, limité à 2 lignes ;
une ligne de metadata en 13px gris (modèle · moteur · langue · durée) ;
un CTA de 44px de haut, aligné à gauche.
Espacement entre cartes : 32px.

Desktop 1280

Conteneur de 1184px (marges 48px), 2 colonnes séparées de 32px.
Photos 576×324, titres en 22px.
Accueil : photo de 1184×560 avec la recherche de 640px centrée sur le bas.
Variante B : « Paddock », éditorial et dense

Accueil : un split. Sur mobile, le titre Onest 32px vient d'abord, la recherche ensuite, puis une photo 16:9 de 358×201. Sur desktop, texte à gauche (5/12 colonnes) et photo à droite (7/12, 680×383).

Catalogue : mobile identique à A. Sur desktop, 3 colonnes de 379×213 séparées de 24px, filtres en barre latérale de 264px, titres en 19px.

Comparaison et choix
Critère	A Atelier	B Paddock
Taille photo desktop	576px	379px
Densité	moyenne	élevée
Effet « app premium »	fort	moyen
Risque d'effet vignette	faible	réel en 3 colonnes

Je retiens A. Le propriétaire refuse les petites vignettes, et le passage à 3 colonnes de B y ramène au-dessus de 1280px. A maximise la photo, garde la même grammaire sur mobile et desktop, et sa colonne unique favorise l'apprentissage séquentiel.

L'onglet Parcours reprend la même carte, avec une numérotation d'étape (« Étape 2 ») à la place du badge. Aucun pourcentage de progression n'est affiché tant qu'aucune donnée réelle n'existe.

Lecteur

Le bloc vidéo source ou la synthèse occupe le haut.
Un en-tête typé apparaît toujours : « Synthèse RaceLink, rédigée à partir de… ». Le mot « officiel » n'est jamais employé.
Une section séparée « Références constructeur » est filtrée par véhicule (marque, modèle, années). Chaque lien affiche son domaine et une icône de lien externe.
La miniature d'une vidéo est uniquement sa vraie miniature. Une synthèse porte une photo légendée « Illustration ».
Tokens
css
:root{
  --c-bg:#101012; --c-surface:#1a1a1d; --c-line:#2a2a2e;
  --c-text:#f8f8f8; --c-muted:#a3a3a8; --c-accent:#c82038;
  --c-accent-hover:#de2a44;
  --f-read:"Onest",system-ui,sans-serif;
  --f-brand:"Orbitron",sans-serif; /* logo uniquement */
  --fs-meta:13px; --fs-body:16px;
  --fs-card:clamp(19px,1.2vw + 14px,22px);
  --fs-hero:clamp(28px,3vw + 16px,48px);
  --sp-1:4px; --sp-2:8px; --sp-3:16px; --sp-4:24px; --sp-5:32px; --sp-6:48px;
  --r-card:12px; --r-ctl:10px;
  --h-cta:44px; --h-search:52px; --h-tab:64px;
  --gutter:16px; --container:1184px;
}
Plan CSS
Layout : .wrap{max-width:var(--container);padding-inline:var(--gutter)}, avec --gutter:48px à partir de 1024px.
Grille : .grid{display:grid;gap:var(--sp-5)}, puis grid-template-columns:repeat(2,1fr) à partir de 900px.
Média : .card__media{aspect-ratio:16/9;overflow:hidden;border-radius:var(--r-card)} et img{width:100%;height:100%;object-fit:cover} avec width/height déclarés pour éviter le décalage de mise en page.
Hero : .hero{height:min(56svh,470px)} sur mobile. .search{margin-top:calc(var(--h-search)/-2);position:relative}.
Catalogue : .search-bar{position:sticky;top:0;z-index:10;background:var(--c-bg)}.
Tab bar : position:fixed;bottom:0;height:calc(var(--h-tab) + env(safe-area-inset-bottom)). Le contenu prévoit un padding-bottom équivalent.
Badges : .badge--source en fond blanc, .badge--synth en contour rouge. Le texte est toujours présent, la couleur n'est jamais le seul signal.
Focus : :focus-visible{outline:2px solid var(--c-accent);outline-offset:2px}.
Mouvement : zoom de l'image de 1.03 au survol, désactivé sous prefers-reduced-motion.
5 erreurs à éviter
Mettre du texte sur une photo sans voile : il faut un dégradé noir d'au moins 60 % et un contraste vérifié AA de 4.5:1.
Charger des photos lourdes : utiliser AVIF/WebP, srcset 400/800/1200, loading="lazy" sauf pour le hero, et fetchpriority="high" sur le hero.
Étendre Orbitron aux titres ou aux boutons : la lisibilité et la cohérence de la marque en souffrent.
Utiliser le rouge partout : il doit rester réservé au CTA principal, à l'onglet actif et au focus. Ailleurs, il dilue la hiérarchie.
Laisser la barre d'onglets ou un bandeau masquer la recherche sur 390×664 (hauteur utile réelle). Testez aussi sur 375×667.

## Décisions RaceLink

Composition A retenue et adaptée : couvertures 16:9, titres sous image, deux colonnes selon largeur disponible, recherche à la jonction de la photo. Fonds clairs maintenus pour la lecture ; recherche du catalogue laissée dans le flux pour éviter les recouvrements observés précédemment. Les tailles proposées par le modèle ne prennent pas toutes en compte la sidebar existante : elles ont été recalculées. La réponse est une proposition, pas une preuve de tests ni de visites des références.
