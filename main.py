import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template
import matplotlib.pyplot as plt
import os
import time
import json

app = Flask(__name__)


json_file_path = "data.json"
timestamps = ["12:00", "12:05", "12:10", "12:15", "12:20", "12:25", "12:30", "12:35", "12:40", "12:45"]


###############################################################################
####################___PARTIE DEDIEE AUX CHEMIN DES PAGES___###################
###############################################################################


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/a_propos")
def a_propos():
    return render_template("a_propos.html")

@app.route("/historique")
def historique():
    return render_template("historique.html")



# Ajoute une fonction pour générer un timestamp dans les templates


@app.route("/statistique")
def statistique():
    
    create_graph_line("temperatures",timestamps,label_x="heures",label_y="°C",titre="Températures")
    create_graph_bar("pluie",timestamps,label_x="heures",label_y="Millimètre",titre="Taux de pluie")
    create_graph_pie("temps","type_temps", titre="Répartition du temps")
    create_graph_line("pression",timestamps,label_x="heures",label_y="hPa",titre="Pressions")
    create_graph_bar("humidite",timestamps,label_x="heures",label_y="%",titre="Taux d'humidité")

    return render_template('statistique.html')



###############################################################################
#######################___PARTIE DEDIEE AU GRAPHIQUE___########################
###############################################################################

@app.context_processor
def inject_timestamp():
    return {"timestamp": lambda: int(time.time())}

def create_graph_line(var,echelle,label_x="abscisse",label_y="ordonnée",titre="Titre du graphique",x=10,y=5,couleur="tab:blue"):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    plt.figure(figsize=(x, y))
    plt.plot(echelle, data.get(var)[-len(timestamps):], marker='o', color=couleur, label=titre)
    plt.title(titre)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)

    file_path = os.path.join(static_dir, f"graph_{var}.png")

    try:
        plt.savefig(file_path)
        plt.close()
        print(f"✅ Graphique sauvegardé à : {file_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        plt.close()
        return "Erreur interne — impossible de générer le graphique", 500
    
def create_graph_bar(var,echelle,label_x="abscisse",label_y="hauteur",titre="Titre du graphique",x=10,y=5,couleur="tab:blue"):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    plt.figure(figsize=(x, y))
    plt.bar(echelle, data.get(var)[-len(timestamps):], color=couleur, label=titre)
    plt.title(titre)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)

    file_path = os.path.join(static_dir, f"graph_{var}.png")

    try:
        plt.savefig(file_path)
        plt.close()
        print(f"✅ Graphique sauvegardé à : {file_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        plt.close()
        return "Erreur interne — impossible de générer le graphique", 500

def create_graph_pie(var,type_var, titre="Diagramme circulaire", x=8, y=8):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Récupère les données du JSON
    value = data.get(var, {})
    type = data.get(type_var,{})
    categories_data = {}
    for i in range(len(set(value))):
        i=str(i)
        var_type = type.get(i)
        categories_data[var_type]= value.count(i)
        print(categories_data)

    labels = list(categories_data.keys())
    sizes = list(categories_data.values())

    # Vérifie qu’il y a des données
    if not labels or not sizes:
        print(f"❌ Aucune donnée pour {var}")
        return

    plt.figure(figsize=(x, y))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
    plt.title(titre)
    plt.axis('equal')  # Pour que le cercle soit rond

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)

    file_path = os.path.join(static_dir, f"graph_{var}.png")

    try:
        plt.savefig(file_path)
        plt.close()
        print(f"✅ Graphique pie sauvegardé à : {file_path}")
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

@app.route("/api/temperature")
def api_temperature():
    temp = api_donnee("temperatures")
    return str(temp)

@app.route("/api/pression")
def api_pression():
    pression = api_donnee("pression")
    return str(pression)

@app.route("/api/humidite")
def api_humidite():
    try:
        humidite = api_donnee("humidite")
    except:
        humidite = "X"
    return str(humidite)

@app.route("/api/temps")
def api_temps():
    temps = api_donnee("temps")
    if temps == "0": # ensoleilé
        return "☀️"
    if temps == "1": # nuageux
        return "☁️"
    if temps == "2": # pluie
        return "🌧️"
    if temps == "3": # orage
        return "🌩️"
    if temps == "4": # neige
        return "🌨️"
    return "X"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)