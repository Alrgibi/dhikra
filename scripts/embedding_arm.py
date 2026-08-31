"""
embedding_arm.py -- what does the handcrafted feature set give up?

=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-23 BEFORE execution.
=============================================================================

WHY. Negative results 4-6 conclude that the handcrafted feature set has
extracted close to the signal available to it, and the thesis states that
pretrained representations are the principal remaining direction. THAT IS
CURRENTLY AN ASSERTION. This measures it.

WHAT IS MEASURED. A 300-dimensional mean document vector from spaCy's
en_core_web_md pretrained word vectors, replacing the 64 handcrafted features
entirely. Same cohort (Pitt, 548), same architecture, same
StratifiedGroupKFold(5, shuffle=True, random_state=42), same seed. The only
thing that changes is the representation.

WHAT THIS DOES AND DOES NOT MEASURE -- state this wherever the number appears.
  IT IS A FLOOR on what pretrained representations offer. en_core_web_md
  carries static, context-independent word vectors: every occurrence of a word
  has the same vector, and averaging them discards word order entirely. A
  contextual transformer would almost certainly do better.
  THE GAP TO A TRANSFORMER IS UNMEASURED AND UNMEASURABLE ON THIS HARDWARE.
  The device has no torch, no transformers library and no network; model
  weights could only arrive through a 20 MB-per-file transfer channel, and the
  runtime alone is hundreds of megabytes. This is not a choice about rigour, it
  is a hardware constraint, and it must be reported as one rather than as a
  judgement that transformers were not worth testing.

CRITERIA, fixed in advance, against the deployed Pitt figure of 0.8095.
  CEILING-CLAIM-REFUTED   -- embedding AUC >= 0.8395 (at least +0.03). A
      generic pretrained representation with no clinical design beats the
      handcrafted set by a margin. The thesis must retract "the feature set has
      extracted close to the available signal" and replace it with a measured
      gap.
  CEILING-CLAIM-QUALIFIED -- embedding AUC between 0.7795 and 0.8395. Broadly
      comparable. The claim survives as "no better", not as "at the ceiling",
      and the honest wording changes.
  CEILING-CLAIM-SUPPORTED -- embedding AUC <= 0.7795 (at least -0.03). A
      generic representation does worse, which is evidence that the clinical
      design is doing work a generic one does not.
Whichever band it lands in is reported. A result that refutes this project's own
stated conclusion is reported exactly as readily as one that confirms it.

WHAT THIS IS NOT. It is not a deployment candidate and no part of it enters the
deployed system. The model, features and threshold are unchanged; Lu is not
read. A 300-dimensional dense vector would also forfeit every deployability
property this project exists for -- no paper fallback, no explainable
indicators, no operator-facing reference ranges -- so even a large gain here is
a measurement of a cost, not a recommendation.

REGISTRATION HISTORY
  (none)
"""
import json, os, sys, glob
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (ExtraTreesClassifier, GradientBoostingClassifier,
                              RandomForestClassifier, VotingClassifier)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import roc_auc_score

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
DB = os.path.join(os.path.expanduser("~"), "mnt", "DementiaBank", "pitt_cookie")
STATE = os.path.join(os.path.expanduser("~"), "state", "emb")
os.makedirs(STATE, exist_ok=True)
os.chdir(REPO)
sys.path.insert(0, "src")
DEPLOYED_PITT = 0.8095


def vectors(chunk=None, nchunks=4):
    cache = os.path.join(STATE, "vecs.csv")
    if os.path.exists(cache):
        return pd.read_csv(cache)
    if chunk is None:
        parts = [os.path.join(STATE, f"v{i}.csv") for i in range(nchunks)]
        if all(os.path.exists(p) for p in parts):
            df = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
            df.to_csv(cache, index=False); print("assembled", len(df)); return df
        raise SystemExit("pending: " + ", ".join(os.path.basename(p) for p in parts
                                                 if not os.path.exists(p)))
    import spacy
    from dhikra.chat_parser import parse_cha
    nlp = spacy.load("en_core_web_md", disable=["ner", "parser", "lemmatizer", "tagger"])
    meta = set(pd.read_csv("results/pitt_cookie/meta.csv").file_id)
    allf = sorted(glob.glob(os.path.join(DB, "**", "*.cha"), recursive=True))
    rows = []
    for f in allf[chunk::nchunks]:
        t = parse_cha(f)
        if t.file_id not in meta:
            continue
        txt = (t.clean_text or "").strip()
        if not txt:
            continue
        v = nlp(txt).vector
        rows.append({"file_id": t.file_id, **{f"e{i}": float(x) for i, x in enumerate(v)}})
    dest = os.path.join(STATE, f"v{chunk}.csv")
    pd.DataFrame(rows).to_csv(dest, index=False)
    print(f"chunk {chunk}: {len(rows)} -> {os.path.basename(dest)}")


def model():
    p = lambda c: Pipeline([("i", SimpleImputer(strategy="median")),
                            ("s", StandardScaler()), ("c", c)])
    ens = VotingClassifier(estimators=[
        ("et", p(ExtraTreesClassifier(500, min_samples_leaf=3, class_weight="balanced",
                                      random_state=42, n_jobs=-1))),
        ("gb", p(GradientBoostingClassifier(n_estimators=150, max_depth=2,
                                            learning_rate=0.05, random_state=42))),
        ("rf", p(RandomForestClassifier(500, min_samples_leaf=3, class_weight="balanced",
                                        random_state=42, n_jobs=-1))),
    ], voting="soft")
    return CalibratedClassifierCV(estimator=ens, method="sigmoid", cv=3)


def data():
    v = vectors()
    meta = pd.read_csv("results/pitt_cookie/meta.csv")
    d = meta.merge(v, on="file_id", how="inner")
    cols = [c for c in d.columns if c.startswith("e") and c[1:].isdigit()]
    return d[cols].values, d.label.values.astype(int), d.participant_id.values


if __name__ == "__main__":
    if sys.argv[1] == "vec":
        vectors(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif sys.argv[1] == "run":
        X, y, g = data(); k = int(sys.argv[2])
        fp = os.path.join(STATE, f"f{k}.npz")
        if os.path.exists(fp): print("cached", k); sys.exit()
        tr, te = list(StratifiedGroupKFold(5, shuffle=True, random_state=42).split(X, y, g))[k]
        m = model().fit(X[tr], y[tr])
        np.savez(fp, te=te, p=m.predict_proba(X[te])[:, 1])
        print(f"fold {k} done (n={len(y)}, dims={X.shape[1]})")
    else:
        X, y, g = data(); oof = np.zeros(len(y))
        for i in range(5):
            z = np.load(os.path.join(STATE, f"f{i}.npz")); oof[z["te"]] = z["p"]
        auc = float(roc_auc_score(y, oof)); delta = auc - DEPLOYED_PITT
        grade = ("CEILING-CLAIM-REFUTED" if delta >= 0.03 else
                 "CEILING-CLAIM-SUPPORTED" if delta <= -0.03 else "CEILING-CLAIM-QUALIFIED")
        out = {"generated": "2026-08-23",
               "preregistration": "criteria fixed in this script's docstring before execution",
               "representation": "mean of spaCy en_core_web_md static word vectors, 300 dimensions",
               "n": int(len(y)), "n_dimensions": int(X.shape[1]),
               "handcrafted_64_feature_pitt_auc": DEPLOYED_PITT,
               "embedding_auc": round(auc, 4), "delta": round(delta, 4), "GRADE": grade,
               "floor_not_ceiling": ("en_core_web_md vectors are STATIC and context-independent, and "
                                     "averaging discards word order. A contextual transformer would "
                                     "almost certainly do better. This is a FLOOR on what pretrained "
                                     "representations offer."),
               "why_no_transformer": ("the device has no torch, no transformers library and no network; "
                                      "weights could only arrive through a 20 MB-per-file channel and "
                                      "the runtime alone is hundreds of megabytes. A hardware "
                                      "constraint, not a judgement."),
               "not_a_deployment_candidate": ("a 300-dimensional dense vector forfeits every "
                                              "deployability property this project exists for: no paper "
                                              "fallback, no explainable indicators, no operator-facing "
                                              "reference ranges."),
               "scope": "Pitt only. The combined-pool comparison against 0.755 is unmeasured.",
               "governance": "Lu not read; deployed model, features and threshold unchanged"}
        json.dump(out, open("results/reconstruction/embedding_arm.json", "w"), indent=2)
        print(json.dumps(out, indent=2))
