"""phase0_free_f.py -- provenance reconstruction of THESIS_PLAN 5.2.1's Pitt-only core.

WRITTEN 2026-08-28 UNDER OWNER RULING (WRITING_FINDINGS 29 pending-item): the
5.2.1 sex-disparity core has no committed producer, no result file and no
working-note record; its figures exist only in the frozen plan's prose. This
driver is NEW CODE WRITTEN TOWARD KNOWN NUMBERS, which is how a script gets
tuned until it agrees -- so every target value is quoted here, from the plan,
BEFORE any code, the method is fixed here, and the mismatch rule is stated in
advance:

    IF A REPRODUCED VALUE DIFFERS FROM THE PLAN, THE REPRODUCED VALUE WINS.
    The plan is corrected, the discrepancy is reported at full strength, and
    5.2.1 is rewritten on the reproduced number. Never the reverse.
    REPORT-AND-STOP: one execution. A code error may be fixed, but the fix is
    disclosed with its timing relative to seeing output.

METHOD, fixed before execution. Inputs: the same eight committed post-lock
files as drivers a-e (hashes in phase0_free_recovery.json). Pitt subset =
source Pitt (548 recordings, 290 participants). Scores = the stored model OOF
predictions; no model is fitted, no threshold touched, no Lu file opened.
AUC = rank statistic (identical to drivers a-e). Bootstrap for T1: participant-
clustered, participants resampled with replacement WITHIN EACH SEX, both sexes
drawn in the same replicate; 2,000 replicates; numpy default_rng(42);
percentile 95% CIs. Mann-Whitney: scipy.stats.mannwhitneyu, two-sided.
Matching for T3: the committed match_participants procedure of
scripts/analyze_pitt.py replicated verbatim (participant-level 1:1, same sex,
age within 3 years, greedy nearest-age, controls without replacement),
seeds 1..10 as section 3.6 records; the plan does not say which run produced
its matched figures, so the ten-seed mean and range are reported and judged
against the plan's values. Sex-stratified control-referenced thresholds for
T7: the 80th percentile (numpy.quantile, linear interpolation) of that sex's
Pitt control OOF scores, sensitivity target 80% at specificity-to-target by
construction. Length quartiles for T9: pandas.qcut(4) on ling.word_count,
declared Pitt-only primary (the plan's 0.78-0.82 values bracket the Pitt
figure, not the combined one); combined printed as a secondary diagnostic.

TARGETS, quoted from THESIS_PLAN 5.2.1 before execution:
 T1 female n 343 prevalence 0.55 AUC 0.869 [0.824, 0.912];
    male n 205 prevalence 0.57 AUC 0.704 [0.605, 0.802];
    difference +0.165 [0.053, 0.273]; female exceeded male in 2,000 of 2,000.
 T2 impaired MMSE female 18.77 vs male 21.35, difference 2.58,
    Mann-Whitney p = 0.0002; impaired age female 72.6 vs male 69.7;
    control MMSE 29.26 vs 28.94.
 T3 matched female 0.837, male 0.746, gap +0.092.
 T4 sensitivity by MMSE band (female, male; n):
    <=15: 0.978 (45), 1.000 (17); 16-20: 0.930 (71), 0.963 (27);
    21-25: 0.773 (44), 0.875 (24); 26+: 0.733 (15), 0.581 (31).
 T5 specificity at 0.367 female 0.545, male 0.438; control mean score
    male 0.447 vs female 0.382; impaired mean male 0.586 vs female 0.641.
 T6 healthy men vs women: iu.total 13.01 vs 14.14 (p = 0.018),
    iu.actions 3.43 vs 3.95 (p = 0.0075), iu.proportion 0.57 vs 0.61;
    impaired men vs women: word count 103.9 vs 90.6, iu.total 10.66 vs 9.81.
 T7 stratified 80%-target thresholds male 0.625 female 0.481;
    specificity female 0.799 male 0.798; sensitivity gap pooled-0.367 0.176
    -> stratified 0.348.
 T8 Delaware by sex: female 0.643, male 0.596.
 T9 Pitt length-quartile AUCs 0.781 / 0.822 / 0.820 / 0.797.

EXTERNAL CHECK available before this run (owner, 2026-08-28): female 0.8687,
male 0.7041, difference +0.1646 -- computed independently from the same
committed files. This script's T1 must agree with those three as well.

EXECUTION NOTE, disclosed with its timing: the first execution hit the
45-second shell limit and was killed with an EMPTY capture -- no output had
been seen. The T1 bootstrap was then reimplemented with numpy-indexed
resampling and scipy rankdata for speed. No numeric definition changed:
same resampling unit, same replicate count, same seed, same estimator.
"""
import numpy as np, pandas as pd, os
from scipy.stats import mannwhitneyu
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
rng = np.random.default_rng(42)

from scipy.stats import rankdata
def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float)
    m = ~np.isnan(s); y, s = y[m], s[m]
    a, b = int((y == 1).sum()), int((y == 0).sum())
    if a == 0 or b == 0: return np.nan
    r = rankdata(s)
    return (r[y == 1].sum() - a * (a + 1) / 2.0) / (a * b)

pm = pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm = pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pf = pd.read_csv(f"{R}/pitt_cookie/features.csv"); df_ = pd.read_csv(f"{R}/delaware/cookie_features.csv")
pm["source"] = "Pitt"; dm["source"] = "Delaware"
if "visit" not in dm.columns: dm["visit"] = 1
meta = pd.concat([pm, dm], ignore_index=True, sort=False)
feat = pd.concat([pf, df_], ignore_index=True, sort=False)
oof = np.load(f"{R}/summary/oof_predictions.npy")
oly = np.load(f"{R}/summary/oof_labels.npy")
olg = np.load(f"{R}/summary/oof_source.npy", allow_pickle=True)
ok = (len(oof) == len(meta)) and bool((oly == meta["label"].values).all()) and bool((olg == meta["source"].values).all())
print("ORDER CHECK (labels+source align):", ok)
meta["oof"] = oof
sexall = meta["sex"].astype(str).str.lower().str[0].values
P = meta[meta.source == "Pitt"].copy(); P["sexc"] = sexall[(meta.source == "Pitt").values]
D = meta[meta.source == "Delaware"].copy(); D["sexc"] = sexall[(meta.source == "Delaware").values]
print(f"Pitt: {len(P)} recordings, {P.participant_id.nunique()} participants")

print("\n== T1  Pitt by-sex AUC, participant-clustered bootstrap 2000, seed 42 ==")
res = {}
for sx in "fm":
    G = P[P.sexc == sx]
    res[sx] = dict(n=len(G), prev=G.label.mean(), auc=auc(G.label.values, G.oof.values))
    print(f"  {sx}: n={res[sx]['n']}  prevalence={res[sx]['prev']:.2f}  AUC={res[sx]['auc']:.4f}")
boots = {"f": [], "m": [], "d": []}
arrs = {}
for sx in "fm":
    G = P[P.sexc == sx]
    arrs[sx] = [(g.label.values, g.oof.values) for _, g in G.groupby("participant_id")]
for _ in range(2000):
    a_ = {}
    for sx in "fm":
        k = len(arrs[sx])
        draw = rng.integers(0, k, size=k)
        yy = np.concatenate([arrs[sx][i][0] for i in draw])
        ss = np.concatenate([arrs[sx][i][1] for i in draw])
        a_[sx] = auc(yy, ss)
    boots["f"].append(a_["f"]); boots["m"].append(a_["m"]); boots["d"].append(a_["f"] - a_["m"])
q = lambda v: (np.percentile(v, 2.5), np.percentile(v, 97.5))
for k, lab in (("f", "female"), ("m", "male"), ("d", "difference")):
    lo, hi = q(boots[k]); print(f"  {lab}: CI95 [{lo:.4f}, {hi:.4f}]")
print(f"  difference point = {res['f']['auc']-res['m']['auc']:+.4f}; replicates female>male: {int(np.sum(np.array(boots['d'])>0))} of 2000")

print("\n== T2  severity composition (Pitt) ==")
imp = P[P.label == 1]; ctl = P[P.label == 0]
for col, grp, name in (("mmse", imp, "impaired MMSE"), ("age", imp, "impaired age"), ("mmse", ctl, "control MMSE")):
    f_ = grp[grp.sexc == "f"][col].dropna(); m_ = grp[grp.sexc == "m"][col].dropna()
    line = f"  {name}: female {f_.mean():.2f} vs male {m_.mean():.2f}"
    if name == "impaired MMSE":
        pv = mannwhitneyu(f_, m_, alternative="two-sided").pvalue
        line += f"  diff {m_.mean()-f_.mean():.2f}  MW p={pv:.4f}"
    print(line)

print("\n== T3  matched gap, committed matching (analyze_pitt), seeds 1-10 ==")
def match(meta_, max_age_diff=3.0, seed=1):
    people = (meta_.groupby("participant_id")
              .agg(age=("age", "mean"), sex=("sexc", "first"), label=("label", "first"))
              .reset_index().dropna(subset=["age"]))
    ctrl = people[people.label == 0]
    impd = people[people.label == 1].sample(frac=1, random_state=seed)
    used, pairs = set(), []
    for _, r in impd.iterrows():
        cand = ctrl[(~ctrl.participant_id.isin(used)) & (ctrl.sex == r.sex) & ((ctrl.age - r.age).abs() <= max_age_diff)]
        if len(cand):
            pick = cand.loc[(cand.age - r.age).abs().idxmin(), "participant_id"]
            used.add(pick); pairs.append((pick, r.participant_id))
    keep = {p for pr in pairs for p in pr}
    return meta_[meta_.participant_id.isin(keep)]
fa, ma = [], []
for seed in range(1, 11):
    M = match(P, seed=seed)
    fa.append(auc(M[M.sexc == "f"].label.values, M[M.sexc == "f"].oof.values))
    ma.append(auc(M[M.sexc == "m"].label.values, M[M.sexc == "m"].oof.values))
fa, ma = np.array(fa), np.array(ma)
print(f"  female mean {fa.mean():.4f} range [{fa.min():.4f},{fa.max():.4f}]")
print(f"  male   mean {ma.mean():.4f} range [{ma.min():.4f},{ma.max():.4f}]")
print(f"  gap    mean {+(fa-ma).mean():.4f} range [{(fa-ma).min():.4f},{(fa-ma).max():.4f}]")

print("\n== T4  sensitivity at 0.367 by MMSE band (Pitt impaired with MMSE) ==")
bands = [("<=15", -1, 15.0001), ("16-20", 15.0001, 20.0001), ("21-25", 20.0001, 25.0001), ("26+", 25.0001, 99)]
for nm, lo, hi in bands:
    row = []
    for sx in "fm":
        g = imp[(imp.sexc == sx) & (imp.mmse > lo) & (imp.mmse <= hi)]
        row.append(f"{sx}: {np.mean(g.oof.values >= 0.367):.3f} (n={len(g)})" if len(g) else f"{sx}: n=0")
    print(f"  {nm:6s} " + "   ".join(row))

print("\n== T5  operating point 0.367 by sex (Pitt) ==")
for sx in "fm":
    c = ctl[ctl.sexc == sx]; i = imp[imp.sexc == sx]
    print(f"  {sx}: specificity {np.mean(c.oof.values < 0.367):.4f}  control mean {c.oof.mean():.4f}  impaired mean {i.oof.mean():.4f}  sensitivity {np.mean(i.oof.values >= 0.367):.4f}")

print("\n== T6  mechanism means (Pitt) ==")
Pf = feat[(meta.source == "Pitt").values].copy(); Pf["sexc"] = P["sexc"].values; Pf["label"] = P["label"].values
for col, group, lab in (("iu.total", 0, "healthy"), ("iu.actions", 0, "healthy"), ("iu.proportion", 0, "healthy"),
                        ("ling.word_count", 1, "impaired"), ("iu.total", 1, "impaired")):
    g = Pf[Pf.label == group]
    m_ = g[g.sexc == "m"][col].dropna(); f_ = g[g.sexc == "f"][col].dropna()
    pv = mannwhitneyu(m_, f_, alternative="two-sided").pvalue
    print(f"  {lab:8s} {col:18s} men {m_.mean():.2f} vs women {f_.mean():.2f}   MW p={pv:.4f}")

print("\n== T7  sex-stratified control-referenced thresholds, 80% specificity target (Pitt) ==")
sens0 = {sx: np.mean(imp[imp.sexc == sx].oof.values >= 0.367) for sx in "fm"}
print(f"  pooled-0.367 sensitivity: f {sens0['f']:.4f}  m {sens0['m']:.4f}  gap {sens0['f']-sens0['m']:.4f}")
for sx in "fm":
    thr = np.quantile(ctl[ctl.sexc == sx].oof.values, 0.80)
    sp = np.mean(ctl[ctl.sexc == sx].oof.values < thr)
    sn = np.mean(imp[imp.sexc == sx].oof.values >= thr)
    print(f"  {sx}: threshold {thr:.4f}  specificity {sp:.4f}  sensitivity {sn:.4f}")

print("\n== T8  Delaware by sex ==")
for sx in "fm":
    g = D[D.sexc == sx]
    print(f"  {sx}: AUC {auc(g.label.values, g.oof.values):.4f} (n={len(g)})")

print("\n== T9  transcript-length quartiles (ling.word_count) ==")
for name, MM, FF in (("Pitt", P, Pf), ):
    wc = FF["ling.word_count"].values
    qt = pd.qcut(wc, 4, labels=False, duplicates="drop")
    aucs = [auc(MM.label.values[qt == k], MM.oof.values[qt == k]) for k in range(4)]
    print(f"  {name}: " + " / ".join(f"{a:.4f}" for a in aucs))
cw = feat["ling.word_count"].values
qt = pd.qcut(cw, 4, labels=False, duplicates="drop")
aucs = [auc(meta.label.values[qt == k], meta.oof.values[qt == k]) for k in range(4)]
print("  combined (diagnostic): " + " / ".join(f"{a:.4f}" for a in aucs))
print("\nDONE phase0_free_f")
