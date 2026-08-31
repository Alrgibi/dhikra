# Figure captions

Faculty format: caption BELOW the figure, centred, bold, numbered `Figure (n.m):`. Numbering is left to the chapter each figure lands in.

**`fig_score_distributions.png`**

> **Figure (n.1):** Screening-score distributions by class in each cohort, with the deployed operating threshold (0.367) marked. Delaware's impaired mean (0.409) is indistinguishable from Pitt's healthy mean (0.406) and below Lu's healthy mean (0.471); a single absolute cut-point therefore cannot carry the same meaning in all three.

**`fig_roc.png`**

> **Figure (n.2):** Receiver operating characteristic curves for each cohort. Discrimination transports well (Pitt 0.809, Lu 0.853); the mild-impairment cohort is the harder target (Delaware 0.629).

**`fig_calibration.png`**

> **Figure (n.3):** Calibration by score band. Points above the diagonal indicate the model understating risk; the development slope is 1.289 with intercept 0.138. Bands containing fewer than five recordings are omitted.

**`fig_sens_spec_tradeoff.png`**

> **Figure (n.4):** Sensitivity and specificity across all thresholds in each cohort. The dashed vertical line is the deployed 0.367; the horizontal reference is the 0.75 sensitivity floor. At 0.367 the Delaware cohort falls below that floor.

**`fig_decision_curve.png`**

> **Figure (n.5):** Decision-curve analysis (Vickers and Elkin, 2006). Net benefit is computed within each cohort at its own prevalence (0.36-0.56); a community setting would sit far lower and every curve would shift down accordingly.

**`fig_effect_sizes.png`**

> **Figure (n.6):** The twelve largest standardised group differences on the matched Pittsburgh cohort. Information content dominates; d = -0.95 for information units.

**`fig_corpus_effect.png`**

> **Figure (n.7):** Left: two groups of healthy speakers from different studies are separable at AUC 0.930 on the full feature set, falling to 0.783 once CHAT transcription markup is removed - the finding that made naive corpus pooling invalid. Right: the same comparison restricted to the 64 deployed features, none of which are CHAT markup; the median absolute shift is 0.22 and only six features exceed 0.5.

**`fig_architecture.png`**

> **Figure (n.8):** System architecture. The screening decision is computed from the picture description alone, the only task with healthy controls in the training corpora; story recall, verbal fluency and Qur'anic recitation contribute severity estimation and supporting context and never enter the screening decision; procedural discourse is recorded as connected-discourse material for the successor corpus and is not analysed.

**REDRAWN 27 August 2026** — the previous PNG predated the 25 August battery revision and omitted the procedural-discourse task. Generator now committed: `scripts/make_fig_architecture.py`. The caption above governs.

**`fig_feature_flow.png`**

> **Figure (n.9):** Feature flow. Of the 117 measures extracted per session, the deployed screening model uses the 64 language features; the acoustic set supports a separate language-independent model and does not enter the screening score.



---

## Specificity chapter (added 2026-08-23)

**`fig_control_referenced.png`**

> **Figure (n.10):** Control-referenced thresholding. The threshold is set at a fixed percentile of the LOCAL healthy-control score distribution. Left: specificity tracks the target in all three cohorts (79.8 / 79.9 / 77.8 per cent at an 80 per cent target); the error bar on Lu is the participant bootstrap, 0.774 [0.69, 0.80], which is an in-sample interval and cannot exceed the target by construction. Right: sensitivity is what varies (0.695 / 0.356 / 0.769), ordered as the cohorts' AUCs predict. Delaware's low sensitivity is its discrimination limit reappearing, not a failure of the rule.

**`fig_recovery_ceiling.png`**

> **Figure (n.11):** Threshold efficiency and the ceilings that bound it. Left: recovery fraction -- specificity achieved divided by the maximum any threshold could achieve at the sensitivity actually reached -- for all 80 rule by target by direction cells. The median is 0.984 and 58 of 80 sit above 0.93; every cell below that line lies in the overshoot region to the right of the dashed line, where the rule has run to the far edge of the ROC curve and the ratio is taken between two near-zero quantities. The rules were not inefficient; they landed in the wrong place. Right: the ceilings themselves. Delaware's 0.376 at 75 per cent sensitivity is why no threshold rule can repair that cohort.

**`fig_lu_false_positives.png`**

> **Figure (n.12):** Why specificity was 33 per cent. The 18 healthy Lu speakers the fixed threshold misclassified, compared with the 9 it classified correctly, on every deployed feature with a standardised mean difference of at least 0.8. The misclassified controls produced 11.5 information units against 14.9, named 4.7 objects against 6.8, and used pronouns in place of nouns at 0.893 against 0.537; 44 per cent mentioned the falling stool against 100 per cent. These are impoverished descriptions, so the model detected what was present rather than malfunctioning, and no threshold rule could have separated them. The age difference (82.6 against 74.2 years) is shown because it is a confound the sample cannot resolve.

**`fig_ppv_prevalence.png`**

> **Figure (n.13):** Predictive values against prevalence, at the deployed threshold of 0.367. Sensitivity and specificity are properties of the test; predictive values are not, and shift with the population tested. At a community prevalence near 10 per cent the positive predictive value falls to 0.14-0.17 while the negative predictive value stays between 0.93 and 0.99. The instrument rules out far better than it rules in, which is what a screening test is for. No predictive value should be quoted without the prevalence it assumes.

**`fig_threshold_precision.png`**

> **Figure (n.14):** How many healthy controls a control-referenced threshold needs. If the threshold is the k-th order statistic of n healthy controls with k the ceiling of 0.80n, the specificity it achieves on a fresh population follows a Beta(k, n+1-k) law. The result is exact and distribution-free, so it holds for a Libyan cohort whose score distribution is unknown. The shaded band is the 95 per cent interval. At the pilot's 20-participant target it spans 0.56 to 0.91; 59 controls are needed for a 10-point interval and 108 for a 7.5-point one. This is the sample-size justification for the pilot's healthy stratum.


---

## Remaining planned figures (added 2026-08-23)

**`fig_ablation.png`**

> **Figure (n.15):** Feature-set ablation on the 987-recording locked development pool, participant-grouped five-fold cross-validation with participant-level bootstrap intervals. No single family carries the result: information content alone reaches 0.711 and the linguistic set alone 0.739, against 0.755 for the deployed ensemble on all 64. Age alone is at 0.557 and its interval touches chance, which is the ablation-side evidence that the matched design removed the age confound. Adding age to the full set would reach 0.767; it is excluded deliberately, because age is applied afterwards as an epidemiological prior rather than learned as a shortcut. The 19-feature Arabic-compatible subset reaches 0.739, within the interval of the full set.

**`fig_robustness.png`**

> **Figure (n.16):** Acoustic feature stability under eight recording degradations, measured on real recordings and expressed as correlation with the same features extracted from the clean audio. Compression to 32 kbps, telephone bandwidth, low volume and clipping are almost free; a phone at table distance is tolerable. Background noise is the one condition that matters, and it attacks pause measurement first: at 20 dB signal-to-noise the pause rate falls to 0.59 while pitch and voice-quality measures are unaffected. At 10 dB extraction fails outright, which is the empirical basis for the quality gate's refusal threshold. A cheap phone is adequate; an open window onto a street is not.

**`fig_validation_story.png`**

> **Figure (n.17):** The validation story. The left-hand column is the sequence of decisions that produced the reported result; the right-hand column is every approach that was tested and rejected, attached to the stage at which it was tested. The lock of 18 August 2026 is marked because it divides the project in two: everything above it could be revised, and nothing below it was. Each rejection is reported in full in Chapter 5, section 5.8.

**SUPERSEDED NOTE — `fig_stimuli`.** An earlier version of this file recorded Figure 19 as *not produced*, reasoning that the Cookie Theft scene belongs to the Boston Diagnostic Aphasia Examination and is not redistributable. The premise is true and the conclusion did not follow: the Cookie Theft is not this project's stimulus. Figure 19 shows the three scenes drawn for this project, and is produced by `scripts/make_fig_stimuli.py`. The BDAE image is not reproduced anywhere in this thesis and must not be — where the training corpora's stimulus needs describing, describe it in words and cite the BDAE. The caption that governs is the one below.


---

## Arabic construct probe (added 2026-08-23)

**`fig_rdi_probe.png`**

> **Figure (n.18):** The referential deficit index, probed in English. The Arabic instrument replaces the English pronoun-overuse marker with demonstratives and vague nouns relative to naming, because Arabic is pro-drop; the index had never been computed on the speech of a diagnosed patient in any language. The pronoun-free variant, which is structurally what the Arabic index is, discriminates on the Pittsburgh dementia cohort and improves under age and sex matching, so the separation is not an age artefact. It fails on the Delaware mild-impairment cohort, but so does the established pronoun marker it replaces, so that is a property of the cohort rather than of the new measure. Adding demonstratives and vague nouns to the established marker neither helps nor harms it in any of the three analysis sets. Criteria were fixed in writing before the analysis was run.

**`fig_stimuli.png`**

> **Figure (n.19):** The three picture-description stimuli, drawn for this project. Each is
> matched on a content specification — three human figures, one animal, roughly fifteen nameable
> objects, eight describable actions, and one hazard nobody in the scene has noticed — so that
> information-unit scoring is comparable across them. The kitchen scene is the only one against
> which the screening model is calibrated; the courtyard and market scenes exist so that a repeat
> assessment need not reuse a picture the participant has already described, and the system
> refuses to produce a score for either. The settings, dress and objects are Libyan rather than
> mid-century American, which the Boston Diagnostic Aphasia Examination's Cookie Theft scene is:
> a participant who has never seen a cookie jar on a high shelf has a harder task for reasons
> that have nothing to do with cognition. The kitchen panel shown here is the artwork as
> corrected on 26 August 2026: an audit of the frozen 23-unit scoring key against the rendered
> scene found that two scored units, the curtain and the dish cloth, were not drawn at all and
> so could not be earned by any speaker, and that the tap, the running water and the overflow
> were hidden behind the standing figure. All three faults were in the picture, not in the
> scorer, and no participant data existed to be invalidated. What the substitution still costs,
> and cannot stop costing, is measured in §4.3.1. Source: `app/static/*.svg`, vector originals
> suitable for direct inclusion; composed by `scripts/make_fig_stimuli.py`.

**Figure (5.20):** Task genre and the mild-cognitive-impairment signal, Delaware, 288 participants at their earliest common visit, 43 features shared by all five task extractors. **(a)** The five tasks separate perfectly by genre: the two connected-discourse tasks occupy the top two places and the three picture-description tasks the bottom three, with no overlap. Individual task intervals are wide and overlapping (n = 288); the claim rests on the ordering together with the paired battery contrast shown, which excludes zero. **(b)** Single-feature AUCs on picture description (open squares, mean of three tasks) against connected discourse (filled circles, mean of two). Volume, lexical-richness, coherence, syntactic and disfluency measures all gain; every measure in the referential family — the construct behind the Arabic referential deficit index — stays at chance in both genres.
