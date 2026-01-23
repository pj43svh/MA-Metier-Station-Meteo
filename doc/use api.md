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

[<-- retour au début](home)