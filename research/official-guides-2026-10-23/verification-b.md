# Références constructeur — lot B

Vérification textuelle des pages officielles le 23 octobre 2026. Le lot contient **11 références directes pour 6 sujets**, toutes en français : Renault, Tesla et Volvo Cars. Le JSON associe chaque sujet à `sources[]`, avec une portée lisible dans `vehicleScope`.

Les sections ont été ouvertes et lues avec l’outil web ; les liens n’ont pas été retenus sur le seul statut HTTP ou sur un extrait de moteur de recherche. Les dates Renault sont retranscrites comme **périodes de notice affichées**, pas comme une date de fabrication décodée. Aucun fragment HTML n’a été inventé : `section` donne le repère exact à chercher sur la page.

## Limites à conserver dans l’interface

- Ces liens sont des sources constructeur, pas une certification des guides RaceLink ni une validation automatique de compatibilité.
- La procédure Tesla de remplacement de batterie est rédigée en français mais explicitement réservée à **l’Amérique du Nord**, pour une batterie **plomb-acide**. Le marché et la technologie doivent rester visibles. La lecture porte sur les préconditions et la première branche de dépose ; la notice complète doit être suivie pour toute intervention.
- Le guide OBD reçoit une référence Volvo **XC90 2025** sur la prise et les conditions d’utilisation. Ce n’est pas une procédure universelle d’effacement des codes ; aucune telle procédure n’a été inventée pour compléter le sujet.
- Les branches d’équipement, l’interdiction de généraliser les références de lampes/fusibles et la distinction entre entretien et reset sont conservées dans les résumés.
- Les exemples de distance/temps du tableau Renault ne sont pas repris comme échéancier d’entretien valable pour tous les moteurs.

## Références examinées puis non retenues

- [Ancien lien d’éclairage Clio 5](https://fr.e-guide.renault.com/fra/Clio-5-ph2/Eclairage-exterieur-remplacement-des-lampes) : redirection réelle vers l’accueil générique. Remplacé par la section directe du nouveau manuel.
- Ancien PDF Clio 4 phase 1 sur `fr.e-guide.renault.com` : réponse 404. La procédure Clio 4 phase 2 du nouveau portail est une source distincte, avec sa propre portée.
- PDF Clio 3 et Lincoln MKZ 2016 : sommaires accessibles, mais vérification de la section détaillée interrompue par des délais de récupération. Non intégrés au lot.
- [Prise OBD Volvo EX60 2027](https://www.volvocars.com/fr-ch/support/car/ex60/article/47d2c97fd33effd3c0a8cc3718c999b7-e1da020cd919ef8bc0a8cc37305f60cc-8664b2fa77a7e089c0a8296870d1a409/) : texte vérifié mais redondant avec le XC90 2025 sur le site France, retenu à sa place.

Les contenus amont ne sont pas recopiés en intégralité. Aucun code applicatif, catalogue ou fichier Git n’a été modifié par ce lot.
