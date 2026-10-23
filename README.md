# RaceLink Academy — bibliothèque ouverte

Version finale **v14c**, commit [f39bfee](https://github.com/ValerionGG/racelink-academy/commit/f39bfee), publiée et contrôlée. Les observations sont détaillées dans [VALIDATION.md](research/ui-redesign-2026-10-23/VALIDATION.md).

[Ouvrir la bibliothèque](https://valeriongg.github.io/racelink-academy/) · [Vidéos en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&format=video)

Bibliothèque de tutoriels autour du sport automobile, de la simulation et de l’entretien automobile, en complément de [Focus](https://focus.racelink-app.co/).

## Nouvelle interface produit — 23 octobre 2026

La **v14 est publiée** dans le commit [d4cdda4](https://github.com/ValerionGG/racelink-academy/commit/d4cdda4). Corps Onest, accents Orbitron, noir/rouge/blanc : la direction reprend le site officiel RaceLink, réellement inspecté. Accueil compact avec champ blanc, photos non teintées et légendes séparées, **11 couvertures de guides SVG originales**. Navigation permanente sur ordinateur, quatre destinations mobiles, recherche et critères véhicule à la demande.

[Ouvrir l’aperçu mobile](https://valeriongg.github.io/racelink-academy/preview-mobile.html) · [Étude de 10 références](research/ui-redesign-2026-10-23/benchmark-mobile.md) · [Comparaison de 6 skills GitHub](research/ui-redesign-2026-10-23/skills-report.md) · [Choix réalisés](research/ui-redesign-2026-10-23/DECISIONS.md) · [Validation et limites](research/ui-redesign-2026-10-23/VALIDATION.md).

Le catalogue n’a pas changé lors de cette refonte. La v14 a été observée via CUA à 1280 × 720 et dans l’aperçu mobile de 390 px : onze guides visibles, guide carburants ouvert/fermé avec focus restauré, recherche française « vidange Clio 3 », suggestions et filtre YouTube conservant la requête et la langue. Aucun débordement horizontal dans la zone mobile mesurée. La retouche v14b compacte le mobile et retire le vert résiduel des badges ; sa validation finale sera consignée séparément dans [le rapport de validation](research/ui-redesign-2026-10-23/VALIDATION.md).

Le snapshot du 21 octobre 2026 référence **36 901 vidéos et 11 guides**, dont **5 022 classées en français** (estimations signalées). La campagne du 21 octobre a ajouté **7 références TikTok**, dont **2 titres/libellés français**, sans ajout Instagram. Les sources sont six titres d’une archive de recherche GitHub et un lien publié sur le site du créateur. Aucun visionnage ni nouvelle transcription n’est revendiqué.

Répartition : 36 502 YouTube, **166 TikTok**, **140 Instagram**, 46 Facebook, 42 Dailymotion, 3 Vimeo, 2 Twitch. Les anciennes fiches sont conservées.

[TikTok en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&platform=tiktok&format=video) · [Instagram en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&platform=instagram&format=video)

**Les milliers de nouveaux tutoriels sociaux ne sont pas encore acquis.** Un [nouveau collecteur et importateur d’exports](collector/README.md) est fourni : liens publiés sur les sites de créateurs, JSON/JSONL/CSV et pages TikTok Display/Meta Graph. La préparation est locale, bornée et relisible ; les tests synthétiques ne font jamais partie du catalogue. [Résultats, alternatives GitHub et conditions d’accès](research/alternative-sociale-2026-10-21.md).

La recherche conserve les précisions de véhicule, moteur, intervention et références techniques. Le choix de langue est visible et indépendant de la langue de l'interface. Favoris, notes et progression restent dans le navigateur. Les vidéos s'ouvrent chez leurs auteurs ou dans un lecteur tiers chargé à la demande.


## Titres et légendes sociales

Les 352 fiches TikTok, Instagram et Facebook disposent désormais de champs distincts : titre, description, hashtags et texte original consultable. Les titres encombrés ont été nettoyés ou reformulés ; les légendes existantes restent distinctes. Les hashtags restent recherchables ; les mentions de véhicule, droits et transcriptions sont conservés. Les résumés éditoriaux sont distingués des légendes sources. Aucun visionnage n’est déduit de ce traitement des métadonnées.

Le skill réutilisable [social-content-structure](skills/social-content-structure/SKILL.md) comprend un séparateur Python autonome et des instructions de revue sémantique. Il distingue les titres natifs, les légendes directes et les extraits indexés. Le code conserve les originaux ; les reformulations sont documentées et les cas ambigus restent signalés.

## Publication

`site/` est l'artefact statique public publié par GitHub Actions à chaque mise à jour de `main`. Le catalogue compressé est décompressé dans un Worker, avec JSON de repli. La consultation ne nécessite aucun compte ou identifiant de service. Le domaine Focus original reste distinct.

La collecte s'appuie sur [Agent Reach](https://github.com/Panniantong/Agent-Reach), yt-dlp et la recherche publique Exa. Le paquet local conserve les caches, preuves et décisions de revue. Cette campagne a effectué 201 recherches Exa et 94 récupérations directes de métadonnées réussies, puis une revue des titres et légendes disponibles. Aucun média, cookie utilisateur ou nouvelle transcription n'a été téléchargé. Aucun run Apify facturable n'a été lancé.

## Historique : identité et navigation du 21 octobre

La version du 21 octobre associe ivoire, graphite et rouge, un monogramme RL original et [28 icônes SVG originales](https://valeriongg.github.io/racelink-academy/identity-icons.html). Le menu visuel organise huit sujets ; la navigation mobile donne accès à l'accueil, à la recherche, aux parcours et à la sélection. Les choix de langue et les filtres existants restent disponibles.

Une planche de direction artistique a été créée dans Flowith ; l'interface fonctionnelle et les SVG sont réalisés en code. Le travail utilise les skills design-inspiration et frontend-design, avec un benchmark documenté dans le paquet local. Les contrôles incluent les largeurs 320 et 390 px, la conservation des critères, les favoris, la traduction du menu et sa fermeture au clavier.
