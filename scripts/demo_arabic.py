"""
demo_arabic.py
--------------
Demonstrates the three Arabic-specific contributions of ذِكرى:

  1. The REFERENTIAL DEFICIT INDEX -- the Arabic analogue of the English
     pronoun-to-noun ratio, redesigned because Arabic is pro-drop.
  2. ROOT-BASED lexical richness -- because Arabic's templatic morphology
     inflates surface type counts.
  3. QURAN RECITATION FIDELITY -- the overlearned-memory probe, and a
     standardised task that requires no literacy.

Run:  python scripts/demo_arabic.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dhikra.linguistic_features_ar import (extract_linguistic_features_ar,
                                           recitation_fidelity,
                                           task_dissociation_index,
                                           normalize_arabic)

# Illustrative transcripts written for demonstration. NOT patient data.
RICH = (
    "الأم واقفة أمام المغسلة تغسل الصحون والماء يفيض على الأرض. "
    "والولد الصغير يتسلق الكرسي الخشبي ليصل إلى برطمان الحلوى في الخزانة. "
    "وأخته الصغيرة تقف تحته ترفع يدها وتضحك وتطلب منه قطعة حلوى."
)
EMPTY = (
    "هذي واحدة تعمل شي هناك. وهو هناك فوق ياخذ الحاجة. "
    "يعني هذا وهذي. والشي يجي من هناك. اه هذا هو."
)

BANNER = "=" * 72


def section(title):
    print(f"\n{BANNER}\n{title}\n{BANNER}")


def main():
    section("1. REFERENTIAL DEFICIT INDEX  (Arabic analogue of pronoun/noun)")
    print("Arabic is PRO-DROP: subject pronouns are omitted because the verb")
    print("carries person, so the English pronoun/noun ratio does not transfer.")
    print("HYPOTHESIS (untested on patients): 'empty speech' surfaces instead")
    print("as POINTING and VAGUENESS (هذا / هناك / شيء / حاجة).\n")

    rich = extract_linguistic_features_ar(RICH)
    empty = extract_linguistic_features_ar(EMPTY)

    rows = [
        ("referential deficit index", "ar_referential_deficit_index", "higher = emptier"),
        ("demonstrative rate", "ar_demonstrative_rate", "pointing not naming"),
        ("vague noun rate", "ar_vague_noun_rate", "'the thing'"),
        ("noun rate", "noun_rate", "actual naming"),
        ("content word ratio", "content_word_ratio", "substance"),
        ("filler rate", "filler_rate", "يعني / اه"),
    ]
    print(f"  {'measure':30s} {'rich':>10s} {'empty':>10s}   note")
    print("  " + "-" * 68)
    for label, key, note in rows:
        print(f"  {label:30s} {rich[key]:>10.3f} {empty[key]:>10.3f}   {note}")

    section("2. ROOT-BASED LEXICAL RICHNESS  (templatic morphology)")
    print("كتب / كاتب / مكتوب / كتاب share one root. Counting SURFACE types")
    print("overstates Arabic richness and breaks cross-language comparison,")
    print("so richness is also computed over lemmas and roots.\n")
    for label, key in [("surface TTR", "type_token_ratio"),
                       ("lemma TTR", "ar_ttr_lemma"),
                       ("root TTR (comparison-safer)", "ar_ttr_root")]:
        print(f"  {label:30s} rich={rich[key]:.3f}   empty={empty[key]:.3f}")

    section("3. QURAN RECITATION FIDELITY  (overlearned-memory probe)")
    print("Overlearned material acquired in childhood and rehearsed for decades")
    print("is preserved far longer in Alzheimer's than spontaneous speech.")
    print("It is also IDENTICAL for every participant and needs NO literacy --")
    print("which makes it a standardised task suited to elderly Libyan speakers.\n")

    attempts = {
        "perfect recall": ("بسم الله الرحمن الرحيم الحمد لله رب العالمين الرحمن الرحيم "
                           "مالك يوم الدين اياك نعبد واياك نستعين اهدنا الصراط المستقيم "
                           "صراط الذين انعمت عليهم غير المغضوب عليهم ولا الضالين"),
        "minor slips": ("بسم الله الرحمن الرحيم الحمد لله رب العالمين الرحمن الرحيم "
                        "مالك يوم الدين اياك نعبد نستعين اهدنا الصراط المستقيم "
                        "صراط الذين انعمت عليهم غير المغضوب ولا الضالين"),
        "stops early": ("بسم الله الرحمن الرحيم الحمد لله رب العالمين الرحمن الرحيم "
                        "مالك يوم الدين اياك نعبد"),
        "fragmented": "بسم الله الرحمن الرحيم الحمد لله رب اه الرحمن اهدنا الصراط يعني الذين",
    }
    print(f"  {'attempt':22s} {'accuracy':>9s} {'WER':>7s} {'edits':>7s}")
    print("  " + "-" * 50)
    for name, txt in attempts.items():
        f = recitation_fidelity(txt)
        print(f"  {name:22s} {f['ar_recite_accuracy']:>9.3f} "
              f"{f['ar_recite_word_error_rate']:>7.3f} "
              f"{f['ar_recite_edit_distance']:>7.0f}")

    section("4. TASK DISSOCIATION  (the core clinical construct)")
    print("Early AD = spontaneous speech degrades WHILE recitation stays fluent.")
    print("The GAP between tasks is more informative than either alone.\n")

    profiles = {
        "early-AD profile": (
            {"phonation_ratio": 0.55, "pause_rate_per_min": 34.0,
             "pause_mean_s": 0.82, "est_articulation_rate_syls": 3.4},
            {"phonation_ratio": 0.80, "pause_rate_per_min": 14.0,
             "pause_mean_s": 0.30, "est_articulation_rate_syls": 4.6}),
        "control profile": (
            {"phonation_ratio": 0.74, "pause_rate_per_min": 20.0,
             "pause_mean_s": 0.42, "est_articulation_rate_syls": 4.4},
            {"phonation_ratio": 0.79, "pause_rate_per_min": 16.0,
             "pause_mean_s": 0.33, "est_articulation_rate_syls": 4.6}),
    }
    for name, (sp, rc) in profiles.items():
        d = task_dissociation_index(sp, rc)
        print(f"  {name}")
        print(f"     phonation gap     {d['dissoc.phonation_ratio_gap']:+.3f}")
        print(f"     pause-rate gap    {d['dissoc.pause_rate_per_min_gap']:+.1f}")
        print(f"     articulation gap  {d['dissoc.est_articulation_rate_syls_gap']:+.2f}")
    print("\n  -> a LARGE gap is the expected early-Alzheimer's signature.")

    section("HONEST LIMITATIONS")
    print("  * No labelled Arabic patient data yet -> this is an implemented")
    print("    METHOD, not a validated classifier. No Arabic accuracy is claimed.")
    print("  * The referential deficit index is a literature-consistent")
    print("    HYPOTHESIS the Libyan pilot is designed to test; the n=24 pilot")
    print("    evaluated the acoustic model, not this index.")
    print("  * Clitic segmentation is unreliable with offline tools and is")
    print("    EXCLUDED from the headline index (see segment_clitics docstring).")
    print("  * Closed-class word lists are drafted in MSA and need review")
    print("    against Libyan dialect by a native speaker.")
    print("  * No offline Arabic dependency parser -> syntactic complexity is")
    print("    approximated by subordinator rate, not parse-tree depth.")


if __name__ == "__main__":
    main()
