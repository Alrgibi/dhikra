# Appendix H — The Risk Adjustment Evidence Base And The Two Preregistration Diagnoses

This appendix holds, in full, the material that section 3.7 states in summary
— the evidence behind every constant in the risk-adjustment chain, the tables
the chain is built from, and its mechanical verification — and the two
diagnostic records that section 3.10 reports in summary: the tokenisation
defect caught by a registered provenance check, and the comparison defect that
reversed a claim's sign. Sources are cited by their numbers in the thesis-wide reference list.

## H.1 The Chain And Its Verification

The chain divides the training prior out of the model's calibrated output
(`TRAINING_PRIOR` = 0.471125, being 465 impaired recordings of 987, recomputed
on the locked pool), applies the age-band prevalence of Table (H.1), applies
one referral-context multiplier and one family-history multiplier on the prior
odds, caps the effective prior at 0.85, and returns a posterior. After the ×4.0 removal the chain was re-verified mechanically over a
1,440-case grid — twelve ages, three contexts, five family-history states and
eight speech scores — against nine registered properties: monotone in speech
score; monotone in age prevalence; population context never exceeding the
concern context; the Bayes identity; neutrality at `TRAINING_PRIOR`; the
posterior bounded in (0, 1); the effective prior bounded by the cap; the
concern and clinical contexts identical with the clinical branch flagged as a
floor; and no surviving ×4.0 anywhere. All 1,440 cases passed with zero
failures (`results/reconstruction/bayes_chain_check.json`). The headline
examples: the same speech score of 0.90 yields a posterior of 4.8% at age 25
and 92.5% at age 85, and a 72-year-old scoring 0.70 receives 0.316 at ×1.0,
0.536 at ×2.5, against 0.649 under the retired ×4.0.

## H.2 Age Band Prevalence


The prior must match what the model detects, not a narrower condition: the
training pool's impaired class contained 234 probable-Alzheimer's, 42 MCI, 21
possible-Alzheimer's, 5 vascular and 3 memory-clinic cases, so the instrument
detects cognitive impairment broadly and the correct prior is the prevalence
of MCI plus dementia. An earlier version used dementia-only prevalence and
systematically understated risk, because MCI is roughly twice as common as
dementia at the ages that matter most for early detection. Table (H.1) gives
the deployed bands.

**Table (H.1) : Age-band prevalence of MCI plus dementia, as deployed**

| Age band | Combined prevalence | Basis |
|---|---|---|
| 0–40 | 0.005 | Degenerative impairment rare at this age; judgment, recorded in `DESIGN_RATIONALE.md` |
| 40–50 | 0.015 | Judgment, as above |
| 50–60 | 0.060 | Community MCI studies from age 50 upward |
| 60–65 | 0.077 | MCI 6.7% [13] plus early-onset dementia [14] |
| 65–70 | 0.110 | MCI 8.4% [13] plus dementia ≈3% [14] |
| 70–75 | 0.150 | MCI 10.1% [13] plus dementia ≈5% [14] |
| 75–80 | 0.250 | MCI 14.8% [13] plus dementia ≈10% [14] |
| 80–85 | 0.420 | MCI 25.2% [13] plus dementia ≈17% [14] |
| 85+ | 0.550 | MCI ≈35% plus dementia 33.4% [14], overlapping |

## H.3 The Retained Multiplier Of 2.5


The ×2.5 concern multiplier was asserted as an engineering assumption before
any source was sought, and support was found afterwards — the true order of
events, stated as such. The supporting derivation: Mitchell's cross-sectional
meta-analysis [4] — cross-sectional being the right object for a *prevalence*
prior — reports subjective memory complaint in 39.8% of those with any
cognitive impairment against 17.4% of healthy elderly (the paper's own
relative risk 2.3). Positive likelihood ratios derived from its published
sensitivity and specificity: **2.29 for MCI-or-dementia**, 2.85 for MCI alone
(sensitivity 37.4%, specificity 86.9%), 3.03 for dementia alone (43.0%,
85.8%). Two longitudinal meta-analyses corroborate the magnitude without
being the derivation: Mitchell et al. 2014, RR 2.07 on n = 29,723 [5], and
Pike et al. 2022, OR 2.48 and HR 1.90 on n > 74,000 [6]. Caveats run both
ways: Mitchell's specificity is computed largely against healthy controls,
which inflates the likelihood ratio, while a person who presents *because*
they noticed a change is more strongly selected than a survey respondent, so
2.3 is plausibly a floor.

## H.4 The Removed Multiplier Of 4.0


No likelihood ratio and no within-study comparison of memory-clinic referral
against an unselected population could be found. The available evidence is an
indirect between-study comparison: clinic case-mix studies give
MCI-or-dementia at 77.5% (Ronner et al., n = 651 [7]), 79.3% (Blane et al.,
n = 313 [8]) and 84% (NHS England audit, 85 services, n ≈ 3,700 aged 65+
[9]), against population prevalence of 32% (Manly et al., n = 3,496 [10]) and
35% (Börsch-Supan et al., n = 47,773 [11]) — an odds ratio of 6.4 to 11.2
unadjusted, or roughly 4 to 8 once the clinic cohorts' higher mean age (≈78)
is allowed for. The indirect evidence therefore says ×4.0 was, if anything,
too low; the multiplier was removed anyway because the same audit that yields
the 84% figure found dementia yield ranging from 22% to 100% across its 85
services, in one country, in one year [9]. A referral rate is a local policy
variable, not a property of the person in the room, and the comparison is
additionally between studies, countries, health systems and diagnostic
constructs — a memory-clinic MCI diagnosis is a multidisciplinary judgment
with imaging, a community MCI diagnosis a cut-off on a battery.

Two structural points complete the record. The referral contexts are mutually
exclusive branches, one per session, because nearly everyone a clinician
refers also has a subjective complaint and applying both multipliers would
double-count the same information. And a multiplier and its baseline prior
must be specified as a matched pair: the ×1.0 baseline presumes an
unselected-population prior, so against a prior already conditioned on age the
implied clinic uplift shrinks from roughly 8 to roughly 4–5.

One citation was withdrawn in this branch, and the withdrawal is recorded so
it is not itself overread. The code had cited a "clinic-vs-community MCI
systematic review, 2018" for clinic rates several times the community rate.
The paper is Hu, Yu, Sun, Zhang, Wang and Qin, *Int. Psychogeriatr.*, vol. 29,
no. 10, pp. 1595–1608, 2017 (not 2018), doi:10.1017/S1041610217000473, and its
abstract reports the opposite for prevalence — MCI prevalence is
*higher* in community samples than clinic samples; what is higher in clinics
is progression — and it publishes no ratio. The citation is withdrawn. The
nuance: Hu measured MCI specifically, and clinic denominators are dominated by
dementia (52–67%), so the finding is a composition artefact with respect to
the composite endpoint — it refutes the citation, not a referral effect.

## H.5 Family History

Family history enters as ×1.73 for one affected first-degree relative and
×3.98 for two or more, from Cannon-Albright's complete-family-history relative
risks [12]. A reported *no* leaves the prior unchanged rather than lowering
it: where diagnosis is scarce, *no* frequently means *nobody in this family
was ever diagnosed*, and treating it as protective would penalise precisely
the families with the least access to diagnosis.

An objection to this branch was tested and withdrawn. It was argued that
family history shares the retired ×4.0's defect — that under-diagnosis makes a
*yes* mean different things in different settings. Written out, the argument
does not hold. Let D be a truly affected first-degree relative and Y the
answer *yes*; a yes requires the relative to have been diagnosed, so
P(Y | D) = *a* for some ascertainment rate *a* < 1 and P(Y | not D) ≈ 0. For
the person's own future risk R, P(Y | R) = *a* · P(D | R) and
P(Y | not R) = *a* · P(D | not R), so the ascertainment rate multiplies both
arms of the likelihood ratio and cancels: LR⁺ = P(D | R) / P(D | not R). Low
ascertainment makes *yes* rarer; it does not make it mean less — provided
under-ascertainment is non-differential. Referral was different in kind,
because a referral rate determines who enters the tested population at all.
The residual differential mechanism is real but second-order: if diagnostic
access tracks education and education is protective, *yes* is over-represented
among lower-risk people and the likelihood ratio is biased downward — that is,
1.73 would be too high — worth this sentence and no change.

The defect that is real is sharper. Cannon-Albright reports *relative risks*;
the chain multiplies prior *odds*; and RR ≈ OR only while baseline risk is
small, which these bands do not stay: RR 3.98 against the 85-and-over
prevalence of 0.550 implies a risk of 2.19 on the risk scale, which is
impossible. The RR was measured against a far lower baseline and is not
transportable multiplicatively to a high one. `MAX_PRIOR` = 0.85 is the
symptom of that rather than a prudence measure: it binds in exactly 4 of the
135 prior combinations — two-or-more-first-degree-relative cases at ages 80–85
(uncapped prior 0.878) and 85 and over (uncapped 0.924), under either uplift —
and would bind in none of the 45 combinations that exist without a referral
multiplier. The arithmetic was not changed, because the correct alternative —
composing on the risk scale with a ceiling — still requires an arbitrary
ceiling, so it trades one declared assumption for another while invalidating
the completed 1,440-case verification. The defect is documented instead, with
its direction: an age-averaged RR composed with an age-specific prevalence
**overstates familial risk at the oldest ages and understates it around 60**,
because familial loading is stronger for earlier onset. A defect characterised
precisely and left unpatched is a stronger position than one patched with a
second arbitrary constant.

## H.6 The Age Flatness Measurement


Section 3.12's conditional-independence test, in full. The threat: age is
recoverable from the deployed features at *R*² = 0.994, so an age-specific
prevalence multiplied onto the model's evidence could double-count age. The
measurement, recomputed after the lock from the stored out-of-fold vector
by the committed `scripts/age_flatness_check.py` (every figure reproduced
within its registered tolerance;
`results/reconstruction/age_flatness_check.json`), is given in Table (H.2).

**Table (H.2) : The model's evidence against age, 987 development recordings**

| Quantity | Value |
|---|---|
| AUC of age alone for the label | 0.6308 |
| Correlation of model log-odds with age, within controls | **−0.084** (p = 0.054) |
| Correlation within the impaired | +0.025 (p = 0.593) |
| Log-odds drift per year of age, within controls | −0.0070 |
| Implied evidence shift across twenty years | LR × 0.87 |
| Pooled correlation, all recordings | +0.091 |

Within each class the evidence is approximately age-flat, and the drift runs
the wrong way for double-counting; the pooled +0.091 is the legitimate label
signal of impaired participants being older *and* scoring higher, not leakage
into the evidence term.

## H.7 Diagnosis One The Tokenisation Defect


The registered provenance check of the referential-deficit-index probe
required the recomputed pronoun-to-noun ratio to reproduce the committed
`ling.pronoun_to_noun_ratio` to within 10⁻⁶ on at least 99% of recordings,
failing which the run is void. It failed, reproducing the committed feature on
36% of Pittsburgh and 82% of Delaware recordings. The diagnosis proceeded by
elimination. First, pronoun counts matched the committed values almost exactly
(r = 0.9995 in both cohorts), so the tagger was not the problem. Second, the
committed Delaware extractor was re-run on forty of its own inputs and
reproduced its committed output to the last digit, so environment drift was
not the problem — the step that matters, because without it the comfortable
conclusion would have been a library version, and the real defect would have
survived. Third, reading the committed source line by line:
`linguistic_features.py:48` filters `words = [t for t in doc if t.is_alpha]`,
and the new script did not, so punctuation, contraction fragments such as
*n't* and *'s*, and numerals were inflating the denominator. The defect was in
the new script, measured against its own registered definition; fixing it
honoured the registration, and after the fix the check passes at 100% in both
cohorts. By the time the bug was found, one cohort's result block had appeared
in terminal output; that is recorded in the driver's registration history in
those words, with the reasons it does not void the run — the fix was
determined by reading the committed source rather than by the result, no
criterion or threshold moved, the declared bands are identical — and with the
sentence *the reader is entitled to weigh that*.

## H.8 Diagnosis Two The Comparison Defect


A hand-countable feature had been reported as matching the calibrated
ensemble. The feature had been selected as the best of 43 candidates on the
same 288 participants; the ensemble had not been selected at all. Estimated
naively, the hand count led the ensemble by +0.0094 (in-sample best single
feature 0.6473 against the ensemble's 0.6379 on the same tasks); estimated
fairly, with the single feature chosen by nested selection inside the existing
folds, the comparator falls to 0.6018 and the ensemble leads by +0.0361
(`results/reconstruction/selection_optimism.json`). The claim reversed sign
once both sides were estimated alike. Nothing in a registration template asks
whether a comparator was selected: the registration for this computation would
have been unimpeachable, the measurement itself was correct, and the
arithmetic reproduces. The defect was in the comparison, and it was caught
only because the claim was uncomfortable enough to invite challenge.

## H.9 The Amended Registrations And The Four Rules

Of seventeen registered runs — a count verified mechanically by
`scripts/check_counts.py`, which counts the scripts carrying a registration
docstring and flags any prose claim that disagrees — three required amendment
on contact with the data, as Table (H.3) records with the timing of each
amendment relative to seeing the result.

**Table (H.3) : The three amended registrations**

| Episode | What was under-specified | When found | Disclosed as |
|---|---|---|---|
| Retention criterion, cross-corpus transfer | The within-corpus denominator was assumed to be a working reference; on one arm it was itself at chance | On contact with the data, **after** the arms were scored | Recorded in the result file and registration history; criterion unchanged, arm not re-run |
| Tokenisation, referential-index probe (H.7) | Which tokens count toward the denominator | By the registration's own sanity gate, **after** one cohort's output was visible | Recorded with *the reader is entitled to weigh that* |
| Label rule, task-count curve | Which visit's label represents a participant with more than one, when 6.25% change label | **After** the first output was seen | Post-result amendment; **both versions reported** |

The generalisation is that pre-registration in work of this kind is
revised on contact with data considerably more often than the published
literature suggests, because what gets published is the registrations that
held. The discipline that matters is therefore not *never amend* — a claim no project could make — but four rules that can be kept. First, never
adjust the rule to reach the assertion: the retention criterion was left
standing and uninterpretable rather than rewritten into something that would
have graded cleanly. Second, record when an amendment was made relative to
seeing the result, in the words a sceptical reader would use. Third, report
both versions whenever an amendment changes an answer, as the task-count
analysis does for its two label rules. Fourth, register a sanity gate on every
derived quantity an analysis depends on, including its labels: the
tokenisation defect was caught by exactly such a gate, the label defect was
not caught because no gate had been placed on the labels, and every
registration written after that episode carries one. The fourth case (H.8)
extends the fourth rule from derived quantities to comparisons: register how
each side of every comparison was arrived at, and refuse any comparison whose
two sides were produced by procedures with different numbers of free
parameters.

