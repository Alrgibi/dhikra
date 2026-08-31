"""
leakage_demonstration.py -- what does the evaluation shortcut buy?

=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-23 BEFORE execution.
=============================================================================

WHY. Published results on the Pitt corpus are frequently obtained with
STRATIFIED cross-validation on a corpus where the same participants recur
across successive annual visits, which allows one person's recordings to appear
in both the training and the test fold. This project used STRATIFIED GROUPED
folds throughout, so that every recording from one participant is confined to a
single fold. The thesis argues that the two protocols measure different things.
This script replaces that argument with a measurement ON THIS PROJECT'S OWN
DATA AND MODEL.

THIS IS A LEAKAGE DEMONSTRATION AND NOT A COMPETING RESULT. The number produced
by the ungrouped arm is what the deployed pipeline reports under a protocol this
project rejects. It is INFLATED BY CONSTRUCTION. It must never be quoted as a
performance figure, must never appear in a headline table, and must always
carry the word "ungrouped". The deployed model, the deployed threshold and every
locked result are untouched.

DESIGN. One cohort (Pitt cookie, 548 recordings, 290 participants), one feature
set (the deployed 64), one architecture (CalibratedClassifierCV(sigmoid, cv=3)
over the committed soft-voting ensemble), one seed (42). The ONLY thing that
differs between the two arms is the cross-validation splitter:
    GROUPED    StratifiedGroupKFold(5, shuffle=True, random_state=42)
    UNGROUPED  StratifiedKFold(5, shuffle=True, random_state=42)

The grouped arm doubles as a reproduction check: it should land near the
committed within-Pitt figure of 0.8137 (cross_corpus_transfer.json, "Pitt
within"). Both arms are run in the same session so the comparison is internal.

MECHANISM. Also recorded: the proportion of test-fold recordings whose
participant also appears in the same fold's training set. Under grouped folds
this is 0 by construction. Under ungrouped folds it is the exposure that
produces the inflation, and reporting it turns the finding from an assertion
into an accounting.

CRITERIA, fixed in advance.
  DEMONSTRATED  -- ungrouped AUC exceeds grouped AUC by at least 0.02.
  NOT-DEMONSTRATED -- difference below 0.02, in which case the thesis must
      soften its protocol argument accordingly and say that on this corpus the
      shortcut buys little. Report either way; this is not a result the project
      is entitled to assume.
  The grouped arm must land within 0.02 of 0.8137 or the run is void, because
  it would mean the harness is not reproducing the committed protocol.

REPORT-AND-STOP. One seed, one run, no re-draws.

GOVERNANCE. Lu is not read. Nothing is written to results/summary. The deployed
model is not modified.

REGISTRATION HISTORY
  (none)
"""
import json, os, sys
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (ExtraTreesClassifier, GradientBoostingClassifier,
                              RandomForestClassifier, VotingClassifier)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.metrics import roc_auc_score

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
STATE = os.path.join(os.path.expanduser("~"), "state", "leak")
os.makedirs(STATE, exist_ok=True)
os.chdir(REPO)
FEATS = json.load(open("results/summary/model_card.json"))["feature_order"]
GROUPED_REFERENCE = 0.8137


def pipe(c):
    return Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler()), ("c", c)])


def model():
    ens = VotingClassifier(estimators=[
        ("et", pipe(ExtraTreesClassifier(500, min_samples_leaf=3, class_weight="balanced",
                                         random_state=42, n_jobs=-1))),
        ("gb", pipe(GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                               learning_rate=0.05, random_state=42))),
        ("rf", pipe(RandomForestClassifier(500, min_samples_leaf=3, class_weight="balanced",
                                           random_state=42, n_jobs=-1))),
    ], voting="soft")
    return CalibratedClassifierCV(estimator=ens, method="sigmoid", cv=3)


def data():
    X = pd.read_csv("results/pitt_cookie/features.csv")[FEATS].values
    m = pd.read_csv("results/pitt_cookie/meta.csv")
    return X, m.label.values.astype(int), m.participant_id.values


def splits(arm, y, g):
    if arm == "grouped":
        return list(StratifiedGroupKFold(5, shuffle=True, random_state=42).split(np.zeros(len(y)), y, g))
    return list(StratifiedKFold(5, shuffle=True, random_state=42).split(np.zeros(len(y)), y))


def run(arm, fold):
    X, y, g = data()
    sp = splits(arm, y, g)
    tr, te = sp[fold]
    fp = os.path.join(STATE, f"{arm}_f{fold}.npz")
    if os.path.exists(fp):
        print("cached", arm, fold); return
    seen = np.isin(g[te], g[tr]).mean()          # the mechanism
    m = model().fit(X[tr], y[tr])
    np.savez(fp, te=te, p=m.predict_proba(X[te])[:, 1], seen=seen)
    print(f"{arm} fold {fold}: {seen:.1%} of test recordings share a participant with training")


def finish():
    X, y, g = data()
    out = {"generated": "2026-08-23",
           "WARNING": "the ungrouped figure is INFLATED BY CONSTRUCTION and is not a performance "
                      "result. Never quote it without the word 'ungrouped'.",
           "preregistration": "criteria fixed in this script's docstring before execution",
           "cohort": {"n_recordings": int(len(y)), "n_participants": int(len(np.unique(g))),
                      "recordings_per_participant": round(len(y) / len(np.unique(g)), 2)},
           "arms": {}}
    for arm in ("grouped", "ungrouped"):
        oof = np.zeros(len(y)); seen = []
        for i in range(5):
            z = np.load(os.path.join(STATE, f"{arm}_f{i}.npz"))
            oof[z["te"]] = z["p"]; seen.append(float(z["seen"]))
        out["arms"][arm] = {"auc": round(float(roc_auc_score(y, oof)), 4),
                            "test_recordings_sharing_a_participant_with_training":
                                round(float(np.mean(seen)), 4)}
    gr, un = out["arms"]["grouped"]["auc"], out["arms"]["ungrouped"]["auc"]
    out["difference_ungrouped_minus_grouped"] = round(un - gr, 4)
    out["reproduction_check"] = {"grouped_arm": gr, "committed_within_pitt": GROUPED_REFERENCE,
                                 "delta": round(gr - GROUPED_REFERENCE, 4),
                                 "void_if_abs_delta_over_0.02": abs(gr - GROUPED_REFERENCE) > 0.02}
    out["GRADE"] = ("VOID -- grouped arm did not reproduce the committed protocol"
                    if abs(gr - GROUPED_REFERENCE) > 0.02 else
                    "DEMONSTRATED" if (un - gr) >= 0.02 else "NOT-DEMONSTRATED")
    json.dump(out, open("results/reconstruction/leakage_demonstration.json", "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], int(sys.argv[3]))
    else:
        finish()
