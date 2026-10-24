# MathQuest — Security & Children's Privacy Architecture

Because MathQuest is designed for young learners aged 8–14, **privacy and security are core architectural invariants**, not afterthoughts.

---

## 1. Zero-PII (Personally Identifiable Information) Policy

MathQuest strictly adheres to the principle of data minimization:

| Data Field | Collected? | Rationale / Architectural Safeguard |
| :--- | :---: | :--- |
| **Real Name** | ❌ NO | Learners use random anonymous tokens (e.g. `mq_k7x9m2ab`) or playful aliases ("Star Voyager"). |
| **Email Address** | ❌ NO | No authentication credentials or accounts requiring email. |
| **Phone Number** | ❌ NO | Never requested or stored. |
| **Date of Birth** | ❌ NO | Age-adaptive content is driven exclusively by demonstrated mathematical mastery, not biological age. |
| **Location / GPS** | ❌ NO | No geolocation data is tracked or logged. |
| **Third-Party Ads** | ❌ NO | Zero ad networks, third-party analytics trackers, or commercial pixels. |

---

## 2. Artificial Intelligence Safety & Data Isolation

- **Prompt Sanitization:** When queries are dispatched to external AI models (e.g. Google Gemini), prompts contain **only pedagogical mathematical constraints** (topic, concept, difficulty level, allowed ranges).
- **No Learner Identity Transmitted:** Learner IDs, aliases, response histories, or timestamps are NEVER sent to the AI model.
- **Untrusted Output Policy:** All AI output is parsed through strict Pydantic schemas and independently validated by `MathValidator`. If an LLM hallucinates an invalid mathematical equation or division by zero, the output is rejected and replaced by a verified question from the deterministic offline question bank.

---

## 3. Server Security Safeguards

- **HTTP Security Headers:**
  - `X-Content-Type-Options: nosniff` (prevents MIME sniffing)
  - `X-Frame-Options: DENY` (clickjacking defense)
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Rate Limiting & Bounded Retries:** Prevents denial-of-service and brute force API abuse.
- **SQL Injection Defense:** All database interactions utilize SQLAlchemy 2.0 ORM with parameterized queries.
- **No Hardcoded Secrets:** Configuration is sourced via environment variables (`.env`), with secrets excluded from version control (`.gitignore`).
- **Safe Development Database Reset:** The database reset utility requires an explicit `--confirm-reset` flag and is never run automatically on application startup.

---

## 4. Regulatory & Compliance Context

While MathQuest's anonymous design eliminates traditional PII risks, commercial deployments in schools or homes should review applicable regional frameworks:
- **COPPA (Children's Online Privacy Protection Act — US):** Complies with the principle of zero personal data collection from children under 13.
- **GDPR-K (General Data Protection Regulation for Children — EU):** Adheres to data minimization and purpose limitation principles.
- **DPDP Act (Digital Personal Data Protection Act — India):** Protects children's digital footprints by avoiding behavioral tracking or targeted commercial profiling.
