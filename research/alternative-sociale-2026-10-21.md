# Nouvelle voie de collecte sociale — 21 octobre 2026

**Résultat de cette itération : 7 nouvelles références TikTok, dont 2 estimées françaises sur le texte source. Aucun ajout Instagram.** Le catalogue passe à **36 901 vidéos**, dont **166 TikTok et 140 Instagram**, et 11 guides. **L’objectif de milliers de nouveaux tutoriels TikTok/Instagram n’est pas atteint.**

## Solution effectivement construite

- `scripts/creator_site_collect.py` : relève les permaliens TikTok/Instagram publiés sur les sites des créateurs, avec le libellé exact et l’empreinte de la page. Le périmètre est une liste de pages autorisées et bornée ; les liens sociaux ne sont pas suivis. Les sorties sont des candidats à relire.
- `scripts/public_export.py` : prépare des lots JSON, JSONL ou CSV, y compris les pages exportées de TikTok Display et Meta Graph. Vérification des empreintes, limites de volume, dédoublonnage, conservation de la provenance, titre/légende/hashtags séparés et quarantaine des cas ambigus. Aucun accès à un compte n’est créé par cet outil.
- Le paquet exécutable est publié dans [collector/ sur GitHub](https://github.com/ValerionGG/racelink-academy/tree/main/collector). La préparation est locale et sans écriture dans la base ; l’application reprend la revue et l’import existants.

## Ce qui a réellement fourni les ajouts

1. **Le site propre d’un créateur** : [Younès Pratik](https://younespratik.fr/) associe un vrai lien TikTok au sujet « Mise à jour GPS VW gratuite ». Nous conservons le sujet GPS VW ; aucun modèle ou moteur cité dans un article voisin n’est attribué à la vidéo.
2. **Une archive GitHub préexistante** : [OriginalityAI/ai-citation-study](https://github.com/OriginalityAI/ai-citation-study/tree/58302b1ceff367804d500f62dbe847a4c657dbe9) contient des résultats de recherche. 60 fichiers ciblés ont produit 34 résultats sociaux / 33 identités ; revue : 7 références retenues, dont 1 déjà présente, soit 6 ajouts. Les extraits composites ne deviennent jamais des légendes. Seuls les liens et titres pertinents sont référencés, pas une republication du dataset.

Les ajouts couvrent l’embrayage, les grades d’huile Toyota Revo, l’outillage, le joint de culasse, le coût d’entretien de transmission et le GPS Volkswagen. Deux fiches ont des mentions de véhicule et cinq un filtre d’intervention. Les sujets de coûts n’affichent aucun montant actuel ni tarif français supposé. Les formats non démontrés restent indéterminés.

Les 7 références reposent sur 6 titres archivés et 1 libellé de lien publié par le créateur. Aucune nouvelle légende native, transcription, langue audio confirmée, licence libre ou recommandation RaceLink n’est revendiquée. Les 36 894 fiches antérieures et leurs relations de recherche sont conservées.

## Autres solutions trouvées et vérifiées

| Solution | Résultat de l’examen | Condition pour la suite |
|---|---|---|
| [Crawlora : TikTok engagement data](https://github.com/Crawlora-org/tiktok-engagement-data) | 4 509 lignes réellement comptées ; ni titre ni légende. Zéro candidat qualifiable. | Ne pas transformer le mot-clé de collecte en sujet de vidéo. |
| [TikHub : plugin et skills](https://github.com/TikHub/tikhub-plugin) / [SDK Python](https://github.com/TikHub/TikHub-API-Python-SDK) | Nouvelle alternative GitHub identifiée. La [marketplace](https://tikhub.io/datasets) annonce des datasets précollectés et un aperçu de 300 lignes. L’accès à l’aperçu redirige effectivement vers une connexion. | Compte nécessaire ; couverture automobile française encore non mesurée. Tarif publié : 2 $ / 1 000 lignes, **minimum 150 $ par commande**. Aucun achat ni création de compte réalisé. Un nombre de lignes n’est pas un nombre de tutoriels retenus. |
| [Supadata : skill vidéo](https://github.com/supadata-ai/skills/blob/main/skills/supadata/references/video.md) | Métadonnées et transcription à partir d’une URL connue, avec clé API. | L’endpoint social documenté ne fournit pas une recherche exhaustive de nouveaux tutoriels. |
| [Bobine](https://github.com/wrouhli/bobine) | Bibliothèque locale depuis des vidéos sauvegardées/exportées par l’utilisateur. | Utile pour une collection déjà possédée, pas une source publique de milliers de nouvelles vidéos. |
| Grands exports Hugging Face | Neuf sources examinées : cartes, schémas, petits aperçus ou fichier complet Crawlora. Aucun nouveau sous-ensemble qualifié. Plusieurs licences sont limitées à la recherche/non-commercial ; d’autres tables manquent de permaliens ou de légendes. | Obtenir un export pertinent, attribuable et utilisable dans la plateforme avant publication. Détails dans `datasets-alternatifs-2026-10-21.md`. |

Agent Reach **1.5.0** est à jour. Sa route GitHub fonctionne via `gh` ; l’extension Instagram n’est pas connectée. Exa reste au quota atteint et vidIQ dispose de 4 crédits pour une recherche coûtant 5. Aucun accès natif refusé n’a été relancé par un autre extracteur.

## Prochaine étape pour un vrai lot de 5 000

La chaîne d’import est prête ; **il manque la source de données accessible**. Deux entrées possibles : un export de publications fourni par des créateurs, ou un export de fournisseur obtenu avec les accès et conditions appropriés. Un pilote ciblé doit mesurer le nombre de vraies références auto en français avant une commande plus importante. Le nouvel adaptateur traite des milliers de lignes ; ses données de test synthétiques ne sont jamais comptées ni publiées comme vidéos.
