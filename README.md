# RaceLink Academy — Catalogue V23

[Voir la bibliothèque](https://valeriongg.github.io/racelink-academy/?release=collection-v23) · [Bilan de collecte](research/scale-v23/results.json) · [Comparatif outils et coûts](research/scale-v23/benchmark.md)

**37,331 références vidéo et 11 guides.** Cette mise à jour ajoute 430 références réelles après dédoublonnage et revue des titres/métadonnées. Les modes clair et sombre V22 sont conservés. Les sources PeerTube se retrouvent avec le filtre « Autres sources ».

Les publications ne sont pas toutes visionnées : leur qualité technique, leur audio et la compatibilité véhicule ne sont pas certifiés. Une langue déclarée par une plateforme ou estimée depuis un titre est identifiée comme telle. Aucune nouvelle transcription ni licence libre n'a été inventée.

Le collecteur sait préparer plus de 100 000 lignes avec reprise, mais **100 000 vidéos nouvelles n'ont pas été acquises**. Le bilan sépare données découvertes, candidats et ajouts. Le pilote Apify de 1 000 publications maximum est préparé, non exécuté. Autorisation actuelle : uniquement les crédits gratuits disponibles, avec zéro dépense réelle ; connexion et crédit gratuit restant doivent être vérifiés avant lancement.

## Outils livrés

- [Préparation de gros lots](collector/SCALE_INGEST.md) : stockage SQLite temporaire, conflits entre variantes, reprise, revue séparée.
- [Collecteur Dailymotion](collector/OPEN-COLLECTOR.md) : métadonnées publiques, limites, cache, pause après refus ou limitation.
- [Pilote TikTok/Instagram](collector/collection/apify-free-credits-pilot/plan.json) : 14 lots préparés, limités aux crédits gratuits effectivement disponibles, sans médias ni transcription.
- [Accès requis et alternatives](research/scale-v23/access-required.json).

GitHub Pages est un aperçu indépendant du domaine Focus. `site/` contient l'export statique ; `collector/` contient les outils. [Validation V22 du design](research/themes-v22/VALIDATION.md).
