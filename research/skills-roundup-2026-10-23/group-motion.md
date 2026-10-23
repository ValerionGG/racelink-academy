# Ressources mouvement et interaction — RaceLink

Vérification du **23 octobre 2026, vers 16:04 UTC**. Périmètre de ce groupe : React Bits, Emil Kowalski Skills, GSAP Skills et Scroll World. La capture complète des douze ressources n’est pas reproduite ici ; les quatre noms assignés ont été rapprochés de leurs dépôts primaires. Aucun frontend, catalogue, paquet npm ou déploiement modifié.

**Décision : conserver les grandes photographies et la navigation native, puis améliorer quelques retours d’action en CSS.** Les skills d’Emil Kowalski apportent surtout une méthode pour éliminer les animations inutiles. GSAP reste une option pour une future séquence explicative complexe ; les interactions actuelles ne justifient pas son ajout. Scroll World correspond à une page de présentation cinématique, pas au moteur de recherche de tutoriels.

## Dépôts exacts et popularité vérifiée

Les étoiles ci-dessous proviennent directement de `gh api repos/{owner}/{repo}`, pas d’un annuaire. Ce sont des instantanés d’intérêt public, pas des notes de qualité, des nombres d’installations ou une mesure de compatibilité.

| Ressource | Dépôt primaire | Étoiles | Nature réelle et décision |
|---|---|---:|---|
| React Bits | [DavidHDev/react-bits](https://github.com/DavidHDev/react-bits) | **50 061** | Bibliothèque de composants React et outils créatifs. Les variantes JS/CSS restent des composants React ; aucune version vanilla prête à brancher n’est déduite de ce nom. Source d’inspiration ponctuelle, sans migration React. |
| Emil Kowalski Skills | [emilkowalski/skills](https://github.com/emilkowalski/skills) | **48 965** | **15 fichiers SKILL.md** dans l’arbre consulté, alors que certains index annoncent encore treize. Conseils de motion, revue, performance et ergonomie mobile. Méthode adaptée à notre stack. |
| GSAP Skills | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | **16 982** | **8 skills officiels** de GreenSock. Documentation de l’API GSAP, de ses cycles de vie et de ses performances ; installer ces textes n’installe pas la bibliothèque. |
| Scroll World | [oso95/scroll-world](https://github.com/oso95/scroll-world) | **10 386** | Un vrai skill accompagné d’un moteur JavaScript natif : scènes et vidéos générées, puis lecture synchronisée au défilement. Correspondance solide avec le nom, sans pouvoir affirmer que la capture visait ce dépôt en l’absence de son lien lisible. |

Références GitHub lues : React Bits `e12c22192ac7b4b452c5e2feb9b586d74765d696`, Emil `2d228630ba1446365f614a108cb8252f1feda202`, GSAP Skills `aed9cfd3277740755f6bfc1155c7aa645403b760`, Scroll World `71cc36d3bb150248ae36a2c552f9cbf88802a79c`. Métadonnées de poussée observées : respectivement 19 octobre, 11 octobre, 29 juillet et 29 juillet 2026. Reproduction : `gh api repos/emilkowalski/skills --jq '{stargazers_count,pushed_at,default_branch}'`, puis même requête pour les autres dépôts.

## Ce qui a été lu et retenu

**React Bits.** Le composant [AnimatedContent](https://github.com/DavidHDev/react-bits/blob/e12c22192ac7b4b452c5e2feb9b586d74765d696/src/content/Animations/AnimatedContent/AnimatedContent.jsx) importe React, GSAP et ScrollTrigger, gère le mouvement réduit, les apparitions uniques et le nettoyage d’un contexte. Ses valeurs par défaut — déplacement de 100 px et durée de 0,8 s — ne conviennent pas à des résultats de recherche fréquemment remplacés. [FadeContent](https://github.com/DavidHDev/react-bits/blob/e12c22192ac7b4b452c5e2feb9b586d74765d696/src/content/Animations/FadeContent/FadeContent.jsx) propose aussi des masques et filtres : cela dépasse le besoin de lire rapidement une photo et un titre. Retenir le principe d’une apparition unique et du nettoyage, pas recopier ces composants ni leurs effets. La [licence actuelle](https://github.com/DavidHDev/react-bits/blob/e12c22192ac7b4b452c5e2feb9b586d74765d696/LICENSE.md) est **MIT + Commons Clause**, avec restriction de redistribution des composants/outils eux-mêmes ; ne pas la présenter comme MIT simple.

**Emil Kowalski.** [Find Animation Opportunities](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/find-animation-opportunities/SKILL.md) impose une justification par fréquence, fonction et délai avant de proposer un mouvement. [Animate](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/animate/SKILL.md) privilégie CSS puis WAAPI lorsque cela suffit. [Mobile Native](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/mobile-native/SKILL.md) distingue gestes tactiles, hover réel, viewport dynamique, zones de sécurité et test sur téléphone. La [revue](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/review-animations/SKILL.md) est volontairement prescriptive. Ses préférences esthétiques ne sont pas des obligations universelles : RaceLink peut conserver une désactivation complète sous mouvement réduit et ses dialogues natifs accessibles.

**GSAP Skills.** [Core](https://github.com/greensock/gsap-skills/blob/aed9cfd3277740755f6bfc1155c7aa645403b760/skills/gsap-core/SKILL.md) documente `gsap.matchMedia()` et la restauration des animations quand un contexte change. [Performance](https://github.com/greensock/gsap-skills/blob/aed9cfd3277740755f6bfc1155c7aa645403b760/skills/gsap-performance/SKILL.md) recommande transforms/opacité, lectures DOM regroupées, limitation des éléments animés et nettoyage des animations inactives. Appliquer ces principes sans dépendance supplémentaire. La licence MIT du dépôt concerne les **skills** ; elle ne suffit pas à qualifier juridiquement tout le moteur GSAP ou ses distributions.

**Scroll World.** Le [README](https://github.com/oso95/scroll-world/blob/71cc36d3bb150248ae36a2c552f9cbf88802a79c/README.md) décrit Monid/Higgsfield avec solde ou crédits, ffmpeg/ffprobe et une chaîne vidéo générée par projet. Son estimation historique de coût n’est pas un devis actuel. Le [skill](https://github.com/oso95/scroll-world/blob/71cc36d3bb150248ae36a2c552f9cbf88802a79c/skills/scroll-world/SKILL.md) traite notamment les raccords, le cadrage portrait et les contraintes mobiles. Le [moteur](https://github.com/oso95/scroll-world/blob/71cc36d3bb150248ae36a2c552f9cbf88802a79c/skills/scroll-world/references/scrub-engine.js) évite le chargement des clips lorsque le mouvement réduit est actif au montage. Bonne idée à retenir : une image statique utile doit suffire. Aucun moteur, script de génération ou abonnement de ce projet n’a été lancé ou installé.

## Applications concrètes pour RaceLink

Les lignes correspondent au code local lu pendant cet audit. Ce tableau propose des changements futurs ; il ne prétend pas qu’ils sont implémentés ou visuellement validés.

| Priorité et emplacement | État observé | But et fréquence | Proposition bornée |
|---|---|---|---|
| 1 — `.save-card`, `product-ui.css:214` | Couleur et état enregistré existent, pas de retour d’enfoncement spécifique. | Confirmer une pression ; occasionnel. | Sur activation pointeur uniquement, `scale(0.97)` puis retour, **120 ms**, `cubic-bezier(0.23,1,0.32,1)`. Ne pas modifier la carte ni différer sa sauvegarde. Clavier : état immédiat. Mouvement réduit : couleur seulement. |
| 2 — `#toast`, `styles.css:1`, `app.js:98` | Transition de 200 ms déjà présente, mais propriété non précisée (`transition:.2s`). | Clarifier une confirmation ; occasionnel. | Conserver le comportement existant et borner à `opacity, transform`, **200 ms**, même courbe ; aucun nouveau rebond ou délai. Toujours un seul toast et son annonce existante. Mouvement réduit : état immédiat. |
| 3 — `#filters-dialog`, `mobile-ui.js:56` | Dialogue natif ouvert directement, contrôles uniques déplacés puis restaurés. | Situer le panneau ; occasionnel. | Au plus une entrée de **200 ms**, `translateY(8px)` vers zéro + opacité, courbe `cubic-bezier(0.32,0.72,0,1)`, uniquement si demande pointeur. Fermeture native immédiate : ne pas attendre l’animation avant de rendre le focus. Sans animation si le support manque ou si mouvement réduit. |

Ces valeurs sont des décisions de produit dans les fourchettes des skills, pas des performances mesurées. Réutiliser des tokens communs plutôt que disperser des durées ; ne pas ajouter `will-change` à toutes les cartes. Une variation CSS explicite ou WAAPI isolée suffit aux trois cas.

### Candidats volontairement écartés

- **Recherche, suggestions et raccourci `/`** : actions fréquentes, navigation clavier et texte en cours de saisie. Aucun effet de frappe, flou, apparition en cascade ou délai de focus.
- **Résultats filtrés et pagination** : pas de Masonry animé, d’ordre spatial recalculé ni de fade relancé à chaque réponse. L’ordre DOM, le rang de pertinence et le titre doivent rester immédiatement lisibles.
- **Hero et cartes photographiques** : pas de vidéo scrubbée, de parallaxe sur les photos sources, de masque bruité ou de texte découpé lettre par lettre. La photo reste l’élément dominant ; un léger hover déjà existant n’a pas besoin d’être multiplié.
- **Fond de page et navigation** : pas de particules, de scroll remplacé par un moteur fluide ou de déplacement du formulaire durant une animation. Les safe areas et le clavier tactile ont priorité.

## Installations effectuées

Le skill système **skill-installer** et ses scripts de téléchargement ont été lus avant exécution. Installation par téléchargement GitHub épinglé, sans `npx`, script distant exécuté, bibliothèque frontend ou dépendance ajoutée. Les deux dossiers sélectionnés ne contiennent qu’un `SKILL.md`.

| Skill | Référence installée | Emplacement local | SHA-256 du fichier |
|---|---|---|---|
| `find-animation-opportunities` | Emil `2d228630ba1446365f614a108cb8252f1feda202` | `C:/Users/Nad/.codex/skills/find-animation-opportunities/SKILL.md` | `d52a377819b84a71930f0c822cfe2849f40301605a2d5c7eccbfa3b257700df2` |
| `gsap-performance` | GSAP `aed9cfd3277740755f6bfc1155c7aa645403b760` | `C:/Users/Nad/.codex/skills/gsap-performance/SKILL.md` | `cb5408d6fba707aabcbfe3320317a14c1f8fca6070074e5261047930f50d441e` |

Ils seront disponibles dans le catalogue des skills **au prochain tour**. Les textes sont déjà consultables ; leur installation ne change pas le modèle et ne prouve aucun gain automatique de design. React Bits et Scroll World n’ont pas été installés. L’intégration éventuelle de GSAP demandera un besoin de séquençage réel, absent de ces trois propositions.

## Validation nécessaire avant un changement d’interface

Conserver les tests de navigation et HTML existants, puis vérifier avec et sans mouvement réduit : recherche depuis une autre vue, saisie conservée, Tab/flèches/Entrée/Escape, ouverture d’une ressource depuis les suggestions, retour du focus, filtre puis changement de largeur 760/761 px. Tester 320 et 390 px, le clavier réel et les safe areas. Les animations éventuelles doivent être annulées au changement de vue et rester sans effet sur les réponses réseau/Worker et les filtres. Un test de performance sur téléphone modeste reste nécessaire avant toute promesse de fluidité.

**Premier chantier conseillé : le retour d’appui du bouton Enregistrer**, puis borner la transition du toast existant. Le catalogue n’a besoin ni d’un moteur cinématique ni de React pour bénéficier de ces ressources.
