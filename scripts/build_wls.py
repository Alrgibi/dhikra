"""
build_wls.py
------------
Builds a dataset from the Wisconsin Longitudinal Study: Cookie Theft
descriptions recorded in 2011, linked to clinical cognitive diagnoses made in
2020.

WHY THIS CORPUS MATTERS, IN TWO DISTINCT WAYS

 1. WHY IT LOOKED LIKE IT WOULD FIX THE SPECIFICITY PROBLEM -- AND WHY IT DID NOT.
    (Outcome, recorded 2026-08-22: pooling WLS was REJECTED. Healthy speakers
    from the two studies separate at AUC 0.930 on transcription convention
    alone -- results/wls/findings.json. The rationale below is kept as the
    reasoning that motivated the check, not as a conclusion.) The Pitt corpus supplies only 243
    control recordings from 99 people, so the model has seen very little
    normal speech and over-flags healthy speakers. WLS adds roughly 1,370
    descriptions of the SAME task from a random population sample, of whom 669
    were confirmed cognitively normal nine years later. Adding normative data
    from WLS is an established technique, reported to improve performance on
    this task (Frontiers in Computer Science, 2021).

 2. IT ALLOWS A PROSPECTIVE TEST OF EARLY DETECTION. Every previous result in
    this project answers "does this person's speech look impaired NOW?" -- the
    speech and the diagnosis come from the same moment. WLS separates them by
    nine years, which permits the question the project actually exists to
    answer: does today's speech predict a diagnosis years before it is made?

    That is a fundamentally stronger claim, and it is the difference between
    detecting disease and detecting risk.

LABELS
The 2020 assessment provides two summary variables. The conservative one
(positive predictive value) minimises false positives; the broad one (negative
predictive value) minimises false negatives and is coded normal / impaired /
dementia. The broad measure is used here because it classifies 941 people
rather than 187, and because for a SCREENING instrument the relevant target is
any cognitive concern rather than confirmed dementia alone.

HONEST CAVEATS RECORDED WITH THE DATA
  * WLS participants are almost entirely white, non-Hispanic Americans with
    about twelve years of education, so the normative range they define is
    narrower than a general population.
  * The 2020 diagnoses were made by telephone interview and consensus review,
    not by imaging or autopsy.
  * A person normal in 2020 may still develop impairment later, so the control
    label means "not yet impaired", not "never will be".
"""
import os
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd

from dhikra.chat_parser import parse_cha
from dhikra.linguistic_features import extract_linguistic_features
from dhikra.information_units import extract_information_units
from dhikra.semantic_features import extract_semantic_features

# Paths come from corpus_paths.json (see src/dhikra/paths.py); the original
# sandbox constants /home/claude/wls and /mnt/user-data/uploads/WLS-data.xlsx
# died with that environment (de-hardcoded 2026-08-20). wls_xlsx is the WLS
# 2020-outcomes spreadsheet from the TalkBank download -- REQUIRED for labels,
# and not yet located on this machine; resolve() raises a clear error until
# the config entry is filled in.
from dhikra.paths import resolve
OUT = "results/wls"

# broad (negative-predictive-value) summary: 1 normal, 2 impaired, 3 dementia
NPV_MAP = {1: 0, 2: 1, 3: 1}
NPV_NAME = {1: "normal", 2: "impaired", 3: "dementia"}
CONSENSUS_NAME = {-2: "not assessed", 1: "normal", 2: "MCI", 3: "dementia",
                  4: "no diagnosis"}


def load_outcomes() -> pd.DataFrame:
    xlsx = resolve("wls_xlsx")
    d2020 = pd.read_excel(xlsx, "Data - 2020")
    d1104 = pd.read_excel(xlsx, "Data - 2004, 2011")

    # the transcript filename is the last five digits of idtlkbnk
    d2020["file_id"] = (d2020.idtlkbnk.astype(str).str[-5:])
    keep = {
        "file_id": "file_id",
        "sex": "sex",
        "age 2020": "age_2020",
        "Research diagnosis via consensus": "consensus_dx",
        "Consensus outcome for Alzheimer\u2019s disease": "ad_outcome",
        "Negative predictive value summary outcome": "npv",
        "Positive predictive value summary outcome": "ppv",
        "TICSm score": "ticsm",
    }
    out = d2020[[c for c in keep if c in d2020.columns]].rename(columns=keep)

    # education and 2011 age from the earlier sheet, matched the same way
    idcol = next((c for c in d1104.columns
                  if "idtlkbnk" in str(c).lower()), None)
    if idcol:
        d1104["file_id"] = d1104[idcol].astype(str).str[-5:]
        cols = {"file_id": "file_id"}
        for c in d1104.columns:
            lc = str(c).lower()
            if "education" in lc:
                cols[c] = "education"
            elif "age" in lc and "2011" in lc:
                cols[c] = "age_2011"
        sub = d1104[[c for c in cols if c in d1104.columns]].rename(columns=cols)
        out = out.merge(sub.drop_duplicates("file_id"), on="file_id", how="left")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    wls_dir = resolve("wls_root")
    files = sorted(glob.glob(os.path.join(wls_dir, "**", "*.cha"),
                             recursive=True))
    print(f"WLS transcripts found: {len(files)}")

    outcomes = load_outcomes()
    print(f"2020 outcome records : {len(outcomes)}")

    rows, metas, skipped = [], [], 0
    for i, path in enumerate(files, 1):
        tr = parse_cha(path)
        text = tr.clean_text.strip()
        if len(text.split()) < 10:          # too little speech to analyse
            skipped += 1
            continue
        feats = {}
        for k, v in extract_linguistic_features(text).items():
            feats[f"ling.{k}"] = v
        feats.update(tr.disfluency_features())
        feats.update(extract_information_units(text, scene="kitchen"))
        feats.update(extract_semantic_features(text))
        rows.append(feats)
        metas.append({"file_id": tr.file_id, "participant_id": tr.file_id,
                      "n_words": len(text.split())})
        if i % 200 == 0:
            print(f"  processed {i}/{len(files)}")

    X = pd.DataFrame(rows)
    meta = pd.DataFrame(metas).merge(outcomes, on="file_id", how="left")
    print(f"\nfeature matrix: {X.shape}   (skipped {skipped} too-short files)")

    meta["label"] = meta.npv.map(NPV_MAP)
    meta["npv_name"] = meta.npv.map(NPV_NAME)
    meta["consensus_name"] = meta.consensus_dx.map(CONSENSUS_NAME)

    have = meta.label.notna()
    print(f"\nlinked to a 2020 outcome: {int(have.sum())} of {len(meta)}")
    print(meta.loc[have, "npv_name"].value_counts().to_string())
    print()
    print("consensus diagnosis (subset with full assessment):")
    print(meta.consensus_name.value_counts(dropna=False).to_string())

    X.to_csv(f"{OUT}/features.csv", index=False)
    meta.to_csv(f"{OUT}/meta.csv", index=False)
    print(f"\nwritten to {OUT}/")


if __name__ == "__main__":
    main()
