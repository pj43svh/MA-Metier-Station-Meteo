## Comment utiliser insérer et lire des données dans la base de données ?

Le fichier [/database.py](/database.py) sert à créer la base de données et créer les tables pour les 2 esps à l'interrieure. Le programme n'est pas prévu pour avoir plus de capteurs. Les variables pour lire et écrire sont à l'interieur du même fichier


### add_data()

La fonction **add_data(**_table,value={}_**)** s'utilise avec les argument suivant

|Argument|Importance|Utilisation|
|-|-|-|
|table |Obligatoire|Indique le nom de la table|
|value |Optionnel|valeur en fomat json qui défini la colone et la valeur à attribuer. Exemple : value = {"temperature":12,3}. Si vide, aucune colone ne va se remplire.|

### read_data()

La fonction **read_data(**_table,column="*",where=None,order=None_) s'utilise avec les argument suivant

|Argument|Imoprtance|Utilisation|exemple|
|-|-|-|-|
|table|Obligatoire|Indique le nom de la table|"esp1"|
|column|Optionnel|Indique la colone à lire. Si non-défini, toute les colones.|column="temperature|
|where|Optionnel|Permet de prendre toutes les lignes avec une valeur identique (voice exemple) va donner toute les données qui ont la date 2026-01-12. On peut mettre ce qu'on veut pour autant qu'il soit compatible avec l'option where en sqlite.|where="'date'='2026-01-12'"|
|order|Optionnel|Permet de trier les données par ordre de colone, croissant ou décroissant et de limiter le nombre de données renvoyé.|id DESC / LIMIT 5|
