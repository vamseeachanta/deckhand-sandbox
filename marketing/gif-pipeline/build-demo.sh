#!/usr/bin/env bash
# build-demo.sh <slug> — inject specs/<slug>.json into template-anim.html ->
# demo-<slug>.html, and compute its DURATION -> demo-<slug>.dur (ms).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
slug="$1"
python3 - "$ROOT" "$slug" <<'PY'
import sys, json
root, slug = sys.argv[1], sys.argv[2]
tpl = open(f'{root}/template-anim.html').read()
spec_txt = open(f'{root}/specs/{slug}.json').read()
spec = json.loads(spec_txt)                       # validate JSON
open(f'{root}/demo-{slug}.html','w').write(tpl.replace('SPEC_PLACEHOLDER', spec_txt))
sp = spec.get('speed', 1) or 1
cur = 3000/sp
for tn in spec['turns']:
    cur += tn.get('hold', 1200 if tn.get('typing') else 3000)/sp
RH = spec['report'].get('hold', 3000)/sp
reportIn = cur + 200/sp; a = reportIn + 600/sp
inEnd = a + RH; toMet = inEnd + 800/sp; metEnd = toMet + RH; toOut = metEnd + 800/sp; outEnd = toOut + RH
closeIn = outEnd + 600/sp; DUR = int(closeIn + 3500/sp)
open(f'{root}/demo-{slug}.dur','w').write(str(DUR))
print(f'demo-{slug}.html DURATION={DUR}ms')
PY
