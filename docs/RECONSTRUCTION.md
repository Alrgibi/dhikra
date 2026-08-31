> **Date correction, 2026-08-22.** Sections 2.10 and 2.11 previously dated the
> housekeeping round and the one-shot Lu reproduction to 2026-08-21. The
> filesystem says otherwise and it is decisive: the protocol document was
> written at 2026-08-20 20:58, the driver at 21:13:09, the tombstone
> `results/reconstruction/LU_ONESHOT_EXECUTED` at 21:13:36 (matching the
> `scored_at` field the driver wrote into
> `lu_oneshot_reproduction.json`), the result file at 21:13:39, and this
> document itself at 21:14:52 — all on **2026-08-20**. A file cannot have an
> mtime before it exists, so the run is fixed to 20 August. The drivers'
> `date.today()` stamps agree with the device clock everywhere else, including
> on files generated on the 21st and 22nd. The acoustic phase genuinely is
> 2026-08-21.

# RECONSTRUCTION.md — what was rebuilt, what was inferred, and the evidence

**Date:** 20 August 2026.
**Context:** The project was developed in a conversational sandbox that no
longer exists. Its handoff (HANDOFF.md, 18 Aug 2026) preserved the code, the
frozen models, and the result files — but several analyses had been run as
one-off inline commands whose exact code was never saved (FILE_MAP.md marks
these "inline" and calls the gap out explicitly). This document records, for
the examiner and for the project's own audit trail, exactly what was
**recovered** (verbatim, from committed code or data), what was
**reconstructed by inference**, and the evidence for each inference. Nothing
in `results/summary/` (the locked numbers) has been modified; every
reconstructed output is written to `results/reconstruction/` and compared
against the locked files field by field.

The governing rule: a reconstructed number is never silently substituted for
a locked one. Where reconstruction and locked record disagree, the
disagreement is itself the finding.

---

## 1. Recovered verbatim (no inference)

| Item | Source |
|---|---|
| All five corpora (Pitt, Pitt-orig, Delaware, Lu, WLS) | Owner's TalkBank zips, extracted 2026-08-20 into per-corpus folders; file counts verified against the archive listings (1290 / 1290 / 455 / 54 / 1368 `.cha`) |
| The 64-feature list of the deployed model | `results/summary/model_card.json` → `feature_order` (24 ling + 31 iu + 9 sem; no chat.*, no ac.*) |
| The ensemble recipe (ExtraTrees 500 + GradientBoosting 150/d2/lr .05 + RandomForest 500, soft voting, seed 42, impute+scale pipelines) | committed in `scripts/early_detection.py::ens()` (same recipe in `fusion_experiments.py`) |
| CV protocol: `StratifiedGroupKFold(5, shuffle=True, random_state=42)`, grouped by participant | committed in scripts and stamped in `model_card.json` |
| Threshold *rule*: highest threshold achieving a sensitivity floor, maximising specificity | `src/dhikra/model.py::screening_threshold` |
| Exclusion criteria: `<10 words`, CHAT-only features, 'Other' diagnosis, one Lu aphasia case | `model_card.json` → `exclusions` |
| Dependency versions: numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, scikit-learn 1.8.0, spacy 3.8.15, Python 3.12 | `model_card.json` → `dependencies`; HANDOFF §8 |

## 2. Reconstructed by inference

### 2.1 The Lu label mapping (committed to `chat_parser.py`, 2026-08-20)

**Problem.** The locked external evaluation
(`locked_external_validation.json`: n = 53, 27 control / 26 impaired) cannot
be produced by the committed `group_to_label`: the Lu `@ID` headers contain
`Alzheimer's`, `Pick's`, and the typo `Conrol`, none of which were in the
committed sets. The build that produced the lock used an extended mapping
that never reached the repository.

**Evidence.** An `@ID`-header audit of all 54 Lu files (metadata only, run
on the owner's machine 2026-08-20) found:

| Folder | Header group | n |
|---|---|---|
| Control | `Control` | 25 |
| Control | `Conrol` (typo, F32.cha) | 1 |
| Dementia | `Alzheimer's` | 16 |
| Dementia | `Dementia` | 6 |
| Dementia | `MCI` | 2 |
| Dementia | `Vascular` | 1 |
| Dementia | `Pick's` | 1 |
| Dementia | `Aphasia` (F16.cha) | 1 |
| Dementia | `Control` (F07.cha) | 1 |

Exactly one mapping reproduces the locked composition:
`Alzheimer's`/`Pick's` → impaired, `Conrol` → control, `Aphasia` → excluded,
header over folder. It yields 27 control (25 + typo + F07) / 26 impaired
(16+6+2+1+1) / 1 excluded — matching the locked n = 53 and the model card's
"one aphasia case in Lu" exclusion. The locked sensitivity 0.9615 (= 25/26)
and specificity 0.3333 (= 9/27) are consistent with these denominators.

**Status.** Inference, not recovery — but over-determined by four
independent constraints (total n, class split, the aphasia note, the
denominators). Committed with a `RECONSTRUCTED` comment;
`scripts/build_lu.py` asserts the composition and names F07/F16 explicitly.

### 2.2 The `pitt_cookie` subset recipe (`scripts/build_pitt_cookie.py`)

**Problem.** `analyze_pitt.py` defaulted to `/home/claude/pitt_cookie`, a
hand-made cookie-only folder; no script created it.

**Evidence.** FILE_MAP's pipeline names "`<Pitt cookie dir>`"; the locked
Pitt n = 548 equals the 552 on-disk cookie files (243 Control + 309
Dementia) minus the model-card exclusions. Pointing the builder at the Pitt
ROOT instead would ingest the patient-only fluency/recall/sentence tasks
(738 more files) and could not produce n = 548.

**Status.** Recipe inferred; the 552→548 count assertion at first run is the
verification. Until that run passes, the *specific* claim "the 4 exclusions
are label-None ('Other') plus <10-word files" is **[UNVERIFIED]**.

### 2.3 The final-model form ("calibrated soft-voting ensemble")

**Problem.** `model_card.json` calls the deployed model a *calibrated*
soft-voting ensemble; the only committed ensemble is uncalibrated.
"Calibrated" may mean (a) a `CalibratedClassifierCV` wrapper, or (b) that
calibration was *measured* on the ensemble's outputs.

**Evidence for (b) first:** `review2_actions.json` records "Probability
calibration — DONE — slope 1.19, intercept 0.06, Brier 0.198, max gap 0.069
→ reportable as a probability", which reads as measurement of existing
outputs; the stale `calibration.json` carries a `verdict` field, again
measurement language.

**Additional argument (owner, 2026-08-20, approved for testing order):** a
*fitted* calibrator could not leave a 0.151 top-band gap on its own training
data — isotonic regression matches observed bin rates by construction. The
observed gap pattern (excellent mid-range, under-stated top band) is what an
uncalibrated tree ensemble's averaged probabilities look like. The
uncalibrated form is therefore the registered first hypothesis.

**Status.** The registered first hypothesis was TESTED on 2026-08-20
(uncalibrated committed recipe, full pipeline, exact pinned versions). It
came out **close but not exact**: counts and participant totals exact; AUCs
within −0.004 (combined 0.7511 vs 0.7550, Pitt 0.8062 vs 0.8095, Delaware
0.6263 vs 0.6291); Brier within 0.0004; but the probability-scale
signatures did not reproduce — floor-0.75 threshold 0.393 (locked 0.367),
max gap 0.084 (locked 0.151), slope 1.131 (locked 1.276), and materially
different bin populations (55/388/266/188/90 vs 20/467/243/203/54). The
conditional model-card correction therefore did NOT trigger; the model card
is left untouched. The pattern — near-identical ranks, different
probability scale, shrunken-but-cleaner locked extremes — is consistent
with per-fold `CalibratedClassifierCV` averaging inside the outer CV.
Discrimination between sigmoid and isotonic proceeds under the
pre-registered protocol in §2.7. The model form remains **[INFERRED]**
until a variant meets the §2.7 criteria.

### 2.4 The screening threshold 0.367

**Problem.** The rule is committed (`screening_threshold`: max specificity
subject to a sensitivity floor) but the invocation that produced 0.367 is
not.

**Evidence.** The locked screening point (sens 75.7%, spec 58.8%) sits
exactly at a 0.75 floor; the stale pre-lock file (`operating_points.json`,
threshold 0.383, sens 75.4%) matches the same rule on the pre-lock pool.
`train_development.py` sweeps floors {0.90…0.70} and reports which
reproduces 0.367.

**Run outcome (2026-08-20, uncalibrated OOF):** floor 0.75 gave threshold
0.393 (sens 0.750, spec 0.590), NOT 0.367 — the rule is committed but the
threshold value depends on the probability scale, which the uncalibrated
form did not reproduce (§2.3). The floor-0.75 inference therefore remains
**open**, to be re-tested on whichever calibrated variant passes §2.7.
(Floor 0.80 landed at 0.365 with sens 0.800 — numerically near 0.367 but
inconsistent with the locked sensitivity 0.757; recorded to pre-empt the
coincidence.) **[INFERRED, floor = 0.75 — UNRESOLVED pending §2.7]**

### 2.5 Participant-level bootstrap CIs

HANDOFF §2 records the method ("2,000 resamples of people, not recordings")
but not the code. Reimplemented as uniform resampling of participants with
all their recordings, seed 42. Exact RNG stream of the original is unknown,
so reconstructed CIs cannot match to the last digit. **Accepted tolerance
(approved 2026-08-20): a reconstructed CI bound within ±0.005 of the stored
bound counts as reproduced; anything larger is a discrepancy to investigate,
not to accept.** **[INFERRED implementation]**

### 2.6 Cross-corpus participant grouping

Whether the inline build prefixed Pitt and Delaware participant ids before
grouping (preventing accidental id collisions from merging two people into
one CV group) is unrecorded. The reconstruction prefixes (`p_`/`d_`) and
asserts 581 unique participants — the locked count — which any collision
would violate. **[INFERRED, verified by the 581 assertion]**

### 2.7 Pre-registered acceptance criteria — calibration discrimination test

**Registered 2026-08-20, BEFORE either variant was run.** Purpose: decide
between the two remaining candidate forms of the "calibrated soft-voting
ensemble" without fitting the reconstruction to its target. Exactly two
variants are authorised (owner approval, 2026-08-20); if neither reaches
MATCH, work stops and the result is reported — no further configuration
sweeps without fresh explicit approval, because matching by trial IS
fitting to the target, and this reconstruction has to survive an examiner.

**The two variants.** Identical to the registered uncalibrated run (same
matrices, 64 locked features, prefixed participant groups, outer
`StratifiedGroupKFold(5, shuffle=True, random_state=42)`, out-of-fold
`predict_proba`) except the estimator is wrapped:

- **Variant A:** `CalibratedClassifierCV(estimator=ens(), method="sigmoid", cv=5)`
- **Variant B:** `CalibratedClassifierCV(estimator=ens(), method="isotonic", cv=5)`

`cv=5` is the scikit-learn integer path: internal `StratifiedKFold(5,
shuffle=False)`, `ensemble=True` — five (sub-model, calibrator) pairs per
outer fold, probabilities averaged. `cv="prefit"` is excluded a priori: a
single monotone calibrator cannot reorder predictions (sigmoid is strictly
monotone; isotonic can only merge ties, which perturbs AUC only by
tie-collapse), so it cannot produce the observed ≈0.004 AUC shift — the AUC
difference implies sub-model averaging, i.e. the integer-cv path.

**Signatures and tolerances** (locked values from
`CURRENT_development_stats.json`):

| # | Signature | Locked | Pass tolerance |
|---|---|---|---|
| S1 | Combined AUC | 0.755016 | abs Δ ≤ 0.001 |
| S2 | Pitt dementia AUC | 0.809472 | abs Δ ≤ 0.001 |
| S3 | Delaware MCI AUC | 0.629077 | abs Δ ≤ 0.001 |
| S4 | Threshold at floor 0.75 | 0.367 | EXACT equality (rule quantises to 3 dp), and sens within ±0.005 of 0.75699, spec within ±0.005 of 0.58812 |
| S5 | Calibration max gap | 0.151310 | abs Δ ≤ 0.010 |
| S6 | Calibration slope / intercept | 1.27639 / 0.13479 | abs Δ ≤ 0.05 each |
| S7 | Bin table (5 bins) | n = 20/467/243/203/54 | every bin: n within ±5, predicted within ±0.010, observed within ±0.025 |

Brier is reported but non-criterial: the uncalibrated form already matched
it (Δ 0.0004), so it does not discriminate. Tolerance rationale: AUC
granularity on 465×522 pairs is ≈4×10⁻⁶, so ±0.001 forgives microscopic
feature drift while sitting an order of magnitude below the uncalibrated
deltas (≈0.003–0.004); the observed tolerance ±0.025 is about one
recording in the smallest locked bin (n=54); slope/intercept ±0.05 is a
third of the uncalibrated miss (0.145 / 0.134).

**Grades.**

- **MATCH** — all seven signatures pass. §2.3 is then settled as that
  variant, recorded as **inferred from output signatures, not recovered
  from code** (this phrasing goes into the thesis).
- **PARTIAL MATCH** — S4 passes and at least four of the remaining six
  pass. Reported as "consistent with, unconfirmed"; §2.3 stays open; work
  still stops (a partial is not a match).
- **FAILURE** — anything else.

**Interpretive asymmetry, registered in advance.** A MATCH is strong
positive evidence (seven joint signatures, tight tolerances). A FAILURE of
both variants does NOT prove the inline pipeline was uncalibrated or
otherwise different — residual drift in the rebuilt feature matrix could
mask a correct method. Failure therefore means "cannot confirm", never
"disconfirmed", and the thesis language must preserve that distinction.

**Mechanical grading.** The tolerances above are encoded in the runner
before execution; grades are computed by code, not judged after seeing the
numbers. Outputs: `results/reconstruction/discriminating_sigmoid.json` and
`discriminating_isotonic.json`, each carrying the full signature table,
per-signature pass/fail, the grade, and provenance. Lu remains untouched
throughout.

**OUTCOME (run 2026-08-20, after registration).** Both variants graded
**FAILURE** by the encoded criteria. Signature table (locked → uncalib /
sigmoid / isotonic):

| Signature | Locked | Uncalibrated | A: sigmoid | B: isotonic |
|---|---|---|---|---|
| Combined AUC | 0.755016 | 0.751147 | 0.754064 ✓S1 | 0.745155 |
| Pitt AUC | 0.809472 | 0.806207 | 0.806746 | 0.799427 |
| Delaware AUC | 0.629077 | 0.626277 | 0.633804 | 0.620206 |
| Threshold @ .75 | 0.367 | 0.393 | 0.353 | 0.346 |
| Max gap | 0.1513 | 0.0840 | 0.0737 | 0.0692 |
| Slope | 1.2764 | 1.1309 | 1.0857 | 0.6702 |
| Brier | 0.19854 | 0.19894 | 0.19733 | 0.20119 |
| Bin n | 20/467/243/203/54 | 55/388/266/188/90 | 81/415/212/178/101 | 119/414/171/136/146 |

Sigmoid passed S1 only (1/7); isotonic passed none (0/7). Per the
registered stopping rule, no further configurations were run. Per the
registered asymmetry, this is **"cannot confirm"**, not "disconfirmed":
the locked probability distribution — mass concentrated in (0.2, 0.4],
small but nearly pure extreme bins (bottom observed 0.100, top observed
0.981), slope 1.28 — is produced by none of the three registered forms,
and both calibration directions moved the signatures further from the
locked shape in the extremes, not closer. The form of the inline model's
probability scale therefore remains **[UNRESOLVED]**; §2.3 and §2.4 stay
open. Observations recorded for the owner's decision (no runs performed):
the locked AUC and Brier are near the uncalibrated form's (Δ 0.004 /
0.0004) while the locked tail behaviour is not, i.e. the discrepancy is
confined to the distribution's extremes.

### 2.8 Verification of the RECOVERED configuration — registered before the run

**Registered 2026-08-20, before execution.** After §2.7 closed (both
registered variants FAILURE, stop honoured), the owner approved two
read-only diagnostics. The second — a search of the handoff archive —
found that the deployed artifact itself contains the full configuration.
Introspection of `models/dhikra_model.pkl` (archive copy, packaged
2026-08-19 19:11) under the pinned scikit-learn 1.8.0 recovered:

```
top-level dict: {'model': ..., 'features': [64], 'auc': 0.7550158612450046,
                 'n': 987, 'screening_threshold': 0.367,
                 'screening_sens': 0.7569892473118279,
                 'screening_spec': 0.5881226053639846, ...}
model = CalibratedClassifierCV(method='sigmoid', cv=3, ensemble='auto')
  wrapping VotingClassifier(voting='soft') of three Pipelines
  (median impute -> standardise -> classifier):
    et: ExtraTreesClassifier(500, min_samples_leaf=3, class_weight='balanced', random_state=42)
    gb: GradientBoostingClassifier(150, max_depth=2, learning_rate=0.05, random_state=42)
    rf: RandomForestClassifier(500, min_samples_leaf=3, class_weight='balanced', random_state=42)
```

The inner ensemble is exactly the committed `early_detection.ens()`
recipe; the wrapper differs from §2.7's variant A in a single parameter
(cv=3, not 5). The artifact's embedded metadata carries the locked
headline values, tying this object to the locked result.

**Epistemic status — the point of this section.** The run authorised here
is **VERIFICATION of a configuration RECOVERED from the deployed
artifact, not a search over configurations.** The configuration was read
from `dhikra_model.pkl` BEFORE the run and is testable exactly once; it
was found, then tested — not selected because it matched. That is the
whole difference between recovery and curve-fitting, and it is the
distinction the thesis must state. The §2.7 acceptance criteria and
grades apply **UNMODIFIED**; grading remains mechanical
(`results/reconstruction/discriminating_sigmoid_cv3.json`).

**Outcome (run 2026-08-20, after registration): MATCH — 7/7 signatures.**

| Signature | Locked | Recovered config (sigmoid, cv=3) | Pass |
|---|---|---|---|
| Combined AUC | 0.755016 | 0.755032 (Δ +1.6e-5) | ✓ |
| Pitt dementia AUC | 0.809472 | 0.809472 (Δ +0.0e+00) | ✓ |
| Delaware MCI AUC | 0.629077 | 0.629122 (Δ +4.5e-5) | ✓ |
| Threshold @ floor 0.75 | 0.367 / .757 / .588 | 0.367 / .757 / .588 | ✓ |
| Max gap | 0.15131 | 0.15131 | ✓ |
| Slope / intercept | 1.2764 / 0.1348 | 1.2887 / 0.1376 | ✓ |
| Bin n | 20/467/243/203/54 | 20/466/244/203/54 | ✓ |
| Brier (non-criterial) | 0.198536 | 0.198536 | — |

The bin table differs by a single recording at the (0.2,0.4]/(0.4,0.6]
boundary; Pitt AUC reproduces to the last digit. The residual slope delta
(+0.012) equals the delta obtained when this document's slope-fit is
applied to the STORED vector itself (§ read-only diagnostic, 2026-08-20),
i.e. it is a property of the slope-fit implementation, not of the
predictions. Participant-bootstrap CIs on the verified vector agree with
all six stored bounds within the registered ±0.005 (max |Δ| = 0.0024;
`discriminating_sigmoid_cv3.json`).

**Resolution.** §2.3 is settled — and upgraded from *inferred* to
**RECOVERED**: the final model form is
`CalibratedClassifierCV(method='sigmoid', cv=3, ensemble='auto')` over the
committed `early_detection.ens()` soft-voter. §2.4 is settled: on the
verified vector the committed `screening_threshold` rule with floor 0.75
yields exactly 0.367 / 75.7% / 58.8% — **[CONFIRMED, floor = 0.75]**.
§2.5 is settled within its stated tolerance. The model card's
architecture field was corrected to the recovered specification, citing
the pickle as source (approved 2026-08-20). The owner's earlier argument
that a fitted calibrator could not leave a 0.151 same-data gap remains
correct as stated — the recovered calibrators are fitted per internal
fold and the gap is measured out-of-fold, which is the case that argument
deliberately did not cover.

### 2.9 Feature-count accounting: 117 vs 64

Traceable arithmetic, verified 2026-08-20 against the built matrices and
the original result files:

| Count | What it is | Composition | Evidence |
|---|---|---|---|
| **117** | measurements EXTRACTED per live assessment (audio + transcript) | 64 transcript-derived + 53 acoustic | HANDOFF §1 L70 ("extracts 117 measurements from the recording and its transcript"); README L68; 64 + 53 = 117 |
| **64** | inputs to the DEPLOYED screening model | 24 ling.* + 31 iu.* + 9 sem.* | `model_card.json` feature_order; pickle `n_features_in_ = 64` |
| **53** | acoustic family — separate channel | ac.* | 53 distinct ac.* rows in `results/pitt_cookie/acoustic_group_comparison.csv` and `acoustic_mmse_correlation.csv`; consumed by `dhikra_acoustic_model.pkl` and report indicators, NOT by the text model |
| **74** | corpus RESEARCH matrices (transcript-only) | 64 + 10 chat.* | built `features.csv` column count; chat.* are CHAT-markup disfluency features, corpus-only ("not computable from live recordings", model-card exclusions) — in neither 117 nor 64 |

So: 117 is the extraction count, 64 the modelling count. The "other 53"
are the acoustic measurements, which feed the language-independent
acoustic model and the report's indicator profile rather than the
deployed text classifier. The 10 chat.* features exist only for corpus
data; `pause_features.py` (unwired) is in none of these counts
(HANDOFF §6.1).

### 2.10 Housekeeping round (owner-approved 2026-08-20) — quarantine, ablation rerun, pause_features

**Quarantine.** `results/development/` moved to
`results/_superseded/development/` (nothing deleted) with a README: its
two files are NON-CITABLE — no committed producer, generating code lost
in the export's stripped tool blocks, baseline pool unverifiable;
superseded by `results/fusion/results.json`. The pre-lock ablation table
moved beside it (`results/_superseded/ablation_pre_lock.json`) — its
pre-lock status is settled by the 16-digit match of its final-ensemble
row to `final_by_population.json`'s combined AUC.

**Ablation rerun (registered design, before execution).** Eight rows
mirroring the pre-lock table, on the locked 987 pool: per-row model = the
verified `CalibratedClassifierCV(sigmoid, cv=3)` over the committed
`ens()` — except the logistic-baseline row, which is what its label
names. The pre-lock table's per-row model is unknown-code; this choice is
registered here, stamped in the output provenance, and not adjusted after
seeing results. The Arabic-compatible 19-feature set is imported from its
committed source (`scripts/estimate_arabic.py::ARABIC_EQUIVALENT`).
Output: `results/reconstruction/ablation_post_lock.json` with per-row
deltas against the pre-lock table. Comparability caveat, stated in
advance: pre-lock rows were computed on a different pool (1,040 with Lu)
by unknown code, so deltas mix pool change with any protocol difference —
the new table REPLACES the old for citation; the deltas are context, not
a verification claim.

*Outcome (run 2026-08-21):* final ensemble 0.7550 [0.7179–0.7926] —
identical to the verified development OOF, as it must be (same model,
folds, pool). Feature-family rows moved ≤ 0.007 from the pre-lock table
(information 0.7107, linguistic 0.7388, Arabic-19 0.7391, logistic
baseline 0.7433, all+age 0.7670). The two larger movers are age-only
(0.623 → 0.557) and semantic-only (0.602 → 0.577), consistent with the
registered caveat (Lu's removal and the fixed per-row model). Arabic-19
retention on the locked pool: 0.7391 / 0.7550 = 97.9% of full
performance, in line with the 97% previously reported.

**pause_features.py** moved to `future_work/` (unmodified; it was
imported nowhere, so behaviour is unchanged) and recorded in
`docs/_working_notes/IMPROVEMENTS.md`. The owner's reasoning, adopted as policy: wiring
it in would change the feature set, so the model would no longer be the
one Lu validated — an improvement, not a repair, and Lu cannot be spent
twice.

**FILE_MAP.md** updated (pipeline line superseded by
`build_pitt_cookie.py`; superseded-outputs section added). Its "(Lu is
built inline)" line is now also stale — flagged for a future approved
edit.

**Lu protocol.** `docs/LU_EVALUATION_PROTOCOL.md` DRAFTED and awaiting
approval: a pre-registered one-shot REPRODUCTION (not a second
evaluation) with per-signature tolerances, mechanical grades, a
report-and-stop failure rule, an explicit no-development-decision clause,
and a tombstone against double execution. Nothing runs until approved.

### 2.11 One-shot Lu reproduction — outcome (executed 2026-08-20T21:13:36 UTC)

Protocol: `docs/LU_EVALUATION_PROTOCOL.md`, approved verbatim by the
owner 2026-08-21 and executed once. Final model trained on all 987
development rows (recovered architecture, seed 42, Lu never seen); Lu
scored a single time; raw predictions written to disk before any metric;
tombstone written; threshold 0.367 held as a fixed input throughout.

| Signature | Locked | Reproduced | Δ | Grade |
|---|---|---|---|---|
| L1 AUC | 0.8532763533 | 0.8532763533 | +0.000000 | PASS |
| L2 Sensitivity @ 0.367 | 25/26 = 0.961538 | 25/26 = 0.961538 | exact | PASS |
| L3 Specificity @ 0.367 | 9/27 = 0.333333 | 9/27 = 0.333333 | exact | PASS |
| L4 Brier | 0.17881487 | 0.17881491 | +4e-8 | PASS |
| L5 CI (bootstrap 2000, seed 42) | [0.737069, 0.945822] | [0.735024, 0.945404] | ≤0.0021 | PASS |

**GRADE: MATCH.** The AUC agrees to ten decimal places, which on 702
discordant pairs means the reproduction's ranking of the 53 Lu
recordings is identical to the original deployed model's; the confusion
matrix at the fixed threshold is identical cell for cell.

**What this establishes.** The entire chain — corpus on disk → label
mapping → feature extraction → 987-row training pool → recovered
architecture → fixed threshold → locked external result — now
reproduces end-to-end from committed code under the pinned environment.
Every step is a script in the repository; nothing load-bearing remains
inline-only.

**What this does not change (registered in advance, §1 of the
protocol).** `results/summary/locked_external_validation.json` remains
the thesis's external evidence; this run is its reproduction, not a
second evaluation. No development decision follows from this outcome.
The tombstone (`results/reconstruction/LU_ONESHOT_EXECUTED`) forbids
re-execution; output and per-recording predictions:
`results/reconstruction/lu_oneshot_reproduction.json` (Lu feature-matrix
SHA-256 recorded inside).

## 3. Known-lost logic (audit register)

Reported numbers that depend on code not in the repository. The
reconstruction so far covers items 1–2; the rest remain to do or to accept
as documented-but-not-reproducible:

1. **Development regeneration** (AUCs 0.755/0.809/0.629, CIs, calibration
   table, operating points, PPV/NPV) — **RESOLVED 2026-08-20**: the
   recovered configuration (§2.8) reproduces all pre-registered
   signatures (MATCH 7/7); CIs within ±0.005.
2. **Lu build + label mapping** (external AUC 0.853 etc.) — mapping
   committed (§2.1); `build_lu.py` parse-only run 2026-08-20: the
   27/26/1 assertion PASSED (F07 control-by-header, F16 excluded, no
   word-count drops). **No scoring performed; Lu remains locked.**
3. **One-shot Lu evaluation runner** — not yet written; to be authored and
   pre-registered before Lu is touched, on explicit approval only.
4. **Bootstrap implementation** — §2.5, **verified** (all six bounds
   within ±0.005 of the stored CIs; max |Δ| = 0.0024).
5. **Threshold invocation** — §2.4.
6. **Severity model trainer** (r = 0.655, ±3.3 MMSE;
   `dhikra_severity_model.pkl`) — inline, not reconstructed.
7. **Delaware task-AUC JSONs** (`single_task_auc.json`,
   `combined_task_auc.json`, task-comparison p = 0.122 paired bootstrap) —
   inline, not reconstructed.
8. **Arabic pilot LOO** (0.622 CI [0.378–0.857]) — whether
   `demo_arabic.py` produces `arabic_pilot/findings.json` is unverified.
9. **Acoustic model trainer** (AUC 0.708, `dhikra_acoustic_model.pkl`) — no
   committed trainer found; also blocked on missing Pitt audio.
10. **`TRAINING_PRIOR` derivation** (0.4721 = 491/1040) —
    `scripts/compute_training_prior.py` committed and run 2026-08-20:
    the post-lock value is **0.471125 (465/987)**
    (`results/reconstruction/training_prior.json`). The constant in
    `risk_adjustment.py` still reads 0.4721; the one-line update is
    prepared and awaits explicit approval.
11. **Ten-seed matching stability** (`matching_stability.csv`, the
    0.838→0.804 correction) — no committed script writes this file.
12. **`results/development/` files** — `development_experiments.py` writes
    `experiments.json`, which does not exist there; the files that DO exist
    (`fusion.json`, `task_fusion.json`) match no committed writer. Supports
    HANDOFF §6.2's unresolved two-folder question.

Missing **inputs** (distinct from missing logic): ~~the WLS 2020-outcomes
spreadsheet (`WLS-data.xlsx`)~~ — FOUND 2026-08-20 at the DementiaBank
root under exactly the expected name, sheets `Data - 2020` and
`Data - 2004, 2011` verified; `corpus_paths.json` points at it. Still
missing: all corpus audio.

**Recovery source for the remaining items:** `archive/USER DATA.zip` is a
Claude account data export (confirmed 2026-08-20: `conversations.json`,
95.5 MB uncompressed, plus project and memory files). The original
development conversations — including, potentially, the inline commands
behind items 3 and 6–12 — are likely recoverable from it. Not yet opened
beyond the member listing.

## 4. Verification protocol

Every builder asserts the locked counts (Pitt 552→548, Delaware 455→439, Lu
54→27/26/1) and stamps a `PROVENANCE.json`. The training reconstruction
writes only to `results/reconstruction/`, embeds the locked values beside
its own with explicit deltas, and refuses to run if Lu-signature labels
appear in a development matrix. The rebuilt environment pins the exact
model-card versions (Python 3.12.11; numpy 2.4.4, pandas 3.0.2, scipy
1.17.1, scikit-learn 1.8.0, spacy 3.8.15, en_core_web_sm/md 3.8.0) so that
version drift cannot masquerade as protocol drift.

## 5. For the thesis

The honest sentence pattern: *"The final development statistics were
regenerated by an unsaved command; the pipeline was reconstructed from its
committed components and verified to reproduce the locked outputs to within
[tolerance achieved], with the reconstruction and its assertions committed
as `scripts/train_development.py`."* The Lu mapping paragraph should state
plainly that the label harmonisation was reconstructed from a header audit
and is over-determined by the locked composition — and that the audit found
one header/folder disagreement (F07) and one corpus typo (F32), both now
documented.
