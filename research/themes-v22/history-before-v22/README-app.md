# RaceLink Academy — bibliothèque d’aide pour Focus

Version courante **cinema-v21**, publiée et vérifiée. [Voir la refonte](https://valeriongg.github.io/racelink-academy/?release=cinema-v21&build=065ab48) · [Validation](research/cinema-v21/VALIDATION.md) · [Brief et sources GitHub](research/cinema-v21/prompt-research.md). Accueil photographique, collections de guides, recherche, pré-fiches, lecteurs, filtres et navigation redessinés. Catalogue et procédures sourcées conservés.

[Ouvrir la bibliothèque](https://valeriongg.github.io/racelink-academy/) · [Vidéos en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&format=video) · [Dépôt Git](https://github.com/ValerionGG/racelink-academy)

Version locale et distribution statique, actualisées le 23 octobre 2026. Le paquet conserve une route `/aide/` à intégrer dans Focus ; le domaine Focus original n’a pas été modifié. [VALIDATION.md](VALIDATION.md) et `../deploiement.json` décrivent les contrôles et le déploiement de cette version.

## Historique : refonte produit V14 — 23 octobre 2026

La **v14 est publiée** dans le commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4). Elle reprend l’identité du site officiel RaceLink : corps Onest, accents Orbitron, noir/rouge/blanc, accueil compact avec recherche blanche. Les trois portes utilisent des photos non teintées et des légendes séparées ; les **11 guides** disposent de couvertures SVG originales noir/argent/rouge. Navigation latérale sur ordinateur et quatre destinations sur mobile ; recherche, langue et critères véhicule restent prioritaires.

[Décisions et limites de vérification](research/ui-redesign-2026-10-23/DECISIONS.md) · [10 références produit](research/ui-redesign-2026-10-23/benchmark-mobile.md) · [6 skills GitHub comparés](research/ui-redesign-2026-10-23/skills-report.md) · [Aperçu mobile public](https://valeriongg.github.io/racelink-academy/preview-mobile.html).

Le catalogue est inchangé. La v14 a été observée via CUA sur l’accueil à 1280 × 720 et dans l’aperçu mobile de 390 px : onze guides visibles, ouverture/fermeture du guide carburants avec retour du focus, recherche française « vidange Clio 3 », suggestions et filtre YouTube conservant la requête et la langue. La zone mobile mesurée ne débordait pas horizontalement. La retouche v14c concerne la compacité mobile et la suppression du vert résiduel des badges ; sa validation finale sera consignée séparément dans [VALIDATION.md](research/ui-redesign-2026-10-23/VALIDATION.md), qui détaille le périmètre réel des contrôles.

Pour modifier les styles, éditer `public/product-ui.css`, puis lancer `python scripts/build_ui.py` avant l’export. `public/app-ui.css` est généré en une seule feuille à deux couches : composants hérités, puis styles produit. `DESIGN.md` est la référence visuelle canonique.

## Historique : identité et collecteur local — 21 octobre 2026

Nouvelle identité avec monogramme RL, 28 SVG originaux, menu visuel à huit sujets et navigation mobile. Une planche Flowith a accompagné la direction artistique ; les composants fonctionnels sont écrits en code. [Étude](research/identity-design-references-2026-10-21.md) · [Flowith](research/flowith-design-brief.md).

Le [collecteur sans abonnement Apify](research/alternative-gratuite-collecte.md) est livré dans `scripts/local_collect.py`. La campagne réelle ajoute **153 références sociales**, dont **35 estimées françaises** sur leur texte source, après examen de 831 liens. [Bilan et limites](research/collecte-sociale-2026-10-21.md).

## Ouvrir la version locale

Avec Python 3.11 ou plus récent, lancer `Demarrer.ps1` ou `python server.py --port 8765`, puis ouvrir http://127.0.0.1:8765/aide/. Aucun paquet Python supplémentaire ni compte n’est nécessaire à la consultation. Garder le serveur ouvert pendant l’utilisation.

La base actuelle contient **36 901 références vidéo et 11 guides**. Répartition : 36 502 YouTube, 166 TikTok, 140 Instagram, 46 Facebook, 42 Dailymotion, 3 Vimeo et 2 Twitch. **5 022 vidéos sont classées en français**, le plus souvent par estimation signalée. Les 62 sélections éditoriales et 7 transcriptions CC BY sont conservées.

Dernière itération : 7 nouvelles références TikTok, dont 2 textes estimés français, et un collecteur de sites de créateurs / importateur d’exports publics. Aucun ajout Instagram dans ce lot. [Résultat et limites de la nouvelle solution](research/alternative-sociale-2026-10-21.md). Le catalogue n’a pas été visionné intégralement ; les droits des autres médias restent inconnus.

## Ce qui fonctionne

- Accueil avec recherche immédiate et trois entrées illustrées : entretien automobile, pilotage et sim racing. Les images de navigation restent distinctes des miniatures réelles des vidéos. Les résultats s’ouvrent dans une vue séparée, avec retour à l’accueil.
- Recherche unifiée sur les vidéos et onze guides internes, avec onglets **Tout / Vidéos / Guides**. L’API `/aide/api/resources` (alias `/api/resources`) recherche les titres, auteurs, descriptions, mots-clés, guides et sept transcriptions. Glossaire français/anglais/espagnol pour certains termes techniques, avec indication des résultats élargis.
- Filtres de discipline, contexte, langue, plateforme, niveau, durée, transcription et licence ouverte ; tri, pagination et URL partageable. Le choix de langue est visible près de la recherche sur ordinateur et mobile, séparé de la langue de l’interface. Le filtre **Type de vidéo** distingue tutoriel, démonstration, cours et direct quand les informations disponibles permettent ce classement ; les formats non déterminés restent inconnus.
- Fiches avec auteur, source, durée, langue, état éditorial et lecteur tiers chargé à la demande. Les démonstrations de tours avec télémétrie sont identifiées.
- Sept textes horodatés, recherche dans le texte, accès au passage du lecteur, synopsis français et points d’apprentissage. Cinq pistes automatiques et deux pistes publiées sont distinguées.
- Huit parcours de quatre étapes, suivi personnel local, favoris, notes et quarante-trois entrées d’aide/FAQ recherchables.
- Interface française, anglaise et espagnole ; titres originaux dans les 12 langues repérées. Les articles d’aide et synopsis restent en français, et les transcriptions dans leur langue source.
- Recherche prédictive sur le vocabulaire des sujets et les titres existants, avec propositions au clavier et conservation des critères de recherche.
- Mise en page ordinateur/mobile, recherche en dialogue plein écran sur téléphone, filtres dans une feuille dédiée, compte des filtres actifs et retour aux résultats.
- Commandes clavier, dialogues HTML natifs, focus visible et réduction des animations.

Les favoris, notes et progrès sont stockés dans ce navigateur. Ils ne sont pas synchronisés avec un compte Focus. Le glossaire ne constitue pas une traduction universelle. L’accès aux vidéos dépend de la plateforme, du créateur et d’éventuelles restrictions régionales.

## Extension « Mon véhicule & entretien »

La bibliothèque permet maintenant de combiner marque, modèle, génération, année, motorisation, énergie et carrosserie avec une intervention : vidange, essuie-glaces, changement de roue, filtres, freins, fusibles, batterie, éclairage, diagnostic, commandes et équipements.

Le véhicule peut être mémorisé localement, rappelé ou oublié depuis l’interface. Les références mentionnées dans les titres sont également filtrables : viscosité d’huile, homologation ou carburant. Une norme typographiée différemment peut être rapprochée, mais deux références différentes ne sont pas déclarées équivalentes.

Les critères d’un véhicule doivent correspondre à une même application citée. Les années et moteurs absents restent inconnus. Il s’agit d’une indexation de titres, **pas d’une garantie de compatibilité** de pièces, huiles ou carburants. Dix guides sourcés, une fiche d’identification, treize FAQ supplémentaires et six portails officiels complètent la recherche.

Voir [le fonctionnement de la recherche automobile](research/recherche-par-vehicule.md), [les sources des guides](research/guide-entretien-sources.md) et [la couverture mesurée](research/automotive-coverage.json).

## Découverte par objectif et sélections

L’accueil donne trois points de départ directs : **Entretenir ma voiture**, **Progresser au volant** et **Sim racing**. Le panneau **Tous les sujets** conserve les six objectifs plus détaillés : entretenir, résoudre un problème, progresser au volant, comprendre la voiture, pratiquer en simulation et construire son projet. Les sujets conduisent à de vraies recherches du catalogue ; leurs compteurs sont calculés sur les données installées. Une ressource peut appartenir à plusieurs sujets.

La saisie propose des sujets et des titres réellement présents, avec navigation au clavier. La prédiction complète les termes du vocabulaire thématique ; une petite faute éventuelle est signalée comme correction proposée. Le reste de la question et les critères précis sont conservés : les chiffres, codes moteur et références d’huile ne sont pas complétés par déduction. Des pistes contextuelles accompagnent les résultats. Le clic sur une suggestion conserve les critères personnels et les précisions de véhicule ou de référence qu’elle a interprétées. Les recherches vides proposent des actions explicites pour retirer des critères ; aucune compatibilité n’est déduite de cet élargissement.

Les mises en avant sont séparées des candidats du catalogue. Le fichier `public/discovery-catalog.json` contrôle leurs identifiants, leur activation, leurs raisons, leurs preuves, leurs dates de revue et d’expiration. Le moteur masque les sélections expirées, désactivées ou sans fiche éditoriale correspondante. Chaque personne peut aussi masquer les sélections dans son navigateur. Il n’y a pas de score de popularité inventé ni de lecture automatique.

Le badge **« Proposé par RaceLink »** concerne actuellement **12 vidéos** et **trois guides internes** : identification du véhicule, références d’huile et carburants. Chaque mise en avant a une raison éditoriale, une preuve de revue et une expiration. Le badge ne remplace pas l’auteur d’origine et ne certifie ni la qualité technique intégrale d’une vidéo ni une compatibilité mécanique. Les autres vidéos associées aux guides ne reçoivent pas automatiquement ce badge.

L’interface utilise des règles explicables et des relations de recherche ; elle ne prétend pas mesurer la compétence de la personne. Les huit disciplines et tous les filtres précis restent disponibles. Le panneau automobile peut être déplié à la demande.

Sur mobile, le même champ de recherche s’ouvre dans un dialogue plein écran et les filtres restent regroupés dans une feuille séparée. Les critères restent visibles et le bouton de retour indique le nombre de résultats courants. Une recherche en cours ou indisponible ne doit pas réutiliser un ancien compteur. La gestion native du focus des dialogues est complétée par un retour vers le déclencheur ou la destination demandée.

Voir [le benchmark de sept plateformes](research/benchmark-decouverte.md), [le complément recherche et mobile](research/benchmark-recherche-mobile.md), [la comparaison de six skills de design GitHub et les règles retenues](research/design-skills-github.md), [les sujets et leur utilité](research/classement-utilite.md) et [les règles de maintenance](research/gestion-decouverte.md).

## Ajouts français et précision de la langue

L’itération du 20 octobre ajoutait **300 vidéos**, sur YouTube, Dailymotion, Instagram, Facebook et Vimeo. Le français représentait alors **4 561 références** : 272 avec langue déclarée par la plateforme, 2 avec une piste source, 4 287 estimées. Ces preuves ne constituent pas un visionnage intégral. Les anciennes langues déduites seulement d’une requête sont retirées, et la langue inconnue reste filtrable.

Le nouveau lot couvre entretien, diagnostic, électrique/hybride, sim racing, pilotage, photographie, métiers et projet professionnel. Six nouvelles mises en avant françaises disposent de vignettes réelles, de raisons explicites et d’une échéance de revue. La recherche reconnaît aussi les formes Clio3 / Clio 3 sans inventer un moteur absent.

Voir [le parcours de langue et ses essais](research/langues-et-referencement.md), [les preuves YouTube](research/french-expansion-preuves.md), [les preuves sociales](research/french-social-preuves.md) et [le bilan d’import](research/french-expansion-import-results.json).

## Références Instagram et Facebook — collecte précédente

Le lot précédent contient **68 fiches candidates : 66 nouvelles identités vidéo et 2 enrichissements de fiches existantes**, avec 40 références Facebook et 28 Instagram. Les légendes couvrent six langues et treize thèmes. Pour 17 fiches, la légende et l’auteur ont été lus sur la page publique via Agent Reach/Jina ; les 51 autres reposent sur les titres et légendes indexés par Exa. Ce niveau de preuve est conservé dans les fiches et ne constitue pas un visionnage ni une validation technique.

Trois questions réellement relevées dans les commentaires de deux publications sont indexées avec leur source : signification des newton-mètres du retour de force, réglage automatique du retour de force et compatibilité d’un scanner avec les moteurs Paccar. Elles décrivent des besoins, sans réponse technique supposée. L’échantillon est partiel et non représentatif.

Aucun nouveau lien TikTok exploitable n’a été obtenu dans cette collecte ; les quatre références précédentes restent au catalogue. Aucun média ni nouvelle transcription n’a été téléchargé. Voir [le rapport social, ses preuves et les mécanismes officiels/GitHub examinés](research/social-expansion-preuves.md).

## Acquisition élargie — 21 octobre 2026

**3 000 nouvelles références YouTube** sont importées sans doublon, dont 410 titres estimés français. Elles sont présélectionnées sur des métadonnées publiques provenant de 26 chaînes : entretien, vidange, diagnostic, systèmes électriques, freins, refroidissement et commandes. Aucun audio ni geste n'a été vérifié dans ce lot. Les 1 189 langues incertaines restent inconnues. [Collecte et preuves](research/bulk-youtube-2026-10-21-preuves.md), [import réel](research/bulk-youtube-2026-10-21-import-results.json).

La route retenue pour les gros volumes TikTok et Instagram combine le skill officiel Apify, ses collecteurs de métadonnées et un nouvel import qualifié. Le [kit de collecte](collection/social-acquisition/README.md) contient 52 entrées contrôlées, un pilote visant 200 résultats et une extension visant jusqu'à 5 000 résultats bruts. **Aucun de ces runs sociaux n'a été exécuté** : compte et budget restent à connecter. Leurs cibles ne sont pas incluses dans les compteurs du site.

Le lanceur prévisualise par défaut, borne chaque run et empêche un renvoi aveugle après issue incertaine. L'import accepte les exports JSON/JSONL Apify et yt-dlp, sépare les candidats de la quarantaine, préserve les preuves de langue et les identifiants canoniques. Voir [le guide d'import](research/bulk-ingestion-guide.md) et [le benchmark des outils et API](research/social-acquisition-options-2026-10-21.md).

## Publication GitHub Pages

Adresse publique : **[https://valeriongg.github.io/racelink-academy/](https://valeriongg.github.io/racelink-academy/)**. Dépôt : [ValerionGG/racelink-academy](https://github.com/ValerionGG/racelink-academy). Consulter [VALIDATION.md](VALIDATION.md) pour le dernier déploiement et les vérifications réellement exécutées ; les fonctions décrites ici ne constituent pas, à elles seules, une preuve de validation de la dernière version en ligne.

Cette publication est distincte du raccordement au domaine `focus.racelink-app.co`. Les instructions ci-dessous restent applicables pour intégrer ensuite la bibliothèque dans Focus.

## Intégrer dans Focus

Deux distributions sont fournies. À cette taille de catalogue, **la version avec API est conseillée** : le navigateur reçoit seulement la page de résultats demandée. La version statique permet une installation plus simple et fournit un catalogue gzip dont le transfert est réduit d’environ **91 %** par rapport au JSON brut. Elle charge néanmoins tout le catalogue au premier accès et le décompresse pour la recherche dans le navigateur.

### Option A — API Python et SQLite

1. Copier ce dossier sur l’hébergement.
2. Faire tourner `server.py` sous un service supervisé, sur `127.0.0.1:8765`.
3. Ajouter au serveur nginx existant les règles du fichier `integration/nginx-location.conf`. Elles rendent `/aide/` accessible via le domaine Focus.
4. Ajouter le lien de navigation décrit ci-dessous.

Le serveur livré est un service Python minimal en lecture seule. Pour une exploitation publique, la terminaison HTTPS et la supervision doivent être assurées par l’hébergement. Les routes, paramètres, imports, tests et limites sont détaillés dans [README-backend.md](README-backend.md).

### Option B — site statique

Le dossier voisin **`focus-academy-static/aide/`** contient une version autonome avec moteur de recherche dans un Web Worker.

1. Copier **uniquement le dossier `aide/`** dans la racine publique du site Focus.
2. Vérifier que `/aide/` sert son propre `index.html` et que les fichiers `.js` et `.json` sont accessibles. Une redirection globale vers l’application principale ne doit pas intercepter cette route.
3. Conserver le fichier `catalog/catalog.json.gz` fourni. Le moteur le décompresse dans le navigateur lorsqu’il est pris en charge, avec repli sur le JSON ordinaire. Activer également le cache et la compression HTTP des autres ressources sur l’hébergement.
4. Ajouter le lien de navigation.

Le `index.html` à la racine du paquet statique sert seulement à l’aperçu isolé. Ne pas le placer à la place du `index.html` actuel de Focus. Les fichiers `_headers` et `_redirects` sont des exemples pour les hébergeurs qui les prennent en charge ; nginx les ignore.

Pour prévisualiser ce paquet séparément :

```powershell
python -m http.server 8766 --bind 127.0.0.1 --directory ../focus-academy-static
```

Ouvrir http://127.0.0.1:8766/aide/. L’ouverture directe en `file://` n’est pas prise en charge.

### Lien « Aide » dans la navigation Focus

Les deux petits fichiers de `integration/` ont été préparés à partir du HTML/CSS/JavaScript publics de Focus. Copier ces fichiers dans les dossiers publics du site, puis ajouter :

```html
<link rel="stylesheet" href="/css/focus-help-link.css">
<!-- Après le script Focus existant : -->
<script src="/js/focus-help-link.js" defer></script>
```

Le script ajoute une cinquième entrée « Aide » à `#focus-nav`. Si ce composant est remplacé lors d’une future évolution, ajouter un lien natif vers `/aide/` dans le nouveau composant. Ce raccordement au site Focus existant reste à réaliser, indépendamment de la publication GitHub Pages réalisée.

## Données, preuves et maintenance

- `data/catalog.sqlite3` : base complète, métadonnées sources, preuves de qualification, transcriptions et index FTS5.
- `data/catalogue.csv` : export des références pour consultation et tri dans un tableur.
- `research/catalogue-statistiques.json` : compteurs exacts de la livraison.
- `research/etude-ux-ui.md` : audit de Focus, comparaison de plateformes d’apprentissage et sources des skills GitHub consultés.
- `research/sources-video.md`, `plan-indexation.md` et `transcriptions-cc.md` : acquisition, portée des droits, limites et évolution du catalogue.
- `collection/` : scripts reproductibles, sources de collecte, snapshot final et preuves CC. Lire son README avant de relancer une acquisition.
- `VALIDATION.md` : contrôles réellement exécutés et limites.
- `screenshots/` : captures du résultat local.

L’acquisition a utilisé Agent Reach, ses outils de lecture web et son backend YouTube/yt-dlp. Les méthodes de conception consultées incluent les Web Design Guidelines de Vercel, UI/UX Pro Max et Impeccable ; leurs liens et leur usage exact figurent dans l’étude.

Pour actualiser, qualifier les nouveaux liens, importer un lot JSON, puis réexporter le site statique si cette distribution est utilisée. L’import dédoublonne les identifiants de plateforme et les URL, et conserve les transcriptions autorisées déjà enregistrées. Ne jamais présenter une transcription comme disponible avant son import réel et la vérification de ses droits.

Les vignettes restent hébergées par leurs plateformes. Les images d’entrée illustrent la navigation et ne sont pas comptées comme ressources pédagogiques ; les onze couvertures de guides utilisent désormais des photographies avec leurs crédits. Les polices Onest et Orbitron sont chargées depuis Google Fonts. Une connexion Internet reste nécessaire aux vidéos et aux ressources distantes, même avec le catalogue local.
