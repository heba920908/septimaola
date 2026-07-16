# ADR-0008: Daily Social Media Automation

## Status

Proposed

## Context

Séptima Ola requires a consistent social media presence to engage with fans and
promote new content. Manual posting is time-consuming and inconsistent. We need
an automated pipeline that:

1. Generates fresh, engaging content daily using AI
2. Features a rotating selection of band photos and music snippets
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
| AI provider | Deepseek (`deepseek-chat`) | Free tier available, OpenAI-compatible API |
| Video generation | `ffmpeg` via subprocess | Broad codec support, available on CI runners |
| Social platforms | Facebook Graph API v18.0, Instagram Graph API | Official APIs |
| Scheduling | GitHub Actions cron (`0 9 * * *`) | Free for public repos, no extra infra |
| Secrets | GitHub Secrets (CI), `dotenv` (local) | Secure and standard |

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
│   ├── ai_client.py            # Deepseek HTTP client
│   ├── selectors.py            # Random image/audio pickers
│   ├── video_generator.py      # ffmpeg wrapper
│   ├── message_generator.py    # Post text builder
│   ├── daily_post.py           # CLI entry point (uv run daily-post)
│   └── social/
│       ├── __init__.py
│       ├── base.py             # Abstract SocialPublisher
│       ├── facebook.py         # Facebook Graph API publisher
│       └── instagram.py        # Instagram Graph API publisher
└── tests/
    └── test_daily_post.py
```

### Dependencies (`pyproject.toml`)

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27.0",        # Async HTTP client
    "python-dotenv>=1.0.0", # .env loading
    "ffmpeg-python>=0.2.0", # ffmpeg subprocess wrapper
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
uv run daily-post --dry-run --verbose    # Generate only, no publishing
uv run daily-post --skip-instagram       # Facebook only
uv run src/septima_automation/daily_post.py  # Direct module invocation

# Tests
uv run pytest tests/
```

### Asset Configuration (`config.py`)

Assets are declared as typed dataclasses. Public URLs are constructed
programmatically from `drive_id` so they never need to be hardcoded.

```python
@dataclass
class ImageAsset:
    slug: str
    drive_id: str
    category: str   # "members" | "gallery" | "promo"

    @property
    def public_url(self) -> str:
        # Google Drive image CDN — same pattern as react/scripts/fetch-images.mjs
        return f"https://lh3.googleusercontent.com/d/{self.drive_id}"

@dataclass
class AudioAsset:
    slug: str
    drive_id: str
    title: str
    author: str

    @property
    def public_url(self) -> str:
        # Google Drive direct download
        return f"https://drive.google.com/uc?export=download&id={self.drive_id}"
```

`IMAGES_CONFIG` mirrors the IDs in `react/scripts/fetch-images.mjs` (members +
gallery). `AUDIO_CONFIG` holds 15-second `.wav` clips — the list is initially
commented-out and must be populated with real Google Drive file IDs before the
script can run.

Additional constants in `config.py`:

```python
HASHTAGS = ["#SéptimaOla", "#Reggae", "#Ska", "#Rocksteady",
            "#MusicaMexicana", "#LaRaza", "#CDMX"]

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL   = "deepseek-chat"

VIDEO_DURATION = 15    # seconds (Instagram feed video limit)
VIDEO_WIDTH    = 1080  # px — square format
VIDEO_HEIGHT   = 1080  # px
VIDEO_FPS      = 30
VIDEO_CODEC    = "libx264"
```

### AI Message Generation (`ai_client.py`)

`DeepseekClient` wraps the Deepseek REST API using `httpx.AsyncClient`.

System prompt (Spanish, fixed per run):
> "Eres un asistente creativo para Séptima Ola, una banda de
> reggae/ska/rocksteady de La Raza, Ciudad de México. Generas mensajes
> inspiradores y auténticos para redes sociales."

User prompt template:
```
Genera un mensaje del día para Séptima Ola...
- Canción destacada: "{title}" por {author}
- Longitud: 2-3 oraciones
- Tono: cercano, auténtico, con groove
- Incluye un emoji musical apropiado
- Idioma: español
Genera solo el mensaje, sin encabezados ni formato adicional.
```

Parameters: `temperature=0.8`, `max_tokens=150`.

### Post Caption Format (`message_generator.py`)

```python
caption = f"""{ai_message}

Canción destacada: {song_title} ({song_author})

{' '.join(random_sample_of_hashtags)}"""
```

A random subset of 4 hashtags is drawn per post for variety.

### Video Generation (`video_generator.py`)

`VideoGenerator` downloads image and audio to temp files, then calls ffmpeg via
`subprocess.run(..., check=True)`.

ffmpeg command breakdown:
```
ffmpeg -y
  -loop 1 -i <image.jpg>          # Loop static image as video source
  -i <audio.wav>                   # Audio input
  -c:v libx264 -preset fast        # H.264 video, fast encode
  -pix_fmt yuv420p                 # Required for Instagram compatibility
  -r 30                            # 30 fps
  -t 15                            # Hard-trim to 15 seconds
  -vf "scale=1080:1080:force_original_aspect_ratio=decrease,
       pad=1080:1080:(ow-iw)/2:(oh-ih)/2"   # Scale + letterbox to 1080×1080
  -c:a aac -b:a 128k               # AAC audio at 128 kbps
  -shortest                        # End at shorter stream
  <output.mp4>
```

Temp files (image, audio) are deleted after encoding regardless of outcome.
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
   accessible video URL and the caption
2. `POST /{ig-user-id}/media_publish` — publish the container

Required permissions: `instagram_basic`, `instagram_content_publish`,
`pages_read_engagement`.

> **Current status**: The Instagram publisher raises `NotImplementedError`
> until a publicly accessible video hosting step is added. In practice the
> video must be reachable by Instagram's servers during container creation.
> The recommended path is to upload the local file to a temporary URL
> (e.g., presigned S3, Cloudinary free tier, or a brief Facebook CDN link)
> before calling the Instagram container endpoint.

### Pipeline Flow (`daily_post.py`)

```
load_dotenv()
│
├─ select_daily_assets()         # Random ImageAsset + AudioAsset
│
├─ DeepseekClient.generate_message()  # AI caption
│
├─ MessageGenerator.generate_post()   # Format full caption
│
├─ VideoGenerator.generate()          # Download assets → ffmpeg → MP4
│
└─ asyncio.gather() — publish concurrently
    ├─ FacebookPublisher.publish(video, caption)
    └─ InstagramPublisher.publish(video, caption)

video_path.unlink()   # Cleanup temp video
print summary
```

Both publishers are awaited concurrently via `asyncio.gather`. Failures on one
platform do not abort the other. Exit code is `0` if at least one platform
published successfully.

CLI flags:
```
--dry-run         Generate content and video; skip publishing
--verbose         Print step-by-step progress
--skip-facebook   Omit Facebook step
--skip-instagram  Omit Instagram step
```

### Environment Variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | `ai_client.py` | Deepseek platform API key |
| `FACEBOOK_PAGE_ID` | `social/facebook.py` | Numeric Facebook Page ID |
| `FACEBOOK_ACCESS_TOKEN` | `social/facebook.py`, `social/instagram.py` | Long-lived Page access token |
| `INSTAGRAM_ACCOUNT_ID` | `social/instagram.py` | Instagram Business Account ID |

Locally sourced from `automation/.env` (gitignored). In CI sourced from
GitHub repository secrets injected as environment variables.

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
`DEEPSEEK_API_KEY`, `FACEBOOK_PAGE_ID`, `FACEBOOK_ACCESS_TOKEN`,
`INSTAGRAM_ACCOUNT_ID`.

## Consequences

### Positive

- **Consistent presence**: Daily posts maintain fan engagement without manual work
- **Low maintenance**: Set-and-forget after initial credential setup
- **Reproducible**: `uv.lock` guarantees identical packages locally and in CI
- **Extensible**: New platforms require only a new `SocialPublisher` subclass
- **Cost-effective**: Deepseek free tier; GitHub Actions free on public repos

### Negative

- **External service dependencies**: Deepseek, Google Drive, Facebook/Instagram APIs
  all introduce availability risk
- **Instagram video hosting gap**: Instagram requires a public URL for video
  container creation; a hosting step is not yet implemented
- **Audio clips must be pre-prepared**: 15-second `.wav` clips need to be uploaded
  to Google Drive and their IDs added to `AUDIO_CONFIG` before the script can run
- **Facebook token expiry**: Page access tokens expire; long-lived tokens must be
  refreshed periodically (typically every 60 days)
- **ffmpeg on CI**: Requires `apt-get install ffmpeg` on each run (~15s overhead)

### Neutral

- **Spanish-only content**: Aligns with primary audience (Mexico)
- **Square 1080×1080 video**: Optimised for Instagram feed; Facebook also
  supports this format without cropping

## Future Enhancements

- Resolve Instagram video hosting gap (presigned URL or Cloudinary upload)
- Add YouTube Shorts / TikTok publishing (new `SocialPublisher` subclasses)
- Implement Facebook token auto-refresh
- Add engagement analytics tracking
- Support story/reel-specific content variants
