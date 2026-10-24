#include "input_manager.h"

InputManager::InputManager()
  : lastDebounceTimeUp(0),
    lastDebounceTimeDown(0),
    lastDebounceTimeSelect(0),
    lastDebounceTimeHint(0),
    lastStateUp(HIGH),
    lastStateDown(HIGH),
    lastStateSelect(HIGH),
    lastStateHint(HIGH) {}

void InputManager::begin() {
  pinMode(BTN_UP_PIN, INPUT_PULLUP);
  pinMode(BTN_DOWN_PIN, INPUT_PULLUP);
  pinMode(BTN_SELECT_PIN, INPUT_PULLUP);
  pinMode(BTN_HINT_PIN, INPUT_PULLUP);
}

ButtonEvent InputManager::checkButtons() {
  unsigned long now = millis();

  // UP Button
  int readingUp = digitalRead(BTN_UP_PIN);
  if (readingUp != lastStateUp) {
    if ((now - lastDebounceTimeUp) > BUTTON_DEBOUNCE_MS) {
      lastDebounceTimeUp = now;
      lastStateUp = readingUp;
      if (readingUp == LOW) return BTN_EVENT_UP;
    }
  }

  // DOWN Button
  int readingDown = digitalRead(BTN_DOWN_PIN);
  if (readingDown != lastStateDown) {
    if ((now - lastDebounceTimeDown) > BUTTON_DEBOUNCE_MS) {
      lastDebounceTimeDown = now;
      lastStateDown = readingDown;
      if (readingDown == LOW) return BTN_EVENT_DOWN;
    }
  }

  // SELECT Button
  int readingSelect = digitalRead(BTN_SELECT_PIN);
  if (readingSelect != lastStateSelect) {
    if ((now - lastDebounceTimeSelect) > BUTTON_DEBOUNCE_MS) {
      lastDebounceTimeSelect = now;
      lastStateSelect = readingSelect;
      if (readingSelect == LOW) return BTN_EVENT_SELECT;
    }
  }

  // HINT Button
  int readingHint = digitalRead(BTN_HINT_PIN);
  if (readingHint != lastStateHint) {
    if ((now - lastDebounceTimeHint) > BUTTON_DEBOUNCE_MS) {
      lastDebounceTimeHint = now;
      lastStateHint = readingHint;
      if (readingHint == LOW) return BTN_EVENT_HINT;
    }
  }

  return BTN_NONE;
}
