"""phase0_free_g.py -- provenance reconstruction of THESIS_PLAN 5.26's indeterminate-band sweep.

WRITTEN 2026-08-28 under the same owner protocol as phase0_free_f (targets quoted
before code; reproduced value wins; report-and-stop, one execution). The plan's
5.26 band-sweep table has no committed producer: the committed
scripts/repeat_sampling_analysis.py computes the +-1 SEM grey zone and its
inside/outside reproducibility (capture: repeat_sampling_stdout_capture.txt,
2026-08-28) but not the narrower half-widths. The formula is evident from that
committed script and is used here unchanged: with stored OOF scores p, threshold
0.367 and SEM 0.1032, d = |p - 0.367|; a case is INDETERMINATE at half-width w
when d <= w*SEM; among definite cases, sensitivity and specificity are computed
at 0.367 and reproducibility is mean Phi(d/SEM). No model is fitted, no Lu file
opened; inputs are the four OOF arrays and the two meta files.

TARGETS, quoted from THESIS_PLAN 5.26 before execution
(band | %indeterminate | sens definite | spec definite | repro definite):
  none  |  0.0% | 0.7570 | 0.5881 | 0.8355
  +-0.25 SEM | 12.7% | 0.7852 | 0.5914 | 0.8772
  +-0.50 SEM | 23.7% | 0.8094 | 0.5757 | 0.9109
  +-0.75 SEM | 32.7% | 0.8361 | 0.5559 | 0.9345
  +-1.00 SEM | 41.5% | 0.8705 | 0.5265 | 0.9538
GATES (must reproduce the committed script's values under the same formula):
  reproducibility_k1 0.8355; grey fraction at +-1 SEM 41.5%;
  inside 0.6690; outside 0.9538.
MISMATCH RULE: a reproduced value that differs from the plan wins; the plan is
corrected and the discrepancy reported at full strength, never the reverse.
"""
import numpy as np, pandas as pd, os
from statistics import NormalDist
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
N = NormalDist()
SEM, THR = 0.1032, 0.367
pm = pd.read_csv(f"{R}/pitt_cookie/meta.csv"); dm = pd.read_csv(f"{R}/delaware/cookie_meta.csv")
meta = pd.concat([pm, dm], ignore_index=True, sort=False)
y = meta["label"].values
p = np.load(f"{R}/summary/oof_predictions.npy")
oly = np.load(f"{R}/summary/oof_labels.npy")
print("ORDER CHECK:", bool((oly == y).all()), len(p), "recordings")
d = np.abs(p - THR)
phi = np.array([N.cdf(x / SEM) for x in d])
print(f"gate: reproducibility_k1 = {phi.mean():.4f}")
grey = d <= SEM
print(f"gate: grey fraction +-1 SEM = {grey.mean()*100:.1f}%  inside {phi[grey].mean():.4f}  outside {phi[~grey].mean():.4f}")
print(f"\n{'band':>10} {'%indet':>7} {'sens_def':>9} {'spec_def':>9} {'repro_def':>10}")
for w in (0.0, 0.25, 0.50, 0.75, 1.00):
    ind = d <= w * SEM if w > 0 else np.zeros(len(d), bool)
    df_ = ~ind
    sens = np.mean(p[df_ & (y == 1)] >= THR)
    spec = np.mean(p[df_ & (y == 0)] < THR)
    rep = phi[df_].mean()
    print(f"{('none' if w==0 else f'+-{w:.2f} SEM'):>10} {ind.mean()*100:>6.1f}% {sens:>9.4f} {spec:>9.4f} {rep:>10.4f}")
print("\nDONE phase0_free_g")
