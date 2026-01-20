# Journal de Bord - Station Meteo Connectee

## Informations Projet
- **Projet** : Station Meteo Connectee
- **Auteur** : Amin Torrisi
- **Date de debut** : 13 Janvier 2026
- **Materiel** : M5Stack Atom Lite + Capteur ENV IV + Raspberry Pi 3

---

## Jour 1 - 13 Janvier 2026

### Objectifs du jour
- [x] Configuration initiale du projet
- [x] Mise en place de l'environnement de developpement
- [x] Programmation de l'ESP32 (Atom Lite)
- [x] Connexion WiFi et envoi des donnees
- [x] Integration du capteur ENV IV
- [x] Mise en place du dashboard cloud (ThingSpeak)

### Travail realise

#### 1. Structure du projet (Matin)
- Creation de l'architecture du projet Flask pour le serveur web
- Fichiers crees :
  - `app/__init__.py` - Factory Flask
  - `app/models.py` - Modeles de base de donnees (Capteur, Mesure)
  - `app/routes.py` - API REST endpoints
  - `app/templates/` - Interface web dashboard
  - `app/static/` - CSS et JavaScript
  - `config.py`, `run.py`, `requirements.txt`

#### 2. Configuration ESP32 avec UIFlow2 (Tentative)
- Essai de programmation via UIFlow2 (interface web M5Stack)
- **Probleme rencontre** : Le firmware UIFlow2 creait une boucle de scan WiFi qui empechait l'execution du code
- **Solution** : Passage a Arduino IDE

#### 3. Configuration Arduino IDE (Apres-midi)
- Installation d'Arduino IDE 2.3.7
- Ajout du support ESP32 via Boards Manager
- URL ajoutee : `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
- Installation du package "esp32 by Espressif Systems"

#### 4. Identification du materiel
- **Decouverte importante** : L'appareil est un **Atom Lite** (ESP32-PICO-D4), pas un AtomS3
- Carte selectionnee dans Arduino : **M5Atom**
- Port : **COM6**

#### 5. Test de connexion WiFi
- Premier code de test uploade avec succes
- Connexion WiFi reussie au reseau "Galaxy Abeeby"
- IP obtenue : 10.244.96.193

#### 6. Integration ThingSpeak (Cloud)
- Creation d'un compte ThingSpeak (gratuit)
- Creation du channel "Station Meteo" avec 3 champs :
  - Field 1 : Temperature
  - Field 2 : Humidite
  - Field 3 : Pression
- **Channel ID** : 3228055
- **Write API Key** : 0TEJ9QR3RFIBFZ3M
- Premier envoi de donnees de test : **SUCCES (code 200)**

#### 7. Integration du capteur ENV IV
- Branchement du capteur ENV IV sur le port Grove
- Installation des bibliotheques Arduino :
  - Adafruit SHT4x (temperature + humidite)
  - Adafruit BMP280 (pression atmospherique)
- Configuration I2C : SDA=26, SCL=32

#### 8. Premier releve de donnees reelles
- **Temperature** : 19.52°C
- **Humidite** : 51.11%
- **Pression** : 891.02 hPa
- Envoi vers ThingSpeak : **SUCCES**

### Problemes rencontres et solutions

| Probleme | Cause | Solution |
|----------|-------|----------|
| UIFlow2 boucle WiFi | Firmware cherche reseau cloud | Utiliser Arduino IDE |
| "Wrong chip ESP32-S3" | Mauvaise carte selectionnee | Choisir M5Atom au lieu de ESP32S3 |
| Port COM6 occupe | UIFlow2 encore connecte | Fermer l'onglet navigateur |
| DHT22 erreur lecture | Code avec capteur non branche | Utiliser code pour ENV IV |
| Serveur Raspberry inaccessible | Serveur non demarre | Utiliser ThingSpeak cloud |

### Temps passe : ~3h

---

## Jour 2 - 19 Janvier 2026

### Objectifs du jour
- [x] Nettoyage du projet (suppression fichiers inutiles)
- [x] Conversion SQLAlchemy vers SQLite pur
- [x] Suppression de la luminosite (capteur ne la mesure pas)
- [x] Documentation complete du code
- [x] Mise a jour du journal de bord

### Travail realise

#### 1. Nettoyage du projet
Suppression des fichiers inutiles :
- `TRELLO_STRUCTURE.md` - pas necessaire
- `CREER_PDF.md` - redondant
- `LISEZ-MOI.txt` - doublon du README
- `GUIDE_COMPLET.md` - fusionne dans README
- `esp32/README.md` - obsolete (parlait de DHT22)
- `__pycache__/` - cache Python

#### 2. Conversion vers SQLite pur
Le cahier des charges demandait d'utiliser SQLite directement, pas SQLAlchemy.

**Fichiers modifies :**

`app/__init__.py` - Avant :
```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
```

`app/__init__.py` - Apres :
```python
import sqlite3
def get_db():
    db = sqlite3.connect('instance/meteo.db')
    return db
```

`app/routes.py` - Avant :
```python
capteur = Capteur.query.filter_by(esp_id='ATOM_001').first()
```

`app/routes.py` - Apres :
```python
capteur = db.execute('SELECT * FROM capteur WHERE esp_id = ?', ('ATOM_001',)).fetchone()
```

**Fichier supprime :**
- `app/models.py` - plus necessaire avec SQLite pur

**requirements.txt mis a jour :**
- Suppression de `flask-sqlalchemy`

#### 3. Suppression de la luminosite
Le capteur ENV IV ne mesure que :
- Temperature (SHT40)
- Humidite (SHT40)
- Pression (BMP280)

Modifications :
- `app/routes.py` : supprime le bloc `if 'luminosite' in data`
- `app/static/js/main.js` : supprime l'affichage luminosite

#### 4. Creation des tables SQL
Les tables sont creees automatiquement au demarrage :

```sql
CREATE TABLE IF NOT EXISTS capteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    esp_id TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    localisation TEXT,
    actif INTEGER DEFAULT 1,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion TEXT
);

CREATE TABLE IF NOT EXISTS mesure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    capteur_id INTEGER NOT NULL,
    type_mesure TEXT NOT NULL,
    valeur REAL NOT NULL,
    unite TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (capteur_id) REFERENCES capteur (id)
);
```

### Structure finale du projet

```
Station meteo/
├── app/
│   ├── __init__.py          # Connexion SQLite
│   ├── routes.py             # API REST
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       └── dashboard.html
│
├── esp32/
│   └── capteur_meteo/
│       └── capteur_meteo.ino
│
├── instance/
│   └── meteo.db              # Base SQLite
│
├── cahiercharge.md
├── config.py
├── JOURNAL_DE_BORD.md
├── README.md
├── requirements.txt
├── run.py
├── install.sh
└── start.sh
```

### Temps passe : ~2h

---

## Notes techniques

### Pinout Atom Lite - ENV IV
```
Atom Lite Grove Port:
- GND (noir)
- 5V (rouge)
- SDA GPIO26 (jaune)
- SCL GPIO32 (blanc)
```

### Adresses I2C
- SHT40 : 0x44
- BMP280 : 0x76

### Requetes SQL utilisees

```sql
-- Recuperer un capteur par son ID ESP
SELECT * FROM capteur WHERE esp_id = 'ATOM_001';

-- Ajouter une mesure
INSERT INTO mesure (capteur_id, type_mesure, valeur, unite)
VALUES (1, 'temperature', 22.5, 'C');

-- Derniere mesure d'un type
SELECT * FROM mesure
WHERE capteur_id = 1 AND type_mesure = 'temperature'
ORDER BY timestamp DESC LIMIT 1;

-- Historique des mesures
SELECT * FROM mesure WHERE capteur_id = 1
ORDER BY timestamp DESC LIMIT 100;
```

### Configuration ESP32

| Variable | Valeur |
|----------|--------|
| WIFI_SSID | Galaxy Abeeby |
| WIFI_PASSWORD | cxie3864 |
| THINGSPEAK_API_KEY | 0TEJ9QR3RFIBFZ3M |
| RASPBERRY_IP | 10.244.96.106 |
| CAPTEUR_ID | ATOM_001 |
| SEND_INTERVAL | 20000 (20 sec) |

---

## Ressources utilisees
- Arduino IDE : https://www.arduino.cc/en/software
- ThingSpeak : https://thingspeak.com/channels/3228055
- Documentation M5Stack : https://docs.m5stack.com
- Bibliotheque Adafruit SHT4x : https://github.com/adafruit/Adafruit_SHT4X
- Bibliotheque Adafruit BMP280 : https://github.com/adafruit/Adafruit_BMP280_Library
- Documentation SQLite : https://www.sqlite.org/docs.html
- Documentation Flask : https://flask.palletsprojects.com
