"""
simulate_cohort.py
------------------
>>> PIPELINE TEST HARNESS -- NOT A SOURCE OF RESULTS <<<

Generates a synthetic cohort of feature vectors so that the modelling code can
be verified end-to-end BEFORE the real DementiaBank corpus arrives. Nothing
produced here is a research finding, and no number from this file will ever
appear in the thesis as a result.

WHY IT EXISTS
Waiting for data access to test the training code would waste weeks. By
simulating a cohort with the same feature names and plausible distributions,
every part of the pipeline (leakage-free CV, metrics, explainability) is
debugged in advance. When the real corpus lands, the ONLY change is the data
loader -- the model code is already proven to run.

HOW THE SYNTHETIC EFFECTS ARE SET
Group differences are injected in the DIRECTIONS reported in the clinical
literature (impaired speakers pause more and longer, speak more slowly, use
more pronouns relative to nouns, show lower lexical richness and simpler
syntax). Effect sizes are set MODEST and deliberately noisy so the harness
does not produce implausibly perfect separation. The true separability here is
an arbitrary choice of the simulation, NOT an estimate of real performance.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

# feature: (control_mean, control_sd, shift_in_SD_for_impaired)
#   positive shift = value goes UP in the impaired group
FEATURE_SPEC = {
    # --- acoustic: timing / fluency ---
    "ac.phonation_ratio":         (0.72, 0.09, -0.55),
    "ac.pause_count":             (12.0, 4.0,  +0.60),
    "ac.pause_mean_s":            (0.45, 0.15, +0.65),
    "ac.pause_sd_s":              (0.20, 0.08, +0.35),
    "ac.pause_rate_per_min":      (22.0, 7.0,  +0.60),
    "ac.dur_total_s":             (75.0, 25.0, +0.15),
    "ac.est_speech_rate_sylpm":   (190.0, 35.0, -0.55),
    "ac.est_articulation_rate_syls": (4.3, 0.8, -0.45),
    # --- acoustic: pitch / voice quality ---
    "ac.f0_mean_hz":              (145.0, 35.0, +0.05),
    "ac.f0_sd_hz":                (28.0, 9.0,  -0.35),
    "ac.f0_cv":                   (0.19, 0.06, -0.35),
    "ac.jitter_local":            (0.018, 0.007, +0.30),
    "ac.shimmer_local":           (0.095, 0.030, +0.30),
    "ac.hnr_db":                  (14.0, 4.0,  -0.30),
    # --- linguistic: richness / productivity ---
    "ling.word_count":            (105.0, 40.0, -0.40),
    "ling.mean_sentence_len":     (11.5, 3.0,  -0.45),
    "ling.type_token_ratio":      (0.62, 0.09, -0.55),
    "ling.mattr_50":              (0.70, 0.07, -0.50),
    "ling.brunet_w":              (9.6, 0.8,  +0.45),
    "ling.honore_r":              (1450.0, 350.0, -0.40),
    # --- linguistic: 'empty speech' markers ---
    "ling.pronoun_rate":          (0.11, 0.04, +0.60),
    "ling.noun_rate":             (0.22, 0.05, -0.55),
    "ling.pronoun_to_noun_ratio": (0.55, 0.25, +0.75),
    "ling.content_word_ratio":    (0.46, 0.06, -0.45),
    "ling.idea_density":          (4.6, 0.8,  -0.40),
    # --- linguistic: syntax / repetition / disfluency ---
    "ling.mean_dependency_distance": (2.6, 0.6, -0.25),
    "ling.mean_tree_depth":       (4.6, 1.0,  -0.45),
    "ling.subordination_rate":    (0.90, 0.40, -0.40),
    "ling.repeated_word_ratio":   (0.38, 0.09, +0.40),
    "ling.repeated_bigram_ratio": (0.06, 0.04, +0.35),
    "ling.filler_rate":           (0.020, 0.015, +0.45),
    # --- CHAT-annotated disfluencies ---
    "chat.retracing_per100":      (2.2, 1.4, +0.50),
    "chat.reformulation_per100":  (1.1, 0.9, +0.45),
    "chat.filled_pause_per100":   (2.6, 1.8, +0.45),
    "chat.unintelligible_per100": (0.7, 0.8, +0.35),
    # --- deliberately UNINFORMATIVE features (noise controls) ---
    "ac.spectral_centroid_mean":  (1800.0, 400.0, 0.0),
    "ac.zcr_mean":                (0.09, 0.03, 0.0),
    "ac.mfcc3_mean":              (-5.0, 8.0, 0.0),
    "ac.mfcc7_sd":                (12.0, 4.0, 0.0),
}


def simulate_cohort(n_control: int = 80, n_impaired: int = 76,
                    seed: int = 42, noise_scale: float = 1.0):
    """
    Returns (X, y, meta). Cohort size defaults roughly mirror the ADReSS
    benchmark scale so the harness exercises the same small-n regime.
    """
    rng = np.random.default_rng(seed)
    rows, labels = [], []

    for label, n in ((0, n_control), (1, n_impaired)):
        for _ in range(n):
            row = {}
            for feat, (mu, sd, shift) in FEATURE_SPEC.items():
                val = rng.normal(mu, sd * noise_scale)
                if label == 1:
                    val += shift * sd
                row[feat] = val
            rows.append(row)
            labels.append(label)

    X = pd.DataFrame(rows)
    y = np.array(labels)

    # simulate realistic missingness (some recordings fail voice-quality extraction)
    for col in ["ac.jitter_local", "ac.shimmer_local", "ac.hnr_db"]:
        mask = rng.random(len(X)) < 0.04
        X.loc[mask, col] = np.nan

    meta = pd.DataFrame({
        "age": rng.normal(70, 8, len(X)).round(1),
        "sex": rng.choice(["male", "female"], len(X)),
        "label": y,
    })

    # shuffle so class order is not an artefact
    idx = rng.permutation(len(X))
    return (X.iloc[idx].reset_index(drop=True),
            y[idx],
            meta.iloc[idx].reset_index(drop=True))


if __name__ == "__main__":
    X, y, meta = simulate_cohort()
    print(f"synthetic cohort: {X.shape[0]} participants x {X.shape[1]} features")
    print(f"  controls={int((y==0).sum())}  impaired={int((y==1).sum())}")
    print(f"  missing values injected: {int(X.isna().sum().sum())}")
