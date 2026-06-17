# Marketing demo-clip generator (Option B — deterministic render)

Generates crisp, branded **animated** demo clips of a Deckhand workflow — a
realistic chat (Deckhand seeks the right inputs → runs → a report scrolls through
Inputs / Methodology / Outputs → CTA) where the header stays fixed and only the
chat pane scrolls. No computer-use, no live channel, no browser-driver deps.

Tracking: deckhand#402 · epic deckhand#389 (#397). Every demo's numbers are
grounded in a real run of its workflow.

## Data-driven: one engine, one spec per workflow
- `template-anim.html` — the engine. Builds the chat + report DOM from a `SPEC`
  object and animates it on a deterministic timeline via `window.seek(t)`.
- `specs/<slug>.json` — one per workflow: channel, title, the chat `turns[]`
  (ask → probe → reply → restate → result), the `report` (inputs/methodology/
  outputs), and the locked `closing` CTA. HTML fields use single-quoted
  attributes so the file stays valid JSON.
- `demos/<slug>.mp4` — the rendered clip (2400×1350, ~37 s, H.264). MP4 is the
  master; for Telegram it autoplays inline like a GIF. (GIFs optional —
  re-render with `GIF=1`.)

## Build & render
```bash
bash build-demo.sh <slug>          # specs/<slug>.json -> demo-<slug>.html (+ .dur)
SLUG=<slug> bash render-anim.sh     # -> demos/<slug>.mp4   (GIF=1 also emits .gif)
bash render-all.sh                  # build + render every spec in specs/
bash view.sh                        # gallery at http://localhost:8777/ (loopback)
```
Tunables (env): `FPS` (24), `W` parallel workers (10), `GIF`/`GIF_FPS`/`GIF_W`.
Pacing lives in each spec's per-turn `hold` ms; the engine derives the timeline.

## How it captures (sandbox-safe)
`render-anim.sh` drives the page with a `?t=<ms>` URL param and captures one PNG
per frame via `google-chrome --headless --screenshot`, fanned across `W` parallel
workers, then `ffmpeg` assembles them. No DevTools/debug port needed.

Requirements: `google-chrome` (headless), `ffmpeg`, `python3`, `bc`.

## Adding a workflow
Copy an existing `specs/*.json`, swap in the real workflow's probe/inputs/result
numbers (run the workflow first — keep it truthful) and the locked CTA, then
`build-demo.sh` + `render-anim.sh`. Operator-only; never wire into a client or
Open Deck channel.
