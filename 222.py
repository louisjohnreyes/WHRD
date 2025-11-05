# A Python script for controlling the tobacco curing process using a DHT22 sensor
# on a Raspberry Pi 4. The script includes both manual and automatic modes, with
# buttons for control, and follows the four stages of flue-curing for tobacco.
#
# Before running, make sure you have installed the required libraries inside your virtual environment:
# pip3 install RPi.GPIO
# pip3 install adafruit-circuitpython-dht
# pip3 install RPLCD

import RPi.GPIO as GPIO
import adafruit_dht
import time
import board
from RPLCD.i2c import CharLCD

# =============================
# LCD Configuration
# =============================
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=20, rows=4, dotsize=8)

# =============================
# Pin definitions (BCM numbering)
# =============================
DHT_PIN = board.D4  # DHT sensor data pin connected to GPIO 4
FAN_PIN = 17
DEHUMIDIFIER_PIN = 27
HEATER_PIN = 22

# Button definitions
MODE_BUTTON_PIN = 5
STAGE_BUTTON_PIN = 6
FAN_BUTTON_PIN = 13
DEHUMIDIFIER_BUTTON_PIN = 19

# =============================
# Relay configuration
# =============================
# Set this to True if your relays are active LOW (most common)
# Set to False if active HIGH
RELAY_ACTIVE_LOW = False

# =============================
# Curing stages configuration
# =============================
CURING_STAGES = {
    "YELLOWING": {"temp": 35.0, "humidity": 85.0, "duration_hours": 48},
    "LEAF_DRYING": {"temp": 46.0, "humidity": 70.0, "duration_hours": 24},
    "MIDRIB_DRYING": {"temp": 65.0, "humidity": 50.0, "duration_hours": 24},
    "ORDERING": {"temp": 25.0, "humidity": 80.0, "duration_hours": 12},
}

# =============================
# State variables
# =============================
current_mode = "AUTO"  # "AUTO" or "MANUAL"
current_stage_index = 0
stage_start_time = 0
fan_on = False
dehumidifier_on = False
heater_on = False

# =============================
# GPIO Setup
# =============================
def setup_gpio():
    """Sets up the GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.setup(DEHUMIDIFIER_PIN, GPIO.OUT)
    GPIO.setup(HEATER_PIN, GPIO.OUT)
    GPIO.setup(MODE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(STAGE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(FAN_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DEHUMIDIFIER_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Initialize all relays OFF
    relay_off(FAN_PIN)
    relay_off(DEHUMIDIFIER_PIN)
    relay_off(HEATER_PIN)

# =============================
# Relay Control Functions
# =============================
def relay_on(pin):
    """Turns ON the relay depending on the relay logic type."""
    if RELAY_ACTIVE_LOW:
        GPIO.output(pin, GPIO.LOW)
    else:
        GPIO.output(pin, GPIO.HIGH)

def relay_off(pin):
    """Turns OFF the relay depending on the relay logic type."""
    if RELAY_ACTIVE_LOW:
        GPIO.output(pin, GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.LOW)

def update_relays(heater_on, dehumidifier_on, fan_on):
    """Updates all relay states."""
    if heater_on:
        relay_on(HEATER_PIN)
    else:
        relay_off(HEATER_PIN)

    if dehumidifier_on:
        relay_on(DEHUMIDIFIER_PIN)
    else:
        relay_off(DEHUMIDIFIER_PIN)

    if fan_on:
        relay_on(FAN_PIN)
    else:
        relay_off(FAN_PIN)

# =============================
# LCD Update Function
# =============================
def update_lcd(temp, hum, stage, mode, heater_on, fan_on, dehum_on):
    """Formats and writes the current status to the LCD screen."""
    lcd.home()
    
    # Line 1: Temperature
    lcd.write_string(f"Temp: {temp:.1f} C")
    
    # Line 2: Humidity
    lcd.crlf()
    lcd.write_string(f"Humidity: {hum:.1f} %")

    # Line 3: Stage and Mode
    lcd.crlf()
    lcd.write_string(f"Stage: {stage}")
    lcd.cursor_pos = (2, 14)
    lcd.write_string(f"M:{mode[:3]}")

    # Line 4: Actuator Status
    lcd.crlf()
    heater_str = "H" if heater_on else "-"
    fan_str = "F" if fan_on else "-"
    dehum_str = "D" if dehum_on else "-"
    lcd.write_string(f"Status: {heater_str}{fan_str}{dehum_str}")

# =============================
# Main Control Loop
# =============================
def main():
    """Main loop for the tobacco curing controller."""
    global current_mode, current_stage_index, stage_start_time, fan_on, dehumidifier_on, heater_on

    setup_gpio()
    dht_device = adafruit_dht.DHT22(DHT_PIN)
    stage_keys = list(CURING_STAGES.keys())
    stage_start_time = time.time()
    last_mode_press = 0
    last_stage_press = 0
    last_fan_press = 0
    last_dehumidifier_press = 0

    try:
        lcd.clear()
        while True:
            # Button reading
            mode_button_pressed = not GPIO.input(MODE_BUTTON_PIN)
            stage_button_pressed = not GPIO.input(STAGE_BUTTON_PIN)
            fan_button_pressed = not GPIO.input(FAN_BUTTON_PIN)
            dehumidifier_button_pressed = not GPIO.input(DEHUMIDIFIER_BUTTON_PIN)

            # Mode switching
            if mode_button_pressed and (time.time() - last_mode_press > 0.2):
                last_mode_press = time.time()
                current_mode = "MANUAL" if current_mode == "AUTO" else "AUTO"
                print(f"Switched to {current_mode} mode")

            # Sensor reading
            try:
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                if temperature is not None and humidity is not None:
                    stage_name = stage_keys[current_stage_index]
                    setpoints = CURING_STAGES[stage_name]

                    # Stage transition and control logic
                    if current_mode == "AUTO":
                        stage_duration_seconds = setpoints["duration_hours"] * 3600
                        if time.time() - stage_start_time > stage_duration_seconds:
                            current_stage_index = (current_stage_index + 1) % len(stage_keys)
                            stage_start_time = time.time()
                            print(f"Auto-advancing to stage: {stage_keys[current_stage_index]}")
                        
                        heater_on = temperature < setpoints["temp"]
                        dehumidifier_on = humidity > setpoints["humidity"]
                        fan_on = dehumidifier_on or (stage_name == "LEAF_DRYING")
                    else:  # MANUAL mode
                        if stage_button_pressed and (time.time() - last_stage_press > 0.2):
                            last_stage_press = time.time()
                            current_stage_index = (current_stage_index + 1) % len(stage_keys)
                            stage_start_time = time.time()
                            print(f"Manually advanced to stage: {stage_keys[current_stage_index]}")
                        
                        if fan_button_pressed and (time.time() - last_fan_press > 0.2):
                            last_fan_press = time.time()
                            fan_on = not fan_on
                        
                        if dehumidifier_button_pressed and (time.time() - last_dehumidifier_press > 0.2):
                            last_dehumidifier_press = time.time()
                            dehumidifier_on = not dehumidifier_on
                        
                        heater_on = temperature < setpoints["temp"]

                    # Update relays (fan, dehumidifier, heater)
                    update_relays(heater_on, dehumidifier_on, fan_on)

                    # Update LCD display
                    update_lcd(temperature, humidity, stage_name, current_mode, heater_on, fan_on, dehumidifier_on)

                    # Console feedback
                    print(f"Stage: {stage_name}, Mode: {current_mode}, Temp: {temperature:.1f}°C, Hum: {humidity:.1f}%")
                    print(f"Heater: {'ON' if heater_on else 'OFF'}, Dehumidifier: {'ON' if dehumidifier_on else 'OFF'}, Fan: {'ON' if fan_on else 'OFF'}")

            except RuntimeError as error:
                print(error.args[0])
            
            time.sleep(0.5)
    finally:
        lcd.clear()
        GPIO.cleanup()

# =============================
# Entry point
# =============================
if __name__ == "__main__":
    main()

