#!/usr/bin/env python3
"""cut2_flips4.py -- fourth flip pass: Chapter 2 (five lines) and Appendix B (six lines)."""
import re
ROOT = "/home/claude/work/src/docs/chapters/"
FILES = {"c2": ROOT + "chapter2.md", "B": ROOT + "_pending/appendix_b.md"}
T = {k: open(v, encoding="utf-8").read() for k, v in FILES.items()}
Bw = {k: len(v.split()) for k, v in T.items()}
def ws(s): return r"\s+".join(re.escape(w) for w in s.split())
def rep(f, old, new):
    pat = ws(old); n = len(re.findall(pat, T[f]))
    assert n == 1, (f, old[:70], n)
    T[f] = re.sub(pat, lambda m: new, T[f])

rep("c2", "To the author's knowledge, no publicly available Libyan Arabic connected-speech corpus for dementia screening has been published, and no prior work has adapted spontaneous picture-description analysis to Arabic. Both clauses are stated at exactly that strength: the searches behind them are documented in section 6.4, and a single counterexample retires the claim. The two arguments of this chapter jointly fix the thesis's position: the field reports high figures in an evaluation regime that has never been shown to transfer, and the regime that does transfer is the one this thesis reports in; the language this project serves has no corpus on which even the field's ordinary regime could be run, and the thesis therefore contributes, alongside its externally evaluated English screening model, the documented absence and the specification that would close it (sections 6.4 and 6.5).",
    "To the author's knowledge, no publicly available Libyan Arabic connected-speech corpus for dementia screening has been published, and no prior work has adapted spontaneous picture-description analysis to Arabic; the searches behind both clauses are documented in section 6.4, and a single counterexample retires the claim. The two arguments of this chapter fix the thesis's position: the field reports high figures in an evaluation regime never shown to transfer, and this thesis reports in the regime that does; the language this project serves has no corpus on which even the field's ordinary regime could be run, so the thesis contributes, beside its externally evaluated English screening model, the documented absence and the specification that would close it (sections 6.4 and 6.5).")
rep("c2", "The remainder of the Arabic landscape divides into acoustic probes and structured instruments. A Tunisian Arabic database supports early-detection work built on voice onset time — an acoustic, phonetic measure, not connected-speech analysis — and is not publicly accessible [14]. An Arabic transcript dataset has been used to classify Alzheimer's from linguistic and acoustic features with standard machine-learning methods, again without public release [15].",
    "A Tunisian Arabic database supports early-detection work on voice onset time, an acoustic measure rather than connected-speech analysis, and is not publicly accessible [14]. An Arabic transcript dataset has been used to classify Alzheimer's from linguistic and acoustic features, again without public release [15].")
rep("c2", "standard clinical voice measures — fundamental frequency, jitter and shimmer, pause and timing statistics — established and language-independent but requiring usable audio, which is why this project implements them in a separate acoustic model that never enters the deployed screening score;",
    "standard clinical voice measures — fundamental frequency, jitter and shimmer, pause and timing statistics — established and language-independent but requiring usable audio, so this project implements them in a separate acoustic model outside the deployed screening score;")
rep("c2", "both above chance (section 5.12). Table (2.2) states the comparison at the level that carries the argument.",
    "both above chance (section 5.12); Table (2.2) states the comparison.")
rep("c2", "retrain on Pittsburgh minus the ADReSS test participants and evaluate on the ADReSS test set, as a reported experiment that never touches the deployed model.",
    "retrain on Pittsburgh minus the ADReSS test participants and evaluate on the ADReSS test set, never touching the deployed model.")

rep("B", "The collaborating clinician is asked for permission to approach patients attending their service, administration or supervision of the Arabic Montreal Cognitive Assessment, confirmation of existing diagnoses from the medical record, a quiet room for about 20 minutes per participant, clinical oversight including the authority to stop any session, and co-authorship on any publication — and is not asked to use the system, act on its output, change any aspect of patient care, or take responsibility for the analysis.",
    "The collaborating clinician is asked for permission to approach patients, administration or supervision of the Arabic Montreal Cognitive Assessment, confirmation of existing diagnoses from the medical record, a quiet room for about 20 minutes per participant, clinical oversight including the authority to stop any session, and co-authorship — and is not asked to use the system, act on its output, change patient care, or take responsibility for the analysis.")
rep("B", "so the protocol is submitted as a completed, ethics-ready study design, which converts \"Arabic validation is future work\" from an aspiration into a specified, costed, ethically framed plan that another researcher could execute.",
    "so the protocol is submitted as a completed, ethics-ready study design that another researcher could execute.")
rep("B", "— an order statistic of a single group, fixed before any group comparison is run and reported whatever that comparison shows.",
    "— an order statistic fixed before any group comparison is run and reported whatever it shows.")
rep("B", "The screening score was calibrated on descriptions of the Cookie Theft picture, which the system does not show,",
    "The screening score was calibrated on the Cookie Theft picture, which the system does not show,")
rep("B", "Two earlier figures in this section were corrected and the corrections are kept on the record:",
    "Two earlier figures were corrected and the corrections kept on the record:")
rep("B", "This subsection fixes the design of the study the pilot exists to make possible, so that the decision is on the record before recruitment starts.",
    "This subsection fixes the design of the study the pilot prepares, so that the decision is on the record before recruitment starts.")
rep("B", "since a dementia diagnosis is at least sometimes recorded in a Libyan family while a mild-impairment diagnosis requires neuropsychological testing the regional literature says is largely unavailable.",
    "since a dementia diagnosis is at least sometimes recorded while a mild-impairment diagnosis requires neuropsychological testing the regional literature says is largely unavailable.")
rep("B", "fails because group and task are different axes: the group axis (dementia, mild impairment, control) is decided here, and the task axis is decided by the battery, which administers both genres to every participant whoever is recruited.",
    "fails because group and task are different axes: the group axis is decided here, the task axis by the battery, which administers both genres to every participant whoever is recruited.")
rep("B", "each condition corresponds to a degradation the platform's quality gate was tested against (section 5.9).",
    "each condition corresponds to a degradation the quality gate was tested against (section 5.9).")
rep("B", "The Qur'anic probe additionally records which surah was recited, self-reported familiarity, approximate age at memorisation and any formal tajweed training, the confounders without which recitation accuracy is uninterpretable.",
    "The Qur'anic probe additionally records the surah recited, self-reported familiarity, approximate age at memorisation and any formal tajweed training, without which recitation accuracy is uninterpretable.")
rep("B", "with total and item-level subscores, the education correction as applied, any existing clinical diagnosis with its date, and whether that diagnosis was made by a specialist. The assessment is administered after the speech recording, so that a demanding test does not fatigue the participant into an unrepresentative speech sample.",
    "with total and item-level subscores, the education correction as applied, any existing clinical diagnosis with its date and whether a specialist made it, administered after the speech recording so that a demanding test does not fatigue the participant into an unrepresentative sample.")
rep("B", "The sample is defined by a minimum of 20 and a target of 40, recruited across the two strata of Table (B.1);",
    "The sample is a minimum of 20 and a target of 40 across the two strata of Table (B.1);")
rep("B", "Each exclusion removes a factor that would confound speech measurement independently of cognition:",
    "Each exclusion removes a confounder of speech measurement independent of cognition:")

for k, v in FILES.items():
    open(v, "w", encoding="utf-8").write(T[k]); print(k, "words", Bw[k], "->", len(T[k].split()))
