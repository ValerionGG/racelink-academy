# 06 · Confiance et qualité

> Savoir quelles vidéos ont vraiment aidé, et améliorer le catalogue en continu.

## Pourquoi

Sur 50 520 vidéos, la plupart sont des **candidates** (`review_status: candidate`), repérées par leurs métadonnées. Le niveau est connu ou estimé pour 32 769 vidéos, et reste inconnu pour 17 751. Un utilisateur ne sait pas si la vidéo en face de lui est bonne. Et nous ne savons pas lesquelles marchent.

## Expérience

### Après une vidéo
```
Cette vidéo t'a aidé ?
[👍 Oui, j'ai réussi]  [🤔 En partie]  [🚫 Pas pour ma voiture]  [⚑ Signaler]
```
- « Pas pour ma voiture » demande, sans obligation, laquelle : on apprend ainsi les mauvaises correspondances de modèle.
- « Signaler » propose : dangereux, hors sujet, mauvaise langue, lien mort.

### Sur les cartes et les fiches
- Un badge **« A aidé 48 personnes »** seulement au-delà d'un seuil (10 retours positifs), pour éviter le bruit.
- Un badge **« Vérifiée par RaceLink »** quand la vidéo a été regardée et relue, distinct de « sélection sur métadonnées », déjà affiché sur l'accueil.
- Le tri « Pertinence » intègre les retours positifs, avec un poids plafonné.

### Côté équipe : tableau qualité
`docs/CHIFFRES.md` (généré par `scripts/report_stats.py`) gagne une section qualité : vidéos signalées, liens morts, modèles mal reconnus, tâches sans vidéo en français, couverture des niveaux.

## Le point dur : il faut un serveur

Le site est statique. Pour recevoir des votes, il faut un petit service. **Décision à prendre** :

| Option | Pour | Contre |
|--------|------|--------|
| A. Formulaire d'issue GitHub prérempli | Aucun serveur ; modération intégrée | Il faut un compte GitHub : très peu de votes |
| B. Petite fonction (Cloudflare Workers avec D1 ou KV, ou équivalent) | Anonyme, un clic ; volume gratuit souvent suffisant | Un service à maintenir ; protection contre les abus nécessaire |
| C. Pas de vote, seulement des signalements par courriel (`mailto:`) | Trivial | Pas de signal de qualité exploitable |

**Recommandation : B**, avec :
- aucune donnée personnelle (ni compte, ni courriel, IP non conservée) ;
- un vote par vidéo et par navigateur (marqueur local) et une limite de débit par IP en mémoire courte ;
- des agrégats publiés **chaque jour** dans `site/catalog/feedback.json` par la CI. Le site lit ce fichier statique et n'interroge jamais le service pour l'affichage.

## Données

```json
// POST /feedback (service)
{"video": "youtube:abc", "kind": "helped | partly | wrong_car | report", "reason": "dangerous", "car": "Renault Clio V", "ui": "fr"}

// site/catalog/feedback.json (agrégats publiés)
{"generated_at": "…", "videos": {"youtube:abc": {"helped": 48, "partly": 6, "wrong_car": 2, "reports": 0}}}
```

## Implémentation

| Fichier | Changement |
|---------|------------|
| `services/feedback/` | Nouveau : la fonction, son schéma, ses tests et un `README` de déploiement |
| `.github/workflows/pages.yml` | Récupère les agrégats avant le build ; si le service est indisponible, garde le dernier fichier |
| `site/resource-detail.js` | Bloc de retour après la vidéo ; badge « A aidé N personnes » |
| `site/catalog-worker.js` | Bonus de pertinence plafonné (exemple : +10 % au maximum) |
| `scripts/report_stats.py` | Section qualité |
| Sécurité du service | CORS limité à `https://valeriongg.github.io` ; si une CSP est ajoutée à `index.html`, `connect-src` doit autoriser le domaine du service |

## Critères d'acceptation

- [ ] Voter prend un clic et fonctionne sans compte.
- [ ] Un même navigateur ne peut pas voter deux fois pour la même vidéo.
- [ ] Aucun badge sous le seuil de 10 retours.
- [ ] Une vidéo signalée « dangereuse » 3 fois est masquée du tri par défaut jusqu'à relecture.
- [ ] Le site s'affiche normalement quand le service est hors ligne.

## Hors périmètre et risques

- Pas de commentaires libres publics : la modération serait trop lourde.
- **Abus** : des votes en masse pour pousser une chaîne. Le plafond de pertinence et la limite de débit en réduisent l'effet.
