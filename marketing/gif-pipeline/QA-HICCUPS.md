# QA hiccups — surfaced by the demo-v3 real-run pass (deckhand#436)

Running all 17 marketing workflows through the real pipeline (capability-smoke →
Path-B report composition) doubles as a QA pass. Findings below — data/input
realism + composer coverage, not bot-chat issues (chat-eval #390–392 covers those).

## Fix-worthy
1. **wall-thickness-quickcheck — internal inconsistency in the agent-composed report.**
   The cached deliverable says Case "…300 bar" but the pressure-basis line says
   "quoted 150 bar is design pressure." Real defect in the agent-composed report →
   tighten the report-gen prompt/template so the basis echoes the actual input.
2. **fdas-field-npv — toy inputs.** Canonical input is `[-1000,+500,+500,+500]` →
   MIRR 422.6%, reads as unrealistic. → swapping to a realistic subsea-tieback case
   (CAPEX/plateau/$bbl/OPEX/life) in a parallel session.
3. **CP pipeline (F103) & fpso (ABS) — thinner reports.** `compose-cp.py` is
   B401-schema-centric (per-zone current-demand chart), so the F103 (attenuation/
   bracelet) and ABS (mass-only) reports lack a tailored chart. → add F103/ABS
   mapping to the composer.

## Truthful-but-worth-noting (no fix, or operator call)
4. **free-span-f105 — canonical 34 m span FAILs** (VIV lock-in, fatigue ~2.5 days).
   Real; kept as an honest "catches a problem" demo (operator decision 2026-06-17).
5. **production-forecast-arps — R²=1.000.** Canonical input is a clean synthetic
   decline → perfect fit. Truthful but idealized; a noisier real-style rate series
   would read as more credible.
6. **fpso-spread-mooring — all 8 lines identical.** Symmetric layout + benign
   head-on screening env → identical per-line tensions. Real output; a quartering
   env would show line-to-line variation.
7. **nodal-analysis — VLP is illustrative.** IPR uses the real Pr/Pb/PI; the
   workflow outputs the operating point (997 bopd @ 2,458 psi), so the VLP curve in
   the report is a representative tubing-intake anchored to pass through that real
   point. Crossing is truthful; the VLP shape is illustrative.

## Pipeline-level
8. **worldenergydata cold-start ~264 s** (arps first run) — consistent with the
   known pre-warm need (#392 / #399 `prewarm-compute.sh`).
9. **15/17 workflows emit no native plots** (empty `Plot/`); the composer
   synthesizes charts from result tables. If native plots are wanted in real
   deliverables, the workflows need plot output.
