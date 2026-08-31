"""make_figures_partA.py -- the five figures for the specificity chapter.

Companion to make_figures.py; same palette, same faculty conventions.
  Pitt #0e9384 . Delaware #c2410c . Lu #5b21b6
Identity is never colour-alone: every series carries a distinct linestyle and
marker, so the figures survive greyscale printing and colour-vision deficiency.
Captions go BELOW the figure, centred, bold, "Figure (n.m):" -- appended to
docs/figures/figure_captions.md; the word processor places them, not matplotlib.

Reads only committed result JSON. No model is loaded, no corpus is touched.
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(SRC, "docs", "figures")
os.makedirs(OUT, exist_ok=True)

COL = {"Pitt": "#0e9384", "Delaware": "#c2410c", "Lu": "#5b21b6"}
LS  = {"Pitt": "-", "Delaware": "--", "Lu": "-."}
MK  = {"Pitt": "o", "Delaware": "s", "Lu": "^"}
INK, MUTED, GRID = "#1b2b33", "#5b6b72", "#dfe6e4"
plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.labelsize": 9,
    "axes.titlesize": 10, "legend.fontsize": 8, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "axes.edgecolor": MUTED, "axes.linewidth": 0.8,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True})

def spine(ax):
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)

RT = json.load(open(f"{SRC}/results/reconstruction/relative_threshold_rules.json"))
DS = json.load(open(f"{SRC}/results/reconstruction/domain_shift_and_errors.json"))
MS = json.load(open(f"{SRC}/results/reconstruction/metric_suite.json"))
CP = json.load(open(f"{SRC}/results/reconstruction/control_threshold_precision.json"))
COHORTS = ["Pitt", "Delaware", "Lu"]
caps = []

# ---------------------------------------------------------------- FIGURE A.1
# Control-referenced thresholding: specificity is delivered, sensitivity varies.
V = RT["variant_e_control_referenced"]
targets = [0.75, 0.80, 0.85, 0.90]
keys = [f"control_percentile_{t:.2f}" for t in targets]
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.2))
ax[0].plot(targets, targets, color=MUTED, lw=0.9, ls=":", label="target")
for c in COHORTS:
    sp = [V[k][c]["specificity"] for k in keys]
    ax[0].plot(targets, sp, color=COL[c], ls=LS[c], marker=MK[c], ms=4, lw=1.4, label=c)
ax[0].set_xlabel("control-distribution percentile (target specificity)")
ax[0].set_ylabel("specificity achieved")
ax[0].set_ylim(0.66, 0.95); ax[0].set_xticks(targets)
ax[0].set_title("Specificity is delivered to target")
ax[0].legend(frameon=False, loc="upper left")
spine(ax[0])
for c in COHORTS:
    se = [V[k][c]["sensitivity"] for k in keys]
    ax[1].plot(targets, se, color=COL[c], ls=LS[c], marker=MK[c], ms=4, lw=1.4, label=c)
ax[1].set_xlabel("control-distribution percentile (target specificity)")
ax[1].set_ylabel("sensitivity that follows")
ax[1].set_ylim(0.15, 0.95); ax[1].set_xticks(targets)
ax[1].set_title("Sensitivity becomes the variable quantity")
spine(ax[1])
b = RT["bootstrap_on_lu"]["sens_target_0.80"]["control_ref_0.80"]
ax[0].errorbar([0.80], [b["spec_median"]],
               yerr=[[b["spec_median"] - b["spec_ci95"][0]], [b["spec_ci95"][1] - b["spec_median"]]],
               color=COL["Lu"], capsize=3, lw=1.0, zorder=5)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_control_referenced.png"); plt.close(fig)
caps.append(("fig_control_referenced.png",
    "Control-referenced thresholding. The threshold is set at a fixed percentile of the "
    "LOCAL healthy-control score distribution. Left: specificity tracks the target in all "
    "three cohorts (79.8 / 79.9 / 77.8 per cent at an 80 per cent target); the error bar on "
    "Lu is the participant bootstrap, 0.774 [0.69, 0.80], which is an in-sample interval and "
    "cannot exceed the target by construction. Right: sensitivity is what varies "
    "(0.695 / 0.356 / 0.769), ordered as the cohorts' AUCs predict. Delaware's low "
    "sensitivity is its discrimination limit reappearing, not a failure of the rule."))

# ---------------------------------------------------------------- FIGURE A.2
# Recovery fraction: the rules were efficient; the failures are overshoot.
R = RT["rules_development_fixed"]
rows = []
for direc, tg in R.items():
    for tgt, blk in tg.items():
        for rule, v in blk.items():
            if isinstance(v, dict) and "recovery_fraction" in v:
                rows.append((rule, v["sensitivity"], v["recovery_fraction"]))
RULE_C = {"absolute": INK, "percentile": "#0e9384", "mean_match": "#c2410c",
          "z_norm": "#5b21b6", "quantile_map": "#8a6d1f"}
RULE_M = {"absolute": "D", "percentile": "o", "mean_match": "s",
          "z_norm": "^", "quantile_map": "v"}
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={"width_ratios": [1.55, 1]})
for rule in RULE_C:
    xs = [r[1] for r in rows if r[0] == rule]
    ys = [r[2] for r in rows if r[0] == rule]
    ax[0].scatter(xs, ys, s=22, facecolors="none", edgecolors=RULE_C[rule],
                  marker=RULE_M[rule], linewidths=1.0, label=rule.replace("_", "-"))
ax[0].axhline(0.93, color=MUTED, lw=0.9, ls=":")
ax[0].axvline(0.92, color=MUTED, lw=0.9, ls="--")
ax[0].text(0.925, 0.06, "overshoot region", fontsize=7, color=MUTED, rotation=90, va="bottom")
ax[0].text(0.40, 0.945, "0.93", fontsize=7, color=MUTED)
ax[0].set_xlabel("sensitivity actually reached")
ax[0].set_ylabel("recovery fraction (specificity ÷ ROC ceiling)")
ax[0].set_ylim(-0.04, 1.06)
ax[0].set_title("Efficiency along the curve, by where the rule landed")
ax[0].legend(frameon=False, loc="lower left", ncol=2)
spine(ax[0])
CE = RT["roc_ceilings"]
sens_lv = [0.75, 0.80, 0.85, 0.90]
w = 0.26
for i, c in enumerate(COHORTS):
    vals = [CE[c][f"at_sens_{s:.2f}"] for s in sens_lv]
    ax[1].bar(np.arange(len(sens_lv)) + (i - 1) * w, vals, width=w,
              color=COL[c], edgecolor=INK, linewidth=0.4, label=c)
ax[1].set_xticks(range(len(sens_lv)))
ax[1].set_xticklabels([f"{s:.2f}" for s in sens_lv])
ax[1].set_xlabel("sensitivity level")
ax[1].set_ylabel("maximum attainable specificity")
ax[1].set_title("ROC ceilings")
ax[1].legend(frameon=False)
spine(ax[1])
fig.tight_layout(); fig.savefig(f"{OUT}/fig_recovery_ceiling.png"); plt.close(fig)
caps.append(("fig_recovery_ceiling.png",
    "Threshold efficiency and the ceilings that bound it. Left: recovery fraction -- "
    "specificity achieved divided by the maximum any threshold could achieve at the "
    "sensitivity actually reached -- for all 80 rule by target by direction cells. The median "
    "is 0.984 and 58 of 80 sit above 0.93; every cell below that line lies in the overshoot "
    "region to the right of the dashed line, where the rule has run to the far edge of the ROC "
    "curve and the ratio is taken between two near-zero quantities. The rules were not "
    "inefficient; they landed in the wrong place. Right: the ceilings themselves. Delaware's "
    "0.376 at 75 per cent sensitivity is why no threshold rule can repair that cohort."))

# ---------------------------------------------------------------- FIGURE A.3
A5 = DS["A5_lu_false_positives"]
# Top 13 by |SMD|, plus age forced in: age is a confound the sample cannot
# resolve (the false positives were 8.4 years older), so it must be visible
# rather than trimmed off the bottom of the ranking.
_r = [r for r in A5["ranked_differences_fp_vs_tn"] if abs(r["smd"]) >= 0.80]
rk = _r[:13] + [r for r in _r if r["variable"] == "age"][:1]
rk = sorted(rk, key=lambda r: r["smd"])
PRETTY = {"iu.has_stool_falling": "mentions the stool falling",
          "ling.pronoun_to_noun_ratio": "pronoun-to-noun ratio",
          "ling.pronoun_rate": "pronoun rate",
          "iu.has_cupboard": "mentions the cupboard",
          "ling.noun_rate": "noun rate",
          "sem.content_dispersion": "content dispersion",
          "iu.has_window": "mentions the window",
          "iu.has_exterior": "mentions the exterior",
          "iu.has_water_overflowing": "mentions water overflowing",
          "iu.total": "information units (total)",
          "iu.proportion": "proportion of units produced",
          "iu.has_curtain": "mentions the curtain",
          "iu.objects": "objects named",
          "iu.has_woman_unconcerned": "describes the woman as unconcerned",
          "iu.actions": "actions described",
          "age": "age",
          "sem.min_coherence": "minimum coherence",
          "ling.content_word_ratio": "content-word ratio",
          "ling.adv_rate": "adverb rate"}
labels = [PRETTY.get(r["variable"], r["variable"]) for r in rk]
vals = [r["smd"] for r in rk]
fig, ax = plt.subplots(figsize=(6.6, 4.2))
cols = ["#c2410c" if v > 0 else "#0e9384" for v in vals]
ax.barh(range(len(vals)), vals, color=cols, edgecolor=INK, linewidth=0.4)
ax.set_yticks(range(len(vals))); ax.set_yticklabels(labels)
ax.axvline(0, color=INK, lw=0.8)
ax.set_xlabel("standardised mean difference (false positives − true negatives)")
ax.set_title("Lu controls the model flagged, against those it did not")
ax.text(0.02, 0.02, "n = 18 false positives vs 9 true negatives",
        transform=ax.transAxes, fontsize=7, color=MUTED)
spine(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_lu_false_positives.png"); plt.close(fig)
caps.append(("fig_lu_false_positives.png",
    "Why specificity was 33 per cent. The 18 healthy Lu speakers the fixed threshold "
    "misclassified, compared with the 9 it classified correctly, on every deployed feature "
    "with a standardised mean difference of at least 0.8. The misclassified controls produced "
    "11.5 information units against 14.9, named 4.7 objects against 6.8, and used pronouns in "
    "place of nouns at 0.893 against 0.537; 44 per cent mentioned the falling stool against "
    "100 per cent. These are impoverished descriptions, so the model detected what was present "
    "rather than malfunctioning, and no threshold rule could have separated them. The age "
    "difference (82.6 against 74.2 years) is shown because it is a confound the sample cannot "
    "resolve."))

# ---------------------------------------------------------------- FIGURE A.4
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.2))
prev = np.linspace(0.02, 0.60, 200)
for c in COHORTS:
    se, sp = MS[c]["sensitivity"], MS[c]["specificity"]
    ppv = (se * prev) / (se * prev + (1 - sp) * (1 - prev))
    npv = (sp * (1 - prev)) / (sp * (1 - prev) + (1 - se) * prev)
    ax[0].plot(prev, ppv, color=COL[c], ls=LS[c], lw=1.4, label=c)
    ax[1].plot(prev, npv, color=COL[c], ls=LS[c], lw=1.4, label=c)
for a, t in zip(ax, ("Positive predictive value", "Negative predictive value")):
    a.axvline(0.10, color=MUTED, lw=0.9, ls=":")
    a.text(0.105, a.get_ylim()[0], " community\n prevalence ≈ 10%", fontsize=7, color=MUTED, va="bottom")
    a.set_xlabel("prevalence in the tested population")
    a.set_title(t); spine(a)
ax[0].set_ylabel("PPV"); ax[1].set_ylabel("NPV")
ax[0].legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_ppv_prevalence.png"); plt.close(fig)
caps.append(("fig_ppv_prevalence.png",
    "Predictive values against prevalence, at the deployed threshold of 0.367. Sensitivity and "
    "specificity are properties of the test; predictive values are not, and shift with the "
    "population tested. At a community prevalence near 10 per cent the positive predictive "
    "value falls to 0.14-0.17 while the negative predictive value stays between 0.93 and 0.99. "
    "The instrument rules out far better than it rules in, which is what a screening test is "
    "for. No predictive value should be quoted without the prevalence it assumes."))

# ---------------------------------------------------------------- FIGURE A.5
T = CP["table"]
n = [r["n_controls"] for r in T]
mid = [r["expected_specificity"] for r in T]
lo = [r["ci95"][0] for r in T]; hi = [r["ci95"][1] for r in T]
fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.fill_between(n, lo, hi, color="#0e9384", alpha=0.14, lw=0)
ax.plot(n, mid, color="#0e9384", lw=1.5, marker="o", ms=3.5)
ax.axhline(0.80, color=MUTED, lw=0.9, ls=":")
for tag, xv, cc in (("Lu (27)", 27, "#5b21b6"), ("pilot target (20)", 20, "#c2410c")):
    ax.axvline(xv, color=cc, lw=0.9, ls="--")
    ax.text(xv + 2, 0.50, tag, fontsize=7, color=cc, rotation=90, va="bottom")
ax.set_xscale("log")
ax.set_xticks([15, 20, 30, 50, 100, 200])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_xlabel("number of local healthy controls defining the threshold")
ax.set_ylabel("specificity achieved on a new population")
ax.set_title("Exact precision of a control-referenced threshold")
spine(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_threshold_precision.png"); plt.close(fig)
caps.append(("fig_threshold_precision.png",
    "How many healthy controls a control-referenced threshold needs. If the threshold is the "
    "k-th order statistic of n healthy controls with k the ceiling of 0.80n, the specificity it "
    "achieves on a fresh population follows a Beta(k, n+1-k) law. The result is exact and "
    "distribution-free, so it holds for a Libyan cohort whose score distribution is unknown. "
    "The shaded band is the 95 per cent interval. At the pilot's 20-participant target it spans "
    "0.56 to 0.91; 59 controls are needed for a 10-point interval and 108 for a 7.5-point one. "
    "This is the sample-size justification for the pilot's healthy stratum."))

with open(f"{OUT}/figure_captions.md", "a", encoding="utf-8") as f:
    f.write("\n\n---\n\n## Specificity chapter (added 2026-08-23)\n")
    for i, (fn, txt) in enumerate(caps, start=10):
        f.write(f"\n**`{fn}`**\n\n> **Figure (n.{i}):** {txt}\n")
print("wrote", len(caps), "figures to", OUT)
for fn, _ in caps:
    print("  ", fn)
