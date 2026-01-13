from datetime import datetime
from app import db

class Capteur(db.Model):
    """Représente un module capteur ESP32"""
    id = db.Column(db.Integer, primary_key=True)
    esp_id = db.Column(db.String(50), unique=True, nullable=False)  # ID unique de l'ESP32
    nom = db.Column(db.String(100), nullable=False)
    localisation = db.Column(db.String(200))
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)

    mesures = db.relationship('Mesure', backref='capteur', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'esp_id': self.esp_id,
            'nom': self.nom,
            'localisation': self.localisation,
            'actif': self.actif,
            'derniere_connexion': self.derniere_connexion.isoformat() if self.derniere_connexion else None
        }


class Mesure(db.Model):
    """Représente une mesure envoyée par un capteur"""
    id = db.Column(db.Integer, primary_key=True)
    capteur_id = db.Column(db.Integer, db.ForeignKey('capteur.id'), nullable=False)
    type_mesure = db.Column(db.String(50), nullable=False)  # temperature, humidite, luminosite, etc.
    valeur = db.Column(db.Float, nullable=False)
    unite = db.Column(db.String(20))  # °C, %, lux, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'capteur_id': self.capteur_id,
            'type_mesure': self.type_mesure,
            'valeur': self.valeur,
            'unite': self.unite,
            'timestamp': self.timestamp.isoformat()
        }
