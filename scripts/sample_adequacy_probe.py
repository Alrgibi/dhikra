"""
SAMPLE-ADEQUACY PROBE  --  PRE-REGISTERED
Written and committed 2026-08-25 BEFORE any arm was executed.

MOTIVATION (from Phase-0 item-6 diagnostics, already run and reported):
  Among the 522 development controls, the 215 flagged at the fixed screening
  threshold 0.367 differ from the 307 correctly passed controls mainly in
  BREVITY -- 103.2 words vs 127.4, iu.total SMD -1.194 -- and NOT in age
  (SMD -0.180) or MMSE (SMD -0.237).  The same pattern appears in the Lu
  false-positive analysis (A5): flagged Lu controls are the ones who did not
  mention the stool falling.  The specificity failure therefore looks like a
  SAMPLE-ADEQUACY failure, not a demographic one.

QUESTION
  Does declaring short recordings NON-REPORTABLE (a validity criterion, as
  standard clinical instruments have) raise specificity without costing
  sensitivity?  This changes NO model, NO feature, NO threshold.  It is a
  protocol rule about when the instrument may be read at all.

DESIGN
  Development set only (Pitt 548 + Delaware 439 cookie).  Fixed threshold
  0.367.  Word count = the deployed extractor's own alpha-token count,
  recovered exactly as 100 * iu.total / iu.per_100_words.
  Gate grid, declared here and not to be extended: W in {50, 60, 75, 90, 100}.

PRIMARY CRITERIA (mechanical)
  For each W:  d_spec = spec(retained) - spec(all)
               d_sens = sens(retained) - sens(all)
               keep_c = retained controls / all controls
               keep_i = retained impaired / all impaired
  GATE-JUSTIFIED      if ANY W has d_spec >= +0.05 AND d_sens >= -0.05
                         AND keep_c >= 0.80 AND keep_i >= 0.80
  GATE-HARMFUL        if the W maximising d_spec has d_sens < -0.10
  GATE-NOT-JUSTIFIED  otherwise
  Report-and-stop.  The grade is whatever the rule returns.

EQUITY CRITERION (co-primary, must also pass for a recommendation to follow)
  Among controls, compare gated-out vs retained on age, education and sex.
  EQUITY-CLEAN if every |SMD| < 0.40 and the sex proportion shifts < 0.10.
  Otherwise EQUITY-COMPROMISED: a gate that preferentially excludes older or
  less-educated speakers transfers the instrument's failure onto them and is
  not recommendable however well it scores above.

GOVERNANCE
  Lu is NOT scored under any grade.  Lu has been evaluated once and is spent.
  This means the probe CANNOT be externally validated, and that limitation is
  the finding's ceiling, not an oversight -- it is the third occasion on which
  the lock rule has cost this project a result (after the Cox recalibration
  decision and the post-lock feature set).  Any recommendation that follows is
  DEVELOPMENT-EVIDENCE ONLY and must be labelled so wherever it appears.

INTERPRETIVE ASYMMETRY
  A negative result is informative and will be reported with equal prominence:
  it would mean brevity in a healthy speaker is genuine signal the model is
  right to weigh, and that the specificity ceiling is intrinsic to the task
  rather than an artefact of inadequate sampling.
"""
import numpy as np, pandas as pd, os, json
R=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","results"))
def auc(y,s):
    y=np.asarray(y); s=np.asarray(s,float); m=~np.isnan(s); y,s=y[m],s[m]
    a,b=int((y==1).sum()),int((y==0).sum())
    if a==0 or b==0: return float("nan")
    r=pd.Series(s).rank().values
    return float((r[y==1].sum()-a*(a+1)/2.0)/(a*b))
THR=0.367; GRID=[50,60,75,90,100]
pm=pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm=pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pf=pd.read_csv(f"{R}/pitt_cookie/features.csv"); df_=pd.read_csv(f"{R}/delaware/cookie_features.csv")
pm["source"]="Pitt"; dm["source"]="Delaware"
meta=pd.concat([pm,dm],ignore_index=True,sort=False); feat=pd.concat([pf,df_],ignore_index=True,sort=False)
meta["oof"]=np.load(f"{R}/summary/oof_predictions.npy")
tot=feat["iu.total"].values.astype(float); den=feat["iu.per_100_words"].values.astype(float)
meta["words"]=np.where(den>0,100.0*tot/den,np.nan)
y=meta.label.values; s=meta.oof.values; w=meta.words.values
spec0=float(np.mean(s[y==0]<THR)); sens0=float(np.mean(s[y==1]>=THR)); auc0=auc(y,s)
print(f"BASELINE  n={len(meta)}  spec={spec0:.4f}  sens={sens0:.4f}  auc={auc0:.4f}")
print(f"{'W':>5} {'keep_c':>7} {'keep_i':>7} {'spec':>7} {'d_spec':>8} {'sens':>7} {'d_sens':>8} {'auc':>7}")
out={}
for W in GRID:
    k=(w>=W)&~np.isnan(w)
    kc=float(np.mean(k[y==0])); ki=float(np.mean(k[y==1]))
    sp=float(np.mean(s[k&(y==0)]<THR)); se=float(np.mean(s[k&(y==1)]>=THR)); au=auc(y[k],s[k])
    out[W]=dict(keep_c=kc,keep_i=ki,spec=sp,d_spec=sp-spec0,sens=se,d_sens=se-sens0,auc=au,
                n_ret=int(k.sum()),n_drop=int((~k).sum()))
    print(f"{W:>5} {kc:>7.3f} {ki:>7.3f} {sp:>7.4f} {sp-spec0:>+8.4f} {se:>7.4f} {se-sens0:>+8.4f} {au:>7.4f}")
ok=[W for W in GRID if out[W]["d_spec"]>=0.05 and out[W]["d_sens"]>=-0.05 and out[W]["keep_c"]>=0.80 and out[W]["keep_i"]>=0.80]
best=max(GRID,key=lambda W:out[W]["d_spec"])
grade="GATE-JUSTIFIED" if ok else ("GATE-HARMFUL" if out[best]["d_sens"]<-0.10 else "GATE-NOT-JUSTIFIED")
print(f"\nGRADE: {grade}   passing W = {ok}   (best d_spec at W={best})")
print("\nEQUITY CHECK (controls only, gate at the best W by d_spec):")
C=meta[meta.label==0].copy(); g=(C.words.values>=best)
eq={}; flag=[]
for col in ["age","education","mmse"]:
    if col in C.columns and C[col].notna().sum()>20:
        v=C[col].astype(float).values; sd=np.nanstd(v)
        smd=float((np.nanmean(v[~g])-np.nanmean(v[g]))/sd) if sd>0 else 0.0
        eq[col]=dict(gated_out=float(np.nanmean(v[~g])),retained=float(np.nanmean(v[g])),smd=smd)
        print(f"  {col:10s} gated-out={np.nanmean(v[~g]):8.2f}  retained={np.nanmean(v[g]):8.2f}  SMD={smd:+.3f}")
        if abs(smd)>=0.40: flag.append(col)
sx=C.sex.astype(str).str.lower().str[0]
pf_=float(np.mean(sx[~g]=="f")); pr=float(np.mean(sx[g]=="f"))
eq["prop_female"]=dict(gated_out=pf_,retained=pr,shift=pf_-pr)
print(f"  {'female':10s} gated-out={pf_:8.3f}  retained={pr:8.3f}  shift={pf_-pr:+.3f}")
if abs(pf_-pr)>=0.10: flag.append("sex")
eqgrade="EQUITY-CLEAN" if not flag else "EQUITY-COMPROMISED"
print(f"  EQUITY GRADE: {eqgrade}  {('violations: '+', '.join(flag)) if flag else ''}")
print(f"  controls gated out at W={best}: {int((~g).sum())} of {len(C)}")
json.dump(dict(registration="module docstring, committed before execution",threshold=THR,grid=GRID,
    baseline=dict(spec=spec0,sens=sens0,auc=auc0,n=len(meta)),arms={str(k):v for k,v in out.items()},
    grade=grade,passing_W=ok,best_W=best,equity=eq,equity_grade=eqgrade,equity_violations=flag,
    governance="Lu NOT scored; development evidence only; cannot be externally validated because Lu is spent"),
    open(f"{R}/reconstruction/sample_adequacy_probe.json","w"),indent=2)
print("\nwritten: results/reconstruction/sample_adequacy_probe.json")
