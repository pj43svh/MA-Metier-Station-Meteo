from flask import jsonify,Blueprint,request
import app.database as db
from app.statistical import create_graph_bar,create_graph_line

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
    from zoneinfo import ZoneInfo

    sensors_status = db.get_all_sensors_status()
    result = []

    now = datetime.now(ZoneInfo("Europe/Zurich"))

    # Recuperer les noms personnalises depuis esp32_devices
    esp32_devices = db.get_all_esp32_devices()
    sensor_names = {}
    for device in esp32_devices:
        if device["sensor_number"]:
            sensor_names[str(device["sensor_number"])] = device["name"]

    for sensor in sensors_status:
        sensor_num = sensor["name"].replace("esp", "")
        # Utiliser le nom personnalise s'il existe, sinon "Sensor X"
        custom_name = sensor_names.get(sensor_num)
        display_name = custom_name if custom_name else f"Sensor {sensor_num}"

        sensor_info = {
            "id": sensor["name"],
            "number": sensor_num,
            "name": display_name,
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
        # Trouver un capteur qui a des donnees pour l'axe des heures
        sensors = db.get_all_sensors()
        device_name = sensors[0] if sensors else "esp1"
    elif type_str == "date":
        col = "date"
        sensors = db.get_all_sensors()
        device_name = sensors[0] if sensors else "esp1"
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



###############################################################################
####################___API ADMIN - GESTION DES ESP32___########################
###############################################################################

@api.route("/esp32/register", methods=["POST"])
def register_esp32():
    """
    Endpoint appele par les ESP32 pour s'enregistrer.
    L'ESP32 envoie son adresse MAC et recoit son numero de capteur.
    """
    data = request.get_json()

    if not data or "mac_address" not in data:
        return jsonify({"error": "mac_address requis"}), 400

    mac_address = data["mac_address"]
    ip_address = data.get("ip_address", request.remote_addr)

    # Enregistrer l'ESP32 et recuperer son numero de capteur
    sensor_number = db.register_esp32(mac_address, ip_address)

    if sensor_number:
        # ESP32 deja configure
        return jsonify({
            "status": "configured",
            "sensor_number": sensor_number,
            "capteur_id": f"ATOM_00{sensor_number}"
        })
    else:
        # ESP32 pas encore configure
        return jsonify({
            "status": "pending",
            "message": "En attente de configuration via l'interface admin"
        })


@api.route("/esp32/config/<mac_address>")
def get_esp32_config(mac_address):
    """
    Retourne la configuration d'un ESP32 par son adresse MAC.
    """
    config = db.get_esp32_config(mac_address)

    if config and config["sensor_number"]:
        return jsonify({
            "status": "configured",
            "sensor_number": config["sensor_number"],
            "capteur_id": f"ATOM_00{config['sensor_number']}",
            "name": config["name"]
        })
    else:
        return jsonify({
            "status": "pending",
            "message": "Non configure"
        })


@api.route("/esp32/devices")
def list_esp32_devices():
    """
    Retourne la liste de tous les ESP32 enregistres.
    Pour l'interface admin.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    devices = db.get_all_esp32_devices()
    now = datetime.now(ZoneInfo("Europe/Zurich"))

    for device in devices:
        # Calculer le statut en ligne/hors ligne
        if device["last_seen"]:
            try:
                last_seen = datetime.strptime(device["last_seen"], "%Y-%m-%d %H:%M:%S")
                diff = (now - last_seen).total_seconds()

                if diff < 120:
                    device["status"] = "online"
                    device["status_text"] = "En ligne"
                elif diff < 300:
                    device["status"] = "recent"
                    device["status_text"] = f"Vu il y a {int(diff // 60)} min"
                else:
                    device["status"] = "offline"
                    minutes = int(diff // 60)
                    if minutes < 60:
                        device["status_text"] = f"Hors ligne ({minutes} min)"
                    elif minutes < 1440:
                        device["status_text"] = f"Hors ligne ({minutes // 60}h)"
                    else:
                        device["status_text"] = f"Hors ligne ({minutes // 1440}j)"
            except:
                device["status"] = "unknown"
                device["status_text"] = "Inconnu"
        else:
            device["status"] = "unknown"
            device["status_text"] = "Jamais vu"

    return jsonify({"devices": devices, "count": len(devices)})


@api.route("/esp32/configure", methods=["POST"])
def configure_esp32():
    """
    Configure un ESP32 (assigne un numero de capteur).
    """
    data = request.get_json()

    if not data or "mac_address" not in data or "sensor_number" not in data:
        return jsonify({"error": "mac_address et sensor_number requis"}), 400

    mac_address = data["mac_address"]
    sensor_number = data["sensor_number"]
    name = data.get("name", f"Capteur {sensor_number}")

    success = db.set_esp32_sensor_number(mac_address, sensor_number, name)

    if success:
        return jsonify({
            "status": "success",
            "message": f"ESP32 configure comme Capteur {sensor_number}"
        })
    else:
        return jsonify({"error": "ESP32 non trouve"}), 404


@api.route("/esp32/delete", methods=["POST"])
def delete_esp32():
    """
    Supprime un ESP32 de la base de donnees.
    """
    data = request.get_json()

    if not data or "mac_address" not in data:
        return jsonify({"error": "mac_address requis"}), 400

    success = db.delete_esp32_device(data["mac_address"])

    if success:
        return jsonify({"status": "success", "message": "ESP32 supprime"})
    else:
        return jsonify({"error": "ESP32 non trouve"}), 404


#api/daily_summary?data=12.3.1
@api.route("/daily_summary", methods=["GET"])
def daily_summary():
    # /api/daily_summary?sensor_id=1&limit=7
    sensor_id = request.args.get("sensor_id", type=int)
    limit = request.args.get("limit", default=7, type=int)
    date = request.args.get("date", default="today", type=str)

    if sensor_id not in (1, 2):
        return jsonify([]), 400

    data = summary(sensor_id, limit,date_filter=date)

    if not data:
        return jsonify([])
    return jsonify(data)


def summary(sensor_id, limit=7,date_filter="today"):
    """
    Calcule les max/min par jour pour un capteur donné.
    Si db.read_data ne supporte pas group_by, on fait le regroupement en Python.
    """
    device_name = f"esp{sensor_id}"

    # Récupérer TOUTES les données (ou les N dernières)
    try:
        # Récupérer les données avec date, temperature, humidity, pressure
        if date_filter != "today":
            results = db.read_data(
            device_name,
            column="date, temperature, humidity, pressure",
            where=f"date = '{date_filter}'",
            order="id DESC",  # Du plus récent au plus ancien Par id
            limit=limit       # Récupérer jusqu'à 24h par jour (sécurité)
        )
        else:
            results = db.read_data(
                device_name,
                column="date, temperature, humidity, pressure",
                order="id DESC",  # Du plus récent au plus ancien Par id
                limit=limit    # Récupérer jusqu'à 24h par jour (sécurité)
            )
    except Exception as e:
        print(f"Erreur dans summary({sensor_id}): {e}")
        return []

    # Si pas de données
    if not results:
        return []

    # Regrouper par date en Python
    from collections import defaultdict
    grouped = defaultdict(lambda: {
        "temperature": [],
        "humidity": [],
        "pressure": []
    })

    for row in results:
        date = row[0]
        temp = row[1]
        hum = row[2]
        press = row[3]

        if temp is not None:
            grouped[date]["temperature"].append(temp)
        if hum is not None:
            grouped[date]["humidity"].append(hum)
        if press is not None:
            grouped[date]["pressure"].append(press)

    # Créer la liste des jours (max/min)
    formatted = []
    for date in grouped:
        t_list = grouped[date]["temperature"]
        h_list = grouped[date]["humidity"]
        p_list = grouped[date]["pressure"]

        formatted.append({
            "date": date,
            "temperature": {
                "max": max(t_list) if t_list else None,
                "min": min(t_list) if t_list else None
            },
            "humidity": {
                "max": max(h_list) if h_list else None,
                "min": min(h_list) if h_list else None
            },
            "pressure": {
                "max": max(p_list) if p_list else None,
                "min": min(p_list) if p_list else None
            }
        })

    # Trier par date décroissante (du plus récent au plus ancien)
    formatted.sort(key=lambda x: x["date"], reverse=True)

    # Limiter au nombre de jours demandé
    return formatted[:limit]




