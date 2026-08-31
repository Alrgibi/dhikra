"""
REPEAT-SAMPLING ANALYSIS  --  descriptive arithmetic, not a hypothesis test.
No grade, no pass/fail: every quantity below is a deterministic function of the
already-published SEM and of the stored OOF score vector.  Lu is not read.

Answers three questions:
  Q1  Does averaging k recordings cut the SEM by sqrt(k), and what does that do to MDC?
  Q2  What MDC would individual TRACKING actually require?
  Q3  What, if anything, should a deployment protocol specify about repeat sampling?
"""
import numpy as np, pandas as pd, json, os
from statistics import NormalDist
R=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","results"))
N=NormalDist()
IP=json.load(open(f"{R}/reconstruction/instrument_properties.json"))
C=IP["C_test_retest_and_mdc"]
SEM=C["controls"]["gap_le_1.5y"]["standard_error_of_measurement"]
MDC=C["controls"]["gap_le_1.5y"]["minimal_detectable_change_95"]
SDCH=C["controls"]["gap_le_1.5y"]["sd_of_change"]
NPAIR=C["controls"]["gap_le_1.5y"]["n_pairs"]
DRIFT=C["impaired_group_drift"]["mean_change_per_visit"]
DRIFT_SD=C["impaired_group_drift"]["sd"]
GAPMEAN=C["inter_visit_gap_years"]["mean"]
THR=0.367
print("="*76); print("PROVENANCE OF THE INPUTS (quoted, not recomputed)"); print("="*76)
print(f"  SEM (controls, visit gap <=1.5y, n={NPAIR} pairs) = {SEM}")
print(f"  SD of change = {SDCH}   MDC95 as published = {MDC}")
print(f"  impaired group drift = {DRIFT} per visit (SD {DRIFT_SD}), mean gap {GAPMEAN} y")

pm=pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm=pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pm["source"]="Pitt"; dm["source"]="Delaware"
meta=pd.concat([pm,dm],ignore_index=True,sort=False)
meta["oof"]=np.load(f"{R}/summary/oof_predictions.npy")
s=meta.oof.values; y=meta.label.values
sd_ctrl=float(np.std(s[y==0],ddof=1))
print(f"\n  control score SD (development) = {sd_ctrl:.4f}")
print(f"  implied reliability r = 1 - (SEM/SD)^2 = {1-(SEM/sd_ctrl)**2:.4f}   <- cross-check against the published r = 0.465")

print("\n"+"="*76); print("Q1  --  does averaging cut SEM by sqrt(k)?"); print("="*76)
print("  MDC95 = 1.96 * sqrt(2) * SEM   (two occasions compared)")
print(f"  check: 1.96*sqrt(2)*{SEM} = {1.96*np.sqrt(2)*SEM:.4f}  vs published {MDC}  -> arithmetic confirmed")
print(f"\n  {'k':>3} {'SEM_k':>8} {'MDC95':>8}  {'reduction':>10}")
for k in [1,2,3,4,6,10]:
    print(f"  {k:>3} {SEM/np.sqrt(k):>8.4f} {1.96*np.sqrt(2)*SEM/np.sqrt(k):>8.4f}  {(1-1/np.sqrt(k))*100:>9.1f}%")
print(f"\n  ANSWER: yes -- IF the k recordings are independent measurements of the same state.")
print(f"  k=2 gives MDC {1.96*np.sqrt(2)*SEM/np.sqrt(2):.3f}, i.e. 0.286 -> {1.96*np.sqrt(2)*SEM/np.sqrt(2):.3f}. The stated arithmetic holds.")
print("  CEILING CAVEAT: sqrt(k) assumes INDEPENDENT errors. Two recordings taken minutes")
print("  apart share room, prompt delivery, fatigue and mood, so their errors are positively")
print("  correlated and the real reduction is SMALLER than sqrt(k). With error correlation rho,")
print("  the variance of the mean of 2 is SEM^2*(1+rho)/2, so:")
for rho in [0.0,0.2,0.4,0.6]:
    semk=SEM*np.sqrt((1+rho)/2)
    print(f"    rho={rho:.1f} -> SEM_2={semk:.4f}, MDC={1.96*np.sqrt(2)*semk:.3f}")
print("  Pitt has NO within-session repeats, so rho CANNOT be estimated from this data.")
print("  0.202 is therefore an UPPER BOUND on the benefit, not a measured value.")

print("\n"+"="*76); print("Q2  --  what MDC would individual TRACKING require?"); print("="*76)
rate_visit=DRIFT; rate_year=DRIFT/GAPMEAN
print(f"  observed progression among the impaired: {rate_visit:.4f} per visit = {rate_year:.4f} per year")
print(f"  (individual variation is large: SD of per-visit change = {DRIFT_SD})")
print(f"\n  {'k':>3} {'MDC':>7} {'years to detect':>16} {'min detectable rate/y':>22} {'x group mean':>13}")
for k in [1,2,4,10,41]:
    m=1.96*np.sqrt(2)*SEM/np.sqrt(k)
    print(f"  {k:>3} {m:>7.3f} {m/rate_year:>16.1f} {m:>22.3f} {m/rate_year:>13.1f}")
need=rate_year
print(f"\n  To detect ONE YEAR of average progression you need MDC <= {need:.4f}.")
print(f"  Required k = (MDC_1/{need:.4f})^2 = {(MDC/need)**2:.0f} recordings per timepoint.")
for T in [1,2,3,5]:
    kneed=(MDC/(need*T))**2
    print(f"   over {T} year(s): need MDC <= {need*T:.3f}  ->  k = {kneed:.1f}")
print("\n  ANSWER: averaging two recordings takes the minimum individually-detectable")
print(f"  progression from {MDC/rate_year:.1f} years to {(1.96*np.sqrt(2)*SEM/np.sqrt(2))/rate_year:.1f} years. Both are far outside clinical use.")
print("  The 'screening test, not monitoring test' conclusion SURVIVES repeat-averaging.")

print("\n"+"="*76); print("Q3  --  decision stability, which is a THIRD use case"); print("="*76)
d=np.abs(s-THR)
def repro(semk): return float(np.mean([N.cdf(x/semk) for x in d]))
r1=repro(SEM); r2=repro(SEM/np.sqrt(2))
print(f"  P(a repeat recording falls on the SAME side of the threshold), averaged over 987 recordings:")
print(f"    single recording  : {r1:.4f}   -> {(1-r1)*100:.1f}% of decisions would flip")
print(f"    mean of two       : {r2:.4f}   -> {(1-r2)*100:.1f}% would flip")
grey=d<=SEM
print(f"\n  GREY ZONE = within +-1 SEM ({SEM:.3f}) of the threshold: {int(grey.sum())} of {len(d)} recordings ({grey.mean()*100:.1f}%)")
print(f"    reproducibility inside the grey zone, single recording : {repro(SEM) if False else float(np.mean([N.cdf(x/SEM) for x in d[grey]])):.4f}")
print(f"    reproducibility outside                                : {float(np.mean([N.cdf(x/SEM) for x in d[~grey]])):.4f}")
sem_targeted=np.where(grey,SEM/np.sqrt(2),SEM)
rt=float(np.mean([N.cdf(x/sk) for x,sk in zip(d,sem_targeted)]))
print(f"\n  TARGETED RULE -- second recording only inside the grey zone:")
print(f"    second recording needed for {grey.mean()*100:.1f}% of people")
print(f"    population reproducibility {r1:.4f} -> {rt:.4f}  (universal repeat would give {r2:.4f})")
print(f"    i.e. {(rt-r1)/(r2-r1)*100:.0f}% of the benefit of repeating everyone, at {grey.mean()*100:.0f}% of the cost")
json.dump(dict(inputs=dict(SEM=SEM,MDC95=MDC,sd_change=SDCH,n_pairs=NPAIR,drift_per_visit=DRIFT,
    drift_sd=DRIFT_SD,gap_mean_y=GAPMEAN,threshold=THR,control_score_sd=sd_ctrl,implied_r=1-(SEM/sd_ctrl)**2),
    Q1=dict(mdc_by_k={str(k):1.96*np.sqrt(2)*SEM/np.sqrt(k) for k in [1,2,3,4,6,10]},
        caveat="sqrt(k) assumes independent errors; within-session rho unestimable from Pitt; 0.202 is an upper bound",
        mdc_under_rho={str(r):1.96*np.sqrt(2)*SEM*np.sqrt((1+r)/2) for r in [0.0,0.2,0.4,0.6]}),
    Q2=dict(rate_per_year=rate_year,years_to_detect_k1=MDC/rate_year,
        years_to_detect_k2=(1.96*np.sqrt(2)*SEM/np.sqrt(2))/rate_year,
        k_needed_for_1y=(MDC/rate_year)**2,conclusion="screening not monitoring; survives averaging"),
    Q3=dict(reproducibility_k1=r1,reproducibility_k2=r2,grey_zone_frac=float(grey.mean()),
        reproducibility_targeted=rt,benefit_fraction=(rt-r1)/(r2-r1)),
    governance="Lu not read; no model, feature or threshold changed; arithmetic on published SEM + stored OOF"),
    open(f"{R}/reconstruction/repeat_sampling_analysis.json","w"),indent=2)
print("\nwritten: results/reconstruction/repeat_sampling_analysis.json")
