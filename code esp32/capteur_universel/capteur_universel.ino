/*
 * Station Meteo - Capteur Universel
 *
 * UN SEUL CODE pour tous les ESP32 !
 * Le numero du capteur se configure dans le portail WiFi.
 *
 * Fonctionnalites:
 * - WiFiManager avec configuration du numero de capteur
 * - Supporte autant de capteurs que tu veux (1, 2, 3, 4...)
 * - Appuie 3 sec sur le bouton pour reconfigurer
 *
 * Auteur: Amin Torrisi / Equipe CPNV
 * Date: Janvier 2026
 */

#include <WiFi.h>
#include <WiFiManager.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_SHT4x.h>
#include <Adafruit_BMP280.h>
#include <Preferences.h>

// ==================== CONFIGURATION ====================
#define SEND_INTERVAL 20000              // Intervalle d'envoi (20 sec)

// ==================== PINS (Atom Lite) ====================
#define BUTTON_PIN 39                    // Bouton
#define LED_PIN 27                       // LED
#define SDA_PIN 26                       // I2C Data
#define SCL_PIN 32                       // I2C Clock

// ==================== OBJETS ====================
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_BMP280 bmp;
WiFiManager wifiManager;
Preferences preferences;

// ==================== VARIABLES CONFIGURABLES ====================
char capteurNumero[3] = "1";             // Numero du capteur (1, 2, 3...)
char serverIP[40] = "192.168.1.100";     // IP du serveur Raspberry
char serverPort[6] = "5000";             // Port du serveur

// ==================== VARIABLES ====================
unsigned long lastSendTime = 0;
unsigned long buttonPressStart = 0;
bool buttonPressed = false;
bool wifiConfigMode = false;
String capteurID;
String serverURL;
String apName;

// ==================== PROTOTYPES ====================
void setLED(bool on);
void sendData(float temp, float hum, float press);
bool initSensors();
void checkButton();
void startConfigPortal();
void loadConfig();
void saveConfig();

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);

    // Configuration des pins
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    setLED(true);  // LED on = demarrage

    // Charger la configuration sauvegardee
    loadConfig();

    // Construire l'ID et le nom du reseau WiFi
    capteurID = "ATOM_00" + String(capteurNumero);
    apName = "METEO_CAPTEUR_" + String(capteurNumero);
    serverURL = "http://" + String(serverIP) + ":" + String(serverPort) + "/request";

    Serial.println("\n========================================");
    Serial.println("   Station Meteo - Capteur " + String(capteurNumero));
    Serial.println("   ID: " + capteurID);
    Serial.println("========================================\n");

    // Initialisation I2C
    Wire.begin(SDA_PIN, SCL_PIN);

    // Initialisation des capteurs
    if (!initSensors()) {
        Serial.println("ERREUR: Capteurs non detectes!");
        // Continue quand meme pour permettre la config WiFi
    }

    // Parametres WiFiManager personnalises
    WiFiManagerParameter custom_capteur_num("capteur", "Numero du capteur (1, 2, 3...)", capteurNumero, 3);
    WiFiManagerParameter custom_server_ip("server", "IP du serveur Raspberry", serverIP, 40);
    WiFiManagerParameter custom_server_port("port", "Port du serveur", serverPort, 6);

    wifiManager.addParameter(&custom_capteur_num);
    wifiManager.addParameter(&custom_server_ip);
    wifiManager.addParameter(&custom_server_port);

    // Callback quand la config est sauvegardee
    wifiManager.setSaveConfigCallback([]() {
        Serial.println("Configuration sauvegardee!");
    });

    wifiManager.setConfigPortalTimeout(180);  // 3 minutes timeout

    // Tentative de connexion automatique
    Serial.println("Connexion WiFi...");
    Serial.println("Reseau AP: " + apName);

    if (wifiManager.autoConnect(apName.c_str(), "meteo123")) {
        Serial.println("WiFi connecte!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());

        // Recuperer les valeurs entrees
        strcpy(capteurNumero, custom_capteur_num.getValue());
        strcpy(serverIP, custom_server_ip.getValue());
        strcpy(serverPort, custom_server_port.getValue());

        // Sauvegarder et reconstruire
        saveConfig();
        capteurID = "ATOM_00" + String(capteurNumero);
        serverURL = "http://" + String(serverIP) + ":" + String(serverPort) + "/request";

        setLED(false);  // LED off = pret
    } else {
        Serial.println("Echec connexion WiFi");
    }

    Serial.println("\n--- Configuration ---");
    Serial.println("Capteur ID: " + capteurID);
    Serial.println("Serveur: " + serverURL);
    Serial.println("\n--- Pret! ---");
    Serial.println("Appuyez 3 sec sur le bouton pour reconfigurer\n");
}

// ==================== LOOP ====================
void loop() {
    // Verifier le bouton pour reset WiFi
    checkButton();

    // Si en mode configuration, ne pas envoyer de donnees
    if (wifiConfigMode) {
        return;
    }

    // Verifier si c'est le moment d'envoyer
    if (millis() - lastSendTime >= SEND_INTERVAL) {
        lastSendTime = millis();

        // Lecture des capteurs
        sensors_event_t humidity, temp;
        sht4.getEvent(&humidity, &temp);
        float temperature = temp.temperature;
        float humidite = humidity.relative_humidity;
        float pression = bmp.readPressure() / 100.0F;

        // Affichage
        Serial.println("--- Mesures (Capteur " + String(capteurNumero) + ") ---");
        Serial.printf("Temperature: %.2f C\n", temperature);
        Serial.printf("Humidite: %.2f %%\n", humidite);
        Serial.printf("Pression: %.2f hPa\n", pression);

        // Envoi des donnees
        if (WiFi.status() == WL_CONNECTED) {
            sendData(temperature, humidite, pression);
            // Blink LED pour indiquer envoi
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

void loadConfig() {
    preferences.begin("meteo", true);  // Read-only
    String num = preferences.getString("capteur", "1");
    String ip = preferences.getString("serverIP", "192.168.1.100");
    String port = preferences.getString("serverPort", "5000");
    preferences.end();

    num.toCharArray(capteurNumero, 3);
    ip.toCharArray(serverIP, 40);
    port.toCharArray(serverPort, 6);

    Serial.println("Config chargee: Capteur " + num + ", IP " + ip + ":" + port);
}

void saveConfig() {
    preferences.begin("meteo", false);  // Read-write
    preferences.putString("capteur", capteurNumero);
    preferences.putString("serverIP", serverIP);
    preferences.putString("serverPort", serverPort);
    preferences.end();

    Serial.println("Config sauvegardee!");
}

bool initSensors() {
    bool success = true;

    // Initialisation SHT40
    if (!sht4.begin()) {
        Serial.println("SHT40 non trouve!");
        success = false;
    } else {
        Serial.println("SHT40 OK");
        sht4.setPrecision(SHT4X_HIGH_PRECISION);
        sht4.setHeater(SHT4X_NO_HEATER);
    }

    // Initialisation BMP280
    if (!bmp.begin(0x76)) {
        if (!bmp.begin(0x77)) {
            Serial.println("BMP280 non trouve!");
            success = false;
        }
    }
    if (success || bmp.begin(0x76) || bmp.begin(0x77)) {
        Serial.println("BMP280 OK");
        bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                        Adafruit_BMP280::SAMPLING_X2,
                        Adafruit_BMP280::SAMPLING_X16,
                        Adafruit_BMP280::FILTER_X16,
                        Adafruit_BMP280::STANDBY_MS_500);
    }

    return success;
}

void sendData(float temp, float hum, float press) {
    HTTPClient http;

    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    // Construction du JSON
    String json = "{";
    json += "\"capteur_id\":\"" + capteurID + "\",";
    json += "\"temperature\":" + String(temp, 2) + ",";
    json += "\"humidite\":" + String(hum, 2) + ",";
    json += "\"pression\":" + String(press, 2);
    json += "}";

    Serial.print("Envoi vers: ");
    Serial.println(serverURL);

    int httpCode = http.POST(json);

    if (httpCode > 0) {
        Serial.printf("Reponse: %d\n", httpCode);
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
            Serial.println("Succes!");
        }
    } else {
        Serial.printf("Erreur HTTP: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
    Serial.println();
}

void checkButton() {
    if (digitalRead(BUTTON_PIN) == LOW) {
        if (!buttonPressed) {
            buttonPressed = true;
            buttonPressStart = millis();
            setLED(true);
        } else if (millis() - buttonPressStart >= 3000) {
            Serial.println("\n*** RESET CONFIG ***\n");
            startConfigPortal();
        }
    } else {
        if (buttonPressed && millis() - buttonPressStart < 3000) {
            setLED(false);
        }
        buttonPressed = false;
    }
}

void startConfigPortal() {
    wifiConfigMode = true;
    setLED(true);

    // Efface les credentials WiFi
    wifiManager.resetSettings();

    // Efface aussi notre config
    preferences.begin("meteo", false);
    preferences.clear();
    preferences.end();

    Serial.println("Redemarrage pour reconfiguration...");
    delay(1000);
    ESP.restart();
}

void setLED(bool on) {
    digitalWrite(LED_PIN, on ? HIGH : LOW);
}
