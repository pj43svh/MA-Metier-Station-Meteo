/*
 * Station Meteo - Capteur Auto-Configure
 *
 * Ce code s'enregistre automatiquement sur le serveur avec son adresse MAC.
 * Le numero de capteur est configure via l'interface admin web.
 *
 * Fonctionnement:
 * 1. L'ESP32 se connecte au WiFi
 * 2. Il envoie son adresse MAC au serveur
 * 3. Le serveur lui renvoie son numero de capteur (si configure)
 * 4. L'ESP32 envoie ses donnees avec ce numero
 *
 * Auteur: Amin Torrisi / Equipe CPNV
 * Date: Janvier 2026
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_SHT4x.h>
#include <Adafruit_BMP280.h>
#include <ArduinoJson.h>

// ==================== CONFIGURATION ====================
#define SEND_INTERVAL 20000              // Intervalle d'envoi (20 sec)
#define CONFIG_CHECK_INTERVAL 60000      // Verification config (60 sec)

// WiFi - Ton hotspot
const char* WIFI_SSID = "Bomboclat";
const char* WIFI_PASSWORD = "zyxouzyxou";

// URL du serveur Railway
const char* SERVER_BASE = "https://nurturing-achievement-production.up.railway.app";

// ==================== PINS (Atom Lite) ====================
#define BUTTON_PIN 39                    // Bouton
#define LED_PIN 27                       // LED
#define SDA_PIN 26                       // I2C Data
#define SCL_PIN 32                       // I2C Clock

// ==================== OBJETS ====================
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_BMP280 bmp;

// ==================== VARIABLES ====================
unsigned long lastSendTime = 0;
unsigned long lastConfigCheck = 0;
unsigned long buttonPressStart = 0;
bool buttonPressed = false;

String macAddress;
int sensorNumber = 0;           // 0 = pas encore configure
String capteurID = "";

// ==================== PROTOTYPES ====================
void setLED(bool on);
void sendData(float temp, float hum, float press);
bool initSensors();
void checkButton();
bool registerWithServer();
bool getConfigFromServer();

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
        // Continue quand meme
    }

    // Connexion WiFi
    Serial.println("\nConnexion WiFi...");
    Serial.print("SSID: ");
    Serial.println(WIFI_SSID);

    WiFi.mode(WIFI_STA);  // Important: definir le mode avant begin()
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

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

        // Recuperer l'adresse MAC APRES connexion WiFi
        macAddress = WiFi.macAddress();

        Serial.println("\n========================================");
        Serial.println("   Station Meteo - Auto-Configure");
        Serial.println("   MAC: " + macAddress);
        Serial.println("========================================\n");

        setLED(false);

        // S'enregistrer sur le serveur et recuperer la config
        registerWithServer();
        getConfigFromServer();
    } else {
        Serial.println("Echec connexion WiFi");
        // Recuperer MAC quand meme pour debug
        macAddress = WiFi.macAddress();
        Serial.println("MAC: " + macAddress);
    }

    Serial.println("\n--- Pret! ---");
    if (sensorNumber > 0) {
        Serial.println("Capteur configure: " + capteurID);
    } else {
        Serial.println("En attente de configuration via l'interface admin...");
        Serial.println("Allez sur: " + String(SERVER_BASE) + "/admin");
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
    WiFiClientSecure client;
    client.setInsecure();
    client.setTimeout(30000);

    HTTPClient http;
    http.setTimeout(30000);

    String url = String(SERVER_BASE) + "/api/esp32/register";

    if (!http.begin(client, url)) {
        Serial.println("Erreur connexion serveur");
        return false;
    }

    http.addHeader("Content-Type", "application/json");

    // JSON avec MAC et IP
    String json = "{\"mac_address\":\"" + macAddress + "\",\"ip_address\":\"" + WiFi.localIP().toString() + "\"}";

    Serial.println("Enregistrement sur le serveur...");
    int httpCode = http.POST(json);

    if (httpCode > 0) {
        String response = http.getString();
        Serial.println("Reponse: " + response);

        // Parser la reponse JSON
        StaticJsonDocument<256> doc;
        if (deserializeJson(doc, response) == DeserializationError::Ok) {
            const char* status = doc["status"];
            if (strcmp(status, "configured") == 0) {
                sensorNumber = doc["sensor_number"];
                capteurID = String(doc["capteur_id"] | "");
                Serial.println("Deja configure comme: " + capteurID);
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
    WiFiClientSecure client;
    client.setInsecure();
    client.setTimeout(30000);

    HTTPClient http;
    http.setTimeout(30000);

    String url = String(SERVER_BASE) + "/api/esp32/config/" + macAddress;

    if (!http.begin(client, url)) {
        return false;
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
                    return true;
                }
            }
        }
    }

    http.end();
    return false;
}

void sendData(float temp, float hum, float press) {
    WiFiClientSecure client;
    client.setInsecure();
    client.setTimeout(30000);
    client.setHandshakeTimeout(30);

    HTTPClient http;
    http.setTimeout(30000);
    http.setConnectTimeout(30000);

    String url = String(SERVER_BASE) + "/request/";

    if (!http.begin(client, url)) {
        Serial.println("Erreur connexion");
        return;
    }
    http.addHeader("Content-Type", "application/json");

    // JSON avec les donnees + MAC pour mise a jour du last_seen
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
            Serial.println("\n*** RESET ***");
            Serial.println("Redemarrage...\n");
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
