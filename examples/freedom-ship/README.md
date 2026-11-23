# Freedom Ship — Concept-Level Weight & Area Model

A worked, **concept-level** sizing study for a *Freedom Ship*-style very-large floating
city: a deck-by-deck area / mass / centre-of-gravity model, a design basis narrative, and
a small set of capacity and population scenarios.

> ⚠️ **This is illustrative, preliminary engineering only.** It is **not** a class-approved,
> flag-state-reviewed, or buildable design. The numbers are first-pass parametric estimates
> meant to demonstrate how a sizing model is structured and reasoned about — verify against
> governing codes, a recognised class society, and your own engineering judgement before any
> real use. See the caveats below.

## What's here

| File | What it is |
|------|------------|
| `freedom-ship-design-basis-2026-06-03.html` | Narrative design basis: scale, regime, structural strategy, regulatory regime, key risks. |
| `build_freedom_ship_weight_area_model.py` | The generator script — builds the model report and data files. |
| `model/freedom-ship-weight-area-model-2026-06-03.html` | The generated weight & area report (25-deck table, weight breakdown, hydrostatics, scenarios). |
| `model/deck_area_weight_model.csv` | Per-deck effective/net area, structure / outfit / payload mass, KG. |
| `model/hydrostatic_capacity_sweep.csv` | Displacement vs. draft / freeboard capacity sweep. |
| `model/population_utility_scenarios.csv` | Population and utility-load scenarios. |
| `model/model_snapshot.json` | Headline figures (LOA, beam, footprint, areas, weight totals). |

## Provenance

Produced via a **Deckhand Open Deck** chat session on **2026-06-03** — an AI agent driving
the modelling work from a chat message under Deckhand's auditable, PR-only guardrails. This
example is the first migration of that work out of an ephemeral working area and into the
public sandbox (Deckhand issue
[vamseeachanta/deckhand#35](https://github.com/vamseeachanta/deckhand/issues/35)).

## How to regenerate

The script has no third-party dependencies (standard library only):

```bash
cd examples/freedom-ship
python3 build_freedom_ship_weight_area_model.py
```

It writes the CSVs, `model_snapshot.json`, and the HTML report into `./model/` by default.
To send the output elsewhere, set `FREEDOM_SHIP_OUTDIR`:

```bash
FREEDOM_SHIP_OUTDIR=/tmp/freedom-ship python3 build_freedom_ship_weight_area_model.py
```

The report carries its own generation timestamp, so a re-run updates that line; the
underlying model figures are deterministic.

## Caveats (read these)

- **Concept-level, not class-approved.** No flag-state, IMO/SOLAS, MARPOL, or class-society
  (ABS / DNV / LR / BV) review has been done. This is a parametric study, not a design.
- **Parametric, not analysed.** Areas, efficiency factors, mass densities, and KG values are
  first-pass estimates. There is no structural FE, stability, seakeeping, or mooring analysis
  behind them.
- **Hydrostatics are simplified.** The capacity sweep is a coarse displacement-vs-draft
  relation, not a validated hydrostatic curve set.
- **Illustrative only.** Treat every number as a starting point for discussion, not a result.
