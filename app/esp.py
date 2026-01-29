# Auteur : Théo Läderach
# Dernière modification : 21.01.2025
# Modifications : correction de la gestion des erreurs
# Fonction : recevoir les requêtes POST des ESP32 et ajouter les données à la base de données

try:
    from app.database import add_data, create_table_if_not_exists, get_all_sensors, register_esp32
except:
    from database import add_data, create_table_if_not_exists, get_all_sensors, register_esp32

from flask import request, Blueprint, jsonify
from werkzeug.exceptions import InternalServerError

from datetime import datetime
from zoneinfo import ZoneInfo
import re

# Fuseau horaire Suisse (Berne)
TIMEZONE_SUISSE = ZoneInfo("Europe/Zurich")


esp = Blueprint("esp",__name__)

@esp.route("/", methods=["POST"])
def esp_request():
    """
    Recoit les donnees d'un capteur ESP32.
    Accepte n'importe quel capteur_id au format ATOM_00X (X = 1, 2, 3, ...)
    """
    # Lire les données JSON
    data = request.get_json()
    if not data:
        print("Aucune donnée JSON reçue")
        return "Bad Request", 400

    capteur_id = data.get('capteur_id')
    temperature = data.get('temperature')
    humidity = data.get('humidite')
    pressure = data.get('pression')
    mac_address = data.get('mac_address')  # Optionnel

    # Utiliser l'heure suisse (Berne)
    now_suisse = datetime.now(TIMEZONE_SUISSE)
    date_now = now_suisse.strftime("%Y-%m-%d")
    hour_now = now_suisse.strftime("%H:%M:%S")
    ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #timestamp

    # Extraire le numero du capteur (ATOM_001 -> 1, ATOM_002 -> 2, etc.)
    match = re.search(r'ATOM_0*(\d+)', capteur_id)
    if match:
        numero = match.group(1)
        table_name = f"esp{numero}"
    else:
        print(f"Format capteur_id invalide: {capteur_id}")
        return jsonify({"error": "Format capteur_id invalide"}), 400

    # Creer la table si elle n'existe pas (nouveau capteur)
    #création dorvée des tables esp1 et esp2
    #Permet d'insérer des valeurs NULL même si l'autre capteur est déconnecté
    create_table_if_not_exists("esp1")
    create_table_if_not_exists("esp2")

    # Mettre a jour last_seen si mac_address fourni
    if mac_address:
        ip_address = request.remote_addr
        register_esp32(mac_address, ip_address)

    # Ajouter les donnees du capteur actif
    result_main = add_data(table_name, value={
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "date": date_now,
        "hour": hour_now
    })

    #Détermination de l'autre capteur (celui qui n'a rien envoyé)
    if table_name == "esp1":
        other_table = "esp2"
    elif table_name == "esp2":
        other_table = "esp1"
    else:
        other_table = None
    
    # Insertion d'une ligne avec valeurs NULL pour le capteur inactif
    # Cela permet de garder une synchronisation temporelle entre les capteurs
    result_other = True
    if other_table:
        result_other = add_data(other_table, value={
            "temperature": None,
            "humidity": None,
            "pressure": None,
            "date": date_now,
            "hour": hour_now
        })

    # Succès uniquement si les deux insertions ont réussi
    if result_main and result_other:
        print(f"Donnees recues de {capteur_id} ({table_name}): T={temperature}C, H={humidity}%, P={pressure}hPa")
        return jsonify({"Serveur local": "Succès", "capteur": table_name}), 201
    else:
        return InternalServerError("Erreur lors de l'ajout de données dans la DB")


@esp.route("/sensors", methods=["GET"])
def list_sensors():
    """
    Retourne la liste des capteurs enregistres
    """
    sensors = get_all_sensors()
    return jsonify({"sensors": sensors})


