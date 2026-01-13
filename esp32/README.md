# Code ESP32 - Station Météo

## Installation

### 1. Arduino IDE

1. Télécharger [Arduino IDE](https://www.arduino.cc/en/software)
2. Ajouter le support ESP32 :
   - Fichier → Préférences
   - URL de gestionnaire de cartes supplémentaires :
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
3. Outils → Gestionnaire de cartes → Rechercher "ESP32" → Installer

### 2. Bibliothèques requises

Dans Arduino IDE : Croquis → Inclure une bibliothèque → Gérer les bibliothèques

- **DHT sensor library** (par Adafruit)
- **ArduinoJson** (par Benoit Blanchon)

## Câblage

### DHT22 (Température & Humidité)

```
DHT22          ESP32
------         -----
VCC    ───────  3.3V
DATA   ───────  GPIO 4
GND    ───────  GND
```

Optionnel : résistance 10kΩ entre VCC et DATA (pull-up)

### LDR (Luminosité)

```
       3.3V
         │
        [LDR]
         │
         ├──── GPIO 34 (ADC)
         │
       [10kΩ]
         │
        GND
```

## Configuration

Modifier ces lignes dans `capteur_meteo.ino` :

```cpp
const char* WIFI_SSID = "VOTRE_SSID";
const char* WIFI_PASSWORD = "VOTRE_MOT_DE_PASSE";
const char* SERVER_URL = "http://192.168.1.XX:5000/api/mesures";
const char* ESP_ID = "ESP32_001";
```

## Upload

1. Connecter l'ESP32 en USB
2. Outils → Type de carte → ESP32 Dev Module
3. Outils → Port → Sélectionner le port COM
4. Cliquer sur "Téléverser" (→)

## Test

1. Ouvrir le Moniteur Série (115200 baud)
2. Vérifier la connexion WiFi
3. Vérifier que les mesures sont envoyées

## Dépannage

| Problème | Solution |
|----------|----------|
| DHT22 renvoie NaN | Vérifier le câblage, ajouter pull-up |
| WiFi ne se connecte pas | Vérifier SSID/mot de passe, distance |
| HTTP erreur -1 | Vérifier l'IP du Raspberry Pi |
| Valeurs LDR incorrectes | Ajuster la conversion dans le code |
