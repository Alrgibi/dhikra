"""make_figures_extra.py -- the three remaining planned thesis figures.

Completes the figure register: the ablation chart, the robustness heatmap and
the validation-story flow diagram (the defence centrepiece). Same palette and
conventions as make_figures.py and make_figures_partA.py.

NOTE ON THE ONE FIGURE THAT IS NOT PRODUCED. The plan also listed "the three
picture stimuli". The Cookie Theft scene belongs to the Boston Diagnostic
Aphasia Examination and is not redistributable; no copy exists in this
repository and none is created here. Describe the stimuli in text, or
reproduce them only under the BDAE's own licence terms.
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(SRC, "docs", "figures")
INK, MUTED, GRID = "#1b2b33", "#5b6b72", "#dfe6e4"
TEAL, RUST, PLUM = "#0e9384", "#c2410c", "#5b21b6"
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

caps = []

# ------------------------------------------------------------------ ABLATION
AB = json.load(open(f"{SRC}/results/reconstruction/ablation_post_lock.json"))["rows"]
AB = sorted(AB, key=lambda r: r["auc"])
lab = [f'{r["set"]}  (n = {r["n_features"]})' for r in AB]
auc = [r["auc"] for r in AB]
lo = [r["auc"] - r["ci"][0] for r in AB]
hi = [r["ci"][1] - r["auc"] for r in AB]
cols = []
for r in AB:
    if r["set"].startswith("all features, final"):
        cols.append(TEAL)
    elif "age" in r["set"]:
        cols.append(RUST)
    elif r["set"].startswith("Arabic"):
        cols.append(PLUM)
    else:
        cols.append(MUTED)
fig, ax = plt.subplots(figsize=(6.8, 3.6))
ax.barh(range(len(AB)), auc, xerr=[lo, hi], color=cols, edgecolor=INK,
        linewidth=0.4, error_kw={"ecolor": INK, "elinewidth": 0.8, "capsize": 2.5})
ax.axvline(0.5, color=INK, lw=0.9, ls=":")
ax.text(0.505, -0.45, "chance", fontsize=7, color=MUTED)
ax.set_yticks(range(len(AB))); ax.set_yticklabels(lab)
ax.set_xlim(0.45, 0.86)
ax.set_xlabel("AUC (participant-grouped 5-fold CV, participant bootstrap 95% CI)")
ax.set_title("Feature-set ablation on the locked development pool")
spine(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_ablation.png"); plt.close(fig)
caps.append(("fig_ablation.png",
    "Feature-set ablation on the 987-recording locked development pool, participant-grouped "
    "five-fold cross-validation with participant-level bootstrap intervals. No single family "
    "carries the result: information content alone reaches 0.711 and the linguistic set alone "
    "0.739, against 0.755 for the deployed ensemble on all 64. Age alone is at 0.557 and its "
    "interval touches chance, which is the ablation-side evidence that the matched design "
    "removed the age confound. Adding age to the full set would reach 0.767; it is excluded "
    "deliberately, because age is applied afterwards as an epidemiological prior rather than "
    "learned as a shortcut. The 19-feature Arabic-compatible subset reaches 0.739, within the "
    "interval of the full set."))

# ---------------------------------------------------------------- ROBUSTNESS
S = pd.read_csv(f"{SRC}/results/robustness/stability.csv")
cond_pretty = {"mp3_64k": "MP3 64 kbps", "mp3_32k": "MP3 32 kbps",
               "noise_20dB": "background noise, 20 dB SNR",
               "noise_10dB": "background noise, 10 dB SNR",
               "distance": "phone at table distance", "quiet": "low recording volume",
               "clipped": "clipping", "downsample_8k": "telephone bandwidth, 8 kHz"}
feat_pretty = {"ac.phonation_ratio": "phonation ratio", "ac.pause_count": "pause count",
               "ac.pause_rate_per_min": "pause rate", "ac.pause_mean_s": "mean pause length",
               "ac.f0_mean_hz": "mean pitch", "ac.f0_cv": "pitch variability",
               "ac.jitter_local": "jitter", "ac.shimmer_local": "shimmer",
               "ac.hnr_db": "harmonics-to-noise ratio"}
order = ["mp3_64k", "mp3_32k", "downsample_8k", "quiet", "clipped", "distance",
         "noise_20dB", "noise_10dB"]
S = S.set_index("condition").loc[[c for c in order if c in set(S.condition if "condition" in S else S.index)]] \
    if "condition" in S.columns else S
S = pd.read_csv(f"{SRC}/results/robustness/stability.csv").set_index("condition")
S = S.loc[[c for c in order if c in S.index]]
M = S.values.astype(float)
fig, ax = plt.subplots(figsize=(7.0, 3.4))
im = ax.imshow(M, cmap="BrBG", vmin=0.4, vmax=1.0, aspect="auto")
ax.set_xticks(range(M.shape[1]))
ax.set_xticklabels([feat_pretty.get(c, c) for c in S.columns], rotation=38, ha="right")
ax.set_yticks(range(M.shape[0]))
ax.set_yticklabels([cond_pretty.get(c, c) for c in S.index])
ax.grid(False)
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M[i, j]
        txt = "—" if not np.isfinite(v) else f"{v:.2f}"
        # BrBG is dark at BOTH ends, so light text is needed for high and low
        # cells alike and dark text only in the pale middle band.
        dark_cell = np.isfinite(v) and (v >= 0.93 or v <= 0.50)
        ax.text(j, i, txt, ha="center", va="center", fontsize=6.5,
                color="white" if dark_cell else INK)
cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
cb.set_label("correlation with the clean recording", fontsize=8)
cb.outline.set_visible(False)
ax.set_title("Acoustic feature stability under recording degradation")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_robustness.png"); plt.close(fig)
caps.append(("fig_robustness.png",
    "Acoustic feature stability under eight recording degradations, measured on real "
    "recordings and expressed as correlation with the same features extracted from the clean "
    "audio. Compression to 32 kbps, telephone bandwidth, low volume and clipping are almost "
    "free; a phone at table distance is tolerable. Background noise is the one condition that "
    "matters, and it attacks pause measurement first: at 20 dB signal-to-noise the pause rate "
    "falls to 0.59 while pitch and voice-quality measures are unaffected. At 10 dB extraction "
    "fails outright, which is the empirical basis for the quality gate's refusal threshold. "
    "A cheap phone is adequate; an open window onto a street is not."))

# ------------------------------------------------------- THE VALIDATION STORY
def box(ax, x, y, w, h, t, edge, face="white", fs=7.4, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.010,rounding_size=0.012",
                                linewidth=1.0, edgecolor=edge, facecolor=face, zorder=2))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs,
            color=INK, zorder=3, weight=weight)

def arr(ax, x1, y1, x2, y2, c=MUTED, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=9, linewidth=0.9, color=c, zorder=1))

fig, ax = plt.subplots(figsize=(7.6, 8.2))
ax.set_xlim(0, 1); ax.set_ylim(0, 1.09); ax.axis("off"); ax.grid(False)
MAIN = [
    (0.925, "1,040 recordings from three DementiaBank corpora\nPitt · Delaware · Lu"),
    (0.815, "Corpus-compatibility test\ntwo studies' healthy speakers separable at AUC 0.930"),
    (0.705, "Rule derived and applied\ncorpora may be pooled only where each contributes both classes"),
    (0.595, "Age confound measured\nage alone reaches AUC 0.707 on the raw Pitt cohort"),
    (0.485, "Age- and sex-matched cohort constructed\nage alone falls to 0.46; speech still reaches 0.80"),
    (0.375, "Participant-grouped 5-fold CV, repeated over ten matching seeds\ncombined AUC 0.755 [0.719, 0.790]"),
    (0.265, "LOCK — 18 August 2026\nLu withheld; threshold fixed at 0.367 before any external scoring"),
    (0.155, "Locked external evaluation, scored once\nAUC 0.853 [0.737, 0.946] · sensitivity 96.2% · specificity 33.3%"),
    (0.045, "Arabic adaptation\nmeasurements reported; no probability, no reference ranges"),
]
for i, (y, t) in enumerate(MAIN):
    edge = PLUM if "LOCK" in t else TEAL
    face = "#f4f1fb" if "LOCK" in t else "white"
    w = "bold" if "LOCK" in t else "normal"
    box(ax, 0.055, y, 0.60, 0.072, t, edge, face, weight=w)
    if i:
        arr(ax, 0.355, MAIN[i - 1][0], 0.355, y + 0.072)
REJ = [
    (0.815, "Pooling a single-class corpus\nREJECTED — label leakage"),
    (0.595, "Age residualisation, apparent AUC 0.853\nREJECTED — age recoverable at R² = 0.994"),
    (0.375, "Task-level fusion −0.047 · late fusion −0.008\nfeature selection k = 15…80: no gain\nREJECTED"),
    (0.265, "Nine-year-ahead prediction, n = 938\nNEGATIVE — AUC 0.548, chance"),
    (0.155, "Pruning corpus-shifted features\nNEGATIVE — Pitt→Delaware falls at every k"),
]
for y, t in REJ:
    box(ax, 0.695, y, 0.265, 0.072, t, RUST, "#fdf1ea", fs=6.6)
    arr(ax, 0.655, y + 0.036, 0.695, y + 0.036, RUST)
ax.text(0.055, 1.085, "The validation story", fontsize=11, weight="bold", color=INK, va="top")
ax.text(0.055, 1.052,
        "Left: what survived. Right: what was measured, failed, and is reported anyway.",
        fontsize=8, color=MUTED, va="top")
fig.tight_layout(); fig.savefig(f"{OUT}/fig_validation_story.png"); plt.close(fig)
caps.append(("fig_validation_story.png",
    "The validation story. The left-hand column is the sequence of decisions that produced the "
    "reported result; the right-hand column is every approach that was tested and rejected, "
    "attached to the stage at which it was tested. The lock of 18 August 2026 is marked because "
    "it divides the project in two: everything above it could be revised, and nothing below it "
    "was. Each rejection is reported in full in Chapter 5, section 5.8."))

with open(f"{OUT}/figure_captions.md", "a", encoding="utf-8") as f:
    f.write("\n\n---\n\n## Remaining planned figures (added 2026-08-23)\n")
    for i, (fn, txt) in enumerate(caps, start=15):
        f.write(f"\n**`{fn}`**\n\n> **Figure (n.{i}):** {txt}\n")
    f.write("\n**NOT PRODUCED — `fig_stimuli`.** The three picture stimuli were listed in the "
            "plan. The Cookie Theft scene belongs to the Boston Diagnostic Aphasia Examination "
            "and is not redistributable; no copy exists in this repository. Describe the "
            "stimuli in text, or reproduce them only under the BDAE's own licence terms.\n")
print("wrote", len(caps), "figures")
for fn, _ in caps:
    print("  ", fn)
