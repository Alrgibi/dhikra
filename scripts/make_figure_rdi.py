"""make_figure_rdi.py -- the English construct probe for the Arabic referential
deficit index. Same palette and faculty conventions as the other figure scripts.
Reads only committed result JSON."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

D = json.load(open(f"{SRC}/results/reconstruction/rdi_english_probe.json"))
sets = [("Pitt  (dementia, n=548)", D["cohorts"]["pitt"]["auc"], TEAL, "o"),
        ("Pitt, matched  (n=368)", D["cohorts"]["pitt"]["matched_subset"]["auc"], PLUM, "^"),
        ("Delaware  (MCI, n=439)", D["cohorts"]["dela"]["auc"], RUST, "s")]
measures = [("pn", "pronouns ÷ nouns\n(established marker)"),
            ("rdi_full", "+ demonstratives\n+ vague nouns"),
            ("rdi_free", "demonstratives + vague nouns\n÷ nouns  (pronoun-free)")]

fig, ax = plt.subplots(figsize=(7.8, 4.6))
ypos, ylab = [], []
y = 0
for mi, (mkey, mlab) in enumerate(measures):
    for si, (slab, blk, col, mk) in enumerate(sets):
        v = blk[mkey]
        lo, hi = v["ci95"]
        ax.plot([lo, hi], [y, y], color=col, lw=1.6, solid_capstyle="butt")
        ax.plot([v["auc"]], [y], marker=mk, ms=6, color=col,
                markerfacecolor="white", markeredgewidth=1.6, zorder=3)
        ax.text(hi + 0.006, y, f'{v["auc"]:.3f}', va="center", fontsize=7, color=MUTED)
        ypos.append(y); ylab.append(slab if mi == 0 else "")
        y -= 1
    y -= 0.6

ax.axvline(0.5, color=INK, lw=1.0, ls=":")
ax.text(0.502, ypos[-1] - 0.3, "chance", fontsize=7, color=MUTED, rotation=90, va="bottom")
ax.set_yticks(ypos)
ax.set_yticklabels([sets[i % 3][0] for i in range(len(ypos))], fontsize=7.5)
# Group headers sit ABOVE each block of three rows rather than beside the
# middle row, which collided with that row's tick label.
for i, (_, mlab) in enumerate(measures):
    top = ypos[i * 3] + 0.85
    ax.text(-0.34, top, mlab.replace("\n", " "), transform=ax.get_yaxis_transform(),
            ha="left", va="center", fontsize=8.5, color=INK, weight="bold")
    ax.plot([-0.34, 1.0], [top - 0.3, top - 0.3], transform=ax.get_yaxis_transform(),
            color=GRID, lw=0.8, clip_on=False, zorder=0)
ax.set_xlim(0.42, 0.80)
ax.set_xlabel("AUC with participant-bootstrap 95% confidence interval")
ax.set_title("The referential deficit index, probed in English", pad=16)
for k in ("top", "right", "left"):
    ax.spines[k].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.subplots_adjust(left=0.40)
fig.savefig(f"{OUT}/fig_rdi_probe.png"); plt.close(fig)

with open(f"{OUT}/figure_captions.md", "a", encoding="utf-8") as f:
    f.write("\n\n---\n\n## Arabic construct probe (added 2026-08-23)\n\n")
    f.write("**`fig_rdi_probe.png`**\n\n> **Figure (n.18):** The referential deficit index, probed in English. "
            "The Arabic instrument replaces the English pronoun-overuse marker with demonstratives and vague nouns "
            "relative to naming, because Arabic is pro-drop; the index had never been computed on the speech of a "
            "diagnosed patient in any language. The pronoun-free variant, which is structurally what the Arabic index "
            "is, discriminates on the Pittsburgh dementia cohort and improves under age and sex matching, so the "
            "separation is not an age artefact. It fails on the Delaware mild-impairment cohort, but so does the "
            "established pronoun marker it replaces, so that is a property of the cohort rather than of the new "
            "measure. Adding demonstratives and vague nouns to the established marker neither helps nor harms it in "
            "any of the three analysis sets. Criteria were fixed in writing before the analysis was run.\n")
print("wrote fig_rdi_probe.png")
