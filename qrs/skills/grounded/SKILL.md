---
name: grounded
description: >-
  Audit a document, AI output, slide, or marketing copy so that every figure is
  tied to a source. Use this skill whenever the user wants to fact-source-check,
  ground, or pressure-test claims before publishing: "is this deck overclaiming?",
  "check every number has a source", "flag unsourced stats", "find the claims that
  need a citation", "ground this draft", "where are we overclaiming?", or before
  sending investor/marketing/regulatory material. It extracts every figure
  (%, $, counts, dates) and superlative (largest/first/only/#1), classifies each as
  sourced / unsourced / illustrative / internally-derived, flags the unsourced,
  suggests labels, and scores "X of Y figures grounded". Free and local.
  Quantum-Native · Patent QRS-001 · powered by the QRS quantum engine (brand).
version: 0.1.0
---

# grounded — every number tied to a source, or flagged

**Quantum-Native · Patent QRS-001 · powered by the QRS quantum engine.** This
skill is the grounding discipline turned into a tool: it makes overclaiming visible
*before* it ships. It is free and local.

## The one thing it does — and the one thing it does NOT do

- It flags **missing grounding**: figures and bold claims that lack a source or a
  truthful label.
- It does **not verify that a sourced number is correct.** A figure with a citation
  is classified "sourced" even if the citation turns out to be wrong — checking
  accuracy is a different, deeper job. Say this plainly so no one mistakes a
  passing audit for a fact-check. (This honesty about your own limits is the whole
  brand.)

## Workflow

1. **Get the text.** Read the document/draft the user gives you (file or pasted).
2. **Extract every claim.** Optionally run the bundled helper to maximize recall —
   it lists candidate figures and superlatives with the sentence each sits in:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/grounded/scripts/extract_figures.py" --file draft.md
   ```

   The script finds candidates; you do the judgment. Add anything it missed
   (qualitative superlatives, implied comparisons).
3. **Classify each claim** into exactly one bucket (definitions below).
4. **Produce the audit table, the score, and the flags.**
5. **Offer a labeled rewrite** if the user wants one.

## Classification buckets

| Bucket | Means | Suggested action |
|---|---|---|
| **sourced** | A citation, link, footnote, or named source is attached or clearly referenced. | Keep. (Note: not verified for correctness.) |
| **unsourced** | A specific factual figure/superlative with no source. **The thing to flag.** | Add a source, or label `[source needed]`, or cut. |
| **illustrative** | A hypothetical/example value, not asserted as real ("e.g., a $10M book"). | Label **illustrative** so it can't be read as actual. |
| **internally-derived** | Computed from the author's own model/data, not an external source ("our model estimates…"). | Label **"modeled — not validated"** (or "modeled — independently validated" only if it truly is). |

When unsure between *sourced* and *unsourced*, treat "a source is alluded to but
not actually given" as **unsourced** — the reader can't follow it.

## Output format

Always produce these four parts:

**1. Audit table**

```
#  | Claim                          | Type        | Classification      | Action
1  | "$37.3M FLCOMM loss"           | currency    | internally-derived  | label "modeled — not validated"
2  | "largest quantum risk engine"  | superlative | unsourced           | [source needed] or cut
3  | "37% of insurers (2025 survey)"| percentage  | sourced             | keep (source present; not accuracy-checked)
4  | "a $10M illustrative portfolio"| currency    | illustrative        | label "illustrative"
```

**2. Grounding score** — `X of Y figures grounded`, where "grounded" = sourced **or**
correctly labeled (illustrative / modeled). Unsourced claims are NOT grounded.
Report it as e.g. **"6 of 9 figures grounded (3 need attention)."**

**3. Flags** — list the unsourced claims explicitly, each with the exact sentence
and the fix. These are the action items.

**4. Optional labeled rewrite** — if asked, return the text with inline labels
inserted (`[source needed]`, *(illustrative)*, *(modeled — not validated)*) so the
draft is publish-safe without inventing any sources. **Never invent a citation to
make a claim look grounded** — that's the opposite of the point.

## Tone and judgment

- Be precise, not pedantic. Round-number framing ("about half") needs less
  policing than a hard stat ("48.2%"). Focus energy on specific, checkable,
  load-bearing claims.
- Superlatives ("first", "only", "largest", "world-leading") are high-risk because
  they're rarely sourced and easily falsified — scrutinize them.
- Words like **"validated", "certified", "guaranteed", "proven"** deserve special
  flags: they imply external attestation. If the doc can't point to who validated
  it, that's an unsourced claim.

## Honesty rails

- Flag missing grounding; don't claim to have verified correctness.
- Don't fabricate sources, and don't soften a real overclaim to be polite — quiet
  flagging now beats a public correction later.
- The quantum branding is the platform's; this audit makes no quantum claim.
