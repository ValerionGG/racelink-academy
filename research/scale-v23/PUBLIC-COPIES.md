# Copies publiques des preuves

Les chemins absolus de la machine et les répertoires utilisateur sont expurgés dans ces copies. Les sources privées de travail ne sont pas modifiées. Les marqueurs `[WORKSPACE]` et `[USER_HOME]` désignent les chemins retirés ; ils ne sont pas des chemins exécutables.

`public-copy-manifest.json` conserve pour chaque copie l'empreinte SHA256 des octets originaux et celle des octets publics. Les SHA présents dans les manifestes de preuve historiques restent les SHA des sources originales : si une copie a été expurgée, son empreinte publique peut donc différer. La copie d'access-required.json est également alignée sur le pilote réel de 14 lots ; cette correction éditoriale est marquée séparément dans le manifeste. Ce traitement n'atteste pas l'absence exhaustive de secrets ; seules les preuves et entrées explicitement prévues sont copiées, sans environnement, identifiants, base ou cache brut de collecte.

Les scripts de tests copiés utilisent une résolution locale du paquet, sans chemin utilisateur. Les tests de build statique ne font pas partie du paquet collector. Les échantillons de qualification sont des fixtures temporaires, pas de nouvelles vidéos publiées.
