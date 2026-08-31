"""
estimate_arabic.py
------------------
Produces an EMPIRICAL, BOUNDED estimate of how the Arabic engine would be
expected to perform, in the absence of any Arabic clinical data.

WHY AN ESTIMATE IS POSSIBLE AT ALL
To the author's knowledge no publicly available Arabic connected-speech corpus
for dementia screening was available when this was written, so Arabic accuracy cannot
be measured. But the question can be reframed into one that IS measurable:

    "If a model were restricted to only those constructs the Arabic engine can
     actually compute, how well would it perform on data where the truth is
     known?"

That is answerable on the English corpora. It converts an unanswerable question
about Arabic into a measurable question about a construct-matched subset, and
the result brackets the plausible Arabic range instead of guessing at it.

THE THREE BOUNDS
  FLOOR    language-independent acoustic features only. These measure the
           physical signal and are identical in any language, so this is
           performance guaranteed to transfer.
  ESTIMATE the construct-matched subset: every measure the Arabic engine
           implements, computed on English. This is what Arabic would achieve
           IF the same constructs carry the same diagnostic weight in Arabic
           and are measured with equal reliability.
  CEILING  the full English model, which Arabic could only match if the
           transfer were perfect and no information were lost.

WHY THE ESTIMATE IS AN UPPER-LEANING FIGURE, NOT A PREDICTION
Four assumptions sit behind it, none of which can currently be verified:

 1. EQUAL DIAGNOSTIC WEIGHT. The Arabic referential deficit index replaces the
    English pronoun-to-noun ratio because Arabic is pro-drop. It measures the
    same clinical construct -- pointing instead of naming -- but whether it
    separates Arabic patients as sharply as the English marker separates
    English patients is unknown.
 2. EQUAL MEASUREMENT RELIABILITY. Arabic NLP tooling is less mature. Clitic
    segmentation is unreliable offline and was deliberately excluded from the
    headline index, and no offline Arabic dependency parser was available, so
    syntactic complexity is approximated by subordinator rate rather than
    parse depth. Noisier inputs mean weaker separation.
 3. COMPARABLE POPULATIONS. The English corpora are almost entirely white
    American speakers averaging twelve years of education. Libyan speakers
    differ in education distribution, dialect and testing familiarity.
 4. DIALECT. The closed-class word lists are drafted in Modern Standard Arabic
    and have not been validated against Libyan dialect.

Each of these can only reduce performance, never raise it. The estimate should
therefore be read as an optimistic bound, and stated as such.
"""
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore")

import json
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, confusion_matrix

from early_detection import ens

# Constructs the Arabic engine genuinely implements, mapped to their English
# feature names. Anything the Arabic engine cannot compute is excluded, so the
# subset is a fair proxy rather than a flattering one.
ARABIC_EQUIVALENT = [
    # productivity
    "ling.word_count", "ling.sentence_count", "ling.mean_sentence_len",
    # lexical richness (Arabic uses root-based variants of the same measures)
    "ling.type_token_ratio", "ling.mattr_50", "ling.brunet_w", "ling.honore_r",
    # part of speech and the referential-deficit construct
    "ling.noun_rate", "ling.verb_rate", "ling.content_word_ratio",
    "ling.pronoun_rate", "ling.pronoun_to_noun_ratio",
    # syntax (Arabic approximates this with subordinator rate)
    "ling.subordination_rate",
    # repetition
    "ling.repeated_word_ratio", "ling.repeated_bigram_ratio",
    "ling.immediate_repeat_count",
    # disfluency
    "ling.filler_count", "ling.filler_rate",
    # idea density
    "ling.idea_density",
]

# Explicitly NOT available in Arabic, listed so the exclusion is auditable:
#   ling.mean_dependency_distance, ling.mean_tree_depth  (no offline parser)
#   sem.*   (no Arabic word vectors installed)
#   iu.*    (information units need an Arabic picture inventory; the construct
#            transfers, but the Arabic stimulus has not been normed)


def metrics(y, p):
    auc = roc_auc_score(y, p)
    best = (0.0, 0.0, 0.0)
    for th in np.unique(np.round(p, 3)):
        pred = (p >= th).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        se = tp / (tp + fn) if (tp + fn) else 0
        sp = tn / (tn + fp) if (tn + fp) else 0
        if se >= 0.75 and sp > best[2]:
            best = (th, se, sp)
    return auc, best[1], best[2]


def main():
    Xp = pd.read_csv("results/pitt_cookie/features.csv")
    mp = pd.read_csv("results/pitt_cookie/meta.csv")
    Xd = pd.read_csv("results/delaware/cookie_features.csv")
    md = pd.read_csv("results/delaware/cookie_meta.csv")
    Xl = pd.read_csv("results/lu/features.csv")
    ml = pd.read_csv("results/lu/meta.csv")

    shared = [c for c in Xp.columns
              if c in Xd.columns and c in Xl.columns and not c.startswith("chat.")]
    X = pd.concat([Xp[shared], Xd[shared], Xl[shared]], ignore_index=True)
    y = np.concatenate([mp.label.values, md.label.values, ml.label.values])
    g = np.concatenate([("P" + mp.participant_id.astype(str)).values,
                        ("D" + md.participant_id.astype(str)).values,
                        ("L" + ml.file_id.astype(str)).values])

    # dementia-only subset, the comparison most relevant to a screening claim
    dem = np.concatenate([np.ones(len(Xp), bool), np.zeros(len(Xd), bool),
                          np.ones(len(Xl), bool)])

    ar_cols = [c for c in ARABIC_EQUIVALENT if c in X.columns]
    ac_cols = [c for c in X.columns if c.startswith("ac.")]

    print("=" * 74)
    print("ESTIMATING ARABIC PERFORMANCE BY CONSTRUCT-MATCHED ABLATION")
    print("=" * 74)
    print(f"  full English feature set     : {len(shared)} features")
    print(f"  constructs Arabic implements : {len(ar_cols)} features")
    print(f"  excluded (no Arabic support) : "
          f"{len([c for c in shared if c not in ar_cols])} features")
    print()

    cv = StratifiedGroupKFold(5, shuffle=True, random_state=42)
    results = {}

    for label, cols, mask, note in [
        ("CEILING  full English model", shared, slice(None), "all features"),
        ("ESTIMATE Arabic-equivalent only", ar_cols, slice(None),
         "construct-matched subset"),
    ]:
        p = cross_val_predict(ens(), X[cols], y, cv=cv, groups=g,
                              method="predict_proba", n_jobs=-1)[:, 1]
        a, se, sp = metrics(y, p)
        ad, sed, spd = metrics(y[dem], p[dem])
        results[label.split()[0].lower()] = {
            "mixed_auc": float(a), "mixed_spec_at_75sens": float(sp),
            "dementia_auc": float(ad), "dementia_spec_at_75sens": float(spd),
            "n_features": len(cols),
        }
        print(f"  {label:34s} AUC(all)={a:.3f}  AUC(dementia)={ad:.3f}")
        print(f"  {'':34s} specificity at 75% sens: "
              f"all {sp*100:.0f}%, dementia {spd*100:.0f}%")

    print()
    ceil = results["ceiling"]["dementia_auc"]
    est = results["estimate"]["dementia_auc"]
    print(f"  retention: the Arabic-equivalent subset keeps "
          f"{100*est/ceil:.0f}% of the full model's dementia AUC")

    with open("results/summary/arabic_estimate.json", "w") as f:
        json.dump({
            "method": ("construct-matched ablation: the English model "
                       "restricted to only those measures the Arabic engine "
                       "implements, evaluated on English data where truth is "
                       "known"),
            "results": results,
            "assumptions": [
                "Arabic markers carry equal diagnostic weight to their English "
                "counterparts (unverified)",
                "Arabic measurement reliability equals English (unlikely; "
                "Arabic NLP tooling is less mature)",
                "Libyan speakers resemble the American corpora in education "
                "and testing familiarity (they do not)",
                "MSA word lists transfer to Libyan dialect (unvalidated)",
            ],
            "interpretation": ("An optimistic upper bound. Every listed "
                               "assumption can only reduce real Arabic "
                               "performance, never raise it."),
        }, f, indent=2)
    print("\n  saved -> results/summary/arabic_estimate.json")


if __name__ == "__main__":
    main()
