#!/usr/bin/env bash
# publish-demos.sh [<slug> ...] — push demo updates live (run after rendering).
#
# Canonical client demo URL:  https://vamseeachanta.github.io/deckhand-sandbox/
# Model: binaries live in the 'demos' GitHub Release (stable URLs, --clobber in place);
#        the gh-pages gallery references them with a ?v=<contenthash> cache-bust. So a
#        revision round is: re-render (update.sh) -> this script. The URL never changes;
#        viewers always get the latest. aceengineer.com just deep-links to this URL.
#
# Steps: 1) rebuild the self-contained gallery (USE_RELEASE -> Release URLs + fresh hash),
#        2) --clobber the binaries to the Release, 3) refresh index.html on gh-pages so the
#        new cache-bust takes effect. Outward-facing — run when you intend to publish.
set -uo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO=vamseeachanta/deckhand-sandbox; TAG=demos
slugs="${*:-}"

echo "1/4 regenerate thumbnails (fast gallery load)"
bash "$R/render-thumbs.sh" $slugs >/dev/null

echo "2/4 rebuild gallery (self-contained, Release URLs)"
USE_RELEASE=1 node "$R/build-web-v3.mjs" >/dev/null

echo "3/4 upload binaries + thumbs to the '$TAG' Release (--clobber, stable URLs)"
if [ -z "$slugs" ]; then
  gh release upload "$TAG" "$R"/demos/*.mp4 "$R"/posters/*.png "$R"/thumbs/*.jpg --clobber -R "$REPO"
else
  for s in $slugs; do
    files=("$R/demos/$s.mp4"); [ -f "$R/demos/${s}v.mp4" ] && files+=("$R/demos/${s}v.mp4")
    [ -f "$R/posters/$s.png" ] && files+=("$R/posters/$s.png")
    [ -f "$R/thumbs/$s.jpg" ] && files+=("$R/thumbs/$s.jpg")
    gh release upload "$TAG" "${files[@]}" --clobber -R "$REPO"
  done
fi

echo "4/4 refresh the live page on gh-pages"
# Structure: the gallery lives at the unguessable REVIEW path (link-only, noindex);
# root is a redirect to it (carry any #hash). .review-token holds the path so every
# session deploys the same shape — do NOT push the gallery to root (breaks the redirect).
TOKEN="$(cat "$R/.review-token" 2>/dev/null || true)"
tmp="$(mktemp -d)"
git clone --depth 1 -b gh-pages "https://github.com/$REPO.git" "$tmp/p" >/dev/null 2>&1
if [ -n "$TOKEN" ]; then
  mkdir -p "$tmp/p/$TOKEN"; cp "$R/web-v3/index.html" "$tmp/p/$TOKEN/index.html"
  cat > "$tmp/p/index.html" <<HTML
<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">
<meta http-equiv="refresh" content="0; url=./$TOKEN/">
<title>Deckhand demos</title>
<script>location.replace('./$TOKEN/'+location.hash)</script>
<p style="font:16px -apple-system,sans-serif;padding:28px">Redirecting… <a href="./$TOKEN/">continue →</a></p>
HTML
else
  cp "$R/web-v3/index.html" "$tmp/p/index.html"
fi
touch "$tmp/p/.nojekyll"
git -C "$tmp/p" add -A
if git -C "$tmp/p" -c user.email=vamsir@gmail.com -c user.name=vamseeachanta commit -q -m "Refresh Deckhand demo gallery"; then
  git -C "$tmp/p" push -q origin gh-pages && echo "LIVE: https://vamseeachanta.github.io/deckhand-sandbox/${TOKEN:+$TOKEN/}"
else
  echo "no page change (binaries still refreshed in place)"
fi
rm -rf "$tmp"
