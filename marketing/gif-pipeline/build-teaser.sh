#!/usr/bin/env bash
# build-teaser.sh <slug> — build a ~15 s teaser variant of specs/<slug>.json by
# injecting a uniform speed scale (env TEASER_SPEED, default 2.3) into the SAME
# engine. Emits demo-<slug>-teaser.html (+ .dur). Render with:
#   SLUG=<slug>-teaser bash render-anim.sh   ->  demos/<slug>-teaser.mp4
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
slug="$1"; SP="${TEASER_SPEED:-2.3}"
python3 - "$ROOT" "$slug" "$SP" <<'PY'
import sys, json
root, slug, sp = sys.argv[1], sys.argv[2], float(sys.argv[3])
tpl = open(f'{root}/template-anim.html').read()
spec = json.loads(open(f'{root}/specs/{slug}.json').read())
spec['speed'] = sp
spec_txt = json.dumps(spec, ensure_ascii=False)
open(f'{root}/demo-{slug}-teaser.html','w').write(tpl.replace('SPEC_PLACEHOLDER', spec_txt))
cur = 3000/sp
for tn in spec['turns']:
    cur += tn.get('hold', 1200 if tn.get('typing') else 3000)/sp
RH = spec['report'].get('hold', 3000)/sp
reportIn = cur + 200/sp; a = reportIn + 600/sp
inEnd = a + RH; toMet = inEnd + 800/sp; metEnd = toMet + RH; toOut = metEnd + 800/sp; outEnd = toOut + RH
closeIn = outEnd + 600/sp; DUR = int(closeIn + 3500/sp)
open(f'{root}/demo-{slug}-teaser.dur','w').write(str(DUR))
print(f'demo-{slug}-teaser.html  speed={sp}  DURATION={DUR}ms (~{DUR/1000:.1f}s)')
PY
