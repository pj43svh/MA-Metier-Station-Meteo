from flask import jsonify,Blueprint,request
import database as db
from statistical import create_graph_bar,create_graph_line

api = Blueprint("api",__name__)


###############################################################################
#######################___NOUVELLE API DYNAMIQUE___############################
###############################################################################

@api.route("/sensors")
def get_sensors():
    """
    Retourne la liste de tous les capteurs enregistres.
    Exemple: {"sensors": ["esp1", "esp2", "esp3"], "count": 3}
    """
    sensors = db.get_all_sensors()
    return jsonify({"sensors": sensors, "count": len(sensors)})


@api.route("/sensors/status")
def get_sensors_status():
    """
    Retourne le statut de tous les capteurs avec leur derniere activite.
    Un capteur est considere "online" s'il a envoye des donnees dans les 2 dernieres minutes.
    """
    from datetime import datetime, timedelta

    sensors_status = db.get_all_sensors_status()
    result = []

    now = datetime.now()

    for sensor in sensors_status:
        sensor_info = {
            "id": sensor["name"],
            "number": sensor["name"].replace("esp", ""),
            "last_date": None,
            "last_hour": None,
            "status": "offline",
            "status_text": "Jamais connecte"
        }

        if sensor["last_activity"]:
            last_date = sensor["last_activity"]["date"]
            last_hour = sensor["last_activity"]["hour"]
            sensor_info["last_date"] = last_date
            sensor_info["last_hour"] = last_hour

            # Calculer si le capteur est online (derniere activite < 2 minutes)
            try:
                last_datetime = datetime.strptime(f"{last_date} {last_hour}", "%Y-%m-%d %H:%M:%S")
                diff = now - last_datetime

                if diff.total_seconds() < 120:  # 2 minutes
                    sensor_info["status"] = "online"
                    sensor_info["status_text"] = "En ligne"
                elif diff.total_seconds() < 300:  # 5 minutes
                    sensor_info["status"] = "recent"
                    sensor_info["status_text"] = f"Vu il y a {int(diff.total_seconds() // 60)} min"
                else:
                    sensor_info["status"] = "offline"
                    minutes = int(diff.total_seconds() // 60)
                    if minutes < 60:
                        sensor_info["status_text"] = f"Hors ligne ({minutes} min)"
                    elif minutes < 1440:
                        sensor_info["status_text"] = f"Hors ligne ({minutes // 60}h)"
                    else:
                        sensor_info["status_text"] = f"Hors ligne ({minutes // 1440}j)"
            except Exception as e:
                sensor_info["status_text"] = f"Derniere activite: {last_hour}"

        result.append(sensor_info)

    return jsonify({"sensors": result, "count": len(result), "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")})


@api.route("/sensor/<int:sensor_id>/latest")
def get_sensor_latest(sensor_id):
    """
    Retourne les dernieres valeurs d'un capteur.
    Exemple: /api/sensor/1/latest -> donnees du capteur esp1
    """
    table_name = f"esp{sensor_id}"

    # Verifier si le capteur existe
    if table_name not in db.get_all_sensors():
        return jsonify({"error": f"Capteur {sensor_id} non trouve"}), 404

    try:
        temp = db.read_data(table_name, column="temperature", order="id DESC LIMIT 1")
        hum = db.read_data(table_name, column="humidity", order="id DESC LIMIT 1")
        press = db.read_data(table_name, column="pressure", order="id DESC LIMIT 1")
        date = db.read_data(table_name, column="date", order="id DESC LIMIT 1")
        hour = db.read_data(table_name, column="hour", order="id DESC LIMIT 1")

        return jsonify({
            "sensor": sensor_id,
            "temperature": temp[0][0] if temp else None,
            "humidity": hum[0][0] if hum else None,
            "pressure": press[0][0] if press else None,
            "date": date[0][0] if date else None,
            "hour": hour[0][0] if hour else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/sensor/<int:sensor_id>/history")
def get_sensor_history(sensor_id):
    """
    Retourne l'historique d'un capteur.
    Parametres optionnels: ?date=2026-01-22&limit=50
    """
    table_name = f"esp{sensor_id}"

    if table_name not in db.get_all_sensors():
        return jsonify({"error": f"Capteur {sensor_id} non trouve"}), 404

    selected_date = request.args.get("date", type=str)
    limit = request.args.get("limit", default=50, type=int)

    try:
        if selected_date:
            where_clause = f"date = '{selected_date}'"
            temp = db.read_data(table_name, column="temperature", where=where_clause, order=f"id DESC LIMIT {limit}")
            hum = db.read_data(table_name, column="humidity", where=where_clause, order=f"id DESC LIMIT {limit}")
            press = db.read_data(table_name, column="pressure", where=where_clause, order=f"id DESC LIMIT {limit}")
            dates = db.read_data(table_name, column="date", where=where_clause, order=f"id DESC LIMIT {limit}")
            hours = db.read_data(table_name, column="hour", where=where_clause, order=f"id DESC LIMIT {limit}")
        else:
            temp = db.read_data(table_name, column="temperature", order=f"id DESC LIMIT {limit}")
            hum = db.read_data(table_name, column="humidity", order=f"id DESC LIMIT {limit}")
            press = db.read_data(table_name, column="pressure", order=f"id DESC LIMIT {limit}")
            dates = db.read_data(table_name, column="date", order=f"id DESC LIMIT {limit}")
            hours = db.read_data(table_name, column="hour", order=f"id DESC LIMIT {limit}")

        return jsonify({
            "sensor": sensor_id,
            "temperature": [r[0] for r in temp][::-1],
            "humidity": [r[0] for r in hum][::-1],
            "pressure": [r[0] for r in press][::-1],
            "date": [r[0] for r in dates][::-1],
            "hour": [r[0] for r in hours][::-1]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/all/latest")
def get_all_latest():
    """
    Retourne les dernieres valeurs de TOUS les capteurs.
    Utile pour le dashboard.
    """
    sensors = db.get_all_sensors()
    result = {}

    for sensor in sensors:
        sensor_num = sensor.replace("esp", "")
        try:
            temp = db.read_data(sensor, column="temperature", order="id DESC LIMIT 1")
            hum = db.read_data(sensor, column="humidity", order="id DESC LIMIT 1")
            press = db.read_data(sensor, column="pressure", order="id DESC LIMIT 1")

            result[sensor] = {
                "temperature": temp[0][0] if temp else None,
                "humidity": hum[0][0] if hum else None,
                "pressure": press[0][0] if press else None
            }
        except:
            result[sensor] = {"temperature": None, "humidity": None, "pressure": None}

    return jsonify(result)


###############################################################################
##########################___PARTIE DEDIEE A L'API___##########################
###############################################################################


def api_data(type_str):
    """Retourne la dernière valeur pour une colonne"""
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
    
def api_datas_list(type_str, limit=100,date_filter="today"):
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

    # Tri par id DESC (du plus récent au plus ancien)
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
    date_list = api_datas_list("date", limit=50, date_filter=selected_date)
    hour_list = api_datas_list("hour", limit=50, date_filter=selected_date)
    temp_list = api_datas_list("temperature1", limit=50, date_filter=selected_date)
    hum_list = api_datas_list("humidity1", limit=50, date_filter=selected_date)
    press_list = api_datas_list("pressure1", limit=50, date_filter=selected_date)

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
    
    date_list = api_datas_list("date", limit=50, date_filter=selected_date)
    hour_list = api_datas_list("hour", limit=50, date_filter=selected_date)
    temp_list = api_datas_list("temperature2", limit=50, date_filter=selected_date)
    hum_list = api_datas_list("humidity2", limit=50, date_filter=selected_date)
    press_list = api_datas_list("pressure2", limit=50, date_filter=selected_date)

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
    return "refresh",200
