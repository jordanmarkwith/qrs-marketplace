<img src="assets/qrs-logo.svg" alt="QRS logo" width="92" height="92">

# QRS — Quantum-Native · Patent QRS-001

**Free, local risk skills + sealed, independently verifiable runs on the QRS
quantum-native engine.** One install gives you three skills that work offline for
free, plus a few free *sealed* runs on the hosted QRS engine. The pitch is not
"our numbers are better" — it's **"don't trust our number; re-run the seal and
check it yourself."**

> **Powered by the QRS quantum-native engine (Patent QRS-001).** That brands the
> platform and is true as a brand statement. It is **not** a claim that any given
> run executed on a quantum processor or was made more accurate by quantum. Every
> sealed run records its *actual* backend in the lineage, and the branding never
> contradicts it. Strong quantum-*advantage* claims are reserved for catastrophe
> tail-risk (rare-event estimation), where the QRS estimator genuinely wins — not
> for the World Cup or other everyday demos.

## What's in the box

| Skill | Cost | Runs where | What it does |
|---|---|---|---|
| **cat-metrics** | Free | Local | Catastrophe loss metrics from a YELT/loss CSV: AAL, OEP/AEP exceedance curves, return-period losses (1-in-10…1000), VaR/TVaR, an EP-curve PNG, a summary table. |
| **grounded** | Free | Local | Per-claim grounding audit of any document: extracts every figure & superlative, classifies sourced / unsourced / illustrative / internally-derived, flags the unsourced, scores "X of Y grounded". |
| **montecarlo** | Free local preview **+** sealed runs | Local + QRS engine | Simulate any uncertain outcome (built-in 2026 World Cup bracket, or your own model) → estimate + Monte Carlo CI. In **sealed** mode, runs on the QRS engine and returns a verifiable `run_id`. |

`cat-metrics` and `grounded` are pure, local credibility builders — no account, no
network, no cost. `montecarlo` adds the hook: a local preview you can play with
now, and sealed runs on the real engine that anyone can verify.

## The honesty promise (this is the product)

- **Modeled is never shown as validated.** The QRS engine is currently
  *honest-unvalidated*; outputs attest **reproducibility, not accuracy**.
- **Sealed ≠ signed.** Until the signing KMS is activated, seals render
  **"UNSIGNED — pre-release"** — never "Verified". The verifier shows this honestly.
- **More sims tighten the estimate; they don't make an outcome more certain.**
- **No fabrication.** Missing inputs → the skills ask. Sealed mode not yet live for
  you → an honest "sealed runs coming online" state, never a faked engine result.

## Setup

The free local skills (`cat-metrics`, `grounded`, and `montecarlo`'s local
preview) need **nothing** beyond Python with `numpy`, `pandas`, and `matplotlib`.

**Sealed runs** call the hosted QRS engine through the bundled `qrs-oracle` MCP
connector, which needs your own API token:

1. Create/sign in to your account at **https://qrsrisk.com**.
2. Generate a personal API token.
3. Set it in your environment as **`QRS_API_TOKEN`** (the plugin reads it from
   there; see `CONNECTORS.md`).

The token is **per-user and is never bundled with the plugin** — a shipped token
would be a leaked shared credential, and your free-run quota is tracked per
account. If no token is set or the engine isn't reachable, sealed mode shows the
honest **"sealed runs coming online — add your QRS token to enable"** state, and
the local preview still works. (The general "sample-and-seal any model" engine mode
and the metered free quota are being brought online; this is expected for now.)

## Using the skills

Just describe what you want — the skills trigger on intent:

- *"Here's my simulated loss file `losses.csv` over 10,000 years — build the EP
  curve and give me the 1-in-100 and 1-in-250."* → **cat-metrics**
- *"Check this investor deck — flag every number that doesn't have a source."* →
  **grounded**
- *"Simulate the 2026 World Cup, 50,000 runs, who wins?"* → **montecarlo** (local
  preview now; sealed when your token + the engine mode are live)
- *"Verify this sealed run."* → **montecarlo** verify flow → **https://qrsrisk.com/trust**

## Freemium funnel

1. Install → `cat-metrics` + `grounded` + `montecarlo` local preview work free.
2. `montecarlo` sealed mode → a few **free sealed runs** per month on the real
   engine (verification is always free and unlimited).
3. **Verify a seal yourself** → **https://qrsrisk.com/trust**.
4. Free sealed-run quota hit → **402** → upgrade for more runs and the catastrophe
   tail-risk product:

| Tier | Price/mo | Sealed runs/mo |
|---|---|---|
| Free / Verify | $0 | 5 (+ unlimited verification) |
| Pro | $499 | 100 |
| Team | $1,999 | 600 |
| Scale | $5,999 | 2,500 |
| Enterprise | Custom | Negotiated |

(Pricing is the current launch plan and may change — see qrsrisk.com for live
pricing. Billing is separate from the seal: a run's seal is identical no matter who
pays.)

## Verify a sealed run

Every sealed run is meant to be checked — by anyone, not just its owner:

> **Don't trust the number — check it yourself.** Verify any QRS seal at
> **https://qrsrisk.com/trust**, via the `qrs_verify_seal` MCP tool, or with the
> open-source `qrs-replay` CLI. Verification proves a run is reproducible and
> traceable to a real sealed run — not that the number is "validated."

## A note on the moat

The QRS sampling core — GPU Monte Carlo + variance reduction + the QAE tail
estimator (the patented QRS-001 IP) — **never ships in this plugin.** `montecarlo`'s
sealed mode is a thin client to the hosted engine. The local preview is a plain,
open NumPy simulator and is labeled as such. That separation is what makes a seal
meaningful: it proves the real hosted engine ran your job, not a local stand-in.

## Brand & visuals

Charts the skills generate (the cat-metrics EP curve, the montecarlo odds chart)
use the QRS data-viz palette — dark teal `#1B3B3A`, navy `#324A6D`, accent teal
`#5BBAB5` on a cream ground — and carry the QRS mark. Palette, logo, and the chart
recipe are in `assets/BRAND.md` (`assets/qrs-logo.svg` + `.png`). Brand styling
never changes a result's status: a local preview stays labeled unsealed, and a
sealed run stays UNSIGNED — pre-release until the KMS is live. Pretty ≠ validated.

## Customization

See `CONNECTORS.md` for the `qrs-oracle` connector and the `QRS_API_TOKEN` setup.

## License

MIT (plugin skills & scripts). The hosted QRS engine and its algorithm are
proprietary and are not included here.
