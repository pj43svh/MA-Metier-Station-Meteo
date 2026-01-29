/*
* Station Meteo - ESP32 Access Point + Configuration WiFi
*
* Cet ESP32 cree le reseau WiFi auquel se connectent:
* - Les ESP32 capteurs (envoient les donnees)
* - Le Raspberry Pi (heberge Flask)
* - Les telephones/PC (pour voir l'interface web)
*
* Configuration par defaut:
* - SSID: "StationMeteo"
* - Password: "meteo2026"
* - IP: 192.168.4.1
*
* Materiel: M5Stack Atom Lite (ou tout ESP32)
*
* Auteur: Station Meteo CPNV
* Date: Janvier 2026
*/

#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>  // Pour NVS

// ==================== CONFIGURATION RESEAU ====================
const char* AP_SSID = "StationMeteo";
const char* AP_PASSWORD = "meteo2026";

// Configuration IP statique pour AP
IPAddress local_IP(192, 168, 4, 1);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);

// ==================== CONFIGURATION HARDWARE ====================
#define LED_PIN 27        // LED sur Atom Lite (GPIO27)
#define BUTTON_PIN 39     // Bouton sur Atom Lite (GPIO39)

// ==================== OBJETS ====================
WebServer server(80);
Preferences preferences;

// ==================== VARIABLES ====================
unsigned long lastBlink = 0;
bool ledState = false;
int connectedDevices = 0;
bool isInConfigMode = false;

// Variables pour la configuration WiFi
String savedSSID = "";
String savedPassword = "";
String savedServerURL = "";

// ==================== PAGE WEB - CONFIGURATION ====================
const char HTML_CONFIG_PAGE[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration WiFi</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.8em;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .card h2 {
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .info-row:last-child { border-bottom: none; }
        .info-label { opacity: 0.8; }
        .info-value { font-weight: bold; }
        .status-ok { color: #4ade80; }
        .status-warning { color: #fbbf24; }
        .instructions {
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        .instructions ol {
            margin-left: 20px;
        }
        .instructions li {
            margin: 8px 0;
        }
        code {
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
        .refresh-btn {
            display: block;
            width: 100%;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 1em;
            cursor: pointer;
            margin-top: 20px;
        }
        .refresh-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        select, input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.1);
            color: white;
        }
        button {
            width: 100%;
            padding: 15px;
            background: #3b82f6;
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 1em;
            cursor: pointer;
            margin-top: 20px;
        }
        button:hover {
            background: #2563eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Configuration WiFi</h1>

        <div class="card">
            <h2>Choisir un réseau WiFi</h2>
            <form action="/save" method="POST">
                <label>SSID:</label>
                <select name="ssid" required>
                    <option value="">-- Sélectionner --</option>
                    %WIFI_LIST%
                </select>
                <label>Mot de passe:</label>
                <input type="password" name="password" placeholder="Mot de passe" required>
                <label>Adresse du serveur:</label>
                <input type="text" name="server" placeholder="http://192.168.4.10:5000/request/" required>
                <button type="submit">Enregistrer et redémarrer</button>
            </form>
        </div>

        <div class="card">
            <h2>Instructions</h2>
            <div class="instructions">
                <p>Une fois enregistré, l'ESP32 redémarrera et se connectera au réseau choisi.</p>
                <p>Assurez-vous que le serveur est accessible depuis le réseau.</p>
            </div>
        </div>
    </div>
</body>
</html>
)rawliteral";

// ==================== PAGE WEB - STATUT ====================
const char HTML_PAGE[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Station Meteo - Access Point</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.8em;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .card h2 {
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .info-row:last-child { border-bottom: none; }
        .info-label { opacity: 0.8; }
        .info-value { font-weight: bold; }
        .status-ok { color: #4ade80; }
        .status-warning { color: #fbbf24; }
        .instructions {
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        .instructions ol {
            margin-left: 20px;
        }
        .instructions li {
            margin: 8px 0;
        }
        code {
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
        .refresh-btn {
            display: block;
            width: 100%;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 1em;
            cursor: pointer;
            margin-top: 20px;
        }
        .refresh-btn:hover {
            background: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Station Meteo - Access Point</h1>

        <div class="card">
            <h2>Statut du reseau</h2>
            <div class="info-row">
                <span class="info-label">SSID</span>
                <span class="info-value">%SSID%</span>
            </div>
            <div class="info-row">
                <span class="info-label">IP Access Point</span>
                <span class="info-value">%IP%</span>
            </div>
            <div class="info-row">
                <span class="info-label">Appareils connectes</span>
                <span class="info-value status-ok">%DEVICES%</span>
            </div>
            <div class="info-row">
                <span class="info-label">Uptime</span>
                <span class="info-value">%UPTIME%</span>
            </div>
        </div>

        <div class="card">
            <h2>Configuration</h2>
            <div class="instructions">
                <p><strong>Pour acceder a l'interface web:</strong></p>
                <ol>
                    <li>Connecter le Raspberry Pi au WiFi <code>%SSID%</code></li>
                    <li>Configurer l'IP statique <code>192.168.4.10</code> sur le Pi</li>
                    <li>Lancer Flask: <code>./start_local.sh</code></li>
                    <li>Ouvrir <code>http://192.168.4.10:5000</code></li>
                </ol>
            </div>
        </div>

        <div class="card">
            <h2>ESP32 Capteurs</h2>
            <div class="instructions">
                <p>Les capteurs doivent etre configures pour:</p>
                <ol>
                    <li>Se connecter au WiFi <code>%SSID%</code></li>
                    <li>Envoyer vers <code>http://192.168.4.10:5000/request/</code></li>
                </ol>
            </div>
        </div>

        <button class="refresh-btn" onclick="location.reload()">Actualiser</button>
    </div>
</body>
</html>
)rawliteral";

// ==================== FONCTIONS ====================

String formatUptime() {
    unsigned long seconds = millis() / 1000;
    unsigned long minutes = seconds / 60;
    unsigned long hours = minutes / 60;

    seconds %= 60;
    minutes %= 60;

    String result = "";
    if (hours > 0) result += String(hours) + "h ";
    if (minutes > 0) result += String(minutes) + "m ";
    result += String(seconds) + "s";

    return result;
}

void handleRoot() {
    String html = String(HTML_PAGE);

    // Remplacer les placeholders
    html.replace("%SSID%", AP_SSID);
    html.replace("%IP%", WiFi.softAPIP().toString());
    html.replace("%DEVICES%", String(WiFi.softAPgetStationNum()));
    html.replace("%UPTIME%", formatUptime());

    server.send(200, "text/html", html);
}

void handleStatus() {
    String json = "{";
    json += "\"ssid\":\"" + String(AP_SSID) + "\",";
    json += "\"ip\":\"" + WiFi.softAPIP().toString() + "\",";
    json += "\"devices\":" + String(WiFi.softAPgetStationNum()) + ",";
    json += "\"uptime\":" + String(millis() / 1000);
    json += "}";

    server.send(200, "application/json", json);
}

void handleConfigRoot() {
    String html = String(HTML_CONFIG_PAGE);

    // Scan WiFi
    int n = WiFi.scanNetworks();
    String wifiList = "";
    for (int i = 0; i < n; ++i) {
        wifiList += "<option value=\"" + WiFi.SSID(i) + "\">" + WiFi.SSID(i) + " (RSSI: " + String(WiFi.RSSI(i)) + ")</option>";
    }

    html.replace("%WIFI_LIST%", wifiList);
    server.send(200, "text/html", html);
}

void handleSaveConfig() {
    if (server.hasArg("ssid") && server.hasArg("password") && server.hasArg("server")) {
        String ssid = server.arg("ssid");
        String password = server.arg("password");
        String serverURL = server.arg("server");

        preferences.begin("wifi_config", false);
        preferences.putString("ssid", ssid);
        preferences.putString("password", password);
        preferences.putString("server", serverURL);
        preferences.end();

        server.send(200, "text/html", "<h1>Configuration enregistrée ! Redémarrage en cours...</h1>");
        delay(2000);
        ESP.restart();
    } else {
        server.send(400, "text/html", "<h1>Erreur: paramètres manquants</h1>");
    }
}

void setLED(bool on) {
    digitalWrite(LED_PIN, on ? HIGH : LOW);
}

void blinkLED() {
    // Blink plus rapide si des appareils sont connectes
    int interval = (WiFi.softAPgetStationNum() > 0) ? 500 : 1000;

    if (millis() - lastBlink >= interval) {
        ledState = !ledState;
        setLED(ledState);
        lastBlink = millis();
    }
}

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);

    // Configuration des pins
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    setLED(true);

    Serial.println();
    Serial.println("========================================");
    Serial.println("   STATION METEO - ACCESS POINT");
    Serial.println("========================================");
    Serial.println();

    // Lire les paramètres sauvegardés
    preferences.begin("wifi_config", true);
    savedSSID = preferences.getString("ssid", "");
    savedPassword = preferences.getString("password", "");
    savedServerURL = preferences.getString("server", "");
    preferences.end();

    // Vérifier si bouton maintenu 3s pour activer mode config
    unsigned long buttonPressStart = 0;
    bool buttonPressed = false;

    // Attendre 1s pour laisser le temps d'appuyer
    delay(1000);

    if (digitalRead(BUTTON_PIN) == LOW) {
        buttonPressStart = millis();
        buttonPressed = true;
        Serial.println("Bouton appuyé - attente 3s pour mode config...");
    }

    while (buttonPressed && (millis() - buttonPressStart < 3000)) {
        if (digitalRead(BUTTON_PIN) == HIGH) {
            buttonPressed = false;
            break;
        }
        delay(10);
    }

    if (buttonPressed && (millis() - buttonPressStart >= 3000)) {
        isInConfigMode = true;
        Serial.println("Mode configuration activé !");
    }

    if (isInConfigMode) {
        // Démarrer en mode AP de configuration
        Serial.println("Configuration du réseau WiFi de configuration...");

        WiFi.mode(WIFI_AP);
        WiFi.softAPConfig(local_IP, gateway, subnet);

        if (WiFi.softAP("CAPTEUR_METEO", "meteo2026", 1, false, 8)) {
            Serial.println("Access Point de configuration démarré avec succès!");
            Serial.println();
            Serial.println("Configuration:");
            Serial.println("- SSID: CAPTEUR_METEO");
            Serial.println("- Password: meteo2026");
            Serial.println("- IP: " + WiFi.softAPIP().toString());
            Serial.println("- Max connexions: 8");
        } else {
            Serial.println("ERREUR: Impossible de démarrer l'Access Point de configuration!");
            while (true) {
                setLED(true);
                delay(100);
                setLED(false);
                delay(100);
            }
        }

        // Configuration du serveur web de config
        server.on("/", HTTP_GET, handleConfigRoot);
        server.on("/save", HTTP_POST, handleSaveConfig);
        server.begin();

        Serial.println();
        Serial.println("Serveur web de configuration démarré sur http://" + WiFi.softAPIP().toString() + "/");
        Serial.println();
        Serial.println("========================================");
        Serial.println("   EN ATTENTE DE CONFIGURATION...");
        Serial.println("========================================");
        Serial.println();

    } else {
        // Mode normal : démarrer en AP
        Serial.println("Configuration du réseau WiFi...");

        WiFi.mode(WIFI_AP);
        WiFi.softAPConfig(local_IP, gateway, subnet);

        if (WiFi.softAP(AP_SSID, AP_PASSWORD, 1, false, 8)) {
            Serial.println("Access Point démarré avec succès!");
            Serial.println();
            Serial.println("Configuration:");
            Serial.println("- SSID: " + String(AP_SSID));
            Serial.println("- Password: " + String(AP_PASSWORD));
            Serial.println("- IP: " + WiFi.softAPIP().toString());
            Serial.println("- Max connexions: 8");
        } else {
            Serial.println("ERREUR: Impossible de démarrer l'Access Point!");
            while (true) {
                setLED(true);
                delay(100);
                setLED(false);
                delay(100);
            }
        }

        // Configuration du serveur web
        server.on("/", HTTP_GET, handleRoot);
        server.on("/status", HTTP_GET, handleStatus);
        server.begin();

        Serial.println();
        Serial.println("Serveur web démarré sur http://" + WiFi.softAPIP().toString() + "/");
        Serial.println();
        Serial.println("========================================");
        Serial.println("   EN ATTENTE DE CONNEXIONS...");
        Serial.println("========================================");
        Serial.println();
    }
}

// ==================== LOOP ====================
void loop() {
    if (isInConfigMode) {
        server.handleClient();
        blinkLED();
        delay(10);
    } else {
        server.handleClient();
        blinkLED();

        // Afficher les connexions/deconnexions
        int currentDevices = WiFi.softAPgetStationNum();
        if (currentDevices != connectedDevices) {
            Serial.print("Appareils connectes: ");
            Serial.println(currentDevices);
            connectedDevices = currentDevices;
        }

        delay(10);
    }
}
