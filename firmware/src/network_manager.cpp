#include "network_manager.h"

NetworkManager::NetworkManager()
  : wifiSsid(DEFAULT_WIFI_SSID),
    wifiPass(DEFAULT_WIFI_PASS),
    lastReconnectAttempt(0),
    backendBaseUrl(DEFAULT_BACKEND_URL) {}

bool NetworkManager::begin(const char* ssid, const char* pass) {
  wifiSsid = ssid;
  wifiPass = pass;
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSsid, wifiPass);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(400);
    attempts++;
  }

  return (WiFi.status() == WL_CONNECTED);
}

bool NetworkManager::isConnected() {
  return (WiFi.status() == WL_CONNECTED);
}

void NetworkManager::maintainConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    unsigned long now = millis();
    if (now - lastReconnectAttempt > WIFI_RECONNECT_INTERVAL_MS) {
      lastReconnectAttempt = now;
      WiFi.reconnect();
    }
  }
}

String NetworkManager::httpGet(const String& url) {
  if (!isConnected()) return "";

  HTTPClient http;
  http.begin(url);
  http.setTimeout(HTTP_TIMEOUT_MS);

  int httpCode = http.GET();
  String payload = "";
  if (httpCode == HTTP_CODE_OK) {
    payload = http.getString();
  }
  http.end();
  return payload;
}

String NetworkManager::httpPost(const String& url, const String& jsonBody) {
  if (!isConnected()) return "";

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(HTTP_TIMEOUT_MS);

  int httpCode = http.POST(jsonBody);
  String payload = "";
  if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
    payload = http.getString();
  }
  http.end();
  return payload;
}

bool NetworkManager::registerAnonymousLearner(String& outLearnerId) {
  String url = backendBaseUrl + "/learners";
  String body = "{\"display_alias\":\"ESP32 Toy Explorer\",\"avatar_icon\":\"robot\"}";
  String resp = httpPost(url, body);

  if (resp.length() == 0) return false;

  DynamicJsonDocument doc(1024);
  DeserializationError err = deserializeJson(doc, resp);
  if (err) return false;

  outLearnerId = doc["id"].as<String>();
  return (outLearnerId.length() > 0);
}

bool NetworkManager::fetchNextQuestion(const String& learnerId, QuestionData& outQuestion) {
  String url = backendBaseUrl + "/questions/next?learner_id=" + learnerId;
  String resp = httpGet(url);

  if (resp.length() == 0) return false;

  DynamicJsonDocument doc(2048);
  DeserializationError err = deserializeJson(doc, resp);
  if (err) return false;

  outQuestion.questionId = doc["question_id"].as<String>();
  outQuestion.topicTitle = doc["topic_title"].as<String>();
  outQuestion.conceptTitle = doc["concept_title"].as<String>();
  outQuestion.difficulty = doc["difficulty"] | 1;
  outQuestion.questionText = doc["question_text"].as<String>();

  JsonArray opts = doc["options"].as<JsonArray>();
  outQuestion.optionCount = 0;
  for (JsonVariant v : opts) {
    if (outQuestion.optionCount < 4) {
      outQuestion.options[outQuestion.optionCount++] = v.as<String>();
    }
  }

  outQuestion.valid = true;
  return true;
}

bool NetworkManager::submitAnswer(
  const String& learnerId,
  const String& questionId,
  const String& answer,
  int responseTimeMs,
  AnswerResult& outResult
) {
  String url = backendBaseUrl + "/questions/answer";
  DynamicJsonDocument reqDoc(512);
  reqDoc["learner_id"] = learnerId;
  reqDoc["question_id"] = questionId;
  reqDoc["submitted_answer"] = answer;
  reqDoc["response_time_ms"] = responseTimeMs;
  reqDoc["hints_used"] = 0;

  String body;
  serializeJson(reqDoc, body);
  String resp = httpPost(url, body);

  if (resp.length() == 0) return false;

  DynamicJsonDocument resDoc(1024);
  DeserializationError err = deserializeJson(resDoc, resp);
  if (err) return false;

  outResult.isCorrect = resDoc["is_correct"] | false;
  outResult.correctAnswer = resDoc["correct_answer"].as<String>();
  outResult.streak = resDoc["current_streak"] | 0;
  outResult.feedbackMessage = resDoc["feedback_message"].as<String>();
  outResult.valid = true;
  return true;
}

bool NetworkManager::fetchHint(
  const String& learnerId,
  const String& questionId,
  int level,
  String& outHintText
) {
  String url = backendBaseUrl + "/questions/hint";
  DynamicJsonDocument reqDoc(256);
  reqDoc["learner_id"] = learnerId;
  reqDoc["question_id"] = questionId;
  reqDoc["hint_level"] = level;

  String body;
  serializeJson(reqDoc, body);
  String resp = httpPost(url, body);

  if (resp.length() == 0) return false;

  DynamicJsonDocument resDoc(1024);
  DeserializationError err = deserializeJson(resDoc, resp);
  if (err) return false;

  outHintText = resDoc["hint_text"].as<String>();
  return true;
}
