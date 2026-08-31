"""
risk_adjustment.py
------------------
Turns a speech-pattern score into an age-appropriate risk estimate, and builds
a cognitive profile across the whole task battery.

──────────────────────────────────────────────────────────────────────────────
PART 1 - WHY AGE MUST BE APPLIED AFTER THE MODEL, NOT INSIDE IT
──────────────────────────────────────────────────────────────────────────────
Age was deliberately excluded from the classifier's inputs, because the
training groups were matched on age precisely so the model could not "cheat" by
learning that older speakers are patients. That was correct for TRAINING.

But it leaves a real deployment flaw: the model answers "does this speech
resemble impaired speech?" and nothing else. A healthy 23-year-old whose speech
is slightly atypical -- through fatigue, a second language, or ordinary
variation -- receives the same score as a 78-year-old with identical speech,
even though Alzheimer's dementia is roughly three hundred times rarer at 23.

The fix is standard Bayesian base-rate correction. The model's output carries
the development set's own class prevalence (TRAINING_PRIOR below, 0.471125 =
465/987 — an early version wrongly assumed 0.50). Dividing that out to a
likelihood ratio and re-applying the true age-specific prevalence produces
the probability that actually answers the clinical question.

PREVALENCE FIGURES (Alzheimer's Association, 2024 Facts and Figures)
    age 65-74 : 5.0%
    age 75-84 : 13.2%
    age 85+   : 33.4%
    age 30-64 : about 110 per 100,000 (0.11%) for younger-onset dementia

──────────────────────────────────────────────────────────────────────────────
PART 2 - WHY EDUCATION CHANGES INTERPRETATION, NOT THE SCORE
──────────────────────────────────────────────────────────────────────────────
Education strongly affects vocabulary richness and verbal fluency in people
with no cognitive impairment whatsoever. A speaker with four years of schooling
may produce a narrower vocabulary than a graduate simply because of schooling.

No education-stratified norms were available for this corpus, so no numeric
correction can be justified. Inventing one would be exactly the kind of
false precision this project has avoided throughout. Instead, education
triggers an explicit interpretive warning when the flagged indicators are the
education-sensitive ones, so the clinician knows which explanation to weigh.

──────────────────────────────────────────────────────────────────────────────
PART 3 - THE SECONDARY TASKS, AND WHAT THE CORPUS LICENSES
──────────────────────────────────────────────────────────────────────────────
Fluency, recall and sentence construction exist in the Pitt corpus for the
dementia group only, so they cannot yield a healthy-vs-impaired threshold.
They CAN, however, be checked against MMSE within the impaired group, and in
this corpus they track severity clearly:

    verbal fluency (animals)   r = 0.397 with MMSE  (n = 207, p < 0.0001)
    story recall (idea units)  r = 0.462 with MMSE  (n = 237, p < 0.0001)
    sentence construction      r = -0.355 with MMSE (n = 201, p < 0.0001)

Fluency and recall correlate only weakly with each other (r = 0.225), meaning
they measure genuinely different abilities rather than repeating one another.

That evidence licenses reporting them as SEVERITY indicators -- how impaired,
given impairment -- while keeping them out of the screening decision, which
remains based on the only task with healthy controls.
"""
from __future__ import annotations

# ── age-specific prevalence ─────────────────────────────────────────────────
# CRITICAL: the prior must match WHAT THE MODEL DETECTS, not a narrower
# condition. The training set's "impaired" class was not Alzheimer's dementia
# alone -- it contained 234 ProbableAD, 42 MCI, 21 PossibleAD, 5 vascular and
# 3 memory-clinic cases. The model therefore detects COGNITIVE IMPAIRMENT
# BROADLY, and the correct prior is the prevalence of MCI plus dementia.
#
# Using dementia-only prevalence (as an earlier version did) systematically
# understated risk, because MCI is roughly twice as common as dementia in the
# ages that matter most for EARLY detection -- which is precisely the
# population this instrument exists to serve.
#
# SOURCES
#   MCI prevalence (Petersen et al. 2018, AAN practice guideline update,
#   Neurology): 6.7% at 60-64, 8.4% at 65-69, 10.1% at 70-74, 14.8% at
#   75-79, 25.2% at 80-84.
#   Alzheimer's dementia prevalence (Alzheimer's Association, 2024 Facts and
#   Figures): 5.0% at 65-74, 13.2% at 75-84, 33.4% at 85+.
#   Younger-onset dementia: global prevalence 119 per 100,000 aged 30-64
#   (Hendriks et al. 2021, JAMA Neurology; the band below uses the order of
#   magnitude, not the exact figure).
#   Community MCI (Bai et al. 2022, Age and Ageing 51:afac173, worldwide
#   meta-analysis of community dwellers 50+): 10.9% at 50-59. The (50,60)
#   band below deliberately uses 6.0% — a conservative down-weighting of a
#   single heterogeneous meta-analysis figure; recorded as a JUDGMENT, see
#   docs/DESIGN_RATIONALE.md.
#
# (lower_age, upper_age, combined MCI + dementia prevalence)
PREVALENCE = [
    (0, 40, 0.005),       # cognitive impairment of any cause is rare and
                          # rarely degenerative at this age
    (40, 50, 0.015),
    (50, 60, 0.060),      # community MCI studies from age 50 upward
    (60, 65, 0.077),      # MCI 6.7% + early-onset dementia
    (65, 70, 0.110),      # MCI 8.4% + dementia ~3%
    (70, 75, 0.150),      # MCI 10.1% + dementia ~5%
    (75, 80, 0.250),      # MCI 14.8% + dementia ~10%
    (80, 85, 0.420),      # MCI 25.2% + dementia ~17%
    (85, 200, 0.550),     # MCI ~35% + dementia 33.4%, overlapping
]

# -- referral context -------------------------------------------------------
# Population prevalence assumes a randomly selected person. Almost nobody is
# screened at random: they are tested because a family member noticed
# something, or because a clinician referred them. Those groups have a higher
# pre-test probability, and ignoring that understates risk for exactly the
# people most likely to be tested.
#
# === CHANGE OF 2026-08-23: THE x4.0 CLINICIAN-REFERRAL MULTIPLIER IS REMOVED ==
# An earlier version applied x4.0 to clinician-referred sessions. It is gone,
# and the reason is NOT that the evidence went against it. The evidence, such
# as it is, points the other way:
#
#   Clinic case-mix studies report MCI-or-dementia at 77.5% (Ronner et al.,
#   BJGP Open 2025, n=651, Netherlands), 79.3% (Blane et al., Sci Rep 15:7765,
#   2025, Oxford Brain Health Clinic, n=313) and 84% (NHS England, 2019
#   National Memory Service Audit, 85 services, n~3,700, aged 65+), against
#   population prevalence of 32% (Manly et al., JAMA Neurol 79(12):1242, 2022,
#   HRS-HCAP, n=3,496) and 35% (Borsch-Supan et al., Sci Rep 15:14024, 2025,
#   SHARE-HCAP, n=47,773). That implies an odds ratio of 6.4-11.2 unadjusted,
#   or roughly 4-8 once the clinic cohorts' higher mean age (~78) is allowed
#   for. If anything, x4.0 was too LOW.
#
# It is removed because REFERRAL IS NOT A DIAGNOSTIC TEST AND HAS NO STABLE
# OPERATING CHARACTERISTICS. The same NHS audit that yields the 84% figure
# found dementia yield ranging from 22% to 100% across 85 services, in one
# country, in one year. A referral rate is a local policy variable -- who a
# service accepts, how long its waiting list is, what a GP believes it is for
# -- not a property of the person in the room. Any single multiplier treats
# that policy variable as a biological constant, and no value chosen from
# British or Dutch memory clinics would transport to a Libyan setting, where
# referral pathways for cognitive complaints are largely absent. The
# comparison above is also between studies, countries, health systems and
# DIAGNOSTIC CONSTRUCTS: a memory-clinic MCI diagnosis is a multidisciplinary
# judgement with imaging; a community MCI diagnosis is a cut-off on a battery.
#
# WHAT REPLACES IT. A clinician-referred session receives the SAME x2.5 as a
# reported concern, and the referral itself is reported qualitatively, with no
# arithmetic attached. This is deliberate, and it is a FLOOR, not an estimate:
#   * nearly everyone referred for cognitive assessment also has a subjective
#     or informant-reported complaint, which is the quantity x2.5 measures;
#   * the case-mix evidence above says the true uplift is larger, so the
#     reported probability UNDERSTATES risk in this branch -- and the output
#     says so in words rather than leaving the reader to assume otherwise;
#   * setting it BELOW the concern multiplier would be incoherent (a clinician
#     referral is not weaker evidence than a family noticing something), and
#     setting it above would reinstate an unsourced number under a new name.
# The referring clinician's own judgement is evidence this figure does not
# contain, and the operator-facing note says exactly that.
#
# === x2.5 (concern): support found AFTER THE FACT, not derived ===============
# 2.5 was asserted as an engineering assumption before any source was sought.
# A literature search on 2026-08-22 then found it sits within rounding of a
# published cross-sectional likelihood ratio:
#   A. J. Mitchell, "The clinical significance of subjective memory complaints
#   in the diagnosis of mild cognitive impairment and dementia: a
#   meta-analysis", Int J Geriatr Psychiatry 23(11):1191-1202, 2008,
#   doi:10.1002/gps.2053, PMID 18500688.
# Cross-sectional, which is the right object for a PREVALENCE prior. Subjective
# memory complaint is present in 39.8% of those with any cognitive impairment
# against 17.4% of healthy elderly (the paper's own relative risk 2.3).
# Positive likelihood ratios derived from its published sensitivity and
# specificity: LR+ 2.29 for MCI-or-dementia, 2.85 for MCI alone (sens 37.4%,
# spec 86.9%), 3.03 for dementia alone (sens 43.0%, spec 85.8%). Two
# longitudinal meta-analyses corroborate the magnitude without being the
# derivation: Mitchell et al. 2014 (RR 2.07, n=29,723) and Pike et al. 2022
# (OR 2.48, HR 1.90, n>74,000).
# State it in the thesis in these words: 2.5 was asserted without derivation
# and happens to agree with a published figure found afterwards. The caveats
# run both ways -- Mitchell's specificity is computed largely against healthy
# controls, which inflates LR+, while someone who presents BECAUSE they
# noticed a change is more strongly selected than a survey respondent, so 2.3
# is plausibly a floor.
#
# === WITHDRAWN CITATION =====================================================
# Earlier versions cited a "clinic-vs-community MCI systematic review, 2018"
# for "MCI/dementia rates several times the community rate". The paper is
# Hu C, Yu D, Sun X, Zhang M, Wang L, Qin H, Int Psychogeriatr
# 29(10):1595-1608, 2017 (not 2018), doi:10.1017/S1041610217000473, PMID
# 28884657, and its abstract says the opposite for prevalence: "Compared with
# clinic-based outcomes, MCI prevalence, SR, and RR are significantly higher
# in community, while DR and AR are lower." What is higher in clinic samples
# is PROGRESSION. It publishes no ratio. The citation is withdrawn.
# One nuance, so the retraction is not itself overread: Hu measured MCI
# SPECIFICALLY, and clinic denominators are dominated by dementia (52-67%),
# which is not MCI -- so its result is a composition artefact with respect to
# the composite endpoint. It refutes the citation; it does not refute a
# referral effect.
#
# The three contexts are MUTUALLY EXCLUSIVE branches -- one per session. That
# is correct: nearly everyone a clinician refers also has a subjective
# complaint, and applying both would double-count the same information.
REFERRAL_CONTEXT = {
    "population": (1.0, "Routine screening, no specific concern raised."),
    "concern": (2.5, "Tested because the person or their family noticed a "
                     "change. A memory complaint is about 2.3 times as common "
                     "in people with cognitive impairment as in healthy older "
                     "adults (Mitchell, Int J Geriatr Psychiatry 2008; derived "
                     "positive likelihood ratio 2.29). The 2.5 used here was "
                     "chosen before that source was found, not derived from "
                     "it."),
    "clinical": (2.5, "Referred by a clinician who already suspected "
                      "impairment. The same uplift as a reported concern is "
                      "applied, because nearly everyone referred also reports "
                      "a change, and that is the only part of this situation "
                      "with a published figure. NO SEPARATE MULTIPLIER IS "
                      "APPLIED FOR THE REFERRAL ITSELF: dementia yield ranged "
                      "from 22% to 100% across 85 NHS memory services in a "
                      "single year, so referral has no stable operating "
                      "characteristics and is not a diagnostic test. Clinic "
                      "case-mix studies imply the true uplift is roughly four "
                      "to eight times, so THIS FIGURE IS A FLOOR AND "
                      "UNDERSTATES RISK. The referring clinician's own "
                      "judgement is evidence this number does not contain, "
                      "and should outweigh it."),
}

# ── family history ──────────────────────────────────────────────────────────
# Family history is one of the three established major risk factors, alongside
# age and genetics.
#
# SOURCE: Cannon-Albright et al., Neurology (2019), a population study of the
# Utah genealogical database, summarised by the US National Institute on Aging:
#   one first-degree relative (parent or sibling)   RR 1.73
#   two first-degree relatives                      RR ~3.98
#   three or more second-degree relatives only      RR ~2.0
#   third-degree relatives only (three or more)     RR ~1.43
#
# >>> A DELIBERATE ASYMMETRY, AND WHY IT MATTERS HERE <<<
# A "yes" is informative; a "no" largely is not. Where dementia frequently
# goes undiagnosed — as in most low-resource settings, Libya among them — a
# grandmother who declined for years may simply have been called old rather
# than ill. Answering "no" therefore often means "nobody was ever diagnosed",
# not "nobody was affected". (An earlier comment cited a specific "75-90%
# undiagnosed in Libya" figure; it could not be sourced and was retracted —
# results/summary/review_corrections.json.)
#
# Treating "no" as protective would penalise precisely the families with the
# least access to diagnosis. So a positive history raises the prior, while a
# negative or unknown history leaves it unchanged rather than lowering it.
# === REVIEW OF 2026-08-23: ONE ARGUMENT WITHDRAWN, ONE DEFECT ESTABLISHED ====
#
# WITHDRAWN. It was argued during review that family history has the same defect
# as the retired x4.0 referral multiplier -- that under-diagnosis makes a "yes"
# answer mean different things in different settings, so no stable multiplier
# exists. That argument does not survive being written down, and it is
# withdrawn.
#
#   Let D = the person truly has an affected first-degree relative, Y = they
#   answer yes. A yes requires the relative to have been diagnosed AND
#   remembered, so P(Y|D) = a for some ascertainment rate a < 1, and false
#   positives are rare, P(Y|not D) ~ 0. Then for the person's own future risk R:
#       P(Y | R)     = a * P(D | R)
#       P(Y | not R) = a * P(D | not R)
#       LR+          = P(D|R) / P(D|not R)          <-- a CANCELS
#   So provided under-ascertainment is NON-DIFFERENTIAL, the likelihood ratio
#   carried by a "yes" is unchanged by how rarely dementia is diagnosed locally.
#   Low ascertainment makes "yes" RARER; it does not make it mean LESS.
#
# That is a genuinely different situation from referral. A referral RATE
# determines who enters the tested population and varied 22%-100% across 85
# services in one year; the multiplier would have been estimating a local policy
# parameter. Family history is a property of the person. The two are not alike
# and should not have been treated as alike.
#
# (The residual differential mechanism is real but second-order: if diagnostic
# access tracks education and urbanicity, and education is protective, then
# "yes" is over-represented among lower-risk people and LR+ is biased DOWNWARD,
# i.e. 1.73 would be too high. Worth one sentence in the thesis, not a change.)
#
# THE DEFECT THAT IS REAL, AND IT IS SHARPER THAN THE ONE WITHDRAWN.
# Cannon-Albright reports RELATIVE RISKS. The chain below multiplies prior
# ODDS. RR ~ OR ~ LR only while baseline risk is small, and these prevalence
# bands do not stay small:
#
#     band prevalence | RR 3.98 on the ODDS scale | RR 3.98 on the RISK scale
#            0.005    |          0.020            |   0.020
#            0.077    |          0.249            |   0.307
#            0.150    |          0.413            |   0.597
#            0.250    |          0.570            |   0.995
#            0.420    |          0.742            |   1.672  <-- IMPOSSIBLE
#            0.550    |          0.830            |   2.189  <-- IMPOSSIBLE
#
# A relative risk of 3.98 cannot be applied to a baseline risk of 0.55, because
# 0.55 x 3.98 exceeds 1. The RR was measured in a population whose baseline risk
# was far lower, and it is not transportable multiplicatively to a high one. The
# odds-scale application hides that by construction -- odds ratios cannot exceed
# 1 -- but hiding an incoherence is not resolving it.
#
# MAX_PRIOR IS THE SYMPTOM, NOT THE FIX. The cap binds in exactly 4 of 135 prior
# combinations, and all four are "two or more affected first-degree relatives"
# at ages 80+ with a referral uplift also applied -- precisely the region where
# the RR-as-odds-multiplier breaks down. The cap is silently absorbing a
# modelling error and making it invisible. Say so in the thesis.
#
# SECOND, SMALLER DEFECT: AGE COMPOSITION. Cannon-Albright's RR is computed
# across ages. Familial loading is stronger for earlier-onset disease, so
# applying an age-AVERAGED RR on top of an age-SPECIFIC prevalence probably
# OVERSTATES familial risk at 85 and UNDERSTATES it at 60.
#
# DECISION: NO CHANGE TO THE ARITHMETIC, and the reason is recorded rather than
# assumed. The correct alternative -- composing on the risk scale,
# p = min(prev * RR, ceiling) -- still requires an arbitrary ceiling (see the
# table above), so it trades one declared assumption for another while
# invalidating the 1,440-case verification and the published worked examples.
# The defect is documented, its direction is stated (overstates at the oldest
# ages), and the cap is disclosed as what absorbs it.
#
# WHAT IS RIGHT AND SHOULD BE KEPT: the asymmetric treatment of "no". A negative
# answer leaves the prior unchanged rather than lowering it, because in a
# low-diagnosis setting "no" frequently means "nobody was ever diagnosed". That
# is correct, and it also makes the whole scale conservative -- declining to
# treat a "no" as protective shifts every negative answer toward caution.
FAMILY_HISTORY = {
    "none": (1.0, "No known family history. In settings where dementia is "
                  "commonly undiagnosed this answer is weakly informative, so "
                  "it has not been treated as protective."),
    "unknown": (1.0, "Family history unknown; no adjustment applied."),
    "one_first_degree": (1.73, "One parent or sibling affected (relative risk "
                               "1.73, Cannon-Albright et al., Neurology 2019)."),
    "two_or_more_first_degree": (3.98, "Two or more parents or siblings "
                                       "affected (relative risk about 4)."),
    "second_degree": (1.5, "Grandparents, aunts or uncles affected. Relative "
                           "risk rises to about 2.0 with three or more such "
                           "relatives; a conservative 1.5 is applied."),
}

# The combined prior is capped. Age, referral context and family history are
# not independent -- a family that has seen dementia before is likelier to seek
# testing, so their effects partly overlap. Multiplying all three unchecked
# would double-count that shared cause and produce a prior no evidence
# supports. The 0.85 value itself has no published derivation; it is a
# declared prudence assumption (docs/DESIGN_RATIONALE.md).
#
# THE CAP IS LIVE, and this was CHECKED rather than assumed. Across the full
# grid of 9 age bands x 3 referral contexts x 5 family-history states (135
# prior combinations) it binds in 4 -- all of them "two or more affected
# first-degree relatives" at age 80+ with a referral uplift applied, where the
# uncapped priors are 0.878 (age 80-85) and 0.924 (85+). With no referral
# multiplier at all it would bind in 0 of 45, so it is the multiplier that
# keeps it live. CORRECTION: an earlier working note in this project stated
# that removing the x4.0 would leave the cap dead. That note was written
# before the grid was recomputed with x2.5 retained on BOTH the concern and
# clinical branches, and it was wrong. Verified 2026-08-23,
# scripts/verify_bayes_chain.py -> results/reconstruction/bayes_chain_check.json.
MAX_PRIOR = 0.85

# Prevalence of the impaired class in the data the model was actually fitted to
# (465 impaired of 987 recordings across Pitt and Delaware, post-Lu-lock). This value
# MUST be the real training prevalence, not an assumed 0.5: the calibrated model
# already encodes it, so dividing by the wrong figure would leave part of the
# development prior inside the likelihood ratio and double-count prior risk.
# 0.471125 = 465 impaired / 987 recordings, the post-Lu-lock development set
# (Pitt cookie 548 + Delaware cookie 439). Derivation:
# scripts/compute_training_prior.py -> results/reconstruction/training_prior.json.
# Updated 2026-08-21 (approved). Previous value 0.4721 (= 491/1040) was measured
# on the PRE-lock pool that still included Lu -- the known inconsistency flagged
# in HANDOFF.md sect 4 and model_card.json known_issues.
TRAINING_PRIOR = 0.471125


# ── banded reporting of the posterior ───────────────────────────────────────
# The Bayesian chain composes an epidemiological prior with a speech likelihood
# ratio and returns a number. That number has NEVER been validated against an
# outcome -- nobody has checked that a person the chain calls 54% is at 54% --
# and with the available data nobody can. Printing it to two decimal places
# therefore claims a precision the evidence does not support, and it is the
# most clinician-visible output the system produces.
#
# So the band is the headline and the number is detail. The exact value stays
# in the machine-readable output for audit and provenance; the operator-facing
# surface shows the band. Boundaries are deliberately coarse and are a declared
# reporting choice, not a measured partition -- there is no calibration
# evidence that would justify finer ones. Added 2026-08-23.
POSTERIOR_BANDS = [
    (0.00, 0.10, "low",
     "Low. On the available evidence, cognitive impairment is unlikely in this "
     "person. A single screening result does not exclude it."),
    (0.10, 0.30, "moderate",
     "Moderate. Enough to warrant attention, not enough to suggest impairment "
     "is more likely than not."),
    (0.30, 0.60, "high",
     "High. Clinical assessment is recommended."),
    (0.60, 1.01, "very high",
     "Very high. Clinical assessment is recommended promptly."),
]


def posterior_band(p: float | None) -> tuple[str, str]:
    """Coarse band for the age-adjusted estimate. See POSTERIOR_BANDS."""
    if p is None:
        return "", ""
    for lo, hi, label, text in POSTERIOR_BANDS:
        if lo <= p < hi:
            return label, text
    return "", ""


def age_prevalence(age: float | None) -> float | None:
    if age is None:
        return None
    for lo, hi, p in PREVALENCE:
        if lo <= age < hi:
            return p
    return None


def adjust_for_age(model_probability: float, age: float | None,
                   context: str = "population",
                   family_history: str = "unknown") -> dict:
    """
    Re-express the model's score as an age-appropriate probability.

    Combines the likelihood ratio implied by the model with the published
    prevalence of cognitive impairment for the person's age, optionally
    scaled by why they are being tested.

    METHOD (standard base-rate correction, stated explicitly because it is the
    step most easily got wrong)
        LR_speech      = odds(model output) / odds(training prevalence)
        odds(patient)  = LR_speech x odds(age-and-context prior)
        P(patient)     = odds / (1 + odds)

    Dividing by the training odds is what removes the development-set prior
    from the model's output. Skipping it would apply the epidemiological prior
    on top of a probability that already contains a prior, counting prior risk
    twice.

    NOTE ON INTERPRETATION: an improvement in AUC after this adjustment does
    NOT mean the speech biomarker became more accurate. It means that speech
    combined with epidemiological risk discriminates better than speech alone,
    which is a different and weaker claim.
    """
    prev = age_prevalence(age)
    if prev is None or model_probability is None:
        return {}
    mult, ctx_text = REFERRAL_CONTEXT.get(context, REFERRAL_CONTEXT["population"])
    fh_mult, fh_text = FAMILY_HISTORY.get(family_history,
                                          FAMILY_HISTORY["unknown"])
    p = min(max(float(model_probability), 1e-6), 1 - 1e-6)

    # model odds, divided out by the balanced training prior, gives the
    # likelihood ratio contributed by the speech itself
    model_odds = p / (1 - p)
    train_odds = TRAINING_PRIOR / (1 - TRAINING_PRIOR)
    lr = model_odds / train_odds

    prior_odds = (prev / (1 - prev)) * mult * fh_mult
    effective_prior = prior_odds / (1 + prior_odds)
    prior_capped = effective_prior > MAX_PRIOR
    if prior_capped:                         # cap overlapping risk factors
        effective_prior = MAX_PRIOR
        prior_odds = MAX_PRIOR / (1 - MAX_PRIOR)
    post_odds = lr * prior_odds
    posterior = post_odds / (1 + post_odds)

    # A clinician referral carries no arithmetic of its own (see the block
    # above). Where the operator selected that context, the output must say
    # in words that the number is a floor -- otherwise removing the x4.0
    # silently turns an overstated figure into an understated one, which is
    # the same error with the sign flipped.
    floor_note = (
        " Because a clinician referred this person, treat the figure as a "
        "LOWER BOUND: no separate adjustment is made for the referral itself, "
        "since referral yield is a property of the service rather than of the "
        "person. The referring clinician's own judgement is evidence this "
        "number does not contain."
        if context == "clinical" else "")
    cap_note = (
        " The starting likelihood was capped at 85% because age, reason for "
        "testing and family history overlap and would otherwise be "
        "double-counted."
        if prior_capped else "")

    return {
        "speech_score": round(float(model_probability), 3),
        "age_prevalence": prev,
        "referral_context": context,
        "referral_multiplier": mult,
        "referral_note": ctx_text,
        "referral_is_floor": context == "clinical",
        "family_history": family_history,
        "family_history_note": fh_text,
        "family_history_multiplier": fh_mult,
        "effective_prior": round(float(effective_prior), 4),
        "prior_capped": bool(prior_capped),
        "likelihood_ratio": round(float(lr), 3),
        "age_adjusted_probability": round(float(posterior), 4),
        # band first; the exact value above stays for audit (see POSTERIOR_BANDS)
        "age_adjusted_band": posterior_band(posterior)[0],
        "age_adjusted_band_text": posterior_band(posterior)[1],
        "explanation": (
            f"The speech pattern alone gives {model_probability*100:.0f}%. "
            f"Cognitive impairment (MCI or dementia) affects about "
            f"{prev*100:.1f}% of people in this age band"
            + ((f", and after accounting for why the person was tested"
                + (" and their family history" if fh_mult != 1.0 else "")
                + f" the starting likelihood is about {effective_prior*100:.1f}%")
               if (mult != 1.0 or fh_mult != 1.0) else "")
            + f". Combining that with the speech evidence gives "
              f"{posterior*100:.1f}%." + cap_note + floor_note),
    }


def age_context_note(age: float | None) -> str | None:
    """A plain-language warning where age makes impairment implausible."""
    if age is None:
        return None
    if age < 45:
        return ("At this age Alzheimer's dementia is extremely rare (well under "
                "1 in 1000). An atypical speech profile here is far more likely "
                "to reflect fatigue, a second language, an unfamiliar task, or "
                "ordinary variation than cognitive impairment.")
    if age < 65:
        return ("Younger-onset dementia affects roughly 1 in 850 adults aged "
                "30 to 64. Impairment is possible but uncommon at this age, and other "
                "explanations should be considered first.")
    return None


# ── education ───────────────────────────────────────────────────────────────
EDUCATION_SENSITIVE = {
    "ling.type_token_ratio", "ling.ar_ttr_root", "ling.honore_r",
    "ling.brunet_w", "ling.mean_sentence_len", "ling.idea_density",
    "ling.content_word_ratio", "iu.per_100_words",
}


def education_note(education_years: float | None, flagged_keys: list[str]) -> str | None:
    """
    Warn when low schooling could explain the specific indicators that flagged.

    Deliberately no numeric adjustment: no education-stratified norms were
    available for this corpus, and inventing a correction would be false
    precision.
    """
    if education_years is None or education_years >= 9:
        return None
    hits = [k for k in flagged_keys if k in EDUCATION_SENSITIVE]
    if not hits:
        return None
    return (f"This participant reported {education_years:.0f} years of "
            "schooling. Vocabulary and sentence-complexity measures are "
            "strongly influenced by education independently of cognition, and "
            f"{len(hits)} of the flagged indicators are of that type. No "
            "education-adjusted norms were available for this corpus, so no "
            "numeric correction has been applied; the result should be read "
            "with this in mind.")


# ── the multi-task cognitive profile ────────────────────────────────────────
# Severity bands measured directly from the Pitt dementia cohort. These are
# NOT healthy-vs-impaired cut-offs; they describe where a score sits among
# people who already have a diagnosis.
FLUENCY_BY_MMSE = [
    (26, 30, 9.4, "mild"),
    (21, 26, 7.6, "mild-moderate"),
    (16, 21, 6.6, "moderate"),
    (11, 16, 3.3, "moderate-severe"),
    (0, 11, 2.7, "severe"),
]


def fluency_severity_context(n_animals: float | None) -> dict:
    """
    Place an animal-fluency count against this corpus's severity gradient.

    Reported as context, never as a diagnosis: the comparison group consists
    entirely of people who already have dementia, so a low score indicates
    where someone would sit WITHIN that group, not whether they belong to it.
    """
    if n_animals is None:
        return {}
    band = None
    for lo, hi, mean_count, label in FLUENCY_BY_MMSE:
        if n_animals >= mean_count:
            band = (lo, hi, label)
            break
    out = {
        "animals_named": float(n_animals),
        "corpus_note": (
            "In the Pitt dementia cohort, animal counts fell steadily with "
            "severity: 9.4 on average at MMSE 26-30, 6.6 at 16-20, and 2.7 "
            "below 11 (r = 0.40 with MMSE, n = 207). For orientation, a "
            "normative study of 4,387 cognitively unimpaired adults aged "
            "30-91 reports a mean of about 20 animals in 60 seconds, SD "
            "about 5 (Karstens et al., J Int Neuropsychol Soc 30(4):389-401, "
            "2023). Age moderates this more strongly than education, so the "
            "figure is not a cut-off and must not be read as one."),
    }
    if band:
        out["comparable_severity"] = (
            f"This count is comparable to the average for MMSE {band[0]}-{band[1]} "
            f"({band[2]}) in the dementia cohort.")
    else:
        out["comparable_severity"] = (
            "This count is below the average of the most severe band measured "
            "in the dementia cohort.")
    return out


def memory_dissociation(recall_idea_units: float | None,
                        recitation_accuracy: float | None) -> dict:
    """
    Contrast NEW learning against OVERLEARNED memory.

    Story recall requires encoding something heard minutes ago -- episodic
    memory, which Alzheimer's attacks first. Quranic recitation draws on
    material rehearsed since childhood -- overlearned memory, preserved far
    longer. The classic early-Alzheimer's profile is therefore poor recall
    alongside intact recitation.

    Failing BOTH suggests either more advanced disease or a different cause,
    and performing well on both is unremarkable. The pattern carries the
    information, which is why neither score alone is reported as a conclusion.

    NOT VALIDATED: no Arabic patient data exists to establish where the
    boundary lies. The pattern is described; no probability is attached.
    """
    if recall_idea_units is None or recitation_accuracy is None:
        return {}
    poor_recall = recall_idea_units <= 3       # corpus median for dementia was 2
    good_recite = recitation_accuracy >= 0.85

    if poor_recall and good_recite:
        pattern = "dissociated"
        meaning = ("Weak recall of newly heard material alongside intact "
                   "recitation of long-memorised text. This is the pattern "
                   "expected in early Alzheimer's, where recent memory fails "
                   "while overlearned memory is preserved.")
    elif poor_recall and not good_recite:
        pattern = "both impaired"
        meaning = ("Both new learning and overlearned material were affected. "
                   "This is less specific and may indicate more advanced "
                   "disease, a different condition, or that the passage was "
                   "not in fact well memorised.")
    elif not poor_recall and good_recite:
        pattern = "both preserved"
        meaning = "Both new learning and overlearned memory appear intact."
    else:
        pattern = "unexpected"
        meaning = ("Good recall of new material but weak recitation. This is "
                   "not a typical dementia pattern; check that the participant "
                   "genuinely knew the passage selected.")

    return {
        "pattern": pattern,
        "recall_idea_units": float(recall_idea_units),
        "recitation_accuracy": round(float(recitation_accuracy), 3),
        "meaning": meaning,
        "caveat": ("Interpretive framework only. No Arabic clinical data "
                   "exists to validate these boundaries."),
    }


def discordance_note(model_probability: float | None, age: float | None) -> str | None:
    """
    Flag the case where the SPEECH is clearly atypical but the person's age
    makes Alzheimer's an implausible explanation.

    This matters because the base-rate correction can otherwise be misread as
    "nothing is wrong". A 25-year-old whose speech scores 90% has genuinely
    unusual speech; what the age adjustment establishes is that Alzheimer's is
    not the likely cause, NOT that the finding should be ignored. Saying only
    "4.8%" would hide a real observation behind a correct statistic. (4.8% is
    the current chain's posterior for a 25-year-old scoring 0.90, population
    screening, unknown family history — verified 2026-08-21; an earlier
    docstring said "0.18%", a relic of a superseded dementia-only prevalence
    table.)
    """
    if model_probability is None or age is None:
        return None
    if model_probability >= 0.60 and age < 60:
        return ("The speech profile itself is clearly atypical, but at this "
                "age Alzheimer's dementia is an improbable explanation. This "
                "combination should not be read as 'nothing is wrong'. Other "
                "causes of atypical speech deserve consideration: speaking a "
                "second language, fatigue or stress, hearing difficulty, "
                "depression, medication effects, or a non-degenerative "
                "neurological condition. A clinician should interpret this, "
                "not the screening result alone.")
    if model_probability < 0.30 and age >= 80:
        return ("The speech profile appears typical, but dementia is common at "
                "this age (about 1 in 3 above 85). A single normal screening "
                "result does not exclude early impairment, and any clinical "
                "concern from the family should be followed up regardless.")
    return None
