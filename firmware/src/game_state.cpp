#include "game_state.h"

GameController::GameController(
  DisplayManager& d,
  InputManager& i,
  AudioManager& a,
  NetworkManager& n
) : display(d),
    input(i),
    audio(a),
    network(n),
    currentState(STATE_INIT),
    learnerId(""),
    selectedOptionIndex(0),
    questionStartTime(0),
    wifiAttemptCount(0) {}

void GameController::begin() {
  display.showSplashScreen(FIRMWARE_VERSION);
  audio.playBootBeep();
  delay(1200);

  currentState = STATE_WIFI_CONNECTING;
  display.showWifiConnecting(++wifiAttemptCount);
}

void GameController::update() {
  network.maintainConnection();

  switch (currentState) {
    case STATE_WIFI_CONNECTING:
      if (network.isConnected()) {
        audio.setWifiLed(true);
        currentState = STATE_READY;

        // Register or load anonymous learner
        if (learnerId.length() == 0) {
          if (!network.registerAnonymousLearner(learnerId)) {
            learnerId = "mq_esp32_dev";
          }
        }
        display.showReadyScreen(learnerId.c_str());
      } else {
        audio.setWifiLed(false);
      }
      break;

    case STATE_READY:
    case STATE_WAITING_INPUT:
    case STATE_FEEDBACK:
    case STATE_SHOWING_HINT:
    case STATE_ERROR_RECOVERY: {
      ButtonEvent btn = input.checkButtons();
      if (btn != BTN_NONE) {
        audio.playClick();
        handleInput(btn);
      }
      break;
    }

    default:
      break;
  }
}

void GameController::handleInput(ButtonEvent event) {
  if (currentState == STATE_READY || currentState == STATE_FEEDBACK || currentState == STATE_ERROR_RECOVERY) {
    if (event == BTN_EVENT_SELECT) {
      fetchNextQuestion();
    }
    return;
  }

  if (currentState == STATE_SHOWING_HINT) {
    if (event == BTN_EVENT_SELECT || event == BTN_EVENT_HINT) {
      // Return to question display
      currentState = STATE_WAITING_INPUT;
      const char* optPtrs[4];
      for (int i = 0; i < currentQuestion.optionCount; i++) {
        optPtrs[i] = currentQuestion.options[i].c_str();
      }
      display.showQuestion(
        currentQuestion.questionText.c_str(),
        optPtrs,
        currentQuestion.optionCount,
        selectedOptionIndex,
        currentQuestion.difficulty
      );
    }
    return;
  }

  if (currentState == STATE_WAITING_INPUT) {
    int count = currentQuestion.optionCount > 0 ? currentQuestion.optionCount : 4;

    if (event == BTN_EVENT_UP) {
      selectedOptionIndex = (selectedOptionIndex - 1 + count) % count;
      const char* optPtrs[4];
      for (int i = 0; i < count; i++) optPtrs[i] = currentQuestion.options[i].c_str();
      display.showQuestion(currentQuestion.questionText.c_str(), optPtrs, count, selectedOptionIndex, currentQuestion.difficulty);
    } else if (event == BTN_EVENT_DOWN) {
      selectedOptionIndex = (selectedOptionIndex + 1) % count;
      const char* optPtrs[4];
      for (int i = 0; i < count; i++) optPtrs[i] = currentQuestion.options[i].c_str();
      display.showQuestion(currentQuestion.questionText.c_str(), optPtrs, count, selectedOptionIndex, currentQuestion.difficulty);
    } else if (event == BTN_EVENT_SELECT) {
      submitSelectedAnswer();
    } else if (event == BTN_EVENT_HINT) {
      requestHint();
    }
  }
}

void GameController::fetchNextQuestion() {
  currentState = STATE_FETCHING_QUESTION;
  display.showFetchingScreen();

  QuestionData q;
  if (network.fetchNextQuestion(learnerId, q)) {
    currentQuestion = q;
    selectedOptionIndex = 0;
    questionStartTime = millis();
    currentState = STATE_WAITING_INPUT;

    const char* optPtrs[4];
    for (int i = 0; i < q.optionCount; i++) {
      optPtrs[i] = q.options[i].c_str();
    }
    display.showQuestion(
      q.questionText.c_str(),
      optPtrs,
      q.optionCount,
      selectedOptionIndex,
      q.difficulty
    );
  } else {
    currentState = STATE_ERROR_RECOVERY;
    audio.playIncorrectSound();
    display.showError("Failed to fetch\nquestion. Check API.");
  }
}

void GameController::submitSelectedAnswer() {
  currentState = STATE_SUBMITTING_ANSWER;
  int responseTimeMs = (int)(millis() - questionStartTime);
  String answer = currentQuestion.options[selectedOptionIndex];

  AnswerResult result;
  if (network.submitAnswer(learnerId, currentQuestion.questionId, answer, responseTimeMs, result)) {
    currentState = STATE_FEEDBACK;
    if (result.isCorrect) {
      audio.playCorrectSound();
    } else {
      audio.playIncorrectSound();
    }
    display.showFeedback(result.isCorrect, result.correctAnswer.c_str(), result.streak);
  } else {
    currentState = STATE_ERROR_RECOVERY;
    audio.playIncorrectSound();
    display.showError("Submission failed.\nPress [SEL] retry.");
  }
}

void GameController::requestHint() {
  currentState = STATE_SHOWING_HINT;
  String hintText = "";
  if (network.fetchHint(learnerId, currentQuestion.questionId, 1, hintText)) {
    display.showHint(hintText.c_str());
  } else {
    display.showHint("Think about the operation rule!");
  }
}
