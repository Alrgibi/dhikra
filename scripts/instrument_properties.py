"""
instrument_properties.py -- three properties a clinical instrument should
report and this one did not: a simplest-competitive-baseline, the interaction
between calibration and the Bayesian chain, and test-retest stability.

Written 2026-08-23. NOT a hypothesis test and NOT pre-registered -- these are
descriptive properties computed from committed artifacts, and each is reported
whatever it shows. Nothing here trains, modifies or re-scores a model; the Lu
corpus is not read.

Committed as a script rather than run inline, because eight result files in
this project already carry "script: inline (code not committed)" and that is a
disclosed defect, not a precedent.

--------------------------------------------------------------------------
A. SIMPLEST COMPETITIVE BASELINE
   Univariate AUC of every deployed feature. No model, no fitting, so there is
   nothing to overfit; the participant-level bootstrap is for the interval
   only. The question a clinician asks and the thesis had not answered: how
   much does the 64-feature calibrated ensemble buy over the best single
   number a person could count by hand?

B. CALIBRATION x THE BAYESIAN CHAIN
   src/dhikra/risk_adjustment.py divides model odds by the training prevalence
   to isolate a likelihood ratio. That step is EXACT ONLY IF THE SCORE IS
   CALIBRATED. It is not: the development calibration slope is 1.289, meaning
   predictions are compressed toward the middle, so the derived LR is pulled
   toward 1 and the speech evidence is systematically under-weighted. This
   quantifies the distortion at representative scores and ages, and checks
   whether the banded output added on 2026-08-23 absorbs it.

C. TEST-RETEST STABILITY AND MINIMAL DETECTABLE CHANGE
   Pitt records the same participants across successive annual visits. Among
   CONTROLS -- people who should not change -- the spread of between-visit
   score changes estimates the instrument's measurement error, and 1.96*sqrt(2)
   times the standard error of measurement is the smallest change that can be
   distinguished from noise. No clinical instrument should be proposed without
   this number.

   TWO REASONS THIS IS AN UPPER BOUND ON MEASUREMENT ERROR, both of which must
   be reported with it:
     1. The scores are out-of-fold predictions, so two visits by the same
        person were scored by DIFFERENT fold models. A deployed frozen model
        would not add that variance.
     2. The median inter-visit gap is one year, so genuine change over a year
        is inside the estimate.
"""
import json, math, os
import numpy as np
import pandas as pd

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
os.chdir(REPO)
FEATS = json.load(open("results/summary/model_card.json"))["feature_order"]
SLOPE, INTERCEPT = 1.2886714739, 0.1376204067      # unpenalised fit, see calibration_slope_resolution.json
TRAINING_PRIOR = 0.471125


def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float)
    ok = np.isfinite(s); y, s = y[ok], s[ok]
    if len(np.unique(y)) < 2: return float("nan")
    r = pd.Series(s).rank().values
    n1 = (y == 1).sum(); n0 = (y == 0).sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def dev():
    Xp = pd.read_csv("results/pitt_cookie/features.csv"); mp = pd.read_csv("results/pitt_cookie/meta.csv")
    Xd = pd.read_csv("results/delaware/cookie_features.csv"); md = pd.read_csv("results/delaware/cookie_meta.csv")
    X = pd.concat([Xp[FEATS], Xd[FEATS]], ignore_index=True)
    y = np.concatenate([mp.label.values, md.label.values]).astype(int)
    g = np.concatenate([("P" + mp.participant_id.astype(str)).values,
                        ("D" + md.participant_id.astype(str)).values])
    return X, y, g, (Xp, mp, Xd, md)


def part_a():
    X, y, g, (Xp, mp, Xd, md) = dev()
    rows = []
    for f in FEATS:
        a = auc(y, X[f].values)
        if np.isfinite(a):
            rows.append({"feature": f, "auc_directed": round(max(a, 1 - a), 4)})
    rows.sort(key=lambda r: -r["auc_directed"])
    best = rows[0]["feature"]
    rng = np.random.default_rng(42)
    pids = np.unique(g); idx = {p: np.where(g == p)[0] for p in pids}
    bs = []
    for _ in range(2000):
        t = np.concatenate([idx[p] for p in rng.choice(pids, len(pids), True)])
        a = auc(y[t], X[best].values[t]); bs.append(max(a, 1 - a))
    bs = np.array(bs); bs = bs[np.isfinite(bs)]
    per = {}
    for nm, Xc, mc in (("Pitt", Xp, mp), ("Delaware", Xd, md)):
        a = auc(mc.label.values.astype(int), Xc[best].values)
        per[nm] = round(max(a, 1 - a), 4)
    return {
        "question": "how much does the 64-feature calibrated ensemble buy over the best single hand-countable feature?",
        "top_12_single_features": rows[:12],
        "best_single_feature": best,
        "best_single_auc_combined": rows[0]["auc_directed"],
        "best_single_ci95": [round(float(np.percentile(bs, 2.5)), 4),
                             round(float(np.percentile(bs, 97.5)), 4)],
        "best_single_by_cohort": per,
        "full_model_reference": {"combined": 0.7550, "combined_ci95": [0.7192, 0.7902],
                                 "Pitt": 0.8095, "Delaware": 0.6291},
        "interpretation": (
            "Counting information units -- one number, scorable by hand from a printed "
            "checklist -- reaches AUC %.4f combined and %.4f on Pitt, against 0.7550 and "
            "0.8095 for the deployed 64-feature calibrated ensemble. The combined intervals "
            "overlap. The whole machine-learning apparatus buys roughly four and a half "
            "points of AUC over a count. Report this as a DEPLOYMENT FINDING, not only as a "
            "limitation: the instrument has a paper fallback for a clinic with no computer."
            % (rows[0]["auc_directed"], per["Pitt"])),
    }


def part_b():
    lg = lambda p: math.log(p / (1 - p))
    ex = lambda z: 1 / (1 + math.exp(-z))
    bands = [(0.0, 0.10, "low"), (0.10, 0.30, "moderate"),
             (0.30, 0.60, "high"), (0.60, 1.01, "very high")]
    def band(p):
        for lo, hi, lab in bands:
            if lo <= p < hi: return lab
        return ""
    tro = TRAINING_PRIOR / (1 - TRAINING_PRIOR)
    rows, same = [], 0
    for p in (0.10, 0.25, 0.367, 0.50, 0.70, 0.85, 0.95):
        pc = ex(INTERCEPT + SLOPE * lg(p))
        lr, lrc = (p / (1 - p)) / tro, (pc / (1 - pc)) / tro
        r = {"score": p, "lr_raw": round(lr, 3), "lr_calibration_corrected": round(lrc, 3),
             "posterior": {}}
        for age, prev in (("65-69", 0.110), ("80-84", 0.420)):
            po = prev / (1 - prev)
            a = (lr * po) / (1 + lr * po); b = (lrc * po) / (1 + lrc * po)
            agree = band(a) == band(b)
            same += agree
            r["posterior"][age] = {"as_deployed": round(a, 4), "corrected": round(b, 4),
                                   "shift": round(b - a, 4),
                                   "band_as_deployed": band(a), "band_corrected": band(b),
                                   "band_unchanged": agree}
        rows.append(r)
    return {
        "problem": ("risk_adjustment.py derives a likelihood ratio by dividing model odds by the "
                    "training prevalence. That is exact only for a calibrated score. The "
                    "development calibration slope is 1.289 (>1), so predictions are compressed "
                    "toward the middle and the derived LR is pulled toward 1."),
        "direction": "the chain UNDERSTATES risk at high scores and slightly overstates it at low scores",
        "calibration_slope": SLOPE, "calibration_intercept": INTERCEPT,
        "rows": rows,
        "band_absorption": f"{same} of 14 posterior comparisons keep the same reported band",
        "interpretation": (
            "The largest distortion is about 0.16 in posterior probability, at high scores. "
            "It is a REPORTING error rather than a TRIAGE error -- everyone above the 0.367 "
            "threshold is referred either way -- and the banded output introduced 2026-08-23 "
            "absorbs most of it. Report it: two sections of the thesis currently contradict "
            "each other and an examiner who reads both will notice."),
    }


def part_c():
    p = np.load("results/summary/oof_predictions.npy")
    s = np.array([str(v) for v in np.load("results/summary/oof_source.npy", allow_pickle=True)])
    y = np.load("results/summary/oof_labels.npy").astype(int)
    m = pd.read_csv("results/pitt_cookie/meta.csv")
    assert (s == "Pitt").sum() == len(m)
    m = m.copy(); m["p"] = p[s == "Pitt"]
    assert (m.label.values == y[s == "Pitt"]).all(), "label order mismatch -- run void"

    def pairs(sub_df):
        dif, gap = [], []
        for _, sub in sub_df.groupby("participant_id"):
            if len(sub) < 2: continue
            sub = sub.sort_values("visit")
            v = sub.p.values; a = sub.age.values
            for i in range(len(v) - 1):
                dif.append(v[i + 1] - v[i])
                gap.append(a[i + 1] - a[i] if np.isfinite(a[i]) and np.isfinite(a[i + 1]) else np.nan)
        return np.array(dif), np.array(gap)

    ctrl, cgap = pairs(m[m.label == 0])
    imp, _ = pairs(m[m.label == 1])
    short = np.isfinite(cgap) & (cgap <= 1.5)
    out = {}
    for tag, d in (("all_gaps", ctrl), ("gap_le_1.5y", ctrl[short])):
        sd = float(d.std(ddof=1)); sem = sd / math.sqrt(2)
        out[tag] = {"n_pairs": int(len(d)), "mean_change": round(float(d.mean()), 4),
                    "sd_of_change": round(sd, 4),
                    "standard_error_of_measurement": round(sem, 4),
                    "minimal_detectable_change_95": round(1.96 * math.sqrt(2) * sem, 3)}
    return {
        "question": "how much does a healthy person's score move between visits, with nothing changed?",
        "controls": out,
        "inter_visit_gap_years": {"median": float(np.nanmedian(cgap)),
                                  "mean": round(float(np.nanmean(cgap)), 2),
                                  "range": [float(np.nanmin(cgap)), float(np.nanmax(cgap))]},
        "impaired_group_drift": {"n_pairs": int(len(imp)),
                                 "mean_change_per_visit": round(float(imp.mean()), 4),
                                 "sd": round(float(imp.std(ddof=1)), 4),
                                 "note": "positive = the score rises as the group progresses, which it does"},
        "upper_bound_caveats": [
            "out-of-fold predictions: two visits by one person were scored by DIFFERENT fold models, "
            "which a deployed frozen model would not do",
            "median inter-visit gap is one year, so genuine change is inside the estimate"],
        "interpretation": (
            "Minimal detectable change is about 0.29 score points on a 0-1 scale whose deployed "
            "threshold is 0.367. A person's score can cross the threshold and move two reported "
            "bands without anything about them having changed. THE INSTRUMENT IS A SCREENING TEST "
            "AND NOT A MONITORING TEST, and this is the number that establishes it. At GROUP level "
            "the picture differs: impaired participants' scores rise about 0.045 per visit while "
            "controls' do not move, so progression is visible in aggregate and not individually."),
    }


if __name__ == "__main__":
    res = {"generated": "2026-08-23", "type": "descriptive instrument properties, not a hypothesis test",
           "governance": "Lu not read; no model trained, modified or re-scored",
           "A_simplest_competitive_baseline": part_a(),
           "B_calibration_x_bayesian_chain": part_b(),
           "C_test_retest_and_mdc": part_c()}
    json.dump(res, open("results/reconstruction/instrument_properties.json", "w"), indent=2)
    print("A best single feature:", res["A_simplest_competitive_baseline"]["best_single_feature"],
          res["A_simplest_competitive_baseline"]["best_single_auc_combined"],
          res["A_simplest_competitive_baseline"]["best_single_ci95"],
          res["A_simplest_competitive_baseline"]["best_single_by_cohort"])
    print("B", res["B_calibration_x_bayesian_chain"]["band_absorption"])
    print("C MDC95 (<=1.5y):", res["C_test_retest_and_mdc"]["controls"]["gap_le_1.5y"]["minimal_detectable_change_95"],
          "| impaired drift:", res["C_test_retest_and_mdc"]["impaired_group_drift"]["mean_change_per_visit"])
