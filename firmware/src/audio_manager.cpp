#include "audio_manager.h"

AudioManager::AudioManager() {}

void AudioManager::begin() {
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_WIFI_PIN, OUTPUT);
  pinMode(LED_SUCCESS_PIN, OUTPUT);
  pinMode(LED_ERROR_PIN, OUTPUT);

  digitalWrite(LED_WIFI_PIN, LOW);
  digitalWrite(LED_SUCCESS_PIN, LOW);
  digitalWrite(LED_ERROR_PIN, LOW);
}

void AudioManager::playTone(int frequency, int durationMs) {
  #if defined(ESP32)
    ledcAttachPin(BUZZER_PIN, BUZZER_PWM_CHANNEL);
    ledcWriteTone(BUZZER_PWM_CHANNEL, frequency);
    delay(durationMs);
    ledcWrite(BUZZER_PWM_CHANNEL, 0);
  #else
    tone(BUZZER_PIN, frequency, durationMs);
    delay(durationMs);
  #endif
}

void AudioManager::playBootBeep() {
  playTone(2000, 60);
  delay(40);
  playTone(2500, 80);
}

void AudioManager::playClick() {
  playTone(1800, 25);
}

void AudioManager::playCorrectSound() {
  digitalWrite(LED_SUCCESS_PIN, HIGH);
  playTone(1046, 60); // C6
  delay(20);
  playTone(1318, 60); // E6
  delay(20);
  playTone(1568, 90); // G6
  digitalWrite(LED_SUCCESS_PIN, LOW);
}

void AudioManager::playIncorrectSound() {
  digitalWrite(LED_ERROR_PIN, HIGH);
  playTone(250, 150);
  delay(30);
  playTone(180, 220);
  digitalWrite(LED_ERROR_PIN, LOW);
}

void AudioManager::setWifiLed(bool on) {
  digitalWrite(LED_WIFI_PIN, on ? HIGH : LOW);
}

void AudioManager::pulseSuccessLed(int durationMs) {
  digitalWrite(LED_SUCCESS_PIN, HIGH);
  delay(durationMs);
  digitalWrite(LED_SUCCESS_PIN, LOW);
}

void AudioManager::pulseErrorLed(int durationMs) {
  digitalWrite(LED_ERROR_PIN, HIGH);
  delay(durationMs);
  digitalWrite(LED_ERROR_PIN, LOW);
}
