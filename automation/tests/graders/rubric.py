"""Standard grading rubric for social media prompt evaluation."""

from .base import GradingRubric


# Default rubric for evaluating social media content
SOCIAL_MEDIA_RUBRIC = GradingRubric(
    criteria={
        "tone_match": 0.25,  # Positive, Mexican Spanish, reggae/jazz vibe
        "length": 0.20,  # 2-3 sentences as specified
        "content": 0.30,  # Includes fun-fact/historical element
        "emoji_usage": 0.15,  # Appropriate musical emoji present
        "language": 0.10,  # Correct Spanish grammar and vocabulary
    },
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
