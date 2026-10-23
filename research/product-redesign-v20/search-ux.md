# V20 — refaire la recherche, les filtres et les fiches

23 octobre 2026. Audit et proposition indépendants. Aucun frontend, catalogue ou état Git modifié.

## Problème à résoudre

**La V19 change l’accueil mais conserve le parcours de consultation précédent.** Sur `mobile-results-final.png`, la recherche « vidange Clio 3 » en français produit deux vidéos ; pourtant aucune photo de résultat n’apparaît au premier écran. Avant elle s’empilent : titre générique, champ, langue, voiture, formats, nombre de résultats, tri, interprétation, filtres actifs et guide conseillé. La bonne réponse est retardée par l’explication du moteur de recherche.

La feuille de filtres commence par neuf choix de sujet, dont sept à zéro dans cette recherche, avant d’atteindre le niveau et la plateforme. La voiture, pourtant centrale pour cette tâche, est une sortie distincte au pied de la feuille. La carte vidéo décrit surtout une ressource et ses classifications ; le lecteur présente le bloc de lecture avant son titre et répartit le contexte entre plusieurs endroits.

**Objectif de V20 :** poser une question, préciser éventuellement une voiture et une langue, puis comparer immédiatement des ressources dont on comprend l’objet et l’origine. La refonte doit être visible dans les trois surfaces, sans réduire les grandes photos.

## Sources inspectées

- Captures V19 réellement ouvertes : `mobile-results-final.png`, `mobile-filters.png`, `mobile-search.png`, `mobile-reader-final.png`, `mobile-guides-final.png`, sous `outputs/focus-academy/research/graphic-redesign-v19/`.
- Code : `public/app.js` (`syncControls`, `cardMarkup`, `loadVideos`, `renderActiveFilters`, `openVideo`, `setDetailTab`), `public/index.html` (catalogue et filtres), `public/mobile-ui.js`, `public/product-ui.css`. Lecture complémentaire du rendu des mentions véhicule dans `automotive-ui.js`.
- Impeccable, registre produit, déjà lu : hiérarchie de tâche, divulgation progressive, contrôles familiers, états explicites. Aucun nouveau thème ni mouvement décoratif proposé.
- Trois sources primaires web lues le 23 octobre : iFixit, AUTODOC Club et l’aide YouTube. Observation de leur contenu HTML/documentation, **pas d’audit visuel de ces sites**.

## Sept décisions concrètes

### 1. Un seul bloc de recherche, organisé autour de trois questions

**Visible par défaut :** « Que cherchez-vous ? », puis deux contrôles courts « Voiture » et « Langue ». Le champ reste un vrai champ de recherche ; la voiture et la langue sont des paramètres de ce même contexte. Le titre « La bibliothèque » devient secondaire sur les résultats et ne consomme plus sa propre grande rangée mobile.

Desktop : champ large, contrôles voiture/langue voisins ou juste en dessous selon largeur. Mobile : champ sur une ligne, voiture/langue sur la suivante, sans un encart de 50 px pour chacun. Le libellé du contrôle affiche sa valeur actuelle : « Clio III » ou « Toutes voitures », « Français » ou « Toutes langues ».

La question possède son bouton d’effacement. Ne pas la répéter dans un badge supprimable puis dans le total. De même, ne pas afficher la langue dans un select et dans une seconde puce identique.

**Réutilisation :** mêmes `#search`, `#search-form`, paramètres `q`, `language` et véhicule. Un seul formulaire déplacé entre surfaces ; pas de duplication d’identifiants. La langue de l’interface reste indépendante.

### 2. La voiture est un contexte progressif, pas un formulaire permanent

Ouvrir « Voiture » montre d’abord marque puis modèle, avec recherche dans les options disponibles. Génération, année et moteur apparaissent dans un second niveau « Préciser la version ». Ne pas imposer ces détails pour chercher un sujet général.

Une voiture reconnue dans la question et une voiture choisie dans les filtres restent distinguées. La première est une interprétation ; la seconde est un choix explicite. Le moteur ne doit pas transformer silencieusement « Clio 3 » en promesse de compatibilité. En cas de conflit, afficher un message visible et actionnable près du contrôle, même si les explications habituelles sont repliées.

Après validation, refermer le panneau et restituer le focus au contrôle. La valeur courte demeure dans la barre. « Retirer la voiture » retire les paramètres dépendants ensemble, sans effacer question et langue. Préserver les relations marque/modèle/moteur déjà implémentées.

### 3. Un panneau de filtres commun à desktop et mobile

**Supprimer la colonne de filtres permanente.** Les résultats gagnent sa largeur ; le même bouton « Filtres » ouvre un panneau à droite sur desktop et une feuille native sur mobile. Ne conserver qu’un exemplaire des contrôles, comme le mécanisme existant le permet déjà.

Organiser les filtres par décisions utiles :

1. **La ressource** : durée, type de vidéo, niveau lorsqu’il est renseigné.
2. **La source et le texte** : plateforme, transcription disponible, licence libre confirmée.
3. **Affiner le sujet** : discipline et contexte ; ouvrir ce groupe seulement si nécessaire.

La voiture/langue restent accessibles depuis leur contexte principal ; ne pas obliger à traverser la liste de sujets pour les atteindre. Les options à zéro ne dominent plus le panneau : les choix possibles passent d’abord, les autres se replient derrière « Autres sujets ». Une option déjà sélectionnée et désormais à zéro doit rester visible et retirable.

Le bouton de pied garde la sémantique réelle : avec les changements immédiats actuels, **« Voir N résultats »**, pas « Appliquer » si les filtres ont déjà été appliqués. Fermer ne doit pas prétendre annuler. Afficher le nombre actualisé seulement pour la dernière requête terminée, sinon un état de chargement. Compter uniquement les filtres additionnels dans le badge du bouton, ou annoncer clairement qu’il comprend aussi voiture/langue.

### 4. La première ressource avant l’explication du classement

Ordre visible après le bloc de recherche :

```text
Tout | Vidéos | Guides                       Filtres
2 résultats                               Pertinence
[grande photo de la première ressource]
```

L’interprétation et le guide général conseillé deviennent un seul élément compact **« Comprendre ces résultats »**, replié par défaut. Il peut se placer sous le total si sa hauteur reste celle d’une ligne ; le guide développé ne doit pas empêcher de reconnaître les premières ressources. Une autre option est de proposer le guide après la première carte.

Supprimer les doublons de contexte au lieu de réduire toute la typographie. Garder une seule ligne de puces pour les filtres supplémentaires réellement actifs : durée, source, transcription… Chaque puce retire un critère clairement identifié.

**Exception importante :** conflit voiture/question, recherche élargie substantiellement ou zéro résultat ne doivent pas être dissimulés dans ce disclosure. Afficher l’avertissement nécessaire à l’interprétation des résultats, sans reproduire tout le vocabulaire interne du moteur.

**Cible de composition à vérifier :** à 390 × 844, la première image commence avant environ 320–360 px du haut, hors état d’erreur ou avertissement important. Ce chiffre est un objectif de dessin, pas une règle WCAG ni une mesure déjà obtenue. À 320 px, accepter le retour à la ligne des contrôles plutôt que du texte minuscule.

### 5. Une carte qui permet de choisir avant d’ouvrir

La « préfiche » est la carte de résultat enrichie, **pas une modale intermédiaire supplémentaire**. Donner à chaque carte quatre zones lisibles :

1. **Grande photo 16:9.** Miniature propre à la vidéo ; photo licenciée du guide. Durée réelle si connue. Éviter d’empiler des badges au-dessus du sujet de l’image.
2. **Sujet + langue**, une ligne courte. La langue estimée reste explicitement marquée. Ne pas répéter « Mécanique », « Mécanique auto » et une longue catégorie quand une seule indication suffit.
3. **Titre et aperçu descriptif attribué.** Titre complet ou intelligible, 20–22 px sur mobile. Une ou deux lignes donnent la portée à partir du résumé ou de la description réellement disponibles. Pour un titre seul, nommer seulement le sujet repéré ; ne pas fabriquer d’étapes, d’outils, de niveau ou d’apprentissage garanti. Un extrait source se présente comme tel. Une absence de description peut rester sans aperçu plutôt qu’être remplie de texte générique.
4. **Auteur/source et action.** Auteur réel, plateforme, puis « Voir la fiche » ; enregistrer reste une commande séparée de 44 px. Si une voiture est citée, afficher « Clio III citée » ou la mention réelle, jamais « Compatible avec votre Clio ».

Les preuves restent proches de ce qu’elles qualifient : « Transcription disponible » uniquement quand elle existe ; sélection RaceLink uniquement selon la sélection réelle ; une langue estimée ne devient pas certaine. Les statuts éditoriaux internes ne prennent pas la place de l’objet de la vidéo.

Desktop : deux grandes colonnes à largeur moyenne, trois uniquement avec une largeur de carte suffisante. Mobile : une photo pleine largeur utile, pas une petite vignette latérale. Guide et vidéo partagent cette ossature, avec leur type et leur CTA distinctifs.

### 6. La fiche devient un écran de décision puis de lecture

Le code actuel place le player avant le titre et éparpille résumé, véhicule et disponibilité du texte. **Nouvel ordre mobile et ordre DOM recommandé :** titre → auteur/source/langue → aperçu du contenu → grande photo/lecteur → informations complémentaires.

À l’ouverture, répondre rapidement à trois questions : **de quoi parle cette ressource, qui la publie, ce qui est réellement consultable ici**. Une action principale selon le cas : « Regarder » charge le lecteur disponible ; sinon « Voir sur TikTok/Instagram/… » ouvre la source. Éviter deux gros boutons qui expriment la même action avec « Voir la source » et « Voir sur la plateforme ».

Desktop : player généreux à gauche et panneau de lecture à droite, mais titre et contexte au-dessus des deux. Mobile : résumé bref avant l’image, puis contenu détaillé. Le texte n’est pas caché derrière un lecteur qui n’a pas encore été chargé.

La section « En bref » réutilise uniquement la matière disponible. La portée véhicule et les limites de compatibilité restent près du contexte automobile. Les détails de collecte/licence se rangent dans « Source et détails », sans disparaître. Les transcriptions disponibles ont un accès direct et leur recherche ; en leur absence, une ligne explicite avec lien source suffit, sans mettre en avant un onglet vide. Les notes personnelles restent accessibles au second niveau.

Ne pas présenter une description comme un résumé du visionnage, ni un résumé comme une transcription. Le guide RaceLink demeure une méthode générale accompagnée de sources constructeur de portée précise.

### 7. Les états utiles font partie de la nouvelle architecture

**Zéro résultat :** proposer d’abord l’action la plus limitée et intelligible : retirer l’année, retirer le moteur, élargir la langue ou supprimer un terme. L’action expose exactement ce qu’elle change et conserve les autres critères. « Tout réinitialiser » reste disponible, mais n’est plus la seule grande issue.

**Chargement :** conserver les dimensions des cartes précédentes ou des squelettes, un seul statut près du total, pas de saut vers le haut à chaque filtre. La dernière réponse gagne ; les réponses obsolètes ne doivent pas réécrire le résultat courant.

**Retour de fiche :** retrouver les mêmes critères, le même scroll et la carte ouverte ; focus restauré sur son bouton. Une fiche ouverte depuis une suggestion ne rouvre pas automatiquement la feuille de recherche.

**Recherche élargie :** une formulation courte et visible explique quand des équivalents techniques ont été employés. Un nombre de résultats ne garantit ni contenu pédagogique vérifié ni compatibilité mécanique.

## Benchmark primaire : ce qui est retenu, et ce qui ne l’est pas

| Source lue | Observation factuelle | Application proposée à RaceLink |
|---|---|---|
| [iFixit — Repair Guides](https://www.ifixit.com/Guide) | La page mène par une question sur l’objet à réparer puis des familles d’objets ; les guides restent nommés par l’intervention. | Commencer par la question ou l’objet, pas par une classification interne. Faire du véhicule un contexte progressif. Ce n’est pas une copie de mise en page. |
| [AUTODOC Club — Manuels et tutoriels](https://club.auto-doc.fr/manuals) | L’entrée de recherche présente constructeur, modèle et catégorie de pièce ; les ressources nomment l’intervention et le véhicule. | Associer besoin et voiture avant les filtres de source. Garder les mentions explicites dans la carte. RaceLink ne possède pas les garanties de compatibilité de toute source tierce et ne les reprend pas. |
| [Aide YouTube — Recherche avancée](https://support.google.com/youtube/answer/111997?hl=fr) | La documentation décrit la saisie d’une recherche, puis l’ouverture des filtres sur la page de résultats, dont le type de contenu. | Afficher les ressources d’abord, réserver les options à un panneau explicite ; conserver Tout/Vidéos/Guides comme choix court. Aucune observation de leur interface actuelle par navigateur n’est revendiquée. |

## Carte des changements pour l’implémentation

| Surface | Points d’entrée existants | Transformation visible |
|---|---|---|
| Recherche/contexte | `index.html` catalogue, `syncControls`, `chooseContentLanguage`, `createMobileUI` | Barre question/voiture/langue, suppression des rangées redondantes et du grand titre générique. |
| Filtres | `#filters`, `openFilters`, `renderFacets` | Un panneau commun, groupes utiles et compteur fiable ; plus de colonne permanente. |
| Résultats | `loadVideos`, `renderActiveFilters`, `renderContext` | Première photo remontée ; explication/guide regroupés et repliés, exceptions importantes visibles. |
| Préfiche | `cardMarkup`, `guideUI.card`, `automotiveUI.cardMarkup` | Photo + objet + aperçu attribué + provenance + CTA explicite. |
| Fiche | `openVideo`, `setDetailTab`, `guide-ui.js` | Titre/contexte et valeur avant la lecture, source et disponibilité du texte explicites. |

Les paramètres d’URL, les données et les preuves existantes restent le contrat de fond. La refonte change leur hiérarchie et leur présentation, pas leur niveau de certitude.

## Première critique des nouveaux rendus

À comparer à V19, avec « vidange Clio 3 » et langue française :

- La première photo apparaît-elle au premier écran sans fermer de panneau ?
- Voiture et langue sont-elles identifiables dans un seul endroit, modifiables sans perdre la question ?
- Le panneau de filtres montre-t-il d’abord des décisions utiles plutôt qu’une grille de disciplines à zéro ?
- Avant d’ouvrir, sait-on distinguer le sujet, l’auteur, la plateforme et la portée de la ressource ?
- À l’ouverture, titre et contenu potentiel précèdent-ils la sollicitation de lecture externe ?
- Les notices, transcriptions absentes et langues estimées restent-elles honnêtement présentées ?
- La silhouette des résultats et des fiches a-t-elle réellement changé, au-delà de la couleur et des rayons ?

État de coordination : l’agent principal a confirmé l’implémentation d’un panneau commun, du contexte compact, du regroupement « Comprendre ces résultats » et de cartes avec aperçu attribué. Ce rapport ne prétend pas que cette nouvelle version est déjà rendue ou testée.
