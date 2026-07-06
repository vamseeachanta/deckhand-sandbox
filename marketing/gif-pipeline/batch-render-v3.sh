#!/usr/bin/env bash
# batch-render-v3.sh — render all factory demos (16:9 + 9:16) serially.
set -uo pipefail
R="/mnt/local-analysis/deckhand-sandbox/marketing/gif-pipeline"
SLUGS="cathodic-protection-pipeline cathodic-protection-jacket cathodic-protection-manifold \
cathodic-protection-monopile cathodic-protection-fpso mooring-fatigue fpso-spread-mooring \
hull-seakeeping ocimf-tanker-loads on-bottom-stability-f109 api579-pipe-ffs-b318 \
production-forecast-arps fdas-field-npv nodal-analysis dynacard-diagnostics"
n=0
for s in $SLUGS; do
  n=$((n+1)); echo "=== [$n] $s ==="
  SLUG="$s"  bash "$R/render-anim.sh" 2>&1 | grep -E "DONE|FAIL"
  SLUG="${s}v" bash "$R/render-vert.sh" 2>&1 | grep -E "DONE|FAIL"
done
echo "=== inventory ==="; ls -1 "$R"/demos/*.mp4 | wc -l
echo "BATCH-V3 DONE"
