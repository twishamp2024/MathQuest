#include "display_manager.h"

DisplayManager::DisplayManager()
  : oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1) {}

bool DisplayManager::begin() {
  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  if (!oled.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS)) {
    return false;
  }
  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);
  oled.display();
  return true;
}

void DisplayManager::clear() {
  oled.clearDisplay();
}

void DisplayManager::display() {
  oled.display();
}

void DisplayManager::drawStatusBar(const char* title, const char* rightText) {
  oled.setTextSize(1);
  oled.setTextColor(SSD1306_WHITE);
  oled.setCursor(0, 0);
  oled.print(title);

  int rightLen = strlen(rightText);
  oled.setCursor(SCREEN_WIDTH - (rightLen * 6), 0);
  oled.print(rightText);

  oled.drawLine(0, 9, SCREEN_WIDTH, 9, SSD1306_WHITE);
}

void DisplayManager::showSplashScreen(const char* version) {
  oled.clearDisplay();
  drawStatusBar("MATHQUEST", "V1.0");

  oled.setTextSize(2);
  oled.setCursor(10, 20);
  oled.print("MATHQUEST");

  oled.setTextSize(1);
  oled.setCursor(14, 44);
  oled.print("Adaptive AI Toy");

  oled.setCursor(30, 55);
  oled.print("Booting...");
  oled.display();
}

void DisplayManager::showWifiConnecting(int attempt) {
  oled.clearDisplay();
  drawStatusBar("CONNECTING", "WIFI");

  oled.setTextSize(1);
  oled.setCursor(4, 24);
  oled.print("Joining Network...");

  oled.setCursor(4, 40);
  oled.printf("Attempt #%d", attempt);

  oled.setCursor(4, 52);
  oled.print("SSID: " DEFAULT_WIFI_SSID);
  oled.display();
}

void DisplayManager::showReadyScreen(const char* learnerId) {
  oled.clearDisplay();
  drawStatusBar("MATHQUEST", "ONLINE");

  oled.setTextSize(1);
  oled.setCursor(4, 18);
  oled.print("Connected & Ready!");

  oled.setCursor(4, 32);
  oled.printf("User: %.10s", learnerId ? learnerId : "Guest");

  oled.setCursor(4, 48);
  oled.print("Press [SEL] to play");
  oled.display();
}

void DisplayManager::showFetchingScreen() {
  oled.clearDisplay();
  drawStatusBar("FETCHING", "AI");

  oled.setTextSize(1);
  oled.setCursor(10, 26);
  oled.print("Loading next");
  oled.setCursor(10, 38);
  oled.print("adaptive challenge...");
  oled.display();
}

void DisplayManager::showQuestion(
  const char* questionText,
  const char* options[],
  int optionCount,
  int selectedIndex,
  int difficulty
) {
  oled.clearDisplay();
  char diffBuf[12];
  snprintf(diffBuf, sizeof(diffBuf), "D%d/5", difficulty);
  drawStatusBar("QUESTION", diffBuf);

  // Question Prompt (up to 2 lines)
  oled.setTextSize(1);
  oled.setCursor(0, 12);
  oled.print(questionText);

  // Render 4 options in 2x2 grid or vertical list
  int startY = 32;
  for (int i = 0; i < optionCount && i < 4; i++) {
    int y = startY + (i * 8);
    bool isSel = (i == selectedIndex);

    if (isSel) {
      oled.fillRect(0, y - 1, SCREEN_WIDTH, 8, SSD1306_WHITE);
      oled.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
      oled.setCursor(2, y);
      oled.printf("> %s", options[i]);
    } else {
      oled.setTextColor(SSD1306_WHITE);
      oled.setCursor(2, y);
      oled.printf("  %s", options[i]);
    }
  }

  oled.display();
}

void DisplayManager::showFeedback(bool isCorrect, const char* correctAnswer, int streak) {
  oled.clearDisplay();
  if (isCorrect) {
    drawStatusBar("CORRECT!", "GREAT!");
    oled.setTextSize(2);
    oled.setCursor(14, 18);
    oled.print("EXCELLENT!");

    oled.setTextSize(1);
    oled.setCursor(14, 40);
    oled.printf("Streak: %d in a row", streak);

    oled.setCursor(14, 52);
    oled.print("Press [SEL] Next");
  } else {
    drawStatusBar("REVIEW", "TRY AGAIN");
    oled.setTextSize(1);
    oled.setCursor(4, 18);
    oled.print("Not quite!");

    oled.setCursor(4, 32);
    oled.printf("Correct: %s", correctAnswer);

    oled.setCursor(4, 50);
    oled.print("Press [SEL] to continue");
  }
  oled.display();
}

void DisplayManager::showHint(const char* hintText) {
  oled.clearDisplay();
  drawStatusBar("HINT", "HELP");

  oled.setTextSize(1);
  oled.setCursor(0, 16);
  oled.print(hintText);

  oled.setCursor(0, 54);
  oled.print("[SEL] Back to question");
  oled.display();
}

void DisplayManager::showError(const char* errorMessage) {
  oled.clearDisplay();
  drawStatusBar("ERROR", "WARN");

  oled.setTextSize(1);
  oled.setCursor(0, 20);
  oled.print(errorMessage);

  oled.setCursor(0, 50);
  oled.print("Press [SEL] to retry");
  oled.display();
}
