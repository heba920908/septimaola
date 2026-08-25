#!/bin/bash
#
# Generate a vertical short-form video by mixing sub-sections from two source
# videos with an MP3 audio track, random effects, and transitions.
#
# Usage:
#   ./generate_reel_from_video.sh [AUDIO_FILE] [MAIN_VIDEO] [ENDING_VIDEO]
#                                [OUTPUT_DIR] [CLIP_DURATION]
#
# Arguments:
#   AUDIO_FILE      MP3 audio track to mux as the final soundtrack
#                   (default: automation/.inputs/input.mp3).
#   MAIN_VIDEO      Video that will be normalized, then randomly split into
#                   3 sub-sections (default: automation/.inputs/video_1.mp4).
#   ENDING_VIDEO    Short closing video appended at the end – trimmed to ~5 s
#                   if longer (default: automation/.inputs/video_1.mp4).
#   OUTPUT_DIR      Directory to save the generated video (default: ./output).
#   CLIP_DURATION   Total duration of the final output in seconds (default: 30).
#
# Pipeline:
#   1. Randomly pick 3 non-overlapping sub-sections from the main video.
#   2. Extract each sub-section, normalize resolution/frame, and apply a random
#      visual effect (sepia, B&W, cool hues, warm hues, vibrance, or pass-through).
#   3. Concatenate sub-sections with crossfade transitions between them.
#   4. Trim ENDING_VIDEO to ~5 s and normalize it to the target resolution.
#   5. Append the ending video and mux the final MP3 audio segment (random start,
#      CLIP_DURATION length) into the video stream.
#
# Examples:
#   ./generate_reel_from_video.sh
#   ./generate_reel_from_video.sh ./song.mp3 ./my_main.mp4 ./my_ending.mp4
#   ./generate_reel_from_video.sh audio.mp3 main.mp4 ending.mp4 ./videos 90
#

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
AUDIO_FILE="${1:-$SCRIPT_DIR/.inputs/input.mp3}"
MAIN_VIDEO="${2:-$SCRIPT_DIR/.inputs/video_1.mp4}"
ENDING_VIDEO="${3:-$SCRIPT_DIR/.inputs/video_1.mp4}"
OUTPUT_DIR="${4:-./output}"
CLIP_DURATION="${5:-30}"

SUB_CLIP_DURATION=5
ENDING_TARGET_SECONDS=5
TRANSITION_DURATION=0.5

VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
VIDEO_FPS=30
VIDEO_CRF=18
VIDEO_PRESET="slow"
AUDIO_BITRATE="192k"
AUDIO_SAMPLE_RATE=44100

CURRENT_TEMP_DIR=""

cleanup_current_temp_dir() {
    if [[ -n "$CURRENT_TEMP_DIR" && -d "$CURRENT_TEMP_DIR" ]]; then
        rm -rf "$CURRENT_TEMP_DIR"
        CURRENT_TEMP_DIR=""
    fi
}

trap cleanup_current_temp_dir EXIT

# ── dependency checks ────────────────────────────────────────────────────────

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

# ── input validation ─────────────────────────────────────────────────────────

for file_arg in "$MAIN_VIDEO" "$ENDING_VIDEO" "$AUDIO_FILE"; do
    if [[ ! -f "$file_arg" ]]; then
        echo "Error: File '$file_arg' does not exist." >&2
        exit 1
    fi
done

for video_arg in "$MAIN_VIDEO" "$ENDING_VIDEO"; do
    ext="${video_arg##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    if [[ "$ext_lower" != "mp4" && "$ext_lower" != "mov" && "$ext_lower" != "mkv" ]]; then
        echo "Error: '$video_arg' must be an .mp4, .mov, or .mkv file." >&2
        exit 1
    fi
done

if ! [[ "$CLIP_DURATION" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: CLIP_DURATION must be a positive integer, got '$CLIP_DURATION'." >&2
    exit 1
fi

# ── probe durations ──────────────────────────────────────────────────────────

main_duration_raw=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MAIN_VIDEO")
main_duration=${main_duration_raw%.*}
if [[ -z "$main_duration" || "$main_duration" -le 0 ]]; then
    echo "Error: Could not determine MAIN_VIDEO duration." >&2
    exit 1
fi

ending_duration_raw=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$ENDING_VIDEO")
ending_duration=${ending_duration_raw%.*}
if [[ -z "$ending_duration" || "$ending_duration" -le 0 ]]; then
    echo "Error: Could not determine ENDING_VIDEO duration." >&2
    exit 1
fi

audio_duration_raw=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO_FILE")
audio_duration=${audio_duration_raw%.*}
if [[ -z "$audio_duration" || "$audio_duration" -le 0 ]]; then
    echo "Error: Could not determine AUDIO_FILE duration." >&2
    exit 1
fi

# ── derive timing ────────────────────────────────────────────────────────────

if [[ "$ending_duration" -gt "$ENDING_TARGET_SECONDS" ]]; then
    effective_ending="$ENDING_TARGET_SECONDS"
else
    effective_ending="$ending_duration"
fi

if [[ "$effective_ending" -ge "$CLIP_DURATION" ]]; then
    echo "Error: Ending video duration (${effective_ending}s) must be shorter than CLIP_DURATION (${CLIP_DURATION}s)." >&2
    exit 1
fi

remaining_clip=$((CLIP_DURATION - effective_ending))
min_sub_section=3

if [[ "$main_duration" -lt $((min_sub_section * SUB_CLIP_DURATION)) ]]; then
    echo "Error: MAIN_VIDEO (${main_duration}s) is too short – need at least $((min_sub_section * SUB_CLIP_DURATION))s to extract 3 non-overlapping sections of ${SUB_CLIP_DURATION}s each." >&2
    exit 1
fi

# ── helpers ──────────────────────────────────────────────────────────────────

randomize_value() {
    local base="$1"
    local spread="$2"
    local value
    value=$(awk -v base="$base" -v spread="$spread" -v seed="$RANDOM" 'BEGIN {
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

color_filter() {
    local style_index="$1"

    local RR="0.393" RG="0.769" RB="0.189"
    local GR="0.349" GG="0.686" GB="0.168"
    local BR="0.272" BG="0.534" BB="0.131"
    local style_name="Sepia"

    case "$style_index" in
        1)
            RR="0.299"; RG="0.587"; RB="0.114"
            GR="0.299"; GG="0.587"; GB="0.114"
            BR="0.299"; BG="0.587"; BB="0.114"
            style_name="Black & White"
            ;;
        2)
            RR="0.200"; RG="0.400"; RB="0.200"
            GR="0.200"; GG="0.700"; GB="0.400"
            BR="0.100"; BG="0.300"; BB="0.900"
            style_name="Cool Blue / Teal"
            ;;
        3)
            RR="0.800"; RG="0.400"; RB="0.000"
            GR="0.300"; GG="0.700"; GB="0.000"
            BR="0.100"; BG="0.100"; BB="0.300"
            style_name="Warm Orange / Golden"
            ;;
        4)
            RR="1.100"; RG="0.100"; RB="-0.100"
            GR="-0.100"; GG="1.100"; GB="0.100"
            BR="0.100"; BG="-0.100"; BB="1.100"
            style_name="Vibrant / Trippy"
            ;;
        5)
            style_name="Pass-through (no color)"
            ;;
    esac

    if [[ "$style_index" -eq 5 ]]; then
        printf 'null'
    else
        AFFECTED_COUNT=$((RANDOM % 5 + 1))
        local -a SELECTED_PARAMS=()

        for ((k = 0; k < AFFECTED_COUNT; k++)); do
            local PARAM=""
            while :; do
                case $((RANDOM % 9)) in
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

        printf 'colorchannelmixer=%s:%s:%s:0:%s:%s:%s:0:%s:%s:%s' \
            "$RR" "$RG" "$RB" "$GR" "$GG" "$GB" "$BR" "$BG" "$BB"
    fi

    echo "  $style_index → $style_name" >&2
}

# ── banner ───────────────────────────────────────────────────────────────────

echo "======================================"
echo "Reel-from-Video Generation"
echo "======================================"
echo "Main video:      $MAIN_VIDEO (${main_duration}s)"
echo "Ending video:    $ENDING_VIDEO (${ending_duration}s → trimmed to ${effective_ending}s)"
echo "Audio file:      $AUDIO_FILE (${audio_duration}s)"
echo "Output directory:$OUTPUT_DIR"
echo "Clip duration:   ${CLIP_DURATION}s"
echo "Sub-sections:    3 random non-overlapping segments"
echo "Resolution:      ${VIDEO_WIDTH}x${VIDEO_HEIGHT} @ ${VIDEO_FPS}fps"
echo "Export preset:   H.264 High@4.1, CRF ${VIDEO_CRF}, AAC ${AUDIO_BITRATE} stereo @ ${AUDIO_SAMPLE_RATE}Hz"
echo "======================================"
echo ""

mkdir -p "$OUTPUT_DIR"

# ── working directories ──────────────────────────────────────────────────────

CURRENT_TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/septimaola-reel-XXXXXX")
NORM_ENDING="$CURRENT_TEMP_DIR/ending_trim_norm.mp4"
CONCAT_LIST="$CURRENT_TEMP_DIR/concat.txt"
MERGED_VIDEO="$CURRENT_TEMP_DIR/merged_video.mp4"

OUTPUT_FILE="$OUTPUT_DIR/$(uuidgen).mp4"

# ── step 1: pick 3 random non-overlapping sub-sections ───────────────────────

echo "[1/5] Selecting 3 random sub-sections..."

section_len="$SUB_CLIP_DURATION"
total_needed=$((SUB_CLIP_DURATION * 3))
max_start_region=$((main_duration - total_needed))

if [[ "$max_start_region" -lt 1 ]]; then
    echo "Error: Main video (${main_duration}s) too short for 3 sections of ${SUB_CLIP_DURATION}s each." >&2
    exit 1
fi

gap=1
chunk_size=$(( (max_start_region) / 3 ))

declare -a START_TIMES
declare -a END_TIMES

for seg in 0 1 2; do
    chunk_start=$((seg * chunk_size))
    if [[ "$seg" -eq 2 ]]; then
        chunk_end="$max_start_region"
    else
        chunk_end=$(( (seg + 1) * chunk_size - section_len ))
    fi
    if [[ "$chunk_end" -le "$chunk_start" ]]; then
        chunk_end="$chunk_start"
    fi
    start_in_chunk=$(( RANDOM % (chunk_end - chunk_start + 1) + chunk_start ))
    START_TIMES[$seg]="$start_in_chunk"
    END_TIMES[$seg]=$((start_in_chunk + section_len))
    echo "  Section $((seg + 1)): ${START_TIMES[$seg]}s → ${END_TIMES[$seg]}s"
done

echo ""

# ── step 2: extract and normalize sub-sections ───────────────────────────────

echo "[2/5] Extracting and normalizing sub-sections with random effects..."
BASE_FILTER=$(frame_filter "base")

SECTION_FILES=()

for seg in 0 1 2; do
    section_path="$CURRENT_TEMP_DIR/section_${seg}.mp4"
    SECTION_FILES+=("$section_path")

    effect_index=$((RANDOM % 6))
    COLOR_STR=$(color_filter "$effect_index")

    echo "  Section $((seg + 1)) → effect: ${COLOR_STR}"

    FILTER="$BASE_FILTER"
    if [[ "$COLOR_STR" != "null" ]]; then
        FILTER="${COLOR_STR},${BASE_FILTER}"
    fi

    ffmpeg -hide_banner -loglevel error \
        -ss "${START_TIMES[$seg]}" -i "$MAIN_VIDEO" \
        -c:v libx264 -preset "$VIDEO_PRESET" -crf "$VIDEO_CRF" -profile:v high -level:v 4.1 \
        -vf "$FILTER" \
        -r "$VIDEO_FPS" \
        -pix_fmt yuv420p \
        -t "$section_len" \
        -an \
        -y "$section_path"
done

echo ""

# ── step 3: concatenate sub-sections with crossfade transitions ──────────────

echo "[3/5] Merging sub-sections with crossfade transitions..."

offset0=$(awk -v sl="$section_len" -v td="$TRANSITION_DURATION" 'BEGIN { printf "%.3f", sl - td }')
offset1=$(awk -v sl="$section_len" -v td="$TRANSITION_DURATION" 'BEGIN { printf "%.3f", sl * 2 - td * 2 }')

xfade_filter="[0:v][1:v]xfade=transition=fade:duration=${TRANSITION_DURATION}:offset=${offset0}[f0];[f0][2:v]xfade=transition=fade:duration=${TRANSITION_DURATION}:offset=${offset1}[vout]"

ffmpeg -hide_banner -loglevel error \
    -i "${SECTION_FILES[0]}" \
    -i "${SECTION_FILES[1]}" \
    -i "${SECTION_FILES[2]}" \
    -filter_complex "$xfade_filter" \
    -map "[vout]" \
    -c:v libx264 -preset "$VIDEO_PRESET" -crf "$VIDEO_CRF" -profile:v high -level:v 4.1 \
    -r "$VIDEO_FPS" \
    -pix_fmt yuv420p \
    -y "$MERGED_VIDEO"

echo ""

# ── step 4: normalize and trim ending video ──────────────────────────────────

echo "[4/5] Normalizing and trimming ending video to ${effective_ending}s..."
ENDING_FILTER=$(frame_filter "ending")

ffmpeg -hide_banner -loglevel error \
    -i "$ENDING_VIDEO" \
    -c:v libx264 -preset "$VIDEO_PRESET" -crf "$VIDEO_CRF" -profile:v high -level:v 4.1 \
    -vf "${ENDING_FILTER}" \
    -r "$VIDEO_FPS" \
    -pix_fmt yuv420p \
    -t "$effective_ending" \
    -an \
    -y "$NORM_ENDING"

echo ""

# ── step 6: mux video + audio ────────────────────────────────────────────────

echo "[5/5] Appending ending video and muxing audio..."

MAIN_AND_ENDING="$CURRENT_TEMP_DIR/main_and_ending.mp4"

ffmpeg -hide_banner -loglevel error \
    -i "$MERGED_VIDEO" \
    -i "$NORM_ENDING" \
    -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" \
    -map "[v]" \
    -c:v libx264 -preset "$VIDEO_PRESET" -crf "$VIDEO_CRF" -profile:v high -level:v 4.1 \
    -movflags +faststart \
    -y "$MAIN_AND_ENDING"

combined_video_duration_raw=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MAIN_AND_ENDING")
combined_video_duration=${combined_video_duration_raw%.*}

if [[ "$combined_video_duration" -le 0 ]]; then
    echo "Error: Combined video has zero duration." >&2
    exit 1
fi

max_audio_start=$((audio_duration - CLIP_DURATION))
if [[ "$max_audio_start" -le 0 ]]; then
    max_audio_start=0
fi

random_audio_start() {
    local upper_bound="$1"
    local random_value

    if [[ "$upper_bound" -le 0 ]]; then
        printf '0'
        return
    fi

    random_value=$(od -An -N4 -tu4 /dev/urandom | tr -d ' ')
    printf '%d' "$((random_value % (upper_bound + 1)))"
}

audio_start=$(random_audio_start "$max_audio_start")
audio_start_formatted=$(printf "%02d:%02d:%02d" $((audio_start / 3600)) $(((audio_start % 3600) / 60)) $((audio_start % 60)))

echo "  Audio start: ${audio_start_formatted} (second $audio_start)"

ffmpeg -hide_banner -loglevel error \
    -ss "$audio_start_formatted" -i "$AUDIO_FILE" \
    -i "$MAIN_AND_ENDING" \
    -map 1:v:0 -map 0:a:0 \
    -c:v copy \
    -c:a aac -b:a "$AUDIO_BITRATE" -ac 2 -ar "$AUDIO_SAMPLE_RATE" \
    -t "$CLIP_DURATION" \
    -movflags +faststart \
    -y "$OUTPUT_FILE"

cleanup_current_temp_dir

echo ""
echo "======================================"
echo "Done: $OUTPUT_FILE"
echo "======================================"