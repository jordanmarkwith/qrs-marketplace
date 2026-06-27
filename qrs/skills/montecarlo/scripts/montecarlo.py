#!/usr/bin/env python3
"""
montecarlo.py  --  GENERIC local Monte Carlo preview.

==============================================================================
  THIS IS NOT THE QRS QUANTUM-NATIVE ENGINE.
  This is a plain, open-source NumPy Monte Carlo simulator that runs entirely
  on your machine. Its output is UNSEALED and ILLUSTRATIVE. It produces NO
  verifiable QRS seal and is NOT a QRS engine run.

  For a sealed, independently verifiable run on the QRS quantum-native engine
  (the patented QRS-001 sampling core stays server-side and never ships here),
  use SEALED mode via the QRS MCP oracle. See the skill's SKILL.md.
==============================================================================

What it does
------------
Estimates a "quantity of interest" for an uncertain process by simulating it
many times and reporting the estimate WITH a 95% Monte Carlo confidence
interval (CI). The CI describes sampling error in the *estimate* only:

    More simulations tighten the estimate. They do NOT make an uncertain
    outcome more certain. A 100-million-path run of a coin flip still says
    "about 50%."

Built-in models
---------------
  world-cup-2026   Elo/Poisson bracket of the 2026 FIFA World Cup
                   (illustrative ratings/groups -- edit them; see
                   ../references/world-cup-2026.md)
  dice             Sum of N dice with S sides
  coin             Number of heads in N fair (or biased) flips

Usage
-----
  python montecarlo.py --model world-cup-2026 --sims 50000 --qoi champion
  python montecarlo.py --model world-cup-2026 --sims 50000 --qoi finalist --top 16
  python montecarlo.py --model dice --dice 2 --sides 6 --sims 200000
  python montecarlo.py --model coin --flips 10 --p-heads 0.5 --sims 200000
  python montecarlo.py --model world-cup-2026 --ratings my_ratings.json --sims 50000

Reproducibility note: this preview is itself reproducible via --seed (same seed
=> same numbers). That is ordinary RNG seeding, NOT a QRS cryptographic seal.
Dependencies: numpy.
"""

import argparse
import json
import os
import sys
import textwrap

import numpy as np

Z95 = 1.959963984540054  # 97.5th percentile of the standard normal

BRAND = "Quantum-Native · Patent QRS-001 · powered by the QRS quantum engine"

LOCAL_LABEL = (
    "LOCAL GENERIC MONTE CARLO PREVIEW — NOT the QRS quantum-native engine. "
    "Unsealed · illustrative · no verifiable seal."
)

# QRS data-viz palette (see ../../../assets/BRAND.md) — navy + teal, never rainbow
C_INK = "#1B3B3A"
C_NAVY = "#324A6D"
C_TEAL_ACCENT = "#5BBAB5"
C_CREAM = "#F4F6F6"
C_MUTED = "#69727d"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                         "assets", "qrs-logo.png")


# --------------------------------------------------------------------------- #
#  Confidence intervals (honest reporting of sampling error)
# --------------------------------------------------------------------------- #
def wilson_ci(k, n, z=Z95):
    """95% Wilson score interval for a probability estimate k/n.

    Wilson is used instead of the plain normal approximation because it stays
    valid for small probabilities (e.g. a long-shot team's title odds), where
    the naive p +/- 1.96*sqrt(p(1-p)/n) can run below zero.
    """
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = (z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return p, max(0.0, center - margin), min(1.0, center + margin)


def mean_ci(samples, z=Z95):
    """95% CI for the mean of a continuous quantity of interest."""
    samples = np.asarray(samples, dtype=float)
    n = samples.size
    mean = float(samples.mean())
    if n < 2:
        return mean, mean, mean
    se = float(samples.std(ddof=1)) / np.sqrt(n)
    return mean, mean - z * se, mean + z * se


# --------------------------------------------------------------------------- #
#  Match model shared by the football bracket (Elo -> Poisson goals)
# --------------------------------------------------------------------------- #
def elo_expected_score(r_a, r_b):
    """Classic Elo expected score for A vs B (used for penalty shootouts)."""
    return 1.0 / (1.0 + 10.0 ** (-(r_a - r_b) / 400.0))


def poisson_goal_lambdas(r_a, r_b, total_goals=2.7, beta=0.9):
    """Map an Elo gap to expected-goals (lambda) for each side.

    A symmetric log-linear map: even teams each average total_goals/2; the
    favourite's expected goals rise and the underdog's fall as the gap widens.
    `beta` controls sensitivity. These are illustrative tuning constants, not
    calibrated parameters -- this is a preview model.
    """
    base = total_goals / 2.0
    diff = (r_a - r_b) / 400.0
    lam_a = base * np.exp(beta * diff)
    lam_b = base * np.exp(-beta * diff)
    return lam_a, lam_b


def play_matches(idx_a, idx_b, ratings, rng, knockout, total_goals, beta):
    """Vectorised match outcome across all simulations.

    idx_a, idx_b : int arrays [N] of team indices meeting in this match
    Returns the array [N] of winning team indices. In group play a draw is
    encoded as winner = -1 (caller handles points); in knockout a draw goes to
    a penalty shootout decided by Elo-weighted coin flip (no fake certainty --
    just the model's tie-break).
    """
    r_a = ratings[idx_a]
    r_b = ratings[idx_b]
    lam_a, lam_b = poisson_goal_lambdas(r_a, r_b, total_goals, beta)
    g_a = rng.poisson(lam_a)
    g_b = rng.poisson(lam_b)
    if knockout:
        pen_a = elo_expected_score(r_a, r_b)
        a_wins = (g_a > g_b) | ((g_a == g_b) & (rng.random(g_a.shape) < pen_a))
        return np.where(a_wins, idx_a, idx_b), g_a, g_b
    winner = np.full(idx_a.shape, -1, dtype=np.int64)  # -1 = draw
    winner = np.where(g_a > g_b, idx_a, winner)
    winner = np.where(g_b > g_a, idx_b, winner)
    return winner, g_a, g_b


def rank_key(points, gd, gf, rng):
    """Composite descending sort key for league tables, with random tie-break.

    Encodes (points, goal difference, goals for) into one float so we can
    argsort each simulation's table independently. Offsets keep goal
    difference non-negative inside its field.
    """
    jitter = rng.random(points.shape)
    return points * 1e9 + (gd + 1000.0) * 1e4 + gf * 10.0 + jitter


# --------------------------------------------------------------------------- #
#  Built-in model: 2026 FIFA World Cup bracket
# --------------------------------------------------------------------------- #
def default_world_cup():
    """ILLUSTRATIVE field, groups, and Elo ratings -- NOT official data.

    48 teams in 12 groups (A-L). Ratings are rough seed values for a playable
    demo; replace them with live ratings/results via --ratings (see
    ../references/world-cup-2026.md). The team list is real national teams but
    the group assignments and numbers are illustrative.
    """
    groups = {
        "A": [["Mexico", 1830], ["South Korea", 1790], ["Czechia", 1760], ["South Africa", 1660]],
        "B": [["Canada", 1800], ["Belgium", 1990], ["Egypt", 1700], ["Jordan", 1560]],
        "C": [["Argentina", 2110], ["Norway", 1860], ["Uzbekistan", 1640], ["Jamaica", 1600]],
        "D": [["USA", 1840], ["Colombia", 1960], ["Australia", 1740], ["DR Congo", 1690]],
        "E": [["France", 2080], ["Sweden", 1820], ["Algeria", 1720], ["New Zealand", 1560]],
        "F": [["Brazil", 2060], ["Japan", 1850], ["Austria", 1810], ["Saudi Arabia", 1640]],
        "G": [["Spain", 2100], ["Uruguay", 1950], ["Ivory Coast", 1730], ["Panama", 1620]],
        "H": [["England", 2030], ["Switzerland", 1880], ["Nigeria", 1780], ["Costa Rica", 1640]],
        "I": [["Portugal", 2040], ["Denmark", 1860], ["Iran", 1730], ["Qatar", 1660]],
        "J": [["Netherlands", 2010], ["Senegal", 1870], ["Serbia", 1820], ["Honduras", 1590]],
        "K": [["Germany", 2020], ["Croatia", 1930], ["Ecuador", 1820], ["Ghana", 1700]],
        "L": [["Morocco", 1900], ["Peru", 1760], ["Poland", 1830], ["Cameroon", 1720]],
    }
    return groups


def load_ratings_override(path, groups):
    """Merge a user JSON {"Team": rating, ...} over the default ratings."""
    with open(path) as fh:
        overrides = json.load(fh)
    for g in groups.values():
        for pair in g:
            if pair[0] in overrides:
                pair[1] = float(overrides[pair[0]])
    return groups


def simulate_world_cup(n_sims, qoi, rng, total_goals=2.7, beta=0.9, ratings_path=None):
    groups = default_world_cup()
    if ratings_path:
        groups = load_ratings_override(ratings_path, groups)

    team_names = []
    for g in sorted(groups):
        for name, _r in groups[g]:
            team_names.append(name)
    name_to_idx = {n: i for i, n in enumerate(team_names)}
    ratings = np.array([r for g in sorted(groups) for _n, r in groups[g]], dtype=float)
    n_teams = len(team_names)

    N = n_sims
    points = np.zeros((N, n_teams))
    gd = np.zeros((N, n_teams))
    gf = np.zeros((N, n_teams))

    # ---- Group stage: round-robin in every group -------------------------- #
    group_team_idx = {}
    for g in sorted(groups):
        idxs = [name_to_idx[name] for name, _r in groups[g]]
        group_team_idx[g] = idxs
        for a in range(4):
            for b in range(a + 1, 4):
                ia = np.full(N, idxs[a], dtype=np.int64)
                ib = np.full(N, idxs[b], dtype=np.int64)
                winner, ga, gb = play_matches(ia, ib, ratings, rng, False, total_goals, beta)
                points[:, idxs[a]] += np.where(winner == idxs[a], 3, np.where(winner == -1, 1, 0))
                points[:, idxs[b]] += np.where(winner == idxs[b], 3, np.where(winner == -1, 1, 0))
                gf[:, idxs[a]] += ga
                gf[:, idxs[b]] += gb
                gd[:, idxs[a]] += ga - gb
                gd[:, idxs[b]] += gb - ga

    # ---- Rank each group, collect winners / runners-up / thirds ----------- #
    winners = np.zeros((N, 12), dtype=np.int64)
    runners = np.zeros((N, 12), dtype=np.int64)
    thirds = np.zeros((N, 12), dtype=np.int64)
    thirds_pts = np.zeros((N, 12))
    thirds_gd = np.zeros((N, 12))
    thirds_gf = np.zeros((N, 12))

    for gi, g in enumerate(sorted(groups)):
        idxs = np.array(group_team_idx[g])
        key = rank_key(points[:, idxs], gd[:, idxs], gf[:, idxs], rng)
        order = np.argsort(-key, axis=1)            # descending
        ranked = idxs[order]                         # team indices, best first
        winners[:, gi] = ranked[:, 0]
        runners[:, gi] = ranked[:, 1]
        third = ranked[:, 2]
        thirds[:, gi] = third
        rows = np.arange(N)
        thirds_pts[:, gi] = points[rows, third]
        thirds_gd[:, gi] = gd[rows, third]
        thirds_gf[:, gi] = gf[rows, third]

    # ---- Best 8 of 12 third-placed teams advance -------------------------- #
    tkey = rank_key(thirds_pts, thirds_gd, thirds_gf, rng)
    torder = np.argsort(-tkey, axis=1)
    best_thirds = np.take_along_axis(thirds, torder[:, :8], axis=1)   # [N, 8]

    # ---- Seed 32 qualifiers: winners, then runners-up, then best thirds --- #
    # Simplified illustrative single-elimination seeding (1 vs 32, 2 vs 31...).
    # This is NOT the official R32 slotting; it is a model convenience and is
    # documented as such. For the official bracket + a sealed run, use the
    # QRS engine.
    bracket = np.concatenate([winners, runners, best_thirds], axis=1)  # [N, 32]

    # ---- Knockout rounds -------------------------------------------------- #
    round_names = ["Round of 32", "Round of 16", "Quarter-final",
                   "Semi-final", "Final"]
    reached = {name: np.zeros(n_teams) for name in
               ["round-of-16", "quarter-final", "semi-final", "final", "champion"]}

    current = bracket
    # teams entering each stage:
    stage_entry_flags = {
        "round-of-16": None, "quarter-final": None, "semi-final": None,
        "final": None,
    }
    for rnd in range(5):
        n_pairs = current.shape[1] // 2
        # seed s vs seed (last - s)
        left = current[:, :n_pairs]
        right = current[:, ::-1][:, :n_pairs]
        winner, _ga, _gb = play_matches(left.reshape(-1), right.reshape(-1),
                                        ratings, rng, True, total_goals, beta)
        winner = winner.reshape(current.shape[0], n_pairs)
        # record who *advanced out of* this round (i.e. reached the next stage)
        next_stage = ["round-of-16", "quarter-final", "semi-final",
                      "final", "champion"][rnd]
        for s in range(n_teams):
            reached[next_stage][s] += np.sum(winner == s)
        current = winner

    # ---- Quantity of interest -------------------------------------------- #
    qoi_map = {
        "champion": "champion",
        "finalist": "final",
        "semifinalist": "semi-final",
        "quarterfinalist": "quarter-final",
        "round-of-16": "round-of-16",
    }
    if qoi not in qoi_map:
        raise SystemExit("world-cup-2026 --qoi must be one of: " + ", ".join(qoi_map))
    counts = reached[qoi_map[qoi]]

    results = []
    for i, name in enumerate(team_names):
        p, lo, hi = wilson_ci(counts[i], N)
        results.append((name, p, lo, hi, int(counts[i])))
    results.sort(key=lambda r: -r[1])
    return {
        "model": "world-cup-2026",
        "qoi": qoi,
        "n_sims": N,
        "results": results,
        "kind": "probability",
        "note": ("Illustrative Elo/Poisson model; ratings and groups are seed "
                 "values, not official data. Simplified single-elimination "
                 "bracket (not the official R32 slotting)."),
    }


# --------------------------------------------------------------------------- #
#  Built-in models: dice and coin (simple generic demos)
# --------------------------------------------------------------------------- #
def simulate_dice(n_sims, dice, sides, rng):
    rolls = rng.integers(1, sides + 1, size=(n_sims, dice))
    totals = rolls.sum(axis=1)
    mean, lo, hi = mean_ci(totals)
    vals, cnts = np.unique(totals, return_counts=True)
    dist = []
    for v, c in zip(vals, cnts):
        p, plo, phi = wilson_ci(c, n_sims)
        dist.append((int(v), p, plo, phi, int(c)))
    return {
        "model": f"dice ({dice}d{sides}, sum)",
        "qoi": "sum",
        "n_sims": n_sims,
        "mean": mean, "mean_lo": lo, "mean_hi": hi,
        "results": dist, "kind": "distribution",
        "note": "Closed-form mean is exact; the CI shows this run's sampling error.",
    }


def simulate_coin(n_sims, flips, p_heads, rng):
    heads = rng.binomial(flips, p_heads, size=n_sims)
    mean, lo, hi = mean_ci(heads)
    vals, cnts = np.unique(heads, return_counts=True)
    dist = []
    for v, c in zip(vals, cnts):
        p, plo, phi = wilson_ci(c, n_sims)
        dist.append((int(v), p, plo, phi, int(c)))
    return {
        "model": f"coin ({flips} flips, p(heads)={p_heads})",
        "qoi": "heads",
        "n_sims": n_sims,
        "mean": mean, "mean_lo": lo, "mean_hi": hi,
        "results": dist, "kind": "distribution",
        "note": "More flips per trial change the distribution; more trials only sharpen the estimate.",
    }


# --------------------------------------------------------------------------- #
#  Reporting
# --------------------------------------------------------------------------- #
def banner():
    bar = "=" * 78
    print(bar)
    print("  " + LOCAL_LABEL)
    print("  " + BRAND)
    print("  (Brand identifies the QRS platform/engine. This local preview did")
    print("   NOT run on it and carries no seal. See SKILL.md > SEALED mode.)")
    print(bar)


def pct(x):
    return f"{100 * x:6.2f}%"


def report(res, top):
    banner()
    print(f"\nModel:            {res['model']}")
    print(f"Quantity:         {res['qoi']}")
    print(f"Simulations (N):  {res['n_sims']:,}")
    if "mean" in res:
        print(f"Mean estimate:    {res['mean']:.4f}  "
              f"(95% CI {res['mean_lo']:.4f} – {res['mean_hi']:.4f})")
    print(f"\nNote: {res['note']}")
    print("\nEstimate with 95% Monte Carlo confidence interval")
    print("(the CI is sampling error in THIS estimate -- it is not a claim that")
    print(" the outcome itself is more or less certain):\n")

    rows = res["results"]
    if res["kind"] == "probability":
        rows = rows[:top]
        print(f"  {'Outcome':<16}{'Estimate':>10}   {'95% CI':>20}")
        print("  " + "-" * 50)
        for name, p, lo, hi, _c in rows:
            print(f"  {name:<16}{pct(p):>10}   [{pct(lo)}, {pct(hi)}]")
    else:
        print(f"  {'Value':>6}{'Estimate':>12}   {'95% CI':>22}")
        print("  " + "-" * 48)
        for v, p, lo, hi, _c in rows:
            print(f"  {v:>6}{pct(p):>12}   [{pct(lo)}, {pct(hi)}]")

    print("\n" + "-" * 78)
    print("More simulations TIGHTEN these intervals; they do not make any single")
    print("outcome more certain. This is an UNSEALED local estimate.")
    print("To get a sealed, verifiable QRS-engine run (and a run_id you or anyone")
    print("can re-run and check), use SEALED mode -- see the skill's SKILL.md.")
    print("-" * 78)


def plot_results(res, top, out_path):
    """Brand-styled chart of the estimate + 95% CI (a shareable launch asset).

    Hard-labeled as a local, unsealed preview. matplotlib is imported lazily so
    the simulation itself needs only numpy.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox

    rows = res["results"][:top][::-1]   # bottom-up for a horizontal bar chart
    labels = [str(r[0]) for r in rows]
    ps = [r[1] * 100 for r in rows]
    err_lo = [(r[1] - r[2]) * 100 for r in rows]
    err_hi = [(r[3] - r[1]) * 100 for r in rows]
    y = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(8.5, max(3.0, 0.45 * len(rows) + 1.6)),
                           facecolor=C_CREAM)
    ax.set_facecolor("#FFFFFF")
    ax.barh(y, ps, color=C_TEAL_ACCENT, edgecolor=C_INK, linewidth=0.6, zorder=3)
    ax.errorbar(ps, y, xerr=[err_lo, err_hi], fmt="none", ecolor=C_NAVY,
                capsize=3, lw=1.3, zorder=4)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, color=C_INK)
    ax.set_xlabel("Probability (%) with 95% Monte Carlo CI", color=C_INK)
    ax.set_title(f"{res['model']} — P({res['qoi']})", color=C_INK,
                 fontsize=14, fontweight="semibold")
    ax.tick_params(colors=C_MUTED)
    for spine in ax.spines.values():
        spine.set_color("#d6dede")
    ax.grid(True, axis="x", ls=":", alpha=0.4, color="#9bb3b1")
    try:
        img = mpimg.imread(LOGO_PATH)
        ax.add_artist(AnnotationBbox(OffsetImage(img, zoom=0.10), (0.99, 0.06),
                      xycoords="axes fraction", frameon=False,
                      box_alignment=(1, 0)))
    except Exception:
        pass
    cap = (f"N = {res['n_sims']:,} sims · {LOCAL_LABEL}\n{BRAND} — "
           "more sims tighten the estimate, not the outcome.")
    fig.text(0.5, -0.04, cap, ha="center", va="top", fontsize=7, color=C_MUTED)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor=C_CREAM)
    plt.close(fig)
    print(f"\nSaved chart (local preview, unsealed): {out_path}")


def main():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(__doc__))
    ap.add_argument("--model", required=True,
                    choices=["world-cup-2026", "dice", "coin"])
    ap.add_argument("--sims", type=int, default=50000, help="number of simulations (N)")
    ap.add_argument("--seed", type=int, default=None,
                    help="RNG seed for a reproducible preview (NOT a QRS seal)")
    ap.add_argument("--qoi", default="champion", help="quantity of interest")
    ap.add_argument("--top", type=int, default=12, help="rows to show for ranked outcomes")
    ap.add_argument("--ratings", default=None,
                    help="JSON {team: rating} to override world-cup ratings")
    ap.add_argument("--dice", type=int, default=2)
    ap.add_argument("--sides", type=int, default=6)
    ap.add_argument("--flips", type=int, default=10)
    ap.add_argument("--p-heads", type=float, default=0.5)
    ap.add_argument("--plot", default=None,
                    help="save a brand-styled estimate+CI chart to this PNG path")
    args = ap.parse_args()

    if args.sims < 1:
        raise SystemExit("--sims must be >= 1")
    rng = np.random.default_rng(args.seed)

    if args.model == "world-cup-2026":
        res = simulate_world_cup(args.sims, args.qoi, rng, ratings_path=args.ratings)
    elif args.model == "dice":
        res = simulate_dice(args.sims, args.dice, args.sides, rng)
    else:
        res = simulate_coin(args.sims, args.flips, args.p_heads, rng)

    report(res, args.top)

    if args.plot:
        plot_results(res, args.top, args.plot)


if __name__ == "__main__":
    main()
