# Ce script sert à envoyer la bonne page quand l'utilisateur va sur un lien
# Exemple : /about => about.html

from flask import Blueprint,render_template, request, jsonify


route = Blueprint("route",__name__)

###############################################################################
####################___PARTIE API : DAILY SUMMARY___############################
###############################################################################

import sqlite3
import os

def get_db_path():
    # Remonte de app/ vers la racine du projet
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "weather_data.db")


@route.route("/daily_summary")
def daily_summary():
    sensor_id = request.args.get("sensor_id", "1")
    limit = int(request.args.get("limit", "999"))

    table = f"esp{sensor_id}"  # esp1, esp2

    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = f"""
    SELECT date,
           MAX(temperature) AS tmax, MIN(temperature) AS tmin,
           MAX(humidity)    AS hmax, MIN(humidity)    AS hmin,
           MAX(pressure)    AS pmax, MIN(pressure)    AS pmin
    FROM {table}
    GROUP BY date
    ORDER BY date DESC
    LIMIT ?
    """

    cur.execute(query, (limit,))
    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "date": r["date"],
            "temperature": {"max": r["tmax"], "min": r["tmin"]},
            "humidity": {"max": r["hmax"], "min": r["hmin"]},
            "pressure": {"max": r["pmax"], "min": r["pmin"]},
        })

    return jsonify(result)


###############################################################################
####################___PARTIE DEDIEE AUX CHEMIN DES PAGES___###################
###############################################################################


@route.route("/")
def index():
    return render_template("index.html")

@route.route("/about") # ici, quand l'utilisateur va aller sur /about
def about(): # la fonction about va être appelée
    return render_template("about.html") # et la page about.html va être affichée.

@route.route("/history")
def history():
    return render_template("history.html")


@route.route("/statistical")
def statistical():

    return render_template('statistical.html')


@route.route("/admin")
def admin():
    return render_template("admin.html")
