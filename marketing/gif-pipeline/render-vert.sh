#!/usr/bin/env bash
# render-vert.sh — render a vertical 9:16 demo (SLUG=<slug>) at 540x960 logical
# -> 1080x1920 MP4 via one-shot Chrome screenshots + ffmpeg. (#434)
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLUG="${SLUG:?set SLUG}"; FPS=${FPS:-24}; W=${W:-10}
TARGET="$ROOT/demo-${SLUG}.html"; DUR=$(cat "$ROOT/demo-${SLUG}.dur")
FRAMEDIR="$ROOT/.frames-${SLUG}"; rm -rf "$FRAMEDIR"; mkdir -p "$FRAMEDIR" "$ROOT/demos"
N=$(( DUR * FPS / 1000 ))
echo "[$SLUG] $N frames @ ${FPS}fps (vertical 1080x1920, DUR=${DUR}ms)"
seq 0 $((N-1)) | xargs -P "$W" -I{} bash -c '
  i="$1"; t=$(( i * 1000 / '"$FPS"' )); ud=$(mktemp -d)
  google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size=540,960 --user-data-dir="$ud" \
    --screenshot="'"$FRAMEDIR"'/f$(printf %05d "$i").png" "file://'"$TARGET"'?t=$t" >/dev/null 2>&1
  rm -rf "$ud"' _ {}
for i in $(seq 0 $((N-1))); do f=$(printf "$FRAMEDIR/f%05d.png" "$i"); [ -f "$f" ] || cp "$(printf "$FRAMEDIR/f%05d.png" $((i-1)))" "$f" 2>/dev/null || true; done
ffmpeg -y -framerate $FPS -i "$FRAMEDIR/f%05d.png" -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -movflags +faststart "$ROOT/demos/${SLUG}.mp4" >/dev/null 2>&1
rm -rf "$FRAMEDIR"
echo "[$SLUG] DONE -> demos/${SLUG}.mp4 ($(ls -lh "$ROOT/demos/${SLUG}.mp4" | awk '{print $5}'))"
