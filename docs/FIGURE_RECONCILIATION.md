# FIGURE_RECONCILIATION.md — one table per multi-valued figure

**Date:** 21 August 2026 · **Dataset state:** post-Lu-lock (development pool =
Pitt cookie 548 + Delaware cookie 439 = 987 recordings, 581 participants; Lu
spent once as the locked external test and since reproduced, tombstone in
place).

**Purpose.** Several quantities in this project exist in more than one version,
because pools, cohorts, feature sets, model forms and the Lu lock changed
during development. Each table below lists every variant of one figure, states
exactly what it was computed on, and says which version is citable. An
examiner who finds two versions of a number should find the difference
explained here, not discover it.

**The rule.** A figure is citable only if (a) it lives in a current result
file (not `results/_superseded/`, not a HANDOFF §5 stale file), (b) its pool
respects the Lu lock or predates any Lu involvement, and (c) its producer is
either a committed script or a deployed artifact whose configuration has been
recovered and stated. Anything else is context, quoted only with its status.

---

## A. Acoustic-only AUC — 0.708 vs 0.63–0.69 vs 0.728

| Figure | Where it lives | Pool / cohort | Features | Model form | Lock state | Citable? |
|---|---|---|---|---|---|---|
| **0.708** (0.7079222720478326) | `models/dhikra_acoustic_model.pkl`, embedded metadata | Pitt cookie, **age/sex-matched** subset of the audio-available recordings: **n = 373** (`multimodal_mask.npy`: 518 with audio → 373 matched) | **27** ac.* — the 53 minus all 26 MFCC mean/sd (dropped as uninterpretable; transcript 2026-08-16) | `CalibratedClassifierCV(method='sigmoid', cv=5)` over impute→scale→`RandomForestClassifier(500, min_samples_leaf=2, class_weight='balanced', max_features='sqrt', random_state=42)` — **recovered by artifact introspection 2026-08-21**; trainer script uncommitted (audit item 9) | Built 2026-08-16, pre-lock by date, but **Pitt-only — Lu never involved** | **Yes — VERIFIED 2026-08-22**: after the Pitt audio re-download, the pre-registered signature test reproduced the embedded figure under the hypothesised protocol (StratifiedGroupKFold(5, shuffle, rs=42), matched-373): OOF AUC 0.7078624813, Δ −6.0×10⁻⁵, grade MATCH (`results/reconstruction/acoustic_regen_verification.json`). **UPDATE 2026-08-23:** the signature test has been promoted into committed code (`scripts/acoustic_signature_test.py`) and re-run from there, reproducing 0.7078624813 against the embedded 0.7079222720478326, Δ = −6.0×10⁻⁵, grade MATCH (`results/reconstruction/acoustic_signature_test.json`). Cite it as: the ORIGINAL TRAINER is uncommitted and unrecoverable, but the configuration is recovered, the protocol is confirmed, and the figure reproduces from a fresh fit run by committed code. Do NOT write "reproducible from stored outputs only" — that was inaccurate. |
| **0.63–0.69** (0.6254–0.6921 across ten seeds, mean 0.665; the seed-1 value 0.6563 also appears in `modality_comparison.csv`) | `results/pitt_cookie/matching_stability.csv` (`auc_acoustic`), `modality_comparison.csv` | Ten re-drawn age/sex-matched cohorts, 368–381 recordings each | 53 ac.* | **Unknown code** — no committed script writes these files (audit item 11) | Pre-lock, Pitt-only | **Context only** — cite as the matched-cohort stability observation, producer gap stated; never as a headline. |
| **0.728** (0.7282, CI 0.667–0.761) | `results/fusion/results.json` → `acoustic_only` | Pitt cookie, **all 518 recordings with audio, unmatched** — the age confound is **not** controlled in this number | 53 ac.* | Uncalibrated soft-voting ensemble local to `fusion_experiments.py` (ExtraTrees 400 + GradientBoosting 150 + RandomForest 400), mean over seeds 42/7/123, `StratifiedGroupKFold(5)` by participant | **Post-lock, Lu-free** (rerun 2026-08-18 17:54; the script's own governance note records why) | **Yes — VERIFIED end-to-end 2026-08-22**: audio re-downloaded, `features_multimodal.csv` regenerated (518 rows; matched mask bit-identical to the original), and the fold-chunked rerun reproduced acoustic_only within Δ −1.5×10⁻⁴ (linguistic_only bit-faithful at Δ 0.0). One caveat stands: the pool is unmatched. `results/reconstruction/acoustic_regen_verification.json`. |

**Why they differ.** Pool (matched 373 vs unmatched 518), feature set (27 vs
53), model form (calibrated RF vs uncalibrated voters), and per-seed matching
variance. They are three different measurements, not three attempts at one.
Consistency check: on the same seed-1 matched set, the 53-feature acoustic arm
scored 0.6563 (`modality_comparison.csv`), inside the ten-seed band.

**For the claim "an acoustic-only model performs above chance without touching
words":** 0.728's CI (0.667–0.761) excludes chance but comes from the
unmatched pool; the matched figures (0.63–0.69, and the artifact's 0.708) are
the confound-controlled ones. State the claim on 0.728 with the unmatched
caveat, or on the artifact's 0.708 with the trainer caveat — never on either
number bare. (Whether to re-download audio and verify the chain end-to-end is
an open owner decision.)

---

## B. Age-alone AUC — 0.7074 vs 0.5149 vs (0.71/0.46) vs 0.6230 vs 0.5571

| Figure | Where it lives | Pool / cohort | Model form | Lock state | Citable? |
|---|---|---|---|---|---|
| **0.7074** (0.7073728671796587) | `results/reconstruction/age_leakage_evidence.json` → `A1_age_only_raw_pitt_548` | Raw, **unmatched** Pitt cookie, 548 recordings — the dementia group averages ~6.6 years older | Age as the only feature, `analyze_pitt.py` §4 LogReg pipeline, `StratifiedGroupKFold(5, shuffle, rs=42)` | **Post-lock regeneration** (2026-08-22, `_bootstrap/ageleak_driver.py`); Pitt-only, Lu never involved | **Yes — the citable raw-Pitt age figure.** Quote with 0.5149 (matched) and 0.7983 (speech); the trio is one demonstration. |
| **0.5149** (0.5149468123081317) | Same file → `A2_age_only_matched_pitt` | **Age/sex-matched** Pitt cohort: 90 matched pairs, 368 recordings (committed `match_participants` defaults, seed 1) | Same | Same | **Yes** — the matched counterpart. Companion speech figure on the same cohort: **0.7983** (`A3_speech_matched_pitt`). |
| **0.71 → 0.46** (transcript: age 0.714) | **Printed only** by an inline run whose code was lost with the sandbox; quoted in `DEVELOPMENT_NARRATIVE.md` entry 4 and in the file above under `narrative_reference_no_result_file` | Same design, different run | Same design, exact code unrecovered | Pre-lock, Pitt-only | **Superseded — narrative history only.** Same design and same conclusion (age discriminates raw, collapses to chance matched); the file-backed values above replace them wherever a number is cited. |
| **0.6230** (0.6230454186282038) | `results/_superseded/ablation_pre_lock.json` (quarantined; echoed as `pre_lock_auc` in the post-lock ablation) | **1,040 recordings including Lu**, unmatched combined pool | Per-row model **unknown code** | **Pre-lock, Lu-inclusive** | **Non-citable** (superseded). |
| **0.5571** (0.5570716433897747, CI 0.510–0.603) | `results/reconstruction/ablation_post_lock.json` → "age only" | Locked **987** (Pitt 548 + Delaware 439), unmatched combined | Verified architecture (`CalibratedClassifierCV(sigmoid, cv=3)` over the committed `ens()`), registered per-row model; participant bootstrap | **Post-lock** | **Yes** — the citable age-only figure for the development pool. |

**Why they differ.** Single-corpus raw Pitt (largest age gap) vs combined
two- and three-corpus pools vs a matched cohort, under different models. The
falling sequence is pool-and-protocol change, not contradiction: age alone is
strongest exactly where the confound is worst, which is the point the matched
cohort was built to remove.

**Companion figure — age recoverability after residualisation.** The rejected
"remove age statistically" shortcut was killed by showing age could be
predicted back out of the residualised features. Two values exist: the
original inline **R² = 0.997** (narrative entry 9, code lost) and the
2026-08-22 regeneration in the same result file — **R² = 0.9938 under
participant-grouped 5-fold CV**, 0.9993 in-sample, n = 548, via per-feature
OLS residualisation then `RandomForestRegressor(500, rs=42)`. The method is a
reconstruction, not the original code; cite **0.994 (grouped CV)** and note
the inline 0.997 as superseded. The conclusion is untouched — age survives
residualisation almost perfectly.

---

## C. Arabic-equivalent figures — 0.782 vs 0.7424 vs 0.7391

| Figure | Where it lives | Pool / population | Features | Model form | Lock state | Citable? |
|---|---|---|---|---|---|---|
| **0.782** (0.7822311737719592) | `results/summary/arabic_estimate.json` → `estimate.dementia_auc` | Pre-lock **1,040 pool including Lu**; **dementia-only** subset (Pitt + Lu vs their controls) | 19 (`ARABIC_EQUIVALENT`) | Uncalibrated committed `ens()` (500/150/500), seed 42, grouped 5-fold | **Pre-lock, Lu-inclusive** | **Non-citable** — stale on two counts (pool and model form). Its companion ceiling 0.805 is the number that had leaked into `libyan_pilot_protocol.md` §2 (fixed 2026-08-21). |
| **0.7424** (0.7423569608137737) | Same file → `estimate.mixed_auc`; **digit-for-digit identical** to the pre-lock ablation's Arabic-19 row | Same pool, **combined** population | 19 | Same | Pre-lock, Lu-inclusive | **Non-citable** — superseded by the row below, which measures the same quantity post-lock. |
| **0.7391** (0.7390639805545255, CI 0.703–0.774) | `results/reconstruction/ablation_post_lock.json` → "Arabic-compatible 19 features" | Locked **987**, combined | 19, imported from `scripts/estimate_arabic.py::ARABIC_EQUIVALENT` | Verified architecture (sigmoid, cv=3, over `ens()`), registered; participant bootstrap | **Post-lock** | **Yes** — the citable Arabic-equivalent figure. Retention: 0.7391 / 0.7550 = **97.9%** (replaces the old "97%"). |

**No post-lock dementia-only analogue of 0.782 exists.** Computing one would
require a new, approved, Lu-free dementia-subset run; until then the thesis
cites 0.7391 and the 97.9% retention, never 0.782. `estimate_arabic.py` itself
must not be re-run as committed: it pools Lu and writes into
`results/summary/`.

**Distinct quantity — the Arabic pilot.** 0.622 (CI 0.378–0.857) and 0.662
(dementia vs normal) in `results/arabic_pilot/findings.json` are the
**English-trained language-independent acoustic model** applied to Arabic
letter-fluency audio (24 speakers): a feasibility signal whose interval spans
chance, and a transfer in which both language and task differ. **The Arabic
linguistic engine and the referential deficit index were not evaluated by the
pilot.** *Reproduction status (2026-08-22): the pilot was re-run once from a
fresh clone of the public source dataset under a pre-registered protocol —
labels re-derived to 7 normal / 6 MCI / 11 dementia (the ambiguous shorthand
"11/6/7" used here previously was being read in two different orders inside
one file; corrected and CLOSED 2026-08-23 against the development transcript,
which records 7/6/11 and states the derivation matched the published paper —
the pilot compares SEVENTEEN impaired speakers against SEVEN controls), and the
24 re-extracted predictions
matched `predictions.npy` with max |Δp| = 0.0 under both pre-declared audio
variants; grade MATCH (`results/reconstruction/arabic_pilot_reproduction.json`).* The referential deficit index's evidential status: implemented and
verified on constructed examples; never computed on real patient speech;
discriminative validity untested.

---

## D. Other multi-valued figures, reconciled elsewhere — pointers

| Figure family | Versions | Resolution | Where documented |
|---|---|---|---|
| Matched-cohort text AUC | 0.838 / 0.802 / 0.804 | 0.838 was one lucky matching draw, retired; 0.802 = ten-seed **text-only** mean, 0.804 = **text+acoustic** mean — same file, two columns | `matching_stability.csv`; `DEVELOPMENT_NARRATIVE.md` entry 6, appendix item 1 |
| External AUC | 0.821 / 0.849 / 0.859 / **0.853** | 0.821 was the only clean pre-lock external figure; 0.849 and 0.859 are contaminated (Lu consulted); **0.853 is the locked one-shot and the only citable external number** | `external_validation_honest.json`; `locked_external_validation.json`; reproduction: `lu_oneshot_reproduction.json` (MATCH) |
| Calibration max gap | 0.069 / **0.151** | 0.069 was computed with Lu in training (stale `calibration.json`); **0.151** is the Lu-free value, deviation confined to the top band and conservative | `CURRENT_development_stats.json`; HANDOFF §0.2 recommended wording |
| TRAINING_PRIOR | 0.50 / 0.4721 / **0.471125** | assumed → measured pre-lock (491/1040, incl. Lu) → **post-lock 465/987**, now the constant in `risk_adjustment.py` | `results/reconstruction/training_prior.json`; `compute_training_prior.py` |
| Delaware MCI AUC | 0.636 / 0.629 / 0.5687 / 0.5061 | **Four figures, three of them correct and answering different questions.** Promoted to its own section — see **§E** below |

---

*Provenance: compiled 2026-08-21 during the Arabic-component audit;
dataset/lock state as stamped in the header. Every value above was read from
the named file in the same session; the acoustic-model architecture comes from
stdlib introspection of the deployed pickle (nothing executed from it). The
"consulted five times" contamination count is committed evidence:
`scripts/fusion_experiments.py`, governance note, lines 28–33.*


---

## E. Delaware MCI AUC — 0.629 vs 0.5687 vs 0.5061 (and the stale 0.636)

Four numbers attach to the phrase "Delaware MCI AUC". **Three of them are correct
and measure different things.** This section exists because that is precisely the
situation this document was created for: the numbers are not in conflict, the
*question* differs in each case, and a reader who sees two of them without the
question will conclude one is an error.

| Figure | Where it lives | Training pool | Feature set | Participant selection | Combination | What question it answers | Citable? |
|---|---|---|---|---|---|---|---|
| **0.629** (0.6290770609) | `results/summary/CURRENT_development_stats.json` → `delaware_mci` | **Pitt + Delaware, 987 recordings** — the deployed development pool | **64 deployed** | **All 439** Delaware cookie recordings; out-of-fold inside the COMBINED folds | single task | *How does the deployed instrument perform on the Delaware MCI subset?* | **Yes — the citable Delaware figure**, and the one that belongs beside 0.755 and 0.809. It is a **subset performance**, not a corpus-held-out fit. |
| **0.5474** (0.5474462366) | `results/reconstruction/cross_corpus_transfer.json` → `R_delaware_within` | **Delaware only**, 439 | 64 deployed | All 439, participant-grouped CV inside this corpus | single task | *Can a model trained on Delaware alone detect Delaware MCI?* | **Yes, as the within-corpus reference.** CI [0.485, 0.605] — **indistinguishable from chance**, which is why the C2 retention ratio in that file is uninterpretable (recorded there). |
| **0.5687** | `results/reconstruction/task_battery_probe.json` → cookie arm, §5.6.1 | Delaware only | 64 deployed | **288 complete-case participants**, one row each chosen by `groupby.first()` = **first row in FILE ORDER** | single task | *(intended)* the Cookie arm of the battery comparison | **No — superseded.** The selection rule is not the first visit; Delaware's meta is not visit-sorted, so for the 18 participants whose label changes across visits it takes an arbitrary visit's label. Its class split (102/186) matches no defensible rule. See §5.6.1's correction notice. |
| **0.5061** | `results/reconstruction/task_count_curve.json` → `AMENDMENT_3_crosssectional.singles.cookie` | Delaware only | **43 shared** — the features every one of the five task extractors computes; Cookie's 31 information-unit features excluded because they do not exist for the other four tasks | **288 complete-case participants at the earliest visit common to all five tasks**, carrying that visit's label (115 impaired / 173 control) | single task, score level | *How does Cookie Theft compare with Delaware's other four tasks, on the same people, on a like-for-like feature set?* | **Yes — the citable figure for the TASK COMPARISON only.** It is deliberately not the deployed configuration: it drops the information-unit block so that five tasks can be compared on identical measures. §5.25. |
| ~~0.636~~ | stale `all_findings.json` | pre-lock era | — | — | — | — | **Non-citable.** Superseded by 0.629. |

**How to use them in one sentence each, without contradiction:**

- **0.629** is what the deployed instrument achieves on Delaware MCI. Quote it in Chapter 5 beside the combined 0.755 and the Pitt 0.809.
- **0.5474** is what a Delaware-only model achieves, and it is at chance. Quote it whenever the question is whether Delaware can be learned from Delaware — including as the reason the pooled design exists.
- **0.5061** is what the *Cookie Theft task* is worth for MCI when measured against Delaware's other four tasks on the same people and the same measures. Quote it **only** inside the task comparison, and never beside 0.629, because it is a different feature set on a different participant selection.

**The trap to avoid, stated explicitly.** 0.629 and 0.5061 are **not** a
before-and-after, a deterioration, or a contradiction. 0.629 has the benefit of
Pitt's 548 recordings in training and the full 64 features including the
information-unit block; 0.5061 has neither, by design, because a comparison across
five tasks cannot use features that only one task has. Writing "Delaware fell
from 0.629 to 0.506" would be false. The correct sentence is: **"On a like-for-like
feature set shared by all five tasks, Cookie Theft is the weakest of the five for
MCI (0.5061), while the deployed instrument — which additionally has Pitt in
training and the information-unit block — reaches 0.629 on the same cohort."**

**And one number that is NOT in this family**, because it is asked of a different
population: **0.6379**, the best two-task combination (cinderella + sandwich) on
the same 288 participants and the same 43 features. It belongs with 0.5061, not
with 0.629, and under the §1.7 rule neither may share a table with a validated
figure.

