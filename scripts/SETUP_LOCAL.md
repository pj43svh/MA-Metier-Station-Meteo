# Guide d'installation - Station Meteo 100% Locale

Ce guide explique comment configurer la station meteo pour fonctionner
entierement en local, sans connexion internet.

## Architecture

```
              [ESP32 Access Point]
              WiFi: "StationMeteo"
              IP: 192.168.4.1
                      |
    +--------+--------+--------+
    |        |        |        |
 [ESP32    [ESP32   [Raspberry Pi]
 Capteur1] Capteur2] Flask + SQLite
                     IP: 192.168.4.10
```

---

## Etape 1: Flasher l'ESP32 Access Point

### Materiel necessaire
- 1x ESP32 (M5Stack Atom Lite recommande)
- Cable USB-C

### Instructions
1. Ouvrir Arduino IDE
2. Ouvrir le fichier `code esp32/access_point_server/access_point_server.ino`
3. Selectionner la carte "M5Stack-ATOM" (ou votre ESP32)
4. Selectionner le port COM
5. Cliquer sur "Upload"

### Verification
- La LED clignote lentement = Access Point actif
- Depuis un telephone, verifier que le WiFi "StationMeteo" apparait

### Configuration par defaut
- SSID: `StationMeteo`
- Password: `meteo2026`
- IP: `192.168.4.1`

---

## Etape 2: Configurer le Raspberry Pi

### 2.1 Connecter au WiFi StationMeteo

```bash
# Editer la configuration WiFi
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Ajouter:
```
network={
    ssid="StationMeteo"
    psk="meteo2026"
    priority=1
}
```

### 2.2 Configurer une IP statique

```bash
sudo nano /etc/dhcpcd.conf
```

Ajouter a la fin:
```
interface wlan0
static ip_address=192.168.4.10/24
static routers=192.168.4.1
static domain_name_servers=192.168.4.1
```

### 2.3 Redemarrer le WiFi

```bash
sudo systemctl restart dhcpcd
sudo systemctl restart wpa_supplicant
```

### 2.4 Verifier la connexion

```bash
# Doit retourner 192.168.4.10
hostname -I

# Doit repondre
ping 192.168.4.1
```

---

## Etape 3: Installer l'application Flask

### 3.1 Cloner le projet (si pas deja fait)

```bash
cd ~
git clone <url-du-repo> station-meteo
cd station-meteo
```

### 3.2 Installer les dependances

```bash
# Python et pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Creer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dependances
pip install -r requirements.txt
```

### 3.3 Demarrer le serveur

```bash
chmod +x scripts/start_local.sh
./scripts/start_local.sh
```

### 3.4 Demarrage automatique (optionnel)

Pour que le serveur demarre automatiquement au boot:

```bash
sudo nano /etc/systemd/system/station-meteo.service
```

Contenu:
```ini
[Unit]
Description=Station Meteo Flask Server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/station-meteo
ExecStart=/home/pi/station-meteo/venv/bin/gunicorn app.main:app --bind 0.0.0.0:5000
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer:
```bash
sudo systemctl enable station-meteo
sudo systemctl start station-meteo
```

---

## Etape 4: Flasher les ESP32 Capteurs

### Pour chaque capteur

1. Ouvrir `code esp32/capteur_local/capteur_local.ino`
2. Flasher l'ESP32
3. Au premier demarrage, le capteur cree un WiFi "ConfigCapteur"
4. Se connecter a ce WiFi et ouvrir http://192.168.4.1/
5. Configurer:
   - SSID: `StationMeteo`
   - Password: `meteo2026`
   - IP serveur: `192.168.4.10`
   - Port: `5000`
   - Nom capteur: `ATOM_001` (ou 002, 003...)
6. Cliquer "Enregistrer"

### Alternative: Configuration par defaut

Si vous ne modifiez pas le code, les valeurs par defaut sont:
- WiFi: StationMeteo / meteo2026
- Serveur: 192.168.4.10:5000
- Nom: ATOM_001

Le capteur se connectera automatiquement si l'Access Point est actif.

### Reset d'un capteur

- Appuyer sur le bouton pendant 3 secondes
- Le capteur redemarre en mode configuration

---

## Etape 5: Acceder a l'interface web

Depuis n'importe quel appareil connecte au WiFi "StationMeteo":

1. Ouvrir un navigateur
2. Aller sur: `http://192.168.4.10:5000`

### Pages disponibles
- `/` - Dashboard avec donnees en temps reel
- `/history` - Historique des mesures
- `/statistical` - Graphiques
- `/admin` - Gestion des capteurs

---

## Depannage

### Le WiFi "StationMeteo" n'apparait pas
- Verifier que l'ESP32 Access Point est alimente
- Verifier que le code a ete correctement flashe
- La LED doit clignoter

### Le Raspberry Pi ne se connecte pas
- Verifier les identifiants WiFi
- Verifier la configuration IP statique
- Redemarrer le Pi

### Les capteurs n'envoient pas de donnees
- Verifier la configuration du capteur (IP serveur)
- Verifier que Flask tourne sur le Pi
- Regarder les logs: `journalctl -u station-meteo -f`

### L'interface web ne charge pas
- Verifier que Flask tourne: `curl http://192.168.4.10:5000`
- Verifier le firewall: `sudo ufw allow 5000`

---

## Configuration avancee

### Changer le SSID/Password

Dans `access_point_server.ino`:
```cpp
const char* AP_SSID = "MonReseau";
const char* AP_PASSWORD = "monmotdepasse";
```

### Changer l'IP du Pi

1. Modifier `/etc/dhcpcd.conf` sur le Pi
2. Mettre a jour la config des capteurs

### Ajouter plus de capteurs

Le systeme supporte jusqu'a 8 appareils connectes simultanement.
Chaque capteur doit avoir un nom unique (ATOM_001, ATOM_002, etc.)

---

## Resume des IPs

| Appareil | IP |
|----------|-----|
| ESP32 Access Point | 192.168.4.1 |
| Raspberry Pi | 192.168.4.10 |
| Capteurs | DHCP (192.168.4.x) |
| Interface web | http://192.168.4.10:5000 |
