#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 4  // Digital pin connected to the DHT sensor

#define DHTTYPE    DHT22     // DHT 22 (AM2302)

DHT_Unified dht(DHTPIN, DHTTYPE);

uint32_t delayMS;

// Set your desired temperature and humidity setpoints
float temperatureSetpoint = 25.0; // Celsius
float humiditySetpoint = 60.0; // %

// Define pins for your control devices (e.g., relays for a heater and a humidifier)
#define HEATER_PIN 16
#define HUMIDIFIER_PIN 17


void setup() {
  Serial.begin(9600);
  // Initialize device.
  dht.begin();
  Serial.println(F("DHTxx Unified Sensor Example"));
  // Print temperature sensor details.
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  Serial.println(F("------------------------------------"));
  Serial.println(F("Temperature Sensor"));
  Serial.print  (F("Sensor Type: ")); Serial.println(sensor.name);
  Serial.print  (F("Driver Ver:  ")); Serial.println(sensor.version);
  Serial.print  (F("Unique ID:   ")); Serial.println(sensor.sensor_id);
  Serial.print  (F("Max Value:   ")); Serial.print(sensor.max_value); Serial.println(F("°C"));
  Serial.print  (F("Min Value:   ")); Serial.print(sensor.min_value); Serial.println(F("°C"));
  Serial.print  (F("Resolution:  ")); Serial.print(sensor.resolution); Serial.println(F("°C"));
  Serial.println(F("------------------------------------"));
  // Print humidity sensor details.
  dht.humidity().getSensor(&sensor);
  Serial.println(F("Humidity Sensor"));
  Serial.print  (F("Sensor Type: ")); Serial.println(sensor.name);
  Serial.print  (F("Driver Ver:  ")); Serial.println(sensor.version);
  Serial.print  (F("Unique ID:   ")); Serial.println(sensor.sensor_id);
  Serial.print  (F("Max Value:   ")); Serial.print(sensor.max_value); Serial.println(F("%"));
  Serial.print  (F("Min Value:   ")); Serial.print(sensor.min_value); Serial.println(F("%"));
  Serial.print  (F("Resolution:  ")); Serial.print(sensor.resolution); Serial.println(F("%"));
  Serial.println(F("------------------------------------"));
  // Set delay between measurements.
  delayMS = sensor.min_delay / 1000;

  pinMode(HEATER_PIN, OUTPUT);
  pinMode(HUMIDIFIER_PIN, OUTPUT);

  digitalWrite(HEATER_PIN, LOW);
  digitalWrite(HUMIDIFIER_PIN, LOW);
}

void loop() {
  // Delay between measurements.
  delay(delayMS);
  // Get temperature event and print its value.
  sensors_event_t event;
  dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) {
    Serial.println(F("Error reading temperature!"));
  }
  else {
    Serial.print(F("Temperature: "));
    Serial.print(event.temperature);
    Serial.println(F("°C"));

    // Temperature control logic
    if (event.temperature < temperatureSetpoint) {
      digitalWrite(HEATER_PIN, HIGH); // Turn on heater
      Serial.println("Heater ON");
    } else {
      digitalWrite(HEATER_PIN, LOW); // Turn off heater
      Serial.println("Heater OFF");
    }
  }
  // Get humidity event and print its value.
  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) {
    Serial.println(F("Error reading humidity!"));
  }
  else {
    Serial.print(F("Humidity: "));
    Serial.print(event.relative_humidity);
    Serial.println(F("%"));

    // Humidity control logic
    if (event.relative_humidity < humiditySetpoint) {
      digitalWrite(HUMIDIFIER_PIN, HIGH); // Turn on humidifier
      Serial.println("Humidifier ON");
    } else {
      digitalWrite(HUMIDIFIER_PIN, LOW); // Turn off humidifier
      Serial.println("Humidifier OFF");
    }
  }
}
