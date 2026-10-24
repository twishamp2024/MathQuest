# MathQuest — Bill of Materials (BOM) & Budget Analysis

**Target Budget:** $\le$ ₹1,500 INR  
**Prototyping Focus:** High reliability, widely available open-source components, child-safe voltages (3.3V / 5V DC), and sustainable/recycled construction materials.

---

## 1. Component Cost Breakdown

| Item | Component Description | Quantity | Unit Price (INR) | Total (INR) | Source / Availability |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **ESP32 DevKit V1** (30-pin NodeMCU / ESP-WROOM-32) | 1 | ₹420 | ₹420 | Robu.in / Amazon / Offline Electronics Market |
| **2** | **0.96" SSD1306 OLED Display** (128x64, 4-pin I2C) | 1 | ₹195 | ₹195 | Robu.in / ElectronicsComp / Robocraze |
| **3** | **12mm Tactile Pushbuttons** (with colored round caps) | 4 | ₹10 | ₹40 | Local component vendor / Robu.in |
| **4** | **5mm Diffused LEDs** (1 Blue, 1 Green, 1 Red) | 3 | ₹3 | ₹9 | Local hobby store |
| **5** | **220Ω Resistors** (1/4W Carbon Film, Current Limiting) | 3 | ₹1 | ₹3 | Standard pack |
| **6** | **Piezo Buzzer** (5V Passive / Active Buzzer) | 1 | ₹25 | ₹25 | Standard hobby buzzer |
| **7** | **400-Point Solderless Breadboard** (or 5x7cm Dot PCB) | 1 | ₹75 | ₹75 | Electronics hobby supplier |
| **8** | **Jumper Wires** (Male-to-Male & Male-to-Female, 20cm) | 15 | ₹2 | ₹30 | Ribbon bundle |
| **9** | **Micro-USB Data & Power Cable** (1 meter) | 1 | ₹60 | ₹60 | Standard cable |
| **10**| **Toy Enclosure** (Recycled cardboard / laser-cut MDF / 3D PLA) | 1 | ₹70 | ₹70 | Recycled packaging or school makerspace |
| **—** | **Total Estimated Prototype Cost** | **—** | **—** | **₹927 INR** | **Well below ₹1,500 limit (~₹573 margin)** |

---

## 2. Component Selection Justifications

1. **ESP32 DevKit V1 over Raspberry Pi Pico W or Arduino Uno:**
   - Onboard 2.4GHz Wi-Fi + Bluetooth LE.
   - Dual-core Tensilica Xtensa 32-bit LX6 running at up to 240 MHz provides ample headroom for networking, graphics, and OTA encryption.
   - 4MB Flash memory allows dual 1.8MB OTA application partitions (`ota_0`, `ota_1`) with room for non-volatile storage (`nvs`).
   - Sells for approximately ₹400–₹450 in India, significantly cheaper than Linux SBCs.

2. **SSD1306 128x64 I2C OLED:**
   - Uses only 2 GPIO pins (GPIO 21 SDA, GPIO 22 SCL) thanks to I2C communication.
   - Consumes negligible power (pixels only draw current when lit).
   - High contrast ensures readability across various ambient lighting conditions.

3. **Active Low Pushbuttons with Internal Pullups:**
   - Eliminates the need for external pullup resistors; ESP32's built-in `INPUT_PULLUP` resistors handle stabilization.
   - Simplifies the circuit and reduces breadboard wiring complexity.

4. **Recycled / Sustainable Enclosure:**
   - Heavy-duty corrugated cardboard or 3mm MDF offcuts can be folded and slotted using common craft knives and hot glue, keeping costs minimal and encouraging hands-on assembly by students.
