# LU_EVALUATION_PROTOCOL.md — pre-registered one-shot reproduction

**STATUS: APPROVED AND SPENT.** Drafted, approved and executed on
**2026-08-20** (document written 20:58 UTC; single run at 21:13:36 UTC).
The reproduction it registers has been performed exactly once, grade MATCH,
and `results/reconstruction/LU_ONESHOT_EXECUTED` blocks any further run. The
draft header that stood here until 2026-08-22 ("NOTHING RUNS until approved",
dated 2026-08-21) was never updated after the run and gave the wrong date;
both are corrected — see the date note at the top of `docs/RECONSTRUCTION.md`.

---

## 1. What this is, and what it is not

The scientific one-shot evaluation of the locked external test corpus (Lu)
was **already spent** on 18 August 2026 (17:59): the deployed model scored
Lu exactly once with a pre-specified threshold, and
`results/summary/locked_external_validation.json` records the result. That
file is, and remains, the thesis's external-validation evidence —
**regardless of anything this protocol produces.**

The run registered here is a **REPRODUCTION**: a single execution that
tests whether the reconstructed pipeline (verified against the development
signatures 7/7 on 2026-08-20, `docs/RECONSTRUCTION.md` §2.8) also
reproduces the locked external result. It is:

- **not** a second scientific evaluation of Lu;
- **not** an opportunity to revise, improve, or re-derive any reported
  number;
- **not** an input to any modelling, threshold, calibration, or feature
  decision.

**No development decision follows from this run in either direction.** If
it matches, the reconstruction is verified end-to-end. If it does not
match, that fact is reported as a reproduction failure and the locked
numbers stand unchanged. Nothing else changes in either case.

## 2. Preconditions (all already satisfied, listed for the record)

1. Model architecture RECOVERED from `models/dhikra_model.pkl` and
   VERIFIED against all seven development signatures
   (`docs/RECONSTRUCTION.md` §2.7–2.8, MATCH 7/7).
2. Lu parsed once, parse-only, with the locked composition asserted:
   **27 control / 26 impaired / 1 excluded (F16, Aphasia); F07
   control-by-header** (`results/lu/PROVENANCE.json`, 2026-08-20).
   `results/lu/features.csv` exists and is untouched since.
3. Pinned environment: Python 3.12.11, scikit-learn 1.8.0, numpy 2.4.4,
   pandas 3.0.2, scipy 1.17.1, spacy 3.8.15 (= `model_card.json`
   dependencies).
4. Lu has entered no training, threshold, calibration, or feature
   decision at any point since the 18 August lock. (The chunked drivers
   assert Lu-signature groups cannot appear in development matrices.)

## 3. Exact procedure (single execution)

1. Load the development matrices: `results/pitt_cookie/features.csv` +
   `meta.csv` (assert 548) and `results/delaware/cookie_features.csv` +
   `cookie_meta.csv` (assert 439); select the 64 `model_card.json`
   `feature_order` columns; assert 987 rows, 581 participants.
2. Train the final model on ALL 987 development rows:
   `CalibratedClassifierCV(estimator=ens(), method='sigmoid', cv=3,
   ensemble='auto')`, where `ens()` is the committed soft-voting
   ExtraTrees(500)/GradientBoosting(150, d2, lr .05)/RandomForest(500)
   with median-impute + standardise pipelines, `random_state=42`
   throughout. **No fitting on Lu of any kind.**
3. Load `results/lu/features.csv` (assert 53 rows, 27/26 labels; record
   its SHA-256 in the output).
4. Score Lu once: `predict_proba(...)[:, 1]`. Write the raw predictions
   to the output file **before** computing any metric.
5. Compute, with the threshold **fixed in advance at 0.367** (an input,
   not an output — it is never re-derived):
   - AUC (probability ranks)
   - sensitivity and specificity at 0.367
   - Brier score
   - 95% bootstrap CI for the AUC: 2,000 resamples, seed 42,
     participant-level (in Lu each participant contributes one recording,
     so participant-level and recording-level resampling coincide; this
     is stated so the CI method is not a degree of freedom).
6. Write `results/reconstruction/lu_oneshot_reproduction.json`
   (predictions, metrics, grades, provenance, feature-matrix hash) and a
   tombstone `results/reconstruction/LU_ONESHOT_EXECUTED`. **The runner
   refuses to execute if the tombstone exists.** Any second execution
   requires a new written approval and a new protocol section explaining
   why.

## 4. Acceptance criteria — registered BEFORE the run

Locked reference: `results/summary/locked_external_validation.json`
(AUC 0.8532763532763533, CI [0.7370689655, 0.9458216462], sensitivity
0.9615384615 = 25/26, specificity 0.3333333333 = 9/27, Brier 0.1788148720,
threshold 0.367, n = 53).

| # | Signature | Locked value | Tolerance | Rationale |
|---|---|---|---|---|
| L1 | AUC | 0.853276 | \|Δ\| ≤ 0.005 | 53 recordings → 702 discordant-pair units of ~0.00142; ≤ 0.005 ≈ three pair swaps of feature-drift headroom, far below any effect size of interest |
| L2 | Sensitivity @ 0.367 | 0.961538 (25/26) | **exact** for MATCH; one recording's flip (±0.0385) tolerated only for PARTIAL | sens is a count over 26; exactness is the honest default |
| L3 | Specificity @ 0.367 | 0.333333 (9/27) | **exact** for MATCH; one recording's flip (±0.0370) tolerated only for PARTIAL | count over 27 |
| L4 | Brier | 0.178815 | \|Δ\| ≤ 0.005 | matches the probability-scale agreement seen in development (Δ ≈ 1e-5 there) |
| L5 | CI bounds | [0.737069, 0.945822] | \|Δ\| ≤ 0.02 per bound | bootstrap on n = 53 is intrinsically noisier; 0.02 is granularity-scaled, not permissive |

**Grades (mechanical, encoded in the runner before execution):**

- **MATCH** — L1–L5 all pass, L2 and L3 exact.
- **PARTIAL** — L1, L4, L5 pass; L2 and L3 within one recording's flip
  each. Reported as "consistent with, not confirmed"; the reproduction
  claim in the thesis is then stated at PARTIAL strength.
- **REPRODUCTION FAILURE** — anything else.

## 5. What happens on failure — registered in advance

If the run does not reach MATCH or PARTIAL:

1. The result is reported **as a reproduction failure**, in
   `docs/RECONSTRUCTION.md` and in the thesis reproducibility statement.
2. **Nothing is tuned, retried, or reconfigured in response.** No second
   run, no alternative configuration, no threshold adjustment, no feature
   investigation that feeds back into any model. The two-variant lesson
   of §2.7 applies with full force: matching by trial would be fitting to
   the target.
3. The locked external result (`locked_external_validation.json`) remains
   the thesis's external evidence — it was produced by the original
   deployed model, whose architecture is recovered and whose development
   behaviour is verified; a reproduction failure would bound the
   reconstruction's fidelity, not the original result's validity.
4. Diagnosis, if the owner wants one, happens **read-only** (comparing
   stored prediction vectors), under a separate written approval, and
   changes nothing.

## 6. Registered constants

Threshold 0.367 (fixed input). Seed 42 everywhere. 2,000 bootstrap
resamples. The 64 `feature_order` columns of `model_card.json`. One
execution. Output only to `results/reconstruction/`;
`results/summary/` is not written.

---

*Approval line: to authorise the run, reply approving this protocol as
committed; the runner will be executed exactly once, chunked for the
45-second tool budget, and graded by the criteria above unmodified.*
