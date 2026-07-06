# "Deckhand — Start Here" onboarding channel — marketing prep (DRAFT)

Front door for the demo-gallery funnel (#407 / epic #405). Demo CTAs already deep-link here:
`t.me/the_deckhand_bot?start=src_<domain>_<workflow>`. **No lobby** (withdrawn 2026-06-18) — the bot
greets, reads the source tag, and routes the contact onward. Copy is public-safe (no PII).
**Ownership:** this marketing copy belongs in `aceengineer-strategy`; routing config in `deckhand`.

---

## 1. Channel identity
- **Display name:** Deckhand — Start Here
- **@handle:** operator to set (e.g. `@deckhand_start`) — CTAs currently route via `@the_deckhand_bot`
- **Avatar:** Deckhand wordmark (assets/deckhand-wordmark.svg)
- **Description / bio (Telegram ≤255 chars):**
  > Run real offshore & subsea engineering checks from a plain-English chat — mooring, pipelines,
  > cathodic protection, wells, and more. Tap a demo, start here. A product of AceEngineer ·
  > powered by digitalmodel. Demos use synthetic inputs.

## 2. Pinned welcome (the marketing pitch)
> 👋 **Welcome to Deckhand.**
>
> Deckhand runs real engineering calculations — mooring, pipelines, cathodic protection, wells, and
> more — from a plain-English conversation, and sends back a **code-checked report you can keep**.
>
> You probably arrived from one of our demos. Pick what's next:
> • ▶️ **Pick up where that demo left off** — jump into the community for that discipline.
> • 🧭 **Explore by discipline** — Floating & Marine · Subsea & Pipelines · Wells & Subsurface.
> • ⚡ **Run a quick calc now** — try one live in ~90 seconds.
> • 🔒 **Work with your own data** — an operator will reach out privately (we never post your data).
>
> Or just reply with your question.

## 3. Arrival greeting (source-tag aware — fired on `?start=src_<domain>_<workflow>`)
> Welcome 👋 — looks like you came in from the **{workflow_title}** demo ({domain_title}).
>
> Want to ▶️ join the **{domain_title}** community, ⚡ run a quick calc, or 🔒 talk to us about your
> own data? Tap below or just ask.

`{workflow_title}` = the demo's `title.big`; `{domain_title}` = the channel name. If the tag is
missing/unknown → fall back to the generic pinned welcome (§2). Tag must validate against the registry
(#431) — unknown domain/workflow → generic welcome, never an error.

## 4. Next-step actions → routes (settled #408 / #432; no lobby)
| Action | Behavior | Destination |
|---|---|---|
| ▶️ Pick up where the demo left off | tag preserved as lead signal | matching community (floating-marine · subsea-pipelines-integrity · wells-subsurface) |
| 🧭 Explore by discipline | grouped menu | chosen community |
| ⚡ Run a quick calc now | re-run the `src` demo live, else a 3-demo starter set | onboarding sandbox (~90 s, host-fail-closed) |
| 🔒 Work with my private data | PII-free lead signal + "an operator will reach out" | operator HITL → aceengineer-strategy PR (#433) |

**Domain → community routing** (all 3 groups EXIST + bound; Cathodic Protection folds into Subsea):
| Demo domain (`src_…`) | Community |
|---|---|
| floating-marine | Floating & Marine Systems group |
| subsea-pipelines-integrity (incl. all 5 CP demos) | Subsea, Pipelines & Integrity group |
| wells-subsurface | Wells & Subsurface group |

## 5. Prep checklist
### Buildable now (no operator action)
- [x] **#431** — `src_<domain>_<workflow>` parser/validator → **deckhand PR #449** (`src/deckhand/source_tag.py`, 10 tests).
- [x] **Marketing copy filed** → **aceengineer-strategy PR #87** (`marketing-ctas/onboarding.md`).
- [ ] **#432** — CTA handler: parse tag → greet (§3) → route (§4), auto (no lobby). *Edits the live
      `on_pre_gateway_dispatch` plugin hook + can only function once the channel + invite links exist —
      build as a dedicated PR, merge/deploy when the channel is up.*
- [ ] **#433** — PII-free lead signal `{src, wants_private, channel:"onboarding", ts}` → operator HITL.

### Staged config — apply in the SAME PR that creates the channel (else the lockstep bijection test fails)
`config/deckhand/scopes.yml` (onboarding scope, fill line ~291):
```yaml
    channel_repo_bindings:
      - platform: telegram
        channel_id: "<NEW_START_HERE_CHANNEL_ID>"   # from operator create-group
        repo: vamseeachanta/deckhand-sandbox
        authorize_members: true
```
`config/deckhand/routing/channel-registry.yaml` (add under `channels:`):
```yaml
  onboarding:
    channel_id: "<NEW_START_HERE_CHANNEL_ID>"
    tier: hub          # front door, not a demo channel (or add 'onboarding' to ALLOWED_TIERS)
    pointers:
      marketing_ctas: "aceengineer-strategy:strategy/deckhand/marketing-ctas/onboarding.md"
      invite_qr: "aceengineer-strategy:strategy/deckhand/release/assets/qr-onboarding.svg"
```
Then: `python -m pytest tests/deckhand/test_channel_registry.py` must stay green (bijection).

### Operator-gated (only the operator)
- [ ] Create the "Deckhand — Start Here" Telegram channel/bot front door; capture `channel_id`.
- [ ] Mint `DECKHAND_PAT_ONBOARDING` (GitHub App token, deckhand-sandbox-scoped) → `~/.hermes/.env`.
- [ ] Set name/@handle/avatar/description (§1), pin the welcome (§2).
- [ ] Bind the channel (fill `scopes.yml:291`), deploy Hermes (render prompts → restart gateway).
- [ ] Repoint demo CTAs from `@the_deckhand_bot` to the final onboarding handle if different (#409;
      one-line in build-web-v3.mjs + republish gallery).

### Parallel (marketing)
- [ ] aceengineer-strategy#76 — final CTA copy, brand, invite/QR assets.
