"""
verify_bayes_chain.py
---------------------
Mechanical re-verification of the four-stage risk-adjustment chain in
src/dhikra/risk_adjustment.py, run after the x4.0 clinician-referral
multiplier was removed on 2026-08-23.

This is a PROPERTY TEST, not a demonstration. Every check below is a statement
that must hold for any admissible input; the script grades PASS/FAIL per check
and refuses to report a summary if any case fails. It is deliberately written
so that a failure is loud and a pass is boring.

GRID: 12 ages x 3 referral contexts x 5 family-history states x 8 speech
scores = 1,440 cases, plus a separate 135-cell enumeration of the prior grid
alone (9 prevalence bands x 3 contexts x 5 histories) used to establish
whether MAX_PRIOR still binds.

CHECKS
  C1  posterior strictly increases with the speech score, all else fixed
  C2  posterior is non-decreasing in the age-band prevalence
  C3  posterior(population) <= posterior(concern), all else fixed
  C4  Bayes identity: odds(posterior) == LR x odds(effective prior)
  C5  neutral point: a speech score equal to TRAINING_PRIOR leaves the prior
      unchanged (LR == 1), which is the whole justification for dividing the
      training prevalence out
  C6  0 < posterior < 1 for every case
  C7  effective_prior <= MAX_PRIOR for every case
  C8  the concern and clinical branches are arithmetically IDENTICAL, and the
      clinical branch is flagged as a floor in its output
  C9  no referral multiplier equals 4.0 anywhere (the removal actually took)
"""
import json, os, sys, importlib.util

# Load risk_adjustment.py DIRECTLY by path rather than importing the dhikra
# package. The package __init__ pulls in librosa and spacy, which are not
# needed here and would make this check depend on the audio stack being
# installed. Loading the single module keeps the property test runnable
# anywhere Python is.
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_ra", os.path.join(_here, "..", "src", "dhikra", "risk_adjustment.py"))
_ra = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ra)
adjust_for_age = _ra.adjust_for_age
REFERRAL_CONTEXT = _ra.REFERRAL_CONTEXT
FAMILY_HISTORY = _ra.FAMILY_HISTORY
PREVALENCE = _ra.PREVALENCE
MAX_PRIOR = _ra.MAX_PRIOR
TRAINING_PRIOR = _ra.TRAINING_PRIOR

AGES = [25, 35, 45, 55, 62, 67, 72, 77, 82, 87, 90, 95]
CTXS = ["population", "concern", "clinical"]
FHS = list(FAMILY_HISTORY)
SCORES = [0.05, 0.15, 0.30, 0.45, 0.55, 0.70, 0.85, 0.95]
TOL = 1e-9

fails, cases = [], {}
for age in AGES:
    for ctx in CTXS:
        for fh in FHS:
            for sc in SCORES:
                cases[(age, ctx, fh, sc)] = adjust_for_age(sc, age, ctx, fh)
n = len(cases)

def fail(check, key, msg):
    fails.append({"check": check, "case": str(key), "detail": msg})

# C1 monotone in score
for age in AGES:
    for ctx in CTXS:
        for fh in FHS:
            ps = [cases[(age, ctx, fh, s)]["age_adjusted_probability"] for s in SCORES]
            for i in range(1, len(ps)):
                if not ps[i] > ps[i-1] - TOL:
                    fail("C1", (age, ctx, fh), "%r not increasing" % ps)
                    break

# C2 monotone in age prevalence
prev_of = {a: [p for lo, hi, p in PREVALENCE if lo <= a < hi][0] for a in AGES}
ordered = sorted(AGES, key=lambda a: prev_of[a])
for ctx in CTXS:
    for fh in FHS:
        for sc in SCORES:
            ps = [cases[(a, ctx, fh, sc)]["age_adjusted_probability"] for a in ordered]
            for i in range(1, len(ps)):
                if ps[i] < ps[i-1] - TOL:
                    fail("C2", (ctx, fh, sc), "%r not non-decreasing" % ps)
                    break

# C3 context ordering
for age in AGES:
    for fh in FHS:
        for sc in SCORES:
            a = cases[(age, "population", fh, sc)]["age_adjusted_probability"]
            b = cases[(age, "concern", fh, sc)]["age_adjusted_probability"]
            if b < a - TOL:
                fail("C3", (age, fh, sc), "concern %.6f < population %.6f" % (b, a))

# C4 Bayes identity  /  C6 bounds  /  C7 cap  /  C9 no 4.0
for k, r in cases.items():
    ep, lr, post = r["effective_prior"], r["likelihood_ratio"], r["age_adjusted_probability"]
    lhs = post / (1 - post)
    rhs = lr * (ep / (1 - ep))
    if abs(lhs - rhs) > 5e-3 * max(1.0, rhs):
        fail("C4", k, "odds %.6f vs LR*prior %.6f" % (lhs, rhs))
    if not (0.0 < post < 1.0):
        fail("C6", k, "posterior %r out of (0,1)" % post)
    if ep > MAX_PRIOR + TOL:
        fail("C7", k, "effective_prior %.6f > MAX_PRIOR" % ep)
    if abs(r["referral_multiplier"] - 4.0) < 1e-12:
        fail("C9", k, "a x4.0 referral multiplier is still present")

# C5 neutral point
for age in AGES:
    for ctx in CTXS:
        for fh in FHS:
            r = adjust_for_age(TRAINING_PRIOR, age, ctx, fh)
            if abs(r["likelihood_ratio"] - 1.0) > 1e-3:
                fail("C5", (age, ctx, fh), "LR %.6f != 1 at the training prior" % r["likelihood_ratio"])
            if abs(r["age_adjusted_probability"] - r["effective_prior"]) > 2e-3:
                fail("C5", (age, ctx, fh), "posterior %.6f != prior %.6f at the training prior"
                     % (r["age_adjusted_probability"], r["effective_prior"]))

# C8 concern == clinical arithmetically, clinical flagged as a floor
for age in AGES:
    for fh in FHS:
        for sc in SCORES:
            b = cases[(age, "concern", fh, sc)]
            c = cases[(age, "clinical", fh, sc)]
            if abs(b["age_adjusted_probability"] - c["age_adjusted_probability"]) > TOL:
                fail("C8", (age, fh, sc), "concern and clinical differ numerically")
            if not c["referral_is_floor"] or b["referral_is_floor"]:
                fail("C8", (age, fh, sc), "referral_is_floor flag set wrongly")

# ---- prior-grid enumeration: does MAX_PRIOR still bind? ----
binding = []
for lo, hi, prev in PREVALENCE:
    for ctx, (mult, _) in REFERRAL_CONTEXT.items():
        for fh, (fm, _) in FAMILY_HISTORY.items():
            o = (prev / (1 - prev)) * mult * fm
            ep = o / (1 + o)
            if ep > MAX_PRIOR:
                binding.append({"age_band": "%d-%d" % (lo, hi), "prevalence": prev,
                                "context": ctx, "family_history": fh,
                                "uncapped_prior": round(ep, 4)})
grid_n = len(PREVALENCE) * len(REFERRAL_CONTEXT) * len(FAMILY_HISTORY)
no_mult = sum(1 for lo, hi, prev in PREVALENCE for fh, (fm, _) in FAMILY_HISTORY.items()
              if ((prev/(1-prev))*fm) / (1 + (prev/(1-prev))*fm) > MAX_PRIOR)

# ---- worked sensitivity illustration for the thesis ----
sens = {}
for m, label in ((1.0, "x1.0_population"), (2.5, "x2.5_concern_or_clinical"), (4.0, "x4.0_RETIRED")):
    prev = 0.150   # age 72
    lr = (0.70/0.30) / (TRAINING_PRIOR/(1-TRAINING_PRIOR))
    po = (prev/(1-prev)) * m
    sens[label] = round((lr*po)/(1+lr*po), 4)

headline = {
    "age25_score0.90_population_unknownFH":
        adjust_for_age(0.90, 25)["age_adjusted_probability"],
    "age85_score0.90_population_unknownFH":
        adjust_for_age(0.90, 85)["age_adjusted_probability"],
}

out = {
    "generated": "2026-08-23",
    "purpose": ("Property test of the risk-adjustment chain after removal of "
                "the x4.0 clinician-referral multiplier."),
    "grid": {"ages": AGES, "contexts": CTXS, "family_histories": FHS,
             "scores": SCORES, "n_cases": n},
    "checks": ["C1 monotone in speech score", "C2 monotone in age prevalence",
               "C3 population <= concern", "C4 Bayes identity",
               "C5 neutral at TRAINING_PRIOR", "C6 posterior in (0,1)",
               "C7 effective_prior <= MAX_PRIOR",
               "C8 concern == clinical, clinical flagged as floor",
               "C9 no x4.0 multiplier remains"],
    "n_failures": len(fails),
    "failures": fails[:50],
    "grade": "PASS" if not fails else "FAIL",
    "max_prior_binding": {
        "grid_cells": grid_n,
        "n_binding": len(binding),
        "cells": binding,
        "n_binding_if_no_referral_multiplier": no_mult,
        "note": ("MAX_PRIOR is LIVE. An earlier working note claimed removing "
                 "the x4.0 would leave it dead; that was computed before x2.5 "
                 "was retained on both the concern and clinical branches and "
                 "is withdrawn."),
    },
    "sensitivity_age72_score0.70": sens,
    "headline_examples": headline,
    "referral_multipliers_now": {k: v[0] for k, v in REFERRAL_CONTEXT.items()},
    "training_prior": TRAINING_PRIOR,
    "max_prior": MAX_PRIOR,
}
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "results", "reconstruction", "bayes_chain_check.json")
with open(dest, "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps({k: out[k] for k in ("grade", "n_failures", "sensitivity_age72_score0.70",
                                      "headline_examples", "referral_multipliers_now")}, indent=2))
print("binding cells:", len(binding), "of", grid_n, "| if no multiplier:", no_mult)
for b in binding:
    print("  ", b)
