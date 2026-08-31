"""
pitt_subsample_probe.py -- is Delaware's within-cohort failure a SIZE effect?

=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-23 before execution. Criteria
fixed below; amendments appended to REGISTRATION HISTORY, never made silently.
=============================================================================

THE FINDING BEING INTERROGATED (results/reconstruction/cross_corpus_transfer.json)
    Pitt trained on Pitt, validated within Pitt      AUC 0.8137 [0.7677, 0.8588]
    Delaware trained on Delaware, within Delaware    AUC 0.5474 [0.4847, 0.6049]
    Pitt trained, evaluated on Delaware              AUC 0.6460 [0.5870, 0.7045]
A foreign model beats the native one, and the native one spans chance.
THESIS_PLAN sect 5.12.1 lists four candidate explanations: (1) MCI is
intrinsically harder, (2) training-set size, (3) MCI label instability, (4) task
administration. Only (2) is cheaply falsifiable, and this script tests it.

TEST. Subsample Pitt by PARTICIPANT to Delaware's recording count (439), then
run the identical within-cohort protocol. Delaware's 5-fold CV trains on roughly
351 recordings per fold; a Pitt subsample of 439 trains on the same. Repeat over
three subsampling seeds because a single draw is a lottery.

ARCHITECTURE, unchanged and verified: CalibratedClassifierCV(estimator=ens(),
method='sigmoid', cv=3) over the committed soft-voting ensemble, each member
behind median-impute -> StandardScaler. StratifiedGroupKFold(5, shuffle,
random_state=42), grouped by participant. Feature order from model_card.json.

CRITERIA, fixed in advance.
  SIZE-RULED-OUT   -- mean subsampled within-Pitt AUC >= 0.75, i.e. it stays
                      near full-Pitt performance. Training-set size does not
                      explain Delaware's 0.547, and explanations 1, 3 and 4
                      remain live.
  SIZE-EXPLAINS    -- mean subsampled within-Pitt AUC <= 0.62, i.e. it falls to
                      roughly Delaware's range. The MCI-difficulty reading
                      weakens considerably and must be reported as weakened.
  PARTIAL          -- anything between. Size contributes but does not account
                      for the gap; report the magnitude and stop.

REPORT-AND-STOP. Whichever band the result lands in is reported. No re-run with
different seeds, no change of subsample size, no second test.

GOVERNANCE. Lu is not read. The deployed model is not modified. These are
throwaway exploratory fits on development data, never applied to anything.

REGISTRATION HISTORY
  2026-08-23, AMENDMENT 2, BEFORE ANY RESULT WAS SEEN: subsampling seeds
  reduced from five to three. One cross-validation fold of the calibrated
  ensemble consumes almost the whole 45-second call budget, so five seeds is 25
  sequential calls and is not affordable against a 1 September deadline. Three
  seeds still guard against a single unlucky draw, which is the only purpose
  the repetition serves. The criteria bands (>= 0.75, <= 0.62) are UNCHANGED,
  and no result had been computed beyond a single fold of seed 11 when this was
  decided.

  2026-08-23, AMENDMENT 1, BEFORE ANY RESULT WAS SEEN: cross-validation folds
  are cached individually. One full 5-fold pass over the calibrated ensemble
  exceeds the Cowork VM's 45-second per-call process limit and was killed with
  no output. Harness change only -- identical subsample, identical splits from
  the identical StratifiedGroupKFold(5, shuffle, random_state=42), identical
  architecture. No criterion, size or seed was altered.
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
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
STATE = os.path.join(os.path.expanduser("~"), "state", "sub")
os.makedirs(STATE, exist_ok=True)
os.chdir(REPO)
FEATS = json.load(open("results/summary/model_card.json"))["feature_order"]
TARGET_N = 439          # Delaware's usable cookie recordings
SEEDS = [11, 22, 33]


def pipe(clf):
    return Pipeline([("i", SimpleImputer(strategy="median")),
                     ("s", StandardScaler()), ("c", clf)])


def ens():
    return VotingClassifier(estimators=[
        ("et", pipe(ExtraTreesClassifier(n_estimators=500, min_samples_leaf=3,
                                         class_weight="balanced", random_state=42, n_jobs=-1))),
        ("gb", pipe(GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                               learning_rate=0.05, random_state=42))),
        ("rf", pipe(RandomForestClassifier(n_estimators=500, min_samples_leaf=3,
                                           class_weight="balanced", random_state=42, n_jobs=-1))),
    ], voting="soft")


def model():
    return CalibratedClassifierCV(estimator=ens(), method="sigmoid", cv=3)


def within(X, y, g, seed, fold=None):
    """Per-fold caching: the Cowork VM kills every process at 45 s, and one
    full 5-fold pass over the calibrated ensemble exceeds that."""
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    splits = list(cv.split(X, y, g))
    for i, (tr, te) in enumerate(splits):
        if fold is not None and i != fold:
            continue
        fp = os.path.join(STATE, f"s{seed}_f{i}.npz")
        if os.path.exists(fp):
            continue
        m = model().fit(X[tr], y[tr])
        np.savez(fp, te=te, p=m.predict_proba(X[te])[:, 1])
        print(f"  seed {seed} fold {i} done")
    done = [os.path.join(STATE, f"s{seed}_f{i}.npz") for i in range(5)]
    if not all(os.path.exists(f) for f in done):
        return None
    oof = np.zeros(len(y))
    for f in done:
        z = np.load(f); oof[z["te"]] = z["p"]
    return float(roc_auc_score(y, oof))


def subsample(seed):
    X = pd.read_csv("results/pitt_cookie/features.csv")[FEATS].values
    m = pd.read_csv("results/pitt_cookie/meta.csv")
    y = m.label.values.astype(int); g = m.participant_id.values
    rng = np.random.default_rng(seed)
    pids = rng.permutation(np.unique(g))
    keep, n = [], 0
    for p in pids:
        idx = np.where(g == p)[0]
        if n + len(idx) > TARGET_N:
            continue
        keep.append(idx); n += len(idx)
        if n >= TARGET_N:
            break
    k = np.concatenate(keep)
    return X[k], y[k], g[k]


def run(seed, fold=None):
    dest = os.path.join(STATE, f"s{seed}.json")
    if os.path.exists(dest):
        print("cached", seed); return
    Xs, ys, gs = subsample(seed)
    a = within(Xs, ys, gs, seed, fold)
    if a is None:
        print(f"seed {seed}: folds still pending"); return
    json.dump({"seed": seed, "n": int(len(ys)), "n_participants": int(len(np.unique(gs))),
               "prevalence": float(ys.mean()), "auc": round(a, 4)}, open(dest, "w"))
    print(f"seed {seed}: n={len(ys)} auc={a:.4f}")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else None)
    else:
        rows = [json.load(open(os.path.join(STATE, f"s{s}.json"))) for s in SEEDS]
        aucs = [r["auc"] for r in rows]
        mean = float(np.mean(aucs))
        grade = ("SIZE-RULED-OUT" if mean >= 0.75 else
                 "SIZE-EXPLAINS" if mean <= 0.62 else "PARTIAL")
        out = {"generated": "2026-08-23", "question": "does training-set size explain Delaware's within-cohort 0.547?",
               "preregistration": "criteria fixed in this script's docstring before execution",
               "reference": {"pitt_within_full_548": 0.8137, "delaware_within_439": 0.5474,
                             "pitt_trained_on_delaware": 0.6460},
               "subsamples": rows, "mean_auc": round(mean, 4),
               "range": [round(min(aucs), 4), round(max(aucs), 4)],
               "GRADE": grade}
        json.dump(out, open("results/reconstruction/pitt_subsample_probe.json", "w"), indent=2)
        print(json.dumps(out, indent=2))
