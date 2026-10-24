# MathQuest — REST API Reference Guide

**Base URL:** `/api/v1`  
**Interactive Swagger UI:** `http://localhost:8000/docs`  
**OpenAPI Specification:** `http://localhost:8000/openapi.json`

---

## 1. System & Health

### `GET /api/v1/health`
Returns system operational status, database connectivity, and active version numbers.
```json
{
  "status": "ok",
  "app_name": "MathQuest Backend",
  "version": "1.0.0",
  "environment": "development",
  "database_connected": true,
  "ai_provider": "offline",
  "content_version": "2026.10.1",
  "firmware_version": "1.0.0"
}
```

### `GET /api/v1/ready`
Kubernetes / Docker readiness probe.
```json
{
  "ready": true
}
```

---

## 2. Anonymous Learner Profiles

### `POST /api/v1/learners`
Create a new anonymous profile without collecting PII.
```json
// Request
{
  "display_alias": "Cosmic Voyager",
  "avatar_icon": "rocket"
}

// Response (201 Created)
{
  "id": "mq_k7x9m2ab",
  "display_alias": "Cosmic Voyager",
  "avatar_icon": "rocket",
  "created_at": "2026-10-24T02:30:00Z",
  "last_active_at": "2026-10-24T02:30:00Z",
  "total_questions_answered": 0,
  "total_correct": 0,
  "current_streak": 0,
  "highest_streak": 0,
  "mastery_records": []
}
```

### `GET /api/v1/learners/{learner_id}`
Retrieve profile and concept mastery records.

### `GET /api/v1/learners/{learner_id}/stats`
Retrieve aggregated statistics and mastery percentage across all active topics.

---

## 3. Learning Sessions

### `POST /api/v1/sessions`
Start a learning session.
```json
// Request
{
  "learner_id": "mq_k7x9m2ab",
  "topic_filter": null,
  "game_mode": "adaptive"
}
```

### `POST /api/v1/sessions/{session_id}/end`
End an active session and retrieve summary accuracy.

---

## 4. Adaptive Questions & Answers

### `GET /api/v1/questions/next`
Fetch the next adaptively recommended question.
**Query Parameters:**
- `learner_id` (string, required)
- `session_id` (string, optional)
- `topic_filter` (string, optional)

```json
// Response
{
  "question_id": "q_9c8b7a6d5e4f3a2b",
  "session_id": "sess_1a2b3c4d",
  "topic_id": "mul_div",
  "topic_title": "Multiplication & Division",
  "concept_id": "multiplication_facts",
  "concept_title": "Times Tables (2 to 12)",
  "difficulty": 2,
  "question_text": "What is 7 × 8?",
  "question_format": "multiple_choice",
  "options": ["48", "54", "56", "64"],
  "has_small_hint": true,
  "has_detailed_hint": true,
  "recommendation_reason": "Selected concept 'Times Tables (2 to 12)' with current mastery 0.65...",
  "created_at": "2026-10-24T02:31:00Z"
}
```
*(Notice: `correct_answer` is strictly omitted from the child-facing response!)*

### `POST /api/v1/questions/answer`
Submit child answer for server-side evaluation.
```json
// Request
{
  "learner_id": "mq_k7x9m2ab",
  "question_id": "q_9c8b7a6d5e4f3a2b",
  "session_id": "sess_1a2b3c4d",
  "submitted_answer": "56",
  "response_time_ms": 3200,
  "hints_used": 0
}

// Response
{
  "is_correct": true,
  "submitted_answer": "56",
  "correct_answer": "56",
  "feedback_message": "Awesome job! That is correct!",
  "detected_misconception": null,
  "explanation_steps": ["7 × 8 means 7 groups of 8", "Result is 56"],
  "current_streak": 3,
  "highest_streak": 3,
  "mastery_change": 0.084,
  "new_mastery_score": 0.734,
  "concept_id": "multiplication_facts"
}
```

### `POST /api/v1/questions/hint`
Request a progressive pedagogical hint (Level 1, 2, or 3).

---

## 5. Firmware OTA & Content Updates

### `POST /api/v1/firmware/check`
Check if an ESP32 hardware device has an authorized update available.
```json
// Request
{
  "current_version": "0.9.0",
  "device_model": "esp32-devkit-v1",
  "channel": "stable"
}

// Response
{
  "update_available": true,
  "current_version": "0.9.0",
  "target_version": "1.0.0",
  "binary_url": "/api/v1/firmware/download/esp32-v1.0.0.bin",
  "sha256_hash": "8f4e2b10a9c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9",
  "is_critical": false,
  "release_notes": "Initial release: Adaptive math game with SSD1306 OLED and buzzer."
}
```
