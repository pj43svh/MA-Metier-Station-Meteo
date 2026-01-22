import sqlite3
import os

# Chemin de la base de donnees (configurable via variable d'environnement pour Railway)
DB_PATH = os.environ.get('DATABASE_PATH', 'weather_data.db')

def get_db_connection():
    """Retourne une connexion SQLite (thread-safe)"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    """Crée les tables si elles n’existent pas
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

    # Extraire les noms de tables
    sensors = [table[0] for table in tables]
    return sensors


def get_sensor_count():
    """
    Retourne le nombre de capteurs enregistres.
    """
    return len(get_all_sensors())


# Appelle create_tables() au demarrage
create_tables()