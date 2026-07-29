"""Codemie-based LLM grader implementation."""

import logging
import re
from typing import Any, Dict

from septima_automation.ai.codemie import CodemieClient
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
        if not isinstance(provider, CodemieClient):
            raise TypeError("CodemieGrader requires a CodemieClient provider")

        grading_prompt = self._build_grading_prompt(content, rubric, context)

        # temperature=0: grading should be as deterministic as possible.
        # The default (0.8, used for content generation) previously leaked
        # into grading via this same method, making scores non-reproducible.
        evaluation_text = await provider.generate_chat_completion(
            [
                {
                    "role": "system",
                    "content": "You are a quality assessment expert. Evaluate content objectively.",
                },
                {"role": "user", "content": grading_prompt},
            ],
            temperature=0,
        )
        logger.info("Codemie grader raw evaluation:\n%s", evaluation_text)

        return self._parse_evaluation(evaluation_text, rubric)

    def _parse_evaluation(
        self, evaluation_text: str, rubric: GradingRubric
    ) -> GradingResult:
        """Parse the LLM's evaluation response into a structured result."""
        criteria_scores: Dict[str, float] = {}
        skipped: list[str] = []

        # Scope extraction to the text after the last "SCORES:" marker, so
        # criterion names appearing earlier (in the criteria list, alongside
        # their weights, e.g. "content (weight: 30%)") are never mistaken
        # for a scored line ("content: 4").
        scores_match = re.search(r"SCORES:", evaluation_text, re.IGNORECASE)
        scored_text = (
            evaluation_text[scores_match.end() :] if scores_match else evaluation_text
        )

        for criterion in rubric.criteria.keys():
            if criterion in rubric.optional_criteria:
                na_patterns = [
                    rf"{criterion}[:\s]+N/?A\b",
                    rf"{criterion.replace('_', ' ')}[:\s]+N/?A\b",
                ]
                if any(re.search(p, scored_text, re.IGNORECASE) for p in na_patterns):
                    skipped.append(criterion)
                    continue

            # Look for patterns like "tone_match: 4" or "tone_match": 4
            patterns = [
                rf"{criterion}[:\s]+(\d+(?:\.\d+)?)",
                rf"{criterion.replace('_', ' ')}[:\s]+(\d+(?:\.\d+)?)",
            ]
            for pattern in patterns:
                match = re.search(pattern, scored_text, re.IGNORECASE)
                if match:
                    score = float(match.group(1))
                    if rubric.scale_min <= score <= rubric.scale_max:
                        criteria_scores[criterion] = score
                        break
            else:
                # Default to middle score if not found
                criteria_scores[criterion] = (rubric.scale_min + rubric.scale_max) / 2
                logger.warning(f"Could not find score for criterion: {criterion}")

        weights = rubric.effective_weights(skipped)
        total = sum(
            criteria_scores.get(criterion, 0) * weight
            for criterion, weight in weights.items()
        )

        # Extract pass/fail
        pass_match = re.search(
            r"PASS[:\s]+(YES|NO|TRUE|FALSE)", evaluation_text, re.IGNORECASE
        )
        passed = bool(pass_match and pass_match.group(1).upper() in ("YES", "TRUE"))

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
            skipped=tuple(skipped),
            weights=weights,
        )

    async def close(self):
        """Close the provider connection."""
        if self._provider:
            await self._provider.close()
            self._provider = None
