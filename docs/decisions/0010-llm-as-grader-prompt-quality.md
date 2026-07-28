# ADR-0010: Live LLM-As-Grader Testing for Prompt Quality

## Status

Accepted

## Context

The social media automation system in `automation/src/septima_automation/ai/prompts.py` generates AI prompts for daily posts. We need to ensure the quality and consistency of these prompts across different AI providers (Deepseek and Codemie). Current testing relies on mocked providers, which doesn't validate actual LLM output quality.

We need a systematic approach to:
1. Measure prompt quality using live LLM responses
2. Validate output against expected criteria (tone, length, content)
3. Enable iterative prompt refinement based on real provider behavior
4. Support multiple providers (Deepseek and Codemie) for comparison

## Decision

Implement an LLM-as-grader testing framework using pytest with live integration tests. The framework will use Codemie as the primary AI rig for testing, with Deepseek as a secondary provider for comparison.

### Architecture

| Component | Choice | Reason |
|-----------|--------|--------|
| Test Framework | pytest with pytest-asyncio | Existing test infrastructure, async support |
| Grader Strategy | LLM-as-grader pattern | Use a separate LLM call to evaluate output quality |
| Primary AI Rig | Codemie | Internal platform with OpenAI-compatible API |
| Secondary Provider | Deepseek | For cross-provider validation |
| Provider Library | openai (OpenAI-compatible) | Unified interface for both providers |
| Test Isolation | `--live` pytest marker | Run live tests only when explicitly requested |
| Grading Criteria | Structured rubric (1-5 scale) | Tone, length, content accuracy, emoji usage |

### Provider Implementation Strategy

The Codemie provider will be enhanced to use the `openai` library instead of direct HTTP calls:

```python
# Current: Direct httpx with Keycloak OAuth
# New: OpenAI-compatible client with Codemie base URL

class CodemieClient(AIProvider):
    def __init__(self, ...):
        self._client = AsyncOpenAI(
            api_key=self._get_token(),  # Dynamic token from Keycloak
            base_url=f"{self.base_url}/code-assistant-api/v1",
        )
```

Key changes:
1. Codemie provider uses OpenAI-compatible endpoint pattern
2. Dynamic token refresh integrated with OpenAI client
3. Unified interface across all providers

### Testing Framework

#### Test Structure

```
automation/tests/
├── test_prompts_live.py          # Live integration tests
├── conftest.py                   # Fixtures and --live flag
└── graders/
    ├── __init__.py
    ├── base.py                   # Grader interface
    ├── codemie_grader.py         # Codemie-based grader
    └── rubric.py                 # Scoring criteria
```

#### Grading Rubric

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Tone Match | 5% | Positive, Mexican Spanish, reggae/jazz vibe |
| Length | 20% | 2-3 sentences as specified |
| Content | 30% | Includes fun-fact/historical element related to the song or to the present month |
| Grounding | 30% | If "septima ola" it is referred in the output, you must ground the facts with the .claude/skills/septimaola-common/SKILL.md, it should match with the facts contents |
| Emoji Usage | 5% | Appropriate musical emoji present |
| Language | 10% | Correct Spanish grammar and vocabulary |

#### Test Execution

```bash
# Run only mocked/unit tests (default)
uv run pytest automation/tests/

# Run with live integration tests
uv run pytest automation/tests/ --live

# Run only live tests
uv run pytest automation/tests/test_prompts_live.py --live -v

# Run with specific provider
AI_PROVIDER=codemie uv run pytest automation/tests/test_prompts_live.py --live

# Run with grader output
uv run pytest automation/tests/test_prompts_live.py --live --grader-verbose
```

### Test Implementation

```python
# test_prompts_live.py
import pytest
from septima_automation.ai.prompts import build_user_prompt, SYSTEM_PROMPT
from septima_automation.ai.factory import create_provider

pytestmark = [pytest.mark.asyncio]

@pytest.mark.live
async def test_build_user_prompt_generates_valid_content():
    """Live test: Generate prompt and validate output quality."""
    provider = create_provider("codemie")

    prompt = build_user_prompt("Redemption Song", "Bob Marley")
    response = await provider.generate_message("Redemption Song", "Bob Marley")

    # LLM-as-grader validation
    grader = create_grader("codemie")
    score = await grader.evaluate(response, rubric=PROMPT_RUBRIC)

    assert score.total >= 3.5, f"Quality score {score.total} below threshold"
    assert score.criteria["tone_match"] >= 3
    assert score.criteria["length"] >= 4

@pytest.mark.live
@pytest.mark.parametrize("provider_name", ["codemie", "deepseek"])
async def test_cross_provider_consistency(provider_name):
    """Validate consistent output across providers."""
    provider = create_provider(provider_name)

    response = await provider.generate_message("Three Little Birds", "Bob Marley")

    # Both providers should produce Spanish content
    assert any(word in response.lower() for word in ["canción", "música", "ritmo"])
```

### Configuration

#### Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `CODEMIE_BASE_URL` | CodemieClient | Codemie instance URL |
| `CODEMIE_KEYCLOAK_URL` | CodemieClient | Keycloak base URL |
| `CODEMIE_REALM` | CodemieClient | Keycloak realm |
| `CODEMIE_CLIENT_ID` | CodemieClient | OAuth client ID |
| `CODEMIE_CLIENT_SECRET` | CodemieClient | OAuth client secret |
| `DEEPSEEK_API_KEY` | DeepseekClient | Deepseek API key |
| `RUN_LIVE_TESTS` | pytest | Enable live tests (alternative to --live flag) |

#### Pytest Configuration (conftest.py)

```python
def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run live integration tests against real LLM providers"
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "live: mark test as requiring live LLM access")

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--live"):
        skip_live = pytest.mark.skip(reason="need --live option to run")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(skip_live)
```

## Consequences

### Positive

- **Quality Validation**: Real LLM output testing ensures prompt effectiveness
- **Provider Comparison**: Can measure quality differences between Codemie and Deepseek
- **Iterative Improvement**: Grader feedback enables data-driven prompt refinement
- **Regression Detection**: Automated testing catches prompt quality degradation
- **Documentation**: Rubric serves as specification for acceptable output
- **Confidence**: Stakeholders can trust automated social media content

### Negative

- **Cost**: Live tests consume LLM tokens (mitigated by running only on-demand)
- **Flakiness**: LLM outputs are non-deterministic; tests need tolerance ranges
- **Latency**: Live tests run slower than mocked tests
- **Maintenance**: Grader prompts need updates as content requirements evolve

### Neutral

- **Manual Triggering**: Live tests require explicit `--live` flag to run
- **Provider Dependency**: Tests fail if Codemie/Deepseek services are unavailable
- **Spanish Focus**: All grading criteria assume Spanish language output

## Future Enhancements

- Automated prompt A/B testing with statistical significance
- Historical quality tracking and trend analysis
- Integration with CI/CD for pre-deployment quality gates
- Expansion to other content types (stories, reels, longer posts)
- Fine-tuned grading model trained on historical quality assessments
