# Template: `world-cup-2026` — an Elo/Poisson bracket of the 2026 FIFA World Cup

This is a **model template**, not official tournament data and not a validated
forecast. It defines an Elo/Poisson simulation of the 48-team 2026 FIFA World Cup
(hosts: Canada, Mexico, USA). The bundled `scripts/montecarlo.py` runs it as a
**local generic preview** (unsealed, illustrative). The same model can be routed
through the QRS engine in **sealed** mode for a verifiable run — see the skill's
SKILL.md.

> **Branding:** Quantum-Native · Patent QRS-001 · powered by the QRS quantum
> engine. This brands the platform. The World Cup demo makes **no quantum-advantage
> claim** — the win here is scale + speed + a reproducible, verifiable seal, not a
> "better prediction." A coin flip simulated a billion times is still 50/50.

## Contents
- Tournament context (as of the launch window)
- The model (how a match, a group, and the bracket are simulated)
- Illustrative team list & Elo ratings (edit these)
- How to run it
- Honesty notes & known simplifications

## Tournament context (as of late June 2026)

The 2026 World Cup is the first 48-team edition: **12 groups of 4 (A–L)**. The top
two of each group plus the **8 best third-placed teams** (32 total) advance to a
**Round of 32**, then Round of 16 → Quarter-finals → Semi-finals → Final
(~mid-July). As of the launch window the tournament is in its **final group-stage
round**, with the knockout rounds beginning imminently — which is exactly why a
fast, sealed, re-runnable bracket simulation is timely.

Because results are still arriving, treat the ratings and group tables here as a
**starting point you update with live results**. The model simulates the groups
itself; to condition on actual standings, raise/lower ratings or restrict the field
via `--ratings`.

## The model

**Match (Elo → Poisson goals).** Each team has an Elo rating `R`. For a match A vs
B, expected goals are a symmetric log-linear function of the rating gap:

```
diff   = (R_A - R_B) / 400
lambda_A = (TOTAL_GOALS/2) * exp(BETA * diff)
lambda_B = (TOTAL_GOALS/2) * exp(-BETA * diff)
goals_A ~ Poisson(lambda_A),  goals_B ~ Poisson(lambda_B)
```

Defaults: `TOTAL_GOALS = 2.7`, `BETA = 0.9`. These are **illustrative tuning
constants**, not calibrated parameters. Even teams each average ~1.35 goals; the
favourite's expected goals rise as the gap widens.

**Group stage.** Round-robin (6 matches/group), 3 points for a win, 1 for a draw.
Teams are ranked by points, then goal difference, then goals scored, then a random
tie-break.

**Qualification.** Top 2 per group advance (24). The **8 best of the 12
third-placed** teams advance, ranked by points → goal difference → goals scored.

**Knockout.** Single elimination, R32 → Final. A drawn knockout match goes to a
penalty shootout decided by an Elo-weighted coin flip (`p_A = 1/(1+10^(-(R_A-R_B)/400))`).
This is a model tie-break, not a claim about real penalties.

**Confidence interval.** Each reported probability comes with a 95% **Wilson**
interval — chosen over the normal approximation so long-shot odds never dip below
zero. The CI is the **sampling error of the estimate**; it shrinks with more sims
and says nothing about how "certain" the real outcome is.

## Illustrative team list & Elo ratings

**These are seed values for a playable demo — not official ratings and not a
ranking QRS endorses.** Replace them with live ratings (e.g. World Football Elo or
your own) via a JSON file and `--ratings`. The team names are real national sides;
the group assignments below are illustrative, not the official draw.

| Group | Teams (illustrative Elo) |
|------|---------------------------|
| A | Mexico 1830 · South Korea 1790 · Czechia 1760 · South Africa 1660 |
| B | Belgium 1990 · Canada 1800 · Egypt 1700 · Jordan 1560 |
| C | Argentina 2110 · Norway 1860 · Uzbekistan 1640 · Jamaica 1600 |
| D | Colombia 1960 · USA 1840 · Australia 1740 · DR Congo 1690 |
| E | France 2080 · Sweden 1820 · Algeria 1720 · New Zealand 1560 |
| F | Brazil 2060 · Japan 1850 · Austria 1810 · Saudi Arabia 1640 |
| G | Spain 2100 · Uruguay 1950 · Ivory Coast 1730 · Panama 1620 |
| H | England 2030 · Switzerland 1880 · Nigeria 1780 · Costa Rica 1640 |
| I | Portugal 2040 · Denmark 1860 · Iran 1730 · Qatar 1660 |
| J | Netherlands 2010 · Senegal 1870 · Serbia 1820 · Honduras 1590 |
| K | Germany 2020 · Croatia 1930 · Ecuador 1820 · Ghana 1700 |
| L | Morocco 1900 · Poland 1830 · Peru 1760 · Cameroon 1720 |

To override, write `wc_ratings.json`:

```json
{ "Argentina": 2120, "France": 2085, "Spain": 2095, "Brazil": 2055 }
```

Only the teams you list are changed; the rest keep their defaults.

## How to run it

```bash
# Championship odds, 50k sims, top 12
python3 "${CLAUDE_PLUGIN_ROOT}/skills/montecarlo/scripts/montecarlo.py" \
  --model world-cup-2026 --sims 50000 --qoi champion --top 12 --seed 1

# P(reach the final), with live ratings
python3 "${CLAUDE_PLUGIN_ROOT}/skills/montecarlo/scripts/montecarlo.py" \
  --model world-cup-2026 --sims 50000 --qoi finalist --top 16 --ratings wc_ratings.json
```

Valid `--qoi`: `champion`, `finalist`, `semifinalist`, `quarterfinalist`,
`round-of-16`.

## Honesty notes & known simplifications

- **Illustrative, unsealed, not validated.** The local run is a generic NumPy
  preview, not the QRS engine, and produces no seal. Don't present it as a QRS
  engine result or attach a `run_id`.
- **Simplified bracket.** Qualifiers are seeded into a single-elimination bracket
  (best vs worst). This is **not** the official R32 slotting (which pairs specific
  group positions and depends on which third-placed teams qualify). It's a model
  convenience for championship odds, documented as such.
- **Toy parameters.** `TOTAL_GOALS` and `BETA` are not fit to data; treat all
  numbers as illustrative.
- **The honest pitch.** The point of the demo is not "QRS predicts the winner."
  It's: run a transparent model at scale, fast, and — in sealed mode — hand back a
  run anyone can independently re-run and verify. *Don't trust the bracket; check
  the seal.*
