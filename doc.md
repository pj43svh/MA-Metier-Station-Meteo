# DOCUMENTRATION

## Installation

### 1. Cloner le répertoire git

``` bash
git clone https://github.com/pj43svh/MA-Metier-Station-Meteo.git
```
### 2. Installer les dépendence

vous aurez besoin de :
- Flask
- matplotlib
- Numpy

``` bash
pip install flask
pip install matplotlib
pip install numpy
```

### 3. Modifier le programme pour connecter les différents modules

- Changer les accès internet

    __important__

    ``` C++
    // ==================== CONFIGURATION WiFi ====================
    const char* WIFI_SSID = "Wifi_ssid";
    const char* WIFI_PASSWORD = "wifi_password";

    // ==================== CONFIGURATION Serveur Local (Raspberry Pi) ====================
    const char* RASPBERRY_IP = "10.244.96.106";  // A modifier selon votre Raspberry Pi
    const int RASPBERRY_PORT = 5000;
    const bool USE_LOCAL_SERVER = true;  // Mettre false pour desactiver
    ```

- Le nom de l'appareil connecté
    __Ces chamgement sont optionnels__

    ligne 26
    ``` python
    if name == "Atom_001": # changer avec le nom de votre esp
            name = "esp1"
        elif name == "Atom_002": # pareil ici avec un autre esp
            name = "esp2"
        else :
            print("Wrong device name : ", name)
            return
    ```
    qui doit être identique au C++ :

    ligne 44
    ``` C++
    // ==================== CONFIGURATION Capteur ====================
    const char* CAPTEUR_ID = "ATOM_001";  // Identifiant unique de ce capteur
    ```

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

## Fonctionnement des API

Dans ce projets, nous utilisons des api pour communiquer entre le serveur web et la page web. Toute les api se trouve dans le fichier [`/api.py`](/api.py)

### Comment s'en servir ?

Dans un fichier JavaScript, copier ce script :

``` javascript
const url = `/api/requete_api`; // <-- remplacer le "requete_api" par la route de la requête
const response = await fetch(url);
```

Puis dans le fichier api.py vous allez envoyer une réponse à la demande :

```python
@api.route("/requete_api")
def api_requete_api():
    result = var # exemple : remplacer par api_data() pour prendre la dernière donnée de la DB
    return result
```

### Fonction api_data et api_datas_list

**api_data()** :
> Pour obtenir la dernière donnée d'une colone d'une table, utiliser `api_data(colone1)` où "colone" correspond à la **colone** et "1" correspond à la table (esp**1**)

**api_datas_list()** :
> Pour obtenir une liste de donnée, utiliser `api_datas_list(colone1, limit=24, date_filter="today")` où "colone" correspond à la **colone** et "1" correspond à la table (esp**1**). La **limit** est le nombre de donnée que la liste va contenir en partant de la fin. Le filtre de **date_filter** va retourner uniquement les données avec la date séléctionnée. *"today"* va prendre les dernières données, dans leur ordre d'ajour dans la base de données.

### Method Get

Pour appeler l'API avec des paramètre, nous utilisons la method get dans notre code

```javascript
var = argument // vous pouvez mettre d'argument que voulez appeler
const url = `/api/requete_api?argument=${var}`; // <-- remplacer le "requete_api" par la route de la requête
// on peut mettre plusieurs arguments : /api/requete_api?argument1=${var1}?argument2=${var2}
const response = await fetch(url);
```

Dans le python, c'est presque pareil mais on doit ajouter de quoi récupérer les arguments grace à la method get

``` python
@api.route("/requete_api", methods=["GET"])
def api_requete_api():
    argument = request.args.get("argument",type=str) # on va récupérer l'argument et le formater en str (on peut aussi en int/float)
    result = function(argument) # exemple : remplacer par api_data() pour prendre la dernière donnée de la DB
    return result
```