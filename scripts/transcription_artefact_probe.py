"""
transcription_artefact_probe.py -- how much of the Pitt figure is transcription
convention rather than speech?

=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-23 BEFORE the model was run.
The diagnostic counts in the DISCOVERY section below were computed first; the
model comparison this script grades had not been run when these criteria were
fixed.
=============================================================================

DISCOVERY. CHAT marks an omitted sound with parentheses -- "dryin(g)" for a
speaker who said "dryin'". chat_parser.clean_utterance strips most CHAT markup
but NOT this, so the token reaching the feature extractors is "dryin(g)".
Consequences, all of them silent:
  * spaCy tokenises it as "dryin" + "(" + "g" + ")", so the VERB IS NEVER
    RECOGNISED. The affected words are precisely the action verbs the
    information-unit scorer looks for: dryin(g) 96, runnin(g) 84, washin(g) 69,
    fallin(g) 67, gettin(g) 67, reachin(g) 43, standin(g) 37.
  * "dryin" and "drying" count as DIFFERENT TYPES, so type-token ratio,
    MATTR-50, Brunet's W and Honore's R are all corrupted.
  * 58.9% of Pitt transcripts are affected, 1,193 tokens, 1.88% of all tokens.

WHY IT MATTERS MORE THAN A TYPO. The rate is DIFFERENTIAL BY CLASS:
      Pitt controls  1.44 paren-forms per 100 words, 49.4% of transcripts
      Pitt impaired  3.18 per 100 words, 77.0% of transcripts
  The artefact ALONE reaches AUC 0.6908 in Pitt -- higher than most individual
  deployed features. The scorer was silently penalising impaired speakers for a
  transcription convention.

IS IT A REAL PHONETIC MARKER OR A SITE CONVENTION? Delaware answers, and the
answer is unambiguous. Same CHAT convention, different site, different
transcribers:
      Delaware controls 0.123 per 100 words, impaired 0.183; AUC 0.5220
  An order of magnitude lower and at chance. A genuine phonetic property of
  impaired speech would not be ten times rarer in another cohort. THIS IS A
  PITTSBURGH TRANSCRIPTION CONVENTION THAT CORRELATES WITH DIAGNOSIS.

WHY IT SURVIVED THE PROJECT'S OWN CHAT-MARKUP EXCLUSION. The deployed feature
set deliberately contains no chat.* features, because the corpus-compatibility
finding showed transcription convention separates healthy speakers at AUC 0.930.
That exclusion removed markup FEATURES. It did not remove markup from the
TRANSCRIPT TEXT the linguistic features are computed on. The exclusion was
incomplete and this is the leak.

WHY IT IS ALSO A TRAIN/SERVE MISMATCH. The deployed application transcribes with
faster-whisper, which emits standard orthography. "dryin(g)" cannot occur at
inference. So the model was fitted partly on a signal channel THAT DOES NOT
EXIST IN DEPLOYMENT, and the corrected figure is closer to what the deployed
system actually receives.

WHAT THIS SCRIPT MEASURES. Re-extract all 64 deployed features from Pitt
transcripts with the artefact removed -- parenthesised sounds restored and
residual non-word characters (stray parentheses, IPA symbols, quotes, & * / :)
stripped -- and re-run the deployed architecture under the deployed protocol.
Everything else identical: same features, same CalibratedClassifierCV(sigmoid,
cv=3) over the committed ensemble, StratifiedGroupKFold(5, shuffle, rs=42),
seed 42.

CRITERIA, fixed in advance.
  ARTEFACT-MATERIAL   -- corrected AUC is at least 0.01 BELOW the deployed
      0.8095. Part of the reported Pitt discrimination is transcription
      convention, the thesis must say so, and the corrected figure is the one
      that describes deployment.
  ARTEFACT-NEGLIGIBLE -- corrected AUC within 0.01 of 0.8095. The defect is
      real and differential but the full model absorbs it; report the defect
      and the null.
  ARTEFACT-HELPS      -- corrected AUC at least 0.01 ABOVE 0.8095, i.e. the
      mangled tokens were costing performance. Report as a correction that
      cannot be deployed without a new external test.
Whichever band it lands in is reported. A result that lowers the headline
figure is reported exactly as readily as one that raises it.

GOVERNANCE AND SCOPE. This is a REPORTED EXPERIMENT, not a deployment change.
Correcting the extractor would change the features the frozen model receives
and would therefore forfeit the locked external validation, so the deployed
pipeline is NOT modified. Lu is not read and not re-scored.

REGISTRATION HISTORY
  2026-08-23, AMENDMENT 1, BEFORE ANY MODEL RESULT: feature re-extraction split
  into five cached chunks. The semantic features load en_core_web_md and the
  single pass exceeded the Cowork VM's 45-second process limit. Harness change
  only -- identical files, identical committed extractors, identical cleaning.
  No criterion or threshold altered.
"""
import json, os, re, sys, glob
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
STATE = os.path.join(os.path.expanduser("~"), "state", "artefact")
os.makedirs(STATE, exist_ok=True)
os.chdir(REPO)
sys.path.insert(0, "src")
FEATS = json.load(open("results/summary/model_card.json"))["feature_order"]
DEPLOYED_PITT = 0.8095

PAREN = re.compile(r"\(([a-zA-Z]+)\)")
RESIDUE = re.compile(r"[^a-zA-Z0-9\s\.\,\?\!']")


def clean(txt):
    """Restore the omitted sound, then strip residual non-word characters --
    i.e. the text as a standard-orthography ASR pipeline would deliver it."""
    return re.sub(r"\s+", " ", RESIDUE.sub(" ", PAREN.sub(r"\1", txt))).strip()


def features(chunk=None, nchunks=5):
    """Chunked: semantic features need en_core_web_md and the whole pass
    exceeds the Cowork VM's 45-second per-call process limit."""
    cache = os.path.join(STATE, "corrected_features.csv")
    if os.path.exists(cache):
        return pd.read_csv(cache)
    if chunk is None:
        parts = [os.path.join(STATE, f"part{i}.csv") for i in range(nchunks)]
        if all(os.path.exists(p) for p in parts):
            df = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
            df.to_csv(cache, index=False); print("assembled", len(df)); return df
        raise SystemExit("chunks pending: " + ", ".join(
            os.path.basename(p) for p in parts if not os.path.exists(p)))
    from dhikra.chat_parser import parse_cha
    from dhikra.linguistic_features import extract_linguistic_features
    from dhikra.information_units import extract_information_units
    from dhikra.semantic_features import extract_semantic_features
    meta = pd.read_csv("results/pitt_cookie/meta.csv").set_index("file_id")
    rows = []
    allf = sorted(glob.glob(os.path.join(DB, "**", "*.cha"), recursive=True))
    for f in (allf[chunk::nchunks] if chunk is not None else allf):
        t = parse_cha(f)
        if t.file_id not in meta.index:
            continue
        txt = clean((t.clean_text or "").strip())
        if not txt:
            continue
        d = {"file_id": t.file_id}
        for k, v in extract_linguistic_features(txt).items():
            d[f"ling.{k}"] = v
        d.update(extract_information_units(txt, scene="kitchen"))
        d.update(extract_semantic_features(txt))
        rows.append(d)
    df = pd.DataFrame(rows)
    dest = cache if chunk is None else os.path.join(STATE, f"part{chunk}.csv")
    df.to_csv(dest, index=False)
    print("re-extracted", len(df), "->", os.path.basename(dest))
    return df


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
    df = features()
    meta = pd.read_csv("results/pitt_cookie/meta.csv")
    d = meta.merge(df, on="file_id", how="inner")
    for c in FEATS:
        if c not in d.columns:
            d[c] = np.nan
    return d[FEATS].values, d.label.values.astype(int), d.participant_id.values


if __name__ == "__main__":
    if sys.argv[1] == "extract":
        features(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif sys.argv[1] == "run":
        X, y, g = data()
        fold = int(sys.argv[2])
        fp = os.path.join(STATE, f"f{fold}.npz")
        if os.path.exists(fp):
            print("cached", fold); sys.exit()
        tr, te = list(StratifiedGroupKFold(5, shuffle=True, random_state=42).split(X, y, g))[fold]
        m = model().fit(X[tr], y[tr])
        np.savez(fp, te=te, p=m.predict_proba(X[te])[:, 1])
        print(f"fold {fold} done (n={len(y)})")
    else:
        X, y, g = data()
        oof = np.zeros(len(y))
        for i in range(5):
            z = np.load(os.path.join(STATE, f"f{i}.npz")); oof[z["te"]] = z["p"]
        auc = float(roc_auc_score(y, oof))
        delta = auc - DEPLOYED_PITT
        grade = ("ARTEFACT-MATERIAL" if delta <= -0.01 else
                 "ARTEFACT-HELPS" if delta >= 0.01 else "ARTEFACT-NEGLIGIBLE")
        out = {"generated": "2026-08-23",
               "preregistration": "criteria fixed in this script's docstring before the model was run",
               "n": int(len(y)),
               "deployed_pitt_auc": DEPLOYED_PITT,
               "corrected_transcript_auc": round(auc, 4),
               "delta": round(delta, 4),
               "GRADE": grade,
               "artefact_rates_per_100_words": {
                   "pitt_control": 1.44, "pitt_impaired": 3.18, "pitt_auc_of_artefact_alone": 0.6908,
                   "delaware_control": 0.123, "delaware_impaired": 0.183,
                   "delaware_auc_of_artefact_alone": 0.5220},
               "single_feature_effect": {"iu.total": {"raw": 0.7538, "corrected": 0.7465},
                                         "iu.actions": {"raw": 0.7332, "corrected": 0.7155}},
               "scope": ("REPORTED EXPERIMENT, NOT A DEPLOYMENT CHANGE. Correcting the extractor "
                         "would change the features the frozen model receives and forfeit the "
                         "locked external validation. Lu not read."),
               "deployment_note": ("faster-whisper emits standard orthography, so the artefact "
                                   "cannot occur at inference. The corrected figure is closer to "
                                   "what the deployed system actually receives than the reported one.")}
        json.dump(out, open("results/reconstruction/transcription_artefact_probe.json", "w"), indent=2)
        print(json.dumps(out, indent=2))
