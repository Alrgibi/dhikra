"""
RDI CROSS-TASK PROBE  --  does the referential deficit index travel off the picture?
=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-25 BEFORE execution.
=============================================================================

WHY THIS IS BEING RUN NOW, BEFORE THE SPECIFICATION IS WRITTEN.
Section 5.25 measured that for MCI, connected-discourse tasks beat picture
description on Delaware. The Arabic contribution of this thesis -- pro-drop, the
referential deficit index, and its English construct validation -- was built
entirely on picture description. If the Libyan battery moves to narrative
retelling and procedural discourse, THE INDEX HAS TO MOVE WITH IT. If it does
not, the task recommendation and the Arabic instrument pull apart, and the
specification has to choose between them. That must be known before the
specification goes into the thesis, not after.

WHAT IS TESTED. Not the Arabic index -- the CONSTRUCT: that pointing and vague
reference, measured relative to naming, carries signal about cognitive
impairment. English is the only place it can be probed (docs/ARABIC_CORPUS_GAP.md).

MEASURES, identical to scripts/rdi_english_probe.py, same tokeniser, same POS
filters, same is_alpha rule:
    pn        = n_pron / n_noun                    (the deployed marker)
    rdi_full  = (n_pron + demo_f + vague_f) / n_noun
    rdi_free  = (demo_f + vague_f) / n_noun        (the ARABIC-RELEVANT form,
                                                    because Arabic drops pronouns)
Naive (unfiltered) variants reported alongside, as before.

ANALYSIS SET. Delaware, all five tasks, restricted to the SAME 288 participants
at the SAME earliest common visit used by section 5.25, so that every task is
measured on the same people and every contrast is paired. Labels are that
visit's labels (18 of 288 participants change label across visits; see 5.25).

TASK GENRE, declared here because it is the structural fact the criteria rest on:
    PICTURE DESCRIPTION  cookie, cat, rockwell
    CONNECTED DISCOURSE  cinderella (story retell from a wordless book),
                         sandwich (procedural)

SANITY GATE, as in the original probe. The pronoun-to-noun ratio recomputed here
must reproduce the committed ling.pronoun_to_noun_ratio in that task's
features.csv on at least 99% of recordings. A task failing this gate is VOID and
reported as void, not silently dropped.

PRIMARY CRITERION, mechanical.
  RDI-TRAVELS            rdi_free has participant-bootstrap 95% CI lower bound
                         > 0.5 on BOTH cinderella AND sandwich.
  RDI-TRAVELS-PARTIALLY  exactly one of the two.
  RDI-DOES-NOT-TRAVEL    neither.
SECONDARY, declared in advance:
  the paired difference  mean(rdi_free AUC over discourse tasks)
                       - mean(rdi_free AUC over picture tasks)
  with a paired participant bootstrap. This is a GENRE contrast and is
  pre-specified rather than selected, unlike any single best task.
  Report-and-stop.

INTERPRETIVE ASYMMETRY, registered.
  RDI-DOES-NOT-TRAVEL is not a small negative. It would mean the Arabic
  instrument as designed is tied to picture description, while the measurement
  says picture description is the weaker task for the target that matters most.
  The specification would then have to either keep picture description for the
  Arabic pilot and accept the weaker task, or move to discourse and rebuild the
  Arabic marker. Reporting that conflict honestly is the point of running this
  before writing rather than after.

GOVERNANCE. Delaware only. Lu is not read. No model is trained or modified.
Corpora are read in place and never copied. Descriptive only.
"""
import json, os, sys, glob
import numpy as np, pandas as pd

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
DB   = os.path.join(os.path.expanduser("~"), "mnt", "DementiaBank")
STATE= os.path.join(os.path.expanduser("~"), "state", "rdi_xtask")
os.makedirs(STATE, exist_ok=True)
os.chdir(REPO); sys.path.insert(0, "src")

TASKS   = ["cookie", "cat", "rockwell", "cinderella", "sandwich"]
PICTURE = ["cookie", "cat", "rockwell"]
DISCOURSE = ["cinderella", "sandwich"]
DEMO  = {"this", "that", "these", "those", "here", "there"}
VAGUE = {"thing", "things", "something", "anything", "stuff", "one", "ones"}

def counts_for(doc):
    words = [t for t in doc if t.is_alpha]
    n_noun = sum(1 for t in words if t.pos_ in ("NOUN", "PROPN"))
    n_pron = sum(1 for t in words if t.pos_ == "PRON")
    demo_f = demo_n = vague_f = vague_n = 0
    for t in words:
        w = t.lower_
        if w in DEMO:
            demo_n += 1
            if w in ("this", "that", "these", "those"):
                if t.pos_ in ("DET", "PRON"): demo_f += 1
            else:
                if t.pos_ == "ADV" and t.dep_ != "expl": demo_f += 1
        if w in VAGUE:
            vague_n += 1
            if t.pos_ in ("NOUN", "PRON"): vague_f += 1
    return dict(n_noun=n_noun, n_pron=n_pron, demo_f=demo_f, demo_n=demo_n,
                vague_f=vague_f, vague_n=vague_n, n_tok=len(words))

def extract(task, chunk=None, nchunks=4):
    """HARNESS-ONLY AMENDMENT (2026-08-25): chunked extraction. The Cowork VM
    kills every process at 45 s and the cinderella/sandwich transcripts are far
    longer than the picture-description ones. Chunking changes no definition, no
    analysis set and no criterion: file order is deterministic and the parts are
    concatenated before any statistic is computed."""
    cache = os.path.join(STATE, f"{task}.csv")
    if os.path.exists(cache): print("cached:", task); return
    if chunk is not None:
        part = os.path.join(STATE, f"{task}.part{chunk}.csv")
        if os.path.exists(part): print("cached part:", task, chunk); return
    import spacy
    nlp = spacy.load("en_core_web_sm")
    from dhikra.multitask_parser import collect_task
    files = [t for t in collect_task(os.path.join(DB, "Delaware"), task)
             if t.group in ("Control", "MCI")]
    files = files if chunk is None else files[chunk::nchunks]
    rows = []
    for t in files:
        txt = (t.clean_text or "").strip()
        if not txt: continue
        r = counts_for(nlp(txt)); r["file_id"] = t.file_id; rows.append(r)
    dest = cache if chunk is None else os.path.join(STATE, f"{task}.part{chunk}.csv")
    pd.DataFrame(rows).to_csv(dest, index=False)
    print(f"{task} chunk={chunk}: {len(rows)} of {len(files)} parsed")

def assemble(task, nchunks=4):
    cache = os.path.join(STATE, f"{task}.csv")
    if os.path.exists(cache): return True
    parts = [os.path.join(STATE, f"{task}.part{c}.csv") for c in range(nchunks)]
    if not all(os.path.exists(x) for x in parts): return False
    pd.concat([pd.read_csv(x) for x in parts], ignore_index=True).to_csv(cache, index=False)
    print(f"assembled {task}: {sum(len(pd.read_csv(x)) for x in parts)} rows"); return True

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "assemble":
        for t in a[1:]: print(t, assemble(t))
    else:
        task = a[0]
        for c in ([int(x) for x in a[1:]] or [None]):
            extract(task, c)


# ---------------------------------------------------------------- scoring ---
def auc(y, v):
    y = np.asarray(y); v = np.asarray(v, float)
    m = ~np.isnan(v); y, v = y[m], v[m]
    a, b = int((y == 1).sum()), int((y == 0).sum())
    if a == 0 or b == 0: return float("nan")
    r = pd.Series(v).rank().values
    return float((r[y == 1].sum() - a * (a + 1) / 2.0) / (a * b))

def score():
    import functools
    R = "results"
    D = {}
    for t in TASKS:
        d = pd.read_csv(os.path.join(STATE, f"{t}.csv"))
        d["pn"] = d.n_pron / d.n_noun.replace(0, np.nan)
        d["rdi_full"] = (d.n_pron + d.demo_f + d.vague_f) / d.n_noun.replace(0, np.nan)
        d["rdi_free"] = (d.demo_f + d.vague_f) / d.n_noun.replace(0, np.nan)
        d["rdi_free_naive"] = (d.demo_n + d.vague_n) / d.n_noun.replace(0, np.nan)
        D[t] = d.set_index("file_id")
    # sanity gate
    gate = {}
    for t in TASKS:
        F = pd.read_csv(f"{R}/delaware/{t}_features.csv")
        M = pd.read_csv(f"{R}/delaware/{t}_meta.csv")
        col = "ling.pronoun_to_noun_ratio"
        if col not in F.columns: gate[t] = None; continue
        c = pd.Series(F[col].values, index=M.file_id.values)
        j = D[t].join(c.rename("committed"), how="inner")
        ok = np.isclose(j.pn.values, j.committed.values, atol=1e-6, equal_nan=True)
        gate[t] = float(np.mean(ok))
    print("SANITY GATE  pn reproduces committed ling.pronoun_to_noun_ratio:")
    for t in TASKS: print(f"   {t:12s} {gate[t] if gate[t] is None else f'{gate[t]:.4f}'}")
    void = [t for t in TASKS if gate[t] is not None and gate[t] < 0.99]
    if void: print(f"   VOID (gate<0.99): {void}")
    # cross-sectional set: earliest visit common to all five, from 5.25
    M = {t: pd.read_csv(f"{R}/delaware/{t}_meta.csv") for t in TASKS}
    for t in TASKS:
        M[t]["visit"] = M[t].file_id.astype(str).str.extract(r"-(\d+)\|")[0].astype(float)
        M[t]["pid"] = M[t].participant_id.astype(str)
    common = None
    for t in TASKS:
        s = set(map(tuple, M[t][["pid", "visit"]].dropna().values))
        common = s if common is None else common & s
    cdf = pd.DataFrame(list(common), columns=["pid", "visit"])
    first = cdf.sort_values("visit").groupby("pid", as_index=False).first()
    rows = {}
    for t in TASKS:
        j = first.merge(M[t][["pid", "visit", "file_id", "label"]], on=["pid", "visit"], how="left")
        rows[t] = j
    y = rows[TASKS[0]].label.values.astype(int)
    n = len(y)
    print(f"\nCROSS-SECTIONAL SET: {n} participants, impaired {int(y.sum())}, control {int((y==0).sum())}")
    V = {}
    for t in TASKS:
        idx = rows[t].file_id.values
        V[t] = {m: D[t].reindex(idx)[m].values for m in ("pn", "rdi_full", "rdi_free", "rdi_free_naive")}
    rng = np.random.default_rng(42)
    boot = [rng.choice(n, n, replace=True) for _ in range(2000)]
    print(f"\n{'task':<12} {'genre':<10} {'pn':>17} {'rdi_full':>17} {'rdi_free':>17}")
    res = {}
    for t in TASKS:
        g = "PICTURE" if t in PICTURE else "DISCOURSE"
        cells, res[t] = [], {}
        for mname in ("pn", "rdi_full", "rdi_free"):
            v = V[t][mname]; a = auc(y, v)
            bs = np.array([auc(y[i], v[i]) for i in boot])
            lo, hi = np.nanpercentile(bs, [2.5, 97.5])
            res[t][mname] = dict(auc=a, ci95=[float(lo), float(hi)], boot=bs)
            cells.append(f"{a:.3f}[{lo:.3f},{hi:.3f}]")
        print(f"{t:<12} {g:<10} " + " ".join(f"{c:>17}" for c in cells))
    lows = {t: res[t]["rdi_free"]["ci95"][0] for t in TASKS}
    trav = [t for t in DISCOURSE if lows[t] > 0.5]
    grade = ("RDI-TRAVELS" if len(trav) == 2 else
             "RDI-TRAVELS-PARTIALLY" if len(trav) == 1 else "RDI-DOES-NOT-TRAVEL")
    print(f"\nrdi_free CI lower bounds: " + ", ".join(f"{t}={lows[t]:.4f}" for t in TASKS))
    print(f"GRADE: {grade}   (discourse tasks clearing 0.5: {trav or 'none'})")
    out = {}
    for mname in ("pn", "rdi_full", "rdi_free"):
        dsc = np.mean([res[t][mname]["boot"] for t in DISCOURSE], axis=0)
        pic = np.mean([res[t][mname]["boot"] for t in PICTURE], axis=0)
        d = dsc - pic
        pt = np.mean([res[t][mname]["auc"] for t in DISCOURSE]) - np.mean([res[t][mname]["auc"] for t in PICTURE])
        lo, hi = np.nanpercentile(d, [2.5, 97.5])
        out[mname] = dict(delta=float(pt), ci95=[float(lo), float(hi)], excludes_zero=bool(lo > 0 or hi < 0))
        print(f"  GENRE CONTRAST {mname:<10} discourse - picture = {pt:>+7.4f} [{lo:>+7.4f},{hi:>+7.4f}] "
              f"{'EXCLUDES 0' if (lo>0 or hi<0) else 'includes 0'}")
    js = dict(registration="module docstring, committed before execution",
              sanity_gate=gate, void_tasks=void, n=n, n_impaired=int(y.sum()),
              per_task={t: {m: {k: v for k, v in res[t][m].items() if k != "boot"} for m in res[t]} for t in TASKS},
              grade=grade, discourse_clearing_chance=trav, genre_contrast=out,
              genre=dict(picture=PICTURE, discourse=DISCOURSE),
              governance="Delaware only; Lu not read; corpora read in place; descriptive")
    json.dump(js, open(f"{R}/reconstruction/rdi_cross_task_probe.json", "w"), indent=2)
    print("\nwritten: results/reconstruction/rdi_cross_task_probe.json")
