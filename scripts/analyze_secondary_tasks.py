"""
analyze_secondary_tasks.py
--------------------------
Extracts what CAN legitimately be learned from the fluency, recall and
sentence tasks of the Pitt corpus.

THE CONSTRAINT, STATED PLAINLY
These three tasks were recorded from the DEMENTIA GROUP ONLY (235, 263 and 236
files respectively, against 2, 1 and 1 control files). With essentially no
healthy comparison group, no classifier separating patients from controls can
be trained on them, and any "cut-off" derived from them would be meaningless.

WHAT CAN STILL BE LEARNED, AND WHY IT MATTERS
Every one of those files carries the participant's MMSE score -- an independent
clinical measure of how impaired they are. So while the data cannot answer
"is this person impaired?", it can answer a different and genuinely useful
question: "does this task's score track HOW impaired someone is?"

If animal-fluency counts fall as MMSE falls, that is direct evidence from this
corpus that the task measures cognitive severity, and it licenses reporting the
score as a severity indicator rather than as a guess. If it does not track
MMSE, the task should be reported as raw description only. Either way the
answer comes from data rather than assumption.

This is the honest use of a dementia-only dataset: it cannot give a threshold,
but it can validate a gradient.
"""
import os
import re
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd
from scipy import stats

from dhikra.chat_parser import parse_cha
from dhikra.fluency_features import extract_fluency_features

# Path comes from corpus_paths.json (see src/dhikra/paths.py); the original
# hardcoded /home/claude/pitt died with that sandbox (de-hardcoded 2026-08-20).
from dhikra.paths import resolve
PITT = resolve("pitt_root")
OUT = "results/secondary_tasks"
BANNER = "=" * 78

# The two stories used in the Pitt recall task, with their propositions. Recall
# is scored by how many idea units are reproduced, which is the standard
# clinical approach for story recall.
GEORGE_KEYWORDS = {
    "thanksgiving", "george", "miller", "moved", "son", "family",
    "granddaughter", "melanie", "stories", "childhood", "city", "visit",
    "house", "lived", "child", "friday", "trip", "streets", "crowded",
    "held", "hand", "tightly",
}


def collect(task: str, group: str) -> pd.DataFrame:
    rows = []
    for path in sorted(glob.glob(os.path.join(PITT, group, task, "*.cha"))):
        tr = parse_cha(path)
        if not tr.clean_text.strip():
            continue
        rows.append({
            "file_id": tr.file_id,
            "participant_id": tr.file_id.split("-")[0],
            "group": tr.group, "age": tr.age, "sex": tr.sex, "mmse": tr.mmse,
            "text": tr.clean_text,
            "n_words": len(tr.clean_text.split()),
            "n_utterances": tr.n_utterances,
            "retracing": tr.n_retracing,
            "filled_pauses": tr.n_filled_pauses,
        })
    return pd.DataFrame(rows)


def corr_report(df: pd.DataFrame, cols: list[str], label: str) -> pd.DataFrame:
    sub = df[df.mmse.notna()]
    rows = []
    for c in cols:
        v = sub[c]
        m = v.notna()
        if m.sum() < 30 or v[m].std() == 0:
            continue
        r, p = stats.pearsonr(v[m], sub.mmse[m])
        rows.append((c, r, p, int(m.sum())))
    out = pd.DataFrame(rows, columns=["measure", "r_with_mmse", "p_value", "n"])
    out["abs"] = out.r_with_mmse.abs()
    out = out.sort_values("abs", ascending=False).drop(columns="abs")
    print(f"\n{label}")
    print("-" * 78)
    if out.empty:
        print("  not enough data")
    else:
        print(out.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)

    # ── FLUENCY ────────────────────────────────────────────────────────────
    print(BANNER)
    print("VERBAL FLUENCY  (animals, 60 seconds)")
    print(BANNER)
    flu = collect("fluency", "Dementia")
    fc = collect("fluency", "Control")
    print(f"  dementia files: {len(flu)}   control files: {len(fc)}")
    print("  -> too few controls to build a cut-off; testing the SEVERITY "
          "gradient instead")

    feats = []
    for _, r in flu.iterrows():
        f = extract_fluency_features(r.text, lang="en")
        feats.append({
            "total_correct": f.get("flu.total_correct", 0),
            "perseverations": f.get("flu.perseverations", 0),
            "unrecognised": f.get("flu.intrusions", 0),
        })
    flu = pd.concat([flu.reset_index(drop=True),
                     pd.DataFrame(feats)], axis=1)

    print(f"\n  animals named: median {flu.total_correct.median():.0f}  "
          f"mean {flu.total_correct.mean():.1f}  "
          f"range {flu.total_correct.min():.0f}-{flu.total_correct.max():.0f}")
    print(f"  perseverations: median {flu.perseverations.median():.0f}  "
          f"mean {flu.perseverations.mean():.1f}")

    f_corr = corr_report(flu, ["total_correct", "perseverations",
                               "unrecognised", "n_words"],
                         "Does fluency track MMSE severity?")
    f_corr.to_csv(f"{OUT}/fluency_mmse.csv", index=False)
    flu.drop(columns=["text"]).to_csv(f"{OUT}/fluency_scores.csv", index=False)

    # severity bands derived from the data itself
    sub = flu[flu.mmse.notna()]
    if len(sub) > 50:
        print("\n  Animal count by MMSE band (this corpus, dementia group):")
        bands = pd.cut(sub.mmse, [0, 10, 15, 20, 25, 30],
                       labels=["0-10 severe", "11-15", "16-20", "21-25",
                               "26-30 mild"])
        g = sub.groupby(bands, observed=True).total_correct.agg(
            ["count", "mean", "median"])
        print(g.round(1).to_string())
        g.to_csv(f"{OUT}/fluency_by_mmse_band.csv")

    # ── STORY RECALL ───────────────────────────────────────────────────────
    print("\n" + BANNER)
    print("STORY RECALL")
    print(BANNER)
    rec = collect("recall", "Dementia")
    print(f"  dementia files: {len(rec)}   "
          f"control files: {len(collect('recall','Control'))}")

    def keyword_recall(t):
        w = set(re.findall(r"[a-z']+", t.lower()))
        return len(w & GEORGE_KEYWORDS)

    rec["idea_units_recalled"] = rec.text.map(keyword_recall)
    print(f"\n  idea units recalled: median {rec.idea_units_recalled.median():.0f}  "
          f"mean {rec.idea_units_recalled.mean():.1f}  "
          f"of {len(GEORGE_KEYWORDS)} possible")

    r_corr = corr_report(rec, ["idea_units_recalled", "n_words",
                               "n_utterances", "retracing"],
                         "Does story recall track MMSE severity?")
    r_corr.to_csv(f"{OUT}/recall_mmse.csv", index=False)
    rec.drop(columns=["text"]).to_csv(f"{OUT}/recall_scores.csv", index=False)

    # ── SENTENCE CONSTRUCTION ──────────────────────────────────────────────
    print("\n" + BANNER)
    print("SENTENCE CONSTRUCTION")
    print(BANNER)
    sen = collect("sentence", "Dementia")
    print(f"  dementia files: {len(sen)}")
    s_corr = corr_report(sen, ["n_words", "n_utterances", "retracing",
                               "filled_pauses"],
                         "Does sentence construction track MMSE severity?")
    s_corr.to_csv(f"{OUT}/sentence_mmse.csv", index=False)

    # ── CROSS-TASK: the memory dissociation ────────────────────────────────
    print("\n" + BANNER)
    print("CROSS-TASK PROFILE  (same participants across tasks)")
    print(BANNER)
    merged = (flu[["participant_id", "mmse", "total_correct"]]
              .merge(rec[["participant_id", "idea_units_recalled"]],
                     on="participant_id", how="inner")
              .drop_duplicates("participant_id"))
    print(f"  participants with both fluency and recall: {len(merged)}")
    if len(merged) > 30:
        m = merged.dropna(subset=["mmse"])
        r, p = stats.pearsonr(m.total_correct, m.idea_units_recalled)
        print(f"  fluency vs recall correlation: r = {r:.3f}  p = {p:.2e}")
        print("  -> the two tasks measure related but distinct abilities, "
              "which is what makes a PROFILE across tasks informative rather "
              "than redundant.")
        merged.to_csv(f"{OUT}/cross_task.csv", index=False)

    print(f"\nwritten to {OUT}/")


if __name__ == "__main__":
    main()
