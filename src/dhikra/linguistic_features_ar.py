"""
linguistic_features_ar.py
-------------------------
Arabic linguistic feature extraction for ذِكرى.

This is NOT a translation of the English module. Arabic differs from English in
three ways that break a naive port, and handling them properly is the core
methodological contribution of the Arabic side of this project.

──────────────────────────────────────────────────────────────────────────────
PROBLEM 1 — Arabic is a PRO-DROP language
    In English, "empty speech" shows up as a high pronoun-to-noun ratio: the
    speaker says "he put it there" instead of "the boy put the jar on the
    shelf". In Arabic the subject pronoun is normally OMITTED entirely,
    because the verb conjugation already encodes person (تغسل = "she washes").
    Baseline pronoun realisation therefore differs so radically from English
    that the English ratio is NOT CROSS-LINGUISTICALLY COMPARABLE: an Arabic
    speaker's pronoun counts sit on a different scale for grammatical, not
    clinical, reasons. (Overt pronouns do exist in Arabic -- emphatic
    subjects, object/possessive clitics -- so the deficit could in principle
    surface in them; what is unsupported is reading the English ratio's
    scale onto Arabic speech.)

    ADAPTATION: the referential deficit is measured instead through
      (a) DEMONSTRATIVES  (هذا، هذه، ذلك، هناك) -- pointing instead of naming
      (b) VAGUE NOUNS     (شيء، حاجة، أشياء)    -- "the thing" instead of the noun
      (c) ATTACHED PRONOUN CLITICS with no named referent
      (d) standalone pronouns (still counted; emphatic use rises under load)
    combined into a REFERENTIAL DEFICIT INDEX -- the Arabic analogue of the
    English pronoun-to-noun ratio. STATUS: a literature-consistent HYPOTHESIS
    (deictic and vague-noun substitution under word-finding load is documented
    in other languages, including pro-drop ones), not a validated marker; the
    Libyan pilot is designed to test it on real patient speech.

PROBLEM 2 — Rich templatic morphology inflates type counts
    Arabic derives many surface forms from one root (كتب، كاتب، مكتوب، كتاب).
    Counting surface word types therefore OVERSTATES lexical richness relative
    to English and makes cross-language comparison invalid.

    ADAPTATION: lexical richness is computed over LEMMAS and ROOTS
    (via qalsadi lemmatiser + tashaphyne light stemmer) as well as surface
    forms, so all three are reported and the root-based measure is the one
    preferred for cross-language description. SAFER, NOT SAFE: root-TTR
    removes the templatic inflation, but no equivalence between Arabic
    root-TTR and English lemma-TTR has been established, so cross-language
    use remains descriptive, not calibrated.

PROBLEM 3 — Clitics fuse multiple words into one token
    وبكتابهم = و + ب + كتاب + هم  (and + with + book + their). Naive
    tokenisation counts this as ONE word, hiding a pronoun and two particles.

    ADAPTATION: rule-based clitic segmentation detects attached pronoun
    suffixes and proclitic particles before POS statistics are computed.

──────────────────────────────────────────────────────────────────────────────
BACKEND (all pure-Python, no external model downloads required)
    pyarabic    -- normalisation, diacritic handling, tokenisation
    qalsadi     -- lemmatisation + coarse POS (noun / verb / stopword)
    tashaphyne  -- light stemming and root extraction
    spacy.lang.ar -- tokenizer + stopword list

FEATURE KEYS are kept 1:1 with the English module wherever the construct is
genuinely equivalent, so the downstream model code stays language-agnostic.
Arabic-only features are prefixed 'ar_'.

>>> VALIDATION NOTE <<<
The closed-class word lists below (fillers, vague nouns, demonstratives) are
drafted from Modern Standard Arabic and need review against LIBYAN DIALECT
speech by a native speaker before the Arabic pilot. Items marked # LIBYAN? are
the ones most in need of that review.
"""
from __future__ import annotations
import math
import re
import numpy as np

import pyarabic.araby as araby
from tashaphyne.stemming import ArabicLightStemmer

_LEMMATIZER = None
_STEMMER = None


def _lemmatizer():
    global _LEMMATIZER
    if _LEMMATIZER is None:
        import qalsadi.lemmatizer as lem
        _LEMMATIZER = lem.Lemmatizer()
    return _LEMMATIZER


def _stemmer():
    global _STEMMER
    if _STEMMER is None:
        _STEMMER = ArabicLightStemmer()
    return _STEMMER


# ───────────────────────────────────────────────────── closed-class lists ────
# Standalone personal pronouns (MSA + common dialectal forms)
STANDALONE_PRONOUNS = {
    "هو", "هي", "هما", "هم", "هن",
    "أنا", "انا", "نحن", "احنا", "إحنا",            # LIBYAN? احنا
    "أنت", "انت", "أنتِ", "انتي", "أنتم", "انتم", "أنتن",
    "إياه", "اياه", "إياها", "اياها",
}

# Demonstratives / deictics -- "pointing" instead of naming
DEMONSTRATIVES = {
    "هذا", "هذه", "هذان", "هاتان", "هؤلاء",
    "ذلك", "تلك", "أولئك", "اولئك",
    "هنا", "هناك", "هنالك",
    "هاذا", "هاذي", "هاك", "هذي",                   # LIBYAN? colloquial variants
}

# Semantically empty / vague nouns -- "the thing", "the stuff"
VAGUE_NOUNS = {
    "شيء", "شي", "أشياء", "اشياء",
    "حاجة", "حاجات",                                # LIBYAN? very common in dialect
    "أمر", "امر", "أمور", "امور",
    "واحد", "وحدة",
}

# Filled pauses / discourse fillers
ARABIC_FILLERS = {
    "يعني", "اه", "اهه", "امم", "ام", "همم", "مم",
    "ايه", "إيه", "طيب", "يالله", "شن",             # LIBYAN? شن، شنو
    "شنو", "هاو", "اي",
}

# Attached pronoun suffixes (enclitic), longest-first for greedy matching
PRONOUN_SUFFIXES = ["هما", "كما", "هنّ", "هن", "هم", "كم", "كن",
                    "نا", "ها", "ه", "ك", "ي"]

# Proclitic particles that fuse to the front of a word
PROCLITICS = ["وبال", "فبال", "بال", "كال", "وال", "فال", "لل",
              "و", "ف", "ب", "ك", "ل", "س"]


# ───────────────────────────────────────────────────────────── utilities ────
def normalize_arabic(text: str) -> str:
    """
    Normalise Arabic text for analysis:
      * strip diacritics (tashkeel) and tatweel
      * unify alef variants (أ إ آ -> ا) and hamza forms
      * unify taa marbuta / haa and alef maqsura / yaa
    Recitation is fully diacritised while spontaneous speech usually is not,
    so normalisation is what makes the two tasks comparable.
    """
    t = araby.strip_tashkeel(text)
    t = araby.strip_tatweel(t)
    # Quranic orthographic marks that strip_tashkeel does NOT remove
    # (superscript alef, hamza marks, small high signs). Without this the
    # diacritised recitation text never matches plain spoken transcription.
    t = re.sub(r"[\u0670\u0653\u0654\u0655\u0656\u0657\u0658"
               r"\u06D6-\u06ED]", "", t)
    t = re.sub(r"[أإآٱ]", "ا", t)
    t = re.sub(r"ة", "ه", t)
    t = re.sub(r"ى", "ي", t)
    t = re.sub(r"ؤ", "و", t)
    t = re.sub(r"ئ", "ي", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def segment_clitics(token: str) -> dict:
    """
    Rule-based clitic segmentation.
    Returns {'stem':..., 'proclitic':..., 'pronoun_suffix':...}

    >>> KNOWN LIMITATION -- READ BEFORE USING <<<
    Surface-form rules cannot reliably distinguish a clitic from a root letter.
    كرسي ("chair") is wrongly segmented as ك + رسي because the initial kaf is
    part of the root, not the preposition "like". The same failure occurs with
    the available offline tools (tashaphyne's light stemmer and qalsadi both
    mis-analyse كرسي), because they are retrieval-oriented stemmers rather than
    full morphological analysers.

    Correct disambiguation requires a morphological database with a lexicon and
    context (CAMeL Tools / MADAMIRA / Farasa). Those need model downloads and
    are therefore listed as a deployment step for the local environment.

    CONSEQUENCE FOR THE FEATURE SET
    Clitic-derived counts are exposed as EXPERIMENTAL features only. They are
    deliberately EXCLUDED from the headline referential-deficit index, which is
    built exclusively from exact closed-class matches (standalone pronouns,
    demonstratives, vague nouns) that carry no segmentation ambiguity.

    Conservative by design: a suffix is only stripped if a plausible stem of at
    least 3 characters remains, to avoid mangling short words.
    """
    out = {"stem": token, "proclitic": None, "pronoun_suffix": None}
    w = token

    for p in PROCLITICS:
        if w.startswith(p) and len(w) - len(p) >= 3:
            out["proclitic"] = p
            w = w[len(p):]
            break

    for s in PRONOUN_SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 3:
            out["pronoun_suffix"] = s
            w = w[: -len(s)]
            break

    out["stem"] = w
    return out


def _safe_div(a, b):
    return a / b if b else float("nan")


# ─────────────────────────────────────────────────────────────── features ────
def extract_linguistic_features_ar(text: str) -> dict:
    """
    Extract Arabic linguistic features from a transcript.
    Feature keys match the English module where the construct is equivalent;
    Arabic-specific measures are prefixed 'ar_'.
    """
    norm = normalize_arabic(text)
    tokens = [t for t in araby.tokenize(norm) if araby.is_arabicword(t)]
    n = len(tokens)
    out: dict[str, float] = {}
    if n == 0:
        return {"word_count": 0}

    # ── productivity ──────────────────────────────────────────────────────
    # sentence segmentation: Arabic speech transcripts rarely carry full stops,
    # so utterance boundaries are taken from punctuation where present and the
    # coordinating particle و is NOT treated as a boundary (it is over-used).
    sents = [s for s in re.split(r"[.!?؟\n]+", norm) if s.strip()]
    n_sents = max(len(sents), 1)
    out["word_count"] = float(n)
    out["sentence_count"] = float(n_sents)
    out["mean_sentence_len"] = n / n_sents

    # ── lexical richness: surface, lemma AND root ─────────────────────────
    lem = _lemmatizer()
    try:
        tagged = lem.lemmatize_text(" ".join(tokens), return_pos=True)
    except Exception:
        tagged = [(t, "noun") for t in tokens]
    lemmas = [w for w, _ in tagged] or tokens
    pos_tags = [p for _, p in tagged]

    st = _stemmer()
    roots = []
    for t in tokens:
        try:
            st.light_stem(t)
            r = st.get_root() or st.get_stem() or t
        except Exception:
            r = t
        roots.append(r)

    surf_types, lem_types, root_types = set(tokens), set(lemmas), set(roots)
    out["type_token_ratio"] = len(surf_types) / n            # surface (inflated)
    out["ar_ttr_lemma"] = len(lem_types) / max(len(lemmas), 1)
    out["ar_ttr_root"] = len(root_types) / n     # cross-language SAFER (see PROBLEM 2)

    # moving-average TTR over roots (length-robust)
    w = 50
    if n >= w:
        out["mattr_50"] = float(np.mean(
            [len(set(roots[i:i + w])) / w for i in range(0, n - w + 1)]))
    else:
        out["mattr_50"] = out["ar_ttr_root"]

    V, N = len(root_types), n
    out["brunet_w"] = float(N ** (V ** -0.165))
    freqs = {r: roots.count(r) for r in root_types}
    v1 = sum(1 for r in root_types if freqs[r] == 1)
    out["honore_r"] = (float(100 * math.log(N) / (1 - v1 / V))
                       if V and v1 < V else float("nan"))

    # ── part of speech ────────────────────────────────────────────────────
    n_noun = pos_tags.count("noun")
    n_verb = pos_tags.count("verb")
    out["noun_rate"] = n_noun / n
    out["verb_rate"] = n_verb / n
    out["content_word_ratio"] = (n_noun + n_verb) / n

    # ── referential deficit (the Arabic analogue of pronoun-to-noun) ──────
    n_standalone_pron = sum(1 for t in tokens if t in STANDALONE_PRONOUNS)
    n_demonstrative = sum(1 for t in tokens if t in DEMONSTRATIVES)
    n_vague = sum(1 for t in tokens if t in VAGUE_NOUNS)
    n_clitic_pron = sum(1 for t in tokens
                        if segment_clitics(t)["pronoun_suffix"] is not None)

    out["pronoun_rate"] = n_standalone_pron / n
    out["ar_demonstrative_rate"] = n_demonstrative / n
    out["ar_vague_noun_rate"] = n_vague / n
    # EXPERIMENTAL: depends on rule-based segmentation (see segment_clitics
    # docstring). Reported for transparency, excluded from the composite below.
    out["ar_clitic_pronoun_rate_EXPERIMENTAL"] = n_clitic_pron / n

    # The composite: pointing/vague reference relative to actual naming.
    # Built ONLY from exact closed-class matches, which require no morphological
    # segmentation and are therefore free of the ambiguity documented above.
    referential = n_standalone_pron + n_demonstrative + n_vague
    out["ar_referential_deficit_index"] = _safe_div(referential, n_noun)
    # kept under the English key so downstream code is language-agnostic
    out["pronoun_to_noun_ratio"] = out["ar_referential_deficit_index"]

    # ── syntactic proxies ─────────────────────────────────────────────────
    # No dependency parser is available offline for Arabic, so complexity is
    # approximated by subordination/relativisation particles and clause length.
    SUBORD = {"الذي", "التي", "الذين", "اللي", "لان", "لأن", "حتي", "حتى",
              "عندما", "بينما", "اذا", "إذا", "كي", "لكي", "ان", "أن"}
    n_subord = sum(1 for t in tokens if t in SUBORD)
    out["subordination_rate"] = n_subord / n_sents
    out["ar_subordinator_rate"] = n_subord / n
    out["mean_dependency_distance"] = float("nan")   # unavailable offline
    out["mean_tree_depth"] = float("nan")            # unavailable offline

    # ── repetition ────────────────────────────────────────────────────────
    out["repeated_word_ratio"] = 1 - (len(surf_types) / n)
    out["ar_repeated_root_ratio"] = 1 - (len(root_types) / n)
    bigrams = list(zip(tokens, tokens[1:]))
    out["repeated_bigram_ratio"] = (1 - len(set(bigrams)) / len(bigrams)) if bigrams else 0.0
    out["immediate_repeat_count"] = float(
        sum(1 for i in range(1, n) if tokens[i] == tokens[i - 1]))

    # ── disfluency ────────────────────────────────────────────────────────
    n_fill = sum(1 for t in tokens if t in ARABIC_FILLERS)
    out["filler_count"] = float(n_fill)
    out["filler_rate"] = n_fill / n

    # ── idea density ──────────────────────────────────────────────────────
    # propositions ≈ verbs + subordinators + prepositional proclitics
    n_proclitic = sum(1 for t in tokens
                      if segment_clitics(t)["proclitic"] is not None)
    out["idea_density"] = 10 * (n_verb + n_subord + n_proclitic) / n

    return out


# ─────────────────────────────────────────── Quran recitation fidelity ────
# Surat Al-Fatiha, normalised reference. Used ONLY as a comparison string for
# measuring recitation accuracy -- the overlearned-memory probe.
BASMALA = "بسم الله الرحمن الرحيم"

FATIHA_REFERENCE = (
    "بسم الله الرحمن الرحيم "
    "الحمد لله رب العالمين "
    "الرحمن الرحيم "
    "مالك يوم الدين "
    "اياك نعبد واياك نستعين "
    "اهدنا الصراط المستقيم "
    "صراط الذين انعمت عليهم غير المغضوب عليهم ولا الضالين"
)


def _levenshtein(a: list[str], b: list[str]) -> int:
    """Word-level edit distance."""
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def recitation_fidelity(transcript: str,
                        reference: str = FATIHA_REFERENCE) -> dict:
    """
    Compare a recited passage against its canonical text.

    RATIONALE, AND ITS LIMITS
    The general principle that overlearned and procedural material is
    relatively spared in Alzheimer's compared with episodic memory is
    established. Whether that specifically extends to Qur'anic recitation, and
    whether recitation accuracy behaves as a diagnostic marker, has NOT been
    demonstrated. This is therefore an EXPLORATORY culturally-adapted
    elicitation task, not a validated biomarker.

    Its practical advantages are real and independent of that question: the
    text is identical for every participant, it requires no literacy, and it
    is familiar enough to reduce test anxiety in elderly Libyan speakers.

    MAJOR CONFOUNDERS, none of which this implementation controls for:
    how much of the Qur'an the person originally memorised; how often they
    currently recite; which surahs they know; recitation (tajweed)
    proficiency; religious and educational exposure; and age at memorisation.
    Any future validation must measure and adjust for these.

    BASMALA HANDLING
    Reciters commonly precede a short surah with "بسم الله الرحمن الرحيم"
    even when it is not part of that surah's text. Scoring is therefore done
    both with and without the leading basmala, and the better match is kept,
    so a correct recitation is never penalised for a conventional preface.

    Returns word error rate, accuracy, and the raw edit operations count.
    """
    hyp_full = normalize_arabic(transcript).split()
    ref = normalize_arabic(reference).split()
    if not ref:
        return {}

    basmala = normalize_arabic(BASMALA).split()
    candidates = [hyp_full]
    # if the reference does NOT already start with the basmala but the
    # recitation does, also try the recitation with that preface removed
    if hyp_full[:len(basmala)] == basmala and ref[:len(basmala)] != basmala:
        candidates.append(hyp_full[len(basmala):])
    # and the converse: reference has it, reciter omitted it
    if ref[:len(basmala)] == basmala and hyp_full[:len(basmala)] != basmala:
        candidates.append(basmala + hyp_full)

    best = min(candidates, key=lambda h: _levenshtein(ref, h))
    dist = _levenshtein(ref, best)
    return {
        "ar_recite_word_error_rate": dist / len(ref),
        "ar_recite_accuracy": max(0.0, 1 - dist / len(ref)),
        "ar_recite_edit_distance": float(dist),
        "ar_recite_len_ratio": len(best) / len(ref),
        "ar_recite_ref_words": float(len(ref)),
        "ar_recite_hyp_words": float(len(hyp_full)),
    }


def task_dissociation_index(spontaneous_feats: dict,
                            recitation_feats: dict) -> dict:
    """
    THE core clinical construct of the Arabic instrument.

    In early Alzheimer's, spontaneous speech degrades while overlearned
    recitation stays fluent. The CONTRAST between the two tasks is therefore
    more informative than either alone: a large gap (fluent recitation,
    impoverished spontaneous speech) is the expected early-AD signature,
    whereas decline in BOTH suggests a different or more advanced picture.

    Computed on measures available from both tasks (acoustic timing measures
    are supplied by the language-independent engine and passed in here).
    """
    out = {}
    for key in ("phonation_ratio", "pause_rate_per_min", "pause_mean_s",
                "est_articulation_rate_syls"):
        s, r = spontaneous_feats.get(key), recitation_feats.get(key)
        if s is not None and r is not None and not (
                isinstance(s, float) and math.isnan(s)):
            out[f"dissoc.{key}_gap"] = r - s
            out[f"dissoc.{key}_ratio"] = _safe_div(s, r)
    return out


if __name__ == "__main__":
    import sys, json
    print(json.dumps(extract_linguistic_features_ar(sys.stdin.read()),
                     indent=2, ensure_ascii=False))
