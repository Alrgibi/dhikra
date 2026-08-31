#!/usr/bin/env python3
"""blanktail.py <pdf> <pages.json> -- fraction of the text area left blank at the foot of each unit's last page
(and every page with a >25% blank tail), measured on the rendered PDF within 9%..90% of page height."""
import sys, json, fitz
pdf = fitz.open(sys.argv[1]); pages = json.load(open(sys.argv[2]))
def blank_tail(pno):
    p = pdf[pno]; H = p.rect.height; W = p.rect.width
    top, bot = 0.09 * H, 0.90 * H
    pix = p.get_pixmap(dpi=36); import numpy as np
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    ink = (a.sum(axis=2) < 700).any(axis=1)
    y0 = int(top / H * pix.height); y1 = int(bot / H * pix.height)
    rows = ink[y0:y1]
    last = None
    for i in range(len(rows) - 1, -1, -1):
        if rows[i]: last = i; break
    if last is None: return 1.0
    return 1 - (last + 1) / len(rows)
units = {k: v for k, v in pages.items() if isinstance(v, list) and len(v) == 2}
tot = 0
for k, (a, b) in sorted(units.items(), key=lambda kv: kv[1][0]):
    bt = blank_tail(b - 1)
    print(f"{k:14s} pages {a:4d}–{b:4d} = {b-a+1:3d}  last-page blank tail {bt:4.2f}")
big = [(i + 1, round(blank_tail(i), 2)) for i in range(pdf.page_count) if blank_tail(i) > 0.25]
print("pages with >25% blank tail:", len(big), big)
print("total blank fraction (pages):", round(sum(blank_tail(i) for i in range(pdf.page_count)), 1))
