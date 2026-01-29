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
import threading
import time

# Fuseau horaire Suisse (Berne)
TIMEZONE_SUISSE = ZoneInfo("Europe/Zurich")

# Buffer pour stocker les données en attente (clé: table_name, valeur: données + timestamp)
pending_data = {}
# Lock pour éviter les conditions de concurrence
pending_data_lock = threading.Lock()


esp = Blueprint("esp",__name__)

def insert_paired_data(table_name, main_data, other_table):
    """
    Insère les données du capteur actif et du capteur inactif dans la DB.
    """
    result_main = add_data(table_name, value=main_data)
    
    result_other = True
    if other_table:
        result_other = add_data(other_table, value={
            "temperature": None,
            "humidity": None,
            "pressure": None,
            "date": main_data["date"],
            "hour": main_data["hour"]
        })
    
    return result_main and result_other


def timeout_callback(table_name, main_data, other_table, capteur_id, temperature, humidity, pressure):
    """
    Appelée après 17 secondes si l'autre capteur n'a pas envoyé ses données.
    Ajoute les données du capteur actif et une ligne vide pour l'autre.
    """
    with pending_data_lock:
        # Vérifier si les données existent toujours (pas encore traitées par l'autre capteur)
        if table_name in pending_data:
            print(f"Timeout pour {capteur_id}: ajout des données avec valeurs NULL pour l'autre capteur")
            insert_paired_data(table_name, main_data, other_table)
            del pending_data[table_name]
        else:
            print(f"Timeout pour {capteur_id}: données déjà traitées par l'autre capteur")


@esp.route("/", methods=["POST"])
def esp_request():
    """
    Recoit les donnees d'un capteur ESP32.
    Accepte n'importe quel capteur_id au format ATOM_00X (X = 1, 2, 3, ...)
    
    Synchronisation des capteurs:
    - Attend 17 secondes pour recevoir les données de l'autre capteur
    - Si reçu: insère les deux données ensemble
    - Si timeout: insère sa valeur + NULL pour l'autre avec la même date/heure
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

    # Extraire le numero du capteur (ATOM_001 -> 1, ATOM_002 -> 2, etc.)
    match = re.search(r'ATOM_0*(\d+)', capteur_id)
    if match:
        numero = match.group(1)
        table_name = f"esp{numero}"
    else:
        print(f"Format capteur_id invalide: {capteur_id}")
        return jsonify({"error": "Format capteur_id invalide"}), 400

    # Creer la table si elle n'existe pas (nouveau capteur)
    create_table_if_not_exists("esp1")
    create_table_if_not_exists("esp2")

    # Mettre a jour last_seen si mac_address fourni
    if mac_address:
        ip_address = request.remote_addr
        register_esp32(mac_address, ip_address)

    # Déterminer l'autre table
    if table_name == "esp1":
        other_table = "esp2"
    elif table_name == "esp2":
        other_table = "esp1"
    else:
        other_table = None

    # Préparer les données
    main_data = {
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "date": date_now,
        "hour": hour_now
    }

    with pending_data_lock:
        # Vérifier si l'autre capteur a des données en attente
        if other_table and other_table in pending_data:
            # L'autre capteur a déjà envoyé ses données!
            other_data = pending_data[other_table]
            del pending_data[other_table]
            
            # Annuler le timeout si encore actif
            if "timer" in other_data:
                other_data["timer"].cancel()
            
            # Ajouter les données du capteur actif dans sa table
            result_main = add_data(table_name, value=main_data)
            
            # Ajouter les données de l'autre capteur dans sa table (reçues avant)
            result_other = add_data(other_table, value=other_data["data"])
            
            if result_main and result_other:
                print(f"Donnees appariées: {capteur_id} (T={temperature}C, H={humidity}%, P={pressure}hPa) + {other_data['capteur_id']}")
                return jsonify({"Serveur local": "Succès appairage", "capteur": table_name, "paired": True}), 201
            else:
                return InternalServerError("Erreur lors de l'ajout de données dans la DB")
        else:
            # Mettre en attente les données du capteur actif
            timer = threading.Timer(
                17.0,
                timeout_callback,
                args=(table_name, main_data, other_table, capteur_id, temperature, humidity, pressure)
            )
            timer.daemon = True
            timer.start()
            
            pending_data[table_name] = {
                "data": main_data,
                "capteur_id": capteur_id,
                "timer": timer
            }
            
            print(f"Donnees en attente de {capteur_id}: en attente de l'autre capteur pendant 17 secondes")
            return jsonify({"Serveur local": "En attente", "capteur": table_name, "timeout": 17}), 202


@esp.route("/sensors", methods=["GET"])
def list_sensors():
    """
    Retourne la liste des capteurs enregistres
    """
    sensors = get_all_sensors()
    return jsonify({"sensors": sensors})


