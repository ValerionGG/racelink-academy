# RaceLink Academy — bibliothèque ouverte

[Ouvrir la bibliothèque](https://valeriongg.github.io/racelink-academy/) · [Vidéos en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&format=video)

Bibliothèque de tutoriels autour du sport automobile, de la simulation et de l’entretien automobile, en complément de [Focus](https://focus.racelink-app.co/).

Le snapshot du 21 octobre 2026 référence **36 786 vidéos et 11 guides**, dont **5 006 vidéos classées en français**, avec estimations signalées. Cette mise à jour ajoute **153 références sociales : 102 TikTok et 51 Instagram**, dont **35 estimées françaises** à partir du texte source. Les vidéos n'ont pas été visionnées. Sept transcriptions existantes disposent d'une preuve CC BY.

Répartition : 36 502 YouTube, 106 TikTok, 85 Instagram, 46 Facebook, 42 Dailymotion, 3 Vimeo, 2 Twitch. Le nouveau lot comprend 28 fiches enrichies par métadonnées directes et 125 fondées sur des titres indexés. 73 références comportent des mentions de véhicule et 129 un sujet précis. Ces mentions ne garantissent pas la compatibilité. Aucun nouveau badge éditorial ou transcription n'a été ajouté.

[TikTok en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&platform=tiktok&format=video) · [Instagram en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&platform=instagram&format=video)

La collecte a examiné 831 identités distinctes. Les milliers de nouveaux tutoriels demandés ne sont pas atteints : la recherche gratuite Exa a rencontré sa limite HTTP 429 et les extractions natives ont été arrêtées sur restrictions d'accès. Les comptes bruts, doublons et candidats écartés ne sont pas présentés comme des vidéos ajoutées.

La recherche conserve les précisions de véhicule, moteur, intervention et références techniques. Le choix de langue est visible et indépendant de la langue de l'interface. Favoris, notes et progression restent dans le navigateur. Les vidéos s'ouvrent chez leurs auteurs ou dans un lecteur tiers chargé à la demande.


## Titres et légendes sociales

Les 237 fiches TikTok, Instagram et Facebook disposent désormais de champs distincts : titre, description, hashtags et texte original consultable. 170 titres ont été nettoyés ou reformulés et 24 descriptions nettoyées. Les hashtags restent recherchables ; les mentions de véhicule, droits et transcriptions sont conservés. Les résumés éditoriaux sont distingués des légendes sources. Aucun visionnage n’est déduit de ce traitement des métadonnées.

Le skill réutilisable [social-content-structure](skills/social-content-structure/SKILL.md) comprend un séparateur Python autonome et des instructions de revue sémantique. Il distingue les titres natifs, les légendes directes et les extraits indexés. Le code conserve les originaux ; les reformulations sont documentées et les cas ambigus restent signalés.

## Publication

`site/` est l'artefact statique public publié par GitHub Actions à chaque mise à jour de `main`. Le catalogue compressé est décompressé dans un Worker, avec JSON de repli. La consultation ne nécessite aucun compte ou identifiant de service. Le domaine Focus original reste distinct.

La collecte s'appuie sur [Agent Reach](https://github.com/Panniantong/Agent-Reach), yt-dlp et la recherche publique Exa. Le paquet local conserve les caches, preuves et décisions de revue. Cette campagne a effectué 201 recherches Exa et 94 récupérations directes de métadonnées réussies, puis une revue des titres et légendes disponibles. Aucun média, cookie utilisateur ou nouvelle transcription n'a été téléchargé. Aucun run Apify facturable n'a été lancé.

## Identité et navigation

La version du 21 octobre associe ivoire, graphite et rouge, un monogramme RL original et [28 icônes SVG originales](https://valeriongg.github.io/racelink-academy/identity-icons.html). Le menu visuel organise huit sujets ; la navigation mobile donne accès à l'accueil, à la recherche, aux parcours et à la sélection. Les choix de langue et les filtres existants restent disponibles.

Une planche de direction artistique a été créée dans Flowith ; l'interface fonctionnelle et les SVG sont réalisés en code. Le travail utilise les skills design-inspiration et frontend-design, avec un benchmark documenté dans le paquet local. Les contrôles incluent les largeurs 320 et 390 px, la conservation des critères, les favoris, la traduction du menu et sa fermeture au clavier.
