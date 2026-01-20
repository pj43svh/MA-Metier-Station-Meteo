from flask import jsonify,Blueprint,request
import database as db
from statistical import create_graph_bar,create_graph_line

api = Blueprint("api",__name__)




###############################################################################
##########################___PARTIE DEDIEE A L'API___##########################
###############################################################################


def api_data(type_str):
    # Extraire colonne et device_id
    col = type_str[:-1]
    device_name = "esp"+type_str[-1]

    # Colonnes autorisées
    ALLOWED_COLUMNS = {"temperature", "humidity", "pressure"}

    if col not in ALLOWED_COLUMNS:
        return "Colonne non autorisée"

    # Requête : dernière valeur pour ce device_id, triée par date_heure DESC
    results = db.read_data(
        device_name,
        column=col,
        order=f"id DESC LIMIT 1"
    )

    if results and len(results) > 0:
        value = results[0][0]  # Premier tuple, première colonne
        return str(value) if value is not None else "NULL"
    else:
        return "Aucune donnée"
    
def api_datas_list(type_str, limit=24,date_filter="today"):
    """Retourne une liste des dernières valeurs pour une colonne"""
    if type_str == "hour":
        col = "hour"
        device_name = "esp1"
    elif type_str == "date":
        col = "date"
        device_name = "esp1"
    else:
        col = type_str[:-1]
        device_name = "esp"+type_str[-1]

    ALLOWED_COLUMNS = {"temperature", "humidity", "pressure", "date", "hour"}

    if col not in ALLOWED_COLUMNS:
        return []

    # ✅ Tri par id DESC (du plus récent au plus ancien)
    if date_filter == "today":
        results = db.read_data(
            device_name,
            column=col,
            order=f"id DESC LIMIT {limit}"
        )
    else :
        try:
            results = db.read_data(
            device_name,
            column=col,
            where=f"date = '{date_filter}'",
            order=f"id DESC LIMIT {limit}"
        )
        except:
            print("Wrong date :",date_filter)
            return
    if not results:
        return []
    

    values = [row[0] for row in results]
    return values[::-1]  # Ne pas inverser — tu veux du plus récent au plus ancien


# exemple d'utilisation
# temp = api_data("temperature1")

##########################___API POUR LES DONNEES___###########################

@api.route("/temperature1")
def api_temperature1():
    temp = api_data("temperature1")
    return temp

@api.route("/pressure1")
def api_pressure1():
    try:
        pressure = api_data("pressure1")
    except:
        pressure = "X"
    return str(pressure)

@api.route("/humidity1")
def api_humidity1():
    try:
        humidity = api_data("humidity1")
    except:
        humidity = "X"
    return str(humidity)

@api.route("/temperature2")
def api_temperature2():
    try:
        temp = api_data("temperature2")
    except:
        temp = "X"
    return str(temp)

@api.route("/pressure2")
def api_pressure2():
    try:
        pressure = api_data("pressure2")
    except:
        pressure = "X"
    return str(pressure)

@api.route("/humidity2")
def api_humidity2():
    try:
        humidity = api_data("humidity2")
    except:
        humidity = "X"
    return str(humidity)


##########################___API POUR L'HISTORIQUE___###########################


@api.route("/dates_unique")
def get_dates_unique():
    """
    Retourne la liste des dates uniques (sans doublons) de la table weather_data
    """
    # Utiliser DISTINCT pour ne pas avoir de doublons
    results = db.read_data(
        "esp1",
        column="DISTINCT date"
    )

    if not results:
        return jsonify([])

    # Extraire les valeurs
    dates = [row[0] for row in results if row[0] is not None]

    return jsonify(dates[::-1])

@api.route('/history1', methods=["GET"])
def get_history1():
    try :
        selected_date = request.args.get("date",type=str)
    except:
        selected_date = "today"
    date_list = api_datas_list("date", limit=24, date_filter=selected_date)
    hour_list = api_datas_list("hour", limit=24, date_filter=selected_date)
    temp_list = api_datas_list("temperature1", limit=24, date_filter=selected_date)
    hum_list = api_datas_list("humidity1", limit=24, date_filter=selected_date)
    press_list = api_datas_list("pressure1", limit=24, date_filter=selected_date)

    return jsonify({
        "date": date_list,
        "hour": hour_list,
        "temperature": temp_list,
        "humidity": hum_list,
        "pressure": press_list
    })



@api.route('/history2',methods=["GET"])
def get_history2():
    try :
        selected_date = request.args.get("date",type=str)
    except:
        selected_date = "today"
    
    date_list = api_datas_list("date", limit=24, date_filter=selected_date)
    hour_list = api_datas_list("hour", limit=24, date_filter=selected_date)
    temp_list = api_datas_list("temperature2", limit=24, date_filter=selected_date)
    hum_list = api_datas_list("humidity2", limit=24, date_filter=selected_date)
    press_list = api_datas_list("pressure2", limit=24, date_filter=selected_date)

    return jsonify({
        "date": date_list,
        "hour": hour_list,
        "temperature": temp_list,
        "humidity": hum_list,
        "pressure": press_list
    })

@api.route("/statistical_refresh", methods=["GET"])
def refresh_statistical():
    try :
        selected_date = request.args.get("date",type=str)
    except:
        selected_date = "today"

# génèration des graphiques quand la page est appelée
    create_graph_line(["temperature1","temperature2"],"hour",label_x="Hours",label_y="°C",line_title=["Sensor 1","Sensor 2"],title="Temperatures", color =["tab:blue","tab:red"],date=selected_date)
    create_graph_line(["pressure1","pressure2"],"hour",label_x="Hours",label_y="hPa",line_title=["Sensor 1","Sensor 2"],title="Pressures", color =["tab:blue","tab:red"],date=selected_date)
    create_graph_bar(["humidity1","humidity2"],"hour",label_x="Hours",label_y="%",bar_title=["Sensor 1","Sensor 2"],title="Humidity levels", color =["tab:blue","tab:red"],date=selected_date)
