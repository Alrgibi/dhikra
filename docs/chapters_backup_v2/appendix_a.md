# Appendix A — The Deployed Feature List With Definitions

This appendix defines every one of the 64 features the frozen screening model consumes, in the order the model card records them (`results/summary/model_card.json`, `feature_order`). Each definition is read from the extraction code that computes it — `src/dhikra/linguistic_features.py`, `src/dhikra/information_units.py` and `src/dhikra/semantic_features.py` — not paraphrased from a description of it, so the tables are the scoring key itself. The features are grouped by the three families of the table in section 3.3: 24 lexical, syntactic and fluency measures computed from the parsed transcript, 31 information-content measures computed by matching the lemmatised transcript against the frozen unit inventory of the validated kitchen scene, and 9 discourse-semantic measures computed from distributional word vectors. Two qualifications of section 3.2 travel with the list: the 64 columns are 63 distinct quantities, because the information-unit proportion is the unit total divided by a constant, and the two filled-pause features are inert in the corpus transcripts (section 3.2.2). Nothing was removed, because any change to the frozen feature vector would void the external validation. The 53 acoustic measures feed the separate language-independent model of section 6.3.1 and are not part of this list; missing values in any column are median-imputed inside the model pipeline (section 4.5.1).

## A.1 Lexical Syntactic And Fluency Features


The 24 features of Table (A.1) are computed from an English dependency parse of the transcript (spaCy `en_core_web_sm`); words are the alphabetic tokens, and part-of-speech rates are proportions of those words.

**Table (A.1) : The 24 lexical, syntactic and fluency features**

| # | Feature | Sub-family | Definition |
|---|---|---|---|
| 1 | `ling.word_count` | Productivity | Number of alphabetic tokens in the transcript. |
| 2 | `ling.sentence_count` | Productivity | Number of sentences as segmented by the parser. |
| 3 | `ling.mean_sentence_len` | Productivity | Words per sentence (word count divided by sentence count). |
| 4 | `ling.type_token_ratio` | Lexical richness | Distinct word forms divided by total words. |
| 5 | `ling.mattr_50` | Lexical richness | Moving-average type-token ratio over a 50-word window (the plain ratio when the transcript is shorter than 50 words); length-robust. |
| 6 | `ling.brunet_w` | Lexical richness | Brunet's index, N to the power (V to the power −0.165), where N is the word count and V the number of distinct forms; lower values indicate richer vocabulary. |
| 7 | `ling.honore_r` | Lexical richness | Honoré's statistic, 100 log N divided by (1 − V1/V), where V1 is the number of words used exactly once; undefined when every form is a singleton. |
| 8 | `ling.pronoun_rate` | Part of speech | Proportion of words tagged as pronouns. |
| 9 | `ling.noun_rate` | Part of speech | Proportion of words tagged as nouns. |
| 10 | `ling.verb_rate` | Part of speech | Proportion of words tagged as verbs. |
| 11 | `ling.adj_rate` | Part of speech | Proportion of words tagged as adjectives. |
| 12 | `ling.adv_rate` | Part of speech | Proportion of words tagged as adverbs. |
| 13 | `ling.det_rate` | Part of speech | Proportion of words tagged as determiners. |
| 14 | `ling.pronoun_to_noun_ratio` | Part of speech | Pronouns divided by nouns and proper nouns — the empty-speech marker (a pronoun standing where a name would be); undefined when no noun occurs. |
| 15 | `ling.content_word_ratio` | Part of speech | Nouns, verbs, adjectives and adverbs as a proportion of all words. |
| 16 | `ling.mean_dependency_distance` | Syntactic complexity | Mean absolute token distance between each word and its syntactic head. |
| 17 | `ling.mean_tree_depth` | Syntactic complexity | Mean depth of the dependency tree across sentences. |
| 18 | `ling.subordination_rate` | Syntactic complexity | Subordinate clauses (adverbial, complement, open-complement, relative and adnominal clauses) per sentence. |
| 19 | `ling.repeated_word_ratio` | Repetition | One minus the type-token ratio: the share of word tokens that repeat an earlier form. |
| 20 | `ling.repeated_bigram_ratio` | Repetition | One minus the share of distinct word pairs among all adjacent word pairs. |
| 21 | `ling.filler_count` | Disfluency | Count of filled-pause tokens (um, uh, er, erm, hmm, mm, uhh, umm, ah). Inert in the corpus transcripts — section 3.2.2. |
| 22 | `ling.filler_rate` | Disfluency | Filled-pause tokens divided by word count. Inert in the corpus transcripts — section 3.2.2. |
| 23 | `ling.immediate_repeat_count` | Disfluency | Number of words identical to the word immediately before them (stutters and repairs). |
| 24 | `ling.idea_density` | Idea density | Propositional density approximated as ten times the count of verbs, adjectives, adverbs, adpositions and conjunctions divided by the word count (after Turner and Greene, 1977). |

## A.2 Information Content Features


The 31 features of Table (A.2) come from the information-unit scorer. Each of the 23 canonical units of the scene is defined by a set of accepted surface forms matched against the lemmatised transcript; an action additionally requires an agent cue and a verb cue in the same utterance, so an isolated noun does not trigger it. Matching is lexical, not semantic: a speaker who conveys a unit in unusual wording is missed, which is why the scorer is reported as a systematic approximation of manual clinical scoring and was checked against a human rater in section 5.5.1. Table (A.3) gives the accepted forms — the frozen key — for every unit.

**Table (A.2) : The eight information-content aggregates**

| # | Feature | Definition |
|---|---|---|
| 25 | `iu.subjects` | Number of the three people (boy, girl, woman) mentioned. |
| 26 | `iu.places` | Number of the two places (kitchen, exterior) mentioned. |
| 27 | `iu.objects` | Number of the twelve objects mentioned. |
| 28 | `iu.actions` | Number of the six actions conveyed. |
| 29 | `iu.total` | Sum of the four category counts — the number of the 23 canonical units produced. |
| 30 | `iu.proportion` | Unit total divided by 23; an exact function of the total (section 3.2). |
| 31 | `iu.per_100_words` | Unit total per hundred words — information efficiency. |
| 32 | `iu.action_object_ratio` | Actions divided by objects (objects floored at one). |

**Table (A.3) : The 23 unit-presence features and the accepted forms that earn each unit**

| # | Feature | Category | Accepted forms (agent cues; verb cues for actions) |
|---|---|---|---|
| 33 | `iu.has_boy` | person | boy, brother, child, kid, lad, son, youngster |
| 34 | `iu.has_girl` | person | child, daughter, girl, kid, sister |
| 35 | `iu.has_woman` | person | housewife, lady, mom, momma, mommy, mother, mum, wife, woman |
| 36 | `iu.has_kitchen` | place | kitchen |
| 37 | `iu.has_exterior` | place | driveway, garden, lawn, outdoors, outside, path, window, yard |
| 38 | `iu.has_cookie` | object | biscuit, biscuits, cookie, cookies |
| 39 | `iu.has_jar` | object | canister, container, cookiejar, jar |
| 40 | `iu.has_stool` | object | chair, ladder, seat, step, stepstool, stool |
| 41 | `iu.has_sink` | object | basin, sink |
| 42 | `iu.has_plate` | object | cup, cups, dish, dishes, plate, plates, saucer |
| 43 | `iu.has_dishcloth` | object | cloth, dishcloth, dishrag, napkin, rag, towel |
| 44 | `iu.has_water` | object | water |
| 45 | `iu.has_cupboard` | object | cabinet, cabinets, closet, cupboard, pantry, shelf, shelves |
| 46 | `iu.has_window` | object | window, windows |
| 47 | `iu.has_curtain` | object | blind, blinds, curtain, curtains, drape, drapes |
| 48 | `iu.has_counter` | object | bench, counter, countertop, worktop |
| 49 | `iu.has_faucet` | object | faucet, spigot, tap |
| 50 | `iu.has_boy_taking_cookie` | action | agent: boy, brother, child, he, kid, son; verb: get, getting, give, grab, grabbing, hand, help, pass, reach, reaching, steal, stealing, take, taking |
| 51 | `iu.has_stool_falling` | action | agent: boy, chair, he, ladder, seat, step, stool; verb: fall, falling, fell, lean, leaning, off, over, overturn, slip, slipping, tip, tipped, tipping, topple, toppling, wobble, wobbling |
| 52 | `iu.has_woman_drying_dishes` | action | agent: lady, mom, mother, mum, she, woman; verb: clean, cleaning, do, doing, dry, drying, wash, washing, wipe, wiping |
| 53 | `iu.has_water_overflowing` | action | agent: faucet, sink, tap, water; verb: drip, dripping, flood, flooding, flow, flowing, out, over, overflow, overflowed, overflowing, pour, pouring, run, running, spill, spilled, spilling |
| 54 | `iu.has_girl_reaching` | action | agent: daughter, girl, she, sister; verb: ask, asking, hand, laugh, laughing, look, looking, reach, reaching, receive, take, taking, up, wait, waiting, want, wanting |
| 55 | `iu.has_woman_unconcerned` | action | agent: lady, mom, mother, she, woman; verb: attention, care, concerned, daydream, daydreaming, ignore, ignoring, look, looking, notice, noticing, oblivious, pay, stare, staring, unaware |

## A.3 Discourse Semantic Features


The nine features of Table (A.4) are computed from the medium English vector model (spaCy `en_core_web_md`): the transcript is split into utterances at sentence punctuation (utterances shorter than three words are dropped), each utterance is represented by the vector model's mean token vector, similarities are cosine similarities, and the description's halves are split by utterance count; the features are left missing, not zero, when fewer than two utterances carry a vector. When the vector model is absent the platform substitutes training medians for these nine columns and says so on the report (section 4.5.1). These are distributional similarities from a general-purpose vector model, not a validated clinical instrument; their value was decided by the ablation of section 5.5, where the discourse-semantic family alone reaches 0.5772.

**Table (A.4) : The nine discourse-semantic features**

| # | Feature | Definition |
|---|---|---|
| 56 | `sem.global_coherence` | Mean cosine similarity between each utterance's vector and the centroid of all utterance vectors; falls when the description wanders off topic. |
| 57 | `sem.global_coherence_sd` | Standard deviation of the per-utterance global-coherence values. |
| 58 | `sem.min_coherence` | The lowest per-utterance global-coherence value. |
| 59 | `sem.local_coherence` | Mean cosine similarity between consecutive utterances; falls when successive sentences do not connect. |
| 60 | `sem.local_coherence_sd` | Standard deviation of the consecutive-utterance similarities. |
| 61 | `sem.loop_rate` | Proportion of consecutive-utterance pairs whose similarity exceeds 0.95 — saying the same thing again in different words. |
| 62 | `sem.progression` | One minus the similarity between the mean vectors of the first and second halves of the utterances (computed when at least four utterances exist); a speaker who moves through the scene produces halves that differ. |
| 63 | `sem.content_dispersion` | One minus the mean similarity of each content word (alphabetic, non-stop-word, with a vector; at least five required) to the centroid of the content-word vectors — an embedding-based analogue of lexical variety insensitive to inflection. |
| 64 | `sem.content_dispersion_sd` | Standard deviation of the content-word-to-centroid similarities. |
