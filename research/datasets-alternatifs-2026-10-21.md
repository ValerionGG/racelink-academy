# Exports publics alternatifs TikTok / Instagram — 21 octobre 2026

## Résultat réel

**Aucun nouveau candidat importable obtenu par cette branche de recherche.** Cela ne signifie pas que les grands jeux examinés ne contiennent aucun tutoriel automobile : leurs cartes et schémas sont accessibles, mais aucun sous-ensemble pertinent n'a pu être extrait et qualifié lors des sondes bornées. Aucun import, téléchargement de média, accès natif TikTok/Instagram ou appel Exa n'a eu lieu.

Agent Reach a été utilisé par sa route GitHub `gh`. Le skill Hugging Face Datasets a guidé les appels publics du Dataset Viewer. Les pauses des fournisseurs précédemment refusés ont été conservées. Tous les accès de ce volet sont des lectures de dépôts/exportations préexistantes indépendants.

## Archives inspectées

| Source | Volume vérifié ou annoncé | Observation réelle | Décision |
|---|---:|---|---|
| [Crawlora TikTok engagement data](https://github.com/Crawlora-org/tiktok-engagement-data) | **4 509 lignes et 4 509 IDs comptés** | JSONL entier lu ; champs de niche, mot de recherche, ID, auteur et statistiques. **Aucun titre ni légende**. Projection sauvegardée sans données de profil. | 0 candidat : le mot de recherche n'est pas une preuve du contenu. |
| [Lingbow TikTok 200K](https://huggingface.co/datasets/lingbow/tiktok-video-engagement-200k) | 209 543 vidéos annoncées par la carte ; non recomptées | Schéma et cinq lignes projetées inspectés. `desc` est distinct de `gpt_summary` et de la transcription. ID vidéo mais aucun permalien/auteur public dans la table vidéo. | Piste de recherche seulement ; licence CC BY-NC 4.0, usage académique/non commercial annoncé. Aucun résumé IA retenu comme preuve. |
| [Shofo TikTok General Small](https://huggingface.co/datasets/Shofo/shofo-tiktok-general-small) | 50 000 annoncées ; non recomptées | Schéma et cinq lignes projetées inspectés ; URL directe, légende, statut publicité et langues disponibles. Les médias et commentaires ont été immédiatement exclus de la projection. | Réservé à la recherche/expérimentation selon la carte ; aucun droit sur les vidéos revendiqué par l'éditeur. Aucun candidat qualifié. |
| [datasocial TikTok 5.6B](https://huggingface.co/datasets/datasocial/tiktok-5.6B-videos) | 5,6 milliards annoncés ; non recomptés | Schéma et cinq lignes projetées inspectés, archives anciennes sans légende dans cet échantillon. ID, caption, type et langue disponibles. | CC BY-NC 4.0 ; l'éditeur réserve l'usage commercial à une offre distincte. Aucun lancement de collecteur ni utilisation du mécanisme mobile décrit par la carte. |
| [The Data Company TikTok-10M](https://huggingface.co/datasets/The-data-company/TikTok-10M) | 10 millions annoncés ; non recomptés | Cinq lignes projetées inspectées ; légendes et URLs de forme `tiktok.com/@/video/ID`, sans auteur dans le chemin. Carte biaisée vers les points d'intérêt aux États-Unis. | Licence indiquée « other » sans autorisation commerciale explicite dans la carte ; aucun sous-ensemble qualifié. |
| [Tarek Masryo Trends 2025](https://huggingface.co/datasets/tarekmasryo/youtube-tiktok-trends-dataset-2025) | Non compté | Schémas `default` et `raw` inspectés. Table analytique ; **ni URL vidéo ni ID de plateforme**. `row_id` est un identifiant de ligne, non une preuve vidéo. | Exclu pour référencement ; aucune affirmation d'authenticité des publications déduite de titres analytiques. |
| [prakhars Instagram Captions](https://huggingface.co/datasets/prakhars/instagram_captions) | 100 lignes de schéma prévisualisées | Champs `text` et `label` uniquement ; pas d'URL, shortcode, format vidéo ni README/licence identifié. Texte non conservé dans la projection. | Exclu pour référencement vidéo. |
| [AparnaHerself Instagram videos](https://huggingface.co/datasets/AparnaHerself/instagram-videos) | **0 fichier listé** au moment de l'audit | API du dépôt accessible, liste de fichiers vide, README absent. | Aucune donnée exploitable. |
| [socialonet Iran Instagram](https://github.com/socialonet/iran-instagram-dataset) | Pas de lignes téléchargées | README et arbre seulement : captions/commentaires des comptes Namava et Filimo, deux plateformes audiovisuelles. | Hors sujet automobile ; CSV non téléchargés, aucun commentaire exploité. |

## Résultats des sondes

- Les lectures de cartes, schémas et premiers aperçus du Dataset Viewer ont réussi.
- Trois essais `/filter` par `LIKE` ont reçu un HTTP 502 pour Shofo et des HTTP 422 pour Lingbow/datasocial. La documentation officielle consultée ensuite documente des prédicats de comparaison, pas `LIKE` : **ces essais ne démontrent pas une absence de contenu ni une interdiction d'accès**.
- Deux recherches `/search` indépendantes, mot `vidange`, limite 20, ont ensuite été tentées sur Lingbow et datasocial. Toutes deux ont expiré après le délai de lecture de 40 secondes. Aucun nouvel essai n'a été lancé.
- Documentation primaire : [filtrer les lignes Hugging Face](https://huggingface.co/docs/dataset-viewer/filter). La recherche de texte est une opération différente des comparaisons filtrées.

## Droits, provenance et utilité à grande échelle

Une licence de dataset ne prouve pas la licence libre de chacune des vidéos ou de leur transcription. Les grands exports constituent des pistes de **découverte**, avec autorisation et provenance à examiner avant réutilisation dans la plateforme publique. Les textes de créateurs, résumés IA et transcriptions ne doivent pas être mélangés. Aucun de ces exports n'est présenté comme un corpus de milliers de tutoriels français vérifiés.

La piste techniquement la plus riche observée est Shofo pour ses URLs et ses légendes séparées ; Lingbow documente mieux les colonnes dérivées. Les deux restent des ressources de recherche, pas une solution prête à publier des milliers de contenus. Pour exploiter un grand export, il manque encore un sous-ensemble récupérable, une qualification sur le texte source, des liens utilisables, des conditions de réutilisation adaptées et une déduplication du catalogue. Les jeux sans permalien ne résolvent pas ce besoin.

## Reproductibilité

Le dossier contient les réponses GitHub/HF, cartes, schémas, projections autorisées et erreurs datées. Les fichiers `*.api.json` fixent les révisions HF ; `crawlora-tree.json` fixe la révision GitHub. Le JSONL Crawlora a pour SHA-256 `d46a72ced4c6c68cf1f4629cdd5124d5cf274a6f3bf14f2a0a50ed06dd3c5915` et la révision `c24e5e1e39e4a99aa2ddc02bb34c0f7e27098b08`.

Les projections n'incluent aucun contenu de commentaire, statistiques de profil, lien média signé, transcription ni résumé IA. Les URLs de vidéos présentes dans les métadonnées n'ont pas été ouvertes. Les scripts de sondage se trouvent dans le dossier parent et n'effectuent aucun import de base.

L'archive OriginalityAI étudiée en parallèle par le parent est une source distincte de **résultats de recherche archivés** ; son rendement n'est pas intégré aux comptages ci-dessus.
