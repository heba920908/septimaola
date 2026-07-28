# ADR-0008: Daily Social Media Automation

## Status

Proposed

## Context

Séptima Ola requires a consistent social media presence to engage with fans and
promote new content. Manual posting is time-consuming and inconsistent. We need
an automated pipeline that:

1. Generates fresh, engaging content daily using AI
2. Features a rotating selection of pre-made band videos
3. Publishes simultaneously to Facebook and Instagram
4. Runs on a predictable schedule without manual intervention

## Decision

A Python-based automation tool is built under `automation/` using `uv` as the
package manager and entry-point runner. The pipeline runs via a GitHub Actions
cron workflow and publishes a video post daily to Facebook and Instagram.

### Architecture

| Component | Choice | Reason |
|-----------|--------|--------|
| Language | Python 3.11+ | Async support, rich ecosystem |
| Package manager | `uv` | Fast installs, locked reproducible envs |
| AI providers | Deepseek (`deepseek-chat`) + Codemie | Deepseek: free tier, OpenAI-compatible API; Codemie: internal platform, OpenAI-compatible via Keycloak OAuth |
| AI Library | `openai` SDK | Unified interface for both providers via OpenAI-compatible APIs |
| Video download | Direct download via `httpx` | Fast, asynchronous download of public Google Drive files |
| Social platforms | Facebook Graph API v18.0, Instagram Graph API | Official APIs |
| Scheduling | GitHub Actions cron (`0 9 * * *`) | Free for public repos, no extra infra |
| Secrets | GitHub Secrets (CI), `dotenv` (local) | Secure and standard |
| Testing | pytest + LLM-as-grader | Live integration tests with `--live` flag for prompt quality validation |

### Project Layout

```
automation/
├── pyproject.toml              # uv project: package, scripts, deps
├── uv.lock                     # Pinned dependency tree
├── .python-version             # "3.11"
├── .env.example                # Template; copy to .env for local use
├── README.md                   # Setup and credential guide
├── src/septima_automation/
│   ├── __init__.py
│   ├── config.py               # Asset manifests and constants
│   ├── ai/                     # AI provider implementations
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract AIProvider interface
│   │   ├── factory.py          # Provider factory
│   │   ├── prompts.py          # Prompt templates and builders
│   │   ├── deepseek.py         # Deepseek provider (OpenAI SDK)
│   │   └── codemie.py          # Codemie provider (OpenAI SDK + Keycloak OAuth)
│   ├── selectors.py            # Random video picker
│   ├── video_downloader.py     # Google Drive file downloader
│   ├── message_generator.py    # Post text builder
│   ├── daily_post.py           # CLI entry point (uv run daily-post)
│   └── social/
│       ├── __init__.py
│       ├── base.py             # Abstract SocialPublisher
│       ├── facebook.py         # Facebook Graph API publisher
│       └── instagram.py        # Instagram Graph API publisher
└── tests/
    ├── conftest.py             # Pytest configuration with --live flag
    ├── test_daily_post.py
    ├── test_prompts_live.py    # Live integration tests with LLM-as-grader
    └── graders/                # LLM grading framework
        ├── __init__.py
        ├── base.py
        ├── codemie_grader.py
        └── rubric.py
```

### Dependencies (`pyproject.toml`)

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27.0",        # Async HTTP client
    "python-dotenv>=1.0.0", # .env loading
]

[project.scripts]
daily-post = "septima_automation.daily_post:main"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.5.0",
]
```

### Execution

```bash
# Local — from automation/ directory
uv run daily-post                        # Full run
uv run daily-post --dry-run --verbose    # Generate and download only, no publishing
uv run daily-post --skip-instagram       # Facebook only
uv run src/septima_automation/daily_post.py  # Direct module invocation

# Tests
uv run pytest tests/
```

### Asset Configuration (`config.py`)

Assets are declared as typed dataclasses. Public direct download URLs are constructed
programmatically from `drive_id` so they never need to be hardcoded.

```python
@dataclass
class VideoAsset:
    slug: str
    drive_id: str
    title: str
    author: str

    @property
    def public_url(self) -> str:
        # Google Drive direct download URL
        return f"https://drive.google.com/uc?export=download&id={self.drive_id}"
```

`VIDEOS_CONFIG` holds pre-made band videos — the list must be populated with real Google Drive file IDs before the script can run.

Additional constants in `config.py`:

```python
HASHTAGS = ["#SéptimaOla", "#Reggae", "#Ska", "#Rocksteady",
            "#MusicaMexicana", "#LaRaza", "#CDMX"]

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL   = "deepseek-chat"
```

### AI Message Generation (`ai/`)

Both providers use the `openai` SDK for a unified interface:

**DeepseekClient** (`ai/deepseek.py`):
- Wraps Deepseek API via OpenAI-compatible SDK
- Authentication: Bearer token via `DEEPSEEK_API_KEY`
- Model: `deepseek-chat`
- Parameters: `temperature=0.3`, `max_tokens=150`, `reasoning_effort=high`

**CodemieClient** (`ai/codemie.py`):
- Wraps Codemie API via Keycloak OAuth2 + OpenAI-compatible endpoint
- Authentication: `client_credentials` grant with automatic token refresh
- Model: Configurable via `CODEMIE_MODEL` (default: `gpt-4o`)
- Parameters: `temperature=0.8`, `max_tokens=150`

**Provider Selection** (`ai/factory.py`):
```python
# Via environment variable
AI_PROVIDER=codemie uv run daily-post

# Via factory function
from ai.factory import create_provider
provider = create_provider("deepseek")  # or "codemie"
```

System and user prompts are defined in `ai/prompts.py`:
- `SYSTEM_PROMPT`: Spanish-language instructions for tone, style, and content
- `build_user_prompt(song_title, song_author)`: Generates context-rich user prompt

Parameters vary by provider to optimize for their respective models.

Note: `ASSISTANT_ID` is not required since both providers use the OpenAI-compatible API with `role: "system"` messages to configure assistant behavior.

### Post Caption Format (`message_generator.py`)

```python
caption = f"""{ai_message}

Canción destacada: {song_title} ({song_author})

{' '.join(random_sample_of_hashtags)}"""
```

A random subset of 4 hashtags is drawn per post for variety.

### Video Downloader (`video_downloader.py`)

`VideoDownloader` downloads the selected video asset from Google Drive using its direct download URL to a temporary file, using `httpx.AsyncClient`.

Temporary files are deleted after publishing regardless of outcome.
Output is written to `tempfile.gettempdir()` by default.

### Facebook Publishing (`social/facebook.py`)

`FacebookPublisher` uses `POST /{page_id}/videos` on Graph API v18.0 with a
multipart upload. Required permissions: `pages_manage_posts`.

```
POST https://graph.facebook.com/v18.0/{page_id}/videos
  data: access_token, description (caption), published=true
  files: file (video/mp4)
→ {"id": "<video_post_id>"}
```

### Instagram Publishing (`social/instagram.py`)

`InstagramPublisher` uses the Instagram Graph API 2-step flow:

1. `POST /{ig-user-id}/media` — create a media container with a publicly
   accessible video URL and the caption. The direct download URL of the Google Drive video file is passed as the `video_url` parameter.
2. Poll container status: Check `/container_id` until `status_code` equals `FINISHED`.
3. `POST /{ig-user-id}/media_publish` — publish the container

Required permissions: `instagram_basic`, `instagram_content_publish`,
`pages_read_engagement`.

### Pipeline Flow (`daily_post.py`)

```
load_dotenv()
│
├─ select_random_video()         # Random VideoAsset
│
├─ DeepseekClient.generate_message()  # AI caption
│
├─ MessageGenerator.generate_post()   # Format full caption
│
├─ VideoDownloader.download()         # Download MP4 from Google Drive
│
└─ asyncio.gather() — publish concurrently
    ├─ FacebookPublisher.publish(video_path, caption)
    └─ InstagramPublisher.publish(video_path, caption, video_url)

video_path.unlink()   # Cleanup temp video
print summary
```

Both publishers are awaited concurrently via `asyncio.gather`. Failures on one
platform do not abort the other. Exit code is `0` if at least one platform
published successfully.

CLI flags:
```
--dry-run         Generate content and download video; skip publishing
--verbose         Print step-by-step progress
--skip-facebook   Omit Facebook step
--skip-instagram  Omit Instagram step
```

### Environment Variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `ai/factory.py` | Provider selection: `deepseek` (default) or `codemie` |
| `DEEPSEEK_API_KEY` | `ai/deepseek.py` | Deepseek platform API key |
| `CODEMIE_BASE_URL` | `ai/codemie.py` | Codemie instance base URL |
| `CODEMIE_KEYCLOAK_URL` | `ai/codemie.py` | Keycloak base URL for OAuth |
| `CODEMIE_REALM` | `ai/codemie.py` | Keycloak realm name |
| `CODEMIE_CLIENT_ID` | `ai/codemie.py` | Keycloak OAuth client ID |
| `CODEMIE_CLIENT_SECRET` | `ai/codemie.py` | Keycloak OAuth client secret |
| `CODEMIE_MODEL` | `ai/codemie.py` | Model name (default: `gpt-4o`) |
| `FACEBOOK_APP_CLIENT_ID` | `social/facebook.py` | Optional Facebook app client ID used for OAuth bootstrap/app-token validation |
| `FACEBOOK_APP_CLIENT_SECRET` | `social/facebook.py` | Optional Facebook app client secret used to mint an app access token |
| `FACEBOOK_PAGE_ID` | `social/facebook.py` | Numeric Facebook Page ID |
| `FACEBOOK_ACCESS_TOKEN` | `social/facebook.py`, `social/instagram.py` | Page access token used for publishing |
| `INSTAGRAM_ACCOUNT_ID` | `social/instagram.py` | Instagram Business Account ID |

Locally sourced from `automation/.env` (gitignored). In CI sourced from
GitHub repository secrets injected as environment variables.

### Authentication Strategy

The Facebook OAuth bootstrap flow was validated locally by sourcing the automation
environment and calling the app-token endpoint with the app ID and app secret.
The endpoint returned a bearer token successfully, which confirms that the
app credentials are usable for app-level authentication.

Implementation notes:

1. Keep `FACEBOOK_PAGE_ID` and `FACEBOOK_ACCESS_TOKEN` as the production runtime
   secrets for publishing. These are the values the current automation code uses.
2. Add optional `FACEBOOK_APP_CLIENT_ID` and `FACEBOOK_APP_CLIENT_SECRET`
   variables for bootstrap/validation. They are useful for pre-flight checks and
   future token refresh automation.
3. Implement a small helper module (for example `social/facebook_auth.py`) with:
   - `get_app_access_token(client_id, client_secret)` — calls
     `https://graph.facebook.com/oauth/access_token` with
     `grant_type=client_credentials`
   - `validate_credentials()` — fails fast at startup when the app credentials are
     missing or invalid
   - `refresh_page_token(...)` — a future hook for refreshing or validating a
     page-scoped token when a longer-lived admin-auth flow is available
4. Clarify the scope boundary in the ADR: the `client_credentials` flow returns an
   app access token, not a page-scoping posting token. For publishing to a Page,
   the automation still needs a Page Access Token with `pages_manage_posts` (and
   `instagram_content_publish` for Instagram) stored in the existing runtime
   secret.
5. Treat the app secret as a bootstrap credential, not the replacement for the
   page token. The app secret itself is long-lived; the token minted from it is
   not.

This keeps the current publishing contract intact while adding a safer bootstrap
path for validation and future maintenance automation.

### GitHub Actions Workflow (`.github/workflows/daily-social.yml`)

```yaml
on:
  schedule:
    - cron: '0 9 * * *'   # Daily 9 AM UTC (3 AM CST)
  workflow_dispatch:        # Manual trigger; exposes dry_run input
    inputs:
      dry_run: { type: choice, options: [false, true] }

jobs:
  daily-post:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - apt-get install ffmpeg
      - astral-sh/setup-uv@v3
      - uv python install 3.11
      - uv sync  (working-directory: automation/)
      - uv run daily-post [--dry-run] --verbose
```

Secrets are injected as env vars in the final step:
`DEEPSEEK_API_KEY` (or Codemie credentials), `FACEBOOK_PAGE_ID`, `FACEBOOK_ACCESS_TOKEN`,
`INSTAGRAM_ACCOUNT_ID`.

### Testing (`tests/`)

The test suite includes both unit tests and live integration tests with LLM-as-grader:

**Unit Tests (default):**
```bash
uv run pytest tests/
```

**Live Integration Tests:**
```bash
# Run live tests with real LLM providers
uv run pytest tests/test_prompts_live.py --live

# Test specific provider
AI_PROVIDER=codemie uv run pytest tests/test_prompts_live.py --live -v

# Run all tests including live
uv run pytest tests/ --live
```

**Test Structure:**
- `conftest.py`: Pytest configuration with `--live` flag
- `test_prompts_live.py`: Live tests using LLM-as-grader for quality validation
- `graders/`: Grading framework with `CodemieGrader` and rubrics

The LLM-as-grader framework validates prompt quality against a rubric including:
- Tone match (25%): Positive, Mexican Spanish, reggae/jazz vibe
- Length (20%): 2-3 sentences as specified
- Content (30%): Includes fun-fact/historical element
- Emoji usage (15%): Appropriate musical emoji
- Language (10%): Correct Spanish grammar

Live tests are opt-in via `--live` flag to manage costs and latency.

## Consequences

### Positive

- **Consistent presence**: Daily posts maintain fan engagement without manual work
- **Low maintenance**: Set-and-forget after initial credential setup
- **Reproducible**: `uv.lock` guarantees identical packages locally and in CI
- **Extensible**: New platforms require only a new `SocialPublisher` subclass
- **Cost-effective**: Deepseek free tier; GitHub Actions free on public repos
- **Resource efficient**: No video encoding/rendering is done on local or CI machines; pre-made video is downloaded and directly published.

### Negative

- **External service dependencies**: Deepseek, Google Drive, Facebook/Instagram APIs
  all introduce availability risk
- **Videos must be pre-prepared**: Pre-made video files need to be uploaded
  to Google Drive and their IDs added to `VIDEOS_CONFIG` before the script can run
- **Facebook token expiry**: Page access tokens expire; long-lived tokens must be
  refreshed periodically (typically every 60 days)

### Neutral

- **Spanish-only content**: Aligns with primary audience (Mexico)

## Future Enhancements

- Add YouTube Shorts / TikTok publishing (new `SocialPublisher` subclasses)
- Implement Facebook token auto-refresh
- Add engagement analytics tracking
- Support story/reel-specific content variants
- Automated A/B testing for prompt variations with statistical significance
- Historical quality tracking dashboard for LLM-as-grader results
- Fine-tuned grading model trained on historical quality assessments
