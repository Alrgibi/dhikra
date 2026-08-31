"""
paths.py
--------
Single source of truth for data locations.

WHY THIS EXISTS
The original development sandbox hardcoded /home/claude/... paths into four
scripts. When that environment was lost (18 Aug 2026 handoff), every one of
those paths died with it and no script could find any data. This module
replaces the constants: every script asks resolve("<key>") and the answer
comes from corpus_paths.json at the repository root.

The JSON stores the user-facing Windows paths. When the code runs inside a
Linux environment that mounts those folders (e.g. the Cowork workspace VM,
where C:\\Users\\PC\\Desktop\\<X> appears at /sessions/<id>/mnt/<X>), the
resolver translates automatically. Overrides, in order of precedence:
  1. env DHIKRA_<KEY> (e.g. DHIKRA_PITT_ROOT=/data/Pitt) wins outright;
  2. env DHIKRA_MOUNT_ROOT names the directory containing the mounted
     Desktop folders, when auto-detection fails.

Added 2026-08-20 as part of the post-handoff reconstruction; see
docs/RECONSTRUCTION.md.
"""
from __future__ import annotations
import glob
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CONFIG = os.path.join(_ROOT, "corpus_paths.json")


def _load() -> dict:
    if not os.path.exists(_CONFIG):
        raise FileNotFoundError(
            f"corpus_paths.json not found at {_CONFIG}. It should sit at the "
            "repository root, next to HANDOFF.md.")
    with open(_CONFIG, encoding="utf-8") as fh:
        return json.load(fh)


def _candidates(raw: str) -> list[str]:
    cands = [raw]
    norm = raw.replace("\\", "/")
    if norm != raw:
        cands.append(norm)
    # Translate .../Desktop/<folder>/<rest> to a Linux mount of that folder.
    parts = norm.split("/")
    if "Desktop" in parts:
        rel = parts[parts.index("Desktop") + 1:]
        if rel:
            roots = []
            if os.environ.get("DHIKRA_MOUNT_ROOT"):
                roots.append(os.environ["DHIKRA_MOUNT_ROOT"])
            roots += sorted(glob.glob("/sessions/*/mnt"))
            for r in roots:
                cands.append(os.path.join(r, *rel))
    return cands


def resolve(key: str, must_exist: bool = True) -> str:
    """Return the configured path for `key`, translated for this machine."""
    env = os.environ.get(f"DHIKRA_{key.upper()}")
    if env:
        return env
    cfg = _load()
    if key not in cfg or cfg[key] in (None, ""):
        raise KeyError(
            f"corpus_paths.json has no usable entry for '{key}' "
            f"(value: {cfg.get(key)!r}). Fill it in. Known keys: "
            f"{sorted(k for k in cfg if not k.startswith('_'))}")
    raw = cfg[key]
    tried = []
    for c in _candidates(raw):
        tried.append(c)
        if os.path.exists(c):
            return c
    if must_exist:
        raise FileNotFoundError(
            f"'{key}' resolved to no existing path. Tried:\n  "
            + "\n  ".join(tried)
            + "\nSet env DHIKRA_" + key.upper() + " or fix corpus_paths.json.")
    # Creation target (must_exist=False) that does not exist yet: prefer a
    # translated candidate whose PARENT directory exists, so new folders are
    # created inside the real mounted tree rather than as a literal
    # "C:/..." directory relative to the CWD. (Fixed 2026-08-20 after the
    # first build created exactly that; see docs/RECONSTRUCTION.md.)
    for c in _candidates(raw):
        if os.path.isdir(os.path.dirname(c)):
            return c
    return raw
