"""
audio_robustness.py
-------------------
Stress-tests the acoustic pipeline under the recording conditions a
low-resource clinic would actually produce.

WHY THIS BELONGS IN A BIOMEDICAL ENGINEERING THESIS
The central claim of this project is accessibility: that screening can be
performed with a phone rather than a clinic. That claim is only credible if
the measurements survive the conditions a phone in a Libyan clinic produces --
compression, background noise, distance from the speaker, low recording level,
and clipping.

Reporting accuracy from clean, professionally recorded research audio and then
asserting field deployability is exactly the gap between a laboratory result
and a device. This module measures that gap instead of assuming it away.

DEGRADATIONS APPLIED, and why each was chosen
  mp3_64k / mp3_32k   phones and messaging apps compress aggressively; a
                      recording sent over WhatsApp is not the file that was
                      captured
  noise_20dB / 10dB   a clinic corridor, an air conditioner, a family member
                      in the room
  distance            the phone on a table rather than held; simulated by
                      attenuation plus mild reverberation
  quiet               the participant speaks softly, or gain was set low
  clipped             gain set too high, peaks flattened
  downsample_8k       telephone-quality capture

WHAT IS MEASURED
For each degradation, the change in every acoustic feature, and whether the
features that matter clinically (pausing, phonation ratio, pitch) survive.
Features that collapse under mild degradation are unsuitable for field use
regardless of how well they perform on clean research audio.
"""
import os
import sys
import glob
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd
import soundfile as sf

from dhikra.acoustic_features import extract_acoustic_features
from dhikra import asr

OUT = "results/robustness"


def _ffmpeg(args):
    exe = asr._find_ffmpeg()
    if exe is None:
        raise RuntimeError("ffmpeg not available")
    r = subprocess.run([exe, "-y", "-loglevel", "error"] + args,
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[:200])


def degrade(src: str, kind: str, dst: str) -> str:
    """Apply one realistic degradation and return the path to the result."""
    if kind == "clean":
        _ffmpeg(["-i", src, "-ac", "1", "-ar", "16000", dst])
        return dst

    if kind.startswith("mp3_"):
        rate = kind.split("_")[1]
        tmp = dst.replace(".wav", ".mp3")
        _ffmpeg(["-i", src, "-ac", "1", "-b:a", rate, tmp])
        _ffmpeg(["-i", tmp, "-ac", "1", "-ar", "16000", dst])
        return dst

    if kind == "downsample_8k":
        tmp = dst.replace(".wav", "_8k.wav")
        _ffmpeg(["-i", src, "-ac", "1", "-ar", "8000", tmp])
        _ffmpeg(["-i", tmp, "-ac", "1", "-ar", "16000", dst])
        return dst

    # the remaining degradations are applied numerically
    audio, sr = sf.read(src, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    rng = np.random.default_rng(42)

    if kind.startswith("noise_"):
        snr_db = float(kind.split("_")[1].replace("dB", ""))
        sig_pow = np.mean(audio ** 2)
        noise_pow = sig_pow / (10 ** (snr_db / 10))
        audio = audio + rng.normal(0, np.sqrt(noise_pow), len(audio))
    elif kind == "distance":
        # attenuation plus a short early reflection, approximating a phone
        # placed on a table rather than held
        audio = audio * 0.35
        delay = int(0.025 * sr)
        echo = np.zeros_like(audio)
        echo[delay:] = audio[:-delay] * 0.30
        audio = audio + echo
    elif kind == "quiet":
        audio = audio * 0.15
    elif kind == "clipped":
        audio = np.clip(audio * 3.5, -1.0, 1.0)

    audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.95
    sf.write(dst, audio.astype("float32"), sr)
    if sr != 16000:
        tmp = dst.replace(".wav", "_r.wav")
        os.replace(dst, tmp)
        _ffmpeg(["-i", tmp, "-ac", "1", "-ar", "16000", dst])
    return dst


CONDITIONS = ["clean", "mp3_64k", "mp3_32k", "noise_20dB", "noise_10dB",
              "distance", "quiet", "clipped", "downsample_8k"]

# The measures that carry clinical meaning. Robustness of these matters far
# more than robustness of the MFCCs, which are conventional rather than
# interpretable.
KEY = ["ac.phonation_ratio", "ac.pause_count", "ac.pause_rate_per_min",
       "ac.pause_mean_s", "ac.f0_mean_hz", "ac.f0_cv", "ac.jitter_local",
       "ac.shimmer_local", "ac.hnr_db"]


def main(audio_dir: str, n_files: int = 25):
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(audio_dir, "**", "*.wav"),
                             recursive=True))[:n_files]
    if not files:
        files = sorted(glob.glob(os.path.join(audio_dir, "**", "*.mp3"),
                                 recursive=True))[:n_files]
    if not files:
        print(f"no audio found under {audio_dir}")
        return
    print(f"stress-testing {len(files)} recordings across "
          f"{len(CONDITIONS)} conditions")

    rows = []
    work = "/tmp/robust"
    os.makedirs(work, exist_ok=True)
    for i, src in enumerate(files, 1):
        fid = os.path.splitext(os.path.basename(src))[0]
        for cond in CONDITIONS:
            dst = os.path.join(work, f"{fid}_{cond}.wav")
            try:
                degrade(src, cond, dst)
                f = extract_acoustic_features(dst)
                rows.append({"file_id": fid, "condition": cond,
                             **{f"ac.{k}": v for k, v in f.items()}})
            except Exception as e:
                rows.append({"file_id": fid, "condition": cond,
                             "_error": f"{type(e).__name__}"})
            finally:
                for p in glob.glob(os.path.join(work, f"{fid}_{cond}*")):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
        if i % 5 == 0:
            print(f"  {i}/{len(files)}")

    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/raw_measurements.csv", index=False)

    base = df[df.condition == "clean"].set_index("file_id")
    print("\n" + "=" * 76)
    print("FEATURE STABILITY UNDER DEGRADATION")
    print("(correlation with the clean recording; 1.0 = unaffected)")
    print("=" * 76)
    summary = []
    print(f"  {'condition':14s} " + " ".join(f"{k.replace('ac.','')[:9]:>10s}"
                                             for k in KEY[:5]))
    for cond in CONDITIONS[1:]:
        sub = df[df.condition == cond].set_index("file_id")
        common = base.index.intersection(sub.index)
        cells, rec = [], {"condition": cond}
        for k in KEY:
            if k not in base or k not in sub:
                cells.append(np.nan)
                continue
            a, b = base.loc[common, k], sub.loc[common, k]
            m = a.notna() & b.notna()
            r = a[m].corr(b[m]) if m.sum() > 3 else np.nan
            rec[k] = float(r) if r == r else None
            cells.append(r)
        summary.append(rec)
        print(f"  {cond:14s} " + " ".join(
            f"{c:10.2f}" if c == c else f"{'--':>10s}" for c in cells[:5]))

    s = pd.DataFrame(summary)
    s.to_csv(f"{OUT}/stability.csv", index=False)
    fails = int(df["_error"].notna().sum()) if "_error" in df else 0
    print(f"\n  extraction failures: {fails} of {len(df)}")
    print(f"  written to {OUT}/")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default="/tmp/arabic_moca")
    ap.add_argument("--n", type=int, default=25)
    a = ap.parse_args()
    main(a.audio, a.n)
