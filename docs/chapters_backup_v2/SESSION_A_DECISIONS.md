# Decisions for Session A — paste this back into that session

**26 August 2026.** Every claim in the session's report was checked against the
files before these decisions were made. Verified findings are marked; two items
were understated and one new finding sits underneath item 1.

---

## 0. Run this first, before anything else

```
bash scripts/setup_env.sh
```

**`$HOME` is ephemeral. The project mount is not.** The pinned environment at
`$HOME/dhenv` was built on 19 August and does not exist in any later session,
which is why that session found it missing — the repository is fine, the machine
is new. `setup_env.sh` rebuilds it, and it is **idempotent and resumable**: the
45-second limit will cut the install off part way, so run it again until it
prints `READY`. Its acceptance test is not that packages imported but that
**`models/dhikra_model.pkl` loads with 64 features and threshold 0.367**, which
is the only thing the environment exists to do.

**Do not create a virtual environment inside the project folder.** The mount
reports **100% used with about 685 MB free**, and scikit-learn, pandas, scipy and
matplotlib together exceed that. This was tested; the venv was created, could not
be completed, and has been moved to `docs/chapters/_tmp/dead_venv`.

---

## 1. The pooled calibration slope — APPROVED, and it is worse than reported

**Verified.** `CURRENT_development_stats.json` gives `calibration.slope`
= 1.2763890437 and `intercept` = 0.1347897983.
`recalibration_decision.json` gives `development_pooled.raw.slope` = 1.2887 and
`intercept` = 0.1376. Two computations of the same nominal quantity, both live.

**The Chapter 3 fix is approved as proposed:** drop the pooled figure from
§3.9.0. The argument there is that 1.516 and 0.823 point in opposite directions;
the pooled average is decoration and its removal costs nothing.

**What the report understated.** The figure register says `fig_calibration.png`
shows *slope 1.289, intercept 0.138*. Those round from **1.2887 / 0.1376** —
the recalibration file — not from NUMBERS.md's 1.2764 / 0.1348. So Chapter 5 is
currently set up to print one number in its text beside a figure drawn from the
other. Log it for Session B as a **blocking item for §5.4**, not an advisory one.

---

## 2. NEW FINDING, and it is larger: nine of twenty figures have no generator

`THESIS_PLAN.md` states *"Generators, all committed"*. **That claim is false.**
No script in `scripts/` names any of these nine figures:

`fig_architecture` · `fig_calibration` · `fig_corpus_effect` · `fig_decision_curve`
· `fig_effect_sizes` · `fig_feature_flow` · `fig_roc` · `fig_score_distributions`
· `fig_sens_spec_tradeoff`

They exist as PNGs whose producing code was never committed. Three of them are
placed by chapters already written or about to be: `fig_corpus_effect` is
Chapter 3's Figure 3.2, and `fig_architecture` and `fig_feature_flow` are
Chapter 4's. **If any number changes, none of them can be redrawn.**

**Decision, and it is deliberately partial.** Reconstruct **`fig_calibration.png`
only**, because it is the one where a figure and a text number are in tension and
§5.4 cannot be written honestly until it is known which source the committed PNG
was drawn from. That is a **reproduction, not a new analysis**: the registered
criterion is *which committed source does the existing PNG match*, and the answer
resolves the pair by looking rather than by choosing. **Declare the other eight**
in the figure-provenance note, alongside the eight already-disclosed uncommitted
code files. Redrawing eight correct figures before 1 September buys nothing.

Correct the plan's *"Generators, all committed"* to name the eleven that have
one and the nine that do not. That is a Kind 2 correction, recorded as one.

---

## 3. The DementiaBank claim and the eight unused corpora — APPROVED

Both correct. *"All from DementiaBank"* is false: the Arabic pilot is not a
DementiaBank corpus, and that absence is the Chapter 6 argument. Fix the sentence
and use the proposed honest rationale for the eight unused corpora — the design
required picture description with diagnostic labels at scale, Pitt and Delaware
are the two largest such corpora, Lu the third suitable as an external test, and
**the remaining eight were obtained and not audited individually**. Log the gap
as a gap; do not invent per-corpus reasons.

---

## 4. The three uncommitted number clusters — option (ii), NOT (i)

**Recompute them.** The reasoning that made option (i) look right does not hold:
this is not a new analysis, it is **provenance recovery**, and its criterion is
pre-registered by construction — *reproduce the reported value to the stated
precision, or report the discrepancy*. That is the same pattern as the locked
corpus's one-shot reproduction. The environment to do it now exists (§0).

Three small scripts, each writing a committed result file:

1. The external-corpus artefact count — eight forms, rates 0.065 / 0.220. **This
   one was declared descriptive when first run**, so recomputing it changes
   nothing about the lock.
2. The feature-health audit — missingness 0.012 / 0.0002, 99.3%, 81.8%, AUC
   0.5075.
3. The age-flatness block — 0.6308, −0.084 (*p* = 0.054), +0.025, −0.0070 per
   year, LR × 0.87, +0.091. **Frozen model, development data, no refit.**

**Report-and-stop applies.** If any figure does not reproduce, that is a finding:
report it, correct the prose to the reproduced value, log it, and **do not chase
it**. Three uncited number clusters becoming three committed files is worth an
hour; a debugging expedition four days before the deadline is not.

---

## 5. Missing plan-required content — APPROVED

All of it: §3.9.7's Lu-free pooling re-examination, §3.12's Consequence 4, §3.7's
two structural points, the bootstrap-units caveat in §3.6, "Craft Story" named in
§3.5, and references [2] and [3] carried by the 23-unit inventory sentence.

---

## 6. The extended cut list — APPROVED

The arithmetic is better than the handover's and supersedes it. Cut where
proposed. **No claim leaves the thesis; each moves to an appendix.**

---

## 7. Appendix lettering — collision confirmed, but take the smaller fix

**Verified register:** A features · B pilot protocol · C model card ·
D reporting-guideline self-assessment · E sample report · F levels of evidence.
The kickoff assigned C and D to the new appendices, which was my error.

**Do not reletter six appendices. Give the two new ones G and H.** The faculty
specification requires only that each appendix sit on its own page and appear in
the contents index — **it does not require citation order**, and the register
already fails that test anyway. G and H changes two words in one chapter; the
proposed relettering changes the meaning of four letters across three documents
and risks the three cross-references to F for no gain.

- **G — the transcription-artefact audit**
- **H — the risk-adjustment evidence base and the two pre-registration diagnoses**

The plan's register gains two rows; nothing existing moves.

**And a third appendix is unwritten.** The register's **Appendix D**, the
STARD-AI / TRIPOD+AI / PROBAST+AI self-assessment, is marked in the plan as
*"STILL NOT WRITTEN, and it is the largest remaining gap in the appendices"*,
budgeted at two hours of assembly rather than new work. **Write it in this
session** if there is room: Session A is the only one that will have §3.9 and
§3.10 fully loaded, and that is exactly where the STARD-AI governance items come
from. If the session is already long, say so and it moves to Session C.

The register's three Chapter-3 tables the draft omitted — age-band prevalence,
multipliers, Bayes property checks — go into **Appendix H**, as proposed. Adding
them to a chapter already over length would be perverse.

---

## 8. Format — APPROVED, with one caution

**Verified**, faculty specification: *"One numbering scheme only. No heading is
left unnumbered."* The unnumbered Overview violates it. **The proposed fix is
better than the one it replaces**: delete the heading and run those paragraphs as
chapter-opening text. It satisfies the specification, cures the adjacent-headings
problem after the chapter title, and keeps the numbering rationale of finding 7
intact. Apply the same pattern to Chapters 4, 5, 6, 2 and 1.

Title Case headings and no colons in headings: approved, including retitling
§3.11 without losing its claim. Citations to paragraph ends: approved. Moving
Figure 3.2's reference to §3.2.1, where the 0.930 measurement lives: approved and
a good catch.

**The caution.** `WRITING_BRIEF.md` records that a fourth-level heading is a
**bold unnumbered heading**, taken from the exemplar. That contradicts the
specification, and **the specification wins**. But do not over-apply it: a bold
sentence opening a paragraph — *"A pre-registered check caught the analyst's own
bug."* — is not a heading and must not be stripped. Strip standalone bold lines
that function as headings; keep bold lead-ins that begin a paragraph of prose.

---

## What is not approved

Nothing. Every item was either approved as proposed or approved with a smaller
fix. **Item 1 was under-stated, item 7 was over-engineered, and the report missed
the missing figure generators** — but it found four real defects in a draft
another session had already run preflight over, which is the whole reason the
verification pass exists.
