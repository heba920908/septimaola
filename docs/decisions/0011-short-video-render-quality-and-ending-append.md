# ADR-0011: Short Video Render Quality and Ending Append

## Status

Accepted

## Context

The `automation/generate_videos.sh` script generates vertical short-form videos
from images, audio, and an optional ending video. The enhanced slideshow flow
introduced two problems:

1. Rendered videos looked low quality after scaling and padding source media to
   the 1080x1920 vertical output frame.
2. When an ending video was provided as the last argument, the generated segment
   was shortened and the ending video effectively replaced the intended final
   image hold. The required behavior is to preserve the last image hold before
   appending the ending video.

The target timing model is:

```text
total_clip = slideshow + last_image_hold + ending_video
```

For example, a 20 second output with a 5 second ending video should render:

```text
5s slideshow + 10s last image hold + 5s ending video
```

## Decision

Keep the generated image segment separate from the optional ending video, then
concatenate both video streams before muxing the final audio. The generated
segment duration remains `CLIP_DURATION - ENDING_DURATION_SECONDS` when an
ending video is provided, but that generated segment itself must still include:

1. A randomized slideshow phase controlled by `SLIDESHOW_SECONDS`.
2. A hold phase using the last selected slideshow image.
3. A final duplicate concat entry so ffmpeg preserves the requested hold
   duration for the last image.

### Requirements

| Requirement | Decision |
|-------------|----------|
| Output shape | Always export strict 1080x1920 vertical video. |
| Output length | Keep the final rendered output at `CLIP_DURATION` seconds. |
| Slideshow timing | Use `SLIDESHOW_SECONDS=5` with one image per second by default. |
| Last image hold | Hold the final slideshow image for the remaining generated segment duration. |
| Ending video behavior | Append the ending video after the held last image, never instead of it. |
| Ending video limit | Reject ending videos that are equal to or longer than `CLIP_DURATION`. |
| Source orientation | Honor image/video source orientation so horizontal media stays horizontal and vertical media stays vertical inside the 1080x1920 frame. |
| Local assets | Use `automation/.inputs/images`, `automation/.inputs/audio/202604_ensayo_acontra_01.mp3`, and `automation/.inputs/video/video_1.mp4` as the documented local asset layout. |
| Audio | Use a random `CLIP_DURATION` segment from the configured audio file. |
| Encoding | Export H.264 High Profile Level 4.1 and AAC for social-platform compatibility. |
| Quality | Prefer sharper scaling and lower compression over smaller files. |

### Implementation Details

The implementation in `automation/generate_videos.sh` uses these constants:

| Setting | Value | Purpose |
|---------|-------|---------|
| `VIDEO_WIDTH` | `1080` | TikTok/Reels vertical width. |
| `VIDEO_HEIGHT` | `1920` | TikTok/Reels vertical height. |
| `VIDEO_FPS` | `30` | Stable social-platform frame rate. |
| `VIDEO_CRF` | `18` | Higher visual quality than the previous CRF 20. |
| `VIDEO_PRESET` | `slow` | Better compression efficiency. |
| `AUDIO_BITRATE` | `192k` | Higher AAC quality than the previous 160k. |
| `SLIDESHOW_SECONDS` | `5` | Initial changing-image phase. |
| `IMAGE_DURATION` | `1` | Per-image slideshow duration. |

The slideshow segment is rendered from a temporary ffconcat playlist generated
by `generate_slideshow_playlist`. Each selected source image is first decoded by
ffmpeg into a temporary PNG so EXIF orientation is applied before the concat
demuxer reads the frame sequence. This prevents horizontal photos from being
treated as vertical frames, and vice versa. The playlist contains randomized
normalized images for the slideshow phase, then repeats the last selected image
for the hold phase. A final duplicate file entry is written because ffmpeg
concat duration metadata requires a following file entry to preserve the final
image duration reliably.

The frame preparation is built by `frame_filter(prefix)` and applied to both the
generated image segment and optional ending video. It:

1. Splits the input into background and foreground streams.
2. Scales and crops the background to fill 1080x1920.
3. Applies blur, slight darkening, and reduced saturation to the background.
4. Scales the foreground with Lanczos while preserving aspect ratio.
5. Centers the foreground over the blurred full-frame background.
6. Normalizes sample aspect ratio and pixel format with `setsar=1` and
   `format=yuv420p`.

When an ending video is provided, the script renders:

```text
TEMP_BASE_VIDEO = slideshow + last image hold
TEMP_CONCAT_VIDEO = TEMP_BASE_VIDEO + ENDING_VIDEO
OUTPUT_FILE = TEMP_CONCAT_VIDEO + random audio segment, trimmed to CLIP_DURATION
```

When no ending video is provided, the script renders:

```text
TEMP_BASE_VIDEO = slideshow + last image hold
OUTPUT_FILE = TEMP_BASE_VIDEO + random audio segment, trimmed to CLIP_DURATION
```

## Consequences

### Positive

- The ending video no longer replaces the held final slideshow image.
- Non-vertical media looks more polished because it uses a blurred full-frame
  background instead of black padding.
- Lanczos scaling and CRF 18 improve perceived sharpness and reduce compression
  artifacts.
- The same frame-normalization path is used for generated media and ending
  videos, making concatenation safer.
- Image EXIF orientation is baked into temporary slideshow frames before concat,
  so source orientation is preserved in the final vertical composition.

### Negative

- Rendering is slower because each clip may require intermediate videos,
  Lanczos scaling, blur, and an additional concat step.
- Output files can be larger because CRF 18 and 192k audio prioritize quality.
- The blurred background intentionally crops the background layer, so only the
  centered foreground preserves the full source frame.
- Image preprocessing adds one short ffmpeg decode per selected slideshow image.

### Neutral

- The final output remains fixed at 20 seconds unless `CLIP_DURATION` changes.
- The default slideshow remains five one-second images followed by a hold.
- Temporary render files are still isolated per clip and removed after each
  output is generated.
