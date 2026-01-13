# Station Météo - Raspberry Pi & ESP32

Station météorologique connectée avec centrale Raspberry Pi et capteurs distribués ESP32.

## Structure du projet

```
Station meteo/
├── app/
│   ├── __init__.py          # Initialisation Flask
│   ├── models.py             # Modèles de données (Capteur, Mesure)
│   ├── routes.py             # Routes API et pages web
│   ├── static/
│   │   ├── css/style.css     # Styles de l'interface
│   │   └── js/main.js        # Logique JavaScript
│   └── templates/
│       ├── base.html         # Template de base
│       └── dashboard.html    # Page principale
├── esp32/                    # Code pour les ESP32 (à créer)
├── config.py                 # Configuration Flask
├── run.py                    # Point d'entrée
├── requirements.txt          # Dépendances Python
└── README.md
```

## Installation (Raspberry Pi)

### 1. Prérequis

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Créer l'environnement virtuel

```bash
cd "Station meteo"
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer le serveur

```bash
python run.py
```

L'interface est accessible sur `http://<IP_RASPBERRY>:5000`

## API REST

### Capteurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/capteurs` | Liste tous les capteurs |
| POST | `/api/capteurs` | Ajoute un capteur |
| PUT | `/api/capteurs/<id>` | Modifie un capteur |
| DELETE | `/api/capteurs/<id>` | Supprime un capteur |

### Mesures

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/mesures` | Envoie des mesures (depuis ESP32) |
| GET | `/api/mesures/latest` | Dernières mesures par capteur |
| GET | `/api/mesures/historique/<id>` | Historique d'un capteur |

### Format d'envoi des mesures (ESP32 → Raspberry Pi)

```json
{
    "esp_id": "ESP32_001",
    "mesures": [
        {"type": "temperature", "valeur": 22.5, "unite": "°C"},
        {"type": "humidite", "valeur": 65, "unite": "%"}
    ]
}
```

## Structure Trello recommandée

Voir le fichier `TRELLO_STRUCTURE.md` pour la configuration détaillée.
