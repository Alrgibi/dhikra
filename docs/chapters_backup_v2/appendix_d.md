# Appendix D — Reporting Guideline Self Assessment

This appendix assesses the thesis against the three current instruments for
studies of this kind: TRIPOD+AI for the reporting of clinical prediction
models [1], STARD-AI for the reporting of diagnostic accuracy studies using
artificial intelligence [2], and PROBAST+AI for risk of bias and
applicability [3]. The tables below state, topic by topic, what is
satisfied, what is partially satisfied, and what is not, with the section of the thesis that carries each answer; the item-by-item checklists are not reproduced, and this topic-level assessment is the record. An assessment of this kind is reported in full or it is decoration: three verdicts below
are *not satisfied*, and they are as informative as the rest.

## D.1 TRIPOD+AI

TRIPOD+AI is a 27-item checklist for studies developing or evaluating a
prediction model, whatever the modelling method [1]. Table (D.1) gives the
topic-level assessment.

**Table (D.1) : TRIPOD+AI self-assessment by topic**

| Topic | Verdict | Where, and why |
|---|---|---|
| Title and abstract | Satisfied | Front matter; the abstract states the target, the data, the model, the development and external figures with their intervals, and the external corpus's exposure |
| Background and intended use | Satisfied | Chapter 1: screening, not diagnosis; the deployment setting and the paper fallback are the design brief |
| Objectives, development and evaluation | Satisfied | Chapter 1; §3.1 and §3.9 separate the development pool from the one-shot external evaluation |
| Data sources and eligibility | Satisfied | §3.1–3.2 and the model card's exclusion list; corpus provenance and membership terms stated. Original collection dates of the archival corpora are carried by the corpus citations, not re-documented |
| Outcome (reference standard) | Satisfied, with a stated limit | Diagnostic labels as distributed by the corpora — clinical diagnoses, not re-adjudicated; the label heterogeneity of the impaired class is itemised in Appendix H.2 |
| Predictors | Satisfied | §3.3, Appendix A: all 64 defined, 63 distinct quantities disclosed |
| Sample size | Partially satisfied | No prospective calculation — the corpora bound the sample; n, participant counts and participant-clustered intervals are reported throughout, and a sample-adequacy probe is reported in Chapter 5 |
| Missing data | Satisfied | §3.2.2 missingness audit (maximum 0.012, mean 0.0002); median imputation inside the deployed pipeline |
| Analytical methods and internal validation | Satisfied | §3.6: participant-grouped stratified five-fold cross-validation, fixed seed; architecture in the model card |
| Class imbalance | Satisfied | Training prior 0.4711 stated and divided out; §3.12 |
| Fairness | Satisfied | The sex disparity is measured, reported first among the limitations, and §3.11 proves no monotone post-processing can repair it — a design requirement for the successor, not a patch |
| Model output | Satisfied | Calibrated probability; §3.12 derives the likelihood-ratio reading and the prevalence chain |
| Performance measures | Satisfied | Discrimination with participant-clustered intervals, calibration slope and intercept separately, operating points, and the locked external one-shot with its interval |
| Model specification and availability | Satisfied | The frozen model, its 64 columns and threshold 0.367 in the model card (Appendix C); the deployed artefact is the specification |
| Usability by intended users | Satisfied | Chapter 4: the application, the quality gate's refusal messages, and the paper fallback |
| Limitations and next steps | Satisfied | Chapter 5 limitations; Chapter 6 carries the specified successor and the corpus specification |
| Registration and protocol | Partially satisfied | The study as a whole was not prospectively registered; every post-lock analysis is pre-registered in committed driver docstrings with mechanical grading (§3.10), and the amendment record is disclosed (Appendix H.9) |
| Data and code availability | Partially satisfied | Corpora are redistributable only under TalkBank membership; derived results and scripts are committed, and the residue of uncommitted producing code is itemised and disclosed (§3.6, Appendix F) rather than implied absent |
| Ethics and funding | Satisfied | Secondary analysis of consented archival data under the corpora's governance; no new human data collected in this work; the prospective study's ethics live in the Libyan pilot protocol (Appendix B). The corpora's supporting grants are acknowledged in the front matter |

## D.2 STARD-AI

STARD-AI is a 40-item guideline for diagnostic accuracy studies using AI,
organised as title/abstract (items 1–2), introduction (3–4), methods (5–23),
results (24–32), discussion (33–35) and other information (36–40), with
fourteen AI-specific items [2]. Table (D.2) gives the assessment by section,
naming the AI-specific items where the thesis has a specific answer.

**Table (D.2) : STARD-AI self-assessment by section**

| Section | Verdict | Where, and why |
|---|---|---|
| Study design | Satisfied | §3.6 development protocol; §3.9 the locked one-shot external evaluation, its threshold fixed in advance |
| Ethics | Satisfied | As in Table (D.1): archival corpora under their own governance; the pilot protocol carries prospective ethics |
| Participants and dataset (items 7, 11–15) | Satisfied, one item not satisfiable | Eligibility at corpus and recording level (§3.1–3.2, model card exclusions); data source and annotation are the corpora's clinical diagnoses; preprocessing disclosed to the level of its audited defects (§3.2.1–3.2.2, Appendix G); partitioning (15b) is participant-grouped with a locked external set. **Capture devices and acquisition protocols (13, 14) cannot be reported**: the archival corpora do not document their recording equipment, and this is declared rather than approximated |
| Index test | Satisfied | The frozen 64-feature model, its architecture, threshold and versioned dependencies (model card); the transcription path and its train/serve mismatch stated (§3.2.1) |
| Reference standard | Satisfied, with the same limit as TRIPOD+AI | Clinical diagnosis as distributed; not re-adjudicated |
| Analysis | Satisfied | Participant-clustered intervals throughout (§3.6); calibration reported separately from discrimination; the five pre-lock scorings and the surviving exposure quantified (§3.9) |
| Fairness (23, 35) | Satisfied | The sex disparity in methods and discussion, with the §3.11 impossibility result |
| Results flow | Satisfied | Cohort tables with recordings and participants; the external confusion matrix cell for cell |
| Discussion | Satisfied | Limitations led by the specificity collapse and the sex gap; applicability argued |
| Commercial interests (39) | Satisfied | None |
| Dataset and code availability (40a) | Partially satisfied | As in Table (D.1) |
| External audit or evaluation (40b) | Partially satisfied | An adversarial external review of the draft claims — which caught the contamination §3.9 reports — and an external advisory review of the results; no formal independent audit of the deployed system has occurred, and none is claimed |

## D.3 PROBAST+AI

PROBAST+AI assesses quality, risk of bias and applicability in two parts —
model development (16 signalling questions) and model evaluation (18) — each
across four domains: participants and data sources, predictors, outcome, and
analysis, with applicability judged on the first three [3]. Table (D.3)
gives this work's self-assessment; a self-assessment is read as the author's
answers, not an independent rating.

**Table (D.3) : PROBAST+AI self-assessment by domain**

| Domain | Development | Evaluation | Applicability to the intended setting |
|---|---|---|---|
| Participants and data sources | Low concern within its frame: clinic-recruited archival cohorts, repeat visits handled by grouping | Low risk of bias for Lu as a cohort; the pool-composition exposure is an analysis-domain entry | **High concern, by design**: English-speaking clinic cohorts against an intended Arabic-speaking community setting — the gap Chapter 6 exists to close, stated rather than discovered |
| Predictors | Low after audit: the transcription artefact was found, measured at −0.0099, graded against a pre-registered band, and disclosed with its train/serve reading (§3.2.1, Appendix G) | Low: the artefact is effectively absent in the external corpus, which bounds artefact dependence | Moderate: transcript-derived predictors transfer only through the successor's language engine, whose evidential status §3.4 states exactly |
| Outcome | Moderate: clinical diagnosis, heterogeneous impaired class, itemised | Low: Lu labels verified during the build (Appendix G.7) | Moderate: the construct is cognitive impairment broadly, matched to the prior (Appendix H.2) |
| Analysis | Low: grouped folds, participant-clustered intervals, no in-fold leakage of preprocessing, calibration reported separately; the fold-grouping null measured (§3.6.1) | **The entry that matters most**: the external evaluation is one-shot, threshold fixed in advance, reproduced once — and its training pool's composition was chosen with knowledge of a score from that corpus. §3.9 quantifies the surviving exposure and both external figures are reported | — (applicability is not assessed on this domain) |

The overall self-assessment therefore reads: development at low to moderate
risk with every identified defect measured and disclosed; evaluation at low
risk of bias save the disclosed composition exposure, which is bounded; and applicability to the intended deployment setting at
high concern by design — the thesis's own position, since nothing in it is
validated in Libya and Chapter 6 says so in its first sentence.

