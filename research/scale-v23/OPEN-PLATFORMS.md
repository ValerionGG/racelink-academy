# Collecte publique Dailymotion, PeerTube et Vimeo — 24 octobre 2026

Le lot figé contient **304 références candidates sur métadonnées**, dont **291 nouvelles identités** comparées au catalogue SQLite en lecture seule : 277 Dailymotion et 14 PeerTube. Parmi les nouvelles références, **167 ont une langue française déclarée par la plateforme**. Cela ne prouve pas la langue audio. Aucune vidéo n’a été visionnée ou téléchargée et aucune procédure n’est certifiée par ce travail.

## Livraison

- `final-v3/normalized-candidates.json` : 304 records au schéma `server.normalize_item`, tous validés hors import ; 13 existent déjà dans le catalogue.
- `final-v3/new-candidates.json` : 291 identités nouvelles seulement.
- `final-v3/manifest.json`, `qualification-report.json` et `source-manifest.json` : compteurs, empreintes et provenance des pages.
- `quarantine.json` : 13 189 identités non retenues pour ce périmètre ou insuffisamment explicites. Ce classement n’est pas un jugement sur leur qualité intrinsèque.
- `raw/dailymotion/`, `raw/peertube/` : réponses publiques de métadonnées, avec URL de requête et date. Aucun média ni commentaire récupéré.
- `peertube-direct-checks.json` : quatre vérifications natives HTTP 200, avec projection des seuls champs de publication utiles ; aucune URL de flux vidéo conservée dans cette projection.
- Les plans, journaux et scripts restent à côté pour la reprise. Ne pas envoyer ce lot à l’adaptateur `bulk_ingest` YouTube/TikTok/Instagram : ces records sont déjà normalisés et gardent leur vrai fournisseur.

Empreinte SHA-256 du lot complet : `2b0874288a4079c013299c1c359964d5c58648e9ad67278a18475b76e0301207`.

Empreinte SHA-256 des nouvelles références : `641409bc5a5903e6180cf4241a81b48bcafb40df8ee8cfa08d935a51682195e3`.

## Rendement constaté

| Étape | Résultat réel |
|---|---:|
| Pages Dailymotion conservées | 162 HTTP 200 |
| Lignes Dailymotion | 15 438 |
| Pages PeerTube conservées | 17 HTTP 200 |
| Lignes PeerTube | 1 086 |
| Total de lignes avant dédoublonnage | 16 524 |
| Identités découvertes | 13 493 |
| Candidats après tri | 304 |
| Candidats Dailymotion / PeerTube | 290 / 14 |
| Nouvelles identités / existantes | 291 / 13 |
| Français déclaré, lot complet / nouvelles | 179 / 167 |
| Métadonnées de véhicule / tâche extraites | 124 / 173 |
| Références techniques explicites extraites | 1 |

Le total des requêtes de métadonnées est **186** : 162 pages et une sonde Dailymotion ; 15 recherches, deux listes de chaîne, quatre fiches natives et une sonde PeerTube ; une sonde Vimeo. Les consultations documentaires et le diagnostic Agent Reach sont séparés. Les sondes déjà représentées dans les listes ne sont pas ajoutées aux volumes de vidéos.

Le corpus retenu contient 294 sujets de mécanique, six de conduite/pilotage et quatre de simulation. La recherche libre Dailymotion renvoie beaucoup de correspondances sur des mots isolés : actualités, musique, sport, jeux et objets domestiques. Les milliers de résultats bruts ne constituent donc pas des milliers de tutoriels. Les listes d’auteurs observés dans ces résultats améliorent la précision, mais n’ont pas démontré un gisement de milliers de nouvelles procédures pertinentes dans ce passage.

## Méthode et qualification

Agent Reach a été lu avec ses références vidéo, web et GitHub ; le diagnostic des backends a été exécuté. Il n’expose pas ici de collecteur Dailymotion/Vimeo/PeerTube dédié : les routes REST ont été vérifiées dans les documentations primaires, puis appelées directement, sans identifiant. Exa et les accès natifs Instagram/TikTok précédemment limités n’ont pas été utilisés.

Dailymotion : 60 recherches diversifiées, deux pages maximum de 100 résultats, puis 13 auteurs identifiés par leurs publications. Chaque liste d’auteur est bornée à dix pages de 100. Une recherche supplémentaire AUTODOC s’est terminée à 12 résultats, sans prolongement artificiel. L’intervalle minimum entre les départs est de 1,5 seconde, sans concurrence sur le fournisseur. Les réponses sont mises en cache par empreinte d’URL ; le journal indique les pages et la fin bornée. Les statuts 401/403/429 déclenchent un fichier de pause et arrêtent les appels suivants ; aucun de ces statuts n’a été rencontré sur la route Dailymotion utilisée.

Les titres doivent montrer une intervention, un apprentissage ou une explication technique et un objet automobile précis. La revue a retiré notamment produits à vendre, annonces et actualités, tours de circuit sans leçon, extraits amusants, motos hors périmètre de cette collecte, bricolage domestique et méthodes demandant une revue technique. Les verbes de pose/dépose ont aussi été retenus pour les titres techniques explicites de la chaîne « Tuto Mercedes » ; ce nom de chaîne n’est pas présenté comme une certification constructeur.

Les 304 titres finaux ont été relus pour leur pertinence. Quelques descriptions natives ont été examinées pour résoudre des ambiguïtés, par exemple une suspension BMW qui concernait une moto et un outil OBD vendu avec remise. Cette revue porte sur les métadonnées, jamais sur la démonstration vidéo. La contrelecture indépendante du backend a retiré six références commerciales ou ne démontrant pas une procédure. La revue UX de 53 entrées a entraîné sept retraits supplémentaires : explication incohérente, compatibilité universelle non établie, légende contradictoire ou promotion seule. Le snapshot initial de 317 reste dans `final/` ; utiliser exclusivement la révision `final-v3/` pour la suite.

`automotive.extract_automotive(title)` utilise **le titre uniquement**, jamais la requête ni l’URL de recherche. Les champs d’origine, les extraits et les empreintes des sources restent disponibles dans `provenance`. Les descriptions affichables sont des extraits de légendes sources identifiés comme tels, sans résumé inventé. Aucune nouvelle transcription n’est produite.

## État des plateformes et sources primaires

### Dailymotion : voie publique exploitable, historique v0

La [documentation des appels v0](https://developers.dailymotion.com/v0/reference/perform-an-api-call) décrit `GET https://api.dailymotion.com/videos` et `GET /user/{id}/videos`. Le [guide de migration officiel](https://developers.dailymotion.com/docs/migrating-from-legacy-api-to-api-v2) confirme ces routes historiques et leurs équivalents v2. Le [guide de collecte des IDs](https://developers.dailymotion.com/me/v0/docs/collect-your-video-ids) documente la liste des publications d’un utilisateur.

Ces appels ont réellement répondu HTTP 200 sans jeton pendant cette collecte. Cela ne garantit pas leur pérennité : l’API v2 est désormais documentée séparément et les règles d’accès peuvent évoluer. Aucun appel n’a demandé de champ privé, de lien de téléchargement ou de flux vidéo. Les champs `private=false` et `published=true` sont exigés pour retenir une référence.

### PeerTube : petit volume, cours utiles et provenance plus précise

La [référence REST PeerTube](https://docs.joinpeertube.org/api-rest-reference.html) documente recherche, fiches et publications des chaînes. La [configuration officielle](https://docs.joinpeertube.org/admin/configuration) désigne `search.joinpeertube.org` comme index global. Les 15 recherches bornées ont été suivies de deux listes natives de chaînes scolaires, et quatre fiches ont été revérifiées auprès de leur instance d’origine.

Les 14 références retenues comprennent des travaux pratiques de pneumatiques/freinage et des tutoriels sur l’outillage, le levage, la vidange, l’alternateur, le démarreur, la courroie et le fonctionnement du diesel. Le profil de la vidéo doit être public et non diffusé en direct. La plateforme du catalogue reste `other`, le fournisseur PeerTube étant explicitement enregistré dans la provenance.

Les labels de licence natifs sont conservés (`Attribution`, `Attribution - Non Commercial`, `Public Domain Dedication` ou inconnue), mais **le champ de licence normalisé reste `unknown`** : aucune version ni URL juridique précise n’a été déduite du seul entier de l’API. Les labels NC ne deviennent pas « libres pour tout usage ». Aucune légende ou vidéo n’est autorisée à une réutilisation intégrale par cette collecte.

### Vimeo : accès non disponible sans jeton

La [documentation d’authentification](https://developer.vimeo.com/api/authentication) demande un jeton d’application, y compris pour l’accès API aux données publiques. La sonde unique `GET /videos?query=car%20repair&per_page=1` a répondu **401, code 8003**, faute d’identifiants. Elle n’a pas été répétée. Les [règles Vimeo](https://developer.vimeo.com/guidelines/rate-limiting) renvoient à l’API et excluent le scraping du site ; aucun repli de ce type n’a été tenté.

## Reprise et limites

Les scripts de collecte ne modifient aucune base. `prepare_candidates.py` ouvre le catalogue existant en `mode=ro`, déduplique les identités et URLs canoniques puis vérifie chaque record avec `normalize_item`. Il produit des candidats, pas une approbation d’import. Le dossier `final-v3/` est un snapshot figé : une nouvelle collecte ou une nouvelle revue doit produire une nouvelle livraison.

Pour reprendre les plans existants sans répéter leurs pages, exécuter les scripts depuis le même dossier de travail ; les fichiers de pause doivent rester respectés. `collect_open.py` exige `--execute`; les petits scripts de collecte complémentaires s’exécutent explicitement lorsqu’on les lance. **Ne pas lancer tous les scripts en parallèle** : ils partagent la limite fournisseur. `prepare_candidates.py` est entièrement hors réseau.

Les listes sont bornées, ne prouvent ni l’exhaustivité des chaînes ni l’absence de doublons de contenu entre plateformes. Une identité distincte désigne une publication distincte, pas forcément une vidéo originale différente. La disponibilité d’un lien et une langue déclarée ne garantissent ni la qualité technique ni la licence de la vidéo. La voie réellement exploitable ici enrichit le catalogue de quelques centaines de références ; les milliers de candidats pertinents demanderaient davantage de créateurs pédagogiques identifiés et un tri supplémentaire, sans promesse de volume.

Agent Reach installé : v1.5.0 ; `check-update` annonce v1.6.0. Aucune mise à jour ni installation n’a été exécutée.
