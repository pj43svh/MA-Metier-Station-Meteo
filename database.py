import sqlite3


def get_db_connection():
    """Retourne une connexion SQLite (thread-safe)"""
    conn = sqlite3.connect("weather_data.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_tables():
    """Crée les tables si elles n’existent pas"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS device (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        address_ip TEXT NOT NULL UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        date_hours TEXT NOT NULL,
        device_id INTEGER NOT NULL,
        FOREIGN KEY (device_id) REFERENCES device (id) ON DELETE NO ACTION ON UPDATE NO ACTION
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

def read_data(table, column="*", where=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        command = f"SELECT {column} FROM `{table}`"
        if where:
            command += f" WHERE {where}"
        cursor.execute(command)
        results = cursor.fetchall()
        return results
    finally:
        conn.close()

# 🚀 Appelle create_tables() au démarrage
create_tables()

# Exemple d'ajout (décommenter si besoin)
# add_data("device", value={"type": "ESP32", "address_ip": "192.168.1.32"})
# add_data("device", value={"type": "ESP32", "address_ip": "192.168.1.33"})
# add_data("weather_data", value={"device_id": 1, "temperature": 15.0, "humidity": 5.2, "pressure": 1016.8, "date_hours": "2026-01-16 12:00:00"})
# add_data("weather_data", value={"device_id": 2, "temperature": 12.3, "humidity": 3.5, "pressure": 1018.0, "date_hours": "2026-01-16 12:00:00"})
# add_data("weather_data", value={"device_id": 1, "temperature": 14.5, "humidity": 5.0, "pressure": 1017.0, "date_hours": "2026-01-16 13:00:00"})
# add_data("weather_data", value={"device_id": 2, "temperature": 13.1, "humidity": 4.0, "pressure": 1017.5, "date_hours": "2026-01-16 13:00:00"})