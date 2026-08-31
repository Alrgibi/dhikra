#!/usr/bin/env python3
"""revise4.py -- Part 5 (pairing rule), the two further 3.7 sites, Part 6 phrase compression,
Chapter 5 caption takeaways, and residual scaffolding in Appendices D and E."""
from revlib import rep, write, count

# ═══════════ Part 5: pairing rule ═══════════
rep("chapter3.md",
    "The specificity collapse is reported rather than buried, because exposing it is what a locked test set is for.",
    "The specificity collapse is reported in full because exposing it is what a locked test set is for; its diagnosis — a threshold referenced to the wrong distribution, with a remedy analysed but not deployed — is in sections 5.15 to 5.19.")
rep("chapter3.md",
    "Delaware trained on itself scores 0.5474, an interval spanning chance, so the ratio came out at 1.18",
    "Delaware trained on itself scores 0.5474, an interval spanning chance (the finding is owned by section 5.12.1, and its remedy — a different elicitation genre — by section 5.25), so the ratio came out at 1.18")
rep("appendix_b.md",
    "and the analysis in `docs/TRANSPORT_AND_REPORTING.md` establishes that this was a *threshold referencing* failure rather than a model failure.",
    "and the analysis of sections 5.15 to 5.19 establishes that this was a *threshold referencing* failure rather than a model failure.")
rep("appendix_b.md",
    "On mild cognitive impairment the instrument is close to chance: the Delaware Cookie Theft task returns 0.5061 and cross-corpus transfer 0.629.",
    "On mild cognitive impairment the instrument is close to chance: the pooled development figure is 0.6291 [0.5703, 0.6868], and the Delaware Cookie Theft task alone returns 0.5061 in the task probe — which is why the battery below leads with connected discourse (section 5.25).")
rep("appendix_b.md", "absolute difference 1.600 against a threshold of 1.200; THESIS_PLAN §5.5.1).",
    "absolute difference 1.600 against a threshold of 1.200; section 5.5.1).")
rep("appendix_c.md",
    "whose protocol the card states in the same words as section C.2.",
    "whose protocol the card states in the same words as section C.2. The `limitations` rows are the locked operating point at threshold 0.367; the specificity they record is diagnosed as a threshold-referencing failure, with the remedy analysed and not deployed, in sections 5.15 to 5.19.")
rep("appendix_c.md",
    'Mild cognitive impairment: "Mild cognitive impairment is materially harder (0.629). Trained on Delaware alone the same architecture reaches only 0.547, an interval spanning chance (results/reconstruction/cross_corpus_transfer.json)."',
    'Mild cognitive impairment: "Mild cognitive impairment is materially harder (0.629). Trained on Delaware alone the same architecture reaches only 0.547, an interval spanning chance (results/reconstruction/cross_corpus_transfer.json)." That limitation is diagnosed in section 5.12.1, and the successor answers it with the task-genre finding of section 5.25.')
rep("front.py", "and 0.6291 [0.5703, 0.6868] for mild cognitive impairment.",
    "and 0.6291 [0.5703, 0.6868] for mild cognitive impairment, the target on which the picture-description architecture performs weakly and for which connected discourse proved the more promising elicitation genre.")
rep("front.py", "و0.6291 [0.5703، 0.6868] للضعف المعرفي البسيط.",
    "و0.6291 [0.5703، 0.6868] للضعف المعرفي البسيط، وهو الهدف الذي تضعف فيه بنية وصف الصورة المنشورة، والذي تبيّن أن الخطاب المتصل هو نوع الاستثارة الأكثر وعداً له.")

# ═══════════ 3.7, two further sites ═══════════
rep("chapter5.md", "which over-refers — the safe failure direction for a screening instrument.",
    "which over-refers. The observed error direction favours sensitivity over missed cases, but excess false positives remain an equity, anxiety and resource-use concern.")
rep("appendix_b.md", "For a screening instrument that is the safe direction of failure: the cost is wasted clinical assessments, not missed cases.",
    "That error direction favours sensitivity over missed cases, but excess false positives remain an equity, anxiety and resource-use concern.")

# ═══════════ Part 6: the "rather than" tic ═══════════
rep("chapter2.md", "The cost is measured rather than denied: the whole", "The cost is measured: the whole")
rep("chapter2.md", "The honest general form is that", "The general form is that")
rep("chapter2.md", "and the honest description of the modelling is modest and real, not state of the art.", "and the modelling is modest and real, not state of the art.")
rep("chapter2.md", "That is a claim about evidence, not about superiority, and it is the honest one.", "That is a claim about evidence, not about superiority.")
rep("chapter3.md", "this was measured rather than assumed and is reported in Chapter 5.", "this was measured and is reported in Chapter 5.")
rep("chapter3.md", "The cost was measured rather than argued: re-extracting", "The cost was measured: re-extracting")
rep("chapter3.md", "failure is reported rather than iterated away.", "failure is reported, not iterated away.")
rep("chapter4.md", "The size of the omission was then measured rather than estimated — pre-registered,", "The size of the omission was then measured — pre-registered,")
rep("chapter5.md", "was searched rather than assumed, under four fixed conditions:", "was searched under four fixed conditions:")
rep("chapter5.md", "The conclusion, searched rather than assumed: under the four constraints", "The conclusion of that search: under the four constraints")
rep("chapter5.md", "the reasons are now measured rather than asserted, which is the difference between a concession and a result.",
    "the reasons are now measured, which is the difference between a concession and a result.")
rep("chapter5.md", "and it was measured rather than argued away.", "and it was measured.")
rep("chapter5.md", "Why this is reported rather than quietly fixed:", "Why the withdrawal is reported:")
rep("chapter5.md", "and that has now been measured rather than assumed.", "and that has now been measured.")
rep("chapter6.md", "which is exactly why the test must be run per project rather than assumed in either direction.",
    "which is exactly why the test must be run per project; it cannot be assumed in either direction.")
rep("chapter6.md", "were checked for provenance rather than assumed clean, and the checking is part of the record.",
    "were checked for provenance, and the checking is part of the record.")
rep("chapter6.md", "is measured rather than worried about: 0.708", "is measured: 0.708")
rep("appendix_d.md", "applicability argued rather than assumed |", "applicability argued |")
rep("appendix_d.md", "the fold-grouping null measured rather than assumed (§3.6.1)", "the fold-grouping null measured (§3.6.1)")

# ═══════════ Part 6: "honest" and the other self-descriptions (Chapters 5, 6, appendices) ═══════════
rep("chapter5.md", "The honest reading favours the design, and it is written as a finding rather than a confession.", "The reading favours the design.")
rep("chapter5.md", "One further honest qualification:", "One further qualification:")
rep("chapter5.md", "The figure is reported with its governance, never without it. 0.8533 is", "0.8533 is")
rep("chapter5.md", "Then the specificity, reported honestly and not left as a bare number: 96.2%", "Then the specificity: 96.2%")
rep("chapter5.md", "so the honest prediction is an AUC near 0.6", "so the prediction is an AUC near 0.6")
rep("chapter5.md", "The honest boundary of the claim is stated, because it is checkable:", "The boundary of the claim is checkable:")
rep("chapter5.md", "because the asymmetry is the honest content of the result.", "because the asymmetry is the content of the result.")
rep("chapter5.md", "It makes specificity the fixed quantity and sensitivity the honest variable.", "It makes specificity the fixed quantity and sensitivity the reported variable.")
rep("chapter5.md", "That property was measured after the fact, and it is stated as such rather than as a design intention.", "That property was measured after the fact, not designed.")
rep("chapter5.md", "Stated plainly before any explanation: within this cohort,", "Within this cohort,")
rep("chapter5.md", "and that is stated plainly as a property of the field's data.", "a property of the field's data.")
rep("chapter5.md", "The verdict is deliberately modest:", "The verdict is modest:")
rep("chapter5.md", "What it costs the Arabic contribution is stated plainly where that contribution is specified:", "What it costs the Arabic contribution is stated where that contribution is specified:")
rep("chapter6.md", "stated as one claim rather than as a series of separate honesty episodes:", "stated as one claim:")
rep("chapter6.md", "sensitivity the honestly reported variable,", "sensitivity the reported variable,")
rep("chapter6.md", "powered on the conservative end of its honest range,", "powered on the conservative end of its range,")
rep("chapter6.md", "since powered honestly the two arms cost essentially the same", "since, powered on the conservative end, the two arms cost essentially the same")
rep("chapter6.md", "The pro-drop argument survives unchanged, and it is stated plainly so the two conclusions are not confused.", "The pro-drop argument survives unchanged, and it is restated so that the two conclusions are not confused.")
rep("chapter6.md", "The cost is stated as directly as it deserves: mild impairment", "The cost is this: mild impairment")
rep("appendix_d.md", "An assessment of this kind is reported honestly or it is decoration:", "An assessment of this kind is reported in full or it is decoration:")
rep("appendix_d.md", "**The honest entry of the whole table**:", "**The entry that matters most**:")
rep("appendix_h.md", "the honest order of", "the true order of")
rep("appendix_h.md", "The honest generalisation is that", "The generalisation is that")
rep("appendix_h.md", "a claim no honest project could make", "a claim no project could make")
rep("appendix_i.md", "Its honest expected value,", "Its expected value,")
rep("appendix_i.md", "and powered honestly the two arms cost essentially the same", "and powered on the conservative end the two arms cost essentially the same")
rep("appendix_b.md", "**Read this honestly rather than as an argument for a bigger study than can be run.**", "**Read this as a bound, not as an argument for a bigger study than can be run.**")
rep("appendix_b.md", "those are the honest figures for a", "those are the figures for a")
rep("appendix_b.md", "**So the honest expectation for an Arabic dementia", "**So the expectation for an Arabic dementia")
rep("appendix_b.md", "**With the comparison stated honestly.**", "**With the comparison stated in full.**")

# ═══════════ residual scaffolding: Appendices D and E ═══════════
rep("appendix_d.md", "All three citations were verified against the published articles during writing. The tables below state,", "The tables below state,")
rep("appendix_d.md",
    "with the section of the thesis that carries each answer; the item-by-item checklists with page references are completed at assembly against the instruments' published PDFs, since page numbers do not exist until the document is laid out.",
    "with the section of the thesis that carries each answer; the item-by-item checklists are not reproduced, and this topic-level assessment is the record.")
rep("appendix_d.md", "| Title and abstract | At assembly | Front matter; the abbreviated abstract checklist is applied there |",
    "| Title and abstract | Satisfied | Front matter; the abstract states the target, the data, the model, the development and external figures with their intervals, and the external corpus's exposure |")
rep("appendix_d.md", "| Ethics and funding | Satisfied / at assembly |", "| Ethics and funding | Satisfied |")
rep("appendix_d.md", "Funding statement at assembly |", "The corpora's supporting grants are acknowledged in the front matter |")
rep("appendix_e.md", "The session was run at assembly through the platform's own interface endpoints,", "The session was run after the lock through the platform's own interface endpoints,")
rep("appendix_e.md", "the saved session file `data/sessions/DEMO-E1_20260828_044613.json` is the source of every figure below.",
    "the saved session file for session DEMO-E1 under `data/sessions/` is the source of every figure below.")

# ═══════════ Chapter 5 caption takeaways (whole caption is bold by style) ═══════════
TAKE = {
 "5.1":  "The dementia target is learned well and the mild-impairment target poorly, and that gap is the chapter's principal finding.",
 "5.2":  "A single hand-countable information-unit total reaches 0.7096 against the deployed model's 0.7550; the model buys about 4.5 points of AUC over a paper checklist.",
 "5.3":  "Women are classified sixteen AUC points better than men, the largest disparity the instrument carries, and neither a threshold nor a rescaling repairs it.",
 "5.4":  "Sensitivity within MMSE band is equal or better for men in three of four bands; the sex gap is a specificity failure, not a sensitivity failure.",
 "5.5":  "The frozen model held its discrimination out of sample; the 33.3% specificity is a threshold-referencing failure diagnosed in sections 5.15 to 5.19, with a remedy analysed but not deployed.",
 "5.6":  "Deviation is confined to the top band and is conservative: the model understates risk where it is most confident.",
 "5.7":  "The uncorrected likelihood ratio understates strong evidence by up to 0.16 of posterior probability and never overstates it.",
 "5.8":  "The recalibration fails in both transfer directions on both criteria, grade CORRECTION-DOES-NOT-TRANSFER, because the two cohorts are miscalibrated in opposite directions.",
 "5.9":  "The 19-feature Arabic-compatible subset keeps 97.9% of the full model's AUC; age alone reaches 0.5571.",
 "5.10": "Sensitivity falls monotonically from 100% in the severe band to 63.0% in the normal-range band; the instrument is weakest where early detection matters most.",
 "5.11": "Fifteen claims were tested and not made; three changed a design decision, and none was a wasted experiment.",
 "5.12": "The pipeline tolerates compression, telephone bandwidth, low volume, clipping and distance, and fails at 10 dB background noise, which is the empirical basis of the quality gate.",
 "5.13": "The pronoun-free index separates the dementia cohort, 0.596 and 0.625 matched, and sits near chance on mild impairment: a dementia-stage marker, not an early one.",
 "5.14": "Predictive values are prevalence-dependent: at 10% prevalence a positive screen is an invitation to assessment, never a finding; the external row carries the exposure history of section 3.9.",
 "5.15": "A model trained only on Delaware ranks Pittsburgh at 0.777, the independent justification for pooling; Delaware's own reference, 0.547, spans chance.",
 "5.16": "The cohorts' score distributions differ structurally, so the threshold and the calibration map are local quantities to be set per deployment.",
 "5.17": "One map fitted on pooled development data improves the external slope while worsening its intercept and Brier score; the transport problem is not a calibration bug.",
 "5.18": "Specificity is delivered to target within two points in all three cohorts and sensitivity becomes the reported variable; Delaware's 0.356 is its discrimination problem reappearing.",
 "5.19": "Prospective specificity from 27 controls is 0.786 [0.62, 0.91]; a ±10-point interval needs about 59 healthy speakers, which sets the pilot's normative sample size.",
 "5.20": "The eighteen misclassified external controls described the picture measurably less well, 11.5 information units against 14.9, so no threshold rule could have separated them.",
 "5.21": "The false positives omitted the scene's key content items, consistent with thin descriptions rather than classifier malfunction.",
 "5.22": "Removing the most corpus-shifted features makes transfer toward the mild-impairment cohort worse at every k; domain shift is not repaired by deletion (negative result 7).",
 "5.23": "The raw information-unit count beats its density form on every set, so the paper fallback stays a count.",
 "5.24": "No minimum-length rule fixes specificity: the largest gain in the sweep, +0.069 at 90 words, keeps only 0.559 of controls, and brevity in a healthy speaker is signal the model is right to weigh.",
 "5.25": "The two connected-discourse tasks occupy the top two places for mild impairment and every picture task sits below them; the recoverable signal lives in the genre, not the picture.",
}
import re
src = __import__("revlib").TXT["chapter5.md"]
for num, take in TAKE.items():
    m = re.search(r"^\*\*Table \(%s\) : (.*?)\*\*$" % re.escape(num), src, re.M)
    assert m, num
    old = m.group(0)
    title = m.group(1).rstrip(".")
    new = "**Table (%s) : %s. %s**" % (num, title, take)
    rep("chapter5.md", old, new)
    src = __import__("revlib").TXT["chapter5.md"]

write("revise4: ")
