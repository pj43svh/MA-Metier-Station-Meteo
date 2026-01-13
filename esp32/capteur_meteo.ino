/*
 * Station Météo - ESP32 Atom (M5Stack)
 *
 * Ce code lit les capteurs et envoie les données
 * au Raspberry Pi via HTTP POST.
 *
 * Matériel requis:
 * - ESP32 Atom (M5Stack)
 * - DHT22 (température + humidité)
 * - LDR + résistance 10kΩ (luminosité) - optionnel
 *
 * Câblage ESP32 Atom (Grove connector):
 * - Port Grove: G26 (données DHT22)
 *
 * Câblage direct:
 * - DHT22 VCC  → 3.3V
 * - DHT22 DATA → G26
 * - DHT22 GND  → GND
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ==================== CONFIGURATION - À MODIFIER ====================

// WiFi
const char* WIFI_SSID = "VOTRE_SSID";           // ← Mettre le nom de ton WiFi
const char* WIFI_PASSWORD = "VOTRE_MOT_DE_PASSE"; // ← Mettre le mot de passe

// Adresse IP du Raspberry Pi (utilise: hostname -I sur le RPi)
const char* SERVER_URL = "http://192.168.1.45:5000/api/mesures"; // ← Mettre l'IP du RPi

// Identifiant unique de cet ESP32 (doit correspondre à celui enregistré sur l'interface web)
const char* ESP_ID = "ESP32_ATOM_001";

// Intervalle d'envoi (en millisecondes)
const unsigned long SEND_INTERVAL = 30000;  // 30 secondes

// ==================== PINS ESP32 ATOM ====================

// Pour ESP32 Atom, utiliser G26 (port Grove) ou G25, G21, G22
#define DHT_PIN 26        // GPIO 26 sur ESP32 Atom
#define DHT_TYPE DHT22    // ou DHT11 si c'est ce que tu as
#define LDR_PIN 32        // GPIO 32 pour le LDR (optionnel)
#define USE_LDR false     // Mettre true si tu as un capteur de luminosité

// ==================== OBJETS ====================

DHT dht(DHT_PIN, DHT_TYPE);
unsigned long lastSendTime = 0;

// ==================== SETUP ====================

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Station Météo ESP32 ===");

    // Initialisation du capteur DHT
    dht.begin();
    Serial.println("DHT22 initialisé");

    // Connexion WiFi
    connectWiFi();
}

// ==================== LOOP ====================

void loop() {
    // Vérifie la connexion WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi déconnecté, reconnexion...");
        connectWiFi();
    }

    // Envoi périodique des données
    if (millis() - lastSendTime >= SEND_INTERVAL) {
        sendData();
        lastSendTime = millis();
    }

    delay(100);
}

// ==================== FONCTIONS ====================

void connectWiFi() {
    Serial.print("Connexion à ");
    Serial.println(WIFI_SSID);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connecté!");
        Serial.print("Adresse IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nÉchec de connexion WiFi");
    }
}

void sendData() {
    // Lecture des capteurs
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int ldrValue = analogRead(LDR_PIN);

    // Conversion LDR en lux (approximatif)
    float luminosity = map(ldrValue, 0, 4095, 0, 10000);

    // Vérification des valeurs DHT
    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Erreur de lecture DHT22!");
        return;
    }

    // Affichage des valeurs
    Serial.println("\n--- Mesures ---");
    Serial.printf("Température: %.1f °C\n", temperature);
    Serial.printf("Humidité: %.1f %%\n", humidity);
    Serial.printf("Luminosité: %.0f lux\n", luminosity);

    // Construction du JSON
    StaticJsonDocument<256> doc;
    doc["esp_id"] = ESP_ID;

    JsonArray mesures = doc.createNestedArray("mesures");

    JsonObject temp = mesures.createNestedObject();
    temp["type"] = "temperature";
    temp["valeur"] = temperature;
    temp["unite"] = "°C";

    JsonObject hum = mesures.createNestedObject();
    hum["type"] = "humidite";
    hum["valeur"] = humidity;
    hum["unite"] = "%";

    JsonObject lum = mesures.createNestedObject();
    lum["type"] = "luminosite";
    lum["valeur"] = luminosity;
    lum["unite"] = "lux";

    String jsonString;
    serializeJson(doc, jsonString);

    Serial.println("Envoi: " + jsonString);

    // Envoi HTTP POST
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(SERVER_URL);
        http.addHeader("Content-Type", "application/json");

        int httpCode = http.POST(jsonString);

        if (httpCode > 0) {
            Serial.printf("Réponse HTTP: %d\n", httpCode);
            if (httpCode == HTTP_CODE_CREATED) {
                Serial.println("Données envoyées avec succès!");
            } else {
                String response = http.getString();
                Serial.println("Réponse: " + response);
            }
        } else {
            Serial.printf("Erreur HTTP: %s\n", http.errorToString(httpCode).c_str());
        }

        http.end();
    }
}
