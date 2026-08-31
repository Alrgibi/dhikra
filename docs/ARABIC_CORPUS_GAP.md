# The Arabic Corpus Gap — A Documented Absence, and a Corpus Specification

*Written 2026-08-23. This replaces the framing in which the Arabic work is "an
adaptation that has been built but not validated" — a framing that invites the
reader to score it as incomplete. The accurate framing is that **the validation
cannot currently be performed by anyone**, that this is a documented property of
the available resources rather than of this project's effort, and that the
useful contribution is to specify precisely what would close the gap.*

---

## 1. The claim, with its scope stated before its evidence

> **As of August 2026, no publicly available corpus pairs cognitively impaired
> and cognitively healthy Arabic speakers on a connected-speech task with
> transcripts.**

Four qualifiers do real work and none may be dropped:

- **Publicly available.** This says nothing about whether such data exists in a
  clinic in Cairo, Rabat or Riyadh. It almost certainly does. It says the data
  cannot be obtained by a researcher.
- **Both classes.** Arabic corpora of healthy speech are abundant. Corpora of
  disordered Arabic speech exist. Neither is usable for a discriminative
  marker, which needs both in one collection.
- **Connected speech.** Word lists, naming tests and sentence repetition do not
  elicit the referential behaviour the proposed index measures. This qualifier
  is what excludes the one dataset that otherwise qualifies.
- **With transcripts.** Audio without orthographic transcription cannot support
  lexical or syntactic measurement, and Arabic ASR is not accurate enough on
  dialectal elderly speech to substitute.

**This is not an impossibility proof and must not be written as one.** It is a
documented absence at a point in time, from the searches in §2, and one
counterexample retires it. That is a feature: the claim is falsifiable, which is
more than "resources are scarce" can say.

---

## 2. The search, and what it found

Performed 2026-08-23 by web search and direct retrieval. **A documented search,
not a systematic review** — see §6 for exactly what that means.

| Source checked | What it is | Result |
|---|---|---|
| **DementiaBank** (`talkbank.org/dementia/access/`) | The field's canonical repository; source of this project's own three corpora | Language sections: **English, German, Greek, Korean, Mandarin, Spanish, Taiwanese. No Arabic.** |
| **Survey of speech-based AD detection**, *Artificial Intelligence Review* (2024), doi:10.1007/s10462-024-10961-6 | Survey of AI techniques, datasets and challenges | Names **12 datasets** — Pitt, ADReSS, ADReSSo, ADReSS-M, TAUKADIAL, VAS, Delaware, Dem@Care, Framingham, Carolina Conversations, Dementia Blog, Multimodal Dementia. English, Greek, Chinese. **No Arabic dataset appears anywhere in it.** |
| **PROCESS-2** (arXiv:2605.14888) | Newest benchmark for early cognitive impairment: 200 healthy, 150 MCI, 50 dementia, with Cookie Theft | **British English only**, named by the authors as a limitation |
| **Modern Standard Arabic speech disorders corpus**, *Int. J. Speech Technology* (2024), doi:10.1007/s10772-024-10086-9 | 40 Jordanian speakers with speech disorders | **Articulation** disorders. Not dementia, no connected-speech task, and **not publicly available** — from the author on request |
| **Rabaya et al.**, *Front. Psychol.* 17:1833118 (2026) | Arabic MoCA dataset, 24 speakers: 7 healthy, 6 MCI, 11 dementia — the dataset this project already used | **Both classes present.** But MoCA is naming, sentence repetition, verbal fluency, abstraction and recall — **no picture description, no narrative.** Word lists, not connected speech |
| **Kabalan et al.**, *Alzheimer's & Dementia* 21(5):e70207 (2025) | Systematic review of cognitive assessment tools for Arabic speakers 50+, **154 studies** to Nov 2023 | The six instruments with good dementia performance are **structured batteries and questionnaires** — MMSE, MoCA, Alzheimer's Questionnaire, mini-ACE, A-IQCODE, Dementia Arabic Scale. No connected-speech instrument among them. Also reports **screening tools perform poorly for MCI** in Arabic speakers, MoCA excepted |
| Large Arabic spontaneous-speech corpora (e.g. Nexdata Saudi Arabic, 849 h) | ASR training data | Connected speech in abundance. **No clinical labels of any kind** |

**The shape of the evidence is what makes it credible, and it should be
presented this way: the gap is bracketed on both sides by near-misses.** Arabic
data with both classes and no connected speech exists (Rabaya). Arabic connected
speech in quantity with no clinical labels exists (ASR corpora). The
intersection does not. A search returning nothing would be weak evidence of
absence; a search returning both halves and never the join is strong evidence
that the join is what is missing.

---

## 3. Why the obvious workaround does not work

The natural response is: translate the English protocol and run it. It does not
work, and the reason is this project's own central linguistic finding.

In English, word-finding difficulty surfaces as **pronoun overuse** — *"he put
it there."* **Arabic is pro-drop**: the subject pronoun is normally omitted
because the verb already carries person, number and gender. Arabic pronoun
counts therefore sit on a different baseline for **grammatical rather than
clinical** reasons, and the English measure does not transfer. (A statement
about non-comparability — *not* the retired claim that the deficit cannot be
signalled in Arabic. Arabic has ample means of vague reference, which is
precisely what the replacement measures.)

So the required corpus is not "the English protocol in Arabic." It is a corpus
collected with a task **designed to elicit referential expressions under
retrieval load in Arabic**, transcribed to a standard that preserves
demonstratives and vague nouns — exactly the items an MSA-normalising
transcription convention regularises away. **That design requirement is itself
part of the contribution** and is not obvious from the English literature.

---

## 4. What the English construct probes changed — read this before §5

The referential deficit index cannot be tested in Arabic, so it was tested in
**English**, twice. The second probe changed the specification below
substantially, and the first one's reading of the Delaware null is now known to
have been wrong.

### 4.1 The index works — on dementia

The pronoun-free index — demonstratives and vague nouns over nouns, which is
structurally what the Arabic index is — reaches AUC **0.596 [0.541, 0.652]** on
Pitt and **0.625 [0.562, 0.690]** on the age- and sex-matched subset
(`scripts/rdi_english_probe.py`, pre-registered; THESIS_PLAN §5.10.1).
**Pitt is a dementia cohort.**

### 4.2 It does not work on MCI — on any task — and the earlier excuse for that does not survive

The first probe found the index at chance on Delaware (MCI) and reasoned that
*"the established pronoun marker it replaces fails too, so that is a property of
the cohort and not of the measure."* **That reasoning is now withdrawn.** It
predicted that nothing detects Delaware MCI. Two later measurements show that
something does.

`scripts/rdi_cross_task_probe.py` (pre-registered; THESIS_PLAN §5.27) computed
the index on **all five** Delaware tasks, on the same 288 participants at the same
visit, with the measurement path verified against the committed
`ling.pronoun_to_noun_ratio` at **100.0%** on every task:

| task | genre | rdi_free (directed AUC) |
|---|---|---|
| cookie | picture | 0.535 [0.466, 0.602] |
| cat | picture | 0.489 [0.420, 0.557] |
| rockwell | picture | 0.570 [0.501, 0.636] |
| cinderella | **discourse** | 0.498 [0.424, 0.568] |
| sandwich | **discourse** | 0.460 [0.393, 0.524] |

**Grade: RDI-DOES-NOT-TRAVEL.** Genre contrast −0.0523 [−0.1098, +0.0054].

Meanwhile, on the same people, the same visit and the same 43 shared features,
**Delaware MCI is detectable** — the best two-task discourse model reaches
**0.638 [0.570, 0.701]** and `ling.word_count` alone reaches **0.631** on
discourse (THESIS_PLAN §5.25, §5.27). So the cohort is not undetectable. **The
referential measures specifically do not detect it**, while volume, lexical
richness, syntactic and coherence measures do.

**The failure is in the CONSTRUCT, not in the implementation and not in the
language.** The natural reading is that the Arabic index is a lossy substitute
that lost too much. It is not. The **English pronoun marker it replaces is at
chance on MCI on all five tasks as well**:

| task | pn (English pronoun-to-noun marker) | rdi_free (the Arabic index's construct) |
|---|---|---|
| cookie | 0.564 [0.497, 0.627] | 0.535 [0.466, 0.602] |
| cat | 0.551 [0.484, 0.620] | 0.489 [0.420, 0.557] |
| rockwell | 0.534 [0.464, 0.603] | 0.570 [0.501, 0.636] |
| cinderella | 0.540 [0.469, 0.609] | 0.498 [0.424, 0.568] |
| sandwich | 0.467 [0.396, 0.533] | 0.460 [0.393, 0.524] |

Every interval contains 0.5. **The index tracks the marker it stands in for, on
both targets** — somewhat lossy on dementia (0.596 against 0.656) and equally
uninformative on MCI. It does what it was designed to do. What it was designed to
stand in for does not detect MCI in English either. Referential deficit is a
**dementia-stage phenomenon**, and no implementation in any language makes it an
early marker.

> **The conclusion the specification must be built on: the referential deficit
> index is a DEMENTIA marker. It has no evidential support as an MCI marker, in
> any language, on any task tested. The task change is not what breaks it — the
> target change is.**

**The pro-drop argument survives unchanged.** That argument is about
*portability*: Arabic is pro-drop, pronoun counts sit on a different scale, and
the English pronoun-overuse marker cannot be carried across. That is a linguistic
fact and nothing here touches it. The referential deficit index remains the
correct replacement for it. **What changes is not whether the replacement works,
but what it is FOR.**

### 4.3 What carries the MCI signal instead

Measured on Delaware's two connected-discourse tasks
(`results/reconstruction/feature_by_task_auc.json`):

| family | representative measure | discourse AUC | picture AUC |
|---|---|---|---|
| **output volume** | `ling.word_count` | **0.631** | 0.554 |
| | `ling.sentence_count` | 0.600 | 0.553 |
| **lexical richness** | `ling.brunet_w` | 0.598 | 0.537 |
| | `ling.type_token_ratio` | 0.584 | 0.527 |
| **semantic coherence** | `sem.content_dispersion` | 0.593 | 0.551 |
| | `sem.progression` | 0.586 | 0.541 |
| **syntactic complexity** | `ling.mean_dependency_distance` | 0.587 | 0.520 |
| **disfluency** | `chat.reformulation_per100` | 0.584 | 0.530 |
| *referential, for contrast* | `ling.pronoun_to_noun_ratio` | 0.537 | 0.564 |
| | `ling.det_rate` | 0.512 | 0.509 |

**Every referential measure sits at chance; every volume, richness, syntax and
coherence measure moves.** That is the marker set an Arabic MCI instrument has to
implement, and it is not the one this project built.

### 4.4 The naive-matching cost still stands

Bare closed-class string matching — the Arabic implementation's approach, chosen
because no Arabic parser is available offline — reaches 0.5005 on Delaware,
exactly chance, against 0.535 when existential *"there is/are"* and complementiser
*"that"* are excluded by part of speech. Arabic **هناك** does the same double
duty. A corpus built to this specification should be transcribed and, where
possible, parsed so these uses can be separated.

---

## 5. The specification: what such a corpus must contain

*Every figure is derived from this project's own results rather than asserted.
This is the section another group could act on. It was revised on 25 August 2026
after §4.2, and the previous version — a single-task picture-description corpus
sized for the referential index — is superseded.*

### 5.1 The claim that transfers: genre, not named tasks

**A corpus built from scratch cannot inherit "use the Cinderella task". It can
inherit a claim about what KIND of task carries the signal, and that is what the
measurement supports.**

Delaware administers five tasks to both classes. Three are **picture
description** — Cookie Theft, Cat Rescue, the Norman Rockwell picture — and two
are **connected discourse** — a story retold from a wordless book, and a
procedural description. The partition comes from the corpus protocol and was
declared before the contrast was computed; it is not a grouping selected from the
ranking.

| AUC (MCI vs control, n = 288) | task | genre |
|---|---|---|
| 0.6071 | making a sandwich | **connected discourse** |
| 0.5999 | Cinderella retell | **connected discourse** |
| 0.5779 | Rockwell | picture description |
| 0.5710 | Cat Rescue | picture description |
| 0.5061 | Cookie Theft | picture description |

**The two discourse tasks take the top two places and the three picture tasks the
bottom three, with no overlap.**

| contrast | delta | 95% CI |
|---|---|---|
| mean discourse − mean picture | +0.0518 | [−0.0014, +0.1062] |
| **two discourse tasks administered together − three picture tasks administered together** | **+0.0788** | **[+0.0042, +0.1579]** |

Both are reported and the second leads. The mean-AUC contrast sits on the
boundary — its lower bound is −0.0014 and that is stated rather than rounded
away. The battery contrast is the one a corpus designer needs, because a study
administers a *set* of tasks rather than a mean of AUCs, and it excludes zero:
**two connected-discourse tasks outperform three picture-description tasks
despite being fewer.** (THESIS_PLAN §5.25, figure 5.20.)

**Why the genre level is the right level, and not a hedge.** "Cookie Theft is a
weak MCI task" is a statement about one stimulus, and a group building an Arabic
corpus cannot act on it except by avoiding that one picture. **"Picture
description is the weaker genre for MCI and connected discourse the stronger" is
a statement about task design**, and it survives translation, cultural
substitution and the replacement of every individual stimulus — which is exactly
what building a corpus in another language requires.

**The mechanism makes the genre claim plausible rather than merely observed.** A
picture bounds what there is to say: once the depicted content is named, output
is capped, and volume carries little information — `ling.word_count` reaches only
0.554 on picture description. A narrative or a procedure does not: the speaker
must generate and sustain structure, so volume becomes a measure of what they can
still produce, and word count rises to **0.631**, the strongest single feature of
the 43 tested (§4.3). The same reasoning explains why MCI's earliest deficits —
episodic recall and the sequencing of extended discourse — are taxed by the
discourse genre and largely untaxed by naming what is in front of you.

**The specification therefore requires both genres**, not because both are
equally useful, but because they serve different targets and because a
single-genre corpus cannot separate a marker failure from a task failure — the
error §6 records this project as having narrowly avoided.

### 5.2 The battery, instantiated for Libya

**Delaware's five tasks separate perfectly by genre for MCI** (THESIS_PLAN
§5.25): the two connected-discourse tasks occupy the top two places, the three
picture-description tasks the bottom three, and two discourse tasks administered
together beat three picture tasks administered together by **+0.079
[+0.004, +0.158]**. The corpus must therefore collect **both genres**, because a
corpus is collected once and a single-genre corpus cannot answer the question the
measurement now says matters.

| # | Task | Genre | Target it serves | Why |
|---|---|---|---|---|
| **1** | **Supplied-narrative retell** | discourse | **MCI (primary)** | Delaware's cinderella task at 0.5999 vs cookie 0.5061. The examiner shows a wordless picture book and **withdraws it** before the retelling, so the task loads immediate episodic recall as well as extended-discourse sequencing — which is where MCI presents first. |
| **2** | **Procedural discourse** | discourse | **MCI (primary)** | Delaware's sandwich task at 0.6071 — the strongest single task of the five. Requires no stimulus material at all, which matters for a paper-and-pencil fallback. |
| **3** | **Picture description** | picture | **dementia**, and continuity | The only genre with an externally validated English model behind it (Lu, AUC 0.853), and the only task on which the referential deficit index has any support. |

**Do not translate the Cinderella task, and the corpus's own protocol is why.**
Read verbatim from a Delaware transcript, the examiner says: *"have you ever heard
the story Cinderella?"*, *"do you remember much about it?"*, *"these pictures might
remind you of how it goes… and then I'll put the book away"*, and finally *"tell me
as much of the Cinderella story as you can — you can use any details you know
about the story as well as the pictures you just looked at."*

**So the task is two things at once**: immediate episodic recall of a picture book
shown and then withdrawn, resting on a **semantic scaffold of prior familiarity
with the story**. The episodic half is what makes it a good MCI task. The
scaffold half is what makes it untranslatable — it explicitly requires the
participant to already know the narrative.

**And there is a psychometric argument for substituting it that is independent of
culture.** Where familiarity with the story varies across participants, that
variance enters the measurement as noise unrelated to cognition. An
examiner-read story equalises prior exposure across every participant by
construction. **The substitution is therefore not a compromise made for cultural
reasons; it is the cleaner instrument.**

**The original warning, which still holds:** The
AphasiaBank protocol shows a wordless Cinderella picture book, so the story is
supplied — but familiarity still helps a speaker, and Cinderella's cultural
standing in Libya is not the same as in Delaware. Two safe instantiations, in
order of preference:

- **(a) Examiner-read story recall.** The examiner reads a short standardised
  story aloud; the participant retells it immediately, and again after a delay.
  Cultural knowledge is removed entirely because the story is supplied in the
  session. This is the **Craft Story 21** paradigm used by the NACC Uniform Data
  Set, so an established scoring tradition and English norms exist to translate
  against. **This is the recommended option.**
- **(b) A wordless picture-book narrative** built on a locally shared story.
  Cheaper to administer, but requires the story to be genuinely universal in the
  target population, which must be established rather than assumed.

**The procedural task must use a locally universal procedure.** "How do you make
a peanut butter and jelly sandwich" is not culturally neutral. **Making tea** is
the obvious Libyan instantiation; the requirement is that essentially every
participant has performed the procedure hundreds of times, so that failure
reflects discourse organisation rather than unfamiliarity.

**Picture description uses this project's own artwork** (THESIS_PLAN figure 19,
`app/static/`), not the Cookie Theft, which is copyrighted.

### 5.3 A protocol requirement that is not optional

**Elicitation must be fixed, because `ling.word_count` is the strongest single
MCI marker on discourse (0.631).** If elicitation time or probing varies between
participants, that measure records examiner behaviour as much as speaker ability
and the corpus's primary MCI signal becomes an artefact. Specify and log, per
session:

- a **fixed prompt**, read verbatim;
- a **fixed maximum duration** per task;
- a **fixed re-prompt rule** — how many probes, with what wording, after how many
  seconds of silence;
- the **elicitation time and probe count actually used**, recorded as metadata.

THESIS_PLAN §5.19 is why this is a requirement rather than a nicety: eighteen
healthy speakers in the locked external corpus were flagged because their
descriptions were genuinely thin, and administration is the most plausible cause
that could have been controlled.

### 5.4 The marker families, by target — and the engineering each needs

**The Arabic engine was built around the referential index, which §4.2 shows is a
dementia marker. The MCI marker set is a different set.** This table is organised
by target rather than by convenience, because that is the distinction the
measurement forces and the one a reader must not be allowed to blur.

#### For the MCI target — measured on connected discourse (§4.3)

| Family | Representative measures | Discourse AUC | Arabic-specific requirement | Status |
|---|---|---|---|---|
| **Output volume** | word count, sentence count, utterance count | **0.631**, 0.600 | counts are trivial to compute, but the measure **requires the fixed elicitation of §5.3** or it records examiner behaviour rather than speaker ability | **available** |
| **Lexical richness** | Brunét's W, type–token ratio, repeated-word ratio | 0.598, 0.584 | Arabic is morphologically rich, so **surface-form type–token ratio is confounded by inflection** — the same lemma appears as many types. Must be **lemma-based** | **needs an Arabic lemmatiser — the primary engineering gap** |
| **Semantic coherence** | content dispersion, semantic progression | 0.593, 0.586 | requires **Arabic word or sentence embeddings** running offline | **not available offline** |
| **Syntactic complexity** | mean dependency distance, mean sentence length | 0.587, 0.574 | mean dependency distance requires an **Arabic dependency parser**; mean sentence length needs only reliable utterance segmentation | **parser not available offline; sentence length available** |
| **Disfluency** | reformulations per 100 words | 0.584 | requires **reformulations and self-corrections to be marked in transcription** — they cannot be recovered from a cleaned transcript | **transcription requirement, §5.7** |

#### For the dementia target

| Family | Measure | Evidence | Status |
|---|---|---|---|
| **Referential** | the referential deficit index — demonstratives and vague nouns over nouns | rdi_free **0.596 [0.541, 0.652]** on Pitt; 0.625 on the matched subset. **At chance on MCI on all five tasks (§4.2), as is the English pronoun marker it replaces** | **implemented** — this is what the Arabic engine does today |

**Label it in the corpus documentation and in any Arabic report as what it is: a
dementia-stage referential measure.** Reporting it beside MCI-target measures
without that label is the error this specification exists to prevent.

**The consequence, stated as a finding rather than buried as a requirement.**
**The Arabic engine as built is a dementia instrument.** Making it an MCI
instrument requires an Arabic **lemmatiser**, an Arabic **dependency parser** and
Arabic **embeddings**, all running offline on hardware chosen precisely because it
has no GPU and no network. That is a substantially different engineering problem
from the one this project solved. Naming it exactly — three named components, one
per family, with the family each unlocks — is worth more than a general statement
that "Arabic NLP tooling is limited", and it is what would let another group cost
the work.

**A partial route worth recording, because it is cheap and it is not nothing.**
Two of the five MCI families need no missing component: **output volume** works
today given fixed elicitation, and **mean sentence length** needs only utterance
segmentation. Volume is also the strongest single family (0.631). **A minimal
Arabic MCI probe is therefore buildable now** — fixed-elicitation discourse tasks
scored on volume and sentence length — and it would be a defensible pilot
measurement rather than a full instrument. It should be specified as such, not
promoted beyond what two families can carry.

### 5.5 The minimal probe: what can be built now, without waiting for anything

**This is the most actionable item in this document, and it is buildable today.**
§5.4 lists five marker families for MCI and says three of them need Arabic
components that do not exist offline. **Two do not.** Output volume needs
counting; mean sentence length needs utterance segmentation, which the
transcription convention of §5.7 already supplies. Neither needs a lemmatiser, a
parser, embeddings, a tagger, ASR, or any Arabic normative data.

**And volume is the strongest family, not the weakest.** Measured on Delaware's
two connected-discourse tasks, the 288 complete-case participants at their
earliest common visit (`results/reconstruction/minimal_probe.json`):

> **CORRECTION, 25 August 2026.** An earlier version of this section reported
> that hand-counted words *match or beat* the calibrated ensemble. **That claim is
> withdrawn.** Word count was the argmax over 43 features on these same 288
> participants, while the ensemble's architecture was fixed before the data was
> seen — the two sides were estimated by different procedures. Re-estimating both
> by nested selection inside the folds gives a single-feature comparator of
> **0.6018**, against the ensemble's 0.6379: **the apparatus buys +0.036, not
> nothing** (THESIS_PLAN §5.28, §6.1.0b). The figures below stand as measured;
> what changed is what may be concluded from them.

| What is computed | How | AUC (MCI vs control) |
|---|---|---|
| **total words spoken across the two tasks** | **counted by hand; one number** | **0.6420 [0.5786, 0.7052]** |
| total utterances across the two tasks | counted by hand | 0.6249 |
| word count, z-scored per task then averaged | needs a calculator | 0.6473 |
| word count + sentence count + mean sentence length | needs a calculator | 0.6539 |
| words per utterance | counted by hand | 0.5516 |
| *for contrast:* total words across the three **picture** tasks | counted by hand | **0.5680** |

**The comparison, stated with its asymmetry in the sentence rather than in a
caveat.** On the same two tasks and the same 288 people the ensemble reaches
**0.6379** and hand-counted words reach **0.6420** — but **word count was chosen
as the best of 43 measures using these very participants, and the ensemble was
not chosen at all.** Estimated the same way, by nested selection inside each
training fold, the single-feature comparator is **0.6018**. **The apparatus buys
+0.036.**

**What survives is still substantial.** Word count remains the best hand-countable
measure by a wide margin — it won three of five folds, no rival won more than one,
and the same count on the three picture tasks reaches only **0.5680**. On
connected discourse at the MCI stage, **how much a person can still produce and
sustain is most of the available signal**, and that quantity needs no software.
What does not survive is the claim that counting it is *as good as* the model.

#### What the minimal probe can claim

- **A measured effect size to power a study against — as a RANGE, not a point.**
  Word count's true value on this population lies between roughly **0.60 and
  0.647**: the upper figure is selection-inflated, the lower is the performance of
  a procedure that in two folds of five chose a different feature and so may
  understate word count specifically. One corpus cannot narrow it further.
  **Power on the conservative end: 0.60, which needs 130 per group.**
- **A deployable instrument with no computer in it.** Two prompts, a stopwatch,
  a transcriber and a word count. It runs where there is no electricity, no
  device and no network, which is the condition this project exists for.
- **The first Arabic normative distribution of connected-discourse output volume
  in healthy older speakers**, which is a corpus contribution independent of any
  classification result.
- **A falsifiable prediction**: if Arabic behaves as English does, total words
  across two discourse tasks should separate MCI from control at roughly 0.64.
  If it does not, that is informative about Arabic and reportable as such.

#### What it cannot claim, stated with the same emphasis

- **It is not the marker set.** Three of five families are missing (§5.4). Two
  families cannot carry a diagnostic claim and the probe must not be described as
  a diagnostic instrument.
- **The feature was selected on the same data that evaluates it.** Word count was
  identified as the strongest single measure from these same 288 participants.
  The interval [0.579, 0.705] does **not** account for that selection, and the
  true value should be expected to be lower.
- **It is an English-derived expectation, not an Arabic measurement.** Everything
  above is Delaware. Arabic word counts are not English word counts:
  morphological richness means Arabic conveys in fewer orthographic words what
  English spreads across more, so **the absolute scale will differ and the
  threshold must be derived from local controls, never imported.**
- **It is valid only under the fixed elicitation of §5.3.** Without a fixed
  prompt, a fixed duration and a fixed re-prompt rule, total words measures the
  examiner. **This is not a caveat on the probe; it is a precondition for it.**
  A minimal probe run under variable administration measures nothing.
- **It has no external validation and cannot obtain one**, and under
  THESIS_PLAN §1.7 it may not appear in a table with a validated figure.

#### The recommendation

**Build the minimal probe into the pilot and report it as a pre-registered
secondary outcome**, with its adequacy criterion fixed in advance. It costs the
pilot nothing beyond the transcription it is already doing, it is the only
component of the MCI arm that can run today, and — given that it matches a
calibrated ensemble on the same tasks — it is not a placeholder for a better
instrument. **It may be the instrument.**

### 5.6 Sample size, recomputed for the revised target

Hanley–McNeil, 80% power, two-sided α = 0.05, equal groups.

| True AUC | n per group | What that effect corresponds to |
|---|---|---|
| 0.596 | **141** | referential index, Pitt **dementia** |
| 0.625 | 83 | referential index, matched Pitt subset |
| **0.631** | **75** | `ling.word_count` on discourse, Delaware **MCI** |
| **0.638** | **68** | best two-task discourse model, Delaware **MCI** |
| **0.600** | **130** | **total words across two discourse tasks, conservative end of the honest range (§5.5)** — *use this one* |
| 0.642 | 65 | same measure, selection-inflated upper end — **do not power on this** |
| 0.650 | 57 | a larger effect |

*A note on a discrepancy, recorded rather than smoothed.* The previous version of
this section quoted 125 / 78 / 53 for AUC 0.60 / 0.625 / 0.65; recomputing gives
130 / 83 / 57. The difference is a power-calculation convention, roughly 8%, and
the **larger figures are used here** because under-powering is the failure mode
this section exists to prevent.

| Purpose | Controls required |
|---|---|
| Deployable control-referenced threshold, ±10 points | 59 |
| ...to ±7.5 points | 108 |

**Recommended target: 120 impaired and 120 healthy — unchanged, for changed
reasons.** Previously that number was driven by the referential index's effect
size. It is now driven by two different constraints: **120 controls** delivers a
threshold precise to roughly ±7 points, and **120 impaired** covers the MCI
discourse effect (68–75) with real margin while approaching the dementia
referential effect (141) without quite reaching it.

**A recommendation withdrawn, 25 August 2026.** An earlier version said: *"if
only one target can be afforded, choose MCI on discourse — it needs 75 per group
rather than 141."* **That rested on the selection-inflated 0.638–0.642 figures.**
Powered honestly on the conservative end of the range, **the MCI arm needs about
130 per group and the dementia arm 141. They cost essentially the same.**

**So the choice between targets is now a scientific one rather than a budgetary
one**, and it should be made on that basis: MCI is where early detection changes
management, and it is the target the Arabic instrument as built cannot yet address
(§5.4). Whichever is chosen, say in the write-up that the other arm is
under-powered by design and its null would be uninterpretable.

### 5.7 Transcription, metadata, dialect

**Transcription.** Orthographic, preserving dialectal forms — demonstratives and
vague nouns *are* the measurement for the dementia arm, so a convention
normalising them to MSA destroys the signal. Minimum: verbatim words, utterance
boundaries, pause locations. **Added 25 August:** mark **repetitions,
self-corrections and reformulations**, because `chat.reformulation_per100` is in
the MCI marker set (§4.3) and cannot be recovered from a cleaned transcript.
Where possible mark existential and complementiser uses (§4.4).

**Metadata.** Age, sex, **years of education** (education drives vocabulary and
syntax independently of cognition, and no education-stratified Arabic norms
exist), dialect region, the reference-standard diagnosis with the instrument used
to make it, and — new — **elicitation time and probe count per task** (§5.2).

**Dialect.** Report it explicitly and do not pool distant varieties without
testing. The project's corpus-compatibility rule applies with force: if a
classifier can separate *healthy* speakers of two dialects, those subsets cannot
be naively pooled (negative result 2, AUC 0.930).

### 5.8 What the 20/20 pilot can and cannot do

`docs/libyan_pilot_protocol.md` targets 20 healthy and 20 impaired. At that size,
80% power detects only a **true AUC of 0.748 or larger**.

| n per group | minimum detectable true AUC at 80% power |
|---|---|
| 20 | **0.748** |
| 30 | 0.705 |
| 40 | 0.678 |
| 60 | 0.646 |
| 120 | 0.604 |

**No effect this project has measured is that large.** The pilot therefore cannot
test the referential index (English predicts ~0.60) and cannot test the discourse
MCI effect (0.631–0.638) either. **It was never going to, and the protocol must
say so in its own words rather than leaving it to be inferred.**

What the pilot *can* do, and these are real: establish feasibility and
administration timing under §5.2; produce the first Arabic healthy normative
distributions; validate the dialect word lists against real speech; expose
transcription-convention problems while they are still cheap to fix; and yield a
provisional control-referenced threshold — with the precision the Beta result
gives for 20 controls, which is wide and must be quoted as wide.

---

## 6. What this project contributes, and what it does not

**Contributed.** The linguistic argument for why the English marker does not
transfer; a working Arabic feature engine that computes the replacement; the
first empirical evidence for the construct, obtained in English (§4); a refusal
architecture that emits no Arabic score without validation; the sample-size
derivations above; and `docs/libyan_pilot_protocol.md`, ethics-ready, whose
healthy arm doubles as the normative sample the threshold rule requires.

**Not contributed, and it belongs in the same paragraph.** No Arabic validation.
The referential deficit index has never been computed on the speech of a
diagnosed **Arabic-speaking** patient. The pilot is a **first increment** of the
corpus specified above and reaches roughly a sixth of the recommended n; the
binding constraints are ethics-committee timelines and clinical collaboration,
not method or effort.

**The limits of the search in §2, stated so nobody has to find them.** English
language, one day, web search and direct retrieval of named sources. **Not a
systematic review**: no Arabic-language databases or regional repositories were
searched, no institutional data-sharing agreements investigated, no authors
contacted. It establishes what is *findable and public*, not what exists.
Whoever writes this up should either run a registered systematic search or state
the claim at the strength this one supports — **"no such corpus could be
identified"**, never "no such corpus exists."

---

## 7. How to falsify this

The claim dies to a single counterexample, and the honest thing is to name what
one would look like: a publicly obtainable collection containing (a) Arabic
speakers with a documented cognitive diagnosis **and** Arabic speakers
documented as cognitively healthy, (b) recorded on a connected-speech task,
(c) with transcripts. Aphasia corpora fail (a) — wrong condition. Healthy ASR
corpora fail (a) — one class. The Arabic MoCA dataset fails (b). If such a
corpus is found, this section is retired and the pilot becomes a replication
rather than a first increment. **That would be good news, and this document
should say so.**
