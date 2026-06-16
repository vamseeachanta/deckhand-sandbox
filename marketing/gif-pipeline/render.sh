#!/usr/bin/env bash
# Deterministic marketing-clip render: HTML scenes -> headless Chrome PNGs (HiDPI)
# -> ffmpeg crossfade -> MP4 + GIF. No computer-use, no live channel.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
DIR="$(pwd)"
mkdir -p frames
W=1200; H=675
DSF="${DSF:-2}"    # device scale factor: 2 = crisp 2x capture (2400x1350)
NSCENES=6          # scenes 0..5
XF=0.45            # crossfade seconds
# Per-scene hold seconds. Pacing tuned for technical content: the result scene
# lingers longest; title/closing are shorter. Total ~15s (printed below).
#        s0   s1   s2   s3   s4   s5
DURS=(  2.6  3.0  3.0  2.6  4.0  2.8 )
GIF_W="${GIF_W:-1080}"   # gif width (palette-limited; mp4 is the crisp master)

echo "== screenshotting $NSCENES scenes @ ${DSF}x =="
for s in $(seq 0 $((NSCENES-1))); do
  google-chrome --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --force-device-scale-factor=${DSF} --window-size=${W},${H} \
    --screenshot="frames/scene_${s}.png" \
    "file://${DIR}/demo.html?scene=${s}" >/dev/null 2>&1
  echo "  scene $s captured"
done

# Build ffmpeg inputs + variable-duration xfade filtergraph
inputs=()
for s in $(seq 0 $((NSCENES-1))); do
  inputs+=( -loop 1 -t "${DURS[$s]}" -i "frames/scene_${s}.png" )
done
filter=""; prev="[0:v]"; L="${DURS[0]}"
for s in $(seq 1 $((NSCENES-1))); do
  off=$(echo "$L - $XF" | bc)
  out="[v${s}]"
  filter+="${prev}[${s}:v]xfade=transition=fade:duration=${XF}:offset=${off}${out};"
  prev="$out"
  L=$(echo "$L + ${DURS[$s]} - $XF" | bc)
done
# even-dimension guard for libx264 (works at any DSF)
filter+="${prev}scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p[vout]"
echo "== total video time: ${L}s  (capture ${DSF}x) =="

echo "== encoding MP4 (crisp master) =="
ffmpeg -y "${inputs[@]}" -filter_complex "$filter" -map "[vout]" \
  -r 30 -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart \
  mooring-fatigue-demo.mp4 >/dev/null 2>&1

echo "== encoding GIF (palette for quality, ${GIF_W}px wide) =="
ffmpeg -y -i mooring-fatigue-demo.mp4 -vf "fps=18,scale=${GIF_W}:-1:flags=lanczos,palettegen=stats_mode=diff" pal.png >/dev/null 2>&1
ffmpeg -y -i mooring-fatigue-demo.mp4 -i pal.png \
  -lavfi "fps=18,scale=${GIF_W}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3" \
  -loop 0 mooring-fatigue-demo.gif >/dev/null 2>&1

echo "== done =="
ls -lh mooring-fatigue-demo.mp4 mooring-fatigue-demo.gif
ffprobe -v error -show_entries stream=width,height -of csv=p=0:s=x mooring-fatigue-demo.mp4 | head -1 | xargs -I{} echo "mp4 resolution: {}"
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 mooring-fatigue-demo.mp4 | xargs -I{} echo "mp4 duration: {}s"
