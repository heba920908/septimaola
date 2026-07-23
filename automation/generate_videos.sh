#!/bin/bash
#
# Generate short videos from random images and sequential audio segments.
#
# Usage:
#   ./generate_videos.sh [OUTPUT_DIR] [COUNT] [IMAGES_DIR] [AUDIO_FILE]
#
# Arguments:
#   OUTPUT_DIR   Directory to save generated videos (default: ./output)
#   COUNT        Number of videos to generate (default: 10)
#   IMAGES_DIR   Directory containing source images (default: ./.images)
#   AUDIO_FILE   Path to long audio file (default: ./audio.mp3)
#
# Example:
#   ./generate_videos.sh ./videos 15 ./photos ./music/podcast.mp3
#

set -euo pipefail

# Configuration with defaults
OUTPUT_DIR="${1:-./output}"
COUNT="${2:-10}"
IMAGES_DIR="${3:-./.images}"
AUDIO_FILE="${4:-./audio.mp3}"
CLIP_DURATION=10
VIDEO_HEIGHT=720
VIDEO_BITRATE="1200k"
AUDIO_BITRATE="128k"

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

MAX_START=$((AUDIO_DURATION - CLIP_DURATION))

if [[ $MAX_START -le 0 ]]; then
    echo "Error: Audio file is too short (need at least ${CLIP_DURATION}s)." >&2
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
echo "Clip duration:    ${CLIP_DURATION}s"
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

    ffmpeg -hide_banner -loglevel error \
        -loop 1 -i "$IMAGE" \
        -ss "$START_FORMATTED" -i "$AUDIO_FILE" \
        -c:v mpeg4 \
        -vf "${FILTER_STRING},scale=-2:${VIDEO_HEIGHT},format=yuv420p" \
        -b:v "$VIDEO_BITRATE" \
        -c:a aac \
        -b:a "$AUDIO_BITRATE" \
        -t "$CLIP_DURATION" \
        -y "$OUTPUT_FILE"

    echo "  Done: $OUTPUT_FILE"
    echo ""
done

echo "======================================"
echo "Video generation complete!"
echo "Generated $COUNT videos in: $OUTPUT_DIR"
echo "======================================"
