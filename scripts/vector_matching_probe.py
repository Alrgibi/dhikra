"""
CAN A FROZEN PRETRAINED MODEL COUNT INFORMATION UNITS BETTER THAN WORD LISTS?
=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-26 BEFORE execution.
=============================================================================

WHY. Section 5.5.1 graded the automated scorer INADEQUATE: mean absolute
difference 1.600 against a registered 1.200, a near-constant undercount of 1.5
units, misses outnumbering false credits 3.7 : 1. The lists are TOO TIGHT. The
question is whether the one pretrained model that runs on this hardware --
en_core_web_md's 300-dimensional word vectors, no torch, no network -- can close
that gap by crediting a unit when a SEMANTICALLY SIMILAR word is used rather than
a listed one.

WHAT IS ALREADY RULED OUT, so this is not re-tested: lemmatisation. The committed
extractor already matches on BOTH t.lemma_ and t.text (information_units.py
_lemma_set), so "kids" already matches "kid". The misses are semantic, not
morphological.

DESIGN
  Reference   the 20 hand-scored transcripts (docs/scorer_check/), the only
              human reference that exists. NEITHER SCORER IS ASSUMED CORRECT:
              the human may over-credit and the software may under-credit. What
              is measured is whether vectors move the automated count TOWARD the
              human count, and in what proportion of misses versus false credits.
  Arms        BASELINE  the committed extractor, unchanged
              VECTOR-k  baseline, plus: credit an entity unit when any content
                        token's cosine similarity to any list member is >= k
  Sweep       k in {0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70},
              declared here and not to be extended.

CRITERION, fixed in advance and applied mechanically.
  VECTORS-HELP   some k in the declared sweep gives mean absolute difference
                 STRICTLY BELOW the baseline's 1.600 AND total false credits no
                 more than double the baseline's 11 (i.e. <= 22).
  VECTORS-HURT   every k either raises the mean absolute difference or more than
                 doubles false credits.
  Report-and-stop. The best k is not tuned further and nothing is deployed:
  changing the extractor changes the model, so any positive result is
  SPECIFIED-SUCCESSOR material under 1.7, never a deployed change.

INTERPRETIVE ASYMMETRY, registered. A negative result closes the question of
whether AI helps the COUNTING on this hardware, and it closes it with a
measurement rather than an assertion -- which is the point of running it. It
would also localise WHY: if similarity cannot separate a true synonym from an
unrelated word at this vector quality, no threshold on it can work, and the
remedy is a better list or a better model, not a better cut-off.
"""
import os, sys, json, csv
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import spacy
from dhikra.information_units import SUBJECTS, PLACES, OBJECTS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
man = json.load(open(f"{ROOT}/docs/scorer_check/sample_manifest.json"))
units = man["units"]
LISTS = {}
for d in (SUBJECTS, PLACES, OBJECTS):
    for k, v in d.items(): LISTS[k] = set(v)
ENT = [u for u in units if u in LISTS]
print(f"entity units with lists: {len(ENT)} of {len(units)}")

txt = open(f"{ROOT}/docs/scorer_check/transcripts.md", encoding="utf-8").read()
T = {}
for blk in txt.split("\n## ")[1:]:
    lab = blk.splitlines()[0].strip()
    body = " ".join(l.strip("> ").strip() for l in blk.splitlines()[1:] if l.strip().startswith(">"))
    T[lab] = body
print(f"transcripts parsed: {len(T)}")

rows = list(csv.DictReader(open(f"{ROOT}/docs/scorer_check/scoring_sheet_FILLED.csv", encoding="utf-8")))
H = {d["transcript"]: {u: int(d[u]) for u in units} for d in rows}
labels = [d["transcript"] for d in rows]

nlp = spacy.load("en_core_web_md")
docs = {l: nlp(T[l]) for l in labels}
def lemset(doc):
    s = {t.lemma_.lower() for t in doc if t.is_alpha}
    s |= {t.text.lower() for t in doc if t.is_alpha}
    return s
LS = {l: lemset(docs[l]) for l in labels}

# baseline per-unit entity decisions, reproduced from the committed rule
base = {l: {u: int(bool(LS[l] & LISTS[u])) for u in ENT} for l in labels}

def maxsim(doc, forms):
    best = 0.0
    keys = [f for f in forms if nlp.vocab[f].has_vector]
    for t in doc:
        if not t.is_alpha or not t.has_vector or t.is_stop: continue
        for f in keys:
            s = t.similarity(nlp.vocab[f])
            if s > best: best = s
    return best
SIM = {l: {u: maxsim(docs[l], LISTS[u]) for u in ENT} for l in labels}

def score(k=None):
    tot, miss, fc = [], 0, 0
    for l in labels:
        n = 0
        for u in units:
            if u in ENT:
                v = base[l][u] or (1 if (k is not None and SIM[l][u] >= k) else 0)
            else:
                v = None
            if v is None: continue
            h = H[l][u]
            if h == 1 and v == 0: miss += 1
            if h == 0 and v == 1: fc += 1
            n += v
        tot.append(n)
    # non-entity units are identical in every arm; compare on entity units only
    hum = [sum(H[l][u] for u in ENT) for l in labels]
    d = np.array(tot, float) - np.array(hum, float)
    return float(np.mean(np.abs(d))), float(np.mean(d)), miss, fc

b = score(None)
print(f"\n{'arm':<12} {'MAE(entity)':>12} {'bias':>8} {'misses':>8} {'false credits':>14}")
print(f"{'BASELINE':<12} {b[0]:>12.3f} {b[1]:>+8.3f} {b[2]:>8} {b[3]:>14}")
res = {"baseline": dict(mae=b[0], bias=b[1], misses=b[2], false_credits=b[3])}
best = None
for k in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
    r = score(k)
    res[f"k={k:.2f}"] = dict(mae=r[0], bias=r[1], misses=r[2], false_credits=r[3])
    flag = "  <-- beats baseline" if (r[0] < b[0] and r[3] <= 2 * b[3]) else ""
    print(f"{'VECTOR '+str(k):<12} {r[0]:>12.3f} {r[1]:>+8.3f} {r[2]:>8} {r[3]:>14}{flag}")
    if r[0] < b[0] and r[3] <= 2 * b[3] and (best is None or r[0] < best[1]): best = (k, r[0])
grade = "VECTORS-HELP" if best else "VECTORS-HURT"
print(f"\nGRADE: {grade}" + (f"   best k = {best[0]} at MAE {best[1]:.3f}" if best else ""))
json.dump(dict(registration="module docstring, committed before execution",
    n_transcripts=len(labels), entity_units=len(ENT), arms=res, grade=grade,
    best=None if not best else dict(k=best[0], mae=best[1]),
    note="entity units only; non-entity units are identical across arms",
    governance="nothing deployed; changing the extractor changes the model, so any gain is specified-successor material"),
    open(f"{ROOT}/results/reconstruction/vector_matching_probe.json", "w"), indent=2)
print("written: results/reconstruction/vector_matching_probe.json")
