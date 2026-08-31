#!/usr/bin/env python3
"""
pitt_filled_pause_count.py -- provenance recovery for the raw filled-pause
figures (approved recount, 26 August 2026).

WHY THIS EXISTS. THESIS_PLAN section 3.2.3 reports that although the two
deployed filler features are inert, the parser captures filled pauses
separately: n_filled_pauses present in 81.8% of transcripts, 1,881 tokens.
feature_health_audit.py reproduced the 81.8% share from the committed rate
column but could not confirm the raw token count by proxy (its
per100 x word-count reconstruction gave 1,637, consistent with the parser
counting on a different denominator). This script recommits the raw count by
running the committed parser itself over the 548 Pittsburgh cookie
transcripts -- the same measurement the original audit made. Descriptive:
counting parser tokens is metadata inspection; no model is loaded and nothing
is scored.

CRITERIA -- fixed in this docstring before execution; grading mechanical;
report-and-stop.

  files  the .cha files under the pitt_cookie root whose file_id appears in
         the committed results/pitt_cookie/meta.csv (asserted 548)
  P1  total ChatTranscript.n_filled_pauses over the 548     1,881  (+/- 1%)
  P2  share of transcripts with n_filled_pauses > 0         81.8%  (+/- 0.5 pp)

Output: results/reconstruction/pitt_filled_pause_count.json
"""
import csv
import glob
import json
import os

import importlib.util

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def _load(name):
    """Load a dhikra module directly by path, bypassing the package __init__
    (which imports acoustic_features -> librosa, absent from the pinned env)."""
    import sys
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(ROOT, "src", "dhikra", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod   # dataclasses resolve types via sys.modules
    spec.loader.exec_module(mod)
    return mod

resolve = _load("paths").resolve
parse_cha = _load("chat_parser").parse_cha


def main():
    with open(os.path.join(ROOT, "results/pitt_cookie/meta.csv")) as fh:
        ids = {row["file_id"] for row in csv.DictReader(fh)}
    assert len(ids) == 548

    root = resolve("pitt_cookie")
    files = {os.path.splitext(os.path.basename(f))[0]: f
             for f in glob.glob(os.path.join(root, "**", "*.cha"), recursive=True)}
    hit = [files[i] for i in ids if i in files]
    assert len(hit) == 548, f"matched {len(hit)} of 548 meta file_ids on disk"

    total = 0
    nonzero = 0
    for f in hit:
        n = parse_cha(f).n_filled_pauses
        total += n
        nonzero += 1 if n > 0 else 0
    share = 100.0 * nonzero / 548

    g = {
        "P1_total_tokens": {"claimed": 1881, "recomputed": total,
                            "tolerance": "1%",
                            "reproduced": bool(abs(total - 1881) <= 18.81)},
        "P2_nonzero_share_pct": {"claimed": 81.8, "recomputed": share,
                                 "tolerance": "0.5 pp",
                                 "reproduced": bool(abs(share - 81.8) <= 0.5)},
    }
    n_ok = sum(1 for v in g.values() if v["reproduced"])
    out = {
        "script": "scripts/pitt_filled_pause_count.py",
        "purpose": "provenance recovery: recommit the raw filled-pause count of THESIS_PLAN section 3.2.3 by running the committed parser over the 548 Pittsburgh cookie transcripts",
        "governance": "descriptive; parser token counting only, no model, nothing scored",
        "criteria": "fixed in the module docstring before execution; report-and-stop",
        "n_files": len(hit),
        "graded": g, "n_reproduced": n_ok, "n_claims": 2,
        "VERDICT": "REPRODUCED" if n_ok == 2 else "PARTIAL",
    }
    dst = os.path.join(ROOT, "results/reconstruction/pitt_filled_pause_count.json")
    json.dump(out, open(dst, "w"), indent=2)
    print("written:", dst)
    print("VERDICT:", out["VERDICT"], "(%d/2)" % n_ok)
    print("  P1 tokens:", total, "(claimed 1881)")
    print("  P2 share: %.2f%% (claimed 81.8%%)" % share)


if __name__ == "__main__":
    main()
