"""
merge_and_analyze.py
--------------------
Merges the locally-extracted acoustic features with the transcript features
and evaluates whether adding the audio actually helps.

WHY A COMPARISON AND NOT JUST A NUMBER
Reporting only the final combined score would leave the central question
unanswered: did the acoustic signal contribute anything, or did 53 extra
columns simply give the model more room to overfit? The three feature sets are
therefore evaluated under identical conditions -- same participants, same
folds, same matching -- so the difference is attributable to the features
rather than to any change in protocol.

The same three safeguards as before apply throughout:
  * participant-level grouping  (Pitt is longitudinal; one person contributes
    up to five recordings, so folds must not split an individual)
  * age and sex matching        (the dementia group is ~6.6 years older, and
    age alone reaches AUC 0.707 if left uncontrolled, falling to 0.515 once
    matched -- results/reconstruction/age_leakage_evidence.json, regenerated
    2026-08-22; the earlier inline 0.71/0.46 pair is superseded)
  * sensitivity and specificity reported, not accuracy alone
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from scipy import stats

from dhikra.model import build_models, evaluate_models, explain_model
from analyze_pitt import match_participants

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score

pd.set_option("display.width", 220)
OUT = "results/pitt_cookie"
BANNER = "=" * 78


def auc_of(X, y, groups, seed=42):
    pipe = Pipeline([("i", SimpleImputer(strategy="median")),
                     ("s", StandardScaler()),
                     ("c", SVC(kernel="rbf", C=1, probability=True,
                               class_weight="balanced", random_state=seed))])
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    s = cross_val_score(pipe, X, y, cv=cv, groups=groups,
                        scoring="roc_auc", n_jobs=-1)
    return s.mean(), s.std()


def main():
    X = pd.read_csv(f"{OUT}/features.csv")
    meta = pd.read_csv(f"{OUT}/meta.csv")
    y = meta["label"].values
    # Path comes from corpus_paths.json; the original upload path
    # /mnt/user-data/uploads/acoustic_features.csv died with the sandbox.
    # Regenerate the file with scripts/extract_audio_features.py (needs the
    # Pitt audio) and point acoustic_features_csv at it.
    from dhikra.paths import resolve
    ac = pd.read_csv(resolve("acoustic_features_csv"))

    # ---- merge -----------------------------------------------------------
    ac_cols = [c for c in ac.columns if c.startswith("ac.")]
    ac_small = ac[["file_id"] + ac_cols].drop_duplicates("file_id")

    merged = meta[["file_id"]].merge(ac_small, on="file_id", how="left")
    assert len(merged) == len(meta)
    Xa = pd.concat([X.reset_index(drop=True),
                    merged[ac_cols].reset_index(drop=True)], axis=1)

    have_audio = merged[ac_cols[0]].notna().values
    print(BANNER)
    print("MERGE")
    print(BANNER)
    print(f"  transcript recordings : {len(X)}")
    print(f"  with acoustic features: {int(have_audio.sum())}")
    print(f"  total features        : {Xa.shape[1]} "
          f"({X.shape[1]} text + {len(ac_cols)} acoustic)")

    # Recordings without audio are dropped for the comparison, so every
    # feature set is evaluated on exactly the same participants -- otherwise
    # the "improvement" could just be a different sample.
    keep = have_audio
    Xa, Xt, ym, mm = (Xa[keep].reset_index(drop=True),
                      X[keep].reset_index(drop=True),
                      y[keep],
                      meta[keep].reset_index(drop=True))
    Xac = Xa[ac_cols]
    print(f"  common subset         : {len(Xa)} recordings, "
          f"{mm.participant_id.nunique()} participants")

    # ---- match -----------------------------------------------------------
    mask, n_pairs = match_participants(mm, ym)
    Xa_m, Xt_m, Xac_m = Xa[mask], Xt[mask], Xac[mask]
    ym_m, mm_m = ym[mask], mm[mask].reset_index(drop=True)
    g = mm_m.participant_id.values
    c = mm_m.loc[ym_m == 0, "age"].dropna()
    d = mm_m.loc[ym_m == 1, "age"].dropna()
    _, p = stats.ttest_ind(c, d, equal_var=False)
    print(f"\n  matched pairs         : {n_pairs}")
    print(f"  matched recordings    : {len(Xa_m)} "
          f"({int((ym_m==0).sum())} control / {int((ym_m==1).sum())} impaired)")
    print(f"  age after matching    : {c.mean():.1f} vs {d.mean():.1f}  p={p:.3f}")

    # ---- does audio help? -------------------------------------------------
    print("\n" + BANNER)
    print("DOES THE AUDIO HELP?  (identical participants, folds and protocol)")
    print(BANNER)
    rows = []
    for name, Xd in [("acoustic only", Xac_m),
                     ("transcript only", Xt_m),
                     ("transcript + acoustic", Xa_m)]:
        m, s = auc_of(Xd, ym_m, g)
        rows.append((name, Xd.shape[1], m, s))
        print(f"  {name:24s} {Xd.shape[1]:3d} features   "
              f"AUC = {m:.3f} (sd {s:.3f})")
    gain = rows[2][2] - rows[1][2]
    print(f"\n  gain from adding audio: {gain:+.3f} AUC")
    pd.DataFrame(rows, columns=["feature_set", "n_features", "roc_auc",
                                "roc_auc_sd"]).to_csv(
        f"{OUT}/modality_comparison.csv", index=False)

    # ---- full model comparison on the combined set -----------------------
    print("\n" + BANNER)
    print("MODEL COMPARISON  (transcript + acoustic, participant-grouped CV)")
    print(BANNER)
    res = evaluate_models(Xa_m, ym_m, groups=g)
    cols = ["model", "accuracy", "accuracy_sd", "roc_auc", "roc_auc_sd",
            "sensitivity", "specificity", "f1"]
    print(res[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    res.to_csv(f"{OUT}/multimodal_model_comparison.csv", index=False)
    best = res.iloc[0]["model"]
    print(f"\n  best: {best}")

    # ---- what drives it ---------------------------------------------------
    print("\n" + BANNER)
    print("FEATURE IMPORTANCE  (combined set)")
    print(BANNER)
    imp = explain_model(build_models()[best], Xa_m, ym_m, top_n=15)
    print(imp.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    imp.to_csv(f"{OUT}/multimodal_feature_importance.csv", index=False)
    n_ac = sum(1 for f in imp.feature if f.startswith("ac."))
    print(f"\n  acoustic features in the top 15: {n_ac}")

    # ---- acoustic group differences --------------------------------------
    print("\n" + BANNER)
    print("ACOUSTIC GROUP DIFFERENCES  (matched cohort)")
    print(BANNER)
    rows = []
    for f in ac_cols:
        a_ = Xac_m.loc[ym_m == 0, f].dropna()
        b_ = Xac_m.loc[ym_m == 1, f].dropna()
        if len(a_) < 10 or len(b_) < 10 or a_.std() == 0 or b_.std() == 0:
            continue
        t, pv = stats.ttest_ind(a_, b_, equal_var=False)
        dd = (b_.mean() - a_.mean()) / np.sqrt((a_.std() ** 2 + b_.std() ** 2) / 2)
        rows.append((f, a_.mean(), b_.mean(), dd, pv))
    gd = pd.DataFrame(rows, columns=["feature", "control_mean",
                                     "impaired_mean", "cohens_d", "p_value"])
    gd["abs_d"] = gd.cohens_d.abs()
    gd = gd.sort_values("abs_d", ascending=False).drop(columns="abs_d")
    print(gd.head(12).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    gd.to_csv(f"{OUT}/acoustic_group_comparison.csv", index=False)

    # ---- severity ---------------------------------------------------------
    print("\n" + BANNER)
    print("ACOUSTIC SEVERITY  (correlation with MMSE, impaired group)")
    print(BANNER)
    sub = mm[(ym == 1) & mm.mmse.notna()]
    Xs = Xac.loc[sub.index]
    rows = []
    for f in ac_cols:
        v = Xs[f]
        m2 = v.notna()
        if m2.sum() < 30 or v[m2].std() == 0:
            continue
        r, pv = stats.pearsonr(v[m2], sub.mmse[m2])
        rows.append((f, r, pv, int(m2.sum())))
    md = pd.DataFrame(rows, columns=["feature", "r_with_mmse", "p_value", "n"])
    md["abs_r"] = md.r_with_mmse.abs()
    md = md.sort_values("abs_r", ascending=False).drop(columns="abs_r")
    print(md.head(10).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    md.to_csv(f"{OUT}/acoustic_mmse_correlation.csv", index=False)

    # save merged matrix for the final model
    Xa.to_csv(f"{OUT}/features_multimodal.csv", index=False)
    mm.to_csv(f"{OUT}/meta_multimodal.csv", index=False)
    np.save(f"{OUT}/multimodal_mask.npy", mask)
    print(f"\nwritten to {OUT}/")


if __name__ == "__main__":
    main()
