# Marketing GIF pipeline (Option B — deterministic render)

Generates crisp, branded demo clips of a Deckhand workflow **without** computer-use
or any live channel: an HTML scene template is rasterised by headless Chrome and
stitched with ffmpeg crossfades into an MP4 (crisp master) + GIF (loop).

Prototype for `digitalmodel:mooring-fatigue` (Floating & Marine Systems). Tracking
issue: deckhand#402. Part of the marketable-workflows epic deckhand#389 (#397).

## Files
- `demo.html` — the scene template. Drive it with `?scene=0..5`:
  0 title · 1 user prompt · 2 intake · 3 running · 4 result · 5 closing CTA.
  Content (prompt, result rows, CTA, logic-flow rail) is the part to parametrise
  per workflow; result numbers should be sourced from the workflow's real run output.
- `render.sh` — screenshots each scene (HiDPI) → ffmpeg variable-duration xfade →
  `mooring-fatigue-demo.mp4` + `.gif`. Prints the **total video time**.
  Tunables at the top: `DSF` (capture scale, default 2x = 2400×1350), `DURS`
  (per-scene hold seconds), `XF` (crossfade), `GIF_W` (gif width).
- `view.sh` — serves the folder on `127.0.0.1` (loopback only) so the MP4/GIF/HTML
  open in a browser even over SSH (`ssh -L 8777:localhost:8777 <host>`).

## Usage
```bash
bash render.sh          # -> mp4 + gif, prints duration
bash view.sh            # -> http://localhost:8777/  (Ctrl-C to stop)
DSF=2 DURS=...          # override pacing/resolution via env or edit the array
```

## Notes
- **Operator-only.** This renders on the host; never wire it into a client / Open
  Deck channel (their execution profile is fail-closed toward the host).
- MP4 is the crisp master (CRF 18, 2× capture). For Telegram, send the MP4 — it
  autoplays inline like a GIF and stays sharp. GIF is palette-limited (256 colours)
  regardless of resolution.
- Requirements: `google-chrome` (headless), `ffmpeg`, `bc`, `python3`.
