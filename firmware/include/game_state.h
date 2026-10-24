#ifndef GAME_STATE_H
#define GAME_STATE_H

#include <Arduino.h>
#include "config.h"
#include "display_manager.h"
#include "input_manager.h"
#include "audio_manager.h"
#include "network_manager.h"

class GameController {
public:
  GameController(
    DisplayManager& display,
    InputManager& input,
    AudioManager& audio,
    NetworkManager& network
  );

  void begin();
  void update();

private:
  DisplayManager& display;
  InputManager& input;
  AudioManager& audio;
  NetworkManager& network;

  SystemState currentState;
  String learnerId;
  QuestionData currentQuestion;
  int selectedOptionIndex;
  unsigned long questionStartTime;
  int wifiAttemptCount;

  void handleInput(ButtonEvent event);
  void fetchNextQuestion();
  void submitSelectedAnswer();
  void requestHint();
};

#endif // GAME_STATE_H
