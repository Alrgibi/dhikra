#!/usr/bin/env python3
"""
feature_health_audit.py -- provenance recovery for the feature-health figures.

WHY THIS EXISTS. THESIS_PLAN.md section 3.2.3 (and Chapter 3 following it)
reports a feature-health audit of the deployed 64 -- maximum missingness 0.012,
mean 0.0002; the two filler features zero in 99.3% of transcripts; the parser's
separately captured filled-pause signal present in 81.8% of transcripts (1,881
tokens; control 2.797 against impaired 3.091 per 100 words) discriminating at
AUC 0.5075. Those figures trace to no result file and no committed script: the
audit was run interactively and its output never committed. This script
recomputes each claim from the committed feature and meta files so the chapter
cites a file rather than a working document.

CRITERIA -- fixed in this docstring before execution; the grading below is
mechanical and the run is report-and-stop. If a figure does not reproduce, the
discrepancy is REPORTED and the prose is corrected to the reproduced value; the
criterion is not adjusted and the run is not iterated.

  population   primary: the 987-recording development pool
               (results/pitt_cookie/features.csv + results/delaware/
               cookie_features.csv, in that order, as train_development.py
               assembles it). The original audit did not record its
               population, so the Pitt-only 548 is also computed and
               reported descriptively; a claim is graded on the primary
               population unless only the secondary matches, in which case
               the match is reported with its population named.
  c1  max missingness over the deployed 64            0.012   (+/- 0.001)
  c2  mean missingness over the deployed 64           0.0002  (+/- 0.0001)
  c3  ling.filler_count == 0 share                    99.3%   (+/- 0.3 pp)
  c4  chat.filled_pause_per100 > 0 share              81.8%   (+/- 0.5 pp)
  c5  filled-pause tokens (per100 * words / 100)      1,881   (+/- 1%)
  c6  mean rate, control / impaired (per 100 words)   2.797 / 3.091 (+/- 0.02)
  c7  AUC of chat.filled_pause_per100 for the label   0.5075  (+/- 0.003)

The deployed 64 are read from results/summary/model_card.json (feature_order).
Missingness is the NaN share per column. AUC is the Mann-Whitney rank AUC.
Nothing here loads a model, scores a recording, or touches the Lu corpus.

Output: results/reconstruction/feature_health_audit.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def rank_auc(score, y):
    score = np.asarray(score, dtype=float)
    y = np.asarray(y, dtype=int)
    m = ~np.isnan(score)
    score, y = score[m], y[m]
    r = rankdata(score)
    n1 = int(y.sum())
    n0 = int(len(y) - n1)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1))


def audit(X, meta, feats):
    y = meta["label"].values.astype(int)
    D = X[feats]
    miss = D.isna().mean()
    out = {
        "n": int(len(X)),
        "max_missingness": float(miss.max()),
        "mean_missingness": float(miss.mean()),
        "argmax_missingness": str(miss.idxmax()),
        "filler_count_zero_share_pct": float((X["ling.filler_count"] == 0).mean() * 100),
        "filler_rate_zero_share_pct": float((X["ling.filler_rate"] == 0).mean() * 100),
        "filled_pause_nonzero_share_pct": float((X["chat.filled_pause_per100"] > 0).mean() * 100),
        "filled_pause_tokens_est": float((X["chat.filled_pause_per100"] * X["ling.word_count"] / 100).sum()),
        "filled_pause_rate_mean_control": float(X.loc[y == 0, "chat.filled_pause_per100"].mean()),
        "filled_pause_rate_mean_impaired": float(X.loc[y == 1, "chat.filled_pause_per100"].mean()),
        "filled_pause_auc": rank_auc(X["chat.filled_pause_per100"].values, y),
    }
    return out


def grade(claims, got):
    g = {}
    for key, (target, tol) in claims.items():
        val = got[key]
        g[key] = {
            "claimed": target,
            "recomputed": val,
            "delta": val - target,
            "reproduced": bool(abs(val - target) <= tol),
            "tolerance": tol,
        }
    return g


def main():
    card = json.load(open(os.path.join(ROOT, "results/summary/model_card.json")))
    feats = card["feature_order"]
    assert len(feats) == 64

    Xp = pd.read_csv(os.path.join(ROOT, "results/pitt_cookie/features.csv"))
    mp = pd.read_csv(os.path.join(ROOT, "results/pitt_cookie/meta.csv"))
    Xd = pd.read_csv(os.path.join(ROOT, "results/delaware/cookie_features.csv"))
    md = pd.read_csv(os.path.join(ROOT, "results/delaware/cookie_meta.csv"))
    assert len(Xp) == len(mp) == 548 and len(Xd) == len(md) == 439

    X = pd.concat([Xp, Xd], ignore_index=True)
    meta = pd.concat([mp[["label"]], md[["label"]]], ignore_index=True)

    primary = audit(X, meta, feats)
    secondary = audit(Xp, mp, feats)

    claims = {
        "max_missingness": (0.012, 0.001),
        "mean_missingness": (0.0002, 0.0001),
        "filler_count_zero_share_pct": (99.3, 0.3),
        "filled_pause_nonzero_share_pct": (81.8, 0.5),
        "filled_pause_tokens_est": (1881.0, 18.81),
        "filled_pause_rate_mean_control": (2.797, 0.02),
        "filled_pause_rate_mean_impaired": (3.091, 0.02),
        "filled_pause_auc": (0.5075, 0.003),
    }
    graded_primary = grade(claims, primary)
    graded_secondary = grade(claims, secondary)

    n_ok = sum(1 for v in graded_primary.values() if v["reproduced"])
    n_ok2 = sum(1 for v in graded_secondary.values() if v["reproduced"])
    verdict = ("REPRODUCED-ON-DEVELOPMENT-POOL" if n_ok == len(claims) else
               "REPRODUCED-ON-PITT-ONLY" if n_ok2 == len(claims) else
               "PARTIAL")

    out = {
        "script": "scripts/feature_health_audit.py",
        "purpose": "provenance recovery: recompute the feature-health figures of THESIS_PLAN section 3.2.3 from committed files",
        "criteria": "fixed in the module docstring before execution; report-and-stop",
        "primary_population": "development pool, 987 recordings (Pitt 548 + Delaware cookie 439)",
        "secondary_population": "Pitt only, 548 recordings (reported because the original audit did not record its population)",
        "primary": {"values": primary, "graded": graded_primary, "n_reproduced": n_ok, "n_claims": len(claims)},
        "secondary_pitt_only": {"values": secondary, "graded": graded_secondary, "n_reproduced": n_ok2},
        "VERDICT": verdict,
    }
    dst = os.path.join(ROOT, "results/reconstruction/feature_health_audit.json")
    json.dump(out, open(dst, "w"), indent=2)
    print("written:", dst)
    print("VERDICT:", verdict, "| primary reproduced %d/%d, pitt-only %d/%d"
          % (n_ok, len(claims), n_ok2, len(claims)))
    for k, v in graded_primary.items():
        flag = "OK " if v["reproduced"] else "DIFF"
        print("  %s %-34s claimed %-9s got %.6g" % (flag, k, v["claimed"], v["recomputed"]))


if __name__ == "__main__":
    main()
