#!/usr/bin/env python3
"""make_qr.py -- regenerate docs/figures/fig_repo_qr.png from build_config.json's repo_url and record its size."""
import json, os, qrcode
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, "build_config.json")))
url = cfg["repo_url"]
FIGDIR = "/home/claude/work/src/docs/figures"
out = os.path.join(FIGDIR, "fig_repo_qr.png")
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
q.add_data(url); q.make(fit=True)
img = q.make_image(fill_color="black", back_color="white").convert("RGB")
img.save(out)
sizes_path = os.path.join(HERE, "figsizes.json")
sizes = json.load(open(sizes_path))
sizes["fig_repo_qr.png"] = list(Image.open(out).size)
json.dump(sizes, open(sizes_path, "w"), indent=1)
print("QR written for", url, Image.open(out).size)
