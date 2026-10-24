/**
 * MathQuest ESP32 Firmware Configuration Header.
 * Pin definitions, network settings, and timing constants.
 */

#ifndef MATHQUEST_CONFIG_H
#define MATHQUEST_CONFIG_H

#include <Arduino.h>

// Firmware versioning
#define FIRMWARE_VERSION "1.0.0"
#define HARDWARE_MODEL "esp32-devkit-v1"

// I2C OLED Display (SSD1306 128x64)
#define OLED_SDA_PIN 21
#define OLED_SCL_PIN 22
#define OLED_I2C_ADDRESS 0x3C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// Input Pushbuttons (Internal Pullups, Active LOW)
#define BTN_UP_PIN 18
#define BTN_DOWN_PIN 19
#define BTN_SELECT_PIN 23
#define BTN_HINT_PIN 5
#define BUTTON_DEBOUNCE_MS 45

// Status LEDs
#define LED_WIFI_PIN 2     // Blue LED (Wi-Fi status)
#define LED_SUCCESS_PIN 4  // Green LED (Correct answer)
#define LED_ERROR_PIN 15   // Red LED (Error / Incorrect)

// Piezo Buzzer
#define BUZZER_PIN 13
#define BUZZER_PWM_CHANNEL 0

// Wi-Fi Configuration (Wokwi-GUEST for simulator or local AP for physical)
#define DEFAULT_WIFI_SSID "Wokwi-GUEST"
#define DEFAULT_WIFI_PASS ""
#define WIFI_RECONNECT_INTERVAL_MS 5000

// Backend API Configuration
// NOTE: For Wokwi simulation on desktop, the Wokwi private gateway or host loopback is used.
// For physical devices, replace with the machine's local IP (e.g., http://192.168.1.100:8000).
#define DEFAULT_BACKEND_URL "http://host.wokwi.internal:8000/api/v1"
#define HTTP_TIMEOUT_MS 6000
#define HTTP_MAX_RETRIES 3

// Game State Definitions
enum SystemState {
  STATE_INIT,
  STATE_WIFI_CONNECTING,
  STATE_READY,
  STATE_FETCHING_QUESTION,
  STATE_WAITING_INPUT,
  STATE_SUBMITTING_ANSWER,
  STATE_FEEDBACK,
  STATE_SHOWING_HINT,
  STATE_ERROR_RECOVERY
};

enum ButtonEvent {
  BTN_NONE = 0,
  BTN_EVENT_UP,
  BTN_EVENT_DOWN,
  BTN_EVENT_SELECT,
  BTN_EVENT_HINT
};

#endif // MATHQUEST_CONFIG_H
