from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from app import db
from app.models import Capteur, Mesure

main = Blueprint('main', __name__)
api = Blueprint('api', __name__)


# ==================== PAGES WEB ====================

@main.route('/')
def dashboard():
    """Page principale - Dashboard météo"""
    return render_template('dashboard.html')


# ==================== API REST ====================

# --- Capteurs ---

@api.route('/capteurs', methods=['GET'])
def get_capteurs():
    """Liste tous les capteurs enregistrés"""
    capteurs = Capteur.query.all()
    return jsonify([c.to_dict() for c in capteurs])


@api.route('/capteurs', methods=['POST'])
def add_capteur():
    """Ajoute un nouveau capteur"""
    data = request.get_json()

    if not data or 'esp_id' not in data or 'nom' not in data:
        return jsonify({'error': 'esp_id et nom requis'}), 400

    # Vérifie si le capteur existe déjà
    existing = Capteur.query.filter_by(esp_id=data['esp_id']).first()
    if existing:
        return jsonify({'error': 'Capteur déjà enregistré', 'capteur': existing.to_dict()}), 409

    capteur = Capteur(
        esp_id=data['esp_id'],
        nom=data['nom'],
        localisation=data.get('localisation', '')
    )
    db.session.add(capteur)
    db.session.commit()

    return jsonify(capteur.to_dict()), 201


@api.route('/capteurs/<int:id>', methods=['PUT'])
def update_capteur(id):
    """Met à jour un capteur"""
    capteur = Capteur.query.get_or_404(id)
    data = request.get_json()

    if 'nom' in data:
        capteur.nom = data['nom']
    if 'localisation' in data:
        capteur.localisation = data['localisation']
    if 'actif' in data:
        capteur.actif = data['actif']

    db.session.commit()
    return jsonify(capteur.to_dict())


@api.route('/capteurs/<int:id>', methods=['DELETE'])
def delete_capteur(id):
    """Supprime un capteur"""
    capteur = Capteur.query.get_or_404(id)
    db.session.delete(capteur)
    db.session.commit()
    return jsonify({'message': 'Capteur supprimé'})


# --- Mesures ---

@api.route('/mesures', methods=['POST'])
def add_mesure():
    """
    Endpoint pour recevoir les données des ESP32
    Format attendu:
    {
        "esp_id": "ESP32_001",
        "mesures": [
            {"type": "temperature", "valeur": 22.5, "unite": "°C"},
            {"type": "humidite", "valeur": 65, "unite": "%"}
        ]
    }
    """
    data = request.get_json()

    if not data or 'esp_id' not in data or 'mesures' not in data:
        return jsonify({'error': 'Format invalide'}), 400

    # Trouve le capteur
    capteur = Capteur.query.filter_by(esp_id=data['esp_id']).first()
    if not capteur:
        return jsonify({'error': 'Capteur non enregistré'}), 404

    # Met à jour la dernière connexion
    capteur.derniere_connexion = datetime.utcnow()

    # Enregistre les mesures
    mesures_ajoutees = []
    for m in data['mesures']:
        mesure = Mesure(
            capteur_id=capteur.id,
            type_mesure=m['type'],
            valeur=m['valeur'],
            unite=m.get('unite', '')
        )
        db.session.add(mesure)
        mesures_ajoutees.append(mesure)

    db.session.commit()

    return jsonify({
        'message': f'{len(mesures_ajoutees)} mesure(s) enregistrée(s)',
        'mesures': [m.to_dict() for m in mesures_ajoutees]
    }), 201


@api.route('/mesures/latest', methods=['GET'])
def get_latest_mesures():
    """Récupère les dernières mesures de chaque capteur"""
    capteurs = Capteur.query.filter_by(actif=True).all()
    result = []

    for capteur in capteurs:
        capteur_data = capteur.to_dict()
        capteur_data['mesures'] = {}

        # Récupère la dernière mesure de chaque type
        types_mesures = db.session.query(Mesure.type_mesure).filter_by(
            capteur_id=capteur.id
        ).distinct().all()

        for (type_mesure,) in types_mesures:
            derniere = Mesure.query.filter_by(
                capteur_id=capteur.id,
                type_mesure=type_mesure
            ).order_by(Mesure.timestamp.desc()).first()

            if derniere:
                capteur_data['mesures'][type_mesure] = {
                    'valeur': derniere.valeur,
                    'unite': derniere.unite,
                    'timestamp': derniere.timestamp.isoformat()
                }

        result.append(capteur_data)

    return jsonify(result)


@api.route('/mesures/historique/<int:capteur_id>', methods=['GET'])
def get_historique(capteur_id):
    """Récupère l'historique des mesures d'un capteur"""
    limite = request.args.get('limite', 100, type=int)
    type_mesure = request.args.get('type', None)

    query = Mesure.query.filter_by(capteur_id=capteur_id)

    if type_mesure:
        query = query.filter_by(type_mesure=type_mesure)

    mesures = query.order_by(Mesure.timestamp.desc()).limit(limite).all()

    return jsonify([m.to_dict() for m in mesures])
