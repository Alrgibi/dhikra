#!/usr/bin/env python3
"""
age_flatness_check.py -- provenance recovery for the section 3.12 age-flatness
figures.

WHY THIS EXISTS. THESIS_PLAN.md section 3.12 tests the conditional-independence
assumption behind applying an age-specific prevalence on top of the model's
likelihood ratio: on the 987 development recordings, the correlation between
the model's log-odds and age is -0.084 (p = 0.054) within controls and +0.025
(p = 0.593) within the impaired; the within-control drift is -0.0070 log-odds
per year, an evidence shift of LR x 0.87 across twenty years; the pooled
correlation is +0.091; and age alone ranks the label at AUC 0.6308. Those
figures trace to no result file and no committed script. This script recomputes
every one of them from the stored out-of-fold vector and the committed meta
files -- the frozen model is not refit and no recording is rescored.

DATA AND ALIGNMENT. results/summary/oof_predictions.npy is the stored
out-of-fold probability vector for the 987-recording development pool, in the
order train_development.py assembles it (Pitt features.csv rows, then Delaware
cookie rows). Alignment is asserted, not assumed: the run is VOID unless
oof_labels.npy equals the concatenated meta labels element for element and the
vector length is 987.

CRITERIA -- fixed in this docstring before execution; grading mechanical;
report-and-stop. A figure that does not reproduce is reported and the prose is
corrected to the reproduced value; no criterion moves and the run is not
iterated. log-odds = logit(p) on the stored probabilities (no clipping needed;
the stored vector lies in [0.15, 0.88]). Correlations are Pearson.

  a1  pooled corr(log-odds, age), n = 987           +0.091            (+/- 0.005)
  a2  corr within controls                          -0.084, p 0.054   (+/- 0.004; p +/- 0.02)
  a3  corr within impaired                          +0.025, p 0.593   (+/- 0.004; p +/- 0.05)
  a4  OLS slope of log-odds on age, controls        -0.0070 per year  (+/- 0.0005)
  a5  exp(20 x a4)                                  0.87              (+/- 0.01)
  a6  rank AUC of age alone for the label           0.6308            (+/- 0.003)

Also recorded descriptively (no criterion; already twice-witnessed in
recalibration_decision.json and oof_vector_diagnostic.json): the unregularised
logistic fit of label on log-odds over the stored vector -- slope and intercept.

Output: results/reconstruction/age_flatness_check.json
"""
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, rankdata
from scipy.optimize import minimize

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = os.path.join(ROOT, "results")


def rank_auc(score, y):
    r = rankdata(score)
    n1 = int(y.sum())
    n0 = len(y) - n1
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1))


def cox_fit(logodds, y):
    """Unregularised logistic fit of y on logit(p): logit p* = a + b * logit p."""
    def nll(w):
        a, b = w
        z = a + b * logodds
        return float(np.sum(np.logaddexp(0, z)) - np.sum(y * z))
    res = minimize(nll, x0=np.array([0.0, 1.0]), method="BFGS")
    a, b = res.x
    return float(b), float(a)


def main():
    p = np.load(os.path.join(R, "summary/oof_predictions.npy"))
    ylab = np.load(os.path.join(R, "summary/oof_labels.npy")).astype(int)
    mp = pd.read_csv(os.path.join(R, "pitt_cookie/meta.csv"))
    md = pd.read_csv(os.path.join(R, "delaware/cookie_meta.csv"))

    assert len(p) == len(ylab) == 987, "VOID: vector length is not 987"
    labels_meta = np.concatenate([mp.label.values, md.label.values]).astype(int)
    assert np.array_equal(ylab, labels_meta), \
        "VOID: stored labels do not equal the concatenated meta labels -- alignment unproven"

    age = np.concatenate([mp.age.values, md.age.values]).astype(float)
    assert np.isfinite(age).all(), "VOID: missing age values -- population differs from the claim's"

    lo = np.log(p / (1 - p))
    ctrl, imp = ylab == 0, ylab == 1

    r_all, p_all = pearsonr(lo, age)
    r_c, p_c = pearsonr(lo[ctrl], age[ctrl])
    r_i, p_i = pearsonr(lo[imp], age[imp])
    slope_c = float(np.polyfit(age[ctrl], lo[ctrl], 1)[0])
    lr20 = float(np.exp(20 * slope_c))
    auc_age = rank_auc(age, ylab)
    b, a = cox_fit(lo, ylab)

    values = {
        "pooled_corr": float(r_all), "pooled_p": float(p_all),
        "control_corr": float(r_c), "control_p": float(p_c),
        "impaired_corr": float(r_i), "impaired_p": float(p_i),
        "control_slope_per_year": slope_c,
        "lr_factor_20y": lr20,
        "age_alone_auc": auc_age,
        "n": 987, "n_controls": int(ctrl.sum()), "n_impaired": int(imp.sum()),
        "cox_on_stored_vector": {"slope": b, "intercept": a,
                                 "note": "descriptive third witness; criteria carried by a1-a6 only"},
    }

    claims = {
        "pooled_corr": (0.091, 0.005),
        "control_corr": (-0.084, 0.004),
        "control_p": (0.054, 0.02),
        "impaired_corr": (0.025, 0.004),
        "impaired_p": (0.593, 0.05),
        "control_slope_per_year": (-0.0070, 0.0005),
        "lr_factor_20y": (0.87, 0.01),
        "age_alone_auc": (0.6308, 0.003),
    }
    graded = {}
    for k, (target, tol) in claims.items():
        v = values[k]
        graded[k] = {"claimed": target, "recomputed": v, "delta": v - target,
                     "tolerance": tol, "reproduced": bool(abs(v - target) <= tol)}
    n_ok = sum(1 for g in graded.values() if g["reproduced"])
    verdict = "REPRODUCED" if n_ok == len(claims) else "PARTIAL"

    out = {
        "script": "scripts/age_flatness_check.py",
        "purpose": "provenance recovery: recompute the section 3.12 age-flatness figures from the stored out-of-fold vector; frozen model untouched, nothing rescored",
        "criteria": "fixed in the module docstring before execution; report-and-stop",
        "alignment": "oof_labels.npy == concat(meta labels) asserted element for element",
        "values": values,
        "graded": graded,
        "n_reproduced": n_ok, "n_claims": len(claims),
        "VERDICT": verdict,
    }
    dst = os.path.join(R, "reconstruction/age_flatness_check.json")
    json.dump(out, open(dst, "w"), indent=2)
    print("written:", dst)
    print("VERDICT:", verdict, "(%d/%d)" % (n_ok, len(claims)))
    for k, g in graded.items():
        flag = "OK " if g["reproduced"] else "DIFF"
        print("  %s %-24s claimed %-8s got %.6g" % (flag, k, g["claimed"], g["recomputed"]))
    print("  cox on stored vector: slope %.4f intercept %.4f" % (b, a))


if __name__ == "__main__":
    main()
