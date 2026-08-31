import numpy as np, pandas as pd, os
from math import sqrt
R = os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","results"))
def auc(y,s):
    y=np.asarray(y); s=np.asarray(s,float); m=~np.isnan(s); y,s=y[m],s[m]
    a,b=int((y==1).sum()),int((y==0).sum())
    if a==0 or b==0: return np.nan
    r=pd.Series(s).rank().values
    return (r[y==1].sum()-a*(a+1)/2.0)/(a*b)
def ndtri(p):
    from statistics import NormalDist; return NormalDist().inv_cdf(p)
def ndtr(x):
    from statistics import NormalDist; return NormalDist().cdf(x)
pm=pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm=pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pf=pd.read_csv(f"{R}/pitt_cookie/features.csv"); df_=pd.read_csv(f"{R}/delaware/cookie_features.csv")
pm["source"]="Pitt"; dm["source"]="Delaware"
if "visit" not in dm.columns: dm["visit"]=1
meta=pd.concat([pm,dm],ignore_index=True,sort=False); feat=pd.concat([pf,df_],ignore_index=True,sort=False)
meta["oof"]=np.load(f"{R}/summary/oof_predictions.npy")
y=meta["label"].values; sex=meta["sex"].astype(str).str.lower().str[0].values; src=meta["source"].values

print("="*78); print("CHECK D -- where does the IU sex gap live?  (the word-count channel)"); print("="*78)
wcol=[c for c in ["n_words","lex.n_words","lex.word_count","tokens.n_words"] if c in feat.columns]
print("  word-count column:", wcol)
if wcol:
    w=feat[wcol[0]].values.astype(float)
    for s in ["f","m"]:
        for l in [0,1]:
            m=(sex==s)&(y==l); print(f"   {s} label{l}: n_words mean={np.nanmean(w[m]):7.2f} sd={np.nanstd(w[m],ddof=1):6.2f} n={int(m.sum())}")
    print(f"   n_words AUC: all={auc(y,-w):.4f} F={auc(y[sex=='f'],-w[sex=='f']):.4f} M={auc(y[sex=='m'],-w[sex=='m']):.4f} gap={auc(y[sex=='f'],-w[sex=='f'])-auc(y[sex=='m'],-w[sex=='m']):+.4f}")
for c in ["iu.total","iu.per_100_words"]:
    v=feat[c].values.astype(float)
    print(f"   {c}: gap={auc(y[sex=='f'],-v[sex=='f'])-auc(y[sex=='m'],-v[sex=='m']):+.4f}  (F={auc(y[sex=='f'],-v[sex=='f']):.4f} M={auc(y[sex=='m'],-v[sex=='m']):.4f})")

print("\n"+"="*78); print("CHECK E -- decomposing the repeat-averaging gain: noise vs progression"); print("="*78)
P=meta[src=="Pitt"].copy(); cnt=P.groupby("participant_id").size(); rep=cnt[cnt>=2].index
Pr=P[P["participant_id"].isin(rep)].copy().sort_values(["participant_id","visit"])
first=Pr.groupby("participant_id").first().reset_index()
mean_=Pr.groupby("participant_id").agg(oof=("oof","mean"),label=("label","max"),sex=("sex","first"),k=("oof","size")).reset_index()
kbar=mean_["k"].mean()
base=auc(first["label"].values,first["oof"].values)
both=auc(mean_["label"].values,mean_["oof"].values)
# arm 1: average controls only, impaired = first visit
mix1=pd.concat([mean_[mean_.label==0][["participant_id","oof","label"]], first[first.label==1][["participant_id","oof","label"]]])
mix2=pd.concat([first[first.label==0][["participant_id","oof","label"]], mean_[mean_.label==1][["participant_id","oof","label"]]])
print(f"  n_part={len(first)}  mean visits per participant = {kbar:.2f}")
print(f"  A first-visit only ................. AUC={base:.4f}")
print(f"  B average CONTROLS only ........... AUC={auc(mix1['label'].values,mix1['oof'].values):.4f}  (delta {auc(mix1['label'].values,mix1['oof'].values)-base:+.4f})  <- pure noise reduction, no progression possible")
print(f"  C average IMPAIRED only ........... AUC={auc(mix2['label'].values,mix2['oof'].values):.4f}  (delta {auc(mix2['label'].values,mix2['oof'].values)-base:+.4f})  <- noise reduction + disease progression")
print(f"  D average BOTH .................... AUC={both:.4f}  (delta {both-base:+.4f})")
# Spearman-Brown prediction from test-retest r
r=0.465
rk=kbar*r/(1+(kbar-1)*r)
d_obs=sqrt(2)*ndtri(base); d_true=d_obs/sqrt(r); d_k=d_true*sqrt(rk)
pred=ndtr(d_k/sqrt(2))
print(f"\n  Spearman-Brown: test-retest r={r:.3f}, k={kbar:.2f} -> reliability of mean = {rk:.3f}")
print(f"  d' observed(first visit) = {d_obs:.4f} ; implied true d' = {d_true:.4f} ; d' of k-mean = {d_k:.4f}")
print(f"  PREDICTED AUC from noise reduction alone = {pred:.4f}")
print(f"  OBSERVED AUC of the k-mean               = {both:.4f}")
print(f"  EXCESS over the noise-reduction prediction = {both-pred:+.4f}  <- attributable to progression / r underestimate")
# specificity at the deployed threshold
THR=0.367
for tag,dfm in [("first visit",first),("mean of visits",mean_)]:
    c0=dfm[dfm.label==0]; c1=dfm[dfm.label==1]
    print(f"  @thr={THR}: {tag:15s} spec={np.mean(c0['oof'].values<THR):.4f} (n={len(c0)})  sens={np.mean(c1['oof'].values>=THR):.4f} (n={len(c1)})")
