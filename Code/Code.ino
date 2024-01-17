#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define DHTTYPE DHT11
//const char* ssid = "ET@eheio";
//const char* password = "eheio2023";
//const char* ssid = "TNCAP9501C8";
//const char* password = "EB51CF2022@";
const char* ssid = "me";
const char* password = "19661966";
const char* serverName = "http://127.0.0.1:8000/arduinoData";

#define dht_dpin 5
DHT dht(dht_dpin, DHTTYPE);

void setup() {
  dht.begin();
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();         
  
  // Créer une chaîne au format souhaité
  String data = String(temperature, 2) + "," + String(humidity, 2);
  Serial.println(data);
  WiFiClient client;
  HTTPClient http;

  http.begin(client, serverName);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(data);

  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    String response = http.getString();
    Serial.print("Server response: ");
    Serial.println(response);
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();

  delay(60000); // Attendre 1 minute avant d'envoyer la prochaine donnée
}
