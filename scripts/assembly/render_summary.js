// render_summary.js -- the two-page project summary, on the thesis pipeline's fonts, sizes and margins
// (Times New Roman 12 pt, A4, 2.54 cm margins), at 1.15 line spacing as the brief allows.
// Usage: node render_summary.js <summary.md> <out.docx>
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, AlignmentType, WidthType, BorderStyle,
        VerticalAlign, Footer, PageNumber, NumberFormat } = require("docx");

const FONT = "Times New Roman", AR_FONT = "Traditional Arabic", MONO = "Courier New";
const BODY = 24, HEAD = 26, TITLE = 28, LINE = 240;   // 12 pt, 13 pt headings, 15 pt title, single spacing
const TEXT_W_DXA = 9029;
const PAGE = { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440, footer: 720, header: 720 } };

// ---------- inline markdown → runs ----------
function inlineRuns(s, extra = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  const push = (text, opts) => {
    // split at Arabic segments so only Arabic characters take the Arabic font
    const parts = text.split(/([؀-ۿ][؀-ۿ\sً-ٰٟ]*)/).filter(x => x.length);
    for (const p of parts) {
      const ar = /[؀-ۿ]/.test(p);
      out.push(new TextRun(Object.assign({ text: p, font: ar ? AR_FONT : (opts.code ? MONO : FONT), size: ar ? (extra.size || BODY) + 2 : (extra.size || BODY),
        rightToLeft: ar || undefined }, opts.bold ? { bold: true } : {}, opts.italics ? { italics: true } : {}, extra.bold ? { bold: true } : {})));
    }
  };
  while ((m = re.exec(s)) !== null) {
    if (m.index > last) push(s.slice(last, m.index), {});
    const tok = m[0];
    if (tok.startsWith("**")) push(tok.slice(2, -2), { bold: true });
    else if (tok.startsWith("`")) push(tok.slice(1, -1), { code: true });
    else push(tok.slice(1, -1), { italics: true });
    last = m.index + tok.length;
  }
  if (last < s.length) push(s.slice(last), {});
  return out;
}
const para = (s, opts = {}) => new Paragraph(Object.assign({ children: inlineRuns(s, opts.extra || {}), alignment: AlignmentType.JUSTIFIED,
  spacing: { line: LINE, before: 0, after: 40, lineRule: "auto" } }, opts.p || {}));

// ---------- blocks ----------
const lines = fs.readFileSync(process.argv[2], "utf8").split("\n");
const children = [];
let i = 0;
while (i < lines.length) {
  const ln = lines[i];
  if (!ln.trim()) { i++; continue; }
  if (ln.startsWith("# ")) {
    children.push(new Paragraph({ children: inlineRuns(ln.slice(2), { size: TITLE, bold: true }), alignment: AlignmentType.CENTER,
      spacing: { line: LINE, before: 0, after: 80, lineRule: "auto" } }));
  } else if (ln.startsWith("## ")) {
    children.push(new Paragraph({ children: inlineRuns(ln.slice(3), { size: HEAD, bold: true }), alignment: AlignmentType.LEFT, keepNext: true,
      spacing: { line: LINE, before: 90, after: 30, lineRule: "auto" } }));
  } else if (ln.startsWith("|")) {
    const rows = [];
    while (i < lines.length && lines[i].startsWith("|")) { rows.push(lines[i]); i++; }
    const cells = r => r.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(c => c.trim());
    const header = cells(rows[0]); const body = rows.slice(2).map(cells);
    const ncol = header.length;
    const cw = ncol === 2 ? [Math.round(TEXT_W_DXA * 0.44), TEXT_W_DXA - Math.round(TEXT_W_DXA * 0.44)] : header.map(() => Math.round(TEXT_W_DXA / ncol));
    const B1 = { style: BorderStyle.SINGLE, size: 6, color: "000000" }, B0 = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
    const mk = (cs, hdr) => new TableRow({ tableHeader: hdr, cantSplit: true, children: cs.map((c, k) => new TableCell({
      width: { size: cw[k], type: WidthType.DXA }, margins: { top: 25, bottom: 25, left: 80, right: 80 }, verticalAlign: VerticalAlign.CENTER,
      borders: hdr ? { bottom: B1 } : {},
      children: [new Paragraph({ children: inlineRuns(c, { size: 18, bold: hdr }), alignment: AlignmentType.LEFT,
        spacing: { line: 240, before: 0, after: 0, lineRule: "auto" } })] })) });
    children.push(new Table({ rows: [mk(header, true), ...body.map(r => mk(r, false))], columnWidths: cw, width: { size: TEXT_W_DXA, type: WidthType.DXA },
      alignment: AlignmentType.CENTER, borders: { top: B1, bottom: B1, left: B1, right: B1, insideHorizontal: B0, insideVertical: B1 } }));
    children.push(new Paragraph({ children: [new TextRun({ text: "", size: 8 })], spacing: { before: 0, after: 60, line: 160, lineRule: "exact" } }));
    continue;
  } else if (ln.startsWith("**Table (")) {
    children.push(new Paragraph({ children: inlineRuns(ln.replace(/\*\*/g, "").replace(" : ", ": "), { size: 22, bold: true }), alignment: AlignmentType.CENTER,
      spacing: { line: LINE, before: 80, after: 40, lineRule: "auto" } }));
  } else {
    // a paragraph (may be hard-wrapped over several lines)
    let s = ln;
    while (i + 1 < lines.length && lines[i + 1].trim() && !/^(#|\||\*\*Table)/.test(lines[i + 1])) { i++; s += " " + lines[i]; }
    children.push(para(s));
  }
  i++;
}
const doc = new Document({
  creator: "[STUDENT FULL NAME]", title: "Dhikra project summary",
  styles: { default: { document: { run: { font: FONT, size: BODY }, paragraph: { spacing: { line: LINE, lineRule: "auto" } } } } },
  sections: [{ properties: { page: Object.assign({}, PAGE, { pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(process.argv[3], buf); console.log("wrote", process.argv[3]); });
