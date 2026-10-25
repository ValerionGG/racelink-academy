# Audit de jeux de données TikTok publics — 25 octobre 2026

## Résultat utilisable pour Racelink

Une nouvelle méthode gratuite fonctionne : lecture HTTP Range des colonnes de métadonnées d'un fichier Parquet public sur Hugging Face, avec plafond réseau. Elle ne nécessite ni compte, ni clé, ni collecte de médias. Le jeu testé ne fournit cependant pas les milliers de tutoriels français recherchés. **Aucun enregistrement de cet audit n'est proposé à la publication.**

### EinzzCookie/tiktok-videos-users-info

Source : <https://huggingface.co/datasets/EinzzCookie/tiktok-videos-users-info>

La fiche actuelle et l'API du Hub indiquent un jeu public, non soumis à autorisation et une licence MIT pour le jeu de données. Cette indication ne transforme pas la licence des vidéos TikTok en MIT. L'auteur demande de créditer EinzzCookie / TikTrack : <https://einzzcookie.org/>.

Mesures réellement exécutées sur les dix groupes du fichier :

| Mesure | Résultat |
|---|---:|
| Lignes Parquet | 950 656 |
| Identifiants vidéo distincts | 6 258 |
| Lignes répétant un identifiant déjà présent | 944 398 |
| Identifiants dont la dernière légende porte `desc_language=fr` | 88 |
| Candidats auto distincts après mots-clés et contrôles de visibilité | 14 |
| Candidats auto français dans cette sélection | 0 |
| Candidats retenus pour publication | 0 |
| Octets reçus pour l'extraction des colonnes utiles | 32 264 100 |
| Octets reçus pour l'audit indépendant des identifiants/langues | 4 909 615 |

Les 88 étiquettes françaises concernent tous les thèmes. `desc_language` décrit la légende selon le fournisseur ; ce n'est pas une vérification de la langue parlée. Le tri automobile est fondé sur des mots-clés français/anglais et des marques : il ne constitue pas une mesure exhaustive de tous les contenus automobiles dans chaque langue.

Les quatorze candidats incluent surtout présentations de voitures, actualités, humour, montage CGI et publicité éditoriale. Une accroche allemande parle de « conseils » sans identifier suffisamment la procédure. Aucun de ces textes n'établit un tutoriel précis à importer. Ils restent dans `einz-automotive-candidates.json` pour audit, hors catalogue.

Les endpoints publics `/rows` et `/splits` fonctionnent. `/search` et `/filter` ont retourné HTTP 500, avec un message d'échec temporaire de vérification interne sur le Hub. Aucune authentification n'a été tentée. La lecture des colonnes par HTTP Range a ensuite réussi ; le fichier complet de 3,87 Go n'a pas été téléchargé. Chaque réponse devait être un HTTP 206 de taille exacte ; le script refuse une réponse contenant le fichier complet.

### Autres pistes vérifiées

| Source | Vérification | Décision |
|---|---|---|
| [datasocial/tiktok-5.6B-videos](https://huggingface.co/datasets/datasocial/tiktok-5.6B-videos) | Public, 5 598 141 717 lignes affichées, environ 460 Go, captions/hashtags/langue/ID. Licence actuelle CC BY-NC 4.0 ; la fiche renvoie les usages commerciaux vers le fournisseur. Petit test de filtre : HTTP 500. | Pas d'import dans le produit ; pas une source commerciale librement réutilisable établie. Aucun téléchargement massif. |
| [Shofo/shofo-tiktok-general-small](https://huggingface.co/datasets/Shofo/shofo-tiktok-general-small) | La fiche actuelle indique `license: other` et réserve l'usage à la recherche et à l'expérimentation. Un résultat de recherche portant sur une ancienne révision annonçait MIT. | Ne pas reprendre l'ancienne licence ; aucun import. |
| kuben-developer/tiktok-videos-4b | API et fiche : HTTP 401. | Arrêt ; aucun accès restreint ni contenu téléchargé. |
| [openinterx/UGC-VideoCap](https://huggingface.co/datasets/openinterx/UGC-VideoCap) | Public, MIT déclaré, benchmark de 1 000 vidéos UGC généralistes. | Pas une source massive de tutoriels auto français ; métadonnées de présentation seulement consultées. |
| [EinzzCookie/TikTok-Video-User-Data](https://huggingface.co/datasets/EinzzCookie/TikTok-Video-User-Data) | Public, MIT, jeu de reposts annoncé 1–10k, fichiers vidéos/auteurs séparés. | Fiche seulement consultée ; aucun volume auto FR établi. |

## Fichiers et reprise

- `einz-id-quality-audit.json` : décompte distinct global et par groupe, langues, empreintes de chaque plage HTTP.
- `einz-parquet-audit.json` : colonnes, nombre de groupes lus, plafond réseau et empreintes des plages de l'extraction.
- `einz-automotive-candidates.json` : métadonnées minimales des quatorze candidats non publiés ; aucune adresse CDN, aucun profil complet, aucun média.
- `remote_parquet_probe.py` : prototype borné à 128 MiB pour ce fichier public et ce schéma. L'URL et la taille sont vérifiées à partir du manifeste public `einz-parquet-list.json`. Ce prototype ne remplace pas la qualification éditoriale.
- `audit_einz_ids.py` : audit distinct indépendant, lecture des seules colonnes ID/langue.
- `dataset-checks.json` et fichiers de fiches : preuves des licences et états d'accès au moment de la vérification.

La bibliothèque PyArrow a été installée dans le sous-dossier local `.deps` de cette recherche. Les scripts utilisent Python 3.12 (`py -3.12`) ; aucun paquet global n'a été modifié. Ce sous-dossier n'est pas un livrable public et ne doit pas être ajouté au paquet de l'application.

Les statuts de visibilité sont ceux du cliché fourni par le dataset ; l'accès actuel sur TikTok n'a pas été confirmé. Aucun contenu n'a été regardé, transcrit ou présenté comme une procédure officielle. Aucune écriture dans la base Racelink, aucun commit Git, aucun paiement, aucune ouverture de compte.
