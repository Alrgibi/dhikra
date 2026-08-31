"""
DOES THE AGE-ADJUSTED POSTERIOR DISCRIMINATE BETTER THAN THE RAW SCORE?
=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-26 BEFORE execution.
=============================================================================

WHY THIS IS NEW. The Bayesian layer has been derived (5.x, 3.12), verified
mechanically (verify_bayes_chain.py, nine properties, 1,440 cases) and sourced
(age-band prevalence table). NOBODY HAS ASKED WHETHER ITS OUTPUT DISCRIMINATES
BETTER THAN ITS INPUT. Property checks answer "is the arithmetic right"; they do
not answer "is the result more useful". A grep of every result file and of the
thesis plan finds no such test.

WHY THE INVARIANCE LEMMA (3.11) DOES NOT DISPOSE OF IT. The posterior is
    logit(P) = logit(p) - logit(pi_0) + logit(pi(age))
which is monotone in p ONLY AT FIXED AGE. Age varies between people, so the
posterior is a TWO-VARIABLE score -- an unweighted sum of the model's log
evidence and an age log-prior -- and discrimination can move in either
direction. This is exactly the case the lemma does not cover.

DESIGN
  Raw arm        the stored out-of-fold probabilities (results/summary/
                 oof_predictions.npy) -- the deployed model's own output.
  Adjusted arm   adjust_for_age(p, age, context="population",
                 family_history="unknown") -- the DEPLOYED DEFAULTS, imported
                 from committed code by path.
  Cohorts        Pitt, Delaware, and the combined development set. Same folds,
                 same people, same order. Lu is NOT read.
  Test           paired participant-clustered bootstrap of the AUC difference,
                 2000 resamples, seed 42; the same resampled people in both arms
                 within each replicate.

CRITERIA, fixed here and applied mechanically.
  PRIMARY, on the combined development set:
    ADJUSTMENT-HELPS      95% CI of AUC(adjusted) - AUC(raw) excludes zero, positive
    ADJUSTMENT-HURTS      excludes zero, negative
    ADJUSTMENT-NEUTRAL    includes zero
  DECISIVE SECONDARY, and it is the reason this script is not just three numbers:
    The same contrast on the AGE- AND SEX-MATCHED Pitt subset
    (results/pitt_cookie/matched_mask.npy). The Pitt dementia group is about
    6.6 years older than its controls BY COHORT CONSTRUCTION. Any gain from
    adding age on unmatched data may be that imbalance rather than clinical
    value. IF THE PRIMARY HELPS BUT THE MATCHED ARM DOES NOT, the gain is a
    corpus artefact and must be reported as one -- never as a clinical benefit.
  Report-and-stop.

FAMILY HISTORY. Requested, and NOT TESTABLE: no corpus in this project records
it. Pitt and Lu carry file_id, participant_id, visit, age, sex, group, mmse,
education, audio_found, label; Delaware carries no family-history field either.
The multiplier is sourced from published relative risks and cannot be validated
on any data available here. That is stated rather than worked around.

INTERPRETIVE ASYMMETRY, registered. ADJUSTMENT-NEUTRAL or ADJUSTMENT-HURTS is
not a defect. The layer's stated purpose is to convert a screening score into an
age-appropriate ABSOLUTE RISK a clinician can act on; that is a CALIBRATION job,
and 3.11 is explicit that calibration and discrimination are different
properties. A neutral result would mean the layer's value is INTERPRETIVE rather
than DISCRIMINATIVE, which is a finding about what the layer is for and belongs
in the thesis as one.
"""
import os, sys, json, importlib.util
import numpy as np, pandas as pd

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
spec = importlib.util.spec_from_file_location("_ra", os.path.join(SRC, "dhikra", "risk_adjustment.py"))
_ra = importlib.util.module_from_spec(spec); spec.loader.exec_module(_ra)

def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float)
    m = ~np.isnan(s); y, s = y[m], s[m]
    a, b = int((y == 1).sum()), int((y == 0).sum())
    if a == 0 or b == 0: return float("nan")
    r = pd.Series(s).rank().values
    return float((r[y == 1].sum() - a * (a + 1) / 2.0) / (a * b))

pm = pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm = pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pm["source"] = "Pitt"; dm["source"] = "Delaware"
meta = pd.concat([pm, dm], ignore_index=True, sort=False)
meta["raw"] = np.load(f"{R}/summary/oof_predictions.npy")
y = meta.label.values.astype(int)
post, prior = [], []
for p_, a_ in zip(meta.raw.values, meta.age.values):
    if pd.isna(a_):
        post.append(np.nan); prior.append(np.nan); continue
    d = _ra.adjust_for_age(float(p_), float(a_), "population", "unknown")
    post.append(d.get("age_adjusted_probability", d.get("probability", np.nan)))
    prior.append(d.get("prior", d.get("age_prior", np.nan)))
meta["post"] = post; meta["prior"] = prior
print(f"n = {len(meta)}   with age = {int(meta.age.notna().sum())}   "
      f"posterior computed = {int(pd.Series(post).notna().sum())}")

rng = np.random.default_rng(42)
def contrast(sel, label):
    d = meta[sel]; yy = d.label.values.astype(int)
    raw, po = d.raw.values, d.post.values
    pid = d.participant_id.astype(str).values
    uniq = np.unique(pid); idx = {p: np.where(pid == p)[0] for p in uniq}
    a_raw, a_post = auc(yy, raw), auc(yy, po)
    a_prior = auc(yy, d.prior.values)
    diffs = []
    for _ in range(2000):
        ii = np.concatenate([idx[p] for p in rng.choice(uniq, len(uniq), replace=True)])
        diffs.append(auc(yy[ii], po[ii]) - auc(yy[ii], raw[ii]))
    lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
    grade = "HELPS" if lo > 0 else "HURTS" if hi < 0 else "NEUTRAL"
    print(f"  {label:<34} raw {a_raw:.4f}   adjusted {a_post:.4f}   "
          f"delta {a_post-a_raw:+.4f} [{lo:+.4f},{hi:+.4f}]  {grade}   (age prior alone {a_prior:.4f})")
    return dict(cohort=label, n=int(len(d)), auc_raw=a_raw, auc_adjusted=a_post,
                auc_age_prior_alone=a_prior, delta=a_post - a_raw,
                ci95=[float(lo), float(hi)], grade=grade)

print("\nPAIRED CONTRAST, participant-clustered bootstrap, 2000 resamples, seed 42\n")
out = {}
out["combined"] = contrast(meta.age.notna(), "COMBINED (primary)")
out["pitt"] = contrast((meta.source == "Pitt") & meta.age.notna(), "Pitt")
out["delaware"] = contrast((meta.source == "Delaware") & meta.age.notna(), "Delaware")

mask_path = f"{R}/pitt_cookie/matched_mask.npy"
if os.path.exists(mask_path):
    mm = np.load(mask_path)
    sel = pd.Series(False, index=meta.index)
    sel.iloc[np.where(meta.source.values == "Pitt")[0][mm]] = True
    print()
    out["pitt_matched"] = contrast(sel & meta.age.notna(), "Pitt, AGE-MATCHED (decisive)")
else:
    print("\n  matched_mask.npy not found -- decisive secondary NOT run")

print(f"\nPRIMARY GRADE: ADJUSTMENT-{out['combined']['grade']}")
if "pitt_matched" in out:
    print(f"MATCHED-SUBSET GRADE: ADJUSTMENT-{out['pitt_matched']['grade']}")
json.dump(dict(registration="module docstring, committed before execution",
    family_history="NOT TESTABLE -- no corpus in this project records it",
    context="population", family_history_arg="unknown", results=out,
    governance="Lu not read; no model, feature or threshold changed; the layer is already deployed"),
    open(f"{R}/reconstruction/age_adjustment_discrimination.json", "w"), indent=2)
print("\nwritten: results/reconstruction/age_adjustment_discrimination.json")
