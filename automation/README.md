# Séptima Ola - Daily Social Media Automation

Automated daily posting pipeline for Séptima Ola's social media presence. Generates AI-powered messages with rotating pre-made video assets downloaded from Google Drive, publishing to Facebook and Instagram.

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Local Setup

1. **Clone and enter the automation directory:**
```bash
cd automation
```

2. **Install dependencies with uv:**
```bash
uv sync
```

3. **Create your environment file:**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

4. **Run the daily post script:**
```bash
uv run daily-post
# Or directly:
uv run src/septima_automation/daily_post.py
```

## Credentials Setup

### Deepseek AI

1. Visit [Deepseek Platform](https://platform.deepseek.com/)
2. Create an account and sign in
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key to your `.env` file as `DEEPSEEK_API_KEY`

### Facebook

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app:
   - Select "Business" as app type
   - Choose "Manage Pages and Ads"
3. Add products to your app:
   - **Facebook Login** (not needed for this use case)
   - **Graph API** (included by default)
4. Add the following app credentials to `.env` for bootstrap/validation:
```bash
FACEBOOK_APP_CLIENT_ID=your_app_client_id
FACEBOOK_APP_CLIENT_SECRET=your_app_client_secret
```
5. Get your publishing credentials:
   - **Page ID**: Go to your Facebook Page → Settings → Page Info → Page ID
   - **Page Access Token**: Use a long-lived Page token for publishing

#### Issuing a long-lived Page access token

The automation needs a Page Access Token, not just an app secret. The recommended flow is:

1. In [Graph API Explorer](https://developers.facebook.com/tools/explorer/), select your app.
2. Generate a short-lived user token and grant the required permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
3. Exchange the short-lived user token for a long-lived user token:
```bash
GET https://graph.facebook.com/v18.0/oauth/access_token?\
  client_id=YOUR_APP_ID\
  &client_secret=YOUR_APP_SECRET\
  &grant_type=fb_exchange_token\
  &fb_exchange_token=SHORT_LIVED_USER_TOKEN
```
4. Request the Page token from your user account:
```bash
GET https://graph.facebook.com/v18.0/me/accounts?\
  fields=id,name,access_token\
  &access_token=LONG_LIVED_USER_TOKEN
```
5. Copy the `access_token` for your target Page to `FACEBOOK_ACCESS_TOKEN`.

6. Add the final values to `.env`:
```bash
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_page_access_token
```

> Note: the `client_credentials` flow can mint an app token, but the automation still needs a Page Access Token with the required page permissions to publish successfully.

### Instagram

1. Connect Instagram to Facebook:
   - Go to your Facebook Page → Settings → Instagram
   - Click "Connect Account" and follow the steps
   - Convert to Business or Creator account if prompted
2. Get your Instagram Business Account ID:
   - Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - Query: `GET /me/accounts`
   - Find your page, look for `instagram_business_account` → `id`
3. Grant permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
4. Add to `.env`:
```bash
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
```

### GitHub Secrets (for CI/CD)

Add these secrets to your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add new repository secrets:
   - `DEEPSEEK_API_KEY`
   - `FACEBOOK_PAGE_ID`
   - `FACEBOOK_ACCESS_TOKEN`
   - `INSTAGRAM_ACCOUNT_ID`

## Configuration

### Video Assets

Edit `src/septima_automation/config.py` - `VIDEOS_CONFIG`:

```python
VIDEOS_CONFIG = [
    {
        "slug": "la_estacion",
        "drive_id": "1XYZ...",  # Google Drive direct download ID for the video
        "title": "La Estación",
        "author": "Séptima Ola"
    },
    # Add your video clips
]
```

### Hashtags

Edit `HASHTAGS` in `config.py`:

```python
HASHTAGS = ["#SéptimaOla", "#Reggae", "#Ska", "#Rocksteady", "#MusicaMexicana"]
```

## How It Works

1. **Select Random Asset**: Picks a random pre-made video asset from `VIDEOS_CONFIG`
2. **Generate Message**: Sends prompt to Deepseek API for Spanish message of the day
3. **Download Video**: Downloads the video file using `httpx` to a temporary directory
4. **Publish**: Uploads video to Facebook and Instagram with AI-generated caption

## Testing Locally

Run with verbose logging:
```bash
uv run daily-post --verbose
```

Dry run (generate but don't publish):
```bash
uv run daily-post --dry-run
```

## CI/CD

The workflow runs daily at 9 AM UTC (3 AM Mexico City time):

```yaml
on:
  schedule:
    - cron: '0 9 * * *'
```

Manual trigger available via GitHub Actions "Run workflow" button.

## Troubleshooting

### API Rate Limits

- **Deepseek**: Check your tier limits at platform.deepseek.com
- **Facebook**: Default rate limits apply; script includes basic retry logic
- **Instagram**: Content publishing has additional restrictions

## Video Generation

* [Link to the video assets](https://drive.google.com/drive/folders/1OfduqBHzvJ9G6uAepvidkpydieitTZUj?usp=drive_link)

### Batch Video Generation Script

Use the included `generate_videos.sh` script to create multiple short videos from random images and sequential audio segments.

**Usage:**
```bash
./generate_videos.sh [OUTPUT_DIR] [COUNT] [IMAGES_DIR] [AUDIO_FILE]
```

**Arguments:**
- `OUTPUT_DIR` - Directory to save generated videos (default: `./output`)
- `COUNT` - Number of videos to generate (default: `10`)
- `IMAGES_DIR` - Directory containing source images (default: `./.images`)
- `AUDIO_FILE` - Path to long audio file (default: `./audio.mp3`)

**Examples:**
```bash
# Generate 10 videos using defaults
./generate_videos.sh

# Generate 20 videos to a custom directory
./generate_videos.sh ./videos 20

# Full custom configuration
./generate_videos.sh ./output 15 ./photos ./music/podcast.mp3

# With final recording
./generate_videos.sh ~/Videos/7aOla/random 1 \
  ~/Pictures/7aola ~/Videos/7aOla/20260515_SkaEnLasMontanas.mp3 \
  ~/Pictures/7aola/video_1_fixed.mp4
```

**Requirements:**
- `ffmpeg` installed
- `uuidgen` installed
- Image directory with .jpg, .jpeg, .png, or .webp files
- Audio file at least 10 seconds long

### Manual Video Generation

Generate a short video from an image and audio using ffmpeg directly:

```shell
ffmpeg -loop 1 -i image.jpg -ss 00:00:30 -i audio.mp3 -c:v mpeg4 -vf "scale=-2:720,format=yuv420p" -b:v 1200k -c:a aac -b:a 128k -t 10 "$(uuidgen).mp4"
```

To add text to the video:

```shell
ffmpeg -i input.mp4 -vf "drawtext=text='Track: My Original Song Name':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.5:x=40:y=h-120" -codec:a copy output.mp4
```

Normalize final/any video with the expected format:

```shell
ffmpeg -i ~/Pictures/7aola/video_1.mp4 \
  -c:v mpeg4 -pix_fmt yuv420p -r 25 -video_track_timescale 12800 \
  -s 960x720 -aspect 4:3 -c:a aac -ar 44100 ~/Pictures/7aola/video_1_fixed.mp4
```

## License

Private - For Séptima Ola internal use only.
