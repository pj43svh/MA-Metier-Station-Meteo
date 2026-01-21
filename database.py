import sqlite3


def get_db_connection():
    """Retourne une connexion SQLite (thread-safe)"""
    conn = sqlite3.connect("weather_data.db")
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
    finally:
        conn.close()

# 🚀 Appelle create_tables() au démarrage
create_tables()

# Exemple d'ajout (décommenter si besoin)