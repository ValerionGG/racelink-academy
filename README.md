# RaceLink Academy — bibliothèque ouverte

[Ouvrir la bibliothèque](https://valeriongg.github.io/racelink-academy/) · [Vidéos en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&format=video)

Bibliothèque de tutoriels autour du sport automobile, de la simulation et de l’entretien automobile, en complément de [Focus](https://focus.racelink-app.co/).

Le snapshot du 21 octobre 2026 référence **36 633 vidéos et 11 guides**, dont **4 971 vidéos classées en français**, avec estimations signalées. Cette mise à jour ajoute **3 000 références YouTube** inédites, qualifiées sur métadonnées publiques de 26 chaînes. Les vidéos n'ont pas été visionnées intégralement. Sept transcriptions disposent d'une preuve CC BY.

Répartition : 36 502 YouTube, 46 Facebook, 42 Dailymotion, 34 Instagram, 4 TikTok, 3 Vimeo, 2 Twitch. Le pipeline TikTok/Instagram à grande échelle est préparé dans le paquet d'intégration ; ses lots non exécutés ne sont pas comptés ici.

La recherche conserve les précisions de véhicule, moteur, intervention et références techniques. Le choix de langue est visible et indépendant de la langue de l'interface. Favoris, notes et progression restent dans le navigateur. Les vidéos s'ouvrent chez leurs auteurs ou dans un lecteur tiers chargé à la demande.

## Publication

`site/` est l'artefact statique public publié par GitHub Actions à chaque mise à jour de `main`. Le catalogue compressé est décompressé dans un Worker, avec JSON de repli. La consultation ne nécessite aucun compte ou identifiant de service. Le domaine Focus original reste distinct.

La collecte s'appuie sur [Agent Reach](https://github.com/Panniantong/Agent-Reach) et yt-dlp. Pour l'extension sociale, le skill officiel [Apify](https://github.com/apify/agent-skills) a été inspecté et ses schémas testés via le MCP de découverte ; aucun run facturable n'a été lancé. Le design s'appuie notamment sur [Impeccable](https://github.com/pbakaus/impeccable).
