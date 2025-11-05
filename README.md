# Raspberry Pi Tobacco Curing Controller

This Python script automates the tobacco curing process using a Raspberry Pi 4, a DHT22 temperature and humidity sensor, and an I2C LCD display. It provides both automatic and manual control over the curing environment, following the four standard stages of flue-curing for tobacco.

## Features

- **Automatic and Manual Modes:** Switch between fully automated curing cycles and manual control of individual components.
- **Four Curing Stages:** The script is pre-programmed with the temperature, humidity, and duration for the four stages of flue-curing:
    1. Yellowing
    2. Leaf Drying
    3. Midrib Drying
    4. Ordering
- **LCD Display:** A 20x4 I2C LCD displays the current temperature, humidity, curing stage, mode, and the status of the heater, fan, and dehumidifier.
- **Button Controls:** Buttons are used to switch between modes, advance the curing stage in manual mode, and control the fan and dehumidifier in manual mode.
- **Relay Control:** The script controls a heater, fan, and dehumidifier via relays.

## Required Hardware

- Raspberry Pi 4
- DHT22 temperature and humidity sensor
- 20x4 I2C LCD display (with PCF8574 expander)
- Relays for controlling the heater, fan, and dehumidifier
- Push buttons for user input
- Jumper wires and a breadboard for connections

## Setup and Installation

1.  **Enable I2C:** On your Raspberry Pi, run `sudo raspi-config`, go to "Interfacing Options," and enable I2C.
2.  **Install Dependencies:**
    ```bash
    pip3 install RPi.GPIO adafruit-circuitpython-dht RPLCD
    ```
3.  **Connections:**
    - Connect the DHT22 sensor to GPIO 4.
    - Connect the I2C LCD to the I2C pins on the Raspberry Pi (SDA and SCL).
    - Connect the relays for the fan, dehumidifier, and heater to GPIO 17, 27, and 22, respectively.
    - Connect the buttons for mode, stage, fan, and dehumidifier to GPIO 5, 6, 13, and 19, respectively.

## Usage

Run the script from your terminal:

```bash
python3 rpi4_tobacco_curing.py
```

The script will start in automatic mode and begin the curing process. You can switch to manual mode at any time using the mode button.

## Pinout (BCM Numbering)

| Component           | GPIO Pin |
| ------------------- | -------- |
| DHT22 Sensor        | 4        |
| Fan Relay           | 17       |
| Dehumidifier Relay  | 27       |
| Heater Relay        | 22       |
| Mode Button         | 5        |
| Stage Button        | 6        |
| Fan Button          | 13       |
| Dehumidifier Button | 19       |
