# RaceLink Academy — bibliothèque ouverte

[Ouvrir la bibliothèque](https://valeriongg.github.io/racelink-academy/) · [Vidéos en français](https://valeriongg.github.io/racelink-academy/?browse=1&language=fr&format=video)

Une bibliothèque autour du sport automobile, de la simulation et de l’entretien automobile, en complément de [Focus](https://focus.racelink-app.co/).

Ce snapshot référence **33 633 vidéos et 11 guides**, dont **4 561 vidéos référencées en français**, avec des preuves de langue de niveaux différents et des estimations signalées. Sept transcriptions ont une preuve de réutilisation CC BY. Une référence publique ne vaut pas licence libre ni validation de compatibilité mécanique.

Le choix de langue des contenus est visible à côté de la recherche, indépendamment de la langue de l’interface. Les suggestions conservent les précisions de véhicule et les références techniques. Six sélections françaises ouvrent sur le pilotage, la simulation, la photo, l’électronique, la formation hybride et les métiers.

Couverture : 33 502 YouTube, 46 Facebook, 42 Dailymotion, 34 Instagram, 4 TikTok, 3 Vimeo, 2 Twitch. Cette itération ajoute 300 vidéos, dédoublonnées et reliées à leurs preuves publiques. Les titres et légendes des ajouts sociaux sont français ; leur audio n’a pas été écouté. Aucun commentaire ni transcription n’est inventé.

Le site fonctionne sans compte. Favoris, notes et progression restent dans le navigateur. Les vidéos s’ouvrent chez leurs auteurs ou dans un lecteur tiers chargé à la demande.

## Publication

`site/` est l’artefact statique public publié par GitHub Actions à chaque mise à jour de `main`. Le catalogue gzip est décompressé dans un Worker, avec JSON de repli. Aucun backend ou identifiant de service n’est nécessaire à cette distribution. Le domaine Focus original reste distinct.

Le design s’appuie notamment sur [Impeccable](https://github.com/pbakaus/impeccable), comparé à d’autres skills GitHub via [Agent Reach](https://github.com/Panniantong/agent-reach). La collecte conserve les sources et ne prétend pas à un visionnage complet.
