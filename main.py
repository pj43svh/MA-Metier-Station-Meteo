import numpy as np
import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, jsonify
import matplotlib.pyplot as plt
import os
import time
import json

import database as db

app = Flask(__name__)


json_file_path = "data.json"


###############################################################################
####################___PARTIE DEDIEE AUX CHEMIN DES PAGES___###################
###############################################################################


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/history")
def history():
    return render_template("history.html")



@app.route("/statistical")
def statistical():
    
    create_graph_line(["temperature1","temperature2"],"date_hours",label_x="",label_y="°C",line_title=["Sensor 1","Sensor 2"],title="Temperatures", color =["tab:blue","tab:red"])
    create_graph_line(["pressure1","pressure2"],"date_hours",label_x="",label_y="hPa",line_title=["Sensor 1","Sensor 2"],title="Pressures", color =["tab:blue","tab:red"])
    create_graph_bar(["humidity1","humidity2"],"date_hours",label_x="",label_y="%",bar_title=["Sensor 1","Sensor 2"],title="Humidity levels", color =["tab:blue","tab:red"])


    return render_template('statistical.html')


###############################################################################
#######################___PARTIE DEDIEE AU GRAPHIQUE___########################
###############################################################################

@app.context_processor
def inject_date_hours():
    return {"date_hours": lambda: int(time.time())}

def create_graph_line(var, echelle, label_x="Date", label_y="Value", line_title=["Line 1"], title="Title", x=10, y=5, color=["tab:blue"]):
    dates = api_datas_list(echelle)
    if not dates:
        print(f"❌ Aucune date trouvée pour {echelle}")
        return

    plt.figure(figsize=(x, y))
    for i in range(len(var)):
        values = api_datas_list(var[i])
        if not values:
            print(f"❌ Aucune valeur trouvée pour {var[i]}")
            continue
        # Ajuster la longueur des valeurs pour correspondre aux dates
        values = values[-len(dates):]  # Prendre les dernières valeurs
        plt.plot(dates, values, marker='o', color=color[i], label=line_title[i])

    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)

    file_path = os.path.join(static_dir, f"graph_{title}.png")

    try:
        plt.savefig(file_path)
        plt.close()
        print(f"✅ Graphique sauvegardé à : {file_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        plt.close()
        return "Erreur interne — impossible de générer le graphique", 500
# exemple d'utilisation
# create_graph_line(["pressure1","pressure2"],"date_hours",label_x="",label_y="hPa",line_title=["Sensor 1","Sensor 2"],title="Pressures", color =["tab:blue","tab:red"])



def create_graph_bar(var,echelle,label_x="abscissa",label_y="height",bar_title=["title of bar"],title="Title",x=10,y=5,color=["tab:blue"]):
    
    plt.figure(figsize=(x, y))
    
    n = len(var)
    bar_width = 0.8 / n
    x_positions = np.arange(len(api_datas_list(echelle)))
    for i in range(n):
        offset = (i - n/2 + 0.5) * bar_width
        plt.bar(x_positions + offset,
                api_datas_list(var[i])[-len(api_datas_list(echelle)):], 
                width=bar_width, 
                color=color[i], 
                label=bar_title[i], 
                alpha=0.7)
    plt.xticks(x_positions, api_datas_list(echelle), rotation=45, ha='right')
    plt.title(title)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)

    file_path = os.path.join(static_dir, f"graph_{title}.png")

    try:
        plt.savefig(file_path)
        plt.close()
        print(f"✅ Graphique sauvegardé à : {file_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        plt.close()
        return "Erreur interne — impossible de générer le graphique", 500

# exemple d'utilisation
# create_graph_bar(["humidity1","humidity2"],"date_hours",label_x="",label_y="%",bar_title=["Sensor 1","Sensor 2"],title="Humidity levels", color =["tab:blue","tab:red"])


###############################################################################
##########################___PARTIE DEDIEE A L'API___##########################
###############################################################################


def api_data(type_str):
    # Extraire colonne et device_id
    col = type_str[:-1]
    device_id = int(type_str[-1])

    # Colonnes autorisées
    ALLOWED_COLUMNS = {"temperature", "humidity", "pressure"}

    if col not in ALLOWED_COLUMNS:
        return "Colonne non autorisée"

    # Requête : dernière valeur pour ce device_id, triée par date_heure DESC
    results = db.read_data(
        "weather_data",
        column=col,
        where=f"device_id = {device_id} ORDER BY date_hours DESC LIMIT 1"
    )

    if results and len(results) > 0:
        value = results[0][0]  # Premier tuple, première colonne
        return str(value) if value is not None else "NULL"
    else:
        return "Aucune donnée"
    
def api_datas_list(type_str, limit=10):
    """Retourne une liste des dernières valeurs pour une colonne et un device_id"""
    if type_str != "date_hours":
        col = type_str[:-1]
        device_id = int(type_str[-1])
    else:
        col = "date_hours"  # ← Important : utiliser le nom exact de la colonne
        device_id = 1  # Arbitraire, car date_hours est commune à tous les devices

    ALLOWED_COLUMNS = {"temperature", "humidity", "pressure", "date_hours"}

    if col not in ALLOWED_COLUMNS:
        return []  # Retourne une liste vide si colonne invalide

    # Requête : récupérer les dernières valeurs triées par date DESC
    results = db.read_data(
        "weather_data",
        column=col,
        where=f"device_id = {device_id} ORDER BY date_hours DESC LIMIT {limit}"
    )

    # Convertir en liste de valeurs (sans tuples)
    if not results:
        return []

    values = [row[0] for row in results]

    # Retourner la liste inversée (du plus ancien au plus récent)
    return values[::-1]

# exemple d'utilisation
# temp = api_data("temperature1")

##########################___API POUR LES DONNEES___###########################

@app.route("/api/temperature1")
def api_temperature1():
    temp = api_data("temperature1")
    return temp

@app.route("/api/pressure1")
def api_pressure1():
    try:
        pressure = api_data("pressure1")
    except:
        pressure = "X"
    return str(pressure)

@app.route("/api/humidity1")
def api_humidity1():
    try:
        humidity = api_data("humidity1")
    except:
        humidity = "X"
    return str(humidity)

@app.route("/api/temperature2")
def api_temperature2():
    try:
        temp = api_data("temperature2")
    except:
        temp = "X"
    return str(temp)

@app.route("/api/pressure2")
def api_pressure2():
    try:
        pressure = api_data("pressure2")
    except:
        pressure = "X"
    return str(pressure)

@app.route("/api/humidity2")
def api_humidity2():
    try:
        humidity = api_data("humidity2")
    except:
        humidity = "X"
    return str(humidity)


##########################___API POUR L'HISTORIQUE___###########################

@app.route('/api/history1')
def get_history1():
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    dates = api_datas_list("date_hours")
    temperatures = api_datas_list("temperature1")
    humiditys = api_datas_list("humidity1")
    pressures = api_datas_list("pressure1")
    
    
    return jsonify({
        "date": dates,
        "temperature": temperatures,
        "humidity": humiditys,
        "pressure": pressures
    })



@app.route('/api/history2')
def get_history2():
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    dates = api_datas_list("date_hours")
    temperatures = api_datas_list("temperature2")
    humiditys = api_datas_list("humidity2")
    pressures = api_datas_list("pressure2")
    
    
    return jsonify({
        "date": dates,
        "temperature": temperatures,
        "humidity": humiditys,
        "pressure": pressures
    })

###############################################################################
###########################___LANCE L'APPLICATION___###########################
###############################################################################
# 🔍 TEST : Vérifie si la base retourne bien des données


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)