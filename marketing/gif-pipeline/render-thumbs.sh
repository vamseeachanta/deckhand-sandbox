#!/usr/bin/env bash
# render-thumbs.sh — representative 640x360 JPG thumbnail per demo, grabbed from a
# real frame ~68% into the 16:9 cut (the report/results view — visually distinct per
# demo). Keeps the gallery fast: cards show a ~30-60KB thumb; the MP4 loads on click.
set -uo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$R/thumbs"
FRAC=0.68
n=0
# Optional slug args → only those thumbs (surgical publish); no args → all specs.
if [ "$#" -gt 0 ]; then specs=(); for s in "$@"; do specs+=("$R/specs/$s.json"); done
else specs=("$R"/specs/*.json); fi
for sp in "${specs[@]}"; do                    # one 16:9 cut per spec slug
  b="$(basename "$sp" .json)"
  v="$R/demos/$b.mp4"
  [ -f "$v" ] || continue
  dur="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v" 2>/dev/null)"
  [ -z "$dur" ] && { echo "  ! no duration for $b"; continue; }
  t="$(awk "BEGIN{printf \"%.2f\", $dur*$FRAC}")"
  ffmpeg -v error -y -ss "$t" -i "$v" -frames:v 1 -vf "scale=640:360" -q:v 4 "$R/thumbs/$b.jpg" && n=$((n+1))
done
echo "thumbs -> $R/thumbs/ ($n)"
