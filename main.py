import numpy as np
import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, jsonify
import matplotlib.pyplot as plt
import os
import time
import json

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
    
    create_graph_line(["temperature1","temperature2"],"timestamp",label_x="",label_y="°C",line_title=["Sensor 1","Sensor 2"],title="Temperatures", color =["tab:blue","tab:red"])
    create_graph_line(["pressure1","pressure2"],"timestamp",label_x="",label_y="hPa",line_title=["Sensor 1","Sensor 2"],title="Pressures", color =["tab:blue","tab:red"])
    create_graph_bar(["humidity1","humidity2"],"timestamp",label_x="",label_y="%",bar_title=["Sensor 1","Sensor 2"],title="Humidity levels", color =["tab:blue","tab:red"])


    return render_template('statistical.html')


###############################################################################
#######################___PARTIE DEDIEE AU GRAPHIQUE___########################
###############################################################################

@app.context_processor
def inject_timestamp():
    return {"timestamp": lambda: int(time.time())}

def create_graph_line(var,echelle,label_x="abscissa",label_y="ordored",line_title=["title of line"] ,title="Title",x=10,y=5,color=["tab:blue"]):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    plt.figure(figsize=(x, y))
    for i in range(len(var)):
        plt.plot(data.get(echelle), data.get(var[i])[-len(data.get(echelle)):], marker='o', color=color[i], label=line_title[i])
    
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
    
def create_graph_bar(var,echelle,label_x="abscissa",label_y="height",bar_title=["title of bar"],title="Title",x=10,y=5,color=["tab:blue"]):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    plt.figure(figsize=(x, y))
    
    n = len(var)
    bar_width = 0.8 / n
    x_positions = np.arange(len(data.get(echelle)))
    for i in range(n):
        offset = (i - n/2 + 0.5) * bar_width
        plt.bar(x_positions + offset,
                data.get(var[i])[-len(data.get(echelle)):], 
                width=bar_width, 
                color=color[i], 
                label=bar_title[i], 
                alpha=0.7)
    plt.xticks(x_positions, data.get(echelle), rotation=45, ha='right')
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
    

###############################################################################
##########################___PARTIE DEDIEE A L'API___##########################
###############################################################################


def api_donnee(type):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    # Récupère la dernière température
    value = data.get(type, ["?"])[-1]  # ? si pas de données
    return value

##########################___API POUR LES DONNEES___###########################

@app.route("/api/temperature1")
def api_temperature1():
    temp = api_donnee("temperature1")
    return str(temp)

@app.route("/api/pressure1")
def api_pressure1():
    pressure = api_donnee("pressure1")
    return str(pressure)

@app.route("/api/humidity1")
def api_humidity1():
    try:
        humidity = api_donnee("humidity1")
    except:
        humidity = "X"
    return str(humidity)

@app.route("/api/temperature2")
def api_temperature2():
    temp = api_donnee("temperature2")
    return str(temp)

@app.route("/api/pressure2")
def api_pressure2():
    pressure = api_donnee("pressure2")
    return str(pressure)

@app.route("/api/humidity2")
def api_humidity2():
    try:
        humidity = api_donnee("humidity2")
    except:
        humidity = "X"
    return str(humidity)


##########################___API POUR L'HISTORIQUE___###########################

@app.route('/api/history1')
def get_history1():
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    dates = data.get("timestamp",[])
    temperatures = data.get("temperature1", [])
    humiditys = data.get("humidity1", [])
    pressures = data.get("pressure1", [])
    
    
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
    dates = data.get("timestamp",[])
    temperatures = data.get("temperature2", [])
    humiditys = data.get("humidity2", [])
    pressures = data.get("pressure2", [])
    
    
    return jsonify({
        "date": dates,
        "temperature": temperatures,
        "humidity": humiditys,
        "pressure": pressures
    })

###############################################################################
###########################___LANCE L'APPLICATION___###########################
###############################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)