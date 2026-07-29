"""Base interface for LLM-as-grader implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable


@dataclass
class GradingRubric:
    """Defines criteria and weights for evaluating prompt quality."""

    criteria: Dict[str, float]
    """Mapping of criterion name to weight (0.0-1.0). Weights should sum to 1.0."""

    scale_min: int = 1
    """Minimum score value."""

    scale_max: int = 5
    """Maximum score value."""

    descriptions: Dict[str, str] = field(default_factory=dict)
    """Optional mapping of criterion name to a human-readable description,
    surfaced to the grading LLM so it knows what each criterion means
    (e.g. what "grounding" refers to)."""

    optional_criteria: frozenset[str] = frozenset()
    """Criteria that may not apply to all content (e.g. "grounding" only
    applies when the content is about Septima Ola). The grader may report
    these as N/A, in which case they are dropped and the remaining weights
    are renormalized via `effective_weights`."""

    def validate_weights(self) -> bool:
        """Check that weights sum to approximately 1.0."""
        total = sum(self.criteria.values())
        return abs(total - 1.0) < 0.001

    def effective_weights(self, skipped: Iterable[str]) -> Dict[str, float]:
        """Return weights with `skipped` criteria dropped and renormalized.

        If all criteria are skipped (degenerate case), returns the original
        weights unchanged rather than dividing by zero.
        """
        skipped_set = set(skipped)
        remaining = {
            name: weight
            for name, weight in self.criteria.items()
            if name not in skipped_set
        }
        total = sum(remaining.values())
        if total <= 0:
            return dict(self.criteria)
        return {name: weight / total for name, weight in remaining.items()}


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

    skipped: tuple[str, ...] = ()
    """Optional criteria the grader reported as not applicable (N/A)."""

    weights: Dict[str, float] = field(default_factory=dict)
    """Effective weights actually used to compute `total` (after dropping
    any `skipped` criteria and renormalizing)."""


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
            context: Optional additional context. Two kinds of entries are
                recognized specially by `_build_grading_prompt`:
                - `grounding_reference`: reference/source-of-truth facts
                  rendered in a distinct block, never as an "expectation".
                - anything else: rendered as an expected attribute
                  (e.g. song_title, expected_tone).

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
            f"- {name} (weight: {weight:.0%})"
            + (f" — {rubric.descriptions[name]}" if name in rubric.descriptions else "")
            for name, weight in rubric.criteria.items()
        )
        score_template = "\n".join(
            f"{name}: [score {rubric.scale_min}-{rubric.scale_max}, or N/A]"
            if name in rubric.optional_criteria
            else f"{name}: [score {rubric.scale_min}-{rubric.scale_max}]"
            for name in rubric.criteria
        )

        expected_attrs = {
            k: v for k, v in (context or {}).items() if k != "grounding_reference"
        }
        grounding_reference = (context or {}).get("grounding_reference")

        ctx_str = ""
        if expected_attrs:
            ctx_str = "\nExpected attributes:\n" + "\n".join(
                f"- {k}: {v}" for k, v in expected_attrs.items()
            )

        reference_str = ""
        if grounding_reference:
            reference_str = (
                f"\nReference facts (grounding source):\n{grounding_reference}\n"
            )

        optional_note = ""
        if rubric.optional_criteria:
            optional_names = ", ".join(sorted(rubric.optional_criteria))
            optional_note = (
                f"\nIf a criterion does not apply to this content, output "
                f"`<name>: N/A` instead of a number. This is expected for: "
                f"{optional_names}."
            )

        return f"""You are a quality grader for social media content. Evaluate the following content against the criteria below.

Content to evaluate:
```
{content}
```

Evaluation Criteria:
{criteria_desc}
{ctx_str}
{reference_str}
Provide your evaluation in this exact format:

SCORES:
{score_template}
TOTAL: [weighted sum from {rubric.scale_min} to {rubric.scale_max}]
PASS: [YES/NO]
FEEDBACK: [2-3 sentences explaining scores]

Be strict but fair. A score of 3 indicates acceptable quality, 4 is good, 5 is excellent.{optional_note}"""
