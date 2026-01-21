from database import add_data
from flask import request, Blueprint
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
    hour_now = datetime.now().strftime("%H:%M")

    print(name,temperature,humidity,pressure,date_now,hour_now)
    if name == "Atom_001":
        name = "esp1"
    elif name == "Atom_002":
        name = "esp2"
    else :
        print("Wrong device name : ", name)
        return
    

    add_data(name, value={"temperature":temperature,"humidity":humidity,"pressure":pressure,"date":date_now,"hour":hour_now})

    


