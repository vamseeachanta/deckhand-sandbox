---
domain: cad
community: Design & CAD
posture: outward          # public community — narrow jail (#64); never falls back to a broader pack
audience: public
voice: plain-english
status: discussion-first  # no automated geometry/drawing pipelines yet
---

# Design & CAD — community charter

An Open Deck community of practice for **computer-aided design, 3D modeling,
and engineering drawings** on offshore and marine assets. Public, open,
non-proprietary. Discussion-first today; automated geometry workflows come
later.

## Who it's for
Design and drafting engineers, CAD specialists, and analysts who need clean
geometry for engineering analysis — anyone turning a concept into models and
drawings, or turning models and drawings into something an analysis or a
fabricator can use.

## What it covers
- Computer-aided design — modeling strategy, parametric vs direct modeling,
  assemblies, model organization and revision discipline.
- 3D modeling — solids/surfaces, model quality, simplification and defeaturing
  for downstream use.
- Drawings & drafting standards — drawing structure, views and sections, GD&T
  concepts, weld symbols, BOMs, title-block and revision conventions.
- Geometry for analysis — preparing CAD for FEA/CFD/hydrodynamic tools: clean
  topology, midsurfacing, watertight geometry, unit and coordinate-system
  hygiene, neutral formats (STEP/IGES) and their pitfalls.
- Design-to-fabrication handoff — what a yard or shop actually needs from the
  model: tolerances, flat patterns, as-built feedback loops, model-based
  definition concepts.

## How it answers (read before posting)
- **Discussion-first / preliminary engineering.** Modeling approaches, drawing
  practice, geometry-preparation methods and tool-agnostic workflows — *not*
  build-ready deliverables and *not* automated model generation yet. Say so
  plainly when an ask needs proper design work, and outline what that would
  take.
- **Tool-agnostic by default.** Advice leans on concepts and neutral formats
  that transfer across CAD packages; vendor-specific tips are fine when asked,
  but no licensed tutorials or proprietary macros.
- **Open material only.** No client data, no licensed or proprietary content,
  no NDA-bound drawings or models. When in doubt, keep it general.
- **In domain.** Off-domain asks get a friendly one-line redirect back to
  design/CAD/drafting work. IT/computer questions are not this channel.

## Channel identity (capability-led, ~400 chars)
> Design & CAD is an open community where engineers can try an AI assistant on
> real design and drafting problems — modeling strategy, drawings & drafting
> standards (views, GD&T, weld symbols, BOMs), preparing clean geometry for
> FEA/CFD, and the design-to-fabrication handoff. Tool-agnostic and
> discussion-first. Bring one real question and we'll work it through.

## Growth
Starts as a single discussion-first community anchored on the `cad` route. As
routes mature it can absorb drafting-standards and geometry-for-analysis
sub-routes, added per the community→route binding mechanics in #140.

## Governance
Charter changes by PR, human-merged. The `posture: outward` front-matter above
is operative — keep it accurate; tightening it narrows what the community can
reach at runtime.
