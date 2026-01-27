# Documentation Technique - Station Météo ESP32

**Auteur:** Amin Torrisi / Équipe CPNV
**Date:** Janvier 2026
**Version:** 2.0 (avec interface admin)

---

## Table des Matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture du système](#2-architecture-du-système)
3. [Composants matériels](#3-composants-matériels)
4. [Structure des fichiers](#4-structure-des-fichiers)
5. [Base de données](#5-base-de-données)
6. [Flux de données](#6-flux-de-données)
7. [API Endpoints](#7-api-endpoints)
8. [Code ESP32](#8-code-esp32)
9. [Interface Web](#9-interface-web)
10. [Déploiement Railway](#10-déploiement-railway)
11. [Problèmes résolus](#11-problèmes-résolus)

---

## 1. Vue d'ensemble

### Qu'est-ce que ce projet ?

Une station météo connectée composée de:
- **2 capteurs ESP32** (Atom Lite) avec capteurs de température, humidité et pression
- **Un serveur Flask** hébergé sur Railway
- **Une interface web** pour visualiser les données en temps réel
- **Une interface admin** pour gérer les ESP32 à distance

### Schéma simplifié

```
┌─────────────────┐     WiFi/HTTPS      ┌──────────────────┐
│   ESP32 #1      │ ──────────────────► │                  │
│   (Capteur 1)   │                     │   Serveur Flask  │
└─────────────────┘                     │   (Railway)      │
                                        │                  │
┌─────────────────┐     WiFi/HTTPS      │   - API REST     │
│   ESP32 #2      │ ──────────────────► │   - SQLite DB    │
│   (Capteur 2)   │                     │   - Dashboard    │
└─────────────────┘                     └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │   Navigateur     │
                                        │   (Dashboard)    │
                                        └──────────────────┘
```

---

## 2. Architecture du système

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| Microcontrôleur | ESP32 Atom Lite (M5Stack) |
| Capteur Temp/Humidité | SHT40 (ENV IV) |
| Capteur Pression | BMP280 (ENV IV) |
| Backend | Python Flask |
| Base de données | SQLite |
| Frontend | HTML/CSS/JavaScript |
| Hébergement | Railway.app |
| Graphiques | Matplotlib |

### Communication

```
ESP32 ──► POST /request/ ──► Flask ──► SQLite
         (JSON: temp, hum, pression)

ESP32 ──► POST /api/esp32/register ──► Flask ──► esp32_devices table
         (JSON: mac_address, ip_address)

ESP32 ──► GET /api/esp32/config/{mac} ──► Flask ──► Retourne sensor_number
```

---

## 3. Composants matériels

### ESP32 Atom Lite (M5Stack)

```
┌─────────────────────────────────────┐
│         ATOM LITE                   │
│    ┌─────────────────────┐          │
│    │      LED (G27)      │          │
│    │      BOUTON (G39)   │          │
│    └─────────────────────┘          │
│                                     │
│    Grove Port:                      │
│    - SDA: G26                       │
│    - SCL: G32                       │
│    - 5V, GND                        │
└─────────────────────────────────────┘
         │
         │ I2C
         ▼
┌─────────────────────────────────────┐
│         ENV IV                      │
│    ┌─────────┐  ┌─────────┐         │
│    │ SHT40   │  │ BMP280  │         │
│    │ (Temp)  │  │ (Press) │         │
│    │ (Hum)   │  │         │         │
│    └─────────┘  └─────────┘         │
└─────────────────────────────────────┘
```

### Adresses I2C

| Capteur | Adresse |
|---------|---------|
| SHT40 | 0x44 |
| BMP280 | 0x76 ou 0x77 |

---

## 4. Structure des fichiers

```
Station meteo/
│
├── main.py                 # Point d'entrée Flask
├── route.py                # Routes principales (/, /admin, /about, etc.)
├── api.py                  # API REST + gestion ESP32
├── esp.py                  # Réception données ESP32 (/request/)
├── database.py             # Fonctions SQLite
├── statistical.py          # Génération des graphiques Matplotlib
├── requirements.txt        # Dépendances Python
│
├── templates/              # Pages HTML (Jinja2)
│   ├── index.html          # Dashboard principal
│   ├── admin.html          # Interface admin ESP32
│   ├── statistical.html    # Page des graphiques
│   ├── history.html        # Historique des données
│   └── about.html          # Page à propos
│
├── static/                 # Fichiers statiques
│   ├── style.css           # Styles CSS
│   ├── icone.png           # Favicon
│   ├── js/
│   │   ├── data.js         # JS Dashboard
│   │   ├── admin.js        # JS Admin
│   │   ├── statistical.js  # JS Graphiques
│   │   └── history.js      # JS Historique
│   └── graph_*.png         # Graphiques générés
│
├── code esp32/
│   └── capteur_auto/
│       └── capteur_auto.ino  # Code Arduino ESP32
│
└── weather_data.db         # Base SQLite (créée automatiquement)
```

---

## 5. Base de données

### Tables

#### Table `esp1`, `esp2`, ... (données des capteurs)

```sql
CREATE TABLE espX (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    date TEXT NOT NULL,      -- Format: "2026-01-22"
    hour TEXT NOT NULL       -- Format: "14:30:45"
);
```

#### Table `esp32_devices` (configuration des ESP32)

```sql
CREATE TABLE esp32_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address TEXT UNIQUE NOT NULL,  -- Ex: "A4:CF:12:34:56:78"
    sensor_number INTEGER,              -- 1, 2, 3... (NULL = pas configuré)
    name TEXT,                          -- "Capteur Salon"
    last_seen TEXT,                     -- Dernière connexion
    ip_address TEXT,                    -- IP locale de l'ESP32
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Relation MAC ↔ Capteur

```
┌────────────────────┐         ┌─────────────┐
│   esp32_devices    │         │    espX     │
├────────────────────┤         ├─────────────┤
│ mac: A4:CF:12:...  │────────►│ temperature │
│ sensor_number: 1   │  ATOM_001│ humidity    │
│ name: "Salon"      │  = esp1  │ pressure    │
└────────────────────┘         └─────────────┘
```

---

## 6. Flux de données

### 1. Enregistrement d'un nouvel ESP32

```
┌──────────┐                              ┌──────────┐
│  ESP32   │                              │  Serveur │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │  POST /api/esp32/register               │
     │  {"mac_address": "A4:CF:...",          │
     │   "ip_address": "192.168.1.50"}        │
     │────────────────────────────────────────►│
     │                                         │
     │                                         │ INSERT INTO esp32_devices
     │                                         │ (si nouveau)
     │                                         │
     │  {"status": "pending",                  │
     │   "message": "En attente config"}      │
     │◄────────────────────────────────────────│
     │                                         │
```

### 2. Configuration via Admin

```
┌──────────┐                              ┌──────────┐
│  Admin   │                              │  Serveur │
│  (Web)   │                              │          │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │  POST /api/esp32/configure              │
     │  {"mac_address": "A4:CF:...",          │
     │   "sensor_number": 1,                   │
     │   "name": "Capteur Salon"}             │
     │────────────────────────────────────────►│
     │                                         │
     │                                         │ UPDATE esp32_devices
     │                                         │ SET sensor_number = 1
     │                                         │
     │  {"status": "success"}                  │
     │◄────────────────────────────────────────│
```

### 3. L'ESP32 récupère sa config

```
┌──────────┐                              ┌──────────┐
│  ESP32   │                              │  Serveur │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │  GET /api/esp32/config/A4:CF:...       │
     │────────────────────────────────────────►│
     │                                         │
     │  {"status": "configured",               │
     │   "sensor_number": 1,                   │
     │   "capteur_id": "ATOM_001"}            │
     │◄────────────────────────────────────────│
     │                                         │
     │  (ESP32 stocke: sensorNumber = 1)      │
     │  (ESP32 stocke: capteurID = "ATOM_001")│
```

### 4. Envoi des données

```
┌──────────┐                              ┌──────────┐
│  ESP32   │                              │  Serveur │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │  POST /request/                         │
     │  {"capteur_id": "ATOM_001",            │
     │   "mac_address": "A4:CF:...",          │
     │   "temperature": 23.5,                  │
     │   "humidite": 45.2,                    │
     │   "pression": 1013.25}                 │
     │────────────────────────────────────────►│
     │                                         │
     │                                         │ ATOM_001 → esp1
     │                                         │ INSERT INTO esp1 (...)
     │                                         │ UPDATE last_seen
     │                                         │
     │  {"status": "success"}                  │
     │◄────────────────────────────────────────│
```

---

## 7. API Endpoints

### Données des capteurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/sensors` | Liste tous les capteurs |
| GET | `/api/sensors/status` | Statut de tous les capteurs |
| GET | `/api/sensor/{id}/latest` | Dernières valeurs d'un capteur |
| GET | `/api/sensor/{id}/history?date=2026-01-22` | Historique |
| GET | `/api/all/latest` | Dernières valeurs de tous |
| POST | `/request/` | Réception données ESP32 |

### Gestion des ESP32

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/esp32/register` | Enregistre un ESP32 |
| GET | `/api/esp32/config/{mac}` | Config d'un ESP32 |
| GET | `/api/esp32/devices` | Liste tous les ESP32 |
| POST | `/api/esp32/configure` | Configure un ESP32 |
| POST | `/api/esp32/delete` | Supprime un ESP32 |

### Graphiques

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/statistical_refresh?date=2026-01-22` | Régénère les graphiques |
| GET | `/api/dates_unique` | Liste des dates disponibles |

### Exemple de requêtes

```bash
# Lister les capteurs
curl https://nurturing-achievement-production.up.railway.app/api/sensors

# Dernières valeurs du capteur 1
curl https://nurturing-achievement-production.up.railway.app/api/sensor/1/latest

# Enregistrer un ESP32
curl -X POST https://nurturing-achievement-production.up.railway.app/api/esp32/register \
  -H "Content-Type: application/json" \
  -d '{"mac_address": "A4:CF:12:34:56:78", "ip_address": "192.168.1.50"}'
```

---

## 8. Code ESP32

### Configuration WiFi

```cpp
const char* WIFI_SSID = "Bomboclat";
const char* WIFI_PASSWORD = "zyxouzyxou";
const char* SERVER_BASE = "https://nurturing-achievement-production.up.railway.app";
```

### Cycle de vie

```
DÉMARRAGE
    │
    ▼
┌───────────────┐
│ Init I2C      │
│ Init SHT40    │
│ Init BMP280   │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Connexion     │
│ WiFi          │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Récupère MAC  │◄── IMPORTANT: après WiFi.begin()
│ (WiFi.macAddress())
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ POST /api/esp32/register
│ {mac, ip}     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ GET /api/esp32/config/{mac}
│ → sensor_number
└───────┬───────┘
        │
        ▼
┌───────────────────────────────────┐
│           BOUCLE PRINCIPALE       │
│  ┌─────────────────────────────┐  │
│  │ Toutes les 20 sec:          │  │
│  │  - Lire capteurs            │  │
│  │  - POST /request/           │  │
│  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐  │
│  │ Si pas configuré:           │  │
│  │  - Toutes les 60 sec        │  │
│  │  - GET /api/esp32/config    │  │
│  └─────────────────────────────┘  │
│  ┌─────────────────────────────┐  │
│  │ Si bouton 3 sec:            │  │
│  │  - ESP.restart()            │  │
│  └─────────────────────────────┘  │
└───────────────────────────────────┘
```

### Format des données envoyées

```json
{
  "capteur_id": "ATOM_001",
  "mac_address": "A4:CF:12:34:56:78",
  "temperature": 23.45,
  "humidite": 45.67,
  "pression": 1013.25
}
```

### Mapping capteur_id → table

| capteur_id | Table SQLite |
|------------|--------------|
| ATOM_001 | esp1 |
| ATOM_002 | esp2 |
| ATOM_003 | esp3 |
| ... | ... |

---

## 9. Interface Web

### Pages disponibles

| URL | Description |
|-----|-------------|
| `/` | Dashboard - affiche les données en temps réel |
| `/admin` | Administration des ESP32 |
| `/statistical` | Graphiques (température, humidité, pression) |
| `/history` | Historique des mesures |
| `/about` | À propos |

### Dashboard (`/`)

- Affiche une carte par capteur
- Données actualisées toutes les 5 secondes
- Indicateur online/offline

### Admin (`/admin`)

- Liste tous les ESP32 enregistrés
- Permet d'assigner un numéro de capteur (1, 2, 3...)
- Affiche MAC, IP, dernière connexion
- Bouton pour supprimer un ESP32

### Graphiques (`/statistical`)

- Graphique ligne: Températures
- Graphique ligne: Pressions
- Graphique barres: Humidité
- Sélecteur de date
- Actualisation automatique

---

## 10. Déploiement Railway

### URL de production

```
https://nurturing-achievement-production.up.railway.app
```

### Variables d'environnement

| Variable | Valeur |
|----------|--------|
| DATABASE_PATH | weather_data.db |

### Commande de déploiement

```bash
# Push vers GitHub (déclenche auto-deploy)
git push origin interface-web-local:interface-web

# Si Railway ne prend pas le bon commit:
# Utiliser le SHA complet du commit
railway deploy --commit 76a7f2bb56f89a54ff585d7b71418cb7397b3a96
```

### Fichier requirements.txt

```
flask==3.0.0
gunicorn==21.2.0
matplotlib==3.8.0
numpy==1.26.4
```

---

## 11. Problèmes résolus

### Bug #1: MAC Address `00:00:00:00:00:00`

**Problème:** Tous les ESP32 s'enregistraient avec la même MAC invalide.

**Cause:** `WiFi.macAddress()` était appelé AVANT `WiFi.begin()`.

**Solution:**
```cpp
// AVANT (bug)
macAddress = WiFi.macAddress();  // Retourne 00:00:00:00:00:00
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

// APRÈS (corrigé)
WiFi.mode(WIFI_STA);
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
// ... attendre connexion ...
macAddress = WiFi.macAddress();  // Retourne vraie MAC
```

### Bug #2: Graphiques vides

**Problème:** Les graphiques ne s'affichaient pas si `esp1` était vide.

**Cause:** L'axe des heures utilisait toujours `esp1` en dur.

**Solution:**
```python
# AVANT
if type_str == "hour":
    device_name = "esp1"  # Hardcodé!

# APRÈS
if type_str == "hour":
    sensors = db.get_all_sensors()
    device_name = sensors[0] if sensors else "esp1"
```

### Bug #3: Double rafraîchissement

**Problème:** Les graphiques se généraient 2 fois à chaque clic.

**Cause:** `refresh_statistical()` appelé 2 fois dans le JavaScript.

**Solution:** Supprimé l'appel dupliqué.

### Bug #4: "Sensor 32_devices" sur le dashboard

**Problème:** La table `esp32_devices` apparaissait comme un capteur.

**Cause:** `get_all_sensors()` retournait toutes les tables `esp%`.

**Solution:**
```python
sensors = [t[0] for t in tables if t[0] != 'esp32_devices']
```

---

## Annexe: Commandes utiles

### Arduino IDE

```bash
# Sélectionner la carte
Outils → Type de carte → ESP32 Arduino → M5Stack-ATOM

# Installer les librairies
- Adafruit SHT4x
- Adafruit BMP280
- ArduinoJson
```

### SQLite (debug)

```bash
# Ouvrir la base
sqlite3 weather_data.db

# Voir les tables
.tables

# Voir les ESP32 enregistrés
SELECT * FROM esp32_devices;

# Dernières mesures
SELECT * FROM esp1 ORDER BY id DESC LIMIT 5;
```

### Git

```bash
# Voir les commits récents
git log --oneline -5

# Push vers Railway
git push origin interface-web-local:interface-web
```

---

## Contact

- **GitHub:** https://github.com/pj43svh/MA-Metier-Station-Meteo
- **Trello:** https://trello.com/b/mbKZJSjJ/station-météo-esp32-rpi
- **CPNV:** https://cpnv.ch
