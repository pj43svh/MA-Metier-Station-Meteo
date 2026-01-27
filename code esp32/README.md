# Configuration des ESP32

Guide pour configurer les deux capteurs ESP32 (Atom Lite + ENV IV).

## Materiel

- 2x M5Stack Atom Lite
- 2x Capteur ENV IV (SHT40 + BMP280)
- 2x Cable Grove

## Installation Arduino IDE

### 1. Ajouter le support ESP32

1. Ouvrir Arduino IDE
2. File → Preferences
3. Dans "Additional Board Manager URLs", ajouter :
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Tools → Board Manager → Rechercher "esp32" → Installer "esp32 by Espressif"

### 2. Installer les bibliotheques

Sketch → Include Library → Manage Libraries

Installer :
- `WiFiManager` by tzapu (version 2.x)
- `Adafruit SHT4x`
- `Adafruit BMP280`
- `Adafruit Unified Sensor`

### 3. Configurer la carte

- Tools → Board → **M5Atom** (ou ESP32 Pico Kit)
- Tools → Port → Selectionner le port COM

## Configuration du code

### Modifier l'adresse du serveur

Dans chaque fichier `.ino`, modifier la ligne :

```cpp
String SERVER_URL = "http://192.168.1.100:5000/request";
```

Remplacer `192.168.1.100` par l'adresse IP de ton Raspberry Pi.

Pour trouver l'IP du Raspberry :
```bash
# Sur le Raspberry
hostname -I
```

## Telecharger le code

### Capteur 1 (ATOM_001)

1. Ouvrir `capteur_1/capteur_1.ino`
2. Brancher l'ESP32 #1
3. Cliquer sur Upload (→)

### Capteur 2 (ATOM_002)

1. Ouvrir `capteur_2/capteur_2.ino`
2. Brancher l'ESP32 #2
3. Cliquer sur Upload (→)

## Utilisation

### Premier demarrage

1. L'ESP32 va demarrer en **mode configuration WiFi**
2. Sur ton telephone/PC, cherche le reseau WiFi :
   - Capteur 1 : `METEO_CAPTEUR_1`
   - Capteur 2 : `METEO_CAPTEUR_2`
3. Mot de passe : `meteo123`
4. Une page web s'ouvre automatiquement (ou va sur http://192.168.4.1)
5. Selectionne ton reseau WiFi et entre le mot de passe
6. L'ESP32 redemarrera et enverra les donnees

### Reconfigurer le WiFi

Si tu changes de reseau WiFi ou que la connexion echoue :

1. **Appuie sur le bouton de l'Atom Lite pendant 3 secondes**
2. La LED devient bleue
3. Le portail de configuration WiFi demarre
4. Connecte-toi au reseau `METEO_CAPTEUR_X`
5. Configure le nouveau WiFi

### Indicateurs LED

| Couleur | Signification |
|---------|---------------|
| Orange | Demarrage |
| Jaune | Connexion WiFi en cours |
| Bleu | Mode configuration WiFi |
| Vert | Connecte, envoi OK |
| Rouge | Erreur (capteur ou WiFi) |

## Branchement du capteur ENV IV

```
Atom Lite (Port Grove)     Capteur ENV IV
─────────────────────      ──────────────
GND (noir)           ───►  GND
5V  (rouge)          ───►  VCC
GPIO26 (jaune)       ───►  SDA
GPIO32 (blanc)       ───►  SCL
```

## Depannage

| Probleme | Solution |
|----------|----------|
| Le portail WiFi ne s'ouvre pas | Ouvre manuellement http://192.168.4.1 |
| Capteur non detecte | Verifie le cable Grove |
| Envoi echoue | Verifie l'IP du serveur et que Flask tourne |
| LED rouge permanente | Verifie le branchement du capteur |

## Moniteur serie

Pour voir les logs, ouvre le moniteur serie :
- Tools → Serial Monitor
- Vitesse : 115200 baud

Tu verras :
```
Station Meteo - Capteur 1 (ATOM_001)
SHT40 OK
BMP280 OK
Connexion WiFi...
WiFi connecte!
IP: 192.168.1.50

--- Mesures ---
Temperature: 22.50 C
Humidite: 55.00 %
Pression: 1013.25 hPa
Envoi vers: http://192.168.1.100:5000/request
Reponse: 201
Succes: {"Serveur local":"Succes"}
```
