"""
multitask_parser.py
-------------------
Splits a CHAT transcript that contains SEVERAL tasks into one record per task.

WHY THIS IS NEEDED
The Pitt corpus stores each task in its own file, so one file equals one task.
The Delaware corpus does not: a single file contains a whole session, with the
tasks separated by `@G:` gem markers -- Cookie Theft, the Cinderella story,
a sandwich-making description, and so on.

Parsing a Delaware file as one unit would blend a picture description, a
narrative and a procedural explanation into a single bag of words. Those tasks
place completely different demands on language, so the resulting measurements
would describe nothing in particular. Each task must be extracted separately.

WHY DELAWARE MATTERS SO MUCH
Until now, only the picture-description task could support a screening
decision, because Pitt recorded its other tasks from patients alone, leaving
no healthy comparison. Delaware ran the full protocol on BOTH groups -- 286 control
and 169 MCI SESSION FILES (455 .cha in total; the usable cookie subset is 292
participants, 439 recordings: 171 control / 121 MCI) -- so for the first time
the story and procedural tasks can be tested for whether they actually
distinguish impaired speakers, rather than merely tracking severity among
people already diagnosed.

It also shifts the clinical question. Pitt's impaired group was mostly
established dementia; Delaware's is MCI, the stage before dementia. Detecting
MCI is markedly harder, and markedly more useful.
"""
from __future__ import annotations

import re
import os
import glob

from .chat_parser import clean_utterance, _parse_id_line, ChatTranscript

_GEM = re.compile(r"^@G:\s*(.+)$")
_UTT = re.compile(r"^\*([A-Z]{3}):\s*(.*)$")
_ID = re.compile(r"^@ID:\s*(.+)$")

# Gem labels vary slightly between files ("Cookies", "Cinderlla_Intro").
# They are normalised so that near-identical labels are not treated as
# separate tasks, which would silently split a task's data in half.
TASK_ALIASES = {
    "cookie": "cookie", "cookies": "cookie",
    "cinderella": "cinderella", "cinderella_intro": "cinderella_intro",
    "cinderlla_intro": "cinderella_intro", "cinderella intro": "cinderella_intro",
    "cat": "cat", "rockwell": "rockwell",
    "sandwich": "sandwich", "sandwich_favorite": "sandwich_favorite",
    "favorite_sandwich": "sandwich_favorite",
    "tea": "tea", "window": "window",
}


def normalise_task(label: str) -> str:
    key = label.strip().lower().replace(" ", "_")
    return TASK_ALIASES.get(key, key)


def parse_multitask(path: str) -> dict[str, ChatTranscript]:
    """
    Parse one multi-task CHAT file into {task_name: ChatTranscript}.

    Utterances before the first gem marker belong to no task and are dropped:
    they are the investigator settling the participant in, and attributing that
    speech to a task would contaminate it.
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()

    merged: list[str] = []
    for ln in lines:
        if ln.startswith("\t") and merged:
            merged[-1] += " " + ln.lstrip("\t")
        else:
            merged.append(ln)

    base = ChatTranscript(file_id=os.path.basename(path).replace(".cha", ""))
    for ln in merged:
        m = _ID.match(ln)
        if m:
            _parse_id_line(m.group(1), base)

    out: dict[str, ChatTranscript] = {}
    current: str | None = None

    for ln in merged:
        g = _GEM.match(ln)
        if g:
            current = normalise_task(g.group(1))
            if current not in out:
                t = ChatTranscript(file_id=f"{base.file_id}|{current}")
                t.corpus, t.age, t.sex = base.corpus, base.age, base.sex
                t.group, t.mmse, t.education = base.group, base.mmse, base.education
                out[current] = t
            continue
        if current is None or ln.startswith("%") or ln.startswith("@"):
            continue
        u = _UTT.match(ln)
        if not u:
            continue
        speaker, payload = u.group(1), u.group(2)
        t = out[current]
        if speaker == "PAR":
            t.n_utterances += 1
            t.n_retracing += len(re.findall(r"\[/\]", payload))
            t.n_reformulation += len(re.findall(r"\[//\]", payload))
            t.n_filled_pauses += len(re.findall(r"&-\w+", payload))
            for p in re.findall(r"\((\.{1,3})\)", payload):
                if len(p) == 1:
                    t.n_short_pauses += 1
                elif len(p) == 2:
                    t.n_medium_pauses += 1
                else:
                    t.n_long_pauses += 1
            c = clean_utterance(payload)
            if c:
                t.participant_utterances.append(c)
        else:
            c = clean_utterance(payload)
            if c:
                t.investigator_utterances.append(c)

    for t in out.values():
        t.clean_text = " ".join(t.participant_utterances)
    return out


def collect_task(corpus_dir: str, task: str, min_words: int = 10) -> list[ChatTranscript]:
    """Every participant's transcript for one named task across a corpus."""
    rows = []
    for path in sorted(glob.glob(os.path.join(corpus_dir, "**", "*.cha"),
                                 recursive=True)):
        try:
            tasks = parse_multitask(path)
        except Exception:
            continue
        t = tasks.get(task)
        if t and len(t.clean_text.split()) >= min_words:
            rows.append(t)
    return rows


def available_tasks(corpus_dir: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in glob.glob(os.path.join(corpus_dir, "**", "*.cha"), recursive=True):
        try:
            for k, t in parse_multitask(path).items():
                if len(t.clean_text.split()) >= 10:
                    counts[k] = counts.get(k, 0) + 1
        except Exception:
            continue
    return dict(sorted(counts.items(), key=lambda x: -x[1]))
