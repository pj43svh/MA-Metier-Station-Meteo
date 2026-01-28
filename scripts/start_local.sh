#!/bin/bash
#
# Station Meteo - Script de demarrage local
#
# Ce script demarre le serveur Flask sur le Raspberry Pi
# pour fonctionner en mode 100% local avec l'ESP32 Access Point.
#
# Usage: ./start_local.sh
#

echo "========================================"
echo "   STATION METEO - SERVEUR LOCAL"
echo "========================================"
echo ""

# Verifier si on est dans le bon repertoire
if [ ! -f "app/main.py" ]; then
    echo "ERREUR: Lancez ce script depuis la racine du projet"
    echo "        cd /chemin/vers/MA-Metier-Station-Meteo-master"
    echo "        ./scripts/start_local.sh"
    exit 1
fi

# Verifier la connexion WiFi
echo "Verification de la connexion reseau..."
if ping -c 1 192.168.4.1 > /dev/null 2>&1; then
    echo "OK - Connecte au reseau StationMeteo"
else
    echo "ATTENTION: L'Access Point (192.168.4.1) n'est pas joignable"
    echo "           Verifiez que vous etes connecte au WiFi 'StationMeteo'"
fi

# Afficher l'IP actuelle
echo ""
echo "Adresses IP:"
ip -4 addr show | grep inet | grep -v 127.0.0.1 | awk '{print "  - " $2}'
echo ""

# Verifier si Python est installe
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python3 n'est pas installe"
    exit 1
fi

# Verifier si les dependances sont installees
echo "Verification des dependances..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installation des dependances..."
    pip3 install -r requirements.txt
fi

# Creer la base de donnees si elle n'existe pas
if [ ! -f "weather_data.db" ]; then
    echo "Creation de la base de donnees..."
    python3 -c "from app.database import create_tables; create_tables()"
fi

echo ""
echo "========================================"
echo "   DEMARRAGE DU SERVEUR"
echo "========================================"
echo ""
echo "Le serveur va demarrer sur:"
echo "  - http://0.0.0.0:5000"
echo "  - http://192.168.4.10:5000 (si IP configuree)"
echo ""
echo "Appuyez Ctrl+C pour arreter"
echo ""

# Demarrer le serveur
# Option 1: Mode developpement (plus de logs)
# python3 -m flask --app app.main run --host=0.0.0.0 --port=5000

# Option 2: Mode production avec Gunicorn (recommande)
if command -v gunicorn &> /dev/null; then
    gunicorn app.main:app --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile -
else
    echo "Gunicorn non installe, utilisation de Flask en mode dev"
    python3 -m flask --app app.main run --host=0.0.0.0 --port=5000
fi
