# Exemplar notes — measured from `docs/_exemplars/REPORT 1.pdf`

Written 28 August 2026 by the assembly session, before anything was built.
Every figure below was **measured from the PDF with PyMuPDF** (font names,
point sizes and bounding boxes read from the file), not estimated from a
rendering. Page = A4, 595.28 × 841.89 pt. Page centre x = 297.6 pt.
REPORT 1 is a LaTeX `report`-class document set in Latin Modern (LMRoman12).
`REPORT 2.pdf` (same class, same fonts) was consulted only where REPORT 1 is
silent — items 7 and 8 say where. Where REPORT 1 and the faculty specification
disagree, the **specification wins**; each item ends with the ruling that the
assembled Dhikra document follows.

## 1. Body text point size

**12 pt** — `LMRoman12-Regular` at 12.0 pt accounts for 89,472 of the
document's characters; nothing else is close (the next entries are monospace
code listings at 8 pt and 10.9 pt). REPORT 2 is also 12 pt (87,738 chars).
Line pitch on a dense prose page is **21.67 pt**, i.e. 1.5 × the 12 pt font's
14.5 pt baseline — the "1.5 line spacing" the specification requires.
Paragraph first-line indent 17–18 pt (≈ 1.5 em); no blank line between
paragraphs. Body text is fully justified (right edge sits at 523.3 pt on 551
of 871 measured lines).

*Specification:* the English body-size cell is blank; Arabic is "14 or 12".
*Ruling:* **12 pt, 1.5 spacing, justified, first-line indent (a tab), no
blank line between paragraphs.**

## 2. Margins

Body-text glyph extents across pages 17–77: left 69.7 pt, right 525.7 pt,
top 74.3 pt, bottom 772.2 pt. Allowing for glyph side-bearings this is the
LaTeX 1-inch frame: **left 72 pt, right 72 pt, top 72 pt, bottom ≈ 70 pt
— 25.4 mm all round**, text width 451 pt (159 mm). Page number centred
at x = 297.6, baseline ≈ 802 pt (**≈ 14 mm above the foot edge**, inside the
bottom margin). No header.

*Specification:* silent on margins. *Ruling:* **2.54 cm all round, page
number centred in the footer.**

## 3. A section heading (size, weight, space above and below)

Measured on §2.4 (page 28) and §1.2 (page 17), both mid-page:

| level | example | font | size | space above (prev. text bottom → heading top) | space below (heading bottom → next text top) |
|---|---|---|---|---|---|
| section x.y | "2.4 Differentiable Logic Gate Networks" | LMRoman12-Bold | **17.2 pt** | **34.7 pt** | **20.5 pt** |
| subsection x.y.z | "2.4.1 Foundation: Deep Differentiable…" | LMRoman12-Bold | **14.3 pt** | **29.8 pt** | **17.0 pt** |

Headings are left-aligned, number then title with a fixed gap (number at
x = 72.0, title at x = 114.0 for x.y; x = 119.5 for x.y.z), no trailing
punctuation, Title Case. Note "Foundation:" — REPORT 1 does put a colon in
a heading; the specification forbids it.

*Specification:* main and sub headings **14 pt bold**, first letter of each
word capital, no `: . - --` in headings; the x.y.z level "has the same font
size but bold". `WRITING_BRIEF.md` (verified against the PDF on 26 August,
and the ruling authority) reads that as *the same size as the heading above,
bold* — 14 pt. The alternative reading — the same size as the *text*, i.e.
12 pt bold, which is what "but bold" would be contrasting with — is recorded
here and not adopted. *Ruling:* **x.y = 14 pt bold Title Case; x.y.z = 14 pt
bold Title Case** (REPORT 1's 17.2 pt sections are over the spec's size; its
14.3 pt subsections match); space above ≈ 18 pt / below ≈ 6 pt at the Word
paragraph level so that the rendered gaps sit close to REPORT 1's proportions
(above > below, roughly 5:3) without inflating page count.

## 4. A chapter title page

Page 16: a **separate page carrying only** "Chapter 1" (LMRoman12-Bold
**24.8 pt**, top of text at y = 158.6 pt — 55 mm below the page top, i.e.
≈ 30 mm below the top margin) and "Introduction" (same font and size, top at
y = 223.4 pt; 40 pt of clear space between the two lines). **Both
left-aligned at the text margin (x = 72), not centred.** The rest of the page
is blank; the chapter's first section starts on the next page. The page
number "1" is printed at the foot (x = 294.7, y = 790).

*Specification:* the chapter number-and-title page is counted in the
numbering **but its number is hidden**; the format is free provided it is the
same for every chapter. REPORT 1 therefore breaks the spec by printing the
number. *Ruling:* **separate title page per chapter, "Chapter N" then the
title, consistent across all six, page number suppressed on it; Arabic
numbering starts at 1 on the Chapter 1 title page.**

## 5. A figure with its caption

Measured on Figure 2.3 (page 32) and the 19 other figures:

- Gap image-bottom → caption-top: **10.4 pt** on every figure (LaTeX
  `\abovecaptionskip`).
- Caption: `LMRoman12-Regular` **12 pt, not bold**; form "Figure 2.3: …"
  (label, chapter.figure, colon); a single-line caption is **centred**, a
  multi-line caption is justified across the full text width, single-spaced
  (14.5 pt pitch) within the caption.
- Figures are **centred** on the page (image centre x = 297.6 on 18 of 20).
- Printed width relative to the 451 pt text width: **80 % is the mode**
  (9 of 20), 100 % for six, 90 %/92 % for two, 60–70 % for two, one at 30 %
  (a small tree diagram) and one side-by-side pair at 48 % each.

*Specification:* figure caption **11 pt bold, centred, below the figure,
"no space between the caption and the figure"**, form
"Figure (3 . 4) : Analog Signal", and the caption font must be distinguished
from body text. REPORT 2 already uses the parenthesised form "Figure (2.1):"
(9 figure captions, 0 in the "Figure 2.1:" form). *Ruling:* **11 pt bold,
centred, immediately below the figure (0 pt before-space), form
"Figure (x.y): Title" — the same punctuation `check_docx.py` expects — figures
80 % of text width by default, centred; the word Figure throughout, never
Fig.**

## 6. A table

Measured on Table 2.1 (page 30) and Table 3.4 (page 52):

- Caption **above** the table, `LMRoman12-Regular` 12 pt, not bold; a
  single-line caption is centred (Table 3.4 runs 88.3 → 506.5 pt, centre
  297.4), multi-line captions are left-set at the margin. Gap caption-bottom →
  table top rule: ≈ 4 pt (Table 2.1: caption line 2 bottom 108.8 pt, top rule
  112.1 pt).
- Borders: horizontal rules **only at the top, under the header row, and at
  the bottom** (0.4 pt); **vertical rules on every column boundary including
  the outer edges** (LaTeX `|c|c|c|` with three `\hline`s). No rules between
  body rows.
- Header row **bold 12 pt**; body cells regular **12 pt** (the body size —
  not reduced); row pitch 14.4 pt (single-spaced inside the table).
- The table is **centred** on the page (Table 2.1 spans 174.9 → 420.4 pt,
  centre 297.6); it is not stretched to the text width.

*Specification:* table caption **11 pt bold, centred, above the table**,
form "Table (2 . 1) : True Table". *Ruling:* **caption 11 pt bold centred
above, form "Table (x.y): Title"; header row bold; single spacing inside
tables; table font 11 pt** (Chapter 5's 25 tables cannot be held to 12 pt
inside 159 mm without wrapping every row — the specification names no cell
size, and 11 pt matches the caption size it does name); rules top / under
header / bottom, plus vertical column rules, per REPORT 1.

## 7. One reference entry, character for character

From page 79 (journal article, with the italic span marked):

> [10] T. Hoefler, D. Alistarh, T. Ben-Nun, N. Dryden, and A. Peste, “Sparsity in deep learning: Pruning and growth for efficient inference and training in neural networks,” *Journal of Machine Learning Research*, vol. 22, no. 241, pp. 1–124, 2021.

and a conference paper from page 78:

> [2] F. Petersen, H. Kuehne, C. Borgelt, and O. Deussen, “Deep differentiable logic gate networks,” in *Advances in Neural Information Processing Systems*, vol. 35, 2022, pp. 3772–3784.

This is IEEE style exactly as `IEEEtran.bst` emits it: initials before the
surname, "and" before the last author, the title in curly double quotes in
sentence case with the comma **inside** the closing quote, the venue in
italics, "vol. / no. / pp." with an en-dash page range, year last, full stop.
The list is headed "Bibliography" (the specification's name is "References"
— spec wins), numbered in order of first citation, label "[n]" at x = 77.9
with a **hanging indent** (continuation lines at x = 96.2, ≈ 18 pt), 12 pt,
one blank half-line (≈ 10 pt) between entries, 1.5-spaced within an entry.
A website entry (page 78, [1]) gives author, quoted title, the URL, the
month/year and "accessed: 2025-10-15" — the specification additionally
wants a line or two describing the site's content.

*Ruling:* **IEEE exactly in this form, heading "References", one merged
list numbered by first citation across the whole thesis, hanging indent,
web sources with the descriptive line the specification asks for.**

## 8. The title page and one index page

**Title page (page 1)** — everything centred on x = 297.6:

| y (top, pt) | content | font / size |
|---|---|---|
| 72–200 | university crest, 31 % of text width, centred | image |
| 227 | University of Tripoli | Regular 14.3 |
| 254 | Faculty of Engineering | Regular 14.3 |
| 276 | Department of Electrical and Electronic Engineering | Regular 14.3 |
| 342–410 | the title, three lines | **Bold 14.3** |
| 459–490 | "A Project Report Submitted in Partial Fulfillment of the Requirements for the Degree of Bachelor of Science in …" | Bold 10.9 |
| 560 / 585 | "Prepared by:" / the student's name | Bold 12 / **Bold 14.3** |
| 623 / 648 | "Supervised by:" / "Dr. …" | Bold 12 / **Bold 14.3** |
| 727 / 749 | "Spring 2025" / "Tripoli - Libya" | Bold 12 |

No page number is printed. REPORT 1 omits the **registration number and the
division** the specification requires; REPORT 2's cover (BME, "Control and
Instrumentation Division", "ID: 2200208522" in Bold 12 under the name) shows
where they go. *Ruling:* REPORT 1's layout, plus the division line under the
department and "ID: <registration number>" under the student's name, the
supervisor with academic qualification, the semester and "Tripoli – Libya".

**Contents (page 6)** — heading "Contents" Bold 24.8 pt at y = 158.6, left
at the margin (the same position as every chapter-title page). Entries begin
at y = 242 (≈ 60 pt below the heading). Front-matter items and chapter lines
are **Bold 12**, flush left, page number flush right at x = 523.3 (right
margin); section lines Regular 12, indented 18 pt (x = 89.9), number then
title 27.5 pt apart, dot leaders to a right-aligned page number. Line pitch
21.7 pt (1.5 spacing) between sections; ≈ 33.6 pt before each chapter line.
The List of Figures and List of Tables (pages 10–13) repeat the layout with
the figure number in the number column. Front matter is numbered i–xiv,
centred at the foot, with the title page counted but unnumbered.

**Verse page** — REPORT 1 has none. REPORT 2 page 2: the Basmala centred
at y = 350 (Traditional Arabic Bold 27.3 pt), the verse in ornamental
brackets ﴿ ﴾ at y = 422 (Traditional Arabic 27.3 pt), the surah and verse
number "سورة طه، الآية 114" at y = 479 (15.8 pt) — all centred, nothing else
on the page. *Ruling:* that layout, and it is the one page the specification
allows in Arabic. REPORT 2's Arabic dedication is against the specification
("everything except the verse in English") — the Dhikra dedication is in
English.

**Arabic abstract** (REPORT 1 page 5): heading "الملخص" Traditional Arabic
Bold 13.2 pt centred; body Traditional Arabic 13.2 pt, right-to-left, 21.7 pt
pitch, same 1-inch frame.

## Rulings carried to assembly (summary)

1. 12 pt body, 1.5 spacing, justified, tab indent, no inter-paragraph gap.
2. 2.54 cm margins; footer page number centred.
3. x.y and x.y.z headings 14 pt bold Title Case (per the brief), no
   punctuation, more space above than below.
4. Separate chapter title page, number hidden; "Chapter N" + title, 24 pt
   bold, left, consistent.
5. Captions 11 pt bold centred: "Figure (x.y): …" below, "Table (x.y): …"
   above; no gap between figure and caption; figures 80 % text width.
6. Tables: bold header, top/header/bottom rules plus column rules, 11 pt
   single-spaced, centred.
7. References: IEEE as in item 7, one merged list, hanging indent.
8. Title page per item 8 plus the spec's division and registration number;
   indices in the REPORT 1 layout with the spec's seven lists, front matter
   in Roman numerals with the cover counted but hidden.
