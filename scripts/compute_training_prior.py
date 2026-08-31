"""
compute_training_prior.py
-------------------------
Derives TRAINING_PRIOR -- the class prevalence of the development set -- so
the constant in risk_adjustment.py is traceable to a script instead of to an
inline calculation.

HISTORY
  v1: 0.50 assumed          (corrected after external review --
                             results/summary/review_corrections.json)
  v2: 0.4721 = 491/1040     (measured on the PRE-LOCK pool including Lu;
                             the known inconsistency of HANDOFF §4)
  v3: this script           (post-lock 987-recording development set)

WHY IT MATTERS
The risk-adjustment chain divides the model's output odds by the training
prevalence to obtain a likelihood ratio (src/dhikra/risk_adjustment.py).
Using the pre-lock value leaves part of the development prior inside the LR
and double-counts prior risk.

This script only DERIVES and RECORDS the value. Updating the constant in
src/dhikra/risk_adjustment.py is a separate, explicitly-approved edit.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd

OUT = "results/reconstruction"


def main():
    mp = pd.read_csv("results/pitt_cookie/meta.csv")
    md = pd.read_csv("results/delaware/cookie_meta.csv")
    assert len(mp) == 548 and len(md) == 439, (
        f"expected the locked 548 + 439 rows, got {len(mp)} + {len(md)} -- "
        f"rebuild with build_pitt_cookie.py / build_delaware.py first")
    n_imp = int(mp.label.sum() + md.label.sum())
    n = len(mp) + len(md)
    prior = n_imp / n
    print(f"impaired {n_imp} of {n}  ->  TRAINING_PRIOR = {prior:.6f}")
    print("pre-lock constant in risk_adjustment.py: 0.4721 (491/1040, incl. Lu)")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "training_prior.json"), "w") as fh:
        json.dump({
            "training_prior_987": prior,
            "n_impaired": n_imp,
            "n_total": n,
            "supersedes": {"value": 0.4721,
                           "basis": "491/1040, pre-lock pool including Lu"},
            "_provenance": {
                "dataset": "Pitt cookie (548) + Delaware cookie (439), Lu locked out",
                "lock_state": "post-Lu-lock",
                "script": "scripts/compute_training_prior.py",
                "generated": datetime.date.today().isoformat(),
            },
        }, fh, indent=2)
    print(f"written to {OUT}/training_prior.json")


if __name__ == "__main__":
    main()
