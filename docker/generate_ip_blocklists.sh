#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Paths relative to script directory
INPUT="$SCRIPT_DIR/ip_blocklists.txt"
OUTPUT="/etc/openresty/block_ips_geo.conf"
TEMP="$SCRIPT_DIR/block_tmp.txt"

rm -f "$TEMP" "$OUTPUT"

# Check that list exists
if [[ ! -f $INPUT ]]; then
    echo "ERROR: $INPUT does not exist!"
    exit 1
fi

# Download all blocklists
while IFS= read -r url; do

    # Skip empty or commented lines
    [[ -z "$url" ]] && continue
    [[ "$url" =~ ^# ]] && continue

    echo "Downloading: $url"

    curl -fsSL "$url" >> "$TEMP" || echo "Failed: $url"

done < "$INPUT"

# Check if anything was downloaded
if [[ ! -s "$TEMP" ]]; then
    echo "ERROR: download failed — TEMP file is empty!"
    exit 1
fi

echo "Cleaning downloaded data…"

grep -vE '^\s*#|^\s*;' "$TEMP" \
| sed '/^\s*$/d' \
| sed 's/[#;].*$//' \
| awk '{print $1}' \
| grep -E '^[0-9a-fA-F:.]+(/[0-9]{1,3})?$' \
| sort -u \
| awk '{print $1 " 1;"}' \
> "$OUTPUT"

rm "$TEMP"

echo "✔ Done"
echo "Final list: $OUTPUT"
wc -l "$OUTPUT"
