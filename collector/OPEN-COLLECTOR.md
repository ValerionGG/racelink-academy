# Collecteur Dailymotion réutilisable

`outputs/focus-academy/scripts/collect_dailymotion.py` utilise **Python 3.9+ et sa bibliothèque standard**, sans installation supplémentaire. Il appelle uniquement la [liste publique de vidéos documentée](https://developers.dailymotion.com/v0/reference/perform-an-api-call), sans identifiant, cookie, proxy d’environnement, média ou écriture en base.

Depuis la racine du projet, aperçu sans réseau et sans création de fichier :

```powershell
python outputs/focus-academy/scripts/collect_dailymotion.py --output work/dailymotion-campaign --query "vidange moteur" --pages 2
```

Ajouter `--execute` lance réellement le plan. Répéter exactement les mêmes paramètres avec `--execute --resume` reprend le checkpoint. Les pages terminées ne sont pas redemandées ; une réponse écrite avant une interruption du checkpoint est reprise du cache. Un plan modifié demande un autre dossier vide. Le dossier doit être réservé à ce collecteur.

On peut répéter `--query` jusqu’à 60 fois. Sans `--query`, le plan embarqué sélectionne les 40 premières recherches automobiles ; `--start 40 --count 20` sélectionne les 20 suivantes. Les requêtes identiques sont refusées. Les bornes sont explicites : `--pages 1–10`, `--page-size 1–100`, `--interval 1.5–60` secondes et `--timeout 5–120` secondes. La première limite atteinte termine le plan ; il n’y a pas de promesse d’exhaustivité.

Fichiers produits seulement avec `--execute` : `plan.json`, `checkpoint.json`, `report.json`, `raw/<empreinte URL>.json`. Les réponses et le checkpoint sont écrits atomiquement ; les empreintes des pages sont vérifiées à la reprise. Un verrou `.collector.lock` empêche deux processus d’écrire dans le même dossier. Après arrêt brutal, vérifier que le processus précédent est terminé avant d’enlever un verrou devenu obsolète. **Ne pas lancer plusieurs campagnes simultanées sur ce fournisseur** : les limites ne sont pas partagées entre dossiers.

HTTP **401/403/429** crée `dailymotion-paused.json` et arrête tous les jobs suivants, sans nouvelle tentative, rotation ni changement d’accès. Le code de sortie est 3. La reprise conserve cette pause ; le script ne supprime jamais son fichier ni l’état correspondant. Les autres erreurs de transport ou de réponse sont également mises en cache et arrêtent le plan (`failed`, sortie 3), sans répétition automatique. Une erreur d’arguments ou de checkpoint sort avec le code 2. Ne pas supprimer ces preuves pour forcer une nouvelle requête ; diagnostiquer d’abord l’état du service et les conditions d’accès.

Le résultat est une **collecte de métadonnées brutes**, pas un lot de tutoriels validés. Le titre, l’auteur, l’ID et la langue déclarée viennent de l’API ; la langue audio et la qualité pédagogique restent non vérifiées. Les règles de qualification, dédoublonnage et revue doivent s’appliquer séparément avant import. Les descriptions sources ne donnent aucun droit de réutilisation des vidéos/transcriptions. Le schéma brut conserve uniquement les champs demandés de publication, pas de flux ni de commentaires.

Tests hors réseau :

```powershell
python work/scale-v23/test_collect_dailymotion.py
```

Le collecteur portable n’a effectué aucune nouvelle collecte pendant sa préparation. Les scripts ad hoc et le lot figé `work/scale-v23/open-platforms/final-v3/` sont les preuves du passage précédent et n’ont pas été modifiés par ce travail.
