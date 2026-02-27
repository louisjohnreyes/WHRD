# Wiring Diagram for T90-5VDC-TL-C Relays

This document provides a detailed wiring diagram for connecting T90-5VDC-TL-C relays to a Raspberry Pi for controlling dehumidifiers and fans in the tobacco curing system.

## Components

*   Raspberry Pi 4
*   4 x T90-5VDC-TL-C Relay Modules (or similar)
*   2 x Dehumidifiers (AC powered)
*   2 x Fans (AC powered)
*   5V DC Power Supply for Raspberry Pi and Relays
*   AC Power Source for Dehumidifiers and Fans
*   Jumper Wires

## Relay Pinout

The T90-5VDC-TL-C relay has the following pinout:

*   **Coil Pins (2):** Connect to the Raspberry Pi's GPIO pins (via the relay module's control pin) and a 5V source.
*   **Common (COM):** The common terminal for the switch.
*   **Normally Open (NO):** This contact is open when the relay is not energized. The appliance will be OFF.
*   **Normally Closed (NC):** This contact is closed when the relay is not energized. The appliance will be ON.

For this application, we will use the **Normally Open (NO)** configuration, so the appliances are off by default.

## Wiring Table

| Raspberry Pi Pin | Relay Module        | Appliance      | Notes                                    |
| ---------------- | ------------------- | -------------- | ---------------------------------------- |
| 5V Power         | VCC Pin on Relays   | -              | Powers the relay coils.                  |
| Ground           | GND Pin on Relays   | -              | Common ground.                           |
| GPIO 23          | IN1 Pin on Relay 1  | Dehumidifier 1 | Controls the first dehumidifier.         |
| GPIO 24          | IN2 Pin on Relay 2  | Dehumidifier 2 | Controls the second dehumidifier.        |
| GPIO 25          | IN3 Pin on Relay 3  | Fan 1          | Controls the first fan.                  |
| GPIO 26          | IN4 Pin on Relay 4  | Fan 2          | Controls the second fan.                 |

## Wiring Diagram (ASCII Art)

```
                            +-----------------+
                            | Raspberry Pi 4  |
                            +-----------------+
                               |           |
     +-------------------------+           +--------------------------+
     | 5V Power                |           | Ground                   |
     +-------------------------+           +--------------------------+
                               |           |
+------------------------------+           +--------------------------------+
|                              |           |                                |
|    +---------------------+   |           |   +---------------------+        |
|    | VCC      IN1      GND |   |           |   | VCC      IN2      GND |        |
|    |      Relay 1      |   |           |   |      Relay 2      |        |
|    | (Dehumidifier 1)    +---+-----------o---+ (Dehumidifier 2)    |        |
|    +---------------------+   GPIO 23         +---------------------+        |
|       |           |                          |           |               |
| AC Hot--+--NO   COM--+-- Dehumidifier 1   AC Hot--+--NO   COM--+-- Dehumidifier 2|
|       |           |                          |           |               |
| AC Neu--+-----------+----------------------AC Neu--+-----------+---------------+
|                                                                                |
|    +---------------------+   +-----------o---+   +---------------------+        |
|    | VCC      IN3      GND |   | GPIO 25       |   | VCC      IN4      GND |        |
|    |      Relay 3      |   |               |   |      Relay 4      |        |
|    |      (Fan 1)      +---+---------------+---+      (Fan 2)      |        |
|    +---------------------+                       +---------------------+        |
|       |           |                              |           |               |
| AC Hot--+--NO   COM--+-- Fan 1                AC Hot--+--NO   COM--+-- Fan 2    |
|       |           |                              |           |               |
| AC Neu--+-----------+--------------------------AC Neu--+-----------+-----------+

```

## Important Notes

*   **High Voltage Warning:** The wiring for the dehumidifiers and fans involves high-voltage AC electricity. Ensure all AC power is disconnected before working on the wiring. If you are not comfortable working with high voltage, consult a qualified electrician.
*   **Relay Module:** This diagram assumes you are using relay *modules* that include the necessary driver circuitry (transistor, flyback diode). If you are using bare relays, you will need to add this circuitry.
*   **`RELAY_ACTIVE_LOW` Setting:** The `rpi4_tobacco_curing.py` script has a `RELAY_ACTIVE_LOW` setting. If your relay modules activate on a LOW signal, set this to `True`. If they activate on a HIGH signal (as is common), set this to `False`. The current script has it set to `True`.

This wiring diagram should provide a clear guide for integrating the T90 relays into your project.
