#!/usr/bin/env bash
# render-all.sh — build + render every spec in specs/ (or SLUGS="a b c").
# Serialized (each render already fans W Chrome workers internally).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
slugs="${SLUGS:-$(ls "$ROOT"/specs/*.json 2>/dev/null | xargs -n1 basename | sed 's/\.json$//')}"
for s in $slugs; do
  [ -f "$ROOT/specs/$s.json" ] || { echo "SKIP $s (no spec)"; continue; }
  bash "$ROOT/build-demo.sh" "$s" >/dev/null 2>&1 || { echo "BUILD FAIL $s"; continue; }
  SLUG="$s" bash "$ROOT/render-anim.sh" 2>&1 | grep -E "DONE" | sed "s/^/  /"
done
echo "ALL DONE -> $ROOT/demos/"
