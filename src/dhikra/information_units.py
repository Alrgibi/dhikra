"""
information_units.py
--------------------
Content-information scoring for the Cookie Theft picture description task.

WHY THIS MATTERS
The measures in linguistic_features.py describe HOW someone speaks -- how
varied their vocabulary is, how complex their sentences are. They say nothing
about WHETHER THE PERSON ACTUALLY DESCRIBED THE PICTURE.

A speaker can produce fluent, grammatical, lexically rich speech that conveys
almost no information about the scene in front of them. That dissociation --
preserved form, degraded content -- is characteristic of Alzheimer's disease,
and it is invisible to purely structural measures.

Clinical practice therefore scores this task by counting INFORMATION UNITS:
the canonical people, objects, places and actions present in the picture.
This is the standard approach in the aphasia and dementia literature
(Yorkston & Beukelman 1980; Nicholas & Brookshire 1993; Croisile et al. 1996),
and reduced information-unit production is one of the most consistently
replicated findings in Alzheimer's picture description.

WHAT IS IMPLEMENTED
Each unit is defined by a set of accepted surface forms (synonyms and common
variants), matched against the lemmatised transcript. Actions additionally
require co-occurrence of an agent-ish and a verb-ish cue within the utterance,
so "the water" alone does not count as "water overflowing".

DESIGN NOTE ON HONESTY
Matching is lexical, not semantic: a speaker who conveys an action in unusual
wording may be missed. The measure is therefore a systematic APPROXIMATION of
manual clinical scoring, not a replacement for it, and is reported as such.
The same rule is applied identically to every transcript. That makes the
counting procedure uniform, but it does NOT by itself make any under-counting
non-differential: impaired speakers use vaguer and more unusual wording -- the
project's own hypothesis -- which is exactly a mechanism by which a fixed
keyword rule could miss more of their content than the controls'. This is
recorded as an ASSUMPTION, not a property, and it is untested.
"""
from __future__ import annotations
import re

# ── SUBJECTS ────────────────────────────────────────────────────────────────
SUBJECTS = {
    "boy": {"boy", "son", "brother", "lad", "kid", "child", "youngster"},
    "girl": {"girl", "daughter", "sister", "kid", "child"},
    "woman": {"woman", "mother", "mom", "mum", "lady", "mommy", "housewife",
              "wife", "momma"},
}

# ── PLACES ──────────────────────────────────────────────────────────────────
PLACES = {
    "kitchen": {"kitchen"},
    "exterior": {"outside", "yard", "garden", "outdoors", "lawn", "window",
                 "driveway", "path"},
}

# ── OBJECTS ─────────────────────────────────────────────────────────────────
OBJECTS = {
    "cookie": {"cookie", "cookies", "biscuit", "biscuits"},
    "jar": {"jar", "cookiejar", "container", "canister"},
    "stool": {"stool", "chair", "seat", "step", "stepstool", "ladder"},
    "sink": {"sink", "basin"},
    "plate": {"plate", "plates", "dish", "dishes", "cup", "cups", "saucer"},
    "dishcloth": {"dishcloth", "cloth", "towel", "rag", "napkin", "dishrag"},
    "water": {"water"},
    "cupboard": {"cupboard", "cabinet", "cabinets", "shelf", "shelves",
                 "pantry", "closet"},
    "window": {"window", "windows"},
    "curtain": {"curtain", "curtains", "drape", "drapes", "blind", "blinds"},
    "counter": {"counter", "countertop", "worktop", "bench"},
    "faucet": {"faucet", "tap", "spigot"},
}

# ── ACTIONS: (agent cues, verb cues) ────────────────────────────────────────
# An action counts only when an agent cue and a verb cue occur in the same
# utterance, so isolated nouns do not spuriously trigger it.
ACTIONS = {
    "boy_taking_cookie": (
        {"boy", "son", "brother", "kid", "child", "he"},
        {"take", "taking", "steal", "stealing", "reach", "reaching", "get",
         "getting", "grab", "grabbing", "hand", "help", "pass", "give"}),
    "stool_falling": (
        {"stool", "chair", "seat", "step", "ladder", "he", "boy"},
        {"fall", "falling", "fell", "tip", "tipping", "tipped", "topple",
         "toppling", "overturn", "wobble", "wobbling", "lean", "leaning",
         "slip", "slipping", "off", "over"}),
    "woman_drying_dishes": (
        {"woman", "mother", "mom", "mum", "lady", "she"},
        {"dry", "drying", "wash", "washing", "wipe", "wiping", "clean",
         "cleaning", "do", "doing"}),
    "water_overflowing": (
        {"water", "sink", "faucet", "tap"},
        {"overflow", "overflowing", "overflowed", "run", "running", "spill",
         "spilling", "spilled", "pour", "pouring", "flow", "flowing", "drip",
         "dripping", "flood", "flooding", "over", "out"}),
    "girl_reaching": (
        {"girl", "sister", "daughter", "she"},
        {"reach", "reaching", "ask", "asking", "want", "wanting", "hand",
         "take", "taking", "receive", "wait", "waiting", "look", "looking",
         "laugh", "laughing", "up"}),
    "woman_unconcerned": (
        {"woman", "mother", "mom", "lady", "she"},
        {"unaware", "oblivious", "notice", "noticing", "ignore", "ignoring",
         "daydream", "daydreaming", "stare", "staring", "look", "looking",
         "pay", "attention", "concerned", "care"}),
}

# ── SCENE INVENTORIES ───────────────────────────────────────────────────────
# Each stimulus needs its own content inventory: scoring a market description
# against a kitchen checklist would be meaningless. The three scenes were drawn
# to a matched specification (3 figures, 1 animal, ~15 objects, 8 actions, one
# unnoticed hazard), so their inventories are comparable in size and structure.
#
# IMPORTANT SCOPE NOTE: the CALIBRATED MODEL was trained on Cookie Theft
# descriptions, whose content the 'kitchen' scene mirrors. Descriptions of the
# market or courtyard scenes are scored for information content, but the
# trained probability does not transfer to them and is withheld.

MARKET_SUBJECTS = {
    "vendor": {"vendor", "seller", "shopkeeper", "merchant", "man", "grocer"},
    "woman": {"woman", "lady", "customer", "shopper", "mother"},
    "child": {"child", "girl", "boy", "kid", "daughter", "son"},
}
MARKET_PLACES = {
    "market": {"market", "shop", "stall", "souk", "store", "bazaar"},
    "street": {"street", "outside", "road", "pavement"},
}
MARKET_OBJECTS = {
    "scale": {"scale", "scales", "balance", "weighing"},
    "orange": {"orange", "oranges", "fruit"},
    "crate": {"crate", "box", "crates", "boxes"},
    "basket": {"basket", "bag"},
    "awning": {"awning", "canopy", "tent", "cover", "shade"},
    "table": {"table", "counter", "stand", "stall"},
    "money": {"money", "cash", "notes", "coins", "banknote"},
    "dates": {"dates", "date"},
    "sack": {"sack", "sacks", "bag", "bags"},
    "bicycle": {"bicycle", "bike"},
    "cat": {"cat", "kitten"},
    "greens": {"greens", "vegetables", "lettuce", "cabbage", "produce"},
}
MARKET_ACTIONS = {
    "vendor_weighing": ({"vendor", "seller", "man", "he"},
                        {"weigh", "weighing", "sell", "selling", "serve",
                         "serving", "measure", "measuring", "hand", "handing"}),
    "crate_falling": ({"crate", "box", "oranges", "fruit"},
                      {"fall", "falling", "fell", "tip", "tipping", "spill",
                       "spilling", "drop", "dropping", "roll", "rolling",
                       "off", "over"}),
    "woman_paying": ({"woman", "lady", "customer", "she"},
                     {"pay", "paying", "buy", "buying", "hold", "holding",
                      "give", "giving", "hand", "shop", "shopping"}),
    "child_reaching": ({"child", "girl", "boy", "kid"},
                       {"reach", "reaching", "want", "wanting", "point",
                        "pointing", "look", "looking", "ask", "asking", "up"}),
    "vendor_unaware": ({"vendor", "seller", "man", "he"},
                       {"unaware", "notice", "noticing", "oblivious", "see",
                        "seeing", "ignore", "ignoring", "busy"}),
}

COURTYARD_SUBJECTS = {
    "man": {"man", "father", "husband", "he"},
    "woman": {"woman", "mother", "wife", "lady"},
    "boy": {"boy", "child", "kid", "son"},
}
COURTYARD_PLACES = {
    "courtyard": {"courtyard", "yard", "garden", "outside", "patio", "backyard"},
    "house": {"house", "home", "wall", "door"},
}
COURTYARD_OBJECTS = {
    "hose": {"hose", "pipe", "hosepipe"},
    "laundry": {"laundry", "washing", "clothes", "clothing"},
    "line": {"line", "clothesline", "rope", "string"},
    "ball": {"ball", "football"},
    "window": {"window", "windows"},
    "tree": {"tree", "trees"},
    "bucket": {"bucket", "pail"},
    "flowers": {"flower", "flowers", "plant", "plants", "pot", "pots"},
    "basket": {"basket"},
    "bird": {"bird", "birds"},
    "door": {"door"},
    "water": {"water", "puddle", "pool"},
}
COURTYARD_ACTIONS = {
    "woman_hanging": ({"woman", "mother", "she"},
                      {"hang", "hanging", "wash", "washing", "put", "putting",
                       "dry", "drying", "peg", "pegging"}),
    "man_watering": ({"man", "father", "he"},
                     {"water", "watering", "hold", "holding", "tend",
                      "tending", "garden", "gardening", "plant", "planting"}),
    "hose_flooding": ({"hose", "water", "pipe"},
                      {"run", "running", "flood", "flooding", "spill",
                       "spilling", "pour", "pouring", "leak", "leaking",
                       "flow", "flowing", "left", "on"}),
    "boy_kicking": ({"boy", "child", "kid", "he"},
                    {"kick", "kicking", "play", "playing", "throw", "throwing",
                     "hit", "hitting", "ball"}),
    "ball_towards_window": ({"ball", "window"},
                            {"fly", "flying", "go", "going", "head", "heading",
                             "break", "breaking", "towards", "toward", "hit"}),
}

SCENES = {
    "kitchen": (SUBJECTS, PLACES, OBJECTS, ACTIONS),
    "market": (MARKET_SUBJECTS, MARKET_PLACES, MARKET_OBJECTS, MARKET_ACTIONS),
    "courtyard": (COURTYARD_SUBJECTS, COURTYARD_PLACES, COURTYARD_OBJECTS,
                  COURTYARD_ACTIONS),
}

ALL_UNITS = (list(SUBJECTS) + list(PLACES) + list(OBJECTS) + list(ACTIONS))
N_UNITS = len(ALL_UNITS)


def scene_unit_count(scene: str = "kitchen") -> int:
    su, pl, ob, ac = SCENES.get(scene, SCENES["kitchen"])
    return len(su) + len(pl) + len(ob) + len(ac)

_WORD = re.compile(r"[a-z']+")


def _lemma_set(text: str, nlp=None) -> tuple[set[str], list[set[str]]]:
    """Return (all lemmas, per-utterance lemma sets)."""
    utterances = [u for u in re.split(r"[.!?]+", text.lower()) if u.strip()]
    if nlp is not None:
        all_l, per = set(), []
        for u in utterances:
            doc = nlp(u)
            s = {t.lemma_.lower() for t in doc if t.is_alpha}
            s |= {t.text.lower() for t in doc if t.is_alpha}
            per.append(s)
            all_l |= s
        return all_l, per
    all_l, per = set(), []
    for u in utterances:
        s = set(_WORD.findall(u))
        # crude de-inflection so 'dishes'/'taking' still match
        s |= {w[:-1] for w in s if w.endswith("s") and len(w) > 3}
        s |= {w[:-3] for w in s if w.endswith("ing") and len(w) > 5}
        per.append(s)
        all_l |= s
    return all_l, per


def extract_information_units(text: str, nlp=None,
                              scene: str = "kitchen") -> dict:
    """
    Score a picture description for information content.

    `scene` selects which content inventory to use. Scoring a description
    against the wrong scene's checklist would produce meaningless counts, so
    the caller must pass the stimulus that was actually shown.
    """
    out: dict[str, float] = {}
    if not text or not text.strip():
        return {"iu.total": 0.0}
    SUB, PLC, OBJ, ACT = SCENES.get(scene, SCENES["kitchen"])
    n_units_scene = len(SUB) + len(PLC) + len(OBJ) + len(ACT)

    lemmas, per_utt = _lemma_set(text, nlp)
    n_words = max(len(_WORD.findall(text.lower())), 1)

    found: dict[str, int] = {}

    for name, forms in {**SUB, **PLC, **OBJ}.items():
        found[name] = int(bool(lemmas & forms))

    for name, (agents, verbs) in ACT.items():
        hit = 0
        for s in per_utt:
            if (s & agents) and (s & verbs):
                hit = 1
                break
        found[name] = hit

    n_subj = sum(found[k] for k in SUB)
    n_place = sum(found[k] for k in PLC)
    n_obj = sum(found[k] for k in OBJ)
    n_act = sum(found[k] for k in ACT)
    total = n_subj + n_place + n_obj + n_act

    out["iu.subjects"] = float(n_subj)
    out["iu.places"] = float(n_place)
    out["iu.objects"] = float(n_obj)
    out["iu.actions"] = float(n_act)
    out["iu.total"] = float(total)
    out["iu.proportion"] = total / n_units_scene
    # EFFICIENCY: how much information per word produced. Empty speech is
    # verbose but uninformative, so this separates fluent-but-vacuous output
    # from genuinely reduced output.
    out["iu.per_100_words"] = 100.0 * total / n_words
    out["iu.action_object_ratio"] = n_act / max(n_obj, 1)

    for k, v in found.items():
        out[f"iu.has_{k}"] = float(v)
    return out
