# Recherche V34 — aide à la formulation et véhicule conservé

## Changement

Une question sans résultat peut désormais proposer un sujet à ouvrir, avec le nombre réel de ressources correspondant aux filtres actuels. « Ma clim ne fait plus de froid » propose par exemple « climatisation ». Les propositions apparaissent aussi pendant la saisie. La question soumise reste inchangée tant que l’utilisateur n’a pas choisi la proposition. Le vocabulaire décrit un sujet de recherche, pas la cause d’une panne.

Six familles de formulations françaises sont configurées dans `public/discovery-catalog.json` : climatisation, démarrage, CarPlay, Android Auto, voyant moteur et une correction d’orthographe des essuie-glaces. Les corrections de mots de sujet déjà présentes restent disponibles. La bibliothèque de formulations est volontairement bornée ; ce n’est pas un système de diagnostic ni une compréhension générale de toutes les phrases.

La recherche reconnaît aussi « pile de ma clé », « pile de la carte » et « pile de télécommande ». Les variantes de casse d’un modèle dans les données ne créent plus une fausse ambiguïté : `Clio` et `clio` représentent désormais le même nom dans l’interprétation de la requête. La génération explicitement demandée reste une contrainte, y compris quand une variante historique utilise un chiffre et une autre un chiffre romain déjà indexé.

## Contrat

`/api/videos` et `/api/resources` renvoient `search_assistance.suggestions` pour une recherche vide. Chaque proposition inclut `query`, `completion`, `filters`, `count`, `reason`, `match_basis` et les changements proposés dans `corrections`. `/api/suggestions` peut renvoyer les mêmes entrées de type `query`.

- Un compteur vient d’une recherche exécutée avec les mêmes critères ; aucune proposition à zéro n’est affichée.
- Les mots extérieurs à la formulation reconnue sont conservés. Les noms de modèles, moteurs, années et références techniques ne sont pas corrigés approximativement.
- Les critères explicites de véhicule, plateforme, langue, durée, droits, transcription, format et identifiants restent appliqués. Un conflit de véhicule empêche les propositions.
- Au plus huit candidats complets sont comptés, pour trois propositions au maximum ; les compteurs utilisent le cache borné existant.
- La langue FR d’une ressource reste une étiquette de métadonnées, pas une certification de l’audio. Une mention de véhicule n’est pas une garantie de compatibilité.

## Vérification du 28 octobre 2026

Le corpus de référence V33 contient **39 845 vidéos et 11 guides**, avant tout import V34. Les résultats ci-dessous décrivent cette base, et peuvent évoluer après de nouveaux imports :

| Recherche avec filtre FR | Résultat observé |
| --- | --- |
| `ma clim ne fait plus de froid` | La recherche reste vide ; proposition `climatisation`, 28 ressources. |
| Même question + TikTok | Proposition avec 4 ressources ; TikTok et FR conservés. |
| Même question + Instagram | Proposition avec 1 ressource ; Instagram et FR conservés. |
| `essuie glasse Clio 4` | Proposition `essuie-glaces Clio 4`, 3 ressources ; Renault, Clio et IV conservés. |
| `carplay se déconnecte` | Proposition `CarPlay`, 48 ressources. |
| `vidange Clio 4` | 2 résultats et véhicule reconnu ; auparavant 1 résultat sans interprétation du véhicule. |
| `pile de ma clé Clio 5` | Tâche et véhicule reconnus ; toujours zéro résultat compatible dans ce corpus. |

53 tests Python passent, dont 8 nouveaux tests couvrant l’aide explicite, les conflits, l’absence de résultat, la conservation des références et la parité JavaScript/Python. Les 35 contrôles statiques existants passent. Seize scénarios supplémentaires sur le corpus réel ont les mêmes compteurs, interprétations et propositions dans les deux moteurs.

Les mesures locales sont réalisées avec Node.js sur le poste Windows. Elles ne constituent pas un test de performance sur téléphone physique ni un contrôle visuel du navigateur. Les validations de l’interface sont documentées séparément par la livraison V34.

## Provenance PeerTube

La sérialisation publique expose `source_provider: peertube` uniquement quand la métadonnée d’import porte exactement `provider: peertube`. Le domaine d’une URL n’est pas utilisé pour inventer ce label. Un test vérifie la liste blanche et l’absence de label pour les autres valeurs. Ce champ ne modifie ni plateforme historique, ni identité de vidéo.
