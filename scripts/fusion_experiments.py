"""
fusion_experiments.py
---------------------
Two architectural questions, tested under one fixed protocol.

QUESTION 1 -- TASK-LEVEL FUSION
The current approach concatenates every task's features into one long vector.
An alternative treats each task as its own mini cognitive test: train a
separate model per task, then feed those task scores into a final classifier.

That matters clinically as well as statistically. Concatenation produces one
opaque number; task-level fusion produces a profile -- "picture description
normal, story recall abnormal" -- which is how a neuropsychologist reasons and
what a clinician can act on.

QUESTION 2 -- LATE FUSION OF MODALITIES
Likewise, acoustic and linguistic features are currently pooled. Training them
separately and combining their predictions lets each model specialise, and
makes the contribution of each modality visible instead of buried.

PROTOCOL, FIXED FOR EVERY ARM
Same participants, same participant-grouped folds, same random seeds, and
nested prediction so the fusion layer never sees a score produced by a model
that had seen the participant. Any arm that varies the protocol is not
comparable, which is exactly how small-dataset experiments manufacture
illusory gains.

>>> GOVERNANCE NOTE <<<
The Lu corpus was consulted five times during earlier development while
choosing which corpora to train on. It is therefore no longer an untouched
external test set, and is NOT used here to select anything. All experiments
below are conducted within the development data only, and results are reported
through leave-one-corpus-out so that no single corpus is privileged.
"""
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore")

import json
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (ExtraTreesClassifier, RandomForestClassifier,
                              GradientBoostingClassifier, VotingClassifier)
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

SEEDS = (42, 7, 123)
TASKS = ["cookie", "cinderella", "cat", "rockwell", "sandwich"]
OUT = "results/fusion"


def pipe(clf):
    return Pipeline([("i", SimpleImputer(strategy="median")),
                     ("s", StandardScaler()), ("c", clf)])


def ens():
    return VotingClassifier([
        ("et", pipe(ExtraTreesClassifier(n_estimators=400, min_samples_leaf=3,
                                         class_weight="balanced",
                                         random_state=42, n_jobs=-1))),
        ("gb", pipe(GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                               learning_rate=0.05,
                                               random_state=42))),
        ("rf", pipe(RandomForestClassifier(n_estimators=400, min_samples_leaf=3,
                                           class_weight="balanced",
                                           random_state=42, n_jobs=-1)))],
        voting="soft")


def boot_ci(y, p, groups, n=1500, seed=1):
    rng = np.random.default_rng(seed)
    u = np.unique(groups)
    out = []
    for _ in range(n):
        pick = rng.choice(u, len(u), replace=True)
        idx = np.concatenate([np.where(groups == q)[0] for q in pick])
        if len(set(y[idx])) < 2:
            continue
        out.append(roc_auc_score(y[idx], p[idx]))
    return np.percentile(out, [2.5, 97.5])


def evaluate(X, y, groups, clf=None):
    """Mean AUC across seeds, plus a bootstrap CI from the first seed."""
    clf = clf or ens()
    aucs, first = [], None
    for s in SEEDS:
        cv = StratifiedGroupKFold(5, shuffle=True, random_state=s)
        p = cross_val_predict(clf, X, y, cv=cv, groups=groups,
                              method="predict_proba", n_jobs=-1)[:, 1]
        aucs.append(roc_auc_score(y, p))
        if first is None:
            first = p
    lo, hi = boot_ci(y, first, groups)
    return float(np.mean(aucs)), float(np.std(aucs)), float(lo), float(hi)


def task_scores(seed: int) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Out-of-fold score from each task's own model, one row per participant.

    Each score is produced by a model that never saw that participant, so the
    fusion layer trains on honest inputs rather than on predictions the base
    models had already memorised.
    """
    frames, labels = {}, {}
    for t in TASKS:
        X = pd.read_csv(f"results/delaware/{t}_features.csv")
        m = pd.read_csv(f"results/delaware/{t}_meta.csv")
        cv = StratifiedGroupKFold(5, shuffle=True, random_state=seed)
        p = cross_val_predict(ens(), X, m.label.values, cv=cv,
                              groups=m.participant_id.values,
                              method="predict_proba", n_jobs=-1)[:, 1]
        d = pd.DataFrame({"pid": m.participant_id.values, f"score_{t}": p,
                          "y": m.label.values}).groupby("pid").mean()
        frames[t] = d[[f"score_{t}"]]
        labels[t] = d["y"]
    S = pd.concat(frames.values(), axis=1)
    y = pd.concat(labels.values(), axis=1).bfill(axis=1).iloc[:, 0]
    return S, y.round().astype(int).values, S.index.values


def main():
    os.makedirs(OUT, exist_ok=True)
    banner = "=" * 76
    results = {}

    # ── baseline: concatenate everything ────────────────────────────────────
    print(banner)
    print("QUESTION 1 — is task-level fusion better than concatenation?")
    print(banner)

    frames = []
    for t in TASKS:
        X = pd.read_csv(f"results/delaware/{t}_features.csv").add_prefix(f"{t}.")
        m = pd.read_csv(f"results/delaware/{t}_meta.csv")
        X["pid"] = m.participant_id.values
        X["y"] = m.label.values
        frames.append(X.groupby("pid").first())
    cat = frames[0]
    for f in frames[1:]:
        cat = cat.join(f.drop(columns="y"), how="outer")
    y_cat = cat.pop("y").fillna(0).round().astype(int).values
    g_cat = cat.index.values

    a, sd, lo, hi = evaluate(cat, y_cat, g_cat)
    results["concatenated_all_tasks"] = {"auc": a, "sd": sd, "ci": [lo, hi],
                                         "n_features": cat.shape[1]}
    print(f"  concatenated ({cat.shape[1]} features)   "
          f"AUC = {a:.3f} +/- {sd:.3f}   [{lo:.3f}, {hi:.3f}]")

    # ── task-level fusion ───────────────────────────────────────────────────
    fus = []
    for s in SEEDS:
        S, y_s, g_s = task_scores(s)
        cv = StratifiedGroupKFold(5, shuffle=True, random_state=s)
        p = cross_val_predict(
            pipe(LogisticRegression(max_iter=5000, class_weight="balanced")),
            S.fillna(S.median()), y_s, cv=cv, groups=g_s,
            method="predict_proba", n_jobs=-1)[:, 1]
        fus.append(roc_auc_score(y_s, p))
        if s == SEEDS[0]:
            first_p, first_y, first_g, first_S = p, y_s, g_s, S
    lo, hi = boot_ci(first_y, first_p, first_g)
    a_f = float(np.mean(fus))
    results["task_level_fusion"] = {"auc": a_f, "sd": float(np.std(fus)),
                                    "ci": [float(lo), float(hi)],
                                    "n_features": 5}
    print(f"  task-level fusion (5 scores)      "
          f"AUC = {a_f:.3f} +/- {np.std(fus):.3f}   [{lo:.3f}, {hi:.3f}]")
    print(f"\n  difference: {a_f - a:+.3f}")

    first_S.assign(label=first_y).to_csv(f"{OUT}/task_scores.csv")

    # which tasks the fusion layer actually relies on
    mdl = pipe(LogisticRegression(max_iter=5000, class_weight="balanced"))
    mdl.fit(first_S.fillna(first_S.median()), first_y)
    coefs = dict(zip(first_S.columns,
                     mdl.named_steps["c"].coef_.ravel().round(3)))
    print("\n  weight the fusion layer gives each task:")
    for k, v in sorted(coefs.items(), key=lambda x: -abs(x[1])):
        print(f"     {k:22s} {v:+.3f}")
    results["fusion_weights"] = {k: float(v) for k, v in coefs.items()}

    # ── modality late fusion, on the combined corpora ───────────────────────
    print("\n" + banner)
    print("QUESTION 2 — separate acoustic and linguistic models, then combine?")
    print(banner)
    Xp = pd.read_csv("results/pitt_cookie/features_multimodal.csv")
    mp = pd.read_csv("results/pitt_cookie/meta_multimodal.csv")
    y = mp.label.values
    g = mp.participant_id.values
    ac = [c for c in Xp.columns if c.startswith("ac.")]
    li = [c for c in Xp.columns
          if not c.startswith(("ac.", "chat.")) ]

    for name, cols in [("acoustic only", ac), ("linguistic only", li),
                       ("pooled (current)", ac + li)]:
        a2, sd2, lo2, hi2 = evaluate(Xp[cols], y, g)
        results[name.replace(" ", "_")] = {"auc": a2, "sd": sd2,
                                           "ci": [lo2, hi2],
                                           "n_features": len(cols)}
        print(f"  {name:22s} ({len(cols):3d})  AUC = {a2:.3f} +/- {sd2:.3f}"
              f"   [{lo2:.3f}, {hi2:.3f}]")

    # late fusion: out-of-fold scores from each modality, combined
    late = []
    for s in SEEDS:
        cv = StratifiedGroupKFold(5, shuffle=True, random_state=s)
        pa = cross_val_predict(ens(), Xp[ac], y, cv=cv, groups=g,
                               method="predict_proba", n_jobs=-1)[:, 1]
        pl = cross_val_predict(ens(), Xp[li], y, cv=cv, groups=g,
                               method="predict_proba", n_jobs=-1)[:, 1]
        Z = pd.DataFrame({"acoustic": pa, "linguistic": pl})
        pf = cross_val_predict(
            pipe(LogisticRegression(max_iter=5000, class_weight="balanced")),
            Z, y, cv=cv, groups=g, method="predict_proba", n_jobs=-1)[:, 1]
        late.append(roc_auc_score(y, pf))
        if s == SEEDS[0]:
            lp, lg = pf, g
    lo3, hi3 = boot_ci(y, lp, lg)
    a_l = float(np.mean(late))
    results["late_fusion"] = {"auc": a_l, "sd": float(np.std(late)),
                              "ci": [float(lo3), float(hi3)]}
    print(f"  {'late fusion':22s} (  2)  AUC = {a_l:.3f} "
          f"+/- {np.std(late):.3f}   [{lo3:.3f}, {hi3:.3f}]")

    with open(f"{OUT}/results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwritten to {OUT}/")


if __name__ == "__main__":
    main()
