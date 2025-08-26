#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

#define DHTPIN 4
#define DHTTYPE DHT22
#define SOIL_MOISTURE_PIN 34
#define LIGHT_SENSOR_PIN 35
#define PH_SENSOR_PIN 32
#define BUZZER_PIN 25

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "*";
const char* password = "*";
const char* backendURL = "*";
String probeLocation = "soil";

struct Thresholds {
  float minTemp, maxTemp;
  float minHumidity, maxHumidity;
  int minLight, maxLight;
  float minPH, maxPH;
  int minSoil, maxSoil;
};

Thresholds thresholds = {0};

bool connectToWiFiFlag = false;

void connectToWiFi() {
  if (!connectToWiFiFlag) {
    Serial.println("WiFi connection is skipped.");
    return;
  }
  
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected!");
}

void fetchThresholds() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(backendURL + String("/get-thresholds"));
    int httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      StaticJsonDocument<512> doc;
      deserializeJson(doc, payload);

      thresholds.minTemp = doc["minTemp"];
      thresholds.maxTemp = doc["maxTemp"];
      thresholds.minHumidity = doc["minHumidity"];
      thresholds.maxHumidity = doc["maxHumidity"];
      thresholds.minLight = doc["minLight"];
      thresholds.maxLight = doc["maxLight"];
      thresholds.minPH = doc["minPH"];
      thresholds.maxPH = doc["maxPH"];
      thresholds.minSoil = doc["minSoil"];
      thresholds.maxSoil = doc["maxSoil"];
      
      Serial.println("Fetched thresholds:");
      Serial.printf("Min Temp: %.2f, Max Temp: %.2f\n", thresholds.minTemp, thresholds.maxTemp);
    } else {
      Serial.println("Error fetching thresholds.");
    }
    http.end();
  } else {
    Serial.println("WiFi is not connected, skipping threshold fetch.");
  }
}

bool isInDanger(float temp, float humidity, int light, float ph, int soil) {
  return temp < thresholds.minTemp || temp > thresholds.maxTemp ||
         humidity < thresholds.minHumidity || humidity > thresholds.maxHumidity ||
         light < thresholds.minLight || light > thresholds.maxLight ||
         ph < thresholds.minPH || ph > thresholds.maxPH ||
         soil < thresholds.minSoil || soil > thresholds.maxSoil;
}

void beepBuzzer(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(300);
    digitalWrite(BUZZER_PIN, LOW);
    delay(300);
  }
}

void sendData(float temp, float humidity, int light, float ph, int soil) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(backendURL);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"location\":\"" + probeLocation + "\",";
    json += "\"temperature\":" + String(temp) + ",";
    json += "\"humidity\":" + String(humidity) + ",";
    json += "\"light\":" + String(light) + ",";
    json += "\"ph\":" + String(ph) + ",";
    json += "\"soil_moisture\":" + String(soil) + "}";

    int code = http.POST(json);
    String response = http.getString();
    Serial.println("Server Response: " + response);
    http.end();
  } else {
    Serial.println("No WiFi connection. Skipping data send.");
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(BUZZER_PIN, OUTPUT);
  connectToWiFi();
  fetchThresholds();
}

void loop() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  int light = analogRead(LIGHT_SENSOR_PIN);
  float ph = analogRead(PH_SENSOR_PIN) * (14.0 / 4095.0);
  int soil = analogRead(SOIL_MOISTURE_PIN);

  Serial.println("Reading sensors...");
  Serial.printf("Temp: %.2f C | Humidity: %.2f %% | Light: %d | pH: %.2f | Soil: %d\n", temp, humidity, light, ph, soil);

  if (isInDanger(temp, humidity, light, ph, soil)) {
    Serial.println("Danger detected!");
    beepBuzzer(3);
  }

  sendData(temp, humidity, light, ph, soil);
  delay(10000);
}

