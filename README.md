<img src="qrs/assets/qrs-logo.svg" alt="QRS logo" width="84" height="84">

# QRS plugin marketplace

The official marketplace for the **QRS** plugin — Quantum-Native · Patent QRS-001.
Free, local risk skills plus sealed, independently verifiable runs on the QRS
quantum-native engine.

## Install

In Claude Code or Cowork:

```
/plugin marketplace add YOUR_GH_USER/qrs-marketplace
/plugin install qrs@qrs-risk
```

Or from the CLI:

```
claude plugin marketplace add YOUR_GH_USER/qrs-marketplace
claude plugin install qrs@qrs-risk
```

(Replace `YOUR_GH_USER/qrs-marketplace` with the repo you publish this to — see
`PUBLISHING.md`. The marketplace id is `qrs-risk`; the plugin id is `qrs`.)

## What you get

| Skill | Cost | What it does |
|---|---|---|
| **cat-metrics** | Free, local | Catastrophe loss metrics from a YELT/CSV — AAL, OEP/AEP EP curves, return-period losses, VaR/TVaR, EP-curve PNG. |
| **grounded** | Free, local | Per-claim grounding audit — flags every unsourced figure/superlative, scores "X of Y grounded". |
| **montecarlo** | Free local preview + sealed runs | Simulate any uncertain outcome (built-in 2026 World Cup bracket or your own model) with a Monte Carlo CI; in sealed mode, a verifiable `run_id` on the QRS engine. |

The free local skills work immediately for anyone. **Sealed runs** require your own
`QRS_API_TOKEN` (from https://qrsrisk.com) and are honestly gated — until the QRS
engine endpoint + signing are live, `montecarlo` shows a "sealed runs coming online"
state and never fabricates a seal.

## Honesty, by design

Modeled is never shown as validated; seals render **UNSIGNED — pre-release** until
the KMS is live; more sims tighten the estimate, not the outcome. **Don't trust the
number — re-run the seal and check it yourself** at https://qrsrisk.com/trust.

## Contents

```
qrs-marketplace/
├── .claude-plugin/marketplace.json   # this marketplace (id: qrs-risk)
├── qrs/                              # the QRS plugin (source: ./qrs)
└── PUBLISHING.md                     # how to publish + update
```
