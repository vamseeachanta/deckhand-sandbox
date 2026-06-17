#!/usr/bin/env python3
# compose-cp.py <cp-slug> <out.html> — Path-B report composer for the cathodic-
# protection family. Dispatches by result schema: B401 (jacket/manifold/monopile,
# zone-based), F103 (pipeline, attenuation/bracelet), ABS (fpso hull, mass-only).
# Reads the workflow's REAL results.yaml + drives GTMReportBuilder. Run from the
# digitalmodel compute checkout:
#   uv run --with plotly --with pandas --with pyyaml python compose-cp.py <slug> <out>
import sys, re, yaml, pathlib
sys.path.insert(0, "/mnt/local-analysis/.deckhand-compute/digitalmodel/examples/demos/gtm")
import plotly.graph_objects as go
import pandas as pd
from report_template import GTMReportBuilder

DM = pathlib.Path("/mnt/local-analysis/.deckhand-compute/digitalmodel")
TEAL, NAVY, MINT, CYAN = "#2BB2A6", "#0B3D91", "#7af0c0", "#4cc2ff"
META = {
 "cathodic-protection-pipeline": ("Pipeline CP Design", "Sacrificial-anode screen · DNV-RP-F103", "DNV-RP-F103-2010"),
 "cathodic-protection-jacket":   ("Fixed-Jacket CP Design", "Zone-by-zone anode screen · DNV-RP-B401", "DNV-RP-B401-2021"),
 "cathodic-protection-manifold": ("Subsea-Manifold CP Design", "Sacrificial-anode screen · DNV-RP-B401", "DNV-RP-B401-2021"),
 "cathodic-protection-monopile": ("Offshore-Wind Monopile CP", "30-yr anode screen · DNV-RP-B401", "DNV-RP-B401-2021"),
 "cathodic-protection-fpso":     ("FPSO-Hull CP Design", "External-hull anode estimate · ABS", "ABS offshore guidance"),
}
num = lambda x: (float(x) if isinstance(x, (int, float)) else None)
def life_chart(cid, title, vals, unit):
    fig = go.Figure(go.Bar(x=["Initial", "Mean", "Final"], y=vals, marker_color=[MINT, TEAL, NAVY],
                           text=[f"{v}" for v in vals], textposition="outside"))
    fig.update_layout(title=f"{title} ({unit})", height=360, template="plotly_white",
                      yaxis_title=unit, margin=dict(t=54, b=30))
    return cid, fig

def build_b401(b, r):
    b.add_methodology("<p>Current demand per exposure zone = area × density × coating breakdown "
        "(mean &amp; final); total charge over the design life → sacrificial-anode mass; then a "
        "current-output check that the anode bank delivers the final demand.</p>")
    areas = r.get("surface_areas_m2", {}); an = r.get("anode_requirements", {}); cov = r.get("current_output_verification", {})
    dem = r.get("current_demand_A", {})
    b.add_assumptions([
        f"Standard: {r.get('standard','—')} · design life {r.get('design_life_years','—')} yr",
        "Surface areas (m²): " + ", ".join(f"{k} {v}" for k, v in areas.items() if k != 'total_m2'),
        f"Anode: {an.get('anode_material','Al')} · {an.get('individual_mass_kg','—')} kg each · "
        f"utilisation {an.get('utilization_factor','—')} · capacity {an.get('electrochemical_capacity_Ah_kg','—')} Ah/kg"])
    rows = [("Mean current demand", f"{dem.get('total_mean_A','—')} A"),
            ("Final current demand", f"{dem.get('total_final_A','—')} A"),
            ("Required anode mass", f"{an.get('total_mass_kg','—'):,} kg" if num(an.get('total_mass_kg')) else "—"),
            ("Anode count (by mass)", f"{an.get('anode_count','—')}")]
    if cov.get("recommended_anode_count"): rows.append(("Anode count (by current output) — governs", f"{cov['recommended_anode_count']}"))
    if cov: rows += [("Bank current output", f"{cov.get('total_anode_current_output_A','—')} A"),
                     ("Current-output adequate", "Yes" if cov.get("adequate") else "No — count increased")]
    b.add_table("Results — anode design", pd.DataFrame(rows, columns=["Quantity", "Value"]), subtitle=r.get('standard',''))
    zones = [k for k in dem if isinstance(dem.get(k), dict)]
    if zones:
        fig = go.Figure()
        fig.add_bar(name="Mean", x=zones, y=[num(dem[z].get("I_mean_A")) for z in zones], marker_color=TEAL)
        fig.add_bar(name="Final", x=zones, y=[num(dem[z].get("I_final_A")) for z in zones], marker_color=NAVY)
        fig.update_layout(barmode="group", title="Current demand by zone (A)", height=380, template="plotly_white", legend_orientation="h")
        b.add_chart("demand", fig, "Current demand by zone", "Mean vs final over design life")
    if cov and num(cov.get("total_anode_current_output_A")):
        fig2 = go.Figure(go.Bar(x=["Bank current output", "Final demand"],
                                y=[num(cov.get("total_anode_current_output_A")), num(dem.get("total_final_A"))],
                                marker_color=[TEAL, NAVY],
                                text=[cov.get("total_anode_current_output_A"), dem.get("total_final_A")], textposition="outside"))
        fig2.update_layout(title="Current-output check (A)", height=340, template="plotly_white", margin=dict(t=54))
        b.add_chart("output", fig2, "Current-output check", "Anode-bank output must exceed final demand")
    n = cov.get("recommended_anode_count") or an.get("anode_count")
    gov = (f"Current-output check governs → use {cov['recommended_anode_count']} anodes."
           if cov.get("recommended_anode_count") else "Current output adequate.")
    b.add_section("Verdict", f"<p><strong>{an.get('total_mass_kg','—')} kg</strong> of {an.get('anode_material','aluminium')} "
                  f"anodes ({n} × {an.get('individual_mass_kg','—')} kg); mean demand {dem.get('total_mean_A','—')} A, "
                  f"final {dem.get('total_final_A','—')} A. {gov}</p>")

def build_f103(b, r):
    g = r.get("pipeline_geometry_m", {}); cb = r.get("coating_breakdown_factors", {})
    cd = r.get("current_demand_A", {}); an = r.get("anode_requirements", {})
    sp = r.get("anode_spacing_m", {}); att = r.get("attenuation_analysis", {})
    dens = r.get("current_densities_mA_m2", {})
    b.add_methodology("<p>Outer surface-area current demand with coating breakdown over the design life "
        f"(initial {cb.get('initial_factor','—')} / mean {cb.get('mean_factor','—')} / final {cb.get('final_factor','—')}), "
        f"mean current density {dens.get('mean_current_density_A_m2','—')} A/m² ({dens.get('table_reference','DNV-RP-F103')}). "
        "Total charge → bracelet-anode mass; spacing from unit mass; an attenuation check that protection reaches "
        "between anodes.</p>")
    b.add_assumptions([
        f"Pipe: OD {g.get('outer_diameter_m','—')*1000:.1f} mm · WT {g.get('wall_thickness_m','—')*1000:.1f} mm · "
        f"length {g.get('length_m','—')} m · {cb.get('burial_condition','—')} · {cb.get('coating_type','')} coating",
        f"Design life {r.get('design_life_years','—')} yr · outer surface area {g.get('outer_surface_area_m2','—')} m²",
        f"Anode: {an.get('anode_material','Al')} bracelet · {an.get('individual_anode_mass_kg','—')} kg each · "
        f"utilisation {an.get('utilization_factor','—')} · contingency {an.get('contingency_factor','—')} · "
        f"capacity {an.get('anode_capacity_Ah_kg','—')} Ah/kg"])
    rows = [("Outer surface area", f"{g.get('outer_surface_area_m2','—')} m²"),
            ("Current demand (init/mean/final)", f"{cd.get('initial_current_demand_A','—')} / {cd.get('mean_current_demand_A','—')} / {cd.get('final_current_demand_A','—')} A"),
            ("Total charge", f"{cd.get('total_charge_Ah','—'):,.0f} Ah" if num(cd.get('total_charge_Ah')) else "—"),
            ("Required anode mass", f"{an.get('total_anode_mass_kg','—')} kg"),
            ("Anodes fitted", f"{an.get('anode_count','—')} × {an.get('individual_anode_mass_kg','—')} kg = {an.get('actual_total_mass_kg','—')} kg"),
            ("Anode spacing", f"{sp.get('spacing_m','—')} m"),
            ("Protection reach", f"{att.get('protection_reach_m','—')} m (vs {att.get('midpoint_distance_m','—')} m half-spacing)"),
            ("Protection adequate", "Yes" if att.get("protection_adequate") else "No")]
    b.add_table("Results — sacrificial-anode design", pd.DataFrame(rows, columns=["Quantity", "Value"]), subtitle="DNV-RP-F103")
    b.add_chart(*life_chart("demand", "Protective current demand over life",
                [num(cd.get("initial_current_demand_A")), num(cd.get("mean_current_demand_A")), num(cd.get("final_current_demand_A"))], "A"),
                title="Current demand over life")
    # attenuation: reach vs half-spacing
    fig = go.Figure(go.Bar(x=["Protection reach", "Half-spacing"],
                           y=[num(att.get("protection_reach_m")), num(att.get("midpoint_distance_m"))],
                           marker_color=[TEAL, NAVY], text=[att.get("protection_reach_m"), att.get("midpoint_distance_m")], textposition="outside"))
    fig.update_layout(title="Attenuation — reach vs half-spacing (m)", height=340, template="plotly_white", margin=dict(t=54))
    b.add_chart("reach", fig, "Protection reach", "Reach must exceed the anode half-spacing")
    adq = "adequate" if att.get("protection_adequate") else "not adequate"
    b.add_section("Verdict", f"<p><strong>{an.get('total_anode_mass_kg','—')} kg</strong> required, "
        f"{an.get('actual_total_mass_kg','—')} kg fitted ({an.get('anode_count','—')} × {an.get('individual_anode_mass_kg','—')} kg "
        f"bracelets) over the {g.get('length_m','—')} m line; each anode polarises {att.get('protection_reach_m','—')} m vs the "
        f"{att.get('midpoint_distance_m','—')} m half-spacing → {adq}.</p>")

def build_abs(b, r):
    dens = r.get("current_densities_mA_m2", {}); cb = r.get("coating_breakdown_factors", {}); cd = r.get("current_demand_A", {})
    b.add_methodology(f"<p>ABS shallow-water current densities {dens.get('initial','—')} / {dens.get('mean','—')} / "
        f"{dens.get('final','—')} mA/m² (initial/mean/final) over the {cb.get('depth_zone','shallow')} depth zone; coating "
        f"breakdown over the design life (initial {cb.get('initial','—')} / mean {cb.get('mean','—')} / final {cb.get('final','—')}); "
        "current demand = area × density × breakdown; aluminium anode mass from total charge.</p>")
    b.add_assumptions([
        f"FPSO external submerged hull {r.get('surface_area_m2','—')} m² · water depth {r.get('water_depth_m','—')} m "
        f"({r.get('climatic_region','')})",
        f"Design life {r.get('design_life_years','—')} yr",
        f"Aluminium hull anodes · capacity {r.get('anode_current_capacity_Ah_kg','—')} Ah/kg · "
        f"utilisation {r.get('anode_utilisation_factor','—')}"])
    rows = [("Current density (init/mean/final)", f"{dens.get('initial','—')} / {dens.get('mean','—')} / {dens.get('final','—')} mA/m²"),
            ("Coating breakdown (init/mean/final)", f"{cb.get('initial','—')} / {cb.get('mean','—')} / {cb.get('final','—')}"),
            ("Current demand (init/mean/final)", f"{cd.get('initial','—')} / {cd.get('mean','—')} / {cd.get('final','—')} A"),
            ("Anode capacity", f"{r.get('anode_current_capacity_Ah_kg','—')} Ah/kg"),
            ("Required anode mass", f"{r.get('anode_mass_kg','—'):,.0f} kg" if num(r.get('anode_mass_kg')) else "—")]
    b.add_table("Results — external-hull CP", pd.DataFrame(rows, columns=["Quantity", "Value"]), subtitle="ABS offshore guidance")
    b.add_chart(*life_chart("demand", "Protective current demand over life",
                [num(cd.get("initial")), num(cd.get("mean")), num(cd.get("final"))], "A"), title="Current demand over life")
    b.add_chart(*life_chart("dens", "Design current density",
                [num(dens.get("initial")), num(dens.get("mean")), num(dens.get("final"))], "mA/m²"), title="Current density")
    b.add_section("Verdict", f"<p><strong>{r.get('anode_mass_kg','—'):,.0f} kg</strong> of aluminium hull anodes; mean demand "
        f"{cd.get('mean','—')} A, rising to {cd.get('final','—')} A as the coating breaks down over the "
        f"{r.get('design_life_years','—')}-yr life.</p>" if num(r.get('anode_mass_kg')) else "")

def compose(slug, out):
    title, subtitle, code = META[slug]
    r = yaml.safe_load((DM/f"examples/workflows/{slug}/results/input.yml").read_text())["results"]
    b = GTMReportBuilder(title=title, subtitle=subtitle, demo_id=slug.replace("-", "_"),
                         case_count=1, code_refs=[code, "digitalmodel cathodic_protection"])
    schema = "F103" if "pipeline_geometry_m" in r else ("ABS" if "climatic_region" in r else "B401")
    {"B401": build_b401, "F103": build_f103, "ABS": build_abs}[schema](b, r)
    b.build(out)
    html = pathlib.Path(out).read_text()
    html = re.sub(r'<div class="case-badge">.*?</div>',
                  f'<div class="case-badge">{code} · deterministic design check</div>', html, flags=re.S)
    html = html.replace("parametric analysis", "engineering analysis")
    pathlib.Path(out).write_text(html)
    print(f"composed {slug} [{schema}] -> {out}")

if __name__ == "__main__":
    compose(sys.argv[1], sys.argv[2])
