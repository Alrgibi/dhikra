"""
semantic_features.py
--------------------
Discourse-level semantic measures using distributional word vectors.

WHAT GAP THIS FILLS
The linguistic module measures words and grammar within an utterance. The
information-unit module measures whether the required content was produced.
Neither captures how the discourse HOLDS TOGETHER across utterances.

In Alzheimer's disease, connected speech tends to lose global coherence:
successive utterances drift, the speaker returns to the same idea repeatedly,
and the description stops progressing through the scene. These are documented
features of AD discourse and are invisible to per-utterance measures.

MEASURES
  * Global coherence   -- mean similarity of each utterance to the whole
                          discourse. Falls when speech wanders off-topic.
  * Local coherence    -- mean similarity between CONSECUTIVE utterances.
                          Falls when successive sentences do not connect.
  * Coherence variance -- instability of the discourse thread.
  * Semantic loop rate -- proportion of utterance pairs that are near-identical
                          in meaning, i.e. saying the same thing again in
                          different words. Verbatim repetition is caught by the
                          repetition features; this catches SEMANTIC repetition,
                          which they miss.
  * Progression        -- similarity between the first and second half of the
                          description. A speaker who moves through the scene
                          produces two halves that differ; a speaker who circles
                          one region produces two halves that are alike.
  * Vector dispersion  -- how spread out the content words are in semantic
                          space, an embedding-based analogue of lexical variety
                          that is insensitive to inflection.

HONEST LIMITATION
These are distributional similarities from a general-purpose vector model, not
a validated clinical instrument. They are exploratory features whose value is
decided by the feature-importance analysis on real data, and they are reported
as such rather than asserted to be clinically meaningful.
"""
from __future__ import annotations
import re
import numpy as np

_NLP = None


def _nlp():
    global _NLP
    if _NLP is None:
        import spacy
        try:
            _NLP = spacy.load("en_core_web_md")       # has vectors
        except OSError:
            _NLP = None                                # gracefully unavailable
    return _NLP


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return np.nan
    return float(np.dot(a, b) / (na * nb))


def extract_semantic_features(text: str) -> dict:
    """
    Discourse coherence features. Returns an empty dict (not zeros) if the
    vector model is unavailable, so downstream imputation treats them as
    missing rather than as a real measurement of zero.
    """
    nlp = _nlp()
    if nlp is None or not text or not text.strip():
        return {}

    utts = [u.strip() for u in re.split(r"[.!?]+", text) if len(u.split()) >= 3]
    if len(utts) < 2:
        return {}

    docs = [nlp(u) for u in utts]
    vecs = [d.vector for d in docs if d.vector_norm > 0]
    if len(vecs) < 2:
        return {}
    vecs = np.array(vecs)

    out: dict[str, float] = {}
    centroid = vecs.mean(axis=0)

    # global coherence: each utterance vs the discourse as a whole
    gl = [_cos(v, centroid) for v in vecs]
    gl = [g for g in gl if not np.isnan(g)]
    if gl:
        out["sem.global_coherence"] = float(np.mean(gl))
        out["sem.global_coherence_sd"] = float(np.std(gl))
        out["sem.min_coherence"] = float(np.min(gl))

    # local coherence: consecutive utterance pairs
    loc = [_cos(vecs[i], vecs[i + 1]) for i in range(len(vecs) - 1)]
    loc = [l for l in loc if not np.isnan(l)]
    if loc:
        out["sem.local_coherence"] = float(np.mean(loc))
        out["sem.local_coherence_sd"] = float(np.std(loc))
        # semantic looping: saying the same thing again in different words
        out["sem.loop_rate"] = float(np.mean([l > 0.95 for l in loc]))

    # progression through the scene: first half vs second half
    if len(vecs) >= 4:
        h = len(vecs) // 2
        out["sem.progression"] = 1.0 - (_cos(vecs[:h].mean(axis=0),
                                             vecs[h:].mean(axis=0)) or 0.0)

    # dispersion of content words in semantic space
    toks = [t for d in docs for t in d
            if t.is_alpha and not t.is_stop and t.has_vector and t.vector_norm > 0]
    if len(toks) >= 5:
        tv = np.array([t.vector for t in toks])
        c = tv.mean(axis=0)
        sims = [_cos(v, c) for v in tv]
        sims = [s for s in sims if not np.isnan(s)]
        if sims:
            out["sem.content_dispersion"] = float(1.0 - np.mean(sims))
            out["sem.content_dispersion_sd"] = float(np.std(sims))
    return out
