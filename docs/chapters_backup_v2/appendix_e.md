# Appendix E — Sample Session Report

This appendix reproduces one complete session administered through the assessment platform of Chapter 4, exactly as the platform saves it. The session was run after the lock through the platform's own interface endpoints, in the order the browser performs them — session start, one recording upload per task, one operator-confirmed transcript per task, then analysis — and the saved session file for session DEMO-E1 under `data/sessions/` is the source of every figure below. **No participant exists.** The recording uploaded for every task is the project's synthetic sample (`data/samples/sample_control.wav`, produced by `scripts/make_sample.py`, 8.3 seconds of synthesised voiced speech), and the transcripts were typed by the operator for the demonstration — the platform's standard fallback when automatic transcription is not installed, and the way the reference corpus itself was transcribed. The demographic entries (age 68, female, twelve years of education, routine population screening, family history unknown) are demonstration values. The appendix therefore shows what the platform produces and how it words it; it shows nothing about any person.

## E.1 The Session As Administered

The session was started in English, so the platform assembled the four-task English battery and did not offer the recitation task, which is Arabic-only (section 4.2). It rotated the stimuli deterministically from the participant code and session number, selecting the kitchen scene — the validated picture — and the story identified as `teacher`. Table (E.1) lists the battery in administration order with the quality-gate result for each recording. Every recording passed the gate: the synthetic sample runs 8.3 seconds with 6.2 seconds of speech, a signal-to-noise ratio of 37.6 dB and a clipped fraction of 0.0002, against the minima of the quality-gate table in section 4.5. The screening result is computed from the picture description alone; the story-recall and procedural-discourse transcripts are collected and reported as context and do not enter it (section 4.1).

**Table (E.1) : The demonstration session, task by task**

| Order | Task | Time allowed | Stimulus | Transcript words | Quality gate |
|---|---|---|---|---|---|
| 1 | Story recall | 90 s | story `teacher`, read once by the operator | 68 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |
| 2 | Procedural discourse | 90 s | "how tea is made", no stimulus | 88 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |
| 3 | Picture description | 90 s | kitchen scene (validated picture) | 134 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |
| 4 | Verbal fluency | 60 s | animal names | 32 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |

The picture-description transcript, the one the screening score is computed from, was entered as follows.

> This is a kitchen. There is a woman standing at the sink washing the dishes and the water is running over the edge of the sink onto the floor, she has not noticed. Behind her a boy is standing on a stool reaching up to a high shelf for a jar, it looks like a jar of biscuits, and the stool is tipping over. A little girl is standing next to him with her hand up, she wants one too, or maybe she is trying to stop him. There is a cat on the floor watching. On the stove there is a teapot with steam coming out of it. There is a cloth hanging over the edge of the counter, and through the window there is a palm tree and the curtains are open.

## E.2 The Screening Result

The platform ran in its screening-score mode, because the trained model was attached, the session was in English and the picture was the calibrated kitchen scene (section 4.5). The model returned a screening score of **0.218** against the fixed threshold of **0.367**, and the report placed the session in the band it labels *typical*, with the wording: "Below the screening threshold. This speech profile resembles the healthy group in the training corpus." The report carries the model note verbatim — "Screening score from a model trained on labelled clinical data -- a screening score, not a clinical probability." — and states which task the result came from: "The screening result is computed from the picture-description task only. That is the sole task in the training corpus that included healthy controls, and it is the task on which this model was externally validated. The story-recall and procedural-discourse tasks are administered first and recorded, but do not contribute to this result: they carry more signal for MILD impairment, and scoring them would require a new validation study rather than a new setting."

## E.3 The Age Adjusted Result


The age-adjustment chain of section 3.7 then converted the screening score into a posterior. Table (E.2) lists every quantity the report prints for it. The explanation printed beside the number reads: "The speech pattern alone gives 22%. Cognitive impairment (MCI or dementia) affects about 11.0% of people in this age band. Combining that with the speech evidence gives 3.7%." The resulting band is *low*: "Low. On the available evidence, cognitive impairment is unlikely in this person. A single screening result does not exclude it."

**Table (E.2) : The age-adjustment chain as printed on the report**

| Quantity | Value | Report wording |
|---|---|---|
| Speech score | 0.218 | the model's screening score |
| Likelihood ratio | 0.313 | derived from the score against the training prior (section 3.12) |
| Age-band prevalence | 0.11 | "Cognitive impairment (MCI or dementia) affects about 11.0% of people in this age band." |
| Referral multiplier | 1.0 | "Routine screening, no specific concern raised." |
| Family-history multiplier | 1.0 | "Family history unknown; no adjustment applied." |
| Effective prior | 0.11 | prior cap not reached |
| Age-adjusted probability | 0.0372 | band *low* |

## E.4 The Indicator Profile

Independently of the score, the report lists every measured indicator against its reference range — the indicator profile that is the platform's only output when no score can be justified (section 4.4). Table (E.3) reproduces the 19 indicators as printed, grouped as the report groups them, with the plain-language meaning the report attaches to each. 1 of the 19 fell outside its reference range: pitch variation, at 0.028 against a floor of 0.1. That flag is an artefact of the input, not a finding — the synthesised sample recording has an almost constant fundamental frequency by construction — and it illustrates the profile doing what it is for: reporting a measurement the score does not use, so that the operator can see it.

**Table (E.3) : The indicator profile as printed on the report**

| Group | Indicator | Value | Reference | Outside range | Meaning printed on the report |
|---|---|---|---|---|---|
| Discourse coherence | Sentence-to-sentence coherence | 0.865 | ≥ 0.66 | no | Whether consecutive sentences connect to one another. |
| Discourse coherence | Overall coherence | 0.943 | ≥ 0.83 | no | Whether the description stays on topic throughout. |
| Discourse coherence | Semantic looping | 0.000 | 0 – 0.15 | no | Repeating the same idea in different words. |
| Fluency & timing | Speaking vs. silence | 0.756 | ≥ 0.55 | no | Proportion of the recording actually spent speaking. |
| Fluency & timing | Pause frequency | 29.055 | 0 – 32 | no | How often speech is interrupted by silence. |
| Fluency & timing | Average pause length | 0.496 | 0 – 0.75 | no | Long pauses often mean searching for a word. |
| Fluency & timing | Filler rate | 0.000 | 0 – 0.06 | no | 'um', 'uh' - hesitation while searching for words. |
| Grammar & structure | Sentence length | 19.143 | ≥ 7 | no | Sentences get shorter and simpler under cognitive load. |
| Information content | Information units | 21 | ≥ 8 | no | How many of the picture's people, objects and actions were mentioned. The single strongest marker measured in this corpus. |
| Information content | Content coverage | 0.913 | ≥ 0.35 | no | Proportion of the scene actually described. |
| Information content | Actions described | 5 | ≥ 1 | no | Describing what is HAPPENING, not just naming objects. |
| Information content | Objects named | 11 | ≥ 4 | no | How many objects in the scene were named. |
| Information content | Information efficiency | 15.672 | ≥ 7 | no | Information conveyed per hundred words. Low values mean fluent but empty speech. |
| Vocabulary & content | Vocabulary variety | 0.530 | ≥ 0.45 | no | How varied the words are. Falls when word retrieval is effortful. |
| Vocabulary & content | Content-word ratio | 0.410 | ≥ 0.38 | no | How much of the speech carries actual meaning. |
| Vocabulary & content | Idea density | 4.030 | ≥ 3.5 | no | Number of ideas expressed per ten words. |
| Voice | Pitch variation | 0.028 | ≥ 0.1 | yes | Flat, monotone delivery. Also a marker in depression. |
| Word finding & naming | Pronoun-to-noun ratio | 0.517 | 0 – 1.2 | no | Saying 'he put it there' instead of naming things - a word-finding sign. |
| Word finding & naming | Naming rate | 0.216 | ≥ 0.18 | no | How often actual nouns are used - that is, naming rather than pointing. |

## E.5 The Context Tasks And The Severity Index

The two context tasks are reported beside the profile and do not affect the result. Verbal fluency counted 32 animal names with 0 repetitions and 0 unrecognised words; the report attaches the corpus note — "In the Pitt dementia cohort, animal counts fell steadily with severity: 9.4 on average at MMSE 26-30, 6.6 at 16-20, and 2.7 below 11 (r = 0.40 with MMSE, n = 207). For orientation, a normative study of 4,387 cognitively unimpaired adults aged 30-91 reports a mean of about 20 animals in 60 seconds, SD about 5 (Karstens et al., J Int Neuropsychol Soc 30(4):389-401, 2023). Age moderates this more strongly than education, so the figure is not a cut-off and must not be read as one." — and the orientation note that ends: "No validated Libyan-Arabic norm exists, so this figure is context for the operator and does NOT affect the screening result." Story recall credited 27 of 35 idea units from 68 words, with the note: "Story recall tracked severity in the training corpus (r = 0.46 with MMSE, n = 237), so it is reported as a severity indicator. It cannot give a healthy-vs-impaired threshold, because the corpus contains this task for the dementia group only." The severity index, estimated from the picture, fluency and recall tasks combined, placed the session in the *mild range* band and printed its own status in full: "r = 0.65 against real MMSE, average error 3.3 points (n = 155) - the deployed model's own recorded figure. A pre-registered rebuild could NOT reproduce it (grade CANNOT-CONFIRM, rebuilt cohort n = 156 against the recorded 155), so treat this as artifact metadata, not a verified result." — the CANNOT-CONFIRM grade of section 5.7 travelling with the output, as the design requires.

## E.6 The Caveats Printed On Every Report

Two texts appear on every screening-score report, and both were present here. The stimulus-substitution caveat of section 4.3.1 reads: "The picture shown is not the picture this model was calibrated on. The original belongs to a published test and cannot be redistributed, so an equivalent scene drawn for this project is used instead. Every item the scorer looks for is present in it, but the two pictures are not interchangeable, and the effect of the substitution on real speakers has never been measured. If this picture costs a speaker even one of the items the original would have prompted, roughly one healthy recording in eight would move from a negative screen to a positive one. Weigh this score accordingly until the substitution has been checked on a local sample." And the disclaimer that heads the report reads: "ذِكرى is a SCREENING aid, not a diagnostic test. It cannot diagnose Alzheimer's disease or any other condition. This report describes measured speech characteristics only and must be interpreted by a qualified clinician. Reference ranges are orientation values, not validated diagnostic cut-offs."

## E.7 What The Demonstration Shows And Does Not


The session exercised every stage the platform performs on a real session — battery assembly, audio conversion, the acoustic engine, the quality gate, the typed-transcript fallback, the linguistic and information-unit engines, the screening model, the age-adjustment chain, the indicator profile, the context tasks and the caveat texts — and produced the report a clinician would receive. Two limitations are stated so that the appendix is not mistaken for more than it is. First, the acoustic indicators (the *Fluency & timing* and *Voice* rows of Table (E.3)) describe an 8.3-second synthesised recording, so their values are meaningful only as evidence that the engine ran; the one atypical flag is the synthesis, not speech. Second, the fluency context text compares a count of 32 animals to the dementia cohort's mildest band, because the report's severity comparison has no band above that cohort's healthiest mean — a wording limitation of the current build that a healthy adult's count exposes, recorded here rather than hidden. The report file, the driver that produced it and the transcripts entered are committed with the project.
