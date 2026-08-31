"""
score_scorer_check.py -- compare the human scoring sheet against the automated
information-unit scorer. Run AFTER the sheet is filled in.

Usage: score_scorer_check.py docs/scorer_check/scoring_sheet_FILLED.csv

=============================================================================
WHICH STATISTICS, AND WHY -- fixed here before any sheet exists
=============================================================================

PRIMARY: BLAND-ALTMAN on the per-transcript TOTAL COUNT.
  Reports the mean difference (automated minus human) and the 95% limits of
  agreement. This is primary because it answers the question that matters --
  does the software produce the count a human would? -- on the absolute scale,
  and because it is NOT distorted by how the sample was drawn. The sample was
  stratified across the range of automated counts, which widens the spread of
  true values; that inflates correlation-type statistics and leaves
  Bland-Altman alone.
  A systematic bias matters more than it first appears: AUC is rank-based and
  survives a constant offset, but the normative comparisons and the reference
  ranges shown to an operator do not.

SECONDARY: ICC(2,1), two-way random effects, absolute agreement, single rater.
  The right ICC form when comparing two raters who are both "the measurement",
  and when absolute agreement rather than mere consistency is required.
  Interpretation follows Koo and Li (2016), the standard reference: below 0.50
  poor, 0.50-0.75 moderate, 0.75-0.90 good, above 0.90 excellent. For an
  automated scorer offered as a substitute for manual scoring, GOOD (>= 0.75)
  is the minimum defensible and EXCELLENT (>= 0.90) is what would justify
  replacing manual scoring outright.
  REPORTED WITH THE STRATIFICATION CAVEAT, because the sampling design inflates
  it. Say so wherever it is quoted.

TERTIARY: per-unit Cohen's kappa on the 23 binary decisions.
  Localises the disagreement. Pooled kappa across units would be misleading
  because base rates differ enormously between units, so kappa is computed per
  unit and reported as a table, lowest first. Units where kappa is low are
  where the fixed synonym lists fail, and that list is the actionable output.
  Landis and Koch bands: 0.61-0.80 substantial, above 0.80 almost perfect.
  Kappa is undefined where a unit is constant in both raters; those are
  reported as raw agreement instead, which is the honest treatment rather than
  dropping them.

ALSO REPORTED: directional error counts per unit -- how often the software
  credited a unit the human did not (FALSE CREDIT, the lists are too loose) and
  how often the human credited a unit the software did not (MISS, the lists are
  too tight). The direction is what tells you how to fix it.

=============================================================================
WHAT THIS CAN AND CANNOT ESTABLISH
=============================================================================
It measures AGREEMENT BETWEEN ONE HUMAN AND THE SOFTWARE. It does NOT measure
human reliability, because there is one rater: no second scorer means no
estimate of how much of any disagreement is the software and how much is one
person's idiosyncrasy. A second scorer on even half the sample would fix that
and should be reported as the limitation it is.
Twenty transcripts also give imprecise limits of agreement -- roughly plus or
minus half a standard deviation of the differences. Report the estimate with
that imprecision stated; do not present a tidy interval.

A POOR RESULT IS A FINDING AND GETS REPORTED. The instrument's most important
feature family failing to match human judgement is a substantive result about
this project and about every project that lemma-matches information units.
"""
import json, os, sys
import numpy as np
import pandas as pd

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
os.chdir(REPO)
sys.path.insert(0, "src")
OUT = "docs/scorer_check"


def icc21(a, b):
    """Two-way random effects, absolute agreement, single measures."""
    Y = np.vstack([a, b]).T.astype(float)
    n, k = Y.shape
    gm = Y.mean()
    msr = k * ((Y.mean(1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((Y.mean(0) - gm) ** 2).sum() / (k - 1)
    mse = ((Y - Y.mean(1, keepdims=True) - Y.mean(0, keepdims=True) + gm) ** 2).sum() / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))


def kappa(a, b):
    a = np.asarray(a, int); b = np.asarray(b, int)
    po = (a == b).mean()
    pe = sum(((a == v).mean() * (b == v).mean()) for v in (0, 1))
    return float("nan") if abs(1 - pe) < 1e-12 else float((po - pe) / (1 - pe)), float(po)


if __name__ == "__main__":
    from dhikra.chat_parser import parse_cha
    from dhikra.information_units import extract_information_units
    import glob
    man = json.load(open(f"{OUT}/sample_manifest.json"))
    UNITS = man["units"]
    human = pd.read_csv(sys.argv[1])
    human.columns = [c.strip() for c in human.columns]
    missing = [u for u in UNITS if u not in human.columns]
    if missing:
        raise SystemExit("scoring sheet is missing columns: " + ", ".join(missing))

    DB = os.path.join(os.path.expanduser("~"), "mnt", "DementiaBank", "pitt_cookie")
    byid = {}
    for f in glob.glob(os.path.join(DB, "**", "*.cha"), recursive=True):
        t = parse_cha(f)
        byid[t.file_id] = (t.clean_text or "").strip()

    auto = []
    for fid in man["file_ids_in_presentation_order"]:
        iu = extract_information_units(byid[fid])
        auto.append([int(iu.get(f"iu.has_{u}", 0.0)) for u in UNITS])
    A = np.array(auto)
    H = human[UNITS].fillna(0).astype(int).values
    if H.shape != A.shape:
        raise SystemExit(f"shape mismatch: human {H.shape} vs automated {A.shape}")

    at, ht = A.sum(1), H.sum(1)
    d = at - ht
    bias, sd = float(d.mean()), float(d.std(ddof=1))
    res = {"generated_from": sys.argv[1], "n_transcripts": int(len(at)), "n_units": len(UNITS),
           "PRIMARY_bland_altman": {
               "mean_difference_auto_minus_human": round(bias, 3),
               "sd_of_differences": round(sd, 3),
               "limits_of_agreement_95": [round(bias - 1.96 * sd, 2), round(bias + 1.96 * sd, 2)],
               "direction": ("the software credits MORE units than the human" if bias > 0
                             else "the software credits FEWER units than the human" if bias < 0
                             else "no mean difference"),
               "caveat": "n=20 gives imprecise limits, roughly +/- half an SD of the differences"},
           "SECONDARY_icc21": {
               "icc": round(icc21(at, ht), 3),
               "koo_li_band": None,
               "caveat": "the sample was stratified across the range of automated counts, which "
                         "INFLATES ICC relative to a random sample. Quote it with this sentence."},
           "human_total_mean": round(float(ht.mean()), 2),
           "automated_total_mean": round(float(at.mean()), 2)}
    i = res["SECONDARY_icc21"]["icc"]
    res["SECONDARY_icc21"]["koo_li_band"] = ("excellent" if i >= 0.90 else "good" if i >= 0.75
                                             else "moderate" if i >= 0.50 else "poor")
    per = []
    for j, u in enumerate(UNITS):
        k = kappa(A[:, j], H[:, j])
        kv, po = (k if isinstance(k, tuple) else (float("nan"), float("nan")))
        per.append({"unit": u, "kappa": None if np.isnan(kv) else round(kv, 3),
                    "raw_agreement": round(po, 3),
                    "false_credit_auto_only": int(((A[:, j] == 1) & (H[:, j] == 0)).sum()),
                    "miss_human_only": int(((A[:, j] == 0) & (H[:, j] == 1)).sum())})
    per.sort(key=lambda r: (r["kappa"] is not None, r["kappa"] if r["kappa"] is not None else 9))
    res["TERTIARY_per_unit"] = per
    res["actionable"] = {
        "lists_too_loose": [p["unit"] for p in per if p["false_credit_auto_only"] >= 3],
        "lists_too_tight": [p["unit"] for p in per if p["miss_human_only"] >= 3]}
    json.dump(res, open("results/reconstruction/scorer_agreement.json", "w"), indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != "TERTIARY_per_unit"}, indent=2))
    print("\nworst-agreeing units:")
    for p in per[:8]:
        print("  %-22s kappa=%-7s raw=%.2f  false-credit=%d  miss=%d"
              % (p["unit"], p["kappa"], p["raw_agreement"],
                 p["false_credit_auto_only"], p["miss_human_only"]))
