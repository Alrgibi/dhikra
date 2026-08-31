"""
acoustic_features.py
--------------------
Language-INDEPENDENT acoustic / prosodic features from an audio recording.

These features work identically for English (DementiaBank) and Arabic
(Quran recitation, picture description), because they measure the *physical
signal*, not the words. This is why the acoustic engine transfers to Arabic
with no retraining.

Feature families
  * Timing & fluency : total duration, speech vs. silence, phonation ratio,
                       pause count, pause statistics, speech/articulation rate
  * Pitch (F0)       : mean, sd, range, coefficient of variation (monotonicity)
  * Voice quality    : jitter (local), shimmer (local), harmonics-to-noise ratio
  * Spectral         : MFCC (mean/sd), spectral centroid / bandwidth / rolloff,
                       zero-crossing rate

Clinical rationale (why these matter for cognitive screening)
  * People in early Alzheimer's pause more and longer (word-finding difficulty),
    speak more slowly, and show reduced pitch variation.
  * Depression flattens pitch (reduced CV) and slows articulation rate.
The model learns which combinations separate groups; we do not hard-code labels.
"""
from __future__ import annotations
import numpy as np
import librosa
import parselmouth
from parselmouth.praat import call


# ---------------------------------------------------------------- timing ----
def _timing_features(y, sr, top_db=30, word_count=None):
    """Pause / rate features from energy-based voice-activity segmentation."""
    total_dur = len(y) / sr
    # non-silent intervals (samples)
    intervals = librosa.effects.split(y, top_db=top_db)
    if len(intervals) == 0:
        return {}

    speech_dur = float(np.sum(intervals[:, 1] - intervals[:, 0]) / sr)
    silence_dur = float(total_dur - speech_dur)

    # pauses = silent gaps BETWEEN speech segments (ignore leading/trailing)
    pauses = []
    for i in range(1, len(intervals)):
        gap = (intervals[i, 0] - intervals[i - 1, 1]) / sr
        if gap > 0.05:                      # count gaps longer than 50 ms
            pauses.append(gap)
    pauses = np.array(pauses) if pauses else np.array([0.0])

    feats = {
        "dur_total_s": total_dur,
        "dur_speech_s": speech_dur,
        "dur_silence_s": silence_dur,
        "phonation_ratio": speech_dur / total_dur if total_dur else 0.0,
        "pause_count": int(np.sum(pauses > 0.05)),
        "pause_total_s": float(np.sum(pauses)),
        "pause_mean_s": float(np.mean(pauses)),
        "pause_sd_s": float(np.std(pauses)),
        "pause_rate_per_min": float(np.sum(pauses > 0.05) / (total_dur / 60.0)),
        "n_speech_segments": int(len(intervals)),
    }

    # rates require a unit count. If a transcript word count is supplied we use
    # it (accurate); otherwise we estimate "syllable-like" nuclei from the
    # energy envelope as a proxy so the field is never empty.
    if word_count:
        feats["speech_rate_wpm"] = word_count / (total_dur / 60.0)
        feats["articulation_rate_wps"] = word_count / speech_dur if speech_dur else 0.0
    else:
        env = librosa.onset.onset_strength(y=y, sr=sr)
        peaks = librosa.util.peak_pick(env, pre_max=3, post_max=3, pre_avg=3,
                                       post_avg=5, delta=0.3, wait=5)
        n_syl = max(len(peaks), 1)
        feats["est_syllable_count"] = int(n_syl)
        feats["est_speech_rate_sylpm"] = n_syl / (total_dur / 60.0)
        feats["est_articulation_rate_syls"] = n_syl / speech_dur if speech_dur else 0.0
    return feats


# ------------------------------------------------------ pitch / voice ----
def _voice_features(path, f0min=75, f0max=400):
    """Pitch, jitter, shimmer and HNR via Praat (parselmouth)."""
    snd = parselmouth.Sound(path)
    out = {}

    pitch = snd.to_pitch(pitch_floor=f0min, pitch_ceiling=f0max)
    f0 = pitch.selected_array["frequency"]
    voiced = f0[f0 > 0]
    if voiced.size:
        out.update({
            "f0_mean_hz": float(np.mean(voiced)),
            "f0_sd_hz": float(np.std(voiced)),
            "f0_min_hz": float(np.min(voiced)),
            "f0_max_hz": float(np.max(voiced)),
            "f0_range_hz": float(np.ptp(voiced)),
            "f0_cv": float(np.std(voiced) / np.mean(voiced)),   # monotonicity
            "voiced_fraction": float(voiced.size / f0.size),
        })

    # jitter / shimmer need a point process over glottal cycles
    try:
        pp = call(snd, "To PointProcess (periodic, cc)", f0min, f0max)
        out["jitter_local"] = float(
            call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3))
        out["shimmer_local"] = float(
            call([snd, pp], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6))
    except Exception:
        out["jitter_local"] = float("nan")
        out["shimmer_local"] = float("nan")

    try:
        harm = snd.to_harmonicity()
        vals = harm.values[harm.values != -200]
        out["hnr_db"] = float(np.mean(vals)) if vals.size else float("nan")
    except Exception:
        out["hnr_db"] = float("nan")
    return out


# ----------------------------------------------------------- spectral ----
def _spectral_features(y, sr, n_mfcc=13):
    out = {}
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    for i in range(n_mfcc):
        out[f"mfcc{i+1}_mean"] = float(np.mean(mfcc[i]))
        out[f"mfcc{i+1}_sd"] = float(np.std(mfcc[i]))
    out["spectral_centroid_mean"] = float(
        np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    out["spectral_bandwidth_mean"] = float(
        np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    out["spectral_rolloff_mean"] = float(
        np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    out["zcr_mean"] = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    return out


# ------------------------------------------------------------- public ----
def extract_acoustic_features(path, word_count=None, top_db=30):
    """
    Extract the full acoustic feature dictionary from a .wav file.

    Parameters
    ----------
    path : str            path to a mono audio file (any sample rate)
    word_count : int|None if the transcript word count is known, exact speech
                          and articulation rates are computed; otherwise a
                          syllable-nuclei estimate is used.
    Returns
    -------
    dict {feature_name: value}
    """
    y, sr = librosa.load(path, sr=16000, mono=True)
    feats = {}
    feats.update(_timing_features(y, sr, top_db=top_db, word_count=word_count))
    feats.update(_voice_features(path))
    feats.update(_spectral_features(y, sr))
    return feats


if __name__ == "__main__":
    import sys, json
    f = extract_acoustic_features(sys.argv[1])
    print(json.dumps(f, indent=2))
