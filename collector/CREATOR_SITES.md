# Collecter des références sur les sites des créateurs

Le script `scripts/creator_site_collect.py` lit uniquement une liste explicite de pages de créateurs ou d’éditeurs. Il extrait les liens vers des publications Instagram/TikTok, leur texte d’ancre et leur contexte local. **Il ne consulte jamais ces publications sociales, ne télécharge aucun média et n’importe rien dans le catalogue.**

## Deux commandes

Depuis le dossier `collector`, pour relire une page déjà archivée, sans réseau :

```powershell
python scripts/creator_site_collect.py extract --html work/page.html --source-url https://younespratik.fr/ --output work/creator-offline-new.json
```

Pour un prochain relevé de pages explicitement choisies, avec un nouveau nom de sortie :

```powershell
python scripts/creator_site_collect.py collect --seed https://younespratik.fr/ --allow-host younespratik.fr --known-ids work/known-social-ids.json --max-pages 1 --delay 2 --max-bytes 2000000 --timeout 15 --output work/creator-public-pages-new.json
```

Un pilote réel a été exécuté une fois sur ce seed avec max-pages=1 et un délai de 1 seconde : robots.txt puis accueil, deux réponses HTTP 200, 7 identités TikTok extraites, aucune erreur et aucun import. Aucun lien social n’a été suivi. Les snapshots de sortie existants ne sont jamais écrasés.

## Garanties et limites

- Seuls les seeds sont visités, sans découverte automatique de pages, pagination ou suivi de liens. Les redirections ne sont pas suivies.
- HTTPS, port 443 et hôtes exacts explicitement autorisés ; pas de credentials dans l’URL, pas de proxy/session/cookie.
- Les hôtes Instagram/TikTok et leurs CDN répertoriés sont refusés, même si quelqu’un les ajoute à l’allowlist.
- Toutes les adresses DNS doivent être publiques. La connexion TLS utilise ensuite une IP numérique prévalidée, avec vérification du certificat pour le nom d’hôte d’origine. Cela évite une seconde résolution DNS au moment de la connexion.
- Les erreurs 401/403/429, les règles robots défavorables et les réponses inattendues arrêtent les requêtes à cet hôte. Aucun réessai ou changement de fournisseur.
- Limites : 1–100 pages explicites, 1–60 secondes de timeout, 1 Ko–5 Mo par réponse et au moins 0,5 seconde entre requêtes. Les délais robots supérieurs à 60 secondes entraînent un arrêt, pas une attente prolongée. Un hôte ajoute au maximum une lecture robots ; le maximum de requêtes est donc deux fois le nombre de seeds.
- Les corps de réponse audio, vidéo ou image sont refusés avant lecture. Aucun script distant ni iframe n’est exécuté.
- Les profils et URL courtes sont ignorés. Un lien Instagram `/p/` reste de type inconnu : il peut représenter une image ou un carrousel.
- Les doublons sont regroupés par identité média, avec toutes les occurrences conservées. `--known-ids` retire les identités déjà présentes à partir d’une liste JSON ; le collecteur ne lit pas la DB.

## Sortie et raccordement à la préparation

La sortie est un objet `review_queue_not_an_import` avec les requêtes, pages, erreurs et `candidates`. Chaque occurrence contient l’URL source, son SHA-256, le `href` canonique sans query/fragment, le texte d’ancre brut/normalisé et au maximum 600 caractères du bloc voisin. Une URL sociale affichée dans le texte est également nettoyée ; le SHA relie la preuve au HTML d’origine. Ce contexte n’est **jamais une légende native**. La langue audio, la licence et la disponibilité de la publication restent inconnues.

Pour le préparateur local `scripts/public_export.py`, mapper uniquement `url`, `title` (le libellé conservé) et les champs réellement démontrés. Choisir `source.kind=indexed_export`, `schema=generic`, et garder `caption` vide. Conserver séparément les `occurrences` comme preuve. Ne pas transférer automatiquement les modèles d’une longue page au véhicule de chaque vidéo. L’étape éditoriale distingue tutoriel, annonce produit, publicité et sujet hors périmètre avant toute approbation.

Le relevé initial Younes fournit un exemple concret : une référence GPS VW proposée et une référence FAP/Topdon gardée en quarantaine. Les scripts d’exploration manuels de ce pilote sous `work/` documentent les observations initiales ; utiliser ce collecteur borné, avec contrôle robots et réseau, pour de futurs relevés.

## Validation

19 tests hors réseau passent : canonicalisation, identité média, profils/shortlinks, ancre et contexte, nettoyage des paramètres des liens sortants, credentials, hôtes exacts, réseaux privés IPv4/IPv6 et réponses DNS mixtes, robots, 403/429, redirections, refus de médias avant lecture, limites et déduplication. Extraction réelle du HTML Younes archivé réussie : 13 occurrences, correspondant à 7 identités TikTok avant sélection éditoriale. Aucune des occurrences n’a été importée automatiquement.

```powershell
python -m unittest discover -s tests -p test_creator_site_collect.py -v
```
