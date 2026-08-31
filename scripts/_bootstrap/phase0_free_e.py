"""Item 6 -- hard-negative analysis on the DEVELOPMENT controls (Lu already done in A5)."""
import numpy as np, pandas as pd, os
R=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","results"))
pm=pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm=pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pf=pd.read_csv(f"{R}/pitt_cookie/features.csv"); df_=pd.read_csv(f"{R}/delaware/cookie_features.csv")
pm["source"]="Pitt"; dm["source"]="Delaware"
meta=pd.concat([pm,dm],ignore_index=True,sort=False); feat=pd.concat([pf,df_],ignore_index=True,sort=False)
meta["oof"]=np.load(f"{R}/summary/oof_predictions.npy")
THR=0.367
C=meta[meta.label==0].copy(); Ci=C.index.values
C["fp"]=(C["oof"]>=THR).astype(int)
print("="*78); print(f"ITEM 6 -- development controls at threshold {THR}"); print("="*78)
print(f"  n controls={len(C)}  false positives={int(C.fp.sum())} ({C.fp.mean():.3f})  by corpus:")
print(C.groupby("source")["fp"].agg(["size","sum","mean"]).to_string())
print("\n  who gets flagged (mean of FP vs TN among controls):")
rows=[]
for col in ["age","education","mmse"]:
    if col in C.columns and C[col].notna().sum()>20:
        a=C.loc[C.fp==1,col].astype(float); b=C.loc[C.fp==0,col].astype(float)
        rows.append((col,a.mean(),b.mean(),(a.mean()-b.mean())/np.nanstd(C[col].astype(float))))
sx=C.groupby("fp")["sex"].apply(lambda s: s.astype(str).str.lower().str[0].value_counts(normalize=True).to_dict())
print(f"   sex mix  TN={sx.get(0)}  FP={sx.get(1)}")
for c,a,b,d in rows: print(f"   {c:10s} FP={a:8.2f}  TN={b:8.2f}  SMD={d:+.3f}")
F=feat.loc[Ci]; fp=C.fp.values
res=[]
for col in F.columns:
    v=F[col].values.astype(float)
    if np.nanstd(v)==0 or np.isnan(v).all(): continue
    d=(np.nanmean(v[fp==1])-np.nanmean(v[fp==0]))/np.nanstd(v)
    res.append((col,np.nanmean(v[fp==1]),np.nanmean(v[fp==0]),d))
res=sorted(res,key=lambda r:-abs(r[3]))[:12]
print("\n  top 12 feature differences, flagged controls vs correctly-passed controls:")
for c,a,b,d in res: print(f"   {c:32s} FP={a:8.3f}  TN={b:8.3f}  SMD={d:+.3f}")
# is being flagged predicted by transcript length?
tot=feat["iu.total"].values.astype(float); den=feat["iu.per_100_words"].values.astype(float)
nw=np.where(den>0,100.0*tot/den,np.nan)
print(f"\n  words: FP={np.nanmean(nw[Ci][fp==1]):.1f}  TN={np.nanmean(nw[Ci][fp==0]):.1f}")
print(f"  iu.total: FP={np.nanmean(tot[Ci][fp==1]):.2f}  TN={np.nanmean(tot[Ci][fp==0]):.2f}")
# how many flagged controls are BELOW the 20th percentile of transcript length?
q=np.nanpercentile(nw[Ci],20)
print(f"  P(short transcript | flagged) = {np.nanmean(nw[Ci][fp==1]<q):.3f}   P(short | passed) = {np.nanmean(nw[Ci][fp==0]<q):.3f}   (short = bottom 20% by words, cut={q:.0f})")
