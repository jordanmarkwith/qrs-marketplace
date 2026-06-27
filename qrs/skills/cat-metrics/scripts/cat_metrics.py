#!/usr/bin/env python3
"""
cat_metrics.py  --  catastrophe loss metrics from a simulated YELT/year table.

Quantum-Native · Patent QRS-001 · powered by the QRS quantum engine.
(Brand identifies the QRS platform. This script is a FREE, LOCAL, open-source
calculator: it computes metrics directly FROM YOUR TABLE on your machine. It does
not call the QRS engine, does not model hazard, and adds no uncertainty of its own.)

What it computes
----------------
  AAL            Average Annual Loss = total loss / N (N = number of SIMULATED
                 YEARS, including zero-loss years).
  OEP curve      Occurrence Exceedance Probability: rank the per-year MAXIMUM
                 single-event loss.
  AEP curve      Aggregate Exceedance Probability: rank the per-year SUM of
                 losses.
  Return-period  Loss at 1-in-10/25/50/100/250/500/1000 (interpolated off the
   losses        curve), for OEP and AEP.
  VaR / TVaR     Value-at-Risk (a percentile of annual aggregate loss) and
                 Tail VaR (mean loss beyond VaR).
  EP-curve PNG   OEP & AEP plotted vs return period.
  Summary table  Printed, and saved as CSV.

THE #1 HAND-ROLLED BUG, AVOIDED
-------------------------------
Exceedance stats must be computed over ALL N simulated years, INCLUDING the
zero-loss years that usually aren't rows in the file. If you divide by the number
of *loss* rows instead of N, every metric is biased high. This script requires you
to pass N (--years) and explicitly folds in the (N - distinct-loss-years)
zero-loss years. It will not guess N.

EP convention
-------------
Exceedance probability uses the Weibull plotting position  EP = rank / (N + 1);
return period  RP = 1 / EP. The largest return period this script will estimate is
about N (you cannot read a 1-in-1000 loss off 100 simulated years); higher targets
are flagged, not fabricated.

Usage
-----
  python cat_metrics.py --csv losses.csv --years 10000
  python cat_metrics.py --csv losses.csv --years 10000 \
      --year-col Year --event-col EventID --loss-col GroundUpLoss \
      --percentiles 90 95 99 99.5 --out-dir ./out

Dependencies: numpy, pandas, matplotlib.
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

BRAND = "Quantum-Native · Patent QRS-001 · powered by the QRS quantum engine"
DEFAULT_RPS = [10, 25, 50, 100, 250, 500, 1000]

# QRS data-viz palette (see ../../../assets/BRAND.md) — navy + teal pair, never rainbow
C_INK = "#1B3B3A"      # primary dark teal — titles
C_NAVY = "#324A6D"     # primary data-viz line (AEP)
C_TEAL = "#29908A"     # secondary line (OEP)
C_TEAL_ACCENT = "#5BBAB5"  # highlight markers
C_CREAM = "#F4F6F6"    # figure background
C_MUTED = "#69727d"    # captions
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                         "assets", "qrs-logo.png")


def _stamp_logo(ax):
    """Stamp the QRS logo in the chart's top-left, if the asset is present."""
    try:
        img = mpimg.imread(LOGO_PATH)
        oi = OffsetImage(img, zoom=0.10)
        ab = AnnotationBbox(oi, (0.985, 0.05), xycoords="axes fraction",
                            frameon=False, box_alignment=(1, 0))
        ax.add_artist(ab)
    except Exception:
        pass  # asset optional; chart works without it


# --------------------------------------------------------------------------- #
#  Column detection
# --------------------------------------------------------------------------- #
def pick_column(df, explicit, candidates, required, what):
    if explicit:
        if explicit not in df.columns:
            raise SystemExit(f"Column '{explicit}' for {what} not found. "
                             f"Available: {list(df.columns)}")
        return explicit
    lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower:
            return lower[cand]
    if required:
        raise SystemExit(
            f"Could not auto-detect the {what} column. Use the explicit flag. "
            f"Available columns: {list(df.columns)}")
    return None


# --------------------------------------------------------------------------- #
#  Core: build the per-year loss vectors over ALL N years
# --------------------------------------------------------------------------- #
def build_annual_vectors(df, year_col, event_col, loss_col, n_years):
    losses = pd.to_numeric(df[loss_col], errors="coerce")
    if losses.isna().any():
        bad = int(losses.isna().sum())
        print(f"  ! {bad} loss value(s) were non-numeric and dropped.")
    work = pd.DataFrame({"year": df[year_col], "loss": losses}).dropna()
    work = work[work["loss"] >= 0]

    grouped = work.groupby("year")["loss"]
    per_year_sum = grouped.sum()          # AEP basis
    per_year_max = grouped.max()          # OEP basis
    distinct_loss_years = per_year_sum.shape[0]

    if distinct_loss_years > n_years:
        raise SystemExit(
            f"Found {distinct_loss_years} distinct loss-years but --years={n_years}. "
            f"N must be >= the number of distinct years in the file.")

    n_zero = n_years - distinct_loss_years
    # Pad with zero-loss years -- THE crucial step.
    agg = np.concatenate([per_year_sum.values, np.zeros(n_zero)])
    occ = np.concatenate([per_year_max.values, np.zeros(n_zero)])
    return agg, occ, distinct_loss_years, n_zero


# --------------------------------------------------------------------------- #
#  EP curve + return-period interpolation
# --------------------------------------------------------------------------- #
def ep_curve(values, n_years):
    """Return (rp_sorted_ascending, ep_ascending, loss) for plotting/interp.

    losses sorted descending -> rank 1..N -> EP = rank/(N+1) -> RP = 1/EP.
    """
    losses_desc = np.sort(values)[::-1]
    ranks = np.arange(1, n_years + 1)
    ep = ranks / (n_years + 1.0)          # ascending with rank
    rp = 1.0 / ep
    return losses_desc, ep, rp


def loss_at_return_period(values, n_years, target_rp):
    losses_desc, ep, _rp = ep_curve(values, n_years)
    target_ep = 1.0 / target_rp
    smallest_ep = ep[0]                   # = 1/(N+1), the rarest estimable point
    if target_ep < smallest_ep:
        return np.nan                     # beyond data support -> don't fabricate
    # ep ascending; losses_desc aligned (largest loss at smallest ep)
    return float(np.interp(target_ep, ep, losses_desc))


def var_tvar(annual_agg, percentiles):
    out = {}
    for p in percentiles:
        var = float(np.percentile(annual_agg, p, method="linear"))
        tail = annual_agg[annual_agg >= var]
        tvar = float(tail.mean()) if tail.size else var
        out[p] = (var, tvar)
    return out


# --------------------------------------------------------------------------- #
#  Plot
# --------------------------------------------------------------------------- #
def plot_ep(occ, agg, n_years, rps, out_path):
    o_loss, o_ep, o_rp = ep_curve(occ, n_years)
    a_loss, a_ep, a_rp = ep_curve(agg, n_years)
    fig, ax = plt.subplots(figsize=(9, 5.5), facecolor=C_CREAM)
    ax.set_facecolor("#FFFFFF")
    ax.plot(a_rp, a_loss, label="AEP (aggregate / year)", color=C_NAVY, lw=2.2)
    ax.plot(o_rp, o_loss, label="OEP (max occurrence / year)", color=C_TEAL,
            lw=2.2, ls="--")
    for rp in rps:
        if rp <= n_years:
            la = loss_at_return_period(agg, n_years, rp)
            if not np.isnan(la):
                ax.scatter([rp], [la], color=C_TEAL_ACCENT, edgecolor=C_NAVY,
                           zorder=5, s=34, linewidth=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("Return period (years, log scale)", color=C_INK)
    ax.set_ylabel("Loss", color=C_INK)
    ax.set_title("Exceedance Probability curves", color=C_INK,
                 fontsize=14, fontweight="semibold")
    ax.tick_params(colors=C_MUTED)
    for spine in ax.spines.values():
        spine.set_color("#d6dede")
    ax.grid(True, which="both", ls=":", alpha=0.4, color="#9bb3b1")
    ax.legend(facecolor="#FFFFFF", edgecolor="#d6dede", labelcolor=C_INK)
    _stamp_logo(ax)
    cap = (f"N = {n_years:,} simulated years (zero-loss years included). "
           f"EP = rank/(N+1).  {BRAND}\n"
           "Computed directly from the loss table — illustrative of the input, "
           "not a validated forecast.")
    fig.text(0.5, -0.02, cap, ha="center", va="top", fontsize=7, color=C_MUTED)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor=C_CREAM)
    plt.close(fig)


# --------------------------------------------------------------------------- #
#  Reporting
# --------------------------------------------------------------------------- #
def money(x):
    if np.isnan(x):
        return "  n/a (N too small)"
    return f"{x:,.0f}"


def main():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
    ap.add_argument("--csv", required=True, help="path to the loss CSV")
    ap.add_argument("--years", type=int, required=True,
                    help="N = number of SIMULATED YEARS (must include zero-loss years)")
    ap.add_argument("--year-col", default=None)
    ap.add_argument("--event-col", default=None)
    ap.add_argument("--loss-col", default=None)
    ap.add_argument("--percentiles", type=float, nargs="+",
                    default=[90, 95, 99, 99.5])
    ap.add_argument("--return-periods", type=int, nargs="+", default=DEFAULT_RPS)
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    if args.years < 1:
        raise SystemExit("--years must be >= 1")
    df = pd.read_csv(args.csv)
    os.makedirs(args.out_dir, exist_ok=True)

    year_col = pick_column(df, args.year_col, ["year", "yr", "sim_year", "trial"],
                           True, "year")
    loss_col = pick_column(df, args.loss_col,
                           ["loss", "grounduploss", "grossloss", "amount", "value"],
                           True, "loss")
    event_col = pick_column(df, args.event_col, ["event", "eventid", "event_id",
                            "peril", "occurrence"], False, "event")

    agg, occ, n_loss_years, n_zero = build_annual_vectors(
        df, year_col, event_col, loss_col, args.years)

    total_loss = float(agg.sum())
    aal = total_loss / args.years

    rps = sorted(args.return_periods)
    oep_rp = {rp: loss_at_return_period(occ, args.years, rp) for rp in rps}
    aep_rp = {rp: loss_at_return_period(agg, args.years, rp) for rp in rps}
    vt = var_tvar(agg, args.percentiles)

    png_path = os.path.join(args.out_dir, "ep_curve.png")
    plot_ep(occ, agg, args.years, rps, png_path)

    # ---- print summary ---- #
    bar = "=" * 76
    print(bar)
    print("  CATASTROPHE LOSS METRICS")
    print("  " + BRAND)
    print("  Computed locally and directly from your table (no hazard modelling,")
    print("  no QRS engine call, no added uncertainty).")
    print(bar)
    print(f"  Source file        : {args.csv}")
    print(f"  Year column        : {year_col}")
    print(f"  Loss column        : {loss_col}")
    print(f"  Event column       : {event_col if event_col else '(none — one loss per row)'}")
    print(f"  Simulated years N  : {args.years:,}")
    print(f"  Years with loss    : {n_loss_years:,}")
    print(f"  Zero-loss years    : {n_zero:,}   <-- INCLUDED in N (must be)")
    print(f"  Convention         : EP = rank/(N+1); RP = 1/EP")
    print("-" * 76)
    print(f"  AAL (Average Annual Loss) : {money(aal)}")
    print(f"  Total modelled loss       : {money(total_loss)}")
    print("-" * 76)
    print(f"  {'Return period':<16}{'OEP loss':>20}{'AEP loss':>20}")
    print(f"  {'(years)':<16}{'(per-occurrence)':>20}{'(annual aggregate)':>20}")
    for rp in rps:
        flag = "" if rp <= args.years else "  *"
        print(f"  1-in-{rp:<11}{money(oep_rp[rp]):>20}{money(aep_rp[rp]):>20}{flag}")
    if any(rp > args.years for rp in rps):
        print(f"  * return period exceeds N={args.years:,}; not estimable from this many "
              "years (not fabricated).")
    print("-" * 76)
    print(f"  {'Percentile':<14}{'VaR (annual agg)':>22}{'TVaR (mean beyond)':>22}")
    for p in args.percentiles:
        var, tvar = vt[p]
        print(f"  {p:<14}{money(var):>22}{money(tvar):>22}")
    print(bar)

    # ---- save CSVs ---- #
    summary_rows = [("AAL", aal), ("total_loss", total_loss),
                    ("N_simulated_years", args.years),
                    ("years_with_loss", n_loss_years),
                    ("zero_loss_years", n_zero)]
    for rp in rps:
        summary_rows.append((f"OEP_1in{rp}", oep_rp[rp]))
        summary_rows.append((f"AEP_1in{rp}", aep_rp[rp]))
    for p in args.percentiles:
        summary_rows.append((f"VaR_{p}", vt[p][0]))
        summary_rows.append((f"TVaR_{p}", vt[p][1]))
    summary_path = os.path.join(args.out_dir, "cat_metrics_summary.csv")
    pd.DataFrame(summary_rows, columns=["metric", "value"]).to_csv(
        summary_path, index=False)

    # full EP curve data
    o_loss, o_ep, o_rp = ep_curve(occ, args.years)
    a_loss, a_ep, a_rp = ep_curve(agg, args.years)
    ep_path = os.path.join(args.out_dir, "ep_curve_data.csv")
    pd.DataFrame({"return_period": o_rp, "exceedance_prob": o_ep,
                  "OEP_loss": o_loss, "AEP_loss": a_loss}).to_csv(ep_path, index=False)

    print(f"  Saved: {png_path}")
    print(f"  Saved: {summary_path}")
    print(f"  Saved: {ep_path}")
    print("  Note: these metrics describe YOUR input table. They are not an")
    print("  independently validated forecast. For a sealed, verifiable run on")
    print("  the QRS engine, see the 'montecarlo' skill / qrsrisk.com.")


if __name__ == "__main__":
    main()
