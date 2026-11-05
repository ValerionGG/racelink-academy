# Collecter le catalogue public d’un créateur autorisé

`creator_api_pages.py` ajoute la pagination réseau qui manque à l’adaptateur local `public_export.py`. Il ne nécessite aucun fournisseur de scraping. Pour TikTok, l’application doit avoir l’accès Display et le créateur doit lui avoir accordé `video.list`. Pour Instagram Login, l’application doit disposer d’un accès autorisé en lecture au compte professionnel concerné. Un jeton de session de navigateur n’est pas un jeton d’application. Aucun utilisateur n’est inscrit ni contacté par ce programme.

Depuis le dossier de l’application ou du collecteur :

```powershell
python scripts/creator_api_pages.py tiktok nom_du_createur --max-pages 250
python scripts/creator_api_pages.py instagram nom_du_createur --account-id 123456789 --graph-version v23.0 --max-pages 250
```

Ces exemples prévisualisent sans réseau ; la version de Graph est illustrative et doit être celle prise en charge par l’application Meta. Pour une campagne autorisée, fournir au processus `RACELINK_TIKTOK_CREATOR_TOKEN` ou `RACELINK_INSTAGRAM_CREATOR_TOKEN`, ajouter `--execute --pages-per-run 2 --output chemin/prive/lot`. Ne pas fournir le jeton en argument, le committer, ni le transmettre dans un message. Les deux routes sont en lecture de métadonnées ; le script ne demande pas la permission de publier. Aucun jeton réel n’a été utilisé pour valider cette livraison.

Une page contient au plus 20 médias ; une campagne de 250 pages peut **examiner au plus 5 000 lignes**, si le compte, son historique accessible et son quota le permettent. Les photos et carrousels Instagram ne comptent pas comme Reels. Les doublons et les entrées non pédagogiques ne sont pas des ajouts. Le chemin d’une publication et son auteur doivent correspondre au profil visé. Le programme n’enregistre pas les URL de pagination du fournisseur, les URLs de fichiers vidéo, les statistiques de personnes, les cookies ou les jetons. Il ne consulte pas les API privées.

Reprendre le même dossier et le même plan après un lot réussi. Une limite, erreur, interruption ou incohérence persistante laisse un marqueur `in-flight` : arrêter et réconcilier avant toute nouvelle requête. Après chaque lot, `manifest.json` et les pages minimales sont compatibles avec `python scripts/public_export.py chemin/prive/lot/manifest.json --output chemin/prive/revue`. Utiliser un nouveau dossier de revue si le manifeste a grandi. Les fiches restent privées jusqu’au contrôle des antécédents, du sujet, de l’identité et des preuves automobiles. Un nom de voiture dans le profil, le commentaire d’un tiers ou une langue d’interface ne suffit pas.

Sources : [TikTok Display API](https://developers.tiktok.com/docs/en/display-api-get-started), [List Videos](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-list), [champs vidéo](https://developers.tiktok.com/docs/en/tiktok-api-v2-video-object), [collection officielle Meta](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api), [SDK Meta sur GitHub](https://github.com/facebook/facebook-python-business-sdk). Meta documente aussi la découverte de comptes professionnels via Facebook Login et une Page liée. Cette autre route n’est pas implémentée ici et ne couvre pas les comptes personnels.
