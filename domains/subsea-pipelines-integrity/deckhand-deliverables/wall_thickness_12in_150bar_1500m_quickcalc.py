#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
SANDBOX_ROOT = OUT_DIR.parents[2]
DIGITALMODEL_REPO = Path(
    os.environ.get('DIGITALMODEL_REPO', SANDBOX_ROOT.parent / 'digitalmodel')
).resolve()
sys.path.insert(0, str(DIGITALMODEL_REPO / 'src'))

from digitalmodel.structural.analysis.wall_thickness import (  # noqa: E402
    DesignCode,
    DesignLoads,
    PipeGeometry,
    PipeMaterial,
)
from digitalmodel.structural.analysis.wall_thickness_comparison import compare_codes  # noqa: E402

OUT_HTML = OUT_DIR / 'wall_thickness_12in_150bar_1500m_with_10in_sensitivity.html'
OUT_JSON = OUT_DIR / 'wall_thickness_12in_150bar_1500m_with_10in_sensitivity.json'

SEAWATER_DENSITY = 1025.0
GRAVITY = 9.81
WATER_DEPTH_M = 1500.0
INTERNAL_PRESSURE_PA = 150e5
CORROSION_ALLOWANCE_M = 0.003
MATERIAL = PipeMaterial(grade='X65', smys=448e6, smts=531e6)
CODES = [c for c in DesignCode if c.value in {'DNV-ST-F101', 'API-RP-1111'}]

CASES = [
    {'label': '12-inch nominal OD', 'outer_diameter_m': 0.3239},
    {'label': '10-inch nominal OD sensitivity', 'outer_diameter_m': 0.2731},
]

def external_pressure(depth_m: float) -> float:
    return SEAWATER_DENSITY * GRAVITY * depth_m

def evaluate(od_m: float, wt_m: float):
    geometry = PipeGeometry(
        outer_diameter=od_m,
        wall_thickness=wt_m,
        corrosion_allowance=CORROSION_ALLOWANCE_M,
    )
    loads = DesignLoads(
        internal_pressure=INTERNAL_PRESSURE_PA,
        external_pressure=external_pressure(WATER_DEPTH_M),
    )
    results = compare_codes(geometry, MATERIAL, loads, codes=CODES)
    max_result = max(results, key=lambda r: r.max_utilisation)
    return results, max_result

def find_min_wt(od_m: float):
    lo = CORROSION_ALLOWANCE_M + 0.001
    hi = 0.080
    # Ensure upper bracket passes.
    _, max_hi = evaluate(od_m, hi)
    if max_hi.max_utilisation > 1.0:
        raise RuntimeError(f'80 mm wall did not pass for OD {od_m}')
    for _ in range(50):
        mid = (lo + hi) / 2
        _, max_mid = evaluate(od_m, mid)
        if max_mid.max_utilisation <= 1.0:
            hi = mid
        else:
            lo = mid
    results, governing = evaluate(od_m, hi)
    return hi, results, governing

def result_to_dict(r):
    return {
        'code_label': r.code_label,
        'max_utilisation': float(r.max_utilisation),
        'governing_check': r.governing_check,
        'is_safe': bool(r.is_safe),
        'checks': {k: float(v) for k, v in r.checks.items()},
    }

def fmt_mm(x):
    return f'{x*1000:.1f}'

def fmt_in_from_m(x):
    return f'{x/0.0254:.3f}'

summary = []
for case in CASES:
    wt, results, governing = find_min_wt(case['outer_diameter_m'])
    summary.append({
        **case,
        'required_wall_m': wt,
        'required_wall_mm': wt * 1000,
        'required_wall_in': wt / 0.0254,
        'governing_code': governing.code_label,
        'governing_check': governing.governing_check,
        'governing_utilisation': float(governing.max_utilisation),
        'code_results': [result_to_dict(r) for r in results],
    })

payload = {
    'computed_at_utc': datetime.now(timezone.utc).isoformat(),
    'basis': {
        'material': 'X65, SMYS 448 MPa, SMTS 531 MPa',
        'internal_pressure_bar': 150.0,
        'water_depth_m': WATER_DEPTH_M,
        'external_pressure_MPa': external_pressure(WATER_DEPTH_M) / 1e6,
        'corrosion_allowance_mm': CORROSION_ALLOWANCE_M * 1000,
        'codes': ['DNV-ST-F101', 'API RP 1111'],
        'method': 'Binary search on nominal wall until max utilisation across both codes <= 1.0',
    },
    'results': summary,
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')

rows = []
for item in summary:
    rows.append(f"""
    <tr>
      <td>{html.escape(item['label'])}</td>
      <td>{item['outer_diameter_m']*1000:.1f}</td>
      <td><strong>{item['required_wall_mm']:.1f}</strong></td>
      <td>{item['required_wall_in']:.3f}</td>
      <td>{html.escape(item['governing_code'])}</td>
      <td>{html.escape(item['governing_check'])}</td>
      <td>{item['governing_utilisation']:.3f}</td>
    </tr>""")

code_rows = []
for item in summary:
    for cr in item['code_results']:
        code_rows.append(f"""
        <tr><td>{html.escape(item['label'])}</td><td>{html.escape(cr['code_label'])}</td><td>{cr['max_utilisation']:.3f}</td><td>{html.escape(str(cr['governing_check']))}</td><td>{'PASS' if cr['is_safe'] else 'FAIL'}</td></tr>""")

html_text = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Pipeline Wall Thickness Quick Check</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2933; line-height: 1.45; }}
h1 {{ color: #0b3d5c; }}
h2 {{ margin-top: 28px; color: #174a66; }}
table {{ border-collapse: collapse; width: 100%; margin: 14px 0; }}
th, td {{ border: 1px solid #c7d2da; padding: 8px 10px; text-align: left; }}
th {{ background: #e8f1f6; }}
.note {{ background: #fff7df; border-left: 4px solid #d99a00; padding: 10px 14px; }}
.pass {{ color: #116329; font-weight: bold; }}
.small {{ color: #52616b; font-size: 0.92em; }}
</style></head>
<body>
<h1>Pipeline Wall Thickness Quick Check</h1>
<p class="small">Computed {html.escape(payload['computed_at_utc'])}. Grounded in the Subsea, Pipelines & Integrity pack and its approved wall-thickness quick-check capability.</p>
<h2>Assumptions</h2>
<ul>
<li>Material: X65, SMYS 448 MPa, SMTS 531 MPa.</li>
<li>Internal pressure: 150 bar; water depth: 1500 m.</li>
<li>External hydrostatic pressure: {payload['basis']['external_pressure_MPa']:.2f} MPa using seawater density 1025 kg/m³ and g = 9.81 m/s².</li>
<li>Corrosion allowance included: 3.0 mm.</li>
<li>Nominal OD cases: 12-inch = 323.9 mm; 10-inch = 273.1 mm.</li>
</ul>
<h2>Headline results</h2>
<table><thead><tr><th>Case</th><th>OD mm</th><th>Minimum nominal WT mm</th><th>WT in</th><th>Governing code</th><th>Governing mode</th><th>Utilisation</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Code check detail at selected wall</h2>
<table><thead><tr><th>Case</th><th>Code</th><th>Max utilisation</th><th>Governing check</th><th>Verdict</th></tr></thead><tbody>{''.join(code_rows)}</tbody></table>
<h2>Design use and limits</h2>
<p>This is a quick-screen minimum nominal wall from the available DNV-ST-F101 / API RP 1111 wall-thickness capability. It is not a purchase wall or issued-for-design recommendation.</p>
<p>Design release would still need project class factors, ovality/manufacturing tolerance, collapse/local buckling detail, installation, thermal/pressure expansion, spans/VIV, stability, fatigue, weld/joint details, corrosion philosophy, and operator/regulator requirements.</p>
<h2>Assumptions &amp; Sensitivity</h2>
<p>The 10-inch OD sensitivity reduces the required nominal wall from {summary[0]['required_wall_mm']:.1f} mm to {summary[1]['required_wall_mm']:.1f} mm on the same pressure, depth, material, and corrosion allowance basis. The governing mode remains DNV-ST-F101 propagation buckling. Higher corrosion allowance, lower material grade, greater depth, or higher design pressure will increase the required wall.</p>
</body></html>"""
OUT_HTML.write_text(html_text, encoding='utf-8')

print(json.dumps(payload, indent=2))
print(f'ARTIFACT: {OUT_HTML}')
print(f'DATA: {OUT_JSON}')
