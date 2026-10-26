# Référentiel véhicule NHTSA vPIC

Cet outil prépare un vocabulaire de marques et modèles par année à examiner avant enrichissement des filtres de RaceLink. Il conserve les identifiants `Make_ID` et `Model_ID` renvoyés par la NHTSA, leurs libellés originaux et la provenance du résultat. Il ne modifie ni le catalogue, ni la base SQLite, ni l’interface.

L’API a été repérée dans [public-apis/public-apis](https://github.com/public-apis/public-apis), révision consultée `82e763edc4919e2cb13ce8c8c57a33bc73ff4caf`. Le contrat utilisé est la [documentation officielle NHTSA vPIC](https://vpic.nhtsa.dot.gov/api/), méthode `GetModelsForMakeYear`, vérifiée le 26 octobre 2026.

## Portée des résultats

- Référentiel américain fondé sur les déclarations constructeurs à la NHTSA. La couverture des véhicules français ou mondiaux n’est pas complète. Une absence ne signifie pas que le modèle n’existe pas.
- La recherche de marque est partielle (`LIKE`). Une réponse peut contenir plusieurs marques. Tous les résultats restent conservés ; `exact_make_name_match` ne compare que le nom normalisé, sans reconnaître d’alias.
- Aucun filtre de type de véhicule n’est appliqué : la réponse peut inclure voitures, motos et autres catégories. Un total d’entrées n’est pas un nombre de voitures particulières.
- L’année est celle demandée à l’API, pas une déduction à partir d’un véhicule observé. L’outil accepte 1996 à l’année courante + 1 ; la borne basse suit le contrat de cette méthode.
- Aucune requête VIN. Aucune garantie de compatibilité d’un tutoriel, d’un moteur ou d’une pièce. Aucune procédure de réparation ni référence d’huile ou de carburant ne provient de cette méthode.

## Utilisation depuis la racine du workspace

Aperçu sans réseau et sans écriture :

```powershell
python -B -X utf8 outputs/focus-academy/scripts/vehicle_reference.py --make Honda --year 2024 --output work/vehicle-reference/honda-2024
```

Collecte bornée à un GET HTTPS, uniquement avec `--execute` :

```powershell
python -B -X utf8 outputs/focus-academy/scripts/vehicle_reference.py --make Honda --year 2024 --output work/vehicle-reference/honda-2024 --execute
```

Le répertoire explicite doit être vide ou contenir le cache valide de cette même requête. Rejouer la commande réutilise un cache complet vérifié sans appel réseau. Changer de marque ou d’année exige un autre répertoire. Un cache incomplet ou altéré provoque un arrêt ; il n’est pas écrasé.

Fichiers produits après validation :

- `response.json` : octets JSON originaux du fournisseur.
- `reference.json` : requête, SHA-256, URL et date UTC de collecte, scope américain, champs normalisés et marqueur `completed`.

Le programme utilise seulement la bibliothèque standard Python : aucun compte, secret, cookie, proxy, abonnement, média téléchargé ou redirection. Délai socket de 20 secondes, configurable de 1 à 60 ; réponse limitée à 8 Mio. Aucun retry automatique. Les erreurs HTTP, formats incohérents, faux décomptes et identifiants invalides interrompent la collecte. Les résultats demandent une revue avant toute intégration métier.

## Vérification hors réseau

```powershell
python -B -X utf8 -m unittest discover -s outputs/focus-academy/scripts -p test_vehicle_reference.py -v
```

Les fixtures des tests sont fictives, marquées comme telles dans le code et ne sont jamais exportées dans RaceLink. Les tests vérifient notamment la conservation des identifiants, les correspondances partielles, la provenance, les limites HTTP, la réutilisation du cache et l’absence d’écrasement d’une autre requête.
