# Station Meteo Locale - Guide Complet
## Raspberry Pi + ESP32 Access Point

**Auteur:** Amin
**Date:** Janvier 2026

---

## Introduction

Ce guide explique comment faire fonctionner la station meteo en mode **100% local**, sans connexion internet. L'ESP32 cree son propre reseau WiFi auquel se connectent les capteurs et le Raspberry Pi.

---

## Architecture du systeme

```
                    [ESP32 Access Point]
                    SSID: "StationMeteo"
                    Password: "meteo2026"
                    IP: 192.168.4.1
                            |
            +---------------+---------------+
            |               |               |
      [ESP32 Capteur 1] [ESP32 Capteur 2] [Raspberry Pi]
      ATOM_001          ATOM_002          IP: 192.168.4.10
      Temperature       Temperature       Flask + SQLite
      Humidite          Humidite          Interface Web
      Pression          Pression
```

**Flux des donnees:**
1. L'ESP32 Access Point cree le reseau WiFi "StationMeteo"
2. Le Raspberry Pi se connecte au WiFi et lance Flask
3. Les ESP32 capteurs se connectent et envoient leurs donnees toutes les 20 secondes
4. Les utilisateurs accedent a l'interface web via http://192.168.4.10:5000

---

## Materiel necessaire

| Composant | Quantite | Role |
|-----------|----------|------|
| ESP32 (Atom Lite) | 1 | Access Point (cree le WiFi) |
| ESP32 (Atom Lite) | 2-3 | Capteurs meteo |
| Capteur ENV IV | 2-3 | SHT40 (temp/hum) + BMP280 (pression) |
| Raspberry Pi | 1 | Serveur Flask + base de donnees |
| Alimentation USB | 4-5 | Pour alimenter tous les appareils |

---

## Partie 1: ESP32 Access Point

### 1.1 Fichier a utiliser
```
code esp32/access_point_server/access_point_server.ino
```

### 1.2 Configuration par defaut
| Parametre | Valeur |
|-----------|--------|
| SSID | StationMeteo |
| Password | meteo2026 |
| IP | 192.168.4.1 |
| Max connexions | 8 |

### 1.3 Flasher l'ESP32

1. Ouvrir **Arduino IDE**
2. Ouvrir le fichier `access_point_server.ino`
3. Selectionner la carte: **M5Stack-ATOM** (ou ESP32)
4. Selectionner le port COM
5. Cliquer sur **Upload**

### 1.4 Verification

- La LED clignote lentement = Access Point actif
- Depuis un telephone, verifier que le WiFi **"StationMeteo"** apparait
- Se connecter et ouvrir http://192.168.4.1 pour voir la page d'info

### 1.5 Modifier le SSID/Password (optionnel)

Dans le fichier `access_point_server.ino`, modifier:
```cpp
const char* AP_SSID = "StationMeteo";      // Changer ici
const char* AP_PASSWORD = "meteo2026";     // Changer ici
```

---

## Partie 2: Raspberry Pi

### 2.1 Se connecter au WiFi StationMeteo

**Methode 1: Interface graphique**
1. Cliquer sur l'icone WiFi
2. Selectionner "StationMeteo"
3. Entrer le mot de passe: `meteo2026`

**Methode 2: Ligne de commande**
```bash
# Editer la configuration
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Ajouter a la fin:
```
network={
    ssid="StationMeteo"
    psk="meteo2026"
    priority=1
}
```

### 2.2 Configurer l'IP statique

```bash
sudo nano /etc/dhcpcd.conf
```

Ajouter a la fin du fichier:
```
interface wlan0
static ip_address=192.168.4.10/24
static routers=192.168.4.1
static domain_name_servers=192.168.4.1
```

### 2.3 Redemarrer le reseau

```bash
sudo systemctl restart dhcpcd
sudo systemctl restart wpa_supplicant
```

### 2.4 Verifier la connexion

```bash
# Verifier l'IP (doit etre 192.168.4.10)
hostname -I

# Tester la connexion a l'Access Point
ping 192.168.4.1
```

---

## Partie 3: Installation de l'application Flask

### 3.1 Cloner le projet

```bash
cd ~
git clone https://github.com/pj43svh/MA-Metier-Station-Meteo.git station-meteo
cd station-meteo
```

### 3.2 Installer Python et les dependances

```bash
# Installer Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Creer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dependances
pip install -r requirements.txt
pip install gunicorn
```

### 3.3 Demarrer le serveur

```bash
# Rendre le script executable
chmod +x scripts/start_local.sh

# Lancer le serveur
./scripts/start_local.sh
```

Le serveur demarre sur: **http://192.168.4.10:5000**

### 3.4 Demarrage automatique au boot (optionnel)

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

Activer le service:
```bash
sudo systemctl enable station-meteo
sudo systemctl start station-meteo

# Verifier le statut
sudo systemctl status station-meteo
```

---

## Partie 4: ESP32 Capteurs

### 4.1 Fichier a utiliser
```
code esp32/capteur_local/capteur_local.ino
```

### 4.2 Configuration par defaut

| Parametre | Valeur |
|-----------|--------|
| WiFi SSID | StationMeteo |
| WiFi Password | meteo2026 |
| IP Serveur | 192.168.4.10 |
| Port | 5000 |
| Nom capteur | ATOM_001 |

### 4.3 Flasher le premier capteur

1. Ouvrir `capteur_local.ino` dans Arduino IDE
2. Flasher l'ESP32
3. L'ESP32 se connecte automatiquement au WiFi "StationMeteo"
4. Il envoie les donnees au Raspberry Pi

### 4.4 Configurer via le portail web

Si le WiFi n'est pas configure ou si tu veux changer les parametres:

1. **Appuyer sur le bouton de l'ESP32 au demarrage**
2. L'ESP32 cree un WiFi temporaire: **"ConfigCapteur"** (password: `config123`)
3. Se connecter a ce WiFi
4. Ouvrir http://192.168.4.1
5. Remplir le formulaire:
   - SSID: `StationMeteo`
   - Password: `meteo2026`
   - IP Serveur: `192.168.4.10`
   - Port: `5000`
   - Nom: `ATOM_001` (ou ATOM_002, ATOM_003...)
6. Cliquer "Enregistrer"
7. L'ESP32 redemarre et se connecte

### 4.5 Reset d'un capteur

- **Appuyer 3 secondes** sur le bouton
- L'ESP32 efface sa configuration et redemarre en mode portail

### 4.6 Ajouter plusieurs capteurs

Repeter les etapes 4.3/4.4 pour chaque capteur avec un nom different:
- Premier capteur: `ATOM_001`
- Deuxieme capteur: `ATOM_002`
- Troisieme capteur: `ATOM_003`

---

## Partie 5: Utilisation

### 5.1 Acceder a l'interface web

Depuis n'importe quel appareil connecte au WiFi "StationMeteo":

1. Ouvrir un navigateur
2. Aller sur: **http://192.168.4.10:5000**

### 5.2 Pages disponibles

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | / | Donnees en temps reel |
| Historique | /history | Tableau des mesures |
| Statistiques | /statistical | Graphiques |
| Admin | /admin | Gestion des ESP32 |

### 5.3 Panneau Admin

Le panneau admin permet de:
- Voir tous les ESP32 connectes
- Configurer le nom des capteurs
- Supprimer un capteur

---

## Depannage

### Le WiFi "StationMeteo" n'apparait pas
- Verifier que l'ESP32 Access Point est alimente
- La LED doit clignoter
- Reflasher le code si necessaire

### Le Raspberry Pi ne se connecte pas au WiFi
- Verifier le SSID et mot de passe
- Verifier la configuration dans `/etc/wpa_supplicant/wpa_supplicant.conf`
- Redemarrer: `sudo reboot`

### Les capteurs n'envoient pas de donnees
- Verifier que le Raspberry Pi est connecte (IP 192.168.4.10)
- Verifier que Flask tourne: `curl http://192.168.4.10:5000`
- Verifier la configuration du capteur (IP serveur)

### L'interface web ne charge pas
- Verifier que Flask est demarre
- Tester: `curl http://192.168.4.10:5000`
- Regarder les logs: `journalctl -u station-meteo -f`

### Un capteur reste affiche apres suppression
- Supprimer via le panneau admin (/admin)
- Redemarrer Flask

---

## Resume des adresses IP

| Appareil | IP | Role |
|----------|-----|------|
| ESP32 Access Point | 192.168.4.1 | Cree le reseau WiFi |
| Raspberry Pi | 192.168.4.10 | Serveur Flask |
| ESP32 Capteurs | DHCP (192.168.4.x) | Envoient les donnees |
| Interface Web | http://192.168.4.10:5000 | Acces navigateur |

---

## Commandes utiles

```bash
# Voir l'IP du Raspberry Pi
hostname -I

# Tester la connexion a l'Access Point
ping 192.168.4.1

# Demarrer Flask manuellement
cd ~/station-meteo
source venv/bin/activate
./scripts/start_local.sh

# Voir les logs du service
sudo journalctl -u station-meteo -f

# Redemarrer le service
sudo systemctl restart station-meteo

# Voir le statut du service
sudo systemctl status station-meteo
```

---

## Schema de cablage ESP32 + Capteur ENV IV

```
ESP32 Atom Lite          Capteur ENV IV
+-------------+          +-------------+
|         3V3 |--------->| VCC         |
|         GND |--------->| GND         |
|      GPIO26 |--------->| SDA         |
|      GPIO32 |--------->| SCL         |
+-------------+          +-------------+
```

---

## Notes importantes

1. **Pas d'internet:** Ce systeme fonctionne sans connexion internet
2. **Portee WiFi:** L'ESP32 a une portee d'environ 10-20 metres en interieur
3. **Nombre de capteurs:** Maximum 8 appareils connectes simultanement
4. **Heure:** Le systeme utilise l'heure suisse (Europe/Zurich)
5. **Base de donnees:** SQLite stockee sur le Raspberry Pi

---

*Documentation creee pour le projet Station Meteo CPNV*
