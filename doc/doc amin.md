# 1. Vue d'ensemble

## Qu'est-ce que ce projet ?

Une station meteo connectee composee de:
- 2 capteurs ESP32 (Atom Lite) avec capteurs de temperature, humidite et pression
- Un serveur Flask heberge sur Railway
- Une interface web pour visualiser les donnees en temps reel
- Une interface admin pour gerer les ESP32 a distance

## Schema simplifie

|Appareil|Transfert|Destinataire|
|-|-|-|
|ESP32 #1|WiFi / HTTPS|Serveur Flask|
|Capteur 1|-------------->|(Railway)|
||||
|ESP32 #2|WiFi / HTTPS|- API REST|
|Capteur 2|-------------->|- SQLite DB|
|||- Dashboard|
|||I|
|||V
|||Navigateur (dashboard)|

# 2. Architecture du systeme

## Stack technique

|Composant|Technologie|
|---------|-----------|
|Microcontroleur|ESP32 Atom Lite (M5Stack)|
|Capteur Temp/Humidité|SHT40 (ENV IV)|
|Capteur Pression|BMP280 (ENV IV)|
|Backend|Python Flask|
|Base de données|SQLite|
|Frontend|HTML / CSS / JavaScript|
|Herbergement|Railwx.app|
|Graphique|Matplotlib|

## Communication
```
ESP32   -->   Post /request/    --> Flask   --> SQLite
    
            (Json:temp,hum,pression)

ESP32   -->   Post /api/esp32/register  --> Flask   --> esp32_device table
    
            (Json: mac_adress, ip_adress)

ESP32   --> GET /api/esp32/config/{mac} --> Flask   --> Retourne sensor_number
```

# 3. Composants materiels

## ESP32 Atom Lite (M5Stack)

L'ATOM Lite est un microcontroleur ESP32 compact de M5Stack.
Il dispose d'un port Grove pour connecter des capteurs I2C.

Broches Grove:
- SDA: GPIO 26
- SCL: GPIO 32
- Alimentation: 5V et GND

## Capteurs ENV IV

Le module ENV IV contient deux capteurs:
- SHT40: Temperature et humidite (adresse I2C: 0x44)
- BMP280: Pression atmospherique (adresse I2C: 0x76 ou 0x77)

|Capteur|Adresse I2C|Mesures|
|-------|-----------|-------|
|SHT40|0x44 |Temperature, Humidite|
|BMP280|0x76/0x77|Pression|

# 5. Structure des fichiers

```
Station meteo/
|
|-- main.py # Point d'entree Flask
|-- route.py # Routes principales
|-- api.py # API REST + gestion ESP32
|-- esp.py # Reception donnees ESP32
|-- database.py # Fonctions SQLite
|-- statistical.py # Generation graphiques
|-- requirements.txt # Dependances Python
|
|-- templates/ # Pages HTML (Jinja2)
| |-- index.html # Dashboard principal
| |-- admin.html # Interface admin ESP32
| |-- statistical.html # Page des graphiques
| |-- history.html # Historique des donnees
| +-- about.html # Page a propos
|
|-- static/ # Fichiers statiques
| |-- style.css # Styles CSS
| |-- js/ # Scripts JavaScript
| +-- graph_*.png # Graphiques generes
|
+-- code esp32/
+-- capteur_auto/
+-- capteur_auto.ino # Code Arduino
```

# 5. Base de données

## Table espX (données des capteurs)

```
CREATE TABLE espX (
id INTEGER PRIMARY KEY AUTOINCREMENT,
temperature REAL,
humidity REAL,
pressure REAL,
date TEXT NOT NULL, -- Format: "2026-01-22"
hour TEXT NOT NULL -- Format: "14:30:45"
);
```

## Table esp32_devices (configuration)

```
CREATE TABLE esp32_devices (
id INTEGER PRIMARY KEY AUTOINCREMENT,
mac_address TEXT UNIQUE NOT NULL, -- "A4:CF:12:34:56:78"
sensor_number INTEGER, -- 1, 2, 3...
name TEXT, -- "Capteur Salon"
last_seen TEXT, -- Derniere connexion
ip_address TEXT, -- IP locale ESP32
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

# 6. Flux de données

## 1. Enregistrement d'un nouvel ESP32

Quand un ESP32 demarre pour la premiere fois:

1. Il se connecte au WiFi
2. Il recupere son adresse MAC (APRES connexion WiFi!)
3. POST /api/esp32/register avec {mac_address, ip_address}
4. Le serveur l'enregistre dans esp32_devices
5. Retourne "pending" si pas encore configure

## 2. Configuration via Admin

L'administrateur:

1. Accede a /admin
2. Voit les ESP32 en attente de configuration
3. Assigne un numero de capteur (1, 2, 3...)
4. Le serveur met a jour esp32_devices avec sensor_number

## 3. L'ESP32 recupere sa config

L'ESP32 verifie periodiquement sa configuration

1. GET /api/esp32/config/{mac}
2. Si configure: recoit sensor_number et capteur_id
3. Stocke: sensorNumber = 1, capteurID = "ATOM_001"

## 4. Envoi des donnees

Toutes les 20 secondes:

1. POST /request/ avec {capteur_id, mac_address, temperature, humidite, pression}
2. Le serveur extrait le numero du capteur_id (ATOM_001 -> 1)
3. INSERT INTO esp1 (temperature, humidity, pressure, date, hour)

# 7. API Endpoints

## Données des capteurs

|Methode|Endpoint|Description|
|-------|--------|-----------|
|GET|/api/sensors|Liste tous les capteurs|
|GET|/api/sensors/status|Statut de tous les capteurs|
|GET|/api/sensor/{id}/latest|Dernieres valeurs d'un capteur|
|GET|/api/all/latest|Dernieres valeurs de tous|
|POST|/request/|Reception donnees ESP32|

## Gestion des ESP32

|Methode|Endpoint|Description|
|-------|--------|-----------|
|POST|/api/esp32/register|Enregistre un ESP32|
|GET|/api/esp32/config/{mac}|Config d'un ESP32|
|GET|/api/esp32/devices|Liste tous les ESP32|
|POST|/api/esp32/configure|Configure un ESP32|
|POST|/api/esp32/delete|Supprime un ESP32|

# 8. Code ESP32

## Configuration WiFi

``` C++
const char* WIFI_SSID = "Bomboclat";
const char* WIFI_PASSWORD = "zyxouzyxou";
const char* SERVER_BASE =
"https://nurturing-achievement-production.up.railway.app";
```
## Cycle de vie

DEMARRAGE:

1. Init I2C, Init SHT40, Init BMP280
2. Connexion WiFi
3. Recupere MAC (IMPORTANT: apres WiFi.begin()!)
4. POST /api/esp32/register {mac, ip}
5. GET /api/esp32/config/{mac} -> sensor_number

BOUCLE PRINCIPALE:

- Toutes les 20 sec: Lire capteurs, POST /request/
- Si pas configure: Toutes les 60 sec, verifier config
- Si bouton 3 sec: ESP.restart()

## Format des données envoyées

```json
{
"capteur_id": "ATOM_001",
"mac_address": "A4:CF:12:34:56:78",
"temperature": 23.45,
"humidite": 45.67,
"pression": 1013.25
}
```

# 9. Interface

|URL|Desciption|
|-|-|
|/|Dashboard - donnees en temps reel|
|/admin|Administration des ESP32|
|/statistical|Graphiques|
|/history|Historique des mesures|
|/about|A propos|

## Dashboard (/)

- Affiche une carte par capteur
- Donnees actualisees toutes les 5 secondes
- Indicateur online/offline

## Admin (/admin)

- Liste tous les ESP32 enregistres
- Permet d'assigner un numero de capteur (1, 2, 3...)
- Affiche MAC, IP, derniere connexion
- Bouton pour supprimer un ESP32

# 10. Deploiement Railway

## URL de production

https://nurturing-achievement-production.up.railway.app

## Commande de deploiement

``` bash
# Push vers GitHub (declenche auto-deploy)
git push origin interface-web-local:interface-web
# Si Railway ne prend pas le bon commit:
railway deploy --commit 76a7f2bb56f89a54ff585d7b71418cb7397b3a96
```

## Fichier requirements.txt

```
flask==3.0.0
gunicorn==21.2.0
matplotlib==3.8.0
numpy==1.26.4
```

# 11. Problèmes resolus

## Bug #1: MAC Address 00:00:00:00:00:00

Probleme: Tous les ESP32 s'enregistraient avec la meme MAC invalide.

Cause: WiFi.macAddress() etait appele AVANT WiFi.begin().
Solution:

```C++
// AVANT (bug)
macAddress = WiFi.macAddress(); // Retourne 00:00:00:00:00:00
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
// APRES (corrige)
WiFi.mode(WIFI_STA);
WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
// ... attendre connexion ...
macAddress = WiFi.macAddress(); // Retourne vraie MAC
```

## Bug #2: Graphiques vides

Probleme: Les graphiques ne s'affichaient pas si esp1 etait vide.

Cause: L'axe des heures utilisait toujours esp1 en dur.

Solution: Utiliser dynamiquement le premier capteur disponible.

## Bug #3: Double rafraichissement

Probleme: Les graphiques se generaient 2 fois a chaque clic.

Cause: refresh_statistical() appele 2 fois dans le JavaScript.

Solution: Supprime l'appel duplique.