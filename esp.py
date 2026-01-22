# Auteur : Théo Läderach
# Dernière modification : 21.01.2025
# Modifications : correction de la gestion des erreurs
# Fonction : recevoir les requêtes POST des ESP32 et ajouter les données à la base de données

from database import add_data
from flask import request, Blueprint, jsonify
from werkzeug.exceptions import InternalServerError

from datetime import datetime


esp = Blueprint("esp",__name__)

@esp.route("/", methods=["POST"])
def esp_request():
    # Lire les données JSON
    data = request.get_json()
    if not data:
        print("Aucune donnée JSON reçue")
        return "Bad Request", 400

    name = data.get('capteur_id')
    temperature = data.get('temperature')
    humidity = data.get('humidite')
    pressure = data.get('pression')

    date_now = datetime.now().strftime("%Y-%m-%d")
    hour_now = datetime.now().strftime("%H:%M:%S")

    if name == "ATOM_001":
        name = "esp1"
    elif name == "ATOM_002":
        name = "esp2"
    else :
        print("Wrong device name : ", name)
    
    

    result = add_data(name, value={"temperature":temperature,"humidity":humidity,"pressure":pressure,"date":date_now,"hour":hour_now})
    
    if result :
        return jsonify({"Serveur local":"Succès"}), 201
    else :
        return InternalServerError("Erreur lors de l'ajout de données dans la DB")

