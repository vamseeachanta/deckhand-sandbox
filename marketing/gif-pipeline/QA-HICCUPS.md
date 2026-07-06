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
3. ~~**CP pipeline (F103) & fpso (ABS) — thinner reports.**~~ **RESOLVED** —
   `compose-cp.py` now dispatches by schema (F103 attenuation/bracelet + reach
   chart; ABS densities + demand chart; B401 zone + current-output charts). All 5
   CP reports ~27 KB, demos re-rendered.

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

10. **dynacard classifiers AND the synthetic-card generator are both mis-calibrated.**
    Two distinct upstream defects surfaced building the 2-card demo:
    - **Classifier:** the shipped `dynacard_classifier.json` (GradientBoosting v1.0)
      mislabels FLUID_POUND/GAS_INTERFERENCE as PARAFFIN_RESTRICTION. The legacy
      threshold path (`PumpDiagnostics._load_model → None`) classifies FLUID_POUND
      correctly but is **seed-sensitive** — of seeds {712,713,717,721} only **721**
      round-tripped to FLUID_POUND; 712/713/717 came back GAS_INTERFERENCE. It also
      emits **no confidence probability** (rule-based), shown as "rule-based" in the
      report.
    - **Synthetic cards:** the generator emits **implausibly high pump fillage for
      every fault mode** (92–97%), and the GAS_LOCK card is internally contradictory
      — a large rounded loop at 96.8% fillage while its own diagnosis text says
      "near-zero card area." GAS_LOCK was therefore **rejected** for the demo (the
      card visibly contradicts the label, defeating the credibility goal).
    - **Demo as shipped:** **PUMP_TAGGING (ML, 100.0% conf, clear load-spike card) +
      FLUID_POUND (legacy rule-based, seed 721, truncated incomplete-fillage card)** —
      the second is the most common rod-pump fault and its card shape matches its
      diagnosis. Operator-chosen 2026-06-17 over GAS_LOCK after seeing both rendered.
    - **Fix-worthy upstream:** (a) retrain `dynacard_classifier.json` so fluid-pound /
      gas-interference classify under the shipped ML; (b) fix the synthetic-card
      fillage/area so GAS_LOCK actually looks gas-locked. Then fluid-pound can run on
      the default classifier with a confidence number.
    *(Cards via `DynacardWorkflow().router(cfg)` honoring `synthetic_card.mode`;
    legacy path forced in `/tmp/run_fluidpound_legacy.py`; `compose-dynacard.py`
    plots both real card signatures.)*

## Pipeline-level
8. **worldenergydata cold-start ~264 s** (arps first run) — consistent with the
   known pre-warm need (#392 / #399 `prewarm-compute.sh`).
9. **15/17 workflows emit no native plots** (empty `Plot/`); the composer
   synthesizes charts from result tables. If native plots are wanted in real
   deliverables, the workflows need plot output.
