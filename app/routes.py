from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from app import get_db

main = Blueprint('main', __name__)
api = Blueprint('api', __name__)


# ==================== PAGES WEB ====================

@main.route('/')
def dashboard():
    """Page principale - Dashboard meteo"""
    return render_template('dashboard.html')


# ==================== API REST ====================

# --- Capteurs ---

@api.route('/capteurs', methods=['GET'])
def get_capteurs():
    """Liste tous les capteurs enregistres"""
    db = get_db()
    cursor = db.execute('SELECT * FROM capteur')
    capteurs = cursor.fetchall()

    # Convertit en liste de dictionnaires
    result = []
    for c in capteurs:
        result.append({
            'id': c['id'],
            'esp_id': c['esp_id'],
            'nom': c['nom'],
            'localisation': c['localisation'],
            'actif': bool(c['actif']),
            'derniere_connexion': c['derniere_connexion']
        })

    return jsonify(result)


@api.route('/capteurs', methods=['POST'])
def add_capteur():
    """Ajoute un nouveau capteur"""
    data = request.get_json()

    if not data or 'esp_id' not in data or 'nom' not in data:
        return jsonify({'error': 'esp_id et nom requis'}), 400

    db = get_db()

    # Verifie si le capteur existe deja
    existing = db.execute('SELECT * FROM capteur WHERE esp_id = ?', (data['esp_id'],)).fetchone()
    if existing:
        return jsonify({'error': 'Capteur deja enregistre'}), 409

    # Insere le nouveau capteur
    cursor = db.execute(
        'INSERT INTO capteur (esp_id, nom, localisation) VALUES (?, ?, ?)',
        (data['esp_id'], data['nom'], data.get('localisation', ''))
    )
    db.commit()

    return jsonify({'message': 'Capteur ajoute', 'id': cursor.lastrowid}), 201


@api.route('/capteurs/<int:id>', methods=['PUT'])
def update_capteur(id):
    """Met a jour un capteur"""
    data = request.get_json()
    db = get_db()

    # Verifie que le capteur existe
    capteur = db.execute('SELECT * FROM capteur WHERE id = ?', (id,)).fetchone()
    if not capteur:
        return jsonify({'error': 'Capteur non trouve'}), 404

    # Met a jour les champs fournis
    if 'nom' in data:
        db.execute('UPDATE capteur SET nom = ? WHERE id = ?', (data['nom'], id))
    if 'localisation' in data:
        db.execute('UPDATE capteur SET localisation = ? WHERE id = ?', (data['localisation'], id))
    if 'actif' in data:
        db.execute('UPDATE capteur SET actif = ? WHERE id = ?', (1 if data['actif'] else 0, id))

    db.commit()
    return jsonify({'message': 'Capteur mis a jour'})


@api.route('/capteurs/<int:id>', methods=['DELETE'])
def delete_capteur(id):
    """Supprime un capteur"""
    db = get_db()
    db.execute('DELETE FROM capteur WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Capteur supprime'})


# --- Mesures ---

@api.route('/mesures', methods=['POST'])
def add_mesure():
    """
    Recoit les donnees de l'ESP32

    Format attendu:
    {
        "capteur_id": "ATOM_001",
        "temperature": 22.5,
        "humidite": 65.0,
        "pression": 1013.25
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Donnees manquantes'}), 400

    if 'capteur_id' not in data:
        return jsonify({'error': 'capteur_id requis'}), 400

    db = get_db()
    esp_id = data['capteur_id']

    # Cherche le capteur ou le cree automatiquement
    capteur = db.execute('SELECT * FROM capteur WHERE esp_id = ?', (esp_id,)).fetchone()

    if not capteur:
        # Auto-enregistrement du capteur
        cursor = db.execute(
            'INSERT INTO capteur (esp_id, nom, localisation) VALUES (?, ?, ?)',
            (esp_id, f'Capteur {esp_id}', 'Non defini')
        )
        db.commit()
        capteur_id = cursor.lastrowid
    else:
        capteur_id = capteur['id']

    # Met a jour la derniere connexion
    db.execute(
        'UPDATE capteur SET derniere_connexion = ? WHERE id = ?',
        (datetime.now().isoformat(), capteur_id)
    )

    # Enregistre les mesures
    mesures_count = 0

    if 'temperature' in data:
        db.execute(
            'INSERT INTO mesure (capteur_id, type_mesure, valeur, unite) VALUES (?, ?, ?, ?)',
            (capteur_id, 'temperature', data['temperature'], 'C')
        )
        mesures_count += 1

    if 'humidite' in data:
        db.execute(
            'INSERT INTO mesure (capteur_id, type_mesure, valeur, unite) VALUES (?, ?, ?, ?)',
            (capteur_id, 'humidite', data['humidite'], '%')
        )
        mesures_count += 1

    if 'pression' in data:
        db.execute(
            'INSERT INTO mesure (capteur_id, type_mesure, valeur, unite) VALUES (?, ?, ?, ?)',
            (capteur_id, 'pression', data['pression'], 'hPa')
        )
        mesures_count += 1

    db.commit()

    return jsonify({
        'message': f'{mesures_count} mesure(s) enregistree(s)',
        'capteur_id': capteur_id
    }), 201


@api.route('/mesures/latest', methods=['GET'])
def get_latest_mesures():
    """Recupere les dernieres mesures de chaque capteur"""
    db = get_db()

    # Recupere tous les capteurs actifs
    capteurs = db.execute('SELECT * FROM capteur WHERE actif = 1').fetchall()

    result = []
    for capteur in capteurs:
        capteur_data = {
            'id': capteur['id'],
            'esp_id': capteur['esp_id'],
            'nom': capteur['nom'],
            'localisation': capteur['localisation'],
            'actif': bool(capteur['actif']),
            'derniere_connexion': capteur['derniere_connexion'],
            'mesures': {}
        }

        # Recupere la derniere mesure de chaque type
        for type_mesure in ['temperature', 'humidite', 'pression']:
            mesure = db.execute('''
                SELECT valeur, unite, timestamp FROM mesure
                WHERE capteur_id = ? AND type_mesure = ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (capteur['id'], type_mesure)).fetchone()

            if mesure:
                capteur_data['mesures'][type_mesure] = {
                    'valeur': mesure['valeur'],
                    'unite': mesure['unite'],
                    'timestamp': mesure['timestamp']
                }

        result.append(capteur_data)

    return jsonify(result)


@api.route('/mesures/historique/<int:capteur_id>', methods=['GET'])
def get_historique(capteur_id):
    """Recupere l'historique des mesures d'un capteur"""
    limite = request.args.get('limite', 100, type=int)
    type_mesure = request.args.get('type', None)

    db = get_db()

    if type_mesure:
        mesures = db.execute('''
            SELECT * FROM mesure
            WHERE capteur_id = ? AND type_mesure = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (capteur_id, type_mesure, limite)).fetchall()
    else:
        mesures = db.execute('''
            SELECT * FROM mesure
            WHERE capteur_id = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (capteur_id, limite)).fetchall()

    result = []
    for m in mesures:
        result.append({
            'id': m['id'],
            'capteur_id': m['capteur_id'],
            'type_mesure': m['type_mesure'],
            'valeur': m['valeur'],
            'unite': m['unite'],
            'timestamp': m['timestamp']
        })

    return jsonify(result)
