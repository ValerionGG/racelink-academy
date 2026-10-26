# Collecte sociale par CUA — protocole et conversion locale

Version du protocole : 26 octobre 2026. Ce workflow complète les exports API/Apify et la découverte par index. Il ne remplace pas leurs accès ni leurs quotas. Le navigateur est piloté uniquement par **CUA**, par l'agent qui en a la responsabilité ; le helper Python ne pilote aucun navigateur.

## État réellement observé

Lors du contrôle CUA de ce tour, le parent a observé :

- TikTok : profil `/@maclede12` visible, mais flux et recherche « tuto mécanique » en erreur serveur.
- Instagram : grille `/norautofr/` accessible, 12 cartes (8 liens Reels, 4 publications observées comme images). Ouvrir un Reel ou « Afficher plus » demande une connexion.

Ces observations ne donnent **aucune légende native complète**. Le convertisseur a lu hors ligne la capture existante `browser/norautofr-public-grid.json` : 12 identités, 12 à documenter, 0 export de légende. La capture héritée ne contient pas un champ de type média observé : le helper conserve donc `unknown`, même pour les 4 images identifiées visuellement par le parent. Il ne transforme pas « Photo by… » en preuve de format ou de langue audio.

## 1. Ouvrir une fenêtre de collecte bornée

L'agent CUA lit la documentation fournie par l'outil et sélectionne l'onglet approprié. En reprise après compaction, il restaure d'abord cette documentation. Il utilise les contrôles et lectures de page officiellement exposés par CUA.

- Une fenêtre : jusqu'à **3 profils ou 30 pages de détail**, et au plus **10 minutes**, au premier seuil atteint. Ce sont nos bornes de travail, pas des quotas officiels de plateforme.
- Un seul agent contrôle l'onglet. Aucun autre collecteur natif en parallèle.
- N'utiliser que des profils et liens déjà observés. La file ne doit pas inventer d'URL à partir d'un pseudo supposé.
- Départ au profil, lecture de la grille actuellement rendue, au plus deux actions de défilement/« plus » par profil si elles sont accessibles. Pas de boucle infinie de scroll.
- Laisser la navigation terminer ; espacer les ouvertures d'au moins 2 secondes. Un signal de limite prévaut sur ce rythme et sur tous les objectifs de volume.

**Interdits dans ce workflow :** OpenCLI, Playwright/Puppeteer externe, requête `fetch`/XHR cachée, inspection du trafic pour rejouer une API, état React ou objets d'hydratation, lecture de cookies/localStorage, session ou token, installation d'extension, accès privé, téléchargement média. Aucune tentative de changement d'IP ou d'identité.

## 2. Capturer la grille sans inventer de contenu

Depuis les cartes effectivement rendues, relever seulement :

- lien direct de publication, après observation de son `href` ;
- texte visible lié à la carte dans `grid_text` ;
- attribut alternatif de son image dans `grid_alt`, en le gardant explicitement comme **alt** ;
- format `video`, `image`, `carousel` seulement si le contrôle ou le rendu le prouve ; sinon `unknown`.

Ne pas conserver les URL CDN, les sources vidéo, les profils de personnes, les commentaires, suggestions, publications voisines ou statistiques. Le lien de grille n'est pas une preuve que le détail ou sa légende est accessible. Un alt généré automatiquement ne devient ni titre, ni légende, ni résumé pédagogique.

Sauvegarder un fichier JSON par observation, avec l'URL de la page et l'heure réelle de capture ISO avec fuseau. Une capture de grille accepte au plus 50 éléments. Le helper reconnaît aussi la forme historique `visible_dom_grid` et **jette les champs image.src sans les consulter** ; les autres champs inconnus sont refusés.

## 3. Ouvrir les détails accessibles

Pour les liens vidéo non encore documentés dans `needs-detail.json`, ouvrir le détail par une action CUA normale. Vérifier que l'URL de la page correspond à la publication choisie et que le compte/publication n'est pas privé.

Relever séparément : auteur visible, éventuel véritable titre de publication, texte de **la légende de cette publication**, date seulement si affichée sans ambiguïté. Ouvrir le bouton visible « plus » de la légende lorsqu'il existe. Si le texte est encore tronqué, utiliser `caption_status: "partial"`. Le texte d'une page entière, mêlant commentaires ou recommandations, n'est jamais une légende complète.

`caption_status: "complete"` est une déclaration de l'agent après lecture du texte développé. Le helper ne peut pas authentifier cette déclaration à partir du JSON. Ne pas déduire la langue audio du texte ; ne pas ajouter de transcription ou de validation technique. Ne pas réécrire les titres/légendes dans la capture.

## 4. Arrêter et reprendre honnêtement

- Login, CAPTCHA, 403, 429, refus, message de limite : arrêter cette plateforme et enregistrer un événement sans items. Aucun autre endpoint ou outil natif n'est essayé en remplacement.
- Erreur serveur ou chargement bloqué : arrêter la fenêtre et conserver `server_error`, sans déclarer une grille vide réussie.
- Profil/publication privé : aucune collecte ; `access: "private"`, `items: []`.
- La connexion éventuelle reste une action de l'utilisateur dans l'interface. La collecte ne reprend qu'après restauration d'accès constatée et instruction de reprise ; elle ne capture ni écran d'identifiants ni données de compte.
- Après authentification, seules les publications publiques restent dans le périmètre. « Visible au compte connecté » ne signifie pas « public ».

Le fichier `checkpoint.json` enregistre les captures traitées et leurs empreintes. Il ne donne aucun droit de reprise réseau et ne lève pas les blocages. `observed_stops` les conserve pour l'opérateur ; le helper ne fait aucune requête.

## 5. Contrat JSON strict

Exemple **synthétique** de détail ; remplacer seulement par des valeurs réellement observées :

```json
{
  "version": 1,
  "kind": "CUA_SOCIAL_CAPTURE",
  "source_url": "https://www.instagram.com/reel/Fixture0001/",
  "captured_at": "2026-01-01T12:00:00Z",
  "surface": "post_detail",
  "access": "public",
  "items": [{
    "url": "https://www.instagram.com/reel/Fixture0001/",
    "media_kind": "video",
    "creator": "Créateur test",
    "visible_title": "",
    "caption": "Fixture : légende effectivement visible, sans commentaires.",
    "caption_status": "complete",
    "evidence_note": "Légende développée dans le détail de cette publication."
  }]
}
```

- `surface` : `profile_grid` ou `post_detail` ; l'URL doit correspondre.
- `access` : `public`, `login_required`, `rate_limited`, `server_error`, `private`, `unavailable`.
- `media_kind` : `video`, `image`, `carousel`, `unknown`.
- `caption_status` : `complete`, `partial`, `unavailable`.
- En grille : `grid_text`/`grid_alt`, jamais `caption`/`visible_title` ; statut `unavailable`.
- Une page de détail contient au plus un item de même identité ; un refus contient zéro item.
- Champs optionnels : `creator`, `visible_title`, `grid_alt`, `grid_text`, `caption`, `published_at`, `evidence_note`. Aucun `language`, cookie, commentaire, HTML brut ou médiaURL.
- `published_at` exige lui aussi une date précise avec fuseau. Omettre « il y a trois jours » plutôt que calculer une date approximative.

## 6. Convertir localement

Depuis la racine du workspace, aperçu sans écriture :

```powershell
python outputs/focus-academy/scripts/browser_social_capture.py work/scale-v25/browser/norautofr-public-grid.json --output work/scale-v25/browser-capture-review
```

Ajouter `--execute` pour écrire les snapshots. Ajouter `--resume` pour ajouter de nouvelles captures après contrôle des empreintes. La conversion vérifie les captures précédentes, les anciens artefacts et le code du helper ; elle refuse les sources altérées. Limites : 2 MiB par capture, 200 captures par campagne, 50 cartes par grille. Clore la campagne avant d'en commencer une autre ; ne pas multiplier des campagnes pour outrepasser un blocage.

Chaque exécution complète crée un répertoire immuable `snapshots/<id>/` :

- `observations.json` : projection sûre et hash du fichier CUA original ; aucun lien CDN archivé dans cette projection.
- `needs-detail.json` : liens de grille, légendes partielles et contradictions entre légendes complètes, avec preuves.
- `excluded.json` : images/carrousels, observations privées ou formats contradictoires.
- `<platform>/publications.json` et `manifest.json` : uniquement les détails publics explicitement vidéo dont une légende complète a été observée. Un manifeste absent signifie zéro ligne admissible de cette plateforme.
- `report.json` : nombres exacts et événements d'arrêt ; `checkpoint.json` ne référence que les snapshots terminés.

L'identité Instagram déduplique les formes `/auteur/reel/ID/` et `/reel/ID/`. Les URLs observées, les variantes textuelles et leurs preuves restent distinctes. Des légendes complètes divergentes demandent une revue ; le helper n'en sélectionne pas arbitrairement une. Une preuve de média non vidéo ou privé prévaut sur une variante vidéo.

Les manifestes sont compatibles avec le helper existant `public_export.py` (`schema: generic`, `kind: provider_export`) :

```powershell
python outputs/focus-academy/scripts/public_export.py CHEMIN_DU_MANIFEST --output DOSSIER_DE_REVUE_NEUF --max-records 5000
```

Cette étape prépare des **candidats**, une quarantaine et une liste d'approbation vide. Elle n'importe rien. Les contrôles métier (tutoriel réel annoncé, absence de promotion, langue estimée, limites automobiles, titre éditorial et droits inconnus) restent nécessaires. Le helper CUA ne transmet pas un statut « expert », une licence ouverte ou un badge.

## Validation et limites

Tests offline : `python -m unittest tests_browser_social_capture -v` depuis `outputs/focus-academy` ; fixtures entièrement synthétiques, compatibilité du manifeste testée sans DB. Un essai séparé a utilisé la vraie grille locale de 12 cartes fournie par CUA, sans rouvrir le site.

Ce composant automatise la validation, les empreintes, les files de détails, la déduplication et la préparation d'exports. **Il ne promet pas des milliers de légendes via une grille bloquée.** Le débit de la partie navigateur dépend de l'accès visible réellement disponible et des limites de la plateforme. L'accès et les conditions de réutilisation d'une légende/vidéo restent des questions distinctes.
