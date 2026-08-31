import numpy as np, pandas as pd, os
R=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","results"))
def auc(y,s):
    y=np.asarray(y); s=np.asarray(s,float); m=~np.isnan(s); y,s=y[m],s[m]
    a,b=int((y==1).sum()),int((y==0).sum())
    if a==0 or b==0: return np.nan
    r=pd.Series(s).rank().values
    return (r[y==1].sum()-a*(a+1)/2.0)/(a*b)
pm=pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm=pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pf=pd.read_csv(f"{R}/pitt_cookie/features.csv"); df_=pd.read_csv(f"{R}/delaware/cookie_features.csv")
pm["source"]="Pitt"; dm["source"]="Delaware"
meta=pd.concat([pm,dm],ignore_index=True,sort=False); feat=pd.concat([pf,df_],ignore_index=True,sort=False)
y=meta["label"].values; sex=meta["sex"].astype(str).str.lower().str[0].values; src=meta["source"].values
# recover word count exactly:  per_100_words = 100*total/n_words
tot=feat["iu.total"].values.astype(float); den=feat["iu.per_100_words"].values.astype(float)
nw=np.where(den>0, 100.0*tot/den, np.nan)
if "n_words" in meta.columns:
    chk=meta["n_words"].values.astype(float); m=~np.isnan(chk)&~np.isnan(nw)
    print(f"  recovery check vs Delaware meta n_words: max abs err = {np.nanmax(np.abs(nw[m]-chk[m])):.6f} on n={int(m.sum())}")
print("="*78); print("CHECK D2 -- the word-count channel"); print("="*78)
for s in ["f","m"]:
    for l in [0,1]:
        m=(sex==s)&(y==l); print(f"  {s} label{l}: words mean={np.nanmean(nw[m]):7.1f} sd={np.nanstd(nw[m],ddof=1):6.1f}  IU mean={np.nanmean(tot[m]):5.2f}  n={int(m.sum())}")
print(f"\n  n_words AUC(-w): all={auc(y,-nw):.4f}  F={auc(y[sex=='f'],-nw[sex=='f']):.4f}  M={auc(y[sex=='m'],-nw[sex=='m']):.4f}  gap={auc(y[sex=='f'],-nw[sex=='f'])-auc(y[sex=='m'],-nw[sex=='m']):+.4f}")
# healthy men vs healthy women: words and IU
from scipy import stats
for nm,v in [("n_words",nw),("iu.total",tot),("iu.per_100_words",den)]:
    a=v[(sex=='f')&(y==0)]; b=v[(sex=='m')&(y==0)]; c=v[(sex=='f')&(y==1)]; d=v[(sex=='m')&(y==1)]
    t0=stats.mannwhitneyu(a[~np.isnan(a)],b[~np.isnan(b)]); t1=stats.mannwhitneyu(c[~np.isnan(c)],d[~np.isnan(d)])
    print(f"  {nm:18s} healthy F={np.nanmean(a):7.2f} vs M={np.nanmean(b):7.2f} p={t0.pvalue:.4f} | impaired F={np.nanmean(c):7.2f} vs M={np.nanmean(d):7.2f} p={t1.pvalue:.4f}")
# partial: does IU count add over word count, within each sex?
import itertools
print("\n  Two-feature check (rank-sum of z of IU and words), within sex:")
for s in ["f","m"]:
    m=(sex==s)
    zi=(tot[m]-np.nanmean(tot[m]))/np.nanstd(tot[m]); zw=(nw[m]-np.nanmean(nw[m]))/np.nanstd(nw[m])
    print(f"   {s}: IU alone={auc(y[m],-zi):.4f}  words alone={auc(y[m],-zw):.4f}  IU+words={auc(y[m],-(zi+zw)):.4f}  IU-words={auc(y[m],-(zi-zw)):.4f}")
