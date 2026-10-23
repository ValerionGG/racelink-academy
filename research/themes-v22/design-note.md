# Thèmes clair et sombre — V22

Le choix d’apparence reste distinct de la langue d’interface, de la langue des vidéos et des filtres. Deux boutons natifs, « Clair » et « Sombre », indiquent leur sélection avec `aria-pressed` ; leurs icônes soleil/lune restent accompagnées d’un libellé accessible en français, anglais ou espagnol.

Le gestionnaire `public/theme.js` est chargé synchronement avant les styles. Il applique `html[data-theme]` et `color-scheme` dès son exécution pour réduire le changement de palette au chargement. La couleur du navigateur suit le mode : `#f5f6f8` en clair, `#101112` en sombre. Le choix explicite est conservé sous `rl-academy-theme`. Sans choix, la préférence système est suivie pendant la visite ; l’indisponibilité du stockage ne bloque pas le changement d’apparence.

La synchronisation et la livraison conservent les catalogues existants. L’inventaire photographique de V21 est repris à l’identique dans `assets-baseline.json` et ses empreintes sont vérifiées dans les trois copies par le script d’archive V22. Aucune nouvelle vidéo, transcription ou photographie n’est introduite par le gestionnaire de thème.

Les tests isolés du gestionnaire couvrent ses comportements et ses libellés. Ils ne valident pas le contraste de toutes les surfaces ni le rendu visuel. Ces conclusions doivent provenir des contrôles navigateur de l’intégration finale, enregistrés séparément dans `browser-checks.json` ; cette note ne les présume pas.
