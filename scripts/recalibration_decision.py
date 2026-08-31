"""
recalibration_decision.py -- should the Bayesian chain use a recalibrated score?

=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-23 BEFORE execution.
=============================================================================

THE PROBLEM (THESIS_PLAN sect 5.4.1). risk_adjustment.py derives a likelihood
ratio by dividing model odds by the training prevalence. That is exact only for
a CALIBRATED score. The development calibration slope is 1.289 > 1, so
predictions are compressed toward the middle, the derived LR is pulled toward
1, and the speech evidence is systematically under-weighted -- by up to 0.16 in
posterior probability at high scores.

THE CANDIDATE FIX. Cox logistic recalibration, the textbook two-parameter
correction (Cox 1958; Miller et al. 1991; Steyerberg, Clinical Prediction
Models): p* = expit(a + b*logit(p)). It is a DERIVATION, not a tuning exercise:
two parameters, estimated by maximum likelihood, no search, no hyperparameters.

WHAT THE FIX CANNOT DISTURB, and this is why it is even considerable:
recalibration with b > 0 is STRICTLY MONOTONE. Ranking is preserved, so AUC is
identical, and every threshold-based operating point is identical under the
correspondingly transformed threshold. The deployed 0.367 screening decision,
the locked external AUC, sensitivity and specificity are ALL INVARIANT. Only
the reported probability from the risk layer changes.

=============================================================================
THE GOVERNANCE PROBLEM, AND HOW IT IS HANDLED
=============================================================================
The obvious way to test whether recalibration helps is to try it on the locked
external corpus. THAT IS FORBIDDEN AND IS NOT DONE HERE. Using Lu to decide
whether to modify the deployed risk layer would be precisely the contamination
that sect 3.9 documents -- an external result informing a development decision --
committed deliberately after writing that section. It would be indefensible.

THE DECISION IS THEREFORE MADE ON DEVELOPMENT DATA ONLY, by cross-cohort
transfer of the recalibration itself:
    fit the two coefficients on PITT out-of-fold predictions, apply to DELAWARE
    fit the two coefficients on DELAWARE out-of-fold predictions, apply to PITT
Each direction is an honest out-of-sample test of whether a recalibration
estimated on one cohort improves calibration on a cohort it has not seen. This
is the deployment question in miniature.

DECISION CRITERIA, fixed in advance, judged on the TWO CROSS-COHORT ARMS ONLY:
  CORRECTION-TRANSFERS -- in BOTH directions the applied recalibration moves
      the calibration slope closer to 1 AND does not worsen Brier by more than
      0.005. => APPLY the correction inside the likelihood-ratio derivation,
      and report both the defect and the fix.
  CORRECTION-DOES-NOT-TRANSFER -- anything else. => DO NOT APPLY. Report the
      defect, its magnitude, its direction and its containment, and report that
      the obvious correction was tested and did not transfer.

Both outcomes are reportable and the write-up is decided by the grade, not by
which is more flattering.

REGISTERED INTERPRETIVE ASYMMETRY / THE LU CHECK. The stored Lu predictions
(already released, already reported) are ALSO scored here, raw and corrected,
as a DESCRIPTIVE post hoc check of the same category as the A5 false-positive
characterisation. IT DOES NOT ENTER THE DECISION, WHATEVER IT SHOWS. This is
declared here, before the numbers exist, so that a reader can see the decision
rule was fixed independently of it. If the Lu check disagrees with the
development decision, that disagreement is reported as a caveat and the
decision still stands as the development arms determined it.

GOVERNANCE: no model is trained, refit or re-scored. Lu is not re-scored; only
its already-released stored predictions are read. The deployed threshold does
not move.

REGISTRATION HISTORY
  (none)
"""
import json, math, os
import numpy as np

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
os.chdir(REPO)
lg = lambda p: np.log(p / (1 - p))
ex = lambda z: 1 / (1 + np.exp(-z))
CLIP = lambda p: np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)


def cox_fit(p, y):
    """Unpenalised logistic recalibration: logit(y) ~ a + b*logit(p).
    C=1e9 matches the committed calibration_block(); a penalty shrinks b and
    understates miscalibration (calibration_slope_resolution.json)."""
    from sklearn.linear_model import LogisticRegression
    z = lg(CLIP(p)).reshape(-1, 1)
    m = LogisticRegression(C=1e9, solver="lbfgs", max_iter=5000).fit(z, y)
    return float(m.intercept_[0]), float(m.coef_[0][0])


def apply_cox(p, a, b):
    return ex(a + b * lg(CLIP(p)))


def brier(p, y):
    return float(np.mean((np.asarray(p, float) - np.asarray(y, float)) ** 2))


def assess(p, y):
    a, b = cox_fit(p, y)
    return {"slope": round(b, 4), "intercept": round(a, 4), "brier": round(brier(p, y), 4),
            "abs_slope_error": round(abs(b - 1.0), 4)}


def dev():
    p = CLIP(np.load("results/summary/oof_predictions.npy"))
    y = np.load("results/summary/oof_labels.npy").astype(int)
    s = np.array([str(v) for v in np.load("results/summary/oof_source.npy", allow_pickle=True)])
    return p, y, s


def lu():
    d = json.load(open("results/reconstruction/lu_oneshot_reproduction.json"))["predictions"]
    return CLIP([r["p"] for r in d]), np.array([r["label"] for r in d], int)


if __name__ == "__main__":
    p, y, s = dev()
    out = {"generated": "2026-08-23",
           "preregistration": "criteria fixed in this script's docstring before execution",
           "governance": "no model refit; Lu not re-scored, only its released predictions read; "
                         "Lu DID NOT enter the decision, by pre-registration"}

    # ---- in-sample reference (expected to be near-perfect; reported to show it is circular)
    a_all, b_all = cox_fit(p, y)
    out["development_pooled"] = {
        "raw": assess(p, y),
        "coefficients_fitted_here": {"intercept": round(a_all, 4), "slope": round(b_all, 4)},
        "corrected_IN_SAMPLE": assess(apply_cox(p, a_all, b_all), y),
        "note": "the corrected row is CIRCULAR by construction -- the coefficients were fitted on "
                "these same points. Shown only to confirm the arithmetic, never as evidence."}

    # ---- THE DECISION: cross-cohort transfer, development only
    arms = {}
    for src, tgt in (("Pitt", "Delaware"), ("Delaware", "Pitt")):
        a, b = cox_fit(p[s == src], y[s == src])
        pt, yt = p[s == tgt], y[s == tgt]
        raw, cor = assess(pt, yt), assess(apply_cox(pt, a, b), yt)
        arms[f"{src}->{tgt}"] = {
            "coefficients_from_source": {"intercept": round(a, 4), "slope": round(b, 4)},
            "target_raw": raw, "target_corrected": cor,
            "slope_moved_toward_1": cor["abs_slope_error"] < raw["abs_slope_error"],
            "brier_not_worse_by_0.005": cor["brier"] <= raw["brier"] + 0.005}
    out["decision_arms_development_only"] = arms
    ok = all(v["slope_moved_toward_1"] and v["brier_not_worse_by_0.005"] for v in arms.values())
    out["GRADE"] = "CORRECTION-TRANSFERS" if ok else "CORRECTION-DOES-NOT-TRANSFER"
    out["DECISION"] = ("APPLY the recalibration inside the likelihood-ratio derivation; report the "
                       "defect and the fix" if ok else
                       "DO NOT APPLY. Report the defect, its magnitude, its direction, its "
                       "containment, and that the obvious correction was tested and did not transfer")

    # ---- descriptive, post hoc, DID NOT ENTER THE DECISION
    lp, ly = lu()
    a_all, b_all = cox_fit(p, y)
    out["lu_descriptive_post_hoc"] = {
        "DECLARED_BEFORE_EXECUTION": "does not enter the decision, whatever it shows",
        "n": int(len(ly)),
        "raw": assess(lp, ly),
        "corrected_with_development_coefficients": assess(apply_cox(lp, a_all, b_all), ly),
        "classification_at_0.367_unchanged": bool(
            ((lp >= 0.367).astype(int) ==
             (apply_cox(lp, a_all, b_all) >= apply_cox(np.array([0.367]), a_all, b_all)[0]).astype(int)).all()),
        "note": "monotone transform, so AUC, sensitivity and specificity are invariant by construction"}

    json.dump(out, open("results/reconstruction/recalibration_decision.json", "w"), indent=2)
    print("GRADE:", out["GRADE"])
    for k, v in arms.items():
        print("  %-20s raw slope %.3f -> corrected %.3f | brier %.4f -> %.4f | toward1=%s brier_ok=%s"
              % (k, v["target_raw"]["slope"], v["target_corrected"]["slope"],
                 v["target_raw"]["brier"], v["target_corrected"]["brier"],
                 v["slope_moved_toward_1"], v["brier_not_worse_by_0.005"]))
    l = out["lu_descriptive_post_hoc"]
    print("  LU (post hoc, not in decision): slope %.3f -> %.3f | brier %.4f -> %.4f | classifications unchanged: %s"
          % (l["raw"]["slope"], l["corrected_with_development_coefficients"]["slope"],
             l["raw"]["brier"], l["corrected_with_development_coefficients"]["brier"],
             l["classification_at_0.367_unchanged"]))
