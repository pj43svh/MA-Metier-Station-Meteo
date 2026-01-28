#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "Adafruit_SHT4x.h"
#include <Adafruit_BMP280.h>
#include "secrets.h"

// ==================== CONFIG PORTAIL ====================
//const char* AP_SSID   = "Apéro ? ^-^";
//const char* AP_PASS   = "bzwd9335";
WebServer server(80);
Preferences prefs;

// ==================== CONFIG STATION ====================
String wifiSsid   = "";
String wifiPass   = "";
String deviceName = "ESP32_DEFAULT";

// ==================== CONFIG THINGSPEAK / LOCAL ====================
String THINGSPEAK_API_KEY = "0TEJ9QR3RFIBFZ3M";
bool   USE_THINGSPEAK     = true;

String RASPBERRY_IP   = "10.54.141.202";
int    RASPBERRY_PORT = 5000;
bool   USE_LOCAL_SERVER = true;

const unsigned long SEND_INTERVAL = 20000; // 20s

// ==================== CAPTEURS ENV IV ====================
Adafruit_SHT4x sht4 = Adafruit_SHT4x();
Adafruit_BMP280 bmp;

bool sht40_ok = false;
bool bmp280_ok = false;
unsigned long lastSend = 0;

// ==================== HTML PORTAIL CONFIG ====================
const char HTML_FORM[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Configuration ESP32</title>
</head>
<body>
  <h1>Configuration ESP32</h1>
  <form method="POST" action="/save">
    <label>SSID WiFi :</label><br>
    <input type="text" name="ssid"><br><br>

    <label>Mot de passe :</label><br>
    <input type="password" name="pass"><br><br>

    <label>Nom de l'ESP32 :</label><br>
    <input type="text" name="name" value="ATOM_002"><br><br>

    <input type="submit" value="Enregistrer">
  </form>
  <p>Apres validation, l'ESP32 redemarrera avec ces parametres.</p>
</body>
</html>
)rawliteral";

// ==================== GESTION CONFIG ====================
void loadConfig() {
  prefs.begin("config", true);              // lecture seule
  wifiSsid   = prefs.getString("ssid", "");
  wifiPass   = prefs.getString("pass", "");
  deviceName = prefs.getString("name", "ESP32_DEFAULT");
  prefs.end();
}

void saveConfig(const String& ssid, const String& pass, const String& name) {
  prefs.begin("config", false);             // ecriture
  prefs.putString("ssid", ssid);
  prefs.putString("pass", pass);
  prefs.putString("name", name);
  prefs.end();
}

void resetConfig() {
  prefs.begin("config", false);
  prefs.clear();
  prefs.end();
}

// ==================== HANDLERS WEB ====================
void handleRoot() {
  server.send(200, "text/html", HTML_FORM);
}

void handleSave() {
  String ssid = server.arg("ssid");
  String pass = server.arg("pass");
  String name = server.arg("name");

  if (ssid.length() == 0) {
    server.send(400, "text/plain", "SSID manquant");
    return;
  }

  saveConfig(ssid, pass, name);

  server.send(200, "text/plain",
              "Configuration enregistree.\n"
              "SSID: " + ssid + "\n"
              "Nom : " + name + "\n\n"
              "Redemarrage dans 2 secondes...");
  delay(2000);
  ESP.restart();
}

void startConfigPortal() {
  Serial.println("=== MODE CONFIGURATION ===");
  Serial.println("AP: " + String(AP_SSID) + " / " + String(AP_PASS));

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);

  IPAddress ip = WiFi.softAPIP();
  Serial.print("Connectez-vous au WiFi '");
  Serial.print(AP_SSID);
  Serial.println("' puis ouvrez http://" + ip.toString() + "/");

  server.on("/", HTTP_GET, handleRoot);
  server.on("/save", HTTP_POST, handleSave);
  server.begin();
}

// ==================== FONCTIONS EXISTANTES ====================
void connectWiFiStation() {
  Serial.print("Connexion WiFi vers ");
  Serial.print(wifiSsid);

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
    Serial.print("Connecte! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Echec de connexion WiFi!");
  }
}

void sendToThingSpeak(float temperature, float humidite, float pression) {
  if (!USE_THINGSPEAK) return;
  if (WiFi.status() != WL_CONNECTED) return;

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
  if (!USE_LOCAL_SERVER) return;
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  String url = "http://" + String(RASPBERRY_IP) + ":" + String(RASPBERRY_PORT) + "/api/mesures";

  String json = "{";
  json += "\"capteur_id\":\"" + deviceName + "\","; // nom config
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

// ==================== SETUP ====================
bool configMode = false;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("========================================");
  Serial.println("   STATION METEO CONNECTEE");
  Serial.println("========================================");
  Serial.println();

  loadConfig();

  // Si bouton de reset ou pas de SSID enregistré = mode portail
  if (wifiSsid == "") {
    configMode = true;
    startConfigPortal();
    return;
  }

  Serial.println("Config existante trouvee :");
  Serial.println("- SSID : " + wifiSsid);
  Serial.println("- Nom  : " + deviceName);
  Serial.println();

  // Initialisation I2C ENV IV
  Wire.begin(26, 32);  // SDA=GPIO26, SCL=GPIO32

  Serial.print("Initialisation SHT40... ");
  if (!sht4.begin()) {
    Serial.println("ERREUR!");
    sht40_ok = false;
  } else {
    Serial.println("OK");
    sht4.setPrecision(SHT4X_HIGH_PRECISION);
    sht40_ok = true;
  }

  Serial.print("Initialisation BMP280... ");
  if (!bmp.begin(0x76)) {
    Serial.println("ERREUR!");
    bmp280_ok = false;
  } else {
    Serial.println("OK");
    bmp280_ok = true;
  }

  connectWiFiStation();

  Serial.println();
  Serial.println("Configuration:");
  Serial.println("- ThingSpeak: " + String(USE_THINGSPEAK ? "Actif" : "Desactive"));
  Serial.println("- Serveur local: " + String(USE_LOCAL_SERVER ? "Actif" : "Desactive"));
  Serial.println("- Intervalle: " + String(SEND_INTERVAL / 1000) + " secondes");
  Serial.println("- Nom capteur: " + deviceName);
  Serial.println("========================================");
}

// ==================== LOOP ====================
void loop() {
  if (configMode) {
    // Mode portail
    server.handleClient();
    return;
  }

  // Mode normal (station meteo)
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi deconnecte - reconnexion...");
    connectWiFiStation();
  }

  if (millis() - lastSend >= SEND_INTERVAL) {
    float temperature = 0;
    float humidite    = 0;
    float pression    = 0;

    if (sht40_ok) {
      sensors_event_t humidity, temp;
      sht4.getEvent(&humidity, &temp);
      temperature = temp.temperature;
      humidite    = humidity.relative_humidity;
    }

    if (bmp280_ok) {
      pression = bmp.readPressure() / 100.0F; // Pa -> hPa
    }

    Serial.println("--- Mesures ---");
    Serial.print("Temp: "); Serial.print(temperature, 2); Serial.println(" C");
    Serial.print("Hum:  "); Serial.print(humidite, 2);    Serial.println(" %");
    Serial.print("Pres: "); Serial.print(pression, 2);    Serial.println(" hPa");

    sendToThingSpeak(temperature, humidite, pression);
    sendToLocalServer(temperature, humidite, pression);

    Serial.println();
    lastSend = millis();
  }

  delay(100);
}
