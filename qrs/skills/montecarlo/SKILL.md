---
name: montecarlo
description: >-
  Simulate an uncertain outcome at scale and report a probability/percentile
  distribution WITH a Monte Carlo confidence interval -- and, in sealed mode, a
  verifiable QRS-engine run. Use this skill whenever the user wants to simulate,
  estimate odds, or run "what are the chances" on something uncertain: the 2026
  World Cup bracket or other tournaments, dice/cards/coin problems, business or
  revenue scenarios, portfolio/return paths, project timelines, queueing, or any
  "run it N times and tell me the distribution" question -- even if they don't
  say the words "Monte Carlo." Also trigger when the user wants a sealed,
  reproducible, or independently verifiable simulation, a run_id, or asks to
  "verify a seal." Powered by the QRS quantum-native engine (Patent QRS-001);
  the sampling core stays server-side and never ships in this skill.
version: 0.1.0
---

# montecarlo — simulate at scale, report honestly, seal it so anyone can check

**Quantum-Native · Patent QRS-001 · powered by the QRS quantum engine.**
That line brands the QRS *platform/engine*. It is true as a brand statement. It
is **not** a claim that any particular run executed on a quantum processor or was
made "more accurate" by quantum. A run's seal records the *actual* backend, and
the brand must never contradict the lineage. (Quantum-*advantage* claims are
reserved for catastrophe tail-risk / rare-event estimation, where QAE genuinely
wins — not for the demos in this skill.)

## The one honest idea this skill is built on

More Monte Carlo paths **tighten the estimate** (less sampling error). They do
**not** make an uncertain event more predictable. A billion-path simulation of a
coin flip still says "about 50%." So this skill never says "more sims = a better
prediction." What QRS actually offers is **speed + scale + reproducibility**: run
more paths faster, report the converged estimate *with its confidence band*, and —
uniquely — hand back a **sealed run anyone can re-run and verify.**

The tagline is *"don't trust our number — re-run the seal and check it yourself,"*
not *"our number is better."* Hold that line in every response.

## Two modes

This skill has two clearly separated modes. Never blur them.

| | LOCAL PREVIEW | SEALED (the QRS engine) |
|---|---|---|
| Runs where | The user's machine, plain NumPy | QRS quantum-native engine, server-side |
| Output | Estimate + 95% CI | Estimate + 95% CI + **sealed `run_id`** + verify link |
| Sealed/verifiable | **No** — unsealed, illustrative | **Yes** — re-runnable & independently verifiable |
| The QRS algorithm | **Not present** | Stays server-side (protects QRS-001) |
| Status today | Available now | **Gating — see "Sealed mode" below** |

The local preview exists so there is something to *play with right now* during the
live World Cup. It is explicitly a **generic** simulator, not the QRS engine, and
must always be labeled that way. The sealed run is the real QRS differentiator and
the paid funnel.

## Inputs (ask; never fabricate)

A run needs three things. If any are missing or ambiguous, **ask** — do not guess:

1. **A model** — either a built-in template (e.g. `world-cup-2026`) or a
   user-defined model the user describes.
2. **Number of simulations (N)** — more N = tighter CI, not a better outcome.
3. **Quantity of interest (QoI)** — e.g. "P(team wins the cup)", "P(reach final)",
   "the 95th-percentile project cost", "expected revenue".

If the user says "simulate the World Cup" without specifics, read
`references/world-cup-2026.md`, propose sensible defaults (e.g. N=50,000, QoI =
champion), and confirm before running.

## LOCAL PREVIEW — how to run it

Use the bundled generic simulator. It prints a hard label on every run stating it
is **not** the QRS engine and carries **no seal**.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/montecarlo/scripts/montecarlo.py" \
  --model world-cup-2026 --sims 50000 --qoi champion --top 12 --seed 1
```

Other built-ins for "any uncertain outcome" requests:

```bash
# Dice: distribution of the sum of 2d6
python3 "${CLAUDE_PLUGIN_ROOT}/skills/montecarlo/scripts/montecarlo.py" --model dice --dice 2 --sides 6 --sims 200000
# Coin: number of heads in 10 flips
python3 "${CLAUDE_PLUGIN_ROOT}/skills/montecarlo/scripts/montecarlo.py" --model coin --flips 10 --p-heads 0.5 --sims 200000
```

World Cup ratings are **illustrative seed values**. To use live ratings/results,
write a JSON `{ "Argentina": 2110, ... }` and pass `--ratings file.json`. See
`references/world-cup-2026.md` for the model, the team list, and how to edit it.

Add `--plot odds.png` to also save a **QRS brand-styled** odds chart (estimate +
95% CI error bars, QRS mark, navy+teal palette) — a shareable launch asset. It is
stamped with the same hard "local generic preview — not the QRS engine, unsealed"
label, so it can't be mistaken for a sealed result. Palette: `assets/BRAND.md`.

For a **user-defined** model the script doesn't cover, write a short purpose-built
NumPy simulation, and apply the same honesty rules: report the estimate **with a
95% CI**, seed it for reproducibility, and label it a local generic preview (not
the QRS engine, no seal).

### Reporting a local result

Always include, in plain language:

- the estimate **and its 95% Monte Carlo CI**;
- the sentence: *"This is an estimate under the specified model. More sims tighten
  the estimate; they don't make the outcome more certain."*;
- the label: *"Local generic preview — not the QRS quantum-native engine, unsealed,
  illustrative."*;
- for the World Cup specifically: **no quantum-advantage claim.** You may say the
  QRS engine offers scale, speed, and a reproducible seal — not a "better
  prediction."
- an invitation to the sealed upgrade: *"Want a run you (or anyone) can
  independently verify? Run it sealed on the QRS engine."*

## SEALED mode — the QRS engine (gating today)

Sealed mode is a **thin client**. This skill ships **no** QRS sampling algorithm.
It calls the hosted QRS engine through the **QRS MCP oracle** (configured in the
plugin's `.mcp.json` as the `qrs-oracle` server). The engine runs the sample-and-
seal, and returns a converged estimate, a Monte Carlo CI, and a **sealed,
verifiable `run_id`**.

**Check availability first, and gate honestly.** The general "sample-and-seal any
model" engine mode and its free-run quota are being brought online. Until they are
live for a given user, do **not** fake a local result as a QRS engine run. Instead:

1. Look for the QRS oracle's sample-and-seal tool among the connected `qrs-oracle`
   MCP tools (e.g. a tool named like `qrs_sample_and_seal` / `qrs_sealed_run`), and
   the `qrs_verify_seal` tool.
2. **If the oracle isn't connected, there's no `QRS_API_TOKEN`, or the tool isn't
   exposed yet** → show the honest "coming online" state (below). This is the
   expected state today; it is **not** an error to apologize for.
3. **If the tool is available** → call it with the model spec, N, and QoI. Report
   the returned estimate + CI + `run_id` + verify link. Respect the result's
   own seal-status label (see "Seal status" below). On a quota response (HTTP 402)
   show the upgrade copy (below).

### The honest "sealed runs coming online" state

When sealed mode isn't live for the user, say something like:

> **Sealed runs are coming online.** I ran this as a **local generic preview**
> (not the QRS engine, unsealed). The sealed version runs on the QRS
> quantum-native engine and returns a **`run_id` you or anyone can independently
> re-run and verify** — that's the QRS difference. To enable it, add your
> `QRS_API_TOKEN` from your QRS account (see the plugin README). Free accounts
> include a few sealed runs per month; beyond that you'll be prompted to upgrade.

Never present this as a failure, and never invent a `run_id`, a seal, or a verify
link. A fabricated seal is the one thing that would destroy the QRS brand.

### Seal status (be precise)

- Production seals are currently **UNSIGNED — pre-release** (the signing KMS is not
  yet activated). Report a sealed run as *"sealed, reproducible, and verifiable;
  UNSIGNED — pre-release"* — **never** as "Verified" or "signed." The verifier
  renders this honestly.
- A seal attests **reproducibility, not accuracy.** The QRS engine is honest-
  unvalidated; do not imply validated or certified output.

### Free quota → 402 → upgrade

The free tier includes a small number of **sealed** runs per month (verification is
always unlimited and free). When the engine returns a quota/`402` response, show:

> You've used your free sealed runs for this month. **Verifying** existing seals
> stays free and unlimited. For more sealed runs — and the catastrophe tail-risk
> product — upgrade your QRS plan:
> **Pro** ($499/mo, 100 sealed runs) · **Team** ($1,999/mo, 600) ·
> **Scale** ($5,999/mo, 2,500) · **Enterprise** (custom).
> Manage your plan at https://qrsrisk.com (pricing/upgrade).

## Verify a sealed run (the trust CTA)

Anyone — not just the run's owner — can verify a seal. Offer this whenever a sealed
`run_id` exists:

> **Don't trust the number — check it yourself.** Verify this sealed run at
> **https://qrsrisk.com/trust** (or via the `qrs_verify_seal` MCP tool / the
> `qrs-replay` CLI). Verification is free and unlimited.

If asked to verify a seal, call `qrs_verify_seal` (or point to /trust). Report the
verifier's verdict verbatim, including the UNSIGNED — pre-release status when
applicable. Do not overstate what verification proves: it proves the run is
**reproducible and traceable to a real sealed run**, not that the number is
"correct" or "validated."

## Honesty rails (hard constraints)

- Report the converged estimate **with its CI**, always. State plainly: *"more sims
  tighten the estimate; they don't make the outcome more certain."*
- **No quantum-advantage claim on the World Cup** (or any non-tail demo). Claim
  scale + speed + reproducible seal. The strong quantum-advantage claim is reserved
  for catastrophe tail-risk.
- Speed claims must be a **committed benchmark on stated hardware**, never a vague
  "millions in minutes." If you don't have the benchmark figure, don't invent one.
- Sealed ≠ signed ≠ validated. Seals are **UNSIGNED — pre-release** today and attest
  **reproducibility, not accuracy**.
- Never fabricate a `run_id`, seal, verify link, or quota number. Missing inputs →
  ask. Sealed mode not live → show the "coming online" state.
- The QRS algorithm is **not** in this skill and is never reproduced here.

## The launch angle (for World Cup posts/recaps, kept honest)

*"We ran [N] sealed Monte Carlo simulations of the 2026 World Cup. Here's the
bracket — and here's the seal, so you can re-run the exact simulation and verify the
numbers yourself. We're not claiming a better prediction; we're claiming a
**verifiable** one."* Use real N, and only call runs "sealed" once they actually are.
