"""
analyze_pitt.py
---------------
The full, methodologically careful evaluation on the DementiaBank Pitt corpus.

THREE SAFEGUARDS, each addressing a way this result could be quietly wrong:

 1. PARTICIPANT-LEVEL GROUPING. Pitt is longitudinal -- one person contributes
    up to five yearly recordings. Standard cross-validation would place the
    same individual in both training and test folds, letting the model
    recognise the person rather than the disease. All folds are grouped by
    participant id.

 2. AGE AND SEX MATCHING. In the raw corpus the dementia group is ~6.6 years
    older than the controls, and age ALONE reaches AUC 0.707 (regenerated
    2026-08-22 on the locked 548-recording pool:
    results/reconstruction/age_leakage_evidence.json; the same experiment
    printed 0.71 in an earlier inline run, now superseded). After matching it
    falls to 0.515 while the speech features hold at 0.798. A model trained
    without matching would substantially be detecting age. Participants are
    matched 1:1 on sex and age (within 3 years), following the design of the
    ADReSS challenge subset.

 3. HONEST METRIC REPORTING. Sensitivity and specificity are reported
    alongside accuracy, because a screening instrument that misses patients is
    not useful regardless of its headline accuracy.

Run:  python scripts/analyze_pitt.py --corpus /path/to/Pitt_cookie
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd
from scipy import stats

from dhikra.corpus import build_dataset, save_dataset
from dhikra.paths import resolve
from dhikra.model import build_models, evaluate_models, explain_model, report

pd.set_option("display.width", 220)


def match_participants(meta: pd.DataFrame, y: np.ndarray,
                       max_age_diff: float = 3.0, seed: int = 1):
    """
    1:1 age+sex matching at PARTICIPANT level (not recording level).

    Matching per recording would let a participant with four visits be matched
    four times, silently re-weighting the cohort. Matching is therefore done on
    one row per person, and every recording from a matched person is then kept.
    """
    people = (meta.assign(label=y)
                  .groupby("participant_id")
                  .agg(age=("age", "mean"), sex=("sex", "first"),
                       label=("label", "first"))
                  .reset_index()
                  .dropna(subset=["age"]))

    ctrl = people[people.label == 0]
    imp = people[people.label == 1].sample(frac=1, random_state=seed)

    used, pairs = set(), []
    for _, r in imp.iterrows():
        cand = ctrl[(~ctrl.participant_id.isin(used)) &
                    (ctrl.sex == r.sex) &
                    ((ctrl.age - r.age).abs() <= max_age_diff)]
        if len(cand):
            pick = cand.loc[(cand.age - r.age).abs().idxmin(), "participant_id"]
            used.add(pick)
            pairs.append((pick, r.participant_id))

    keep_ids = {p for pair in pairs for p in pair}
    mask = meta.participant_id.isin(keep_ids).values
    return mask, len(pairs)


def main():
    ap = argparse.ArgumentParser()
    # default comes from corpus_paths.json; the old hardcoded default
    # /home/claude/pitt_cookie died with the original sandbox. The subset
    # itself is created by scripts/build_pitt_cookie.py.
    ap.add_argument("--corpus", default=None)
    ap.add_argument("--out", default="results/pitt_cookie")
    args = ap.parse_args()
    if args.corpus is None:
        args.corpus = resolve("pitt_cookie")

    os.makedirs(args.out, exist_ok=True)
    banner = "=" * 78

    # ── 1. build ────────────────────────────────────────────────────────────
    X, y, meta = build_dataset(args.corpus, use_audio=False, verbose=False)
    save_dataset(X, y, meta, args.out)
    print(banner)
    print("DATASET")
    print(banner)
    print(f"  recordings           : {len(X)}")
    print(f"  unique participants  : {meta.participant_id.nunique()}")
    print(f"  features             : {X.shape[1]}")
    print(f"  controls / impaired  : {int((y==0).sum())} / {int((y==1).sum())}")

    # ── 2. the age confound, stated explicitly ──────────────────────────────
    c = meta.loc[y == 0, "age"].dropna()
    d = meta.loc[y == 1, "age"].dropna()
    t, p = stats.ttest_ind(c, d, equal_var=False)
    print(f"\n  age (raw corpus)     : control {c.mean():.1f} vs impaired "
          f"{d.mean():.1f}   p={p:.1e}   <- confound present")

    # ── 3. match ────────────────────────────────────────────────────────────
    mask, n_pairs = match_participants(meta, y)
    Xm, ym, mm = X[mask].reset_index(drop=True), y[mask], meta[mask].reset_index(drop=True)
    c2 = mm.loc[ym == 0, "age"].dropna()
    d2 = mm.loc[ym == 1, "age"].dropna()
    t2, p2 = stats.ttest_ind(c2, d2, equal_var=False)
    print(f"\n  matched pairs        : {n_pairs} participants per group")
    print(f"  matched recordings   : {len(Xm)} "
          f"({int((ym==0).sum())} control / {int((ym==1).sum())} impaired)")
    print(f"  age (matched)        : control {c2.mean():.1f} vs impaired "
          f"{d2.mean():.1f}   p={p2:.3f}   <- confound removed")
    np.save(os.path.join(args.out, "matched_mask.npy"), mask)

    groups = mm.participant_id.values

    # ── 4. confound check on the matched set ────────────────────────────────
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedGroupKFold, cross_val_score

    def auc(Xd, yy, g):
        pipe = Pipeline([("i", SimpleImputer(strategy="median")),
                         ("s", StandardScaler()),
                         ("c", LogisticRegression(max_iter=5000))])
        cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        return cross_val_score(pipe, Xd, yy, cv=cv, groups=g,
                               scoring="roc_auc", n_jobs=-1).mean()

    print(f"\n  AUC from AGE alone   : {auc(mm[['age']].fillna(mm.age.mean()), ym, groups):.3f}"
          "   <- expected near chance after matching")
    print(f"  AUC from SPEECH      : {auc(Xm, ym, groups):.3f}")

    # ── 5. model comparison ─────────────────────────────────────────────────
    print("\n" + banner)
    print("MODEL COMPARISON  (participant-grouped stratified 5-fold CV)")
    print(banner)
    res = evaluate_models(Xm, ym, groups=groups)
    cols = ["model", "accuracy", "accuracy_sd", "roc_auc", "roc_auc_sd",
            "sensitivity", "specificity", "f1"]
    print(res[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    res.to_csv(os.path.join(args.out, "model_comparison.csv"), index=False)

    best_name = res.iloc[0]["model"]
    print(f"\n  best by ROC-AUC: {best_name}")

    # ── 6. explainability ───────────────────────────────────────────────────
    print("\n" + banner)
    print("FEATURE IMPORTANCE  (permutation, ROC-AUC)")
    print(banner)
    imp = explain_model(build_models()[best_name], Xm, ym, top_n=15)
    print(imp.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    imp.to_csv(os.path.join(args.out, "feature_importance.csv"), index=False)

    # ── 7. group statistics ─────────────────────────────────────────────────
    print("\n" + banner)
    print("GROUP DIFFERENCES  (matched cohort, Welch t-test)")
    print(banner)
    rows = []
    for f in Xm.columns:
        a = Xm.loc[ym == 0, f].dropna()
        b = Xm.loc[ym == 1, f].dropna()
        if len(a) < 10 or len(b) < 10 or a.std() == 0 or b.std() == 0:
            continue
        t3, p3 = stats.ttest_ind(a, b, equal_var=False)
        dd = (b.mean() - a.mean()) / np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
        rows.append((f, a.mean(), b.mean(), dd, p3))
    gd = (pd.DataFrame(rows, columns=["feature", "control_mean", "impaired_mean",
                                      "cohens_d", "p_value"])
            .reindex(columns=["feature", "control_mean", "impaired_mean",
                              "cohens_d", "p_value"]))
    gd["abs_d"] = gd.cohens_d.abs()
    gd = gd.sort_values("abs_d", ascending=False).drop(columns="abs_d")
    print(gd.head(15).to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    gd.to_csv(os.path.join(args.out, "group_comparison.csv"), index=False)

    # ── 8. severity: do measures track MMSE within the impaired group? ──────
    print("\n" + banner)
    print("SEVERITY  (correlation with MMSE within the impaired group)")
    print(banner)
    imp_idx = (meta.label if "label" in meta else pd.Series(y)) == 1
    sub = meta[(y == 1) & meta.mmse.notna()]
    Xs = X.loc[sub.index]
    rows = []
    for f in Xs.columns:
        v = Xs[f]
        m2 = v.notna()
        if m2.sum() < 30 or v[m2].std() == 0:
            continue
        r, p4 = stats.pearsonr(v[m2], sub.mmse[m2])
        rows.append((f, r, p4, int(m2.sum())))
    md = pd.DataFrame(rows, columns=["feature", "r_with_mmse", "p_value", "n"])
    md["abs_r"] = md.r_with_mmse.abs()
    md = md.sort_values("abs_r", ascending=False).drop(columns="abs_r")
    print(md.head(12).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    md.to_csv(os.path.join(args.out, "mmse_correlation.csv"), index=False)

    print(f"\nresults written to {args.out}/")


if __name__ == "__main__":
    main()
