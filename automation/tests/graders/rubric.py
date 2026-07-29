"""Standard grading rubric for social media prompt evaluation."""

from .base import GradingRubric


# Default rubric for evaluating social media content.
# Weights and descriptions mirror the "Grading Rubric" table in
# docs/decisions/0010-llm-as-grader-prompt-quality.md. `grounding` is
# optional: it only applies when the content is about Septima Ola, and is
# reported as N/A (then dropped + renormalized) otherwise — see
# GradingRubric.effective_weights and CodemieGrader._parse_evaluation.
SOCIAL_MEDIA_RUBRIC = GradingRubric(
    criteria={
        "tone_match": 0.05,
        "length": 0.20,
        "content": 0.30,
        "grounding": 0.30,
        "emoji_usage": 0.05,
        "language": 0.10,
    },
    descriptions={
        "tone_match": "Positive, Mexican Spanish, reggae/jazz vibe",
        "length": "2-3 sentences as specified",
        "content": "Includes a fun-fact or brief historical element",
        "grounding": (
            'Includes factual information from "Septima Ola" if the '
            "content is about Septima Ola; N/A for other artists"
        ),
        "emoji_usage": "Appropriate musical emoji present",
        "language": "Correct Spanish grammar and vocabulary",
    },
    optional_criteria=frozenset({"grounding"}),
    scale_min=1,
    scale_max=5,
)

# Rubric specifically for prompt engineering quality
PROMPT_ENGINEERING_RUBRIC = GradingRubric(
    criteria={
        "clarity": 0.30,  # Instructions are clear and unambiguous
        "completeness": 0.25,  # All required elements are present
        "context": 0.25,  # Song/artist context is properly integrated
        "constraints": 0.20,  # Constraints (length, language, tone) are clear
    },
    scale_min=1,
    scale_max=5,
)
