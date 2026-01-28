/*
 * Station Meteo - Capteur Local
 *
 * ESP32 capteur qui se connecte au reseau WiFi de l'Access Point
 * et envoie les donnees vers le Raspberry Pi local.
 *
 * Fonctionnalites:
 * - Mode portail de configuration si WiFi non configure
 * - Envoi des donnees toutes les 20 secondes
 * - LED status
 * - Bouton reset (appui 3 sec)
 *
 * Materiel:
 * - M5Stack Atom Lite (ESP32)
 * - Capteur ENV IV (SHT40 + BMP280)
 *
 * Auteur: Station Meteo CPNV
 * Date: Janvier 2026
 */

#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "Adafruit_SHT4x.h"
#include <Adafruit_BMP280.h>

// ==================== CONFIGURATION PAR DEFAUT ====================
// Ces valeurs sont utilisees si aucune config n'est sauvegardee
#define DEFAULT_WIFI_SSID "StationMeteo"
#define DEFAULT_WIFI_PASS "meteo2026"
#define DEFAULT_SERVER_IP "192.168.4.10"
#define DEFAULT_SERVER_PORT 5000
#define DEFAULT_DEVICE_NAME "ATOM_001"

// ==================== CONFIGURATION PORTAIL ====================
const char* AP_SSID = "ConfigCapteur";
const char* AP_PASS = "config123";

// ==================== CONFIGURATION HARDWARE ====================
#define LED_PIN 27
#define BUTTON_PIN 39
#define SDA_PIN 26
#define SCL_PIN 32

// ==================== INTERVALLE ====================
const unsigned long SEND_INTERVAL = 20000; // 20 secondes

// ==================== OBJETS ====================
WebServer server(80);
Preferences prefs;
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_BMP280 bmp;

// ==================== VARIABLES CONFIG ====================
String wifiSsid = "";
String wifiPass = "";
String serverIP = "";
int serverPort = 5000;
String deviceName = "";

// ==================== VARIABLES ====================
bool configMode = false;
bool sht40_ok = false;
bool bmp280_ok = false;
unsigned long lastSend = 0;
unsigned long buttonPressStart = 0;
bool buttonPressed = false;

// ==================== HTML PORTAIL ====================
const char HTML_FORM[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Capteur</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"],
        input[type="password"],
        input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            opacity: 0.9;
        }
        .info {
            background: #f0f0f0;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
        .section-title {
            font-size: 14px;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 15px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Configuration Capteur</h1>
        <form method="POST" action="/save">
            <div class="section-title">Reseau WiFi</div>
            <div class="form-group">
                <label>SSID du reseau</label>
                <input type="text" name="ssid" value="StationMeteo" required>
            </div>
            <div class="form-group">
                <label>Mot de passe</label>
                <input type="password" name="pass" value="meteo2026">
            </div>

            <div class="section-title">Serveur</div>
            <div class="form-group">
                <label>IP du Raspberry Pi</label>
                <input type="text" name="server_ip" value="192.168.4.10" required>
            </div>
            <div class="form-group">
                <label>Port</label>
                <input type="number" name="server_port" value="5000" required>
            </div>

            <div class="section-title">Capteur</div>
            <div class="form-group">
                <label>Nom du capteur (ex: ATOM_001)</label>
                <input type="text" name="name" value="ATOM_001" required>
            </div>

            <button type="submit">Enregistrer et redemarrer</button>
        </form>

        <div class="info">
            Apres enregistrement, le capteur redemarrera et se connectera
            automatiquement au reseau WiFi configure.
        </div>
    </div>
</body>
</html>
)rawliteral";

// ==================== FONCTIONS CONFIG ====================

void loadConfig() {
    prefs.begin("capteur", true);
    wifiSsid = prefs.getString("ssid", DEFAULT_WIFI_SSID);
    wifiPass = prefs.getString("pass", DEFAULT_WIFI_PASS);
    serverIP = prefs.getString("server_ip", DEFAULT_SERVER_IP);
    serverPort = prefs.getInt("server_port", DEFAULT_SERVER_PORT);
    deviceName = prefs.getString("name", DEFAULT_DEVICE_NAME);
    prefs.end();
}

void saveConfig() {
    prefs.begin("capteur", false);
    prefs.putString("ssid", wifiSsid);
    prefs.putString("pass", wifiPass);
    prefs.putString("server_ip", serverIP);
    prefs.putInt("server_port", serverPort);
    prefs.putString("name", deviceName);
    prefs.end();
}

void resetConfig() {
    prefs.begin("capteur", false);
    prefs.clear();
    prefs.end();
}

// ==================== HANDLERS WEB ====================

void handleRoot() {
    server.send(200, "text/html", HTML_FORM);
}

void handleSave() {
    wifiSsid = server.arg("ssid");
    wifiPass = server.arg("pass");
    serverIP = server.arg("server_ip");
    serverPort = server.arg("server_port").toInt();
    deviceName = server.arg("name");

    if (wifiSsid.length() == 0 || serverIP.length() == 0) {
        server.send(400, "text/plain", "SSID et IP serveur requis!");
        return;
    }

    saveConfig();

    String response = "Configuration sauvegardee!\n\n";
    response += "WiFi: " + wifiSsid + "\n";
    response += "Serveur: " + serverIP + ":" + String(serverPort) + "\n";
    response += "Capteur: " + deviceName + "\n\n";
    response += "Redemarrage dans 2 secondes...";

    server.send(200, "text/plain", response);
    delay(2000);
    ESP.restart();
}

void startConfigPortal() {
    Serial.println();
    Serial.println("========================================");
    Serial.println("   MODE CONFIGURATION");
    Serial.println("========================================");

    configMode = true;

    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);

    Serial.println();
    Serial.println("Portail de configuration actif:");
    Serial.println("- WiFi: " + String(AP_SSID));
    Serial.println("- Password: " + String(AP_PASS));
    Serial.println("- URL: http://" + WiFi.softAPIP().toString() + "/");
    Serial.println();

    server.on("/", HTTP_GET, handleRoot);
    server.on("/save", HTTP_POST, handleSave);
    server.begin();
}

// ==================== FONCTIONS WIFI ====================

bool connectWiFi() {
    Serial.print("Connexion WiFi vers " + wifiSsid);

    WiFi.mode(WIFI_STA);
    WiFi.begin(wifiSsid.c_str(), wifiPass.c_str());

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Connecte! IP: " + WiFi.localIP().toString());
        return true;
    } else {
        Serial.println("Echec de connexion!");
        return false;
    }
}

// ==================== FONCTIONS CAPTEURS ====================

bool initSensors() {
    Wire.begin(SDA_PIN, SCL_PIN);

    Serial.print("Initialisation SHT40... ");
    if (sht4.begin()) {
        Serial.println("OK");
        sht4.setPrecision(SHT4X_HIGH_PRECISION);
        sht40_ok = true;
    } else {
        Serial.println("ERREUR!");
        sht40_ok = false;
    }

    Serial.print("Initialisation BMP280... ");
    if (bmp.begin(0x76) || bmp.begin(0x77)) {
        Serial.println("OK");
        bmp280_ok = true;
    } else {
        Serial.println("ERREUR!");
        bmp280_ok = false;
    }

    return sht40_ok || bmp280_ok;
}

// ==================== ENVOI DONNEES ====================

void sendData(float temperature, float humidite, float pression) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi deconnecte, impossible d'envoyer");
        return;
    }

    HTTPClient http;
    String url = "http://" + serverIP + ":" + String(serverPort) + "/request/";

    String json = "{";
    json += "\"capteur_id\":\"" + deviceName + "\",";
    json += "\"temperature\":" + String(temperature, 2) + ",";
    json += "\"humidite\":" + String(humidite, 2) + ",";
    json += "\"pression\":" + String(pression, 2);
    json += "}";

    Serial.print("Envoi vers " + url + "... ");

    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(10000);

    int httpCode = http.POST(json);

    if (httpCode > 0) {
        Serial.print(httpCode);
        if (httpCode == 201 || httpCode == 200) {
            Serial.println(" OK");
        } else {
            Serial.println(" (reponse inattendue)");
        }
    } else {
        Serial.print("Erreur: ");
        Serial.println(http.errorToString(httpCode));
    }

    http.end();
}

// ==================== FONCTIONS UTILITAIRES ====================

void setLED(bool on) {
    digitalWrite(LED_PIN, on ? HIGH : LOW);
}

void checkButton() {
    if (digitalRead(BUTTON_PIN) == LOW) {
        if (!buttonPressed) {
            buttonPressed = true;
            buttonPressStart = millis();
            setLED(true);
        } else if (millis() - buttonPressStart >= 3000) {
            Serial.println("\n*** RESET CONFIG ***\n");
            resetConfig();
            delay(500);
            ESP.restart();
        }
    } else {
        if (buttonPressed && millis() - buttonPressStart < 3000) {
            setLED(false);
        }
        buttonPressed = false;
    }
}

// ==================== SETUP ====================

void setup() {
    Serial.begin(115200);
    delay(1000);

    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    setLED(true);

    Serial.println();
    Serial.println("========================================");
    Serial.println("   STATION METEO - CAPTEUR LOCAL");
    Serial.println("========================================");
    Serial.println();

    // Charger la configuration
    loadConfig();

    Serial.println("Configuration actuelle:");
    Serial.println("- WiFi: " + wifiSsid);
    Serial.println("- Serveur: " + serverIP + ":" + String(serverPort));
    Serial.println("- Capteur: " + deviceName);
    Serial.println();

    // Verifier si le bouton est appuye au demarrage = mode config
    if (digitalRead(BUTTON_PIN) == LOW) {
        delay(100);
        if (digitalRead(BUTTON_PIN) == LOW) {
            startConfigPortal();
            return;
        }
    }

    // Initialiser les capteurs
    if (!initSensors()) {
        Serial.println("ATTENTION: Aucun capteur detecte!");
    }

    // Connexion WiFi
    if (!connectWiFi()) {
        Serial.println("Impossible de se connecter au WiFi");
        Serial.println("Demarrage du portail de configuration...");
        startConfigPortal();
        return;
    }

    setLED(false);

    Serial.println();
    Serial.println("========================================");
    Serial.println("   CAPTEUR PRET - Envoi toutes les 20s");
    Serial.println("   Appui 3s sur bouton = reset config");
    Serial.println("========================================");
    Serial.println();
}

// ==================== LOOP ====================

void loop() {
    // Mode configuration
    if (configMode) {
        server.handleClient();
        // Blink LED en mode config
        static unsigned long lastBlink = 0;
        if (millis() - lastBlink >= 200) {
            setLED(!digitalRead(LED_PIN));
            lastBlink = millis();
        }
        return;
    }

    // Mode normal
    checkButton();

    // Reconnexion WiFi si necessaire
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi deconnecte - reconnexion...");
        connectWiFi();
    }

    // Envoi periodique
    if (millis() - lastSend >= SEND_INTERVAL) {
        float temperature = 0;
        float humidite = 0;
        float pression = 0;

        if (sht40_ok) {
            sensors_event_t humidity, temp;
            sht4.getEvent(&humidity, &temp);
            temperature = temp.temperature;
            humidite = humidity.relative_humidity;
        }

        if (bmp280_ok) {
            pression = bmp.readPressure() / 100.0F;
        }

        Serial.println("--- Mesures ---");
        Serial.printf("Temperature: %.2f C\n", temperature);
        Serial.printf("Humidite: %.2f %%\n", humidite);
        Serial.printf("Pression: %.2f hPa\n", pression);

        sendData(temperature, humidite, pression);

        // Blink LED pour indiquer envoi
        setLED(true);
        delay(100);
        setLED(false);

        Serial.println();
        lastSend = millis();
    }

    delay(100);
}
