"""Non-live tests for the grading rubric and parser (no LLM calls)."""

import pytest

from graders import PROMPT_ENGINEERING_RUBRIC, SOCIAL_MEDIA_RUBRIC
from graders.base import GradingRubric
from graders.codemie_grader import CodemieGrader


class TestRubricWeights:
    def test_social_media_rubric_weights_sum_to_one(self):
        assert SOCIAL_MEDIA_RUBRIC.validate_weights()

    def test_prompt_engineering_rubric_weights_sum_to_one(self):
        assert PROMPT_ENGINEERING_RUBRIC.validate_weights()

    def test_social_media_rubric_matches_adr_weights(self):
        """Weights must match the ADR-0010 "Grading Rubric" table."""
        assert SOCIAL_MEDIA_RUBRIC.criteria == {
            "tone_match": 0.05,
            "length": 0.20,
            "content": 0.30,
            "grounding": 0.30,
            "emoji_usage": 0.05,
            "language": 0.10,
        }

    def test_grounding_is_optional(self):
        assert "grounding" in SOCIAL_MEDIA_RUBRIC.optional_criteria

    def test_descriptions_cover_all_criteria(self):
        for criterion in SOCIAL_MEDIA_RUBRIC.criteria:
            assert criterion in SOCIAL_MEDIA_RUBRIC.descriptions
            assert SOCIAL_MEDIA_RUBRIC.descriptions[criterion]


class TestEffectiveWeights:
    def test_no_skip_returns_original_weights(self):
        weights = SOCIAL_MEDIA_RUBRIC.effective_weights([])
        assert weights == SOCIAL_MEDIA_RUBRIC.criteria

    def test_skipping_grounding_renormalizes_to_one(self):
        weights = SOCIAL_MEDIA_RUBRIC.effective_weights(["grounding"])
        assert "grounding" not in weights
        assert abs(sum(weights.values()) - 1.0) < 1e-9

    def test_skipping_grounding_preserves_relative_proportions(self):
        weights = SOCIAL_MEDIA_RUBRIC.effective_weights(["grounding"])
        # tone_match (0.05) and length (0.20) should keep a 1:4 ratio.
        assert weights["length"] / weights["tone_match"] == pytest.approx(4.0)

    def test_skipping_all_criteria_falls_back_to_original(self):
        """Degenerate case: never divide by zero."""
        weights = SOCIAL_MEDIA_RUBRIC.effective_weights(SOCIAL_MEDIA_RUBRIC.criteria)
        assert weights == SOCIAL_MEDIA_RUBRIC.criteria


class TestGradingPromptBuilding:
    def test_prompt_includes_weights_and_descriptions(self):
        grader = CodemieGrader()
        prompt = grader._build_grading_prompt("some content", SOCIAL_MEDIA_RUBRIC)
        assert "grounding (weight: 30%)" in prompt
        assert SOCIAL_MEDIA_RUBRIC.descriptions["grounding"] in prompt

    def test_prompt_mentions_na_for_optional_criteria(self):
        grader = CodemieGrader()
        prompt = grader._build_grading_prompt("some content", SOCIAL_MEDIA_RUBRIC)
        assert "N/A" in prompt
        assert "grounding" in prompt

    def test_context_splits_expected_attrs_from_grounding_reference(self):
        grader = CodemieGrader()
        prompt = grader._build_grading_prompt(
            "some content",
            SOCIAL_MEDIA_RUBRIC,
            context={
                "song_author": "Septima Ola",
                "grounding_reference": "Septima Ola: reggae, ska, rocksteady.",
            },
        )
        assert "Expected attributes:" in prompt
        assert "song_author: Septima Ola" in prompt
        assert "Reference facts (grounding source):" in prompt
        assert "Septima Ola: reggae, ska, rocksteady." in prompt
        # The grounding reference must not appear as an "expected attribute".
        expected_block = prompt.split("Expected attributes:")[1].split(
            "Reference facts"
        )[0]
        assert "grounding_reference" not in expected_block


class TestParseEvaluation:
    """Test CodemieGrader._parse_evaluation without any live LLM calls."""

    def test_parses_numeric_scores_and_computes_weighted_total(self):
        grader = CodemieGrader()
        text = (
            "SCORES:\n"
            "tone_match: 5\n"
            "length: 4\n"
            "content: 3\n"
            "grounding: N/A\n"
            "emoji_usage: 5\n"
            "language: 4\n"
            "PASS: YES\n"
            "FEEDBACK: Solid post."
        )
        result = grader._parse_evaluation(text, SOCIAL_MEDIA_RUBRIC)

        assert result.skipped == ("grounding",)
        assert "grounding" not in result.criteria
        assert result.passed is True
        assert result.feedback == "Solid post."

        expected_weights = SOCIAL_MEDIA_RUBRIC.effective_weights(["grounding"])
        expected_total = sum(
            result.criteria[c] * w for c, w in expected_weights.items()
        )
        assert result.total == pytest.approx(expected_total)

    def test_na_on_required_criterion_falls_back_to_midpoint(self):
        """A required criterion should never be silently dropped; N/A on a
        required criterion is a grader anomaly, not a valid skip."""
        grader = CodemieGrader()
        text = (
            "SCORES:\n"
            "tone_match: N/A\n"
            "length: 4\n"
            "content: 3\n"
            "grounding: 4\n"
            "emoji_usage: 5\n"
            "language: 4\n"
            "PASS: YES\n"
            "FEEDBACK: ok"
        )
        result = grader._parse_evaluation(text, SOCIAL_MEDIA_RUBRIC)
        assert "tone_match" not in result.skipped
        assert result.criteria["tone_match"] == 3.0  # midpoint of 1-5

    def test_immune_to_weights_printed_in_criteria_list(self):
        """Regression test: the criteria list echoed back by a verbose LLM
        response must not be parsed as scores (this was the historical
        grader defect noted in ADR-0010)."""
        grader = CodemieGrader()
        text = (
            "Evaluation Criteria:\n"
            "- tone_match (weight: 5%)\n"
            "- length (weight: 20%)\n"
            "- content (weight: 30%)\n"
            "- grounding (weight: 30%)\n"
            "- emoji_usage (weight: 5%)\n"
            "- language (weight: 10%)\n"
            "\n"
            "SCORES:\n"
            "tone_match: 5\n"
            "length: 5\n"
            "content: 5\n"
            "grounding: N/A\n"
            "emoji_usage: 5\n"
            "language: 5\n"
            "PASS: YES\n"
            "FEEDBACK: Great."
        )
        result = grader._parse_evaluation(text, SOCIAL_MEDIA_RUBRIC)
        # If the weights had leaked in as scores, tone_match would be 0.05
        # (clamped out of range) rather than 5.
        assert result.criteria["tone_match"] == 5.0
        assert result.criteria["length"] == 5.0

    def test_missing_criterion_defaults_to_midpoint_with_warning(self, caplog):
        grader = CodemieGrader()
        text = (
            "SCORES:\n"
            "length: 4\n"
            "content: 3\n"
            "grounding: N/A\n"
            "emoji_usage: 5\n"
            "language: 4\n"
            "PASS: YES\n"
            "FEEDBACK: ok"
        )
        result = grader._parse_evaluation(text, SOCIAL_MEDIA_RUBRIC)
        assert result.criteria["tone_match"] == 3.0

    def test_weights_field_reflects_effective_weights_used(self):
        grader = CodemieGrader()
        text = (
            "SCORES:\n"
            "tone_match: 5\n"
            "length: 4\n"
            "content: 3\n"
            "grounding: N/A\n"
            "emoji_usage: 5\n"
            "language: 4\n"
            "PASS: YES\n"
            "FEEDBACK: ok"
        )
        result = grader._parse_evaluation(text, SOCIAL_MEDIA_RUBRIC)
        assert "grounding" not in result.weights
        assert abs(sum(result.weights.values()) - 1.0) < 1e-9


class TestGradingRubricConstruction:
    def test_default_optional_criteria_is_empty(self):
        rubric = GradingRubric(criteria={"a": 0.5, "b": 0.5})
        assert rubric.optional_criteria == frozenset()

    def test_default_descriptions_is_empty(self):
        rubric = GradingRubric(criteria={"a": 0.5, "b": 0.5})
        assert rubric.descriptions == {}
