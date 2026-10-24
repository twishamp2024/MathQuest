#ifndef AUDIO_MANAGER_H
#define AUDIO_MANAGER_H

#include <Arduino.h>
#include "config.h"

class AudioManager {
public:
  AudioManager();
  void begin();

  void playTone(int frequency, int durationMs);
  void playBootBeep();
  void playClick();
  void playCorrectSound();
  void playIncorrectSound();

  void setWifiLed(bool on);
  void pulseSuccessLed(int durationMs = 800);
  void pulseErrorLed(int durationMs = 800);

private:
  void noTone();
};

#endif // AUDIO_MANAGER_H
