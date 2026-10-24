# Passage à grande échelle : audit et évolution backend

24 octobre 2026. Ce travail ne réalise aucune acquisition réseau et n’ouvre pas le catalogue de production. Il augmente la capacité de préparation de métadonnées déjà accessibles ; il ne démontre pas l’existence de centaines de milliers de tutoriels pertinents disponibles dans la session.

## Lacune confirmée

`bulk_ingest.py:741` regroupe toutes les variantes et sorties dans des listes/dictionnaires en mémoire ; sa borne est de 100 000 lignes brutes. `public_export.py:244` possède une reprise par page, mais reconstitue ensuite `all_rows`, `grouped` et les sorties en mémoire, avec la même borne. Les limites évitent une exécution imprévue ; augmenter simplement ces constantes ne rendrait pas les campagnes robustes.

`local_collect.py:381` possède déjà des travaux bornés, un verrou, des empreintes de cache, une reprise et un arrêt après refus d’accès. Son fichier final `records.jsonl` garde une variante choisie par identité (`local_collect.py:452`). Pour une revue conservant les contradictions, il faut fournir au staging **toutes les variantes des caches vérifiés**, pas seulement cette projection dédupliquée. La qualification ne peut conserver une preuve négative supprimée en amont.

## Évolution livrée

Nouveau module : `outputs/focus-academy/scripts/scale_ingest.py`. Aucun collecteur existant, adaptateur, serveur, exporteur ou catalogue n’est modifié.

```text
Sources autorisées et métadonnées publiques
  → collecteurs bornés, caches et preuves de requêtes
  → snapshot JSONL immuable conservant toutes les variantes
  → scale_ingest stage : SQLite de travail + offsets + empreintes
  → campagne complète, scellée avant la première préparation
  → réconciliation par identité globale
  → lots de revue de 1 000 identités, candidats et quarantaines
  → revue éditoriale des IDs exacts
  → bulk_ingest apply existant, simulation puis autorisation explicite
```

Le module appelle `bulk_ingest.adapt()` sans changer les règles pédagogiques, les preuves de langue ou l’extraction automobile. Il garde la provenance originale de chaque variante et son SHA256. Les légendes/titres/hashtags suivent le séparateur social existant ; un corps composite Exa ne devient pas une légende directe. Les commentaires, médias et champs d’identifiants inconnus ne sont pas copiés dans le staging normalisé.

Le stockage de travail a son propre marqueur SQLite. Une base étrangère est refusée avant écriture. Le curseur de fichier et les lignes sont enregistrés dans la même transaction ; une interruption repart du dernier commit. Les JSONL sont lus par ligne physique, donc U+2028 ne fragmente pas les légendes. Une modification d’un fichier source, du moteur de qualification, du fournisseur ou d’un paquet préparé bloque la reprise.

Les variantes d’une même identité, y compris celles provenant de fichiers différents ou d’une URL TikTok dont l’auteur a changé, restent dans le même groupe. Les indications privées/non-vidéo, promotions et conflits de langue conservent la quarantaine. Seuls les manques de preuve d’un index peuvent être résolus selon la politique déjà utilisée par `bulk_ingest.prepare()` ; les tests comparent les décisions des deux chemins.

## Échec, reprise et publication prématurée

La revue indépendante a identifié un cas de mutation de fichier pendant le staging après commits partiels. La version 1.0.1 marque alors le stage comme définitivement invalidé ; restaurer le fichier ne permet plus de reprendre ni de préparer ces lignes. Une régression dédiée reproduit ce cas.

- Aucun paquet ne peut être préparé tant qu’un fichier enregistré reste incomplet.
- La campagne est scellée avant sa première préparation. Un fichier contenant une nouvelle variante ne peut plus être ajouté ; une nouvelle campagne et une nouvelle revue sont nécessaires.
- Une interruption au milieu d’un paquet rejoue ce paquet depuis le dernier checkpoint complet. Les paquets déjà terminés sont vérifiés par empreinte.
- L’intégralité des lignes du staging doit être couverte lorsque la préparation est déclarée complète.
- `approval.template.json` contient une liste vide. Le nouvel outil n’a aucune commande d’application ou de publication ; le chemin historique refuse une écriture sans approbation explicite liée à l’empreinte.
- Les campagnes sont des snapshots : une preuve apparue plus tard ne retire pas automatiquement une vidéo déjà publiée. Il faut la traiter dans une campagne de maintenance et conserver les anciennes exclusions/provenances lors de la préparation. Le module ne prétend pas assurer ce retrait éditorial automatique.

## Limites et capacité réelle

Entrées du nouveau module : **métadonnées brutes JSONL YouTube, TikTok et Instagram**, selon les adaptateurs existants. Un objet média par ligne ; les conteneurs doivent être aplatis en amont avec leur provenance. Les fichiers `accepted.json` déjà normalisés par un autre adaptateur ne doivent pas être réinterprétés comme des données natives.

Dailymotion, Vimeo, Facebook et PeerTube ne sont pas ajoutés à ces adaptateurs. Leurs lots normalisés restent une voie distincte, à vérifier puis intégrer avec `server.import_items` sous la revue de l’intégration. PeerTube est accepté par le serveur comme plateforme `other` avec provenance `peertube`, pas comme un faux export YouTube.

Bornes : 1 000 000 lignes au maximum par invocation de staging, commits de 1 à 5 000 lignes ; 2 MiB par ligne ; préparation de 1 à 5 000 identités par paquet, 1 à 1 000 paquets par invocation. La capacité totale dépend du disque et du nombre de reprises. Une identité dépassant 10 000 variantes interrompt la préparation pour revue ; elle n’est pas tronquée silencieusement.

La mesure reproductible est dans `benchmark-results.json` : plus de 100 000 lignes synthétiques, entièrement temporaires, avec cinq reprises de staging et des paquets bornés. **Ces identités synthétiques ne sont jamais acquises, importées ou comptées comme vidéos réelles.** Le résultat est une mesure locale de traitement de métadonnées courtes, pas une garantie de vitesse sur toutes les légendes.

Résultat mesuré sur la version 1.0.1 (SHA conservé dans benchmark-results.json), avant le correctif de chemin d’erreur 1.0.2 : **100 301 lignes**, **100 200 identités**, **101 variantes doublonnées**, **101 paquets**. Staging : 80,760 s ; préparation : 35,142 s ; durée totale : 116,343 s. Pic mémoire processus : 66 764 800 octets. Disque temporaire : 416 903 168 octets pour le stage et 327 386 016 octets pour les paquets. Les 23 tests du nouveau module et les 97 régressions des adaptateurs passent ; les pannes injectées couvrent la transaction de staging et l'écriture d'un paquet.

## Acquisition et quotas : ce qui demeure séparé

Les archives du 21 octobre documentent 201 requêtes Exa, 831 identités distinctes et un arrêt après HTTP 429 ; 94 métadonnées directes avaient ensuite été récupérées, avant des refus natifs Instagram/TikTok. Ce sont des faits historiques, pas un diagnostic d’indisponibilité actuel. L’intégration principale a signalé une nouvelle sonde Exa fonctionnelle le 24 octobre et gère sa campagne séparément.

Le staging ne consomme aucun quota et n’utilise aucun secret. Les quotas, le coût et l’arrêt sur refus restent au niveau du fournisseur/collecteur. Le verrou d’un collecteur protège son répertoire, pas tous les processus indépendants : lancer plusieurs plans séparés exige un ordonnanceur partagé du fournisseur pour conserver les limites globales. Aucun contournement, cookie, proxy ou acteur payant n’est ajouté ici.

Pour viser un catalogue très large, mesurer séparément résultats bruts, identités uniques, nouveautés, preuves de langue française, candidats pédagogiques, références retenues après revue et liens encore disponibles. Les milliers de résultats d’une API ou d’un index ne sont pas des milliers de tutoriels validés. La langue audio et les droits restent inconnus lorsque seules les métadonnées le permettent.

## Preuves et références

- Skills lus : `[USER_HOME]/.codex/skills/agent-reach/SKILL.md`, ses références `video.md` et `search.md`, et `[USER_HOME]/.codex/skills/social-content-structure/SKILL.md`.
- Archives de collecte : `work/social-scale-2026-10-21/collection-final-report.json` et `outputs/focus-academy/research/collecte-sociale-2026-10-21.md`.
- Adaptateur d’exports autorisés : `work/social-alternative-2026-10-21/backend/PUBLIC_EXPORT.md`, avec ses références primaires déjà archivées ; ce présent audit ne réaffirme aucun ancien tarif.
- Sources de l’outillage existant : [Agent Reach](https://github.com/Panniantong/Agent-Reach), [yt-dlp](https://github.com/yt-dlp/yt-dlp), [Exa MCP](https://github.com/exa-labs/exa-mcp-server). Aucun nouvel appel à ces plateformes n’a été nécessaire pour cet audit local.
