"""
ذِكرى (Dhikra) — speech-based screening for cognitive decline.

Public API
----------
extract_acoustic_features(wav_path)             -> dict   (language-independent)
extract_linguistic_features(text)               -> dict   (English)
extract_linguistic_features_ar(text)            -> dict   (Arabic)
extract_all_features(wav_path, text, lang)      -> dict   (combined, namespaced)
recitation_fidelity(transcript)                 -> dict   (Quran probe)
task_dissociation_index(spont, recit)           -> dict   (core clinical construct)
analyze_session(...)                            -> dict   (full 4-task battery)
"""
from .acoustic_features import extract_acoustic_features
from .linguistic_features import extract_linguistic_features

__version__ = "0.2.0"


def extract_all_features(wav_path: str, text: str | None = None,
                         lang: str = "en") -> dict:
    """
    Combine acoustic + linguistic features into one flat, namespaced dict
    ready to become a row in the feature matrix used for model training.

    acoustic features are prefixed 'ac.'  ;  linguistic features 'ling.'
    """
    feats = {}
    wc = len(text.split()) if text else None
    for k, v in extract_acoustic_features(wav_path, word_count=wc).items():
        feats[f"ac.{k}"] = v

    if text is not None:
        if lang == "en":
            ling = extract_linguistic_features(text)
        elif lang == "ar":
            from .linguistic_features_ar import extract_linguistic_features_ar
            ling = extract_linguistic_features_ar(text)
        else:
            raise ValueError(f"unsupported lang: {lang}")
        for k, v in ling.items():
            feats[f"ling.{k}"] = v
    return feats


def analyze_session(spontaneous_wav: str, spontaneous_text: str,
                    recitation_wav: str | None = None,
                    recitation_text: str | None = None,
                    lang: str = "ar") -> dict:
    """
    Analyse a full assessment session.

    The Arabic instrument pairs a SPONTANEOUS task (picture description --
    degrades earliest in Alzheimer's) with an OVERLEARNED task (Quran
    recitation -- preserved longest). The dissociation between them is the
    core clinical construct: fluent recitation alongside impoverished
    spontaneous speech is the expected early-AD signature.

    Returns one flat feature dict covering both tasks plus the dissociation.
    """
    from .linguistic_features_ar import (recitation_fidelity,
                                         task_dissociation_index)

    feats = {}
    # ---- spontaneous task ----
    spont = extract_all_features(spontaneous_wav, spontaneous_text, lang=lang)
    for k, v in spont.items():
        feats[f"spont.{k}"] = v

    # ---- overlearned (recitation) task ----
    if recitation_wav and recitation_text:
        recit_ac = extract_acoustic_features(
            recitation_wav, word_count=len(recitation_text.split()))
        for k, v in recit_ac.items():
            feats[f"recit.ac.{k}"] = v
        feats.update(recitation_fidelity(recitation_text))

        # ---- the dissociation ----
        spont_ac = {k[3:]: v for k, v in spont.items() if k.startswith("ac.")}
        feats.update(task_dissociation_index(spont_ac, recit_ac))

    return feats
