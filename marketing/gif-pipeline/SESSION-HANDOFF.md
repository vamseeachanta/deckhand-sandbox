# Session handoff — Deckhand marketing demos + onboarding funnel (2026-06-18/19)

Big multi-thread session: v3 demo gallery → GitHub Pages hosting → onboarding funnel
(#407) built B-then-A → 2 parallel demo sessions integrated. Cross-session durable
record also in auto-memory: `deckhand-demo-gallery-live`, `deckhand-onboarding-lobby-directive`.

## LIVE now
- **Demo gallery (the link to send):** https://vamseeachanta.github.io/deckhand-sandbox/review-94111d02a8/
  — link-only (unguessable + `noindex`), **18 demos**, left sidebar topic menu, real-frame thumbnails,
  click-to-play lightbox, onboarding CTAs. **Root redirects** to it. Binaries in the **`demos` GitHub
  Release** (`--clobber`). Update flow: `bash update.sh <slug>` → `bash publish-demos.sh <slug>`.
- **Onboarding "Deckhand — Start Here" group:** Telegram `chat_id -5565822305`, invite
  `https://t.me/+iUstcUn2dHA4YWQ5`, bot admin. **Phase B deployed** (binding + per-scope greeting +
  allowlist + gateway restart). Pending: owner **test-join** + set **avatar (wordmark) + description**.

## PRs
| Repo | PR | What | State |
|---|---|---|---|
| deckhand | #449 | `src_` tag parser `source_tag.py` | MERGED |
| deckhand | #450 | bind Start Here channel (scopes+registry+groups+tier) | MERGED |
| deckhand | #451 | onboarding welcome greeting (per-scope override) | MERGED |
| deckhand | #459 | rebase `05-skill-resolution.patch` drift | MERGED |
| deckhand | #460 | **Phase A** `deckhand-onboarding` plugin (`/start src_` DM handler) | **MERGED — needs deploy** |
| aceengineer-strategy | #87 | onboarding marketing copy | MERGED |
| deckhand-sandbox `feat/marketing-cta-polish` | — | all gallery/CTA/factory work | committed (3b66cf1 + 096bab1 + a141860 + 80b31d0 + 471093c); **branch not yet PR'd to main** |

## PENDING — operator
1. **Test-join** `t.me/+iUstcUn2dHA4YWQ5` (non-operator acct) → confirm "Welcome to Deckhand — Start Here" greeting. Set group **avatar + description** (§1 of `START-HERE-CHANNEL.md`).
2. **Deploy Phase A** (#460 merged): `cd /mnt/local-analysis/deckhand` (must be deploy path that feeds `deckhand-live`) → `bash scripts/deckhand/bootstrap-gateway-clone.sh --apply` → `bash scripts/deckhand/deploy-preflight.sh` (now GO — #459 cleared the drift) → `bash scripts/deckhand/install-hermes-b2.sh --apply` → `hermes gateway restart`. Smoke: `/start src_floating-marine_mooring-fatigue` from a non-operator acct → named-discipline DM greeting.
3. **THEN flip the gallery CTAs to activate Phase A per-demo routing:** in `build-web-v3.mjs`, the card CTA `href` `${START_HERE}` → `${FRONT_DOOR}?start=${tag}` (header start button too), then `bash publish-demos.sh`. Do this **after** Phase A is deployed + smoke-tested (else CTAs hit an unhandled DM). *(An agent/owner can ask this session's successor to do it.)*
4. **Open the `feat/marketing-cta-polish` → main PR** for deckhand-sandbox when the marketing work is ready to merge.
5. **Restore the deckhand human clone branch:** I switched `/mnt/local-analysis/deckhand` to `main` during the Phase-B deploy; another session's work was on `docs/lr-coordination` → `git -C /mnt/local-analysis/deckhand checkout docs/lr-coordination` (coordinate first).
6. **Phase-out** the github.io gallery ~**2026-06-25** (1-week review window). A session-cron was set but is not durable across restarts — do it manually or re-schedule: `gh api -X DELETE repos/vamseeachanta/deckhand-sandbox/pages`.

## GOTCHAS (cost time this session)
- **Gateway deploys from `/mnt/local-analysis/deckhand-live`** (dedicated pristine clone, #152 isolation), NOT the human clone. Refresh it with `bootstrap-gateway-clone.sh --apply` (pins detached @ origin/main); `deploy-preflight` reads patches from there, so a fix isn't "live" until merge + refresh.
- **Shared `deckhand-sandbox` working tree** (`feat/marketing-cta-polish`) — 3+ sessions; **don't branch-switch** while others have uncommitted work; commit selectively.
- **`publish-demos.sh` deploys the gallery to the REVIEW PATH + root redirect** (reads `.review-token`, gitignored). **Never push the gallery to gh-pages root** — that clobbers the redirect (happened once, fixed).
- **`.review-token`** holds the unguessable review path — gitignored so the link-only URL stays out of the public repo.

## NEXT THREADS (for the successor)
- **Activate Phase A** = deploy #460 + flip CTAs (pending-#2/#3 above) → per-demo `?start=src_` routing live with attribution.
- **Per-discipline invites (option ii):** config-only — add `invite_link:` per discipline in `channel-registry.yaml`; the `deckhand-onboarding` plugin already has the fallback seam (`# TODO(#407 ii)`).
- **Dynacard / upstream fixes** flagged in `QA-HICCUPS.md` (classifier + synthetic-card calibration).
- **aceengineer.com echo** of the gallery URL (deep-link card) when content is final.
