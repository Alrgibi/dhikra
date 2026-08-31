# ذِكرى — Libyan Arabic Feasibility Study
## Protocol for Ethics Submission and Clinical Collaboration

**Version 1.0** · Prepared for submission to the University of Tripoli research
ethics committee and to the collaborating clinical service.

---

## 1. What this study is, and what it deliberately is not

This is a **feasibility and normative study**, not a diagnostic accuracy study.

That distinction governs the entire design and must be stated to the ethics
committee, the collaborating clinician, and later to the thesis examiners. A
diagnostic accuracy study asks *"how well does this tool detect impairment?"*
and requires roughly **240 participants — 120 per group** — stratified across
cognitive categories to answer with any precision; that figure is derived in
`docs/ARABIC_CORPUS_GAP.md` §5.6 from this project's own effect sizes rather
than taken as a rule of thumb. A feasibility study asks a different
and answerable set of questions:

1. Can elderly Libyan participants **complete** the four-task battery?
2. Does the recording setup produce **analysable audio** in a real clinic?
3. Do the Arabic feature extractors **run correctly** on genuine Libyan
   dialectal speech, rather than the Modern Standard Arabic they were drafted
   against?
4. What do the measurements **look like** in cognitively healthy Libyan
   speakers — the first Libyan normative observations for these features?
5. Are the closed-class word lists (fillers, vague nouns, demonstratives)
   appropriate for **Libyan dialect**, or do they need revision?

**No diagnostic accuracy figure will be computed from this pilot**, and no
Arabic AUC will be reported from it. A sample of this size cannot support one,
and producing a number the data cannot justify is precisely the failure this
project has avoided throughout.

---

## 2. Why this is needed

No publicly available Libyan Arabic connected-speech corpus for dementia
screening has been published. Arabic AD speech datasets exist — a Tunisian
database using syllable-repetition tasks and an Arabic transcript dataset —
but neither is Libyan, neither uses connected picture-description speech, and
neither is publicly accessible.

A 2026 systematic review and meta-analysis of dementia prevalence across the
Middle East and North Africa pooled 52 studies covering 1,045,908 people and
reported a regional prevalence of 12.16% (95% CI 9.61–14.96), ranging from
17.00% in Israel to 6.86% in Egypt [Sedighi et al., *Alzheimer's & Dementia*,
22(1):e71109, 2026]. **Libya is not among the countries it reports.** A
companion narrative review by overlapping authors gives the reason directly —
*"Libya and West Bank and Gaza are not included due to the lack of recently
published data"* [Dajani et al., *J. Global Health*, 16:04181, 2026] — and an
earlier systematic review of Arab-world dementia epidemiology searched for
Libyan studies and found none eligible [El-Metwally et al., *Behavioural
Neurology*, 2019, art. 3935943]. **Libya's population prevalence of dementia
has never been characterised.** (Corrected 2026-08-22: an earlier version of
this paragraph said the meta-analysis discarded Libyan data "because only
hospital-based studies existed". That clause could not be verified in any
source and has been withdrawn.)

The screening system described in this thesis reaches AUC 0.809 for dementia
in English on its development data (95% CI 0.761–0.855; Pitt corpus,
participant-grouped cross-validation, locked external test set excluded) and
AUC 0.853 (95% CI 0.737–0.946) on that locked external corpus, evaluated
exactly once. Its Arabic component is an implemented *method* — verified on
constructed examples, never yet computed on real patient speech — with no
clinical validation whatsoever. This pilot is the first step toward closing
that gap.

---

## 3. Participants

### Target sample
**Minimum 20, target 40**, recruited across two strata:

| Stratum | Target | Source |
|---|---|---|
| Cognitively healthy older adults | 20 | community, families of clinic attendees, staff relatives |
| Patients with diagnosed cognitive impairment | 20 | collaborating memory or neurology service |

A balanced design is preferred but not required; the healthy stratum alone
delivers objectives 1–5 and is the easier group to recruit.

### The healthy stratum is also the normative sample — and that changes its size

**Added 2026-08-23.** The main system's weakest reported figure is its 33.3%
specificity on the locked external corpus, and the analysis in
`docs/TRANSPORT_AND_REPORTING.md` establishes that this was a *threshold
referencing* failure rather than a model failure. The remedy is
**control-referenced thresholding**: set the operating threshold at a fixed
percentile of the **local cognitively healthy** score distribution. Specificity
is then fixed by construction and does not move with local prevalence.

**That rule needs healthy speakers and no patients at all — which is precisely
what this study's healthy stratum is.** The same recruitment therefore delivers
two things: the Arabic feature validation it was designed for, and the
normative distribution from which a Libyan operating threshold can be derived.
No additional patients, no additional consent burden, one study.

**The consequence for sample size, stated exactly.** If the threshold is the
k-th order statistic of *n* healthy controls with k = ⌈0.80n⌉, then the
specificity it achieves on the wider healthy population is distribution-free
and follows a Beta(k, n+1−k) law — no assumption about the shape of the score
distribution is required:

| Healthy *n* | Expected specificity | Exact 95% interval | Width |
|---|---|---|---|
| 15 | 0.750 | [0.52, 0.92] | 0.40 |
| **20 (current target)** | 0.762 | **[0.56, 0.91]** | 0.35 |
| 30 | 0.774 | [0.61, 0.90] | 0.29 |
| 50 | 0.784 | [0.66, 0.89] | 0.22 |
| 100 | 0.792 | [0.71, 0.87] | 0.16 |
| 200 | 0.796 | [0.74, 0.85] | 0.11 |

**Read this honestly rather than as an argument for a bigger study than can be
run.** At the current target of 20 healthy participants the derived threshold
is *provisional*: the specificity it would deliver prospectively lies anywhere
between 56% and 91%. That is still a decisive improvement on a threshold
transplanted from English-speaking American cohorts, whose specificity in a
Libyan clinic is not merely uncertain but unestimable. **The recommendation is
therefore: keep the 20-participant minimum for feasibility, but treat every
healthy participant beyond 20 as directly buying threshold precision, and state
n ≥ 30 as the point at which the normative deliverable becomes worth
publishing.** Roughly 59 healthy participants would be needed for a ±10-point
interval and 108 for a ±7.5-point one; those are the honest figures for a
follow-on normative study, not for this pilot.

**The interval above is a FLOOR on the uncertainty, not the whole of it.** The
Beta(k, n+1−k) result is exact and distribution-free, but it assumes the control
sample is drawn **independently from the population the threshold will be
applied to**. This study recruits healthy participants from "community, families
of clinic attendees, staff relatives" (§3). That is a convenience sample, and it
is plausibly healthier, better educated, more urban and younger than the
population a deployed instrument would meet. The table therefore states the
sampling error and **not** the selection error, and the two do not add in any
way this study can quantify.

**State the direction of the resulting bias, because it is favourable and that
matters clinically.** A healthier-than-typical control sample produces *lower*
scores, so its 80th percentile sits *lower*, so the derived threshold is *lower*
than it should be, so *more* people are flagged. The instrument therefore
**over-refers** rather than under-refers, and true specificity in the deployed
population falls **below** the target rather than above it. For a screening
instrument that is the safe direction of failure: the cost is wasted clinical
assessments, not missed cases. **Report it as a bounded, directional limitation
rather than as an unknown**, and say plainly that the magnitude is not estimable
from this design.

**Two cheap mitigations, both worth writing into the analysis plan.** Record
education, urban/rural residence and age for every healthy participant, and
report the threshold recomputed with the sample reweighted to the age and
education distribution of the local population if census figures are available.
Neither removes the bias; both make its size visible instead of invisible.

**One caveat that must travel with the headline number.** The bootstrap
interval reported for this rule on the Lu corpus — specificity 0.774, 95% CI
[0.69, 0.80] on 27 controls — is an **in-sample** quantity: the same 27
controls both defined the threshold and were scored against it, which
correlates the two and is why the interval cannot exceed the 0.80 target. The
exact prospective interval for 27 controls is the wider **[0.62, 0.91]** in the
table above. **Quote the bootstrap figure for how precisely the rule hits its
own target, and the Beta interval for what a new population would experience.
They answer different questions.**

### Inclusion criteria
- Aged 55 years or older
- Native Libyan Arabic speaker
- Able to hear and understand spoken instructions
- Provides informed consent, or assents with consent from a legally
  authorised representative

### Exclusion criteria
Each exclusion below removes a factor that would confound speech measurement
independently of cognition:
- Diagnosed speech or language disorder (aphasia, dysarthria, severe stammer)
- Significant uncorrected hearing loss preventing task comprehension
- Acute illness, delirium, or intoxication at the time of assessment
- Severe uncorrected visual impairment (prevents the picture task)
- Active psychosis or severe untreated depression, both of which alter speech
  independently of dementia
- Recent stroke (within 6 months) affecting speech

---

## 4. Consent, and the capacity question

This is the part the ethics committee will scrutinise most closely, so it must
be addressed directly rather than in passing.

**For participants with capacity:** written informed consent in Arabic, after a
verbal explanation. The information sheet must state that participation is
voluntary, that refusal affects no aspect of their care, that they may withdraw
at any time without giving a reason, and that withdrawal deletes their
recording.

**For participants with impaired capacity:** written consent from a legally
authorised representative (typically the son or daughter accompanying them),
**plus ongoing assent from the participant themselves**. Assent is behavioural
as much as verbal: if the participant becomes distressed, refuses a task, tries
to leave, or repeatedly asks to stop, the session ends immediately. Consent
from a relative does not override the participant's own reluctance in the
moment.

**Explicitly stated to every participant:**
- The recording measures *how* they speak, not what they know
- There are **no right or wrong answers**
- The result is **not a diagnosis** and will not be entered in their medical
  record
- No clinical decision will be made on the basis of this recording

**The form itself is drafted** at `docs/forms/CONSENT_FORM_ar.md` (26 August
2026): information sheet and signature page as two separate documents, the
assent acknowledgement placed above the representative's signature so it is
operative rather than aspirational, and five fields left bracketed because they
cannot be invented — approval number, complaints contact, retention period,
withdrawal window, site. **It is deliberately more conservative than this section
in three places, each argued at its foot;** the most important is that **no
participant in any stratum is given a screening result**, because disclosing to
one stratum and not another makes the silence itself informative.

**Incidental findings.** If a healthy-stratum participant produces a markedly
atypical profile, the research team will **not** disclose a screening result —
the tool is not validated for that purpose. The protocol instead states that
any participant or family expressing concern about memory will be advised to
consult the collaborating clinician in the normal way. This must be written
into the protocol before collection begins, not decided ad hoc afterwards.

---

## 5. Reference standard

Every participant receives an independent cognitive assessment administered by
the collaborating clinician, **blind to any output of the system**.

**Instrument: the Arabic Montreal Cognitive Assessment (MoCA), Arabic version.**
The Arabic MoCA has published reliability and validity data (Rahman & El
Gaafary, 2009, validated in Cairo geriatric clinics) and is the most widely
used validated Arabic cognitive screen.

**Recorded for each participant:**
- MoCA total and item-level subscores
- The education correction (+1 point for ≤12 years of schooling) applied per
  official guidelines, and recorded as applied
- Existing clinical diagnosis, if any, and its date
- Whether diagnosis was made by a specialist

**Order matters:** the cognitive assessment is administered **after** the speech
recording, so that the participant's performance on a demanding test does not
fatigue them into an unrepresentative speech sample.

---

## 6. Data collected per participant

### Demographics — every field has a stated reason
| Field | Why it is collected |
|---|---|
| Age | strongest single risk factor; required for the risk adjustment |
| Sex | affects pitch measures directly |
| **Years of education** | strongly affects vocabulary and fluency independently of cognition |
| **Literacy** (can read / cannot read) | determines which tasks are valid |
| **Dialect region** (Tripoli, Benghazi, Misrata, south, other) | Libyan Arabic is not uniform |
| Languages spoken | bilingualism affects fluency measures |
| Family history of dementia | first-degree, second-degree, none, unknown |
| Reason for attendance | routine, family concern, clinical referral |
| Hearing aid use | affects comprehension of instructions |

### The task battery — REVISED 25 August 2026, and the ordering is the revision

**What changed and why.** The battery previously led with picture description
because that is what the deployed English model reads. A pre-registered
measurement on the one corpus that can answer the question
(THESIS_PLAN §5.25; `results/reconstruction/task_count_curve.json`) found that
**for mild cognitive impairment, picture description is the weakest of five
tasks and performs at chance**, while connected-discourse tasks — story retell
and procedural description — beat it by roughly a tenth of an AUC with intervals
excluding zero. Two discourse tasks administered together beat three picture
tasks administered together (+0.079 [+0.004, +0.158]).

**MCI is the target where early detection changes management, so the battery now
leads with connected discourse.** Picture description is retained, unchanged, for
the dementia target — where it works (Pitt 0.809, external Lu 0.853) and where it
is the only task with an externally validated model behind it.

| # | Task | Duration | Genre | Primary target |
|---|---|---|---|---|
| **1** | **Story recall** — a short standardised story read aloud once by the examiner, then retold immediately | 90 s | connected discourse | **MCI** |
| **2** | **Procedural discourse** — *"tell me, step by step, how you make tea"* | 90 s | connected discourse | **MCI** |
| 3 | **Picture description** — the kitchen scene | 90 s | picture | dementia |
| 4 | **Verbal fluency** — animals | 60 s | category fluency | both |
| 5 | **Quran recitation** — a surah the participant selects from those they know | 60 s | over-learned speech | cultural probe |

**Task 1 is already the right paradigm and is unchanged in content.** A story
supplied by the examiner and retold immediately removes any requirement for
cultural knowledge of the narrative — which is why this protocol does **not**
adopt the Cinderella retell used by the corpus that produced the finding. The
paradigm matches Craft Story 21 as used by the NACC Uniform Data Set, so an
established scoring tradition exists to translate against. **Add a delayed
retell** if session length permits; delayed recall is where MCI presents most
sharply and it costs 60 seconds.

**Task 2 is new.** The procedural task requires no stimulus material at all,
which makes it the one task that survives intact in a paper-and-pencil fallback
and on a device with no screen. *Making tea* is chosen because essentially every
participant has performed it hundreds of times, so failure reflects discourse
organisation rather than unfamiliarity. **Do not translate "making a peanut
butter and jelly sandwich."**

### Elicitation must be fixed, and this is not a formatting preference

`ling.word_count` is the strongest single MCI marker on connected discourse
(AUC 0.631; `results/reconstruction/feature_by_task_auc.json`). **If elicitation
time or probing varies between participants, that measure records examiner
behaviour as much as speaker ability**, and the battery's primary MCI signal
becomes an artefact of administration.

Fix and log, for every task and every participant:

- the **prompt, read verbatim** from the script — no paraphrase;
- the **maximum duration**, enforced;
- the **re-prompt rule** — at most two probes, using the exact wording *"tell me
  anything else you can"*, each after 10 s of silence;
- **recorded as metadata**: elicitation time actually used, and probe count.

THESIS_PLAN §5.19 is why this is a requirement: eighteen healthy speakers in the
locked external corpus were flagged because their descriptions were genuinely
thin, and administration is the most plausible cause that could have been
controlled. §5.23 adds the other half — a minimum-length rule was tested and
**refused**, so thin descriptions cannot be filtered out after the fact. They have
to be prevented at elicitation.

**Additional data required for the Quran probe**, because without it the task
cannot be interpreted:
- Which surah was recited
- Self-reported familiarity: recites daily / weekly / rarely / knows but does
  not recite
- Approximate age at memorisation, if known
- Whether they have formal tajweed training

These are the confounders that make recitation accuracy uninterpretable if left
unmeasured, and they cost thirty seconds to collect.

---

## 7. Recording conditions

- **Quiet room**, door closed, no radio or television
- Device held or placed approximately **30 cm** from the participant
- The **same device** for every participant in the pilot; model recorded
- Sample rate 44.1 kHz or higher, uncompressed where the device permits
- A **10-second room-tone recording** before the first task, to characterise
  background noise
- Session start time and approximate room noise noted

**The operator must not:**
- Prompt with example words during verbal fluency
- Fill silences — pauses are the measurement
- Correct or complete the participant's speech
- Comment on performance during the session

---

## 8. Data handling

- Participants identified only by code (LY-001 onward); the linking key is held
  separately by the clinician, not by the researcher
- Recordings stored encrypted, on a device that is not shared
- No names, national ID numbers, addresses or phone numbers in any file that
  travels with the audio
- Recordings deleted on withdrawal request
- Data retained for the period specified by the ethics committee, then deleted
- Recordings are **not** uploaded to any third-party service, and not shared
  outside the named research team without a further ethics amendment

---

## 9. Outcomes — what the pilot will actually report

### Primary (feasibility)
- **Task completion rate** per task, by cognitive group
- **Recording quality**: proportion of recordings from which the acoustic
  extractor runs without error; signal-to-noise estimate; clipping rate
- **Session duration** in practice, against the 6-minute design target
- **Transcription feasibility**: word error rate of automatic Arabic
  transcription against manual transcription on a subset, since Libyan dialect
  transcription is a known weakness

### Secondary (normative and linguistic)
- Distribution of each Arabic feature in the **healthy** stratum: median and
  observed range, reported as such rather than as percentiles unless n ≥ 30
- **Word-list validation**: every filler, vague noun and demonstrative actually
  produced, and which items on the drafted Modern Standard Arabic lists never
  appear in Libyan speech
- Whether the **referential deficit index** behaves as intended on real Libyan
  speech
- Quran task: completion rate, surah distribution, familiarity distribution
- **A provisional Libyan operating threshold**, derived as the 80th percentile
  of the healthy stratum's score distribution, reported together with its exact
  Beta(k, n+1−k) interval and explicitly labelled provisional at n < 30 (§3)

### The endpoint decision for the study this pilot is preparing — fixed 26 August 2026

**This pilot is a feasibility study and its own outcomes are above. This section
fixes the design of the study it exists to make possible, so that the decision is
on the record before recruitment starts rather than argued about after.**

**Primary endpoint: dementia versus healthy controls. Powered.**

Three reasons, and each is forced by evidence this project already holds:

1. **It is the only endpoint with evidence behind it.** The external validation is
   a dementia result — AUC 0.8533 [0.7371, 0.9458] on 53 recordings. On mild
   cognitive impairment the instrument is close to chance: the Delaware Cookie
   Theft task returns 0.5061 and cross-corpus transfer 0.629.
2. **It is the only endpoint that can be powered on a defensible estimate.**
   141 per group for the dementia effect against 130 for the MCI discourse
   effect — but the MCI figure assumes the discourse advantage is real at the
   size one corpus estimated, on a corpus whose own picture task was at chance.
   **A primary endpoint should not rest on the weaker of two estimates.**
3. **It is the only endpoint whose labels are obtainable here.** A dementia
   diagnosis is at least sometimes recorded in a Libyan family. An MCI diagnosis
   requires neuropsychological testing that the regional review literature says
   is largely unavailable. A study cannot have a primary endpoint whose reference
   standard it cannot get.

**Secondary endpoint: a mild-cognitive-impairment arm. Pre-specified, explicitly
underpowered, and DESCRIPTIVE ONLY.**

- **No test statistic and no AUC are reported for this arm.** It has no null to
  reject and it will not be given one.
- What it produces is the first Libyan normative description of both task genres
  in speakers with suspected mild impairment: distributions, medians, observed
  ranges, and per-unit information production.
- It costs recruitment effort and nothing else. It cannot fail. It is the only
  route by which the MCI question is ever asked in this population.

**Why the objection that prompted this is answered rather than overruled.** The
concern was that a dementia-only cohort discards the reason the battery
administers both task genres to every participant. It does not, because those are
two different axes:

| Axis | What varies | Decided by |
|---|---|---|
| **Group** | dementia / MCI / control | this section |
| **Task** | picture description / connected discourse | **the battery — both, on every participant, whoever is recruited** |

Giving every participant both genres is a property of the battery and survives
any cohort choice. The picture-versus-discourse contrast is obtained on the same
speakers in a dementia-versus-controls study exactly as it would be in any other.
**What a dementia-only cohort would lose is the MCI question**, and the
pre-specified descriptive secondary arm above is what stops that loss.

**This is §1.7 applied to a study design instead of a table.** The powered arm
and the descriptive arm are reported separately and never in the same table, for
the same reason a validated figure never shares a table with a specified one.

---

### What this study is NOT powered to do — added 2026-08-23, and it is a real limit

**This study cannot test the referential deficit index, and the arithmetic
should be in the protocol rather than discovered later.** The index was probed
in English on 987 labelled recordings (`docs/ARABIC_CORPUS_GAP.md` §4): its
pronoun-free form — which is structurally what the Arabic index is, because
Arabic drops pronouns — reaches AUC 0.596 on Pittsburgh and 0.625 on the age-
and sex-matched subset. **So the honest expectation for an Arabic dementia
sample is roughly 0.60.**

Detecting a true AUC of 0.60 at 80% power requires **130 participants per
group**. This study targets **20 per group**, which can detect only a true AUC
of **0.748 or larger** — far above what the English evidence predicts. **A null
result here would therefore be uninterpretable**, and must not be reported as
evidence against the index.

*Two figures corrected 25 August 2026, and both were stale in the same
paragraph. The requirement was written as 125 per group; recomputing gives 130,
and the conservative figure is used (`ARABIC_CORPUS_GAP.md` §5.6 records the
~8% power-convention difference). The detectable AUC was written as 0.645,
**which is the figure for sixty per group, not twenty** — at twenty it is
0.748. The second is the more serious: it made this study look roughly twice as
sensitive as it is, and it survived here for three days after being corrected
elsewhere in this same document.*

What the study *can* deliver is unchanged and worth doing: feasibility of the
battery in elderly Libyan participants, healthy-stratum normative distributions,
validation of the filler, vague-noun and demonstrative word lists against speech
people actually produce, a provisional control-referenced threshold, and the
task-administration measurements (§10) that no existing corpus records. The
discriminative question needs the larger corpus specified in
`docs/ARABIC_CORPUS_GAP.md` §5, of which this study is a first increment.


**Quantified 25 August 2026.** At 20 per group, 80% power detects only a **true
AUC of 0.748 or larger** (Hanley–McNeil, two-sided α = 0.05).

| n per group | minimum detectable true AUC at 80% power |
|---|---|
| **20 (this pilot)** | **0.748** |
| 30 | 0.705 |
| 40 | 0.678 |
| 60 | 0.646 |
| 120 | 0.604 |

**No effect this project has measured is that large.** The referential deficit
index reaches 0.596 in English on dementia; the connected-discourse MCI effect is
0.631–0.638. **This pilot cannot test either, and saying so here is deliberate.**
A study that reported a null at this size would be reporting the sample size, not
the instrument. `docs/ARABIC_CORPUS_GAP.md` §5.6 gives the sizes that could:
**about 130 per group for the MCI discourse effect and 141 for the dementia
referential effect — they cost essentially the same.** *(Corrected 25 August
2026. This previously read "75 per group for the MCI discourse effect", which
rested on a selection-inflated estimate withdrawn in THESIS_PLAN §5.28. The
withdrawal was written into the corpus specification and not into this
document.)*

### Scoring rule — required, and added 26 August 2026 on a measured result

**The automated information-unit scorer was checked against a human on 20
transcripts and graded INADEQUATE** against its pre-registered criterion (mean
absolute difference 1.600 against a threshold of 1.200; THESIS_PLAN §5.5.1). The
disagreement is a near-constant undercount of about **1.5 units** — the software
ranks speakers as a human does (ICC 0.904, against a published human–human 0.347)
but counts low, with misses outnumbering false credits 3.7 : 1.

**Two consequences bind this protocol.**

1. **Every scorer is trained against `docs/scorer_check/CODING_RULES.md` before
   collection begins**, and the training is recorded.
2. **A subsample of at least ten sessions is double-scored by a second person.**
   The check above had one scorer and therefore could not separate software error
   from one person's idiosyncrasy — a limitation stated in its registration
   before the sheet was opened. This study should not repeat it.

**And a threshold rule that follows directly.** A person counting units by hand
arrives at roughly 1.5 more units than the software for the same speech.
**A threshold derived from software counts therefore does not transfer to hand
counts.** The paper instrument must take its cut-off from **hand-scored local
controls**, not from the software's. This is a second and independent reason for
control-referenced thresholding.

### Secondary outcome, pre-registered: is the substituted picture equivalent?

**Added 26 August 2026 on a measured result.** The screening probability this
system reports was calibrated on descriptions of the Cookie Theft picture. The
system does not show that picture — it is not redistributable — and shows a
scene drawn for this project instead. On 26 August the frozen model was probed
to find how much the substitution would have to cost before the decision
changed. The answer: **one displaced information unit crosses 13.1% of control
recordings over the threshold; two crosses 26.7%**
(`results/stimulus_inventory_probe.json`, graded DISPLACEMENT-MATERIAL). The
substitution is therefore not a footnote and this pilot is the first and only
opportunity to measure it on real speakers.

**What is computed.** For every participant, the information-unit count from the
kitchen scene, scored by the committed English key where the description is in
English and by the Arabic key otherwise, together with the per-unit indicators.

**What is reported.** (a) The unit-level production rate for each of the 23
units, with exact binomial intervals; (b) the count of units produced by fewer
than 5% of the healthy stratum, which is the operational definition of a unit
the picture fails to elicit; (c) the total information-unit distribution in the
healthy stratum, compared against the Pittsburgh control distribution
(mean 12.1 units is *not* the comparison — the comparison is the full
distribution, because a shift in the mean and a change in shape have different
causes).

**What it cannot do.** This is a comparison between a Libyan sample on our
picture and an American sample on the Cookie Theft. Any difference confounds
stimulus with population, language and era, and the design cannot separate them.
It is reported as a bound, not as an estimate: if Libyan healthy speakers
produce information units at a rate comparable to American controls, the
substitution is probably not costing much; if they produce markedly fewer, the
cause is unidentified and the threshold must be re-derived locally rather than
inherited.

**The one design that would separate them** — administering both pictures to the
same speakers — requires a BDAE licence and is recorded in §11 as something to
ask the collaborating institution about, not assumed.

**Registered decision rule.** If any unit is produced by fewer than 5% of the
healthy stratum, that unit is reported as not elicited by this stimulus and the
finding is carried into any future revision of the artwork. It does **not**
license removing the unit from the scorer: the scorer computes the frozen
model's input and cannot change.

---

### Secondary outcome, pre-registered: the minimal probe

**Added 25 August 2026.** One outcome of this pilot *can* be a discriminative
measurement, and it should be registered as such before collection begins.

**What is computed:** the **total number of words the participant speaks across
the two connected-discourse tasks** (story recall and procedural discourse),
under the fixed elicitation of §6. One number, counted from the transcript, with
no software.

**Why it is worth registering.** On Delaware, on 288 participants at their
earliest common visit, that single hand-counted number reaches **AUC 0.6420
[0.5786, 0.7052]** for MCI against control, while the same count on the three
picture-description tasks reaches only **0.5680**. It is far and away the best of
the countable measures.

**With the comparison stated honestly.** Word count was selected as the strongest
of 43 measures using those same participants; the calibrated ensemble on the same
two tasks (0.6379) was not selected. Estimated the same way — nested selection
inside each fold — the single-feature comparator is **0.6018**, so **the modelling
apparatus buys about +0.036 and the hand count does not match it.** Word count's
true value lies somewhere in **0.60 to 0.647**. (`minimal_probe.json`,
`selection_optimism.json`; THESIS_PLAN §5.28, §6.1.0b.)

**The criterion, fixed in advance.** This pilot is **not powered** to test it —
20 per group detects only a true AUC of 0.748 or larger. What is registered here
is therefore **descriptive and normative, not a test**:

- report the **distribution of total discourse words in healthy Libyan
  participants** — the first such normative observation in Arabic;
- report the impaired group's distribution beside it, **with no significance
  test and no AUC**, because n = 20 per group cannot support one;
- report the **fraction of sessions in which the fixed elicitation was actually
  achieved** (§6), since the measure is invalid without it.

**Interpretive asymmetry, registered.** If Libyan healthy speakers produce
markedly fewer words than the English reference distribution, that is expected —
Arabic is morphologically rich and conveys in fewer orthographic words what
English spreads across more. **It is a reason the threshold must be derived from
local controls and never imported, not a reason to doubt the measure.**

### Explicitly NOT an outcome
- Diagnostic accuracy, sensitivity, specificity, or AUC
- Any claim that the system detects impairment in Arabic

**This boundary is unchanged by the normative-threshold deliverable above, and
the distinction matters.** Deriving a threshold from the healthy stratum
produces a specificity that is *known by construction*, with a stated interval.
It does **not** measure specificity, says nothing about sensitivity, and makes
no accuracy claim whatsoever. Measuring what that threshold actually does
requires a later study with a diagnosed comparison group. **Do not report the
Beta interval as though it were a validation result.**

---

## 10. Analysis plan, fixed before collection

1. Descriptive statistics only for the primary outcomes
2. Healthy-stratum feature distributions reported as median and range
3. If both strata reach n ≥ 15, an **exploratory** group comparison with effect
   sizes and confidence intervals, explicitly labelled as hypothesis-generating
4. No classifier will be trained on this sample. Prior work in this project
   demonstrated that 24 participants produced results ranging from AUC 0.420 to
   0.655 depending only on model choice — a range wider than any plausible real
   effect, and a concrete demonstration of why small-sample training is
   meaningless here.
5. **The 80th percentile of the healthy stratum's screening-score distribution
   is computed and reported with its exact Beta(k, n+1−k) interval.** This is
   an order statistic of a single group, not a fitted quantity: no model is
   trained, no threshold is optimised against outcomes, and nothing is selected
   by looking at the impaired stratum. It is fixed *before* any group
   comparison in item 3 is run, and it is reported whatever that comparison
   shows.

---

## 11. What the collaborating clinician is being asked for

Stated plainly, because a clear ask is more likely to be accepted:

1. **Permission** to approach patients attending their service
2. **Administration of the Arabic MoCA**, or supervision of its administration
3. **Confirmation of existing diagnoses** from the medical record
4. **A quiet room** for approximately 20 minutes per participant
5. **Clinical oversight** — the authority to stop any session
6. **Co-authorship** on any publication arising, and named collaboration in
   the thesis

**What the clinician is NOT being asked for:** to use the system, to act on its
output, to change any aspect of patient care, or to take responsibility for the
research analysis.

---

## 12. Realistic timeline

| Stage | Duration |
|---|---|
| Ethics submission prepared | 1 week |
| Committee review | 2–8 weeks, outside the researcher's control |
| Clinic scheduling | 1–2 weeks |
| Collection, 20–40 participants | 3–6 weeks |
| Analysis | 1 week |

**This cannot be completed before the thesis deadline.** The protocol is
therefore submitted as a completed, ethics-ready study design constituting the
principal future work of the project, with any data collected before submission
reported as a preliminary technical demonstration rather than as study results.

A completed protocol is itself a contribution: it converts "Arabic validation
is future work" from an aspiration into a specified, costed, ethically framed
plan that another researcher could execute.
