# Station Meteo Connectee

Station meteorologique connectee avec ESP32 et Raspberry Pi.

**Auteur :** Amin Torrisi
**Date :** Janvier 2026

---

## Description du projet

Ce projet permet de :
- Mesurer la temperature, l'humidite et la pression atmospherique
- Envoyer les donnees vers un serveur local (Raspberry Pi)
- Envoyer les donnees vers le cloud (ThingSpeak)
- Visualiser les donnees sur une interface web

```
┌─────────────────┐      WiFi       ┌──────────────────┐
│  Capteur ENV IV │ ──────────────► │   ThingSpeak     │
│  + Atom Lite    │                 │   (Cloud)        │
└─────────────────┘                 └──────────────────┘
        │
        │ WiFi
        ▼
┌─────────────────┐                 ┌──────────────────┐
│  Raspberry Pi   │ ◄─────────────► │   Navigateur     │
│  (Serveur Flask)│                 │   (Dashboard)    │
└─────────────────┘                 └──────────────────┘
```

---

## Materiel utilise

| Composant | Description |
|-----------|-------------|
| M5Stack Atom Lite | Microcontroleur ESP32-PICO-D4 |
| Capteur ENV IV | Temperature + Humidite (SHT40) + Pression (BMP280) |
| Raspberry Pi 3 | Serveur web local |
| Cable Grove | Connexion I2C entre Atom et capteur |

---

## Structure du projet

```
Station meteo/
│
├── app/                        # Application web Flask
│   ├── __init__.py            # Initialisation + connexion SQLite
│   ├── routes.py              # API REST (endpoints)
│   ├── templates/             # Pages HTML
│   │   ├── base.html
│   │   └── dashboard.html
│   └── static/                # Fichiers statiques
│       ├── css/style.css
│       └── js/main.js
│
├── esp32/                      # Code microcontroleur
│   └── capteur_meteo/
│       └── capteur_meteo.ino  # Programme Arduino
│
├── instance/                   # Donnees
│   └── meteo.db               # Base de donnees SQLite
│
├── config.py                   # Configuration Flask
├── run.py                      # Point d'entree serveur
├── requirements.txt            # Dependances Python
├── install.sh                  # Script installation Raspberry
├── start.sh                    # Script demarrage Raspberry
│
├── cahiercharge.md            # Cahier des charges
├── JOURNAL_DE_BORD.md         # Journal du projet
└── README.md                  # Ce fichier
```

---

## Installation

### 1. Serveur (PC ou Raspberry Pi)

```bash
# Cloner ou copier le projet
cd "Station meteo"

# Creer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows :
.\.venv\Scripts\Activate.ps1
# Linux/Mac :
source .venv/bin/activate

# Installer les dependances
pip install -r requirements.txt

# Lancer le serveur
python run.py
```

Le serveur est accessible sur `http://localhost:5000`

### 2. ESP32 (Arduino IDE)

1. **Installer Arduino IDE** : https://www.arduino.cc/en/software

2. **Ajouter le support ESP32** :
   - File → Preferences
   - Additional Board Manager URLs :
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
   - Tools → Board Manager → Rechercher "esp32" → Installer

3. **Installer les bibliotheques** :
   - Sketch → Include Library → Manage Libraries
   - Rechercher et installer :
     - `Adafruit SHT4x`
     - `Adafruit BMP280`
     - `Adafruit Unified Sensor`

4. **Configurer la carte** :
   - Tools → Board → **M5Atom**
   - Tools → Port → **COM6** (ou autre)

5. **Ouvrir et telecharger** :
   - File → Open → `esp32/capteur_meteo/capteur_meteo.ino`
   - Modifier la configuration WiFi si necessaire
   - Cliquer sur Upload (→)

---

## Configuration

### ESP32 (dans capteur_meteo.ino)

```cpp
// WiFi
const char* WIFI_SSID = "Galaxy Abeeby";
const char* WIFI_PASSWORD = "cxie3864";

// ThingSpeak (cloud)
const char* THINGSPEAK_API_KEY = "0TEJ9QR3RFIBFZ3M";

// Serveur local
const char* RASPBERRY_IP = "10.244.96.106";
const int RASPBERRY_PORT = 5000;

// Identification
const char* CAPTEUR_ID = "ATOM_001";

// Intervalle d'envoi (millisecondes)
const unsigned long SEND_INTERVAL = 20000;  // 20 secondes
```

### Branchement du capteur

```
Atom Lite (Port Grove)     Capteur ENV IV
─────────────────────      ──────────────
GND (noir)           ───►  GND
5V  (rouge)          ───►  VCC
GPIO26 (jaune)       ───►  SDA
GPIO32 (blanc)       ───►  SCL
```

---

## Base de donnees SQLite

### Tables

**Table `capteur`** - Les capteurs enregistres
```sql
CREATE TABLE capteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    esp_id TEXT UNIQUE NOT NULL,     -- Identifiant unique "ATOM_001"
    nom TEXT NOT NULL,                -- Nom affiche "Salon"
    localisation TEXT,                -- Emplacement
    actif INTEGER DEFAULT 1,          -- 1=actif, 0=inactif
    date_creation TEXT,               -- Date d'ajout
    derniere_connexion TEXT           -- Derniere communication
);
```

**Table `mesure`** - Les mesures enregistrees
```sql
CREATE TABLE mesure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capteur_id INTEGER NOT NULL,      -- Lie a la table capteur
    type_mesure TEXT NOT NULL,        -- "temperature", "humidite", "pression"
    valeur REAL NOT NULL,             -- Valeur numerique
    unite TEXT,                       -- "C", "%", "hPa"
    timestamp TEXT,                   -- Date/heure de la mesure
    FOREIGN KEY (capteur_id) REFERENCES capteur (id)
);
```

### Exemples de requetes

```sql
-- Voir tous les capteurs
SELECT * FROM capteur;

-- Voir les mesures d'un capteur
SELECT * FROM mesure WHERE capteur_id = 1 ORDER BY timestamp DESC;

-- Derniere temperature
SELECT valeur FROM mesure
WHERE type_mesure = 'temperature'
ORDER BY timestamp DESC LIMIT 1;

-- Moyenne de temperature aujourd'hui
SELECT AVG(valeur) FROM mesure
WHERE type_mesure = 'temperature'
AND date(timestamp) = date('now');
```

---

## API REST

### Endpoints disponibles

| Methode | URL | Description |
|---------|-----|-------------|
| GET | `/` | Dashboard web |
| GET | `/api/capteurs` | Liste des capteurs |
| POST | `/api/capteurs` | Ajouter un capteur |
| PUT | `/api/capteurs/<id>` | Modifier un capteur |
| DELETE | `/api/capteurs/<id>` | Supprimer un capteur |
| POST | `/api/mesures` | Envoyer des mesures |
| GET | `/api/mesures/latest` | Dernieres mesures |
| GET | `/api/mesures/historique/<id>` | Historique d'un capteur |

### Format des donnees (JSON)

**Envoi de mesures** (POST /api/mesures) :
```json
{
    "capteur_id": "ATOM_001",
    "temperature": 22.5,
    "humidite": 65.0,
    "pression": 1013.25
}
```

**Reponse** :
```json
{
    "message": "3 mesure(s) enregistree(s)",
    "capteur_id": 1
}
```

---

## Utilisation

### Demarrer le serveur

```bash
# Windows
cd "C:\Users\pb51qua\Desktop\Station meteo"
.\.venv\Scripts\Activate.ps1
python run.py

# Linux/Raspberry
cd /chemin/vers/station-meteo
source .venv/bin/activate
python run.py
```

### Voir les donnees

- **Interface web locale** : http://localhost:5000
- **ThingSpeak (cloud)** : https://thingspeak.com/channels/3228055

### Tester l'API

```bash
# Voir les capteurs
curl http://localhost:5000/api/capteurs

# Simuler un envoi de l'ESP32
curl -X POST http://localhost:5000/api/mesures \
  -H "Content-Type: application/json" \
  -d '{"capteur_id":"TEST","temperature":25,"humidite":50,"pression":1013}'

# Voir les dernieres mesures
curl http://localhost:5000/api/mesures/latest
```

---

## Depannage

| Probleme | Cause | Solution |
|----------|-------|----------|
| ESP32 ne se connecte pas au WiFi | SSID/mot de passe incorrect | Verifier les majuscules et caracteres |
| `Envoi: -1` dans le moniteur serie | Serveur non accessible | Verifier que le serveur tourne et l'IP |
| Port COM occupe | Autre programme utilise le port | Fermer Arduino IDE / UIFlow2 |
| `Wrong chip detected` | Mauvaise carte selectionnee | Choisir M5Atom, pas ESP32S3 |
| Capteur renvoie 0 | Cable mal branche | Verifier le cable Grove |
| Base de donnees vide | Premiere utilisation | Les tables sont creees au demarrage |

### Verifier la connexion WiFi (ESP32)

Dans le moniteur serie (115200 baud), tu dois voir :
```
Connexion WiFi...
Connecte! IP: 10.244.96.XXX
```

### Verifier le serveur

```bash
# Le serveur doit afficher :
 * Running on http://127.0.0.1:5000
```

---

## ThingSpeak

Plateforme cloud gratuite pour visualiser les donnees.

- **URL** : https://thingspeak.com/channels/3228055
- **Channel ID** : 3228055
- **Write API Key** : 0TEJ9QR3RFIBFZ3M

Les graphiques se mettent a jour automatiquement toutes les 20 secondes.

---

## Technologies utilisees

- **ESP32** : Microcontroleur avec WiFi integre
- **Python/Flask** : Framework web leger
- **SQLite** : Base de donnees embarquee
- **HTML/CSS/JavaScript** : Interface web
- **ThingSpeak** : Plateforme IoT cloud
- **I2C** : Protocole de communication avec les capteurs

---

## Licence

Projet educatif - Libre d'utilisation.
