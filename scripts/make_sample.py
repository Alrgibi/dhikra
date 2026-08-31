"""
make_sample.py
--------------
Generates a synthetic, speech-LIKE audio file so the acoustic pipeline can be
tested end-to-end WITHOUT any real recording. This is a source-filter model:
a (slightly jittered) glottal pulse train excites a set of formant resonances,
amplitude-enveloped into "syllables", with silent pauses between "phrases".

This is ONLY a test fixture. Real DementiaBank / Arabic recordings replace it
later with zero code changes -- the extractor reads any .wav the same way.
"""
import numpy as np
from scipy.signal import lfilter
import soundfile as sf
import argparse


def _formant_filter(x, formants, bandwidths, sr):
    """Cascade of 2nd-order resonators approximating a vowel tract."""
    y = x.copy()
    for f, bw in zip(formants, bandwidths):
        r = np.exp(-np.pi * bw / sr)
        theta = 2 * np.pi * f / sr
        a = [1.0, -2 * r * np.cos(theta), r * r]
        b = [1.0 - r]  # simple gain
        y = lfilter(b, a, y)
    return y


def _glottal_train(dur, sr, f0=120.0, jitter=0.02):
    """Impulse train with small cycle-to-cycle period perturbation (jitter)."""
    n = int(dur * sr)
    out = np.zeros(n)
    t = 0.0
    while t < dur:
        idx = int(t * sr)
        if idx < n:
            out[idx] = 1.0
        period = (1.0 / f0) * (1.0 + np.random.uniform(-jitter, jitter))
        t += period
    return out


# A few vowel-like formant sets (F1, F2, F3) in Hz
VOWELS = {
    "a": ([730, 1090, 2440], [80, 90, 120]),
    "i": ([270, 2290, 3010], [60, 90, 120]),
    "u": ([300, 870, 2240], [60, 90, 120]),
    "e": ([530, 1840, 2480], [70, 90, 120]),
    "o": ([570, 840, 2410], [70, 90, 120]),
}


def make_sample(path="sample.wav", sr=16000, seed=0,
                phrases=(4, 5, 3, 6, 4), f0=120.0, jitter=0.015):
    """
    phrases: tuple giving the number of "syllables" in each phrase. Pauses are
    inserted between phrases (longer) and lightly between syllables (shorter).
    """
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    vowels = list(VOWELS.keys())
    chunks = []

    for p_i, n_syll in enumerate(phrases):
        for s in range(n_syll):
            syl_dur = rng.uniform(0.16, 0.28)          # syllable length
            v = vowels[rng.integers(0, len(vowels))]
            formants, bws = VOWELS[v]
            src = _glottal_train(syl_dur, sr, f0=f0 * rng.uniform(0.95, 1.05),
                                 jitter=jitter)
            voiced = _formant_filter(src, formants, bws, sr)
            # amplitude envelope (attack-decay) + small shimmer
            env = np.hanning(len(voiced)) * rng.uniform(0.9, 1.0)
            voiced = voiced * env
            voiced /= (np.max(np.abs(voiced)) + 1e-9)
            chunks.append(voiced * 0.8)
            # short intra-phrase pause
            if s < n_syll - 1:
                chunks.append(np.zeros(int(rng.uniform(0.03, 0.09) * sr)))
        # longer inter-phrase pause (a "breath")
        if p_i < len(phrases) - 1:
            chunks.append(np.zeros(int(rng.uniform(0.35, 0.7) * sr)))

    audio = np.concatenate(chunks)
    audio += rng.normal(0, 0.003, len(audio))          # faint background noise
    audio /= (np.max(np.abs(audio)) + 1e-9)
    sf.write(path, audio.astype(np.float32), sr)
    return path, len(audio) / sr


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sample.wav")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    p, dur = make_sample(args.out, seed=args.seed)
    print(f"wrote {p}  ({dur:.2f} s)")
