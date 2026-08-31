"""
corpus.py
---------
Builds the feature matrix from a real corpus directory (DementiaBank / Pitt).

This is the ONLY component that has to change when real data arrives -- the
feature engines, the model code and the explainability layer are already
proven. Point this at the corpus folder and it produces (X, y, meta) in exactly
the shape the modelling pipeline expects.

Expected layout (either works)
    corpus/
      Control/*.cha        Dementia/*.cha           <- transcripts
      Control/*.mp3|wav    Dementia/*.mp3|wav       <- audio (optional)
  or a flat folder of .cha files with the group encoded in the @ID header.

Audio is matched to its transcript by filename stem. If audio is absent the
row is still produced from linguistic + CHAT features alone, so the pipeline
degrades gracefully rather than failing.
"""
from __future__ import annotations
import os
import glob
import numpy as np
import pandas as pd

import re
from .chat_parser import parse_cha, group_to_label


def parse_participant_id(file_id: str) -> tuple[str, int | None]:
    """
    Split a Pitt filename into (participant_id, visit_number).

    Pitt is LONGITUDINAL: '002-0', '002-1', '002-3' are three yearly visits by
    the SAME person. This matters enormously for evaluation -- if one visit is
    used for training and another for testing, the classifier can recognise the
    individual's idiosyncratic speech style rather than the disease, and the
    reported accuracy becomes badly optimistic. Grouping by participant is
    therefore mandatory, not optional.
    """
    m = re.match(r"^(\d+)[-_](\d+)$", file_id)
    if m:
        return m.group(1), int(m.group(2))
    return file_id.split("-")[0], None
from .linguistic_features import extract_linguistic_features
from .acoustic_features import extract_acoustic_features
from .information_units import extract_information_units
from .semantic_features import extract_semantic_features

AUDIO_EXT = (".wav", ".mp3", ".WAV", ".MP3")


def _find_audio(cha_path: str) -> str | None:
    stem = os.path.splitext(cha_path)[0]
    for ext in AUDIO_EXT:
        if os.path.exists(stem + ext):
            return stem + ext
    # also look for audio in a sibling folder with the same stem
    base = os.path.basename(stem)
    root = os.path.dirname(os.path.dirname(cha_path))
    for ext in AUDIO_EXT:
        hits = glob.glob(os.path.join(root, "**", base + ext), recursive=True)
        if hits:
            return hits[0]
    return None


def build_dataset(corpus_dir: str, use_audio: bool = True,
                  verbose: bool = True) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    """
    Walk `corpus_dir`, parse every .cha file, extract all features.

    Returns
    -------
    X    : DataFrame  (n_participants x n_features)
    y    : ndarray    binary labels (1 = impaired, 0 = control)
    meta : DataFrame  file_id, age, sex, group, mmse, education, audio_found
    """
    cha_files = sorted(glob.glob(os.path.join(corpus_dir, "**", "*.cha"),
                                 recursive=True))
    if not cha_files:
        raise FileNotFoundError(f"no .cha files found under {corpus_dir}")

    rows, labels, metas = [], [], []
    skipped = 0

    for i, path in enumerate(cha_files, 1):
        tr = parse_cha(path)
        label = group_to_label(tr.group)
        if label is None or not tr.clean_text.strip():
            skipped += 1
            continue

        feats: dict[str, float] = {}

        # linguistic (from the gold-standard transcript)
        for k, v in extract_linguistic_features(tr.clean_text).items():
            feats[f"ling.{k}"] = v
        # CHAT-annotated disfluencies
        feats.update(tr.disfluency_features())
        # information content (Cookie Theft task only -- measures WHETHER the
        # picture was actually described, not merely how fluently)
        feats.update(extract_information_units(tr.clean_text))
        # discourse-level semantic coherence (exploratory)
        feats.update(extract_semantic_features(tr.clean_text))
        # acoustic (optional)
        audio = _find_audio(path) if use_audio else None
        if audio:
            wc = len(tr.clean_text.split())
            try:
                for k, v in extract_acoustic_features(audio, word_count=wc).items():
                    feats[f"ac.{k}"] = v
            except Exception as e:
                if verbose:
                    print(f"  ! acoustic extraction failed for {tr.file_id}: {e}")

        rows.append(feats)
        labels.append(label)
        pid, visit = parse_participant_id(tr.file_id)
        metas.append({
            "file_id": tr.file_id, "participant_id": pid, "visit": visit,
            "age": tr.age, "sex": tr.sex,
            "group": tr.group, "mmse": tr.mmse, "education": tr.education,
            "audio_found": bool(audio),
        })

        if verbose and i % 25 == 0:
            print(f"  processed {i}/{len(cha_files)} files...")

    X = pd.DataFrame(rows)
    y = np.array(labels)
    meta = pd.DataFrame(metas)

    if verbose:
        n_people = meta["participant_id"].nunique() if len(meta) else 0
        print(f"\nbuilt dataset: {X.shape[0]} recordings x {X.shape[1]} features")
        print(f"  from {n_people} unique participants (corpus is longitudinal)")
        print(f"  controls={int((y==0).sum())}  impaired={int((y==1).sum())}")
        print(f"  with audio={int(meta['audio_found'].sum())}   skipped={skipped}")
    return X, y, meta


def save_dataset(X, y, meta, out_dir: str = "data/processed") -> None:
    os.makedirs(out_dir, exist_ok=True)
    X.to_csv(os.path.join(out_dir, "features.csv"), index=False)
    meta.assign(label=y).to_csv(os.path.join(out_dir, "meta.csv"), index=False)
    print(f"saved -> {out_dir}/features.csv , {out_dir}/meta.csv")


# ── ON COMBINING CORPORA ────────────────────────────────────────────────────
# An earlier formulation of this project's finding read: "corpora may be
# combined only when each contributes both classes." That is too strong.
# Balanced class contribution removes the most severe failure mode -- corpus
# identity acting as a proxy for the label -- but it does not eliminate
# residual site effects arising from recording conditions, transcription
# conventions, elicitation wording or population differences.
#
# The defensible statement is:
#
#   Datasets in which corpus or site is strongly associated with diagnostic
#   class should not be naively pooled. Source effects must be explicitly
#   quantified (for example by testing how well corpus membership itself can
#   be predicted, and how strongly it predicts the label) and controlled,
#   whatever the class balance.
#
# Measured in this project: healthy speakers from Pitt versus WLS were
# separable at AUC 0.930 (results/wls/findings.json). A second separability
# figure of 0.872 for Pitt versus Delaware was quoted here until 2026-08-22;
# it traces to no result file and has been withdrawn -- the 0.930 result
# carries the argument on its own, and it is substantial even though Delaware
# contributes both classes.
