#!/usr/bin/env python3
"""revise3.py -- Part 2.2 (headline sentence) and Part 3 (precision sentences 3.2-3.10)."""
from revlib import rep, write, count

HEADLINE = ("Locked external performance: AUC 0.8533 [0.7371, 0.9458], sensitivity 96.2%, specificity 33.3%. "
            "Subsequent threshold-transport analysis recovered external specificity to 77.8% by control-referenced thresholding "
            "— a post-hoc methodological contribution, not preregistered, not deployed, and requiring prospective validation.")
CANON = ("The corpus was excluded from the training data of the final model and from every modelling decision after the lock. "
         "Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool.")

# ───────── 2.2 + 3.2: abstract (EN, AR) ─────────
rep("front.py",
    "Scored once on a third corpus at a threshold fixed in advance, the deployed model reached AUC 0.8533 [0.7371, 0.9458] with sensitivity 0.9615 and specificity 0.3333; the corpus was excluded from the training data of the final model and from every modelling decision after the lock. Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool. That exposure is reported rather than hidden. The specificity failure was diagnosed as a threshold-transport problem and answered with a control-referenced thresholding rule that reads no labels and holds specificity to target in every cohort, an analysed rather than deployed contribution.",
    "Scored once on a third corpus at a threshold fixed in advance, the frozen English screening model reached external AUC 0.8533 [0.7371, 0.9458], sensitivity 96.2%, specificity 33.3%; " + CANON.replace("The corpus", "the corpus") + " That exposure is reported, not hidden. Subsequent threshold-transport analysis recovered external specificity to 77.8% by control-referenced thresholding, a rule that reads no labels — a post-hoc methodological contribution, not preregistered, not deployed, and requiring prospective validation.")
rep("front.py",
    "وعند تقييم النموذج مرة واحدة على مجموعة ثالثة عند عتبة حُدِّدت مسبقاً، بلغ 0.8533 [0.7371، 0.9458] بحساسية 0.9615 ونوعية 0.3333؛",
    "وعند تقييم نموذج الفحص الإنجليزي المجمَّد مرة واحدة على مجموعة ثالثة عند عتبة حُدِّدت مسبقاً، كان الأداء الخارجي المقفل: مساحة تحت المنحنى 0.8533 [0.7371، 0.9458]، وحساسية 96.2%، ونوعية 33.3%؛")
rep("front.py",
    "شُخِّص فشل النوعية بوصفه مشكلة في نقل العتبة، وعولج بقاعدة عتبة مرجعية بالضوابط لا تقرأ أي تصنيف وتحافظ على النوعية عند الهدف في كل مجموعة، وهي مساهمة محلَّلة لا منشورة للاستخدام.",
    "وقد استعاد تحليلٌ لاحق لنقل العتبة النوعيةَ الخارجية إلى 77.8% عبر عتبة مرجعية بالضوابط لا تقرأ أي تصنيف — وهي مساهمة منهجية لاحقة، غير مسجَّلة مسبقاً، وغير منشورة للاستخدام، وتتطلب تحققاً استباقياً.")

# ───────── 2.2 + 3.2: Chapter 1 §1.7 ─────────
rep("chapter1.md",
    "Validated: the deployed instrument was evaluated exactly once, on a corpus evaluated at a threshold fixed in advance — AUC 0.853 [0.737, 0.946] — under the governance of section 3.9: the corpus was excluded from the training data of the final model and from every modelling decision after the lock. Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool. The figure is reported under the exposure history reported in full in section 3.9. That evaluation cannot be repeated:",
    "Validated: the frozen English screening model was evaluated exactly once, on an external corpus, at a threshold fixed in advance. " + HEADLINE + " " + CANON.replace("development pool.", "development pool (section 3.9).") + " That evaluation cannot be repeated:")

# ───────── 2.2 + 3.4 + 3.8 + 3.10: Chapter 5 opening ─────────
rep("chapter5.md",
    "At the pre-specified threshold, the one-shot external evaluation returned 96.2% sensitivity and 33.3% specificity, and sections 5.15 to 5.21 establish that the specificity was not a failure of the model but a failure of what the threshold was referenced to.",
    HEADLINE + " Sections 5.15 to 5.21 establish that the specificity was not a failure of the model but a failure of what the threshold was referenced to.")
rep("chapter5.md",
    "The status of that diagnosis is stated in the same breath, so the headline cannot erode it: control-referenced thresholding is a post hoc analysis on a frozen model — not pre-registered, not deployed, and not what produced the primary result. The pre-specified operating point remains 0.367,",
    "The pre-specified operating point remains 0.367,")
rep("chapter5.md",
    "First, the external evaluation demonstrates non-degradation on a corpus collected by different investigators, at a threshold fixed in advance and a single scoring — the property most published systems in this field never test (section 5.3).",
    "First, no degradation was observed in the external point estimate, on a corpus collected by different investigators, at a threshold fixed in advance and a single scoring — a property most published systems in this field never test, though the evaluation was not designed as a formal non-inferiority study (section 5.3).")
rep("chapter5.md",
    "Third, the mild-impairment target resists this method as deployed — Delaware cannot be learned from its own recordings (section 5.12.1) — and the recoverable signal lives in connected discourse rather than picture description (section 5.25), the pair of findings that reshaped the successor battery.",
    "Third, the deployed picture-description architecture performs weakly for mild impairment — Delaware cannot be learned from its own recordings (section 5.12.1) — and within the available multi-task corpus, connected discourse is the more promising elicitation genre (section 5.25), the pair of findings that reshaped the successor battery.")
rep("chapter5.md",
    "appears not to be reported anywhere in this literature, and naming, measuring and bounding it is a contribution (section 5.26.1).",
    "appears, within the literature identified by this search, not to be reported, and naming, measuring and bounding it is a contribution (section 5.26.1).")

# ───────── 3.4 + 3.2: §5.3 ─────────
rep("chapter5.md",
    "What the evaluation establishes is that performance did not degrade on a corpus collected by different investigators, under a threshold fixed in advance and a single scoring — which is what a held-out external test exists to determine, and non-degradation is the finding being claimed.",
    "What the evaluation establishes is narrower: no degradation was observed in the external point estimate, on a corpus collected by different investigators, under a threshold fixed in advance and a single scoring. The evaluation was not designed as a formal non-inferiority study, and none is claimed.")
rep("chapter5.md", "0.8533 is the deployed system's number and it is not free of the earlier exposure:",
    "0.8533 is the frozen English screening model's number, and it is not free of the earlier exposure:")

# ───────── 3.2: Chapter 6 and Appendix F prose ─────────
rep("chapter6.md",
    "The deployed instrument reaches AUC 0.8533 [0.7371, 0.9458] on data absent from its training, at a threshold fixed in advance, scored once, under the exposure history of section 3.9.",
    "The frozen English screening model reached external AUC 0.8533 [0.7371, 0.9458] on data absent from its training, at a threshold fixed in advance, scored once, under the exposure history of section 3.9.")
rep("chapter6.md", "so 0.8533 validates the deployed system on data absent from its training but is not free of that one prior exposure (section 3.9).",
    "so 0.8533 validates the frozen English screening model on data absent from its training but is not free of that one prior exposure (section 3.9).")
rep("chapter6.md", "The external test set's exposure is stated in the canonical form: The corpus was excluded",
    "The external test set's exposure is stated in the canonical form: the corpus was excluded")
rep("appendix_f.md", "0.8533 [0.7371, 0.9458] validates the deployed system on data absent from its training,",
    "0.8533 [0.7371, 0.9458] validates the frozen English screening model on data absent from its training,")

# ───────── 3.3: screening score / development-calibrated probability estimate ─────────
rep("chapter1.md", "it must degrade gracefully from a calibrated probability to an indicator profile to a paper checklist.",
    "it must degrade gracefully from a screening score — a development-calibrated probability estimate — to an indicator profile to a paper checklist.")
rep("chapter3.md",
    "The model output is a probability conditioned on the class balance of the training pool, 465 impaired recordings in 987, or 0.4711, and almost nobody is screened at a prevalence of 47%. The risk-adjustment stage therefore divides out the training prior, applies an age-specific population prevalence, a multiplier for why the person is being tested and one for family history, and returns a posterior.",
    "The model output is a screening score: a development-calibrated probability estimate conditioned on the class balance of the training pool, 465 impaired recordings in 987, or 0.4711, and almost nobody is screened at a prevalence of 47%. The risk-adjustment stage therefore divides out the training prior, applies an age-specific population prevalence, a multiplier for why the person is being tested and one for family history, and returns a context-adjusted estimated risk — not a probability clinically calibrated for Libya.")
rep("chapter4.md", "must therefore degrade gracefully, from a calibrated screening probability, through an indicator profile",
    "must therefore degrade gracefully, from a screening score, through an indicator profile")
rep("chapter4.md",
    "the frozen screening model turns that vector into a calibrated probability; the risk-adjustment stage of section 3.7 turns the probability into an age- and context-conditioned posterior;",
    "the frozen screening model turns that vector into a screening score, a development-calibrated probability estimate; the risk-adjustment stage of section 3.7 turns that score into a context-adjusted estimated risk, conditioned on age and referral context and not clinically calibrated for Libya;")
rep("chapter4.md", "and never claims a probability it cannot justify.", "and never claims a screening score it cannot justify.")
rep("chapter4.md", "The screening result is a band with the probability behind it,", "The screening result is a band with the screening score behind it,")
rep("chapter4.md", "converts the score into an age- and context-conditioned posterior, the referral multiplier",
    "converts the score into a context-adjusted estimated risk, not clinically calibrated for Libya, the referral multiplier")
rep("chapter4.md", "an Arabic session, for which no validated probability exists", "an Arabic session, for which no validated screening score exists")
rep("chapter4.md", "for which the trained probability is withheld while the indicator profile stands",
    "for which the trained model's screening score is withheld while the indicator profile stands")
rep("chapter4.md", "because a probability computed from ten seconds of mumbling", "because a score computed from ten seconds of mumbling")
rep("chapter6.md", "for an Arabic session — no validated Arabic probability exists —", "for an Arabic session — no validated Arabic screening score exists —")
rep("chapter6.md", "a screening probability where computer, model and recogniser are present;", "a screening score where computer, model and recogniser are present;")

# ───────── 3.5: §3.12 likelihood ratio as an empirical evidence estimator ─────────
rep("chapter3.md",
    "is an invariant evidence term multiplied by a local prior.",
    "is an invariant evidence term multiplied by a local prior. In deployment the likelihood ratio functions as an empirical evidence estimator rather than an exact density ratio: it inherits whatever miscalibration *p*(*x*) carries, and with the development calibration slope above one (section 5.4.1) it conservatively underweights extreme values, understating strong evidence rather than overstating it.")

# ───────── 3.6: PPV/NPV prevalence-dependence ─────────
rep("chapter5.md",
    "The instrument rules out far better than it rules in, which is what a screening test is for, and it is why a positive result is an invitation to assessment and never a finding.",
    "Both values are prevalence-dependent rather than properties of the instrument alone: at 10% prevalence the negative predictive value is high because most people screened are unimpaired, and the positive predictive value is low for the same reason, which is why a positive result is an invitation to assessment and never a finding.")

# ───────── 3.7: the "safer failure" ─────────
rep("chapter5.md",
    "And the deployed pooled choice turns out to be the safer failure: it over-refers men (specificity 0.438 against 0.545) rather than under-detecting them, which for a screening instrument is the correct direction — the cost is wasted assessments, not missed cases.",
    "The deployed pooled choice over-refers men (specificity 0.438 against 0.545) rather than under-detecting them. The observed error direction favours sensitivity over missed cases, but excess false positives remain an equity, anxiety and resource-use concern.")

# ───────── 3.8: priority claims and the RDI explanation ─────────
rep("chapter5.md", "Until this probe, that index had never been computed on the speech of a diagnosed patient in any language.",
    "Within the literature identified by this search, that index had not previously been computed on the speech of a diagnosed patient in any language.")
rep("chapter5.md", "That number appears not to be reported anywhere in the speech-based screening literature, and the strongest available counter-case",
    "Within the speech-based screening literature identified by this search, that number appears not to be reported, and the strongest available counter-case")
rep("chapter5.md", "the first direct test of the stage dissociation this search located, resting on one corpus, one target, n = 288.",
    "the first direct test of the stage dissociation among the literature identified by this search, resting on one corpus, one target, n = 288.")
rep("chapter6.md", "— the first time the construct had been computed on the speech of diagnosed patients in any language (section 5.10.1).",
    "— within the literature identified by this search, the first computation of the construct on the speech of diagnosed patients in any language (section 5.10.1).")
rep("chapter6.md", "On this evidence, referential deficit is a dementia-stage phenomenon, and no implementation in any language makes it an early marker.",
    "On this English evidence, target and stage are the dominant explanation: the index separates at the dementia stage and not at the mild-impairment stage, and nothing measured here supports it as an early marker in any language.")

# ───────── 3.9: Appendix B battery ─────────
rep("appendix_b.md", "Can elderly Libyan participants **complete** the four-task battery?",
    "Can elderly Libyan participants **complete** the battery of four core assessment tasks plus one optional exploratory Qur'anic recitation probe?")
rep("appendix_b.md", "| 5 | **Quran recitation** — a surah the participant selects from those they know | 60 s | over-learned speech | cultural probe |",
    "| 5 | **Qur'anic recitation, optional exploratory probe** — a surah the participant selects from those they know | 60 s | over-learned speech | cultural probe |")

# ───────── 3.10: the MCI sentence, Chapter 6 ─────────
rep("chapter6.md",
    "Mild cognitive impairment is where the instrument is genuinely weak, and no threshold rule can change that: at the deployed model's discrimination on that cohort the specificity ceiling at 75% sensitivity is 0.376 (section 5.15), the cohort cannot be learned from its own recordings at all (section 5.12.1), and the recoverable signal lives in a task genre the deployed model was never fitted on (section 5.25).",
    "The deployed picture-description architecture performs weakly for mild impairment, and no threshold rule can change that: at the deployed model's discrimination on that cohort the specificity ceiling at 75% sensitivity is 0.376 (section 5.15), and the cohort cannot be learned from its own recordings at all (section 5.12.1). Within the available multi-task corpus, connected discourse is the more promising elicitation genre — a genre the deployed model was never fitted on (section 5.25).")

write("revise3: ")
