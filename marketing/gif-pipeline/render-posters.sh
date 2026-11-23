#!/usr/bin/env bash
# render-posters.sh — capture one branded poster/thumbnail per demo (the closing
# card: logo + headline + CTA) -> demos/<slug>.poster.png. Good for web/YouTube/
# LinkedIn/email. Set SLUGS="a b c" to limit; defaults to every spec.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
slugs="${SLUGS:-$(ls "$ROOT"/specs/*.json 2>/dev/null | xargs -n1 basename | sed 's/\.json$//')}"
mkdir -p "$ROOT/demos"
for s in $slugs; do
  [ -f "$ROOT/specs/$s.json" ] || { echo "SKIP $s"; continue; }
  bash "$ROOT/build-demo.sh" "$s" >/dev/null 2>&1 || { echo "BUILD FAIL $s"; continue; }
  DUR=$(cat "$ROOT/demo-$s.dur"); t=$(( DUR - 2300 ))   # close card, CTA visible
  ud=$(mktemp -d)
  google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --window-size=1200,675 --user-data-dir="$ud" \
    --screenshot="$ROOT/demos/$s.poster.png" "file://$ROOT/demo-$s.html?t=$t" >/dev/null 2>&1
  rm -rf "$ud"
  echo "  poster -> demos/$s.poster.png ($(ls -lh "$ROOT/demos/$s.poster.png" 2>/dev/null | awk '{print $5}'))"
done
echo "POSTERS DONE"
