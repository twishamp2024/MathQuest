# MathQuest: Adaptive AI-Based Educational Toy

[![Tests](https://img.shields.io/badge/Tests-34%20Passed-brightgreen)](file:///f:/Antigravity/MathQuest/backend/tests)
[![Coverage](https://img.shields.io/badge/Coverage-89%25-green)](file:///f:/Antigravity/MathQuest/docs/IMPLEMENTATION_STATUS.md)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Target Budget](https://img.shields.io/badge/Prototype%20BOM-%E2%89%A4%20%E2%82%B91%2C500%20INR-orange)](docs/HARDWARE_BOM.md)

**MathQuest** is an interactive, low-cost mathematics learning product designed for children aged approximately 8–14.

Unlike conventional quiz software that presents identical static problems to every child, MathQuest maintains a **zero-PII anonymous learning profile** and adapts every problem in real time based on demonstrated conceptual mastery, response times, and detected misconceptions.

The project features a **software-first, fully runnable stack** comprising:
- A high-performance **FastAPI REST backend** with SQLite persistence.
- A **Deterministic Adaptive Learning Engine** enforcing a 10-domain curriculum DAG.
- A **Dual Question Generation Engine** (AI-assisted with guaranteed offline fallback).
- A child-facing **Responsive Web Adventure Game** with synthesized Web Audio sound.
- An interactive **Virtual ESP32 Toy Simulator** emulating a 128x64 OLED display, tactile pushbuttons, status LEDs, and a piezo buzzer.
- Complete **ESP32 C++/Arduino firmware** with Wokwi simulation project files.
- An **Over-The-Air (OTA) and Content Update architecture**.

---

## Architecture Overview

```
                      +---------------------------------------+
                      |           Interaction Layer           |
                      |  - Web Adventure Game (Desktop/Mobile)|
                      |  - Virtual ESP32 Toy Simulator (Web)  |
                      |  - Physical ESP32 Hardware Prototype  |
                      +-------------------+-------------------+
                                          |
                                   HTTP / JSON REST
                                          |
                                          v
                      +---------------------------------------+
                      |         FastAPI REST Gateway          |
                      |        /api/v1 (CORS, Security)       |
                      +-------------------+-------------------+
                                          |
                  +-----------------------+-----------------------+
                  |                                               |
                  v                                               v
    +---------------------------+                   +---------------------------+
    |   Deterministic Engine    |                   |   Question Generation     |
    | - Zone of Proximal Dev.   |                   | - Google Gemini AI        |
    | - Prerequisite DAG Tree   |                   | - Verified Offline Bank   |
    | - EWMA Mastery Tracking   |                   | - Math Validator          |
    | - Misconception Detection |                   | - 3-Tier Progressive Hint |
    +-------------+-------------+                   +-------------+-------------+
                  |                                               |
                  +-----------------------+-----------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |       SQLite Persistence Layer        |
                      |  - Anonymous Profiles (Zero PII)      |
                      |  - Mastery Logs & Hysteresis Records  |
                      |  - Versioned OTA Release Manifests    |
                      +---------------------------------------+
```

---

## 10-Domain Primary Mathematics Curriculum

MathQuest models mathematical fluency across 10 interconnected domains:
1. **Addition & Subtraction:** Single-digit recall, multi-digit regrouping, directed negative integers.
2. **Multiplication & Division:** Times tables (2–12), division facts, multi-digit factors, PEMDAS order of operations.
3. **Fractions & Equivalent Fractions:** Part-whole visual concepts, simplifying fractions.
4. **Comparing & Ordering Fractions:** Like and unlike denominators, cross-multiplication.
5. **Fraction Operations:** Common denominators, like and unlike fraction arithmetic.
6. **Decimals & Percentages:** Place value (tenths, hundredths), decimal arithmetic, percentage conversions.
7. **Ratios & Proportions:** Ratio representation, unitary method, proportional scaling.
8. **Basic Algebra:** Missing numbers, one-step equations, two-step balancing.
9. **Geometry & Measurement:** 2D perimeter, rectangle/triangle area, interior triangle angles.
10. **Number Patterns & Logic:** Arithmetic sequences, geometric multiplicative progressions.

---

## Quick Start (Run Locally)

### Prerequisites
- Python 3.10+ (Tested on Python 3.14 on Windows 10/11)
- Git

### 1. Start the Server (Windows PowerShell)
```powershell
.\scripts\start_server.ps1
```

### 2. Start the Server (Linux / macOS)
```bash
chmod +x scripts/start_server.sh
./scripts/start_server.sh
```

### 3. Open in Browser
- **Play the Web Game & Virtual ESP32 Toy:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Probe:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Running Automated Tests

Execute the automated test suite with coverage reporting:
```powershell
.\scripts\run_tests.ps1
```
Or directly with pytest:
```bash
pytest -v backend/tests
```

**Verification Results:**
- 34 passing automated tests in < 1 second.
- 89% total code coverage across all core modules.
- Multi-learner divergence tests prove that learners with differing performance histories receive distinct, personalized question paths and difficulty adjustments.

---

## Virtual ESP32 Toy Simulator

You do not need to purchase physical hardware to experience MathQuest.
1. Open [http://localhost:8000](http://localhost:8000).
2. Click the **"📟 Virtual ESP32 Toy"** tab.
3. Experience the full toy lifecycle:
   - SSD1306 128x64 OLED pixel display emulation.
   - Status LEDs: Blue (Wi-Fi), Green (Correct Answer), Red (Error Buzz).
   - Audio synthesized directly in-browser using the Web Audio API.
   - Keyboard navigation: **Arrow Up / Down** to navigate options, **Enter** to submit, **H** for hints.

---

## Physical Hardware Prototype (BOM $\le$ ₹1,500 INR)

For physical hardware builds, the prototype uses low-cost, off-the-shelf components:

| Component | Specification | Estimated Cost (INR) |
| :--- | :--- | :---: |
| Microcontroller | ESP32 DevKit V1 (30-pin, 4MB Flash) | ₹420 |
| Display | 0.96" SSD1306 128x64 I2C OLED (4-pin) | ₹195 |
| Buttons | 4x 12mm Tactile Pushbuttons (UP, DOWN, SELECT, HINT) | ₹40 |
| LEDs | 3x 5mm Diffused (Blue, Green, Red) + 220Ω Resistors | ₹12 |
| Audio | 5V Piezo Buzzer | ₹25 |
| Assembly | 400-Point Breadboard + Jumper Wires + USB Cable | ₹165 |
| Enclosure | Recycled corrugated cardboard / 3mm MDF craft casing | ₹70 |
| **Total Prototype Cost** | | **₹927 INR** |

*See [docs/HARDWARE_BOM.md](docs/HARDWARE_BOM.md) and [docs/WIRING_AND_SCHEMATICS.md](docs/WIRING_AND_SCHEMATICS.md) for pinout details and wiring diagrams.*

---

## Configuring Optional External AI (Google Gemini)

MathQuest runs fully offline by default using its verified deterministic question generator. To enable dynamic generative questions via Google Gemini:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Configure your Gemini API key:
   ```ini
   MATHQUEST_AI_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
3. If the external API times out or is unreachable, the system automatically falls back to the deterministic offline generator with zero user interruption.

---

## Detailed Documentation Directory

- [docs/PROJECT_AUDIT.md](docs/PROJECT_AUDIT.md): Initial audit and environment inventory.
- [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md): Current milestone status and verification results.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Full system architecture, diagrams, and component interactions.
- [docs/CURRICULUM_AND_ADAPTIVE_ENGINE.md](docs/CURRICULUM_AND_ADAPTIVE_ENGINE.md): Mathematical curriculum DAG and EWMA formulas.
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md): REST API reference guide.
- [docs/HARDWARE_BOM.md](docs/HARDWARE_BOM.md): Complete Bill of Materials and budget breakdown.
- [docs/WIRING_AND_SCHEMATICS.md](docs/WIRING_AND_SCHEMATICS.md): Hardware schematics and wiring tables.
- [docs/WOKWI_SIMULATION.md](docs/WOKWI_SIMULATION.md): Step-by-step Wokwi simulation guide.
- [docs/OTA_UPDATE_SPEC.md](docs/OTA_UPDATE_SPEC.md): Dual-partition OTA update specification.
- [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md): Zero-PII children's privacy architecture.
