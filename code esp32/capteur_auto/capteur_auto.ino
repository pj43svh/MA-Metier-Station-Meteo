/*
 * Station Meteo - Capteur Auto-Configure avec WiFi Manager
 *
 * Fonctionnement:
 * 1. Au premier demarrage, l'ESP32 cree un point d'acces WiFi "StationMeteo-XXXX"
 * 2. Se connecter a ce reseau, un portail web s'ouvre
 * 3. Configurer: reseau WiFi + adresse IP du serveur (Raspberry Pi ou Railway)
 * 4. L'ESP32 redemarre et se connecte automatiquement
 * 5. Appui 3 sec sur le bouton = reset config (reouvre le portail)
 *
 * Auteur: Amin Torrisi / Equipe CPNV
 * Date: Janvier 2026
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <Wire.h>
#include <Adafruit_SHT4x.h>
#include <Adafruit_BMP280.h>
#include <ArduinoJson.h>

// ==================== CONFIGURATION ====================
#define SEND_INTERVAL 20000              // Intervalle d'envoi (20 sec)
#define CONFIG_CHECK_INTERVAL 60000      // Verification config (60 sec)
#define DNS_PORT 53

// ==================== PINS (Atom Lite) ====================
#define BUTTON_PIN 39                    // Bouton
#define LED_PIN 27                       // LED
#define SDA_PIN 26                       // I2C Data
#define SCL_PIN 32                       // I2C Clock

// ==================== OBJETS ====================
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_BMP280 bmp;
Preferences preferences;
WebServer server(80);
DNSServer dnsServer;

// ==================== VARIABLES ====================
unsigned long lastSendTime = 0;
unsigned long lastConfigCheck = 0;
unsigned long buttonPressStart = 0;
bool buttonPressed = false;
bool portalActive = false;

String macAddress;
int sensorNumber = 0;           // 0 = pas encore configure
String capteurID = "";

// Config sauvegardee
String savedSSID = "";
String savedPassword = "";
String savedServerIP = "";
bool isConfigured = false;

// ==================== PROTOTYPES ====================
void setLED(bool on);
void sendData(float temp, float hum, float press);
bool initSensors();
void checkButton();
bool registerWithServer();
bool getConfigFromServer();
void startPortal();
void handleRoot();
void handleSave();
void handleScan();
String getServerURL();
bool isLocalServer();
String buildPortalHTML();

// ==================== PAGE HTML DU PORTAIL ====================
String buildPortalHTML() {
    // Scanner les reseaux WiFi
    int n = WiFi.scanNetworks();

    String options = "";
    for (int i = 0; i < n; i++) {
        String ssid = WiFi.SSID(i);
        int rssi = WiFi.RSSI(i);
        String signal = "";
        if (rssi > -50) signal = "Excellent";
        else if (rssi > -60) signal = "Bon";
        else if (rssi > -70) signal = "Moyen";
        else signal = "Faible";

        options += "<option value=\"" + ssid + "\">" + ssid + " (" + signal + ")</option>";
    }

    String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Station Meteo</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: #16213e;
            padding: 30px;
            border-radius: 15px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        h1 {
            text-align: center;
            margin-bottom: 5px;
            font-size: 22px;
            color: #e94560;
        }
        .subtitle {
            text-align: center;
            color: #888;
            font-size: 13px;
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #ccc;
            font-size: 14px;
        }
        select, input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #333;
            border-radius: 8px;
            background: #0f3460;
            color: #fff;
            font-size: 14px;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #e94560;
        }
        .hint {
            font-size: 12px;
            color: #666;
            margin-top: -10px;
            margin-bottom: 15px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover { background: #c73652; }
        .mac {
            text-align: center;
            font-size: 11px;
            color: #555;
            margin-top: 15px;
        }
        .refresh {
            text-align: center;
            margin-bottom: 15px;
        }
        .refresh a {
            color: #e94560;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Station Meteo</h1>
        <p class="subtitle">Configuration du capteur</p>

        <div class="refresh">
            <a href="/scan">Rescanner les reseaux</a>
        </div>

        <form action="/save" method="POST">
            <label>Reseau WiFi</label>
            <select name="ssid">
                <option value="">-- Choisir un reseau --</option>
                )rawliteral";

    html += options;

    html += R"rawliteral(
            </select>

            <label>Mot de passe WiFi</label>
            <input type="password" name="password" placeholder="Mot de passe du reseau">

            <label>Adresse du serveur</label>
            <input type="text" name="server" placeholder="192.168.1.100 ou URL Railway">
            <p class="hint">IP du Raspberry Pi ou URL complète du serveur Railway</p>

            <button type="submit">Sauvegarder et connecter</button>
        </form>

        <p class="mac">MAC: )rawliteral";

    html += macAddress;
    html += "</p></div></body></html>";

    return html;
}

// ==================== PORTAIL CAPTIF ====================

void handleRoot() {
    server.send(200, "text/html", buildPortalHTML());
}

void handleScan() {
    server.send(200, "text/html", buildPortalHTML());
}

void handleSave() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");
    String serverIP = server.arg("server");

    if (ssid.length() == 0) {
        server.send(200, "text/html",
            "<html><body style='background:#1a1a2e;color:#fff;text-align:center;padding:50px;font-family:Arial'>"
            "<h2>Erreur</h2><p>Veuillez selectionner un reseau WiFi</p>"
            "<a href='/' style='color:#e94560'>Retour</a></body></html>");
        return;
    }

    if (serverIP.length() == 0) {
        server.send(200, "text/html",
            "<html><body style='background:#1a1a2e;color:#fff;text-align:center;padding:50px;font-family:Arial'>"
            "<h2>Erreur</h2><p>Veuillez entrer l'adresse du serveur</p>"
            "<a href='/' style='color:#e94560'>Retour</a></body></html>");
        return;
    }

    // Sauvegarder dans Preferences (NVS)
    preferences.begin("meteo", false);
    preferences.putString("wifi_ssid", ssid);
    preferences.putString("wifi_pass", password);
    preferences.putString("server_ip", serverIP);
    preferences.putBool("configured", true);
    preferences.end();

    Serial.println("Configuration sauvegardee!");
    Serial.println("SSID: " + ssid);
    Serial.println("Serveur: " + serverIP);

    server.send(200, "text/html",
        "<html><body style='background:#1a1a2e;color:#fff;text-align:center;padding:50px;font-family:Arial'>"
        "<h2 style='color:#4CAF50'>Configuration sauvegardee!</h2>"
        "<p>Connexion a <b>" + ssid + "</b>...</p>"
        "<p>Serveur: <b>" + serverIP + "</b></p>"
        "<p style='color:#888;margin-top:20px'>Redemarrage en cours...</p>"
        "</body></html>");

    delay(2000);
    ESP.restart();
}

void startPortal() {
    portalActive = true;

    // Recuperer MAC pour le nom du reseau
    WiFi.mode(WIFI_AP_STA);
    macAddress = WiFi.macAddress();
    String apName = "StationMeteo-" + macAddress.substring(12);
    apName.replace(":", "");

    Serial.println("\n========================================");
    Serial.println("   MODE CONFIGURATION");
    Serial.println("   Reseau: " + apName);
    Serial.println("   IP: 192.168.4.1");
    Serial.println("========================================\n");

    // Demarrer le point d'acces
    WiFi.softAP(apName.c_str());
    delay(500);

    // DNS captif: redirige tout vers 192.168.4.1
    dnsServer.start(DNS_PORT, "*", WiFi.softAPIP());

    // Routes du serveur web
    server.on("/", handleRoot);
    server.on("/scan", handleScan);
    server.on("/save", HTTP_POST, handleSave);
    // Captive portal: rediriger toutes les requetes inconnues
    server.onNotFound(handleRoot);

    server.begin();
    Serial.println("Portail captif demarre!");
    Serial.println("Connectez-vous au reseau '" + apName + "'");
    Serial.println("Puis ouvrez http://192.168.4.1\n");

    // LED clignote en mode portail
    while (portalActive) {
        dnsServer.processNextRequest();
        server.handleClient();

        // Clignotement LED
        static unsigned long lastBlink = 0;
        if (millis() - lastBlink > 500) {
            lastBlink = millis();
            static bool ledState = false;
            ledState = !ledState;
            setLED(ledState);
        }

        // Verifier bouton pour forcer restart
        if (digitalRead(BUTTON_PIN) == LOW) {
            delay(3000);
            if (digitalRead(BUTTON_PIN) == LOW) {
                ESP.restart();
            }
        }

        delay(10);
    }
}

// ==================== HELPERS SERVEUR ====================

bool isLocalServer() {
    // Si l'adresse ne contient que des chiffres et des points = IP locale
    for (unsigned int i = 0; i < savedServerIP.length(); i++) {
        char c = savedServerIP.charAt(i);
        if (c != '.' && c != ':' && (c < '0' || c > '9')) {
            return false;  // Contient des lettres = URL
        }
    }
    return true;
}

String getServerURL() {
    if (isLocalServer()) {
        // Raspberry Pi local: HTTP
        String url = "http://" + savedServerIP;
        if (savedServerIP.indexOf(':') == -1) {
            url += ":5000";  // Port par defaut Flask
        }
        return url;
    } else {
        // Railway ou autre: HTTPS
        String url = savedServerIP;
        if (!url.startsWith("http")) {
            url = "https://" + url;
        }
        return url;
    }
}

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);

    // Configuration des pins
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    setLED(true);  // LED on = demarrage

    // Initialisation I2C
    Wire.begin(SDA_PIN, SCL_PIN);

    // Initialisation des capteurs
    if (!initSensors()) {
        Serial.println("ERREUR: Capteurs non detectes!");
    }

    // Charger la configuration sauvegardee
    preferences.begin("meteo", true);  // true = lecture seule
    isConfigured = preferences.getBool("configured", false);
    savedSSID = preferences.getString("wifi_ssid", "");
    savedPassword = preferences.getString("wifi_pass", "");
    savedServerIP = preferences.getString("server_ip", "");
    preferences.end();

    if (!isConfigured || savedSSID.length() == 0) {
        // Pas de config: lancer le portail captif
        Serial.println("Aucune configuration trouvee.");
        startPortal();
        return;  // Ne sort jamais de startPortal (boucle interne)
    }

    // Config trouvee: connexion WiFi
    Serial.println("\nConnexion WiFi...");
    Serial.print("SSID: ");
    Serial.println(savedSSID);

    WiFi.mode(WIFI_STA);
    WiFi.begin(savedSSID.c_str(), savedPassword.c_str());

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("WiFi connecte!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());

        macAddress = WiFi.macAddress();

        String serverURL = getServerURL();
        Serial.println("\n========================================");
        Serial.println("   Station Meteo - Auto-Configure");
        Serial.println("   MAC: " + macAddress);
        Serial.println("   Serveur: " + serverURL);
        Serial.println("========================================\n");

        setLED(false);

        // S'enregistrer sur le serveur et recuperer la config
        registerWithServer();
        getConfigFromServer();
    } else {
        Serial.println("Echec connexion WiFi!");
        Serial.println("Lancement du portail de configuration...");
        // Reset config et relancer le portail
        preferences.begin("meteo", false);
        preferences.putBool("configured", false);
        preferences.end();
        startPortal();
        return;
    }

    Serial.println("\n--- Pret! ---");
    if (sensorNumber > 0) {
        Serial.println("Capteur configure: " + capteurID);
    } else {
        Serial.println("En attente de configuration via l'interface admin...");
        Serial.println("Allez sur: " + getServerURL() + "/admin");
    }
    Serial.println();
}

// ==================== LOOP ====================
void loop() {
    checkButton();

    // Verifier la config periodiquement si pas encore configure
    if (sensorNumber == 0 && millis() - lastConfigCheck >= CONFIG_CHECK_INTERVAL) {
        lastConfigCheck = millis();
        Serial.println("Verification de la configuration...");
        getConfigFromServer();
    }

    // Envoyer les donnees si configure
    if (sensorNumber > 0 && millis() - lastSendTime >= SEND_INTERVAL) {
        lastSendTime = millis();

        // Lecture des capteurs
        sensors_event_t humidity, temp;
        sht4.getEvent(&humidity, &temp);
        float temperature = temp.temperature;
        float humidite = humidity.relative_humidity;
        float pression = bmp.readPressure() / 100.0F;

        // Affichage
        Serial.println("--- Mesures (" + capteurID + ") ---");
        Serial.printf("Temperature: %.2f C\n", temperature);
        Serial.printf("Humidite: %.2f %%\n", humidite);
        Serial.printf("Pression: %.2f hPa\n", pression);

        // Envoi des donnees
        if (WiFi.status() == WL_CONNECTED) {
            sendData(temperature, humidite, pression);
            setLED(true);
            delay(100);
            setLED(false);
        } else {
            Serial.println("WiFi deconnecte! Reconnexion...");
            WiFi.reconnect();
        }
    }

    delay(100);
}

// ==================== FONCTIONS ====================

bool initSensors() {
    bool success = true;

    if (!sht4.begin()) {
        Serial.println("SHT40 non trouve!");
        success = false;
    } else {
        Serial.println("SHT40 OK");
        sht4.setPrecision(SHT4X_HIGH_PRECISION);
        sht4.setHeater(SHT4X_NO_HEATER);
    }

    if (!bmp.begin(0x76)) {
        if (!bmp.begin(0x77)) {
            Serial.println("BMP280 non trouve!");
            success = false;
        }
    }
    if (bmp.begin(0x76) || bmp.begin(0x77)) {
        Serial.println("BMP280 OK");
        bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                        Adafruit_BMP280::SAMPLING_X2,
                        Adafruit_BMP280::SAMPLING_X16,
                        Adafruit_BMP280::FILTER_X16,
                        Adafruit_BMP280::STANDBY_MS_500);
    }

    return success;
}

bool registerWithServer() {
    String serverURL = getServerURL();
    String url = serverURL + "/api/esp32/register";

    HTTPClient http;
    http.setTimeout(30000);

    if (isLocalServer()) {
        // HTTP local
        WiFiClient client;
        if (!http.begin(client, url)) {
            Serial.println("Erreur connexion serveur");
            return false;
        }
    } else {
        // HTTPS distant
        WiFiClientSecure client;
        client.setInsecure();
        client.setTimeout(30000);
        if (!http.begin(client, url)) {
            Serial.println("Erreur connexion serveur");
            return false;
        }
    }

    http.addHeader("Content-Type", "application/json");

    String json = "{\"mac_address\":\"" + macAddress + "\",\"ip_address\":\"" + WiFi.localIP().toString() + "\"}";

    Serial.println("Enregistrement sur le serveur...");
    int httpCode = http.POST(json);

    if (httpCode > 0) {
        String response = http.getString();
        Serial.println("Reponse: " + response);

        StaticJsonDocument<256> doc;
        if (deserializeJson(doc, response) == DeserializationError::Ok) {
            const char* status = doc["status"];
            if (strcmp(status, "configured") == 0) {
                sensorNumber = doc["sensor_number"];
                capteurID = String(doc["capteur_id"] | "");
                Serial.println("Deja configure comme: " + capteurID);
                http.end();
                return true;
            } else {
                Serial.println("En attente de configuration...");
            }
        }
    } else {
        Serial.printf("Erreur HTTP: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
    return false;
}

bool getConfigFromServer() {
    String serverURL = getServerURL();
    String url = serverURL + "/api/esp32/config/" + macAddress;

    HTTPClient http;
    http.setTimeout(30000);

    if (isLocalServer()) {
        WiFiClient client;
        if (!http.begin(client, url)) return false;
    } else {
        WiFiClientSecure client;
        client.setInsecure();
        client.setTimeout(30000);
        if (!http.begin(client, url)) return false;
    }

    int httpCode = http.GET();

    if (httpCode > 0) {
        String response = http.getString();

        StaticJsonDocument<256> doc;
        if (deserializeJson(doc, response) == DeserializationError::Ok) {
            const char* status = doc["status"];
            if (strcmp(status, "configured") == 0) {
                int newSensorNumber = doc["sensor_number"];
                if (newSensorNumber != sensorNumber) {
                    sensorNumber = newSensorNumber;
                    capteurID = String(doc["capteur_id"] | "");
                    Serial.println("*** Configuration recue! ***");
                    Serial.println("Capteur ID: " + capteurID);
                    http.end();
                    return true;
                }
            }
        }
    }

    http.end();
    return false;
}

void sendData(float temp, float hum, float press) {
    String serverURL = getServerURL();
    String url = serverURL + "/request/";

    HTTPClient http;
    http.setTimeout(30000);
    http.setConnectTimeout(30000);

    if (isLocalServer()) {
        WiFiClient client;
        if (!http.begin(client, url)) {
            Serial.println("Erreur connexion");
            return;
        }
    } else {
        WiFiClientSecure client;
        client.setInsecure();
        client.setTimeout(30000);
        client.setHandshakeTimeout(30);
        if (!http.begin(client, url)) {
            Serial.println("Erreur connexion");
            return;
        }
    }

    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"capteur_id\":\"" + capteurID + "\",";
    json += "\"mac_address\":\"" + macAddress + "\",";
    json += "\"temperature\":" + String(temp, 2) + ",";
    json += "\"humidite\":" + String(hum, 2) + ",";
    json += "\"pression\":" + String(press, 2);
    json += "}";

    int httpCode = http.POST(json);

    if (httpCode > 0) {
        Serial.printf("Envoi OK (%d)\n", httpCode);
    } else {
        Serial.printf("Erreur: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
}

void checkButton() {
    if (digitalRead(BUTTON_PIN) == LOW) {
        if (!buttonPressed) {
            buttonPressed = true;
            buttonPressStart = millis();
            setLED(true);
        } else if (millis() - buttonPressStart >= 3000) {
            Serial.println("\n*** RESET CONFIGURATION ***");
            Serial.println("Effacement de la config...");

            // Effacer la configuration
            preferences.begin("meteo", false);
            preferences.clear();
            preferences.end();

            Serial.println("Redemarrage en mode configuration...\n");
            delay(1000);
            ESP.restart();
        }
    } else {
        if (buttonPressed && millis() - buttonPressStart < 3000) {
            setLED(false);
        }
        buttonPressed = false;
    }
}

void setLED(bool on) {
    digitalWrite(LED_PIN, on ? HIGH : LOW);
}
