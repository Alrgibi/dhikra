# Appendix G — The Transcription Artefact Audit

This appendix is the full record of the transcription artefact summarised in
section 3.2.1: what the defect is, how large it is, why it correlates with
diagnosis, why it survived a guard designed to exclude exactly this class of
contamination, what it costs, and why it was left in place. Sources:
`scripts/transcription_artefact_probe.py`, whose docstring carries the audit
record and whose criteria were committed before the measurement ran, and
`results/reconstruction/transcription_artefact_probe.json`.

## G.1 The Defect

CHAT transcription marks an omitted sound with parentheses: a speaker who said
*dryin'* is transcribed `dryin(g)`. The transcript cleaner
(`chat_parser.clean_utterance`) strips most CHAT markup and not this form, so
the token reaching the feature extractors is `dryin(g)`, with three silent
consequences. First, the tokeniser splits it into four tokens — `dryin`, `(`,
`g`, `)` — so the verb is never recognised, and the affected words are exactly
the action verbs the information-unit scorer looks for: `dryin(g)` occurs 96
times, `runnin(g)` 84, `washin(g)` 69, `fallin(g)` 67, `gettin(g)` 67,
`reachin(g)` 43 and `standin(g)` 37. Second, `dryin` and `drying` count as
different types, corrupting the type-token ratio, MATTR-50, Brunet's W and
Honoré's R. Third, the scale is material: 58.9% of Pittsburgh transcripts are
affected, 1,193 tokens in all, 1.88% of every token in the corpus.

## G.2 The Rate Is Differential By Class

The reason this is more than a typo is that the rate differs by diagnosis, as
Table (G.1) shows.

**Table (G.1) : Parenthesised-omission rates by corpus and class**

| Corpus | Control rate (per 100 words) | Impaired rate | Transcripts affected (control / impaired) | AUC of the artefact alone |
|---|---|---|---|---|
| Pittsburgh | 1.44 | **3.18** | 49.4% / 77.0% | **0.6908** |
| Delaware | 0.123 | 0.183 | 10.8% / 15.0% | 0.5220 |
| Lu | 0.084 | 0.210 | — | — (8 forms in the whole corpus) |

The Pittsburgh artefact alone discriminates at 0.6908 — above most individual
deployed features. The other two corpora settle what it is: the same CHAT
convention, at different sites with different transcribers, occurs an order of
magnitude less often and discriminates at chance, and a genuine phonetic
property of impaired speech would not be ten times rarer in another cohort of
impaired speakers. This is a Pittsburgh transcription practice that correlates
with diagnosis.

## G.3 Why It Survived The Guard

The deployed feature set deliberately contains no `chat.*` markup features,
because the corpus-compatibility finding showed transcription convention alone
separates two *healthy* groups from different corpora at an AUC of 0.930. That
exclusion removed markup *features*; it did not remove markup from the
*transcript text* that the linguistic features are computed on. The guard was
correct in principle and incomplete in execution, and it took a hand audit of
the raw text to find the residue. The lesson generalises: excluding a
contaminated feature family does not exclude the contamination if it is also
inside the input.

## G.4 What It Costs As Measured


All 64 deployed features were re-extracted from corrected text — parenthesised
sounds restored, residual non-word characters stripped — with the deployed
architecture, folds and seed unchanged. The Pittsburgh AUC moved from 0.8095
to 0.7996, a difference of −0.0099 against a pre-registered material band of
−0.01: the registered grade is ARTEFACT-NEGLIGIBLE, by one ten-thousandth, and
the number, the band and the margin are all reported because the grade without
the margin would be a rounding. At single-feature level the largest movements
are the information-unit totals (`iu.total` 0.7538 to 0.7465, `iu.actions`
0.7332 to 0.7155), consistent with the mechanism in section G.1.

Two further readings follow. The artefact is also a train/serve mismatch: the
application transcribes with a speech recogniser that emits standard
orthography, so the parenthesised form cannot occur at inference, the model
was fitted partly on a signal channel that does not exist in deployment, and
0.7996 is the closer estimate of what the deployed system receives. And the
external result cannot be artefact-driven: the check of the Lu corpus —
declared descriptive before it ran, since counting a text pattern is metadata
inspection of the same category as reading the header fields that supply ages
and diagnoses — found eight parenthesised-omission forms in the entire corpus —
seventeen times rarer than Pittsburgh's control rate. A model that depended on
that channel would have lost performance where the channel is absent; it
produced its highest figure there instead.

## G.5 Why It Was Not Fixed

Correcting the extractor changes the features the frozen model receives and
would forfeit the locked external validation, which cannot be repeated. The
correction is instead specified for the next iteration:
`clean_utterance` should restore parenthesised sounds and strip residual
non-word characters, and the next external corpus should be spent on the
corrected pipeline.

## G.6 A Smaller Defect From The Same Audit

The information-unit key contains `window` in both the `exterior` place
category and the `window` object category, so a speaker who says *window* and
nothing else about outdoors earns two information units where the standard
Cookie Theft checklists credit one. It is a deviation from the
Yorkston–Beukelman and Nicholas–Brookshire inventories the rest of the list
follows [2, 3], and it inflates `iu.total` by one for those speakers. It is
left in place for the same reason as the artefact — the model is frozen — and
carried on the same fix list.

## G.7 Provenance Notes

Two details complete the record. First, a corroborating observation from the
descriptive check: one Lu file's group header reads `Conrol`, and the locked
27 control / 26 impaired split adds up exactly only if that file was handled
as a control, which the corpus build did — evidence of care in the build,
found while counting something else. Second, the sourcing of the counts in this
appendix. The Pittsburgh artefact figures are recorded in the committed probe
script and its result file, and the raw filled-pause count reproduces exactly
— 1,881 of 1,881 — from the committed parser
(`results/reconstruction/pitt_filled_pause_count.json`). The Lu counts were
recommitted after the lock (`scripts/lu_artefact_check.py` →
`results/reconstruction/lu_artefact_check.json`): the count of eight
reproduces exactly once the pattern is read as the original evidently read it
— all parenthesised omissions, whole-word forms such as *(be)cause* and
*(there)* included, not only word-attached sounds — and the class rates in
Table (G.1) are the recommitted values (0.084 control, 0.210 impaired per 100
words; the working record's 0.065/0.220 came from the uncommitted run and is
superseded). The registered word-attached criterion is recorded as failed as
written, with the decoding in the result file's post-execution notes; the
substance — the channel is effectively absent externally — is unchanged under
either reading.
