#!/usr/bin/env python3
"""revise5.py -- Part 6 compression of meta-methodological prose in Chapters 5 and 6, the last two
'rather than assumed' instances, and one further 3.3 site in Chapter 4."""
from revlib import rep, write

rep("chapter3.md", "Whether that costs anything was checked rather than assumed:", "Whether that costs anything was checked:")
rep("appendix_d.md", "which is bounded rather than assumed away;", "which is bounded;")
rep("chapter4.md", "Every probability from the validated picture is delivered alongside", "Every screening score from the validated picture is delivered alongside")

# Chapter 5
rep("chapter5.md", "so the column is unusable, and this is said because education is the confound a reader will ask about first.",
    "so the column is unusable.")
rep("chapter5.md", "The prediction was wrong and is reported because it was made.", "The prediction was wrong.")
rep("chapter5.md", "That is stated as a positive claim about scope, not an apology — this is a screening test and not a monitoring test, and 0.286 is the number that establishes it.",
    "This is a screening test and not a monitoring test, and 0.286 is the number that establishes it.")
rep("chapter5.md", "The external row carries the exposure history of section 3.9, as everywhere.", "")
rep("chapter5.md", "This probe also cannot be externally validated, and that is the point of recording it: testing it on the spent corpus would be a second evaluation, making this the third occasion",
    "This probe also cannot be externally validated: testing it on the spent corpus would be a second evaluation, making this the third occasion")
rep("chapter5.md", "it was a selection artefact, and the sequence is recorded rather than deleted because the sequence is the point.",
    "it was a selection artefact, and the sequence is recorded.")
rep("chapter5.md", "That is a live demonstration, on this project's own work and in the same week its governance section was written, of what the rule is for — and it is worth more than the correction would have been.",
    "That is a demonstration, on this project's own work, of what the rule is for.")
rep("chapter5.md", "The grade stands and is reported first; what follows does not soften it — it says what kind of failure it is, which is the only useful question left.",
    "The grade stands; what follows says what kind of failure it is.")
rep("chapter5.md", "A threshold rule cannot fix this, and the test is reported because its result is counter-intuitive.",
    "A threshold rule cannot fix this, and the test that shows it is counter-intuitive.")
rep("chapter5.md", "The gradient is the expected one, and its implication is stated for what it means about early detection:",
    "The gradient is the expected one, and its implication for early detection is this:")
rep("chapter5.md", "One caveat must accompany the tight interval, because an examiner who notices it unaided will conclude nothing else was checked: it is an in-sample quantity",
    "One caveat accompanies the tight interval: it is an in-sample quantity")
rep("chapter5.md", "The strongest apparent counter-case is quoted because an examiner who knows it will raise it:", "The strongest apparent counter-case:")
rep("chapter5.md", "The same standard this thesis applies to itself — a group difference is not a usable decision — yields:",
    "The same standard applied throughout — a group difference is not a usable decision — yields:")
# Chapter 6
rep("chapter6.md", "That produces a reversal this thesis states rather than smooths:", "That produces a reversal:")

write("revise5: ")
