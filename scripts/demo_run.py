"""
demo_run.py
-----------
End-to-end demonstration: given a recording + its transcript, produce the
single combined feature vector that becomes one row of the model's training
matrix. Run:  python scripts/demo_run.py
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dhikra import extract_all_features

SAMPLE_WAV = os.path.join(os.path.dirname(__file__), "..",
                          "data", "samples", "sample_control.wav")

# In production this transcript comes from Whisper ASR of the same recording.
SAMPLE_TRANSCRIPT = (
    "The mother is standing at the sink washing the dishes while the water "
    "overflows onto the floor and the boy is reaching for the cookie jar."
)


def main():
    feats = extract_all_features(SAMPLE_WAV, SAMPLE_TRANSCRIPT, lang="en")
    print(f"Combined feature vector: {len(feats)} features\n")
    ac = {k: v for k, v in feats.items() if k.startswith("ac.")}
    ling = {k: v for k, v in feats.items() if k.startswith("ling.")}
    print(f"  acoustic (language-independent): {len(ac)} features")
    print(f"  linguistic (English)          : {len(ling)} features")
    print("\nFull vector (JSON):")
    print(json.dumps(feats, indent=2))


if __name__ == "__main__":
    main()
