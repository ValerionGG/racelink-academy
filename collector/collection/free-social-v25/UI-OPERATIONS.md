# Pilote via Apify Console et reprise future

Cette fiche décrit une procédure opérateur, vérifiée dans la documentation publique le 26 octobre 2026. Elle ne lance rien, n'importe aucun reçu et ne constate pas l'état d'un compte. Le launcher reste une CLI explicite ; une connexion au navigateur ne configure pas `APIFY_TOKEN`.

## Avant chaque Start

Vérifier dans Billing le plan Free sans abonnement payant ni recharge, l'allocation gratuite disponible et son cycle. Vérifier qu'aucun run n'est actif. Conserver la preuve de ces observations, sans jeton ni données de compte inutiles. Déduire prudemment chaque plafond déjà engagé dans le cycle, même après la fin du run, et garder 0,25 USD de marge globale. Deux lots de 0,50 USD représentent donc une réserve de 1 USD, même si leur facture finale est inférieure. Cette règle locale est plus prudente que l'affichage de consommation susceptible de se mettre à jour avec retard. [Facturation Apify](https://docs.apify.com/account/billing)

Ouvrir Input et charger le JSON préparé du lot. Dans Run options, définir les paramètres suivants avant un seul clic sur Start. [Options officielles](https://docs.apify.com/actors/development/quick-start/web-ide)

| Lot | Profil / maximum brut | Build revu | Timeout | Mémoire | Maximum cost per run |
| --- | --- | --- | --- | --- | --- |
| fr-tiktok-06 | maclede12 / 60 | 0.0.620 | 600 s | 4096 MB | 0,50 USD |
| fr-instagram-01 | norautofr / 100 | 0.0.618 | 600 s | 1024 MB | 0,50 USD |

Relire prix et schéma avant exécution : un changement par rapport aux fixtures nécessite une revue. Les entrées fournies désactivent téléchargements de médias, commentaires, abonnés, transcriptions et enrichissements. Les plafonds portent sur un run, pas sur un abonnement. Ne pas utiliser No maximum limit, Restart/Resurrect ou un second Start pour résoudre un statut incertain. Examiner le run déjà créé et conserver son identifiant. La console indique son origine WEB ; ce n'est pas une exécution CLI. [Cycle de vie et origine des runs](https://docs.apify.com/actors/running/runs-and-builds)

## Export pour revue

Dans Output ou Storage > Datasets, sélectionner le dataset du run, puis Export > JSON. Select fields attend les clés de premier niveau : `authorMeta` et `videoMeta`, pas `authorMeta.name` ou `videoMeta.duration`. Omit fields accepte les chemins imbriqués ; on peut y exclure les contacts et biographies lorsque ces champs existent. Le prévisualiser avant Download. Conserver localement l'export jusqu'à sa projection, sans partager le dataset ni télécharger les fichiers médias. [Dataset et export Console](https://docs.apify.com/storage/dataset)

La liste de sélection complète est `DATASET_FIELDS` dans `launch_free_pilot.py`. Préserver notamment les restrictions de publication privée, sponsorisée, photo, story ou IA. L'export JSON garde les tableaux et objets nécessaires. Appliquer ensuite `safe_post_metadata` en mémoire à chaque ligne avant de conserver les pages de revue. Cette fonction garde seulement le compte auteur public, la légende, les hashtags, la durée, les liens de publication et miniatures admissibles, avec leurs restrictions. Le manifeste et les hashes doivent être créés selon le contrat PUBLIC_EXPORT ; ne pas qualifier un export Console brut de page déjà filtrée. Aucun import automatique en base n'est prévu par cette fiche.

## Proposition de rapprochement des runs Console

Le marqueur local **`UI_RUNS_UNRECONCILED`**, placé à côté de `launch_free_pilot.py`, bloque les nouveaux démarrages réels avant lecture du jeton, réseau et création du runtime. Son contenu n'est jamais lu ; un fichier vide suffit. La garde est répétée juste avant la soumission. L'aperçu et la reprise GET d'un reçu CLI existant restent possibles. Un ledger situé ailleurs n'est pas découvert automatiquement : l'opérateur doit poser ce marqueur dans chaque copie CLI qu'une automatisation peut utiliser avant de lancer des lots dans la Console. Le fichier est ignoré par Git et doit rester hors distribution.

Le programme ne retire jamais ce marqueur. Il ne doit être retiré qu'après rapprochement complet de tous les runs UI, de leurs issues et de leurs réservations durables pour le cycle. Le supprimer simplement pour débloquer un lancement perdrait la protection recherchée. Le marqueur protège la copie CLI où il se trouve ; il ne coordonne pas une autre installation ou un autre opérateur.

Le code actuel ne possède pas de commande d'adoption d'un run UI. Ne pas fabriquer un reçu `explicit_cli_free_credits_only` ou un `budget_check` qui prétendrait à une vérification API passée. Avant toute future exécution CLI, rapprocher tous les runs Console et les réservations ; une copie de paquet sans cet historique ne doit pas lancer de nouveaux lots.

Une commande d'adoption à développer devrait fonctionner ainsi :

1. Prendre le même verrou local et créer une réservation bloquante durable avant tout rapprochement. Un état inconnu doit bloquer les nouveaux lancements ; le code actuel reconnaît `submission_pending` et `outcome_unknown_do_not_resubmit` dans les reçus `fr-*.json`. Ne pas écrire une date de cycle ou un coût supposé.
2. Enregistrer les observations Console avec leur source et date : acteur, run ID, dataset ID, input JSON exact et hash, build, plafond visible, période de crédit et consommation observée. Conserver `origin=WEB` et `execution_mode=console_ui_observed`. L'absence d'une preuve reste explicite.
3. Après configuration explicite de `APIFY_TOKEN`, effectuer seulement des GET : identité/plan/cycle/usage actuels et statut, origine, acteur, dataset, input et options du run connu. Comparer le run et l'entrée au lot préparé, notamment le plafond effectif inférieur ou égal à 0,50 USD. Aucun POST, Restart, Resurrect, abonnement ni modification de limite.
4. Construire un reçu de reprise uniquement après concordance. Pour un cycle donné, partir du maximum entre consommation actuelle vérifiée et réservations déjà durables, puis ajouter les plafonds entiers des runs UI non encore intégrés. Cette méthode peut compter deux fois une consommation déjà reflétée ; elle est volontairement prudente. Ne pas diminuer une réserve antérieure à partir du seul coût final et ne jamais compter deux fois le même run ID dans le journal d'adoption.
5. Écrire et synchroniser chaque reçu puis seulement lever le blocage de rapprochement. Le reçu garde une origine Console et sépare preuves observées dans l'UI et preuves GET ultérieures. La reprise utilise exclusivement le run ID existant. En cas de doute, conserver le blocage ; ne pas changer le batch ID pour relancer.

La garde par marqueur est implémentée ; la procédure d'adoption reste une proposition. Aucune réservation, aucun marqueur réel ni aucun reçu réel n'a été créé ou modifié lors de sa rédaction ou de ses tests temporaires.
