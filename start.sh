#!/bin/bash
# ===========================================
# Démarrage - Station Météo
# ===========================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Récupérer l'IP
IP=$(hostname -I | awk '{print $1}')

clear
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   🌤️  STATION MÉTÉO - Serveur                             ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "  ${GREEN}Adresse IP :${NC} $IP"
echo -e "  ${GREEN}Interface  :${NC} http://$IP:5000"
echo ""
echo -e "${YELLOW}  Appuie sur Ctrl+C pour arrêter${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Activer l'environnement virtuel et lancer
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 run.py
