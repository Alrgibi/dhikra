"""
train_development.py
--------------------
The full 987-recording development pipeline, reconstructed as a script.

WHAT THIS REPRODUCES
CURRENT_development_stats.json -- the authoritative post-lock numbers -- was
produced by an inline (unsaved) command on 18 Aug 2026 (FILE_MAP: "inline
regeneration"). This script re-implements that pipeline from its committed
pieces and recorded outputs:

  data      results/pitt_cookie/{features,meta}.csv   (548, build_pitt_cookie.py)
            results/delaware/cookie_{features,meta}.csv (439, build_delaware.py)
  features  the 64 columns recorded in results/summary/model_card.json
            (feature_order) -- ling.* + iu.* + sem.*; no chat.*, no ac.*
  model     soft-voting ensemble ExtraTrees(500)/GB(150,d2,lr.05)/RF(500),
            each in an impute+scale pipeline -- the committed form of the
            "final ensemble" (scripts/early_detection.py::ens())
  protocol  StratifiedGroupKFold(5, shuffle=True, random_state=42), grouped
            by participant; out-of-fold predict_proba
  CIs       participant-level bootstrap, 2000 resamples
  threshold the screening_threshold rule from src/dhikra/model.py, floor
            swept over {0.90, 0.85, 0.80, 0.75, 0.70} to locate the rule
            that yields the locked 0.367

Everything it cannot know for certain is INFERRED and marked as such in the
output; docs/RECONSTRUCTION.md carries the evidence. Reconstructed numbers
are compared field-by-field against CURRENT_development_stats.json and the
deltas are written next to them -- nothing in results/summary/ is modified.

WHAT THIS SCRIPT REFUSES TO DO
  * touch Lu: it asserts no Lu row can enter, and never reads results/lu/
  * write into results/summary/: output goes to results/reconstruction/ only

Usage:  python scripts/train_development.py            (run from dhikra/)
        python scripts/train_development.py --quick    (skip bootstrap CIs)
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (ExtraTreesClassifier, GradientBoostingClassifier,
                              RandomForestClassifier, VotingClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, brier_score_loss, confusion_matrix

from dhikra.model import screening_threshold

OUT = "results/reconstruction"
CURRENT = "results/summary/CURRENT_development_stats.json"
MODEL_CARD = "results/summary/model_card.json"


def pipe(clf):
    return Pipeline([("i", SimpleImputer(strategy="median")),
                     ("s", StandardScaler()), ("c", clf)])


def ens():
    """Identical to scripts/early_detection.py::ens() -- the committed form
    of the final ensemble (ExtraTrees + GradientBoosting + RandomForest,
    soft voting, seed 42)."""
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


def load_data():
    Xp = pd.read_csv("results/pitt_cookie/features.csv")
    mp = pd.read_csv("results/pitt_cookie/meta.csv")
    Xd = pd.read_csv("results/delaware/cookie_features.csv")
    md = pd.read_csv("results/delaware/cookie_meta.csv")

    assert len(Xp) == 548, f"Pitt cookie: expected 548 rows, got {len(Xp)}"
    assert len(Xd) == 439, f"Delaware cookie: expected 439 rows, got {len(Xd)}"

    # Lu lockout: nothing that looks like Lu may enter this pipeline.
    for m, name in ((mp, "Pitt"), (md, "Delaware")):
        if "group" in m:
            bad = m.group.astype(str).str.lower().isin(
                {"alzheimer's", "pick's", "conrol"})
            assert not bad.any(), (
                f"{name} meta contains Lu-signature groups -- Lu data may "
                f"have leaked into a development matrix. STOP.")

    feats = json.load(open(MODEL_CARD))["feature_order"]
    assert len(feats) == 64, "model_card feature_order must list 64 features"
    for f in feats:
        assert f in Xp.columns, f"Pitt matrix missing locked feature {f}"
        assert f in Xd.columns, f"Delaware matrix missing locked feature {f}"

    X = pd.concat([Xp[feats], Xd[feats]], ignore_index=True)
    y = np.concatenate([mp.label.values, md.label.values]).astype(int)
    src = np.array(["pitt"] * len(Xp) + ["delaware"] * len(Xd))
    groups = np.concatenate([
        "p_" + mp.participant_id.astype(str).values,
        "d_" + md.participant_id.astype(str).values,
    ])

    assert len(X) == 987, f"combined: expected 987 recordings, got {len(X)}"
    n_participants = len(np.unique(groups))
    assert n_participants == 581, (
        f"expected 581 unique participants, got {n_participants} -- "
        f"participant-id derivation differs from the locked build")
    return X, y, src, groups


def participant_bootstrap(y, p, groups, n=2000, seed=42):
    """Participant-level bootstrap CI for AUC: resample PEOPLE, keep all
    their recordings (HANDOFF §2: 'resamples of people, not recordings')."""
    rng = np.random.default_rng(seed)
    uniq = np.unique(groups)
    idx_of = {g: np.flatnonzero(groups == g) for g in uniq}
    aucs = []
    for _ in range(n):
        take = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_of[g] for g in take])
        yy, pp = y[idx], p[idx]
        if len(np.unique(yy)) < 2:
            continue
        aucs.append(roc_auc_score(yy, pp))
    return float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def calibration_block(y, p):
    bins = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
    rows, gaps = [], []
    for lo, hi in bins:
        m = (p > lo) & (p <= hi)
        if m.sum() == 0:
            rows.append({"bin": f"({lo}, {hi}]", "n": 0}); continue
        pred, obs = float(p[m].mean()), float(y[m].mean())
        rows.append({"bin": f"({lo}, {hi}]", "n": int(m.sum()),
                     "predicted": round(pred, 3), "observed": round(obs, 3)})
        gaps.append(abs(obs - pred))
    eps = 1e-9
    logit = np.log(np.clip(p, eps, 1 - eps) / np.clip(1 - p, eps, 1 - eps))
    lr = LogisticRegression(C=1e9, max_iter=5000).fit(logit.reshape(-1, 1), y)
    return {
        "brier": float(brier_score_loss(y, p)),
        "slope": float(lr.coef_[0][0]),
        "intercept": float(lr.intercept_[0]),
        "max_gap": float(max(gaps)) if gaps else None,
        "bins": rows,
    }


def sens_spec(y, p, th):
    pred = (p >= th).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return tp / (tp + fn), tn / (tn + fp)


def spec_floor_threshold(y, p, min_specificity=0.90):
    """Mirror of model.screening_threshold for the rule-in point: the LOWEST
    threshold that still achieves the required specificity (maximises
    sensitivity subject to it)."""
    best = (0.5, 0.0, 0.0)
    for th in np.unique(np.round(p, 3)):
        s, sp = sens_spec(y, p, th)
        if sp >= min_specificity and s > best[1]:
            best = (float(th), float(s), float(sp))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip bootstrap CIs")
    args = ap.parse_args()

    print("=" * 78)
    print("RECONSTRUCTED DEVELOPMENT PIPELINE  (Pitt + Delaware, Lu locked out)")
    print("=" * 78)
    X, y, src, groups = load_data()
    print(f"  {len(X)} recordings, {len(np.unique(groups))} participants, "
          f"{X.shape[1]} features")

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    print("  running out-of-fold predictions (5-fold, grouped)...")
    p = cross_val_predict(ens(), X, y, cv=cv, groups=groups,
                          method="predict_proba", n_jobs=1)[:, 1]

    res = {}
    subsets = {"combined": np.ones(len(y), bool),
               "pitt_dementia": src == "pitt",
               "delaware_mci": src == "delaware"}
    for name, m in subsets.items():
        auc = float(roc_auc_score(y[m], p[m]))
        entry = {"auc": auc, "n": int(m.sum())}
        if not args.quick:
            lo, hi = participant_bootstrap(y[m], p[m], groups[m])
            entry["ci95"] = [lo, hi]
        res[name] = entry
        print(f"  {name:15s} AUC {auc:.4f}  n={int(m.sum())}")

    res["calibration"] = calibration_block(y, p)

    # threshold rule sweep: which sensitivity floor reproduces 0.367?
    sweep = {}
    for floor in (0.90, 0.85, 0.80, 0.75, 0.70):
        th, s, sp = screening_threshold(y, p, min_sensitivity=floor)
        sweep[str(floor)] = {"threshold": th, "sensitivity": s, "specificity": sp}
        print(f"  floor {floor:.2f} -> th {th:.3f}  sens {s:.3f}  spec {sp:.3f}")
    res["threshold_rule_sweep"] = sweep

    th_hi, s_hi, sp_hi = screening_threshold(y, p, min_sensitivity=0.90)
    th_scr, s_scr, sp_scr = screening_threshold(y, p, min_sensitivity=0.75)
    th_sp, s_sp, sp_sp = spec_floor_threshold(y, p, min_specificity=0.90)
    res["operating_points"] = {
        "high_sensitivity": {"threshold": th_hi, "sensitivity": s_hi, "specificity": sp_hi},
        "screening": {"threshold": th_scr, "sensitivity": s_scr, "specificity": sp_scr},
        "high_specificity": {"threshold": th_sp, "sensitivity": s_sp, "specificity": sp_sp},
    }

    ppv = []
    for prev in (0.01, 0.05, 0.077, 0.11, 0.15, 0.25, 0.42):
        se, sp = s_scr, sp_scr
        ppv.append({"prevalence": prev,
                    "ppv": se * prev / (se * prev + (1 - sp) * (1 - prev)),
                    "npv": sp * (1 - prev) / ((1 - se) * prev + sp * (1 - prev))})
    res["ppv_npv"] = ppv

    # ---- compare against the locked CURRENT file ----
    comparison = {}
    if os.path.exists(CURRENT):
        cur = json.load(open(CURRENT))
        for k in ("combined", "pitt_dementia", "delaware_mci"):
            comparison[k] = {
                "locked_auc": cur[k]["auc"],
                "reconstructed_auc": res[k]["auc"],
                "delta": res[k]["auc"] - cur[k]["auc"],
            }
        comparison["screening_threshold"] = {
            "locked": cur["operating_points"]["screening"]["threshold"],
            "reconstructed": th_scr,
        }
        comparison["calibration_max_gap"] = {
            "locked": cur["calibration"]["max_gap"],
            "reconstructed": res["calibration"]["max_gap"],
        }
    res["comparison_to_locked"] = comparison

    res["_provenance"] = {
        "dataset": "Pitt cookie (548) + Delaware cookie (439) = 987 recordings, "
                   "581 participants; Lu not read by this script",
        "lock_state": "post-Lu-lock reconstruction; results/summary/ not modified",
        "script": "scripts/train_development.py",
        "model": "soft-voting ET/GB/RF (early_detection.ens recipe) -- "
                 "INFERRED to be the final ensemble; see docs/RECONSTRUCTION.md",
        "cv": "StratifiedGroupKFold(5, shuffle=True, random_state=42), "
              "grouped by participant (prefixed pitt/delaware ids)",
        "bootstrap": None if args.quick else "participant-level, 2000 resamples, seed 42",
        "generated": datetime.date.today().isoformat(),
        "python": sys.version.split()[0],
    }

    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, "development_stats_reconstructed.json")
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"\n  written to {out_path}")
    if comparison:
        print("\n  COMPARISON TO LOCKED NUMBERS")
        for k, v in comparison.items():
            print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
