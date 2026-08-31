"""phase0_free_f_addendum.py -- ONE quantity, written AFTER phase0_free_f's output was seen.

DISCLOSED TIMING: phase0_free_f declared the plan's "sensitivity gap ... from
0.176" as the by-sex sensitivity gap at the fixed 0.367 threshold, ran once,
and got 0.0733 -- a mismatch. Re-reading THESIS_PLAN 5.2.1, the sentence
compares the STRATIFIED control-referenced threshold against the POOLED
control-referenced threshold at the same 80% specificity target, not against
0.367. This addendum computes that one baseline and nothing else. It is a
correction of the reconstruction's declaration, made after seeing output, and
is recorded exactly as such (the class of Chapter 3's worked example 1).

TARGET, quoted before this run: pooled-threshold sensitivity gap 0.176.
METHOD: threshold = numpy.quantile(Pitt control OOF, 0.80) pooled across
sexes; sensitivity by sex at that threshold; gap = female - male.
"""
import numpy as np, pandas as pd, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
pm = pd.read_csv(f"{R}/pitt_cookie/meta.csv"); pm["source"]="Pitt"
dm = pd.read_csv(f"{R}/delaware/cookie_meta.csv"); dm["source"]="Delaware"
if "visit" not in dm.columns: dm["visit"]=1
meta = pd.concat([pm,dm],ignore_index=True,sort=False)
meta["oof"]=np.load(f"{R}/summary/oof_predictions.npy")
P = meta[meta.source=="Pitt"].copy()
P["sexc"]=P["sex"].astype(str).str.lower().str[0]
ctl, imp = P[P.label==0], P[P.label==1]
thr = np.quantile(ctl.oof.values, 0.80)
print(f"pooled control-referenced threshold (80% target, all Pitt controls): {thr:.4f}")
for sx in "fm":
    sp = np.mean(ctl[ctl.sexc==sx].oof.values < thr)
    sn = np.mean(imp[imp.sexc==sx].oof.values >= thr)
    print(f"  {sx}: specificity {sp:.4f}  sensitivity {sn:.4f}")
sf = np.mean(imp[imp.sexc=="f"].oof.values >= thr); sm = np.mean(imp[imp.sexc=="m"].oof.values >= thr)
print(f"pooled-threshold sensitivity gap (f - m): {sf-sm:.4f}   [plan target: 0.176]")
