"""
chat_parser.py
--------------
Parser for CHAT-format (.cha) transcripts, the format used by TalkBank /
DementiaBank (Pitt Corpus).

WHY THIS MATTERS
DementiaBank ships human-verified transcripts alongside the audio. That means
the English pipeline needs NO speech recognition: it reads gold-standard text.
It also means the CHAT annotations give us *clinically labelled disfluencies*
that an ASR system would silently discard -- retracing, reformulation, filled
pauses, unintelligible speech and timed pauses are all explicitly marked.

WHAT IT EXTRACTS
  1. Metadata from the @ID header  : age, sex, diagnostic group, MMSE score
  2. Participant utterances (*PAR:) separated from investigator (*INV:)
  3. A CLEAN plain-text transcript for the linguistic engine
  4. CHAT-annotated disfluency counts, kept as extra features

CHAT constructs handled
  @ID: lang|corpus|code|age|sex|group|SES|role|education|custom|
  *PAR:  participant utterance     %mor:/%gra: dependent tiers (skipped)
  [/]    retracing (repeat)        [//]  reformulation      [///] rephrasing
  &-um &=laughs   filled pauses / paralinguistic events
  &+wor  phonological fragment     xxx / yyy  unintelligible
  (.) (..) (...)  short/medium/long pauses
  [: text]  replacement            [* err]  error code       @u @n  markers
  \x15...\x15  media time bullets

REFERENCE: CHAT manual, TalkBank (talkbank.org/0info/manuals/CHAT.pdf)
"""
from __future__ import annotations
import os
import re
from dataclasses import dataclass, field, asdict


# ------------------------------------------------------------- patterns ----
_ID_LINE = re.compile(r"^@ID:\s*(.+)$")
_UTT_LINE = re.compile(r"^\*([A-Z]{3}):\s*(.*)$")
_CONT_LINE = re.compile(r"^\t(.*)$")          # continuation of previous line
_DEP_TIER = re.compile(r"^%")                 # %mor:, %gra: etc -> skip
_TIME_BULLET = re.compile(r"\x15[^\x15]*\x15")
_SQUARE = re.compile(r"\[[^\[\]]*\]")         # [/] [//] [: x] [* err] [+ ...]
_ANGLE = re.compile(r"[<>]")
_AMP_EVENT = re.compile(r"&[=+\-]?\w+")       # &-um  &=laughs  &+wor
_PAUSE = re.compile(r"\((\.{1,3})\)")
_UNINTELLIGIBLE = re.compile(r"\b(?:xxx|yyy|www)\b")
_SPECIAL_CHARS = re.compile(r"[\u2308\u2309\u230a\u230b\u21d7\u2197\u2193\u21d8\u2192‡„]")
_MULTISPACE = re.compile(r"\s+")


@dataclass
class ChatTranscript:
    """One parsed .cha file."""
    file_id: str = ""
    # --- metadata from @ID ---
    corpus: str | None = None
    age: float | None = None
    sex: str | None = None
    group: str | None = None          # e.g. Control, ProbableAD, MCI
    mmse: float | None = None
    education: str | None = None
    # --- content ---
    participant_utterances: list[str] = field(default_factory=list)
    investigator_utterances: list[str] = field(default_factory=list)
    clean_text: str = ""
    # --- CHAT-annotated disfluency counts (participant only) ---
    n_retracing: int = 0              # [/]   word repeated verbatim
    n_reformulation: int = 0          # [//]  word/phrase corrected
    n_rephrasing: int = 0             # [///] whole utterance rephrased
    n_filled_pauses: int = 0          # &-um, &-uh
    n_paraling_events: int = 0        # &=laughs, &=coughs
    n_unintelligible: int = 0         # xxx / yyy
    n_short_pauses: int = 0           # (.)
    n_medium_pauses: int = 0          # (..)
    n_long_pauses: int = 0            # (...)
    n_utterances: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    def disfluency_features(self) -> dict:
        """CHAT-derived disfluency features, normalised per 100 words."""
        wc = max(len(self.clean_text.split()), 1)
        per100 = lambda x: 100.0 * x / wc
        return {
            "chat.retracing_per100": per100(self.n_retracing),
            "chat.reformulation_per100": per100(self.n_reformulation),
            "chat.rephrasing_per100": per100(self.n_rephrasing),
            "chat.filled_pause_per100": per100(self.n_filled_pauses),
            "chat.unintelligible_per100": per100(self.n_unintelligible),
            "chat.short_pause_per100": per100(self.n_short_pauses),
            "chat.medium_pause_per100": per100(self.n_medium_pauses),
            "chat.long_pause_per100": per100(self.n_long_pauses),
            "chat.utterance_count": float(self.n_utterances),
            "chat.mean_utterance_len": wc / max(self.n_utterances, 1),
        }


# ----------------------------------------------------------- helpers ----
def _parse_id_line(payload: str, t: ChatTranscript) -> None:
    """
    Parse the participant's @ID header.

    The generic CHAT specification is:
        @ID: language|corpus|code|age|sex|group|SES|role|education|custom|

    BUT the Pitt corpus (DementiaBank) documents its own use of those slots:
        @ID: language|corpus|PAR|age|sex|diagnosis||Participant|MMSEscore||
        e.g.  eng|Pitt|PAR|57;|male|ProbableAD||Participant|18||

    So in Pitt the slot that generic CHAT reserves for EDUCATION actually holds
    the MMSE score, written as a bare number rather than as 'MMSE=18'. Reading
    it generically would silently produce a null MMSE for every participant and
    file the cognitive score under 'education' -- quietly corrupting both the
    clinical covariate and any analysis that adjusts for schooling.

    The corpus name in slot 1 is therefore used to switch interpretation, and
    the 'MMSE=' form is still honoured for corpora that use it.
    """
    parts = [p.strip() for p in payload.split("|")]
    if len(parts) < 8 or parts[2] != "PAR":
        return                                     # only the participant's ID
    t.corpus = parts[1] or None
    # age like '66;11.' (years;months) or '66;' or '66'
    raw_age = parts[3].rstrip(".")
    if raw_age:
        if ";" in raw_age:
            yrs, _, mons = raw_age.partition(";")
            try:
                t.age = float(yrs) + (float(mons) / 12.0 if mons else 0.0)
            except ValueError:
                pass
        else:
            try:
                t.age = float(raw_age)
            except ValueError:
                pass
    t.sex = parts[4] or None
    t.group = parts[5] or None

    # 1. explicit 'MMSE=18' form, wherever it appears
    for p in parts[6:]:
        m = re.search(r"MMSE\s*=\s*([\d.]+)", p, re.I)
        if m:
            try:
                t.mmse = float(m.group(1))
            except ValueError:
                pass

    slot8 = parts[8] if len(parts) > 8 else ""
    is_pitt = (t.corpus or "").lower() == "pitt"

    if t.mmse is None and slot8 and is_pitt:
        # Pitt: slot 8 is the MMSE score, not education
        try:
            t.mmse = float(slot8)
        except ValueError:
            t.education = slot8
    elif slot8 and not is_pitt:
        t.education = slot8


def _count_annotations(raw: str, t: ChatTranscript) -> None:
    t.n_retracing += len(re.findall(r"\[/\]", raw))
    t.n_reformulation += len(re.findall(r"\[//\]", raw))
    t.n_rephrasing += len(re.findall(r"\[///\]", raw))
    t.n_filled_pauses += len(re.findall(r"&-\w+", raw))
    t.n_paraling_events += len(re.findall(r"&=\w+", raw))
    t.n_unintelligible += len(_UNINTELLIGIBLE.findall(raw))
    for p in _PAUSE.findall(raw):
        if len(p) == 1:
            t.n_short_pauses += 1
        elif len(p) == 2:
            t.n_medium_pauses += 1
        else:
            t.n_long_pauses += 1


def clean_utterance(raw: str) -> str:
    """Strip CHAT markup down to plain readable words."""
    s = raw
    s = _TIME_BULLET.sub(" ", s)
    s = _PAUSE.sub(" ", s)
    s = _AMP_EVENT.sub(" ", s)          # remove &-um, &=laughs, &+wor
    # replacements [: target] -> keep the target word
    s = re.sub(r"\[:\s*([^\]]+)\]", r"\1", s)
    prev = None
    while prev != s:                     # nested/stacked square brackets
        prev = s
        s = _SQUARE.sub(" ", s)
    s = _ANGLE.sub(" ", s)
    s = _UNINTELLIGIBLE.sub(" ", s)
    s = _SPECIAL_CHARS.sub(" ", s)
    s = s.replace("+...", " ").replace("+/.", " ").replace("+//.", " ")
    s = re.sub(r"[\+\^_@]", " ", s)
    s = _MULTISPACE.sub(" ", s).strip()
    return s


# -------------------------------------------------------------- public ----
def parse_cha(path: str) -> ChatTranscript:
    """Parse one .cha file into a ChatTranscript."""
    # os.path.basename, NOT path.split("/"): on Windows, glob returns
    # backslash paths, and split("/") kept the whole path as the file_id --
    # silently corrupting participant grouping (the anti-leakage mechanism)
    # and every merge keyed on file_id. Fixed 2026-08-20; byte-identical
    # output for the forward-slash paths all locked results were built with.
    t = ChatTranscript(file_id=os.path.basename(path).replace(".cha", ""))
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()

    # join tab-continuation lines onto their parent line first
    merged: list[str] = []
    for ln in lines:
        if ln.startswith("\t") and merged:
            merged[-1] += " " + ln.lstrip("\t")
        else:
            merged.append(ln)

    for ln in merged:
        m_id = _ID_LINE.match(ln)
        if m_id:
            _parse_id_line(m_id.group(1), t)
            continue
        if _DEP_TIER.match(ln) or ln.startswith("@"):
            continue
        m_utt = _UTT_LINE.match(ln)
        if not m_utt:
            continue
        speaker, payload = m_utt.group(1), m_utt.group(2)
        if speaker == "PAR":
            t.n_utterances += 1
            _count_annotations(payload, t)
            cleaned = clean_utterance(payload)
            if cleaned:
                t.participant_utterances.append(cleaned)
        else:
            cleaned = clean_utterance(payload)
            if cleaned:
                t.investigator_utterances.append(cleaned)

    t.clean_text = " ".join(t.participant_utterances)
    return t


# Diagnostic-group harmonisation -> binary label used for training.
# Diagnosis labels observed in the Pitt corpus. "Probable" and "Dementia"
# appear in a handful of files as abbreviated forms. "Other" is deliberately
# EXCLUDED -- it is not a known impairment category, and guessing would inject
# label noise.
#
# RECONSTRUCTED MAPPING (2026-08-20) -- NOT original code.
# The Lu external test set locked on 18 Aug 2026 was labelled by inline code
# that never reached this file. An @ID-header audit of all 54 Lu files
# (metadata only; see docs/RECONSTRUCTION.md) showed the locked counts
# (27 control / 26 impaired / 1 excluded) are reproduced exactly iff:
#   "Alzheimer's" -> impaired   (16 files, Dementia folder)
#   "Pick's"      -> impaired   (1 file, Dementia folder)
#   "Conrol"      -> control    (1 file, Control/F32.cha; typo in the corpus)
#   "Aphasia"     -> excluded   (1 file, Dementia/F16.cha; language disorder,
#                                not dementia -- matches the model-card note)
# and the header takes precedence over the folder (Dementia/F07.cha carries
# header group 'Control' and was evaluated as a control). Labels here have
# always come from the header, so precedence needs no code change.
IMPAIRED_GROUPS = {"probablead", "possiblead", "mci", "vascular", "memory",
                   "ad", "probable", "dementia",
                   # reconstructed additions (Lu header audit, 2026-08-20):
                   "alzheimer's", "pick's"}
CONTROL_GROUPS = {"control", "hc", "healthy",
                  # reconstructed addition (corpus typo, Lu Control/F32.cha):
                  "conrol"}


def group_to_label(group: str | None) -> int | None:
    """Map a CHAT diagnostic group to 1 = impaired, 0 = control, None = unknown."""
    if not group:
        return None
    g = group.strip().lower().replace(" ", "")
    if g in IMPAIRED_GROUPS:
        return 1
    if g in CONTROL_GROUPS:
        return 0
    return None


if __name__ == "__main__":
    import sys, json
    tr = parse_cha(sys.argv[1])
    d = tr.to_dict()
    d["clean_text"] = d["clean_text"][:300] + "..."
    print(json.dumps(d, indent=2))
