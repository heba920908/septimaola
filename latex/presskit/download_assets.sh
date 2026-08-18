#!/usr/bin/env bash
set -euo pipefail

# This script downloads member images from public Google Drive IDs used in react/src/components/Members.jsx
# Output folder: ./assets

OUT_DIR="./assets"
mkdir -p "$OUT_DIR"

declare -A images=(
  [Sandy_Robinsuell]=11URa6v_EjHpjz9s23eAo8siVFfbRcLkc
  [Alfred_Herrera]=1NLXEkoOz8CcVXXAFOMoCwttNoPVw7t35
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

shared_zip_id="1hYChucBrjdjkYjl1iyFMZohzh4mSEXAC"
shared_zip="$OUT_DIR/septimaola_shared_assets.zip"

echo "Downloading shared ZIP bundle ($shared_zip_id) -> $shared_zip"
COOKIE_JAR=$(mktemp)
CONFIRM_PAGE=$(curl -s -L -c "$COOKIE_JAR" "https://drive.google.com/uc?export=download&id=$shared_zip_id")
CONFIRM_TOKEN=$(printf '%s\n' "$CONFIRM_PAGE" | grep -o 'name="confirm" value="[^"]*"' | sed 's/.*value="\([^"]*\)"/\1/' | head -n 1)
CONFIRM_UUID=$(printf '%s\n' "$CONFIRM_PAGE" | grep -o 'name="uuid" value="[^"]*"' | sed 's/.*value="\([^"]*\)"/\1/' | head -n 1)

if [ -z "$CONFIRM_TOKEN" ]; then
  curl --fail -L -o "$shared_zip" "https://drive.google.com/uc?export=download&id=$shared_zip_id"
else
  DRIVE_DOWNLOAD_URL="https://drive.usercontent.google.com/download?id=$shared_zip_id&export=download&confirm=$CONFIRM_TOKEN"
  if [ -n "$CONFIRM_UUID" ]; then
    DRIVE_DOWNLOAD_URL="$DRIVE_DOWNLOAD_URL&uuid=$CONFIRM_UUID"
  fi
  curl --fail -L -b "$COOKIE_JAR" -o "$shared_zip" "$DRIVE_DOWNLOAD_URL"
fi
rm -f "$COOKIE_JAR"

if file --mime-type "$shared_zip" | grep -qE 'application/(zip|x-zip)|application/octet-stream'; then
  unzip -o "$shared_zip" -d "$OUT_DIR"
  echo "Success: extracted $shared_zip into $OUT_DIR/"
  mv -v $OUT_DIR/7aola/* "$OUT_DIR/"
else
  echo "ERROR: failed to download a valid ZIP archive for ID '$shared_zip_id'" >&2
fi

echo "Done. Downloaded assets are in $OUT_DIR/"
