#!/bin/bash
#
# Generate vertical short-form videos from random images and audio segments.
#
# Usage:
#   ./generate_videos.sh [OUTPUT_DIR] [COUNT] [IMAGES_DIR] [AUDIO_FILE] [ENDING_VIDEO]
#
# Arguments:
#   OUTPUT_DIR     Directory to save generated videos (default: ./output)
#   COUNT          Number of videos to generate (default: 10)
#   IMAGES_DIR     Directory containing source images (default: ./automation/.inputs/images)
#   AUDIO_FILE     Path to long audio file (default: ./automation/.inputs/audio/202604_ensayo_acontra_01.mp3)
#   ENDING_VIDEO   Optional .mp4 file appended after the slideshow segment.
#
# Example:
#   ./generate_videos.sh ./videos 15 ./photos ./music/podcast.mp3 ./final.mp4
#

set -euo pipefail

# Configuration with defaults
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
OUTPUT_DIR="${1:-./output}"
COUNT="${2:-10}"
IMAGES_DIR="${3:-$SCRIPT_DIR/.inputs/images}"
AUDIO_FILE="${4:-$SCRIPT_DIR/.inputs/audio/202604_ensayo_acontra_01.mp3}"
ENDING_VIDEO="${5:-}"
CLIP_DURATION=20
# TikTok and Instagram Reels export preset.
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
VIDEO_FPS=30
VIDEO_CRF=18
VIDEO_PRESET="slow"
AUDIO_BITRATE="192k"
AUDIO_SAMPLE_RATE=44100
ENDING_DURATION_SECONDS=0
EFFECTIVE_CLIP_DURATION="$CLIP_DURATION"
ENDING_VIDEO_ABS=""
CURRENT_TEMP_DIR=""
SLIDESHOW_SECONDS=5
IMAGE_DURATION=1
SLIDESHOW_IMAGES=$((SLIDESHOW_SECONDS / IMAGE_DURATION))

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

if ! command -v ffprobe &>/dev/null; then
    echo "Error: ffprobe is required but not installed." >&2
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

if ! [[ "$COUNT" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: COUNT must be a positive integer, got '$COUNT'." >&2
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

    if [[ "$ENDING_DURATION_SECONDS" -ge "$CLIP_DURATION" ]]; then
        echo "Error: Ending video must be shorter than the ${CLIP_DURATION}s clip duration." >&2
        exit 1
    fi
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
    echo "Clip duration:    $((CLIP_DURATION - ENDING_DURATION_SECONDS))s generated segment (${SLIDESHOW_SECONDS}s slideshow + hold last image) + ${ENDING_DURATION_SECONDS}s appended video"
else
    echo "Clip duration:    ${CLIP_DURATION}s"
fi
echo "Resolution:       ${VIDEO_WIDTH}x${VIDEO_HEIGHT} @ ${VIDEO_FPS}fps"
echo "Export preset:    H.264 High@4.1, CRF ${VIDEO_CRF}, AAC ${AUDIO_BITRATE} stereo @ ${AUDIO_SAMPLE_RATE}Hz"
echo "======================================"
echo ""

# Randomly vary one or more of the main colorchannelmixer coefficients
randomize_value() {
    local base="$1"
    local spread="$2"
    local seed="$RANDOM"
    local value

    value=$(awk -v base="$base" -v spread="$spread" -v seed="$seed" 'BEGIN {
        srand(seed)
        value = base + (rand() * 2 - 1) * spread
        if (value < -0.50) value = -0.50
        if (value > 1.50) value = 1.50
        printf "%.3f", value
    }')

    printf '%s' "$value"
}

frame_filter() {
    local prefix="$1"

    printf 'split=2[%s_bg][%s_fg];[%s_bg]scale=%s:%s:force_original_aspect_ratio=increase:flags=lanczos,crop=%s:%s,boxblur=24:2,eq=brightness=-0.08:saturation=0.85[%s_bg];[%s_fg]scale=%s:%s:force_original_aspect_ratio=decrease:flags=lanczos[%s_fg];[%s_bg][%s_fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p' \
        "$prefix" "$prefix" "$prefix" "$VIDEO_WIDTH" "$VIDEO_HEIGHT" "$VIDEO_WIDTH" "$VIDEO_HEIGHT" "$prefix" "$prefix" "$VIDEO_WIDTH" "$VIDEO_HEIGHT" "$prefix" "$prefix" "$prefix"
}

generate_slideshow_playlist() {
    local playlist_path="$1"
    local hold_duration="$2"
    local image_change_duration="$3"
    local normalized_images_dir="$4"
    local images_count=${#IMAGES[@]}
    local selected_image="${IMAGES[$((RANDOM % images_count))]}"
    local selected_image_abs=""
    local normalized_image=""
    local repeat_count=$((image_change_duration / IMAGE_DURATION))
    local image_index=0

    printf 'ffconcat version 1.0\n' > "$playlist_path"

    normalize_playlist_image() {
        local source_image="$1"
        local output_image="$2"

        ffmpeg -hide_banner -loglevel error \
            -i "$source_image" \
            -frames:v 1 \
            -y "$output_image"
    }

    for ((k = 0; k < repeat_count; k++)); do
        selected_image="${IMAGES[$((RANDOM % images_count))]}"
        selected_image_abs=$(readlink -f "$selected_image")
        normalized_image="$normalized_images_dir/image_$(printf "%03d" "$image_index").png"
        image_index=$((image_index + 1))
        normalize_playlist_image "$selected_image_abs" "$normalized_image"
        printf "file '%s'\n" "$normalized_image" >> "$playlist_path"
        printf "duration %s\n" "$IMAGE_DURATION" >> "$playlist_path"
    done

    if [[ "$hold_duration" -gt 0 ]]; then
        printf "file '%s'\n" "$normalized_image" >> "$playlist_path"
        printf "duration %s\n" "$hold_duration" >> "$playlist_path"
    fi

    if [[ -n "$normalized_image" ]]; then
        printf "file '%s'\n" "$normalized_image" >> "$playlist_path"
    fi
}

# Generate videos sequentially
for ((i = 0; i < COUNT; i++)); do
    # Pick a random start time that keeps the clip inside the audio duration
    START_TIME=$((RANDOM % (MAX_START + 1)))

    # Format start time for ffmpeg
    START_FORMATTED=$(printf "%02d:%02d:%02d" $((START_TIME / 3600)) $(((START_TIME % 3600) / 60)) $((START_TIME % 60)))

    OUTPUT_FILE="$OUTPUT_DIR/$(uuidgen).mp4"

    echo "[$((i + 1))/$COUNT] Generating: $OUTPUT_FILE"
    echo "  Audio start: ${START_FORMATTED} (second $START_TIME)"

    # Select a random filter style profile
    # 0: Sepia (warm vintage)
    # 1: Black & White / Grayscale / Duotone
    # 2: Cool Blue / Teal
    # 3: Warm Orange / Golden
    # 4: Vibrant / Trippy / Cross-process
    STYLE_INDEX=$((RANDOM % 5))
    STYLE_NAME="Sepia"

    # Base coefficients
    RR="0.393"; RG="0.769"; RB="0.189"
    GR="0.349"; GG="0.686"; GB="0.168"
    BR="0.272"; BG="0.534"; BB="0.131"

    case "$STYLE_INDEX" in
        1)
            RR="0.299"; RG="0.587"; RB="0.114"
            GR="0.299"; GG="0.587"; GB="0.114"
            BR="0.299"; BG="0.587"; BB="0.114"
            STYLE_NAME="Black & White"
            ;;
        2)
            RR="0.200"; RG="0.400"; RB="0.200"
            GR="0.200"; GG="0.700"; GB="0.400"
            BR="0.100"; BG="0.300"; BB="0.900"
            STYLE_NAME="Cool Blue / Teal"
            ;;
        3)
            RR="0.800"; RG="0.400"; RB="0.000"
            GR="0.300"; GG="0.700"; GB="0.000"
            BR="0.100"; BG="0.100"; BB="0.300"
            STYLE_NAME="Warm Orange / Golden"
            ;;
        4)
            RR="1.100"; RG="0.100"; RB="-0.100"
            GR="-0.100"; GG="1.100"; GB="0.100"
            BR="0.100"; BG="-0.100"; BB="1.100"
            STYLE_NAME="Vibrant / Trippy"
            ;;
    esac

    echo "  Style profile: $STYLE_NAME"

    AFFECTED_COUNT=$((RANDOM % 5 + 1))
    SELECTED_PARAMS=()

    for ((j = 0; j < AFFECTED_COUNT; j++)); do
        while :; do
            PARAM_INDEX=$((RANDOM % 9))
            PARAM=""
            case "$PARAM_INDEX" in
                0) PARAM="RR" ;;
                1) PARAM="RG" ;;
                2) PARAM="RB" ;;
                3) PARAM="GR" ;;
                4) PARAM="GG" ;;
                5) PARAM="GB" ;;
                6) PARAM="BR" ;;
                7) PARAM="BG" ;;
                8) PARAM="BB" ;;
            esac

            if [[ " ${SELECTED_PARAMS[*]} " != *" $PARAM "* ]]; then
                SELECTED_PARAMS+=("$PARAM")
                break
            fi
        done

        case "$PARAM" in
            RR) RR=$(randomize_value "$RR" 0.15) ;;
            RG) RG=$(randomize_value "$RG" 0.15) ;;
            RB) RB=$(randomize_value "$RB" 0.15) ;;
            GR) GR=$(randomize_value "$GR" 0.15) ;;
            GG) GG=$(randomize_value "$GG" 0.15) ;;
            GB) GB=$(randomize_value "$GB" 0.15) ;;
            BR) BR=$(randomize_value "$BR" 0.15) ;;
            BG) BG=$(randomize_value "$BG" 0.15) ;;
            BB) BB=$(randomize_value "$BB" 0.15) ;;
        esac
    done

    FILTER_STRING="colorchannelmixer=${RR}:${RG}:${RB}:0:${GR}:${GG}:${GB}:0:${BR}:${BG}:${BB}"
    BASE_FILTER=$(frame_filter "base")
    ENDING_FILTER=$(frame_filter "ending")
    BASE_DURATION="$CLIP_DURATION"

    if [[ -n "$ENDING_VIDEO" ]]; then
        BASE_DURATION=$((CLIP_DURATION - ENDING_DURATION_SECONDS))
    fi

    IMAGE_CHANGE_DURATION=$SLIDESHOW_SECONDS
    if [[ "$IMAGE_CHANGE_DURATION" -gt "$BASE_DURATION" ]]; then
        IMAGE_CHANGE_DURATION="$BASE_DURATION"
    fi

    HOLD_DURATION=$((BASE_DURATION - IMAGE_CHANGE_DURATION))
    CURRENT_TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/septimaola-render-XXXXXX")
    TEMP_PLAYLIST="$CURRENT_TEMP_DIR/playlist.txt"
    TEMP_NORMALIZED_IMAGES_DIR="$CURRENT_TEMP_DIR/images"
    TEMP_BASE_VIDEO="$CURRENT_TEMP_DIR/base.mp4"
    TEMP_CONCAT_VIDEO="$CURRENT_TEMP_DIR/joined.mp4"
    mkdir -p "$TEMP_NORMALIZED_IMAGES_DIR"

    generate_slideshow_playlist "$TEMP_PLAYLIST" "$HOLD_DURATION" "$IMAGE_CHANGE_DURATION" "$TEMP_NORMALIZED_IMAGES_DIR"

    echo "  Slideshow: ${IMAGE_CHANGE_DURATION}s of changing images, hold last image for ${HOLD_DURATION}s"

    ffmpeg -hide_banner -loglevel error \
        -f concat -safe 0 -i "$TEMP_PLAYLIST" \
        -c:v libx264 -preset "$VIDEO_PRESET" -crf "$VIDEO_CRF" -profile:v high -level:v 4.1 \
        -vf "${FILTER_STRING},${BASE_FILTER}" \
        -r "$VIDEO_FPS" \
        -pix_fmt yuv420p \
        -t "$BASE_DURATION" \
        -an \
        -y "$TEMP_BASE_VIDEO"

    if [[ -n "$ENDING_VIDEO" ]]; then
        ffmpeg -hide_banner -loglevel error \
            -i "$TEMP_BASE_VIDEO" \
            -i "$ENDING_VIDEO_ABS" \
            -filter_complex "[0:v:0]fps=${VIDEO_FPS},${BASE_FILTER}[v0];[1:v:0]fps=${VIDEO_FPS},${ENDING_FILTER}[v1];[v0][v1]concat=n=2:v=1:a=0[v]" \
            -map "[v]" \
            -c:v libx264 -preset "$VIDEO_PRESET" -crf "$VIDEO_CRF" -profile:v high -level:v 4.1 \
            -movflags +faststart \
            -y "$TEMP_CONCAT_VIDEO"

        ffmpeg -hide_banner -loglevel error \
            -ss "$START_FORMATTED" -i "$AUDIO_FILE" \
            -i "$TEMP_CONCAT_VIDEO" \
            -map 1:v:0 -map 0:a:0 \
            -c:v copy \
            -c:a aac -b:a "$AUDIO_BITRATE" -ac 2 -ar "$AUDIO_SAMPLE_RATE" \
            -t "$CLIP_DURATION" \
            -movflags +faststart \
            -y "$OUTPUT_FILE"
    else
        ffmpeg -hide_banner -loglevel error \
            -ss "$START_FORMATTED" -i "$AUDIO_FILE" \
            -i "$TEMP_BASE_VIDEO" \
            -map 1:v:0 -map 0:a:0 \
            -c:v copy \
            -c:a aac -b:a "$AUDIO_BITRATE" -ac 2 -ar "$AUDIO_SAMPLE_RATE" \
            -t "$CLIP_DURATION" \
            -movflags +faststart \
            -y "$OUTPUT_FILE"
    fi

    cleanup_current_temp_dir

    echo "  Done: $OUTPUT_FILE"
    echo ""
done

echo "======================================"
echo "Video generation complete!"
echo "Generated $COUNT videos in: $OUTPUT_DIR"
echo "======================================"
