"""
make_fig_stimuli.py  --  Figure 19, the three picture stimuli.

RUN LOCATION: this script renders SVG, which needs cairosvg + matplotlib.
Those are NOT in the pinned device environment ($HOME/dhenv), so it is run in
the analysis container against copies of app/static/*.svg and the PNG is
committed back to docs/figures/. No corpus data is involved.

REGENERATE WHENEVER ANY STIMULUS SVG CHANGES. It last changed on 2026-08-26,
when the kitchen scene gained a curtain and a dish cloth (both were in the
frozen scoring key but absent from the picture) and the woman was moved behind
the counter so that the tap, the running water and the overflow are visible.
"""
import cairosvg, io, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

PANELS = [("scene_kitchen.svg",   "Kitchen  — the calibrated stimulus"),
          ("scene_courtyard.svg", "Courtyard  — matched, not calibrated"),
          ("scene_market.svg",    "Market  — matched, not calibrated")]
W = 1420
BG = "#fdfcf7"

imgs = []
for f, _ in PANELS:
    png = cairosvg.svg2png(url=f, output_width=W)
    imgs.append(Image.open(io.BytesIO(png)).convert("RGB"))

plt.rcParams["font.family"] = "serif"
fig, axes = plt.subplots(len(PANELS), 1, figsize=(W / 100.0, 21.2), dpi=100)
fig.patch.set_facecolor("white")
for ax, im, (_, cap) in zip(axes, imgs, PANELS):
    ax.imshow(im)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#b9b4a6"); sp.set_linewidth(1.0)
    ax.set_xlabel(cap, fontsize=17, loc="left", labelpad=10, color="#1f2d3a")
fig.subplots_adjust(left=0.012, right=0.988, top=0.994, bottom=0.006, hspace=0.10)
fig.savefig("fig_stimuli.png", dpi=100, facecolor="white")
print("written fig_stimuli.png")
