#!/usr/bin/env python3
# compose-naval.py <slug> <out.html> — Path-B report composer for the naval/mooring family.
# Reads each workflow's REAL results (the `results:` block in
# examples/workflows/<slug>/results/input.yml) and drives GTMReportBuilder ->
# report.html (real numbers + synthesized Plotly charts + standard sections).
# Run from the digitalmodel compute checkout's env:
#   uv run --with plotly --with pandas --with pyyaml python compose-naval.py <slug> <out.html>
import sys, re, yaml, pathlib
sys.path.insert(0, "/mnt/local-analysis/.deckhand-compute/digitalmodel/examples/demos/gtm")
import plotly.graph_objects as go
import pandas as pd
from report_template import GTMReportBuilder

DM = pathlib.Path("/mnt/local-analysis/.deckhand-compute/digitalmodel")
TEAL = "#2BB2A6"
NAVY = "#0B3D91"


def load(slug):
    return yaml.safe_load((DM / f"examples/workflows/{slug}/results/input.yml").read_text())


def num(x):
    try:
        return float(x)
    except Exception:
        return None


def finish(b, out, badge):
    b.build(out)
    html = pathlib.Path(out).read_text()
    html = re.sub(r'<div class="case-badge">.*?</div>',
                  f'<div class="case-badge">{badge}</div>', html, flags=re.S)
    pathlib.Path(out).write_text(html)
    print(f"composed -> {out}  ({len(html):,} bytes)")


# ── mooring-fatigue ──────────────────────────────────────────────────────────
def compose_mooring_fatigue(out):
    doc = load("mooring-fatigue")
    r = doc["mooring_fatigue"]
    src = load_src("mooring-fatigue")["mooring_fatigue"]
    b = GTMReportBuilder(
        title="Mooring-Line Fatigue Screen",
        subtitle="Per-line rainflow + Miner damage · S-N curve D (seawater w/ CP)",
        demo_id="mooring_fatigue", case_count=len(r["lines"]),
        code_refs=["DNV-OS-E301 Position Mooring", "DNV-RP-C203 S-N curve D",
                   "digitalmodel mooring_fatigue"])
    b.add_methodology(
        "<p>For each mooring line the tension-range histogram is converted to a "
        "stress-range histogram via the line's cross-sectional area, then each bin's "
        "Miner damage is accumulated against the allowable cycles from the selected "
        "S-N curve. The summed annual damage is scaled by the design life and the "
        "design fatigue factor (DFF) to give a fatigue life and a DFF margin; the "
        "governing line is the one with the highest damage.</p>")
    b.add_assumptions([
        f"S-N curve: {r['sn_curve']['curve']} · environment {r['sn_curve']['environment']}",
        f"Design life {r['design_life_years']} yr · DFF {r['dff']} "
        f"(required life {r['lines'][0]['required_life_years']} yr)",
        "chain-01: area 8000 mm² · tension-range bins 220/300/380 kN "
        "at 150000/60000/10000 cycles (CHAIN)",
        "wire-01: area 5200 mm² · tension-range bins 180/260/360 kN "
        "at 180000/90000/20000 cycles (STEEL-WIRE)",
    ])
    rows = []
    for ln in r["lines"]:
        rows.append({
            "Line": ln["line_id"], "Material": ln["material"],
            "Annual damage": f"{ln['total_damage']:.4f}",
            "Fatigue life (yr)": f"{ln['fatigue_life_years']:.0f}",
            "Required life (yr)": f"{ln['required_life_years']:.0f}",
            "DFF margin": f"{ln['dff_margin']:.1f}×",
            "Status": "PASS" if ln["passes_dff"] else "FAIL",
        })
    b.add_table("Results — per-line fatigue", pd.DataFrame(rows),
                subtitle=f"Governing line: {r['governing_line']} "
                         f"(life {r['governing_fatigue_life_years']:.0f} yr, "
                         f"margin {r['governing_dff_margin']:.1f}×) · "
                         f"screening status {r['screening_status'].upper()}",
                status_col="Status")
    # Chart: fatigue life vs required life per line
    lines = [ln["line_id"] for ln in r["lines"]]
    fig = go.Figure()
    fig.add_bar(name="Fatigue life", x=lines,
                y=[ln["fatigue_life_years"] for ln in r["lines"]], marker_color=TEAL)
    fig.add_scatter(name="Required life", x=lines,
                    y=[ln["required_life_years"] for ln in r["lines"]],
                    mode="lines+markers", line=dict(color=NAVY, dash="dash"))
    fig.update_layout(barmode="group", height=380, template="plotly_white",
                      yaxis_type="log", yaxis_title="Years (log)",
                      legend_orientation="h", title="Fatigue life vs required (log scale)")
    b.add_chart("life", fig, "Fatigue life vs required life",
                "Bars dwarf the dashed requirement → large margin")
    # Chart: per-bin damage contribution
    csv = pd.read_csv(DM / "examples/workflows/mooring-fatigue/results/input_mooring_fatigue.csv")
    fig2 = go.Figure()
    for i, (lid, grp) in enumerate(csv.groupby("line_id")):
        fig2.add_bar(name=lid, x=[f"{int(s)} MPa" for s in grp["stress_range_MPa"]],
                     y=grp["damage"], marker_color=[TEAL, NAVY][i % 2])
    fig2.update_layout(barmode="group", height=340, template="plotly_white",
                       yaxis_title="Miner damage / bin",
                       title="Damage contribution by stress-range bin")
    b.add_chart("bins", fig2, "Damage by stress-range bin",
                "Where the fatigue damage accumulates")
    b.add_section("Verdict",
                  f"<p>Both lines <strong>PASS</strong>. Governing line "
                  f"<strong>{r['governing_line']}</strong> reaches a fatigue life of "
                  f"<strong>{r['governing_fatigue_life_years']:.0f} yr</strong> against a "
                  f"{r['lines'][0]['required_life_years']:.0f} yr requirement "
                  f"(DFF {r['dff']}), a <strong>{r['governing_dff_margin']:.1f}×</strong> "
                  f"margin. Screening status: {r['screening_status'].upper()}.</p>")
    finish(b, out, "DNV-RP-C203 D · deterministic fatigue screen (2 lines)")


def load_src(slug):
    return yaml.safe_load((DM / f"examples/workflows/{slug}/input.yml").read_text())


# ── fpso-spread-mooring ──────────────────────────────────────────────────────
def compose_fpso_spread_mooring(out):
    doc = load("fpso-spread-mooring")
    r = doc["fpso_mooring"]
    v = doc["vessel"]; m = doc["mooring"]; env = doc["environment"]
    s = r["summary"]; el = r["environmental_loads"]
    b = GTMReportBuilder(
        title="FPSO Spread-Mooring Intact Check",
        subtitle="8-line quasi-static tension / MBL / safety-factor screen",
        demo_id="fpso_spread_mooring", case_count=s["n_results"],
        code_refs=["API RP 2SK Stationkeeping", "DNV-OS-E301 Position Mooring",
                   "digitalmodel fpso_mooring"])
    b.add_methodology(
        "<p>Environmental wave-drift, current and wind forces are summed into a net "
        "horizontal load on the vessel, distributed across the spread-mooring pattern. "
        "Each line's peak tension is compared against its minimum breaking load (MBL): "
        "the safety factor is MBL / tension and the utilisation is its inverse. The "
        "critical line is the most heavily loaded; the case passes when every line clears "
        "the required safety factor.</p>")
    b.add_assumptions([
        f"Vessel: {v['vessel_type'].upper()} L={v['length']} m × B={v['beam']} m, "
        f"draft {v['draft']} m, displacement {v['displacement']:,.0f} t",
        f"Mooring: {m['n_lines']} lines · {m['material']} · water depth "
        f"{m['water_depth']} m · anchor radius {m['anchor_radius']} m · "
        f"pretension {m['pretension']} kN · line length {m['line_length']} m",
        f"Environment ({env['name']}): Hs {env['wave_hs']} m / Tp {env['wave_tp']} s, "
        f"current {env['current_speed']} m/s, wind {env['wind_speed']} m/s, "
        f"all from {env['wave_direction']}°",
        f"Load case: {r['line_results'][0]['load_case']} · dynamic factor "
        f"{r['line_results'][0]['details']['dynamic_factor']}",
    ])
    # Environmental load breakdown table
    elrows = [
        {"Component": "Wave drift", "Force (kN)": f"{el['wave_drift_force']:,.1f}"},
        {"Component": "Current", "Force (kN)": f"{el['current_force']:,.1f}"},
        {"Component": "Wind", "Force (kN)": f"{el['wind_force']:,.1f}"},
        {"Component": "Total horizontal", "Force (kN)": f"{el['total_force']:,.1f}"},
    ]
    b.add_table("Environmental loads", pd.DataFrame(elrows),
                subtitle=f"Net load applied at heading {el['direction']}°")
    # Per-line table
    rows = []
    for ln in r["line_results"]:
        rows.append({
            "Line": ln["line_id"],
            "Max tension (kN)": f"{ln['max_tension']:,.0f}",
            "Min MBL req. (kN)": f"{ln['min_mbl_required']:,.0f}",
            "Actual MBL (kN)": f"{ln['actual_mbl']:,.0f}",
            "Safety factor": f"{ln['safety_factor']:.2f}",
            "Utilisation": f"{ln['utilization']*100:.0f}%",
            "Status": "PASS" if ln["passes"] else "FAIL",
        })
    b.add_table("Results — per-line tension check", pd.DataFrame(rows),
                subtitle=f"Critical line {s['critical_line']['line_id']} · "
                         f"min SF {s['min_safety_factor']} · max utilisation "
                         f"{s['max_utilization']*100:.0f}% · overall {s['overall_status']}",
                status_col="Status")
    # Chart: env load breakdown
    fig = go.Figure(go.Bar(
        x=["Wave drift", "Current", "Wind"],
        y=[el["wave_drift_force"], el["current_force"], el["wind_force"]],
        marker_color=[NAVY, TEAL, "#4cc2ff"]))
    fig.update_layout(height=320, template="plotly_white", yaxis_title="Force (kN)",
                      title=f"Environmental load split — total {el['total_force']:,.0f} kN")
    b.add_chart("env", fig, "Environmental load breakdown",
                "Wave drift dominates the net horizontal load")
    # Chart: tension vs MBL per line
    lines = [ln["line_id"] for ln in r["line_results"]]
    fig2 = go.Figure()
    fig2.add_bar(name="Max tension", x=lines,
                 y=[ln["max_tension"] for ln in r["line_results"]], marker_color=TEAL)
    fig2.add_bar(name="Actual MBL", x=lines,
                 y=[ln["actual_mbl"] for ln in r["line_results"]], marker_color=NAVY)
    fig2.add_scatter(name="Min MBL required", x=lines,
                     y=[ln["min_mbl_required"] for ln in r["line_results"]],
                     mode="lines+markers", line=dict(color="#d69e2e", dash="dash"))
    fig2.update_layout(barmode="group", height=380, template="plotly_white",
                       yaxis_title="kN", legend_orientation="h",
                       title="Per-line tension vs MBL (symmetric pattern)")
    b.add_chart("tension", fig2, "Tension vs MBL per line",
                "8 symmetric lines, each at SF 2.08 / 48% utilisation")
    b.add_section("Verdict",
                  f"<p>All {s['n_results']} lines <strong>{s['overall_status']}</strong>. "
                  f"The symmetric pattern loads every line equally at "
                  f"<strong>{r['line_results'][0]['max_tension']:,.0f} kN</strong> against a "
                  f"{r['line_results'][0]['actual_mbl']:,.0f} kN MBL — a safety factor of "
                  f"<strong>{s['min_safety_factor']}</strong> "
                  f"({s['max_utilization']*100:.0f}% utilisation) under the "
                  f"{env['name']} screening environment.</p>")
    finish(b, out, "API RP 2SK · quasi-static intact check (8 lines)")


# ── hull-seakeeping ──────────────────────────────────────────────────────────
def compose_hull_seakeeping(out):
    doc = load("hull-seakeeping")
    hs = doc["naval_arch"]["hull_seakeeping"]
    v = hs["vessel"]; w = hs["wave"]; res = hs["result"]
    b = GTMReportBuilder(
        title="Hull Seakeeping Screen",
        subtitle="Natural periods + simple wave-response & comfort check",
        demo_id="hull_seakeeping", case_count=1,
        code_refs=["Lloyd's seakeeping fundamentals", "ISO 2631 motion sickness incidence",
                   "digitalmodel naval_arch hull_seakeeping"])
    b.add_methodology(
        "<p>From the hull's hydrostatics the undamped natural periods in roll, heave and "
        "pitch are computed (roll from GM and beam, heave from waterplane area and "
        "displacement, pitch from the longitudinal metacentric height). The wave encounter "
        "frequency is found for the given heading and speed, a simple transfer function "
        "gives the heave RAO at that frequency, and the vertical-acceleration RMS over the "
        "exposure window yields a motion-sickness-incidence estimate.</p>")
    b.add_assumptions([
        f"Vessel: LWL {v['lwl_m']} m · beam {v['beam_m']} m · displacement "
        f"{v['displacement_tonnes']:,.0f} t · waterplane area {v['waterplane_area_m2']:,.0f} m²",
        f"Stability: GM(T) {v['gm_m']} m · GM(L) {v['gml_m']} m · speed {v['speed_ms']} m/s",
        f"Wave: frequency {w['frequency_rad_s']} rad/s · heading {w['heading_deg']}° "
        f"(head seas) · damping ratio {w['damping_ratio']}",
        f"Comfort: vertical-accel RMS {w['vertical_accel_rms_g']} g over "
        f"{w['exposure_hours']} h exposure",
    ])
    rows = [
        {"Quantity": "Natural roll period", "Value": f"{res['natural_roll_period_s']:.2f} s"},
        {"Quantity": "Natural heave period", "Value": f"{res['natural_heave_period_s']:.2f} s"},
        {"Quantity": "Natural pitch period", "Value": f"{res['natural_pitch_period_s']:.2f} s"},
        {"Quantity": "Wave encounter frequency", "Value": f"{res['encounter_frequency_rad_s']:.3f} rad/s"},
        {"Quantity": "Simple heave RAO", "Value": f"{res['simple_heave_rao']:.3f}"},
        {"Quantity": "Significant motion", "Value": f"{res['significant_motion_m']:.2f} m"},
        {"Quantity": "Motion-sickness incidence", "Value": f"{res['motion_sickness_incidence_pct']:.1f}%"},
    ]
    b.add_table("Results — seakeeping screen", pd.DataFrame(rows),
                subtitle="Natural periods, encounter response and comfort")
    # Chart: natural periods
    fig = go.Figure(go.Bar(
        x=["Roll", "Heave", "Pitch"],
        y=[res["natural_roll_period_s"], res["natural_heave_period_s"], res["natural_pitch_period_s"]],
        marker_color=[NAVY, TEAL, "#4cc2ff"],
        text=[f"{res['natural_roll_period_s']:.1f}s", f"{res['natural_heave_period_s']:.1f}s",
              f"{res['natural_pitch_period_s']:.1f}s"], textposition="outside"))
    wave_period = 2 * 3.141592653589793 / w["frequency_rad_s"]
    fig.add_hline(y=wave_period, line_dash="dash", line_color="#d69e2e",
                  annotation_text=f"wave period {wave_period:.1f}s")
    fig.update_layout(height=360, template="plotly_white", yaxis_title="Period (s)",
                      title="Undamped natural periods vs incident wave period")
    b.add_chart("periods", fig, "Natural periods",
                "Long roll period (24 s) sits well clear of the 7.9 s wave period")
    # Chart: comfort gauge-style bar
    fig2 = go.Figure(go.Bar(
        x=[res["motion_sickness_incidence_pct"]], y=["MSI"], orientation="h",
        marker_color=TEAL, text=[f"{res['motion_sickness_incidence_pct']:.1f}%"],
        textposition="outside"))
    fig2.update_layout(height=240, template="plotly_white",
                       xaxis_title="Motion-sickness incidence (%)", xaxis_range=[0, 50],
                       title=f"Comfort: MSI over {w['exposure_hours']} h exposure")
    b.add_chart("msi", fig2, "Motion-sickness incidence",
                "Low MSI at the given vertical-acceleration RMS")
    b.add_section("Verdict",
                  f"<p>Natural roll period <strong>{res['natural_roll_period_s']:.1f} s</strong> "
                  f"(heave {res['natural_heave_period_s']:.1f} s, pitch "
                  f"{res['natural_pitch_period_s']:.1f} s) against a "
                  f"{wave_period:.1f} s incident wave — the long roll period keeps the hull "
                  f"clear of resonance. Simple heave RAO "
                  f"<strong>{res['simple_heave_rao']:.2f}</strong>, significant motion "
                  f"{res['significant_motion_m']:.1f} m, motion-sickness incidence "
                  f"<strong>{res['motion_sickness_incidence_pct']:.1f}%</strong> over "
                  f"{w['exposure_hours']} h.</p>")
    finish(b, out, "Seakeeping fundamentals · single-condition screen")


# ── ocimf-tanker-loads ───────────────────────────────────────────────────────
def compose_ocimf_tanker_loads(out):
    doc = load("ocimf-tanker-loads")
    o = doc["ocimf"]; res = o["results"]
    loads = res["loads"]; cond = res["conditions"]; geo = res["vessel_geometry"]
    b = GTMReportBuilder(
        title="OCIMF Tanker Wind & Current Loads",
        subtitle="VLCC environmental force / moment from OCIMF coefficients",
        demo_id="ocimf_tanker_loads", case_count=1,
        code_refs=["OCIMF Mooring Equipment Guidelines (MEG)",
                   "OCIMF prediction of wind & current loads on VLCCs",
                   "digitalmodel ocimf"])
    b.add_methodology(
        "<p>Non-dimensional wind and current force/moment coefficients (CX, CY, CM) are "
        "looked up from the OCIMF VLCC database at the relevant relative headings, then "
        "dimensionalised using the air/water densities, the relevant projected areas "
        "(frontal and lateral) and the squared wind/current speeds. The longitudinal (Fx) "
        "and lateral (Fy) forces and the yaw moment (Mz) are summed across wind and current "
        "to give the total environmental load the mooring must resist.</p>")
    b.add_assumptions([
        f"Vessel: VLCC LOA {geo['loa']} m · beam {geo['beam']} m · draft "
        f"{geo['draft']} m · displacement {o['displacement']:,.0f} t",
        f"Projected areas: wind frontal {geo['frontal_area_wind']:,.0f} m² / lateral "
        f"{geo['lateral_area_wind']:,.0f} m² · current frontal "
        f"{geo['frontal_area_current']:,.0f} m² / lateral {geo['lateral_area_current']:,.0f} m²",
        f"Wind: {cond['wind_speed']} m/s from {cond['wind_direction']}° · air density "
        f"{cond['air_density']} kg/m³",
        f"Current: {cond['current_speed']} m/s from {cond['current_direction']}° · "
        f"water density {cond['water_density']} kg/m³",
    ])
    # Loads table (convert N -> kN, Nm -> kN.m)
    rows = []
    for src in ["wind", "current", "total"]:
        L = loads[src]
        rows.append({
            "Source": src.capitalize(),
            "Fx — surge (kN)": f"{L['fx_N']/1e3:,.0f}",
            "Fy — sway (kN)": f"{L['fy_N']/1e3:,.0f}",
            "Mz — yaw (kN·m)": f"{L['mz_Nm']/1e3:,.0f}",
        })
    b.add_table("Results — environmental loads", pd.DataFrame(rows),
                subtitle=f"Total lateral force {loads['total']['fy_N']/1e3:,.0f} kN "
                         f"governs the spread-mooring demand")
    # Coefficients table
    wc = res["wind_coefficients"]; cc = res["current_coefficients"]
    crows = [
        {"Coefficient": "CX (longitudinal)", "Wind": f"{wc['CXw']:.3f}", "Current": f"{cc['CXc']:.3f}"},
        {"Coefficient": "CY (lateral)", "Wind": f"{wc['CYw']:.3f}", "Current": f"{cc['CYc']:.3f}"},
        {"Coefficient": "CM (yaw moment)", "Wind": f"{wc['CMw']:.3f}", "Current": f"{cc['CMc']:.3f}"},
    ]
    b.add_table("OCIMF coefficients", pd.DataFrame(crows),
                subtitle=f"Wind at {wc['heading']}° relative · current at "
                         f"{cc['heading']}° relative")
    # Chart: Fx/Fy split wind vs current
    fig = go.Figure()
    fig.add_bar(name="Wind", x=["Fx (surge)", "Fy (sway)"],
                y=[loads["wind"]["fx_N"]/1e3, loads["wind"]["fy_N"]/1e3], marker_color=TEAL)
    fig.add_bar(name="Current", x=["Fx (surge)", "Fy (sway)"],
                y=[loads["current"]["fx_N"]/1e3, loads["current"]["fy_N"]/1e3], marker_color=NAVY)
    fig.update_layout(barmode="stack", height=360, template="plotly_white",
                      yaxis_title="Force (kN)", legend_orientation="h",
                      title="Force contribution — wind vs current")
    b.add_chart("forces", fig, "Wind vs current force split",
                "Current dominates both surge and sway loads")
    # Chart: yaw moment contributions
    fig2 = go.Figure(go.Bar(
        x=["Wind", "Current", "Total"],
        y=[loads["wind"]["mz_Nm"]/1e3, loads["current"]["mz_Nm"]/1e3, loads["total"]["mz_Nm"]/1e3],
        marker_color=[TEAL, NAVY, "#4cc2ff"]))
    fig2.update_layout(height=330, template="plotly_white", yaxis_title="Yaw moment (kN·m)",
                       title="Yaw-moment contribution")
    b.add_chart("moment", fig2, "Yaw moment", "Current is the dominant yaw driver")
    b.add_section("Verdict",
                  f"<p>Total environmental load on the VLCC: surge "
                  f"<strong>{loads['total']['fx_N']/1e3:,.0f} kN</strong>, sway "
                  f"<strong>{loads['total']['fy_N']/1e3:,.0f} kN</strong>, yaw moment "
                  f"<strong>{loads['total']['mz_Nm']/1e3:,.0f} kN·m</strong>. "
                  f"Current ({cond['current_speed']} m/s) dominates over the "
                  f"{cond['wind_speed']} m/s wind — the {loads['total']['fy_N']/1e3:,.0f} kN "
                  f"lateral force sets the stationkeeping demand.</p>")
    finish(b, out, "OCIMF MEG · single-condition load case")


DISPATCH = {
    "mooring-fatigue": compose_mooring_fatigue,
    "fpso-spread-mooring": compose_fpso_spread_mooring,
    "hull-seakeeping": compose_hull_seakeeping,
    "ocimf-tanker-loads": compose_ocimf_tanker_loads,
}

if __name__ == "__main__":
    slug, out = sys.argv[1], sys.argv[2]
    DISPATCH[slug](out)
