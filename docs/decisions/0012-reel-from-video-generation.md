# ADR-0012: Reel-from-Video Generation

## Status

Accepted

## Context

The `automation/generate_videos.sh` script generates vertical short-form videos
from still images and an optional ending video. This works well for slideshow-
style content, but the band also has longer performance recordings that could
power a different type of reel — one made entirely from video clips rather than
still images.

The requirement is a second generation script that:

1. Takes a longer main video (e.g., a rehearsal or performance recording).
2. Extracts multiple short, non-overlapping sub-sections from it.
3. Applies random visual effects to each sub-section for variety.
4. Transitions between sub-sections with crossfades for smooth replay.
5. Appends a short branded ending video.
6. Muxes with an MP3 audio track (randomly positioned).

The output is a self-contained vertical reel ready for TikTok / Instagram Reels,
with the same encoding quality standards as the existing slideshow generator.

## Decision

Create a new script `automation/generate_reel_from_video.sh` that implements the
video-to-reel pipeline described above. The script reuses encoding constants and
frame-normalization logic from `generate_videos.sh` to keep output quality
consistent, but replaces the slideshow phase with video sub-section extraction,
randomized effects, and crossfade transitions.

### Requirements

| Requirement | Decision |
|-------------|----------|
| Output shape | Always export strict 1080x1920 vertical video. |
| Output length | Controlled by `CLIP_DURATION` (default 30 s). The ending video is subtracted from this. |
| Sub-sections | 3 non-overlapping segments extracted from the main video. |
| Sub-section duration | Fixed at `SUB_CLIP_DURATION` (5 s each, independent of `CLIP_DURATION`). |
| Ending video | Trim to ~5 s, normalize to target resolution, append after merged sub-sections. |
| Ending video limit | Reject ending videos equal to or longer than `CLIP_DURATION`. |
| Source orientation | Honor source orientation inside the 1080x1920 frame via Lanczos scaling. |
| Frame background | Blurred full-frame version of the same source (matching `generate_videos.sh`). |
| Encoding | H.264 High Profile Level 4.1, CRF 18, slow preset, AAC 192k @ 44.1 kHz stereo. |
| Audio | Random `CLIP_DURATION` segment from the configured MP3 audio file. |
| Transitions | Crossfade (`xfade=transition=fade`) between successive sub-sections. |
| Visual effects | Random per-sub-section color effect (sepia, B&W, cool, warm, vibrate, or pass-through). |

### Implementation Details

The implementation in `automation/generate_reel_from_video.sh` uses these
constants:

| Setting | Value | Purpose |
|---------|-------|---------|
| `VIDEO_WIDTH` | `1080` | TikTok/Reels vertical width. |
| `VIDEO_HEIGHT` | `1920` | TikTok/Reels vertical height. |
| `VIDEO_FPS` | `30` | Stable social-platform frame rate. |
| `VIDEO_CRF` | `18` | High visual quality. |
| `VIDEO_PRESET` | `slow` | Better compression efficiency. |
| `AUDIO_BITRATE` | `192k` | High AAC quality. |
| `AUDIO_SAMPLE_RATE` | `44100` | Standard audio sample rate. |
| `CLIP_DURATION` | `30` | Default total output duration in seconds. |
| `SUB_CLIP_DURATION` | `5` | Fixed duration for each sub-section extracted from main video. |
| `ENDING_TARGET_SECONDS` | `5` | Target duration for the ending video after trim. |
| `TRANSITION_DURATION` | `0.5` | Crossfade duration between sub-sections. |

#### Pipeline Steps

1. **Normalize main video** — scale and pad to 1080x1920 using the reusable
   `frame_filter()` (split, background blur/darken, foreground center, Lanczos
   scaling, `yuv420p`).

2. **Select sub-sections** — divide the normalized video's available time range
   into 3 roughly equal chunks and pick one random start time per chunk. Each
sub-section is `SUB_CLIP_DURATION` (5 s) long. A 1 s gap is enforced between
    sections.

3. **Render sub-sections with effects** — for each sub-section, randomly choose
   one of 6 color effect profiles (0=sepia, 1=B&W, 2=cool/teal, 3=warm/golden,
   4=vibrant/trippy, 5=pass-through). Non-pass-through effects perturb 1–5 color
   matrix coefficients by ±0.15 for organic variation.

4. **Merge with crossfades** — use `xfade=transition=fade:duration=0.5` to
   crossfade between successive sub-sections, producing a single merged video.

5. **Normalize ending video** — trim to ~5 s and apply the same frame filter
   (blurred background, centered foreground).

6. **Concatenate + mux audio** — concat merged sections with ending video, then
   mux a random-positioned MP3 segment. `faststart` is used for streaming.

#### Color Effect Profiles

| Index | Name | Matrix Description |
|-------|------|--------------------|
| 0 | Sepia | Warm brown-tone color-channel mix |
| 1 | Black & White | Luminance-only grayscale |
| 2 | Cool Blue / Teal | Blue-shifted color balance |
| 3 | Warm Orange / Golden | Warm orange/golden tones |
| 4 | Vibrant / Trippy | Boosted saturation with contrast |
| 5 | Pass-through | No color modification (identity) |

Each profile is implemented via `ffmpeg`'s `colorchannelmixer` filter, and
coefficients are randomly perturbed within ±0.15 for non-identity profiles.

### Script Interface

```
usage: generate_reel_from_video.sh [AUDIO_FILE] [MAIN_VIDEO] [ENDING_VIDEO]
                                   [OUTPUT_DIR] [CLIP_DURATION]
```

All arguments are optional. Defaults:
- `AUDIO_FILE`: `automation/.inputs/input.mp3`
- `MAIN_VIDEO`: `automation/.inputs/video_1.mp4`
- `ENDING_VIDEO`: `automation/.inputs/video_1.mp4`
- `OUTPUT_DIR`: `./output`
- `CLIP_DURATION`: `30`

## Consequences

### Positive

- Produces dynamic, effect-rich reels from longer video recordings without
  manual editing.
- Reuses proven encoding constants and frame-normalization logic from
  `generate_videos.sh`, keeping output quality consistent.
- Random color effects and random sub-section selection produce unique output
  on each run, enabling batch generation for variety.
- Crossfade transitions make the sub-section stitching feel intentional rather
  than abrupt.
- Same encoding quality guarantees as the existing slideshow generator (CRF 18,
  Lanczos scaling, `faststart` metadata).

### Negative

- Slower rendering due to multiple intermediate video encodes (normalization,
  per-section effect render, crossfade merge, ending concat).
- Output files can be large because CRF 18 and 192k audio prioritize quality.
- The blurred-background approach crops the background layer, so only the
  centered foreground preserves the full source frame.
- Random sub-section selection may pick less interesting parts of the source
  video.
- Main video must be at least ~3x the per-section duration to satisfy the
  non-overlapping constraint; very short source videos are rejected.

### Neutral

- The script is independent from `generate_videos.sh` — no shared code, just
  copied constants and helpers.
- Temporary render files are isolated per run under `mktemp` and cleaned up
  via a trap.