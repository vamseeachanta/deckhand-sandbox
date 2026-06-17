#!/usr/bin/env python3
# compose-cp.py <cp-slug> — Path-B report composer for the cathodic-protection family.
# Reads the workflow's REAL results.yaml + drives GTMReportBuilder -> report.html
# (real numbers + synthesized Plotly charts + the standard report sections).
# Run from the digitalmodel compute checkout's env:
#   uv run --with plotly --with pandas --with pyyaml python compose-cp.py <slug> <out.html>
import sys, yaml, pathlib
sys.path.insert(0, "/mnt/local-analysis/.deckhand-compute/digitalmodel/examples/demos/gtm")
import plotly.graph_objects as go
import pandas as pd
from report_template import GTMReportBuilder

DM = pathlib.Path("/mnt/local-analysis/.deckhand-compute/digitalmodel")
META = {
 "cathodic-protection-pipeline": ("Pipeline CP Design", "Sacrificial-anode screen · DNV-RP-F103", "DNV-RP-F103-2010"),
 "cathodic-protection-jacket":   ("Fixed-Jacket CP Design", "Zone-by-zone anode screen · DNV-RP-B401", "DNV-RP-B401-2021"),
 "cathodic-protection-manifold": ("Subsea-Manifold CP Design", "Sacrificial-anode screen · DNV-RP-B401", "DNV-RP-B401-2021"),
 "cathodic-protection-monopile": ("Offshore-Wind Monopile CP", "30-yr anode screen · DNV-RP-B401", "DNV-RP-B401-2021"),
 "cathodic-protection-fpso":     ("FPSO-Hull CP Design", "External-hull anode estimate · ABS", "ABS offshore guidance"),
}

def num(x):
    try: return float(x)
    except Exception: return None

def compose(slug, out):
    title, subtitle, code = META[slug]
    doc = yaml.safe_load((DM/f"examples/workflows/{slug}/results/input.yml").read_text())
    r = doc["results"]
    b = GTMReportBuilder(title=title, subtitle=subtitle, demo_id=slug.replace("-", "_"),
                         case_count=1, code_refs=[code, "digitalmodel cathodic_protection"])
    # Methodology
    b.add_methodology(
        "<p>Surface-area current demand with coating breakdown over design life "
        "(initial/mean/final), total charge → sacrificial-anode mass, then a "
        "current-output check that the anode bank delivers the final demand.</p>")
    # Assumptions / inputs
    areas = r.get("surface_areas_m2", {})
    an = r.get("anode_requirements", {})
    asum = [f"Standard: {r.get('standard','—')} · design life {r.get('design_life_years','—')} yr",
            "Surface areas (m²): " + ", ".join(f"{k} {v}" for k, v in areas.items() if k != 'total_m2'),
            f"Anode: {an.get('anode_material','Al')} · {an.get('individual_mass_kg','—')} kg each · "
            f"utilisation {an.get('utilization_factor','—')} · capacity {an.get('electrochemical_capacity_Ah_kg','—')} Ah/kg"]
    b.add_assumptions(asum)
    # Results table
    dem = r.get("current_demand_A", {})
    cov = r.get("current_output_verification", {})
    rows = [
        ("Mean protective current", f"{dem.get('total_mean_A','—')} A"),
        ("Final protective current", f"{dem.get('total_final_A','—')} A"),
        ("Required anode mass", f"{an.get('total_mass_kg','—'):,} kg" if num(an.get('total_mass_kg')) else "—"),
        ("Anode count (by mass)", f"{an.get('anode_count','—')}"),
    ]
    if "recommended_anode_count" in r.get("current_output_verification", {}):
        rows.append(("Anode count (by current output)", f"{cov.get('recommended_anode_count')}"))
    if cov:
        rows.append(("Bank current output", f"{cov.get('total_anode_current_output_A','—')} A"))
        rows.append(("Current-output adequate", "Yes" if cov.get("adequate") else "No — increase count"))
    b.add_table("Results — anode design", pd.DataFrame(rows, columns=["Quantity", "Value"]),
                subtitle=f"{r.get('standard','')}")
    # Chart: per-zone current demand (mean vs final)
    zones = [k for k in dem.keys() if isinstance(dem.get(k), dict)]
    if zones:
        fig = go.Figure()
        fig.add_bar(name="Mean", x=zones, y=[num(dem[z].get("I_mean_A")) for z in zones], marker_color="#2BB2A6")
        fig.add_bar(name="Final", x=zones, y=[num(dem[z].get("I_final_A")) for z in zones], marker_color="#0B3D91")
        fig.update_layout(barmode="group", title="Current demand by zone (A)", height=380,
                          template="plotly_white", legend_orientation="h")
        b.add_chart("demand", fig, "Current demand by zone", "Mean vs final over design life")
    # Chart: anode mass / count headline
    fig2 = go.Figure(go.Bar(x=["Required mass (kg)"], y=[num(an.get("total_mass_kg"))], marker_color="#4cc2ff"))
    fig2.update_layout(title=f"Total anode mass — {an.get('anode_count','')} × {an.get('individual_mass_kg','')} kg",
                       height=320, template="plotly_white")
    b.add_chart("mass", fig2, "Sacrificial-anode mass")
    b.add_section("Verdict", f"<p><strong>{an.get('total_mass_kg','—')} kg</strong> of "
                  f"{an.get('anode_material','aluminium')} anodes "
                  f"({an.get('anode_count','—')} × {an.get('individual_mass_kg','—')} kg); mean demand "
                  f"{dem.get('total_mean_A','—')} A, final {dem.get('total_final_A','—')} A. "
                  + ("Current output adequate." if cov.get("adequate") else
                     f"Current-output check governs → use {cov.get('recommended_anode_count','more')} anodes.") + "</p>")
    b.build(out)
    # truthfulness: this is a single deterministic design check, not an overnight parametric sweep
    import re
    html = pathlib.Path(out).read_text()
    html = re.sub(r'<div class="case-badge">.*?</div>',
                  f'<div class="case-badge">{code} · deterministic design check</div>', html, flags=re.S)
    pathlib.Path(out).write_text(html)
    print(f"composed {slug} -> {out}")

if __name__ == "__main__":
    compose(sys.argv[1], sys.argv[2])
