# 05 · Progression

> Des parcours qu'on termine, des notions qu'on retient.

## Pourquoi

Les 8 parcours existent, avec des étapes cochables (clé `rl-library-progress`, `app.js` vers la ligne 351), mais rien ne vérifie qu'on a compris, et rien ne fait revenir. Regarder une vidéo ne veut pas dire savoir faire.

## Expérience

### Fin d'étape : 3 questions
À la fin d'une étape de parcours, un mini-quiz de 3 questions. Pas de note sur 20 : la bonne réponse et une phrase d'explication.

```
QUESTION 2 / 3 · FREINER PLUS TARD
Où se situe le point de freinage le plus tard possible ?
( ) Au point de corde
(•) Là où l'on peut encore ralentir assez pour la vitesse du virage
( ) Toujours au panneau des 100 m
✓ Exact. Le panneau aide à se repérer, mais le point dépend de la voiture et de l'adhérence.
[Revoir le passage de la vidéo ▸ 3:12]
```

### Cartes de révision
Les notions clés deviennent des cartes : « Que veut dire 5W30 ? », « Pourquoi un couple de serrage ? », « Que montre une trace de frein ? ». Elles reviennent au bon moment grâce à [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs) (MIT). Une session de 2 minutes maximum depuis l'accueil, avec le libellé « 5 notions à revoir ».

### Tableau de progression
```
TA PROGRESSION
Entretenir sa voiture   ████████░░  4/5 étapes · 2 quiz réussis
Freiner plus tard       ██░░░░░░░░  1/4
Notions retenues        23 · 5 à revoir aujourd'hui
[Exporter ma progression]
```

Pas de série de jours, pas de classement : RaceLink n'est pas un jeu. La seule récompense est un **certificat de parcours** en image, que l'utilisateur garde et partage, avec la mention « autoformation, non certifiant ».

## Données

```json
// site/quizzes.json (éditorial)
{"version": "1.0.0", "tracks": {"brake-later": [{"step": 0, "questions": [
  {"id": "bl-0-1", "q": {"fr": "…", "en": "…", "es": "…"}, "choices": [{"fr": "…"}], "answer": 1,
   "explain": {"fr": "…"}, "video": {"id": "youtube:…", "at": 192}}]}]},
 "cards": [{"id": "oil-5w30", "front": {"fr": "Que veut dire 5W30 ?"}, "back": {"fr": "…"}, "topic": "lubrication"}]}

// localStorage « rl-learning » : réponses et état FSRS de chaque carte
```

Les questions sont rédigées à partir des vidéos et des guides et **relues**. Une question sans source vérifiable ne part pas.

## Implémentation

| Fichier | Changement |
|---------|------------|
| `site/quizzes.json` | Nouveau, éditorial : 3 questions par étape, 40 cartes au lancement |
| `site/learning.js` | Nouveau : quiz, file de révision ; import de `ts-fsrs` en ESM, fichier copié et versionné dans `site/vendor/` (pas de CDN, à cause de la CSP) |
| `app.js` (vue des parcours) | Quiz en fin d'étape ; l'étape n'est validée qu'avec le quiz réussi ou volontairement passé |
| `site/paddock-home.js` | Encart « 5 notions à revoir » s'il y a des cartes dues |
| Export et import | Le même mécanisme que le garage de [03](03-ma-voiture.md) |

## Critères d'acceptation

- [ ] Les 8 parcours ont un quiz à chaque étape.
- [ ] Une mauvaise réponse montre l'explication et un lien vers le moment de la vidéo.
- [ ] Les cartes reviennent selon FSRS ; une carte bien connue revient de plus en plus tard.
- [ ] La progression survit au rechargement ; l'export puis l'import la restaurent.
- [ ] Aucun mot « certifié » ou « diplôme » sur le certificat.

## Hors périmètre et risques

- Pas de compte ni de synchronisation entre appareils dans cette phase : l'export JSON en tient lieu.
- **Risque** : des questions mal écrites décrédibilisent tout le site. Une relecture technique est obligatoire.
