#ifndef INPUT_MANAGER_H
#define INPUT_MANAGER_H

#include <Arduino.h>
#include "config.h"

class InputManager {
public:
  InputManager();
  void begin();
  ButtonEvent checkButtons();

private:
  unsigned long lastDebounceTimeUp;
  unsigned long lastDebounceTimeDown;
  unsigned long lastDebounceTimeSelect;
  unsigned long lastDebounceTimeHint;

  int lastStateUp;
  int lastStateDown;
  int lastStateSelect;
  int lastStateHint;
};

#endif // INPUT_MANAGER_H
