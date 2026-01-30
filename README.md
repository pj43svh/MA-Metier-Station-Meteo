# Station Météo IoT - ESP32

Système de monitoring environnemental connecté développé au CPNV. Mesure en temps réel la température, l'humidité et la pression atmosphérique via des capteurs ESP32, avec un dashboard web accessible de partout.

---

## Fonctionnalités

- **Capteurs ESP32** (Atom Lite M5Stack) avec SHT40 + BMP280
- **WiFi Manager** : portail captif pour configurer les capteurs sans modifier le code
- **Dashboard temps réel** avec indicateur de statut (vert/orange/rouge)
- **Graphiques** d'évolution (Chart.js)
- **Historique** complet des mesures
- **Admin panel** pour nommer et gérer les capteurs
- **Déploiement** cloud (Railway) ou local (Raspberry Pi)

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Microcontrôleur | ESP32 Atom Lite (M5Stack) |
| Capteurs | SHT40 (temp/hum) + BMP280 (pression) |
| Backend | Python Flask + SQLite |
| Frontend | HTML / CSS / JavaScript / Chart.js |
| Cloud | Railway.app |
| Local | Raspberry Pi |

---

## Installation

### 1. Cloner le répertoire

```bash
git clone https://github.com/pj43svh/MA-Metier-Station-Meteo.git
cd MA-Metier-Station-Meteo
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer le serveur

```bash
python app/main.py
```

Le serveur démarre sur `http://localhost:5000`.

### 4. Flasher un ESP32

1. Ouvrir `code esp32/capteur_auto/capteur_auto.ino` dans Arduino IDE
2. Carte : **M5Stack-ATOM**
3. Installer les librairies : Adafruit SHT4x, Adafruit BMP280, ArduinoJson
4. Téléverser
5. Au premier démarrage, se connecter au réseau **StationMeteo-XXXX** et configurer via le portail captif

---

## Documentation

- [Documentation Technique](DOCUMENTATION_TECHNIQUE.md) (PDF disponible)
- [Guide Utilisateur](GUIDE_UTILISATEUR.md) (PDF disponible)
- [Cahier des charges](Cahier%20des%20charges%20station%20météo.md)

---

## Liens utiles

- [KanBan Trello](https://trello.com/invite/b/6965f7158ea7d04041b38cae/ATTI88c024b14cb4c763a97249e76ec05ee959BB9D3A/station-meteo-esp32-rpi)
- [Disponibilités équipe](disponibilite.md)

---

## Équipe

| Membre | GitHub |
|--------|--------|
| Amin Torrisi | [@pj43svh](https://github.com/pj43svh) |
| Lilibeth Zerda Macias | [@Abeeby](https://github.com/Abeeby) |
| Aurélien Robert | [@AurelienRo](https://github.com/AurelienRo) |
| Théo Läderach | [@TonUserName](https://github.com/TonUserName) |

---

### CPNV Sainte-Croix

![cpnv_logo](https://www.cpnv.ch/app/uploads/2018/05/logo.png)
