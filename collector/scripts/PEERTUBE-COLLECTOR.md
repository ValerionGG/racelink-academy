# Collecteur PeerTube / SepiaSearch

Vérifié le 28 octobre 2026. Le script `peertube_collect.py` lit uniquement des métadonnées publiques, sans compte, cookie, navigateur, abonnement ou fichier vidéo. Son résultat est une file de revue, jamais un import automatique.

## Utilisation

Python 3.11+ et curl avec TLS sont suffisants. Créer un plan de recherches :

```json
{"jobs":[{"query":"entretien automobile","limit":20,"language":"fr"}]}
```

Ou suivre une chaîne dont l’URL publique a été attestée :

```json
{"jobs":[{"channel":"https://tube-enseignement-professionnel.apps.education.fr/video-channels/lycee_guynemer","limit":25}]}
```

Les chaînes sont limitées aux deux hôtes éducatifs explicitement examinés dans `CHANNEL_HOSTS`. Ajouter un nouvel hôte exige une vérification de sa documentation, de son caractère public et de ses règles. Le mode recherche utilise exclusivement l’API publique de SepiaSearch.

Depuis le dossier du collecteur :

```powershell
python -B -X utf8 scripts/peertube_collect.py plan.json --output collection/peertube-nouveau-lot
python -B -X utf8 scripts/peertube_collect.py plan.json --output collection/peertube-nouveau-lot --execute
```

La première commande prévisualise. Chaque requête est bornée à 25 résultats. Le plan utilise au maximum 100 résultats par défaut, avec un plafond absolu de 500 explicitement paramétrable. L’intervalle est de 3 secondes, jamais inférieur à 2 secondes ; un seul processus et aucune relance réseau automatique. Les erreurs HTTP, limitations, réponses inattendues ou appels interrompus bloquent la source.

Une reprise emploie le même plan, le même dossier et `--resume --execute`. Elle ne rejoue pas les pages terminées. Une requête restée `pending`/`blocked` ou un verrou actif impose une revue de l’état avant toute reprise : ne pas créer un nouveau dossier pour la rejouer. Les réponses sont limitées à 8 Mio ; aucun téléchargement de média, suivi de redirection, proxy ou extraction de session.

## Preuves et revue

- `checkpoint.json` : plan scellé, URL de chaque requête, statut et SHA-256 de sa réponse.
- `raw/` : réponses natives privées, conservées sans modification.
- `records.json` : identités canoniques `peertube:hôte:UUID`, titre, description présente ou absente, tags, hashtags, auteur, langue déclarée, durée, miniature native et provenance.
- `duplicates.json` et `rejected.json` : doublons, variantes et résultats dont la visibilité publique n’est pas attestée.
- `result.json` : reçus, distincts, invalides, doublons. Les valeurs `imported` et `published` restent à zéro.

Les descriptions de listing peuvent être tronquées. Une langue déclarée ne prouve pas la langue audio. Une licence affichée est une déclaration source, pas une validation de droits ; aucune licence libre, transcription, compatibilité automobile ou procédure constructeur n’est déduite. Les miniatures sont des URL natives, sans téléchargement par le collecteur. Les titres/descriptions doivent être relus avec `social_metadata.py` avant import.

Pour intégrer au schéma existant, conserver `platform=other`, `provider=peertube`, un identifiant stable, les preuves natives et `review_status=candidate` / `verification_scope=public_api_metadata`. La revue compare les URL avec SQLite en lecture seule. La sauvegarde, l’approbation scellée, l’import strict et la vérification avant/après restent des opérations distinctes.

## Pilote V34

Huit appels publics ont reçu **95 lignes**, représentant **89 identités** : 6 doublons internes, 13 références déjà présentes, 21 en attente, 54 exclues et **1 nouvelle référence retenue** sur la gestion des déchets des concessions. Le résultat ne démontre pas un gisement massif ; les recherches globales étaient bruitées et les meilleures vidéos de maintenance étaient déjà référencées. La nouvelle voie permet surtout de suivre précisément des chaînes pédagogiques avec des preuves natives.

21 tests hors réseau couvrent les plafonds, URL, visibilité publique, hashtags, descriptions absentes, identité, photos natives, empreintes, déduplication, blocage 429, verrou et reprise sans rejouer.

```powershell
python -B -X utf8 -m unittest discover -s scripts -p test_peertube_collect.py -v
```

Sources : [recherche PeerTube](https://docs.joinpeertube.org/use/search), [API officielle et listes de chaînes](https://docs.joinpeertube.org/api-rest-reference.html), [SepiaSearch](https://sepiasearch.org/), [code de l’index Framasoft](https://framagit.org/framasoft/peertube/search-index), [mentions légales](https://framasoft.org/en/legals/).
