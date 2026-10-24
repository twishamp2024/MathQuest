#ifndef NETWORK_MANAGER_H
#define NETWORK_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

struct QuestionData {
  String questionId;
  String topicTitle;
  String conceptTitle;
  int difficulty;
  String questionText;
  String options[4];
  int optionCount;
  bool valid;
};

struct AnswerResult {
  bool isCorrect;
  String correctAnswer;
  int streak;
  String feedbackMessage;
  bool valid;
};

class NetworkManager {
public:
  NetworkManager();
  bool begin(const char* ssid = DEFAULT_WIFI_SSID, const char* pass = DEFAULT_WIFI_PASS);
  bool isConnected();
  void maintainConnection();

  bool registerAnonymousLearner(String& outLearnerId);
  bool fetchNextQuestion(const String& learnerId, QuestionData& outQuestion);
  bool submitAnswer(const String& learnerId, const String& questionId, const String& answer, int responseTimeMs, AnswerResult& outResult);
  bool fetchHint(const String& learnerId, const String& questionId, int level, String& outHintText);

private:
  const char* wifiSsid;
  const char* wifiPass;
  unsigned long lastReconnectAttempt;
  String backendBaseUrl;

  String httpGet(const String& url);
  String httpPost(const String& url, const String& jsonBody);
};

#endif // NETWORK_MANAGER_H
