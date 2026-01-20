import sqlite3
import os
from flask import Flask, g
from flask_cors import CORS

# Chemin vers la base de donnees
DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'meteo.db')


def get_db():
    """Ouvre une connexion a la base de donnees"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Pour acceder aux colonnes par nom
    return g.db


def close_db(e=None):
    """Ferme la connexion a la base de donnees"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Cree les tables si elles n'existent pas"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    # Table des capteurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS capteur (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            esp_id TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            localisation TEXT,
            actif INTEGER DEFAULT 1,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
            derniere_connexion TEXT
        )
    ''')

    # Table des mesures
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capteur_id INTEGER NOT NULL,
            type_mesure TEXT NOT NULL,
            valeur REAL NOT NULL,
            unite TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (capteur_id) REFERENCES capteur (id)
        )
    ''')

    db.commit()
    db.close()


def create_app():
    """Cree l'application Flask"""
    app = Flask(__name__)

    # Cree le dossier instance si necessaire
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

    # Initialise la base de donnees
    init_db()

    # CORS pour les requetes cross-origin
    CORS(app)

    # Ferme la connexion a la fin de chaque requete
    app.teardown_appcontext(close_db)

    # Enregistre les routes
    from app.routes import main, api
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app
