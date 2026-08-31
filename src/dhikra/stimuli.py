"""
stimuli.py
----------
The stimulus bank: pictures, stories and Quranic surahs for the task battery.

──────────────────────────────────────────────────────────────────────────────
WHY THESE ARE HAND-DESIGNED AND NOT AI-GENERATED
──────────────────────────────────────────────────────────────────────────────
A picture-description task is a MEASURING INSTRUMENT. Its scores mean something
only because every participant faces the same measured difficulty -- which is
precisely why the field has used one standard picture for decades.

If each session showed a different randomly generated image, then a change in a
participant's score could mean their cognition changed, OR simply that this
month's picture happened to be busier. The measurement would stop being
comparable across sessions and across people, which is the entire point of a
screening instrument. Random image generation would therefore make the tool
*look* more advanced while making its numbers meaningless.

The correct solution to repeat-testing is not randomness but PARALLEL FORMS:
a small set of deliberately MATCHED stimuli, each built to the same
specification, so they can be rotated without changing what is measured.

Every picture below is drawn to the same recipe:
    3 human figures  ·  1 animal  ·  ~14-16 nameable objects
    ~8 depicted actions  ·  exactly 1 "unnoticed hazard"
The unnoticed hazard (water overflowing, a pot boiling over, a ball about to
break a window) is a deliberate design element: describing it requires noticing
and reporting something implicit, which is more cognitively demanding than
simply listing objects.

The same logic governs the stories (matched proposition counts) and the surah
set (short, universally memorised, scored by length-normalised error rate).

ROTATION POLICY
Stimuli rotate deterministically by participant code + session number, so a
repeat visit gets a different form while the same session is reproducible.
The stimulus id is recorded in every saved session, so any later comparison
knows which form was used.
"""
from __future__ import annotations
import hashlib


# ═════════════════════════════════════════════════════════════ PICTURES ════
# Each entry documents its content inventory so equivalence is auditable.
PICTURES = [
    {
        "id": "kitchen",
        "file": "scene_kitchen.svg",
        "title_ar": "مشهد المطبخ", "title_en": "Kitchen scene",
        "figures": 3, "animals": 1, "objects": 15, "actions": 8,
        "hazard": "water overflowing from the sink, unnoticed",
        "key_content": ["أم", "ولد", "بنت", "قطة", "كرسي", "خزانة", "برطمان",
                        "خبز", "صحون", "ماء", "نافذة", "نخلة", "إبريق شاي",
                        "طاولة", "أكواب", "ستارة", "فوطة", "حنفية"],
        # Audited against the frozen English scoring key on 2026-08-26 by
        # rendering the SVG and checking every one of the 23 units in
        # information_units.SCENES["kitchen"] against what is actually drawn.
        # Two units -- curtain and dishcloth -- were IN THE KEY BUT NOT IN THE
        # PICTURE, and were unearnable by any speaker however intact. Both have
        # been added to the artwork. Separately, the tap, the running water and
        # the overflow were drawn but OCCLUDED by the woman's body; she now
        # stands behind the counter. All 23 units are earnable as of that date.
        # The size of the omission defect is measured in
        # results/stimulus_inventory_probe.json (Analysis A).
        "unscored_content": ["قطة", "إبريق شاي", "موقد", "خبز", "طاولة", "نخلة"],
    },
    {
        "id": "market",
        "file": "scene_market.svg",
        "title_ar": "مشهد السوق", "title_en": "Market scene",
        "figures": 3, "animals": 1, "objects": 15, "actions": 8,
        "hazard": "a crate of oranges tipping off the stall, unnoticed",
        "key_content": ["بائع", "امرأة", "طفل", "قطة", "ميزان", "برتقال",
                        "صندوق", "سلة", "مظلة", "طاولة", "نقود", "كيس",
                        "تمر", "خيمة", "دراجة"],
    },
    {
        "id": "courtyard",
        "file": "scene_courtyard.svg",
        "title_ar": "مشهد الفناء", "title_en": "Courtyard scene",
        "figures": 3, "animals": 1, "objects": 14, "actions": 8,
        "hazard": "a hose left running, flooding the courtyard, unnoticed",
        "key_content": ["رجل", "امرأة", "ولد", "طائر", "خرطوم", "غسيل",
                        "حبل", "كرة", "نافذة", "شجرة", "دلو", "زهور",
                        "سلة", "باب"],
    },
]

PICTURE_PROMPT = {
    "ar": "انظر إلى الصورة، واحكِ لي كل ما يحدث فيها.",
    "en": "Look at the picture and tell me everything you see happening.",
}


# ══════════════════════════════════════════════════════════════ STORIES ════
# Matched on length and on number of propositions (idea units), because story
# recall is scored on how many ideas are reproduced.
STORIES = [
    {
        "id": "well",
        "propositions": 12,
        "ar": ("خرج رجلٌ من قريته صباحاً ومعه ثلاثةُ أرغفةٍ من الخبز وإبريقُ ماء. "
               "وفي الطريق قابل امرأةً عجوزاً تجلس تحت نخلة، فأعطاها رغيفاً وشرِبت "
               "من مائه. فشكرَته وقالت له إنه سيجد ما فقده عند البئر. ولمّا وصل "
               "البئر وجد خاتم أمه الذي ضاع منه منذ سنوات."),
        "en": ("A man left his village one morning carrying three loaves of bread "
               "and a jug of water. On the road he met an old woman sitting under a "
               "palm tree. He gave her one loaf and she drank from his water. She "
               "thanked him and told him he would find what he had lost at the well. "
               "When he reached the well he found his mother's ring, which had been "
               "missing for years."),
    },
    {
        "id": "fisherman",
        "propositions": 12,
        "ar": ("ذهب صيادٌ إلى البحر عند الفجر ومعه شبكتُه القديمة وقليلٌ من التمر. "
               "وبينما هو يُلقي الشبكة رأى طفلاً يبكي على الشاطئ لأنه أضاع حذاءه. "
               "فأعطاه الصياد بعض التمر وساعده في البحث حتى وجدا الحذاء بين الصخور. "
               "وفي ذلك اليوم عاد الصياد إلى بيته بأكبر صيدٍ في حياته."),
        "en": ("A fisherman went to the sea at dawn carrying his old net and a few "
               "dates. While he was casting the net he saw a child crying on the "
               "shore because he had lost his shoe. The fisherman gave him some "
               "dates and helped him search until they found the shoe among the "
               "rocks. That day the fisherman returned home with the largest catch "
               "of his life."),
    },
    {
        "id": "teacher",
        "propositions": 12,
        "ar": ("كانت معلمةٌ تسكن في بيتٍ صغير قرب المدرسة ولها حديقةٌ فيها شجرةُ "
               "زيتون. وفي ليلةٍ عاصفة انكسر غصنٌ كبير وسقط على سور الجيران. "
               "فاعتذرت المعلمة في الصباح وعرضت أن تُصلح السور بنفسها، لكن الجار "
               "رفض وقال إن الشجرة أطعمت أولاده سنواتٍ طويلة. وفي الربيع التالي "
               "زرعا معاً شجرةً جديدة."),
        "en": ("A teacher lived in a small house near the school with a garden that "
               "had an olive tree. On a stormy night a large branch broke and fell "
               "onto the neighbours' wall. In the morning the teacher apologised and "
               "offered to repair the wall herself, but the neighbour refused and "
               "said the tree had fed his children for many years. The following "
               "spring they planted a new tree together."),
    },
]

STORY_PROMPT = {
    "ar": "سأقرأ عليك قصة قصيرة مرة واحدة، ثم أعِد حكايتها بكلماتك.",
    "en": "I will read you a short story once, then please retell it in your own words.",
}


# ═══════════════════════════════════════════════════════════════ SURAHS ════
# Short, near-universally memorised surahs. Texts are stored WITHOUT diacritics
# because normalize_arabic() strips them anyway before scoring.
#
# WHY OFFER A CHOICE: the probe only works on material the participant actually
# has overlearned. Asking a person to recite something they never memorised
# measures unfamiliarity, not memory preservation. So the operator selects what
# the participant knows, and the app draws from that set.
#
# WHY LENGTH VARIES: scoring uses word error rate, which is normalised by the
# reference length, so surahs of different lengths remain broadly comparable.
# For strict longitudinal comparison the app reuses the SAME surah for the same
# participant unless the operator changes the selection.
SURAHS = [
    {"id": "fatiha", "name_ar": "الفاتحة", "name_en": "Al-Fatiha", "words": 29,
     "text": ("بسم الله الرحمن الرحيم الحمد لله رب العالمين الرحمن الرحيم "
              "مالك يوم الدين اياك نعبد واياك نستعين اهدنا الصراط المستقيم "
              "صراط الذين انعمت عليهم غير المغضوب عليهم ولا الضالين")},
    {"id": "ikhlas", "name_ar": "الإخلاص", "name_en": "Al-Ikhlas", "words": 15,
     "text": ("قل هو الله احد الله الصمد لم يلد ولم يولد "
              "ولم يكن له كفوا احد")},
    {"id": "falaq", "name_ar": "الفلق", "name_en": "Al-Falaq", "words": 23,
     "text": ("قل اعوذ برب الفلق من شر ما خلق ومن شر غاسق اذا وقب "
              "ومن شر النفاثات في العقد ومن شر حاسد اذا حسد")},
    {"id": "nas", "name_ar": "الناس", "name_en": "An-Nas", "words": 20,
     "text": ("قل اعوذ برب الناس ملك الناس اله الناس "
              "من شر الوسواس الخناس الذي يوسوس في صدور الناس من الجنة والناس")},
    {"id": "kawthar", "name_ar": "الكوثر", "name_en": "Al-Kawthar", "words": 10,
     "text": "انا اعطيناك الكوثر فصل لربك وانحر ان شانئك هو الابتر"},
    {"id": "asr", "name_ar": "العصر", "name_en": "Al-Asr", "words": 14,
     "text": ("والعصر ان الانسان لفي خسر الا الذين امنوا وعملوا الصالحات "
              "وتواصوا بالحق وتواصوا بالصبر")},
    {"id": "nasr", "name_ar": "النصر", "name_en": "An-Nasr", "words": 19,
     "text": ("اذا جاء نصر الله والفتح ورايت الناس يدخلون في دين الله افواجا "
              "فسبح بحمد ربك واستغفره انه كان توابا")},
    {"id": "kafirun", "name_ar": "الكافرون", "name_en": "Al-Kafirun", "words": 27,
     "text": ("قل يا ايها الكافرون لا اعبد ما تعبدون ولا انتم عابدون ما اعبد "
              "ولا انا عابد ما عبدتم ولا انتم عابدون ما اعبد لكم دينكم ولي دين")},
    {"id": "masad", "name_ar": "المسد", "name_en": "Al-Masad", "words": 20,
     "text": ("تبت يدا ابي لهب وتب ما اغنى عنه ماله وما كسب "
              "سيصلى نارا ذات لهب وامراته حمالة الحطب في جيدها حبل من مسد")},
    {"id": "fil", "name_ar": "الفيل", "name_en": "Al-Fil", "words": 23,
     "text": ("الم تر كيف فعل ربك باصحاب الفيل الم يجعل كيدهم في تضليل "
              "وارسل عليهم طيرا ابابيل ترميهم بحجارة من سجيل فجعلهم كعصف ماكول")},
    {"id": "quraysh", "name_ar": "قريش", "name_en": "Quraysh", "words": 17,
     "text": ("لايلاف قريش ايلافهم رحلة الشتاء والصيف فليعبدوا رب هذا البيت "
              "الذي اطعمهم من جوع وامنهم من خوف")},
    {"id": "maun", "name_ar": "الماعون", "name_en": "Al-Ma'un", "words": 25,
     "text": ("ارايت الذي يكذب بالدين فذلك الذي يدع اليتيم ولا يحض على طعام المسكين "
              "فويل للمصلين الذين هم عن صلاتهم ساهون الذين هم يراءون ويمنعون الماعون")},
]

BASMALA = "بسم الله الرحمن الرحيم"

RECITATION_PROMPT = {
    "ar": "اقرأ سورة {name} كما تحفظها.",
    "en": "Please recite Surat {name} as you know it.",
}


# ══════════════════════════════════════════════════════════ SELECTION ════
def _stable_index(seed_text: str, n: int) -> int:
    """Deterministic index from a seed string -- same input, same form."""
    h = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % max(n, 1)


def _rotate(seed_text: str, session_number: int, n: int) -> int:
    """
    Pick a stimulus that is stable per participant but ADVANCES each session.

    A pure hash of (participant, session) can collide, handing the same picture
    to consecutive visits -- which would reintroduce the practice effect the
    rotation exists to avoid. Combining a per-participant starting offset with
    the session number guarantees consecutive sessions differ whenever more
    than one form exists, while remaining fully reproducible.
    """
    if n <= 0:
        return 0
    start = _stable_index(seed_text, n)
    return (start + max(session_number, 1) - 1) % n


# The trained classifier learned from Cookie Theft descriptions, whose content
# the 'kitchen' scene mirrors. It is therefore the only stimulus for which a
# screening score can be reported.
#
# ─────────────────────────────────────────────────────────────────────────────
# WHAT "MIRRORS" DOES AND DOES NOT MEAN  (audited 2026-08-26)
# ─────────────────────────────────────────────────────────────────────────────
# It means: every one of the 23 information units in the frozen scoring key can
# be earned from this picture. That was CHECKED, not assumed, by rendering the
# artwork and reading the key unit by unit; it was FALSE on two units until the
# artwork was corrected on that date.
#
# It does NOT mean the two pictures are interchangeable. This scene contains
# salient content with no slot in the key -- a cat, a teapot, a stove, bread, a
# table, a palm tree -- listed above as `unscored_content`. Naming them earns
# nothing. The key cannot be extended to cover them, because the key defines the
# model's input and the model is frozen: adding a unit would change iu.* for the
# training transcripts and void the calibration.
#
# The consequence was measured against the frozen model
# (results/stimulus_inventory_probe.json, Analysis B, pre-registered):
# if the substituted picture costs a speaker as little as ONE information unit
# relative to the Cookie Theft, 13.1% of control recordings cross the screening
# threshold; two units, 26.7%. Whether it costs anything at all is UNKNOWN and
# cannot be known without Libyan data. What is known is that the margin is thin.
#
# This is the strongest single argument in the project for treating the
# reported probability as a screening prompt and not a result, and it is why
# the Libyan protocol carries a pre-specified stimulus-equivalence endpoint.
VALIDATED_PICTURE = "kitchen"


def pick_picture(participant_code: str = "", session_number: int = 1,
                 rotate: bool = False) -> dict:
    """
    Choose the picture for this session.

    DEFAULT IS NOT TO ROTATE, and the reason matters. Rotation exists to stop a
    participant memorising one scene across repeat visits. But the calibrated
    model was trained on descriptions of a single scene, so rotating away from
    it means the session gets no probability at all -- trading a real,
    validated result for protection against a problem that only arises on
    repeat testing.

    The validated scene is therefore used by default. Rotation is available
    (rotate=True) for repeat visits where practice effects outweigh the loss,
    and for Arabic sessions, which have no calibrated model to lose. Extending
    calibration to the other scenes is future work.
    """
    if not rotate:
        return get_picture(VALIDATED_PICTURE) or PICTURES[0]
    return PICTURES[_rotate(f"{participant_code}|pic", session_number, len(PICTURES))]


def pick_story(participant_code: str = "", session_number: int = 1) -> dict:
    return STORIES[_rotate(f"{participant_code}|story", session_number, len(STORIES))]


def pick_surah(known_ids: list[str] | None = None,
               participant_code: str = "", session_number: int = 1) -> dict | None:
    """
    Choose from the surahs the participant actually knows.

    An EMPTY list means the operator stated the participant knows none, so the
    recitation task is SKIPPED -- administering an unmemorised passage would
    measure unfamiliarity rather than memory preservation, which is the exact
    opposite of what the probe is for. `None` means simply unspecified, in
    which case the whole bank is eligible.

    NOTE ON REPEAT VISITS: unlike the picture and story, the surah does NOT
    rotate. Recitation accuracy is only comparable across sessions when the
    same passage is used, so the choice is fixed per participant.
    """
    if known_ids is not None and len(known_ids) == 0:
        return None
    pool = [s for s in SURAHS if not known_ids or s["id"] in known_ids]
    if not pool:
        return None
    return pool[_stable_index(f"{participant_code}|surah", len(pool))]


def get_surah(surah_id: str) -> dict | None:
    for s in SURAHS:
        if s["id"] == surah_id:
            return s
    return None


def get_picture(pic_id: str) -> dict | None:
    for p in PICTURES:
        if p["id"] == pic_id:
            return p
    return None


def surah_choices() -> list[dict]:
    """Lightweight list for the operator's 'which surahs do they know?' picker."""
    return [{"id": s["id"], "name_ar": s["name_ar"], "name_en": s["name_en"],
             "words": s["words"]} for s in SURAHS]


def best_surah_match(transcript: str, candidate_ids: list[str] | None = None):
    """
    Identify which surah was ACTUALLY recited.

    WHY THIS EXISTS
    The app asks for a specific surah, but an elderly participant may begin a
    different one they know better. Scoring that recitation against the
    assigned text would return a very low accuracy and look like severe memory
    impairment, when in fact the person recited a different passage perfectly.
    That is a false positive of the worst kind -- it would frighten a family
    over a task-administration slip.

    So the recitation is scored against every candidate surah and the best
    match is used, with a flag recording whether it differed from the assigned
    passage. This makes the probe robust to a very ordinary human deviation.

    Returns (surah_dict, fidelity_dict) or (None, {}).
    """
    from .linguistic_features_ar import recitation_fidelity
    pool = [s for s in SURAHS if not candidate_ids or s["id"] in candidate_ids]
    if not pool or not transcript.strip():
        return None, {}
    best, best_f = None, None
    for sur in pool:
        f = recitation_fidelity(transcript, sur["text"])
        if not f:
            continue
        if best_f is None or f["ar_recite_accuracy"] > best_f["ar_recite_accuracy"]:
            best, best_f = sur, f
    return best, (best_f or {})
