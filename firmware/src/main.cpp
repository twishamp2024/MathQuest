/**
 * MathQuest ESP32 Firmware Entry Point.
 */

#include <Arduino.h>
#include "config.h"
#include "display_manager.h"
#include "input_manager.h"
#include "audio_manager.h"
#include "network_manager.h"
#include "game_state.h"

// Hardware Singletons
DisplayManager displayMgr;
InputManager inputMgr;
AudioManager audioMgr;
NetworkManager networkMgr;
GameController gameCtrl(displayMgr, inputMgr, audioMgr, networkMgr);

void setup() {
  Serial.begin(115200);
  Serial.println("\n==========================================");
  Serial.println("  MathQuest: Adaptive AI Educational Toy  ");
  Serial.println("  ESP32 Firmware v" FIRMWARE_VERSION);
  Serial.println("==========================================");

  // Initialize display
  if (!displayMgr.begin()) {
    Serial.println("ERROR: SSD1306 OLED initialization failed!");
  }

  // Initialize I/O
  inputMgr.begin();
  audioMgr.begin();

  // Begin network and game state
  networkMgr.begin();
  gameCtrl.begin();
}

void loop() {
  gameCtrl.update();
  delay(10); // Small cooperative yield for ESP32 FreeRTOS watchdog
}
