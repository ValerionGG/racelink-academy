# RaceLink Academy — bibliothèque ouverte

[Ouvrir la bibliothèque](https://valeriongg.github.io/racelink-academy/) · [Vidéos en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&format=video)

Bibliothèque de tutoriels autour du sport automobile, de la simulation et de l’entretien automobile, en complément de [Focus](https://focus.racelink-app.co/).

Le snapshot du 21 octobre 2026 référence **36 633 vidéos et 11 guides**, dont **4 971 vidéos classées en français**, avec estimations signalées. Cette mise à jour ajoute **3 000 références YouTube** inédites, qualifiées sur métadonnées publiques de 26 chaînes. Les vidéos n'ont pas été visionnées intégralement. Sept transcriptions disposent d'une preuve CC BY.

Répartition : 36 502 YouTube, 46 Facebook, 42 Dailymotion, 34 Instagram, 4 TikTok, 3 Vimeo, 2 Twitch. Le pipeline TikTok/Instagram à grande échelle est préparé dans le paquet d'intégration ; ses lots non exécutés ne sont pas comptés ici.

La recherche conserve les précisions de véhicule, moteur, intervention et références techniques. Le choix de langue est visible et indépendant de la langue de l'interface. Favoris, notes et progression restent dans le navigateur. Les vidéos s'ouvrent chez leurs auteurs ou dans un lecteur tiers chargé à la demande.

## Publication

`site/` est l'artefact statique public publié par GitHub Actions à chaque mise à jour de `main`. Le catalogue compressé est décompressé dans un Worker, avec JSON de repli. La consultation ne nécessite aucun compte ou identifiant de service. Le domaine Focus original reste distinct.

La collecte s'appuie sur [Agent Reach](https://github.com/Panniantong/Agent-Reach) et yt-dlp. Le paquet local contient aussi un collecteur sans abonnement : recherches et chaînes YouTube, liens publics Instagram/TikTok, découverte Exa facultative, cache et déduplication. Les essais sociaux portent sur un petit échantillon et ne garantissent pas une collecte massive. Aucun run Apify facturable n'a été lancé.

## Identité et navigation

La version du 21 octobre associe ivoire, graphite et rouge, un monogramme RL original et [28 icônes SVG originales](https://valeriongg.github.io/racelink-academy/identity-icons.html). Le menu visuel organise huit sujets ; la navigation mobile donne accès à l'accueil, à la recherche, aux parcours et à la sélection. Les choix de langue et les filtres existants restent disponibles.

Une planche de direction artistique a été créée dans Flowith ; l'interface fonctionnelle et les SVG sont réalisés en code. Le travail utilise les skills design-inspiration et frontend-design, avec un benchmark documenté dans le paquet local. Les contrôles incluent les largeurs 320 et 390 px, la conservation des critères, les favoris, la traduction du menu et sa fermeture au clavier.
