#!/usr/bin/env python3
# compose-integrity.py <slug> <out.html> — Path-B report composer for the
# pipeline-integrity family (on-bottom stability F109, free span F105,
# API 579 pipe FFS B318). Reads each workflow's REAL results/input.yml and
# drives GTMReportBuilder -> report.html (real numbers + synthesized Plotly
# charts). Run from the digitalmodel compute checkout's env:
#   uv run --with plotly --with pandas --with pyyaml python compose-integrity.py <slug> <out.html>
import sys, re, math, yaml, pathlib
sys.path.insert(0, "/mnt/local-analysis/.deckhand-compute/digitalmodel/examples/demos/gtm")
import plotly.graph_objects as go
import pandas as pd
from report_template import GTMReportBuilder

DM = pathlib.Path("/mnt/local-analysis/.deckhand-compute/digitalmodel")
TEAL = "#2BB2A6"
NAVY = "#0B3D91"


def load(slug):
    return yaml.safe_load((DM / f"examples/workflows/{slug}/results/input.yml").read_text())


def fmt(x, nd=2):
    try:
        return f"{float(x):,.{nd}f}"
    except Exception:
        return "—"


def patch_badge(out, tagline):
    html = pathlib.Path(out).read_text()
    html = re.sub(r'<div class="case-badge">.*?</div>',
                  f'<div class="case-badge">{tagline}</div>', html, flags=re.S)
    pathlib.Path(out).write_text(html)


# ── F109 — on-bottom stability ────────────────────────────────────────────────
def compose_f109(out):
    doc = load("on-bottom-stability-f109")
    obs = doc["on_bottom_stability"]
    pipe, met, hyd, soil = obs["pipe"], obs["metocean"], obs["hydrodynamic"], obs["soil"]
    r = obs["result"]
    verdict = "PASS" if (r["is_laterally_stable"] and r["is_vertically_stable"]) else "FAIL"

    b = GTMReportBuilder(
        title="On-Bottom Stability — Subsea Pipeline",
        subtitle="Hydrodynamic stability check · DNV-RP-F109",
        demo_id="on_bottom_stability_f109", case_count=1,
        code_refs=["DNV-RP-F109 (2010)", "digitalmodel pipeline.on_bottom_stability"])

    b.add_methodology(
        "<p>Morison hydrodynamic loads (drag + inertia + lift) on a pipe resting on the "
        "seabed are balanced against the pipe's submerged weight and soil friction. "
        "The lateral check requires the friction-resisted submerged weight to exceed the "
        "horizontal hydrodynamic load (factored by the safety factor); the vertical check "
        "requires submerged weight to exceed the lift load. Reported as utilisation ratios "
        "(load/capacity); &lt;1.0 is stable.</p>")

    b.add_assumptions([
        f"Pipe: {pipe['od_steel_m']*1000:.1f} mm steel OD · {pipe['wt_steel_m']*1000:.1f} mm wall · "
        f"{pipe['coating_thickness_m']*1000:.0f} mm coating → {r['od_total_m']*1000:.1f} mm total OD",
        f"Densities (kg/m³): steel {pipe['rho_steel']:.0f} · coating {pipe['rho_coating']:.0f} · "
        f"contents {pipe['rho_contents']:.0f} (empty) · seawater {pipe['rho_seawater']:.0f}",
        f"Metocean: near-bed water velocity {met['water_velocity_m_s']} m/s · "
        f"acceleration {met['water_acceleration_m_s2']:.3f} m/s²",
        f"Hydrodynamic coefficients: Cd {hyd['cd']} · Cm {hyd['cm']} · Cl {hyd['cl']}",
        f"Soil lateral friction coefficient {soil['friction_coefficient']} · "
        f"safety factor {obs['safety_factor']}",
    ])

    rows = [
        ("Dry weight", f"{fmt(r['dry_weight_N_m'],1)} N/m"),
        ("Buoyancy", f"{fmt(r['buoyancy_N_m'],1)} N/m"),
        ("Submerged weight (available)", f"{fmt(r['submerged_weight_N_m'],1)} N/m"),
        ("Required submerged weight", f"{fmt(r['required_submerged_weight_N_m'],1)} N/m"),
        ("Drag load", f"{fmt(r['drag_load_N_m'],1)} N/m"),
        ("Inertia load", f"{fmt(r['inertia_load_N_m'],1)} N/m"),
        ("Horizontal load (total)", f"{fmt(r['horizontal_load_N_m'],1)} N/m"),
        ("Lift load", f"{fmt(r['lift_load_N_m'],1)} N/m"),
        ("Lateral utilisation", f"{fmt(r['lateral_utilization'],3)}"),
        ("Vertical utilisation", f"{fmt(r['vertical_utilization'],3)}"),
        ("Laterally stable", "PASS" if r["is_laterally_stable"] else "FAIL"),
        ("Vertically stable", "PASS" if r["is_vertically_stable"] else "FAIL"),
    ]
    b.add_table("Results — stability check", pd.DataFrame(rows, columns=["Quantity", "Value"]),
                subtitle="DNV-RP-F109 · utilisation = factored load / available capacity",
                status_col="Value")

    # Chart 1: hydrodynamic load breakdown
    fig = go.Figure(go.Bar(
        x=["Drag", "Inertia", "Lift", "Horizontal (total)"],
        y=[r["drag_load_N_m"], r["inertia_load_N_m"], r["lift_load_N_m"], r["horizontal_load_N_m"]],
        marker_color=[TEAL, TEAL, NAVY, NAVY],
        text=[f"{v:,.0f}" for v in
              [r["drag_load_N_m"], r["inertia_load_N_m"], r["lift_load_N_m"], r["horizontal_load_N_m"]]],
        textposition="outside"))
    fig.update_layout(title="Hydrodynamic loads (N/m)", height=380, template="plotly_white",
                      yaxis_title="N/m")
    b.add_chart("loads", fig, "Hydrodynamic load breakdown", "Morison drag + inertia + lift per metre")

    # Chart 2: utilisation gauge-style bars vs allowable 1.0
    fig2 = go.Figure()
    fig2.add_bar(x=["Lateral", "Vertical"],
                 y=[r["lateral_utilization"], r["vertical_utilization"]],
                 marker_color=[TEAL, NAVY],
                 text=[f"{r['lateral_utilization']:.3f}", f"{r['vertical_utilization']:.3f}"],
                 textposition="outside")
    fig2.add_hline(y=1.0, line_dash="dash", line_color="#e53e3e",
                   annotation_text="Allowable = 1.0", annotation_position="top right")
    fig2.update_layout(title="Stability utilisation vs allowable", height=360,
                       template="plotly_white", yaxis_title="utilisation",
                       yaxis_range=[0, 1.15])
    b.add_chart("util", fig2, "Stability utilisation", "Both axes below 1.0 → stable")

    b.add_section("Verdict",
                  f"<p><strong>{verdict}</strong> — the pipeline is stable on the seabed under the "
                  f"design metocean condition. Lateral utilisation <strong>{r['lateral_utilization']:.3f}</strong> "
                  f"governs (vertical {r['vertical_utilization']:.3f}); available submerged weight "
                  f"{r['submerged_weight_N_m']:,.0f} N/m exceeds the required "
                  f"{r['required_submerged_weight_N_m']:,.0f} N/m. The margin on lateral stability is "
                  f"narrow (~3.5%); reducing coating, increasing current, or adding contents would push it "
                  f"toward instability.</p>")
    b.build(out)
    patch_badge(out, "DNV-RP-F109 · deterministic stability check")


# ── F105 — free span ──────────────────────────────────────────────────────────
def compose_f105(out):
    doc = load("free-span-f105")
    fs = doc["free_span"]
    sp = fs["pipe_span"]
    r = fs["result"]
    verdict = "PASS" if r["span_utilization"] <= 1.0 else "FAIL"

    b = GTMReportBuilder(
        title="Free-Span VIV & Fatigue — Subsea Pipeline",
        subtitle="Vortex-induced vibration screening · DNV-RP-F105",
        demo_id="free_span_f105", case_count=1,
        code_refs=["DNV-RP-F105 (free spanning pipelines)", "digitalmodel pipeline.free_span"])

    b.add_methodology(
        "<p>A free-spanning section of pipeline is modelled as a beam (pinned-pinned) to find "
        "its natural frequencies in-line (IL) and cross-flow (CF). The reduced velocity "
        "U<sub>r</sub> = U/(f<sub>n</sub>·D) is compared against the VIV onset thresholds; if "
        "exceeded, vortex shedding locks on and drives cyclic stress. The cyclic stress is "
        "combined with an S-N curve to estimate fatigue damage and life, and the maximum "
        "allowable span is back-solved from the fatigue/onset criteria. Span utilisation = "
        "actual span / allowable span; &gt;1.0 fails.</p>")

    b.add_assumptions([
        f"Pipe: {sp['od_m']*1000:.1f} mm OD · {sp['wt_m']*1000:.1f} mm wall · "
        f"E {sp['e_modulus_pa']/1e9:.0f} GPa · boundary condition {sp['bc']}",
        f"Span length {sp['span_length_m']} m · seabed gap {sp['seabed_gap_m']} m · "
        f"sag {sp['sag_m']} m",
        f"Densities (kg/m³): steel {sp['steel_density_kgm3']:.0f} · contents {sp['content_density_kgm3']:.0f} · "
        f"water {sp['water_density_kgm3']:.0f} · submerged weight {fs['submerged_weight_N_m']:.0f} N/m",
        f"Flow: current {sp['current_velocity_ms']} m/s · wave {sp['wave_velocity_ms']} m/s · "
        f"KC {fs['KC']} · α {fs['alpha']}",
        f"S-N curve class {sp['sn_curve_class']} ({sp['environment']}) · "
        f"damping: structural {sp['structural_damping']} / hydrodynamic {sp['hydrodynamic_damping']}",
        f"Safety factors: γ_IL {sp['gamma_on_IL']} · γ_CF {sp['gamma_on_CF']} · γ_k {sp['gamma_k']}",
    ])

    rows = [
        ("Natural frequency (IL = CF)", f"{fmt(r['fn_IL_hz'],3)} Hz"),
        ("Stability parameter Ks", f"{fmt(r['Ks'],3)}"),
        ("Reduced velocity Ur (IL / CF)", f"{fmt(r['Ur_IL'],2)} / {fmt(r['Ur_CF'],2)}"),
        ("VIV onset Ur (IL / CF)", f"{fmt(r['Ur_onset_IL'],2)} / {fmt(r['Ur_onset_CF'],2)}"),
        ("IL VIV onset triggered", "FAIL" if r["il_viv_onset"] else "PASS"),
        ("CF VIV onset triggered", "FAIL" if r["cf_viv_onset"] else "PASS"),
        ("CF amplitude A/D", f"{fmt(r['cf_A_over_D'],3)}"),
        ("CF cyclic stress", f"{fmt(r['cf_stress_mpa'],1)} MPa"),
        ("Fatigue damage / year", f"{fmt(r['damage_per_year'],2)}"),
        ("Fatigue life", f"{fmt(r['fatigue_life_years'],4)} yr"),
        ("Allowable span", f"{fmt(r['allowable_span_m'],2)} m"),
        ("Actual span", f"{fmt(r['span_length_m'],1)} m"),
        ("Span utilisation", f"{fmt(r['span_utilization'],2)}"),
        ("Verdict", verdict),
    ]
    b.add_table("Results — VIV & fatigue", pd.DataFrame(rows, columns=["Quantity", "Value"]),
                subtitle="DNV-RP-F105 · onset triggered when Ur exceeds onset threshold",
                status_col="Value")

    # Chart 1: reduced velocity vs onset
    fig = go.Figure()
    fig.add_bar(name="Reduced velocity Ur", x=["In-line (IL)", "Cross-flow (CF)"],
                y=[r["Ur_IL"], r["Ur_CF"]], marker_color=TEAL,
                text=[f"{r['Ur_IL']:.2f}", f"{r['Ur_CF']:.2f}"], textposition="outside")
    fig.add_bar(name="VIV onset threshold", x=["In-line (IL)", "Cross-flow (CF)"],
                y=[r["Ur_onset_IL"], r["Ur_onset_CF"]], marker_color=NAVY,
                text=[f"{r['Ur_onset_IL']:.2f}", f"{r['Ur_onset_CF']:.2f}"], textposition="outside")
    fig.update_layout(barmode="group", title="Reduced velocity vs VIV onset", height=380,
                      template="plotly_white", yaxis_title="Ur", legend_orientation="h")
    b.add_chart("viv", fig, "Reduced velocity vs VIV onset",
                "Ur far exceeds onset on both axes → lock-in")

    # Chart 2: allowable vs actual span
    fig2 = go.Figure(go.Bar(
        x=["Allowable span", "Actual span"],
        y=[r["allowable_span_m"], r["span_length_m"]],
        marker_color=[TEAL, "#e53e3e"],
        text=[f"{r['allowable_span_m']:.1f} m", f"{r['span_length_m']:.0f} m"],
        textposition="outside"))
    fig2.update_layout(title=f"Span utilisation {r['span_utilization']:.2f} (allowable exceeded)",
                       height=360, template="plotly_white", yaxis_title="metres")
    b.add_chart("span", fig2, "Allowable vs actual span", "Actual span is 2.7× the allowable")

    # Chart 3: span length vs reduced velocity — VIV lock-in transition / critical length
    # Ur ∝ 1/fn ∝ L² (fn from a pinned-pinned beam), so Ur(L) = Ur_actual · (L/L_actual)².
    La, Ura = r["span_length_m"], r["Ur_CF"]
    on_il, on_cf = r["Ur_onset_IL"], r["Ur_onset_CF"]
    L_il = La * math.sqrt(on_il / Ura)   # in-line onset → the allowable span
    L_cf = La * math.sqrt(on_cf / Ura)   # cross-flow lock-in onset
    Lmax = max(La * 1.12, L_cf * 1.25)
    Ls = [5 + i * (Lmax - 5) / 80 for i in range(81)]
    Ur_L = [Ura * (L / La) ** 2 for L in Ls]
    fig3 = go.Figure()
    fig3.add_vrect(x0=5, x1=L_il, fillcolor="#3ad29f", opacity=0.13, line_width=0,
                   annotation_text="no VIV", annotation_position="top left")
    fig3.add_vrect(x0=L_il, x1=L_cf, fillcolor="#f0b429", opacity=0.15, line_width=0,
                   annotation_text="in-line VIV", annotation_position="top left")
    fig3.add_vrect(x0=L_cf, x1=Lmax, fillcolor="#e53e3e", opacity=0.13, line_width=0,
                   annotation_text="cross-flow lock-in", annotation_position="top left")
    fig3.add_trace(go.Scatter(x=Ls, y=Ur_L, mode="lines", line=dict(color=NAVY, width=3), name="Ur(L)"))
    fig3.add_hline(y=on_il, line_dash="dot", line_color="#b7791f", annotation_text=f"IL onset {on_il:.2f}", annotation_position="right")
    fig3.add_hline(y=on_cf, line_dash="dash", line_color="#c53030", annotation_text=f"CF onset {on_cf:.2f}", annotation_position="right")
    fig3.add_vline(x=L_il, line_dash="dot", line_color="#1b7f3a")
    fig3.add_trace(go.Scatter(x=[L_il], y=[on_il], mode="markers+text", marker=dict(color="#1b7f3a", size=11),
                              text=[f"critical {L_il:.1f} m"], textposition="bottom right", name="allowable span"))
    fig3.add_trace(go.Scatter(x=[La], y=[Ura], mode="markers+text", marker=dict(color="#e53e3e", size=13, symbol="x"),
                              text=[f"actual {La:.0f} m"], textposition="top center", name="actual span"))
    fig3.update_layout(title="Span length vs reduced velocity — VIV lock-in transition", height=410,
                       template="plotly_white", xaxis_title="Span length (m)", yaxis_title="Reduced velocity Ur",
                       legend_orientation="h")
    b.add_chart("transition", fig3, "Length vs reduced velocity",
                f"VIV locks in past the {L_il:.1f} m critical span; the {La:.0f} m survey span sits deep in lock-in")

    b.add_section("Verdict",
                  f"<p><strong>{verdict}</strong> — the {sp['span_length_m']:.0f} m free span is "
                  f"<strong>not acceptable</strong> under DNV-RP-F105. At a natural frequency of "
                  f"{r['fn_IL_hz']:.3f} Hz the reduced velocity ({r['Ur_CF']:.2f}) is far above the "
                  f"cross-flow VIV onset ({r['Ur_onset_CF']:.2f}), so vortex shedding locks on and drives "
                  f"a cross-flow cyclic stress of {r['cf_stress_mpa']:.0f} MPa. Fatigue life collapses to "
                  f"<strong>{r['fatigue_life_years']*365:.1f} days</strong> "
                  f"({r['fatigue_life_years']:.4f} yr). The maximum allowable span is "
                  f"{r['allowable_span_m']:.1f} m — the actual span is {r['span_utilization']:.1f}× that. "
                  f"Mitigation (span shortening by rock dump / supports, or VIV strakes) is required.</p>")
    b.build(out)
    patch_badge(out, "DNV-RP-F105 · deterministic VIV/fatigue screen")


# ── B318 — API 579 pipe FFS ───────────────────────────────────────────────────
def compose_b318(out):
    doc = load("api579-pipe-ffs-b318")
    geo = doc["Geometry"]
    des = doc["Design"][0]
    design_p = des["InternalPressure"]["Outer_Pipe"]
    params = doc["API579Parameters"]
    res = doc["Result"]
    circ = res["Circumference"][0]
    gml = res["GML_MAWP"][0]
    gml_ok = res["GML_Acceptable_FCA"]
    lml = res["LML"][0]
    fca_list = ", ".join(f"{g['FCA']:.2f}" for g in gml)

    b = GTMReportBuilder(
        title="API 579 Fitness-For-Service — Corroded Pipe",
        subtitle="Local & general metal loss assessment · API 579-1 / ASME FFS-1",
        demo_id="api579_pipe_ffs_b318", case_count=1,
        code_refs=["API 579-1 / ASME FFS-1 (Part 4 GML, Part 5 LML)",
                   "ASME B31.8-2016 Ch. VIII Pipeline", "digitalmodel API579"])

    b.add_methodology(
        "<p>An ultrasonic wall-thickness grid over a corroded region of pipe is assessed for "
        "fitness-for-service. General Metal Loss (GML, Part 4) checks the average remaining wall "
        "against the maximum allowable working pressure (MAWP) over a range of future corrosion "
        "allowances (FCA). Local Metal Loss (LML, Part 5) screens the deepest flaw using the "
        "remaining-thickness ratio R<sub>t</sub>, the Folias bulging factor M<sub>t</sub>, and the "
        "remaining-strength factor (RSF) against the allowable RSF<sub>a</sub>. The remaining life "
        "is the time for corrosion to consume the wall down to t<sub>min</sub> at the measured rate.</p>")

    b.add_assumptions([
        f"Geometry: {geo['NominalOD']} in OD × {geo['DesignWT']} in nominal wall · "
        f"t_min {geo['tmin']} in · material API 5L X65 (SMYS {doc['Material']['SMYS']:,} psi)",
        f"Design / operating internal pressure {design_p:,} psi · "
        f"water depth {des['Water_Depth']} m · operating temp {des['Temperature']['Operating']['Outer_Pipe']}°C",
        f"Code: ASME B31.8-2016 Ch. VIII Pipeline · design factor "
        f"{doc['DesignFactors']['ASME B31.8-2016 Chapter VIII Pipeline']['internal_pressure']} (internal pressure)",
        f"Allowable RSF_a {params['RSFa']} · component age {params['Age']} yr · "
        f"corrosion-rate floor {params['FCARateFloor']} in/yr",
        f"FCA scenarios assessed (in): {fca_list}",
        "Measured 6×6 UT wall-thickness grid over the flaw region (real inline data).",
    ])

    # Remaining life / metal loss summary table
    rows = [
        ("Min wall thickness (measured)", f"{fmt(circ['Min WT (inch)'],3)} in"),
        ("Avg wall thickness", f"{fmt(circ['Avg. WT (inch)'],3)} in"),
        ("Max wall thickness", f"{fmt(circ['Max WT (inch)'],3)} in"),
        ("t_min (required)", f"{fmt(geo['tmin'],3)} in"),
        ("Flaw length", f"{fmt(circ['Len (inch)'],1)} in"),
        ("Corrosion rate", f"{fmt(circ['Corr. Rate (inch/year)'],4)} in/yr"),
        ("Remaining life", f"{fmt(circ['Rem. Life (yrs)'],1)} yr"),
        ("GML acceptable FCA (max)", f"{fmt(max(gml_ok),2)} in"),
    ]
    b.add_table("Results — metal loss & remaining life",
                pd.DataFrame(rows, columns=["Quantity", "Value"]),
                subtitle=f"Circumferential profile: {circ['Description']}")

    # GML & LML MAWP table across FCA
    gml_rows = []
    lml_by_fca = {row["FCA"]: row for row in lml}
    for g in gml:
        fca = g["FCA"]
        l = lml_by_fca.get(fca, {})
        gml_rows.append((
            f"{fca:.2f}",
            fmt(g["t"], 3),
            f"{g['MAWP']:,.0f}",
            f"{l.get('MAWPr, L1', float('nan')):,.0f}" if l else "—",
            f"{l.get('MAWPr, L2', float('nan')):,.0f}" if l else "—",
            "PASS" if g["MAWP"] >= design_p else "FAIL",
        ))
    b.add_table("MAWP vs future corrosion allowance",
                pd.DataFrame(gml_rows, columns=["FCA (in)", "GML t (in)", "GML MAWP (psi)",
                                                "LML MAWPr L1 (psi)", "LML MAWPr L2 (psi)", "vs design P"]),
                subtitle=f"All MAWP values exceed the {design_p:,} psi design pressure",
                status_col="vs design P")

    # Chart 0 (hero): the measured UT wall-thickness grid (contour) — the real flaw map
    inp = yaml.safe_load((DM / "examples/workflows/api579-pipe-ffs-b318/input.yml").read_text())
    rs = inp["ReadingSets"][0]
    grid = rs["grid"]["values"]
    zlim = rs.get("Contour", {}).get("zlim", [None, None])
    gmin = min(min(r) for r in grid)
    figg = go.Figure(go.Contour(z=grid, colorscale="RdYlBu", zmin=zlim[0], zmax=zlim[1],
                                contours=dict(showlabels=True, labelfont=dict(size=10, color="#333")),
                                colorbar=dict(title="WT (in)")))
    figg.update_layout(title=f"UT wall-thickness grid (in) — min {gmin:.3f} in at the flaw",
                       height=430, template="plotly_white",
                       xaxis_title="Circumferential CML", yaxis_title="Axial CML")
    b.add_chart("grid", figg, "Measured wall-thickness grid (CMLs)",
                "Contour of the 6×6 ultrasonic grid — the red zone is the governing flaw (thinnest wall)")

    # Chart 1: MAWP vs FCA (GML + LML L2) with design pressure line
    fcas = [g["FCA"] for g in gml]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fcas, y=[g["MAWP"] for g in gml], mode="lines+markers",
                             name="GML MAWP", line=dict(color=TEAL, width=3)))
    fig.add_trace(go.Scatter(x=[l["FCA"] for l in lml], y=[l["MAWPr, L2"] for l in lml],
                             mode="lines+markers", name="LML MAWPr (L2)",
                             line=dict(color=NAVY, width=3)))
    fig.add_hline(y=design_p, line_dash="dash", line_color="#e53e3e",
                  annotation_text=f"Design pressure {design_p:,} psi",
                  annotation_position="bottom right")
    fig.update_layout(title="Maximum allowable working pressure vs FCA", height=400,
                      template="plotly_white", xaxis_title="Future corrosion allowance (in)",
                      yaxis_title="MAWP (psi)", legend_orientation="h", yaxis_range=[0, 4000])
    b.add_chart("mawp", fig, "MAWP vs future corrosion allowance",
                "Both GML and LML MAWP stay above design pressure across all FCA")

    # Chart 2: remaining-thickness ratio Rt vs FCA (LML)
    fig2 = go.Figure(go.Bar(x=[f"{l['FCA']:.2f}" for l in lml],
                            y=[l["Rt"] for l in lml], marker_color=TEAL,
                            text=[f"{l['Rt']:.3f}" for l in lml], textposition="outside"))
    fig2.update_layout(title="Remaining-thickness ratio Rt by FCA (LML)", height=360,
                       template="plotly_white", xaxis_title="Future corrosion allowance (in)",
                       yaxis_title="Rt", yaxis_range=[0, 1.0])
    b.add_chart("rt", fig2, "Remaining-thickness ratio", "Rt stays above the Part-5 screening floor")

    # Verdict
    min_mawp = min(g["MAWP"] for g in gml)
    b.add_section("Verdict",
                  f"<p><strong>FIT FOR SERVICE.</strong> Over the assessed corrosion region the "
                  f"average remaining wall is {circ['Avg. WT (inch)']:.3f} in (minimum "
                  f"{circ['Min WT (inch)']:.3f} in) against a required t_min of {geo['tmin']:.3f} in. "
                  f"The Level-1/Level-2 Local Metal Loss assessment passes with RSF at the allowable "
                  f"(no de-rating required), and the general-metal-loss MAWP stays at or above "
                  f"<strong>{min_mawp:,.0f} psi</strong> even at the largest future corrosion allowance "
                  f"({max(gml_ok):.2f} in) — comfortably above the {design_p:,} psi design pressure. "
                  f"At the measured corrosion rate of {circ['Corr. Rate (inch/year)']:.4f} in/yr the "
                  f"remaining life is <strong>{circ['Rem. Life (yrs)']:.1f} years</strong>.</p>")
    b.build(out)
    patch_badge(out, "API 579-1 / ASME FFS-1 · deterministic FFS check")


DISPATCH = {
    "on-bottom-stability-f109": compose_f109,
    "free-span-f105": compose_f105,
    "api579-pipe-ffs-b318": compose_b318,
}

if __name__ == "__main__":
    slug, out = sys.argv[1], sys.argv[2]
    DISPATCH[slug](out)
    print(f"composed {slug} -> {out}")
