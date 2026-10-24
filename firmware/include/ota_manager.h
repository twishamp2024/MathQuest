#ifndef OTA_MANAGER_H
#define OTA_MANAGER_H

#include <Arduino.h>
#include <Update.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

class OtaManager {
public:
  OtaManager();
  bool checkForUpdate(const String& backendUrl, String& outTargetVersion, String& outBinaryUrl, String& outSha256);
  bool performOtaUpdate(const String& binaryUrl, const String& expectedSha256);

private:
  bool verifyPartitionIntegrity();
};

#endif // OTA_MANAGER_H
