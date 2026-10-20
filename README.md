# RaceLink Academy — bibliothèque ouverte

Une bibliothèque d’aide et de ressources publiques autour du sport automobile, de la simulation et de la mécanique automobile, en complément de [Focus](https://focus.racelink-app.co/).

Ce snapshot référence 33 333 vidéos et 11 guides et propose 7 transcriptions avec preuve de réutilisation. Les fiches précisent la source, la qualification éditoriale et les limites des métadonnées. Une référence publique ne vaut pas licence libre ni validation de compatibilité mécanique.

Le site fonctionne sans compte. Favoris, notes et progression restent dans le navigateur. Les vidéos sont ouvertes chez leurs auteurs ou chargées à la demande depuis leur plateforme.

## Publication

`site/` est l’artefact statique public. GitHub Actions le publie avec GitHub Pages à chaque mise à jour de `main`. Les données sont chargées sous forme gzip par le Worker lorsque le navigateur le permet ; un JSON de repli reste disponible.

Aucun backend, base privée, média vidéo téléchargé ni identifiant de service n’est nécessaire au fonctionnement de cette distribution.

## Recherche et découverte

Trois entrées illustrées mènent à l'entretien automobile, au pilotage et à la simulation. Les résultats disposent d'onglets Tout / Vidéos / Guides, de filtres de plateforme et de critères avancés. Les suggestions conservent les précisions de véhicule et les références techniques. Les guides généraux ne confirment aucune compatibilité propre à une voiture.

Le catalogue comprend 42 références Facebook et 29 Instagram, ainsi que 4 TikTok. Le dernier lot ajoute 66 identités nouvelles et enrichit 2 fiches existantes. Trois questions réellement consultées dans des commentaires sont reformulées en français, indexées et reliées à leur contexte ; elles ne sont pas présentées comme des réponses validées.

Le design a été simplifié à l'aide d'[Impeccable](https://github.com/pbakaus/impeccable), retenu après comparaison de skills GitHub via [Agent Reach](https://github.com/Panniantong/agent-reach). Le classement des sources ne prétend pas à un visionnage complet ; seules sept transcriptions réutilisables sont disponibles.
