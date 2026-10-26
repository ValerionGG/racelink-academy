# RaceLink Academy : collecte sociale automatisée

État au 26 octobre 2026. L'autorisation de dépense reste **0 USD hors crédits gratuits**. Les vidéos sont référencées, jamais générées. Le site publié reste la version V24 à 37 896 vidéos tant qu'un nouvel import revu n'a pas été validé.

## Accès réellement constatés

- Le navigateur accessible à cette tâche est le navigateur intégré. Chrome et Edge ne figurent pas parmi les navigateurs connectés.
- Apify attend une connexion utilisateur dans l'onglet 2, via GitHub. Une demande de connexion a été présentée à l'utilisateur ; ne pas demander un mot de passe, code ou token dans le chat. Ne pas inspecter ce formulaire pendant la saisie.
- TikTok affiche le profil public Ma Clé de 12, mais son flux et la recherche « tuto mécanique » ont renvoyé une erreur de serveur. Un seul nouvel essai du flux a été effectué.
- Instagram affiche 12 publications publiques de norautofr. La lecture d'un Reel et le chargement de publications supplémentaires demandent une connexion. Les textes alternatifs de cette grille ne sont pas des légendes.
- Le MCP vidIQ répond, avec 4 crédits. La première recherche sociale coûte 5 crédits : aucun appel social n'a été exécuté ni aucun crédit acheté.

## Ce qui a été exécuté

La file `creator-queue` a effectué 200 recherches Exa, à partir de profils présents dans les références existantes. Les 4 693 variantes correspondent à 280 identités distinctes, dont 4 413 répétitions d'identité. Ce résultat ne prouve ni l'appartenance au créateur demandé ni l'exhaustivité de son profil : Exa élargit parfois les résultats. Ne pas répéter cette campagne pour gonfler les chiffres.

Le snapshot immuable `creator-snapshot` conserve toutes les variantes. Sa préparation dans `creator-review` a produit 70 candidats automatiques et 210 mises en quarantaine. Parmi les 70 candidats, 38 identités ne sont pas déjà dans le catalogue. Leur revue a retenu 16 candidats en anglais pour un prochain import, laissé 16 cas en attente et exclu 6 cas. Les 8 restrictions pertinentes issues des revues précédentes sont conservées. Aucun nouveau candidat français n'a été retenu et aucun import n'a été effectué. Les titres d'index restent des indices de contenu, pas des légendes natives ou une preuve de visionnage. La revue est dans `work/scale-v25/research/editorial-review.json`.

## Exécution et reprise

Le dossier de travail de cette tâche est `WORKSPACE`.

Dans la distribution GitHub, le code applicatif se trouve dans `collector/` : les chemins `outputs/focus-academy/scripts/...` deviennent `scripts/...` depuis ce dossier. Le répertoire `work/` cité dans ce document est l'historique local de la tâche ; ses bases, captures brutes et reçus de comptes ne sont pas distribués. Les rapports publics sont dans `research/automation-v25/` à la racine du dépôt.

```powershell
python -B -X utf8 outputs/focus-academy/scripts/social_queue.py status --queue work/scale-v25/creator-queue
```

Cette file est terminée. Ne pas réinitialiser ses quotas ou ses preuves. Une nouvelle recherche doit apporter une source ou une requête réellement nouvelle. Une réponse 403/429, une demande d'authentification ou un résultat incertain met le travail concerné en pause ; une reprise demande un changement d'état constaté et documenté.

Le collecteur 1.0.2 termine désormais ses sous-processus lorsqu'il est interrompu. La file 1.0.1 dispose d'un arrêt coopératif, d'un état consultable pendant la collecte, d'un journal de migration du collecteur, de plafonds persistants et de snapshots scellés. Le correctif a été appliqué après les 200 recherches ; l'ancien hash reste dans le manifeste de leur snapshot.

## Apify après connexion

Le package autonome `outputs/focus-academy/collection/free-social-v25` contient le vérificateur de crédit et le lanceur de lots par profil. L'aperçu n'appelle pas le réseau. L'exécution exige une configuration explicite de `APIFY_TOKEN` dans l'environnement ; aucun secret n'est recherché dans des fichiers ou profils de navigateur. Utiliser la console Apify si la session navigateur est connectée, en appliquant les mêmes contrôles et les mêmes limites, sans installer une autre automatisation de navigateur.

Avant chaque lancement : vérifier le plan Free non payant, le crédit mensuel disponible, l'absence d'autre Actor actif, le schéma et les prix actuels. Un lot est plafonné à 0,50 USD de crédits gratuits, dans la limite du solde disponible et de la réserve. Un compte payant, un solde indéterminé, un changement de prix ou un lancement incertain bloque la suite. Aucun abonnement, recharge ou crédit acheté n'est autorisé.

Commencer par les profils pilotes, examiner le rendement pédagogique puis étendre seulement si utile. Les réservations de plafond restent conservées pendant le cycle pour couvrir le retard possible des relevés de consommation. Un manque de crédit arrête les lancements ; la collecte ne continue pas sur un solde payé. Les résultats réels peuvent être très inférieurs au nombre de publications demandé. Un lot déjà reçu ne se relance pas : `--resume` lit seulement le run existant. Ne pas copier l'état ou créer une seconde instance du paquet pour contourner les réservations. Si le fournisseur change son build ou son schéma, comparer les sources publiques, relire l'impact et refaire les tests avant de modifier le contrat local.

## Navigateur connecté

Le protocole `browser-workflow.md` utilise exclusivement CUA et les éléments visibles. Le helper `scripts/browser_social_capture.py` transforme les captures locales complètes en un export à qualifier ; une grille incomplète reste une liste de liens à lire. Il ne lit pas les cookies, les requêtes internes, le stockage du navigateur ou les messages privés, et ne résout pas les CAPTCHA. Seules les métadonnées de publications publiques pertinentes entrent dans la revue.

## Du résultat à la publication

Conserver l'identifiant, l'URL, la source et le texte original. Séparer titre, légende et hashtags avec le skill `social-content-structure`. Ne pas déduire une langue audio d'un profil français, une compatibilité véhicule d'un hashtag ou une transcription d'un extrait d'index. Les sources publiques ne sont pas présumées libres de réutilisation.

Préparer les lots hors base, les relire et garder les cas ambigus en attente. Un traitement récurrent peut réaliser cette revue sans solliciter l'utilisateur pour chaque fiche, dans le périmètre déjà autorisé. Importer uniquement les références retenues, préserver les anciennes fiches, vérifier le catalogue et publier le nouvel export sur le dépôt GitHub existant. Vérifier ensuite le catalogue servi par GitHub Pages et actualiser le paquet local. Ne pas annoncer une hausse avant que l'import et sa publication soient constatés.

## Cadence

Le suivi quotidien « RaceLink Academy — collecte et classement » a été créé avec le statut ACTIVE dans l'application. Il reprend l'état existant, privilégie un accès natif connecté et évite les campagnes web répétitives. Il peut traiter un lot Apify après vérification des seuls crédits gratuits, ou des captures CUA publiques accessibles, puis classer les nouvelles références. Si aucune connexion n'est disponible, conserver le blocage et poursuivre uniquement le travail local utile ; ne pas multiplier les formulaires de connexion ou les demandes identiques. Le programme planifié n'a pas encore exécuté de passage : son activation ne prouve pas que la collecte native est débloquée.

Les copies distribuées ont été testées depuis le dossier `collector/` : 82 tests de file, transport et captures, puis 44 tests du sous-paquet Apify, tous réussis hors réseau. Le contrôle réel du budget en mode lecture s'est arrêté avant réseau avec `APIFY_TOKEN_not_configured`.
