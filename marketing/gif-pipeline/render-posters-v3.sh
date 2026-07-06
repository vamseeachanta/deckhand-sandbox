#!/usr/bin/env bash
# render-posters-v3.sh — branded title-card cover thumbnail per v3 demo
# -> posters/<slug>.png (2400×1350). For gallery / YouTube / email / LinkedIn.
# SLUGS="a b" to limit; defaults to every 16:9 demo-*.html (skips the 9:16 *v).
set -uo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; mkdir -p "$R/posters"
slugs="${SLUGS:-$(ls "$R"/demo-*.html 2>/dev/null | xargs -n1 basename | sed 's/^demo-//;s/\.html$//' | grep -vE 'v$|-teaser$')}"
for s in $slugs; do
  [ -f "$R/demo-$s.html" ] || continue
  out="$s"; [ "$s" = "wt-v3" ] && out="wall-thickness-quickcheck"
  ud=$(mktemp -d)
  google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size=1200,675 --user-data-dir="$ud" --virtual-time-budget=3500 \
    --screenshot="$R/posters/$out.png" "file://$R/demo-$s.html?t=1400" >/dev/null 2>&1
  rm -rf "$ud"
done
echo "posters -> $R/posters/ ($(ls "$R"/posters/*.png 2>/dev/null | wc -l))"
