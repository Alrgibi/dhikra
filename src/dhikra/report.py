"""
report.py
---------
Turns extracted features into an interpretable screening report.

>>> CRITICAL SCIENTIFIC BOUNDARY <<<
Until a model is trained on the real labelled corpus, this module does NOT
predict a diagnosis and does NOT output a probability. It reports each measured
indicator against a REFERENCE RANGE and counts how many fall outside it.

That distinction matters. A trained classifier's probability is meaningful only
because it was fitted to real patients with known outcomes. Producing a
confident-looking percentage from hand-picked thresholds would be dressing up a
guess as a result -- exactly what an examiner should tear apart.

So the report has two modes:
  MODE 1 (now)      : 'indicator profile' -- how many markers are atypical, and
                      which ones, with the direction of each. Honest, useful,
                      and defensible.
  MODE 2 (with data): once a model has been fitted on the real corpus, the same
                      report adds a SCREENING SCORE with the model's own
                      explainability. attach_model() switches modes.

A NOTE ON WHAT THE SCORE IS (recorded 2026-08-22)
The model's output is a SCREENING SCORE, not a calibrated clinical
probability. On the locked 987-recording development set the calibration slope
is 1.289, the intercept 0.138 and the Brier score 0.199, with one material
deviation: in the top band the model reports about 0.83 for a group whose
observed rate is 0.98. It therefore understates risk at the top and never
overstates it -- acceptable for screening, but not a number to read as "this
person's probability of impairment". Source:
results/summary/CURRENT_development_stats.json -> calibration.

REFERENCE RANGES
The values below are ORIENTATION RANGES for adult connected speech, used to
flag 'atypical' -- they are not diagnostic cut-offs and are labelled as such
everywhere they appear. They will be replaced by empirical percentiles from the
corpus (and eventually from Libyan norms) as data arrives.
"""
from __future__ import annotations
from datetime import datetime, timezone

# key: (low, high, direction_of_concern, human label, plain-language meaning)
#   direction 'up'   -> values ABOVE high are the concerning side
#   direction 'down' -> values BELOW low are the concerning side
REFERENCE_RANGES = {
    # ---------- English linguistic ----------
    "ling.pronoun_to_noun_ratio": (0.0, 1.20, "up", "Pronoun-to-noun ratio",
        "Saying 'he put it there' instead of naming things - a word-finding sign."),
    "ling.type_token_ratio": (0.45, 1.0, "down", "Vocabulary variety",
        "How varied the words are. Falls when word retrieval is effortful."),
    "ling.mean_sentence_len": (7.0, 40.0, "down", "Sentence length",
        "Sentences get shorter and simpler under cognitive load."),
    "ling.content_word_ratio": (0.38, 1.0, "down", "Content-word ratio",
        "How much of the speech carries actual meaning."),
    "ling.idea_density": (3.5, 10.0, "down", "Idea density",
        "Number of ideas expressed per ten words."),
    "ling.filler_rate": (0.0, 0.06, "up", "Filler rate",
        "'um', 'uh' - hesitation while searching for words."),
    # NOTE: 'repeated_word_ratio' is deliberately NOT listed here. It is
    # defined as 1 - type_token_ratio, so reporting both would flag a single
    # measurement twice and inflate the count of atypical indicators. Verbatim
    # repetition is instead captured by chat.retracing_per100, which counts
    # actual repeated-word events rather than restating vocabulary variety.
    # ---------- Arabic linguistic ----------
    "ling.ar_referential_deficit_index": (0.0, 1.20, "up", "Referential deficit index",
        "Pointing (هذا/هناك) and vagueness (شيء/حاجة) instead of naming - the "
        "Arabic equivalent of the pronoun-to-noun marker."),
    "ling.ar_demonstrative_rate": (0.0, 0.14, "up", "Demonstrative rate",
        "Pointing words used in place of specific nouns."),
    "ling.ar_vague_noun_rate": (0.0, 0.06, "up", "Vague-noun rate",
        "'the thing', 'the stuff' instead of the real word."),
    "ling.noun_rate": (0.18, 1.0, "down", "Naming rate",
        "How often actual nouns are used - i.e. naming rather than pointing."),
    "ling.ar_ttr_root": (0.45, 1.0, "down", "Vocabulary variety (root-based)",
        "Word variety measured over Arabic roots, not surface forms."),
    # ---------- Acoustic (language-independent) ----------
    "ac.phonation_ratio": (0.55, 1.0, "down", "Speaking vs. silence",
        "Proportion of the recording actually spent speaking."),
    "ac.pause_rate_per_min": (0.0, 32.0, "up", "Pause frequency",
        "How often speech is interrupted by silence."),
    "ac.pause_mean_s": (0.0, 0.75, "up", "Average pause length",
        "Long pauses often mean searching for a word."),
    "ac.f0_cv": (0.10, 1.0, "down", "Pitch variation",
        "Flat, monotone delivery. Also a marker in depression."),
    # ---------- Information content (Cookie Theft) ----------
    "iu.total": (8.0, 100.0, "down", "Information units",
        "How many of the picture's people, objects and actions were mentioned. "
        "The single strongest marker measured in this corpus."),
    "iu.proportion": (0.35, 1.0, "down", "Content coverage",
        "Proportion of the scene actually described."),
    "iu.actions": (1.0, 100.0, "down", "Actions described",
        "Describing what is HAPPENING, not just naming objects."),
    "iu.objects": (4.0, 100.0, "down", "Objects named",
        "How many objects in the scene were named."),
    "iu.per_100_words": (7.0, 100.0, "down", "Information efficiency",
        "Information conveyed per hundred words. Low values mean fluent but "
        "empty speech."),
    # ---------- Discourse coherence ----------
    "sem.local_coherence": (0.66, 1.0, "down", "Sentence-to-sentence coherence",
        "Whether consecutive sentences connect to one another."),
    "sem.global_coherence": (0.83, 1.0, "down", "Overall coherence",
        "Whether the description stays on topic throughout."),
    "sem.loop_rate": (0.0, 0.15, "up", "Semantic looping",
        "Repeating the same idea in different words."),
    # ---------- CHAT-annotated disfluency ----------
    "chat.retracing_per100": (0.0, 2.25, "up", "Repetitions",
        "Repeating words verbatim while searching for the next one."),
    "chat.reformulation_per100": (0.0, 2.85, "up", "Self-corrections",
        "Starting a phrase, abandoning it, and restarting."),
    "chat.long_pause_per100": (0.0, 0.65, "up", "Long pauses",
        "Extended silences, often while searching for a word."),
}

# Which indicators belong to which construct, for the report's grouping
GROUPS = {
    "Word finding & naming": [
        "ling.pronoun_to_noun_ratio", "ling.ar_referential_deficit_index",
        "ling.ar_demonstrative_rate", "ling.ar_vague_noun_rate", "ling.noun_rate"],
    "Vocabulary & content": [
        "ling.type_token_ratio", "ling.ar_ttr_root",
        "ling.content_word_ratio", "ling.idea_density"],
    "Grammar & structure": ["ling.mean_sentence_len"],
    "Information content": [
        "iu.total", "iu.proportion", "iu.actions", "iu.objects",
        "iu.per_100_words"],
    "Discourse coherence": [
        "sem.local_coherence", "sem.global_coherence", "sem.loop_rate"],
    "Fluency & timing": [
        "ac.phonation_ratio", "ac.pause_rate_per_min", "ac.pause_mean_s",
        "ling.filler_rate"],
    "Voice": ["ac.f0_cv"],
}

# THE DEPLOYED OPERATING POINT (corrected 2026-08-22).
# 0.367 is the threshold of the deployed model: the highest cut-off that still
# holds sensitivity at or above the 0.75 screening floor on the locked
# 987-recording development set, giving 0.757 sensitivity and 0.588
# specificity (results/summary/CURRENT_development_stats.json ->
# operating_points.screening; floor sweep in
# results/reconstruction/sensitivity_floor_sweep.json).
#
# It replaces 0.234, which was the 85%-sensitivity point of a PRE-LOCK model
# fitted on the age/sex-matched Pitt cohort (transcript 2026-08-16T15:18) --
# three pool changes and one retrain out of date, and present in no result
# file. A screening instrument is tuned for sensitivity, not overall accuracy;
# the floor is 0.75, not 0.85 (see src/dhikra/model.py::screening_threshold).
SCREENING_THRESHOLD = 0.367

_MODEL = None          # set by attach_model() once a real model exists
_MODEL_FEATURES = None


def load_empirical_ranges(path: str) -> int:
    """
    Replace the hand-set orientation ranges with EMPIRICAL ones derived from
    the healthy control group of a real corpus.

    The defaults above were reasonable starting values chosen from the
    literature, but they were not measured. Percentiles computed from actual
    healthy speakers turn "outside the expected range" from an informed guess
    into an observation: the 5th-95th percentile band means 90% of healthy
    controls fall inside it. Returns how many ranges were replaced.
    """
    import json
    with open(path, encoding="utf-8") as f:
        emp = json.load(f)
    n = 0
    for key, band in emp.items():
        if key not in REFERENCE_RANGES:
            continue
        low, high, direction, label, meaning = REFERENCE_RANGES[key]
        if direction == "up":
            REFERENCE_RANGES[key] = (low, band["p95"], direction, label, meaning)
        else:
            REFERENCE_RANGES[key] = (band["p5"], high, direction, label, meaning)
        n += 1
    return n


def attach_model(pipeline, feature_names, threshold: float | None = None) -> None:
    """
    Switch the report into scored mode using a model trained on real data.
    Called once a classifier has been fitted on the real corpus.

    `threshold` overrides SCREENING_THRESHOLD when the model bundle carries
    one. When it does not, the module default (0.367) applies -- which is why
    that default must stay equal to the deployed operating point.
    """
    global _MODEL, _MODEL_FEATURES, SCREENING_THRESHOLD
    _MODEL, _MODEL_FEATURES = pipeline, list(feature_names)
    if threshold is not None:
        SCREENING_THRESHOLD = float(threshold)


def model_attached() -> bool:
    return _MODEL is not None


def _model_probability(features: dict):
    """Screening score from the trained model, or None if unavailable."""
    if _MODEL is None:
        return None
    try:
        import numpy as np
        import pandas as pd
        row = pd.DataFrame([{f: features.get(f, np.nan) for f in _MODEL_FEATURES}])
        return float(_MODEL.predict_proba(row)[0, 1])
    except Exception:
        return None


def _evaluate_indicator(key, value, language="en"):
    """
    Compare one measurement against its reference range.

    LANGUAGE GATE: the empirical ranges were derived from ENGLISH-speaking
    controls. Speech rate, lexical diversity, pronoun frequency, sentence
    length and pause distribution all vary substantially between languages and
    between elicitation tasks, so applying an English range to Arabic speech
    would manufacture "abnormal" findings out of ordinary linguistic
    difference. Arabic sessions therefore report the measured value with the
    range marked as not established, rather than judging it.
    """
    if key not in REFERENCE_RANGES or value is None:
        return None
    low, high, direction, label, meaning = REFERENCE_RANGES[key]
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v != v:                       # NaN
        return None
    if language != "en":
        return {"key": key, "label": label, "value": v, "meaning": meaning,
                "reference": "not established for Arabic",
                "direction": direction, "atypical": False, "severity": 0.0,
                "range_unavailable": True}
    atypical = v > high if direction == "up" else v < low
    # distance outside the range, normalised, for ordering the findings
    if direction == "up":
        severity = max(0.0, (v - high) / (abs(high) + 1e-9))
    else:
        severity = max(0.0, (low - v) / (abs(low) + 1e-9))
    return {
        "key": key, "label": label, "value": v, "meaning": meaning,
        "reference": f"{low:g} – {high:g}" if direction == "up" else f"≥ {low:g}",
        "direction": direction, "atypical": bool(atypical),
        "severity": round(float(severity), 3),
    }


def build_report(features: dict, session_meta: dict | None = None,
                 recitation: dict | None = None,
                 dissociation: dict | None = None) -> dict:
    """
    Build the full screening report from a session's extracted features.

    Returns a dict ready to render as JSON / HTML.
    """
    meta = session_meta or {}
    indicators, groups_out = [], {}

    for group, keys in GROUPS.items():
        rows = []
        for k in keys:
            ev = _evaluate_indicator(k, features.get(k),
                                     meta.get("language", "ar"))
            if ev:
                rows.append(ev)
                indicators.append(ev)
        if rows:
            groups_out[group] = rows

    n_total = len(indicators)
    n_atypical = sum(1 for i in indicators if i["atypical"])
    ranges_unavailable = any(i.get("range_unavailable") for i in indicators)
    flagged = sorted([i for i in indicators if i["atypical"]],
                     key=lambda i: -i["severity"])

    # ---- banding ----------------------------------------------------------
    # When a calibrated model is available the band comes from the MODEL, not
    # from counting indicators. Counting treats every measure as equally
    # important, which is false: information units carry an effect size of
    # ~0.95 while some others are near zero. The trained model already weights
    # them according to what actually separated patients from controls, so
    # deferring to it is both more accurate and more honest. The indicator
    # count is retained alongside as a human-readable explanation.
    prob = None
    if model_attached() and meta.get("language", "ar") == "en":
        prob = _model_probability(features)

    if n_total == 0:
        band, band_text = "insufficient", "Not enough usable speech to analyse."
    elif ranges_unavailable:
        band = "insufficient"
        band_text = ("Measurements are reported, but no Arabic normative "
                     "reference ranges have been established, so no judgement "
                     "of typicality can be made. Values below are raw "
                     "measurements only.")
    elif prob is not None:
        # Thresholds derived from the corpus. 0.367 is the deployed operating
        # point: it holds sensitivity at 0.757 (the 0.75 screening floor) for
        # 0.588 specificity, because a missed case costs far more than an
        # unnecessary referral.
        if prob < SCREENING_THRESHOLD:
            band = "typical"
            band_text = ("Below the screening threshold. This speech profile "
                         "resembles the healthy group in the training corpus.")
        elif prob < 0.50:
            band = "borderline"
            band_text = ("Above the high-sensitivity screening threshold but "
                         "below the balanced decision point. At this setting "
                         "the test deliberately over-refers, so many people in "
                         "this band are not impaired.")
        elif prob < 0.75:
            band = "elevated"
            band_text = ("This speech profile resembles the impaired group. "
                         "A clinical assessment is recommended.")
        else:
            band = "high"
            band_text = ("This speech profile strongly resembles the impaired "
                         "group. A clinical assessment is recommended.")
    elif n_atypical == 0:
        band = "typical"
        band_text = "All measured indicators fall within the reference range."
    elif n_atypical <= max(1, n_total // 5):
        band = "borderline"
        band_text = ("A small number of indicators fall outside the reference "
                     "range. This is common and not in itself a concern.")
    elif n_atypical <= max(2, n_total // 2):
        band = "elevated"
        band_text = ("Several indicators fall outside the reference range. "
                     "A clinical assessment is recommended.")
    else:
        band = "high"
        band_text = ("Most indicators fall outside the reference range. "
                     "A clinical assessment is recommended.")

    report = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "participant": {
            "code": meta.get("code", ""), "age": meta.get("age"),
            "sex": meta.get("sex", ""), "education": meta.get("education"),
            "language": meta.get("language", "ar"),
        },
        "mode": ("screening_score"
                 if (model_attached() and meta.get("language", "ar") == "en")
                 else "indicator_profile"),
        "band": band,
        "band_text": band_text,
        "counts": {"atypical": n_atypical, "total": n_total},
        "groups": groups_out,
        "flagged": flagged[:8],
        "recitation": recitation or {},
        "dissociation": dissociation or {},
        "disclaimer": (
            "ذِكرى is a SCREENING aid, not a diagnostic test. It cannot "
            "diagnose Alzheimer's disease or any other condition. This report "
            "describes measured speech characteristics only and must be "
            "interpreted by a qualified clinician. Reference ranges are "
            "orientation values, not validated diagnostic cut-offs."),
    }

    if prob is not None:
        report["model_probability"] = round(prob, 3)
        report["screening_threshold"] = SCREENING_THRESHOLD
        report["model_note"] = (
            "Screening score from a model trained on labelled clinical data "
            f"(threshold {SCREENING_THRESHOLD:g}; sensitivity 0.76, "
            "specificity 0.59 on the development set). A screening score, "
            "not a clinical probability.")

    # ---- calibrated mode, once a real trained model is attached ----
    # The model was fitted on ENGLISH transcripts. Emitting its probability for
    # an Arabic session would present a number with no validity behind it, so
    # Arabic sessions stay in indicator-profile mode until Arabic clinical data
    # exists. This is the boundary the whole project rests on.
    if model_attached() and meta.get("language", "ar") == "en":
        import numpy as np
        import pandas as pd
        row = pd.DataFrame([{f: features.get(f, np.nan) for f in _MODEL_FEATURES}])
        try:
            prob = float(_MODEL.predict_proba(row)[0, 1])
            report["model_probability"] = round(prob, 3)
            report["model_note"] = ("Screening score from a model trained on "
                                    "labelled clinical data -- a screening "
                                    "score, not a clinical probability.")
        except Exception as e:
            report["model_note"] = f"Model scoring unavailable: {type(e).__name__}"

    return report


def report_to_text(report: dict) -> str:
    """Plain-text rendering, for saving alongside the session."""
    p = report["participant"]
    lines = [
        "ذِكرى (Dhikra) — Speech Screening Report",
        "=" * 60,
        f"Participant : {p.get('code','—')}   age {p.get('age','—')}   {p.get('sex','')}",
        f"Language    : {p.get('language','')}",
        f"Generated   : {report['generated']}",
        f"Mode        : {report['mode']}",
        "",
        f"RESULT: {report['band'].upper()}  "
        f"({report['counts']['atypical']} of {report['counts']['total']} "
        f"indicators outside reference range)",
        report["band_text"],
        "",
    ]
    if report.get("model_probability") is not None:
        lines += [
            f"Screening score: {report['model_probability']*100:.1f}%",
            "  (how closely this speech profile resembles the impaired group "
            "in the training corpus -- a screening score, NOT a calibrated "
            "probability of impairment)",
            "",
        ]
    for c in report.get("model_caveats", []) or []:
        lines += [f"NOTE: {c}", ""]
    if report.get("age_adjusted"):
        a = report["age_adjusted"]
        lines += ["Stage 2 - age-appropriate risk", "-" * 60,
                  f"  speech pattern alone     : {a['speech_score']*100:.0f}%",
                  f"  prevalence at this age   : {a['age_prevalence']*100:.2f}%",
                  f"  starting likelihood      : {a.get('effective_prior',0)*100:.1f}% "
                  f"(age, reason for testing, family history)",
                  f"  FINAL ESTIMATE           : {a['age_adjusted_probability']*100:.1f}%",
                  "", f"  {a.get('explanation','')}", ""]
    if report.get("age_note"):
        lines += [f"AGE CONTEXT: {report['age_note']}", ""]
    if report.get("education_note"):
        lines += [f"EDUCATION CONTEXT: {report['education_note']}", ""]
    if report.get("memory_profile"):
        m = report["memory_profile"]
        lines += ["Memory profile - new learning vs overlearned", "-" * 60,
                  f"  pattern: {m['pattern'].upper()}", f"  {m['meaning']}", ""]
    ctx = report.get("context_tasks", {})
    if ctx.get("fluency"):
        f = ctx["fluency"]
        lines += ["Verbal fluency (severity context, not a diagnosis)", "-" * 60,
                  f"  animals named  : {f.get('total_correct')}",
                  f"  perseverations : {f.get('perseverations')}",
                  f"  {f.get('comparable_severity','')}", ""]
    if ctx.get("story_recall"):
        r = ctx["story_recall"]
        lines += ["Story recall (severity context)", "-" * 60,
                  f"  idea units recalled: {r.get('idea_units_recalled')}", ""]

    if report.get("flagged"):
        lines.append("Indicators outside the reference range")
        lines.append("-" * 60)
        for f in report["flagged"]:
            arrow = "high" if f["direction"] == "up" else "low"
            lines.append(f"  • {f['label']}: {f['value']:.3f} "
                         f"({arrow}; reference {f['reference']})")
            lines.append(f"      {f['meaning']}")
        lines.append("")
    if report.get("recitation"):
        r = report["recitation"]
        if "ar_recite_accuracy" in r:
            lines += ["Recitation (overlearned-memory probe)", "-" * 60,
                      f"  accuracy {r['ar_recite_accuracy']:.3f}   "
                      f"word error rate {r['ar_recite_word_error_rate']:.3f}", ""]
    lines += ["", report["disclaimer"]]
    return "\n".join(lines)
