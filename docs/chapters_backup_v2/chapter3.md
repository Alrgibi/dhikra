# Chapter 3 — Methodology

Sections 3.1 to 3.5 cover the material — the corpora, the preparation of the
transcripts, the measures computed from them, and the task battery; sections
3.6 to 3.8 the evaluation protocol, the risk adjustment that converts a model
output into a statement about a person, and the quality gate; sections 3.9 to
3.12 governance and derivation. The last group is why this chapter is longer
than its counterparts: a speech-based screening result is easy to produce and
hard to trust, and what a reader must assess is not the number reported but
the number of decisions taken with knowledge of the data the number was
computed on. This work makes that quantity auditable — an external corpus
locked and scored once, a pre-registration practice applied to every post-lock
analysis, and a written record of the occasions on which both mechanisms
failed. A governance account that reports only successes is indistinguishable
from no governance account at all, so three of these sections report a
failure. Sections 3.11 and 3.12 are derivations rather than measurements,
placed here because they constrain what the results of Chapter 5 can mean.

---

## 3.1 Corpora

Five corpora were considered and three were used for development and external
validation, all three from DementiaBank, the dementia section of the TalkBank
archive, which distributes transcribed picture-description sessions under a
membership agreement. The Arabic pilot corpus is not a DementiaBank holding —
that archive has no Arabic section, an absence Chapter 6 returns to — but an
independent public dataset used for a single acoustic probe. Table (3.1)
states what each corpus contributed [1].

**Table (3.1) : The corpora, and the role each played**

| Corpus | Recordings | Participants | Role |
|---|---|---|---|
| Pittsburgh | 548 | 290 | Development pool; dementia target |
| Delaware | 439 | 291 | Development pool; mild-impairment target |
| **Development, combined** | **987** | **581** | Fitting, feature decisions, threshold |
| Lu | 53 | 53 | **Locked external test set**, scored once |
| Wisconsin Longitudinal Study | — | — | **Excluded**: 100% controls |
| Arabic pilot | 24 | 24 | Acoustic probe only; independent public dataset |

The exclusions matter more than the inclusions. The Wisconsin corpus contains
only healthy speakers, so pooling it makes corpus membership nearly equivalent
to class membership and a model can score highly by learning which archive a
recording came from; this was measured and is reported in Chapter 5. The Lu corpus was excluded from the training data of the final model and from every modelling decision after the lock. Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool. The reasons are given in section 3.9. Eight further DementiaBank corpora — Baycrest,
Baycrest-PPA, DePaul, Holland, Hopkins, Kempler, Lanzi and VAS — were obtained
and not used: the design required picture description with diagnostic labels
at a scale supporting cross-validated fitting, which Pittsburgh, Delaware and
Lu alone meet, and the eight were not audited individually against it. The
Arabic pilot sits outside the development pool and evaluated the
language-independent acoustic model only. **No Arabic-language model exists in
this work and none is claimed.**

---

## 3.2 Data Preparation

All three DementiaBank corpora are distributed in CHAT format, the TalkBank
transcription standard. Preparation consisted of parsing the files, separating
the participant's speech from the investigator's, stripping transcription
markup, and — for the Delaware corpus, whose sessions hold five tasks in one
file — splitting each file at its task boundaries. One parsing detail is
recorded because it silently destroys a variable most work on this corpus
depends on: the Pittsburgh corpus stores the Mini-Mental State Examination
score in the field the CHAT specification reserves for years of education, so
a parser that reads the specification rather than the corpus loses every
cognitive score in the archive while appearing to succeed [1].

### 3.2.1 A Transcription Convention That Correlates With Diagnosis

CHAT marks an omitted sound with parentheses, so a speaker who said *dryin'*
is transcribed `dryin(g)`. The transcript cleaner stripped most CHAT markup
and not this one, so the parser split the form into four tokens and never
recognised the verb — and the affected words are exactly the action verbs the
information-unit scorer looks for. The forms occur in 58.9% of
Pittsburgh transcripts at a rate that is **differential by class** — 3.18 per
hundred words among the impaired against 1.44 among controls — discriminating
alone at an AUC of 0.6908, above most individual deployed features. The
Delaware and Lu corpora settle what it is: the same convention, at different
sites, occurs an order of magnitude less often and discriminates at chance,
and a genuine phonetic property of impaired speech would not be ten times
rarer in another cohort of impaired speakers. **This is a Pittsburgh
transcription practice that correlates with diagnosis.** Appendix G carries
the full audit.

It survived a guard that was correct in principle. The deployed feature set
contains no markup-derived features, because transcription convention alone
separates *healthy* speakers of different corpora at an AUC of 0.930, as
Figure (3.1) shows. **That exclusion removed markup features; it did not
remove markup from the transcript text the linguistic features are computed
on.**

**Figure (3.1) : The corpus effect. Left: two groups of healthy speakers from
different studies are separable at AUC 0.930 on the full feature set, falling
to 0.783 once CHAT transcription markup is removed — the finding that made
naive corpus pooling invalid. Right: the same comparison restricted to the 64
deployed features, none of which are CHAT markup; the median absolute shift is
0.22 and only six features exceed 0.5.**

The cost was measured: re-extracting all 64 features from
corrected text, with architecture, folds and seed unchanged, moved the
Pittsburgh AUC from 0.8095 to 0.7996 — **−0.0099 against a pre-registered
material band of −0.01**. The registered grade is *negligible*, by one
ten-thousandth, and reporting the grade without the margin would be exactly
the rounding this work exists not to perform. The application transcribes with
a recogniser emitting standard orthography, so the form **cannot occur at
inference** and 0.7996 is the closer estimate of what the deployed system
receives. The extractor was **not corrected**: changing the features the
frozen model receives would forfeit an unrepeatable external validation.

The external corpus was checked for the same pattern, under a check declared
descriptive before it ran — counting a text pattern is metadata inspection of
the same category as reading the header fields that supply ages and diagnoses
— and **eight** such forms exist in the entire corpus. The inference favours
this work and is volunteered: the model was fitted where the artefact is
common and correlates with diagnosis, and evaluated where it is effectively
absent. **Had it depended on that channel it would have lost performance
externally; it produced its highest figure there instead.**

### 3.2.2 Two Features That Measure Nothing

A feature-health audit found the deployed set clean — maximum missingness
0.012, mean 0.0002 — with two exceptions. The two filler-count features are
zero in 99.3% of transcripts, because CHAT encodes filled pauses with a prefix
the cleaner strips *before* the counter runs, and a parsing-order interaction
disabled them silently. Whether that costs anything was checked: the parser captures the same information separately, in 81.8% of
Pittsburgh transcripts, and its discriminative value there is an AUC of
0.4925, which is chance. Both halves are reported — a parsing-order defect
disabled two features, and the marker they were built for does not
discriminate in this cohort in any case.

---

## 3.3 Feature Extraction

A total of 117 measures were implemented across five families — the instrument's full measurement set — of which 64 are
deployed. The reduction is not a selection on performance; it is the set
computable from a transcript alone, because the deployed model must run where
no usable audio exists. Table (3.2) gives the composition.

**Table (3.2) : The 64 deployed features by family**

| Family | Columns | What it measures |
|---|---|---|
| Lexical, syntactic, fluency | 24 | Word and sentence counts, lexical diversity, part-of-speech rates, dependency distance, tree depth, repetition |
| Information content | 31 | Presence of each of 23 canonical scene units, category totals, the unit total, three derived efficiency measures |
| Discourse semantics | 9 | Sentence-to-sentence and global coherence from distributional word vectors, dispersion, looping |

Two qualifications travel with the table. The 64 columns are **63 distinct
quantities**, because the information-unit proportion is the unit total
divided by a constant, and two of the 24 lexical columns are the inert
features of section 3.2.2; neither was removed, because any change to the
frozen feature vector would void the external validation. Acoustic measures
were implemented and evaluated but are **not deployed**: they require clean
audio, and a system that produces no result without it fails the setting this
work targets. The information-content family follows the established
information-unit inventories for this task, scoring the presence of 23
canonical scene units [2, 3].

---

## 3.4 The Arabic Engine

The marker most often reported for English does not transfer, and the reason
is grammatical rather than clinical. In English, word-finding difficulty
surfaces as pronoun overuse: a speaker who cannot retrieve *the boy* says
*he*. Arabic is a pro-drop language, in which the verb carries person and
number and the subject pronoun is normally omitted; overt pronouns exist — as
emphatic subjects, object and possessive clitics — but their baseline rate
sits on a different scale for grammatical reasons. The English pronoun-to-noun
ratio is therefore **not cross-linguistically comparable**: not that the
measure cannot be computed, but that its normal value means something else.

The replacement proposed here is a referential deficit index built from
demonstratives and semantically vague nouns relative to specific naming, on
the reasoning that a pro-drop language expresses referential imprecision
through the constructions it does use. **Its evidential status must be stated
exactly**: implemented and verified on constructed examples; never computed on
the speech of a diagnosed patient in any language; discriminative validity
untested — the 24-recording Arabic pilot evaluated the acoustic model, not
this index. It is a literature-consistent hypothesis that the protocol of
Chapter 6 is designed to test, not an established marker.

---

## 3.5 The Task Battery And Why Its Order Changed

The battery administers story recall, procedural discourse, picture
description, verbal fluency and Qur'anic recitation. Until the ordering was revised it led with picture description, on the reasoning that picture description is what
the deployed model reads. **That ordering was withdrawn on evidence reported
in Chapter 5.** On the one corpus permitting a within-participant comparison,
picture description is the weakest of five tasks for mild cognitive impairment
and performs at chance, while two discourse tasks administered together beat
three picture-description tasks by +0.0788, participant-clustered interval
[0.0042, 0.1579].

The battery therefore leads with **story recall** — the Craft Story paradigm,
in which the examiner supplies the narrative so no cultural knowledge of a
story is required — and **procedural discourse**, which needs no stimulus
material and is the only task that survives a paper fallback intact. **Picture
description is retained unchanged** for the dementia target, where it works
and where it alone has an externally validated model behind it. Ordering
administration is not changing what is scored, and only the first was done.

Elicitation is fixed and logged — a verbatim prompt, an enforced maximum
duration, a stated re-prompt rule, elicitation time and probe count recorded
per session — because word count is the strongest single marker for mild
impairment on connected discourse, and variable administration would make the
battery's primary signal an artefact of the examiner. Chapter 5 supplies the
other half: a minimum-length filter was tested and **refused**, so thin
samples must be prevented at elicitation rather than removed afterwards. The
Qur'anic task is **exploratory** throughout, with six documented confounders,
and is not claimed as a validated biomarker.

---

## 3.6 Validation Protocol

Cross-validation folds are stratified by class and **grouped by participant**,
five folds, fixed seed: the Pittsburgh corpus follows the same people across
annual visits, so a fold assignment that ignores participant identity can
place one person's recordings in both training and test. Age and sex matching
were applied where a matched analysis is reported, repeated across ten seeds
so no result depends on one lucky pairing.

The same clustering governs every uncertainty statement: each confidence
interval in this thesis is **participant-clustered**, resampling participants
rather than recordings, because repeat visits are correlated within a person.
The resampling unit of every interval-bearing result file is audited in a
committed registry (`results/BOOTSTRAP_UNITS.json`), which declares the five
files whose units could not be verified because their producing code was not
committed; every headline figure traces to a verified unit or to one that
coincides with the participant by construction.

### 3.6.1 What Participant Grouping Actually Buys

Much published work on this corpus uses stratified folds without grouping.
The claim that the two protocols measure different things was **replaced with
a measurement**, on the principle that a methodological claim which can be
tested and is not tested is an opinion. Everything was held constant except
the splitter, as Table (3.3) reports.

**Table (3.3) : Grouped against ungrouped folds, everything else identical**

| Splitting protocol | AUC | Test recordings sharing a participant with training |
|---|---|---|
| Stratified, grouped by participant | **0.8228** | 0.0% |
| Stratified, not grouped | 0.8203 | **68.4%** |
| Difference | **−0.0025** | |

The pre-registered threshold for demonstrating an advantage was a gain of at
least 0.02 to the ungrouped arm; it came in at −0.0025 and the registered
grade is *not demonstrated*. The opportunity for leakage was overwhelmingly
present and the model did not take it. The explanation is already in this
work: visit-to-visit agreement among control participants is **0.465**, so a
person's own two recordings barely resemble each other and memorising a
participant at one visit buys little at the next.

Three conclusions follow, and the third takes the most discipline. Participant
grouping **remains correct practice**: whether a risk materialised is not the
test of whether guarding against it was right. This work **may not claim
published figures are inflated by fold leakage**: capacity is the uncontrolled
variable — a tree ensemble over 64 aggregate features has far less ability to
memorise a speaker than a transformer over raw text — so Chapter 2's
comparison rests on the external-validation column, not the fold-protocol
column. And **the null is reported prominently rather than buried**: this is
the work testing for an advantage it expected, failing to find it, and
declining to claim it.

---

## 3.7 Risk Adjustment

The model output is a screening score: a development-calibrated probability estimate conditioned on the class balance of the training pool, 465 impaired recordings in 987, or 0.4711, and almost nobody is screened at a prevalence of 47%. The risk-adjustment stage therefore divides out the training prior, applies an age-specific population prevalence, a multiplier for why the person is being tested and one for family history, and returns a context-adjusted estimated risk — not a probability clinically calibrated for Libya. Section 3.12 derives the chain; Appendix H holds the
evidence base for every constant, the prevalence and multiplier tables, and
the property-based verification. Two parameters changed during this work, and
each carries a methodological point that generalises.

**One referral multiplier was retained and one removed.** The retained
multiplier is ×2.5, applied when the person or their family has noticed a
change. It was asserted as an engineering assumption before any source was
sought, and support was found afterwards; those words are the honest
description and are used deliberately, since a published meta-analysis gives a
positive likelihood ratio of 2.29 for the same evidence and agrees with the
asserted figure within rounding [4, 5, 6].

The removed multiplier is ×4.0 for clinician referral, and **it was not
removed because the evidence went against it** — the available indirect
comparison implies an odds ratio of roughly 4 to 8 once the clinic cohorts'
higher mean age is allowed for [7, 8, 9, 10, 11].

It was removed because **referral is not a diagnostic test and has no stable
operating characteristics**: the same national audit that yields the highest
of those figures found dementia yield ranging from 22% to 100% across 85
services, in one country, in one year. A referral rate is a local policy
variable, and no value calibrated on British or Dutch memory clinics would
transport to a setting where referral pathways for cognitive complaint are
largely absent. **A quantity can be well evidenced in direction, large in
magnitude, and still not be a parameter, because it has no stable referent**
[9].

A clinician-referred session now receives the same ×2.5 as a reported concern,
declared as a **floor rather than an estimate**: nearly everyone referred also
reports a change, and the indirect evidence says the true uplift is larger.
**Removing an overstated figure without saying so would simply have converted
it into an understated one — the same error with the sign reversed.** Two
structural points govern the chain: the referral contexts are mutually
exclusive branches, one per session, since applying both would double-count
the same information; and a multiplier and its baseline are a matched pair —
the ×1.0 baseline presumes an unselected population, so against an
age-conditioned prior the implied clinic uplift shrinks from roughly eight to
roughly four to five.

Family history enters as a multiplier of 1.73 for one affected first-degree
relative and 3.98 for two or more, with a reported *no* leaving the prior
unchanged rather than lowering it, because in a low-diagnosis setting *no*
very often means *nobody in this family was ever diagnosed* [12].

That branch carries a defect which is disclosed rather than patched: the
published figures are **relative risks**, the chain multiplies prior **odds**,
and the two diverge once baseline risk is large, so the composition
**overstates familial risk at the oldest ages**. The prior cap of 0.85 is
**the symptom rather than a prudence measure**, binding in exactly 4 of 135
prior combinations — all two-first-degree-relative cases at ages 80 and above
with a referral uplift — and in none without a referral multiplier. Appendix H
sets out the defect and its direction across the age range, the reason the
arithmetic is left unpatched, and an objection to the family-history branch
itself that was tested and withdrawn.

The chain was verified mechanically over 1,440 cases against nine properties,
**all 1,440 passing with zero failures**; the same speech score of 0.90 yields
a posterior of 4.8% at age 25 and 92.5% at age 85. The size of what was
removed is reported so it can be judged: a 72-year-old scoring 0.70 receives a
posterior of 0.316 with no context multiplier and 0.536 under the ×2.5 uplift,
and would have received 0.649 under the retired ×4.0.

---

## 3.8 Quality Control

A recording that cannot support the measures computed from it is refused
rather than scored. The gate estimates signal-to-noise ratio, clipping and
duration and returns a refusal with a stated reason. Its thresholds are
empirical, set from the degradation study of Chapter 5, in which real
recordings were subjected to eight controlled degradations and each feature
family's stability measured against the clean original. Background noise is
the condition that matters and it attacks pause measurement first; at a 10 dB
signal-to-noise ratio extraction fails outright, which is the basis for the
refusal threshold.

---

## 3.9 External Test Set Governance And The Failure That Produced It

This is the methodological centre of the chapter, written in the order below
because a reader is entitled to meet the rule working before meeting the
reason it exists.

### 3.9.0 The Day The Lock Rule Changed A Decision

A defect was **found**: the Bayesian chain's likelihood-ratio step assumes a
calibrated score, and Chapter 5 shows the score is not calibrated. The
**standard correction was derived** — Cox logistic recalibration, two
coefficients, no tuning, strictly monotone and therefore incapable of
disturbing any locked result — and a **transfer test was pre-registered**: fit
on one development cohort, apply to the other, both directions, criteria
written first. **It failed**, moving the Delaware slope from 0.823 to 0.543
and the Pittsburgh slope from 1.516 to 1.841, with the Brier score worsening
both ways. Why it failed is the finding: **the two development cohorts are
miscalibrated in opposite directions**, so any pooled slope averages two
numbers pointing opposite ways and no single map fits both — the
miscalibration belongs to the cohort, not the model.

The obvious test of the correction was the locked corpus, and that was
forbidden: the pre-registration declared, before execution, that the locked
corpus would be scored descriptively afterwards and **would not enter the
decision whatever it showed**. On that corpus the raw slope is 1.886, the most
compressed of the three, and the development correction moves it to 1.464 —
*toward* 1, passing both criteria the development arms had failed. **Had the
locked corpus been consulted, the correction would have been applied. The rule
that forbade consulting it changed the decision, and changed it rightly** — a
case in which the rule and the analyst's judgement diverged and the rule was
correct, which is more than arguing that a rule is prudent.

### 3.9.1 What Went Wrong

The Lu corpus was obtained to serve as an external test set, and in the hours before the lock it was scored five times while training configurations were compared. The first scoring, of a Pittsburgh-trained model, gave **0.821** before any modelling decision had been informed by the corpus, and that figure is clean. A subsequent scoring of a Pittsburgh-plus-Delaware model gave **0.859**,
and **that comparison is what admitted Delaware to the training pool**; a
corpus used to choose between training configurations is a model-selection
set, not a held-out test set. A third error followed: the corpus was added to
the training pool, and the cross-validated figure obtained *within* that pool,
0.849, was reported as external validation. Both claims cannot be true at once.

### 3.9.2 How It Was Caught And The Correction

It was not caught by an internal check. An adversarial external review of the
draft claims identified the contamination the same day. **This work's own
governance did not catch it**, and that is stated plainly rather than
presenting the correction as foresight.

The corpus was then locked out. The final model was retrained on the
development pool alone, 987 recordings from 581 participants, the operating
threshold was fixed at 0.367 on development data **before** the run, and the corpus was scored exactly once, after the lock: **AUC 0.8533, 95% confidence interval
[0.7371, 0.9458], sensitivity 96.2% at 25 of 26, specificity 33.3% at 9 of
27.** The specificity collapse is reported in full because exposing it is what a locked test set is for; its diagnosis — a threshold referenced to the wrong distribution, with a remedy analysed but not deployed — is in sections 5.15 to 5.19. Subsequently the evaluation was reproduced under a protocol permitting one execution and no decision in
either direction; the AUC matched to ten decimal places and the confusion
matrix cell for cell, and a tombstone file now blocks any further run.
Figure (3.2) places this sequence alongside every approach that was tested and
rejected.

**Figure (3.2) : The validation story. The left-hand column is the sequence of
decisions that produced the reported result; the right-hand column is every
approach tested and rejected, attached to the stage at which it was tested.
The lock is marked because it divides the work in two:
everything above it could be revised, and nothing below it was. Each rejection
is reported in full in Chapter 5, section 5.8.**

### 3.9.3 What Each External Figure Validates

Both external figures are reported, because each validates something the other
does not, as Table (3.4) states.

**Table (3.4) : The two external figures**

| Figure | Model | What it validates | What it does not |
|---|---|---|---|
| 0.821 | Pittsburgh only | Genuine external generalisation, uncontaminated: no decision had yet been informed by this corpus | Not the deployed system — a smaller model on a smaller pool |
| **0.8533** [0.7371, 0.9458] | Deployed model | The deployed system, on data absent from its training, at a threshold fixed in advance, scored once | **Not free of the earlier exposure**: its training pool's composition was chosen using a score from this corpus |

The two sit 0.032 apart on the same 53 recordings, and 0.821 falls inside the
confidence interval of 0.8533. That proximity **bounds** how large the
selection effect can be — a pool choice that had badly inflated the external
estimate would not leave the two figures this close — though the gap mixes
selection with the genuine benefit of more training data and so bounds their
sum. **One architectural decision** — which corpora entered the training pool
— was made with knowledge of a score from the external corpus, and nothing
else was: no hyperparameter, no operating threshold, no feature selection, no
calibration method, no model form. That is a fact about the *scope* of the
contamination, recorded after the problem was volunteered; it is not a defence, and it does not shorten the exposure history recorded in section 3.9.

The pooling decision was also re-examined without touching the locked corpus.
The exact pre-lock comparison cannot be reproduced Lu-free — it needs a third
corpus containing both classes, the Wisconsin corpus is all controls, and Lu
is spent — so a weaker, Lu-free proposition was pre-registered and tested
instead: whether the two development corpora are mutually informative. They
are, in both directions; section 5.12 reports the transfer figures.

---

## 3.10 Preregistration As A Working Method Including Where It Failed

The pattern used throughout the post-lock work is uniform: the criteria,
tolerances and stop rule for a run are written into the driver script's
docstring and committed **before the run**, the grading is mechanical, and
failure is reported, not iterated away. The interpretive direction is
registered too — for the acoustic protocol test, failure meant *the protocol
is not confirmed*, never *the model is wrong*. Two worked examples show the
machinery catching a defect in a **rule** and a defect in the **analyst**.

**A pre-registered check caught the analyst's own bug.** The probe of the
referential deficit index registered a provenance check with nothing to do
with the hypothesis: the recomputed pronoun-to-noun ratio must reproduce the
committed feature to within one part in a million on at least 99% of
recordings, failing which the run is void. **It failed**, reproducing the
committed feature on 36% of Pittsburgh and 82% of Delaware recordings; the
diagnosis, set out in Appendix H, ruled out the tagger, the environment and
the committed extractor in turn, the defect was in the **new script**, and
fixing it **honoured** the pre-registration rather than relaxing it. What must
not be smoothed over is that one cohort's result had appeared in terminal
output before the fix; that is recorded in the driver's registration history
in those words, with the reasons it does not void the run and with the
sentence *the reader is entitled to weigh that*. **The check that caught it was not the interesting one**: it was a
provenance formality nobody expected to fail, and the value of
pre-registration is concentrated in the checks written when the author is not
worried.

**A criterion that failed on contact with the data.** The cross-corpus
transfer analysis registered two criteria. The first, that transfer exceeds
chance, held. The second was a retention ratio — transfer AUC over the
within-corpus reference of the test corpus, at least 0.90 strong, below 0.75
weak. A ratio silently assumes its denominator is a working reference, and in
one direction it is not: Delaware trained on itself scores 0.5474, an interval spanning chance (the finding is owned by section 5.12.1, and its remedy — a different elicitation genre — by section 5.25), so the ratio came out at 1.18 and the registered rule stamped
it **strong** — a meaningless verdict, since nothing can retain 118% of a
reference that does not work. **The criterion was left exactly as registered
and the arm was not re-run**, the defect recorded in two places: **a rule
rewritten after seeing the result is the result wearing a rule's clothes.**
The first criterion passed on its own terms, so the transfer finding stands
and only the retention framing is void. **Neither failure was found by a
reviewer; both were found by the machinery, which is the only test of whether
the machinery is real.**

### 3.10.1 Three Underspecifications In Seventeen Registered Runs

Three registrations required amendment on contact with the data — the
retention criterion above; the tokenisation of the referential-index probe;
and the label rule of the task-count curve, where 6.25% of participants change
label across visits. Appendix H tabulates each with its timing relative to
seeing the result, which is the fact a sceptical reader needs. They share a
shape, and the shape is the finding: in none of the three was the
defect in the hypothesis, the criterion band or the analysis set — the three
things a registration template asks for. **A pre-registration protects the
parts of a design its author already knows are contestable; it does not
protect the parts they have not thought of, and in practice those are where
the defects are.** The working discipline this produced is four rules, stated
with their derivations in Appendix H: never adjust the rule to reach the
assertion; record when an amendment was made relative to seeing the result;
report both versions whenever an amendment changes an answer; and register a
sanity gate on every derived quantity an analysis depends on, including its
labels. A fourth case, reported in full in Appendix H, extends the last rule
to comparisons: a claim that a hand-countable feature matched the calibrated
ensemble **reversed sign once both sides were estimated alike**, because one
side had been selected as the best of 43 on the same participants and the
other not selected at all. The defect was in the comparison, not the
measurement, and the rule extends to refusing any comparison whose sides were
produced by procedures with different numbers of free parameters. It was
caught only because the claim was uncomfortable enough to invite challenge; a
comfortable version of the same error would still be in this work.

---

## 3.11 Monotone Transforms Move Calibration And Never Discrimination

Three separate methodological questions in this work have the same answer, and
stating the reason once turns three empirical findings into one argument with
three corollaries.

**The lemma.** The area under the receiver-operating-characteristic curve is a
function only of the *ranking* a score induces within the population being
ranked, so any strictly monotone transform applied uniformly to a group leaves
every within-group ranking, and therefore every within-group AUC, exactly
unchanged. Discrimination is a property of how far two distributions overlap;
recentring and rescaling move both distributions together.

Three corollaries follow. Cox logistic recalibration is strictly monotone, so
it was never a candidate for improving separation, only for repairing
probability estimates. Sex-stratified thresholding cannot close a sex gap in
discrimination: it equalised specificity at 0.799 against 0.798 and *widened*
the sensitivity gap from 0.176 to 0.348, because moving a threshold within a
group redistributes errors rather than reducing them. And normative
normalisation against local healthy controls cannot close it either: z-scoring
the information-unit total within sex leaves the within-sex AUCs identical to
four decimal places, moving only the pooled figure, and moving it *down* by
0.0015. **These were not close calls; they are the lemma being observed.**

The positive half matters more. The lemma says what normative normalisation
*is* good for — calibration and thresholds, which are exactly ranking-position
questions. Control-referenced thresholding, this work's principal
methodological contribution, is a normative normalisation, and it works
precisely because a threshold is a calibration property rather than a
discrimination property: **the lemma is not a limitation on the contribution
but the reason it is correctly aimed.** It also settles the sex gap: if no
monotone transform can close it, only a different feature set or model can,
and under the frozen-model constraint neither is available, so the gap is
reported, explained mechanistically in Chapter 5, and carried into Chapter 6
as a design requirement rather than repaired by a step that provably cannot
repair it.

---

## 3.12 The Calibration Architecture Is A Density Ratio Likelihood Ratio

The system converts a speech sample into a probability, then re-applies a
deployment-specific prevalence. The chain is verified mechanically but has so
far been justified operationally rather than derived; deriving it makes the
prevalence-independence claim provable rather than asserted.

A calibrated classifier trained at prevalence *π*₀ outputs *p*(*x*). Dividing
out the prior it was trained with gives the Bayes factor the speech sample
contributes:

> **LR(*x*) = [ *p*(*x*) / (1 − *p*(*x*)) ] × [ (1 − *π*₀) / *π*₀ ]**

By construction this equals the ratio of the class-conditional densities,
*f*₁(*x*) / *f*₀(*x*) — the **density ratio** between how impaired and healthy
speakers distribute over the feature space. Deployment then applies the local
prior, so the posterior odds are LR(*x*) × *π* / (1 − *π*). **Prevalence
independence becomes a theorem:** neither class-conditional density is a
function of *π*, so LR(*x*) is invariant to prevalence, and every
prevalence-dependent quantity — predictive values, the posterior bands — is an invariant evidence term multiplied by a local prior. In deployment the likelihood ratio functions as an empirical evidence estimator rather than an exact density ratio: it inherits whatever miscalibration *p*(*x*) carries, and with the development calibration slope above one (section 5.4.1) it conservatively underweights extreme values, understating strong evidence rather than overstating it.

**Cox recalibration decomposes into two distinct failures**, which must never
again be reported as one number. Recalibration fits logit *p*\* = *a* + *b* ·
logit *p*, and Table (3.5) gives what each coefficient means here.

**Table (3.5) : The two recalibration coefficients, read as likelihood
ratios**

| Parameter | What it rescales | What a departure means |
|---|---|---|
| *b* | The **log-likelihood-ratio** — the strength of the evidence | *b* ≠ 1 means the model over- or under-states what a given speech sample is worth |
| *a* | The **implied prior** | *a* ≠ 0 means the training prevalence embedded in the output is wrong for this population |

That is the sharp reading of the calibration result. Pittsburgh returned a
slope of 1.516 and Delaware 0.823 — not merely that calibration does not
transfer, but that *evidence strength itself is corpus-dependent and in
opposite directions*. One global recalibration cannot repair two errors of
opposite sign, which is why section 3.9.0's pre-registered decision was that
the correction does not transfer: **the lock rule and the mathematics reached
the same conclusion independently.**

**The multipliers are separate likelihood ratios**, and multiplying likelihood
ratios is exactly correct provided the sources are conditionally independent
given class. That proviso is the whole of the assumption, and it was tested
where it is most at risk. Age is recoverable from the deployed features at
*R*² = 0.994, so a reader is entitled to suspect that multiplying an
age-specific prevalence onto the model's evidence double-counts age. Measured
on the 987 development recordings, it does not: **within each class the
model's evidence is approximately age-flat**, and the residual drift — a
factor of 0.87 on the likelihood ratio across a twenty-year span — runs the
wrong way for double-counting; the measurement is reproduced in Appendix H.
**The information being present is not the same as the information being
used**: age being reconstructable from the feature vector is a statement about
information content, not a demonstration that the classifier routes its
decision through age, and here it demonstrably does not. The age prior may
therefore be applied on top of the model's likelihood ratio, and the
age-matched training design intended to guarantee that is confirmed to have
worked.

Control-referenced thresholding and the likelihood ratio are complementary
rather than competing. A threshold at a fixed percentile of the local
healthy-control distribution is a threshold on the control distribution
function — it fixes the false-positive rate by construction and needs no
prevalence estimate — while the likelihood ratio supplies what a percentile
cannot, how much evidence a given sample carries, with prevalence entering
only at the final step. **The operating point is set by the control
distribution; the reported risk is set by the likelihood ratio and the local
prior. Two mechanisms, two jobs, no overlap.**

---

**References Cited In This Chapter.** Numbering is local to this draft and is merged into the thesis-wide IEEE list at assembly; this is scaffolding, not a thesis heading, which is why it carries no section number.
Numbering is local to this draft and is merged into the thesis-wide IEEE list
at assembly. Sources [4] to [12] are the risk-adjustment evidence base and are
reproduced in full in Appendix H.

1. B. MacWhinney, *The CHILDES Project: Tools for Analyzing Talk*, 3rd ed.
   Mahwah, NJ: Lawrence Erlbaum, 2000. (TalkBank / DementiaBank; membership
   agreement.)
2. K. M. Yorkston and D. R. Beukelman, "An analysis of connected speech samples
   of aphasic and normal speakers," *J. Speech Hear. Disord.*, vol. 45, no. 1,
   pp. 27–36, 1980.
3. M. L. Nicholas and R. H. Brookshire, "A system for quantifying the
   informativeness and efficiency of the connected speech of adults with
   aphasia," *J. Speech Hear. Res.*, vol. 36, no. 2, pp. 338–350, 1993.
4. A. J. Mitchell, "The clinical significance of subjective memory complaints in
   the diagnosis of mild cognitive impairment and dementia: a meta-analysis,"
   *Int. J. Geriatr. Psychiatry*, vol. 23, no. 11, pp. 1191–1202, 2008,
   doi:10.1002/gps.2053.
5. A. J. Mitchell, H. Beaumont, D. Ferguson, M. Yadegarfar and B. Stubbs, "Risk
   of dementia and mild cognitive impairment in older people with subjective
   memory complaints: meta-analysis," *Acta Psychiatr. Scand.*, vol. 130, no. 6,
   pp. 439–451, 2014.
6. K. E. Pike, M. J. Cavuoto, L. Li, B. J. Wright and G. J. Kinsella,
   "Subjective cognitive decline: level of risk for future dementia and mild
   cognitive impairment, a meta-analysis of longitudinal studies," *Neuropsychol.
   Rev.*, vol. 32, no. 4, pp. 703–735, 2022.
7. F. Ronner *et al.*, "Diagnostic outcomes in a primary-care memory pathway,"
   *BJGP Open*, 2025, n = 651.
8. J. Blane *et al.*, "The Oxford Brain Health Clinic: case mix and diagnostic
   yield," *Sci. Rep.*, vol. 15, art. 7765, 2025, n = 313.
9. NHS England, *2019 National Memory Service Audit*, 85 services, n ≈ 3,700
   aged 65+.
10. J. J. Manly *et al.*, "Estimating the prevalence of dementia and mild
    cognitive impairment in the US: the Health and Retirement Study Harmonized
    Cognitive Assessment Protocol," *JAMA Neurol.*, vol. 79, no. 12, p. 1242,
    2022.
11. A. Börsch-Supan *et al.*, "Prevalence of cognitive impairment in Europe:
    SHARE-HCAP," *Sci. Rep.*, vol. 15, art. 14024, 2025, n = 47,773.
12. L. A. Cannon-Albright *et al.*, "Relative risk for Alzheimer disease based on
    complete family history," *Neurology*, vol. 92, no. 15, pp. e1745–e1753,
    2019.
