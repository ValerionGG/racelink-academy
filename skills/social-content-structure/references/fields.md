# Champs et exemples

Le helper reçoit un dictionnaire de métadonnées. Les entrées peuvent être des champs déjà normalisés ou des champs de collecteurs (`title`, `caption`, `description`, `text`, `desc`, `metadata_json`). Examiner la provenance avant de lui confier un nouvel export : il ne remplace pas l'adaptateur propre à une API.

```python
from social_metadata import normalize_social_metadata
result = normalize_social_metadata(record, title_override={
    'title': 'Honda Accord VI (1997–2002) : localiser la prise OBD2',
    'basis': 'Reformulation du sujet, du modèle et des années explicitement cités.'
})
```

Le résultat contient :

| Champ | Usage |
|---|---|
| `title` | Titre de présentation, sans collage de légende ou hashtags |
| `description` | Corps descriptif nettoyé, jamais une transcription inventée |
| `hashtags` | Tags sources avec `#`, première casse conservée, doublons retirés |
| `mentions` | Comptes sources avec `@` |
| `links` | Liens présents dans les champs fiables |
| `needs_title_review` | Candidat incomplet ou ambigu demandant une décision éditoriale |
| `source_metadata` | Champs originaux conservés sans perte pour reprise ou contrôle |
| `field_provenance` | Origine et opérations appliquées à chaque champ |
| `normalization` | Version et informations de normalisation |

## Fournir des champs fiables

Les listes `hashtags`, `mentions` et `links` déjà séparées sont acceptées, dédoublonnées et conservées en provenance. Les champs source `url` et `source_url` sont archivés, sans être confondus avec les liens présents dans la légende.

Si `description` est un résumé rédigé par le catalogue, transmettre `description_type: "editorial_summary"` (ou `descriptionType` / `description_basis`) ; une légende native disponible peut rester dans `caption`. Les adaptateurs doivent préciser ce rôle : le helper ne peut pas le déduire du seul texte. Les extraits composites indexés restent exclus. Les entités HTML des textes sont décodées pour la lecture ; les URL et les sources originales restent intactes.

Un titre provisoire non vide peut encore être trop long : `needs_title_review` impose alors une décision éditoriale avant publication. Le helper ne remplace pas cette étape par une coupure arbitraire. Une entrée sans texte utile reste vide et demande une source exploitable.

## Exemples de décisions

**Légende directe** : « ⚙️ Comment passer la marche arrière sur boîte manuelle (exemple Skoda Fabia 2025) ? Sur ce modèle… #permis #conduite »

- Titre éditorial : « Škoda Fabia 2025 : engager la marche arrière ».
- Description : l'explication et les différences entre commandes selon le véhicule.
- Hashtags : `#permis`, `#conduite`.
- Ne pas déduire une carrosserie du mot « avant » dans « avant d'engager ».

**Titre natif utile** : « VW Golf 1.6 TDI : filtre à huile, partie 2 » et une description séparée.

Conserver le titre et la séparation native. Le point décimal de `1.6` ne termine pas une phrase ; « partie 2 » n'est pas du bruit à supprimer.

**Résultat indexé** : « Comment tester un fusible de voiture avec un multimètre | TikTok », avec un extrait qui décrit ensuite d'autres vidéos.

Garder le sujet du titre ; exclure l'extrait composite de la description et des hashtags affichés. La description peut rester vide. Ne pas écrire des étapes de mesure qui ne figurent pas dans les preuves.

**Texte composite Facebook** : « Réglage du retour de force | Explication… | By Auteur ».

Séparer sujet, corps et signature avec leurs provenances. Si le milieu n'est qu'un extrait indexé non attribuable au média, le conserver en archive et ne pas l'afficher comme légende vérifiée.

## Hors du helper

Une plateforme, un collecteur ou une API peut changer ses noms de champs. Le skill n'impose pas de schéma officiel figé. Les recherches et scrapers éventuels doivent fournir leurs propres preuves et respecter leurs limites d'accès. Aucun compte, abonnement, cookie ou clé n'est requis pour normaliser un export local.

Pour RaceLink, le titre éditorial ne remplace pas les preuves automobiles conservées et les hashtags ne deviennent pas des garanties de compatibilité. La présentation peut utiliser un résumé éditorial existant, une légende nettoyée et un volet « Texte d'origine », chacun clairement identifié.
