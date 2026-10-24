# MathQuest — Wokwi ESP32 Simulation Guide

MathQuest provides two complementary simulation workflows so that no physical hardware is needed for development or testing:
1. **Interactive In-Browser Toy Simulator:** Integrated directly into the MathQuest web app (`http://localhost:8000`).
2. **Wokwi Microcontroller Simulator:** Simulates actual ESP32 silicon, peripherals, and C++ firmware execution.

---

## 1. Quick Start: Built-in Web Simulator (Zero Setup)

The fastest way to test the physical toy experience:
1. Start the MathQuest server:
   ```powershell
   .\scripts\start_server.ps1
   ```
2. Open your web browser to:
   ```
   http://localhost:8000
   ```
3. Click the **"📟 Virtual ESP32 Toy"** tab in the navigation bar.
4. Interact using the on-screen tactile buttons or keyboard shortcuts:
   - **Arrow Up / W:** Move cursor up
   - **Arrow Down / S:** Move cursor down
   - **Enter / Space:** Select / Submit answer
   - **H:** Request hint

---

## 2. Running the Wokwi ESP32 Firmware Project

The firmware project files are located in `firmware/`:
- `firmware/platformio.ini`: PlatformIO build specification.
- `firmware/wokwi/diagram.json`: Complete circuit diagram with ESP32, SSD1306 OLED, 4 buttons, 3 LEDs, and Buzzer.
- `firmware/wokwi/wokwi.toml`: Simulator configuration.

### Option A: Wokwi for VS Code Extension
1. Install the official **Wokwi Simulator** extension in VS Code.
2. Open the `firmware/wokwi/diagram.json` file.
3. Press `F1` and select **Wokwi: Start Simulator**.
4. The virtual ESP32 will boot, connect to simulated Wi-Fi (`Wokwi-GUEST`), and render the MathQuest OLED user interface.

### Option B: Wokwi Web Editor
1. Visit [https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32).
2. Copy the contents of `firmware/wokwi/diagram.json` into the diagram tab.
3. Paste the C++ source files from `firmware/src/` and `firmware/include/`.
4. Click **Play** to start the simulation.

---

## 3. Simulator Network Configuration

- **Simulated Wi-Fi:** Wokwi provides a built-in virtual access point called `Wokwi-GUEST` with no password, which connects through the Wokwi IoT Gateway.
- **Backend Host Resolution:**
  - Inside the Wokwi simulator, your local development machine is addressed via `http://host.wokwi.internal:8000`.
  - On physical hardware, configure your PC's LAN IP address (e.g. `http://192.168.1.50:8000`) in `firmware/include/config.h`.
