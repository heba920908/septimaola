"""Codemie-based LLM grader implementation."""

import logging
import re
from typing import Any, Dict

from septima_automation.ai.factory import create_provider

from .base import GradingRubric, GradingResult, LLMGrader

logger = logging.getLogger(__name__)


class CodemieGrader(LLMGrader):
    """Grader implementation using Codemie as the evaluation LLM."""

    def __init__(self, provider_name: str = "codemie"):
        self.provider_name = provider_name
        self._provider = None

    async def _get_provider(self):
        """Lazy initialization of provider."""
        if self._provider is None:
            self._provider = create_provider(self.provider_name)
        return self._provider

    async def evaluate(
        self,
        content: str,
        rubric: GradingRubric,
        context: Dict[str, Any] | None = None,
    ) -> GradingResult:
        """Evaluate content using Codemie LLM."""
        provider = await self._get_provider()

        grading_prompt = self._build_grading_prompt(content, rubric, context)

        # Call Codemie for evaluation - use a simple system prompt
        from septima_automation.ai.prompts import SYSTEM_PROMPT

        response = await provider._client.chat.completions.create(
            model=getattr(provider, "model", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a quality assessment expert. Evaluate content objectively.",
                },
                {"role": "user", "content": grading_prompt},
            ],
            temperature=0.3,
            max_tokens=300,
            stream=False,
        )

        evaluation_text = response.choices[0].message.content or ""

        return self._parse_evaluation(evaluation_text, rubric)

    def _parse_evaluation(
        self, evaluation_text: str, rubric: GradingRubric
    ) -> GradingResult:
        """Parse the LLM's evaluation response into a structured result."""
        criteria_scores: Dict[str, float] = {}

        # Extract scores for each criterion
        for criterion in rubric.criteria.keys():
            # Look for patterns like "tone_match: 4" or "tone_match": 4
            patterns = [
                rf"{criterion}[:\s]+(\d+(?:\.\d+)?)",
                rf"{criterion.replace('_', ' ')}[:\s]+(\d+(?:\.\d+)?)",
            ]
            for pattern in patterns:
                match = re.search(pattern, evaluation_text, re.IGNORECASE)
                if match:
                    criteria_scores[criterion] = float(match.group(1))
                    break
            else:
                # Default to middle score if not found
                criteria_scores[criterion] = (rubric.scale_min + rubric.scale_max) / 2
                logger.warning(f"Could not find score for criterion: {criterion}")

        # Extract total score
        total_match = re.search(
            r"TOTAL[:\s]+(\d+(?:\.\d+)?)", evaluation_text, re.IGNORECASE
        )
        if total_match:
            total = float(total_match.group(1))
        else:
            # Calculate weighted total
            total = sum(
                criteria_scores.get(c, 0) * w for c, w in rubric.criteria.items()
            )

        # Extract pass/fail
        pass_match = re.search(
            r"PASS[:\s]+(YES|NO|TRUE|FALSE)", evaluation_text, re.IGNORECASE
        )
        passed = pass_match and pass_match.group(1).upper() in ("YES", "TRUE")

        # Extract feedback (everything after FEEDBACK: or the whole text if no markers)
        feedback_match = re.search(
            r"FEEDBACK[:\s]+(.+)", evaluation_text, re.IGNORECASE | re.DOTALL
        )
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        else:
            feedback = evaluation_text.strip()

        return GradingResult(
            criteria=criteria_scores,
            total=total,
            feedback=feedback,
            passed=passed,
        )

    async def close(self):
        """Close the provider connection."""
        if self._provider:
            await self._provider.close()
            self._provider = None
