## [Installation](installation)


## [Comment utiliser l'api](use%20api.md)



## Fonctionnement du code
```
Station meteo/
│
├── app/
│   ├── main.py                         # fichiers principales qui lance le site internet et qui gère les autres script
│   ├── routes.py                       # script qui gère les chemin pour afficher les bonnes pages
│   ├── api.py                          # fichier qui va lire la db et qui va envoyer les données
│   ├── database.py                     # script qui gère la création de la db, l'envoit et la lecture
│   ├── esp.py                          # script qui sert à récuperer et envoyer les données dans la DB
│   ├── statistical.py                  # fichier qui gère la génération de graphique
│   ├── weather_data.db                 # base de données
│   ├── templates/                      # dosseier avec toute les pages webs
│   │   ├── index.html
│   │   ├── about.html
│   │   ├── history.html
│   │   └── statistical.html
│   └── static/                         
│       ├── graph_Humidity levels.png   # graphique
│       ├── graph_Pressures.png         # graphique
│       ├── graph_Temperatures.png      # graphique
│       ├── icone.png                   # icone du site internet
│       ├── style.css                   # fichiers css pour rendre la page jolie
│       └── js/
│           ├── data.js                 # Fichier qui actualise les données sur la pagfe d'accueil
│           ├── history.js              # Fichier qui actualise l'historique en fonction de la date
│           └── statistical.js          # Fichier qui gère les graphiques en fonction de la date

```

***

description détaillée de chaque fichier :

- `main.py` : Au lancement du programme, le fichiers `main.py` va lancer le serveur et va initialisé les blueprint. Les blueprints serevnt à séparer les différentes parties de l'application. Par exemple : quand on va sur /api/quelquechose, ça va aller dans `api.py` puis sur les routes définies dans là bas.



- `route.py` : Quand l'utilisateur va vouloir se connecter à une page (/about), le serveur web va lui afficher la page `about.html`

- `api.py` : Dans ce fichier, on va prendre les requête /api/qqch, pour aller dans la db et renvoyer la données demandée

- `database.py` : Ce script crée un base de données si elle n'existe pas et va ajouter les tables. Elle gère aussi l'ajout et la lecture de données.

- `esp.py` : Fichier qui gère requête http de l'esp pour recolter les donneés et les incrire dans la DB

- `statiscal.py` : Script qui gère la création de graphique.

- `weather_data.db` : Base de données sqlite

- `/static/js/data.js` : Fichiers qui permet d'actualiser les données affichées sur la page en interrogeant la base de donnée.

- `/static/js/history.js` : Fichiers qui permet d'actualiser l'historique sur la page en fonction de la date avec une liste déroulante, en interrogeant la base de donnée.

- `/static/js/statistical.js` : Fichiers qui permet de modifier le jour auquel les graphiques font référence à l'aide d'une option déroulante.

- `/template/...` : Dossier qui contient toutes les pages.