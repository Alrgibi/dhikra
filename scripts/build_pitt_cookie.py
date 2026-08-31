"""
build_pitt_cookie.py
--------------------
Creates the cookie-task-only Pitt subset, and optionally its feature matrix.

WHY THIS SCRIPT EXISTS
The original development environment held a hand-assembled folder
/home/claude/pitt_cookie containing only the Cookie Theft files from both
groups. analyze_pitt.py and everything downstream assumed it existed, but no
script created it -- it was made inline and the recipe was lost with the
sandbox (HANDOFF §5, FILE_MAP: "inline"). Pointing the pipeline at the Pitt
ROOT instead would silently ingest all four tasks -- including the
patient-only fluency/recall/sentence recordings -- and build a wrong dataset
without erroring. This script makes the recipe explicit, and refuses to
proceed if the counts drift from the locked expectations.

COUNT ASSERTIONS (added 2026-08-20, per the reconstruction plan)
  on disk : 243 Control/cookie + 309 Dementia/cookie = 552 .cha files
  usable  : 548 recordings after exclusions (label None -- e.g. the 'Other'
            diagnosis group -- or fewer than 10 words), matching
            CURRENT_development_stats.json (pitt_dementia n=548).
A failed assertion means the corpus on disk or the exclusion logic no longer
matches the locked numbers; the build stops rather than producing a silently
different dataset.

Usage
    python scripts/build_pitt_cookie.py             # create/verify the subset
    python scripts/build_pitt_cookie.py --features  # also build features.csv
"""
import argparse
import datetime
import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dhikra.paths import resolve

OUT = "results/pitt_cookie"


def build_subset() -> str:
    src_root = resolve("pitt_root")
    dest = resolve("pitt_cookie", must_exist=False)
    expected = {"Control": 243, "Dementia": 309}

    for grp, n_exp in expected.items():
        src_dir = os.path.join(src_root, grp, "cookie")
        files = sorted(glob.glob(os.path.join(src_dir, "*.cha")))
        assert len(files) == n_exp, (
            f"Pitt corpus drift: expected {n_exp} .cha in {src_dir}, "
            f"found {len(files)}")
        os.makedirs(os.path.join(dest, grp), exist_ok=True)
        copied = kept = 0
        for f in files:
            tgt = os.path.join(dest, grp, os.path.basename(f))
            if os.path.exists(tgt) and os.path.getsize(tgt) == os.path.getsize(f):
                kept += 1
                continue
            shutil.copy2(f, tgt)
            copied += 1
        print(f"  {grp}: {len(files)} files ({copied} copied, {kept} already present)")

    total = len(glob.glob(os.path.join(dest, "**", "*.cha"), recursive=True))
    assert total == 552, f"subset drift: expected 552 .cha files, found {total}"
    print(f"  subset verified: 552 cookie transcripts at {dest}")
    return dest


def build_features(subset_dir: str) -> None:
    from dhikra.corpus import build_dataset, save_dataset

    X, y, meta = build_dataset(subset_dir, use_audio=False, verbose=False)
    n_parsed = len(X)

    # exclusion 2: fewer than 10 words (model_card.json, "exclusions")
    assert "ling.word_count" in X, "ling.word_count missing from feature matrix"
    keep = (X["ling.word_count"] >= 10).values
    X2 = X[keep].reset_index(drop=True)
    y2 = y[keep]
    meta2 = meta[keep].reset_index(drop=True)

    print(f"  parsed rows       : {n_parsed}  (label-None / empty already dropped "
          f"by build_dataset: {552 - n_parsed})")
    print(f"  <10-word excluded : {int((~keep).sum())}")
    print(f"  final rows        : {len(X2)}")
    assert len(X2) == 548, (
        f"Pitt cookie drift: expected 548 usable recordings (locked n), "
        f"got {len(X2)}. Breakdown above -- do NOT weaken this assertion; "
        f"find out what changed.")

    os.makedirs(OUT, exist_ok=True)
    save_dataset(X2, y2, meta2, OUT)
    with open(os.path.join(OUT, "PROVENANCE.json"), "w") as fh:
        json.dump({
            "dataset": "Pitt cookie task, Control+Dementia (DementiaBank)",
            "n_cha_files": 552,
            "n_usable": 548,
            "exclusions": "label None (e.g. 'Other' dx) or <10 words",
            "lock_state": "post-Lu-lock; Lu untouched by this script",
            "source_corpus": subset_dir,
            "script": "scripts/build_pitt_cookie.py",
            "generated": datetime.date.today().isoformat(),
        }, fh, indent=2)
    print(f"  features + meta + PROVENANCE written to {OUT}/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", action="store_true",
                    help="also build features.csv/meta.csv into results/pitt_cookie/")
    args = ap.parse_args()

    print("=" * 74)
    print("PITT COOKIE SUBSET")
    print("=" * 74)
    subset = build_subset()
    if args.features:
        build_features(subset)


if __name__ == "__main__":
    main()
