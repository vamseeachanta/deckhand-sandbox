#!/usr/bin/env bash
# update.sh [<slug> ...] — sustainable update loop for the v3 demos.
# Per slug: make-demo (spec + report -> both cut HTMLs) -> render 16:9 + 9:16.
# Then refresh posters + regenerate the gallery, and PRINT the publish commands
# (publishing is outward-facing / operator-gated, so it's an explicit step).
#
# Sustainable model: binaries live in ONE GitHub Release (stable URLs, --clobber to
# update in place); the gallery points <video> at those URLs with a ?v=<hash> cache-bust;
# every external reference points at the ONE gallery URL, so updates never break links.
set -uo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="vamseeachanta/deckhand-sandbox"; TAG="demos"
slugs="${*:-$(ls "$R"/specs/*.json 2>/dev/null | xargs -n1 basename | sed 's/\.json$//')}"
for s in $slugs; do
  echo "== $s =="
  python3 "$R/make-demo.py" "$s" 2>&1 | tail -1 || { echo "  skip $s (no report?)"; continue; }
  SLUG="$s"   bash "$R/render-anim.sh" 2>&1 | grep -E "DONE|FAIL" | sed 's/^/  /'
  SLUG="${s}v" bash "$R/render-vert.sh" 2>&1 | grep -E "DONE|FAIL" | sed 's/^/  /'
done
SLUGS="$slugs" bash "$R/render-posters-v3.sh"
USE_RELEASE=1 node "$R/build-web-v3.mjs"
echo
echo "Built. To publish (outward-facing — run when ready):"
echo "  gh release create $TAG -R $REPO -t 'Deckhand demos' 2>/dev/null; \\"
echo "  gh release upload $TAG $R/demos/*.mp4 $R/posters/*.png --clobber -R $REPO   # stable URLs, in-place update"
echo "  # then publish web-v3/ to aceengineer.com (content/demos/deckhand/) — operator PR"
