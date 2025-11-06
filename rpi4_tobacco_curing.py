# A Python script for controlling the tobacco curing process using a DHT22 sensor
# on a Raspberry Pi 4. The script includes both manual and automatic modes, with
# buttons for control, and follows the four stages of flue-curing for tobacco.
#
# Before running, make sure you have installed the required libraries inside your virtual environment:
# pip3 install RPi.GPIO
# pip3 install adafruit-circuitpython-dht
# pip3 install RPLCD

try:
    import RPi.GPIO as GPIO
    import board
    import adafruit_dht
    from RPLCD.i2c import CharLCD
except (RuntimeError, ImportError):
    import mock_gpio as GPIO
    import mock_board as board
    import mock_adafruit_dht as adafruit_dht
    from mock_rplcd import CharLCD
import time
import threading
import csv
import os
from flask import Flask, jsonify, render_template_string

# =============================
# Flask App Initialization
# =============================
app = Flask(__name__)

# =============================
# Web Server Routes
# =============================
@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the current status of the curing process."""
    min_temp = target_temperature - 2
    max_temp = target_temperature + 2
    status = {
        "mode": current_mode,
        "stage": list(CURING_STAGES.keys())[current_stage_index],
        "temperature": temperature,
        "humidity": humidity,
        "target_temperature": target_temperature,
        "min_temp": min_temp,
        "max_temp": max_temp,
        "heater_on": heater_on,
        "fan_on": fan_on,
        "dehumidifier_on": dehumidifier_on,
        "buzzer_on": buzzer_on
    }
    return jsonify(status)

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Sets the curing mode."""
    global current_mode
    current_mode = "MANUAL" if current_mode == "AUTO" else "AUTO"
    return jsonify({"mode": current_mode})

@app.route('/api/stage', methods=['POST'])
def set_stage():
    """Sets the curing stage."""
    global current_stage_index
    current_stage_index = (current_stage_index + 1) % len(list(CURING_STAGES.keys()))
    return jsonify({"stage": list(CURING_STAGES.keys())[current_stage_index]})

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tobacco Curing Control</title>
            <style>
                body { font-family: sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .status { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
                .status-item { padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
                .controls { margin-top: 20px; }
                .controls button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Tobacco Curing Control</h1>
                <div class="status">
                    <div class="status-item"><strong>Mode:</strong> <span id="mode"></span></div>
                    <div class="status-item"><strong>Stage:</strong> <span id="stage"></span></div>
                    <div class="status-item"><strong>Temperature:</strong> <span id="temperature"></span> &deg;C</div>
                    <div class="status-item"><strong>Humidity:</strong> <span id="humidity"></span> %</div>
                    <div class="status-item"><strong>Min Temp:</strong> <span id="min_temp"></span> &deg;C</div>
                    <div class="status-item"><strong>Max Temp:</strong> <span id="max_temp"></span> &deg;C</div>
                    <div class="status-item"><strong>Heater:</strong> <span id="heater_on"></span></div>
                    <div class="status-item"><strong>Fan:</strong> <span id="fan_on"></span></div>
                    <div class="status-item"><strong>Dehumidifier:</strong> <span id="dehumidifier_on"></span></div>
                    <div class="status-item"><strong>Buzzer:</strong> <span id="buzzer_on"></span></div>
                </div>
                <div class="controls">
                    <button id="toggle-mode">Toggle Mode</button>
                    <button id="next-stage">Next Stage</button>
                </div>
            </div>
            <script>
                function updateStatus() {
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('mode').textContent = data.mode;
                            document.getElementById('stage').textContent = data.stage;
                            document.getElementById('temperature').textContent = data.temperature.toFixed(1);
                            document.getElementById('humidity').textContent = data.humidity.toFixed(1);
                            document.getElementById('min_temp').textContent = data.min_temp.toFixed(1);
                            document.getElementById('max_temp').textContent = data.max_temp.toFixed(1);
                            document.getElementById('heater_on').textContent = data.heater_on ? 'ON' : 'OFF';
                            document.getElementById('fan_on').textContent = data.fan_on ? 'ON' : 'OFF';
                            document.getElementById('dehumidifier_on').textContent = data.dehumidifier_on ? 'ON' : 'OFF';
                            document.getElementById('buzzer_on').textContent = data.buzzer_on ? 'ON' : 'OFF';
                        });
                }

                document.getElementById('toggle-mode').addEventListener('click', () => {
                    fetch('/api/mode', { method: 'POST' })
                        .then(() => updateStatus());
                });

                document.getElementById('next-stage').addEventListener('click', () => {
                    fetch('/api/stage', { method: 'POST' })
                        .then(() => updateStatus());
                });

                setInterval(updateStatus, 2000);
                updateStatus();
            </script>
        </body>
        </html>
        """
    )

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
temperature = 0.0
humidity = 0.0

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
def update_lcd(temp, hum, stage, mode, heater_on, fan_on, dehum_on, min_temp, max_temp):
    """Formats and writes the current status to the LCD screen."""
    lcd.home()

    # Line 1: Temperature
    lcd.write_string(f"Temp:{temp:.1f} R:{min_temp:.1f}-{max_temp:.1f}")

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
# Data Logging
# =============================
def log_data(timestamp, temp, hum, stage, mode, heater_on, fan_on, dehum_on, alarm_on):
    """Logs the current state to a CSV file."""
    log_file = 'curing_log.csv'
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'temperature', 'humidity', 'stage', 'mode', 'heater_on', 'fan_on', 'dehumidifier_on', 'alarm_on']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'timestamp': timestamp,
            'temperature': temp,
            'humidity': hum,
            'stage': stage,
            'mode': mode,
            'heater_on': heater_on,
            'fan_on': fan_on,
            'dehumidifier_on': dehum_on,
            'alarm_on': alarm_on
        })

def handle_sensor_failure():
    """Handles DHT22 sensor failure by shutting down actuators and displaying an error."""
    global heater_on, fan_on, dehumidifier_on, buzzer_on

    print("DHT22 sensor error. Turning off actuators.")

    # Turn off all actuators for safety
    heater_on = False
    fan_on = False
    dehumidifier_on = False
    update_relays(heater_on, dehumidifier_on, fan_on)

    # Turn off buzzer
    buzzer_on = False
    control_buzzer(buzzer_on)

    # Display error message on LCD
    lcd.clear()
    lcd.write_string("Sensor Error!")
    lcd.crlf()
    lcd.write_string("Check DHT22 wiring.")

    # Log the failure
    log_data(time.time(), -1, -1, "SENSOR_ERROR", current_mode, False, False, False, False)

# =============================
# Main Control Loop
# =============================
def main():
    """Main loop for the tobacco curing controller."""
    global current_mode, current_stage_index, stage_start_time, fan_on, dehumidifier_on, heater_on, target_temperature, buzzer_on, temperature, humidity

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
                if temperature is None or humidity is None:
                    handle_sensor_failure()
                    time.sleep(5)  # Wait before retrying
                    continue

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

                    min_temp = loop_target_temperature - 2
                    max_temp = loop_target_temperature + 2
                    buzzer_on = not (min_temp <= temperature <= max_temp)
                    control_buzzer(buzzer_on)

                    # Update LCD display
                    update_lcd(temperature, humidity, stage_name, current_mode, heater_on, fan_on, dehumidifier_on, min_temp, max_temp)

                    # Console feedback
                    print(f"Stage: {stage_name}, Mode: {current_mode}, Temp: {temperature:.1f}°C, Hum: {humidity:.1f}%")
                    print(f"Heater: {'ON' if heater_on else 'OFF'}, Dehumidifier: {'ON' if dehumidifier_on else 'OFF'}, Fan: {'ON' if fan_on else 'OFF'}")

                    # Log data
                    log_data(time.time(), temperature, humidity, stage_name, current_mode, heater_on, fan_on, dehumidifier_on, buzzer_on)

            except RuntimeError as error:
                print(error.args[0])
                handle_sensor_failure()

            time.sleep(2)
    finally:
        lcd.clear()
        GPIO.cleanup()

# =============================
# Entry point
# =============================
if __name__ == "__main__":
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    flask_thread.daemon = True
    flask_thread.start()

main()
