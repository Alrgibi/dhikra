"""
DELAWARE TASK-COUNT CURVE  --  how many tasks, and which?
=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-25 BEFORE execution.
=============================================================================

WHY. Delaware MCI AUC 0.629 is this project's weakest number and its most
important scientific weakness. Section 5.6.1 established BATTERY-BETTER -- five
tasks beat Cookie alone -- but did not establish HOW MANY tasks are needed or
WHICH. The deployed system administers four; that was a clinical judgment, never
a measured one. This is the only lever on the weakest number that does not touch
the deployed model.

DESIGN.
  Cohort      the Delaware participants who completed ALL FIVE tasks (n = 288),
              complete-case, so every subset is scored on exactly the same people.
  Features    the 43 features shared by all five task extractors. Cookie's extra
              31 information-unit features are Cookie-SPECIFIC -- there is no
              cookie jar in Cinderella -- and excluding them is what makes the
              five tasks like-for-like. A sixth REFERENCE arm uses Cookie's full
              74 to connect the curve to the deployed configuration.
  Model       the committed architecture, unchanged: CalibratedClassifierCV
              (sigmoid, cv=3) over the soft-voting ensemble, seed 42.
  Protocol    StratifiedGroupKFold(5, shuffle=True, random_state=42) grouped by
              participant. One fit per task. OOF probability per recording,
              averaged within participant to one score per participant per task.
  Combination SCORE-LEVEL AVERAGING, not feature concatenation.
              This is deliberate and it corrects a defect in the existing
              combined_task_auc.json figures, where "all 5 tasks" used 246
              features against Cookie's 74: that comparison confounds TASK COUNT
              with COLUMN COUNT and cannot separate them. Averaging scores holds
              dimensionality constant across every subset size, so a gain cannot
              be a dimensionality artefact. It is also the deployable operation --
              administer k tasks, score each with the same model, average.
  Arms        all 31 non-empty subsets of the five tasks.
  Test        paired participant bootstrap, 2000 resamples, seed 42; the same
              resampled people in every arm within a replicate.

CRITERIA, fixed in advance and mechanically applied.
  SATURATION POINT = the smallest k such that the paired 95% CI of
      (best subset at k+1) - (best subset at k)  INCLUDES ZERO.
  BATTERY-CONFIRMED      if CI of (best at 5) - (best at 1) excludes zero, positive.
  BATTERY-NOT-CONFIRMED  otherwise.
  COOKIE-DISPENSABLE     if the best subset AT the saturation point does not
                         contain cookie. Registered in advance precisely because
                         it is the uncomfortable outcome: Cookie is the deployed
                         system's primary task and the only task Pitt and Lu share.
  Report-and-stop. Selecting "best at k" on the same data that evaluates it is
  an optimistic operation; the curve is therefore reported as an UPPER BOUND on
  what task selection can achieve, and the paired intervals are between
  already-selected arms, not corrected for selection. This is stated here, before
  execution, rather than discovered afterwards.

INTERPRETIVE ASYMMETRY. A negative result is informative and gets equal
prominence: BATTERY-NOT-CONFIRMED would mean multi-task administration cannot be
justified by measurement on this corpus, and that the four-task design rests on
clinical reasoning alone -- which the thesis would then have to say plainly.

GOVERNANCE. Delaware only. Lu is not read. The deployed model, feature set and
threshold are unchanged by anything here. Nothing in this file is externally
validated and none of it may appear in a table with a validated figure: it
belongs to the specified-successor chapter, not to Chapter 5.

USAGE:  python task_count_curve.py fit <task>   (one task per call, cached)
        python task_count_curve.py combine
"""
import json, os, sys, functools
import numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (ExtraTreesClassifier, GradientBoostingClassifier,
                              RandomForestClassifier, VotingClassifier)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedGroupKFold

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
CACHE = os.path.join(R, "reconstruction", "_taskcurve_cache")
os.makedirs(CACHE, exist_ok=True)
TASKS = ["cookie", "cinderella", "cat", "rockwell", "sandwich"]

def pipe(c):
    return Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler()), ("c", c)])
def model():
    ens = VotingClassifier(estimators=[
        ("et", pipe(ExtraTreesClassifier(500, min_samples_leaf=3, class_weight="balanced",
                                         random_state=42, n_jobs=-1))),
        ("gb", pipe(GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                               learning_rate=0.05, random_state=42))),
        ("rf", pipe(RandomForestClassifier(500, min_samples_leaf=3, class_weight="balanced",
                                           random_state=42, n_jobs=-1))),
    ], voting="soft")
    return CalibratedClassifierCV(estimator=ens, method="sigmoid", cv=3)

def shared_cols():
    cs = [set(pd.read_csv(f"{R}/delaware/{t}_features.csv", nrows=1).columns) for t in TASKS]
    return sorted(functools.reduce(lambda a, b: a & b, cs))

def complete_participants():
    ss = [set(pd.read_csv(f"{R}/delaware/{t}_meta.csv").participant_id) for t in TASKS]
    return sorted(functools.reduce(lambda a, b: a & b, ss))

def fit_task(task, full=False, budget=24.0):
    """Fold-level caching with a wall-clock budget: the VM kills the process at
    45 s, so each call fits as many uncached folds as it can and exits cleanly.
    Repeated calls make progress. HARNESS-ONLY amendment (2026-08-25): chunking
    changes nothing about the model, the folds or the data -- StratifiedGroupKFold
    is deterministic at seed 42, so fold f is identical whenever it is computed."""
    import time
    t0 = time.time()
    tag = task + ("_full74" if full else "")
    F = pd.read_csv(f"{R}/delaware/{task}_features.csv")
    M = pd.read_csv(f"{R}/delaware/{task}_meta.csv")
    cols = list(F.columns) if full else shared_cols()
    X = F[cols].values.astype(float); y = M.label.values; g = M.participant_id.astype(str).values
    splits = list(StratifiedGroupKFold(5, shuffle=True, random_state=42).split(X, y, g))
    done = []
    for f, (tr, te) in enumerate(splits):
        fp = os.path.join(CACHE, f"{tag}_fold{f}.npz")
        if os.path.exists(fp):
            done.append(f); continue
        if time.time() - t0 > budget:
            print(f"{tag}: budget reached, {len(done)}/5 folds cached"); return False
        m = model(); m.fit(X[tr], y[tr])
        np.savez(fp, te=te, p=m.predict_proba(X[te])[:, 1])
        done.append(f); print(f"  {tag} fold {f} done ({time.time()-t0:.1f}s)")
    oof = np.zeros(len(y))
    for f in range(5):
        d = np.load(os.path.join(CACHE, f"{tag}_fold{f}.npz"))
        oof[d["te"]] = d["p"]
    np.savez(os.path.join(CACHE, f"{tag}.npz"), oof=oof, y=y, g=g, cols=np.array(cols, dtype=object))
    print(f"COMPLETE {tag}: n={len(y)} feats={len(cols)}")
    return True

def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float)
    a, b = int((y == 1).sum()), int((y == 0).sum())
    if a == 0 or b == 0: return float("nan")
    r = pd.Series(s).rank().values
    return float((r[y == 1].sum() - a * (a + 1) / 2.0) / (a * b))

def combine():
    keep = complete_participants()
    P = {}
    for t in TASKS:
        d = np.load(os.path.join(CACHE, f"{t}.npz"), allow_pickle=True)
        s = pd.DataFrame({"g": d["g"], "y": d["y"], "p": d["oof"]}).groupby("g").agg(y=("y", "max"), p=("p", "mean"))
        P[t] = s.reindex([str(k) for k in keep])
    y = P[TASKS[0]]["y"].values.astype(int)
    S = {t: P[t]["p"].values for t in TASKS}
    dF = np.load(os.path.join(CACHE, "cookie_full74.npz"), allow_pickle=True)
    sF = pd.DataFrame({"g": dF["g"], "y": dF["y"], "p": dF["oof"]}).groupby("g").agg(p=("p", "mean")).reindex([str(k) for k in keep])["p"].values
    n = len(y); print(f"complete-case participants: {n}  impaired: {int(y.sum())}  controls: {int((y==0).sum())}")
    subsets = []
    for mask in range(1, 32):
        sel = [TASKS[i] for i in range(5) if mask >> i & 1]
        sc = np.mean([S[t] for t in sel], axis=0)
        subsets.append(dict(tasks=sel, k=len(sel), auc=auc(y, sc), score=sc))
    rng = np.random.default_rng(42)
    idx = [rng.choice(n, n, replace=True) for _ in range(2000)]
    for r in subsets:
        r["boot"] = np.array([auc(y[i], r["score"][i]) for i in idx])
    ref = dict(tasks=["cookie(full 74)"], k=1, auc=auc(y, sF), score=sF)
    ref["boot"] = np.array([auc(y[i], sF[i]) for i in idx])
    return y, subsets, ref, n

if __name__ == "__main__":
    if sys.argv[1] == "fit":
        args = sys.argv[2:]
        full = "full" in args
        names = [a for a in args if a in TASKS] or TASKS
        import time; t0 = time.time()
        for t in names:
            if os.path.exists(os.path.join(CACHE, t + ("_full74" if full else "") + ".npz")):
                print(f"cached: {t}"); continue
            if time.time() - t0 > 24: print("budget reached"); break
            fit_task(t, full=full, budget=24.0 - (time.time() - t0))
    else:
        y, subs, ref, n = combine()
        best = {}
        for k in range(1, 6):
            best[k] = max([r for r in subs if r["k"] == k], key=lambda r: r["auc"])
        print(f"\n{'k':>2} {'best subset':<44} {'AUC':>7} {'95% CI':>18}")
        for k in range(1, 6):
            b = best[k]; lo, hi = np.percentile(b["boot"], [2.5, 97.5])
            print(f"{k:>2} {'+'.join(b['tasks']):<44} {b['auc']:>7.4f} [{lo:>6.4f},{hi:>6.4f}]")
        lo, hi = np.percentile(ref["boot"], [2.5, 97.5])
        print(f"{'--':>2} {'REFERENCE cookie, full 74 (deployed cfg)':<44} {ref['auc']:>7.4f} [{lo:>6.4f},{hi:>6.4f}]")
        print(f"\n{'step':<12} {'delta':>8} {'95% CI':>20} {'excludes 0':>11}")
        sat = None
        for k in range(1, 5):
            d = best[k + 1]["boot"] - best[k]["boot"]
            lo, hi = np.percentile(d, [2.5, 97.5]); ex = lo > 0 or hi < 0
            print(f"{f'{k}->{k+1}':<12} {best[k+1]['auc']-best[k]['auc']:>+8.4f} [{lo:>+7.4f},{hi:>+7.4f}] {str(ex):>11}")
            if sat is None and not ex: sat = k
        if sat is None: sat = 5
        d51 = best[5]["boot"] - best[1]["boot"]; lo51, hi51 = np.percentile(d51, [2.5, 97.5])
        grade = "BATTERY-CONFIRMED" if lo51 > 0 else "BATTERY-NOT-CONFIRMED"
        cook = "COOKIE-DISPENSABLE" if "cookie" not in best[sat]["tasks"] else "cookie retained at saturation"
        print(f"\n5 vs 1: {best[5]['auc']-best[1]['auc']:+.4f} [{lo51:+.4f},{hi51:+.4f}]")
        print(f"SATURATION POINT: k = {sat}   ({'+'.join(best[sat]['tasks'])})")
        print(f"GRADE: {grade}   |   {cook}")
        print(f"\nall single tasks:")
        for r in sorted([r for r in subs if r["k"] == 1], key=lambda r: -r["auc"]):
            lo, hi = np.percentile(r["boot"], [2.5, 97.5])
            print(f"   {r['tasks'][0]:<12} {r['auc']:.4f} [{lo:.4f},{hi:.4f}]")
        json.dump(dict(registration="module docstring, committed before execution",
            n_participants=n, n_impaired=int(y.sum()),
            curve={str(k): dict(tasks=best[k]["tasks"], auc=best[k]["auc"],
                   ci95=list(np.percentile(best[k]["boot"], [2.5, 97.5]))) for k in range(1, 6)},
            reference_cookie_full74=dict(auc=ref["auc"], ci95=list(np.percentile(ref["boot"], [2.5, 97.5]))),
            all_subsets=[dict(tasks=r["tasks"], k=r["k"], auc=r["auc"]) for r in sorted(subs, key=lambda r: -r["auc"])],
            saturation_point=sat, grade=grade, cookie_status=cook,
            five_vs_one=dict(delta=best[5]["auc"] - best[1]["auc"], ci95=[lo51, hi51]),
            caveats=["best-at-k selected on the same data that evaluates it: the curve is an UPPER BOUND",
                     "score-level averaging holds dimensionality constant; supersedes combined_task_auc.json which confounded task count with column count",
                     "Delaware only; Lu not read; not externally validated; specified-successor material, not Chapter 5"],
            governance="deployed model, feature set and threshold unchanged"),
            open(f"{R}/reconstruction/task_count_curve.json", "w"), indent=2)
        print("\nwritten: results/reconstruction/task_count_curve.json")


# =============================================================================
# AMENDMENT 3 -- 2026-08-25, DISCLOSED AS POST-RESULT.
# =============================================================================
# The registration specified the COHORT ("participants who completed all five
# tasks") but did NOT specify the LABEL RULE for a participant with more than one
# visit. The first execution used max(label) -- "ever impaired" -- and its output
# was seen before this defect was noticed. The reader is entitled to weigh that.
#
# WHY IT MATTERS. Delaware contains 18 of 288 complete-case participants (6.25%)
# whose label CHANGES across visits, including MCI -> Control reversion:
# participant 01 is MCI at age 84 and Control at 87 and 88. "Ever impaired" is
# therefore not a cross-sectional label at all -- it marks a person impaired at
# visits when the corpus records them as healthy.
#
# THE CORRECTION. One recording per participant per task, taken at the EARLIEST
# visit present in all five tasks, carrying THAT VISIT'S label. This is a genuine
# cross-sectional comparison, it never averages across a changing state, and it
# never averages across visits at all.
#
# BOTH results are reported. Neither replaces the other silently.
# =============================================================================
def combine_crosssectional():
    import re
    keep = complete_participants()
    per = {}
    for t in TASKS:
        d = np.load(os.path.join(CACHE, f"{t}.npz"), allow_pickle=True)
        M = pd.read_csv(f"{R}/delaware/{t}_meta.csv")
        v = M.file_id.astype(str).str.extract(r"-(\d+)\|")[0].astype(float)
        per[t] = pd.DataFrame(dict(pid=M.participant_id.astype(str), visit=v,
                                   y=M.label.values, p=d["oof"]))
    common = None
    for t in TASKS:
        s = set(map(tuple, per[t][["pid", "visit"]].dropna().values))
        common = s if common is None else common & s
    cdf = pd.DataFrame(list(common), columns=["pid", "visit"])
    first = cdf.sort_values("visit").groupby("pid", as_index=False).first()
    first = first[first.pid.isin([str(k) for k in keep])]
    S, Y = {}, None
    for t in TASKS:
        j = first.merge(per[t], on=["pid", "visit"], how="left")
        S[t] = j.p.values
        if Y is None: Y = j.y.values.astype(int)
        else: assert (Y == j.y.values).all(), "label disagreement across tasks at the same visit"
    n = len(Y)
    print(f"CROSS-SECTIONAL: {n} participants, earliest visit common to all five tasks")
    print(f"  labels at that visit: impaired {int(Y.sum())}, control {int((Y==0).sum())}")
    print(f"  visit used: {pd.Series(first.visit.values).value_counts().sort_index().to_dict()}")
    subs = []
    for mask in range(1, 32):
        sel = [TASKS[i] for i in range(5) if mask >> i & 1]
        subs.append(dict(tasks=sel, k=len(sel), score=np.mean([S[t] for t in sel], axis=0)))
    for r in subs: r["auc"] = auc(Y, r["score"])
    rng = np.random.default_rng(42)
    idx = [rng.choice(n, n, replace=True) for _ in range(2000)]
    for r in subs: r["boot"] = np.array([auc(Y[i], r["score"][i]) for i in idx])
    return Y, subs, n
