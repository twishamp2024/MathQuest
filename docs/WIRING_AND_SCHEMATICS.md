# MathQuest — Hardware Wiring & Schematics Guide

## 1. GPIO Pinout Mapping Table

| Periph / Component | Pin on Component | ESP32 Pin | Function / Notes |
| :--- | :--- | :--- | :--- |
| **SSD1306 OLED** | VCC | `3V3` | 3.3V Power rail |
| | GND | `GND` | Common Ground |
| | SCL | `GPIO 22` | I2C Clock (Hardware I2C Wire) |
| | SDA | `GPIO 21` | I2C Data (Hardware I2C Wire) |
| **UP Button (Green)** | Pin 1 | `GPIO 18` | Active LOW (`pinMode(18, INPUT_PULLUP)`) |
| | Pin 2 | `GND` | Ground |
| **DOWN Button (Green)**| Pin 1 | `GPIO 19` | Active LOW (`pinMode(19, INPUT_PULLUP)`) |
| | Pin 2 | `GND` | Ground |
| **SELECT Button (Blue)**| Pin 1 | `GPIO 23` | Active LOW (`pinMode(23, INPUT_PULLUP)`) |
| | Pin 2 | `GND` | Ground |
| **HINT Button (Yellow)**| Pin 1 | `GPIO 5` | Active LOW (`pinMode(5, INPUT_PULLUP)`) |
| | Pin 2 | `GND` | Ground |
| **Wi-Fi LED (Blue)** | Anode (+) | `GPIO 2` | Active HIGH (Onboard or External) |
| | Cathode (-) | via 220Ω to `GND` | Current limiting resistor |
| **Correct LED (Green)**| Anode (+) | `GPIO 4` | Active HIGH |
| | Cathode (-) | via 220Ω to `GND` | Current limiting resistor |
| **Error LED (Red)** | Anode (+) | `GPIO 15`| Active HIGH |
| | Cathode (-) | via 220Ω to `GND` | Current limiting resistor |
| **Piezo Buzzer** | Positive (+) | `GPIO 13`| PWM Audio Tone Channel 0 |
| | Negative (-) | `GND` | Common Ground |

---

## 2. Schematic Diagram

```
                 +-------------------+
                 |    ESP32 DEVKIT   |
                 |                   |
 (3V3 Power) ----| 3V3           GND |---- (Common Ground Rail)
                 |                   |
  (OLED SDA) ----| GPIO 21   GPIO 22 |---- (OLED SCL)
                 |                   |
    (BTN UP) ----| GPIO 18   GPIO 23 |---- (BTN SELECT)
  (BTN DOWN) ----| GPIO 19   GPIO 5  |---- (BTN HINT)
                 |                   |
  (LED BLUE) ----| GPIO 2    GPIO 4  |---- (LED GREEN)
                 |                   |
   (LED RED) ----| GPIO 15   GPIO 13 |---- (BUZZER +)
                 +-------------------+

 [Buttons connect between GPIO pin and GND. Internal pullups enabled.]
 [LEDs connect from GPIO pin -> Anode -> Cathode -> 220 Ohm resistor -> GND.]
 [Buzzer connects from GPIO 13 -> Positive terminal -> Negative terminal -> GND.]
```

---

## 3. Power Requirements & Safety Considerations

- **Operating Voltage:** 3.3V Logic. The ESP32 is powered via its 5V Micro-USB port through an onboard low-dropout voltage regulator (AMS1117-3.3 or similar).
- **Current Consumption:**
  - Active Wi-Fi transmit burst: ~180 mA – 240 mA.
  - Normal idle / display active: ~60 mA – 80 mA.
  - Can easily run off any standard 5V 1A phone charger or portable USB power bank.
- **Safety:** All external user-facing buttons and LEDs operate at safe extra-low voltage (SELV $\le 3.3\text{V}$ DC). No mains AC voltage is exposed anywhere on the physical toy.
