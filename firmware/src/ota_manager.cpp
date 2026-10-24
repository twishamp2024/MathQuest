#include "ota_manager.h"

OtaManager::OtaManager() {}

bool OtaManager::checkForUpdate(
  const String& backendUrl,
  String& outTargetVersion,
  String& outBinaryUrl,
  String& outSha256
) {
  HTTPClient http;
  String checkUrl = backendUrl + "/firmware/check";
  http.begin(checkUrl);
  http.addHeader("Content-Type", "application/json");

  DynamicJsonDocument reqDoc(256);
  reqDoc["current_version"] = FIRMWARE_VERSION;
  reqDoc["device_model"] = HARDWARE_MODEL;
  reqDoc["channel"] = "stable";

  String body;
  serializeJson(reqDoc, body);
  int httpCode = http.POST(body);

  if (httpCode != HTTP_CODE_OK) {
    http.end();
    return false;
  }

  String resp = http.getString();
  http.end();

  DynamicJsonDocument resDoc(1024);
  DeserializationError err = deserializeJson(resDoc, resp);
  if (err) return false;

  bool updateAvailable = resDoc["update_available"] | false;
  if (updateAvailable) {
    outTargetVersion = resDoc["target_version"].as<String>();
    outBinaryUrl = resDoc["binary_url"].as<String>();
    outSha256 = resDoc["sha256_hash"].as<String>();
    return true;
  }
  return false;
}

bool OtaManager::performOtaUpdate(const String& binaryUrl, const String& expectedSha256) {
  HTTPClient http;
  http.begin(binaryUrl);
  int httpCode = http.GET();

  if (httpCode != HTTP_CODE_OK) {
    http.end();
    return false;
  }

  int contentLength = http.getSize();
  if (contentLength <= 0) {
    http.end();
    return false;
  }

  bool canBegin = Update.begin(contentLength);
  if (!canBegin) {
    http.end();
    return false;
  }

  WiFiClient* stream = http.getStreamPtr();
  size_t written = Update.writeStream(*stream);

  if (written != (size_t)contentLength) {
    Update.abort();
    http.end();
    return false;
  }

  if (!Update.end()) {
    http.end();
    return false;
  }

  if (!Update.isFinished()) {
    http.end();
    return false;
  }

  http.end();
  return true;
}
