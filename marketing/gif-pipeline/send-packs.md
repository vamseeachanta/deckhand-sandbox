# Deckhand Open Deck — channel send packs

Ready-to-distribute outreach material, one section per channel. Locked 2026-06-16 (deckhand#389 / #397 / #409).

**Funnel (all channels):** every CTA points to the onboarding front door — message **@the_deckhand_bot** ("Deckhand — Start Here") with the source-tagged deep link `t.me/the_deckhand_bot?start=<tag>`; onboarding greets, qualifies, and routes the contact to the named channel (deckhand#407/#408).

**Distribution (all channels):**
- **Telegram (primary):** send the asset **natively in-chat** — Tier A = the demo **MP4** (autoplays inline, ~4–5 MB); Tier B = the prompt **card PNG**.
- **LinkedIn / email / website:** link to the **aceengineer-website demo page** (hosted gallery, animates in-browser) and/or YouTube (aceengineer channel). [hosted link: TBD — pending aceengineer-website page]

---

## 🌊 Floating & Marine Systems  (Tier A — runnable demos)
**For:** FPSO/floater naval architects · mooring & station-keeping engineers · marine-operations leads · hull/seakeeping specialists.
**Invite:** *A working assistant for floating & mooring systems — ask a real question in plain English and it runs the calc and sends back a code-checked answer with a report. Here's a 35-second look.*
**Assets:** `demos/mooring-fatigue.mp4` · `demos/fpso-spread-mooring.mp4` · `demos/hull-seakeeping.mp4` · `demos/ocimf-tanker-loads.mp4`
**Try asking (send-this prompts):**
- "Screen the fatigue life of my R4 chain mooring in 1500 m." → `start=demo_floating-marine_mooring-fatigue`
- "Spread-mooring safety-factor check for my 12-line FPSO in 1200 m." → `start=demo_floating-marine_fpso-spread-mooring`
- "Natural periods, RAOs and motion comfort for this hull?" → `start=demo_floating-marine_hull-seakeeping`
- "Wind + current loads on a 320 m VLCC at 30° (OCIMF)?" → `start=demo_floating-marine_ocimf-tanker-loads`

## 🛢️ Subsea, Pipelines & Integrity  (Tier A — runnable demos)
**For:** subsea/pipeline engineers · flowline & integrity engineers · asset-integrity/inspection leads · geotechnical engineers.
**Invite:** *Quick pipeline & integrity screens to the design codes — answer in minutes, with a report you can keep. Short demo attached.*
**Assets:** `demos/wall-thickness-quickcheck.mp4` · `demos/on-bottom-stability-f109.mp4` · `demos/free-span-f105.mp4` · `demos/api579-pipe-ffs-b318.mp4`
**Try asking:**
- "Min wall thickness for a 12-inch X65 line at 250 bar?" → `start=demo_subsea-pipelines-integrity_wall-thickness-quickcheck`
- "On-bottom stability for my 16-inch line in a 1-year storm (F109)?" → `start=demo_subsea-pipelines-integrity_on-bottom-stability-f109`
- "Allowable span for this 40 m free span (F105)?" → `start=demo_subsea-pipelines-integrity_free-span-f105`
- "Fitness-for-service on my corroded line from these readings (API 579)." → `start=demo_subsea-pipelines-integrity_api579-pipe-ffs-b318`

## ⛏️ Wells & Subsurface  (Tier A — runnable demos)
**For:** production & reservoir engineers · petroleum economists / FDP leads · artificial-lift engineers · drilling engineers.
**Invite:** *From a rate curve or a dynamometer card to a forecast, an economics case, or a pump diagnosis — ask and get the result. Quick demo here.*
**Assets:** `demos/production-forecast-arps.mp4` · `demos/fdas-field-npv.mp4` · `demos/nodal-analysis.mp4` · `demos/dynacard-diagnostics.mp4`
**Try asking:**
- "Fit an Arps decline and give me the EUR from this monthly oil rate." → `start=demo_wells-subsurface_production-forecast-arps`
- "NPV, IRR and payback for an 8-well field at $60/bbl?" → `start=demo_wells-subsurface_fdas-field-npv`
- "IPR/VLP operating point for this well?" → `start=demo_wells-subsurface_nodal-analysis`
- "Read this dynamometer card — what's wrong with my pump?" → `start=demo_wells-subsurface_dynacard-diagnostics`

---

## 📐 Codes, Standards & Maritime Law  (Tier B — advisory; prompt card)
**For:** verification/certification engineers · project engineers choosing codes · QA/compliance leads · marine/regulatory advisors.
**Invite:** *Which code applies — and what does the clause actually say? Ask and get a standards-grounded answer with the citation. (For a full study, a tracked request, 24-hour response.)*
**Asset:** `cards/codes-standards-maritime-law.png`  · card title: **"The governing code and clause — cited."**
**Try asking:** which design code/standard governs a piece of work (and why) · what a specific code clause requires, with the citation · the standards a project needs to meet · classification-society, flag-state & IMO requirements.
**Source tag:** `start=demo_codes-standards-maritime-law`

## ⚡ Power, Electrical & Controls  (Tier B — advisory; prompt card)
**For:** offshore electrical engineers · power-systems & controls engineers · electrification/feasibility leads · subsea power specialists.
**Invite:** *Offshore power & controls — from electrification feasibility to protection coordination. Ask, and we'll point you the right way (or open a tracked study).*
**Asset:** `cards/electrical.png`  · card title: **"Offshore power & controls — feasibility to protection."**
**Try asking:** plan an offshore electrification / power-from-shore feasibility study · what a load-flow + short-circuit study needs · how to coordinate protection on a switchboard · what drives subsea power-umbilical sizing on a long tieback.
**Source tag:** `start=demo_electrical`

## ✏️ Design & CAD  (Tier B — advisory; prompt card)
**For:** design engineers · CAD/drafting leads · geometry-for-analysis specialists · design-to-fabrication coordinators.
**Invite:** *Plan clean handoffs — 3D model to analysis, and design to fabrication. Ask and get a grounded checklist (or open a tracked review).*
**Asset:** `cards/cad.png`  · card title: **"Plan your CAD-to-analysis & fabrication handoffs."**
**Try asking:** plan a 3D-model-to-analysis handoff · what a drawing-package review covers · geometry cleanup to make a part mesh-ready · what a clean design-to-fabrication handoff needs.
**Source tag:** `start=demo_cad`

## 🔧 Manufacturing & Fabrication  (Tier B — advisory; prompt card)
**For:** fabrication & welding engineers · QA/QC and NDE leads · production-planning engineers · shop/yard managers.
**Invite:** *Welding, NDE and fabrication quality — planned. Ask and get a grounded plan (or open a tracked review).*
**Asset:** `cards/manufacturing.png`  · card title: **"Plan welding, NDE & fabrication QA."**
**Try asking:** plan a welding-procedure (WPS/PQR) review · fabrication tolerances for a welded assembly · NDE coverage for a set of welds · a quality plan for a fabrication package.
**Source tag:** `start=demo_manufacturing`

---

### Notes
- Tier B is advisory (no runnable compute yet) → cards, not demos. A demo replaces a card the moment a runnable path lands (e.g. cathodic-protection for Subsea, #403).
- Source tags use the onboarding deep-link scheme `demo_<domain>[_<workflow>]` so onboarding can attribute and route (deckhand#409).
