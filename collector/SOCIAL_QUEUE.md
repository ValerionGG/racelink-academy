# File de découverte sociale

Version 1.0.1, 26 octobre 2026. Le script `scripts/social_queue.py` appelle le collecteur Exa MCP public existant, conserve les preuves et prépare des paquets de revue. Il ne connecte aucun compte, ne lance aucun Actor payant, ne télécharge aucun média et n’importe rien dans le catalogue. Python, Node et `mcporter` doivent déjà être disponibles.

## Bilan réel et limites

La campagne a terminé **200 recherches**, produisant **4 693 variantes pour 280 identités distinctes**. La préparation a isolé 70 candidats automatiques, dont 38 absents du catalogue. La revue éditoriale par un agent de ces 38 retient **16 candidats (4 Instagram, 12 TikTok)** : titres textuels anglais, audio non vérifié. Les 16 autres sont en attente et 6 sont exclus ; les 8 restrictions V23/V24 rencontrées restent conservées. **Les 16 retenus attendent un prochain import. Le site et le catalogue restent V24.**

Ce résultat modeste ne satisfait pas l’objectif de collecte massive. Exa peut retourner des vidéos d’autres auteurs que le profil recherché. Le curseur avance dans une file de requêtes : **il n’y a ni pagination de profil, ni rafraîchissement quotidien automatique**. Les requêtes identiques sont dédoublonnées durablement ; répéter la commande ne relance pas les 200 recherches terminées.

## Commandes

Depuis le dossier `collector/` du paquet, ou `outputs/focus-academy/` dans les sources. Les chemins `runs/` ci-dessous désignent une nouvelle campagne d’exemple, pas une remise à zéro de la campagne existante.

Un plan JSON contient `jobs`, avec des requêtes explicites issues de profils ou de liens réellement observés. Exemple de structure :

```json
{"jobs":[{"kind":"exa_search_advanced","value":"Instagram norautofr reel tutoriel mécanique entretien réparation voiture","limit":50,"include_domains":["instagram.com"],"include_text":[],"user_location":"FR"}]}
```

Enregistrer le plan dans `creator-plan.json`, puis :

```powershell
python -B -X utf8 scripts/social_queue.py init --queue runs/creator-queue --request-cap 200 --daily-cap 200 --result-cap 10000 --interval 2
python -B -X utf8 scripts/social_queue.py enqueue --queue runs/creator-queue creator-plan.json
python -B -X utf8 scripts/social_queue.py run --queue runs/creator-queue --max-jobs 20 --max-seconds 600
python -B -X utf8 scripts/social_queue.py run --queue runs/creator-queue --max-jobs 20 --max-seconds 600 --execute
python -B -X utf8 scripts/social_queue.py status --queue runs/creator-queue
```

Sans `--execute`, `run` donne un aperçu sans réseau. Avec ce drapeau, il traite seulement les travaux encore en attente, dans les plafonds persistants. Chaque tentative réserve son coût en requêtes et son maximum de résultats **avant** l’appel ; une erreur ou une interruption ne libère pas ce quota. Les limites journalières utilisent UTC. Une invocation est bornée à 200 travaux et une heure au maximum.

Ces plafonds locaux ne prouvent pas le crédit gratuit disponible chez le fournisseur et ne couvrent pas les appels d’autres outils. Une réponse 403/429, une demande d’authentification ou un échec met la file en pause persistante, sans contournement ni repli payant. Ne pas créer une nouvelle file pour esquiver un quota épuisé. `include_text`, la requête et `user_location` ne prouvent ni la langue audio ni l’appartenance au créateur recherché.

## Arrêt, reprise et suivi

```powershell
python -B -X utf8 scripts/social_queue.py request-stop --queue runs/creator-queue --reason "Pause pour revue des résultats"
python -B -X utf8 scripts/social_queue.py status --queue runs/creator-queue
python -B -X utf8 scripts/social_queue.py resume-after-review --queue runs/creator-queue --reason "État vérifié, reprise autorisée"
```

L’arrêt coopératif laisse finir la requête en cours puis bloque la suivante. `status` est en lecture seule et fonctionne pendant la collecte. La reprise ne remet aucun quota à zéro. Un résultat de requête incertain n’est pas répété automatiquement ; `--retry-job N` sur `resume-after-review` demande explicitement une nouvelle tentative, consomme une nouvelle réservation et peut répéter un appel déjà effectué. Ne l’utiliser qu’après vérification de l’état réel.

Après un changement de collecteur relu et testé, utiliser une migration explicite, sans job actif ni verrou :

```powershell
python -B -X utf8 scripts/social_queue.py rebind-collector --queue runs/creator-queue --expected-old-hash SHA256_EXACT_LU_DANS_STATUS --reason "Correctif du collecteur relu et testé"
```

Cette commande journalise les deux empreintes et préserve les quotas, états, pauses et anciennes preuves. Le correctif d’interruption du sous-processus, dans `local_collect` 1.0.2, a été appliqué après les 200 recherches ; leur snapshot conserve l’ancienne version. Ne pas supprimer un verrou avant d’avoir confirmé la fin du processus et de son enfant.

Un suivi quotidien peut consulter `status` et reprendre jusqu’à 20 travaux **déjà autorisés et encore en attente**. Une file terminée ou épuisée ne produit rien de nouveau. Les nouvelles recherches doivent apporter des sources réellement nouvelles et respecter le quota restant ; aucun mécanisme de rafraîchissement daté des mêmes profils n’est implémenté.

## Préparation et revue hors catalogue

```powershell
python -B -X utf8 scripts/social_queue.py snapshot --queue runs/creator-queue --output runs/creator-snapshot-001
python -B -X utf8 scripts/social_queue.py prepare --snapshot runs/creator-snapshot-001 --output runs/creator-review-001 --max-records 25000 --batch-size 1000 --max-batches 10
```

Le snapshot doit aller dans un dossier neuf, séparé de la file. Répéter la même commande `prepare` jusqu’à `complete=true`. La préparation vérifie les empreintes et réconcilie toutes les variantes avant de créer `review/batch-000000/accepted.json`, `quarantine.jsonl`, `report.json` et un modèle d’approbation vide. `accepted` signifie candidat automatique, pas autorisation de publication.

Relire les titres indexés, les preuves directes disponibles, les exclusions antérieures et les informations véhicule. Les corps composites Exa ne sont jamais des légendes natives. Aucune langue audio, transcription, licence libre ou compatibilité technique ne doit être inventée. Une nouvelle preuve contradictoire impose une nouvelle revue ; aucune approbation historique n’est transférée automatiquement.

La campagne réelle se trouve dans `work/scale-v25/creator-queue`, son snapshot dans `creator-snapshot` et sa préparation dans `creator-review`. `research/editorial-review.json` conserve les 38 décisions, les 16 identités retenues et le SHA256 du snapshot accepté. La file n’a aucune commande d’import ou de publication.

Validation hors réseau de la version livrée : **28 tests de file et 30 tests du collecteur**, dont quotas persistants, interruption, arrêt coopératif, migration, conflits entre variantes et altération de preuves. Les fixtures de ces tests sont synthétiques ; elles ne comptent pas comme vidéos collectées.
