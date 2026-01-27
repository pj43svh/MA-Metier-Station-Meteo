# Guide d'Installation ESP32 - Pas a Pas

## Materiel necessaire

- 2x M5Stack Atom Lite (ESP32-PICO)
- 2x Capteur ENV IV
- 2x Cable Grove
- Cable USB-C

---

## ETAPE 1 : Configurer Arduino IDE

### 1.1 Ajouter l'URL ESP32

1. Ouvre **Arduino IDE**
2. Va dans **File** → **Preferences**
3. Dans le champ **"Additional Board Manager URLs"**, colle :
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Clique **OK**

### 1.2 Installer le package ESP32

1. Va dans **Tools** → **Board** → **Boards Manager**
2. Dans la recherche, tape : `esp32`
3. Trouve **"esp32 by Espressif Systems"**
4. Clique **INSTALL**

⚠️ **ATTENTION** : N'utilise PAS "Arduino ESP32 Boards", utilise celui de **Espressif Systems** !

### 1.3 Selectionner la carte

1. Va dans **Tools** → **Board** → **esp32**
2. Selectionne **M5Atom** (ou "ESP32 Pico Kit" si M5Atom n'apparait pas)

⚠️ **NE PAS** selectionner ESP32S3 Dev Module !

---

## ETAPE 2 : Installer les bibliotheques

1. Va dans **Sketch** → **Include Library** → **Manage Libraries**
2. Installe ces 4 bibliotheques :

| Bibliotheque | Auteur | A quoi ca sert |
|--------------|--------|----------------|
| WiFiManager | tzapu | Configuration WiFi via portail web |
| Adafruit SHT4x | Adafruit | Capteur temperature + humidite |
| Adafruit BMP280 | Adafruit | Capteur pression |
| Adafruit Unified Sensor | Adafruit | Dependance pour les capteurs |

### Comment installer une bibliotheque :

1. Tape le nom dans la barre de recherche
2. Trouve la bonne bibliotheque
3. Clique **INSTALL**

---

## ETAPE 3 : Modifier l'adresse du serveur

Avant d'uploader, tu dois modifier l'IP du serveur dans le code.

### 3.1 Trouver l'IP du Raspberry Pi

Sur le Raspberry, ouvre un terminal et tape :
```bash
hostname -I
```
Exemple de resultat : `192.168.1.50`

### 3.2 Modifier le code

Dans le fichier `.ino`, trouve cette ligne (vers la ligne 15) :
```cpp
String SERVER_URL = "http://192.168.1.100:5000/request";
```

Remplace `192.168.1.100` par l'IP de ton Raspberry :
```cpp
String SERVER_URL = "http://192.168.1.50:5000/request";
```

---

## ETAPE 4 : Uploader le code

### Premier ESP32 (Capteur 1)

1. Branche le **premier** Atom Lite en USB
2. Branche le capteur ENV IV sur le port Grove
3. Dans Arduino IDE :
   - **File** → **Open** → `code esp32/capteur_1/capteur_1.ino`
   - **Tools** → **Port** → Selectionne le port COM (ex: COM6)
   - **Tools** → **Board** → **M5Atom**
4. Clique sur **Upload** (fleche →)
5. Attends que ca dise "Done uploading"

### Deuxieme ESP32 (Capteur 2)

1. Debranche le premier Atom Lite
2. Branche le **deuxieme** Atom Lite en USB
3. Branche le capteur ENV IV
4. Dans Arduino IDE :
   - **File** → **Open** → `code esp32/capteur_2/capteur_2.ino`
   - **Tools** → **Port** → Selectionne le port COM
5. Clique sur **Upload** (fleche →)

---

## ETAPE 5 : Configurer le WiFi

### 5.1 Premier demarrage

Quand l'ESP32 demarre pour la premiere fois, il cree un reseau WiFi.

### 5.2 Se connecter au portail

1. Sur ton telephone ou PC, va dans les reseaux WiFi
2. Connecte-toi a :
   - **METEO_CAPTEUR_1** (pour le capteur 1)
   - **METEO_CAPTEUR_2** (pour le capteur 2)
3. Mot de passe : `meteo123`

### 5.3 Configurer le WiFi

1. Une page web s'ouvre automatiquement
   - Si elle ne s'ouvre pas, va sur : **http://192.168.4.1**
2. Clique sur **Configure WiFi**
3. Selectionne ton reseau WiFi (ex: ta box internet)
4. Entre le mot de passe de ton WiFi
5. Clique **Save**
6. L'ESP32 redemarrera et se connectera automatiquement

---

## ETAPE 6 : Verifier que ca marche

### 6.1 Moniteur Serie

1. Dans Arduino IDE : **Tools** → **Serial Monitor**
2. En bas a droite, selectionne **115200 baud**
3. Tu dois voir :

```
========================================
   Station Meteo - Capteur 1 (ATOM_001)
========================================

SHT40 OK
BMP280 OK
Connexion WiFi...
WiFi connecte!
IP: 192.168.1.50

--- Pret! ---
Appuyez 3 sec sur le bouton pour reconfigurer le WiFi

--- Mesures ---
Temperature: 22.50 C
Humidite: 55.00 %
Pression: 1013.25 hPa
Envoi vers: http://192.168.1.100:5000/request
Reponse: 201
Succes: {"Serveur local":"Succes"}
```

### 6.2 Interface Web

1. Lance le serveur Flask sur le Raspberry :
   ```bash
   cd /chemin/vers/projet
   python main.py
   ```
2. Ouvre un navigateur : **http://IP_DU_RASPBERRY:5000**
3. Tu dois voir les donnees des capteurs sur le dashboard

---

## Reconfigurer le WiFi plus tard

Si tu changes de reseau WiFi :

1. **Appuie sur le bouton de l'Atom Lite pendant 3 secondes**
2. La LED devient bleue
3. Le portail de configuration redemarre
4. Connecte-toi au reseau METEO_CAPTEUR_X
5. Configure le nouveau WiFi

---

## Depannage

### "Wrong chip" ou erreur de carte

→ Verifie que tu as selectionne **M5Atom** (pas ESP32S3)

### "Port not found" ou pas de port COM

→ Verifie le cable USB et les drivers
→ Essaie un autre port USB

### "SHT40 non trouve" ou "BMP280 non trouve"

→ Verifie que le capteur ENV IV est bien branche sur le port Grove
→ Verifie que le cable est bien enfonce

### L'envoi echoue (code -1)

→ Verifie que le serveur Flask tourne sur le Raspberry
→ Verifie l'IP dans le code
→ Verifie que l'ESP32 et le Raspberry sont sur le meme reseau WiFi

### Le portail WiFi ne s'ouvre pas

→ Ouvre manuellement **http://192.168.4.1** dans ton navigateur

---

## Resume

| Action | Capteur 1 | Capteur 2 |
|--------|-----------|-----------|
| Code | `capteur_1.ino` | `capteur_2.ino` |
| ID | ATOM_001 | ATOM_002 |
| Reseau WiFi | METEO_CAPTEUR_1 | METEO_CAPTEUR_2 |
| Mot de passe | meteo123 | meteo123 |
