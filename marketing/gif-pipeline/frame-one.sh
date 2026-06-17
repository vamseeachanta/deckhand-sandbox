#!/usr/bin/env bash
# Render one frame of $TARGET (html) at index $1 -> $FRAMEDIR. Sandbox-safe one-shot
# screenshot (no debug port). Called by render-anim.sh with TARGET/FRAMEDIR/FPS in env.
idx="$1"
t=$(( idx * 1000 / ${FPS:-24} ))
ud=$(mktemp -d "${TMPDIR:-/tmp}/cr.XXXXXX")
google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1200,675 --user-data-dir="$ud" \
  --screenshot="${FRAMEDIR}/f$(printf '%05d' "$idx").png" \
  "file://${TARGET}?t=$t" >/dev/null 2>&1
rm -rf "$ud"
