# Recherche, apprentissage et consultation mobile — RaceLink Academy

**Statut : étude préalable, conservée pour ses sources et ses hypothèses.** Les choix publiés sont décrits dans [DECISIONS.md](DECISIONS.md) et [DESIGN.md](../../DESIGN.md). La proposition initiale Barlow/ivoire a été suivie d’une première refonte Manrope, puis de la v14 Onest/Orbitron, noir/rouge/blanc et surfaces de lecture neutres. La navigation mobile commence par « Accueil » ; les fiches utilisent un dialogue natif plein écran. Les essais de l’application publiée figurent dans [VALIDATION.md](VALIDATION.md).

Étude du 23 octobre 2026. Recherche seule : aucun fichier applicatif, compte, catalogue ou dépôt Git modifié par cette recherche. Skill utilisé : `design-inspiration`.

## Conclusion de produit

RaceLink doit fonctionner comme une **bibliothèque d’atelier**, utilisable près d’une voiture aussi bien que pour apprendre le pilotage. Le parcours central est **question → résultats → fiche → source**. Le véhicule et la langue affinent cette recherche ; ils ne forment pas un questionnaire préalable. Les parcours organisés et les sélections sont des alternatives utiles, accessibles sans dominer l’écran.

La combinaison retenue est précise : la préparation d’iFixit, le contexte automobile d’AUTODOC, les facettes et l’enregistrement de Skillshare, la consultation textuelle de YouTube et la continuité de recherche de Linear/Raycast. Il s’agit d’emprunter des principes, pas de copier leurs écrans ni leurs actifs.

## Périmètre et niveau de preuve

Contexte lu intégralement : `outputs/focus-academy/PRODUCT.md` et `public/index.html`. Le produit revendique déjà une recherche principale, une interface FR/EN/ES, des langues de contenu distinctes, des critères exacts de véhicule et une prudence sur les métadonnées. Le HTML expose une recherche, des suggestions, une entrée véhicule, des filtres, des formats, une sélection personnelle, des parcours et une navigation mobile à quatre destinations. Les recommandations préservent ces fonctions.

La structure source juxtapose encore accueil, entrée Explorer, Bibliothèque, parcours, langue du site, langue vidéo, suggestions, image héro, découverte, résultats et véhicule. Cela signale un risque de multiplication des points d’entrée ; sans rendu actuel, ce n’est pas une mesure du défilement réellement nécessaire.

Les sources primaires ont été recherchées et leurs pages textuelles consultées. **Aucune image de référence n’a pu être inspectée visuellement dans cette session** : l’ouverture d’un onglet CUA a indiqué que le navigateur intégré n’était pas disponible, puis l’inventaire des navigateurs était vide. Aucun onglet du parent n’a été touché. Les descriptions d’images du moteur de recherche ne constituent pas une observation visuelle et ne fondent aucune décision de couleur ou de composition.

Pinterest et une première référence Behance ont renvoyé 403. Aucun autre moyen n’a été utilisé pour accéder à ces pages. Une autre étude Behance, accessible normalement, a pu être lue. Ce rapport de recherche contient donc **sept références de produits documentées, deux références de portfolio lisibles en texte et une référence Pinterest repérée mais exclue du fondement des décisions**. **Complément ultérieur confirmé par l’agent principal :** il a réellement inspecté l’image Dribbble de Parthik Kalsariya et le site officiel RaceLink, puis testé des parcours de la v14 publiée. Ces preuves sont distinctes ; consulter [brand-direction.md](brand-direction.md) et [VALIDATION.md](VALIDATION.md). Cela ne transforme pas les autres observations documentaires en inspections visuelles. Ce n’est pas un classement empirique des « meilleurs » produits : aucune étude comparative de succès utilisateur n’a été réalisée.

## Dix références et décisions transférables

### 1. iFixit — préparer une intervention avant de commencer

Source : [Parts of a Guide Page](https://about.ifixit.com/Wiki/Parts_of_a_Guide_Page), équipe iFixit ; [Car and Truck](https://www.ifixit.com/Device/Car_and_Truck), catégorie automobile. **Preuve : texte des pages consulté.**

**Observation.** La documentation organise un guide en introduction, détails et étapes. Les détails comprennent temps, difficulté, outils, pièces et prérequis. Elle distingue un démontage pédagogique d’une procédure de réparation. Le mode plein écran est présenté pour l’utilisation sur mobile/tablette. La catégorie automobile sépare remplacement, techniques et diagnostic.

**Interprétation pour RaceLink.** Avant le lien sortant, une fiche doit permettre de savoir ce que la ressource traite et ce qu’elle suppose. Les étiquettes « Tutoriel », « Démonstration » et « Cours » ne sont pas interchangeables. N’afficher temps de travail, outils ou prérequis que si une source les donne ; la durée de la vidéo n’est pas celle de l’intervention.

**Ne pas reprendre.** Ni promesse de guide complet, ni étapes reconstruites à partir d’un simple titre. Une référence externe ne devient pas une procédure RaceLink validée.

### 2. AUTODOC Club — chercher par véhicule et par pièce

Source : [Car repair manuals and video guides](https://club.autodoc.co.uk/manuals) et [Wiper Blades](https://club.autodoc.co.uk/manuals/windscreen-cleaning-system/wiper-blades), AUTODOC. **Preuve : texte des pages consulté.**

**Observation.** L’entrée des manuels propose marque, modèle et catégorie de pièce, puis une action de recherche. La même page offre des accès directs par pièce, ainsi que des vidéos et des guides PDF identifiés séparément. Les titres associent généralement une intervention à un modèle précis.

**Interprétation pour RaceLink.** Deux entrées complémentaires doivent fonctionner : « changer les essuie-glaces » sans voiture renseignée, ou « Clio » puis intervention. Un bouton véhicule permanent évite d’obliger à ressaisir le contexte. Les précisions moteur/année apparaissent ensuite, facultativement.

**Ne pas reprendre.** Le catalogue RaceLink n’a pas les mêmes garanties de compatibilité que le producteur d’un manuel. Écrire « Clio mentionnée dans la source », jamais « convient à votre Clio » sur la seule extraction du titre. Les pièces à acheter et les offres commerciales ne sont pas l’action principale.

### 3. YouTube — séparer recherche, type de résultat et passage utile

Sources : [Recherche avancée](https://support.google.com/youtube/answer/111997?hl=fr), [Transcriptions](https://support.google.com/youtube/answer/15930243?hl=fr), [Vidéos avec sous-titres](https://support.google.com/youtube/answer/3029103?hl=fr), Google. **Preuve : aide primaire consultée ; pas de session de lecture vidéo testée.**

**Observation.** La recherche est saisie avant l’affinage. Les filtres distinguent notamment des types de contenus. La transcription, quand elle existe, permet de lire le texte et de rejoindre un passage en touchant une ligne. La présence de sous-titres peut aussi servir de filtre.

**Interprétation pour RaceLink.** « Vidéo / Guide » décrit le format de ressource ; « YouTube / TikTok… » décrit son hébergeur. Sur la fiche, une transcription disponible mérite une entrée directe, avec langue, caractère automatique éventuel et recherche dans son texte. Si des horodatages sont réellement disponibles et exploités, chaque passage peut proposer un accès au moment correspondant.

**Ne pas reprendre.** Pas d’autoplay, de fil infini de divertissement ni de bouton transcription lorsqu’aucun texte n’est présent. Sous-titres et transcription locale sont deux disponibilités différentes.

### 4. Skillshare — filtres compréhensibles et retour à une sélection

Sources : [Search FAQ](https://help.skillshare.com/hc/en-us/articles/16267180286221-Search-FAQ), mise à jour affichée 17 juillet 2025 ; [Save a class](https://help.skillshare.com/hc/en-us/articles/204537268-How-do-I-save-a-class-for-later), mise à jour affichée 24 octobre 2025. **Preuve : texte primaire consulté.**

**Observation.** Skillshare sépare classes et parcours, rend les filtres accessibles par un bouton, affiche des quantités par facette et grise les combinaisons sans résultat. Sa documentation distingue les filtres disponibles sur le web mobile de ceux de l’app. L’enregistrement est proposé sur la carte et la fiche ; la collection est accessible dans le menu inférieur mobile.

**Interprétation pour RaceLink.** Afficher un panneau de filtres lisible avec résultat attendu et un accès « Enregistrés » durable. Garder la valeur sélectionnée visible lorsqu’elle aboutit à zéro, et proposer de retirer un critère à la fois. Afficher les langues disponibles globalement, pas seulement celles des résultats déjà filtrés.

**Ne pas reprendre.** Aucun badge « meilleur enseignant », notation ou popularité ne doit être fabriqué. Le critère de langue doit rester disponible sur mobile même quand il se trouve dans un panneau secondaire.

### 5. MasterClass — distinguer les états de consultation

Source : [Downloading Classes for Offline Viewing](https://www.masterclass.com/help-center/masterclass/answers/downloading-classes-for-offline-viewing--id--c1GMEnNOQqiRDFdE0oa_pA), MasterClass. **Preuve : aide primaire consultée, app non testée.**

**Observation.** La documentation différencie les cours consultables en ligne, ceux éligibles au téléchargement et ceux effectivement téléchargés. Un changement d’icône matérialise la fin du téléchargement. La rubrique de suivi est accessible depuis la navigation inférieure.

**Interprétation pour RaceLink.** Un état utilisateur doit décrire une action réelle : enregistré, ouvert, terminé volontairement dans un parcours. Un signet ne signifie pas « appris », et avoir ouvert une source externe ne prouve pas le visionnage complet. La sélection personnelle doit être immédiatement retrouvable.

**Ne pas reprendre.** Ni téléchargement des vidéos tierces ni promesse hors connexion. Cette référence sert à la clarté des états, pas à justifier un catalogue de portraits prestigieux ou un grand écran promotionnel.

### 6. Linear — garder la recherche et ses critères comme un contexte

Sources : [Search](https://linear.app/docs/search) et [Filters](https://linear.app/docs/filters), Linear. **Preuve : documentation primaire consultée.**

**Observation.** La recherche dispose d’un accès direct, distingue recherche globale et recherche dans une vue, rappelle les éléments récents et permet d’ajouter des critères. Les filtres principaux se reflètent dans l’URL partageable ; les résultats se mettent à jour selon les critères appliqués.

**Interprétation pour RaceLink.** Une requête et ses filtres forment un état unique, conservé entre résultats, fiche, retour et partage. Le véhicule et la langue restent visibles. Les suggestions peuvent proposer un sujet ou un guide, mais leur type doit être nommé et leur sélection ne doit pas effacer les contraintes déjà choisies.

**Ne pas reprendre.** Les opérateurs avancés et raccourcis spécialisés restent facultatifs. Le mobile n’a pas besoin d’une interface de gestion de projet, de codes cryptiques ou d’un menu de commandes rempli d’options rares.

### 7. Raycast — un champ, des suggestions, une action principale

Sources : [Search Bar](https://manual.raycast.com/search-bar) et [Action Panel](https://manual.raycast.com/action-panel), Raycast. **Preuve : documentation primaire consultée ; référence d’interaction desktop, pas modèle de navigation mobile testé.**

**Observation.** Le champ de recherche constitue l’entrée centrale. Les résultats s’affichent sous le champ ; l’action primaire est distincte des opérations secondaires contextuelles. Le système documente la navigation fléchée et l’exécution par Entrée, ainsi que les favoris et éléments récents.

**Interprétation pour RaceLink.** Rendre la saisie immédiate et le résultat sélectionnable en une action. Dans les suggestions, séparer « chercher cette expression » de « ouvrir ce guide ». Sur une carte, consulter est l’action principale et enregistrer une action indépendante. Une liste courte aide à décider ; elle ne doit pas répliquer tout le catalogue.

**Ne pas reprendre.** Pas de personnalisation opaque reposant sur une prétendue connaissance de l’utilisateur. Des récents locaux peuvent être proposés avec possibilité de les effacer, si cette fonction est réellement implémentée.

### 8. Dribbble — Modern Mobile UI for Online Learning Platform

Source : [projet de Parthik Kalsariya](https://dribbble.com/shots/26306305-Modern-Mobile-UI-for-Online-Learning-Platform). **Preuve : page textuelle consultée par l’agent de recherche ; image réelle ensuite inspectée par l’agent principal via CUA.** Les observations ci-dessous restent celles du relevé textuel initial.

**Observation limitée.** L’auteur décrit explicitement recherche et filtres, cours classés et navigation inférieure. La page donne une palette, mais elle n’a pas été utilisée comme preuve du rendu. Un résultat de recherche d’images renvoie aussi à cette création ; sa description automatique n’est pas une inspection.

**Interprétation pour RaceLink.** Le couple recherche + destinations stables mérite une proposition à tester. Le portfolio n’apporte aucune mesure d’efficacité, ni preuve que les états vides, la traduction ou le clavier fonctionnent. Il ne justifie ni sa palette ni ses proportions dans notre produit.

**Ne pas reprendre.** Aucun actif, avatar, indicateur de progression ou écran exact. Il s’agit d’un concept, pas d’un produit audité.

### 9. Behance — E-learning mobile app, UX Case Study / Lingua Attack

Source : [Gorsel Kutman, 14 juin 2021](https://www.behance.net/gallery/115613205/E-learning-mobile-app-UX-Case-Study). **Preuve : étude textuelle consultée ; visuels non inspectés.**

**Observation.** L’auteur décrit quatre expériences pédagogiques, des prototypes successifs et des tests. Ses principes déclarés comprennent une complexité progressive et la distinction entre commande et configuration. Le texte documente une démarche ; ses résultats ne sont pas une validation indépendante des performances actuelles.

**Interprétation pour RaceLink.** « Rechercher » déclenche une tâche ; « Langue » et « Véhicule » en règlent le contexte. Cette séparation évite de présenter toutes les options comme des actions concurrentes. Tester des parcours complets avant de polir une page d’accueil.

**Ne pas reprendre.** Ni onboarding obligatoire ni collection de modes pédagogiques artificiels. Le projet date de 2021 ; il apporte une structure de réflexion, pas une preuve d’interface actuelle.

### 10. Pinterest — Simple E-Learning App UI Design

Source : [pin 30680841204302881](https://www.pinterest.com/pin/simple-elearning-app-ui-design--30680841204302881/). Auteur original non établi. **Preuve : titre indexé uniquement, ouverture 403.**

La référence a été recherchée conformément au périmètre. Aucun visuel ni créateur n’est confirmé ; aucun principe spécifique n’en est déduit. Elle reste une piste à regarder ultérieurement avec un accès ordinaire autorisé, et non une pièce justificative de cette étude. La première page Behance [Insightlancer](https://www.behance.net/gallery/179376823/Online-Learning-Mobile-App-E-Learning-App-UI) a également renvoyé 403 ; elle n’est pas utilisée dans les décisions.

## Architecture mobile recommandée

### Explorer : une entrée de travail compacte

Au premier écran : logo discret, titre court « Qu’aimeriez-vous apprendre ? », recherche, ligne de contexte véhicule/langue, puis quelques ressources utiles. Conserver trois accès illustrés Entretien / Pilotage / Sim racing, mais limiter leur hauteur et ne pas en faire une étape obligatoire. Les huit disciplines restent accessibles depuis « Tous les sujets ». Éviter d’empiler objectifs, thèmes, catégories et sélections qui conduisent au même résultat.

Une préférence de langue mémorisée peut être réutilisée si elle est visible. Sans choix antérieur, proposer « Toutes les langues » et un raccourci explicite « Français ». Modifier la langue du site ne doit pas modifier celle des vidéos. La présence de ressources en langue estimée doit être compréhensible sans ouvrir une note de bas de page.

### Rechercher : résultats dans la continuité du champ

Le champ devient l’en-tête de la vue de recherche. Le clavier peut ouvrir les suggestions, puis Entrée conduit aux résultats de la saisie réelle. Prévoir une action « Rechercher “…” » même si aucun sujet prédéfini ne correspond. Les suggestions sont limitées et typées ; les termes du catalogue et les critères déjà actifs restent exacts.

Ordre vertical proposé après validation : champ → contexte et filtres actifs → formats Tout/Vidéos/Guides → nombre de résultats + tri → cartes. La zone fixe doit rester courte ; quatre rangées persistantes mangeraient l’écran avec le clavier. En défilement, conserver seulement recherche compacte + bouton Filtres. Les filtres secondaires restent accessibles sans revenir en haut.

### Véhicule : préciser uniquement ce qui est connu

Le bouton « Véhicule : tous » ouvre une vue/panneau dédié. Première étape marque et modèle ; deuxième étape optionnelle génération, année, moteur, carrosserie, carburant. Les valeurs proviennent des facettes réelles. Un champ sans choix connu n’est pas complété automatiquement. Une valeur sélectionnée à zéro reste visible et supprimable.

Résumé proposé : « Renault Clio · année non précisée » plutôt qu’un faux véhicule complet. Sous les résultats : « Ces ressources mentionnent votre sélection. Vérifiez la version dans la source. » Une fiche générale sur les essuie-glaces ne gagne aucune compatibilité par association avec la recherche.

Pour le pilotage, la simulation ou les métiers, le véhicule n’est pas imposé. Si un filtre véhicule résiduel limite ces sujets, le contexte reste visible et propose de l’enlever ; aucune suppression silencieuse de préférence.

### Filtres : moins visibles, mais plus compréhensibles

Panneau mobile avec sections courtes : Sujet ; Langue du contenu ; Format de ressource ; Niveau ; Durée. Plateforme, type de vidéo, transcription et droits restent dans « Plus de critères ». Le niveau et la langue gardent leurs statuts d’estimation. Les titres de sections utilisent des mots normaux, pas une cascade d’acronymes.

Choisir un modèle d’application cohérent : recommandations **brouillon dans le panneau puis bouton « Afficher N résultats »**, afin de ne pas déplacer la liste à chaque réglage. Fermer sans appliquer laisse l’état précédent. Si le code existant applique immédiatement, ne pas simuler un bouton de validation qui ne fait rien : l’implémentation et le libellé doivent raconter la même interaction.

Les puces actives affichent leur catégorie quand la valeur serait ambiguë : « Langue : français », « Niveau : débutant », « Véhicule : Clio ». Une croix retire un seul critère, avec un nom accessible complet. « Effacer les filtres » conserve la question saisie ; l’action plus large « Nouvelle recherche » est distincte.

### Cartes : choisir sans décoder des badges

Sur téléphone, une liste à une colonne avec miniature et texte suffisamment larges. Prototype de densité à tester : image 128–144 px de large en paysage, titre de trois lignes au maximum, suivi de l’auteur et de la plateforme. En dessous, seulement les informations qui distinguent vraiment le choix : langue, durée connue et mention de véhicule pertinente. À 320 px ou avec texte agrandi, passer l’image au-dessus plutôt que comprimer le titre.

Pour les vidéos verticales, utiliser un cadre cohérent et éviter de couper les gestes importants ; ne pas étirer l’image. Si la miniature manque, utiliser un fond neutre avec pictogramme et mention de la source. Une illustration éditoriale n’est pas une capture de la vidéo.

Le titre ouvre la fiche ; le bouton signet est un contrôle frère, jamais imbriqué dans un bouton englobant. Libellé accessible « Enregistrer [titre] », état pressé et retour bref. Le nombre de vues n’est pas un indicateur de sûreté ni une raison suffisante de mise en avant.

### Fiche : comprendre puis consulter

Sur mobile, préférer une vue pleine page à une fenêtre superposée de plus en plus longue. En tête : retour, titre, auteur, plateforme et image. L’action principale « Voir sur YouTube/TikTok/Instagram… » indique la destination externe ; le signet reste secondaire. Puis : sujet réellement décrit, véhicule/norme mentionnés avec preuve courte, description de source, texte/transcription s’il existe, et ressources proches.

Le résumé éditorial éventuel reste nommé comme tel. Une légende native, un titre indexé et une transcription ne doivent pas partager un même libellé. « Français estimé à partir du titre » renseigne une preuve de texte ; cela ne certifie pas l’audio. Une provenance détaillée peut se déplier, mais une incertitude de véhicule ou de langue reste proche du champ concerné.

Si le lien externe n’est pas lisible localement, conserver l’URL d’origine et expliquer seulement l’état connu. Ne pas afficher « vidéo indisponible » sur une simple erreur de chargement de miniature. Aucune lecture automatique ou téléchargement non demandé.

### Navigation inférieure : quatre destinations persistantes

Proposition : **Explorer · Rechercher · Parcours · Enregistrés**. Le premier niveau doit rester identique entre les écrans. « Véhicule » est un contexte de recherche, pas une destination de même rang ; l’aide et les réglages d’interface passent dans le menu secondaire. « Enregistrés » est plus explicite que « Ma sélection » pour une action de signet ; conserver un seul terme partout.

Une action de navigation reçoit un état actif visible et accessible. Les intitulés accompagnent toujours les pictogrammes. Prévoir l’inset inférieur du téléphone et un espace de contenu qui évite de masquer le dernier résultat. Avec le clavier, la navigation peut se retirer visuellement si elle gêne, mais la fermeture du clavier ne doit pas changer de destination.

## État, erreurs et accessibilité à tester

| Situation | Comportement attendu |
|---|---|
| Catalogue en cours de chargement | Montrer la recherche utilisable, un état explicite et une attente réelle ; jamais un compte de résultats inventé. |
| Saisie très rapide | Une réponse ancienne ne remplace pas les suggestions de la dernière saisie. |
| Entrée sans suggestion sélectionnée | Rechercher le texte libre, avec les critères actifs conservés. |
| Suggestion de guide | Fermer la recherche, ouvrir le guide ; le retour ne rouvre pas automatiquement clavier/modale. |
| Aucun résultat en français pour ce véhicule | Garder les contrôles et valeurs ; proposer séparément enlever le véhicule ou élargir la langue, sans le faire automatiquement. |
| Retour depuis une fiche | Restaurer requête, filtres, tri, page/position et focus d’origine. |
| Enregistrement | Changer le signet, annoncer l’état, garder la carte en place. Préciser le stockage local si c’est le fonctionnement réel. |
| Miniature en erreur | Remplacement neutre à dimensions stables ; aucun échec de toute la fiche. |
| Guide général avec véhicule sélectionné | Ne jamais présenter une compatibilité à partir de ce contexte. |
| Erreur réseau / catalogue | Séparer de zéro résultat ; action Réessayer visible. |

La [combobox WAI-ARIA](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) décrit navigation au clavier, état ouvert, sélection et fermeture sans imposer la validation d’une suggestion. Appliquer ces comportements à la recherche sans intercepter les touches normales d’édition. Un champ possède un nom visible/accessible stable ; le placeholder ne remplace pas le label. Le focus doit rester perceptible après chaque transition.

Cible de conception tactile proposée : contrôles d’environ 48 px de haut, avec espacement, textes de formulaire à 16 px au moins et états distingués autrement que par la couleur. Ce sont des choix de produit à vérifier, pas une déclaration de conformité WCAG. Tester 360 × 800, 390 × 844, 430 × 932 et un agrandissement de texte à 200 %, ainsi que la navigation clavier sur ordinateur. Aucun audit d’accessibilité complet n’a été effectué ici.

## Hypothèse visuelle initiale — remplacée par les décisions de réalisation

- **Hiérarchie** : recherche et titre de ressource dominants ; provenance de second niveau ; informations techniques longues dépliables.
- **Typographie** : conserver Barlow pour lecture et contrôles, Barlow Condensed pour titres courts ; éviter les longues lignes en capitales. Échelle mobile indicative 28/22/18/16/13 px.
- **Surfaces** : fond ivoire existant, cartes claires, anthracite pour la lecture. Rouge RaceLink pour action principale, sélection et repères ponctuels. La qualité d’une source n’est pas codée par un voyant vert.
- **Rythme** : marge latérale mobile 16–20 px, groupes espacés de 24 px, cartes séparées de 12–16 px. Les lignes de résultats restent compactes sans devenir un tableau minuscule.
- **Images** : miniatures réelles créditées et illustrations RaceLink existantes pour les thèmes. Aucun actif de portfolio importé. L’image soutient le sujet ; elle ne remplace pas le titre ni l’auteur.
- **Icônes** : une famille cohérente de tracés simples, 20–24 px, avec intitulé pour les actions importantes. Pas d’icône différente pour la même action suivant l’écran.
- **Mouvement** : transitions brèves facultatives, respect de la réduction des animations, pas de carrousel automatique ni de parallaxe.

## Validation proposée avant publication

Ces scénarios constituent un protocole à exécuter, pas des tests déjà passés :

1. Un novice saisit « essuie-glaces Clio » et atteint une fiche compréhensible sans connaître la taxonomie. Observer les hésitations et le nombre d’étapes.
2. Une personne précise son véhicule, change de langue et revient d’une fiche : aucun critère ne disparaît.
3. Un professionnel cherche une norme exacte d’huile : les correspondances textuelles sont conservées ; aucun moteur n’est supposé.
4. Une personne cherche une technique de freinage en français sans voiture renseignée : le parcours reste direct.
5. Une recherche sans résultat permet d’enlever un seul critère et d’obtenir un nouvel état explicite.
6. Ouvrir un guide depuis les suggestions, le fermer, reprendre la recherche : pas de réouverture parasite ni de perte de texte.
7. Enregistrer deux sources de plateformes différentes puis les retrouver depuis la barre inférieure.
8. Ouvrir une transcription réellement disponible et comprendre sa langue, son origine et ses limites ; une autre fiche sans transcription n’en promet aucune.

Objectifs proposés : recherche accessible en un geste depuis une destination principale ; première carte sans contenu promotionnel entre la validation et les résultats ; fiche vers source en une action clairement nommée ; zéro perte de contexte dans les retours. Mesurer le succès des tâches avant d’affirmer que la nouvelle interface est meilleure.

## Ordre de réalisation

**P0 — Simplifier le parcours et garantir l’état.** Consolider les entrées recherche/résultats, rendre véhicule et langue lisibles, préserver les contraintes, corriger les transitions de recherche et de guide.

**P1 — Clarifier le choix.** Cartes homogènes, titres exacts, auteur et plateforme visibles, vraie fiche mobile, action externe évidente et incertitudes locales. La transcription n’est affichée que lorsqu’elle existe.

**P2 — Raffiner la découverte.** Quelques sélections justifiées, accès aux disciplines et parcours avec prérequis documentés. Ajouter des récents seulement si leur stockage et leur effacement sont réels. Aucun faux suivi de visionnage ou de progression.

Les preuves et limites source par source figurent dans [source-manifest.json](source-manifest.json). Aucun comportement des apps natives, rendu visuel ou taux de réussite utilisateur n’est revendiqué sans observation.
