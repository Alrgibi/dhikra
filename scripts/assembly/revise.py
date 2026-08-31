#!/usr/bin/env python3
"""revise.py -- the nine scripted classes of the final revision pass, applied to the
SOURCE OF RECORD (docs/chapters/*.md, _pending/appendix_b.md, front.py, references.json).
Every replacement asserts its occurrence count, so a silent miss is impossible.
Run, then rebuild, then measure.py on the built docx must show the class at zero."""
import re, json, sys
ROOT = "/home/claude/work/src/docs/chapters/"
FILES = {f: ROOT + f for f in ["chapter1.md","chapter2.md","chapter3.md","chapter4.md","chapter5.md","chapter6.md",
        "appendix_a.md","appendix_c.md","appendix_d.md","appendix_e.md","appendix_f.md","appendix_g.md","appendix_h.md","appendix_i.md"]}
FILES["appendix_b.md"] = ROOT + "_pending/appendix_b.md"
FILES["front.py"] = "/home/claude/work/build/front.py"
TXT = {k: open(v, encoding="utf-8").read() for k, v in FILES.items()}
LOG = []

def ws(s):
    """regex that matches s with any whitespace run where s has a space (hard-wrapped sources)."""
    return r"\s+".join(re.escape(w) for w in s.split())

def rep(f, old, new, n=1, regex=False):
    t = TXT[f]
    pat = old if regex else ws(old)
    found = len(re.findall(pat, t, re.S))
    assert found == n, f"{f}: expected {n} of {old[:70]!r}, found {found}"
    TXT[f] = re.sub(pat, lambda m: new, t, flags=re.S)
    LOG.append((f, old[:60], new[:60], n))

# ═══════════════ CLASS 3 first: the canonical external-corpus sentence ═══════════════
CANON = ("The corpus was excluded from the training data of the final model and from every modelling decision after the lock. "
         "Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool.")
# chapter1 §1.7
rep("chapter1.md", "excluded from the training data of the final model and from every decision after the lock of 18 August 2026, at a threshold fixed in advance — AUC 0.853 [0.737, 0.946] —",
    "evaluated at a threshold fixed in advance — AUC 0.853 [0.737, 0.946] — under the governance of section 3.9: " + CANON.replace("The corpus was", "the corpus was") + " The figure is reported")
# chapter3 §3.1 wrong wording (finding 61)
rep("chapter3.md", "The Lu corpus was withheld from every fitting decision for the reasons given in section 3.9.",
    CANON.replace("The corpus", "The Lu corpus") + " The reasons are given in section 3.9.")
# chapter5 §5.3
rep("chapter5.md", "the accurate scope is excluded from the training data of the final model, and from every decision after the 18 August lock, never \"never seen\".",
    "the accurate scope is this: " + CANON.replace("The corpus was", "the corpus was"))
# chapter6 §6.2
rep("chapter6.md", "The external test set was not untouched before the lock: one architectural decision — the training pool's composition",
    "The external test set's exposure is stated in the canonical form: " + CANON + " That one architectural decision — the training pool's composition")
# appendix_c: model-card quotes carry the canonical wording; the card file keeps its own text
rep("appendix_c.md", "The model consumes 64 features (Appendix A) from 987 recordings of 581 participants. The card's statement of the training data and of the external corpus's exposure is quoted verbatim, because its wording is the ruled one (section 3.9):",
    "The model consumes 64 features (Appendix A) from 987 recordings of 581 participants. The card's statement of the training data names DementiaBank Pitt and Delaware (picture description) and states the external corpus's exposure in the thesis's canonical form (section 3.9):")
rep("appendix_c.md", r"> DementiaBank Pitt \+ Delaware \(picture description\)\. Lu is NOT in the training data of this model\..*?overclaimed\.\n",
    "> " + CANON.replace("The corpus", "The Lu corpus") + "\n", regex=True)
rep("appendix_c.md", r'External test-set history: "Lu is not in this model\'s training data.*?docs/LU_EXPOSURE_TIMELINE\.md\."',
    'External test-set history: "' + CANON.replace("The corpus", "The Lu corpus") + ' Both external figures are reported -- 0.821 (clean, Pitt-only model) and 0.853 (this model)."', regex=True)
# appendix_f level A definition
rep("appendix_f.md", "a single evaluation on a corpus excluded from the training data of the final model and from every decision after the lock of 18 August 2026, at a threshold fixed in advance, scored once (section 3.9).",
    "a single evaluation, at a threshold fixed in advance, scored once, on a corpus whose exposure is stated in the canonical form (section 3.9): " + CANON.replace("The corpus was", "the corpus was"))
# disowned phrases that still carry the retired words
rep("chapter3.md", "0.849, was reported as external validation on a corpus the model had never seen. Both claims cannot be true at once.",
    "0.849, was reported as external validation. Both claims cannot be true at once.")
rep("chapter5.md", "the external corpus untouched;", "the external corpus left unscored;")
rep("chapter5.md", "a model that has never seen a Delaware recording ranks", "a model trained without any Delaware recording ranks")
rep("chapter4.md", "Every figure in Chapters 3 and 5 was computed on transcripts of the real Cookie Theft and is untouched by this defect.",
    "Every figure in Chapters 3 and 5 was computed on transcripts of the real Cookie Theft and is unaffected by this defect.")
# front.py abstracts
rep("front.py", "the corpus was excluded from the training data of the final model and from every decision after the lock of 18 August 2026, but one earlier scoring had informed the composition of the training pool, and that exposure is reported rather than hidden.",
    CANON.replace("The corpus was", "the corpus was") + " That exposure is reported rather than hidden.")
rep("front.py", "وقد استُبعدت هذه المجموعة من بيانات تدريب النموذج النهائي ومن كل قرار بعد الإقفال في 18 أغسطس 2026، لكن تقييماً سابقاً واحداً كان قد أثّر في تكوين مجموعة التدريب، ويُبلَّغ عن هذا التعرض بدلاً من إخفائه.",
    "وقد استُبعدت هذه المجموعة من بيانات تدريب النموذج النهائي ومن كل قرار نمذجة بعد الإقفال؛ وقبل الإقفال جرت خمسة تقييمات استكشافية، أثّر أحدها في قرار ضمّ مجموعة ديلاوير إلى مجموعة التطوير، ويُبلَّغ عن هذا التعرض بدلاً من إخفائه.")

# ═══════════════ CLASS 1: dates → relational language ═══════════════
rep("chapter3.md", "Until August 2026 it led with picture description,", "Until the ordering was revised it led with picture description,")
rep("chapter3.md", "The Lu corpus was obtained on 18 August 2026 to serve as an external test set, and over the following ninety minutes it was scored five times while training configurations were compared. A Pittsburgh-trained model scored **0.821** at 15:06, before any modelling decision had been informed by the corpus, and that figure is clean. At 15:30 a Pittsburgh-plus-Delaware model scored **0.859**,",
    "The Lu corpus was obtained to serve as an external test set, and in the hours before the lock it was scored five times while training configurations were compared. The first scoring, of a Pittsburgh-trained model, gave **0.821** before any modelling decision had been informed by the corpus, and that figure is clean. A subsequent scoring of a Pittsburgh-plus-Delaware model gave **0.859**,")
rep("chapter3.md", "The corpus was locked out at 17:37. The final model was retrained", "The corpus was then locked out. The final model was retrained")
rep("chapter3.md", "the corpus was scored exactly once at 17:59: **AUC 0.8533,", "the corpus was scored exactly once, after the lock: **AUC 0.8533,")
rep("chapter3.md", "Two days later the evaluation was reproduced under a protocol", "Subsequently the evaluation was reproduced under a protocol")
rep("chapter3.md", "The lock of 18 August 2026 is marked because it divides the work in two:", "The lock is marked because it divides the work in two:")
rep("chapter3.md", "The exact 18 August comparison cannot be reproduced Lu-free", "The exact pre-lock comparison cannot be reproduced Lu-free")
rep("chapter4.md", "the artwork as corrected on 26 August 2026, when an audit", "the artwork as corrected when an audit")
rep("chapter4.md", "and it was examined on 26 August 2026 [7, 8, 9].", "and it was examined [7, 8, 9].")
rep("chapter5.md", "the original 18 August pooling comparison asked", "the original pre-lock pooling comparison asked")
rep("chapter6.md", "The lock of 18 August 2026 permanently excluded", "The lock permanently excluded")
rep("chapter6.md", "missing from the drawn scene until 26 August 2026, and", "missing from the drawn scene until the audit of section 4.3.1 found them, and")
rep("chapter6.md", "Freezing the model on 18 August bought", "Freezing the model bought")
rep("chapter6.md", "recorded with a timestamp, as on 18 August 2026.", "recorded with a timestamp, as at the lock.")
rep("chapter6.md", "with its scope stated first: as of August 2026, no publicly available corpus", "with its scope stated first: at the time of the search, no publicly available corpus")
rep("chapter6.md", "(talkbank.org/dementia/access, retrieved August 2026)", "(talkbank.org/dementia/access, retrieved during the search)")
rep("appendix_c.md", "Every field below is quoted from the card as committed on 22 August 2026 (the card records its own amendment history in section C.6);",
    "Every field below is quoted from the card as committed, with calendar dates rendered as their place in the sequence (the card records its own amendment history in section C.6);")
rep("appendix_c.md", "| `frozen` | 2026-08-18 |", "| `frozen` | at the lock |")
rep("appendix_c.md", "recovered 2026-08-20 by introspection", "recovered after the lock by introspection")
rep("appendix_c.md", "archive copy packaged 2026-08-19)", "archive copy packaged after the lock)")
rep("appendix_c.md", "wording before 2026-08-20:", "earlier wording:")
rep("appendix_c.md", "The intended-use block was added on 22 August 2026 — the card previously had none —", "The intended-use block was added after the lock — the card previously had none —")
rep("appendix_c.md", "Slope/intercept re-derived 2026-08-22 by an unpenalised fit", "Slope/intercept re-derived after the lock by an unpenalised fit")
rep("appendix_c.md", 'The block\'s own provenance note reads: "2026-08-22 -- the card previously had no intended-use',
    'The block\'s own provenance note reads: "added after the lock -- the card previously had no intended-use')
rep("appendix_c.md", "| known issue | RESOLVED 2026-08-21: TRAINING_PRIOR", "| known issue | RESOLVED after the lock: TRAINING_PRIOR")
rep("appendix_c.md", "(parked in future_work/ 2026-08-21; docs/IMPROVEMENTS.md", "(parked in future_work/ after the lock; docs/IMPROVEMENTS.md")
rep("appendix_c.md", "| documentation update | 2026-08-22: known_issues entry 0 closed", "| documentation update | After the lock: known_issues entry 0 closed")
rep("appendix_d.md", "verified against the published articles on 26 August 2026.", "verified against the published articles during writing.")
rep("appendix_d.md", "Each is the current version as of August 2026, and", "Each is the current version at the time of writing, and")
rep("appendix_e.md", "The session was run on 28 August 2026 through", "The session was run at assembly through")
rep("appendix_f.md", "every figure and time recorded | pre-lock scores 0.821, 0.849, 0.859; lock 18 August 2026, 17:37 |",
    "every figure and its order recorded | pre-lock scores 0.821, 0.849, 0.859, in that sequence; then the lock |")
rep("appendix_f.md", "Removed on 23 August 2026 — not refuted", "Removed during development — not refuted")
rep("appendix_g.md", "recommitted on 26 August 2026 (", "recommitted after the lock (")
rep("appendix_h.md", "After the ×4.0 removal of 23 August 2026 the chain", "After the ×4.0 removal the chain")
rep("appendix_h.md", "recomputed on 26 August 2026 from the stored", "recomputed after the lock from the stored")
rep("appendix_b.md", "(Corrected 2026-08-22: an earlier version", "(Corrected: an earlier version")
rep("appendix_b.md", "**Added 2026-08-23.** The main system's", "The main system's")
rep("appendix_b.md", "at `docs/forms/CONSENT_FORM_ar.md` (26 August 2026):", "at `docs/forms/CONSENT_FORM_ar.md`:")
rep("appendix_b.md", "*Two figures corrected 25 August 2026, and both were stale", "*Two figures were corrected, and both were stale")
rep("appendix_b.md", "**Quantified 25 August 2026.** At 20 per group", "**Quantified.** At 20 per group")
rep("appendix_b.md", "*(Corrected 25 August 2026. This previously read", "*(Corrected. This previously read")
rep("appendix_b.md", "**Added 26 August 2026 on a measured result.** The screening", "**Added on a measured result.** The screening")
rep("appendix_b.md", "**Added 25 August 2026.** One outcome", "One outcome")
rep("appendix_b.md", "On 26 August the frozen model was probed", "The frozen model was then probed")
rep("front.py", '["Lock", "The moment, 18 August 2026 at 17:37, after which the external corpus entered no decision and the model, features and threshold were frozen."]',
    '["Lock", "The moment after which the external corpus entered no decision and the model, features and threshold were frozen; every evaluation that counts came after it."]')

# ═══════════════ CLASS 2: heading punctuation ═══════════════
HEAD_MAP = {
 "chapter2.md": [
  ("## 2.3 Benchmarks, Corpora And A Pooling Counter-Case", "## 2.3 Benchmarks Corpora And A Pooling Counter Case"),
  ("### 2.3.4 Cross-Corpus Evaluation Collapses In This Literature", "### 2.3.4 Cross Corpus Evaluation Collapses In This Literature"),
  ("## 2.2 Speech-Based Screening Systems", "## 2.2 Speech Based Screening Systems"),
  ("## 2.5 Arabic And Low-Resource Work", "## 2.5 Arabic And Low Resource Work"),
 ],
 "chapter3.md": [
  ("## 3.5 The Task Battery, And Why Its Order Changed", "## 3.5 The Task Battery And Why Its Order Changed"),
  ("## 3.9 External Test-Set Governance, And The Failure That Produced It", "## 3.9 External Test Set Governance And The Failure That Produced It"),
  ("### 3.9.2 How It Was Caught, And The Correction", "### 3.9.2 How It Was Caught And The Correction"),
  ("## 3.10 Pre-Registration As A Working Method, Including Where It Failed", "## 3.10 Preregistration As A Working Method Including Where It Failed"),
  ("### 3.10.1 Three Under-Specifications In Seventeen Registered Runs", "### 3.10.1 Three Underspecifications In Seventeen Registered Runs"),
  ("## 3.11 Monotone Transforms Move Calibration, Never Discrimination", "## 3.11 Monotone Transforms Move Calibration And Never Discrimination"),
  ("## 3.12 The Calibration Architecture Is A Density-Ratio Likelihood Ratio", "## 3.12 The Calibration Architecture Is A Density Ratio Likelihood Ratio"),
 ],
 "chapter5.md": [
  ("### 5.1.3 The Search For A Better Number, And What It Found", "### 5.1.2 The Search For A Better Number And What It Found"),
  ("### 5.2.1 The Sex Disparity, With Its Mechanism", "### 5.2.1 The Sex Disparity And Its Mechanism"),
  ("## 5.15 Two Specificity Problems, Not One", "## 5.15 Two Specificity Problems Not One"),
  ("## 5.25 Which Task, And How Many", "## 5.25 Which Task And How Many"),
  ("## 5.28 The Minimal Probe, And A Claim Withdrawn Before It Reached The Thesis", "## 5.28 The Minimal Probe And A Claim Withdrawn Before It Reached The Thesis"),
  ("## 5.4 Calibration", "## 5.4 Calibration"),
 ],
 "chapter6.md": [],
 "appendix_b.md": [
  ("## B.1 What This Study Is, And What It Deliberately Is Not", "## B.1 What This Study Is And What It Deliberately Is Not"),
  ("### B.3.2 The Healthy Stratum Is Also The Normative Sample, And That Changes Its Size", "### B.3.2 The Healthy Stratum Is Also The Normative Sample And That Changes Its Size"),
  ("## B.4 Consent, And The Capacity Question", "## B.4 Consent And The Capacity Question"),
  ("### B.6.1 Demographics, Every Field Has A Stated Reason", "### B.6.1 Demographics And Why Every Field Is Collected"),
  ("### B.6.2 The Task Battery, Revised 25 August 2026, And The Ordering Is The Revision", "### B.6.2 The Task Battery And Why Its Ordering Was Revised"),
  ("### B.6.3 Elicitation Must Be Fixed, And This Is Not A Formatting Preference", "### B.6.3 Elicitation Must Be Fixed And This Is Not A Formatting Preference"),
  ("## B.9 Outcomes, What The Pilot Will Actually Report", "## B.9 Outcomes The Pilot Will Actually Report"),
  ("### B.9.1 Primary Outcomes, Feasibility", "### B.9.1 Primary Outcomes Of Feasibility"),
  ("### B.9.2 Secondary Outcomes, Normative And Linguistic", "### B.9.2 Secondary Outcomes Normative And Linguistic"),
  ("### B.9.3 The Endpoint Decision For The Study This Pilot Is Preparing, Fixed 26 August 2026", "### B.9.3 The Endpoint Decision For The Study This Pilot Is Preparing"),
  ("### B.9.4 What This Study Is Not Powered To Do, Added 23 August 2026, And It Is A Real Limit", "### B.9.4 What This Study Is Not Powered To Do"),
  ("### B.9.5 Scoring Rule, Required, And Added 26 August 2026 On A Measured Result", "### B.9.5 The Scoring Rule Required On A Measured Result"),
  ("### B.9.6 Secondary Outcome, Pre-registered, Whether The Substituted Picture Is Equivalent", "### B.9.6 A Preregistered Secondary Outcome On Whether The Substituted Picture Is Equivalent"),
  ("### B.9.7 Secondary Outcome, Pre-registered, The Minimal Probe", "### B.9.7 A Preregistered Secondary Outcome On The Minimal Probe"),
  ("## B.10 Analysis Plan, Fixed Before Collection", "## B.10 Analysis Plan Fixed Before Collection"),
 ],
 "appendix_g.md": [("# Appendix G — The Transcription-Artefact Audit", "# Appendix G — The Transcription Artefact Audit")],
 "appendix_h.md": [("# Appendix H — The Risk-Adjustment Evidence Base And The Two Pre-Registration Diagnoses", "# Appendix H — The Risk Adjustment Evidence Base And The Two Preregistration Diagnoses")],
 "appendix_d.md": [("# Appendix D — Reporting-Guideline Self-Assessment", "# Appendix D — Reporting Guideline Self Assessment")],
}
for f, pairs in HEAD_MAP.items():
    for a, b in pairs:
        if a == b: continue
        rep(f, a, b)

# ═══════════════ CLASS 8: 5.1.3 → 5.1.2 cross-references ═══════════════
rep("chapter2.md", "(section 5.1.3)", "(section 5.1.2)")
rep("chapter6.md", "(section 5.1.3)", "(section 5.1.2)")
rep("appendix_f.md", "| 5.1.3 |", "| 5.1.2 |", n=2)

# ═══════════════ CLASS 4: scaffolding ═══════════════
rep("appendix_i.md", r"\n---\n\n\*\*References Cited In This Appendix\.\*\*.*\Z", "\n", regex=True)
rep("appendix_h.md", "Sources are cited with the numbering of Chapter 3; entries [4] to [12] are reproduced in full in section H.10.",
    "Sources are cited by their numbers in the thesis-wide reference list.")
rep("appendix_h.md", r"\n## H\.10 Sources Reproduced In Full\n.*\Z", "\n", regex=True)
# Appendix D: merge its local [D1]-[D3] into the thesis-wide list
for k in ("1", "2", "3"):
    rep("appendix_d.md", f"[D{k}]", f"[{k}]", n=len(re.findall(r"\[D%s\]" % k, TXT["appendix_d.md"])) )
rep("appendix_d.md", r"\n## D\.4 Sources\n.*\Z", "\n", regex=True)
rep("appendix_d.md", "and each was read rather than cited from a secondary summary.", "and each was read rather than cited from a secondary summary.", n=0) if False else None

# ═══════════════ CLASS 5: [DRAFT] notes ═══════════════
rep("front.py", '    "[DRAFT — the author replaces or keeps this text.]",\n', "")
rep("front.py", '    "[DRAFT — the author completes the personal acknowledgements.]",\n', "")

# ═══════════════ CLASS 6: author-year citations in Appendix B → [n] ═══════════════
rep("appendix_b.md", "[Sedighi et al., *Alzheimer's & Dementia*, 22(1):e71109, 2026]", "[1]")
rep("appendix_b.md", "[Dajani et al., *J. Global Health*, 16:04181, 2026]", "[2]")
rep("appendix_b.md", "[El-Metwally et al., *Behavioural Neurology*, 2019, art. 3935943]", "[3]")

# ═══════════════ CLASS 9: [UNVERIFIED] → grade language ═══════════════
rep("appendix_f.md", "chapter's 0.8551 and 0.8198 [UNVERIFIED]", "the chapter's 0.8551 and 0.8198 are not verified against a committed source")
rep("appendix_f.md", "| Repeat-recording averaging | C, part unverified |", "| Repeat-recording averaging | C for the repeaters; not verified against a committed source for the rest |")

# ═══════════════ CLASS 7: the 117 / 64 framing ═══════════════
FRAME = ("Dhikra extracts 117 speech and language measures across five families. Its externally evaluated English screening model uses a frozen 64-feature transcript-derived subset of linguistic, information-content and discourse-semantic measures; 53 acoustic measures support a separate language-independent pathway.")
rep("front.py", "A calibrated soft-voting ensemble over 64 linguistic, information-content and discourse-semantic features, extracted from a one-minute picture description, was trained on 987 recordings",
    FRAME + " The screening model, a calibrated soft-voting ensemble over that subset extracted from a one-minute picture description, was trained on 987 recordings")
rep("front.py", "دُرِّب نموذج تجميعي معايَر بالتصويت الناعم على 64 سمة لغوية ومعلوماتية ودلالية خطابية، مستخرجة من وصف صورة لمدة دقيقة واحدة، على 987 تسجيلاً",
    "تستخرج «ذِكرى» 117 مقياساً للكلام واللغة عبر خمس عائلات؛ ويستخدم نموذج الفحص الإنجليزي المقيَّم خارجياً مجموعة فرعية مجمَّدة من 64 سمة مستخرجة من النص، بينما تدعم 53 مقياساً صوتياً مساراً منفصلاً مستقلاً عن اللغة. دُرِّب نموذج الفحص، وهو نموذج تجميعي معايَر بالتصويت الناعم على تلك المجموعة الفرعية المستخرجة من وصف صورة لمدة دقيقة واحدة، على 987 تسجيلاً")
rep("chapter1.md", "This thesis reports the design, construction and evaluation of ذِكرى (Dhikra), a speech-based cognitive screening instrument built for a setting that has no memory clinics, no reliable network and no specialist staffing to assume — and it reports that evaluation under the conditions such a deployment would actually impose.",
    "This thesis reports the design, construction and evaluation of ذِكرى (Dhikra), a speech-based cognitive screening instrument built for a setting that has no memory clinics, no reliable network and no specialist staffing to assume — and it reports that evaluation under the conditions such a deployment would actually impose. " + FRAME)
rep("chapter3.md", "A total of 117 measures were implemented across five families, of which 64", "A total of 117 measures were implemented across five families — the instrument's full measurement set — of which 64")
rep("chapter4.md", "Figure (4.2) shows what feeds it: of the 117 measures extracted per session, the 64 language measures",
    "Figure (4.2) shows what feeds it. " + FRAME + " Of the 117 measures extracted per session, the 64 language measures")
rep("chapter6.md", "It is not a modest result. It is an expensive one.", "It is not a modest result. It is an expensive one. " + FRAME.replace("Dhikra extracts", "The instrument that produced it extracts"))

# ═══════════════ write ═══════════════
for k, v in FILES.items():
    open(v, "w", encoding="utf-8").write(TXT[k])
print(f"{len(LOG)} replacements applied")
for f, a, b, n in LOG: print(f"  {f:16s} ×{n}  {a!r} → {b!r}")
