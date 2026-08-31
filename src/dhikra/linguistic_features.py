"""
linguistic_features.py
----------------------
Language features from a TRANSCRIPT (English). These capture *what and how*
someone speaks -- the layer that degrades earliest in Alzheimer's.

Feature families
  * Productivity   : word count, sentence count, mean sentence length
  * Lexical richness: type-token ratio, moving-average TTR, Brunet's W,
                      Honore's statistic  (all drop in cognitive decline)
  * Part-of-speech : pronoun rate, noun rate, verb rate, PRONOUN-TO-NOUN ratio
                      (the "empty speech" marker: "he put it there" instead of
                      "the boy put the jar on the shelf"), content-word ratio
  * Syntactic      : mean dependency distance, parse-tree depth, subordination
  * Repetition     : repeated-word and repeated-bigram ratios
  * Disfluency     : filled pauses (um/uh), immediate word repeats (repairs)
  * Idea density   : propositions per 10 words (approximation after Turner & Greene, 1977, Tech. Rep. 63, Univ. of Colorado)

Arabic note: the SAME feature families apply, but the extractor needs an
Arabic NLP backend (e.g. CAMeL Tools / Stanza-ar) instead of spaCy-en. The
Arabic module mirrors this file's structure -- see linguistic_features_ar.py
(scaffold) -- which is why the method "transfers" while the tooling differs.
"""
from __future__ import annotations
import math
import numpy as np
import spacy

_NLP = None
FILLERS = {"um", "uh", "er", "erm", "hmm", "mm", "uhh", "umm", "ah"}


def _nlp():
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _tree_depth(token):
    """Depth of a token's subtree (recursion over dependency children)."""
    if not list(token.children):
        return 1
    return 1 + max(_tree_depth(c) for c in token.children)


def extract_linguistic_features(text: str) -> dict:
    doc = _nlp()(text)
    words = [t for t in doc if t.is_alpha]
    n = len(words)
    out = {}
    if n == 0:
        return {"word_count": 0}

    lower = [t.text.lower() for t in words]
    types = set(lower)

    # ---- productivity ----
    sents = list(doc.sents)
    out["word_count"] = n
    out["sentence_count"] = len(sents)
    out["mean_sentence_len"] = n / len(sents) if sents else float(n)

    # ---- lexical richness ----
    ttr = len(types) / n
    out["type_token_ratio"] = ttr
    # moving-average TTR (window 50) -- length-robust
    w = 50
    if n >= w:
        mattrs = [len(set(lower[i:i+w])) / w for i in range(0, n - w + 1)]
        out["mattr_50"] = float(np.mean(mattrs))
    else:
        out["mattr_50"] = ttr
    V, N = len(types), n
    out["brunet_w"] = float(N ** (V ** -0.165))            # lower = richer
    freqs = {t: lower.count(t) for t in types}
    v1 = sum(1 for t in types if freqs[t] == 1)             # hapax legomena
    out["honore_r"] = float(100 * math.log(N) / (1 - (v1 / V))) if V and v1 < V else float("nan")

    # ---- part of speech ----
    pos = [t.pos_ for t in words]
    def rate(tag):
        return pos.count(tag) / n
    out["pronoun_rate"] = rate("PRON")
    out["noun_rate"] = rate("NOUN")
    out["verb_rate"] = rate("VERB")
    out["adj_rate"] = rate("ADJ")
    out["adv_rate"] = rate("ADV")
    out["det_rate"] = rate("DET")
    n_noun = pos.count("NOUN") + pos.count("PROPN")
    out["pronoun_to_noun_ratio"] = pos.count("PRON") / n_noun if n_noun else float("nan")
    content = pos.count("NOUN") + pos.count("VERB") + pos.count("ADJ") + pos.count("ADV")
    out["content_word_ratio"] = content / n

    # ---- syntactic complexity ----
    dep_dist = [abs(t.i - t.head.i) for t in words if t.head != t]
    out["mean_dependency_distance"] = float(np.mean(dep_dist)) if dep_dist else 0.0
    depths = [_tree_depth(s.root) for s in sents] if sents else [0]
    out["mean_tree_depth"] = float(np.mean(depths))
    subord = sum(1 for t in doc if t.dep_ in {"advcl", "ccomp", "xcomp", "relcl", "acl"})
    out["subordination_rate"] = subord / len(sents) if sents else 0.0

    # ---- repetition ----
    out["repeated_word_ratio"] = 1 - (len(types) / n)
    bigrams = list(zip(lower, lower[1:]))
    out["repeated_bigram_ratio"] = (
        1 - len(set(bigrams)) / len(bigrams)) if bigrams else 0.0

    # ---- disfluency ----
    out["filler_count"] = sum(1 for t in lower if t in FILLERS)
    out["filler_rate"] = out["filler_count"] / n
    immediate = sum(1 for i in range(1, len(lower)) if lower[i] == lower[i-1])
    out["immediate_repeat_count"] = immediate      # "the the", stutters/repairs

    # ---- idea density (propositions / 10 words) ----
    prop_pos = {"VERB", "ADJ", "ADV", "ADP", "CCONJ", "SCONJ"}
    props = sum(1 for p in pos if p in prop_pos)
    out["idea_density"] = 10 * props / n
    return out


if __name__ == "__main__":
    import sys, json
    print(json.dumps(extract_linguistic_features(sys.stdin.read()), indent=2))
