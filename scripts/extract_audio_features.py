"""
extract_audio_features.py
-------------------------
Run this on YOUR computer, on the DementiaBank audio you downloaded.

WHY THIS EXISTS
The Pitt media collection is roughly 17 GB, which is impractical to move
around. But the audio's only purpose here is to produce 53 numbers per
recording. Those numbers total a few hundred kilobytes. So the audio stays on
your machine and only the resulting table travels.

WHAT IT DOES
Walks a folder of recordings, extracts the full acoustic feature set from each
one (pauses, speech rate, pitch, voice quality, spectral shape), and writes a
single CSV. Nothing is uploaded, nothing leaves your computer except the file
you choose to share.

HOW TO USE
  1. Download the cookie-task audio from
       https://media.talkbank.org/dementia/English/Pitt/
     keeping the folder names, so you end up with something like:

       audio/
         Control/cookie/002-0.mp3 ...
         Dementia/cookie/001-0.mp3 ...

  2. From inside the dhikra folder, run:

       python scripts/extract_audio_features.py --audio "C:/path/to/audio"

  3. Send back the file it creates:  results/acoustic_features.csv

It is safe to stop and re-run: completed files are skipped, so an interrupted
run picks up where it left off.
"""
import os
import re
import sys
import glob
import argparse
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd

from dhikra.acoustic_features import extract_acoustic_features
from dhikra import asr

AUDIO_EXT = ("*.mp3", "*.wav", "*.MP3", "*.WAV", "*.m4a", "*.ogg")

# Chrome and bulk downloaders append markers when a name already exists:
#   002-0(1).mp3   002-0 (1).mp3   002-0 - Copy.mp3
# The duplicate is frequently a truncated or error-page file rather than real
# audio, so the id must be normalised and the candidates tried in order of
# plausibility rather than trusting whichever name came first.
_DUP_SUFFIX = re.compile(r"\s*(\(\d+\)|-\s*Copy(\s*\(\d+\))?|_\d+)$", re.I)


def normalize_id(path: str) -> str:
    """Strip duplicate markers so '002-0(1).mp3' and '002-0.mp3' share an id."""
    stem = os.path.splitext(os.path.basename(path))[0]
    prev = None
    while prev != stem:
        prev = stem
        stem = _DUP_SUFFIX.sub("", stem).strip()
    return stem


def find_audio(root: str) -> list[str]:
    files = []
    for pat in AUDIO_EXT:
        files += glob.glob(os.path.join(root, "**", pat), recursive=True)
    return sorted(set(files))


def group_from_path(path: str) -> str:
    """Infer Control / Dementia from the folder name, as TalkBank ships it."""
    p = path.replace("\\", "/").lower()
    if "/control/" in p:
        return "Control"
    if "/dementia/" in p:
        return "Dementia"
    return ""


def load_group_lookup() -> dict:
    """
    Fallback group lookup, keyed by file id.

    Bulk downloaders drop every file into one folder, which destroys the
    Control/ and Dementia/ folder names the group label would otherwise come
    from. The transcripts already record each participant's group, and file ids
    are unique across the two groups (verified: no collisions), so the label can
    always be recovered from meta.csv even when the folder structure is lost.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    meta_path = os.path.join(here, "..", "results", "pitt_cookie", "meta.csv")
    if not os.path.exists(meta_path):
        return {}
    try:
        m = pd.read_csv(meta_path)
        return dict(zip(m.file_id.astype(str), m.group.astype(str)))
    except Exception:
        return {}


def task_from_path(path: str) -> str:
    p = path.replace("\\", "/").lower()
    for t in ("cookie", "fluency", "recall", "sentence"):
        if f"/{t}/" in p:
            return t
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True, help="folder containing the recordings")
    ap.add_argument("--out", default="results/acoustic_features.csv")
    ap.add_argument("--task", default="cookie",
                    help="only process this task folder ('all' for everything)")
    args = ap.parse_args()

    files = find_audio(args.audio)
    if args.task != "all":
        files = [f for f in files if task_from_path(f) in (args.task, "")]
    files = [f for f in files if os.path.getsize(f) > 0]
    if not files:
        print(f"No audio found under {args.audio}\n")
        if not os.path.exists(args.audio):
            print("  That folder does not exist on this computer.")
        else:
            entries = os.listdir(args.audio)
            print(f"  The folder exists and contains {len(entries)} items.")
            exts: dict[str, int] = {}
            for e in entries:
                ext = os.path.splitext(e)[1].lower() or "(no extension)"
                exts[ext] = exts.get(ext, 0) + 1
            print(f"  File types present: {exts}")
            print("  First few items:")
            for e in sorted(entries)[:10]:
                print(f"      {e}")
        # Point at the most likely real location. Browser downloads land in
        # the user's Downloads folder, which is where the files almost always
        # are when this message appears.
        dl = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.isdir(dl):
            found = []
            for pat in AUDIO_EXT:
                found += glob.glob(os.path.join(dl, "**", pat), recursive=True)
            if found:
                print(f"\n  FOUND {len(found)} audio files in your Downloads "
                      f"folder instead:")
                print(f'      {dl}')
                print("\n  Re-run with that path:")
                print(f'      python scripts/extract_audio_features.py --audio "{dl}"')
        return

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    # resume support
    done = set()
    if os.path.exists(args.out):
        try:
            prev = pd.read_csv(args.out)
            done = set(prev["file_id"])
            print(f"resuming: {len(done)} files already processed")
        except Exception:
            prev = None
    rows = []

    # ---- collapse duplicates ----------------------------------------------
    # Group every file under its normalised id. Candidates are ordered largest
    # first because a truncated download or a saved error page is far smaller
    # than a real recording; if the largest still fails to decode, the next is
    # tried, so a broken copy never costs us the participant.
    by_id: dict[str, list[str]] = {}
    for f in files:
        by_id.setdefault(normalize_id(f), []).append(f)
    for k in by_id:
        by_id[k].sort(key=lambda p: os.path.getsize(p), reverse=True)

    n_dupes = sum(len(v) - 1 for v in by_id.values())

    lookup = load_group_lookup()
    print(f"found {len(files)} files -> {len(by_id)} unique recordings")
    if n_dupes:
        print(f"  {n_dupes} duplicate copies detected; the working copy of each "
              "will be used")
    if lookup:
        print(f"group lookup loaded for {len(lookup)} file ids "
              "(used when folder names are missing)")
    if not asr.ffmpeg_available():
        print("\n! ffmpeg not found. Install it with:  pip install imageio-ffmpeg")
        print("  (mp3 files cannot be read without it)")
        return

    failed, recovered = 0, 0
    ids = sorted(by_id)
    for i, fid in enumerate(ids, 1):
        if fid in done:
            continue
        feats, used = None, None
        for attempt, path in enumerate(by_id[fid]):
            try:
                feats = extract_acoustic_features(path)
                used = path
                if attempt > 0:
                    recovered += 1
                break
            except Exception:
                continue
        if feats is None:
            failed += 1
            print(f"  ! {fid}: no readable copy "
                  f"({len(by_id[fid])} file(s) tried)")
        else:
            grp = group_from_path(used) or lookup.get(fid, "")
            row = {"file_id": fid, "group": grp,
                   "task": task_from_path(used) or "cookie"}
            row.update({f"ac.{k}": v for k, v in feats.items()})
            rows.append(row)

        if i % 25 == 0 or i == len(ids):
            print(f"  {i}/{len(ids)} processed ({failed} unreadable"
                  f"{f', {recovered} recovered from a duplicate' if recovered else ''})")
            # write incrementally so an interrupted run is not wasted
            if rows:
                df = pd.DataFrame(rows)
                if os.path.exists(args.out):
                    df.to_csv(args.out, mode="a", header=False, index=False)
                else:
                    df.to_csv(args.out, index=False)
                rows = []

    if rows:
        df = pd.DataFrame(rows)
        if os.path.exists(args.out):
            df.to_csv(args.out, mode="a", header=False, index=False)
        else:
            df.to_csv(args.out, index=False)

    if os.path.exists(args.out):
        final = pd.read_csv(args.out)
        size_kb = os.path.getsize(args.out) / 1024
        print(f"\ndone: {len(final)} recordings x {final.shape[1]} columns")
        print(f"written to {args.out}  ({size_kb:.0f} KB)")
        print("\nThis file is small enough to send back. The audio stays here.")


if __name__ == "__main__":
    main()
