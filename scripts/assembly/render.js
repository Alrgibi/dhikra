// render.js -- build/model.json + build/front.json -> build/thesis.docx
// Format: EXEMPLAR_NOTES.md rulings (spec over REPORT 1): 12 pt body, 1.5 lines,
// justified, tab indent; headings 14 pt bold Title Case; captions 11 pt bold
// centred ("Figure (x.y): ..." below / "Table (x.y): ..." above); 1-inch margins;
// Roman numerals in the front matter (hidden on the cover), Arabic from the
// Chapter 1 title page (hidden on every chapter/appendix title page).
const fs = require("fs");
const path = require("path");
const D = require("docx");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, PageBreak, PageNumber, Footer, Header, WidthType,
  BorderStyle, TabStopType, TabStopPosition, LevelFormat, NumberFormat,
  Bookmark, SimpleField, PositionalTab, PositionalTabAlignment, PositionalTabLeader,
  PositionalTabRelativeTo, ShadingType, VerticalAlign, SectionType,
} = D;

const MODEL = JSON.parse(fs.readFileSync(path.join(__dirname, "model.json"), "utf8"));
const FRONT = JSON.parse(fs.readFileSync(path.join(__dirname, "front.json"), "utf8"));
const FIGSIZES = JSON.parse(fs.readFileSync(path.join(__dirname, "figsizes.json"), "utf8"));
const FIGDIR = "/home/claude/work/src/docs/figures";
const OUT = process.argv[2] || path.join(__dirname, "thesis.docx");

const FONT = "Times New Roman";
const AR_FONT = "Traditional Arabic";
const MONO = "Courier New";
const TEXT_W = 9360;            // 6.5 in in DXA (A4 8.27in - 2in margins = 6.27in = 9029 DXA)
const TEXT_W_DXA = 9029;
const PX_TEXT_W = 602;          // 6.27 in at 96 px/in
const LINE = 360;               // 1.5 lines
const BODY = 24;                // 12 pt in half-points
const HEAD = 28;                // 14 pt
const CAP = 22;                 // 11 pt
const TITLE = 48;               // 24 pt

// ---------- helpers ----------
function run1(r, text, extra, arabic) {
  const o = { text, font: r.code ? MONO : FONT, size: extra.size || BODY };
  if (r.b) o.bold = true;
  if (r.i) o.italics = true;
  if (r.s) o.strike = true;
  if (r.sup) o.superScript = true;
  if (r.sub) o.subScript = true;
  if (r.code) o.size = (extra.size || BODY) - 2;
  if (extra.bold) o.bold = true;
  if (arabic) { o.font = AR_FONT; o.size = (extra.size || BODY) + 2; o.rightToLeft = true; }
  return new TextRun(o);
}
function run(r, extra = {}) {
  // a long code token (a repository path) gets zero-width break opportunities after / and _ so a justified line is not stretched around it
  if (r.code && r.text.length > 18 && /[\/_]/.test(r.text)) r = Object.assign({}, r, { text: r.text.replace(/([\/_])(?=\S)/g, "$1\u200B") });
  // split at Arabic segments so only Arabic characters take the Arabic font
  const parts = r.text.split(/([؀-ۿ][؀-ۿ\s\u064B-\u065F\u0670]*)/).filter(s => s.length);
  return parts.map(s => run1(r, s, extra, /[؀-ۿ]/.test(s)));
}
function runs(rs, extra = {}) { return rs.flatMap(r => run(r, extra)); }
function T(text, opts = {}) { return new TextRun(Object.assign({ text, font: FONT, size: BODY }, opts)); }

function bodyPara(rs, opts = {}) {
  return new Paragraph(Object.assign({
    children: runs(rs), alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LINE, after: 0, before: 0, lineRule: "auto" },
    indent: { firstLine: 720 },
  }, opts));
}
function quotePara(rs) {
  return new Paragraph({
    children: runs(rs), alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LINE, before: 120, after: 120, lineRule: "auto" },
    indent: { left: 720, right: 720 },
  });
}
function headingPara(number, text, level, bookmarkId) {
  const t = number ? `${number} ${text}` : text;
  const children = [new TextRun({ text: t, bold: true, font: FONT, size: HEAD })];
  const p = {
    heading: level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3,
    spacing: { before: level === 2 ? 280 : 200, after: 80, line: LINE, lineRule: "auto" },
    keepNext: true, keepLines: true, alignment: AlignmentType.LEFT, indent: { firstLine: 0 },
    children: bookmarkId ? [new Bookmark({ id: bookmarkId, children })] : children,
  };
  return new Paragraph(p);
}
function captionPara(text, kind, bookmarkId) {
  const children = [new TextRun({ text, bold: true, font: FONT, size: CAP })];
  return new Paragraph({
    children: bookmarkId ? [new Bookmark({ id: bookmarkId, children })] : children,
    alignment: AlignmentType.CENTER,
    spacing: kind === "Figure" ? { before: 0, after: 160, line: 276 } : { before: 160, after: 60, line: 276 },
    keepNext: kind === "Table", keepLines: true, indent: { firstLine: 0 },
  });
}
function figurePara(file) {
  const [w, h] = FIGSIZES[file];
  const aspect = w / h;
  // page-budget ruling: figures sized to fit beside their text (widths as a fraction of the text width)
  const FIG_SCALE = { "fig_roc.png": 0.55, "fig_calibration.png": 0.55, "fig_effect_sizes.png": 0.6, "fig_control_referenced.png": 0.62,
                      "fig_task_genre.png": 0.8, "fig_validation_story.png": 0.5, "fig_architecture.png": 0.68, "fig_stimuli.png": 0.55, "fig_repo_qr.png": 0.22 };
  let pw = Math.round(PX_TEXT_W * (FIG_SCALE[file] || (aspect > 1.3 ? 0.75 : 0.6)));
  if (/qr/.test(file)) pw = Math.round(96 * 1.6);   // a scannable code needs 1.6 inches, not 75% of the text width
  let ph = Math.round(pw / aspect);
  const maxH = Math.round(96 * 7.2);
  if (ph > maxH) { ph = maxH; pw = Math.round(ph * aspect); }
  return new Paragraph({
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(FIGDIR, file)), transformation: { width: pw, height: ph } })],
    alignment: AlignmentType.CENTER, keepNext: true, keepLines: true,
    spacing: { before: 200, after: 60, line: 240, lineRule: "auto" }, indent: { firstLine: 0 },
  });
}
function cellText(cellRuns, size, bold, align) {
  // long plain-text identifiers (file names, paths) get zero-width break opportunities after _ . / so they wrap sensibly
  const soft = cellRuns.map(r => (r.code || !/[_./]\S{6,}/.test(r.text)) ? r : Object.assign({}, r, { text: r.text.replace(/([_./])(?=\S)/g, "$1\u200B") }));
  return new Paragraph({
    children: runs(soft, { size, bold }), alignment: align,
    spacing: { line: 240, before: 0, after: 0, lineRule: "auto" }, indent: { firstLine: 0 },
  });
}
function tableBlock(b) {
  const header = b.header.length ? b.header[0] : null;
  const ncol = Math.max(...[...(b.header), ...(b.rows)].map(r => r.length));
  let size = ncol <= 4 ? 20 : ncol <= 6 ? 20 : 18;
  // column widths proportional to the longest cell text, bounded
  const lens = new Array(ncol).fill(6);
  for (const row of [...(b.header), ...(b.rows)]) row.forEach((c, i) => {
    const L = c.map(r => r.text).join("").length; lens[i] = Math.max(lens[i], Math.min(L, 260));
  });
  // a column whose longest cell is prose (> 40 characters) is set left-aligned; numeric columns stay centred
  const prose = lens.map(L => L > 40);
  const tot = lens.reduce((a, x) => a + x, 0);
  const anyProse = lens.some(L => L > 40);
  if (anyProse) size = Math.min(size, 20);   // prose-heavy tables are set at 10 pt
  if (b.rows.length > 10) size = Math.min(size, 18);   // long registers and dictionaries at 9 pt
  // an identifier column (its longest unbreakable token, e.g. a feature name in code) must not wrap letter by letter:
  // its minimum width is that token's rendered width (Courier 0.6 em, Times ~0.5 em) plus cell margins
  const tokw = new Array(ncol).fill(0);
  for (const row of [...(b.header), ...(b.rows)]) row.forEach((c, i) => {
    for (const r of c) for (const tk of r.text.split(/\s+/)) {
      const w = tk.length * (size / 2) * (r.code ? 0.6 : 0.5) * 20 + 200;
      if (r.code && tk.length >= 8) tokw[i] = Math.max(tokw[i], Math.min(2600, Math.round(w)));
      else if (!r.code && tk.length >= 6) tokw[i] = Math.max(tokw[i], Math.min(1800, Math.round(tk.length * (size / 2) * 0.52 * 20 + 220)));
    }
  });
  const widths = lens.map((L, i) => Math.max(tokw[i], (i === 0 && anyProse) ? 1700 : (ncol <= 5 ? 1150 : 900), Math.round(TEXT_W_DXA * L / tot)));
  const sumw = widths.reduce((a, x) => a + x, 0);
  // shrink only the columns that have slack above their token minimum
  let cw = widths.map(w => Math.round(w * TEXT_W_DXA / sumw));
  const under = cw.map((w, i) => Math.max(0, tokw[i] - w));
  if (under.some(u => u > 0)) {
    const need = under.reduce((a, x) => a + x, 0);
    const slack = cw.map((w, i) => Math.max(0, w - Math.max(tokw[i], 900)));
    const stot = slack.reduce((a, x) => a + x, 0);
    const take = Math.min(need, stot);                      // never push a column below 900 dxa
    cw = cw.map((w, i) => under[i] > 0 ? w + Math.round(under[i] * take / need) : w - Math.round(take * slack[i] / (stot || 1)));
    const s2 = cw.reduce((a, x) => a + x, 0); cw = cw.map(w => Math.max(300, Math.round(w * TEXT_W_DXA / s2)));
  }
  const B1 = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
  const B0 = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const mkRow = (cells, isHeader) => new TableRow({
    tableHeader: isHeader, cantSplit: true,
    children: cells.map((c, i) => new TableCell({
      width: { size: cw[i], type: WidthType.DXA },
      margins: { top: 25, bottom: 25, left: 80, right: 80 },
      verticalAlign: VerticalAlign.CENTER,
      borders: isHeader ? { bottom: B1 } : {},
      children: [cellText(c, size, isHeader, (i === 0 || prose[i]) ? AlignmentType.LEFT : AlignmentType.CENTER)],
    })),
  });
  const pad = r => { const x = r.slice(); while (x.length < ncol) x.push([{ text: "" }]); return x; };
  const rows = [];
  if (header) rows.push(mkRow(pad(header), true));
  for (const r of b.rows) rows.push(mkRow(pad(r), false));
  return new Table({
    rows, columnWidths: cw, width: { size: TEXT_W_DXA, type: WidthType.DXA },
    alignment: AlignmentType.CENTER,
    borders: { top: B1, bottom: B1, left: B1, right: B1, insideHorizontal: B0, insideVertical: B1 },
  });
}
let listInstance = 0;
function listBlock(b, level = 0) {
  const out = [];
  const inst = ++listInstance;
  for (const it of b.items) {
    it.paras.forEach((pr, k) => {
      out.push(new Paragraph({
        children: runs(pr), alignment: AlignmentType.JUSTIFIED,
        spacing: { line: LINE, before: 0, after: 0, lineRule: "auto" },
        numbering: k === 0 ? { reference: b.ordered ? "numbers" : "bullets", level, instance: inst } : undefined,
        indent: k === 0 ? undefined : { left: 720 + 360 * level, firstLine: 0 },
      }));
    });
    for (const ch of it.children) out.push(...listBlock(ch, level + 1));
  }
  return out;
}

function renderBlocks(blocks, secId) {
  const out = [];
  let pendingFigure = null;
  blocks.forEach((b, idx) => {
    if (b.type === "heading") {
      out.push(headingPara(b.number, b.text, b.level, `h_${b.number.replace(/\./g, "_")}`));
    } else if (b.type === "para") {
      out.push(bodyPara(b.runs));
    } else if (b.type === "quote") {
      out.push(quotePara(b.runs));
    } else if (b.type === "list") {
      out.push(...listBlock(b));
    } else if (b.type === "table") {
      out.push(tableBlock(b));
      out.push(new Paragraph({ children: [new TextRun({ text: "", size: 8 })], spacing: { before: 0, after: 80, line: 160, lineRule: "exact" } }));
    } else if (b.type === "caption") {
      const bid = `c_${b.kind}_${b.chapter}_${b.n}`;
      if (b.kind === "Figure") {
        if (b.file) out.push(figurePara(b.file));
        out.push(captionPara(b.text, "Figure", bid));
      } else {
        out.push(captionPara(b.text, "Table", bid));
      }
    }
  });
  return out;
}

// ---------- section factories ----------
function footerNum(fmt) {
  return new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: BODY })] })] });
}
const emptyFooter = new Footer({ children: [new Paragraph({ children: [] })] });
const PAGE = { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440, footer: 720, header: 720 } };

function titlePageParas(label, title, bookmarkId) {
  return [
    new Paragraph({
      heading: HeadingLevel.HEADING_1, alignment: AlignmentType.LEFT, indent: { firstLine: 0 },
      spacing: { before: 1700, after: 400, line: 276, lineRule: "auto" },
      children: [new Bookmark({ id: bookmarkId, children: [new TextRun({ text: label, bold: true, font: FONT, size: TITLE })] })],
    }),
    new Paragraph({
      alignment: AlignmentType.LEFT, indent: { firstLine: 0 }, spacing: { before: 0, after: 0, line: 276, lineRule: "auto" },
      children: [new TextRun({ text: title, bold: true, font: FONT, size: TITLE })],
    }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}
function bodySection(label, title, blocks, bookmarkId, isFirst, compact = false) {
  const page = Object.assign({}, PAGE, { pageNumbers: { formatType: NumberFormat.DECIMAL } });   // continuous: the count carries on from the front matter (author's ruling)
  if (compact) {
    // appendices: heading block at the top of the first text page, no separate title page (page budget ruling)
    const head = [
      new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.LEFT, indent: { firstLine: 0 },
        spacing: { before: 0, after: 120, line: 276, lineRule: "auto" },
        children: [new Bookmark({ id: bookmarkId, children: [new TextRun({ text: label, bold: true, font: FONT, size: TITLE })] })] }),
      new Paragraph({ alignment: AlignmentType.LEFT, indent: { firstLine: 0 }, spacing: { before: 0, after: 360, line: 276, lineRule: "auto" },
        children: [new TextRun({ text: title, bold: true, font: FONT, size: TITLE })] }),
    ];
    return { properties: { type: SectionType.NEXT_PAGE, page }, footers: { default: footerNum() }, children: [...head, ...renderBlocks(blocks)] };
  }
  return {
    properties: { type: SectionType.NEXT_PAGE, page, titlePage: true },
    footers: { default: footerNum(), first: emptyFooter },
    children: [...titlePageParas(label, title, bookmarkId), ...renderBlocks(blocks)],
  };
}
function plainSection(children, fmt, opts = {}) {
  const page = Object.assign({}, PAGE, { pageNumbers: Object.assign({ formatType: fmt }, opts.start ? { start: opts.start } : {}) });
  const sec = { properties: { type: SectionType.NEXT_PAGE, page, titlePage: !!opts.titlePage }, footers: { default: footerNum() }, children };
  if (opts.titlePage) sec.footers.first = emptyFooter;
  return sec;
}

// ---------- front matter ----------
function centered(text, size, bold = false, before = 0, after = 0, font = FONT) {
  return new Paragraph({ alignment: AlignmentType.CENTER, indent: { firstLine: 0 }, spacing: { before, after, line: 276, lineRule: "auto" },
    children: [new TextRun({ text, bold, font, size })] });
}
function arabicPara(text, size, bold = false, before = 0, after = 0, align = AlignmentType.CENTER) {
  return new Paragraph({ alignment: align, bidirectional: true, indent: { firstLine: 0 }, spacing: { before, after, line: LINE, lineRule: "auto" },
    children: [new TextRun({ text, bold, font: AR_FONT, size, rightToLeft: true })] });
}
function frontTitle(text, bookmarkId) {
  const children = [new TextRun({ text, bold: true, font: FONT, size: TITLE })];
  return new Paragraph({ heading: HeadingLevel.HEADING_1, alignment: AlignmentType.LEFT, indent: { firstLine: 0 }, pageBreakBefore: true,
    spacing: { before: 1000, after: 500, line: 276, lineRule: "auto" }, children: bookmarkId ? [new Bookmark({ id: bookmarkId, children })] : children });
}
function pb() { return new Paragraph({ children: [new PageBreak()] }); }

function coverChildren(c) {
  const out = [];
  if (fs.existsSync(path.join(__dirname, "crest.png"))) {
    out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 300 }, indent: { firstLine: 0 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(__dirname, "crest.png")), transformation: { width: 150, height: 141 } })] }));
  }
  out.push(centered("University of Tripoli", 28, false, 0, 120));
  out.push(centered("Faculty of Engineering", 28, false, 0, 120));
  out.push(centered("Department of Biomedical Engineering", 28, false, 0, 120));
  out.push(centered(c.division, 28, false, 0, 600));
  for (const line of c.title_lines) out.push(centered(line, 28, true, 0, 120));
  out.push(centered("A Project Report Submitted in Partial Fulfilment of the Requirements for the", 22, true, 700, 60));
  out.push(centered("Degree of Bachelor of Science in Biomedical Engineering", 22, true, 0, 700));
  out.push(centered("Prepared by:", 24, true, 0, 120));
  out.push(centered(c.student, 28, true, 0, 60));
  out.push(centered(`ID: ${c.registration}`, 24, true, 0, 400));
  out.push(centered("Supervised by:", 24, true, 0, 120));
  out.push(centered(c.supervisor, 28, true, 0, 700));
  out.push(centered(c.semester, 24, true, 0, 120));
  out.push(centered("Tripoli – Libya", 24, true, 0, 0));
  return out;
}

function indexLine(text, page, bookmark, indentLeft = 0, bold = false) {
  const children = [
    new TextRun({ text: text + "\t", font: FONT, size: BODY, bold }),
    new TextRun({ text: String(page), font: FONT, size: BODY, bold }),
  ];
  return new Paragraph({ children, spacing: { line: LINE, before: 0, after: 0, lineRule: "auto" },
    indent: { left: indentLeft, right: 1400, firstLine: 0 }, alignment: AlignmentType.LEFT,
    tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W_DXA - 720, leader: "dot" }] });
}
function termTable(rows, headers) {
  const B1 = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
  const B0 = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const cw = headers.length === 2 ? [2600, 6429] : [1600, 7429];
  const mk = (cells, hdr) => new TableRow({ tableHeader: hdr, cantSplit: true, children: cells.map((t, i) => new TableCell({
    width: { size: cw[i], type: WidthType.DXA }, margins: { top: 40, bottom: 40, left: 80, right: 80 }, borders: hdr ? { bottom: B1 } : {},
    children: [new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: BODY, bold: hdr })], spacing: { line: 276, before: 40, after: 40, lineRule: "auto" }, indent: { firstLine: 0 }, alignment: AlignmentType.LEFT })] })) });
  return new Table({ rows: [mk(headers, true), ...rows.map(r => mk(r, false))], columnWidths: cw, width: { size: TEXT_W_DXA, type: WidthType.DXA },
    borders: { top: B1, bottom: B1, left: B1, right: B1, insideHorizontal: B0, insideVertical: B1 } });
}

function frontMatterChildren(F) {
  const out = [];
  // Quranic verse page
  out.push(new Paragraph({ children: [], spacing: { before: 4800 } }));
  out.push(arabicPara(F.verse.basmala, 52, true, 0, 600));
  out.push(arabicPara(F.verse.text, 52, false, 0, 500));
  out.push(arabicPara(F.verse.ref, 30, false, 0, 0));
  // Dedication
  out.push(frontTitle("Dedication", "fm_dedication"));
  for (const p of F.dedication) out.push(bodyPara([{ text: p }]));
  // Acknowledgement
  out.push(frontTitle("Acknowledgement", "fm_ack"));
  for (const p of F.acknowledgement) out.push(bodyPara([{ text: p }]));
  // Abstract (English)
  out.push(frontTitle("Abstract", "fm_abstract"));
  for (const p of F.abstract_en) out.push(bodyPara([{ text: p }]));
  // Abstract (Arabic)
  out.push(new Paragraph({ alignment: AlignmentType.CENTER, bidirectional: true, indent: { firstLine: 0 }, pageBreakBefore: true, spacing: { before: 1000, after: 500, line: 276, lineRule: "auto" },
    children: [new Bookmark({ id: "fm_abstract_ar", children: [new TextRun({ text: F.abstract_ar_title, bold: true, font: AR_FONT, size: 40, rightToLeft: true })] })] }));
  for (const p of F.abstract_ar) out.push(arabicPara(p, 26, false, 0, 100, AlignmentType.JUSTIFIED));
  // Contents
  out.push(frontTitle("Table of Contents", "fm_contents"));
  for (const e of F.indices.contents) out.push(indexLine(e.text, e.page, e.bookmark, e.indent, e.bold));
  out.push(frontTitle("Index of Figures", "fm_figures"));
  for (const e of F.indices.figures) out.push(indexLine(e.text, e.page, e.bookmark, 0, false));
  out.push(frontTitle("Index of Tables", "fm_tables"));
  for (const e of F.indices.tables) out.push(indexLine(e.text, e.page, e.bookmark, 0, false));
  out.push(frontTitle("Index of Scientific Terms", "fm_terms"));
  out.push(termTable(F.indices.terms, ["Term", "Meaning"]));
  out.push(frontTitle("Index of Abbreviations", "fm_abbr"));
  out.push(termTable(F.indices.abbreviations, ["Abbreviation", "Definition"]));
  out.push(frontTitle("Index of Symbols", "fm_symbols"));
  out.push(termTable(F.indices.symbols, ["Symbol", "Meaning"]));
  out.push(frontTitle("Index of Appendices", "fm_appendices"));
  for (const e of F.indices.appendices) out.push(indexLine(e.text, e.page, e.bookmark, 0, false));
  return out;
}

// ---------- references ----------
function refParagraph(n, entry) {
  // *italic* markup -> italic runs
  const parts = entry.split(/(\*[^*]+\*)/g).filter(s => s.length);
  const children = [new TextRun({ text: `[${n}]\t`, font: FONT, size: BODY })];
  for (const s of parts) {
    if (s.startsWith("*") && s.endsWith("*")) children.push(new TextRun({ text: s.slice(1, -1), italics: true, font: FONT, size: BODY }));
    else children.push(new TextRun({ text: s, font: FONT, size: BODY }));
  }
  return new Paragraph({ children, alignment: AlignmentType.JUSTIFIED, spacing: { line: LINE, before: 0, after: 120, lineRule: "auto" },
    indent: { left: 720, hanging: 720 }, tabStops: [{ type: TabStopType.LEFT, position: 720 }] });
}

// ---------- assemble ----------
const sections = [];
// cover (Roman, hidden)
sections.push({
  properties: { type: SectionType.NEXT_PAGE, page: Object.assign({}, PAGE, { pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } }), titlePage: true },
  footers: { default: footerNum(), first: emptyFooter },
  children: coverChildren(FRONT.cover),
});
// rest of front matter (Roman, continuing)
sections.push(plainSection(frontMatterChildren(FRONT), NumberFormat.UPPER_ROMAN));
// chapters
MODEL.chapters.forEach((c, i) => {
  sections.push(bodySection(`Chapter ${c.id}`, FRONT.chapter_titles[String(c.id)] || c.title, c.blocks, `ch_${c.id}`, i === 0));
});
// references
const refChildren = [frontTitle("References", "references")];
for (const r of MODEL.references) refChildren.push(refParagraph(r.n, r.entry));
sections.push(plainSection(refChildren, NumberFormat.DECIMAL));
// appendices
MODEL.appendices.forEach(a => {
  sections.push(bodySection(`Appendix ${a.id}`, a.title, a.blocks, `app_${a.id}`, false, true));
});

const doc = new Document({
  creator: FRONT.cover.student, title: FRONT.cover.title_lines.join(" "),
  styles: {
    default: { document: { run: { font: FONT, size: BODY }, paragraph: { spacing: { line: LINE, lineRule: "auto" } } } },
    paragraphStyles: [
      { id: "Normal", name: "Normal", quickFormat: true, run: { font: FONT, size: BODY }, paragraph: { spacing: { line: LINE, lineRule: "auto" } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: TITLE, bold: true, font: FONT, color: "000000" }, paragraph: { spacing: { before: 1700, after: 400 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: HEAD, bold: true, font: FONT, color: "000000" }, paragraph: { spacing: { before: 280, after: 80 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: HEAD, bold: true, font: FONT, color: "000000" }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2, keepNext: true } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
      ] },
      { reference: "numbers", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.LOWER_LETTER, text: "%2.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
      ] },
    ],
  },
  sections,
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
