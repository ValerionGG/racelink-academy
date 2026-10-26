# Collecteur social Bright Data

Le collecteur complète le référencement de RaceLink Academy avec des métadonnées de publications publiques : lien, auteur, légende, date et hashtags. Il ne télécharge pas les vidéos. Le mode TikTok « Posts by Profile Fast API » a été exécuté avec succès dans la Console le 26 octobre 2026. Les filtres de dates ont été vérifiés sur les exports reçus.

## Exécution et reprise

L’agent peut utiliser la Console déjà connectée, télécharger un export JSON et poursuivre automatiquement la qualification locale. Le client REST fourni est une autre voie, testée hors réseau : il exige une variable `BRIGHTDATA_API_KEY` explicitement configurée. Cette livraison ne contient aucune clé. Aucun appel authentifié de ce client n’est présenté comme exécuté.

Le client `scripts/brightdata_collect.py` expose `init`, `trigger`, `collect`, `adopt-ui` et `reconcile-snapshot`. `trigger` et `collect` produisent un aperçu sans `--execute`. `adopt-ui` reprend l’identifiant réel d’un lot lancé dans la Console, sans nouveau démarrage ni seconde réservation. Ne pas adopter un démarrage rejeté sans identifiant.

Le contrat TikTok utilisé est `gd_m7n5v2gq296pex2f5m` : profil public, `num_of_posts` borné, dates `YYYY-MM-DD` et `limit_per_input` dans le corps de la requête. Pour parcourir des archives, calculer la plus ancienne date réellement reçue ; l’ordre du tableau n’est pas nécessairement chronologique. Une borne de date est inclusive. Les identifiants déjà examinés, y compris les publications écartées, restent dans le registre de dédoublonnage.

## Crédits gratuits

Le registre privé local conserve l’observation datée des crédits gratuits, l’absence de carte, les réservations de tous les lots et leurs identifiants. Un lot est réservé avant son unique démarrage. Une réponse incertaine ne provoque aucune relance automatique. Le plafond de campagne est de 4 000 références réservées, avec une marge de 1 000 crédits ; les réservations ne sont pas effacées à la suite d’un échec. Le changement de mois exige une nouvelle observation, sans remise à zéro implicite.

Le solde monétaire affiché par `bdata budget` ne représente pas le quota gratuit des scrapers. Le flux `bdata login` n’est pas utilisé ici : sa version examinée crée aussi des zones inutiles à cette collecte. Aucun abonnement, dépôt ou paiement n’est nécessaire à la route gratuite utilisée.

## Qualité du catalogue

`scripts/brightdata_export.py` convertit l’export en `PUBLIC_EXPORT`, puis `scripts/public_export.py` prépare les candidats. Les photos, résultats d’erreur, identités contradictoires et publications sans légende exploitable sont écartés. La revue sépare titre éditorial, description et hashtags. Les véhicules, années et moteurs ne sont classés que lorsque la légende les mentionne. Les champs de langue décrivent la prose source ; ils ne certifient pas la langue parlée.

L’import exige une sélection scellée, une sauvegarde SQLite et un contrôle du delta. Les anciennes lignes restent intactes. Aucun transcript, droit de réutilisation ou caractère officiel d’une procédure n’est déduit d’une publication publique. Les exports bruts, registres, captures de compte et secrets restent hors du site et du paquet distribué.

La découverte Instagram par profil a renvoyé des erreurs de limitation de requêtes lors de cette session. Cette route est suspendue pour la journée ; ces erreurs ne sont pas comptées comme des vidéos ajoutées.

## Sources et validation

- [Documentation TikTok Bright Data](https://docs.brightdata.com/products/scrapers/tiktok/introduction)
- [Contrat des requêtes asynchrones](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
- [Crédits gratuits](https://docs.brightdata.com/general/account/billing-and-pricing/free-tier)
- [CLI officiel](https://github.com/brightdata/cli)

Les 54 tests fournis couvrent budgets, reprises, identités, secrets, formats et absence de relance du démarrage. Un audit indépendant ajoute neuf cas réussis ; la durée Instagram reste non vérifiée faute d’unité établie.
