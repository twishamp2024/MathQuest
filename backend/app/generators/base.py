"""Abstract Base Class for Question Generators."""

from abc import ABC, abstractmethod
from typing import Optional
from backend.app.schemas.question import QuestionConstraint, GeneratedQuestionPayload


class BaseQuestionGenerator(ABC):
    """Abstract interface for all question generation providers."""

    @abstractmethod
    def generate(self, constraints: QuestionConstraint) -> GeneratedQuestionPayload:
        """
        Generate a validated question matching the provided constraints.
        Must return a structured GeneratedQuestionPayload.
        """
        pass
