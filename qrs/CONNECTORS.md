# Connectors

The QRS plugin bundles **one** connector: the **QRS oracle** (`qrs-oracle`), the
hosted QRS engine's MCP server. It powers `montecarlo`'s **sealed** mode (run a
model on the real engine and get a verifiable `run_id`) and seal **verification**.

The free local skills — `cat-metrics`, `grounded`, and `montecarlo`'s local
preview — do **not** use any connector and work fully offline.

## The `qrs-oracle` connector

| | |
|---|---|
| Server name | `qrs-oracle` |
| Transport | HTTP (streamable) |
| Endpoint | `https://api.qrsrisk.com/mcp` |
| Auth | `Authorization: Bearer ${QRS_API_TOKEN}` |
| Defined in | `.mcp.json` |

This is a **specific hosted service**, not a swappable tool category — there's no
generic substitute, so the plugin names it directly rather than using a
`~~category` placeholder.

### Required token: `QRS_API_TOKEN`

1. Sign in at **https://qrsrisk.com** and generate a personal API token.
2. Set it in your environment:

   ```bash
   export QRS_API_TOKEN="your-token-here"
   ```

3. Restart the app so the connector picks it up.

**Why per-user, never bundled:** the token authenticates *your* account and meters
*your* free sealed-run quota (free tier → 402 → upgrade). A token shipped inside the
plugin would be a leaked shared credential and would break per-user metering, so the
plugin never contains one.

### Expected tools (read-only / sealed)

When the oracle is live, it exposes QRS tools such as:

- a **sample-and-seal** tool (e.g. `qrs_sample_and_seal`) — runs a model on the QRS
  engine and returns the estimate, a Monte Carlo CI, and a sealed `run_id`;
- **`qrs_verify_seal`** — independently verifies a seal.

The oracle only ever returns figures grounded in a real sealed run; it refuses
rather than emit an ungrounded number.

### Honest gating (today)

The general "sample-and-seal any model" engine mode and the metered free quota are
being brought online. Until they're live for your account — or if `QRS_API_TOKEN`
is unset or the endpoint is unreachable — `montecarlo` shows an honest **"sealed
runs coming online — add your QRS token to enable"** state and falls back to the
clearly-labeled local preview. This is expected and is **not** an error. The plugin
never fabricates a `run_id`, a seal, or a verification result.

### Seal status

Until the signing KMS is activated, seals are **"UNSIGNED — pre-release"**: they are
reproducible and verifiable, attesting **reproducibility, not accuracy**, and are
never labeled "Verified" or "signed."
