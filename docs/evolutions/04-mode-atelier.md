# 04 · Mode atelier

> Suivre une intervention étape par étape, téléphone posé sur l'aile, les mains pleines de graisse.

## Pourquoi

Au garage, l'écran se met en veille, la vidéo défile trop vite et on ne peut pas toucher le téléphone. C'est le moment où l'utilisateur abandonne ou se trompe. Aucune plateforme de tutos auto gratuite ne traite ce moment.

Le catalogue a peu de chapitres : seules **87 vidéos** ont au moins deux chapitres dans leur description, et 26 ont une transcription. Le mode atelier doit donc marcher avec trois sources d'étapes, dans cet ordre :
1. les **chapitres** de la vidéo (`parseChapters()` dans `paddock-home.js`) ;
2. les **étapes types** de la [fiche intervention](01-fiche-intervention.md), sans minutage ;
3. les **étapes** d'un guide RaceLink.

## Expérience

Bouton **« Mode atelier »** sur une fiche vidéo ou une fiche intervention.

```
┌───────────────────────────────────────────┐
│ ✕  Plaquettes de frein · étape 3 / 7  🔒☀ │
│ ┌───────────────────────────────────────┐ │
│ │        (vidéo, segment 4:50 à 6:10)   │ │
│ └───────────────────────────────────────┘ │
│                                           │
│  DÉPOSER L'ÉTRIER                         │
│  Deux vis de 13 à l'arrière de l'étrier.  │
│  Suspendre l'étrier : ne jamais le        │
│  laisser pendre par le flexible.          │
│                                           │
│  ⏲ Minuteur  ☐ J'ai fini cette étape     │
│ ┌──────────┐            ┌───────────────┐ │
│ │ ◀ Retour │            │   Suivant ▶   │ │
│ └──────────┘            └───────────────┘ │
│ 🎙 « suivant » · « répète » · « pause »    │
└───────────────────────────────────────────┘
```

- **Écran toujours allumé** avec la [Screen Wake Lock API](https://web.dev/blog/screen-wake-lock-supported-in-all-browsers) (Chrome 84, Firefox 126, Safari 16.4 ; HTTPS, ce qu'est GitHub Pages). Le verrou peut être retiré par l'appareil : le reprendre à `visibilitychange` et afficher l'icône 🔒 seulement quand il est actif.
- **Lecture par segment** avec le lecteur YouTube : `enablejsapi=1`, puis `loadVideoById({videoId, startSeconds, endSeconds})`. Le départ peut tomber jusqu'à environ 2 s plus tôt (image clé) ; c'est sans conséquence. « Répète » rejoue le segment.
- **Très gros boutons** (au moins 64 px de haut), contraste élevé, texte de 20 px minimum, bascule claire ou sombre selon la lumière du garage.
- **Commandes vocales** en option, avec l'API Web Speech, seulement si `SpeechRecognition` existe. Le support réel est à vérifier par navigateur ; ne jamais en dépendre.
- **Minuteur** par étape (temps de séchage, de vidange de l'huile…), avec un son.
- **Hors ligne** : le texte des étapes, la fiche et la liste d'outils restent disponibles sans réseau grâce à un service worker. La vidéo, elle, a besoin du réseau ; le dire clairement.
- **Reprise** : fermer et revenir rouvre à la même étape, mémorisée par intervention.

## Données

Aucune nouvelle source. Format interne d'une étape :

```json
{"index": 3, "title": {"fr": "Déposer l'étrier"}, "text": {"fr": "…"},
 "video": {"id": "youtube:abc", "start": 290, "end": 370}, "source": "chapters | task_sheet | guide"}
```

`source` s'affiche discrètement : « Étapes tirées des chapitres de la vidéo » ou « Étapes types RaceLink, la vidéo peut suivre un autre ordre ».

**Collecte** : à chaque passage, enregistrer les chapitres YouTube quand ils existent. L'API YouTube Data ne fournit pas les chapitres ; ils sont dans la description. Vérifier si `bulk_ingest.py` tronque les descriptions : c'est probablement la raison du faible nombre de chapitres.

## Implémentation

| Fichier | Changement |
|---------|------------|
| `site/workshop.js` | Nouveau : vue plein écran, wake lock, lecteur, minuteur, voix |
| `site/sw.js` | Nouveau service worker, réservé aux fiches, guides et outils : surtout pas le catalogue de 77 Mo |
| `site/resource-detail.js`, futur `site/intervention.js` | Bouton « Mode atelier » quand au moins 3 étapes existent |
| `site/app.js` (lecteur, vers la ligne 399) | Le lecteur est déjà une iframe YouTube : ajouter `enablejsapi=1` et charger `https://www.youtube.com/iframe_api` seulement en mode atelier. `index.html` n'a pas de CSP aujourd'hui ; si on en ajoute une, y autoriser ce script |
| `collector/scripts/bulk_ingest.py` | Garder la description complète, ou au moins ses lignes minutées |

## Critères d'acceptation

- [ ] Sur Android Chrome et iPhone Safari, l'écran ne se met pas en veille pendant 10 minutes en mode atelier.
- [ ] « Suivant » et « Retour » fonctionnent au clavier (flèches, espace) et au toucher.
- [ ] Une étape minutée joue son segment et s'arrête à la fin.
- [ ] Sans commande vocale disponible, aucun bouton ni texte ne la mentionne.
- [ ] En mode avion, une fiche déjà ouverte affiche ses étapes et ses outils.
- [ ] Fermer et rouvrir reprend à la bonne étape.

## Hors périmètre et risques

- Pas de réalité augmentée dans cette phase.
- **Sécurité** : le texte d'étape garde ses avertissements (étrier, chandelles) même quand le reste est condensé.
