"""
task_battery_probe.py -- does a multi-task battery beat picture description
alone? Delaware is the only cohort that can answer, because it is the only one
with healthy controls on more than one task.

=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-23 BEFORE execution.
=============================================================================

WHY THIS MATTERS TO THE DESIGN. Every screening decision in this project rests
on picture description. That was not an evidence-based choice: the Pitt corpus
has healthy controls on that task ONLY, so no other task could be used. The
deployed system nonetheless administers FOUR tasks, and the thesis currently
justifies that by clinical reasoning rather than by measurement.

Delaware administers five tasks to both classes. Three existing files
(single_task_auc.json, combined_task_auc.json, task_comparison_test.json) bear
on this, and all three carry "script: inline (code not committed)". More
importantly, THE COMPARISON THE DESIGN NEEDS IS NOT AMONG THEM: there is a
paired test of Cinderella against Cookie (+0.069 [-0.017, +0.157], p = 0.122),
but NO interval and NO paired test for the five-task battery against Cookie
alone. This script supplies it, from committed code.

DESIGN.
  Cohort     Delaware participants who completed ALL FIVE tasks, so that the
             two arms are evaluated on exactly the same people. A comparison
             across different participant sets would confound task content with
             sample composition, which is the flaw that makes the existing
             0.688-vs-0.575 figure uninterpretable as a paired claim.
  Arms       COOKIE  -- deployed 64 features from the cookie transcript only
             BATTERY -- the same 64 features computed on each of the five
                        tasks and concatenated
  Protocol   identical to the rest of the project: CalibratedClassifierCV
             (sigmoid, cv=3) over the committed soft-voting ensemble,
             StratifiedGroupKFold(5, shuffle=True, random_state=42), grouped by
             participant, seed 42.
  Test       paired participant-level bootstrap of the AUC difference,
             2000 resamples of PEOPLE, seed 42. The same resampled people are
             used for both arms in each replicate, which is what makes it
             paired.

CRITERIA, fixed in advance.
  BATTERY-BETTER      -- the 95% interval of (BATTERY - COOKIE) excludes zero
                         and is positive. The four-task design is supported by
                         measurement.
  OBSERVED-NOT-PROVEN -- point estimate positive, interval includes zero.
                         Report as observed, in the wording the project already
                         uses for Cinderella-vs-Cookie, and say plainly that the
                         battery design remains a clinical judgement.
  NO-BENEFIT          -- point estimate at or below zero. Report it. The
                         four-task design would then rest on the severity and
                         dissociation arguments alone, and the thesis must say so.

THE CONFOUND THAT MUST BE REPORTED WHATEVER THE RESULT. BATTERY has five times
the features of COOKIE on a few hundred recordings. Any advantage it shows is
an advantage of "five tasks with five times the features", not of task variety
holding dimensionality constant. This script does not separate the two and does
not claim to; the honest object of the test is the BATTERY AS A DESIGN, which is
what the pilot actually administers.

REPORT-AND-STOP. One seed, no re-draws, no third arm added afterwards.

GOVERNANCE. Delaware only. Lu is not read. The deployed model is not modified;
these are exploratory fits that are never applied to anything.

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
from sklearn.model_selection import StratifiedGroupKFold

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
STATE = os.path.join(os.path.expanduser("~"), "state", "batt")
os.makedirs(STATE, exist_ok=True)
os.chdir(REPO)
FEATS = json.load(open("results/summary/model_card.json"))["feature_order"]
TASKS = ["cookie", "cinderella", "cat", "rockwell", "sandwich"]


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


def build():
    """Participants with all five tasks; one row per participant per arm."""
    frames = {}
    for t in TASKS:
        X = pd.read_csv(f"results/delaware/{t}_features.csv")
        m = pd.read_csv(f"results/delaware/{t}_meta.csv")
        cols = [c for c in FEATS if c in X.columns]
        d = X[cols].copy()
        for c in FEATS:
            if c not in d.columns:
                d[c] = np.nan
        d = d[FEATS]
        d.columns = [f"{t}.{c}" for c in FEATS]
        d["participant_id"] = m.participant_id.values
        d["label"] = m.label.values
        # one recording per participant per task (first, deterministic)
        d = d.groupby("participant_id", as_index=False).first()
        frames[t] = d
    shared = set(frames[TASKS[0]].participant_id)
    for t in TASKS[1:]:
        shared &= set(frames[t].participant_id)
    shared = sorted(shared)
    merged = frames[TASKS[0]][frames[TASKS[0]].participant_id.isin(shared)].sort_values("participant_id")
    y = merged.label.values.astype(int)
    g = merged.participant_id.values
    cook = merged[[f"cookie.{c}" for c in FEATS]].values
    parts = [cook]
    for t in TASKS[1:]:
        f = frames[t][frames[t].participant_id.isin(shared)].sort_values("participant_id")
        parts.append(f[[f"{t}.{c}" for c in FEATS]].values)
    return cook, np.hstack(parts), y, g


def run(arm, fold):
    cook, batt, y, g = build()
    X = cook if arm == "cookie" else batt
    sp = list(StratifiedGroupKFold(5, shuffle=True, random_state=42).split(X, y, g))
    tr, te = sp[fold]
    fp = os.path.join(STATE, f"{arm}_f{fold}.npz")
    if os.path.exists(fp):
        print("cached", arm, fold); return
    m = model().fit(X[tr], y[tr])
    np.savez(fp, te=te, p=m.predict_proba(X[te])[:, 1])
    print(f"{arm} fold {fold} done  (n={len(y)}, features={X.shape[1]})")


def auc(y, s):
    r = pd.Series(s).rank().values
    n1 = (y == 1).sum(); n0 = (y == 0).sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def finish():
    cook, batt, y, g = build()
    oof = {}
    for arm in ("cookie", "battery"):
        v = np.zeros(len(y))
        for i in range(5):
            z = np.load(os.path.join(STATE, f"{arm}_f{i}.npz"))
            v[z["te"]] = z["p"]
        oof[arm] = v
    rng = np.random.default_rng(42)
    idx = {p: np.where(g == p)[0] for p in np.unique(g)}
    pids = np.array(list(idx))
    diffs, ac, ab = [], [], []
    for _ in range(2000):
        t = np.concatenate([idx[p] for p in rng.choice(pids, len(pids), True)])
        if len(np.unique(y[t])) < 2:
            continue
        a = auc(y[t], oof["cookie"][t]); b = auc(y[t], oof["battery"][t])
        ac.append(a); ab.append(b); diffs.append(b - a)
    d = np.array(diffs)
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    point = float(auc(y, oof["battery"]) - auc(y, oof["cookie"]))
    grade = ("BATTERY-BETTER" if lo > 0 else
             "NO-BENEFIT" if point <= 0 else "OBSERVED-NOT-PROVEN")
    out = {"generated": "2026-08-23",
           "preregistration": "criteria fixed in this script's docstring before execution",
           "cohort": {"n_participants_with_all_five_tasks": int(len(y)),
                      "n_impaired": int(y.sum()), "n_control": int((y == 0).sum())},
           "cookie": {"auc": round(float(auc(y, oof["cookie"])), 4),
                      "ci95": [round(float(np.percentile(ac, 2.5)), 4),
                               round(float(np.percentile(ac, 97.5)), 4)],
                      "n_features": int(cook.shape[1])},
           "battery": {"auc": round(float(auc(y, oof["battery"])), 4),
                       "ci95": [round(float(np.percentile(ab, 2.5)), 4),
                                round(float(np.percentile(ab, 97.5)), 4)],
                       "n_features": int(batt.shape[1])},
           "paired_difference_battery_minus_cookie": {
               "point": round(point, 4), "ci95": [round(lo, 4), round(hi, 4)],
               "p_two_sided_approx": round(float(2 * min((d <= 0).mean(), (d >= 0).mean())), 4)},
           "GRADE": grade,
           "confound_to_report": ("BATTERY carries five times the features of COOKIE. Any advantage "
                                  "is an advantage of the battery AS A DESIGN, not of task variety at "
                                  "matched dimensionality, and this test does not separate the two."),
           "governance": "Delaware only; Lu not read; exploratory fits never applied to anything"}
    json.dump(out, open("results/reconstruction/task_battery_probe.json", "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], int(sys.argv[3]))
    else:
        finish()
