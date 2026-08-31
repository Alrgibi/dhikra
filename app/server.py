"""
server.py — ذِكرى Assessment Platform
=====================================
The real clinical instrument: administers the task battery, records the
participant, transcribes, analyses, and produces a screening report.

    pip install flask
    python app/server.py
    # open http://127.0.0.1:5000

WHO OPERATES IT
Not the elderly person alone. A family member, nurse or health worker opens it,
hands over the phone/tablet, and the participant simply talks. The whole session
is about six minutes.

THE TASK BATTERY
  1. Picture description  - spontaneous speech (degrades earliest in AD)
  2. Verbal fluency       - "name as many animals as you can in one minute"
  3. Story recall         - probes episodic memory
  4. Quran recitation     - overlearned speech (preserved longest); Arabic only

WHAT RUNS WHERE
  browser : MediaRecorder captures audio (webm/ogg)
  server  : ffmpeg -> 16 kHz mono WAV
            acoustic engine  (librosa + Praat)        <- never needs words
            transcription    (Whisper, or operator typing)
            linguistic engine (spaCy / qalsadi+pyarabic)
            report engine    (indicator profile, or screening score if trained)

HONEST NOTE ON TRANSCRIPTION
Whisper downloads model weights on first use and needs internet on the machine
running this. If it is unavailable the platform does NOT fail and does NOT
invent text - it asks the operator to type the transcript, which is how the
DementiaBank reference corpus itself was built. Acoustic analysis is unaffected
either way.
"""
from __future__ import annotations

import io
import json
import re
import os
import sys
import tempfile
import traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from flask import Flask, request, jsonify, render_template, send_from_directory

from dhikra.acoustic_features import extract_acoustic_features
from dhikra.linguistic_features import extract_linguistic_features
from dhikra.linguistic_features_ar import (extract_linguistic_features_ar,
                                           recitation_fidelity,
                                           task_dissociation_index,
                                           FATIHA_REFERENCE)
from dhikra.information_units import extract_information_units
from dhikra.fluency_features import extract_fluency_features, NORM_NOTE
from dhikra import risk_adjustment as risk
from dhikra import quality_control as qc
from dhikra.semantic_features import extract_semantic_features
from dhikra.report import build_report, report_to_text, model_attached
from dhikra import stimuli
from dhikra import asr

BASE = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(BASE, "..", "data", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(BASE, "templates"),
            static_folder=os.path.join(BASE, "static"))
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024   # 64 MB per upload

# in-memory store for the session currently being administered
SESSIONS: dict[str, dict] = {}


def load_trained_model() -> bool:
    """
    Load the model trained on DementiaBank, if it has been built.

    When present, the report switches from 'indicator profile' (counting how
    many measures fall outside reference ranges) to a CALIBRATED probability
    from a classifier fitted on real labelled patients. Absent, the platform
    still works and simply never claims a probability it cannot justify.
    """
    path = os.path.join(BASE, "..", "models", "dhikra_model.pkl")
    if not os.path.exists(path):
        return False
    try:
        import pickle
        with open(path, "rb") as f:
            bundle = pickle.load(f)
        from dhikra.report import attach_model, load_empirical_ranges
        attach_model(bundle["model"], bundle["features"],
                     bundle.get("screening_threshold"))
        rp = os.path.join(BASE, "..", "results", "pitt_cookie",
                          "reference_ranges.json")
        if os.path.exists(rp):
            n = load_empirical_ranges(rp)
            print(f"  empirical ranges     : {n} loaded from the control group")
        app.config["MODEL_INFO"] = {k: v for k, v in bundle.items()
                                    if k not in ("model", "features")}
        return True
    except Exception as e:
        print(f"  ! could not load trained model: {type(e).__name__}: {e}")
        return False


MODEL_LOADED = load_trained_model()


# ─────────────────────────────────────────────────────────── task battery ────
def build_battery(lang: str, code: str, session_no: int,
                  known_surahs: list[str] | None) -> tuple[list[dict], dict]:
    """
    Assemble the battery for this session, selecting stimuli from the bank.

    Stimuli rotate per participant per session (parallel forms) so a repeat
    visit does not reuse the same picture or story, while each session remains
    reproducible. The chosen stimulus ids are returned so they can be recorded.
    """
    # Rotate only when there is no scored result to lose: on repeat visits
    # (where practice effects matter) or in Arabic (no English model applies).
    rotate = (session_no > 1) or (lang != "en")
    pic = stimuli.pick_picture(code, session_no, rotate=rotate)
    story = stimuli.pick_story(code, session_no)
    surah = stimuli.pick_surah(known_surahs, code, session_no) if lang == "ar" else None

    ar = lang == "ar"
    # TASK ORDER, revised 2026-08-25 (THESIS_PLAN 3.5, 5.25).
    # The two CONNECTED-DISCOURSE tasks are administered FIRST because they are
    # the stronger genre for mild cognitive impairment -- Delaware's five tasks
    # separate perfectly by genre, and two discourse tasks administered together
    # beat three picture-description tasks together (+0.079 [+0.004, +0.158]).
    # Picture description is RETAINED, unchanged, and still supplies the
    # screening score: it is the only task with an externally validated model
    # behind it (see the note at `primary` below). Ordering administration is not
    # the same as changing what is scored, and only the first is done here.
    tasks = [
        {"id": "story", "type": "story",
         "title": "استرجاع القصة" if ar else "Story recall",
         "instruction": stimuli.STORY_PROMPT["ar" if ar else "en"],
         "seconds": 90,
         "hint": "اقرأ القصة مرة واحدة بوضوح، ثم سجّل إعادة الحكاية." if ar
                 else "Read the story once, clearly, then record the retelling.",
         "text": story["ar" if ar else "en"], "stimulus_id": story["id"]},
        # Procedural discourse. Added 2026-08-25 on the evidence of THESIS_PLAN
        # 5.25: on the one corpus that can compare tasks, procedural discourse is
        # the STRONGEST of five for MCI (AUC 0.607) while picture description is
        # the weakest (0.506). It needs NO stimulus material at all, which makes
        # it the only task in this battery that survives intact in the paper
        # fallback and on a device with no screen. "Making tea" is chosen over
        # the corpus's sandwich prompt because it is culturally universal here.
        {"id": "procedure", "type": "timed",
         "title": "وصف إجراء" if ar else "Procedural discourse",
         "instruction": ("احكِ لي، خطوة بخطوة، كيف تُحضّر الشاي."
                         if ar else
                         "Tell me, step by step, how you make tea."),
         "seconds": 90,
         "hint": ("لا تقدّم خطوات. أعد الطلب مرّة واحدة فقط بعد صمت عشر ثوانٍ: "
                  "«هل هناك شيء آخر؟»" if ar else
                  "Do not supply steps. Re-prompt once only, after 10 s of "
                  "silence: 'anything else?'")},
        {"id": "picture", "type": "picture",
         "title": "وصف الصورة" if ar else "Picture description",
         "instruction": stimuli.PICTURE_PROMPT["ar" if ar else "en"],
         "seconds": 90,
         "hint": "شجّع المشارك على الاستمرار: «وماذا أيضاً؟»" if ar
                 else "Encourage continuation: 'anything else?'",
         "image": pic["file"], "stimulus_id": pic["id"]},
        {"id": "fluency", "type": "timed",
         "title": "الطلاقة اللفظية" if ar else "Verbal fluency",
         "instruction": ("اذكر أكبر عدد ممكن من أسماء الحيوانات في دقيقة واحدة."
                         if ar else
                         "Name as many animals as you can in one minute."),
         "seconds": 60,
         "hint": "لا تساعد بأمثلة. اترك الصمت كما هو." if ar
                 else "Do not give examples. Let silences stand."},
    ]

    chosen = {"picture": pic["id"], "story": story["id"], "surah": None}

    if surah:
        tasks.append({
            "id": "recitation", "type": "recitation",
            "title": f"تلاوة سورة {surah['name_ar']}",
            "instruction": stimuli.RECITATION_PROMPT["ar"].format(name=surah["name_ar"]),
            "seconds": 60,
            "hint": "مهمة الذاكرة المُفرطة التعلّم — تبقى محفوظة لفترة أطول.",
            "surah_id": surah["id"], "surah_name": surah["name_ar"],
            "stimulus_id": surah["id"]})
        chosen["surah"] = surah["id"]

    return tasks, chosen


# ───────────────────────────────────────────────────────────────── routes ────
def _vectors_available() -> bool:
    """True when spaCy's vector model is installed. See the startup banner."""
    try:
        import spacy
        spacy.load("en_core_web_md")
        return True
    except Exception:
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config")
def config():
    """Tell the front end what the environment can actually do."""
    return jsonify({
        "asr_available": asr.whisper_available(),
        "ffmpeg_available": asr.ffmpeg_available(),
        "model_attached": model_attached(),
        "model_info": app.config.get("MODEL_INFO", {}),
        "fatiha_reference": FATIHA_REFERENCE,
    })


@app.route("/api/surahs")
def surahs():
    """The list the operator picks from: which surahs does the participant know?"""
    return jsonify(stimuli.surah_choices())


@app.route("/api/session/start", methods=["POST"])
def session_start():
    d = request.get_json(force=True)
    lang = d.get("language", "ar")
    code = (d.get("code") or "").strip() or f"P{datetime.now():%y%m%d%H%M%S}"
    # distinguish "knows none" (empty list -> skip task) from "unspecified" (None)
    known = d.get("known_surahs")
    if known is not None and not isinstance(known, list):
        known = None

    # session number = how many previous sessions this participant already has
    session_no = 1 + sum(1 for fn in os.listdir(SESSION_DIR)
                         if fn.startswith(f"{code}_") and fn.endswith(".json"))

    sid = f"{code}_{datetime.now():%Y%m%d_%H%M%S}"
    tasks, chosen = build_battery(lang, code, session_no, known)

    SESSIONS[sid] = {
        "id": sid,
        "meta": {"code": code, "age": d.get("age"), "sex": d.get("sex", ""),
                 "education": d.get("education"), "language": lang,
                 "referral_context": d.get("referral_context", "population"),
                 "family_history": d.get("family_history", "unknown"),
                 "session_number": session_no, "stimuli": chosen,
                 "known_surahs": known,
                 "started": datetime.now(timezone.utc).isoformat(timespec="seconds")},
        "tasks": {},
    }
    return jsonify({"session_id": sid, "tasks": tasks,
                    "session_number": session_no, "stimuli": chosen})


@app.route("/api/task/upload", methods=["POST"])
def task_upload():
    """
    Receive one task recording. Converts to WAV, runs the acoustic engine
    immediately (words not required), then attempts transcription.
    """
    sid = request.form.get("session_id", "")
    task_id = request.form.get("task_id", "")
    lang = request.form.get("language", "ar")
    if sid not in SESSIONS:
        return jsonify({"error": "unknown session"}), 400
    if "audio" not in request.files:
        return jsonify({"error": "no audio uploaded"}), 400

    tmpdir = tempfile.mkdtemp(prefix="dhikra_")
    raw_path = os.path.join(tmpdir, f"{task_id}.webm")
    request.files["audio"].save(raw_path)

    out = {"task_id": task_id}
    try:
        wav = asr.convert_to_wav(raw_path)
        out["duration_ok"] = True
    except Exception as e:
        return jsonify({"error": f"audio conversion failed: {e}"}), 500

    # ---- acoustic analysis (always runs; needs no words) ----
    try:
        ac = extract_acoustic_features(wav)
        out["acoustic"] = ac
        out["acoustic_ok"] = True
    except Exception as e:
        out["acoustic"] = {}
        out["acoustic_ok"] = False
        out["acoustic_error"] = f"{type(e).__name__}: {e}"

    # ---- quality gate: refuse rather than analyse an unusable recording ----
    try:
        chk = qc.check_recording(wav, out.get("acoustic"))
        out["quality"] = chk
    except Exception:
        out["quality"] = {"usable": True, "severity": "ok", "issues": [],
                          "metrics": {}}

    # ---- transcription (may be unavailable -> operator types it) ----
    tr = asr.transcribe(wav, lang=lang)
    out["transcript"] = tr["text"]
    out["asr_available"] = tr["available"]
    out["asr_engine"] = tr["engine"]
    out["asr_message"] = tr["message"]

    SESSIONS[sid]["tasks"][task_id] = {
        "wav": wav, "acoustic": out.get("acoustic", {}),
        "transcript": tr["text"], "quality": out.get("quality", {}),
    }
    return jsonify(out)


@app.route("/api/task/transcript", methods=["POST"])
def task_transcript():
    """Operator confirms or corrects the transcript for a task."""
    d = request.get_json(force=True)
    sid, task_id = d.get("session_id"), d.get("task_id")
    if sid not in SESSIONS:
        return jsonify({"error": "unknown session"}), 400
    SESSIONS[sid]["tasks"].setdefault(task_id, {})["transcript"] = d.get("text", "")
    return jsonify({"ok": True})


@app.route("/api/session/analyze", methods=["POST"])
def session_analyze():
    """Run the full analysis across the battery and build the report."""
    d = request.get_json(force=True)
    sid = d.get("session_id")
    if sid not in SESSIONS:
        return jsonify({"error": "unknown session"}), 400

    sess = SESSIONS[sid]
    lang = sess["meta"].get("language", "ar")
    tasks = sess["tasks"]

    features: dict[str, float] = {}

    # ---- primary spontaneous task drives the linguistic analysis ----
    # DELIBERATELY UNCHANGED, 2026-08-25. THESIS_PLAN 5.25 shows connected
    # discourse is the stronger genre for MCI, and the battery is now
    # administered in that order -- but the deployed model was trained and
    # EXTERNALLY VALIDATED on picture description (Lu, AUC 0.853 [0.737, 0.946]).
    # Scoring a task the model was never fitted for would forfeit that
    # validation, which is the one property nothing else in this project has.
    # The discourse transcripts are therefore COLLECTED (they are the material
    # the Libyan MCI corpus needs, docs/ARABIC_CORPUS_GAP.md 5) but do not
    # contribute to the screening score. Changing this line requires a new
    # external validation, not a new argument.
    primary = tasks.get("picture") or tasks.get("story") or {}
    text = (primary.get("transcript") or "").strip()
    stim = sess["meta"].get("stimuli", {}).get("picture")
    if text:
        try:
            ling = (extract_linguistic_features_ar(text) if lang == "ar"
                    else extract_linguistic_features(text))
            for k, v in ling.items():
                features[f"ling.{k}"] = v
        except Exception as e:
            features["_ling_error"] = f"{type(e).__name__}: {e}"

        if lang == "en":
            # Information units are defined against the training picture's
            # content inventory. The 'kitchen' scene was designed with the same
            # structure as the corpus stimulus (person at a sink, water
            # overflowing, child on a tipping stool reaching a jar), so the
            # inventory transfers. The market and courtyard scenes depict
            # entirely different content, so scoring them against this
            # inventory would be meaningless -- the features are left MISSING
            # rather than computed as spurious zeros.
            try:
                features.update(extract_information_units(
                    text, scene=stim or "kitchen"))
            except Exception:
                pass
            try:
                features.update(extract_semantic_features(text))
            except Exception:
                pass

    # ---- acoustic from the same primary task ----
    for k, v in (primary.get("acoustic") or {}).items():
        features[f"ac.{k}"] = v

    # ---- per-task acoustic kept for the record ----
    per_task = {tid: {"has_audio": bool(t.get("acoustic")),
                      "words": len((t.get("transcript") or "").split())}
                for tid, t in tasks.items()}

    # ---- Quran recitation probe ----
    recit = {}
    if "recitation" in tasks and (tasks["recitation"].get("transcript") or "").strip():
        assigned_id = sess["meta"].get("stimuli", {}).get("surah")
        known = sess["meta"].get("known_surahs")
        text_r = tasks["recitation"]["transcript"]

        # Score against what was ACTUALLY recited, not merely what was asked
        # for -- see stimuli.best_surah_match for why this matters.
        pool = known if known else ([assigned_id] if assigned_id else None)
        matched, recit = stimuli.best_surah_match(text_r, pool)
        if matched:
            recit["surah_name"] = matched["name_ar"]
            recit["surah_id"] = matched["id"]
            recit["assigned_surah_id"] = assigned_id
            recit["recited_as_assigned"] = (assigned_id == matched["id"])
        elif assigned_id:
            sur = stimuli.get_surah(assigned_id)
            recit = recitation_fidelity(text_r, sur["text"] if sur else FATIHA_REFERENCE)

    # ---- task dissociation: spontaneous vs overlearned ----
    dissoc = {}
    if primary.get("acoustic") and tasks.get("recitation", {}).get("acoustic"):
        dissoc = task_dissociation_index(primary["acoustic"],
                                         tasks["recitation"]["acoustic"])

    # ---- secondary tasks: reported as clinical context, NOT scored ----
    # The Pitt corpus contains fluency, recall and sentence tasks for the
    # dementia group ONLY, with no healthy controls, so no threshold for them
    # could be learned from the data used here. They are measured and shown to
    # the operator, and deliberately excluded from the screening decision.
    context = {}
    ftxt = (tasks.get("fluency", {}).get("transcript") or "").strip()
    if ftxt:
        fl = extract_fluency_features(ftxt, lang=lang)
        context["fluency"] = {
            "total_correct": fl.get("flu.total_correct"),
            "perseverations": fl.get("flu.perseverations"),
            "unrecognised": fl.get("flu.intrusions"),
            "words": fl.get("_correct_words", [])[:40],
            "repeated": fl.get("_perseverated", [])[:10],
            "note": NORM_NOTE,
        }
    stxt = (tasks.get("story", {}).get("transcript") or "").strip()
    recall_units = None
    if stxt:
        story_id = sess["meta"].get("stimuli", {}).get("story")
        st = next((x for x in stimuli.STORIES if x["id"] == story_id), None)
        if st:
            # Count CONTENT words shared with the story, not every word.
            # The severity model was trained on content-word overlap bounded by
            # the story's own vocabulary; counting function words ("the", "and")
            # would inflate the score far beyond that range and corrupt the
            # severity estimate.
            stop = {"the","a","an","and","or","but","of","to","in","on","at",
                    "for","with","from","by","he","she","it","they","him","her",
                    "his","hers","them","that","this","was","were","is","are",
                    "had","has","have","been","be","would","will","did","do",
                    "not","so","as","if","then","when","there","their","one",
                    "في","من","على","الى","إلى","عن","مع","هو","هي","هم","ان",
                    "أن","إن","كان","كانت","التي","الذي","ما","لا","و","ثم"}
            src = st["ar" if lang == "ar" else "en"].lower()
            key = {w for w in re.findall(r"[\w\u0600-\u06FF]{3,}", src)
                   if w not in stop}
            said = set(re.findall(r"[\w\u0600-\u06FF]{3,}", stxt.lower()))
            recall_units = len(key & said)
            context_max = len(key)
        context["story_recall"] = {
            "words_produced": len(stxt.split()),
            "idea_units_recalled": recall_units,
            "of_possible": context_max,
            "note": ("Story recall tracked severity in the training corpus "
                     "(r = 0.46 with MMSE, n = 237), so it is reported as a "
                     "severity indicator. It cannot give a healthy-vs-impaired "
                     "threshold, because the corpus contains this task for the "
                     "dementia group only."),
        }

    # ---- session-level quality verdict ----
    checks = {t: v.get("quality", {}) for t, v in tasks.items() if v.get("quality")}
    verdict = qc.session_verdict(checks) if checks else {"scoreable": True}

    report = build_report(features, sess["meta"], recitation=recit,
                          dissociation=dissoc)
    report["quality"] = {"per_task": checks, "verdict": verdict}
    if not verdict.get("scoreable", True):
        report["band"] = "insufficient"
        report["band_text"] = verdict["reason"]
        report.pop("model_probability", None)
        report["mode"] = "refused"
    report["context_tasks"] = context

    # ---- STAGE 2: age adjustment, education caveat, cross-task profile ----
    age = sess["meta"].get("age")
    edu = sess["meta"].get("education")
    prob = report.get("model_probability")

    if prob is not None and age is not None:
        report["age_adjusted"] = risk.adjust_for_age(
            prob, age,
            sess["meta"].get("referral_context", "population"),
            sess["meta"].get("family_history", "unknown"))
    note = risk.age_context_note(age)
    if note:
        report["age_note"] = note
    disc = risk.discordance_note(prob, age)
    if disc:
        report["discordance_note"] = disc

    edu_note = risk.education_note(edu, [f["key"] for f in report.get("flagged", [])])
    if edu_note:
        report["education_note"] = edu_note

    if context.get("fluency", {}).get("total_correct") is not None:
        context["fluency"].update(
            risk.fluency_severity_context(context["fluency"]["total_correct"]))

    # ---- composite severity index across the battery ----
    sev_path = os.path.join(BASE, "..", "models", "dhikra_severity_model.pkl")
    if os.path.exists(sev_path):
        try:
            import pickle as _pk
            import pandas as _pd
            sb = _pk.load(open(sev_path, "rb"))
            iu_p = features.get("iu.proportion")
            fl_c = context.get("fluency", {}).get("total_correct")
            rc_u = recall_units
            if sum(v is not None for v in (iu_p, fl_c, rc_u)) >= 2:
                row = _pd.DataFrame([{"iu": iu_p, "total_correct": fl_c,
                                      "idea_units_recalled": rc_u}])
                est = float(sb["model"].predict(row)[0])
                # BANDED, NOT NUMERIC (changed 2026-08-23). A one-decimal
                # MMSE estimate reads as a measurement whatever caveat sits
                # beside it, and this model's own reported accuracy could NOT
                # be reproduced by a pre-registered rebuild (CANNOT-CONFIRM).
                # The band is what the evidence supports; the point estimate is
                # kept in the machine-readable field below for audit only and
                # must not be surfaced to an operator.
                _e = max(0.0, min(30.0, est))
                _band = ("severe" if _e < 11 else
                         "moderate-to-severe" if _e < 16 else
                         "moderate" if _e < 21 else
                         "mild-to-moderate" if _e < 26 else "mild range")
                report["severity_index"] = {
                    "severity_band": _band,
                    "band_basis": ("MMSE bands measured in the Pitt dementia "
                                   "cohort. This places someone WITHIN a "
                                   "diagnosed group; it is not a "
                                   "healthy-versus-impaired judgement."),
                    "_estimated_mmse_audit_only": round(_e, 1),
                    "tasks_used": int(sum(v is not None
                                          for v in (iu_p, fl_c, rc_u))),
                    "accuracy": (f"r = {sb['r']:.2f} against real MMSE, average "
                                 f"error {sb['mae']:.1f} points (n = {sb['n']}) "
                                 "- the deployed model's own recorded figure. "
                                 "A pre-registered rebuild could NOT reproduce "
                                 "it (grade CANNOT-CONFIRM, rebuilt cohort "
                                 "n = 156 against the recorded 155), so treat "
                                 "this as artifact metadata, not a verified "
                                 "result."),
                    "note": ("Estimated from the picture, fluency and recall "
                             "tasks combined. Alone, story recall predicts MMSE "
                             "at r = 0.46 and verbal fluency at r = 0.40; the "
                             "combined index is recorded at r = 0.66, though "
                             "that combined figure is unconfirmed (see above). "
                             "This estimates HOW impaired someone is IF they "
                             "are impaired - it was trained only on people who "
                             "already had a diagnosis, so it cannot indicate "
                             "whether impairment is present."),
                }
        except Exception:
            pass

    ra = recit.get("ar_recite_accuracy") if recit else None
    if recall_units is not None and ra is not None:
        report["memory_profile"] = risk.memory_dissociation(recall_units, ra)
    report["scored_from"] = {
        "task": "picture",
        "stimulus": stim,
        "note": ("The screening result is computed from the picture-"
                 "description task only. That is the sole task in the "
                 "training corpus that included healthy controls, and it "
                 "is the task on which this model was externally "
                 "validated. The story-recall and procedural-discourse "
                 "tasks are administered first and recorded, but do not "
                 "contribute to this result: they carry more signal for "
                 "MILD impairment, and scoring them would require a new "
                 "validation study rather than a new setting."),
        "administration_order": ["story", "procedure", "picture",
                                 "fluency", "recitation"],
        "collected_not_scored": ["story", "procedure"],
    }
    report["per_task"] = per_task
    report["stimulus"] = stim

    # State plainly where the trained model does and does not apply.
    if model_attached():
        caveats = []
        # Decision stability. THESIS_PLAN 5.26.1: the probability that a repeat
        # recording falls on the same side of the threshold is 0.8355 across the
        # development set -- one screening decision in six would reverse -- but
        # it is not uniform: 0.954 for scores more than one standard error of
        # measurement from the threshold, and 0.669 for scores within it
        # (SEM 0.1032, results/reconstruction/repeat_sampling_analysis.json).
        # This is a STATEMENT, not a decision rule: no band, threshold or score
        # is altered by it. The three-band report that 5.26 recommends is NOT
        # implemented here, because its band is defined against a LOCAL
        # control-referenced threshold that does not exist until local controls
        # are collected, and hard-coding the development SEM against a fixed
        # 0.367 is the practice this project argues against.
        _p = report.get("model_probability")
        _thr = report.get("screening_threshold")
        if _p is not None and _thr is not None and abs(_p - _thr) <= 0.1032:
            caveats.append(
                "This score sits close to the screening threshold. Scores in "
                "this region are the least stable part of the instrument: on "
                "the development set, a repeat recording agreed with the first "
                "on which side of the threshold it fell about two thirds of the "
                "time here, against about 95% for scores further away. Treat "
                "this result as borderline, and consider a second recording or "
                "clinical judgement rather than the number alone.")
        if lang != "en":
            caveats.append(
                "The trained model was fitted on English transcripts. "
                "Arabic sessions are reported as an indicator profile; no "
                "Arabic-validated probability exists yet.")
        elif stim not in (None, "kitchen"):
            caveats.append(
                "The trained model was fitted on descriptions of a kitchen "
                "scene. This session used a different picture, so the trained "
                "probability does not transfer and has been withheld; the "
                "indicator profile below still applies.")
            report.pop("model_probability", None)
            report["mode"] = "indicator_profile"
        # STIMULUS SUBSTITUTION. THESIS_PLAN 4.3.1. The calibrated model was
        # fitted on descriptions of the Boston Diagnostic Aphasia Examination's
        # Cookie Theft picture. That picture is not redistributable, so this
        # system shows a scene drawn for the project. On 26 August 2026 the
        # frozen model was probed to find how far the substitution would have to
        # act before the decision changed
        # (results/stimulus_inventory_probe.json, pre-registered): ONE displaced
        # information unit crosses 13.1% of control recordings over the
        # threshold, two crosses 26.7%. Whether it displaces anything at all is
        # unknown and cannot be known without Libyan data.
        #
        # This caveat is attached to EVERY score from the validated picture, not
        # only borderline ones, and it does not change the score. The system has
        # no evidence that would justify withholding the probability, and no
        # evidence that would justify presenting it as though the substitution
        # were free. It says which of those two it is.
        if _p is not None and lang == "en" and stim in (None, "kitchen"):
            caveats.append(
                "The picture shown is not the picture this model was "
                "calibrated on. The original belongs to a published test and "
                "cannot be redistributed, so an equivalent scene drawn for "
                "this project is used instead. Every item the scorer looks "
                "for is present in it, but the two pictures are not "
                "interchangeable, and the effect of the substitution on real "
                "speakers has never been measured. If this picture costs a "
                "speaker even one of the items the original would have "
                "prompted, roughly one healthy recording in eight would move "
                "from a negative screen to a positive one. Weigh this score "
                "accordingly until the substitution has been checked on a "
                "local sample.")
        if _p is not None and not _vectors_available():
            caveats.append(
                "Nine of the sixty-four measurements this score is built from "
                "could not be computed on this computer, because the English "
                "word-meaning model is not installed. They have been replaced "
                "by the average value from the training data, which is the "
                "safest available substitute but is not a measurement of this "
                "person. Install it (python -m spacy download en_core_web_md) "
                "and re-analyse before relying on the score.")
        if caveats:
            report["model_caveats"] = caveats
    report["session_id"] = sid

    # ---- persist ----
    try:
        path = os.path.join(SESSION_DIR, f"{sid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"meta": sess["meta"], "features": features,
                       "report": report,
                       "transcripts": {t: (v.get("transcript") or "")
                                       for t, v in tasks.items()}},
                      f, ensure_ascii=False, indent=2)
        report["saved_to"] = os.path.basename(path)
    except Exception as e:
        report["save_error"] = f"{type(e).__name__}: {e}"

    return jsonify(report)


@app.route("/api/session/<sid>/text")
def session_text(sid):
    """Plain-text report, for printing or pasting into notes."""
    path = os.path.join(SESSION_DIR, f"{sid}.json")
    if not os.path.exists(path):
        return "not found", 404
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return report_to_text(data["report"]), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/api/sessions")
def sessions_list():
    """Past sessions, for longitudinal tracking."""
    out = []
    for fn in sorted(os.listdir(SESSION_DIR), reverse=True):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(SESSION_DIR, fn), encoding="utf-8") as f:
                d = json.load(f)
            out.append({"session_id": fn[:-5],
                        "code": d["meta"].get("code"),
                        "started": d["meta"].get("started"),
                        "band": d["report"].get("band"),
                        "atypical": d["report"]["counts"]["atypical"],
                        "total": d["report"]["counts"]["total"]})
        except Exception:
            continue
    return jsonify(out)


@app.errorhandler(500)
def on_error(e):
    return jsonify({"error": "server error", "detail": traceback.format_exc()[-600:]}), 500


if __name__ == "__main__":
    print("=" * 66)
    print("  ذِكرى Assessment Platform")
    print("=" * 66)
    # Nine of the model's sixty-four features come from spaCy's VECTOR model
    # (en_core_web_md). Without it they are returned as MISSING and the
    # pipeline's median imputer fills them with the training median for every
    # participant -- the app still produces a score, and the score is quietly
    # computed from 55 measurements instead of 64. That must not be silent.
    print(f"  ffmpeg available     : {asr.ffmpeg_available()}")
    print(f"  vector model (md)    : {_vectors_available()}"
          f"{'' if _vectors_available() else '   <-- 9 of 64 features will be imputed; run: python -m spacy download en_core_web_md'}")
    print(f"  auto-transcription   : {asr.whisper_available()}"
          f"{'' if asr.whisper_available() else '  (operator will type transcripts)'}")
    _mi = app.config.get("MODEL_INFO", {})
    print(f"  trained model        : {model_attached()}"
          f"{f'  (n={_mi.get(chr(110))}, AUC={_mi.get(chr(97)+chr(117)+chr(99)):.3f})' if model_attached() and _mi.get('auc') else '  (indicator-profile mode)'}")
    print(f"  sessions saved to    : {os.path.abspath(SESSION_DIR)}")
    print("-" * 66)
    print("  open  ->  http://127.0.0.1:5000")
    print("=" * 66)
    app.run(host="127.0.0.1", port=5000, debug=False)
