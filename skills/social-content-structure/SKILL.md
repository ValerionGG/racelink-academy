---
name: social-content-structure
description: Structurer des publications Instagram, TikTok, Facebook et autres réseaux en titre, description, hashtags, mentions et liens distincts ; reformuler les titres encombrés pour un catalogue ou une application en préservant les preuves sources.
---

# Titres et légendes sociales

Transformer des métadonnées sociales en fiches lisibles : un titre qui annonce le sujet, une description qui explique le contenu, des hashtags séparés. S'applique à un export, une fiche ou un lot déjà accessible. La collecte et la publication dépendent de la demande en cours ; ce skill ne donne pas d'autorisation supplémentaire.

## Comprendre la source avant de réécrire

Inspecter les champs réels de quelques entrées, leur provenance et le format de leur collecteur. Le nom d'un champ ne prouve pas sa fonction : un extracteur peut fabriquer `title` avec les premiers caractères de `caption` ou `description`.

- Conserver un vrai titre natif utile lorsqu'il existe. Instagram et TikTok peuvent n'offrir qu'une légende ; il faut alors construire un titre de présentation distinct, sans prétendre qu'il vient de l'auteur.
- Ne pas découper systématiquement au premier `|` : « Renault Mégane 2 | Changer le filtre à air » contient le véhicule et l'action. Retirer les signatures ou enveloppes « By auteur », « Instagram », « TikTok » seulement lorsqu'elles sont identifiables.
- Un titre d'index est une preuve plus limitée qu'une légende directe. Les extraits composites de moteurs de recherche peuvent mêler recommandations et commentaires : ne pas les transformer en description du média cible.
- Une analyse du texte ne constitue ni un visionnage, ni une transcription, ni une confirmation de la langue audio ou de la compatibilité d'une pièce.

## Séparer les champs

Utiliser [scripts/social_metadata.py](scripts/social_metadata.py) pour le nettoyage déterministe. Le contrat et les exemples sont dans [references/fields.md](references/fields.md).

Conserver les textes originaux sans perte dans `source_metadata`, y compris les champs ambigus exclus de l'affichage. Produire séparément titre, description, hashtags, mentions et liens. Les hashtags sont ceux de la source, dédoublonnés ; les mots-clés éditoriaux éventuels appartiennent à un autre champ. Ne pas confondre `C#`, un numéro, une référence technique ou le fragment d'une URL avec un hashtag.

Préserver les paragraphes utiles de la description. Une description éditoriale existante et une légende source ne sont pas interchangeables : garder leur nature explicite. Ne pas remplir une description absente avec des étapes imaginées. Une extraction de titre ou une formulation minimale fondée sur le titre reste signalée comme telle.

## Écrire un titre clair et engageant

Le script prépare un candidat, il ne comprend pas la vidéo. Relire les cas `needs_title_review` et les titres longs, incomplets, vagues ou exagérés. La reformulation s'effectue à partir des seules preuves disponibles.

Préférer **action ou question précise + objet + véhicule ou contrainte utile**. Exemple : « Honda Accord VI (1997–2002) : où se trouve la prise OBD2 ? ». Conserver moteur, année, génération, partie du tutoriel et norme lorsqu'ils délimitent le contenu. Ne pas tronquer au milieu d'un code ou d'un nom pour atteindre une longueur fixe ; environ 50 à 100 caractères est une cible de lecture, pas une règle qui prime sur la précision.

Garder la langue de la source, sauf traduction demandée ; stocker une traduction séparément. Un titre engageant exprime le bénéfice réellement annoncé. Retirer les superlatifs et promesses non étayées (« garanti », « sans risque », « compatible avec toutes les voitures », « seuls 1 % savent »). Ne pas inventer de difficulté, durée ou économie. Les réserves importantes (« selon le modèle », intervention professionnelle) doivent rester accessibles dans la description.

Soumettre au helper une reformulation sous la forme `{title, basis}`. Conserver l'ancien titre, la raison et l'extrait source utilisé. Un nom présent seulement dans un hashtag peut rester dans les hashtags ; ne pas en déduire une application véhicule.

## Appliquer et vérifier

Pour un lot, préparer un aperçu avant/après puis vérifier les reformulations et les cas ambigus. L'aperçu n'implique pas une nouvelle demande de confirmation quand la correction est déjà autorisée.

Lors d'une migration, modifier les seuls champs de présentation et leurs métadonnées. Préserver identifiants, URL, auteur, langue, droits, transcriptions, badges et taxonomie de véhicule. Si le nouveau titre retire une preuve textuelle utilisée par un filtre, conserver cette preuve source dans son champ dédié ; ne pas recalculer silencieusement la compatibilité depuis le titre éditorial.

Vérifier l'idempotence, la conservation des originaux, les caractères Unicode, les titres techniques et la séparation réelle dans l'API, l'export et l'écran. Afficher les hashtags dans une zone dédiée de la fiche ; rendre le texte d'origine consultable sans encombrer le titre. N'afficher que des chaînes échappées et des liens validés.
