#!/usr/bin/env python3
"""
lu_artefact_check.py -- provenance recovery for the Lu artefact figures
(approved recount, 26 August 2026).

WHY THIS EXISTS. Section 3.2.1 (and THESIS_PLAN section 3.2.2) reports that the
parenthesised-omission convention is effectively absent from the locked
external corpus: eight forms in the entire 54-file corpus, at 0.065 per 100
words among controls and 0.220 among the impaired. Those figures came from the
descriptive check of 23 August 2026, whose run was never committed. This
script recommits the measurement. It is descriptive in exactly the sense the
original declared: counting a text pattern is metadata inspection of the same
category as reading the header fields that supply ages and diagnoses. No model
is loaded, nothing is scored, no threshold moves, and the tombstone is not
touched.

CRITERIA -- fixed in this docstring before execution; grading mechanical;
report-and-stop. If a figure does not reproduce, the discrepancy is reported
and the prose corrected to the reproduced value; nothing is iterated.

  corpus       every .cha file under the Lu root (the build asserts 54 on
               disk; the aphasia exclusion F16 leaves 53 labelled recordings,
               labels from the committed results/lu/meta.csv)
  text         ChatTranscript.clean_text from the committed parser -- the text
               the feature extractors actually receive, where the form
               survives cleaning
  L1  word-attached forms  [a-zA-Z]+\\([a-zA-Z]+\\)  across all 54 files == 8
      (the bare parenthesised-letters count is also reported, descriptively)
  L2  control rate per 100 words   0.065  (+/- 0.02)
  L3  impaired rate per 100 words  0.220  (+/- 0.02)
      Rates are computed over the 53 labelled recordings two ways -- aggregate
      (100 x class matches / class words) and mean of per-recording rates --
      because the original did not record which it used; a claim is graded
      reproduced if either matches, with the matching definition named.

Output: results/reconstruction/lu_artefact_check.json
"""
import glob
import json
import os
import re

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

WORD_ATTACHED = re.compile(r"[a-zA-Z]+\(([a-zA-Z]+)\)")
BARE = re.compile(r"\(([a-zA-Z]+)\)")


def main():
    import csv
    lu_root = resolve("lu_root")
    files = sorted(glob.glob(os.path.join(lu_root, "**", "*.cha"), recursive=True))
    assert len(files) == 54, f"expected 54 .cha files, found {len(files)}"

    labels = {}
    with open(os.path.join(ROOT, "results/lu/meta.csv")) as fh:
        for row in csv.DictReader(fh):
            labels[row["file_id"]] = int(row["label"])
    assert len(labels) == 53

    total_attached = 0
    total_bare = 0
    per_class = {0: {"matches": 0, "words": 0, "rates": []},
                 1: {"matches": 0, "words": 0, "rates": []}}
    forms = []
    for f in files:
        t = parse_cha(f)
        txt = t.clean_text or ""
        m_att = WORD_ATTACHED.findall(txt)
        n_att = len(m_att)
        total_attached += n_att
        total_bare += len(BARE.findall(txt))
        if n_att:
            forms += [w for w in re.findall(r"[a-zA-Z]+\([a-zA-Z]+\)", txt)]
        fid = os.path.splitext(os.path.basename(f))[0]
        if fid in labels:
            y = labels[fid]
            w = max(len(txt.split()), 1)
            per_class[y]["matches"] += n_att
            per_class[y]["words"] += w
            per_class[y]["rates"].append(100.0 * n_att / w)

    agg = {y: 100.0 * d["matches"] / d["words"] for y, d in per_class.items()}
    mean = {y: sum(d["rates"]) / len(d["rates"]) for y, d in per_class.items()}

    def graded(name, claimed, tol, candidates):
        best_kind, best = min(candidates.items(), key=lambda kv: abs(kv[1] - claimed))
        return {"claimed": claimed, "tolerance": tol,
                "aggregate": candidates["aggregate"], "mean_of_recordings": candidates["mean_of_recordings"],
                "matching_definition": best_kind if abs(best - claimed) <= tol else None,
                "reproduced": bool(abs(best - claimed) <= tol)}

    g = {
        "L1_total_word_attached_forms": {
            "claimed": 8, "recomputed": total_attached,
            "reproduced": bool(total_attached == 8),
            "bare_parenthesised_letters_descriptive": total_bare,
            "forms_found": forms,
        },
        "L2_control_rate_per100": graded("L2", 0.065, 0.02,
            {"aggregate": agg[0], "mean_of_recordings": mean[0]}),
        "L3_impaired_rate_per100": graded("L3", 0.220, 0.02,
            {"aggregate": agg[1], "mean_of_recordings": mean[1]}),
    }
    n_ok = sum(1 for v in g.values() if v["reproduced"])
    out = {
        "script": "scripts/lu_artefact_check.py",
        "purpose": "provenance recovery: recommit the Lu artefact counts of THESIS_PLAN section 3.2.2 / chapter section 3.2.1 / Appendix G",
        "governance": "descriptive metadata inspection, declared as such in the original and here; no model loaded, nothing scored, tombstone untouched",
        "criteria": "fixed in the module docstring before execution; report-and-stop",
        "n_files": len(files), "n_labelled": len(labels),
        "graded": g, "n_reproduced": n_ok, "n_claims": 3,
        "VERDICT": "REPRODUCED" if n_ok == 3 else "PARTIAL",
    }
    dst = os.path.join(ROOT, "results/reconstruction/lu_artefact_check.json")
    json.dump(out, open(dst, "w"), indent=2)
    print("written:", dst)
    print("VERDICT:", out["VERDICT"], "(%d/3)" % n_ok)
    print("  L1 forms:", total_attached, "(claimed 8) | bare:", total_bare, "|", forms)
    print("  L2 control: agg %.4f mean %.4f (claimed 0.065)" % (agg[0], mean[0]))
    print("  L3 impaired: agg %.4f mean %.4f (claimed 0.220)" % (agg[1], mean[1]))


if __name__ == "__main__":
    main()
