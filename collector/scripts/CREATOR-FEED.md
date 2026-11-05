# Référencer les cartes Instagram affichées par un éditeur

Certains ateliers affichent leurs propres publications Instagram sur leur site avec le plugin WordPress Smash Balloon. Le type de média, le lien du post et la légende peuvent alors être lus ensemble sur la page de l’atelier. Cette méthode n’utilise ni compte ni crédit. Elle dépend des cartes que l’éditeur décide d’afficher. [Plugin WordPress](https://wordpress.org/plugins/instagram-feed/) · [Documentation des modèles HTML](https://smashballoon.com/doc/guide-to-creating-custom-templates/) · [Miroir historique GitHub](https://github.com/wp-plugins/instagram-feed)

Enregistrer un plan local au format suivant, après avoir choisi les pages publiques des éditeurs. Chaque éditeur doit avoir son propre domaine et l’URL doit commencer par HTTPS.

```json
{"jobs":[{"url":"https://www.example.org/realisations/","creator":"Nom de l’atelier"}]}
```

Prévisualiser un éditeur, puis l’exécuter. Python 3.10 ou supérieur suffit.

```text
python creator_feed_collect.py plan.json --job 0
python creator_feed_collect.py plan.json --job 0 --checkpoint campagne-editeurs --execute
```

Le collecteur lit les consignes robots.txt et la page approuvée. Il conserve au plus 30 cartes par éditeur, associées au lien source et à l’empreinte de la page. Une réponse limitée, une redirection ou un délai élevé suspend cet éditeur. Le dossier de suivi est lié au plan exact. Tout travail déjà amorcé doit être réconcilié avant une nouvelle campagne.

Pour un passage ultérieur, comparer chaque identifiant à ceux du catalogue et de toutes les vagues précédentes, inclus les refus et les attentes. Un résultat ambigu reste en attente. Une vidéo est retenue seulement si le geste ou l’explication est identifiable. Saisir la langue d’après les mots réellement fournis. Attribuer une marque, un modèle, un moteur ou une année uniquement lorsque la légende du même post les établit. La lecture audio, la licence, la compatibilité et la conformité à une procédure constructeur demandent chacune une preuve distincte.

Le pilote a lu 44 cartes sur quatre sites. Elles comprenaient 14 vidéos, 20 carrousels et 10 photos. Les légendes des vidéos présentaient des réalisations, des services, une équipe ou une course. Six vidéos attendent une meilleure preuve du geste montré. Aucun tutoriel de ces quatre flux n’a été retenu.

```text
python test_creator_feed_collect.py
```
