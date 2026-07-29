"""Base interface for LLM-as-grader implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class GradingRubric:
    """Defines criteria and weights for evaluating prompt quality."""

    criteria: Dict[str, float]
    """Mapping of criterion name to weight (0.0-1.0). Weights should sum to 1.0."""

    scale_min: int = 1
    """Minimum score value."""

    scale_max: int = 5
    """Maximum score value."""

    def validate_weights(self) -> bool:
        """Check that weights sum to approximately 1.0."""
        total = sum(self.criteria.values())
        return abs(total - 1.0) < 0.001


@dataclass
class GradingResult:
    """Result of a grading evaluation."""

    criteria: Dict[str, float]
    """Individual scores for each criterion (scale_min to scale_max)."""

    total: float
    """Weighted total score."""

    feedback: str
    """Textual feedback explaining the evaluation."""

    passed: bool
    """Whether the content passed the minimum threshold."""


class LLMGrader(ABC):
    """Abstract base class for LLM-based content graders."""

    @abstractmethod
    async def evaluate(
        self,
        content: str,
        rubric: GradingRubric,
        context: Dict[str, Any] | None = None,
    ) -> GradingResult:
        """Evaluate content against a rubric.

        Args:
            content: The text content to evaluate.
            rubric: The grading criteria and weights.
            context: Optional additional context (e.g., song title, expected tone).

        Returns:
            GradingResult with scores and feedback.
        """
        pass

    def _build_grading_prompt(
        self,
        content: str,
        rubric: GradingRubric,
        context: Dict[str, Any] | None = None,
    ) -> str:
        """Build a prompt for the LLM grader.

        This default implementation creates a structured prompt.
        Subclasses may override for provider-specific optimization.
        """
        criteria_desc = "\n".join(
            f"- {name}: score {rubric.scale_min}-{rubric.scale_max} (weight: {weight:.0%})"
            for name, weight in rubric.criteria.items()
        )
        score_template = "\n".join(
            f"{name}: [score {rubric.scale_min}-{rubric.scale_max}]"
            for name in rubric.criteria
        )

        ctx_str = ""
        if context:
            ctx_str = "\nContext:\n" + "\n".join(
                f"- {k}: {v}" for k, v in context.items()
            )

        return f"""You are a quality grader for social media content. Evaluate the following content against the criteria below.

Content to evaluate:
```
{content}
```

Evaluation Criteria:
{criteria_desc}
{ctx_str}

Provide your evaluation in this exact format:

SCORES:
{score_template}
TOTAL: [weighted sum from {rubric.scale_min} to {rubric.scale_max}]
PASS: [YES/NO]
FEEDBACK: [2-3 sentences explaining scores]

Be strict but fair. A score of 3 indicates acceptable quality, 4 is good, 5 is excellent."""
