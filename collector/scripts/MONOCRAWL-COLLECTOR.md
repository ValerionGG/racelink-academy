# Collecteur Monocrawl — pilote borné RaceLink

Contrat vérifié le 26 octobre 2026. Adaptateur Python standard, sans dépendance
supplémentaire, pour chercher des **publications publiques réelles** puis préparer
leur revue. Ce document et les tests ne prouvent pas une collecte : **aucun appel
payant, aucune vidéo importée et aucun compte connecté par cet adaptateur à ce
stade**. Les exemples des tests sont fictifs et restent dans des dossiers temporaires.

## Sources vérifiées

- [Skill officiel v1.6.1](https://raw.githubusercontent.com/monocrawl/monocrawl-mcp/main/skills/monocrawl/SKILL.md) et [dépôt MCP](https://github.com/monocrawl/monocrawl-mcp).
- [TikTok search](https://www.monocrawl.com/docs/endpoints/tiktok/search) :
  `GET /v1/tiktok/search`, tarif affiché de **2 crédits** par appel ; pas de
  garantie de quantité. `region=FR` est un lieu de requête, pas une langue audio.
- [Instagram search-reels](https://www.monocrawl.com/docs/endpoints/instagram/search-reels) :
  `GET /v1/instagram/search-reels`, **1 crédit** affiché. La couverture de l'index
  peut être incomplète ou en retard. Ce pilote garde le mode de recherche par
  défaut, sans date forcée ni mode natif supplémentaire.
- [Crédits](https://www.monocrawl.com/docs/credits),
  [tarification](https://www.monocrawl.com/docs/endpoint-pricing) et
  [authentification](https://www.monocrawl.com/docs/authentication).
- [Pagination et cache](https://www.monocrawl.com/docs/pagination-caching).

Le README GitHub annonce 1 000 crédits mensuels, tandis que certaines pages de
documentation annoncent 150 crédits de démarrage. **Aucune de ces promesses ne
constitue le solde du compte** : enregistrer seulement les crédits gratuits et
réglages réellement observés, avec leur date. Ne pas activer carte, abonnement,
rechargement ni dépassement payant.

## Connexion et plafond

Le MCP officiel est privilégié : `call_endpoint` expose `max_credits` et
`idempotency_key`. Son skill décrit un helper de connexion par navigateur qui
conserve la clé hors du chat. Il faut examiner ce helper avant installation,
utiliser le compte voulu, puis vérifier que les outils sont réellement chargés
avec `get_balance`. La présence d'une configuration n'est pas une connexion
vérifiée. Le présent script n'installe et ne configure aucun MCP.

En REST, utiliser seulement `MONOCRAWL_API_KEY`, explicitement fourni dans
l'environnement, pour une **clé dédiée dont la limite cumulée a été observée**.
La limite doit être inférieure ou égale au budget gratuit du pilote. Les limites
locales ne protègent pas seules contre un prix modifié ou un autre consommateur
du même compte ; la limite de clé fournit la borne côté service. Le script ne
cherche jamais une clé dans le navigateur, un fichier de connexion ou un cache.
Les requêtes refusent les redirections et n'inscrivent pas les secrets dans les
logs, les réponses conservées ou les paramètres d'URL.

## Plan et commandes

Créer un JSON privé après observation du compte. Exemple de **structure** à
adapter aux chiffres constatés ; ces chiffres ne sont pas des crédits acquis :

```json
{
  "version": 1,
  "free_credits": 10,
  "budget_credits": 6,
  "checked_at": "REMPLACER_PAR_DATE_UTC_OBSERVEE",
  "auto_reload": false,
  "overage": false,
  "out_of_pocket_usd": 0,
  "transport": "mcp",
  "key_credit_limit": null,
  "jobs": [
    {"id":"clio","platform":"tiktok","query":"Comment changer le filtre à air Renault Clio","region":"FR","max_pages":3},
    {"id":"freins","platform":"instagram","query":"Comment changer les plaquettes de frein voiture","region":null,"max_pages":3}
  ]
}
```

La date doit dater de moins de 24 heures. Le pilote accepte jusqu'à 50 recherches
explicites, 100 crédits au total au plus, sans dépasser le gratuit observé.
Une exécution REST fait au plus trois pages, espacées de deux secondes.

```text
python -B scripts/monocrawl_collect.py init --plan CHEMIN_PRIVE/plan.json --directory CHEMIN_PRIVE/campagne
python -B scripts/monocrawl_collect.py preview --directory CHEMIN_PRIVE/campagne --job clio
```

`preview` n'envoie aucune requête et ne lit aucun secret. Pour le MCP :

```text
python -B scripts/monocrawl_collect.py reserve --directory CHEMIN_PRIVE/campagne --job clio
```

Transmettre exactement l'objet `mcp` retourné au `call_endpoint` officiel, une
seule fois. Conserver l'enveloppe JSON complète dans un fichier privé puis :

```text
python -B scripts/monocrawl_collect.py accept --directory CHEMIN_PRIVE/campagne --reservation 0 --response CHEMIN_PRIVE/reponse.json
```

Si le MCP renvoie `stored_result`, récupérer gratuitement ses données complètes
selon le skill officiel **avant** `accept`, sans répéter la recherche payante.
Ne pas reconstruire une enveloppe à partir d'un résumé ou d'une réponse tronquée.

Pour REST, définir `transport=rest` et le `key_credit_limit` observé dans le plan.
Une fois la variable d'environnement fournie à ce processus :

```text
python -B scripts/monocrawl_collect.py run --directory CHEMIN_PRIVE/campagne --job clio
python -B scripts/monocrawl_collect.py run --directory CHEMIN_PRIVE/campagne --job clio --execute --max-pages 1
```

Sans `--execute`, `run` reste une prévisualisation. Aucune route d'achat,
transcription, profil privé, téléchargement vidéo ou recherche hors liste n'est
appelée. Les tarifs listés sont des réservations prudentes, pas une promesse que
tous les appels seront facturés au même prix. Le reçu de chaque appel fait foi.

## Reprise, provenance et revue

Le registre réserve avant l'appel. Un timeout, HTTP 403/429, JSON invalide,
facturation indéterminée ou dépassement du montant réservé bloque la suite.
Un `receipt_pending` imbriqué reste indéterminé même avec un montant provisoire.
Une réponse d'erreur, même accompagnée de zéro crédit, reste conservée et bloquée
pour réconciliation : elle n'est jamais reclassée en recherche vide réussie.
Il n'y a **aucune nouvelle tentative automatique** et aucune remise à zéro des
crédits. Examiner le reçu et les transactions du service pour réconcilier le
résultat. Ne pas supprimer la réservation ou créer une autre campagne pour
contourner cet arrêt. Une réservation MCP conserve sa clé d'idempotence ; un
rejeu nécessite cette même clé et les mêmes paramètres, après examen du résultat.

Chaque réponse valide conserve son enveloppe native, son empreinte SHA-256 et
son identifiant de requête. Un cache gratuit n'augmente jamais le budget local.
Le dernier solde peut réduire le budget utilisable, jamais l'augmenter. La limite
observée de la clé borne aussi les réservations locales avant envoi.
Le curseur retourné est recopié sans modification, avec la même recherche et la
même région. Une page vide ou un curseur absent ou répété termine ce parcours ; cela ne signifie
pas que tout le réseau a été parcouru. Une réponse partielle suspend la collecte.

Les fichiers `review-*.json` contiennent des **candidats**, jamais une validation
pédagogique. L'adaptateur utilise `bulk_ingest.adapt` comme schéma de compatibilité
et `social_metadata` pour séparer titre, description, hashtags et texte source.
La provenance reste `monocrawl`, avec la réserve `public_search_metadata`.
La durée musicale et la région ne deviennent ni durée vidéo ni langue audio.
Aucun audio, commentaire ou transcription n'a été analysé par cet outil.

Avant import : vérifier utilité automobile, titre, doublons, langue des
métadonnées, véhicule/modèle/moteur attestés et caractère public. Les champs
inconnus restent inconnus. Les publicités et cas ambigus restent en revue ; une
référence publique n'accorde aucun droit de réutiliser la vidéo. Ne publier ni
réponses brutes, ni registre, ni données de compte avec le site.

## Vérification

```text
python -B -X utf8 scripts/test_monocrawl_collect.py
```

Tests hors réseau : prévisualisation, plafond gratuit, observations périmées,
clé REST bornée, curseurs et filtres exacts, réservations bloquantes, reçu
comptabilisé une fois, arrêt sur coût incertain, refus des échantillons,
séparation des champs, aucune invention de langue audio, données privées ou
images refusées et absence de nouvelle tentative après panne.
La revue adversaire ajoute des cas de reçu imbriqué en attente, page vide,
solde inférieur au coût, confidentialité de l'auteur, vidéo explicitement
absente, titre natif et hashtag numérique. **42 tests hors réseau réussis.**
