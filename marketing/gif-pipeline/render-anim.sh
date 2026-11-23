#!/usr/bin/env bash
# render-anim.sh — render one built demo (SLUG=<spec-slug>) to demos/<slug>.mp4
# via parallel one-shot Chrome screenshots of the in-page animation (?t timeline).
# Header stays fixed; only the chat pane scrolls. Set GIF=1 to also emit a .gif.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export FPS=${FPS:-24}; W=${W:-10}; GIF=${GIF:-0}; GIF_FPS=${GIF_FPS:-15}; GIF_W=${GIF_W:-760}
SLUG="${SLUG:?set SLUG=<spec-slug>}"
export TARGET="$ROOT/demo-${SLUG}.html"
DUR=$(cat "$ROOT/demo-${SLUG}.dur")
export FRAMEDIR="$ROOT/.frames-${SLUG}"
mkdir -p "$ROOT/demos"; rm -rf "$FRAMEDIR"; mkdir -p "$FRAMEDIR"
N=$(( DUR * FPS / 1000 ))
echo "[$SLUG] $N frames @ ${FPS}fps x${W} workers (DUR=${DUR}ms)"
seq 0 $((N-1)) | xargs -P "$W" -I{} bash "$ROOT/frame-one.sh" {}
for i in $(seq 0 $((N-1))); do f=$(printf "$FRAMEDIR/f%05d.png" "$i"); [ -f "$f" ] || cp "$(printf "$FRAMEDIR/f%05d.png" $((i-1)))" "$f" 2>/dev/null || true; done
ffmpeg -y -framerate $FPS -i "$FRAMEDIR/f%05d.png" -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -movflags +faststart "$ROOT/demos/${SLUG}.mp4" >/dev/null 2>&1
if [ "$GIF" = "1" ]; then
  ffmpeg -y -i "$ROOT/demos/${SLUG}.mp4" -vf "fps=${GIF_FPS},scale=${GIF_W}:-1:flags=lanczos,palettegen=stats_mode=diff" "$FRAMEDIR/pal.png" >/dev/null 2>&1
  ffmpeg -y -i "$ROOT/demos/${SLUG}.mp4" -i "$FRAMEDIR/pal.png" -lavfi "fps=${GIF_FPS},scale=${GIF_W}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" -loop 0 "$ROOT/demos/${SLUG}.gif" >/dev/null 2>&1
fi
rm -rf "$FRAMEDIR"
echo "[$SLUG] DONE -> demos/${SLUG}.mp4 ($(ls -lh "$ROOT/demos/${SLUG}.mp4" | awk '{print $5}'))"
