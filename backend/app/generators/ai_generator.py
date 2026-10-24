"""AI-assisted Question Generator with Structured Output, Validation, and Offline Fallback.

Supports:
- Google Gemini API via official google-genai SDK
- Strict JSON schema enforcement
- Independent server-side mathematical validation
- Bounded retries and graceful fallback to OfflineQuestionGenerator
"""

import json
import logging
import os
from typing import Optional, Tuple
from backend.app.core.config import settings
from backend.app.generators.base import BaseQuestionGenerator
from backend.app.generators.offline_generator import OfflineQuestionGenerator
from backend.app.schemas.question import QuestionConstraint, GeneratedQuestionPayload
from backend.app.validators.math_validator import MathValidator

logger = logging.getLogger(__name__)


class AIQuestionGenerator(BaseQuestionGenerator):
    """
    AI-backed question generator with strict mathematical validation and guaranteed offline fallback.
    """

    def __init__(self, offline_fallback: Optional[OfflineQuestionGenerator] = None):
        self.offline = offline_fallback or OfflineQuestionGenerator()
        self.provider = settings.AI_PROVIDER.lower()
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model_name = settings.GEMINI_MODEL
        self.timeout = settings.AI_TIMEOUT_SECONDS
        self.max_retries = settings.AI_MAX_RETRIES

    def generate(self, constraints: QuestionConstraint) -> Tuple[GeneratedQuestionPayload, str]:
        """
        Generate a question matching constraints.
        Returns (payload, source_identifier) where source is 'gemini' or 'offline_fallback'.
        """
        # If provider is configured to offline or API key is missing, immediately use offline generator
        if self.provider == "offline" or not self.api_key:
            return self.offline.generate(constraints), "offline"

        # Attempt AI generation with bounded retries
        for attempt in range(self.max_retries + 1):
            try:
                payload = self._call_ai_provider(constraints)
                # Sever-side mathematical validation
                is_valid, reason = MathValidator.validate_question_payload(payload)
                if is_valid:
                    return payload, "gemini"
                else:
                    logger.warning(f"AI generated question failed mathematical validation (attempt {attempt+1}): {reason}")
            except Exception as e:
                logger.warning(f"AI generation error on attempt {attempt+1}: {e}")

        # If all retries fail, seamlessly fall back to offline generator
        logger.info("Falling back to deterministic offline question generator.")
        return self.offline.generate(constraints), "offline_fallback"

    def _call_ai_provider(self, constraints: QuestionConstraint) -> GeneratedQuestionPayload:
        """Call external Gemini API asking for strictly structured JSON output."""
        prompt = self._build_prompt(constraints)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json",
                ),
            )

            raw_text = response.text or "{}"
            data = json.loads(raw_text)

            # Ensure required fields match constraints
            data["topic_id"] = constraints.topic_id
            data["concept_id"] = constraints.concept_id
            data["difficulty"] = constraints.difficulty
            data["question_format"] = constraints.question_format
            data["expected_answer_type"] = constraints.expected_answer_type

            return GeneratedQuestionPayload(**data)
        except Exception as err:
            raise RuntimeError(f"Gemini API invocation failed: {err}")

    def _build_prompt(self, c: QuestionConstraint) -> str:
        """Build a strict, constraint-bound prompt for the AI model."""
        avoid_str = ", ".join(f'"{q}"' for q in c.questions_to_avoid) if c.questions_to_avoid else "None"
        
        return f"""You are an educational mathematics question generator for children aged 8-14.
Generate ONE math question strictly adhering to these pedagogical constraints:
- Topic: {c.topic_id}
- Concept: {c.concept_id}
- Learning Objective: {c.learning_objective}
- Difficulty Level (1 easy to 5 master): {c.difficulty}
- Question Format: {c.question_format}
- Expected Answer Type: {c.expected_answer_type}
- Permitted Range: between {c.min_numeric_value} and {c.max_numeric_value}
- Avoid duplicating any of these questions: [{avoid_str}]

Output MUST be a valid JSON object matching this schema:
{{
  "question_text": "Clear child-friendly question text",
  "options": ["opt1", "opt2", "opt3", "opt4"],  // List of 4 distinct choices if question_format is multiple_choice or comparison
  "correct_answer": "Exact correct answer string that matches one of the options",
  "explanation_steps": ["Step 1...", "Step 2...", "Final step..."],
  "hint_small": "Gentle conceptual nudge without giving away the calculation",
  "hint_detailed": "Clear guidance on how to solve the problem"
}}
Do NOT output markdown fences. Return ONLY the raw JSON object.
"""
