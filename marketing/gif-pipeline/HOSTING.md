# Demo hosting & distribution — decision record (deckhand#420)

Status: **proposed** (recommendation; operator sign-off needed on the 3 starred items)
Date: 2026-06-17 · Epic #389 / #397 / #409 · supersedes the "hosted link: TBD" in `send-packs.md`

One canonical model for hosting and distributing the Open Deck demo assets across
**every** marketing surface (Telegram, website, email, LinkedIn, YouTube), reusable
for all ventures — not just this batch.

## Context

- The pipeline (`marketing/gif-pipeline/`) is **data-driven**: one engine
  (`template-anim.html`) + one `specs/<slug>.json` per workflow → a deterministic
  animation. Today it renders to `demos/<slug>.mp4` (2400×1350, ~37 s, H.264, ~4–5 MB).
- 12 Tier-A demos = **~52 MB of MP4 in git** today, and it grows with every demo
  (CP set #417 adds 5 more). The same specs can also animate **live in a browser**
  (no video file) — the engine just needs an autoplay loop instead of a `?t` seek.
- Two distinct things need a "home": the **binary master** (for Telegram/LinkedIn
  native upload) and the **canonical viewing link** (for email/web/LinkedIn-as-link).

## Decision

**Two homes, one canonical link.**

1. **Canonical viewing link = an in-browser live gallery on aceengineer.com**
   (`https://aceengineer.com/demos/deckhand/`), generated from the specs by
   `build-web.mjs` → `web/`. It animates the *same* specs in-browser, so:
   - **no video binary on the production website** (zero repo bloat there),
   - it is **always in sync** with the specs (re-generate on spec change),
   - it is **one durable link** usable in email, LinkedIn, and the website itself.
   Each demo card carries a source-tagged CTA → onboarding (below).

2. **Binary master = deckhand-sandbox** (`marketing/gif-pipeline/demos/*.mp4`),
   the source of truth for the MP4s that get **uploaded natively** to Telegram and
   LinkedIn. To stop git bloat, publish the MP4s as **GitHub Release assets** on
   deckhand-sandbox (one tagged release per refresh, e.g. `demos-2026.06`) and keep
   only `specs/` + one **poster PNG per demo** in-tree (★ migration below).

3. **Source of truth for the animation is always `specs/<slug>.json`.** MP4, GIF,
   live page, and poster are all *derived* — never hand-edited.

## Per-surface delivery matrix

| Surface | Asset format | Host | Link / action |
|---|---|---|---|
| **Telegram** (primary funnel) | **MP4**, native inline autoplay | sent in-chat | upload the `demos/<slug>.mp4` file (~4–5 MB) |
| **Website** (aceengineer.com) | **live in-browser animation** (no file) | GitHub Pages | `https://aceengineer.com/demos/deckhand/` |
| **Email** | **static poster PNG** + link (avoid MP4/GIF attach — size + client autoplay blocks) | poster inline, link to site | poster + "watch the 35-s demo →" → live page (UTM) |
| **LinkedIn** | **native MP4 upload** (best reach) *or* link to live page | LinkedIn native / link | upload MP4; put the live-page link in the first comment |
| **YouTube** (optional) ★ | MP4 upload, **unlisted → public** | aceengineer channel | gives analytics + auto-captions; embed on site / link in email |
| **CDN / raw link** | raw MP4 | **GitHub Release assets** (no separate CDN needed yet) | raw release asset URL |

## Attribution

- **Funnel entry (all CTAs):** the onboarding deep link
  `t.me/the_deckhand_bot?start=demo_<domain>[_<workflow>]` — the existing
  `send-packs.md` / #409 scheme. Onboarding attributes + routes by the `start` tag.
- **Web/email/LinkedIn link clicks:** add **UTM** to the live-page link so the
  site's existing Google Analytics attributes the surface:
  `…/demos/deckhand/?utm_source=<linkedin|email|web>&utm_medium=<social|email>&utm_campaign=opendeck&utm_content=<slug>`.
- **YouTube:** its own analytics; keep the same `?start=` CTA in the description.
- Telegram `?start=` tags the funnel; UTM tags the surface — they compose.

## Privacy / ownership

- The live gallery is **public** (it is marketing). Every demo uses **synthetic
  inputs** — no client PII in any spec, MP4, poster, or page (consistent with the
  open-deck isolation rules).
- YouTube: **unlisted** for targeted sends, **public** only for broad campaigns (★).
- Binary ownership: deckhand-sandbox (private repo) + a public Release for raw links.

## ★ Operator / owner decisions (needed before publish)

1. **Publish the live gallery to aceengineer.com?** The website repo requires
   plan + owner approval before implementation; the generated `web/` is ready to PR.
2. **YouTube channel** — confirm the aceengineer channel + unlisted-vs-public default.
3. **Migrate MP4s to a GitHub Release** (recommended, de-bloats git ~52 MB→specs+posters)
   vs. keep them in-tree. Either way the live page is the canonical link.

## Setup steps (once the ★ items are decided)

1. `node build-web.mjs` → regenerates `web/` (gallery + one live player per demo + posters).
2. Copy `web/` into aceengineer-website as `content/demos/deckhand/` (source) — the
   site build (`npm run build`, posthtml) publishes it to `/demos/deckhand/`; add a
   link from `content/demos/index.html`. Open a PR for owner approval.
3. (Optional) `gh release create demos-2026.06 demos/*.mp4 -R vamseeachanta/deckhand-sandbox`
   then gitignore `demos/*.mp4` and commit posters only.
4. Fill `send-packs.md`: replace `[hosted link: TBD …]` with
   `https://aceengineer.com/demos/deckhand/` (+ per-surface UTM).
5. (Optional) Upload MP4s to YouTube (unlisted), embed the playlist on the page.
