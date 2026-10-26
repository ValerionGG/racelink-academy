# Validation V30 — bibliothèque, cartes et filtres

**182 contrôles automatiques réussis**, plus contrôle de syntaxe des modules JavaScript. [Résultats et empreintes](checks.json).

- Cartes et lecteurs vidéo, cartes de guides : 58 contrôles. Échappement des textes, liens autorisés, sauvegarde, trois langues, sources constructeur, légende originale et absence de lecteur chargé automatiquement.
- Navigation : 17 ; collections d’accueil : 20 ; thèmes : 36.
- Brouillon des filtres : 14 ; références constructeur : 10 ; contenu social : 7 ; sélections RaceLink : 6 ; structure HTML/imports/bundle : 14.

Les tests utilisent les modules réels, des doubles DOM et des guides sources réels. Ils vérifient notamment l’application unique des filtres, l’annulation à la fermeture et le maintien de la langue et du véhicule. Les contrôles HTML valident les IDs, liens de libellés et l’entrée CSS générée. Ils ne constituent pas un audit d’accessibilité exhaustif.

**Contrôle visuel indisponible** : le navigateur intégré n’a pas attaché l’aperçu. Aucun rendu V30 à 320, 390, 768 ou 1440 px n’a été inspecté. Les règles responsive et leur héritage ont été relus, mais cela ne prouve pas leur rendu dans un navigateur ni sur un appareil réel. Les captures des anciennes versions ne sont pas utilisées comme preuve V30.

## Catalogue : fonctionnement et limite de mesure

Le Worker ES module exporté a été exécuté par ses vraies routes, avec lecture locale contrôlée des fichiers statiques : **39 469 ressources et 287 nouvelles références vérifiées** contre le lot approuvé. Quatre recherches françaises ciblées passent : filtre habitacle Clio IV, bougies Clio III 1.4 16V, ampoules Peugeot 206 et courroie Peugeot 207 1.6 HDi. Pagination courroies Peugeot : 9 résultats sur 3 pages, 6 nouvelles références et aucun doublon. Quatre combinaisons de filtres incompatibles renvoient zéro résultat ; quatre fiches conservent titre, description, langue estimée, tâches et véhicules cités, sans transcription inventée. Ces vérifications sont comptées séparément des 182 contrôles UI.

**Diagnostic Node uniquement, pas un temps de chargement navigateur.** Sur Windows / Node.js v24.16.0, sans précharger une seconde copie du catalogue, le chemin gzip via Web Streams prend 65,8 s, puis l’indexation 2,18 s. Le JSON direct prend 1,08 s, puis 1,80 s d’indexation. Une variante privée du flux prend 20,66 s ; la décompression native de diagnostic prend 0,28 s, le décodage UTF‑8 0,12 s et le parsing JSON 0,76 s. La lecture du fichier gzip ne prend que 10 ms. L’attente observée se situe donc dans le chemin gzip / Web Streams de cet environnement Node ; la cause interne exacte et les performances du navigateur ne sont pas établies.

Le préchargement du vérificateur augmente la mémoire avant Worker de 60 à environ 345 Mo RSS, mais ne suffit pas à expliquer cette attente : le JSON direct reste bien plus rapide avec cette copie supplémentaire. Ces mesures isolées ne constituent pas un benchmark comparatif reproductible. **Aucun changement de décompression ni de moteur n’a été livré**, et aucun polyfill natif Node n’a été ajouté au site. Les scripts fonctionnels et rapports détaillés de diagnostic restent dans le dossier de travail privé.

## Changements

Recherche avant les sélections, rail de navigation desktop, panneau véhicule, cartes photographiques avec une cible d’ouverture, filtres latéraux sur grand écran et brouillon dans le panneau mobile. Les fiches commencent par la vidéo et regroupent la provenance dans des sections dépliables. Les modes clair/sombre et les sources officielles des guides sont conservés.

[Références étudiées](https://valeriongg.github.io/racelink-academy/design-sources.md) · [Ouvrir l’aperçu](https://valeriongg.github.io/racelink-academy/?release=studio-v30)
