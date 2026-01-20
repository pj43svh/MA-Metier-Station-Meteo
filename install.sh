#!/bin/bash
# ===========================================
# Installation automatique - Station Météo
# Compatible Raspberry Pi OS (Linux)
# ===========================================

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   🌤️  STATION MÉTÉO - Installation automatique            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}[INFO]${NC} Dossier d'installation : $SCRIPT_DIR"
echo ""

# ============ ÉTAPE 1 : Conversion des fichiers Windows -> Linux ============
echo -e "${BLUE}[1/6]${NC} Conversion des fichiers pour Linux..."

# Installer dos2unix si nécessaire
if ! command -v dos2unix &> /dev/null; then
    sudo apt-get install -y dos2unix > /dev/null 2>&1 || true
fi

# Convertir tous les fichiers texte
if command -v dos2unix &> /dev/null; then
    find . -name "*.py" -exec dos2unix {} \; 2>/dev/null || true
    find . -name "*.sh" -exec dos2unix {} \; 2>/dev/null || true
    find . -name "*.html" -exec dos2unix {} \; 2>/dev/null || true
    find . -name "*.css" -exec dos2unix {} \; 2>/dev/null || true
    find . -name "*.js" -exec dos2unix {} \; 2>/dev/null || true
    find . -name "*.txt" -exec dos2unix {} \; 2>/dev/null || true
    find . -name "*.md" -exec dos2unix {} \; 2>/dev/null || true
fi
echo -e "${GREEN}[OK]${NC} Fichiers convertis"

# ============ ÉTAPE 2 : Mise à jour du système ============
echo ""
echo -e "${BLUE}[2/6]${NC} Mise à jour du système..."
sudo apt-get update -y > /dev/null 2>&1
echo -e "${GREEN}[OK]${NC} Système mis à jour"

# ============ ÉTAPE 3 : Installation de Python ============
echo ""
echo -e "${BLUE}[3/6]${NC} Installation de Python et dépendances système..."
sudo apt-get install -y python3 python3-pip python3-venv python3-full > /dev/null 2>&1
echo -e "${GREEN}[OK]${NC} Python installé"

# ============ ÉTAPE 4 : Environnement virtuel ============
echo ""
echo -e "${BLUE}[4/6]${NC} Création de l'environnement virtuel Python..."

# Supprimer l'ancien venv s'il existe (venv Windows ne marche pas sur Linux)
if [ -d "venv" ]; then
    rm -rf venv
fi
if [ -d ".venv" ]; then
    rm -rf .venv
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}[OK]${NC} Environnement virtuel créé"

# ============ ÉTAPE 5 : Installation des packages Python ============
echo ""
echo -e "${BLUE}[5/6]${NC} Installation des packages Python (Flask, etc.)..."
pip install flask flask-sqlalchemy flask-cors python-dotenv > /dev/null 2>&1
echo -e "${GREEN}[OK]${NC} Packages Python installés"

# ============ ÉTAPE 6 : Service systemd ============
echo ""
echo -e "${BLUE}[6/6]${NC} Configuration du démarrage automatique..."

SERVICE_FILE="/etc/systemd/system/station-meteo.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Station Météo - Serveur Flask
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
ExecStart=$SCRIPT_DIR/venv/bin/python3 run.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable station-meteo.service > /dev/null 2>&1
echo -e "${GREEN}[OK]${NC} Service configuré"

# ============ TERMINÉ ============
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   ✅  INSTALLATION TERMINÉE AVEC SUCCÈS !                  ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Récupérer l'IP
IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${GREEN}Adresse IP du Raspberry Pi :${NC} $IP"
echo ""
echo -e "  ${GREEN}Interface web :${NC} http://$IP:5000"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Pour démarrer maintenant :  ${BLUE}./start.sh${NC}"
echo ""
echo -e "  Ou redémarre le Raspberry Pi, le serveur démarrera"
echo -e "  automatiquement au boot."
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
