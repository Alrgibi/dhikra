# Appendix C — The Model Card

This appendix reproduces the model card of the frozen screening model, `results/summary/model_card.json`, in full. The card is the machine-readable statement of what the deployed artifact is, what it was trained on, how it performed, what it is for and what it is not for; the platform of Chapter 4 reads it at start-up, and Chapter 6 treats its out-of-scope list as binding. Every field below is quoted from the card as committed, with calendar dates rendered as their place in the sequence (the card records its own amendment history in section C.6); where a field's wording differs from a chapter's, the card's is the artifact's own and the chapter's is the thesis's, and the two are reconciled in `docs/FIGURE_RECONCILIATION.md`. The card rounds its headline figures to three decimals; the four-decimal values with their intervals are those of Chapter 5.

## C.1 Identity And Provenance

The card identifies the artifact by version and freeze date and records how its architecture came to be known: not from a committed training script, which does not exist, but from introspection of the deployed file under the pinned library, verified against seven pre-registered signatures (section 3.9). Table (C.1) gives the identity fields.

**Table (C.1) : Identity and provenance fields of the model card**

| Field | Value |
|---|---|
| `model_version` | 2.0-lu-locked |
| `frozen` | at the lock |
| `supersedes` | 1.0 (n=1040, included Lu; superseded when Lu was locked as external test set) |
| `architecture` | CalibratedClassifierCV(method='sigmoid', cv=3, ensemble='auto') wrapping VotingClassifier(voting='soft') of three pipelines (median impute -> standardise -> classifier): ExtraTreesClassifier(n_estimators=500, min_samples_leaf=3, class_weight='balanced', random_state=42) + GradientBoostingClassifier(n_estimators=150, max_depth=2, learning_rate=0.05, random_state=42) + RandomForestClassifier(n_estimators=500, min_samples_leaf=3, class_weight='balanced', random_state=42) |
| `architecture_source` | recovered after the lock by introspection of models/dhikra_model.pkl (the deployed artifact; archive copy packaged after the lock) under the pinned scikit-learn 1.8.0; verified against the locked outputs 7/7 pre-registered signatures (docs/RECONSTRUCTION.md sect 2.7-2.8) |
| `architecture_history` | earlier wording: 'calibrated soft-voting ensemble (ExtraTrees + GradientBoosting + RandomForest)' -- accurate but under-specified: calibration method (sigmoid), internal cv (3) and member hyperparameters were unrecorded |
| `random_seed` | 42 |
| `cv` | StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42), grouped by participant |
| `dependencies` | scikit-learn 1.8.0; numpy 2.4.4; pandas 3.0.2; scipy 1.17.1; spacy 3.8.15 |

## C.2 The Training Data The Features And The Exclusions


The model consumes 64 features (Appendix A) from 987 recordings of 581 participants. The card's statement of the training data names DementiaBank Pitt and Delaware (picture description) and states the external corpus's exposure in the thesis's canonical form (section 3.9):

> The Lu corpus was excluded from the training data of the final model and from every modelling decision after the lock. Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool.

Four exclusions are recorded: recordings with fewer than 10 words; CHAT-annotation features (not computable from live recordings); Other diagnosis group (not a defined impairment category); one aphasia case in Lu (language disorder, not dementia).

## C.3 Performance As Recorded On The Card

Table (C.2) lists the performance fields exactly as the card stores them. The development figures are participant-grouped cross-validation on the pooled corpus (section 5.1); the external figures are the single locked evaluation (section 5.3), whose protocol the card states in the same words as section C.2. The `limitations` rows are the locked operating point at threshold 0.367; the specificity they record is diagnosed as a threshold-referencing failure, with the remedy analysed and not deployed, in sections 5.15 to 5.19.

**Table (C.2) : Performance fields of the model card**

| Field | Value |
|---|---|
| `development_auc` | 0.755 |
| `screening_threshold` | 0.367 |
| `screening_sensitivity` | 0.757 |
| `screening_specificity` | 0.5881 |
| `external_validation.corpus` | Lu |
| `external_validation.n` | 53 |
| `external_validation.auc` | 0.853 [0.737, 0.946] |
| `limitations.external_sensitivity` | 0.9615 |
| `limitations.external_specificity` | 0.3333 |
| `limitations.external_brier` | 0.1788 |

## C.4 Intended Use And Out Of Scope

The intended-use block was added after the lock — the card previously had none — and reads as follows. Purpose: "SCREENING ONLY -- to flag adults whose connected speech resembles that of people with diagnosed cognitive impairment, so that they can be referred for proper assessment. It does not diagnose, stage, or rule out any condition." Users: "a family member, nurse or health worker administering the session; results are interpreted by a clinician." Input: "about one minute of spontaneous description of the validated kitchen scene, in ENGLISH." Output: "a screening score, not a calibrated clinical probability (see limitations)." The five out-of-scope uses, which Chapter 4 section 4.5 enforces in code for the first three and states in documentation for the last two, are listed in Table (C.3).

**Table (C.3) : The out-of-scope list of the model card**

| # | Out of scope |
|---|---|
| 1 | Arabic sessions -- no Arabic-validated threshold exists; the system returns an indicator profile and no score |
| 2 | any picture other than the validated kitchen scene |
| 3 | recordings that fail the quality gate |
| 4 | staging, monitoring, or treatment decisions |
| 5 | any use as a diagnostic device |

## C.5 Limitations

The card states six limitations in prose, quoted here verbatim. Calibration: "Screening score, not a clinical probability: slope 1.289, intercept 0.138, Brier 0.199, largest predicted-vs-observed gap 0.151, confined to the top band (predicted 0.830 vs observed 0.981, n=54). The model understates risk at the top and never overstates it. Slope/intercept re-derived after the lock by an unpenalised fit of the stored out-of-fold vector; the previously reported 1.276/0.135 came from a penalised fit (results/reconstruction/calibration_slope_resolution.json)." Discrimination: "AUC 0.755 combined means that given one impaired and one healthy recording the model ranks them correctly about three times in four. At the deployed threshold overall accuracy is about 67 percent -- roughly one person in three is misclassified." Mild cognitive impairment: "Mild cognitive impairment is materially harder (0.629). Trained on Delaware alone the same architecture reaches only 0.547, an interval spanning chance (results/reconstruction/cross_corpus_transfer.json)." That limitation is diagnosed in section 5.12.1, and the successor answers it with the task-genre finding of section 5.25. External test-set history: "The Lu corpus was excluded from the training data of the final model and from every modelling decision after the lock. Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool. Both external figures are reported -- 0.821 (clean, Pitt-only model) and 0.853 (this model)." Population: "Trained on American English clinic recordings. Never validated on Libyan speakers, and never used with a patient in a real clinic." The block's own provenance note reads: "added after the lock -- the card previously had no intended-use or limitations section, and its external block omitted sensitivity, specificity and Brier."

## C.6 Known Issues And Amendment History

Table (C.4) reproduces the card's known-issues list and its documentation-update record. The first issue is recorded as resolved; the second is the parked timing module of section 6.2; the third is the top-band calibration deviation of section 5.4.

**Table (C.4) : Known issues and documentation updates recorded on the card**

| Kind | Entry |
|---|---|
| known issue | RESOLVED after the lock: TRAINING_PRIOR in risk_adjustment.py was 0.4721 (pre-lock 1,040 pool); recomputed and updated to 0.471125 = 465/987 (scripts/compute_training_prior.py -> results/reconstruction/training_prior.json). Earlier copies of this card listed it as open. |
| known issue | pause_features.py is implemented but not wired into the feature pipeline (parked in future_work/ after the lock; docs/IMPROVEMENTS.md - wiring it in would change the model Lu validated) |
| known issue | calibration deviates in the top predicted band (n=54): predicted 0.830 vs observed 0.981 (conservative direction; report output as a screening score) |
| documentation update | After the lock: known_issues entry 0 closed after the constant update; stale docstrings in risk_adjustment.py cleaned the same day (owner-approved). No model, threshold or metric changed. |
