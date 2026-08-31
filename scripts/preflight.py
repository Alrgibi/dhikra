#!/usr/bin/env python3
"""
preflight.py -- the gate that runs before anything leaves this project.

Nothing here is clever. Every check exists because this project has already made
that exact mistake at least once, and each was caught by someone happening to
read the line rather than by anything mechanical:

  COUNTS      three stale count claims in one week -- "seven negative results"
              surviving in three passages, a figure-register heading disagreeing
              with its own table, and a figure row inserted into the WRONG
              register entirely.  -> scripts/check_counts.py
  SUPERSEDED  the reason docs/FIGURE_RECONCILIATION.md exists: the same quantity
              has had several values, and a retired one quoted in prose reads as
              a contradiction.  Non-citable figures are listed below with the
              value that replaced them.
  POINTERS    a thesis that cites results/reconstruction/foo.json had better
              contain results/reconstruction/foo.json.

USAGE
    python scripts/preflight.py              # gate: exit 1 on any failure
    python scripts/preflight.py --verbose    # list every check performed
    python scripts/preflight.py --list       # print the superseded-figure table

The exporters (make_summary_pdf.py, make_summary_pdf_ar.py) call this first and
refuse to run if it fails.  They accept --allow-unverified, which does NOT skip
the check: it runs it, prints every failure prominently, and continues.  A gate
with no override gets commented out; a gate that shouts is kept.
"""
import os, re, sys, glob, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "docs")

# value -> (what replaced it, why it is retired).  Only distinctive figures: a
# value that also occurs incidentally would generate noise and get ignored.
SUPERSEDED = {
    "0.636":   ("0.629",     "Delaware MCI AUC, pre-lock all_findings.json"),
    "0.849":   ("0.853",     "external AUC, Lu consulted -- contaminated"),
    "0.859":   ("0.853",     "external AUC, Lu consulted -- contaminated"),
    "0.5687":  ("0.5061",    "Delaware cookie, first-row-in-file-order label rule"),
    "0.7424":  ("0.7391",    "Arabic-equivalent AUC, pre-lock Lu-inclusive pool"),
    "0.6230":  ("0.5571",    "age-only AUC, pre-lock Lu-inclusive pool"),
    "0.997":   ("0.994",     "age-reconstruction R-squared, inline value superseded"),
    "0.4721":  ("0.471125",  "TRAINING_PRIOR, pre-lock 1040-recording pool"),
    "0.6455":  ("0.6379",     "five-task battery, retracted arm (label rule + dimensionality)"),
}
# A line carrying any of these is discussing the retired value on purpose.
EXEMPT = re.compile(
    r"supersed|non-citable|not citable|withdraw|retract|stale|previously|"
    r"earlier version|earlier draft|corrected|historical|contaminat|pre-lock|"
    r"reconcil|~~|CORRECTION|RETRACTED", re.I)
# Files whose whole job is to discuss retired values.
# Documents whose whole job is to catalogue discrepancies between figures. They
# quote retired and wrong values ON PURPOSE, so scanning them for retired values
# reports the document's own contents back as errors.
EXEMPT_FILES = {"FIGURE_RECONCILIATION.md", "DEVELOPMENT_NARRATIVE.md",
                "LU_EXPOSURE_TIMELINE.md", "RECONSTRUCTION.md",
                "PRE_WRITING_AUDIT.md", "ASSESSMENT_INDEPENDENT.md"}

def docfiles():
    # docs/chapters/*.md are INCLUDED. Until 26 August 2026 they were not, which
    # meant the chapters -- the only documents that are actually submitted -- were
    # the one class of file no gate scanned. Every check below now covers them:
    # a retired figure quoted in Chapter 5, a pointer to a result file that is not
    # there, an interval that disagrees with its source. That is the cheap half of
    # cross-chapter consistency; check_chapters() below is the other half.
    fs = sorted(glob.glob(os.path.join(DOCS, "*.md")))
    fs += sorted(glob.glob(os.path.join(DOCS, "chapters", "*.md")))
    root_plan = os.path.join(ROOT, "THESIS_PLAN.md")
    if os.path.exists(root_plan): fs.append(root_plan)
    return fs


def chapterfiles():
    return sorted(glob.glob(os.path.join(DOCS, "chapters", "chapter*.md"))) + \
           sorted(glob.glob(os.path.join(DOCS, "chapters", "appendix*.md")))

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

# A result file that carries a `_note` beside a value is telling a reader that the
# value does not mean what it appears to mean. On 22 August the calibration block
# of CURRENT_development_stats.json acquired exactly such a note -- the stored
# slope is an L2-penalised fit and must not be cited -- and NOTHING READ IT.
# make_numbers_doc.py took the numeric field, NUMBERS.md published it as the
# authoritative value, and Chapter 5 was four days from quoting the one number its
# own source forbade. Each note below has been read and acted on; a NEW note fails
# this gate until someone reads it too.
ACKNOWLEDGED_NOTES = {
    # READ 2026-08-26: the stored slope/intercept are an L2-penalised fit and
    # must not be cited. make_numbers_doc.py now overrides them explicitly.
    ("results/summary/CURRENT_development_stats.json", "calibration"),
    # READ 2026-08-26: all three are EXPLANATORY -- they say what a quantity
    # means, not that it is wrong. No published value is affected. They are
    # listed rather than exempted by pattern, so that a note which is NOT
    # explanatory cannot hide among them.
    ("results/reconstruction/relative_threshold_rules.json", "roc_ceilings"),
    ("results/reconstruction/relative_threshold_rules.json", "variant_e_control_referenced"),
    ("results/reconstruction/relative_threshold_rules.json", "bootstrap_on_lu"),
}


def check_notes(verbose):
    print("\n── SOURCE NOTES ──────────────────────────────────")
    import json
    found, unread = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "**", "*.json"),
                              recursive=True)):
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue

        def walk(o, block):
            if not isinstance(o, dict):
                return
            for k, v in o.items():
                if k.startswith("_note") and isinstance(v, str):
                    found.append((rel, block, v))
                    if (rel, block) not in ACKNOWLEDGED_NOTES:
                        unread.append((rel, block, v))
                walk(v, k)
        walk(d, "")
    print("  %d value(s) carry a note in their source file" % len(found))
    for rel, block, v in unread:
        print("  ! %s [%s] carries an UNACKNOWLEDGED note:" % (rel, block))
        print("      %s" % (v[:160] + ("..." if len(v) > 160 else "")))
    if found and not unread:
        print("  every note has been read and acted on")
    return not unread


def check_format(verbose):
    """
    Mechanical format compliance, checked against the faculty specification as
    read from the PDF on 26 August 2026 -- not from a transcription of it.

    WHY THIS IS A GATE AND NOT A CHECKLIST. Session A spent part of its budget
    DISCOVERING these rules, then applying them by hand to one chapter. Five
    chapters remain. A rule that a human has to remember five more times is a rule
    that will be broken at least once, and every break costs the assembly session
    a fix across six files. The rules below are the ones a machine can check;
    the rest -- fonts, spacing, indices, page numbering -- belong to assembly.

    ONE RULE HERE IS SUBTLER THAN IT LOOKS. The specification forbids ": - --"
    in SECTION HEADINGS, and REQUIRES a colon in figure and table CAPTIONS: its
    own examples are "Figure (3 . 4) : Analog Signal" and
    "Table (2 . 1) : True Table". Applying the heading rule to captions would
    strip the colon the specification asks for.
    """
    print("\n── FORMAT ────────────────────────────────────────────")
    chs = chapterfiles()
    if not chs:
        print("  no chapters written yet; nothing to check")
        return True
    # CASE-INSENSITIVE since 28 Aug 2026, and that is the whole point of this
    # comment. From 26 to 28 August this pattern was case-SENSITIVE, so it could
    # not see "We", "Our", "You" or "Us" -- a sentence-initial pronoun, which is
    # the single most likely form of the violation. Six chapter files passed a
    # pronoun gate that was blind to the commonest case. Re-scanned when the bug
    # was found: the only case-insensitive hits in the whole thesis were "US" in
    # a reference title, so the exposure was zero and the writing discipline had
    # held on its own. The gate had not.
    #
    # "US" in capitals is the country or an acronym, never the pronoun -- a real
    # "us" is lower case except sentence-initially, and "Us" opening a sentence
    # does not occur in academic prose. It is excluded by case, not by a word
    # list, so no legitimate pronoun can hide behind the exception.
    PRON = re.compile(r"(?<![A-Za-z])(we|our|ours|us|you|your|yours|I)(?![A-Za-z])",
                      re.IGNORECASE)
    bad = []
    for f in chs:
        name = os.path.basename(f)
        lines = read(f).splitlines()
        prev_head = False
        for i, ln in enumerate(lines, 1):
            t = ln.strip()
            quoted = t.startswith(">")
            if not quoted:
                # Appendix I (added 28 Aug 2026): the letter I in "Appendix I",
                # in lettered headings ("I.1") and in caption labels ("(I.1)") is
                # a label, not a pronoun. Strip those tokens before the scan.
                cleaned = re.sub(r"`[^`]*`", "", ln)
                cleaned = re.sub(r"\bAppendix I\b", "Appendix", cleaned)
                cleaned = re.sub(r"\bI(?=\.\d)", "", cleaned)
                for m in PRON.finditer(cleaned):
                    if m.group(1) == "US":          # the country, not the pronoun
                        continue
                    bad.append((name, i, "personal pronoun %r" % m.group(1)))
                    break
            if "Fig." in ln:
                bad.append((name, i, "uses 'Fig.'; the project uses 'Figure'"))
            h = re.match(r"^(#{2,4})\s+(.*)$", t)
            if h:
                title = h.group(2)
                # An appendix heading is lettered, not numbered -- "G.2", "H.1" --
                # and that is correct. Accept either form; reject only a heading
                # that carries no label at all.
                if not re.match(r"^(?:[A-J]|\d+)\.\d+", title):
                    bad.append((name, i, "unnumbered heading: %r" % title[:40]))
                body = re.sub(r"^(?:[A-J]|\d+)(\.\d+)*\s*", "", title)
                for ch in (":", " - ", "--"):
                    if ch in body:
                        bad.append((name, i, "heading contains %r" % ch.strip()))
                        break
                for w in re.findall(r"[A-Za-z][A-Za-z'\u2019-]*", body):
                    if "." in w or "_" in w:
                        continue
                    if w[0].islower():
                        bad.append((name, i,
                                    "heading not Title Case at %r" % w)); break
                if prev_head:
                    bad.append((name, i, "two headings with no text between"))
                prev_head = True
            elif t:
                if prev_head and re.match(r"^([-*+]\s|\d+\.\s|\|)", t):
                    bad.append((name, i, "list or table immediately after a heading"))
                prev_head = False
        for m in re.finditer(r"\*\*(Figure|Table) \(\d+\.\d+\)(.{0,3})", read(f)):
            if ":" not in m.group(2):
                bad.append((name, 0, "%s caption missing its colon" % m.group(1)))
    print("  %d chapter file(s) scanned against the specification" % len(chs))
    for n, i, msg in bad[:40]:
        print("  ! %s%s: %s" % (n, (":%d" % i) if i else "", msg))
    if len(bad) > 40:
        print("  ... and %d more" % (len(bad) - 40))
    if not bad:
        print("  headings numbered and Title Case, no pronouns, captions well formed")
    return not bad


def check_chapters(verbose):
    """
    Cross-chapter consistency: the class of defect that six independently written
    chapters produce and that no single chapter can see.

    THE PRINCIPLE IS THE PROJECT'S OWN (THESIS_PLAN 6.1 item 9). A component
    whose contract is to return a value cannot report that the value stopped
    meaning what it meant; something outside it must. A session writing Chapter 5
    cannot know that Chapter 3 numbered a table differently, or that its own
    Figure 5.7 has no caption, or that it cited a section that does not exist.
    Nothing inside that session will raise an error. So this runs outside them.

    Three checks, all mechanical:

      NUMBERING   figure and table captions must run 1..n within a chapter with
                  no gaps and no repeats. A gap means a caption was cut and its
                  siblings were not renumbered -- which is exactly what happened
                  to Chapter 3 on 26 August when two tables were moved to an
                  appendix.
      RESOLUTION  every "Figure (n.m)" or "Table (n.m)" mentioned in prose must
                  have a caption in that chapter, and every caption must be
                  mentioned before it appears. The faculty specification requires
                  the second; the first is what stops a dangling reference.
      SECTIONS    every section cross-reference must resolve against the union of
                  THESIS_PLAN's sections and those defined in written chapters.
                  A chapter may legitimately renumber its own sections; it may
                  not point at one that exists nowhere.
    """
    print("\n── CHAPTER CONSISTENCY ─────────────────────────")
    chs = chapterfiles()
    if not chs:
        print("  no chapters written yet; nothing to check")
        return True

    # known section numbers: the plan's, plus every chapter's own headings
    known = set()
    plan = read(os.path.join(DOCS, "THESIS_PLAN.md"))
    known |= set(re.findall(r"\*\*(\d+\.\d+(?:\.\d+)?)\s", plan))
    known |= set(re.findall(r"^#{2,4}\s+(\d+\.\d+(?:\.\d+)?)\s", plan, re.M))
    known |= set(re.findall(r"^\u00a7(\d+\.\d+(?:\.\d+)?)", plan, re.M))
    for f in chs:
        known |= set(re.findall(r"^#{2,4}\s+(\d+\.\d+(?:\.\d+)?)\s",
                                read(f), re.M))

    bad = []
    for f in chs:
        name = os.path.basename(f); t = read(f)
        for kind in ("Figure", "Table"):
            caps = re.findall(r"\*\*%s \((\d+\.\d+)\)" % kind, t)
            if caps:
                nums = [int(c.split(".")[1]) for c in caps]
                if nums != list(range(1, len(nums) + 1)):
                    bad.append((name, "%s captions are %s, not 1..%d"
                                % (kind.lower(), nums, len(nums))))
                if len(set(caps)) != len(caps):
                    bad.append((name, "duplicate %s caption number" % kind.lower()))
            refs = set(re.findall(r"(?<!\*\*)%s \((\d+\.\d+)\)" % kind, t))
            for r in sorted(refs - set(caps)):
                bad.append((name, "%s (%s) is referenced but has no caption"
                            % (kind, r)))
            for c in sorted(set(caps) - refs):
                bad.append((name, "%s (%s) has a caption but is never referenced"
                            % (kind, c)))
        for sec in sorted(set(re.findall(r"section (\d+\.\d+(?:\.\d+)?)", t))
                          | set(re.findall(r"\u00a7(\d+\.\d+(?:\.\d+)?)", t))):
            if sec not in known:
                bad.append((name, "cites section %s, which exists nowhere" % sec))

    print("  %d chapter file(s) scanned" % len(chs))
    for n, msg in bad:
        print("  ! %s: %s" % (n, msg))
    if not bad:
        print("  figure and table numbering sequential, every reference resolves")
    return not bad


def check_counts(verbose):
    print("── COUNTS ─────────────────────────────────────────────────────────")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_counts.py")]
                       + (["--verbose"] if verbose else []),
                       capture_output=True, text=True)
    print(r.stdout.rstrip())
    if r.stderr.strip(): print(r.stderr.rstrip())
    return r.returncode == 0

# A decimal inside [ ... ] is a confidence bound, not a citation of a figure, and
# a decimal introduced by "spec"/"sens" is a different quantity that happens to
# share a value.  Both were false positives on this checker's first run.
BRACKETED = re.compile(r"\[[^\]]*\]|^[^\[]*?\]")   # also a bracket fragment left by a wrapped line
PRECEDED  = re.compile(r"(spec|sens|sensitivity|specificity|precision|recall|r\s*=|rho|\u03c1)\s*$", re.I)
CONTEXT   = 15   # lines either side; an exemption marker anywhere in the passage

def check_superseded(verbose):
    print("\n── SUPERSEDED FIGURES ─────────────────────────────────────────────")
    bad = []
    for f in docfiles():
        base = os.path.basename(f)
        if base in EXEMPT_FILES: continue
        lines = read(f).splitlines()
        for i, line in enumerate(lines, 1):
            block = "\n".join(lines[max(0, i - 1 - CONTEXT): i + CONTEXT])
            if EXEMPT.search(block): continue
            stripped = BRACKETED.sub(" ", line)          # drop confidence intervals
            for old, (new, why) in SUPERSEDED.items():
                for m in re.finditer(r"(?<![\d.])" + re.escape(old) + r"(?![\d])", stripped):
                    if PRECEDED.search(stripped[:m.start()]): continue
                    bad.append((os.path.relpath(f, ROOT), i, old, new, why, line.strip()[:90]))
                    break
    print(f"  scanned {len(docfiles())} documents for {len(SUPERSEDED)} retired figures"
          f" ({len(EXEMPT_FILES)} files exempt by design)")
    for rel, i, old, new, why, ctx in bad:
        print(f"  ! {rel}:{i}  quotes {old}, superseded by {new} ({why})")
        print(f"      {ctx}")
    if not bad: print("  no retired figure quoted outside its reconciliation context")
    return not bad

def check_pointers(verbose):
    print("\n── FILE POINTERS ──────────────────────────────────────────────────")
    pat = re.compile(r"`((?:results|scripts|src|app|docs|models)/[A-Za-z0-9_./-]+\.(?:json|py|csv|npy|md|png|html))`")
    missing, seen = [], set()
    for f in docfiles():
        # KICKOFF.md is exempt, narrowly and for a reason. Every other document
        # CITES evidence, so a pointer to a missing file is a defect. KICKOFF.md
        # INSTRUCTS a future session to CREATE files -- chapters, appendices --
        # that by definition do not exist yet. Gating it would leave the gate
        # red for as long as the thesis is unwritten, which trains a reader to
        # ignore it. Those pointers are still checked where it matters: once a
        # chapter exists every other document's reference to it is checked here
        # as normal, and the assembly session fails if a promised file is absent.
        if os.path.relpath(f, ROOT).replace(os.sep, '/') == 'docs/KICKOFF.md':
            continue
        for i, line in enumerate(read(f).splitlines(), 1):
            for m in pat.finditer(line):
                rel = m.group(1); seen.add(rel)
                if not os.path.exists(os.path.join(ROOT, rel)):
                    missing.append((os.path.relpath(f, ROOT), i, rel))
    print(f"  {len(seen)} distinct file references cited in prose")
    for src, i, rel in missing: print(f"  ! {src}:{i}  cites {rel}, which does not exist")
    if not missing: print("  every cited file exists")
    return not missing


# ── outbound manifest ────────────────────────────────────────────────────────
# Everything that may be sent to a supervisor, a committee or an examiner. The
# retracted five-task battery result survived three days in SUMMARY_ACADEMIC.md
# because only the PDF exporters were gated; a document that leaves by being
# emailed leaves ungated unless it is named here.
OUTBOUND = [
    # The writing set -- opened when a chapter is started.
    "docs/THESIS_PLAN.md", "docs/NUMBERS.md", "docs/WRITING_BRIEF.md",
    "docs/FILE_MAP.md", "docs/WRITING_FINDINGS.md",
    # Sources.
    "docs/DESIGN_RATIONALE.md", "docs/ARABIC_CORPUS_GAP.md",
    "docs/STAKEHOLDER_ENGAGEMENT.md",
    "docs/libyan_pilot_protocol.md", "docs/LU_EVALUATION_PROTOCOL.md",
    "docs/TRANSPORT_AND_REPORTING.md", "docs/WHERE_THIS_IS_WEAK.md",
    # Evidence.
    "docs/DEVELOPMENT_NARRATIVE.md", "docs/FIGURE_RECONCILIATION.md",
    "docs/LU_EXPOSURE_TIMELINE.md", "docs/RECONSTRUCTION.md",
    "docs/PRE_WRITING_AUDIT.md",
    # Sendable summaries.
    "docs/PROJECT_SUMMARY.md", "docs/SUMMARY_ACADEMIC.md", "docs/SUMMARY_PLAIN.md",
]
# The two summary PDFs were REMOVED from this manifest on 25 August 2026 and moved
# to docs/_archive_stale/. They were generated on 23 August and are wrong in five
# specific ways; that folder's README lists them. Regenerate before external use.
# docs/_working_notes/ and docs/_archive_stale/ are out of scope automatically:
# docfiles() globs docs/*.md and does not descend.

def check_manifest(verbose):
    print("\n\u2500\u2500 OUTBOUND MANIFEST \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    missing = [f for f in OUTBOUND if not os.path.exists(os.path.join(ROOT, f))]
    scanned = {os.path.relpath(f, ROOT).replace(os.sep, "/") for f in docfiles()}
    unscanned = [f for f in OUTBOUND if f.endswith(".md") and f not in scanned]
    print(f"  {len(OUTBOUND)} documents declared outbound; "
          f"{len([f for f in OUTBOUND if f.endswith('.md')])} of them markdown and scanned by the checks above")
    for f in missing: print(f"  ! declared outbound but not on disk: {f}")
    for f in unscanned: print(f"  ! outbound but NOT covered by the scans: {f}")
    extra = sorted(scanned - set(OUTBOUND) - {"THESIS_PLAN.md"})
    if extra and verbose:
        print(f"  (scanned but not declared outbound, which is fine: {', '.join(extra)})")
    if not missing and not unscanned: print("  every outbound document exists and is covered")
    return not missing and not unscanned

# ── retraction registration ─────────────────────────────────────────────────
# FIRST ATTEMPT, ABANDONED, and the reason is recorded because it is a real
# limit rather than an oversight: harvesting every figure out of a retraction
# passage and flagging it elsewhere produced 133 hits and was useless. This
# project's retraction convention QUOTES the withdrawn sentence and then gives
# the corrected figure in the same paragraph, so an automatic harvester cannot
# tell the retired value from the one that replaced it.
#
# WHAT IS DONE INSTEAD. Retracted text in this project is always quoted, so only
# figures inside a QUOTED span within a retraction passage are harvested — those
# are the withdrawn ones. Each is then required to be present in the SUPERSEDED
# table above, which is what check_superseded() propagates across documents.
# The check therefore answers one question: "you wrote a retraction; did you
# register the figure it retired?"
RETRACT_MARK = re.compile(r"RETRACTED|retracted|withdraw|WITHDRAWN|"
                          r"CORRECTION, |does not survive|is withdrawn", re.I)
QUOTED = re.compile(r"[\u201c\u201d\"']([^\u201c\u201d\"']{10,400}?)[\u201c\u201d\"']", re.S)
DECIMAL = re.compile(r"(?<![\d.])(0\.\d{3,4})(?![\d])")

def check_retractions(verbose):
    print("\n\u2500\u2500 RETRACTION REGISTRATION \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    passages, unregistered = 0, []
    for f in docfiles():
        lines = read(f).splitlines()
        i = 0
        while i < len(lines):
            if RETRACT_MARK.search(lines[i]):
                passages += 1
                block = "\n".join(lines[i: i + 12])
                for q in QUOTED.finditer(block):
                    for m in DECIMAL.finditer(BRACKETED.sub(" ", q.group(1))):
                        if m.group(1) not in SUPERSEDED:
                            unregistered.append((os.path.relpath(f, ROOT), i + 1, m.group(1),
                                                 q.group(1).strip()[:70]))
                i += 12
            else:
                i += 1
    seen, uniq = set(), []
    for e in unregistered:
        if e[2] in seen: continue
        seen.add(e[2]); uniq.append(e)
    print(f"  {passages} retraction passages across {len(docfiles())} documents;"
          f" {len(SUPERSEDED)} figures registered as retired")
    for rel, i, val, ctx in uniq:
        print(f"  ? {rel}:{i} retracts a passage quoting {val}, which is not in the retired-figure table")
        print(f'      "{ctx}"')
    if not uniq:
        print("  every figure inside a quoted retraction is registered as retired")
    print("  ADVISORY, and deliberately not a gate. A quoted retraction usually cites the")
    print("  CORRECTED figure in the same sentence as the withdrawn one, so roughly two")
    print("  hits in three above are the current value quoted in context, not a retired")
    print("  one. A check that fails on those would be overridden within a week. Read the")
    print("  list, register anything genuinely retired in SUPERSEDED, and check_superseded()")
    print("  will then propagate it across every document.")
    return True


# ── near-miss detector: the class the other checks cannot see ───────────────
# A figure that is CORRECT somewhere and WRONG here passes every register check.
# One did: Chapter 6 quoted the pilot's detectable AUC as 0.645, which is the
# figure for sixty participants per group, in a sentence about twenty. Nothing
# mechanical saw it; someone read the line.
#
# This is the closest mechanical approximation available. Authoritative values are
# read FROM THE RESULT FILES at runtime -- never typed here, so this table cannot
# drift from its sources. For each quantity, any line mentioning it is scanned for
# a decimal that is CLOSE TO BUT NOT A ROUNDING OF the authoritative value.
# Confidence bounds are stripped first. It is a heuristic and it is reported as
# one: it narrows where to read, it does not replace reading.
def _canon():
    import json
    def j(rel, *ks):
        try:
            d = json.load(open(os.path.join(ROOT, rel)))
            for k in ks: d = d[k]
            return float(d)
        except Exception: return None
    C = "results/summary/CURRENT_development_stats.json"
    I = "results/reconstruction/instrument_properties.json"
    X = "results/reconstruction/cross_corpus_transfer.json"
    return [
        ("external AUC",        j("results/summary/locked_external_validation.json", "external_auc"),
         [r"\bexternal\b", r"\bLu\b", r"one-shot", r"locked"]),
        ("development combined", j(C, "combined", "auc"),        [r"combined", r"development", r"\b987\b"]),
        ("Pitt subset",          j(C, "pitt_dementia", "auc"),   [r"\bPitt\b"]),
        ("Delaware subset",      j(C, "delaware_mci", "auc"),    [r"\bDelaware\b"]),
        ("screening threshold",  j(C, "operating_points", "screening", "threshold"), [r"threshold"]),
        ("screening sensitivity",j(C, "operating_points", "screening", "sensitivity"), [r"sensitivit"]),
        ("screening specificity",j(C, "operating_points", "screening", "specificity"), [r"specificit"]),
        ("calibration max gap",  j(C, "calibration", "max_gap"), [r"max.?gap", r"calibration"]),
        ("Brier",                j(C, "calibration", "brier"),   [r"[Bb]rier"]),
        ("SEM",                  j(I, "C_test_retest_and_mdc", "controls", "gap_le_1.5y", "standard_error_of_measurement"),
         [r"\bSEM\b", r"standard error of measurement"]),
        ("MDC95",                j(I, "C_test_retest_and_mdc", "controls", "gap_le_1.5y", "minimal_detectable_change_95"),
         [r"\bMDC\b", r"minimal detectable"]),
        ("iu.total single feature", j(I, "A_simplest_competitive_baseline", "best_single_auc_combined"),
         [r"iu\.total", r"hand-count", r"single.feature", r"information unit"]),
        ("Delaware within-corpus", j(X, "R_delaware_within", "auc"), [r"within-corpus", r"Delaware-only", r"Delaware only"]),
        ("Delaware->Pitt",       j(X, "delaware_to_pitt", "auc"), [r"Delaware\s*[\u2192>-]+\s*Pitt"]),
        ("Pitt->Delaware",       j(X, "pitt_to_delaware", "auc"), [r"Pitt\s*[\u2192>-]+\s*Delaware"]),
        ("nested best single",   j("results/reconstruction/selection_optimism.json", "nested_best_auc"),
         [r"nested", r"fairly estimated"]),
        ("hand-counted words",   j("results/reconstruction/minimal_probe.json", "raw_total_words_two_discourse_tasks", "auc"),
         [r"total words", r"counted by hand", r"hand.count"]),
    ]

def _is_rounding(v, canon):
    return any(abs(v - round(canon, d)) < 1e-9 for d in (2, 3, 4)) or abs(v - canon) < 1e-9

def check_near_misses(verbose):
    print("\n\u2500\u2500 NEAR-MISS FIGURES \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    canon = [(n, v, [re.compile(k, re.I) for k in ks]) for n, v, ks in _canon() if v is not None]
    print(f"  {len(canon)} quantities, authoritative values read from result files at runtime")
    hits = []
    for f in docfiles():
        if os.path.basename(f) in EXEMPT_FILES: continue
        for i, line in enumerate(read(f).splitlines(), 1):
            if EXEMPT.search(line): continue
            stripped = BRACKETED.sub(" ", line)
            vals = [float(m.group(1)) for m in re.finditer(r"(?<![\d.])(0\.\d{2,4})(?![\d])", stripped)]
            if not vals: continue
            for name, cv, keys in canon:
                if not any(k.search(line) for k in keys): continue
                for v in vals:
                    if _is_rounding(v, cv): continue
                    if 0 < abs(v - cv) <= 0.015:
                        hits.append((os.path.relpath(f, ROOT), i, name, v, cv, line.strip()[:86]))
    seen = set(); uniq = []
    for h in hits:
        k = (h[0], h[1], h[3])
        if k in seen: continue
        seen.add(k); uniq.append(h)
    for rel, i, name, v, cv, ctx in uniq:
        print(f"  ? {rel}:{i}  {v} appears beside \"{name}\" (authoritative {cv:.4f}, difference {abs(v-cv):.4f})")
        print(f"      {ctx}")
    if not uniq: print("  no decimal sits suspiciously close to a different authoritative value")
    print("  ADVISORY. A near miss is usually a different quantity that happens to be close;")
    print("  a genuine stale figure is usually a near miss. Read each, do not act on the count.")
    return True


# ── confidence intervals against source ─────────────────────────────────────
# This check found the most serious defect of the pre-submission pass, and none
# of the others could have. TRANSPORT_AND_REPORTING.md carried AUC intervals
# 1.09-1.31x NARROWER than every other document, because its source had
# resampled RECORDINGS rather than PARTICIPANTS -- ignoring within-participant
# clustering and understating uncertainty. Every value was internally consistent
# and correctly transcribed from its stated source, so no register check could
# see it. An anti-conservative interval is the one error that makes a result look
# BETTER than it is.
#
# The diagnostic that identified it is worth keeping in mind: Lu has one
# recording per participant, so the two bootstrap units must agree there. They
# did, to four decimals. They diverged only where clustering existed.
def _canon_intervals():
    import json
    def j(rel, *ks):
        try:
            d = json.load(open(os.path.join(ROOT, rel)))
            for k in ks: d = d[k]
            return [float(d[0]), float(d[1])]
        except Exception: return None
    C = "results/summary/CURRENT_development_stats.json"
    X = "results/reconstruction/cross_corpus_transfer.json"
    return {k: v for k, v in {
        "0.853":  j("results/summary/locked_external_validation.json", "ci"),
        "0.755":  j(C, "combined", "ci95"),
        "0.8095": j(C, "pitt_dementia", "ci95"),
        "0.629":  j(C, "delaware_mci", "ci95"),
        "0.7096": j("results/reconstruction/instrument_properties.json",
                    "A_simplest_competitive_baseline", "best_single_ci95"),
        "0.5474": j(X, "R_delaware_within", "ci95"),
        "0.7772": j(X, "delaware_to_pitt", "ci95"),
        "0.6460": j(X, "pitt_to_delaware", "ci95"),
    }.items() if v is not None}

# Values that collide with a headline figure to within the matching tolerance but
# are a different quantity. Each verified by hand; add to this list only after
# checking, never to silence a failure.
INTERVAL_COLLISIONS = {"0.6455", "0.547"}
IPAT = re.compile(r"(0\.\d{3,4})\s*\**\s*(?:\*\*)?\[\s*(0\.\d{3,4})\s*,\s*(0\.\d{3,4})\s*\]")

def check_intervals(verbose):
    print("\n\u2500\u2500 CONFIDENCE INTERVALS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    canon = _canon_intervals()
    ok, bad = 0, []
    for f in docfiles():
        for i, line in enumerate(read(f).splitlines(), 1):
            for m in IPAT.finditer(line):
                v, lo, hi = m.group(1), float(m.group(2)), float(m.group(3))
                if v in INTERVAL_COLLISIONS: continue
                key = next((k for k in canon if abs(float(v) - float(k)) < 0.0006), None)
                if key is None: continue
                ci = canon[key]
                if abs(lo - ci[0]) < 0.0015 and abs(hi - ci[1]) < 0.0015:
                    ok += 1
                else:
                    bad.append((os.path.relpath(f, ROOT), i, v, lo, hi, ci, line.strip()[:80]))
    print(f"  {len(canon)} headline figures with authoritative intervals; {ok} quotations match source")
    for rel, i, v, lo, hi, ci, ctx in bad:
        print(f"  ! {rel}:{i}  {v} [{lo}, {hi}] but source says [{ci[0]:.4f}, {ci[1]:.4f}]")
        print(f"      {ctx}")
    if not bad: print("  every quoted interval on a headline figure matches its source file")
    return not bad


def check_numbers_current(verbose):
    """NUMBERS.md is GENERATED. If it has drifted from the result files it names,
    the one-authoritative-source-per-number rule has already failed. Read-only:
    the generator is asked for its output on stdout and diffed. Nothing is
    written and nothing is deleted."""
    import subprocess
    print("\n\u2500\u2500 NUMBERS.md CURRENCY \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    tgt = os.path.join(ROOT, "docs", "NUMBERS.md")
    if not os.path.exists(tgt):
        print("  ! docs/NUMBERS.md is missing -- run scripts/make_numbers_doc.py")
        return False
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "make_numbers_doc.py"), "--stdout"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("  ! the generator failed:"); print("   ", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "?")
        return False
    if read(tgt) == r.stdout:
        print("  NUMBERS.md is current with every result file it names")
        return True
    print("  ! docs/NUMBERS.md has drifted from its sources."
          "\n    Run: python scripts/make_numbers_doc.py")
    return False

def main():
    verbose = "--verbose" in sys.argv
    if "--list" in sys.argv:
        print(f"{'retired':>10}  {'replaced by':>12}   reason")
        for k, (v, w) in SUPERSEDED.items(): print(f"{k:>10}  {v:>12}   {w}")
        return 0
    print("PREFLIGHT — nothing leaves this project until these pass\n")
    ok = [check_notes(verbose), check_format(verbose), check_chapters(verbose),
          check_counts(verbose), check_superseded(verbose), check_pointers(verbose),
          check_intervals(verbose), check_numbers_current(verbose),
          check_retractions(verbose),
          check_near_misses(verbose), check_manifest(verbose)]
    print("\n" + "═" * 68)
    if all(ok):
        print("PREFLIGHT PASSED — safe to export")
        print("\nWhat this gate does NOT cover, stated so it is not mistaken for more\n"
              "than it is: it catches a RETIRED value quoted as current, a count that\n"
              "disagrees with its register, and a pointer to a file that is not there.\n"
              "It cannot catch a value that is correct somewhere and wrong here — a\n"
              "power figure for n = 60 quoted for n = 20 passes every check above, and\n"
              "one did, until someone read the line. Reading is still required.")
        return 0
    names = ["source notes", "format", "chapter consistency",
             "counts", "superseded figures", "file pointers", "confidence intervals",
             "NUMBERS.md currency", "retraction registration", "near misses",
             "outbound manifest"]
    print("PREFLIGHT FAILED: " + ", ".join(n for n, o in zip(names, ok) if not o))
    return 1

if __name__ == "__main__":
    sys.exit(main())
