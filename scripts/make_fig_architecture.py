#!/usr/bin/env python3
"""
make_fig_architecture.py -- committed generator for docs/figures/fig_architecture.png

WHY THIS EXISTS (2026-08-27). The original fig_architecture.png was one of the
eight figures whose producing code was never committed. It was drawn before the
battery revision of 2026-08-25 (THESIS_PLAN 3.5, 5.25) and therefore omitted the
procedural-discourse task, which the deployed system administers, records, and
does not analyse. A figure of the deployed architecture that omits an
administered task contradicts Chapter 4's battery table, so the figure was
redrawn -- the only permitted ground for regeneration: a source file
(app/server.py, battery of 2026-08-25) changed after the figure was made.

WHAT IT SHOWS, unchanged from the original in every scored respect: the
screening decision is computed from picture description alone (the only task
with healthy controls in training); the supporting tasks feed severity and
context and never the screening decision. Added: the procedural-discourse lane,
recorded as material for the successor corpus and not analysed.

Style follows the project's figure conventions: 300 dpi, palette teal #0e9384 /
orange #c2410c / purple #5b21b6, serif text, rounded boxes, slate arrows.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

TEAL, ORANGE, PURPLE, SLATE, GRAY = "#0e9384", "#c2410c", "#5b21b6", "#5b7078", "#6b7280"
plt.rcParams["font.family"] = "serif"

fig, ax = plt.subplots(figsize=(13.0, 6.9), dpi=300)
ax.set_xlim(0, 130); ax.set_ylim(0, 69); ax.axis("off")


def box(x, y, w, h, color, text, fs=15, dashed=False, lw=2.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.6,rounding_size=1.6",
                                linewidth=lw, edgecolor=color, facecolor="white",
                                linestyle=(0, (5, 3)) if dashed else "solid"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color="#1f2933", linespacing=1.45)
    return x, y, w, h


def arrow(x1, y1, x2, y2, dashed=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=22, linewidth=2.2, color=SLATE,
                                 linestyle=(0, (5, 3)) if dashed else "solid",
                                 shrinkA=2, shrinkB=2))


# ── primary lane (teal), y 46..60 ──────────────────────────────────────────
ax.text(4, 64.5, "PRIMARY – the only task with healthy controls in training",
        fontsize=15, color=TEAL, ha="left", va="center")
box(4, 47, 25, 14, TEAL, "Picture\ndescription")
box(36, 47, 25, 14, TEAL, "64 language\nfeatures")
box(68, 47, 25, 14, TEAL, "screening model\n(frozen)", fs=14.5)
arrow(29.7, 54, 35.3, 54); arrow(61.7, 54, 67.3, 54)

# ── supporting lane (orange), y 22..40 ─────────────────────────────────────
box(4, 23, 25, 17, ORANGE, "Story recall\nVerbal fluency\nQur'anic recitation", fs=13.2)
box(36, 25.5, 25, 12, ORANGE, "task measures")
box(68, 25.5, 25, 12, ORANGE, "severity index\n(status: unconfirmed)", fs=12.4)
arrow(29.7, 31.5, 35.3, 31.5); arrow(61.7, 31.5, 67.3, 31.5)
ax.text(4, 19.2, "SUPPORTING – severity and context; never the screening decision",
        fontsize=15, color=ORANGE, ha="left", va="center")

# ── collected lane (gray, dashed), y 3..14 ─────────────────────────────────
box(4, 4.5, 25, 11, GRAY, "Procedural\ndiscourse", fs=13.8, dashed=True)
box(36, 4.5, 62, 11, GRAY, "recorded, not analysed – connected-discourse\nmaterial for the successor corpus (section 5.25)",
    fs=12.6, dashed=True)
arrow(29.7, 10, 35.3, 10, dashed=True)
ax.text(4, 0.9, "COLLECTED – stored with the session; no score is computed from it",
        fontsize=15, color=GRAY, ha="left", va="center")

# ── report box (purple), right, spanning primary+supporting ────────────────
box(101, 29, 25, 25, PURPLE, "report\nscreening score\n+ supporting detail", fs=13.2, lw=3.0)
arrow(93.7, 54, 100.3, 47.5)
arrow(93.7, 31.5, 100.3, 36)

fig.savefig("fig_architecture.png", dpi=300, bbox_inches="tight",
            facecolor="white")
print("written fig_architecture.png")
