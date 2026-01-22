/*
 * Station Meteo - Capteur 1 (ATOM_001)
 *
 * ESP32 Atom Lite + Capteur ENV IV (SHT40 + BMP280)
 *
 * Fonctionnalites:
 * - WiFiManager: Appuie 3 sec sur le bouton pour configurer le WiFi
 * - Envoi des donnees vers le serveur Flask local
 * - LED RGB pour indiquer l'etat
 *
 * Auteur: Amin Torrisi
 * Date: Janvier 2026
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_SHT4x.h>
#include <Adafruit_BMP280.h>

// ==================== CONFIGURATION ====================
#define CAPTEUR_ID "ATOM_001"           // Identifiant du capteur
#define SEND_INTERVAL 20000              // Intervalle d'envoi (20 sec)

// URL du serveur Railway (cloud)
String SERVER_URL = "https://nurturing-achievement-production.up.railway.app/request/";

// ==================== PINS ====================
#define BUTTON_PIN 39                    // Bouton sur Atom Lite
#define LED_PIN 27                       // LED RGB sur Atom Lite
#define SDA_PIN 26                       // I2C Data
#define SCL_PIN 32                       // I2C Clock

// ==================== OBJETS ====================
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_BMP280 bmp;
WiFiManager wifiManager;

// ==================== VARIABLES ====================
unsigned long lastSendTime = 0;
unsigned long buttonPressStart = 0;
bool buttonPressed = false;
bool wifiConfigMode = false;

// ==================== PROTOTYPES ====================
void setLED(uint8_t r, uint8_t g, uint8_t b);
void sendData(float temp, float hum, float press);
bool initSensors();
void checkButton();
void startConfigPortal();

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n========================================");
    Serial.println("   Station Meteo - Capteur 1 (ATOM_001)");
    Serial.println("========================================\n");

    // Configuration des pins
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);

    // LED orange = demarrage
    setLED(255, 165, 0);

    // Initialisation I2C
    Wire.begin(SDA_PIN, SCL_PIN);

    // Initialisation des capteurs
    if (!initSensors()) {
        Serial.println("ERREUR: Capteurs non detectes!");
        setLED(255, 0, 0);  // LED rouge
        while(1) delay(1000);
    }

    // Configuration WiFiManager
    wifiManager.setConfigPortalTimeout(180);  // 3 minutes timeout
    wifiManager.setAPCallback([](WiFiManager *myWiFiManager) {
        Serial.println("Mode configuration WiFi active!");
        Serial.println("Connectez-vous au reseau: METEO_CAPTEUR_1");
        Serial.println("Puis allez sur: 192.168.4.1");
        setLED(0, 0, 255);  // LED bleue = mode config
    });

    // Tentative de connexion automatique
    Serial.println("Connexion WiFi...");
    setLED(255, 255, 0);  // LED jaune = connexion

    if (wifiManager.autoConnect("METEO_CAPTEUR_1", "meteo123")) {
        Serial.println("WiFi connecte!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
        setLED(0, 255, 0);  // LED verte = connecte
    } else {
        Serial.println("Echec connexion WiFi");
        setLED(255, 0, 0);  // LED rouge
    }

    Serial.println("\n--- Pret! ---");
    Serial.println("Appuyez 3 sec sur le bouton pour reconfigurer le WiFi\n");
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
        Serial.println("--- Mesures ---");
        Serial.printf("Temperature: %.2f C\n", temperature);
        Serial.printf("Humidite: %.2f %%\n", humidite);
        Serial.printf("Pression: %.2f hPa\n", pression);

        // Envoi des donnees
        if (WiFi.status() == WL_CONNECTED) {
            sendData(temperature, humidite, pression);
            setLED(0, 255, 0);  // LED verte
        } else {
            Serial.println("WiFi deconnecte!");
            setLED(255, 0, 0);  // LED rouge

            // Tentative de reconnexion
            WiFi.reconnect();
        }
    }

    delay(100);
}

// ==================== FONCTIONS ====================

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
    if (success) {
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
    WiFiClientSecure client;
    client.setInsecure();  // Desactive la verification du certificat SSL
    client.setTimeout(30000);  // Timeout de 30 secondes pour SSL
    client.setHandshakeTimeout(30);  // Timeout handshake SSL en secondes

    HTTPClient http;
    http.setTimeout(30000);  // Timeout HTTP de 30 secondes
    http.setConnectTimeout(30000);  // Timeout connexion de 30 secondes

    Serial.println("Connexion HTTPS en cours...");

    if (!http.begin(client, SERVER_URL)) {
        Serial.println("Erreur: Impossible d'initialiser la connexion HTTP");
        return;
    }
    http.addHeader("Content-Type", "application/json");

    // Construction du JSON
    String json = "{";
    json += "\"capteur_id\":\"" + String(CAPTEUR_ID) + "\",";
    json += "\"temperature\":" + String(temp, 2) + ",";
    json += "\"humidite\":" + String(hum, 2) + ",";
    json += "\"pression\":" + String(press, 2);
    json += "}";

    Serial.print("Envoi vers: ");
    Serial.println(SERVER_URL);
    Serial.print("JSON: ");
    Serial.println(json);

    int httpCode = http.POST(json);

    if (httpCode > 0) {
        Serial.printf("Reponse: %d\n", httpCode);
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
            String response = http.getString();
            Serial.println("Succes: " + response);
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
        } else if (millis() - buttonPressStart >= 3000) {
            // Bouton appuye pendant 3 secondes
            Serial.println("\n*** RESET WIFI ***\n");
            startConfigPortal();
        }
    } else {
        buttonPressed = false;
    }
}

void startConfigPortal() {
    wifiConfigMode = true;
    setLED(0, 0, 255);  // LED bleue

    // Efface les credentials WiFi sauvegardes
    wifiManager.resetSettings();

    // Demarre le portail de configuration
    Serial.println("Demarrage du portail de configuration...");
    Serial.println("Connectez-vous au reseau: METEO_CAPTEUR_1");
    Serial.println("Mot de passe: meteo123");
    Serial.println("Puis ouvrez: http://192.168.4.1");

    if (wifiManager.startConfigPortal("METEO_CAPTEUR_1", "meteo123")) {
        Serial.println("WiFi configure avec succes!");
        setLED(0, 255, 0);
    } else {
        Serial.println("Configuration annulee ou timeout");
        setLED(255, 165, 0);
    }

    wifiConfigMode = false;
    ESP.restart();
}

void setLED(uint8_t r, uint8_t g, uint8_t b) {
    // Pour Atom Lite, la LED est sur le pin 27
    // Cette fonction simple allume juste la LED
    // Pour les couleurs RGB, il faudrait utiliser FastLED ou NeoPixel
    if (r > 0 || g > 0 || b > 0) {
        digitalWrite(LED_PIN, HIGH);
    } else {
        digitalWrite(LED_PIN, LOW);
    }
}
