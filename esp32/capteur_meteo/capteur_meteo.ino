/*
 * Station Meteo Connectee
 * ESP32 Atom Lite + Capteur ENV IV
 *
 * Envoie les donnees vers:
 * 1. ThingSpeak (cloud) - pour visualisation internet
 * 2. Serveur local Raspberry Pi - pour interface locale
 *
 * Materiel:
 * - M5Stack Atom Lite (ESP32-PICO-D4)
 * - Capteur ENV IV (SHT40 + BMP280)
 *
 * Configuration Arduino IDE:
 * - Carte: M5Atom
 * - Port: COM6 (ou autre selon votre PC)
 *
 * Bibliotheques requises (a installer via Library Manager):
 * - Adafruit SHT4x
 * - Adafruit BMP280
 *
 * Date: 13 Janvier 2026
 * Auteur: Amin Torrisi
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "Adafruit_SHT4x.h"
#include <Adafruit_BMP280.h>

// ==================== CONFIGURATION WiFi ====================
const char* WIFI_SSID = "Galaxy Abeeby";
const char* WIFI_PASSWORD = "cxie3864";

// ==================== CONFIGURATION ThingSpeak ====================
const char* THINGSPEAK_API_KEY = "0TEJ9QR3RFIBFZ3M";
const bool USE_THINGSPEAK = true;  // Mettre false pour desactiver

// ==================== CONFIGURATION Serveur Local (Raspberry Pi) ====================
const char* RASPBERRY_IP = "10.244.96.106";  // A modifier selon votre Raspberry Pi
const int RASPBERRY_PORT = 5000;
const bool USE_LOCAL_SERVER = true;  // Mettre false pour desactiver

// ==================== CONFIGURATION Capteur ====================
const char* CAPTEUR_ID = "ATOM_001"; // Identifiant unique de ce capteur
const char* CAPTEUR_ID = "ATOM_002" // le deuxième capteur
// ==================== INTERVALLE ====================
// ThingSpeak gratuit: minimum 15 secondes entre envois
const unsigned long SEND_INTERVAL = 20000;  // 20 secondes

// ==================== OBJETS CAPTEURS ====================
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_BMP280 bmp;

// ==================== VARIABLES ====================
bool sht40_ok = false;
bool bmp280_ok = false;
unsigned long lastSend = 0;

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println();
    Serial.println("========================================");
    Serial.println("   STATION METEO CONNECTEE");
    Serial.println("   " + String(CAPTEUR_ID));
    Serial.println("========================================");
    Serial.println();

    // Initialisation I2C sur les pins Grove de l'Atom Lite
    Wire.begin(26, 32);  // SDA=GPIO26, SCL=GPIO32

    // Initialisation du capteur SHT40 (temperature + humidite)
    Serial.print("Initialisation SHT40... ");
    if (!sht4.begin()) {
        Serial.println("ERREUR!");
        sht40_ok = false;
    } else {
        Serial.println("OK");
        sht4.setPrecision(SHT4X_HIGH_PRECISION);
        sht40_ok = true;
    }

    // Initialisation du capteur BMP280 (pression)
    Serial.print("Initialisation BMP280... ");
    if (!bmp.begin(0x76)) {
        Serial.println("ERREUR!");
        bmp280_ok = false;
    } else {
        Serial.println("OK");
        bmp280_ok = true;
    }

    // Connexion WiFi
    connectWiFi();

    Serial.println();
    Serial.println("Configuration:");
    Serial.println("- ThingSpeak: " + String(USE_THINGSPEAK ? "Actif" : "Desactive"));
    Serial.println("- Serveur local: " + String(USE_LOCAL_SERVER ? "Actif" : "Desactive"));
    Serial.println("- Intervalle: " + String(SEND_INTERVAL/1000) + " secondes");
    Serial.println();
    Serial.println("========================================");
    Serial.println("   Demarrage des mesures...");
    Serial.println("========================================");
    Serial.println();
}

// ==================== LOOP ====================
void loop() {
    // Verifie la connexion WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi deconnecte - reconnexion...");
        connectWiFi();
    }

    // Envoi periodique
    if (millis() - lastSend >= SEND_INTERVAL) {
        // Lecture des capteurs
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
            pression = bmp.readPressure() / 100.0F;  // Pa -> hPa
        }

        // Affichage
        Serial.println("--- Mesures ---");
        Serial.print("Temperature: "); Serial.print(temperature, 2); Serial.println(" C");
        Serial.print("Humidite:    "); Serial.print(humidite, 2); Serial.println(" %");
        Serial.print("Pression:    "); Serial.print(pression, 2); Serial.println(" hPa");

        // Envoi vers ThingSpeak
        if (USE_THINGSPEAK) {
            sendToThingSpeak(temperature, humidite, pression);
        }

        // Envoi vers serveur local (Raspberry Pi)
        if (USE_LOCAL_SERVER) {
            sendToLocalServer(temperature, humidite, pression);
        }

        Serial.println();
        lastSend = millis();
    }

    delay(100);
}

// ==================== FONCTIONS ====================

void connectWiFi() {
    Serial.print("Connexion WiFi vers ");
    Serial.print(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("Connecte! IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("Echec de connexion WiFi!");
    }
}

void sendToThingSpeak(float temperature, float humidite, float pression) {
    HTTPClient http;

    String url = "http://api.thingspeak.com/update?api_key=";
    url += THINGSPEAK_API_KEY;
    url += "&field1=" + String(temperature, 2);
    url += "&field2=" + String(humidite, 2);
    url += "&field3=" + String(pression, 2);

    http.begin(url);
    int httpCode = http.GET();

    Serial.print("ThingSpeak: ");
    if (httpCode > 0) {
        Serial.print(httpCode);
        Serial.println(" OK");
    } else {
        Serial.print("Erreur ");
        Serial.println(httpCode);
    }

    http.end();
}

void sendToLocalServer(float temperature, float humidite, float pression) {
    HTTPClient http;

    String url = "http://" + String(RASPBERRY_IP) + ":" + String(RASPBERRY_PORT) + "/api/mesures";

    // Construction du JSON
    String json = "{";
    json += "\"capteur_id\":\"" + String(CAPTEUR_ID) + "\",";
    json += "\"temperature\":" + String(temperature, 2) + ",";
    json += "\"humidite\":" + String(humidite, 2) + ",";
    json += "\"pression\":" + String(pression, 2);
    json += "}";

    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    int httpCode = http.POST(json);

    Serial.print("Serveur local: ");
    if (httpCode > 0) {
        Serial.print(httpCode);
        if (httpCode == 201) {
            Serial.println(" OK");
        } else {
            Serial.println(" (reponse inattendue)");
        }
    } else {
        Serial.print("Erreur ");
        Serial.println(httpCode);
    }

    http.end();
}
