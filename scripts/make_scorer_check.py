"""
make_scorer_check.py -- materials for a blind human validation of the automated
information-unit scorer.

WHY. src/dhikra/information_units.py scores a description by lemma-matching
against fixed synonym lists. It is the most important feature family in the
system -- and after the single-feature analysis (THESIS_PLAN 5.1.1) a single
count from it nearly matches the whole model. Its implementation has never been
compared against a human. The module's own docstring already records this as an
untested assumption.

BLINDING. The generated materials contain NO model scores, NO diagnoses and NO
automated counts. The sample is drawn with a fixed seed and the selected file
ids are recorded, so the automated counts can be regenerated at scoring time
rather than existing anywhere in advance.

DESIGN NOTE THAT MATTERS. The human scores SEMANTICALLY -- "did the speaker
convey this?" -- and is not shown the synonym lists. Showing them would turn
the human into a slow regex and the agreement would measure nothing. Scoring by
meaning is what makes the disagreements informative: they localise exactly
where fixed lemma matching fails to capture what a reader would credit.

SAMPLING. Stratified across the range of automated counts, balanced across
classes, then shuffled so that presentation order encodes nothing. Stratifying
widens the spread of true values, which INFLATES the intraclass correlation
relative to a random sample -- so ICC is secondary here and Bland-Altman bias
and limits of agreement, which are not affected by the sampling spread, are
primary. That choice is recorded here so it cannot look like a post hoc
preference for whichever statistic came out better.
"""
import json, os, sys, glob
import numpy as np
import pandas as pd

REPO = os.path.join(os.path.expanduser("~"), "mnt", "Dhikra Cowork", "dhikra")
DB = os.path.join(os.path.expanduser("~"), "mnt", "DementiaBank", "pitt_cookie")
OUT = os.path.join(REPO, "docs", "scorer_check")
os.makedirs(OUT, exist_ok=True)
os.chdir(REPO)
sys.path.insert(0, "src")
N_PER_CLASS = 10
SEED = 20260824

from dhikra.chat_parser import parse_cha
from dhikra.information_units import SUBJECTS, PLACES, OBJECTS, ACTIONS, extract_information_units

UNITS = list(SUBJECTS) + list(PLACES) + list(OBJECTS) + list(ACTIONS)

PLAIN = {
 "boy": "the BOY (a male child)",
 "girl": "the GIRL (a female child)",
 "woman": "the WOMAN (the adult female figure)",
 "kitchen": "the KITCHEN named as the setting",
 "exterior": "the OUTSIDE — anything beyond the room: a garden, yard, path, the view out",
 "cookie": "the COOKIES / biscuits themselves",
 "jar": "the JAR or container the cookies are in",
 "stool": "the STOOL / chair / step the boy is standing on",
 "sink": "the SINK or basin",
 "plate": "the DISHES — plates, cups, saucers",
 "dishcloth": "the CLOTH / towel the woman is using",
 "water": "the WATER",
 "cupboard": "the CUPBOARD / cabinet / shelf",
 "window": "the WINDOW",
 "curtain": "the CURTAINS / drapes / blinds",
 "counter": "the COUNTER / worktop",
 "faucet": "the TAP / faucet",
 "boy_taking_cookie": "the boy IS TAKING / reaching for / stealing a cookie",
 "stool_falling": "the stool IS FALLING / tipping / about to go over",
 "woman_drying_dishes": "the woman IS WASHING or DRYING dishes",
 "water_overflowing": "the water IS OVERFLOWING / running over / spilling",
 "girl_reaching": "the girl IS REACHING / asking / waiting for a cookie",
 "woman_unconcerned": "the woman HAS NOT NOTICED — she is oblivious, distracted, paying no attention",
}

RULES = """# Information-unit scoring — coding rules

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
{people}

### Places (2)
{places}

### Objects (12)
{objects}

### Actions (6)
{actions}

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
"""


def build():
    files = sorted(glob.glob(os.path.join(DB, "**", "*.cha"), recursive=True))
    meta = pd.read_csv("results/pitt_cookie/meta.csv").set_index("file_id")
    rows = []
    for f in files:
        t = parse_cha(f)
        if t.file_id not in meta.index:
            continue
        txt = (t.clean_text or "").strip()
        if len(txt.split()) < 25:          # too short to score meaningfully
            continue
        iu = extract_information_units(txt)
        rows.append({"file_id": t.file_id, "text": txt,
                     "label": int(meta.loc[t.file_id, "label"]),
                     "auto_total": iu.get("iu.total", 0.0)})
    df = pd.DataFrame(rows)
    picked = []
    for lab in (0, 1):
        sub = df[df.label == lab].sort_values("auto_total").reset_index(drop=True)
        qs = np.linspace(0, len(sub) - 1, N_PER_CLASS).round().astype(int)
        picked.append(sub.iloc[np.unique(qs)])
    sel = pd.concat(picked).sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    sel["code"] = [f"T{i+1:02d}" for i in range(len(sel))]

    with open(os.path.join(OUT, "transcripts.md"), "w", encoding="utf-8") as fh:
        fh.write("# Transcripts for information-unit scoring\n\n"
                 "Anonymised and shuffled. Presentation order encodes nothing — not "
                 "diagnosis, not score, not length. Read `CODING_RULES.md` first.\n\n---\n")
        for _, r in sel.iterrows():
            fh.write(f"\n## {r.code}\n\n> {r.text}\n\n---\n")

    sheet = pd.DataFrame({"transcript": sel.code})
    for u in UNITS:
        sheet[u] = ""
    sheet["ambiguous_notes"] = ""
    sheet.to_csv(os.path.join(OUT, "scoring_sheet.csv"), index=False)

    def block(keys):
        return "\n".join(f"- **{k}** — {PLAIN[k]}" for k in keys)
    with open(os.path.join(OUT, "CODING_RULES.md"), "w", encoding="utf-8") as fh:
        fh.write(RULES.format(people=block(list(SUBJECTS)), places=block(list(PLACES)),
                              objects=block(list(OBJECTS)), actions=block(list(ACTIONS))))

    json.dump({"seed": SEED, "n": int(len(sel)), "units": UNITS,
               "file_ids_in_presentation_order": sel.file_id.tolist(),
               "note": "automated counts and labels are DELIBERATELY NOT STORED; they are "
                       "regenerated from these file ids at comparison time"},
              open(os.path.join(OUT, "sample_manifest.json"), "w"), indent=2)
    print(f"wrote {len(sel)} transcripts, {len(UNITS)} units -> docs/scorer_check/")
    print("files:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    build()
