#!/bin/bash
#
# Generate short videos from random images and sequential audio segments.
#
# Usage:
#   ./generate_videos.sh [OUTPUT_DIR] [COUNT] [IMAGES_DIR] [AUDIO_FILE] [ENDING_VIDEO]
#
# Arguments:
#   OUTPUT_DIR     Directory to save generated videos (default: ./output)
#   COUNT          Number of videos to generate (default: 10)
#   IMAGES_DIR     Directory containing source images (default: ./.images)
#   AUDIO_FILE     Path to long audio file (default: ./audio.mp3)
#   ENDING_VIDEO   Optional .mp4 file to append after each generated clip. When
#                  provided, the generated segment lasts 5s and is followed by
#                  the supplied video.
#
# Example:
#   ./generate_videos.sh ./videos 15 ./photos ./music/podcast.mp3 ./final.mp4
#

set -euo pipefail

# Configuration with defaults
OUTPUT_DIR="${1:-./output}"
COUNT="${2:-10}"
IMAGES_DIR="${3:-./.images}"
AUDIO_FILE="${4:-./audio.mp3}"
ENDING_VIDEO="${5:-}"
CLIP_DURATION=10
# Quality settings tuned to match .inputs/video_1.mp4 (1920x1080, 24fps,
# H.264 High profile, ~13.6 Mbps).
VIDEO_WIDTH=1920
VIDEO_HEIGHT=1080
VIDEO_FPS=24
VIDEO_CRF=18
VIDEO_BITRATE="13000k"
VIDEO_MAXRATE="13000k"
VIDEO_BUFSIZE="26000k"
AUDIO_BITRATE="128k"
ENDING_BASE_DURATION=5
ENDING_DURATION_SECONDS=0
EFFECTIVE_CLIP_DURATION="$CLIP_DURATION"
ENDING_VIDEO_ABS=""
CURRENT_TEMP_DIR=""

cleanup_current_temp_dir() {
    if [[ -n "$CURRENT_TEMP_DIR" && -d "$CURRENT_TEMP_DIR" ]]; then
        rm -rf "$CURRENT_TEMP_DIR"
        CURRENT_TEMP_DIR=""
    fi
}

trap cleanup_current_temp_dir EXIT

# Validate dependencies
if ! command -v ffmpeg &>/dev/null; then
    echo "Error: ffmpeg is required but not installed." >&2
    exit 1
fi

if ! command -v uuidgen &>/dev/null; then
    echo "Error: uuidgen is required but not installed." >&2
    exit 1
fi

# Validate inputs
if [[ ! -d "$IMAGES_DIR" ]]; then
    echo "Error: Images directory '$IMAGES_DIR' does not exist." >&2
    exit 1
fi

if [[ ! -f "$AUDIO_FILE" ]]; then
    echo "Error: Audio file '$AUDIO_FILE' does not exist." >&2
    exit 1
fi

if [[ -n "$ENDING_VIDEO" ]]; then
    if [[ ! -f "$ENDING_VIDEO" ]]; then
        echo "Error: Ending video '$ENDING_VIDEO' does not exist." >&2
        exit 1
    fi

    if [[ "$ENDING_VIDEO" != *.mp4 && "$ENDING_VIDEO" != *.MP4 ]]; then
        echo "Error: Ending video '$ENDING_VIDEO' must be an .mp4 file." >&2
        exit 1
    fi

    ENDING_VIDEO_ABS=$(readlink -f "$ENDING_VIDEO")
    if [[ -z "$ENDING_VIDEO_ABS" || ! -f "$ENDING_VIDEO_ABS" ]]; then
        echo "Error: Could not resolve ending video path '$ENDING_VIDEO'." >&2
        exit 1
    fi

    ENDING_DURATION_RAW=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ENDING_VIDEO_ABS")
    ENDING_DURATION_SECONDS=$(awk -v d="$ENDING_DURATION_RAW" 'BEGIN {
        if (d <= 0) {
            print 0
        } else if (d == int(d)) {
            printf "%d", d
        } else {
            printf "%d", int(d) + 1
        }
    }')

    if [[ "$ENDING_DURATION_SECONDS" -le 0 ]]; then
        echo "Error: Could not determine ending video duration." >&2
        exit 1
    fi

    EFFECTIVE_CLIP_DURATION=$((ENDING_BASE_DURATION + ENDING_DURATION_SECONDS))
fi

# Get all images
mapfile -t IMAGES < <(find "$IMAGES_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) | sort -R)

if [[ ${#IMAGES[@]} -eq 0 ]]; then
    echo "Error: No images found in '$IMAGES_DIR'." >&2
    exit 1
fi

# Get audio duration
AUDIO_DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO_FILE")
AUDIO_DURATION=${AUDIO_DURATION%.*}

if [[ -z "$AUDIO_DURATION" || "$AUDIO_DURATION" -le 0 ]]; then
    echo "Error: Could not determine audio duration." >&2
    exit 1
fi

MAX_START=$((AUDIO_DURATION - EFFECTIVE_CLIP_DURATION))

if [[ $MAX_START -le 0 ]]; then
    echo "Error: Audio file is too short (need at least ${EFFECTIVE_CLIP_DURATION}s)." >&2
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "======================================"
echo "Video Generation Configuration"
echo "======================================"
echo "Output directory: $OUTPUT_DIR"
echo "Videos to create: $COUNT"
echo "Images source:    $IMAGES_DIR (${#IMAGES[@]} images available)"
echo "Audio source:     $AUDIO_FILE (${AUDIO_DURATION}s duration)"
if [[ -n "$ENDING_VIDEO" ]]; then
    echo "Ending video:     $ENDING_VIDEO_ABS"
    echo "Clip duration:    ${ENDING_BASE_DURATION}s generated segment + ${ENDING_DURATION_SECONDS}s appended video"
else
    echo "Clip duration:    ${CLIP_DURATION}s"
fi
echo "Resolution:       ${VIDEO_WIDTH}x${VIDEO_HEIGHT} @ ${VIDEO_FPS}fps"
echo "Video bitrate:    ${VIDEO_BITRATE} (crf ${VIDEO_CRF}, maxrate ${VIDEO_MAXRATE})"
echo "======================================"
echo ""

# Randomly vary one or two of the main colorchannelmixer coefficients
randomize_value() {
    local base="$1"
    local spread="$2"
    local value

    value=$(awk -v base="$base" -v spread="$spread" 'BEGIN {
        value = base + (rand() * 2 - 1) * spread
        if (value < 0.10) value = 0.10
        if (value > 0.95) value = 0.95
        printf "%.3f", value
    }')

    printf '%s' "$value"
}

# Generate videos sequentially
for ((i = 0; i < COUNT; i++)); do
    # Cycle through images randomly
    IMAGE="${IMAGES[$((i % ${#IMAGES[@]}))]}"

    # Pick a random start time that keeps the clip inside the audio duration
    START_TIME=$((RANDOM % (MAX_START + 1)))

    # Format start time for ffmpeg
    START_FORMATTED=$(printf "%02d:%02d:%02d" $((START_TIME / 3600)) $(((START_TIME % 3600) / 60)) $((START_TIME % 60)))

    OUTPUT_FILE="$OUTPUT_DIR/$(uuidgen).mp4"

    echo "[$((i + 1))/$COUNT] Generating: $OUTPUT_FILE"
    echo "  Image: $IMAGE"
    echo "  Audio start: ${START_FORMATTED} (second $START_TIME)"

    RR="0.393"
    RG="0.769"
    GG="0.686"
    BB="0.131"
    AFFECTED_COUNT=$((RANDOM % 2 + 1))
    SELECTED_PARAMS=()

    for ((j = 0; j < AFFECTED_COUNT; j++)); do
        while :; do
            PARAM_INDEX=$((RANDOM % 4))
            PARAM=""
            case "$PARAM_INDEX" in
                0) PARAM="RR" ;;
                1) PARAM="RG" ;;
                2) PARAM="GG" ;;
                3) PARAM="BB" ;;
            esac

            if [[ " ${SELECTED_PARAMS[*]} " != *" $PARAM "* ]]; then
                SELECTED_PARAMS+=("$PARAM")
                break
            fi
        done

        case "$PARAM" in
            RR) RR=$(randomize_value "$RR" 0.08) ;;
            RG) RG=$(randomize_value "$RG" 0.08) ;;
            GG) GG=$(randomize_value "$GG" 0.08) ;;
            BB) BB=$(randomize_value "$BB" 0.08) ;;
        esac
    done

    FILTER_STRING="colorchannelmixer=${RR}:${RG}:0.189:0:0.349:${GG}:0.168:0:0.272:0.534:${BB}"
    BASE_DURATION="$CLIP_DURATION"

    if [[ -n "$ENDING_VIDEO" ]]; then
        BASE_DURATION="$ENDING_BASE_DURATION"
    fi

    if [[ -n "$ENDING_VIDEO" ]]; then
        CURRENT_TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/septimaola-render-XXXXXX")
        TEMP_BASE_VIDEO="$CURRENT_TEMP_DIR/base.mp4"
        TEMP_CONCAT_VIDEO="$CURRENT_TEMP_DIR/joined.mp4"

        ffmpeg -hide_banner -loglevel error \
            -loop 1 -i "$IMAGE" \
            -c:v libx264 -preset veryfast -crf "$VIDEO_CRF" \
            -vf "${FILTER_STRING},scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=increase:out_range=tv,crop=${VIDEO_WIDTH}:${VIDEO_HEIGHT},setsar=1,format=yuv420p" \
            -r "$VIDEO_FPS" \
            -b:v "$VIDEO_BITRATE" -maxrate "$VIDEO_MAXRATE" -bufsize "$VIDEO_BUFSIZE" \
            -an \
            -t "$BASE_DURATION" \
            -y "$TEMP_BASE_VIDEO"

        ffmpeg -hide_banner -loglevel error \
            -i "$TEMP_BASE_VIDEO" \
            -i "$ENDING_VIDEO_ABS" \
            -filter_complex "[0:v:0]fps=${VIDEO_FPS},scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=increase:out_range=tv,crop=${VIDEO_WIDTH}:${VIDEO_HEIGHT},setsar=1,format=yuv420p[v0];[1:v:0]fps=${VIDEO_FPS},scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=increase:out_range=tv,crop=${VIDEO_WIDTH}:${VIDEO_HEIGHT},setsar=1,format=yuv420p[v1];[v0][v1]concat=n=2:v=1:a=0[v]" \
            -map "[v]" \
            -c:v libx264 -preset veryfast -crf "$VIDEO_CRF" \
            -b:v "$VIDEO_BITRATE" -maxrate "$VIDEO_MAXRATE" -bufsize "$VIDEO_BUFSIZE" \
            -y "$TEMP_CONCAT_VIDEO"

        ffmpeg -hide_banner -loglevel error \
            -ss "$START_FORMATTED" -i "$AUDIO_FILE" \
            -i "$TEMP_CONCAT_VIDEO" \
            -map 1:v:0 -map 0:a:0 \
            -c:v copy \
            -c:a aac -b:a "$AUDIO_BITRATE" \
            -shortest \
            -y "$OUTPUT_FILE"

        cleanup_current_temp_dir
    else
        ffmpeg -hide_banner -loglevel error \
            -loop 1 -i "$IMAGE" \
            -ss "$START_FORMATTED" -i "$AUDIO_FILE" \
            -c:v libx264 -preset veryfast -crf "$VIDEO_CRF" \
            -vf "${FILTER_STRING},scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=increase:out_range=tv,crop=${VIDEO_WIDTH}:${VIDEO_HEIGHT},setsar=1,format=yuv420p" \
            -r "$VIDEO_FPS" \
            -b:v "$VIDEO_BITRATE" -maxrate "$VIDEO_MAXRATE" -bufsize "$VIDEO_BUFSIZE" \
            -c:a aac \
            -b:a "$AUDIO_BITRATE" \
            -t "$BASE_DURATION" \
            -y "$OUTPUT_FILE"
    fi

    echo "  Done: $OUTPUT_FILE"
    echo ""
done

echo "======================================"
echo "Video generation complete!"
echo "Generated $COUNT videos in: $OUTPUT_DIR"
echo "======================================"
