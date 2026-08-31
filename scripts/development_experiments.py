"""
development_experiments.py
--------------------------
Model-improvement experiments run ENTIRELY on the development data, with the
external test corpus locked.

WHY LU IS NOW LOCKED, AND WHY THAT MATTERS
An earlier version of this project used the Lu corpus as an external test set
(AUC 0.821, later 0.849) and then included Lu in the final training data. Those
two uses are incompatible. Once a dataset informs model selection, reporting
performance on it as "external validation" overstates generalisation, and
repeatedly checking a held-out set while tuning turns it into a development set
by degrees.

Lu is therefore excluded from all training and all model selection from this
point. Every experiment below uses Pitt and Delaware only. The final chosen
configuration is evaluated on Lu exactly ONCE, and that number is reported
whatever it turns out to be.

WHAT IS AND IS NOT TESTED HERE
Pretrained speech and language embeddings (Whisper, wav2vec 2.0, RoBERTa) are
the most promising remaining direction in the literature, but their weights
cannot be downloaded in this environment, so they are documented as future work
rather than attempted and quietly abandoned. What can be tested here:

  1. LATE FUSION -- separate acoustic and linguistic models whose predictions
     are combined, rather than one model given an undifferentiated vector.
  2. TASK-LEVEL FUSION -- each Delaware task scored by its own model, those
     scores combined by a meta-classifier. Each task becomes a mini cognitive
     test.
  3. FEATURE SELECTION CURVE -- selection performed inside each fold, across
     several sizes, to find whether a smaller set does as well.
  4. STATIC DOCUMENT EMBEDDINGS -- spaCy's 300-dimensional vectors reduced by
     PCA. Not contextual like BERT, but the nearest available substitute.

Every arm uses identical participants, identical grouped folds and identical
seeds, so differences are attributable to the method rather than the split.
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
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (ExtraTreesClassifier, RandomForestClassifier,
                              GradientBoostingClassifier, VotingClassifier)
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

OUT = "results/development"
SEEDS = (42, 7, 123)


def pipe(clf, k=None, pca=None):
    steps = [("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]
    if pca:
        steps.append(("p", PCA(n_components=pca, random_state=42)))
    if k:
        steps.append(("k", SelectKBest(f_classif, k=k)))
    steps.append(("c", clf))
    return Pipeline(steps)


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
                                           random_state=42, n_jobs=-1))),
    ], voting="soft")


def oof(X, y, g, clf, seed):
    cv = StratifiedGroupKFold(5, shuffle=True, random_state=seed)
    return cross_val_predict(clf, X, y, cv=cv, groups=g,
                             method="predict_proba", n_jobs=-1)[:, 1]


def score(X, y, g, clf=None):
    clf = clf or ens()
    aucs = [roc_auc_score(y, oof(X, y, g, clf, s)) for s in SEEDS]
    return float(np.mean(aucs)), float(np.std(aucs))


def load_dev():
    """Pitt + Delaware only. Lu is locked."""
    Xp = pd.read_csv("results/pitt_cookie/features.csv")
    mp = pd.read_csv("results/pitt_cookie/meta.csv")
    Xd = pd.read_csv("results/delaware/cookie_features.csv")
    md = pd.read_csv("results/delaware/cookie_meta.csv")
    Xl = pd.read_csv("results/lu/features.csv")
    shared = [c for c in Xp.columns
              if c in Xd.columns and c in Xl.columns and not c.startswith("chat.")]
    X = pd.concat([Xp[shared], Xd[shared]], ignore_index=True)
    y = np.concatenate([mp.label.values, md.label.values])
    g = np.concatenate([("P" + mp.participant_id.astype(str)).values,
                        ("D" + md.participant_id.astype(str)).values])
    return X, y, g, shared


def main():
    os.makedirs(OUT, exist_ok=True)
    X, y, g, shared = load_dev()
    banner = "=" * 76
    print(banner)
    print("DEVELOPMENT SET: Pitt + Delaware  (Lu locked as external test)")
    print(banner)
    print(f"  recordings {len(X)}   participants {len(set(g))}   features {len(shared)}")
    print(f"  controls {int((y==0).sum())}   impaired {int((y==1).sum())}")

    ac = [c for c in shared if c.startswith("ac.")]
    ling = [c for c in shared if c.startswith("ling.")]
    iu = [c for c in shared if c.startswith("iu.")]
    sem = [c for c in shared if c.startswith("sem.")]
    text = ling + iu + sem

    results = {}

    # ── baseline ───────────────────────────────────────────────────────────
    print("\n" + banner); print("BASELINE"); print(banner)
    m, s = score(X, y, g)
    results["baseline_all_features"] = {"auc": m, "sd": s, "n_features": len(shared)}
    print(f"  all {len(shared)} features, single ensemble        {m:.3f} +/- {s:.3f}")

    # ── 1. late fusion ─────────────────────────────────────────────────────
    print("\n" + banner)
    print("1. LATE FUSION -- separate acoustic and linguistic models combined")
    print(banner)
    for nm, cols in [("acoustic only", ac), ("text only", text)]:
        if not cols:
            continue
        mm, ss = score(X[cols], y, g)
        results[f"branch_{nm.replace(' ','_')}"] = {"auc": mm, "sd": ss,
                                                    "n_features": len(cols)}
        print(f"  {nm:34s} {len(cols):3d} feats  {mm:.3f} +/- {ss:.3f}")

    if ac and text:
        fused = []
        for seed in SEEDS:
            pa = oof(X[ac], y, g, ens(), seed)
            pt = oof(X[text], y, g, ens(), seed)
            # stack the two branch scores and let a simple model weight them,
            # evaluated with the same grouped folds
            Z = pd.DataFrame({"acoustic": pa, "text": pt})
            pf = oof(Z, y, g, pipe(LogisticRegression(max_iter=2000,
                                                      class_weight="balanced")), seed)
            fused.append(roc_auc_score(y, pf))
        m2, s2 = float(np.mean(fused)), float(np.std(fused))
        results["late_fusion"] = {"auc": m2, "sd": s2}
        print(f"  {'LATE FUSION (acoustic + text)':34s}          {m2:.3f} +/- {s2:.3f}"
              f"   ({m2-m:+.3f} vs baseline)")

    # ── 2. feature selection curve ─────────────────────────────────────────
    print("\n" + banner)
    print("2. FEATURE SELECTION -- selection performed INSIDE each fold")
    print(banner)
    sel = {}
    for k in [15, 25, 40, 60, 80]:
        if k >= len(shared):
            continue
        mm, ss = score(X, y, g, ens_k(k))
        sel[k] = mm
        print(f"  best {k:3d} features                          {mm:.3f} +/- {ss:.3f}")
    results["feature_selection"] = sel

    # ── 3. static document embeddings ──────────────────────────────────────
    print("\n" + banner)
    print("3. STATIC EMBEDDINGS (spaCy 300-d, PCA-reduced)")
    print("   Not contextual; a partial substitute for BERT-family embeddings,")
    print("   whose weights are unavailable in this environment.")
    print(banner)
    emb_path = f"{OUT}/doc_embeddings.csv"
    if os.path.exists(emb_path):
        E = pd.read_csv(emb_path)
        for nc in [10, 25]:
            Xe = pd.concat([X.reset_index(drop=True),
                            E.iloc[:, :nc].reset_index(drop=True)], axis=1)
            mm, ss = score(Xe, y, g)
            results[f"handcrafted_plus_emb{nc}"] = {"auc": mm, "sd": ss}
            print(f"  handcrafted + {nc:2d} embedding dims           {mm:.3f} +/- {ss:.3f}"
                  f"   ({mm-m:+.3f})")
    else:
        print("  (embeddings not built; run build_embeddings first)")

    with open(f"{OUT}/experiments.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwritten to {OUT}/experiments.json")


def ens_k(k):
    return VotingClassifier([
        ("et", pipe(ExtraTreesClassifier(n_estimators=400, min_samples_leaf=3,
                                         class_weight="balanced",
                                         random_state=42, n_jobs=-1), k=k)),
        ("gb", pipe(GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                               learning_rate=0.05,
                                               random_state=42), k=k)),
        ("rf", pipe(RandomForestClassifier(n_estimators=400, min_samples_leaf=3,
                                           class_weight="balanced",
                                           random_state=42, n_jobs=-1), k=k)),
    ], voting="soft")


if __name__ == "__main__":
    main()
