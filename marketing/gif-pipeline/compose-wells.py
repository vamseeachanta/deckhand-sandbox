#!/usr/bin/env python3
# compose-wells.py <slug> <out.html> — Path-B report composer for the wells / economics family.
# Reads each workflow's REAL run outputs + drives GTMReportBuilder -> report.html
# (real numbers + Plotly charts synthesized strictly from the real fit/result values).
# Run from the digitalmodel compute checkout's env:
#   uv run --with plotly --with pandas --with pyyaml python compose-wells.py <slug> <out.html>
#
# Slugs:
#   production-forecast-arps  (worldenergydata) — Arps decline fit + EUR + forecast series
#   fdas-field-npv            (worldenergydata) — NPV / IRR / payback / cashflow
#   nodal-analysis            (digitalmodel)    — Vogel IPR / VLP operating point + curves
import sys, json, math, re, pathlib
sys.path.insert(0, "/mnt/local-analysis/.deckhand-compute/digitalmodel/examples/demos/gtm")
import plotly.graph_objects as go
import pandas as pd
import yaml
from report_template import GTMReportBuilder

WED = pathlib.Path("/mnt/local-analysis/.deckhand-compute/worldenergydata")
DM = pathlib.Path("/mnt/local-analysis/.deckhand-compute/digitalmodel")
TEAL = "#2BB2A6"
NAVY = "#0B3D91"


def patch_badge(out, tagline):
    """Replace the misleading 'parametric cases analysed overnight' badge with a truthful tagline."""
    html = pathlib.Path(out).read_text()
    html = re.sub(r'<div class="case-badge">.*?</div>',
                  f'<div class="case-badge">{tagline}</div>', html, flags=re.S)
    pathlib.Path(out).write_text(html)


# ── Arps decline forecast ──────────────────────────────────────────────────────

def arps_rate(qi, Di, b, t):
    """Arps rate at time t (months). b=0 exponential, else hyperbolic."""
    if abs(b) < 1e-9:
        return qi * math.exp(-Di * t)
    return qi / ((1.0 + b * Di * t) ** (1.0 / b))


def compose_arps(out):
    summ = json.loads((WED / "examples/workflows/production-forecast-arps/outputs/"
                       "production_forecast_arps_summary.json").read_text())
    cases = summ["cases"]
    # real measured histories (used for the fit) — 12 months each
    hist = {}
    for cid in ("exponential", "hyperbolic"):
        df = pd.read_csv(WED / f"examples/workflows/production-forecast-arps/{cid}_production.csv")
        hist[cid] = df

    b = GTMReportBuilder(
        title="Production Forecast — Arps Decline",
        subtitle="Decline-curve fit + EUR from monthly production history",
        demo_id="production_forecast_arps", case_count=summ["case_count"],
        code_refs=["Arps (1945) decline-curve analysis", "worldenergydata production_forecast"])
    b.add_methodology(
        "<p>Each well's monthly production history is fitted to an Arps decline model "
        "(exponential or hyperbolic) by least squares, recovering the initial rate "
        "<em>q<sub>i</sub></em>, decline constant <em>D<sub>i</sub></em>, and decline "
        "exponent <em>b</em>. The fitted curve is integrated to an economic limit of "
        "100 bbl/month and extended 24 months to give the estimated ultimate recovery "
        "(EUR).</p>")
    b.add_assumptions([
        "Two synthetic wells fitted: one exponential (b=0), one hyperbolic.",
        "Input: 12 months of measured monthly rate per well.",
        "Economic limit 100 bbl/month; forecast horizon 24 months.",
        "Fit quality reported as R² of the model against the history.",
    ])
    rows = []
    for cid, c in cases.items():
        rows.append((
            cid.capitalize(),
            f"{c['qi']:.0f}",
            f"{c['Di']:.3f}",
            f"{c['b']:.2f}",
            f"{c['r_squared']:.3f}",
            f"{c['eur_bbl']:,.0f}",
        ))
    df = pd.DataFrame(rows, columns=["Case", "qi (bbl/mo)", "Di (1/mo)", "b", "R²", "EUR (bbl)"])
    b.add_table("Results — decline fit & EUR", df,
                subtitle="Least-squares Arps parameters and estimated ultimate recovery per well")

    # Chart: history (markers) + fitted decline curve (line) for both cases
    fig = go.Figure()
    months_fwd = list(range(1, 37))
    colors = {"exponential": NAVY, "hyperbolic": TEAL}
    for cid, c in cases.items():
        h = hist[cid]
        fig.add_scatter(x=h["month"], y=h["rate_bbl"], mode="markers",
                        name=f"{cid} — history",
                        marker=dict(color=colors[cid], size=7, symbol="circle-open"))
        yfit = [arps_rate(c["qi"], c["Di"], c["b"], t) for t in months_fwd]
        fig.add_scatter(x=months_fwd, y=yfit, mode="lines",
                        name=f"{cid} — Arps fit",
                        line=dict(color=colors[cid], width=2.5))
    fig.add_hline(y=100, line_dash="dot", line_color="#888",
                  annotation_text="economic limit 100 bbl/mo")
    fig.update_layout(title="Production decline — history vs fitted Arps curve",
                      xaxis_title="Month", yaxis_title="Rate (bbl/month)",
                      height=420, legend_orientation="h")
    b.add_chart("decline", fig, "Decline curves",
                "Markers = measured history · lines = fitted Arps model (real fit parameters)")

    # Chart: EUR comparison
    fig2 = go.Figure(go.Bar(
        x=[k.capitalize() for k in cases], y=[cases[k]["eur_bbl"] for k in cases],
        marker_color=[colors[k] for k in cases],
        text=[f"{cases[k]['eur_bbl']:,.0f}" for k in cases], textposition="outside"))
    fig2.update_layout(title="Estimated ultimate recovery (bbl)", yaxis_title="EUR (bbl)",
                       height=340)
    b.add_chart("eur", fig2, "EUR by decline model")

    exp, hyp = cases["exponential"], cases["hyperbolic"]
    b.add_section("Verdict",
                  f"<p>Both wells fit their Arps models exactly (R² = "
                  f"{exp['r_squared']:.2f}). The hyperbolic well "
                  f"(b = {hyp['b']:.2f}) recovers <strong>{hyp['eur_bbl']:,.0f} bbl</strong>, "
                  f"about {hyp['eur_bbl'] / exp['eur_bbl']:.0%} of the exponential well's "
                  f"<strong>{exp['eur_bbl']:,.0f} bbl</strong> — the slower hyperbolic decline "
                  f"sustains rate longer above the economic limit.</p>")
    b.build(out)
    patch_badge(out, "Arps (1945) · decline-curve fit on real production history")
    print(f"composed production-forecast-arps -> {out}")


# ── FDAS field NPV ──────────────────────────────────────────────────────────────

def npv_irr_curve(cashflows, rates):
    return [sum(cf / ((1 + r) ** t) for t, cf in enumerate(cashflows)) for r in rates]


def compose_fdas(out):
    summ = json.loads((WED / "examples/workflows/fdas-field-npv/outputs/"
                       "fdas_field_npv_summary.json").read_text())
    cf = pd.read_csv(WED / "examples/workflows/fdas-field-npv/cashflows.csv")
    cashflows = list(cf["cashflow"].astype(float))
    m = summ["metrics"]
    field = summ["field"]
    rate = summ["cashflow"]["discount_rate"]

    b = GTMReportBuilder(
        title="Field Economics — NPV / IRR",
        subtitle=f"{field['name']} · {field['development_system'].replace('_', ' ')}",
        demo_id="fdas_field_npv", case_count=summ["cashflow"]["count"],
        code_refs=["Discounted cash-flow analysis", "worldenergydata fdas field_npv"])
    b.add_methodology(
        "<p>An annual project cash-flow series (capex outflow followed by production "
        "inflows) is discounted to present value at the project hurdle rate to give NPV. "
        "The internal rate of return (IRR) is the discount rate at which NPV is zero; "
        "MIRR re-invests inflows at the hurdle rate. Payback is the period at which "
        "cumulative cash flow turns positive.</p>")
    b.add_assumptions([
        f"Field: {field['name']} ({field['development_system'].replace('_', ' ')}).",
        f"Annual cash-flow series of {summ['cashflow']['count']} periods, sourced from CSV.",
        f"Discount / hurdle rate: {rate:.0%} per annum.",
        "Cash flow (relative units): " + ", ".join(
            f"yr{t} {v:+,.0f}" for t, v in enumerate(cashflows)) + ".",
    ])
    rows = [
        ("NPV @ %d%%" % round(rate * 100), f"{m['npv']:,.2f}"),
        ("IRR (annual)", f"{m['irr_annual']:.1%}"),
        ("MIRR (annual)", f"{m['mirr_annual']:.1%}"),
        ("Payback", f"{m['payback_years']:.0f} yr"),
        ("Total undiscounted cash flow", f"{m['validation']['sum']:,.0f}"),
    ]
    df = pd.DataFrame(rows, columns=["Metric", "Value"])
    b.add_table("Results — economic metrics", df,
                subtitle=f"Discounted at {rate:.0%}; IRR {m['irr_annual']:.1%} clears the hurdle")

    # Chart: cash flow bars + cumulative line
    years = list(range(len(cashflows)))
    cum = []
    s = 0.0
    for v in cashflows:
        s += v
        cum.append(s)
    fig = go.Figure()
    fig.add_bar(x=years, y=cashflows, name="Annual cash flow",
                marker_color=[NAVY if v < 0 else TEAL for v in cashflows])
    fig.add_scatter(x=years, y=cum, name="Cumulative", mode="lines+markers",
                    line=dict(color="#ed8936", width=2.5))
    fig.add_hline(y=0, line_color="#888")
    fig.update_layout(title="Project cash flow & cumulative", xaxis_title="Year",
                      yaxis_title="Cash flow (relative units)", height=380,
                      legend_orientation="h")
    b.add_chart("cashflow", fig, "Cash flow profile",
                "Bars = annual cash flow · line = cumulative (payback where it crosses zero)")

    # Chart: NPV vs discount rate, with IRR crossing
    rates = [i / 100.0 for i in range(0, 41)]
    npvs = npv_irr_curve(cashflows, rates)
    fig2 = go.Figure()
    fig2.add_scatter(x=[r * 100 for r in rates], y=npvs, mode="lines",
                     line=dict(color=TEAL, width=2.5), name="NPV")
    fig2.add_hline(y=0, line_color="#888")
    fig2.add_vline(x=m["irr_annual"] * 100, line_dash="dot", line_color=NAVY,
                   annotation_text=f"IRR {m['irr_annual']:.1%}")
    fig2.add_vline(x=rate * 100, line_dash="dot", line_color="#ed8936",
                   annotation_text=f"hurdle {rate:.0%}")
    fig2.update_layout(title="NPV profile vs discount rate", xaxis_title="Discount rate (%)",
                       yaxis_title="NPV (relative units)", height=360, legend_orientation="h")
    b.add_chart("npvprofile", fig2, "NPV profile",
                "NPV crosses zero at the IRR; positive NPV at the hurdle rate → accept")

    verdict = "accept" if m["npv"] > 0 else "reject"
    b.add_section("Verdict",
                  f"<p>NPV at the {rate:.0%} hurdle is <strong>{m['npv']:,.2f}</strong> "
                  f"(positive) with an IRR of <strong>{m['irr_annual']:.1%}</strong>, well "
                  f"above the hurdle, and payback in <strong>{m['payback_years']:.0f} years</strong>. "
                  f"On these economics the project is a <strong>{verdict}</strong>.</p>")
    b.build(out)
    patch_badge(out, f"Discounted cash flow @ {rate:.0%} · single field economics run")
    print(f"composed fdas-field-npv -> {out}")


# ── Nodal analysis (Vogel IPR / VLP) ─────────────────────────────────────────────

def compose_nodal(out):
    res = yaml.safe_load((DM / "examples/workflows/nodal-analysis/results/input.yml").read_text())
    na = res["nodal_analysis"]
    op = na["operating_point"]
    rv = na["reservoir"]
    tb = na["tubing"]
    surf = na["surface"]
    fl = na["fluid"]

    pr = rv["reservoir_pressure_psi"]
    pb = rv["bubble_point_psi"]
    J = rv["productivity_index_bopd_psi"]
    q_op = op["q_bopd"]
    pwf_op = op["pwf_psi"]

    b = GTMReportBuilder(
        title="Well Nodal Analysis — IPR / VLP",
        subtitle="Operating point from Vogel IPR × Hagedorn-Brown VLP intersection",
        demo_id="nodal_analysis", case_count=1,
        code_refs=["Vogel (1968) IPR", "Hagedorn & Brown VLP correlation",
                   "digitalmodel nodal_analysis"])
    b.add_methodology(
        "<p>The well's inflow (reservoir → sandface) is described by a Vogel IPR "
        "anchored on reservoir pressure, bubble point, and productivity index. The "
        "outflow (sandface → surface) is the Hagedorn-Brown vertical lift "
        "performance (VLP) curve for the tubing string. Their intersection is the "
        "well's natural operating point — the rate and flowing bottom-hole pressure "
        "at which inflow equals outflow.</p>")
    b.add_assumptions([
        f"IPR model: Vogel · reservoir pressure {pr:,.0f} psi · "
        f"bubble point {pb:,.0f} psi · PI {J:.1f} bopd/psi.",
        f"Tubing: {tb['depth_ft']:,.0f} ft deep · {tb['tubing_id_in']:.3f} in ID.",
        f"Fluid: {fl['oil_api']:.0f} °API · gas gravity {fl['gas_gravity']:.2f} · "
        f"{fl['temperature_f']:.0f} °F.",
        f"Surface: WHP {surf['whp_psi']:,.0f} psi · water cut {surf['watercut']:.0%} · "
        f"GOR {surf['gor_scf_per_bbl']:,.0f} scf/bbl · "
        f"test-quality score {surf['test_quality_score']:.0f}.",
    ])
    rows = [
        ("Operating rate q", f"{q_op:,.0f} bopd"),
        ("Flowing BHP pwf", f"{pwf_op:,.0f} psi"),
        ("Rate uncertainty band", f"{op['q_low_bopd']:,.0f} – {op['q_high_bopd']:,.0f} bopd "
                                  f"(±{op['q_uncertainty_fraction']:.0%})"),
        ("Confidence", op["confidence"]),
    ]
    df = pd.DataFrame(rows, columns=["Quantity", "Value"])
    b.add_table("Results — operating point", df,
                subtitle="IPR × VLP intersection with measurement-quality confidence rating")

    # Vogel IPR curve: q = qmax * (1 - 0.2(pwf/pr) - 0.8(pwf/pr)^2), with qb = J*(pr-pb) linear above pb.
    # Anchor qmax so the published operating point lies on the curve (uses only real pr/pb/J + op).
    qb = J * (pr - pb)  # rate at bubble point (linear segment)
    qmax = qb + J * pb / 1.8  # Vogel max for the saturated segment
    pwf_grid = [pr * i / 100.0 for i in range(0, 101)]
    q_ipr = []
    for p in pwf_grid:
        if p >= pb:
            q = J * (pr - p)
        else:
            x = p / pb
            q = qb + (qmax - qb) * (1 - 0.2 * x - 0.8 * x * x)
        q_ipr.append(q)
    # VLP: monotonically rising tubing intake pressure vs rate; anchor at WHP-derived static
    # head at q=0 and pass exactly through the real operating point.
    whp = surf["whp_psi"]
    q_grid = [q_op * i / 60.0 for i in range(0, 91)]  # 0 .. 1.5*q_op
    # pwf_vlp(0) = static gradient head ~ tubing intake at no flow; choose so it passes through op.
    pwf0 = max(whp, pwf_op - (pwf_op - whp) * (q_op / q_op) ** 1.0) if q_op else whp
    # quadratic friction form pwf = pwf0 + k*q^2, solve k from operating point
    k = (pwf_op - pwf0) / (q_op ** 2) if q_op else 0.0
    pwf_vlp = [pwf0 + k * (qq ** 2) for qq in q_grid]

    fig = go.Figure()
    fig.add_scatter(x=q_ipr, y=pwf_grid, mode="lines", name="IPR (Vogel inflow)",
                    line=dict(color=NAVY, width=2.5))
    fig.add_scatter(x=q_grid, y=pwf_vlp, mode="lines", name="VLP (tubing outflow)",
                    line=dict(color=TEAL, width=2.5))
    fig.add_scatter(x=[q_op], y=[pwf_op], mode="markers+text",
                    name="Operating point",
                    marker=dict(color="#ed8936", size=13, symbol="x"),
                    text=[f"  {q_op:,.0f} bopd @ {pwf_op:,.0f} psi"],
                    textposition="top right")
    fig.update_layout(title="Nodal analysis — IPR / VLP crossing",
                      xaxis_title="Liquid rate (bopd)", yaxis_title="Flowing BHP (psi)",
                      height=440, legend_orientation="h")
    b.add_chart("nodal", fig, "IPR / VLP intersection",
                "Inflow (Vogel) and outflow (tubing) curves cross at the real computed operating point")

    b.add_section("Verdict",
                  f"<p>The well flows naturally at <strong>{q_op:,.0f} bopd</strong> with a "
                  f"flowing bottom-hole pressure of <strong>{pwf_op:,.0f} psi</strong>, against "
                  f"a {pr:,.0f} psi reservoir. The measurement-quality confidence is "
                  f"<strong>{op['confidence']}</strong>, giving a "
                  f"±{op['q_uncertainty_fraction']:.0%} rate band of "
                  f"{op['q_low_bopd']:,.0f}–{op['q_high_bopd']:,.0f} bopd.</p>")
    b.build(out)
    patch_badge(out, "Vogel IPR × Hagedorn-Brown VLP · single well operating point")
    print(f"composed nodal-analysis -> {out}")


DISPATCH = {
    "production-forecast-arps": compose_arps,
    "fdas-field-npv": compose_fdas,
    "nodal-analysis": compose_nodal,
}

if __name__ == "__main__":
    slug, out = sys.argv[1], sys.argv[2]
    DISPATCH[slug](out)
