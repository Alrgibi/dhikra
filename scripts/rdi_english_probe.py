"""
rdi_english_probe.py -- construct probe for the Arabic referential deficit index,
run in ENGLISH, where the components are best understood and both classes exist.

=============================================================================
PRE-REGISTRATION. Written and committed 2026-08-23 BEFORE any data was read.
Criteria below are fixed. Amendments, if any, are APPENDED to a REGISTRATION
HISTORY at the foot of this docstring and never made silently.
=============================================================================

MOTIVATION
The Arabic instrument replaces the English pronoun-overuse marker with a
REFERENTIAL DEFICIT INDEX, because Arabic is pro-drop and pronoun counts sit on
a different baseline for grammatical rather than clinical reasons. As
implemented in src/dhikra/linguistic_features_ar.py:

    RDI = (standalone pronouns + demonstratives + vague nouns) / nouns

The index has NEVER been computed on the speech of a diagnosed patient, in any
language. That is the weakest evidential point in the thesis. It cannot be
fixed in Arabic -- no public Arabic corpus pairs impaired and healthy speakers
on a connected-speech task (docs/ARABIC_CORPUS_GAP.md). It CAN be probed in
English, where demonstratives and vague nouns also exist, where the pronoun
marker is established, and where 987 labelled recordings are already on disk.

WHAT IS BEING TESTED. Not the Arabic index -- the CONSTRUCT behind it: that
pointing and vague reference, measured relative to naming, carries signal about
cognitive impairment.

DEFINITIONS, fixed in advance.
  Denominator  n_noun = count(POS == NOUN) + count(POS == PROPN), which is
               exactly the denominator the deployed ling.pronoun_to_noun_ratio
               uses (src/dhikra/linguistic_features.py:90). Same tokeniser,
               same model (en_core_web_sm). The comparison is like for like.
  Pronouns     count(POS == PRON), as deployed.
  Demonstratives, POS-FILTERED variant:
               {this, that, these, those} where POS is DET or PRON -- which
               excludes complementiser "that" (POS SCONJ, dep mark); plus
               {here, there} where POS is ADV and dep is NOT "expl" -- which
               excludes existential "there is / there are".
  Vague nouns, POS-FILTERED variant:
               {thing, things, something, anything, stuff, one, ones} where POS
               is NOUN or PRON -- which excludes numeral "one" (POS NUM).
  NAIVE variant: the same word lists by bare string match, with no POS
               filtering. This mirrors the ARABIC implementation, which
               deliberately uses exact closed-class matches and no tagger
               ("Built ONLY from exact closed-class matches"). Reporting both
               is itself informative: if they disagree materially, the Arabic
               index inherits a confound it does not currently control for,
               because Arabic hunaak does the same double duty as English
               "there".

  Note, recorded in advance so it is not presented later as a discovery: vague
  nouns appear in BOTH numerator and denominator, since spaCy tags them NOUN.
  The Arabic index has the same property. This is a faithful port, not an error.

THREE MEASURES, all computed per recording:
  pn        = pron / n_noun                      (the established marker)
  rdi_full  = (pron + demo + vague) / n_noun     (the Arabic index, ported)
  rdi_free  = (demo + vague) / n_noun            (pronoun-free; this is what the
                                                  Arabic index EFFECTIVELY is,
                                                  because Arabic drops pronouns)

PRIMARY QUESTION. Does rdi_free discriminate impaired from healthy?
  POSITIVE  -- participant-bootstrap 95% CI for AUC excludes 0.5 in BOTH Pitt
               and Delaware.
  PARTIAL   -- excludes 0.5 in exactly one cohort.
  NEGATIVE  -- includes 0.5 in both.
  A NEGATIVE IS A REPORTABLE RESULT AND WILL BE REPORTED. It would mean the
  referential-deficit construct, as operationalised, carries no discriminative
  signal in the one language where it can currently be checked. That materially
  weakens the Arabic design and must be stated in those terms, not softened.

SECONDARY QUESTION. Does adding demonstratives and vague nouns to the
established marker help or hurt? Judged on the PAIRED bootstrap difference
AUC(rdi_full) - AUC(pn), resampled over the same participants:
  ENHANCEMENT -- difference CI excludes 0 and is positive.
  DILUTION    -- difference CI excludes 0 and is negative.
  NEUTRAL     -- CI includes 0.
  A DILUTION result matters as much as an enhancement: it would mean the Arabic
  index degrades a good marker by folding two things together, and the Arabic
  implementation should be revised to keep the components separate.

TERTIARY QUESTION (convergent validity). Spearman rho between rdi_free and pn,
computed WITHIN the control group and WITHIN the impaired group separately, so
that the correlation is not manufactured by the group difference itself.
  |rho| > 0.5 in both -- the two measure substantially the same thing.
  |rho| < 0.3 in both, with rdi_free discriminating -- they measure
                        COMPLEMENTARY aspects, which would be the more
                        interesting outcome.

REGISTERED INTERPRETIVE ASYMMETRY. Positive and negative results do NOT
transfer equally, and this is fixed before seeing either:
  * A POSITIVE result is construct evidence IN ENGLISH ONLY. It does not
    validate the Arabic index. Arabic demonstratives and vague nouns may behave
    differently, Arabic morphology attaches pronouns as clitics, and the Arabic
    index operates without the pronoun term.
  * A NEGATIVE result transfers MORE strongly, because it would show the
    construct fails in the language where its components are best understood
    and best tagged. English is the easy case for this construct.

ANALYSIS SETS. Pitt cookie (552 .cha) and Delaware cookie (455 .cha),
separately, joined to the committed meta.csv label columns. Pitt is
additionally analysed on the age- and sex-matched subset (matched_mask.npy) as
the confound-controlled check, because pronoun and naming behaviour vary with
age.

BOOTSTRAP. Participant-level, 2000 resamples, seed 42 -- the same protocol as
every other interval in this project.

GOVERNANCE. The Lu corpus is not read and not referenced. No model is trained,
loaded or modified. No threshold moves. Nothing here can alter a locked result;
this is descriptive measurement on development data only.

SANITY CHECK, declared in advance: the recomputed `pn` must reproduce the
committed ling.pronoun_to_noun_ratio in features.csv to within 1e-6 on at least
99% of recordings. If it does not, the extraction is wrong and the run is void.

REGISTRATION HISTORY
  2026-08-23, AMENDMENT 3 -- AND THIS ONE WAS MADE AFTER PART OF A RESULT WAS
  VISIBLE, WHICH IS DISCLOSED HERE RATHER THAN CONCEALED. The first completed
  run FAILED this script's own pre-declared sanity check: recomputed `pn`
  reproduced the committed ling.pronoun_to_noun_ratio on only 36% of Pitt and
  82% of Delaware recordings, against a declared floor of 99%. Diagnosis, in
  order: (i) pronoun counts matched the committed values almost perfectly
  (r = 0.9995 in both cohorts), so the tagger was not the problem; (ii) the
  committed Delaware extractor was re-run today on 40 of its own inputs and
  reproduced its committed output EXACTLY, ruling out environment drift;
  (iii) the committed extractor filters tokens with `words = [t for t in doc
  if t.is_alpha]` (linguistic_features.py:48) and this script did not, so
  punctuation, contraction fragments such as "n't" and "'s", and numerals were
  entering the counts. That is a defect in THIS script measured against its own
  registered definition -- which said the denominator would be "exactly the
  denominator the deployed ling.pronoun_to_noun_ratio uses". Fixing it HONOURS
  the pre-registration; it does not relax it. No criterion, threshold or
  analysis set was changed. All caches were deleted and both cohorts
  re-extracted from source.
  DISCLOSURE: the Delaware AUC block of the failed run was visible in terminal
  output before this fix was made. The fix was determined by reading the
  committed source, not by the result, and the criteria below are unchanged
  from the original registration. The reader is entitled to weigh that.

  2026-08-23, AMENDMENT 2, BEFORE ANY RESULT WAS SEEN: the Delaware extraction
  was reading whole .cha files. Delaware .cha files contain FIVE tasks each
  (cookie, cinderella, cat, rockwell, sandwich), so this was not the registered
  analysis set -- which is the Delaware COOKIE segment, the segment
  cookie_features.csv was built from. Corrected to call the committed
  dhikra.multitask_parser.collect_task path used by
  scripts/build_delaware.py::build_task, with the same Control/MCI filter. This
  was caught by the pre-declared join check (0 of 453 extracted ids matched the
  committed meta keys) and NOT by looking at any result; the first Delaware
  chunk cache was deleted and re-extracted. No criterion, definition or
  threshold was altered.

  2026-08-23, AMENDMENT 1, BEFORE ANY RESULT WAS SEEN: extraction was split
  into four cached chunks per cohort. The Delaware pass exceeded the Cowork
  VM's 45-second per-call process limit and was killed with no output. This is
  a HARNESS change only -- identical files, identical parser, identical spaCy
  model, identical counting code; chunk k processes files[k::4] and `assemble`
  concatenates. No criterion, definition, analysis set or threshold was
  altered, and no data had been inspected when this was made.
"""
import json, os, sys, glob, math
import numpy as np
import pandas as pd

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
DB = os.path.join(os.path.expanduser("~"), "mnt", "DementiaBank")
STATE = os.path.join(os.path.expanduser("~"), "state", "rdi")
os.makedirs(STATE, exist_ok=True)
os.chdir(REPO)
sys.path.insert(0, "src")

DEMO = {"this", "that", "these", "those", "here", "there"}
VAGUE = {"thing", "things", "something", "anything", "stuff", "one", "ones"}


def counts_for(doc):
    # is_alpha filter and nothing else, because that is exactly what the
    # committed extractor does (src/dhikra/linguistic_features.py:48,
    # `words = [t for t in doc if t.is_alpha]`). Counting punctuation,
    # contraction fragments and numerals gave a denominator that did not match
    # the deployed pronoun-to-noun ratio and failed this script's own
    # pre-declared sanity check.
    words = [t for t in doc if t.is_alpha]
    n_noun = sum(1 for t in words if t.pos_ in ("NOUN", "PROPN"))
    n_pron = sum(1 for t in words if t.pos_ == "PRON")
    demo_f = demo_n = vague_f = vague_n = 0
    for t in words:
        w = t.lower_
        if w in DEMO:
            demo_n += 1
            if w in ("this", "that", "these", "those"):
                if t.pos_ in ("DET", "PRON"):
                    demo_f += 1
            else:                                   # here / there
                if t.pos_ == "ADV" and t.dep_ != "expl":
                    demo_f += 1
        if w in VAGUE:
            vague_n += 1
            if t.pos_ in ("NOUN", "PRON"):
                vague_f += 1
    return dict(n_noun=n_noun, n_pron=n_pron, demo_f=demo_f, demo_n=demo_n,
                vague_f=vague_f, vague_n=vague_n, n_tok=len(words))


def extract(cohort, chunk=None, nchunks=4):
    """Chunked because the Cowork VM kills every process at the end of a 45 s
    tool call. Each chunk caches its own slice; `finish` concatenates them."""
    cache = os.path.join(STATE, f"{cohort}.csv")
    if os.path.exists(cache):
        print("cached:", cache); return
    if chunk is not None:
        part = os.path.join(STATE, f"{cohort}.part{chunk}.csv")
        if os.path.exists(part):
            print("cached:", part); return
    import spacy
    nlp = spacy.load("en_core_web_sm")   # full pipeline, as the committed extractor loads it
    if cohort == "pitt":
        from dhikra.chat_parser import parse_cha
        root = os.path.join(DB, "pitt_cookie")
        files = sorted(glob.glob(os.path.join(root, "**", "*.cha"), recursive=True))
    else:
        # Delaware .cha files contain FIVE tasks each. The registered analysis
        # set is the Delaware COOKIE segment, which is what cookie_features.csv
        # was built from, so the committed collect_task path is used verbatim
        # (scripts/build_delaware.py::build_task). Reading whole files would
        # mix in cinderella, cat, rockwell and sandwich and make the comparison
        # against the committed pronoun-to-noun feature meaningless.
        from dhikra.multitask_parser import collect_task
        files = [t for t in collect_task(os.path.join(DB, "Delaware"), "cookie")
                 if t.group in ("Control", "MCI")]
    sel = files if chunk is None else files[chunk::nchunks]
    rows = []
    for f in sel:
        t = parse_cha(f) if cohort == "pitt" else f
        txt = (t.clean_text or "").strip()
        if not txt:
            continue
        r = counts_for(nlp(txt))
        r["file_id"] = t.file_id
        rows.append(r)
    dest = cache if chunk is None else os.path.join(STATE, f"{cohort}.part{chunk}.csv")
    pd.DataFrame(rows).to_csv(dest, index=False)
    print(f"{cohort} chunk={chunk}: {len(rows)} of {len(sel)} parsed -> {dest}")


def assemble(cohort, nchunks=4):
    cache = os.path.join(STATE, f"{cohort}.csv")
    if os.path.exists(cache):
        return
    parts = [os.path.join(STATE, f"{cohort}.part{i}.csv") for i in range(nchunks)]
    missing = [p for p in parts if not os.path.exists(p)]
    if missing:
        raise SystemExit("missing chunks: " + ", ".join(os.path.basename(m) for m in missing))
    pd.concat([pd.read_csv(p) for p in parts], ignore_index=True).to_csv(cache, index=False)
    print("assembled", cache)


def auc(y, s):
    y = np.asarray(y); s = np.asarray(s)
    ok = np.isfinite(s)
    y, s = y[ok], s[ok]
    if len(np.unique(y)) < 2: return float("nan")
    r = pd.Series(s).rank().values
    n1 = (y == 1).sum(); n0 = (y == 0).sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def boot(df, cols, seed=42, B=2000):
    rng = np.random.default_rng(seed)
    pids = df.participant_id.unique()
    idx = {p: np.where(df.participant_id.values == p)[0] for p in pids}
    out = {c: [] for c in cols}
    diffs = []
    for _ in range(B):
        take = np.concatenate([idx[p] for p in rng.choice(pids, len(pids), True)])
        d = df.iloc[take]
        vals = {}
        for c in cols:
            vals[c] = auc(d.label.values, d[c].values)
            out[c].append(vals[c])
        diffs.append(vals.get("rdi_full", np.nan) - vals.get("pn", np.nan))
    res = {}
    for c in cols:
        a = np.array(out[c]); a = a[np.isfinite(a)]
        res[c] = {"auc": round(float(auc(df.label.values, df[c].values)), 4),
                  "ci95": [round(float(np.percentile(a, 2.5)), 4),
                           round(float(np.percentile(a, 97.5)), 4)]}
    dd = np.array(diffs); dd = dd[np.isfinite(dd)]
    res["_paired_diff_rdi_full_minus_pn"] = {
        "point": round(float(auc(df.label.values, df.rdi_full.values)
                             - auc(df.label.values, df.pn.values)), 4),
        "ci95": [round(float(np.percentile(dd, 2.5)), 4),
                 round(float(np.percentile(dd, 97.5)), 4)]}
    return res


def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    if len(a) < 5: return float("nan")
    ra = pd.Series(a).rank().values; rb = pd.Series(b).rank().values
    ra = ra - ra.mean(); rb = rb - rb.mean()
    den = math.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / den) if den else float("nan")


def build(cohort):
    c = pd.read_csv(os.path.join(STATE, f"{cohort}.csv"))
    if cohort == "pitt":
        meta = pd.read_csv("results/pitt_cookie/meta.csv")
        feats = pd.read_csv("results/pitt_cookie/features.csv")
    else:
        meta = pd.read_csv("results/delaware/cookie_meta.csv")
        feats = pd.read_csv("results/delaware/cookie_features.csv")
    feats = feats.copy()
    if "file_id" not in feats.columns:
        feats["file_id"] = meta.file_id.values
    d = c.merge(meta[["file_id", "participant_id", "label"]], on="file_id", how="inner")
    d = d.merge(feats[["file_id", "ling.pronoun_to_noun_ratio"]], on="file_id", how="left")
    nn = d.n_noun.replace(0, np.nan)
    d["pn"] = d.n_pron / nn
    d["rdi_full"] = (d.n_pron + d.demo_f + d.vague_f) / nn
    d["rdi_free"] = (d.demo_f + d.vague_f) / nn
    d["rdi_full_naive"] = (d.n_pron + d.demo_n + d.vague_n) / nn
    d["rdi_free_naive"] = (d.demo_n + d.vague_n) / nn
    return d.dropna(subset=["label"])


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "extract":
        extract(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None)
    elif mode == "assemble":
        assemble(sys.argv[2])
    elif mode == "finish":
        COLS = ["pn", "rdi_full", "rdi_free", "rdi_full_naive", "rdi_free_naive"]
        out = {"generated": "2026-08-23",
               "preregistration": "criteria fixed in this script's docstring before execution",
               "governance": "Lu not read; no model trained or modified; descriptive only",
               "cohorts": {}}
        for cohort in ("pitt", "dela"):
            d = build(cohort)
            # declared sanity check
            chk = d.dropna(subset=["ling.pronoun_to_noun_ratio"])
            agree = float((np.abs(chk.pn - chk["ling.pronoun_to_noun_ratio"]) < 1e-6).mean()) if len(chk) else float("nan")
            blk = {"n_recordings": int(len(d)),
                   "n_participants": int(d.participant_id.nunique()),
                   "n_impaired": int((d.label == 1).sum()),
                   "sanity_pn_reproduces_committed_feature": round(agree, 4),
                   "auc": boot(d, COLS)}
            blk["convergent_spearman_rdi_free_vs_pn"] = {
                "within_controls": round(spearman(d[d.label == 0].rdi_free, d[d.label == 0].pn), 4),
                "within_impaired": round(spearman(d[d.label == 1].rdi_free, d[d.label == 1].pn), 4)}
            blk["means"] = {c: {"healthy": round(float(d[d.label == 0][c].mean()), 4),
                                "impaired": round(float(d[d.label == 1][c].mean()), 4)}
                            for c in COLS}
            if cohort == "pitt" and os.path.exists("results/pitt_cookie/matched_mask.npy"):
                m = np.load("results/pitt_cookie/matched_mask.npy")
                mf = pd.read_csv("results/pitt_cookie/meta.csv").loc[m, "file_id"]
                dm = d[d.file_id.isin(set(mf))]
                blk["matched_subset"] = {"n": int(len(dm)), "auc": boot(dm, COLS)}
            out["cohorts"][cohort] = blk
        with open("results/reconstruction/rdi_english_probe.json", "w") as f:
            json.dump(out, f, indent=2)
        print(json.dumps(out, indent=2)[:4000])
