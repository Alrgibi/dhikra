"""
build_delaware.py
-----------------
Builds a feature matrix for every Delaware task and tests the question that
the Pitt corpus could not answer.

THE QUESTION PITT COULD NOT ANSWER
Pitt recorded verbal fluency, story recall and sentence construction from
patients only. With no healthy comparison group, those tasks could establish
how severe someone's impairment was, but never whether impairment was present.
Every screening decision in this project therefore rested on a single task.

Delaware ran its full protocol on both groups, so each task can now be tested
directly: does it separate impaired speakers from healthy ones, and does
combining tasks beat the best single task?

A HARDER AND MORE USEFUL TARGET
Delaware's impaired group is MCI -- mild cognitive impairment, the stage before
dementia. Pitt's was largely established dementia. Detecting MCI is
substantially harder because the language changes are subtler, so lower
accuracy here is expected. It is also far more valuable, because MCI is where
intervention is still possible, and it is precisely the population a screening
instrument exists to find.

TASKS
  cookie      -- Cookie Theft picture description (directly comparable to Pitt)
  cinderella  -- narrative retelling of a familiar story
  cat         -- picture description, cat-rescue scene
  rockwell    -- picture description, Norman Rockwell painting
  sandwich    -- procedural discourse, describing how to make a sandwich
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd

from dhikra.multitask_parser import collect_task
from dhikra.linguistic_features import extract_linguistic_features
from dhikra.information_units import extract_information_units
from dhikra.semantic_features import extract_semantic_features

# Path comes from corpus_paths.json (see src/dhikra/paths.py). The original
# hardcoded sandbox path /home/claude/corpora/Delaware__1 died with that
# environment (de-hardcoded 2026-08-20).
from dhikra.paths import resolve
CORPUS = resolve("delaware_root")
OUT = "results/delaware"
TASKS = ["cookie", "cinderella", "cat", "rockwell", "sandwich"]


def build_task(task: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, metas = [], []
    for t in collect_task(CORPUS, task):
        if t.group not in ("Control", "MCI"):
            continue
        text = t.clean_text
        feats = {}
        for k, v in extract_linguistic_features(text).items():
            feats[f"ling.{k}"] = v
        feats.update(t.disfluency_features())
        # information units are defined for the Cookie Theft scene only; on
        # any other stimulus the checklist is meaningless, so it is omitted
        # rather than producing counts that describe nothing
        if task == "cookie":
            feats.update(extract_information_units(text, scene="kitchen"))
        feats.update(extract_semantic_features(text))
        rows.append(feats)
        pid = t.file_id.split("|")[0].split("-")[0]
        metas.append({"file_id": t.file_id, "participant_id": pid,
                      "age": t.age, "sex": t.sex, "group": t.group,
                      "label": 1 if t.group == "MCI" else 0,
                      "n_words": len(text.split()), "task": task})
    return pd.DataFrame(rows), pd.DataFrame(metas)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("=" * 74)
    print("BUILDING DELAWARE TASK DATASETS")
    print("=" * 74)
    # COUNT ASSERTION (added 2026-08-20): the locked development set used
    # 455 Delaware .cha files yielding 439 usable cookie transcripts
    # (CURRENT_development_stats.json n=439). A different count means the
    # corpus on disk or the exclusion logic has drifted -- stop, don't build.
    n_cha = len(glob.glob(os.path.join(CORPUS, "**", "*.cha"), recursive=True))
    assert n_cha == 455, (
        f"Delaware corpus drift: expected 455 .cha files, found {n_cha} "
        f"under {CORPUS}")
    for task in TASKS:
        X, meta = build_task(task)
        if len(X) == 0:
            print(f"  {task}: no usable data")
            continue
        if task == "cookie":
            assert len(X) == 439, (
                f"Delaware cookie drift: expected 439 usable transcripts "
                f"(locked n), got {len(X)}")
        X.to_csv(f"{OUT}/{task}_features.csv", index=False)
        meta.to_csv(f"{OUT}/{task}_meta.csv", index=False)
        n_ctrl = int((meta.label == 0).sum())
        n_mci = int((meta.label == 1).sum())
        print(f"  {task:12s} {len(X):4d} transcripts  "
              f"({n_ctrl} control / {n_mci} MCI)  {X.shape[1]} features  "
              f"median {meta.n_words.median():.0f} words")
    with open(f"{OUT}/PROVENANCE.json", "w") as fh:
        json.dump({
            "dataset": "Delaware (DementiaBank), Control+MCI, all 5 tasks",
            "n_cha_files": 455, "cookie_rows": 439,
            "lock_state": "post-Lu-lock; Lu untouched by this script",
            "source_corpus": CORPUS,
            "script": "scripts/build_delaware.py",
            "generated": __import__("datetime").date.today().isoformat(),
        }, fh, indent=2)
    print(f"\nwritten to {OUT}/")


if __name__ == "__main__":
    main()
