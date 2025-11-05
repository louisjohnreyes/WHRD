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
DHT_PIN = board.D4 # DHT sensor data pin connected to GPIO 4
FAN_PIN_1 = 17
FAN_PIN_2 = 18
DEHUMIDIFIER_PIN_1 = 27
DEHUMIDIFIER_PIN_2 = 23
HEATER_PIN = 22
BUZZER_PIN = 24

# Button definitions
MODE_BUTTON_PIN = 5
STAGE_BUTTON_PIN = 6
FAN_BUTTON_PIN = 13
DEHUMIDIFIER_BUTTON_PIN = 19

# LED Indicator definitions
YELLOWING_LED_PIN = 16
LEAF_DRYING_LED_PIN = 20
MIDRIB_DRYING_LED_PIN = 21
ORDERING_LED_PIN = 26

AUTO_MODE_LED_PIN = 12
MANUAL_MODE_LED_PIN = 25

# =============================
# Relay configuration
# =============================
# Set this to True if your relays are active LOW (most common)
# Set to False if active HIGH
RELAY_ACTIVE_LOW = True

# =============================
# Curing stages configuration
# =============================
CURING_STAGES = {
    "YELLOWING": {"max_temp": 42.0, "humidity": 85.0},
    "LEAF_DRYING": {"max_temp": 55.0, "humidity": 70.0},
    "MIDRIB_DRYING": {"max_temp": 70.0, "humidity": 50.0},
    "ORDERING": {"temp": 25.0, "humidity": 80.0},
}

# =============================
# State variables
# =============================
current_mode = "AUTO" # "AUTO" or "MANUAL"
current_stage_index = 0
stage_start_time = 0
fan_on = False
dehumidifier_on = False
heater_on = False
buzzer_on = False
target_temperature = 0.0

# =============================
# GPIO Setup
# =============================
def setup_gpio():
    """Sets up the GPIO pins."""
    GPIO.setmode(GPIO.BCM)

    # Output pins for relays
    GPIO.setup(FAN_PIN_1, GPIO.OUT)
    GPIO.setup(FAN_PIN_2, GPIO.OUT)
    GPIO.setup(DEHUMIDIFIER_PIN_1, GPIO.OUT)
    GPIO.setup(DEHUMIDIFIER_PIN_2, GPIO.OUT)
    GPIO.setup(HEATER_PIN, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    # Output pins for LEDs
    GPIO.setup(YELLOWING_LED_PIN, GPIO.OUT)
    GPIO.setup(LEAF_DRYING_LED_PIN, GPIO.OUT)
    GPIO.setup(MIDRIB_DRYING_LED_PIN, GPIO.OUT)
    GPIO.setup(ORDERING_LED_PIN, GPIO.OUT)
    GPIO.setup(AUTO_MODE_LED_PIN, GPIO.OUT)
    GPIO.setup(MANUAL_MODE_LED_PIN, GPIO.OUT)

    # Input pins for buttons
    GPIO.setup(MODE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(STAGE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(FAN_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DEHUMIDIFIER_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Initialize all relays OFF
    relay_off(FAN_PIN_1)
    relay_off(FAN_PIN_2)
    relay_off(DEHUMIDIFIER_PIN_1)
    relay_off(DEHUMIDIFIER_PIN_2)
    relay_off(HEATER_PIN)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

    # Initialize all LEDs OFF
    GPIO.output(YELLOWING_LED_PIN, GPIO.LOW)
    GPIO.output(LEAF_DRYING_LED_PIN, GPIO.LOW)
    GPIO.output(MIDRIB_DRYING_LED_PIN, GPIO.LOW)
    GPIO.output(ORDERING_LED_PIN, GPIO.LOW)
    GPIO.output(AUTO_MODE_LED_PIN, GPIO.LOW)
    GPIO.output(MANUAL_MODE_LED_PIN, GPIO.LOW)

# =============================
# Actuator Control Functions
# =============================
def control_buzzer(buzzer_on):
    """Controls the buzzer."""
    if buzzer_on:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
    else:
        GPIO.output(BUZZER_PIN, GPIO.LOW)

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
        relay_on(DEHUMIDIFIER_PIN_1)
        relay_on(DEHUMIDIFIER_PIN_2)
    else:
        relay_off(DEHUMIDIFIER_PIN_1)
        relay_off(DEHUMIDIFIER_PIN_2)

    if fan_on:
        relay_on(FAN_PIN_1)
        relay_on(FAN_PIN_2)
    else:
        relay_off(FAN_PIN_1)
        relay_off(FAN_PIN_2)

# =============================
# LED Control Logic
# =============================
def update_leds(stage_name, mode):
    """Updates the LED indicators for stage and mode."""
    # Turn off all stage LEDs first
    GPIO.output(YELLOWING_LED_PIN, GPIO.LOW)
    GPIO.output(LEAF_DRYING_LED_PIN, GPIO.LOW)
    GPIO.output(MIDRIB_DRYING_LED_PIN, GPIO.LOW)
    GPIO.output(ORDERING_LED_PIN, GPIO.LOW)

    # Turn on the current stage LED
    if stage_name == "YELLOWING":
        GPIO.output(YELLOWING_LED_PIN, GPIO.HIGH)
    elif stage_name == "LEAF_DRYING":
        GPIO.output(LEAF_DRYING_LED_PIN, GPIO.HIGH)
    elif stage_name == "MIDRIB_DRYING":
        GPIO.output(MIDRIB_DRYING_LED_PIN, GPIO.HIGH)
    elif stage_name == "ORDERING":
        GPIO.output(ORDERING_LED_PIN, GPIO.HIGH)

    # Update mode LEDs
    if mode == "AUTO":
        GPIO.output(AUTO_MODE_LED_PIN, GPIO.HIGH)
        GPIO.output(MANUAL_MODE_LED_PIN, GPIO.LOW)
    else: # MANUAL
        GPIO.output(AUTO_MODE_LED_PIN, GPIO.LOW)
        GPIO.output(MANUAL_MODE_LED_PIN, GPIO.HIGH)

# =============================
# LCD Update Function
# =============================
def update_lcd(temp, hum, stage, mode, heater_on, fan_on, dehum_on, target_temp):
    """Formats and writes the current status to the LCD screen."""
    lcd.home()

    # Line 1: Temperature
    lcd.write_string(f"Temp: {temp:.1f}/{target_temp:.1f} C")

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
    global current_mode, current_stage_index, stage_start_time, fan_on, dehumidifier_on, heater_on, target_temperature, buzzer_on

    setup_gpio()
    dht_device = adafruit_dht.DHT22(DHT_PIN)
    stage_keys = list(CURING_STAGES.keys())
    stage_start_time = time.time()
    last_mode_press = 0
    last_stage_press = 0
    last_fan_press = 0
    last_dehumidifier_press = 0
    last_temp_increase_time = time.time()
    initial_temp_set = False

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
                initial_temp_set = False

            # Sensor reading
            try:
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                if temperature is not None and humidity is not None:
                    stage_name = stage_keys[current_stage_index]
                    setpoints = CURING_STAGES[stage_name]

                    if not initial_temp_set:
                        if stage_name in ["YELLOWING", "LEAF_DRYING", "MIDRIB_DRYING"]:
                            target_temperature = temperature
                        else:  # ORDERING
                            target_temperature = setpoints.get("temp", temperature)
                        initial_temp_set = True
                        last_temp_increase_time = time.time()

                    # Stage transition and control logic
                    if current_mode == "AUTO":
                        if stage_name in ["YELLOWING", "LEAF_DRYING", "MIDRIB_DRYING"]:
                            if time.time() - last_temp_increase_time >= 3600:  # 1 hour
                                if target_temperature < setpoints["max_temp"]:
                                    target_temperature += 1.0
                                    print(f"Increased target temperature to: {target_temperature:.1f}°C")
                                last_temp_increase_time = time.time()

                        loop_target_temperature = target_temperature
                        heater_on = temperature < loop_target_temperature
                        dehumidifier_on = humidity > setpoints["humidity"]
                        fan_on = dehumidifier_on or (stage_name == "LEAF_DRYING")
                    else:  # MANUAL mode
                        if stage_button_pressed and (time.time() - last_stage_press > 0.2):
                            last_stage_press = time.time()
                            current_stage_index = (current_stage_index + 1) % len(stage_keys)
                            stage_start_time = time.time()
                            print(f"Manually advanced to stage: {stage_keys[current_stage_index]}")
                            initial_temp_set = False

                        if fan_button_pressed and (time.time() - last_fan_press > 0.2):
                            last_fan_press = time.time()
                            fan_on = not fan_on

                        if dehumidifier_button_pressed and (time.time() - last_dehumidifier_press > 0.2):
                            last_dehumidifier_press = time.time()
                            dehumidifier_on = not dehumidifier_on

                        loop_target_temperature = setpoints.get("max_temp", setpoints.get("temp", temperature))
                        heater_on = temperature < loop_target_temperature

                    # Update relays (fan, dehumidifier, heater)
                    update_relays(heater_on, dehumidifier_on, fan_on)

                    # Update LED indicators
                    update_leds(stage_name, current_mode)

                    buzzer_on = not (loop_target_temperature - 2 <= temperature <= loop_target_temperature + 2)
                    control_buzzer(buzzer_on)

                    # Update LCD display
                    update_lcd(temperature, humidity, stage_name, current_mode, heater_on, fan_on, dehumidifier_on, loop_target_temperature)

                    # Console feedback
                    print(f"Stage: {stage_name}, Mode: {current_mode}, Temp: {temperature:.1f}°C, Hum: {humidity:.1f}%")
                    print(f"Heater: {'ON' if heater_on else 'OFF'}, Dehumidifier: {'ON' if dehumidifier_on else 'OFF'}, Fan: {'ON' if fan_on else 'OFF'}")

            except RuntimeError as error:
                print(error.args[0])

            time.sleep(2)
    finally:
        lcd.clear()
        GPIO.cleanup()

# =============================
# Entry point
# =============================
if __name__ == "__main__":
main()
