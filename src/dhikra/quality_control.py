"""
quality_control.py
------------------
Decides whether a recording is good enough to analyse, and refuses when it is
not.

WHY A MEDICAL TOOL SHOULD REFUSE
A system that always returns a number is more dangerous than one that
sometimes declines. If a recording contains ten seconds of mumbling in a noisy
corridor, the pipeline will still produce 117 numbers and the model will still
produce a probability. That probability will be meaningless, and nothing in the
output would reveal it.

WHAT THE THRESHOLDS ARE BASED ON
Two of the gates are empirical and the rest are asserted, and the distinction
matters (recorded 2026-08-22). The SNR thresholds and the clipping tolerance
come from a degradation experiment on real recordings, which measured how
each acoustic feature survives realistic field conditions:

    mp3 compression (64k, 32k)   correlation ~1.00 with clean audio
    telephone-quality 8 kHz      ~1.00
    low recording volume         ~1.00
    clipping from excess gain    ~1.00
    phone at table distance      0.90 - 1.00
    background noise, 20 dB SNR  0.59 - 0.96  (pause measures degrade)
    background noise, 10 dB SNR  extraction FAILS

The conclusion is specific and useful: this pipeline is robust to compression,
sampling rate, volume and clipping, and is broken by background noise. The
gates below therefore police noise strictly and everything else loosely, which
is the opposite of what a generic audio-quality check would do.

A tool intended for a Libyan clinic must tolerate a cheap phone. It must not
tolerate an open window onto a busy street.

MIN_DURATION_S, MIN_SPEECH_S and MIN_WORDS, by contrast, were ASSERTED as
engineering minima; no experiment derives them. The Libyan pilot's
feasibility outcomes are the natural place to revisit them.
"""
from __future__ import annotations

import numpy as np


# Thresholds. MIN_SNR_DB / WARN_SNR_DB / MAX_CLIP_FRACTION are tied to the
# experiment above; MIN_DURATION_S / MIN_SPEECH_S / MIN_WORDS are asserted
# minima (see docstring).
MIN_DURATION_S = 8.0        # asserted: below this there is too little speech
MIN_SPEECH_S = 4.0          # asserted: actual voiced time, not just length
# CALIBRATED EMPIRICALLY, not assumed. The estimator below is a percentile
# ratio rather than a true SNR, so its scale had to be established against
# recordings of known quality. On real corpus audio it returned a median of
# 11.1 dB for clean originals and 3.1 dB for the same files degraded to 10 dB
# SNR -- the level at which pause detection was measured to fail outright.
# The reject threshold sits between those distributions; the warning threshold
# sits at the lower edge of the clean range.
MIN_SNR_DB = 7.0
WARN_SNR_DB = 10.0
MAX_CLIP_FRACTION = 0.05    # clipping proved harmless up to heavy levels
MIN_WORDS = 8               # asserted: transcript measures need some text


def estimate_snr(audio: np.ndarray, sr: int) -> float:
    """
    Crude signal-to-noise estimate: the ratio of energy in loud frames to
    energy in quiet frames. Quiet frames in a speech recording are dominated
    by background noise, so their level approximates the noise floor.
    """
    frame = int(0.025 * sr)
    if len(audio) < frame * 4:
        return 0.0
    n = len(audio) // frame
    energies = np.array([np.mean(audio[i * frame:(i + 1) * frame] ** 2)
                         for i in range(n)])
    energies = energies[energies > 0]
    if len(energies) < 4:
        return 0.0
    noise = np.percentile(energies, 10)
    signal = np.percentile(energies, 90)
    if noise <= 0:
        return 40.0
    return float(10 * np.log10(signal / noise))


def check_recording(wav_path: str, acoustic: dict | None = None,
                    transcript: str | None = None) -> dict:
    """
    Assess one recording and return a verdict.

    Returns {'usable': bool, 'severity': 'ok'|'warn'|'reject',
             'issues': [...], 'metrics': {...}}
    """
    import soundfile as sf

    issues, metrics, severity = [], {}, "ok"
    try:
        audio, sr = sf.read(wav_path, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
    except Exception as e:
        return {"usable": False, "severity": "reject",
                "issues": [f"The audio file could not be read ({type(e).__name__}). "
                           "Please record again."], "metrics": {}}

    dur = len(audio) / sr
    metrics["duration_s"] = round(dur, 1)
    if dur < MIN_DURATION_S:
        issues.append(f"The recording is only {dur:.1f} seconds. At least "
                      f"{MIN_DURATION_S:.0f} seconds of speech is needed for the "
                      "measurements to mean anything.")
        severity = "reject"

    snr = estimate_snr(audio, sr)
    metrics["snr_db"] = round(snr, 1)
    if snr < MIN_SNR_DB:
        issues.append(f"Background noise is too high (signal-to-noise about "
                      f"{snr:.0f} dB). In the degradation experiment pause "
                      "detection failed outright at 10 dB SNR, and pause "
                      "measures are among the "
                      "strongest markers. Please move to a quieter room and "
                      "record again.")
        severity = "reject"
    elif snr < WARN_SNR_DB:
        issues.append(f"Background noise is noticeable ({snr:.0f} dB). The "
                      "result is usable but timing measures may be less "
                      "reliable. A quieter room would be better.")
        severity = max(severity, "warn", key=["ok", "warn", "reject"].index)

    clip = float(np.mean(np.abs(audio) > 0.99))
    metrics["clipped_fraction"] = round(clip, 4)
    if clip > MAX_CLIP_FRACTION:
        issues.append(f"{clip*100:.0f}% of the recording is clipped. Testing "
                      "showed clipping is largely harmless, but at this level "
                      "the microphone gain should be reduced.")
        severity = max(severity, "warn", key=["ok", "warn", "reject"].index)

    if acoustic:
        sp = acoustic.get("dur_speech_s")
        if sp is not None:
            metrics["speech_s"] = round(float(sp), 1)
            if sp < MIN_SPEECH_S:
                issues.append(f"Only {sp:.1f} seconds of actual speech was "
                              "detected. The participant may not have "
                              "understood the task, or may have declined it.")
                severity = "reject"
        pr = acoustic.get("phonation_ratio")
        if pr is not None and pr > 0.98:
            issues.append("Almost no silence was detected, which usually means "
                          "continuous background sound rather than continuous "
                          "speech. Check the recording.")
            severity = max(severity, "warn", key=["ok", "warn", "reject"].index)

    if transcript is not None:
        w = len(transcript.split())
        metrics["words"] = w
        if w < MIN_WORDS:
            issues.append(f"The transcript contains only {w} words. Word-based "
                          "measures need more text; acoustic measures are "
                          "unaffected.")
            severity = max(severity, "warn", key=["ok", "warn", "reject"].index)

    return {"usable": severity != "reject", "severity": severity,
            "issues": issues, "metrics": metrics}


def session_verdict(task_checks: dict) -> dict:
    """
    Decide whether a whole session can be scored.

    The screening result comes from the picture task alone, so that task
    failing means no result can be produced. Failures elsewhere reduce the
    supporting detail but do not invalidate the screen.
    """
    primary = task_checks.get("picture", {})
    if primary and not primary.get("usable", True):
        return {"scoreable": False,
                "reason": ("The picture-description recording did not meet "
                           "quality requirements, and it is the only task the "
                           "screening result is computed from. No result can "
                           "be reported for this session."),
                "detail": primary.get("issues", [])}
    warns = [t for t, c in task_checks.items() if c.get("severity") == "warn"]
    rejects = [t for t, c in task_checks.items()
               if c.get("severity") == "reject" and t != "picture"]
    return {"scoreable": True,
            "degraded_tasks": rejects,
            "warned_tasks": warns,
            "reason": (f"{len(rejects)} secondary task(s) unusable; the "
                       "screening result is unaffected but supporting detail "
                       "is reduced.") if rejects else None}
