"""make_figure_genre.py -- Figure 20: task genre and the MCI signal.

Same palette and faculty conventions as make_figures.py / make_figures_partA.py.
Identity is never colour-alone: genre carries a distinct marker and fill as well
as a hue, so the figure survives greyscale printing.

Reads only committed result JSON. No model is loaded, no corpus is touched.
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(SRC, "docs", "figures"); os.makedirs(OUT, exist_ok=True)
DEL, INK, MUTED, GRID = "#c2410c", "#1b2b33", "#5b6b72", "#dfe6e4"
plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.labelsize": 9,
    "axes.titlesize": 10, "legend.fontsize": 8, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "axes.edgecolor": MUTED, "axes.linewidth": 0.8,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True})
def spine(ax):
    for k in ("top", "right"): ax.spines[k].set_visible(False)

TC = json.load(open(f"{SRC}/results/reconstruction/task_count_curve.json"))
RD = json.load(open(f"{SRC}/results/reconstruction/rdi_cross_task_probe.json"))
FT = json.load(open(f"{SRC}/results/reconstruction/feature_by_task_auc.json"))
A3 = TC["AMENDMENT_3_crosssectional"]
DISC = set(TC["genre_contrast"]["discourse"])

fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.6, 4.0),
                               gridspec_kw={"width_ratios": [1.0, 1.15]})

# ---- Panel A: the five tasks, ordered, by genre --------------------------
name = {"cookie": "Cookie Theft", "cat": "Cat Rescue", "rockwell": "Rockwell",
        "cinderella": "Cinderella retell", "sandwich": "Making a sandwich"}
singles = A3["singles"]
order = sorted(singles, key=lambda t: singles[t])
ys = np.arange(len(order))
for i, t in enumerate(order):
    d = t in DISC
    ci = RD["per_task"][t]  # CIs for the model score are per-subset; use task CI from curve
    axA.plot(singles[t], i, marker="o" if d else "s", ms=7 if d else 6,
             mfc=DEL if d else "white", mec=DEL if d else MUTED, mew=1.4,
             linestyle="none", zorder=3)
axA.axvline(0.5, color=MUTED, lw=0.9, ls=":", zorder=1)
axA.text(0.5, -0.42, " chance", color=MUTED, fontsize=7.5, va="center")
axA.axhspan(-0.55, 2.5, color=MUTED, alpha=0.06, zorder=0)
axA.axhspan(2.5, 4.75, color=DEL, alpha=0.07, zorder=0)
axA.text(0.655, 0.75, "picture\ndescription", color=MUTED, fontsize=8,
         ha="right", va="center", style="italic")
axA.text(0.655, 3.75, "connected\ndiscourse", color=DEL, fontsize=8,
         ha="right", va="center", style="italic")
axA.text(0.468, 4.35, "two discourse tasks administered together\n"
         "beat three picture tasks administered together\n"
         r"$+0.079$   95% CI [$+0.004$, $+0.158$]", color=INK, fontsize=7.2,
         ha="left", va="top", linespacing=1.5)
axA.set_yticks(ys); axA.set_yticklabels([name[t] for t in order])
axA.set_xlim(0.462, 0.662); axA.set_ylim(-0.55, 4.75)
axA.set_xlabel("AUC, MCI vs control (Delaware, n = 288)")
axA.set_title("(a)  The five tasks separate by genre", loc="left")
axA.grid(axis="y", visible=False)
spine(axA)

# ---- Panel B: which measures move on discourse ---------------------------
FAM = [("ling.word_count", "word count", "volume"),
       ("ling.sentence_count", "sentence count", "volume"),
       ("ling.brunet_w", "Brunét's W", "lexical richness"),
       ("ling.type_token_ratio", "type–token ratio", "lexical richness"),
       ("sem.content_dispersion", "content dispersion", "coherence"),
       ("sem.progression", "semantic progression", "coherence"),
       ("ling.mean_dependency_distance", "mean dep. distance", "syntax"),
       ("chat.reformulation_per100", "reformulations", "disfluency"),
       ("ling.pronoun_to_noun_ratio", "pronoun : noun", "REFERENTIAL"),
       ("ling.pronoun_rate", "pronoun rate", "REFERENTIAL"),
       ("ling.det_rate", "determiner rate", "REFERENTIAL")]
FAM = [f for f in FAM if f[0] in FT]
ys = np.arange(len(FAM))[::-1]
for y, (k, lab, fam) in zip(ys, FAM):
    d, p = FT[k]["disc_mean"], FT[k]["pic_mean"]
    ref = fam == "REFERENTIAL"
    axB.plot([p, d], [y, y], color=MUTED if ref else DEL, lw=1.2,
             alpha=0.45 if ref else 0.8, zorder=2, solid_capstyle="round")
    axB.plot(p, y, marker="s", ms=5, mfc="white", mec=MUTED, mew=1.2,
             linestyle="none", zorder=3)
    axB.plot(d, y, marker="o", ms=6.5, mfc=MUTED if ref else DEL,
             mec=MUTED if ref else DEL, linestyle="none", zorder=3)
axB.axvline(0.5, color=MUTED, lw=0.9, ls=":", zorder=1)
axB.axhspan(-0.5, 2.5, color=MUTED, alpha=0.06, zorder=0)
axB.set_yticks(ys)
axB.set_yticklabels([f"{lab}" for _, lab, _ in FAM])
for tick, (_, _, fam) in zip(axB.get_yticklabels(), FAM):
    if fam == "REFERENTIAL": tick.set_color(MUTED); tick.set_style("italic")
axB.set_xlim(0.46, 0.66); axB.set_ylim(-0.75, len(FAM) - 0.25)
axB.set_xlabel("single-feature AUC, MCI vs control")
axB.set_title("(b)  What moves when the task changes", loc="left")
axB.grid(axis="y", visible=False)
axB.text(0.658, 0.15, "referential family — the construct\nbehind the Arabic index", color=MUTED,
         fontsize=7.2, ha="right", va="center", style="italic")
h = [plt.Line2D([], [], marker="s", ms=5, mfc="white", mec=MUTED, ls="none",
                label="picture description (mean of 3)"),
     plt.Line2D([], [], marker="o", ms=6.5, mfc=DEL, mec=DEL, ls="none",
                label="connected discourse (mean of 2)")]
axB.legend(handles=h, loc="upper left", frameon=False, fontsize=7.5,
           bbox_to_anchor=(0.0, 1.0))
spine(axB)

fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_task_genre.png"))
print("written:", os.path.join(OUT, "fig_task_genre.png"))

CAP = ("**Figure (5.20):** Task genre and the mild-cognitive-impairment signal, "
       "Delaware, 288 participants at their earliest common visit, 43 features "
       "shared by all five task extractors. **(a)** The five tasks separate "
       "perfectly by genre: the two connected-discourse tasks occupy the top two "
       "places and the three picture-description tasks the bottom three, with no "
       "overlap. Two discourse tasks administered together beat three picture "
       "tasks administered together by +0.079 [+0.004, +0.158]. **(b)** Single-"
       "feature AUCs on picture description (open squares, mean of three tasks) "
       "against connected discourse (filled circles, mean of two). Volume, "
       "lexical-richness, coherence, syntactic and disfluency measures all gain; "
       "every measure in the referential family — the construct behind the "
       "Arabic referential deficit index — stays at chance in both genres.")
capf = os.path.join(OUT, "figure_captions.md")
with open(capf, "a", encoding="utf-8") as f:
    f.write("\n\n" + CAP + "\n")
print("caption appended to", capf)
