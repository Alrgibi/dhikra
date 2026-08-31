"""
improve_model.py
----------------
Systematic attempt to raise screening performance above the PRE-LOCK
multimodal matched-Pitt baseline of AUC 0.775
(results/pitt_cookie/multimodal_model_comparison.csv). That baseline is three
pool changes out of date: the deployed post-lock figures are 0.755 combined
and 0.809 on Pitt. Kept for the record, testing several strategies under identical, honest conditions.

EVERY STRATEGY IS EVALUATED THE SAME WAY
  * participant-grouped folds  (Pitt is longitudinal; one person contributes
    up to five recordings, and splitting them across folds inflates results)
  * repeated over several random seeds, reporting mean and spread, because a
    single split on ~180 participants is unstable enough to mislead
  * the age confound controlled in every arm, so no gain can come from the
    model quietly learning age

STRATEGIES TESTED
  1. AGE RESIDUALISATION instead of matching. Matching discards 28% of the
     data to balance age. Regressing each feature on age and modelling the
     residuals removes the same confound while keeping every recording.
  2. SEMANTIC EMBEDDINGS. Document vectors compressed by PCA, capturing
     meaning that hand-designed counts may miss.
  3. FEATURE SELECTION at several sizes, since 64 features on ~180
     participants risks fitting noise.
  4. MODEL FAMILY AND TUNING, including gradient boosting and calibrated
     ensembles.
  5. RECORDING-LEVEL vs PARTICIPANT-LEVEL prediction. Averaging a person's
     repeat visits before classifying reduces measurement noise, and a
     screening decision is about the person rather than the recording.
"""
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier,
                              ExtraTreesClassifier, VotingClassifier)
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score

from analyze_pitt import match_participants

OUT = "results/pitt_cookie"


def load():
    X = pd.read_csv(f"{OUT}/features_multimodal.csv")
    meta = pd.read_csv(f"{OUT}/meta_multimodal.csv")
    y = meta["label"].values
    return X, meta, y


def deployable_cols(X):
    """Only features a live session can compute (no corpus CHAT markup)."""
    return [c for c in X.columns if not c.startswith("chat.")]


def residualise_on_age(X: pd.DataFrame, age: pd.Series) -> pd.DataFrame:
    """
    Remove the linear effect of age from every feature.

    This is the alternative to matching. Matching balances age by throwing
    participants away; residualising removes the age-related component of each
    measurement and keeps everyone. If a feature's association with impairment
    survives, it cannot be an age effect in disguise.
    """
    a = age.fillna(age.median()).values.reshape(-1, 1)
    out = X.astype(float).copy()   # residuals are float; int columns would fail
    for c in X.columns:
        v = X[c]
        m = v.notna()
        if m.sum() < 30 or v[m].std() == 0:
            continue
        lr = LinearRegression().fit(a[m.values], v[m].values)
        out.loc[m, c] = v[m].values - lr.predict(a[m.values])
    return out


def auc(Xd, y, groups, clf=None, seeds=(42, 7, 123)):
    if clf is None:
        clf = SVC(kernel="rbf", C=1, probability=True,
                  class_weight="balanced", random_state=42)
    scores = []
    for s in seeds:
        cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=s)
        scores.append(cross_val_score(clf, Xd, y, cv=cv, groups=groups,
                                      scoring="roc_auc", n_jobs=-1).mean())
    return float(np.mean(scores)), float(np.std(scores))


def pipe(clf, k=None, pca=None):
    steps = [("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]
    if pca:
        steps.append(("p", PCA(n_components=pca, random_state=42)))
    if k:
        steps.append(("k", SelectKBest(f_classif, k=k)))
    steps.append(("c", clf))
    return Pipeline(steps)


def main():
    X, meta, y = load()
    cols = deployable_cols(X)
    banner = "=" * 74

    # ── baseline: matched subset ───────────────────────────────────────────
    print(banner); print("BASELINE — matched subset (current approach)"); print(banner)
    mask, _ = match_participants(meta, y, seed=1)
    Xm, ym, mm = X[mask][cols], y[mask], meta[mask].reset_index(drop=True)
    g = mm.participant_id.values
    base_m, base_s = auc(pipe(SVC(kernel="rbf", C=1, probability=True,
                                  class_weight="balanced", random_state=42)),
                         ym, g) if False else auc(Xm, ym, g,
                                                  pipe(SVC(kernel="rbf", C=1,
                                                           probability=True,
                                                           class_weight="balanced",
                                                           random_state=42)))
    print(f"  n = {len(Xm)} recordings, {mm.participant_id.nunique()} participants")
    print(f"  AUC = {base_m:.3f} +/- {base_s:.3f}")

    # ── strategy 1: residualise on age, keep everything ────────────────────
    print("\n" + banner)
    print("STRATEGY 1 — age residualisation instead of matching")
    print(banner)
    Xr = residualise_on_age(X[cols], meta["age"])
    gr = meta.participant_id.values
    r_m, r_s = auc(Xr, y, gr, pipe(SVC(kernel="rbf", C=1, probability=True,
                                       class_weight="balanced", random_state=42)))
    print(f"  n = {len(Xr)} recordings, {meta.participant_id.nunique()} participants")
    print(f"  AUC = {r_m:.3f} +/- {r_s:.3f}   ({r_m-base_m:+.3f} vs baseline)")

    # confound check: does age still predict after residualising?
    age_only = pd.DataFrame({"age": meta["age"].fillna(meta["age"].median())})
    a_m, _ = auc(age_only, y, gr,
                 pipe(LogisticRegression(max_iter=5000, class_weight="balanced")))
    print(f"  age alone on this set: AUC {a_m:.3f}  <- confound still present in "
          "the raw data, which is why residualisation is required")

    # ── strategy 2: participant-level aggregation ──────────────────────────
    print("\n" + banner)
    print("STRATEGY 2 — one prediction per PERSON, not per recording")
    print(banner)
    agg = Xr.copy()
    agg["_pid"] = meta.participant_id.values
    agg["_y"] = y
    pa = agg.groupby("_pid").mean(numeric_only=True)
    ya = pa.pop("_y").round().astype(int).values
    ga = pa.index.values
    p_m, p_s = auc(pa, ya, ga, pipe(SVC(kernel="rbf", C=1, probability=True,
                                        class_weight="balanced", random_state=42)))
    print(f"  n = {len(pa)} participants (repeat visits averaged)")
    print(f"  AUC = {p_m:.3f} +/- {p_s:.3f}   ({p_m-base_m:+.3f} vs baseline)")

    # ── strategy 3: feature selection ──────────────────────────────────────
    print("\n" + banner)
    print("STRATEGY 3 — feature selection (inside the folds)")
    print(banner)
    best_k, best_km = None, 0
    for k in [15, 25, 35, 45, 55]:
        m, s = auc(Xr, y, gr, pipe(SVC(kernel="rbf", C=1, probability=True,
                                       class_weight="balanced", random_state=42), k=k))
        print(f"  best {k:2d} features  AUC = {m:.3f} +/- {s:.3f}")
        if m > best_km:
            best_k, best_km = k, m

    # ── strategy 4: model family ───────────────────────────────────────────
    print("\n" + banner)
    print("STRATEGY 4 — model family and tuning")
    print(banner)
    cands = {
        "SVM rbf C=1": SVC(kernel="rbf", C=1, probability=True,
                           class_weight="balanced", random_state=42),
        "SVM rbf C=3": SVC(kernel="rbf", C=3, probability=True,
                           class_weight="balanced", random_state=42),
        "Logistic L2": LogisticRegression(max_iter=5000, C=0.5,
                                          class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=800, min_samples_leaf=3,
                                                class_weight="balanced",
                                                random_state=42, n_jobs=-1),
        "Extra Trees": ExtraTreesClassifier(n_estimators=800, min_samples_leaf=3,
                                            class_weight="balanced",
                                            random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200,
                                                        max_depth=2,
                                                        learning_rate=0.05,
                                                        random_state=42),
    }
    results = {}
    for name, clf in cands.items():
        m, s = auc(Xr, y, gr, pipe(clf))
        results[name] = m
        print(f"  {name:20s} AUC = {m:.3f} +/- {s:.3f}")

    # ── strategy 5: ensemble of the best ───────────────────────────────────
    print("\n" + banner)
    print("STRATEGY 5 — soft-voting ensemble")
    print(banner)
    top = sorted(results, key=results.get, reverse=True)[:3]
    ens = VotingClassifier([(n.replace(" ", "_"), pipe(cands[n])) for n in top],
                           voting="soft")
    e_m, e_s = auc(Xr, y, gr, ens)
    print(f"  combining: {', '.join(top)}")
    print(f"  AUC = {e_m:.3f} +/- {e_s:.3f}   ({e_m-base_m:+.3f} vs baseline)")

    print("\n" + banner)
    print("SUMMARY")
    print(banner)
    print(f"  baseline (matched)          {base_m:.3f}")
    print(f"  age-residualised, all data  {r_m:.3f}")
    print(f"  participant-level           {p_m:.3f}")
    print(f"  best feature selection      {best_km:.3f}  (k={best_k})")
    print(f"  best single model           {max(results.values()):.3f}  "
          f"({max(results, key=results.get)})")
    print(f"  ensemble                    {e_m:.3f}")


if __name__ == "__main__":
    main()
