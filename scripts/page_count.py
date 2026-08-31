#!/usr/bin/env python3
"""
page_count.py -- how many pages a chapter actually is, at the faculty format.

WHY THIS EXISTS. Chapter length was being estimated by dividing a markdown word
count by 243 words per page. That constant is REPORT 1's average over its whole
body INCLUDING its figure-heavy and half-empty pages; it is not a conversion
factor for a chapter's prose. Applying it made Chapter 4 look like 15.0 pages
against a 10-12 allocation. Typeset at the specification it is 11 -- inside the
allocation -- and two sessions were about to cut good material to fix a number
that was an artefact of the arithmetic.

Measured from REPORT 1 itself: 205 words per page averaged over all 128 pages,
and about 340 on a page that is solid prose. A chapter's real page count depends
on how many figures and tables it carries, which is exactly what a word count
cannot see and a typesetter can.

This is a MEASURING INSTRUMENT, not the assembly step. It approximates the
specification -- A4, 12pt Times, 1.5 line spacing, 25mm margins, justified, tab
indent, 14pt bold headings, 11pt bold centred captions, 70mm reserved per figure
-- closely enough to rule on allocation. The submitted document is built by the
assembly session from the docx skill, and its page count is the one that counts.

    python scripts/page_count.py docs/chapters/chapter4.md [more.md ...]

Needs reportlab and pypdf (both in requirements.txt; setup_env.sh installs them).
"""
import re, sys, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from pypdf import PdfReader

BODY = ParagraphStyle("b", fontName="Times-Roman", fontSize=12, leading=18,
                      alignment=TA_JUSTIFY, firstLineIndent=12, spaceAfter=0)
HEAD = ParagraphStyle("h", fontName="Times-Bold", fontSize=14, leading=21,
                      spaceBefore=10, spaceAfter=6)
CAP  = ParagraphStyle("c", fontName="Times-Bold", fontSize=11, leading=15,
                      alignment=TA_CENTER, spaceBefore=4, spaceAfter=8)
CELL = ParagraphStyle("t", fontName="Times-Roman", fontSize=11, leading=14)


def _clean(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r"\1", t)
    return t.replace("&", "&amp;").replace("&amp;lt;", "&lt;")


def pages(md_path, pdf_out=None):
    src = open(md_path, encoding="utf-8").read()
    story, rows, nfig, ntab = [], None, 0, 0
    for ln in src.split("\n"):
        s = ln.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            rows = (rows or []) + [[Paragraph(_clean(c), CELL) for c in cells]]
            continue
        if rows:
            t = Table(rows, hAlign="CENTER")
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 4),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
            story += [t, Spacer(1, 8)]; ntab += 1; rows = None
        if not s:
            continue
        if s.startswith("#"):
            story.append(Paragraph(_clean(re.sub(r"^#+\s*", "", s)), HEAD)); continue
        if re.match(r"^\*\*Figure \(", s):
            story += [Spacer(1, 70 * mm), Paragraph(_clean(s.strip("*")), CAP)]
            nfig += 1; continue
        if re.match(r"^\*\*Table \(", s):
            story.append(Paragraph(_clean(s.strip("*")), CAP)); continue
        story.append(Paragraph(_clean(s.lstrip("> ")), BODY))
    out = pdf_out or (os.path.splitext(md_path)[0] + ".preview.pdf")
    SimpleDocTemplate(out, pagesize=A4, leftMargin=25 * mm, rightMargin=25 * mm,
                      topMargin=25 * mm, bottomMargin=25 * mm).build(story)
    n = len(PdfReader(out).pages)
    words = len(re.sub(r"[`*#>|_\[\]]", " ", src).split())
    return n, words, nfig, ntab, out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    print("%-28s %6s %8s %5s %5s  %s" % ("chapter", "PAGES", "words", "figs", "tabs", "w/page"))
    for p in sys.argv[1:]:
        n, w, f, t, _ = pages(p)
        print("%-28s %6d %8d %5d %5d  %6.0f" % (os.path.basename(p), n, w, f, t, w / n))
