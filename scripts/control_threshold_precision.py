"""
control_threshold_precision.py
------------------------------
How many healthy controls does a control-referenced threshold need?

CONTEXT. The specificity problem (THESIS_PLAN sect 5.15-5.19) is a threshold
REFERENCING problem, and the remedy analysed there is to set the threshold at a
fixed percentile of the LOCAL healthy-control score distribution. That rule
fixes specificity by construction -- but only up to the sampling error of the
control sample that defines it. This script computes that error EXACTLY.

THE RESULT, which needs no simulation and no distributional assumption.
Let the threshold be the k-th order statistic of n iid healthy control scores,
k = ceil(0.80 * n). The proportion of a fresh healthy population falling below
that threshold is the value of the population CDF at a sample order statistic,
and that quantity is distribution-free:

    achieved_specificity ~ Beta(k, n + 1 - k)

This is the standard nonparametric-tolerance result (Wilks 1941). It holds for
any continuous score distribution, so it applies to a Libyan cohort whose score
distribution is unknown and cannot be assumed to match any American corpus.

WHY IT MATTERS FOR THIS PROJECT. The bootstrap interval reported for the rule
on the Lu corpus -- specificity 0.774, 95% CI [0.69, 0.80] on 27 controls -- is
an IN-SAMPLE quantity: the same 27 controls defined the threshold and were then
scored against it. That is why the interval cannot exceed the 0.80 target. The
Beta interval below answers the different, prospective question, and for n = 27
it is [0.62, 0.91] -- appreciably wider. Both belong in the write-up, labelled.

No model is loaded and no corpus is touched. This is arithmetic.
"""
import json, os
from math import comb, ceil


def beta_cdf_int(x, a, b):
    """Exact CDF of Beta(a, b) for INTEGER a, b, via the binomial identity
    I_x(a, b) = sum_{j=a}^{a+b-1} C(a+b-1, j) x^j (1-x)^{a+b-1-j}."""
    n = a + b - 1
    return sum(comb(n, j) * x ** j * (1 - x) ** (n - j) for j in range(a, n + 1))


def beta_ppf_int(p, a, b, tol=1e-12):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if beta_cdf_int(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2


def row(n, target=0.80):
    k = ceil(target * n)
    a, b = k, n + 1 - k
    return {
        "n_controls": n,
        "order_statistic_k": k,
        "expected_specificity": round(a / (a + b), 4),
        "median_specificity": round(beta_ppf_int(0.50, a, b), 4),
        "ci95": [round(beta_ppf_int(0.025, a, b), 4),
                 round(beta_ppf_int(0.975, a, b), 4)],
        "ci95_width": round(beta_ppf_int(0.975, a, b) - beta_ppf_int(0.025, a, b), 4),
    }


def n_for_width(w, target=0.80, cap=2000):
    for n in range(10, cap):
        if row(n, target)["ci95_width"] <= w:
            return n
    return None


TABLE = [row(n) for n in (15, 20, 25, 27, 30, 40, 50, 75, 100, 150, 200)]
out = {
    "generated": "2026-08-23",
    "question": ("Prospective specificity of a control-referenced threshold set "
                 "at the 80th percentile of n local healthy controls."),
    "result": "achieved specificity ~ Beta(k, n+1-k), k = ceil(0.80n); exact and distribution-free (Wilks 1941)",
    "target_percentile": 0.80,
    "table": TABLE,
    "sample_size_for_interval_width": {
        "0.20": n_for_width(0.20),
        "0.15": n_for_width(0.15),
        "0.10": n_for_width(0.10),
    },
    "lu_comparison": {
        "n_controls": 27,
        "in_sample_bootstrap_specificity": 0.774,
        "in_sample_bootstrap_ci95": [0.69, 0.80],
        "prospective_beta_ci95": row(27)["ci95"],
        "note": ("The bootstrap interval is in-sample -- the same 27 controls set "
                 "the threshold and were scored against it, which is why it cannot "
                 "exceed the 0.80 target. It measures how precisely the rule hits "
                 "its own target. The Beta interval measures what a new population "
                 "would experience. Report both, labelled."),
    },
    "pilot_implication": ("docs/libyan_pilot_protocol.md targets 20 healthy "
                          "participants, giving [0.56, 0.91]. n >= 30 is the point "
                          "at which the normative deliverable is worth publishing; "
                          "59 buys a +/-10-point interval and 108 a +/-7.5-point one."),
    "caveat": ("Assumes the local control sample is iid from the population the "
               "threshold will be applied to. It says nothing about sensitivity, "
               "and it is not a validation result."),
}
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "results", "reconstruction", "control_threshold_precision.json")
with open(dest, "w") as f:
    json.dump(out, f, indent=2)
print("%5s %4s %9s   %s" % ("n", "k", "E[spec]", "95% interval"))
for r in TABLE:
    print("%5d %4d %9.3f   [%.3f, %.3f]  width %.3f"
          % (r["n_controls"], r["order_statistic_k"], r["expected_specificity"],
             r["ci95"][0], r["ci95"][1], r["ci95_width"]))
print("\nwidth <= 0.20 needs n =", out["sample_size_for_interval_width"]["0.20"])
print("width <= 0.15 needs n =", out["sample_size_for_interval_width"]["0.15"])
print("width <= 0.10 needs n =", out["sample_size_for_interval_width"]["0.10"])
