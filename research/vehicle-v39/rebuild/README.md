# Reconstruire la maquette de la Clio V phase 2

Le générateur dessine les volumes pédagogiques de la Clio 5 restylée, leur applique les matériaux et les regroupe pour le moteur 3D de RaceLink. Il conserve les formes modélisées des vitrages, du pavillon et des montants dans des groupes que le visualiseur peut masquer pour ouvrir l’habitacle. Les angles de caméra et les huit images de repli sont dans [le visualiseur de cette fiche](../../../site/clio-v/model/).

La construction publiée utilise Node 24, Python 3.11, Three.js 0.180.0, gltfpack 0.24.0, NumPy 2.4.3 et Pillow 12.3.0. Depuis une copie de ce dossier, exécuter les commandes suivantes dans un environnement Python virtuel.

```sh
npm ci --ignore-scripts
python -m pip install -r requirements.txt
npm run model
python finish.py
```

Le fichier final est `build/deliver/clio-v.glb`. Le fichier intermédiaire `build/clio-raw.glb` est plus volumineux. Chaque exécution remplace seulement les produits de construction de ce dossier. Three.js et gltfpack sont sous licence MIT. Le panorama de réflexion et l’ombre de contact sont calculés localement.

Les coordonnées sont en mètres. Le sol est à Y = 0 et l’avant est dirigé vers Z positif. Les deux essieux ont pour abscisses longitudinales −1,3895 et +1,1935. Le dessin part de 4,053 m de longueur et de 2,583 m d’empattement publiés dans la brochure du véhicule. Les courbes de tôle, les volumes intérieurs et les positions des commandes sont des approximations originales. Les organes mécaniques internes n’ont pas été reconstitués.

Pour une autre voiture, rechercher d’abord la génération, la phase, le marché et les dimensions documentées. Remplacer les profils de capot et de pavillon, le contour des ouvrants, les surfaces de feux et l’implantation intérieure en se fondant sur ses propres documents. Vérifier visuellement la silhouette, les vitres, le tableau de bord et les huit angles en regard de photographies du bon modèle avant de publier. Le changement d’intitulé ou d’empattement d’une maquette existante ne suffit pas à reproduire un autre véhicule.

[Présentation et photographies de Renault, 18 avril 2023](https://media.renault.com/nouvelle-renault-clio-la-reference-des-citadines-polyvalentes-inaugure-un-nouveau-style/?lang=fra) · [Brochure Renault BJABR23F07, dimensions page 16](https://www.fiches-auto.fr/catalogues-pdf-officiels/637-Clio-5-03_06_2024-clio-5-restylee.pdf)
