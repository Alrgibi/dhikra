"""
early_detection.py
------------------
The prospective test: does speech recorded in 2011 predict a cognitive
diagnosis made in 2020, nine years later?

WHY THIS IS A DIFFERENT AND STRONGER QUESTION
Every result obtained from the Pitt corpus is CONCURRENT -- the recording and
the diagnosis come from the same period, so the model is recognising
impairment that already exists. That is useful, but it is detection, not early
detection.

The Wisconsin Longitudinal Study separates the two by nine years. Every
participant here was living in the community in 2011, undiagnosed, and
described the same picture. Their cognitive status was assessed clinically in
2020. So a model trained on the 2011 speech is being asked to identify people
who had not yet been diagnosed and in most cases had no complaint at all.

Performance will necessarily be LOWER than concurrent detection, and that is
expected rather than disappointing: most of the signal a concurrent model uses
simply is not present yet. What matters is whether it exceeds chance, because
anything above chance means the speech carried information about a diagnosis
that was still nine years away.

ANALYSES
 1. Prospective prediction of 2020 status from 2011 speech.
 2. The same restricted to the consensus-diagnosed subgroup, which has the
    most reliable labels.
 3. Which individual measures separate future cases from future controls.
 4. Whether adding WLS controls to the Pitt training set improves specificity,
    which is the weakest metric of the concurrent model.
"""
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (ExtraTreesClassifier, RandomForestClassifier,
                              GradientBoostingClassifier, VotingClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import roc_auc_score, confusion_matrix

WLS = "results/wls"
PITT = "results/pitt_cookie"
BANNER = "=" * 78


def pipe(clf):
    return Pipeline([("i", SimpleImputer(strategy="median")),
                     ("s", StandardScaler()), ("c", clf)])


def ens():
    return VotingClassifier([
        ("et", pipe(ExtraTreesClassifier(n_estimators=500, min_samples_leaf=3,
                                         class_weight="balanced",
                                         random_state=42, n_jobs=-1))),
        ("gb", pipe(GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                               learning_rate=0.05,
                                               random_state=42))),
        ("rf", pipe(RandomForestClassifier(n_estimators=500, min_samples_leaf=3,
                                           class_weight="balanced",
                                           random_state=42, n_jobs=-1))),
    ], voting="soft")


def auc_cv(X, y, clf=None, seeds=(42, 7, 123)):
    clf = clf or ens()
    out = []
    for s in seeds:
        cv = StratifiedKFold(5, shuffle=True, random_state=s)
        out.append(cross_val_score(clf, X, y, cv=cv, scoring="roc_auc",
                                   n_jobs=-1).mean())
    return float(np.mean(out)), float(np.std(out))


def main():
    Xw = pd.read_csv(f"{WLS}/features.csv")
    mw = pd.read_csv(f"{WLS}/meta.csv")

    # ── 1. prospective prediction ──────────────────────────────────────────
    print(BANNER)
    print("1. PROSPECTIVE: 2011 speech -> 2020 diagnosis (nine years later)")
    print(BANNER)
    have = mw.label.notna()
    Xp, yp, mp = Xw[have].reset_index(drop=True), mw.loc[have, "label"].astype(int).values, mw[have].reset_index(drop=True)
    print(f"  participants        : {len(Xp)}")
    print(f"  normal in 2020      : {int((yp==0).sum())}")
    print(f"  impaired/dementia   : {int((yp==1).sum())}")

    m, s = auc_cv(Xp, yp)
    print(f"\n  AUC = {m:.3f} +/- {s:.3f}")
    if m > 0.60:
        print("  -> speech in 2011 carried real information about a diagnosis")
        print("     that was still nine years away.")
    elif m > 0.55:
        print("  -> weak but above-chance prospective signal.")
    else:
        print("  -> essentially no prospective signal in these features.")

    # age is a confound here too: older people in 2011 are likelier to be
    # impaired by 2020, so its contribution is measured separately
    if "age_2020" in mp:
        age = mp[["age_2020"]].fillna(mp.age_2020.median())
        am, _ = auc_cv(age, yp, pipe(LogisticRegression(max_iter=5000,
                                                        class_weight="balanced")))
        print(f"  age alone           : AUC {am:.3f}")
        Xa = Xp.copy()
        Xa["age"] = mp.age_2020.values
        cm, _ = auc_cv(Xa, yp)
        print(f"  speech + age        : AUC {cm:.3f}")

    # ── 2. dementia only, the cleanest signal ──────────────────────────────
    print("\n" + BANNER)
    print("2. PROSPECTIVE, dementia versus normal only")
    print(BANNER)
    sub = mw.npv_name.isin(["normal", "dementia"])
    Xd = Xw[sub].reset_index(drop=True)
    yd = (mw.loc[sub, "npv_name"] == "dementia").astype(int).values
    print(f"  n = {len(Xd)}  ({int((yd==1).sum())} developed dementia)")
    dm, ds = auc_cv(Xd, yd)
    print(f"  AUC = {dm:.3f} +/- {ds:.3f}")

    # ── 3. which measures foreshadow decline ───────────────────────────────
    print("\n" + BANNER)
    print("3. WHICH 2011 MEASURES DIFFERED IN THOSE LATER DIAGNOSED")
    print(BANNER)
    rows = []
    for f in Xp.columns:
        a = Xp.loc[yp == 0, f].dropna()
        b = Xp.loc[yp == 1, f].dropna()
        if len(a) < 30 or len(b) < 20 or a.std() == 0 or b.std() == 0:
            continue
        t, p = stats.ttest_ind(a, b, equal_var=False)
        d = (b.mean() - a.mean()) / np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
        rows.append((f, a.mean(), b.mean(), d, p))
    gd = pd.DataFrame(rows, columns=["feature", "normal_2020", "impaired_2020",
                                     "cohens_d", "p_value"])
    gd["abs"] = gd.cohens_d.abs()
    gd = gd.sort_values("abs", ascending=False).drop(columns="abs")
    print(gd.head(12).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    gd.to_csv(f"{WLS}/prospective_group_comparison.csv", index=False)
    sig = int((gd.p_value < 0.05).sum())
    print(f"\n  {sig} of {len(gd)} measures differed significantly, nine years "
          "before diagnosis")

    # ── 4. do WLS controls fix Pitt's specificity? ─────────────────────────
    print("\n" + BANNER)
    print("4. ADDING WLS CONTROLS TO THE PITT MODEL")
    print(BANNER)
    Xpitt = pd.read_csv(f"{PITT}/features.csv")
    mpitt = pd.read_csv(f"{PITT}/meta.csv")
    shared = [c for c in Xw.columns if c in Xpitt.columns]
    print(f"  shared features: {len(shared)}")

    # WLS people confirmed normal in 2020 are strong controls: they were still
    # unimpaired nine years after the recording
    wls_ctrl = mw.npv_name == "normal"
    Xc = Xw.loc[wls_ctrl, shared]
    print(f"  WLS confirmed-normal controls available: {len(Xc)}")

    ypitt = mpitt.label.values
    base_X, base_y = Xpitt[shared], ypitt
    bm, bs = auc_cv(base_X, base_y)
    print(f"\n  Pitt alone           n={len(base_X):4d}  AUC = {bm:.3f} +/- {bs:.3f}")

    for n_add in (250, 500, len(Xc)):
        add = Xc.sample(n=min(n_add, len(Xc)), random_state=42)
        Xaug = pd.concat([base_X, add], ignore_index=True)
        yaug = np.concatenate([base_y, np.zeros(len(add), dtype=int)])
        am2, as2 = auc_cv(Xaug, yaug)
        print(f"  + {len(add):4d} WLS controls  n={len(Xaug):4d}  "
              f"AUC = {am2:.3f} +/- {as2:.3f}")

    # specificity at a fixed sensitivity, which is the metric that matters
    print("\n  SPECIFICITY AT 80% SENSITIVITY")
    for label, Xd_, yd_ in [("Pitt alone", base_X, base_y),
                            ("Pitt + all WLS controls",
                             pd.concat([base_X, Xc], ignore_index=True),
                             np.concatenate([base_y, np.zeros(len(Xc), dtype=int)]))]:
        prob = cross_val_predict(ens(), Xd_, yd_,
                                 cv=StratifiedKFold(5, shuffle=True, random_state=42),
                                 method="predict_proba", n_jobs=-1)[:, 1]
        best = 0.0
        for th in np.unique(np.round(prob, 3)):
            pred = (prob >= th).astype(int)
            tn, fp, fn, tp = confusion_matrix(yd_, pred, labels=[0, 1]).ravel()
            se = tp / (tp + fn) if (tp + fn) else 0
            sp = tn / (tn + fp) if (tn + fp) else 0
            if se >= 0.80 and sp > best:
                best = sp
        print(f"    {label:26s} specificity = {best*100:.1f}%  "
              f"(AUC {roc_auc_score(yd_, prob):.3f})")

    print(f"\nwritten to {WLS}/")


if __name__ == "__main__":
    main()
