"""Structured Hint and Explanation Engine.

Provides 3 graduated levels of scaffolding:
- Level 1: Conceptual prompt / Gentle nudge (does not reveal method or numbers)
- Level 2: Strategic guidance / Step formulation (breaks down calculation technique)
- Level 3: Worked example / Full solution walkthrough
"""

from typing import List, Optional
from backend.app.schemas.answer import HintResponse


class HintEngine:
    """Manages progressive hints and explanations."""

    @classmethod
    def get_hint(
        cls,
        question_id: str,
        hint_level: int,
        hint_small: Optional[str],
        hint_detailed: Optional[str],
        explanation_steps: List[str],
        correct_answer: str,
    ) -> HintResponse:
        """Return appropriately scaffolded hint based on requested level (1-3)."""
        clamped_level = max(1, min(3, hint_level))

        if clamped_level == 1:
            # Level 1: Conceptual prompt
            text = hint_small or "Think about the definition of this operation. What is being combined or compared?"
            return HintResponse(
                question_id=question_id,
                hint_level=1,
                hint_text=text,
                step_by_step=None,
                worked_example=None,
            )

        elif clamped_level == 2:
            # Level 2: Strategic guidance
            text = hint_detailed or "Break the problem down into two simpler steps."
            steps = explanation_steps[:-1] if len(explanation_steps) > 1 else explanation_steps
            return HintResponse(
                question_id=question_id,
                hint_level=2,
                hint_text=text,
                step_by_step=steps,
                worked_example=None,
            )

        else:
            # Level 3: Worked example / Complete walkthrough
            steps = explanation_steps if explanation_steps else [f"The correct answer is {correct_answer}."]
            text = "Here is the step-by-step worked solution:"
            worked = " -> ".join(steps)
            return HintResponse(
                question_id=question_id,
                hint_level=3,
                hint_text=text,
                step_by_step=steps,
                worked_example=worked,
            )
