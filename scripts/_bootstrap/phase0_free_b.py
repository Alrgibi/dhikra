import numpy as np, pandas as pd, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
rng = np.random.default_rng(42)
def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, float); m = ~np.isnan(s); y, s = y[m], s[m]
    npos, nneg = int((y==1).sum()), int((y==0).sum())
    if npos==0 or nneg==0: return np.nan
    r = pd.Series(s).rank().values
    return (r[y==1].sum() - npos*(npos+1)/2.0)/(npos*nneg)
pm = pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm = pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pf = pd.read_csv(f"{R}/pitt_cookie/features.csv"); df_ = pd.read_csv(f"{R}/delaware/cookie_features.csv")
pm["source"]="Pitt"; dm["source"]="Delaware"
if "visit" not in dm.columns: dm["visit"]=1
meta = pd.concat([pm,dm],ignore_index=True,sort=False); feat = pd.concat([pf,df_],ignore_index=True,sort=False)
meta["oof"] = np.load(f"{R}/summary/oof_predictions.npy")
y = meta["label"].values; sex = meta["sex"].astype(str).str.lower().str[0].values
src = meta["source"].values; pid = meta["participant_id"].astype(str).values

print("="*78); print("CHECK  A2 -- is iu.proportion a duplicate of iu.total?"); print("="*78)
a=feat["iu.total"].values.astype(float); b=feat["iu.proportion"].values.astype(float)
rr = b/np.where(a==0,np.nan,a)
print(f"  spearman = {pd.Series(a).corr(pd.Series(b),method='spearman'):.6f}   pearson = {pd.Series(a).corr(pd.Series(b)):.6f}")
print(f"  ratio proportion/total: unique values = {np.unique(np.round(rr[~np.isnan(rr)],9))[:5]}  (n unique={len(np.unique(np.round(rr[~np.isnan(rr)],9)))})")

print("\n"+"="*78); print("CHECK  B -- repeat-averaging x sex  (Pitt longitudinal visits)"); print("="*78)
P = meta[src=="Pitt"].copy()
cnt = P.groupby("participant_id").size()
rep = cnt[cnt>=2].index
print(f"  Pitt: {len(cnt)} participants, {len(rep)} with >=2 recordings, {int(cnt[cnt>=2].sum())} recordings among repeaters")
Pr = P[P["participant_id"].isin(rep)].copy()
Pr["sx"] = Pr["sex"].astype(str).str.lower().str[0]
lab = Pr.groupby("participant_id")["label"].max()
print("  repeaters by sex:", Pr.groupby('participant_id').first()['sx'].value_counts().to_dict())
for tag, sel in [("ALL", None), ("F", "f"), ("M", "m")]:
    S = Pr if sel is None else Pr[Pr["sx"]==sel]
    if len(S)==0: continue
    a_single = auc(S["label"].values, S["oof"].values)
    g = S.groupby("participant_id").agg(p=("oof","mean"), l=("label","max"))
    a_avg = auc(g["l"].values, g["p"].values)
    # single-visit reference: first visit only, participant level
    f1 = S.sort_values("visit").groupby("participant_id").first()
    a_first = auc(f1["label"].values, f1["oof"].values)
    print(f"  {tag:3s} n_rec={len(S):4d} n_part={S['participant_id'].nunique():3d} | recording-level AUC={a_single:.4f} | first-visit-only AUC={a_first:.4f} | mean-of-visits AUC={a_avg:.4f} | gain over first-visit={a_avg-a_first:+.4f}")

print("\n"+"="*78); print("CHECK  C -- within-sex normative z-scoring of iu.total (free proxy, IN-SAMPLE)"); print("="*78)
v = feat["iu.total"].values.astype(float)
z = np.full_like(v, np.nan)
for s in ["f","m"]:
    m0 = (sex==s) & (y==0)
    mu, sd = np.nanmean(v[m0]), np.nanstd(v[m0], ddof=1)
    z[sex==s] = (v[sex==s]-mu)/sd
    print(f"  control {s}: mean={mu:.3f} sd={sd:.3f} n={int(m0.sum())}")
    m1=(sex==s)&(y==1); print(f"  impaired {s}: mean={np.nanmean(v[m1]):.3f} sd={np.nanstd(v[m1],ddof=1):.3f} n={int(m1.sum())}")
gr=auc(y[sex=='f'],-v[sex=='f'])-auc(y[sex=='m'],-v[sex=='m'])
gz=auc(y[sex=='f'],-z[sex=='f'])-auc(y[sex=='m'],-z[sex=='m'])
print(f"  RAW  : all={auc(y,-v):.4f}  F={auc(y[sex=='f'],-v[sex=='f']):.4f}  M={auc(y[sex=='m'],-v[sex=='m']):.4f}  gap={gr:+.4f}")
print(f"  Z-SEX: all={auc(y,-z):.4f}  F={auc(y[sex=='f'],-z[sex=='f']):.4f}  M={auc(y[sex=='m'],-z[sex=='m']):.4f}  gap={gz:+.4f}")
print(f"  delta pooled = {auc(y,-z)-auc(y,-v):+.4f}")
o = meta["oof"].values.astype(float)
zo = np.full_like(o, np.nan)
for s in ["f","m"]:
    m0=(sex==s)&(y==0); zo[sex==s]=(o[sex==s]-np.nanmean(o[m0]))/np.nanstd(o[m0],ddof=1)
print(f"  MODEL raw  : all={auc(y,o):.4f}  F={auc(y[sex=='f'],o[sex=='f']):.4f}  M={auc(y[sex=='m'],o[sex=='m']):.4f}  gap={auc(y[sex=='f'],o[sex=='f'])-auc(y[sex=='m'],o[sex=='m']):+.4f}")
print(f"  MODEL z-sex: all={auc(y,zo):.4f}  delta pooled = {auc(y,zo)-auc(y,o):+.4f}")
