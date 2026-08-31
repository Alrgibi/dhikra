"""
train.py
--------
THE command to run once the DementiaBank corpus is available.

    python scripts/train.py --corpus /path/to/dementiabank/Pitt

It builds the feature matrix, evaluates every model with leakage-free repeated
cross-validation, prints the clinical metrics table, reports which speech
measures drove the decision, and writes everything to results/.

Run with --simulate to exercise the whole pipeline on the synthetic test
cohort instead (no data required). Anything produced in --simulate mode is a
pipeline check, NOT a research result.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from dhikra.model import (build_models, evaluate_models, explain_model,
                          linear_coefficients, report)

pd.set_option("display.width", 220)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", help="path to the corpus root (folder of .cha files)")
    ap.add_argument("--simulate", action="store_true",
                    help="use the synthetic test cohort instead of real data")
    ap.add_argument("--no-audio", action="store_true",
                    help="transcripts only, skip acoustic extraction")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    if args.simulate:
        from simulate_cohort import simulate_cohort
        print(">>> SIMULATION MODE - pipeline check only, NOT results <<<\n")
        X, y, meta = simulate_cohort()
    elif args.corpus:
        from dhikra.corpus import build_dataset, save_dataset
        X, y, meta = build_dataset(args.corpus, use_audio=not args.no_audio)
        save_dataset(X, y, meta)
    else:
        ap.error("provide --corpus PATH or --simulate")

    os.makedirs(args.out, exist_ok=True)

    print(f"\ndataset: {X.shape[0]} recordings x {X.shape[1]} features")
    print(f"  controls={int((y == 0).sum())}   impaired={int((y == 1).sum())}\n")

    # ---- model comparison ----
    print("=" * 78)
    print("MODEL COMPARISON  (repeated stratified 5-fold CV, 10 repeats)")
    print("=" * 78)
    res = evaluate_models(X, y)
    cols = ["model", "accuracy", "accuracy_sd", "roc_auc",
            "sensitivity", "specificity", "f1"]
    print(res[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    res.to_csv(os.path.join(args.out, "model_comparison.csv"), index=False)

    best_name = res.iloc[0]["model"]
    models = build_models()
    best = models[best_name]
    print(f"\nbest by ROC-AUC: {best_name}")

    # ---- detailed clinical report ----
    print("\n" + "=" * 78)
    print(f"CLINICAL REPORT  ({best_name}, out-of-fold predictions)")
    print("=" * 78)
    print(report(best, X, y))

    # ---- explainability ----
    print("\n" + "=" * 78)
    print("FEATURE IMPORTANCE  (permutation, scoring = ROC-AUC)")
    print("=" * 78)
    imp = explain_model(best, X, y, top_n=15)
    print(imp.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    imp.to_csv(os.path.join(args.out, "feature_importance.csv"), index=False)

    # ---- interpretable direction ----
    print("\n" + "=" * 78)
    print("SIGNED COEFFICIENTS  (Logistic Regression - direction of effect)")
    print("=" * 78)
    co = linear_coefficients(models["Logistic Regression"], X, y, top_n=15)
    for _, r in co.iterrows():
        arrow = "higher -> MORE risk" if r["coefficient"] > 0 else "higher -> LESS risk"
        print(f"  {r['feature']:36s} {r['coefficient']:+.3f}   {arrow}")
    co.to_csv(os.path.join(args.out, "coefficients.csv"), index=False)

    print(f"\nresults written to {args.out}/")


if __name__ == "__main__":
    main()
