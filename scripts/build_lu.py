"""
build_lu.py
-----------
Builds the feature matrix for the LOCKED external test corpus (Lu).

########################################################################
#  LU IS THE LOCKED EXTERNAL TEST SET.                                 #
#  It must never enter training, threshold selection, calibration,     #
#  feature selection, or any other development decision.               #
#  This script only PARSES Lu into features + metadata. Scoring it     #
#  against a model is a separate, one-shot, pre-registered act.        #
########################################################################

WHY THIS SCRIPT EXISTS
The Lu build that produced the locked evaluation of 18 Aug 2026 was inline
and its code was lost with the sandbox (HANDOFF §6.3, FILE_MAP: "Lu is built
inline"). Its label logic was reconstructed from an @ID-header audit of all
54 files (docs/RECONSTRUCTION.md) and committed to
src/dhikra/chat_parser.py on 2026-08-20. This script re-runs that build
reproducibly and REFUSES to complete unless it reproduces the locked
composition exactly.

COUNT ASSERTIONS (the locked composition)
  54 .cha files on disk (26 Control folder + 28 Dementia folder)
  1 excluded  : Dementia/F16.cha, header group 'Aphasia' (language disorder,
                not dementia -- the model-card exclusion)
  27 control  : 25 'Control' + 1 'Conrol' (typo, Control/F32.cha)
                + 1 'Control' header inside the Dementia folder (F07.cha --
                header takes precedence over folder)
  26 impaired : 16 Alzheimer's + 6 Dementia + 2 MCI + 1 Vascular + 1 Pick's
  0 dropped for word count (all 53 labelled recordings are usable)
"""
import datetime
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dhikra.paths import resolve

OUT = "results/lu"


def main():
    print("=" * 74)
    print("BUILDING LU (LOCKED EXTERNAL TEST SET) -- parse only, no scoring")
    print("=" * 74)

    lu_root = resolve("lu_root")
    files = sorted(glob.glob(os.path.join(lu_root, "**", "*.cha"), recursive=True))
    assert len(files) == 54, (
        f"Lu corpus drift: expected 54 .cha files, found {len(files)} under {lu_root}")

    from dhikra.corpus import build_dataset, save_dataset
    X, y, meta = build_dataset(lu_root, use_audio=False, verbose=False)

    n_ctrl = int((y == 0).sum())
    n_imp = int((y == 1).sum())
    n_excl = 54 - len(X)
    print(f"  labelled control : {n_ctrl}")
    print(f"  labelled impaired: {n_imp}")
    print(f"  excluded         : {n_excl}")

    assert (n_ctrl, n_imp, n_excl) == (27, 26, 1), (
        f"Lu label drift: expected 27 control / 26 impaired / 1 excluded "
        f"(the locked composition), got {n_ctrl}/{n_imp}/{n_excl}. "
        f"Check src/dhikra/chat_parser.py group mapping against "
        f"docs/RECONSTRUCTION.md before doing ANYTHING else.")

    # the two special files, verified by name
    f07 = meta.loc[meta.file_id == "F07"]
    assert len(f07) == 1 and int(y[f07.index[0]]) == 0, (
        "F07 must be present and labelled CONTROL (header takes precedence "
        "over its Dementia folder)")
    assert "F16" not in set(meta.file_id), (
        "F16 (Aphasia) must be the excluded file")

    # no word-count drops: all 53 labelled recordings must be usable
    assert "ling.word_count" in X and int((X["ling.word_count"] < 10).sum()) == 0, (
        "unexpected short Lu recording -- the locked evaluation used all 53")

    os.makedirs(OUT, exist_ok=True)
    save_dataset(X, y, meta, OUT)
    with open(os.path.join(OUT, "PROVENANCE.json"), "w") as fh:
        json.dump({
            "dataset": "Lu (DementiaBank) -- LOCKED EXTERNAL TEST SET",
            "n_cha_files": 54,
            "composition": {"control": 27, "impaired": 26, "excluded_aphasia": 1},
            "label_logic": "reconstructed mapping in chat_parser.py "
                           "(2026-08-20 header audit; docs/RECONSTRUCTION.md)",
            "lock_state": "LOCKED. Features parsed for the one-shot evaluation "
                          "only. Never for training or any development decision.",
            "source_corpus": lu_root,
            "script": "scripts/build_lu.py",
            "generated": datetime.date.today().isoformat(),
        }, fh, indent=2)
    print(f"  features + meta + PROVENANCE written to {OUT}/")
    print("\n  REMINDER: Lu is locked. Do not score it without the "
          "pre-registered one-shot protocol.")


if __name__ == "__main__":
    main()
