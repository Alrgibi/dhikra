"""
fluency_features.py
-------------------
Scoring for the semantic verbal fluency task ("name as many animals as you
can in one minute").

WHY THIS TASK IS IN THE BATTERY
Semantic verbal fluency is one of the most widely used cognitive screening
tasks in clinical neuropsychology. It is sensitive to Alzheimer's disease
early, because retrieving category members depends on the semantic memory
network that degrades first. The animal category specifically is the standard
choice and is used across languages, which matters for an Arabic instrument.

WHAT IS SCORED (the established clinical protocol)
  * TOTAL correct    -- number of distinct valid category members produced
  * PERSEVERATIONS   -- repeating an item already said. Rises in AD because the
                        person loses track of what they have already produced.
  * INTRUSIONS       -- items outside the category. A marker of semantic
                        breakdown rather than simple slowness.
  * TIME COURSE      -- healthy speakers produce most items early and taper.
                        Reported as first-half vs second-half output.

>>> HONESTY BOUNDARY -- READ BEFORE INTERPRETING <<<
These scores are NOT part of the calibrated probability, and they cannot be,
because the Pitt corpus contains the fluency task for the DEMENTIA GROUP ONLY.
With no healthy controls for this task, no threshold could be learned from the
data used in this project.

Published population norms exist. The largest recent normative study reports
a mean of about 20 animals in 60 seconds (SD ~5) for cognitively unimpaired
adults aged 30-91 (n = 4,387; Karstens et al., "Mayo normative studies:
regression-based normative data for ages 30-91", J. Int. Neuropsychol. Soc.,
30(4):389-401, 2023, doi:10.1017/S1355617723000760), and the classic
stratified norms are Tombaugh, Kozak & Rees, Arch. Clin. Neuropsychol.,
14(2):167-177, 1999 (n = 1,300, stratified by age and education). BOTH
studies exist precisely because a single range is inadequate: age alone
explains ~15-23% of the variance in animal fluency, more than education does,
so scores below 18 are ordinary in the oldest and least-educated bands. No
validated Libyan-Arabic norm was available. The score is therefore
reported to the operator as clinical context with the published range shown
for orientation, and it is explicitly excluded from the screening decision.
Presenting it as a validated cut-off would be inventing precision that the
data in this project cannot support.
"""
from __future__ import annotations
import re

# A working animal lexicon. Deliberately broad rather than exhaustive: an
# unrecognised animal is counted as an intrusion, so under-coverage would
# understate a participant. The operator can correct the transcript, and the
# raw word list is always shown alongside the score for exactly this reason.
ANIMALS_EN = {
    "dog", "cat", "horse", "cow", "sheep", "goat", "pig", "chicken", "hen",
    "rooster", "duck", "goose", "turkey", "rabbit", "donkey", "mule", "camel",
    "lion", "tiger", "leopard", "cheetah", "elephant", "giraffe", "zebra",
    "hippo", "hippopotamus", "rhino", "rhinoceros", "monkey", "ape", "gorilla",
    "chimpanzee", "bear", "wolf", "fox", "deer", "moose", "elk", "bison",
    "buffalo", "antelope", "gazelle", "kangaroo", "koala", "panda", "sloth",
    "squirrel", "mouse", "rat", "hamster", "gerbil", "guinea", "mole", "bat",
    "hedgehog", "porcupine", "beaver", "otter", "badger", "raccoon", "skunk",
    "weasel", "ferret", "seal", "walrus", "whale", "dolphin", "shark", "fish",
    "salmon", "tuna", "trout", "cod", "carp", "eel", "octopus", "squid",
    "crab", "lobster", "shrimp", "jellyfish", "starfish", "turtle", "tortoise",
    "snake", "cobra", "python", "viper", "lizard", "gecko", "chameleon",
    "iguana", "crocodile", "alligator", "frog", "toad", "salamander",
    "bird", "eagle", "hawk", "falcon", "owl", "parrot", "pigeon", "dove",
    "sparrow", "crow", "raven", "seagull", "penguin", "ostrich", "flamingo",
    "peacock", "swan", "stork", "woodpecker", "hummingbird", "canary",
    "bee", "wasp", "ant", "butterfly", "moth", "spider", "scorpion", "fly",
    "mosquito", "beetle", "cockroach", "grasshopper", "cricket", "worm",
    "snail", "slug", "centipede", "llama", "alpaca", "yak", "reindeer",
    "hyena", "jackal", "meerkat", "lemur", "platypus", "armadillo", "puppy",
    "kitten", "calf", "lamb", "foal", "piglet",
}

ANIMALS_AR = {
    "كلب", "قط", "قطة", "حصان", "خيل", "بقرة", "بقر", "خروف", "غنم", "ماعز",
    "عنزة", "خنزير", "دجاجة", "دجاج", "ديك", "بطة", "بط", "وزة", "أرنب",
    "ارنب", "حمار", "بغل", "جمل", "ناقة", "أسد", "اسد", "نمر", "فهد",
    "فيل", "زرافة", "حمار وحشي", "وحيد القرن", "قرد", "غوريلا", "دب", "ذئب",
    "ثعلب", "غزال", "ظبي", "كنغر", "باندا", "سنجاب", "فأر", "فار", "جرذ",
    "خفاش", "قنفذ", "نيص", "قندس", "ثعبان", "أفعى", "افعى", "حية", "كوبرا",
    "سحلية", "حرباء", "تمساح", "ضفدع", "سلحفاة", "سمكة", "سمك", "قرش",
    "حوت", "دلفين", "أخطبوط", "سرطان", "جمبري", "طائر", "طير", "نسر", "صقر",
    "بومة", "ببغاء", "حمامة", "عصفور", "غراب", "نورس", "بطريق", "نعامة",
    "طاووس", "بجعة", "لقلق", "نحلة", "نحل", "دبور", "نملة", "نمل", "فراشة",
    "عنكبوت", "عقرب", "ذبابة", "بعوضة", "خنفساء", "صرصور", "جراد", "دودة",
    "حلزون", "ضبع", "ابن آوى", "وطواط", "حمل", "عجل", "مهر",
}

# Published orientation ranges for 60-second animal fluency in healthy adults.
# Reported to the operator as CONTEXT only -- see the module docstring.
NORM_NOTE = ("For orientation only: a large normative study of cognitively "
             "unimpaired adults aged 30-91 reports a mean of about 20 animals "
             "in 60 seconds (SD about 5) -- Karstens et al., J. Int. "
             "Neuropsychol. Soc. 30(4):389-401, 2023. Age is the dominant "
             "moderator (more than education), so a single range cannot be "
             "applied without knowing the person's age band; stratified norms "
             "are in Tombaugh, Kozak & Rees, Arch. Clin. Neuropsychol. "
             "14(2):167-177, 1999. No validated Libyan-Arabic norm exists, so "
             "this figure is context for the operator and does NOT affect the "
             "screening result.")

_TOKEN = re.compile(r"[\w\u0600-\u06FF']+")


def _normalise(word: str, lang: str) -> str:
    w = word.strip().lower()
    if lang == "ar":
        w = re.sub(r"[\u064B-\u0652\u0670]", "", w)
        w = re.sub(r"^(ال)", "", w)
        w = re.sub(r"[أإآٱ]", "ا", w).replace("ة", "ه").replace("ى", "ي")
    else:
        # crude de-pluralisation so 'dogs' matches 'dog'
        if w.endswith("s") and len(w) > 3 and w[:-1] in ANIMALS_EN:
            w = w[:-1]
    return w


def extract_fluency_features(text: str, lang: str = "en") -> dict:
    """
    Score a verbal fluency response.

    Returns counts plus the actual word lists, so the operator can always see
    what was and was not recognised rather than trusting an opaque number.
    """
    if not text or not text.strip():
        return {}

    lexicon = ANIMALS_AR if lang == "ar" else ANIMALS_EN
    raw = [t for t in _TOKEN.findall(text) if len(t) > 1]
    words = [_normalise(w, lang) for w in raw]

    seen, correct, perseverations, intrusions = set(), [], [], []
    for w in words:
        if w in lexicon:
            if w in seen:
                perseverations.append(w)
            else:
                seen.add(w)
                correct.append(w)
        else:
            intrusions.append(w)

    n = len(correct)
    out = {
        "flu.total_correct": float(n),
        "flu.perseverations": float(len(perseverations)),
        "flu.intrusions": float(len(intrusions)),
        "flu.unrecognised_words": float(len(intrusions)),
    }
    # time course: healthy speakers front-load, producing most items early
    if n >= 4:
        half = n // 2
        out["flu.first_half"] = float(half)
        out["flu.second_half"] = float(n - half)
        out["flu.taper_ratio"] = (n - half) / half if half else float("nan")

    out["_correct_words"] = correct
    out["_perseverated"] = perseverations
    out["_unrecognised"] = intrusions
    return out
