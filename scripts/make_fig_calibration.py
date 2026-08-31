#!/usr/bin/env python3
"""
make_fig_calibration.py -- committed generator for fig_calibration.png, written
2026-08-26 as provenance recovery.

WHY THIS EXISTS. fig_calibration.png is one of nine thesis figures whose
producing code was never committed (WRITING_FINDINGS entry 12). It is the one
of the nine reconstructed before submission, because a figure and a text
number are in tension: the caption register carries slope 1.289 / intercept
0.138, while docs/NUMBERS.md points section 5.4 at 1.2764 / 0.1348 from
CURRENT_development_stats.json. Two committed witnesses -- the raw fit in
recalibration_decision.json and the stored-vector refit in
oof_vector_diagnostic.json -- give 1.2887 / 0.1376; the canonical pair is the
one without a second witness.

WHAT IT DRAWS, from committed inputs only: per-cohort calibration curves in
0.2-wide score bands (bands with fewer than five recordings omitted), mean
predicted score against observed impairment rate, for Pitt and Delaware from
the stored out-of-fold vector (oof_predictions/labels/source .npy, order
asserted against the meta files) and for Lu from the 53 stored predictions in
lu_oneshot_reproduction.json. Nothing is refit and nothing is rescored; the
Lu list is read the way any result file is read.

CRITERION -- fixed before execution, report-and-stop: the reconstructed
per-cohort band points must visually and numerically match the committed PNG
(same bands survive the n >= 5 filter; same band means and observed rates to
plotting precision). The reconstruction is written BESIDE the original as
fig_calibration_reconstructed.png; the original is not overwritten. Whether
section 5.4's text cites 1.2887/0.1376 (the twice-witnessed pair the figure
caption rounds to) or regenerates the canonical summary is Session B's
decision and is logged as blocking for section 5.4.

Output: docs/figures/fig_calibration_reconstructed.png
        results/reconstruction/fig_calibration_provenance.json
"""
import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = os.path.join(ROOT, "results")

BANDS = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
MIN_N = 5
STYLE = {
    "Pitt":     dict(color="#0e9384", ls="-",  marker="o"),
    "Delaware": dict(color="#c2410c", ls="--", marker="s"),
    "Lu":       dict(color="#5b21b6", ls="-.", marker="^"),
}


def band_points(p, y):
    pts = []
    for lo, hi in BANDS:
        m = (p > lo) & (p <= hi)
        if int(m.sum()) >= MIN_N:
            pts.append({"band": f"({lo}, {hi}]", "n": int(m.sum()),
                        "mean_predicted": float(p[m].mean()),
                        "observed_rate": float(y[m].mean())})
    return pts


def main():
    p = np.load(os.path.join(R, "summary/oof_predictions.npy"))
    y = np.load(os.path.join(R, "summary/oof_labels.npy")).astype(int)
    src = np.load(os.path.join(R, "summary/oof_source.npy"), allow_pickle=True)
    mp = pd.read_csv(os.path.join(R, "pitt_cookie/meta.csv"))
    md = pd.read_csv(os.path.join(R, "delaware/cookie_meta.csv"))
    assert len(p) == 987
    assert np.array_equal(y, np.concatenate([mp.label.values, md.label.values]).astype(int)), \
        "VOID: stored labels do not match the meta files -- alignment unproven"
    pitt_mask = np.zeros(987, dtype=bool)
    pitt_mask[:548] = True
    assert len(set(str(s) for s in src[:548])) == 1 and len(set(str(s) for s in src[548:])) == 1 \
        and str(src[0]) != str(src[-1]), "VOID: oof_source does not split 548/439"

    lu = json.load(open(os.path.join(R, "reconstruction/lu_oneshot_reproduction.json")))["predictions"]
    p_lu = np.array([r["p"] for r in lu])
    y_lu = np.array([r["label"] for r in lu], dtype=int)
    assert len(p_lu) == 53

    curves = {
        "Pitt": band_points(p[pitt_mask], y[pitt_mask]),
        "Delaware": band_points(p[~pitt_mask], y[~pitt_mask]),
        "Lu": band_points(p_lu, y_lu),
    }

    fig, ax = plt.subplots(figsize=(5.2, 5.0), dpi=300)
    ax.plot([0, 1], [0, 1], ":", color="0.55", lw=1, zorder=1)
    for name, pts in curves.items():
        xs = [q["mean_predicted"] for q in pts]
        ys = [q["observed_rate"] for q in pts]
        ax.plot(xs, ys, label=name, lw=2.2, markersize=7, zorder=3, **STYLE[name])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("mean predicted score")
    ax.set_ylabel("observed impairment rate")
    ax.grid(True, color="0.92", lw=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    dst_png = os.path.join(ROOT, "docs/figures/fig_calibration_reconstructed.png")
    fig.savefig(dst_png)

    out = {
        "script": "scripts/make_fig_calibration.py",
        "purpose": "committed generator reconstructed for fig_calibration.png; original left untouched",
        "inputs": ["results/summary/oof_predictions.npy (+labels/source, order asserted)",
                   "results/reconstruction/lu_oneshot_reproduction.json -> predictions (53, stored)"],
        "bands": "0.2-wide, bands with n < 5 omitted",
        "curves": curves,
        "slope_intercept_context": {
            "caption_register": {"slope": 1.289, "intercept": 0.138},
            "CURRENT_development_stats (NUMBERS canonical, sec 5.4)": {"slope": 1.2764, "intercept": 0.1348},
            "recalibration_decision.json development_pooled.raw": {"slope": 1.2887, "intercept": 0.1376},
            "oof_vector_diagnostic.json stored_vector": {"slope": 1.2887, "intercept": 0.1376},
            "note": "the caption pair rounds from the twice-witnessed stored-vector fit, not from the canonical summary; BLOCKING for section 5.4 (Session B)",
        },
    }
    dst = os.path.join(R, "reconstruction/fig_calibration_provenance.json")
    json.dump(out, open(dst, "w"), indent=2)
    print("written:", dst_png)
    print("written:", dst)
    for name, pts in curves.items():
        print(" ", name, [(round(q["mean_predicted"], 3), round(q["observed_rate"], 3), q["n"]) for q in pts])


if __name__ == "__main__":
    main()
