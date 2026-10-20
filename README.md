# RaceLink Academy — bibliothèque ouverte

Une bibliothèque d’aide et de ressources publiques autour du sport automobile, de la simulation et de la mécanique automobile, en complément de [Focus](https://focus.racelink-app.co/).

Ce snapshot référence 33,267 vidéos et propose 7 transcriptions avec preuve de réutilisation. Les fiches précisent la source, la qualification éditoriale et les limites des métadonnées. Une référence publique ne vaut pas licence libre ni validation de compatibilité mécanique.

Le site fonctionne sans compte. Favoris, notes et progression restent dans le navigateur. Les vidéos sont ouvertes chez leurs auteurs ou chargées à la demande depuis leur plateforme.

## Publication

`site/` est l’artefact statique public. GitHub Actions le publie avec GitHub Pages à chaque mise à jour de `main`. Les données sont chargées sous forme gzip par le Worker lorsque le navigateur le permet ; un JSON de repli reste disponible.

Aucun backend, base privée, média vidéo téléchargé ni identifiant de service n’est nécessaire au fonctionnement de cette distribution.
