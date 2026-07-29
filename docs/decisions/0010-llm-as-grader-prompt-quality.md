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

Implement an LLM-as-grader testing framework using pytest with live integration tests. The framework uses Codemie as the sole live AI rig for generation and grading. Deepseek remains the production provider and is covered by mocked provider-integration tests.

### Architecture

| Component | Choice | Reason |
|-----------|--------|--------|
| Test Framework | pytest with pytest-asyncio | Existing test infrastructure, async support |
| Grader Strategy | LLM-as-grader pattern | Use a separate LLM call to evaluate output quality |
| Primary AI Rig | Codemie | Internal platform with OpenAI-compatible Chat Completions API |
| Production Provider | Deepseek | Generates production content; mocked tests cover its tool loop |
| Provider Library | `openai` (OpenAI-compatible) | Unified interface for both providers |
| Test Isolation | `--live` pytest marker | Run live tests only when explicitly requested |
| Grading Criteria | Structured rubric (1-5 scale) | Tone, length, content, conditional grounding, emoji usage, language |
| Band grounding | OpenAI-compatible function tool | Canonical band-only facts are supplied on demand |

### Provider Implementation Strategy

The Codemie provider uses its documented OpenAI-compatible Chat Completions
endpoint with `system` and `user` role messages:

```python
client = AsyncOpenAI(
    api_key=await self._get_token(),
    base_url=f"{self.base_url}/code-assistant-api/v1",
)
response = await client.chat.completions.create(
    model=self.model,
    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
)
```

Key changes:
1. `CODEMIE_TOKEN_URL` provides the complete OAuth token endpoint
2. `CODEMIE_BASE_URL` accepts either the service origin or a legacy API base URL
3. Token refresh recreates the OpenAI-compatible client as required
4. `CODEMIE_MODEL` defaults to `gpt-4.1` for both generation and grading
5. The grader calls Codemie with `temperature=0` for repeatable evaluations

### Band-Fact Grounding

Both OpenAI-compatible providers receive the `get_septima_ola_facts` function
tool. `automation/src/septima_automation/ai/band_context.py` contains a
manually synchronized, band-only representation of the canonical profile from
`.claude/skills/septimaola-common/SKILL.md`; it must not contain member or crew
facts. The shared tool loop resolves up to three model-requested tool rounds.

The tool is intended only for Séptima Ola content. If a Codemie model rejects
the `tools` parameter, the client retries once without tools and adds a compact
band-context system message as a fallback. Deepseek tool behavior is covered by
mocked tests because its configured live credentials were invalid during this
decision's implementation.

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
| Content | 30% | Includes a fun-fact or brief historical element |
| Grounding | 30% | Includes factual information from "septima ola" if related |
| Emoji Usage | 5% | Appropriate musical emoji present |
| Language | 10% | Correct Spanish grammar and vocabulary |

The weights total 100% and are implemented by `SOCIAL_MEDIA_RUBRIC` in
`automation/tests/graders/rubric.py`. Scores are on a 1-5 scale. The primary
quality gate is a weighted score of at least 3.5/5 (70% of the maximum), with
additional minimum scores of 3/5 for tone and 4/5 for length in the Codemie
generation test.

Grounding applies only when the generated content concerns Séptima Ola. For
other artists, the grader must emit `grounding: N/A`; the criterion is removed
and the remaining weights are renormalized before the total is computed. For
Séptima Ola content, live tests require a canonical fact marker and a grounding
score of at least 4/5.

#### Test Execution

```bash
# Run from the automation project directory
cd automation

# Run the prompt test module without live calls; live tests are skipped
uv run pytest tests/test_prompts_live.py -v

# Run with live integration tests
uv run pytest tests/ --live

# Run only live tests
uv run pytest tests/test_prompts_live.py --live -v

# Run with specific provider
uv run pytest tests/test_prompts_live.py --live -v -k codemie
```

Live-test logging is enabled in pytest configuration. Each provider response,
the raw grader evaluation, and parsed grader result are emitted at INFO level,
so generated content is visible for both passing and failing live tests.

`AI_PROVIDER`, `--grader-verbose`, and `RUN_LIVE_TESTS` are not implemented by
the current test harness and must not be used as execution controls.

### Test Implementation

```python
# test_prompts_live.py
import pytest
from septima_automation.ai.factory import create_provider
from graders import CodemieGrader, SOCIAL_MEDIA_RUBRIC

MIN_TOTAL_SCORE = 3.5
MIN_TONE_SCORE = 3.0
MIN_LENGTH_SCORE = 4.0

@pytest.mark.live
@pytest.mark.asyncio
async def test_codemie_generates_valid_content():
    """Live test: Generate prompt and validate output quality."""
    provider = create_provider("codemie")
    response = await provider.generate_message("Redemption Song", "Bob Marley")

    # LLM-as-grader validation
    grader = CodemieGrader("codemie")
    result = await grader.evaluate(response, rubric=SOCIAL_MEDIA_RUBRIC)

    assert result.total >= MIN_TOTAL_SCORE
    assert result.criteria["tone_match"] >= MIN_TONE_SCORE
    assert result.criteria["length"] >= MIN_LENGTH_SCORE
```

The representative example reflects `automation/tests/test_prompts_live.py`.
The suite also checks two Séptima Ola songs for canonical grounding. Deepseek
and cross-provider live tests are retained but permanently skipped; mocked tests
verify its tool-call integration and `reasoning_content` fallback.

### Configuration

#### Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `CODEMIE_BASE_URL` | CodemieClient | Codemie instance URL |
| `CODEMIE_TOKEN_URL` | CodemieClient | Keycloak OAuth token endpoint |
| `CODEMIE_CLIENT_ID` | CodemieClient | OAuth client ID |
| `CODEMIE_CLIENT_SECRET` | CodemieClient | OAuth client secret |
| `CODEMIE_MODEL` | CodemieClient | Chat Completions model ID (default: `gpt-4.1`) |
| `DEEPSEEK_API_KEY` | DeepseekClient | Deepseek API key |

#### Codemie Model Discovery

The available model catalogue is account- and deployment-specific. Retrieve it
with a fresh client-credentials token; do not print or persist the token:

```bash
curl --silent --show-error --fail-with-body \
  --header "Authorization: Bearer $TOKEN" \
  "$BASE_URL/code-assistant-api/v1/llm_models?include_all=true"
```

Catalogue retrieved on 2026-07-28 (38 models):

| Family | Available model IDs |
|--------|---------------------|
| Claude | `claude-4-5-sonnet`, `claude-4-5-sonnet-vertex`, `claude-haiku-4-5-20251001`, `claude-opus-4-5-20251101`, `claude-opus-4-6-20260205`, `claude-opus-4-6-vertex`, `claude-opus-4-7`, `claude-opus-4-8`, `claude-opus-5`, `claude-sonnet-4-5-20250929`, `claude-sonnet-4-6`, `claude-sonnet-4-6-vertex`, `claude-sonnet-5` |
| DeepSeek | `deepseek-r1` |
| Gemini | `gemini-3-flash`, `gemini-3.1-flash-image-preview`, `gemini-3.1-pro`, `gemini-3.5-flash` |
| GPT | `gpt-4.1`, `gpt-4.1-mini`, `gpt-5-1-codex-2025-11-13`, `gpt-5-2-2025-12-11`, `gpt-5-2025-08-07`, `gpt-5-mini-2025-08-07`, `gpt-5-nano-2025-08-07`, `gpt-5.4-2026-03-05`, `gpt-5.5-2026-04-24`, `gpt-5.6-luna-2026-07-09`, `gpt-5.6-sol-2026-07-09`, `gpt-5.6-terra-2026-07-09` |
| Other | `moonshotai.kimi-k2.5`, `o1`, `o3-2025-04-16`, `o3-mini`, `o4-mini-2025-04-16`, `qwen.qwen3-coder-30b-a3b-v1`, `qwen.qwen3-coder-480b-a35b-v1` |

Set `CODEMIE_MODEL` to an ID from the current catalogue and run a Chat
Completions smoke test before using it in a live quality suite.

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

### Live Test Run Record

Run date: 2026-07-28

Command executed from `automation/`:

```bash
uv run pytest tests/test_prompts_live.py --live -v
```

Initial result: 3 passed, 8 failed in 5.94 seconds. The three non-live
prompt-structure tests passed. None of the eight live tests reached content
generation or the LLM-as-grader evaluation, so this run provides no
prompt-quality score.

| Provider | Tests affected | Result | Observed cause |
|----------|----------------|--------|----------------|
| Codemie | 7 | Failed before generation | Keycloak token request returned HTTP 404 at the configured token endpoint |
| Deepseek | 1 direct test; 2 cross-provider tests also depend on it | Failed before grading | API returned HTTP 401: configured API key is invalid |

After changing the Codemie configuration to use `CODEMIE_TOKEN_URL`, a focused
retry with `uv run pytest tests/test_prompts_live.py --live -v -k codemie`
selected five Codemie tests; all five failed before generation in 1.79 seconds
because the configured token URL host could not be resolved. The URL was read
only by the test process; its value was not inspected or recorded.

After updating the environment again, the same focused command reached the
Codemie chat-completions request, confirming that token acquisition succeeded.
All five selected tests still failed, now with HTTP 404 (`{"detail":"Not
Found"}`) from the chat-completions endpoint in 4.77 seconds. No response was
generated and the LLM-as-grader was not invoked. The remaining Codemie blocker
was the unsupported assumption that this deployment exposes an
OpenAI-compatible `/chat/completions` route.

Manual verification normalized the configured base URL before requesting
`/code-assistant-api/v1/chat/completions`. The token request and Chat
Completions request each returned HTTP 200, and the response used the expected
OpenAI `choices[0].message.content` shape. The model was obtained from
`/code-assistant-api/v1/llm_models?include_all=true`; no credential, token,
model identifier, or response content was recorded. This confirms role-based
messages are viable without an assistant ID.

The initial SDK retry still returned HTTP 404 despite the successful raw request.
The OpenAI client resolves relative endpoint paths against its base URL, so the
configured base must retain a trailing slash; otherwise URL joining can remove
the final `v1` path segment. The Codemie client now supplies
`/code-assistant-api/v1/` as its OpenAI base URL.

With the environment explicitly sourced before pytest, the Codemie suite reached
generation and grading: all five selected tests returned generated content. The
quality test failed on its length sub-gate and the four song smoke tests failed
because their responses lacked a required musical emoji. This is the first run
that exercised prompt quality rather than provider connectivity. It also exposed
a grader parser defect: its score regex read rubric weights as scores. The
grader now requests unambiguous score lines and always computes the weighted
total from criterion scores in the 1-5 range.

The credentials-presence checks only verify that variables are non-empty; they
do not validate that endpoints, DNS, or credentials work. A successful live run
requires a resolvable and reachable Codemie token endpoint, plus a valid
`DEEPSEEK_API_KEY` for the Deepseek and cross-provider tests, then rerunning
the command above.

For comparison, the same module without `--live` completed with 3 passed and
8 skipped in 0.75 seconds, confirming the explicit live-test gate works.

After the grounding/tool-loop implementation, the non-live automation suite
passed with `78 passed, 9 skipped` using `uv run pytest tests/ -v`. A refreshed
Codemie live run on 2026-07-28 passed with `8 passed, 3 skipped` using
`uv run pytest tests/test_prompts_live.py --live -v`. The live result confirmed
that non-Séptima Ola content receives `grounding: N/A` and that both grounded
Séptima Ola cases invoked the fact tool and received grounding scores of 5/5.
Deepseek remains excluded from live prompt-quality tests until valid credentials
are available.

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
