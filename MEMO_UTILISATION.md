# Mémo Utilisation - Station Météo

**Pour moi - Amin Torrisi**

---

## 1. Flasher un ESP32

1. Ouvrir **Arduino IDE**
2. Fichier → Ouvrir → `code esp32/capteur_auto/capteur_auto.ino`
3. Outils → Type de carte → **M5Stack-ATOM**
4. Outils → Port → Sélectionner le port COM de l'ESP32
5. Cliquer sur **Téléverser** (flèche →)

### Librairies nécessaires
- Adafruit SHT4x
- Adafruit BMP280
- ArduinoJson

Les librairies `WebServer`, `DNSServer`, `Preferences` sont déjà incluses avec ESP32 Arduino.

---

## 2. Premier démarrage d'un ESP32

1. Brancher l'ESP32
2. Il crée automatiquement un réseau WiFi : **StationMeteo-XXXX**
3. La LED clignote = mode configuration
4. Se connecter au réseau avec son téléphone ou PC
5. Le portail s'ouvre automatiquement (sinon aller sur `192.168.4.1`)

### Sur le portail :
- **Réseau WiFi** : choisir dans la liste (scan automatique)
- **Mot de passe** : mot de passe du WiFi
- **Adresse serveur** :
  - Raspberry Pi local : `192.168.1.XXX` (l'IP du Raspberry)
  - Railway : `nurturing-achievement-production.up.railway.app`
- Cliquer **Sauvegarder et connecter**
- L'ESP32 redémarre et se connecte

---

## 3. Reconfigurer un ESP32

**Appuyer 3 secondes** sur le bouton de l'ESP32
→ Efface la config WiFi et serveur
→ Redémarre en mode portail captif
→ Refaire l'étape 2

---

## 4. Configurer le capteur (numéro + nom)

Après que l'ESP32 est connecté au WiFi :

1. Aller sur le **dashboard** → Admin ESP32
   - Railway : `https://nurturing-achievement-production.up.railway.app/admin`
   - Raspberry Pi : `http://IP_RASPBERRY:5000/admin`
2. L'ESP32 apparaît avec son adresse MAC
3. Choisir le **numéro de capteur** (1, 2, 3...)
4. Entrer un **nom** (ex: "Salon", "Extérieur")
5. Cliquer **Configurer**

---

## 5. Serveur Flask

### Sur Railway (distant)
- URL : `https://nurturing-achievement-production.up.railway.app`
- Auto-deploy quand on push sur GitHub
- Push : `git push origin main`

### Sur Raspberry Pi (local)
```bash
# Se connecter au Raspberry
ssh pi@192.168.1.XXX

# Aller dans le dossier
cd Station-meteo

# Lancer le serveur
python main.py
# ou avec gunicorn :
gunicorn main:app -b 0.0.0.0:5000
```

Le serveur tourne sur le port **5000** par défaut.

---

## 6. Base de données

### Voir les ESP32 enregistrés
```bash
sqlite3 weather_data.db
SELECT * FROM esp32_devices;
```

### Voir les dernières mesures
```bash
SELECT * FROM esp1 ORDER BY id DESC LIMIT 5;
```

### Voir les tables
```bash
.tables
```

---

## 7. Git - Commandes rapides

```bash
# Voir le statut
git status

# Ajouter + commit + push
git add .
git commit -m "Description"
git push origin main
```

---

## 8. Dépannage rapide

| Problème | Solution |
|----------|----------|
| ESP32 ne crée pas le réseau WiFi | Vérifier qu'il est bien flashé, débrancher/rebrancher |
| Le portail ne s'ouvre pas | Aller manuellement sur `192.168.4.1` |
| ESP32 connecté mais pas de données | Vérifier l'IP du serveur dans la config, vérifier que Flask tourne |
| "Hors ligne" sur le dashboard | ESP32 pas alimenté, mauvais WiFi, ou mauvaise IP serveur |
| Changer de réseau WiFi | Appui 3 sec sur le bouton → reconfigurer |
| Changer de serveur | Appui 3 sec sur le bouton → reconfigurer |
| Graphiques vides | Vérifier qu'il y a des données pour la date sélectionnée |
| Nom capteur pas à jour | Rafraîchir la page du dashboard (F5) |

---

## 9. Infos utiles

| Info | Valeur |
|------|--------|
| URL Railway | `nurturing-achievement-production.up.railway.app` |
| Port Flask | 5000 |
| IP portail ESP32 | 192.168.4.1 |
| Intervalle envoi données | 20 secondes |
| Capteur temp/humidité | SHT40 (I2C 0x44) |
| Capteur pression | BMP280 (I2C 0x76 ou 0x77) |
| Bouton ESP32 | GPIO 39 |
| LED ESP32 | GPIO 27 |
| I2C SDA | GPIO 26 |
| I2C SCL | GPIO 32 |
