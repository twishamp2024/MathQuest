#ifndef DISPLAY_MANAGER_H
#define DISPLAY_MANAGER_H

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "config.h"

class DisplayManager {
public:
  DisplayManager();
  bool begin();
  void clear();
  void display();

  void showSplashScreen(const char* version);
  void showWifiConnecting(int attempt);
  void showReadyScreen(const char* learnerId);
  void showFetchingScreen();
  void showQuestion(const char* questionText, const char* options[], int optionCount, int selectedIndex, int difficulty);
  void showFeedback(bool isCorrect, const char* correctAnswer, int streak);
  void showHint(const char* hintText);
  void showError(const char* errorMessage);

private:
  Adafruit_SSD1306 oled;
  void drawStatusBar(const char* title, const char* rightText);
};

#endif // DISPLAY_MANAGER_H
