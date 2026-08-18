#!/usr/bin/env bash
set -euo pipefail

# This script downloads member images from public Google Drive IDs used in react/src/components/Members.jsx
# Output folder: ./assets

OUT_DIR="./assets"
mkdir -p "$OUT_DIR"

declare -A images=(
  [Sandy_Robinsuell]=11URa6v_EjHpjz9s23eAo8siVFfbRcLkc
  [Itzel_BP]=1NyA4KL3OsFB9m2W4u6JS7qcTJ_5-K3Mq
  [Alfred_Herrera]=1NLXEkoOz8CcVXXAFOMoCwttNoPVw7t35
  [Lemanu]=1vZxL4byBgKMExxKbakuZhEgQ2hsFDPVY
  [Levi]=1kh42JDOOif795zfIgig1c3THcWXdvsYq
  [Rodrigo_Mera]=1EXP5Kh_RfxbQLrNVMUn7-Fygg1LrC7Xw
  [Arthur_Mono]=10nWFvuwRtm_hR9LMtT5SmwRO5NCWey30
)

download_from_drive() {
  local file_id="$1"
  local out_path="$2"

  # First attempt via Google Drive direct download endpoint
  curl -L -o "$out_path" "https://drive.google.com/uc?export=download&id=$file_id"

  # If the file is not an image (e.g., HTML warning page), try public image URL fallback
  if ! file --mime-type "$out_path" | grep -qE 'image/'; then
    echo "Warning: first download for $file_id did not look like an image; retrying with `lh3.googleusercontent.com` fallback." >&2
    curl -L -o "$out_path" "https://lh3.googleusercontent.com/d/$file_id"
  fi

  # Final validation
  if ! file --mime-type "$out_path" | grep -qE 'image/'; then
    echo "ERROR: failed to download valid image for ID '$file_id' to '$out_path'" >&2
    return 1
  fi
}

for name in "${!images[@]}"; do
  id="${images[$name]}"
  outfile="$OUT_DIR/${name}.jpg"
  echo "Downloading $name ($id) -> $outfile"
  if download_from_drive "$id" "$outfile"; then
    echo "Success: $outfile"
  else
    echo "Failed: $name ($id)" >&2
  fi
done

echo "Done. Downloaded images are in $OUT_DIR/"
