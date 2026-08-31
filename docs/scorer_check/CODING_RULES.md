# Information-unit scoring — coding rules

**You are validating an automated scorer. Score by MEANING, not by wording.**

You will read 20 anonymised picture descriptions. For each, mark every
information unit the speaker **conveyed**. There are 23 units: 3 people,
2 places, 12 objects, 6 actions.

You are **not** being shown how the software decides. That is deliberate. If you
tried to imitate it, the comparison would measure nothing. Score the way a
clinician marking a checklist would score, and the disagreements will show
exactly where the software's fixed word lists fall short of what a reader
credits.

---

## The 23 units

### People (3)
- **boy** — the BOY (a male child)
- **girl** — the GIRL (a female child)
- **woman** — the WOMAN (the adult female figure)

### Places (2)
- **kitchen** — the KITCHEN named as the setting
- **exterior** — the OUTSIDE — anything beyond the room: a garden, yard, path, the view out

### Objects (12)
- **cookie** — the COOKIES / biscuits themselves
- **jar** — the JAR or container the cookies are in
- **stool** — the STOOL / chair / step the boy is standing on
- **sink** — the SINK or basin
- **plate** — the DISHES — plates, cups, saucers
- **dishcloth** — the CLOTH / towel the woman is using
- **water** — the WATER
- **cupboard** — the CUPBOARD / cabinet / shelf
- **window** — the WINDOW
- **curtain** — the CURTAINS / drapes / blinds
- **counter** — the COUNTER / worktop
- **faucet** — the TAP / faucet

### Actions (6)
- **boy_taking_cookie** — the boy IS TAKING / reaching for / stealing a cookie
- **stool_falling** — the stool IS FALLING / tipping / about to go over
- **woman_drying_dishes** — the woman IS WASHING or DRYING dishes
- **water_overflowing** — the water IS OVERFLOWING / running over / spilling
- **girl_reaching** — the girl IS REACHING / asking / waiting for a cookie
- **woman_unconcerned** — the woman HAS NOT NOTICED — she is oblivious, distracted, paying no attention

---

## Consistency rules — read these before starting and apply them the same way every time

**1. Credit a unit once, however many times it is mentioned.** Every column is
0 or 1. A speaker who says "cookie" nine times scores 1 for cookie. Repetition
is measured elsewhere in the system and must not inflate this count.

**2. Paraphrase counts. Naming is not required.** "The thing you keep biscuits
in" is the JAR. "The lady" is the WOMAN. "It's coming down off the seat" is the
STOOL FALLING. Credit the content, not the vocabulary.

**3. Pronouns count ONLY when the referent is unambiguous from what the speaker
themselves said.** "She's washing them" credits WOMAN, DISHES and WOMAN DRYING
DISHES *if* the woman and the dishes have already been established. If the
speaker has said nothing but "she's doing it over there", credit nothing — you
cannot resolve it from their words alone, and neither could a listener. **Do not
use the picture to resolve a pronoun the speaker left open.** This is the rule
most likely to drift, so apply it strictly: if you had only the transcript and
not the picture, could you tell what "it" was?

**4. Partial or hedged mentions count if the content is there.** "Some kind of
a jar or something" is the JAR. "Water or maybe soap, going over" is WATER and
WATER OVERFLOWING. Uncertainty in the speaker is not absence of content.

**5. Wrong content does not count.** If a speaker says the boy is *sitting* on
the stool, do not credit STOOL FALLING. If they say the woman *has noticed*,
do not credit WOMAN UNCONCERNED. Score what was said, not what is in the
picture.

**6. Actions need the doer and the doing, from the same speaker.** "The stool"
alone is the STOOL object, not STOOL FALLING. "Falling" alone is neither. You
need both, though not necessarily in one sentence — rule 3 governs whether a
pronoun carries the doer across sentences.

**7. The OUTSIDE unit is for anything beyond the room** — a garden, a path, the
lawn, the view through the window. Note that mentioning the window may or may
not imply seeing outside; use rule 5 and score what was said.

**8. When genuinely torn, mark 0 and note the transcript number.** A list of
the cases you found ambiguous is as useful as the scores, because ambiguity for
you is very likely failure for the software.

---

## Worked example — check yourself against this before starting

> *"Well the mother is uh drying the dishes there. And the water's running over
> the sink onto the floor. The little boy is up on the stool getting into the
> cookie jar and it's tipping. The girl is reaching up. That's about it."*

| Unit | Score | Why |
|---|---|---|
| boy | 1 | "the little boy" |
| girl | 1 | "the girl" |
| woman | 1 | "the mother" |
| kitchen | 0 | never named — do not infer it from the scene |
| exterior | 0 | nothing beyond the room |
| cookie | 1 | "cookie jar" conveys the cookies |
| jar | 1 | "cookie jar" |
| stool | 1 | "on the stool" |
| sink | 1 | "over the sink" |
| plate | 1 | "the dishes" |
| dishcloth | 0 | not mentioned |
| water | 1 | "the water's" |
| cupboard | 0 | not mentioned |
| window | 0 | not mentioned |
| curtain | 0 | not mentioned |
| counter | 0 | not mentioned |
| faucet | 0 | not mentioned |
| boy_taking_cookie | 1 | "getting into the cookie jar" |
| stool_falling | 1 | "it's tipping" — rule 3: "it" resolves to the stool from the same sentence |
| woman_drying_dishes | 1 | "drying the dishes" |
| water_overflowing | 1 | "running over ... onto the floor" |
| girl_reaching | 1 | "reaching up" |
| woman_unconcerned | 0 | not stated — she is described as drying, not as unaware |
| **TOTAL** | **14** | |

Two judgements in that example are the ones most likely to separate you from
the software, so note how they were made: **kitchen scored 0** although the
scene is obviously a kitchen (rule 5 — score what was said), and
**woman_unconcerned scored 0** although she plainly has not noticed (rule 5
again — the speaker did not say it).

---

## When you are done

Save the sheet and send it back. The automated counts do not exist yet — they
are regenerated at comparison time from the recorded sample, so there is
nothing for you to see even accidentally.
