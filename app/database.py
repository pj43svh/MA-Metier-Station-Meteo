# Auteur : Théo Läderach
# Dernière modification : 21.01.2025
# Modifications : ajout d'une description au fonctions
# Fonction : créer la DB SQLite et gérer les opérations de base de données

import sqlite3
import os

# Chemin de la base de donnees (configurable via variable d'environnement pour Railway)
DB_PATH = os.environ.get('DATABASE_PATH', 'weather_data.db')

def get_db_connection():
    """Retourne une connexion SQLite (thread-safe)"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    """Crée les tables si elles n'existent pas
    Le nom de la table est l'adresse ip de l'appareil"""
    conn = get_db_connection()
    cursor = conn.cursor()

    name = ["esp1","esp2"]
    for i in name :
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {i} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            date TEXT NOT NULL,
            hour TEXT NOT NULL
        );
        """)

    # Table pour la configuration des ESP32
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS esp32_devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac_address TEXT UNIQUE NOT NULL,
        sensor_number INTEGER,
        name TEXT,
        last_seen TEXT,
        ip_address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

def add_data(table, value={}):
    """Ajoute une ligne dans une table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    columns = ", ".join(f"`{k}`" for k in value.keys())
    placeholders = ", ".join("?" for _ in value.values())
    command = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"

    values = tuple(value.values())
    cursor.execute(command, values)
    conn.commit()
    conn.close()
    return True

def read_data(table, column="*", where=None,order=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        command = f"SELECT {column} FROM `{table}`"
        if where:
            command += f" WHERE {where}"
        if order:
            command += f" ORDER BY {order}"
        cursor.execute(command)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Erreur lecture table {table}: {e}")
        return []
    finally:
        conn.close()


def create_table_if_not_exists(table_name):
    """
    Cree une table pour un nouveau capteur si elle n'existe pas.
    Permet d'ajouter des capteurs dynamiquement (esp1, esp2, esp3, esp4...)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        date TEXT NOT NULL,
        hour TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print(f"Table {table_name} prete")


def get_all_sensors():
    """
    Retourne la liste de tous les capteurs (tables esp*) dans la base de donnees.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Recuperer toutes les tables qui commencent par 'esp'
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'esp%' ORDER BY name")
    tables = cursor.fetchall()

    conn.close()

    # Extraire les noms de tables (exclure esp32_devices qui est une table de config)
    sensors = [table[0] for table in tables if table[0] != 'esp32_devices']
    return sensors


def get_sensor_count():
    """
    Retourne le nombre de capteurs enregistres.
    """
    return len(get_all_sensors())


def get_sensor_last_activity(table_name):
    """
    Retourne la date et l'heure de la derniere activite d'un capteur.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT date, hour FROM `{table_name}` ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            return {"date": result[0], "hour": result[1]}
        return None
    except Exception as e:
        print(f"Erreur lecture activite {table_name}: {e}")
        return None
    finally:
        conn.close()


def get_all_sensors_status():
    """
    Retourne le statut de tous les capteurs avec leur derniere activite.
    """
    sensors = get_all_sensors()
    status_list = []

    for sensor in sensors:
        last_activity = get_sensor_last_activity(sensor)
        status_list.append({
            "name": sensor,
            "last_activity": last_activity
        })

    return status_list


# ==================== GESTION DES ESP32 ====================

def register_esp32(mac_address, ip_address=None):
    """
    Enregistre un nouvel ESP32 ou met a jour son IP et last_seen.
    Retourne le numero de capteur assigne (ou None si pas encore configure).
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifier si l'ESP32 existe deja
    cursor.execute("SELECT sensor_number FROM esp32_devices WHERE mac_address = ?", (mac_address,))
    result = cursor.fetchone()

    if result:
        # Mettre a jour last_seen et IP
        cursor.execute(
            "UPDATE esp32_devices SET last_seen = ?, ip_address = ? WHERE mac_address = ?",
            (now, ip_address, mac_address)
        )
        conn.commit()
        conn.close()
        return result[0]  # Retourne le sensor_number (peut etre None)
    else:
        # Nouvel ESP32, l'ajouter sans numero de capteur
        cursor.execute(
            "INSERT INTO esp32_devices (mac_address, ip_address, last_seen) VALUES (?, ?, ?)",
            (mac_address, ip_address, now)
        )
        conn.commit()
        conn.close()
        return None  # Pas encore configure


def get_esp32_config(mac_address):
    """
    Retourne la configuration d'un ESP32 par son adresse MAC.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT sensor_number, name FROM esp32_devices WHERE mac_address = ?",
        (mac_address,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"sensor_number": result[0], "name": result[1]}
    return None


def set_esp32_sensor_number(mac_address, sensor_number, name=None):
    """
    Assigne un numero de capteur a un ESP32.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if name:
        cursor.execute(
            "UPDATE esp32_devices SET sensor_number = ?, name = ? WHERE mac_address = ?",
            (sensor_number, name, mac_address)
        )
    else:
        cursor.execute(
            "UPDATE esp32_devices SET sensor_number = ? WHERE mac_address = ?",
            (sensor_number, mac_address)
        )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    # Creer la table pour ce capteur si elle n'existe pas
    if rows_affected > 0 and sensor_number:
        create_table_if_not_exists(f"esp{sensor_number}")

    return rows_affected > 0


def get_all_esp32_devices():
    """
    Retourne la liste de tous les ESP32 enregistres.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mac_address, sensor_number, name, last_seen, ip_address, created_at
        FROM esp32_devices
        ORDER BY sensor_number, created_at
    """)
    results = cursor.fetchall()
    conn.close()

    devices = []
    for row in results:
        devices.append({
            "mac_address": row[0],
            "sensor_number": row[1],
            "name": row[2],
            "last_seen": row[3],
            "ip_address": row[4],
            "created_at": row[5]
        })

    return devices


def delete_esp32_device(mac_address):
    """
    Supprime un ESP32 de la base de donnees.
    Supprime aussi la table de donnees du capteur (espX).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Recuperer le numero du capteur avant suppression
    cursor.execute("SELECT sensor_number FROM esp32_devices WHERE mac_address = ?", (mac_address,))
    result = cursor.fetchone()
    sensor_number = result[0] if result else None

    # Supprimer l'entree de esp32_devices
    cursor.execute("DELETE FROM esp32_devices WHERE mac_address = ?", (mac_address,))
    rows_affected = cursor.rowcount

    # Supprimer aussi la table de donnees si elle existe
    if sensor_number:
        table_name = f"esp{sensor_number}"
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"Table {table_name} supprimee")
        except Exception as e:
            print(f"Erreur suppression table {table_name}: {e}")

    conn.commit()
    conn.close()

    return rows_affected > 0


# Appelle create_tables() au demarrage
create_tables()