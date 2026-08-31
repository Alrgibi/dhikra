"""
stimulus_inventory_probe.py
===========================
PRE-REGISTERED.  Criteria below were written and committed BEFORE the script
was executed.  Report-and-stop: the grid, the cohort and the grades are fixed
here and are not revised after seeing output.

THE QUESTION
------------
The calibrated model was fitted on descriptions of the Cookie Theft picture
(Boston Diagnostic Aphasia Examination).  The deployed app does not show that
picture -- it shows an original scene, `scene_kitchen.svg`, drawn for this
project because the Cookie Theft is not redistributable.  The information-unit
scorer, however, still applies the Cookie Theft key: the 23 units in
`information_units.SCENES["kitchen"]`.

Direct inspection of the rendered stimulus on 2026-08-26 found:

  (a) two units in the key -- `curtain` and `dishcloth` -- were NOT DEPICTED in
      the deployed picture, and so could not be earned by any speaker,
      however intact;
  (b) the deployed picture contains salient content with NO slot in the key
      (a cat, a teapot on a stove, bread, a table, a palm tree), for which a
      speaker earns nothing.

(a) is a defect of omission and has been corrected in the artwork.  (b) cannot
be corrected by editing the key, because the key defines the model's input and
the model is frozen: changing the key changes `iu.*` for the training
transcripts and voids the calibration.  (b) is therefore permanent, and its
only possible effect is behavioural -- attention spent naming unscored content
is attention not spent naming scored content.

Neither effect is measurable without Libyan data.  What IS answerable now, from
the frozen model alone, is the inverse question:

    HOW MANY INFORMATION UNITS WOULD THE SUBSTITUTED STIMULUS HAVE TO COST A
    SPEAKER BEFORE THE SCREENING DECISION CHANGES?

COHORT AND GOVERNANCE
---------------------
Pittsburgh development cohort, `results/pitt_cookie/features.csv`.  Lu is NOT
touched: this is not a performance claim and requires no held-out set.  No
model is fitted, refitted or recalibrated.  The frozen bundle
`models/dhikra_model.pkl` is loaded and ONLY ITS INPUTS ARE PERTURBED.  The
feature set and the threshold carried in the bundle are used as they stand.

PERTURBATION
------------
To make a unit u unearnable for a row: set iu.has_u = 0, decrement the owning
category count (iu.subjects / iu.places / iu.objects / iu.actions) and
iu.total by 1, then recompute the three derived features by the formulas in
information_units.extract_information_units:

    iu.proportion        = iu.total / 23
    iu.per_100_words     = 100 * iu.total / n_words
    iu.action_object_ratio = iu.actions / max(iu.objects, 1)

n_words is recovered from the unperturbed row as
    n_words = 100 * iu.total / iu.per_100_words
which is exact where iu.total > 0; rows with iu.total == 0 are left unchanged
(nothing can be removed from them).  All other features are untouched.

ANALYSES
--------
A. THE DEFECT AS IT STOOD.  Make `curtain` and `dishcloth` unearnable for every
   row.  Report the change in mean probability, the number and percentage of
   rows crossing from p < tau to p >= tau, and sensitivity and specificity at
   tau before and after.

B. RESIDUAL DISPLACEMENT.  For k = 1..6, remove k units drawn uniformly at
   random WITHOUT replacement from the units that row actually earned
   (40 repetitions, seed 42).  Report the mean crossing rate, overall and
   among controls.  k = 6 is the pessimistic bound: the deployed picture has
   six salient unscored elements, so no more than six scored mentions can be
   displaced by them.

GRADES -- FIXED BEFORE EXECUTION
--------------------------------
A is PRE-EDIT-DEFECT-MATERIAL if removing curtain+dishcloth either moves
specificity at tau by >= 5 percentage points, or crosses >= 5% of CONTROL rows
from below tau to at-or-above tau.  Otherwise PRE-EDIT-DEFECT-CONTAINED.

B is DISPLACEMENT-MATERIAL   if the mean control crossing rate at k = 2 is >= 10%;
     DISPLACEMENT-MINOR      if < 10% at k = 2 but >= 10% at k = 4;
     DISPLACEMENT-NEGLIGIBLE if < 10% at k = 4.

REGISTERED INTERPRETIVE ASYMMETRY
---------------------------------
MATERIAL on either arm means the deployed app cannot report a probability from
this stimulus without a stated correction, and the substitution enters the
thesis as a quantified limitation of the parallel-form design.
CONTAINED / NEGLIGIBLE is reported as a bounded limitation and the app is
unchanged.  NEITHER OUTCOME LICENSES CHANGING THE MODEL, THE FEATURE SET OR THE
THRESHOLD.  A result in the unwanted direction is reported at full strength.

HARNESS AMENDMENT #1 -- recorded BEFORE any result was seen
-----------------------------------------------------------
The device shell imposes a 45-second wall-clock limit per call and background
jobs do not survive it.  The analysis is therefore executed in PARTS
(`--part A`, `--part B --k N`, `--combine`), each caching to
results/_partial_stimulus_probe/.  This changes NOTHING about the cohort, the
perturbation, the k grid, the repetition count, the seed or the grades, all of
which are as registered above.  It is a change to how the computation is
scheduled, not to what is computed.

HARNESS AMENDMENT #2 -- recorded BEFORE any Part B result was seen
------------------------------------------------------------------
A single `predict_proba` call costs 1.52 s on 548 rows and 2.03 s on 5 480:
the cost is almost entirely fixed overhead.  Part B therefore builds all 40
perturbed replicates into one frame and predicts once per k, instead of once
per replicate.  The rows, the model, the random draws and their order are
identical; only the number of calls changes.

DISCLOSED INCOMPLETENESS IN THIS REGISTRATION
---------------------------------------------
The registration fixes "40 repetitions, seed 42" but does not state how the
seed maps to k.  The implementation uses default_rng(42 + 1000*k).  This is a
gap in the registration and is recorded as one.  It is immaterial to every
grade: the estimand is a mean over 40 replicates, the criterion is a
percentage, and the between-replicate standard deviation is reported alongside
each figure (1.2-1.5 percentage points, against an effect of 13.1 at k = 1).
It is NOT listed among the under-specifications in THESIS_PLAN 3.10, which
records registrations that turned out ambiguous in a way that changed what was
computed; this one did not.

UNIT OF ANALYSIS
----------------
Rows are RECORDINGS, not participants: the Pittsburgh cohort has repeat visits,
so 548 recordings come from fewer people.  Every percentage below is a
percentage of recordings.  The grades were written in rows for that reason.

OUTPUT
------
results/stimulus_inventory_probe.json
"""
from __future__ import annotations
import json, os, pickle, sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from dhikra.information_units import SUBJECTS, PLACES, OBJECTS, ACTIONS  # noqa

N_UNITS = 23
CATEGORY = {}
for u in SUBJECTS: CATEGORY[u] = "iu.subjects"
for u in PLACES:   CATEGORY[u] = "iu.places"
for u in OBJECTS:  CATEGORY[u] = "iu.objects"
for u in ACTIONS:  CATEGORY[u] = "iu.actions"
assert len(CATEGORY) == N_UNITS, len(CATEGORY)

RNG_SEED = 42
N_REPS = 40
K_GRID = [1, 2, 3, 4, 5, 6]


def recompute(df: pd.DataFrame, nwords: np.ndarray) -> pd.DataFrame:
    df = df.copy()
    tot = df["iu.total"].to_numpy(float)
    df["iu.proportion"] = tot / N_UNITS
    with np.errstate(divide="ignore", invalid="ignore"):
        df["iu.per_100_words"] = np.where(nwords > 0, 100.0 * tot / nwords,
                                          df["iu.per_100_words"])
    df["iu.action_object_ratio"] = (df["iu.actions"].to_numpy(float)
                                    / np.maximum(df["iu.objects"].to_numpy(float), 1.0))
    return df


def remove_units(df: pd.DataFrame, nwords: np.ndarray, mask: np.ndarray,
                 units: list[str]) -> pd.DataFrame:
    """mask[i, j] == True -> remove units[j] from row i (only where earned)."""
    out = df.copy()
    for j, u in enumerate(units):
        col = f"iu.has_{u}"
        hit = mask[:, j] & (out[col].to_numpy(float) > 0)
        if not hit.any():
            continue
        out.loc[hit, col] = 0.0
        out.loc[hit, CATEGORY[u]] = out.loc[hit, CATEGORY[u]] - 1.0
        out.loc[hit, "iu.total"] = out.loc[hit, "iu.total"] - 1.0
    return recompute(out, nwords)


PART_DIR = None


def _load():
    with open(os.path.join(ROOT, "models", "dhikra_model.pkl"), "rb") as f:
        bundle = pickle.load(f)
    model, feats = bundle["model"], list(bundle["features"])
    tau = float(bundle.get("screening_threshold", 0.367))
    X = pd.read_csv(os.path.join(ROOT, "results", "pitt_cookie", "features.csv"))
    M = pd.read_csv(os.path.join(ROOT, "results", "pitt_cookie", "meta.csv"))
    assert len(X) == len(M), (len(X), len(M))
    y = M["label"].to_numpy(int)
    tot0 = X["iu.total"].to_numpy(float)
    p100 = X["iu.per_100_words"].to_numpy(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        nwords = np.where(p100 > 0, 100.0 * tot0 / p100, 0.0)
    p0 = model.predict_proba(X[feats])[:, 1]
    return model, feats, tau, X, y, nwords, p0


def part_A(pd_dir):
    model, feats, tau, X, y, nwords, p0 = _load()
    ctrl = y == 0

    def rates(p):
        return (float((p[y == 1] >= tau).mean()), float((p[ctrl] < tau).mean()))

    sens0, spec0 = rates(p0)
    units_A = ["curtain", "dishcloth"]
    XA = remove_units(X, nwords, np.ones((len(X), 2), bool), units_A)
    pA = model.predict_proba(XA[feats])[:, 1]
    sensA, specA = rates(pA)
    crossed = (p0 < tau) & (pA >= tau)
    out = {
        "threshold": tau, "n_rows": int(len(X)),
        "baseline": {"mean_p": float(p0.mean()), "sensitivity": sens0,
                     "specificity": spec0, "n_above": int((p0 >= tau).sum())},
        "unit_prevalence": {
            u: {"overall": float(X["iu.has_" + u].mean()),
                "controls": float(X.loc[ctrl, "iu.has_" + u].mean()),
                "impaired": float(X.loc[y == 1, "iu.has_" + u].mean())}
            for u in ("curtain", "dishcloth", "cookie", "water", "faucet",
                      "counter", "jar", "stool")},
        "A_pre_edit_defect": {
            "units_removed": units_A,
            "mean_p_before": float(p0.mean()), "mean_p_after": float(pA.mean()),
            "mean_delta_p": float((pA - p0).mean()),
            "max_delta_p": float((pA - p0).max()),
            "n_crossed": int(crossed.sum()),
            "pct_crossed_all": float(100.0 * crossed.mean()),
            "pct_crossed_controls": float(100.0 * crossed[ctrl].mean()),
            "sensitivity_before": sens0, "sensitivity_after": sensA,
            "specificity_before": spec0, "specificity_after": specA,
            "specificity_drop_pp": float(100.0 * (spec0 - specA))},
    }
    out["A_grade"] = ("PRE-EDIT-DEFECT-MATERIAL"
                      if (100.0 * (spec0 - specA) >= 5.0
                          or 100.0 * crossed[ctrl].mean() >= 5.0)
                      else "PRE-EDIT-DEFECT-CONTAINED")
    with open(os.path.join(pd_dir, "A.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["A_pre_edit_defect"], indent=2))
    print("A:", out["A_grade"])


def part_B(pd_dir, k):
    model, feats, tau, X, y, nwords, p0 = _load()
    ctrl = y == 0
    units_all = list(CATEGORY)
    hasmat = X[["iu.has_" + u for u in units_all]].to_numpy(float) > 0
    rng = np.random.default_rng(RNG_SEED + 1000 * k)
    frames = []
    for _ in range(N_REPS):
        mask = np.zeros_like(hasmat)
        for i in range(len(X)):
            idx = np.flatnonzero(hasmat[i])
            if len(idx) == 0:
                continue
            mask[i, rng.choice(idx, size=min(k, len(idx)), replace=False)] = True
        frames.append(remove_units(X, nwords, mask, units_all)[feats])
    big = pd.concat(frames, ignore_index=True)
    pall = model.predict_proba(big)[:, 1].reshape(N_REPS, len(X))
    ca, cc, dps = [], [], []
    for pk in pall:
        c = (p0 < tau) & (pk >= tau)
        ca.append(100.0 * c.mean()); cc.append(100.0 * c[ctrl].mean())
        dps.append(float((pk - p0).mean()))
    rec = {"k": k, "n_reps": N_REPS,
           "mean_pct_crossed_all": float(np.mean(ca)),
           "mean_pct_crossed_controls": float(np.mean(cc)),
           "sd_pct_crossed_controls": float(np.std(cc)),
           "mean_delta_p": float(np.mean(dps)),
           "mean_units_lost": float(np.minimum(hasmat.sum(1), k).mean())}
    with open(os.path.join(pd_dir, "B_k%d.json" % k), "w") as f:
        json.dump(rec, f, indent=2)
    print(json.dumps(rec, indent=2))


def part_C(pd_dir):
    """
    POST-HOC.  Declared as post-hoc: this was NOT pre-registered, it was added
    after Part B returned DISPLACEMENT-MATERIAL, and IT DOES NOT CHANGE THAT
    GRADE.  Its only purpose is to establish what the app should DO about the
    finding, which requires knowing whether the rows that cross were already
    inside the decision-stability band the report already flags
    (|p - tau| <= 0.1032, app/server.py).  If they were, the app already warns
    about them; if they were not, it does not.
    """
    model, feats, tau, X, y, nwords, p0 = _load()
    BAND = 0.1032
    ctrl = y == 0
    units_all = list(CATEGORY)
    hasmat = X[["iu.has_" + u for u in units_all]].to_numpy(float) > 0
    out = {"post_hoc": True, "changes_grade": False, "band": BAND,
           "baseline_controls_in_band_pct":
               float(100.0 * (np.abs(p0[ctrl] - tau) <= BAND).mean()),
           "baseline_controls_below_tau_pct":
               float(100.0 * (p0[ctrl] < tau).mean()),
           "by_k": {}}
    for k in (1, 2, 6):
        rng = np.random.default_rng(RNG_SEED + 1000 * k)
        frames = []
        for _ in range(N_REPS):
            mask = np.zeros_like(hasmat)
            for i in range(len(X)):
                idx = np.flatnonzero(hasmat[i])
                if len(idx) == 0:
                    continue
                mask[i, rng.choice(idx, size=min(k, len(idx)), replace=False)] = True
            frames.append(remove_units(X, nwords, mask, units_all)[feats])
        pall = model.predict_proba(pd.concat(frames, ignore_index=True))[:, 1]
        pall = pall.reshape(N_REPS, len(X))
        inband, n_cross = [], []
        for pk in pall:
            c = (p0 < tau) & (pk >= tau) & ctrl
            if c.sum() == 0:
                continue
            inband.append(100.0 * (np.abs(p0[c] - tau) <= BAND).mean())
            n_cross.append(int(c.sum()))
        out["by_k"][str(k)] = {
            "mean_n_controls_crossing": float(np.mean(n_cross)),
            "pct_of_crossers_already_in_band": float(np.mean(inband))}
        print(k, out["by_k"][str(k)], flush=True)
    with open(os.path.join(pd_dir, "C.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


def combine(pd_dir):
    res = {"pre_registered": True, "lu_touched": False, "model_refitted": False,
           "seed": RNG_SEED, "n_reps": N_REPS, "k_grid": K_GRID}
    res.update(json.load(open(os.path.join(pd_dir, "A.json"))))
    B = {}
    for k in K_GRID:
        B[str(k)] = json.load(open(os.path.join(pd_dir, "B_k%d.json" % k)))
    res["B_displacement"] = {"by_k": B}
    cpath = os.path.join(pd_dir, "C.json")
    if os.path.exists(cpath):
        res["C_post_hoc_band_diagnostic"] = json.load(open(cpath))
    c2 = B["2"]["mean_pct_crossed_controls"]; c4 = B["4"]["mean_pct_crossed_controls"]
    res["B_grade"] = ("DISPLACEMENT-MATERIAL" if c2 >= 10.0
                      else "DISPLACEMENT-MINOR" if c4 >= 10.0
                      else "DISPLACEMENT-NEGLIGIBLE")
    out = os.path.join(ROOT, "results", "stimulus_inventory_probe.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    print("A:", res["A_grade"], "| B:", res["B_grade"], "->", out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["A", "B", "C", "combine"], required=True)
    ap.add_argument("--k", type=int)
    a = ap.parse_args()
    d = os.path.join(ROOT, "results", "_partial_stimulus_probe")
    os.makedirs(d, exist_ok=True)
    if a.part == "A":
        part_A(d)
    elif a.part == "B":
        part_B(d, a.k)
    elif a.part == "C":
        part_C(d)
    else:
        combine(d)
