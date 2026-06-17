# Release plan — Deckhand v3 GTM demo distribution (ADR)

Status: **proposed** — needs operator sign-off on the 4 ★ items.
Date: 2026-06-17 · Epic deckhand#389 / #397 / #405 · funnel #431 / #409 / #407.
**Supersedes the binary-hosting half of `HOSTING.md` (#420)** — see "What this changes".

## Two facts that change HOSTING.md's assumptions
1. **v3 is real MP4**, not the v2 in-browser live-animation page. There is now a binary to host
   (`build-web-v3.mjs` → `web-v3/` MP4 `<video>` grid).
2. **aceengineer.com runs on Vercel, not GitHub Pages** (`vercel.json`: build `npm run build`,
   out `dist`, 301 apex→`www.`; CNAME aceengineer.com). Vercel CDN serves static assets with an
   immutable long-cache header already set for `/assets/*`. The GitHub-Pages bandwidth limits in
   HOSTING.md **do not apply**. GA4 is live: **`G-K31E51DQ47`**.

## Verified external limits (informing the matrix)
| Limit | Value | Implication |
|---|---|---|
| Telegram bot `sendVideo` | **50 MB**; MP4/H.264 autoplays inline; `supports_streaming` | All 34 cuts (max ~9 MB) send natively — no host needed |
| GitHub Release asset | **2 GiB/file**, **no bandwidth cap** | Durable raw master for 250 MB |
| YouTube Shorts | 9:16, 1080×1920, ≤180 s | The `v` cuts qualify as-is |
| LinkedIn native | native ≈5× reach; external link in body ≈60% penalty | Upload natively; link in first comment |
| Email | MP4 attach tanks deliverability; poster+link CTR higher | Never attach MP4 — poster PNG → linked gallery |

## Decision
1. **Canonical binary home = a GitHub Release** on `vamseeachanta/deckhand-sandbox` (tag `demos-2026.06`,
   all 34 MP4s + 17 posters) — durable raw master for Telegram/LinkedIn native upload; de-bloats git
   (gitignore `demos/*.mp4`, keep `specs/` + posters). **+ a Vercel-served copy** of the MP4s co-located
   with the gallery for in-browser `<video>` playback (250 MB is fine on Vercel CDN).
2. **Gallery → aceengineer.com `/demos/deckhand/`** (Vercel): `build-web-v3.mjs` output → website repo
   `content/demos/deckhand/`, MP4s + posters co-located. Canonical URL
   **`https://www.aceengineer.com/demos/deckhand/`** (note `www.`). Doubles as the ecosystem advert.
   (YouTube adopted as a *secondary* surface for Shorts + analytics, not the binary home. Object-store/CDN
   unnecessary at 250 MB.)

## Per-surface distribution matrix
| Surface | Cut / format | Host | Link / action |
|---|---|---|---|
| **Telegram** (primary) | 16:9 MP4 native inline | sent in-chat (file) | upload `demos/<slug>.mp4` (≪50 MB); Tier B = card PNG |
| **Website** | MP4 `<video>` autoplay-muted-loop grid | Vercel (co-located) | `…/demos/deckhand/?utm_source=web&utm_medium=referral&utm_campaign=opendeck` |
| **YouTube** | 9:16 `v` cut → **Shorts**; 16:9 → unlisted (optional) | aceengineer channel | unlisted (targeted) / public (broad); `?start=` CTA + gallery link in description |
| **Email** | **poster PNG + link** (never attach MP4) | poster inline; link → gallery | `…/demos/deckhand/?utm_source=email&utm_medium=email&utm_campaign=opendeck&utm_content=<slug>` |
| **LinkedIn** | **native upload — 9:16 `v` cut** | LinkedIn native | upload directly; gallery link in first comment; `utm_source=linkedin&utm_medium=social` |
| **Raw / fallback** | raw MP4 | GitHub Release asset | `…/releases/download/demos-2026.06/<slug>.mp4` |

## Links & attribution
- **Funnel entry (every CTA):** `t.me/the_deckhand_bot?start=src_<domain>_<workflow>` per contract #431 —
  **do NOT hand-format**; `build-web-v3.mjs` emits `data-start="src_<domain>_<slug>"`, the append wires via #409.
- **Web/email/LinkedIn:** UTM on the gallery link so the live GA4 (`G-K31E51DQ47`) attributes the surface.
- Telegram `?start=` tags the funnel; UTM tags the surface — orthogonal, both fire.

## Privacy / ownership / cost
Public-safe (synthetic inputs, no PII). `deckhand-sandbox` owns the public artifacts + Release;
`aceengineer-website` owns the published gallery. **Cost = $0** (Release + Vercel + YouTube all free).

## Runbook (ordered)
1. `node build-web-v3.mjs` → `web-v3/`. *(automatable)*
2. `gh release create demos-2026.06 demos/*.mp4 posters/*.png -R vamseeachanta/deckhand-sandbox -t "Deckhand demos 2026.06"`; then gitignore `demos/*.mp4`, commit specs+posters. *(★ confirm git-removal)*
3. **Publish gallery (operator-gated PR to aceengineer-website):** copy `web-v3/index.html` → `content/demos/deckhand/`, co-locate the two main-cut `demos/` + `posters/`; link from `content/demos/index.html` + `content/deckhand.html`; `npm run build`, verify `<video>` srcs resolve; PR for owner approval (website governance). Vercel deploys on merge.
4. **YouTube (operator):** upload 17 `v` cuts as Shorts (unlisted), optionally 16:9 unlisted; `?start=` CTA + gallery link in descriptions.
5. **Wire CTAs (#409/#431):** confirm `?start=src_<domain>_<slug>` resolves per demo (gated on #409; until then the generic front door).
6. **Fill `send-packs.md`:** replace `[hosted link: TBD]` → `https://www.aceengineer.com/demos/deckhand/` + UTM template. *(automatable PR)*
7. **Distribute per the matrix** — Telegram native first, then web/email/LinkedIn/YouTube campaigns.

## ★ Operator decisions / sign-offs
1. **Publish the v3 gallery to aceengineer.com?** (`content/demos/deckhand/`) — co-locate ~250 MB of MP4 on Vercel, OR point `<video>` at the Release raw URLs to keep the website repo lean (trades repo size for cross-origin).
2. **YouTube channel + privacy default** (unlisted vs public; Shorts in-scope this wave?).
3. **De-bloat git via Release** (290 MB → specs+posters) vs keep MP4s in-tree.
4. **LinkedIn lead cut** — recommendation is the 9:16 `v` cut (more organic reach) vs 16:9.

## What this changes vs HOSTING.md (#420)
- **Binary home:** #420 said "no video binary on the website"; v3 reverses this (MP4 co-located on Vercel + Release raw master).
- **Host platform:** #420 cited GitHub Pages bandwidth limits — corrected: the site is on **Vercel** (no Pages ceiling).
- **Canonical link:** corrected to the `www.` host (Vercel 301s the apex).
- **CTA scheme:** `demo_*` → `src_*` per #431.
- **Unchanged:** specs are source of truth; synthetic-only/no-PII; UTM+`?start` composition; Telegram native MP4 primary; YouTube secondary.

Sources verified by the research pass: GitHub Releases/Pages limits, Telegram sendVideo, YouTube Shorts specs, LinkedIn video specs/algorithm, cold-email attachments-vs-links.
