# ESP32 DHT22 Temperature and Humidity Controller

This Arduino sketch turns an ESP32 into a temperature and humidity controller using a DHT22 sensor.

## Hardware Requirements

*   ESP32 development board
*   DHT22 (or AM2302) temperature and humidity sensor
*   A relay module to control a heater
*   A relay module to control a humidifier
*   Jumper wires
*   5V power supply for the relay modules (optional, depending on the module)

## Software Requirements

*   [Arduino IDE](https://www.arduino.cc/en/software)
*   [ESP32 board support for the Arduino IDE](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
*   [DHT sensor library by Adafruit](https://github.com/adafruit/DHT-sensor-library)
*   [Adafruit Unified Sensor library](https://github.com/adafruit/Adafruit_Sensor)

## Circuit Setup

1.  **DHT22 Sensor:**
    *   Connect the VCC pin of the DHT22 to the 3.3V pin on the ESP32.
    *   Connect the GND pin of the DHT22 to a GND pin on the ESP32.
    *   Connect the Data pin of the DHT22 to pin D4 on the ESP32.
    *   Place a 10k ohm pull-up resistor between the VCC and Data pins of the DHT22.

2.  **Relay Modules:**
    *   Connect the IN pin of the heater relay module to pin D16 on the ESP32.
    *   Connect the IN pin of the humidifier relay module to pin D17 on the ESP32.
    *   Connect the VCC and GND pins of the relay modules to a suitable power source (e.g., the 5V pin on the ESP32 or an external power supply).
    *   Connect your heater and humidifier to the output terminals of their respective relay modules according to the relay module's documentation.

## How to Use

1.  **Install the necessary libraries:**
    *   Open the Arduino IDE.
    *   Go to **Sketch > Include Library > Manage Libraries...**
    *   Search for and install the "DHT sensor library by Adafruit".
    *   Search for and install the "Adafruit Unified Sensor" library.

2.  **Configure the code:**
    *   Open the `esp32_dht22_controller.ino` file in the Arduino IDE.
    *   Adjust the `temperatureSetpoint` and `humiditySetpoint` variables to your desired values.

3.  **Upload the code:**
    *   Select your ESP32 board from the **Tools > Board** menu.
    *   Select the correct COM port from the **Tools > Port** menu.
    *   Click the "Upload" button.

## Code Explanation

*   **Libraries:** The code uses the Adafruit DHT and Unified Sensor libraries to interact with the DHT22 sensor.
*   **Pin Definitions:** The `DHTPIN`, `HEATER_PIN`, and `HUMIDIFIER_PIN` constants define the ESP32 pins connected to the sensor and relays.
*   **Setpoints:** The `temperatureSetpoint` and `humiditySetpoint` variables store the desired temperature and humidity levels.
*   **`setup()`:**
    *   Initializes serial communication for debugging.
    *   Initializes the DHT22 sensor.
    *   Sets the heater and humidifier control pins as outputs and initializes them to LOW (off).
*   **`loop()`:**
    *   Reads the temperature and humidity from the DHT22 sensor.
    *   If the temperature is below the setpoint, it turns the heater on; otherwise, it turns it off.
    *   If the humidity is below the setpoint, it turns the humidifier on; otherwise, it turns it off.
    *   Prints the current temperature, humidity, and the status of the heater and humidifier to the serial monitor.
