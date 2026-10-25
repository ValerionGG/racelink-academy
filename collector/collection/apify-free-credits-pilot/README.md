# Pilote Apify — crédits gratuits uniquement

Autorisation utilisateur : « Uniquement les crédits gratuits disponibles ».

Le plan reprend les 14 lots précédemment préparés, avec un maximum de 1 000 publications brutes. Les 5 $ représentent uniquement la somme des plafonds techniques historiques. Le plafond réellement utilisable dépend du crédit gratuit restant, vérifié dans le compte connecté. Aucun coût réel, crédit acheté, abonnement ou recharge n’est autorisé.

État : connexion et crédit gratuit non vérifiés, aucun lot lancé. Ne pas passer ce plan à un lanceur ancien qui ignore `spending_policy`.

Avant chaque lancement : vérifier la provenance gratuite du crédit, son solde, le prix effectif de l’Actor et l’absence de risque de facturation au-delà. Lancer un seul lot à la fois avec un plafond inférieur au crédit gratuit disponible ; vérifier la consommation avant le suivant. Une issue réseau inconnue exige de retrouver l’exécution existante, jamais de la relancer aveuglément.

Le lanceur local actuel bloque les plans `free_credits_only` à l’exécution, car il ne vérifie pas le crédit du compte. L’aperçu reste disponible. Un lancement dans la console ne peut être envisagé qu’après vérification du crédit et du plafond.

Aperçu depuis le dossier de l’application ou `collector/` :

```powershell
python scripts/start_social_batch.py --plan collection/apify-free-credits-pilot/plan.json --batch fr-tiktok-01
```

Validation locale : 12 tests réussis, dont refus avant accès aux identifiants, reçus et réseau ; aucun lot réel lancé.
