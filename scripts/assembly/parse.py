#!/usr/bin/env python3
"""
parse.py -- markdown chapters/appendices -> build/model.json (document model)

Reads the fifteen thesis source files, the merged reference list
(refs/references.json) and the figure map, and emits a JSON model that
render.js turns into the .docx. Global citation numbers are assigned by order
of first citation in thesis order (chapters 1-6, then appendices A-I).

No prose is altered. The only text-level edits are: citation renumbering
[local] -> [global]; removal of the chapter-local "References Cited In This
Chapter" scaffolding; stripping of leading tabs (indent is a paragraph style).
"""
import json, os, re, sys
from markdown_it import MarkdownIt

ROOT = "/home/claude/work/src/docs/chapters"
REFS = "/home/claude/work/refs/references.json"
OUT = "/home/claude/work/build/model.json"

CHAPTERS = [(1, "chapter1.md"), (2, "chapter2.md"), (3, "chapter3.md"),
            (4, "chapter4.md"), (5, "chapter5.md"), (6, "chapter6.md")]
APPENDICES = [("A", "appendix_a.md"), ("B", "_pending/appendix_b.md"), ("C", "appendix_c.md"),
              ("D", "appendix_d.md"), ("E", "appendix_e.md"), ("F", "appendix_f.md"),
              ("G", "appendix_g.md"), ("H", "appendix_h.md"), ("I", "appendix_i.md"), ("J", "appendix_j.md")]
FIGMAP = {  # (chapter, n) -> file   (post-cut numbering)
    (3, 1): "fig_validation_story.png",
    (4, 1): "fig_architecture.png", (4, 2): "fig_stimuli.png",
    (5, 1): "fig_roc.png", (5, 2): "fig_calibration.png", (5, 3): "fig_effect_sizes.png",
    (5, 4): "fig_control_referenced.png", (5, 5): "fig_task_genre.png",
    ("J", 1): "fig_repo_qr.png",
}

md = MarkdownIt("commonmark").enable("table").enable("strikethrough")

SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "−", "⁺": "+"}
SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"}

# ---------- references ----------
refs = json.load(open(REFS, encoding="utf-8"))
alias = {}
for r in refs:
    for f, n in r["aliases"]:
        if not str(n).isdigit():
            continue  # Appendix D's [D1]-[D3] stay local to that appendix
        alias[(os.path.basename(f), int(n))] = r["key"]
global_num = {}   # key -> number, assigned in first-citation order
order = []

CITE = re.compile(r"\[(\d{1,3}(?:,\s*\d{1,3})*)\]")

def renumber_text(text, fname):
    def rep(m):
        parts = [p.strip() for p in m.group(1).split(",")]
        out = []
        for p in parts:
            key = alias.get((fname, int(p)))
            if key is None:
                return m.group(0)  # not a citation for this file (e.g. an interval); leave
            if key not in global_num:
                global_num[key] = len(order) + 1
                order.append(key)
            out.append(str(global_num[key]))
        return "[" + ", ".join(str(x) for x in sorted(int(x) for x in out)) + "]"
    return CITE.sub(rep, text)

# ---------- inline ----------
def split_scripts(text, base):
    """Turn unicode super/subscript characters into sup/sub runs."""
    runs = []
    buf = ""; mode = None
    def flush():
        nonlocal buf
        if buf:
            r = dict(base); r["text"] = buf
            if mode == "sup": r["sup"] = True
            if mode == "sub": r["sub"] = True
            runs.append(r)
        buf = ""
    for ch in text:
        m = "sup" if ch in SUP else ("sub" if ch in SUB else None)
        if m != mode:
            flush(); mode = m
        buf += SUP.get(ch, SUB.get(ch, ch))
    flush()
    return runs

def inline_runs(tokens, fname):
    runs = []
    st = {"b": False, "i": False, "code": False, "s": False}
    for t in tokens:
        if t.type == "strong_open": st["b"] = True
        elif t.type == "strong_close": st["b"] = False
        elif t.type == "em_open": st["i"] = True
        elif t.type == "em_close": st["i"] = False
        elif t.type == "s_open": st["s"] = True
        elif t.type == "s_close": st["s"] = False
        elif t.type == "code_inline":
            runs.append({"text": t.content, "code": True, "b": st["b"], "i": st["i"]})
        elif t.type == "softbreak":
            runs.append({"text": " "})
        elif t.type == "hardbreak":
            runs.append({"text": " "})
        elif t.type == "text":
            base = {"b": st["b"], "i": st["i"], "s": st["s"]}
            runs.append({"text": t.content, "_raw": True, **base})
        elif t.type == "link_open":
            pass
        elif t.type == "link_close":
            pass
        elif t.type == "html_inline":
            runs.append({"text": t.content})
        else:
            if t.content:
                runs.append({"text": renumber_text(t.content, fname)})
    # coalesce adjacent raw text pieces (markdown-it splits at brackets), then renumber
    co = []
    for r in runs:
        if r.get("_raw") and co and co[-1].get("_raw") and all(co[-1].get(k) == r.get(k) for k in ("b", "i", "s")):
            co[-1]["text"] += r["text"]
        else:
            co.append(dict(r))
    runs = []
    for r in co:
        if r.get("_raw"):
            base = {k: r.get(k) for k in ("b", "i", "s")}
            runs.extend(split_scripts(renumber_text(r["text"], fname), base))
        else:
            runs.append(r)
    # merge adjacent identical-format runs
    merged = []
    for r in runs:
        if merged and all(merged[-1].get(k) == r.get(k) for k in ("b", "i", "code", "s", "sup", "sub")):
            merged[-1]["text"] += r["text"]
        else:
            merged.append(dict(r))
    for r in merged:
        r["text"] = r["text"].replace("\t", "")
    return [r for r in merged if r["text"] != ""]

def plain(runs):
    return "".join(r["text"] for r in runs)

CAP = re.compile(r"^(Figure|Table)\s*\(\s*([A-Z]|\d+)\s*\.\s*(\d+)\s*\)\s*:\s*(.*)$", re.S)

# ---------- block parsing ----------
def parse_file(path, fname, kind, ident):
    src = open(path, encoding="utf-8").read()
    # drop the scaffolding reference list
    src = re.sub(r"^\t+", "", src, flags=re.M)   # a leading tab would read as an indented code block
    cut = src.find("**References Cited In This Chapter.**")
    if cut > 0:
        src = src[:cut]
    tokens = md.parse(src)
    blocks = []
    i = 0
    title = None
    list_stack = []
    while i < len(tokens):
        t = tokens[i]
        if t.type == "heading_open":
            inl = tokens[i + 1]; i += 3
            text = plain(inline_runs(inl.children, fname)).strip()
            lvl = int(t.tag[1])
            if lvl == 1:
                m = re.match(r"^(Chapter\s+\d+|Appendix\s+[A-Z])\s*[—–-]\s*(.*)$", text)
                title = m.group(2).strip() if m else text
                continue
            m = re.match(r"^((?:[A-Z]|\d+)(?:\.\d+)+)\s+(.*)$", text)
            blocks.append({"type": "heading", "level": lvl, "number": m.group(1) if m else "",
                           "text": m.group(2) if m else text})
            continue
        if t.type == "paragraph_open":
            inl = tokens[i + 1]; i += 3
            runs = inline_runs(inl.children, fname)
            text = plain(runs)
            m = CAP.match(text)
            if m and runs and runs[0].get("b"):
                kindc, ch, n, rest = m.group(1), m.group(2), int(m.group(3)), m.group(4)
                cap = {"type": "caption", "kind": kindc, "chapter": ch, "n": n,
                       "text": f"{kindc} ({ch}.{n}): {rest.strip()}"}
                if kindc == "Figure":
                    key = (int(ch) if ch.isdigit() else ch, n)
                    cap["file"] = FIGMAP.get(key)
                    if cap["file"] is None:
                        print(f"!! no figure file for {kindc} ({ch}.{n}) in {fname}", file=sys.stderr)
                blocks.append(cap)
                continue
            if list_stack:
                list_stack[-1]["items"][-1]["paras"].append(runs)
            else:
                blocks.append({"type": "para", "runs": runs})
            continue
        if t.type == "blockquote_open":
            i += 1
            qruns = []
            while tokens[i].type != "blockquote_close":
                if tokens[i].type == "paragraph_open":
                    qruns.append(inline_runs(tokens[i + 1].children, fname)); i += 3
                else:
                    i += 1
            i += 1
            for q in qruns:
                blocks.append({"type": "quote", "runs": q})
            continue
        if t.type in ("bullet_list_open", "ordered_list_open"):
            lst = {"type": "list", "ordered": t.type == "ordered_list_open", "items": [], "level": len(list_stack)}
            if list_stack:
                list_stack[-1]["items"][-1]["children"].append(lst)
            else:
                blocks.append(lst)
            list_stack.append(lst); i += 1; continue
        if t.type in ("bullet_list_close", "ordered_list_close"):
            list_stack.pop(); i += 1; continue
        if t.type == "list_item_open":
            list_stack[-1]["items"].append({"paras": [], "children": []}); i += 1; continue
        if t.type == "list_item_close":
            i += 1; continue
        if t.type == "table_open":
            rows = []; cur = None; header = True; hdr_rows = []
            i += 1
            while tokens[i].type != "table_close":
                tt = tokens[i]
                if tt.type == "thead_open": header = True
                elif tt.type == "tbody_open": header = False
                elif tt.type == "tr_open": cur = []
                elif tt.type == "tr_close":
                    (hdr_rows if header else rows).append(cur)
                elif tt.type in ("th_open", "td_open"):
                    cur.append(inline_runs(tokens[i + 1].children, fname)); i += 3; continue
                i += 1
            i += 1
            blocks.append({"type": "table", "header": hdr_rows, "rows": rows})
            continue
        if t.type == "hr":
            i += 1; continue
        if t.type == "fence" or t.type == "code_block":
            blocks.append({"type": "para", "runs": [{"text": t.content.strip(), "code": True}]}); i += 1; continue
        if t.type == "html_block":
            i += 1; continue
        i += 1
    # attach figures: a Figure caption block becomes a figure block (image + caption)
    return {"kind": kind, "id": ident, "file": fname, "title": title, "blocks": blocks}

PLACEMENT = [
    # (chapter, caption-prefix to move, anchor caption-prefix, "after"|"before") -- none needed after the cut; the sources carry the order
]
def apply_placement(model):
    for ch, cap, anchor, where in PLACEMENT:
        c = next(x for x in model["chapters"] if x["id"] == ch); B = c["blocks"]
        i = next(k for k, b in enumerate(B) if b["type"] == "caption" and b["text"].startswith(cap))
        blk = B.pop(i)
        j = next(k for k, b in enumerate(B) if b["type"] == "caption" and b["text"].startswith(anchor))
        if where == "before":
            B.insert(j, blk)
        else:  # after the table that follows the anchor caption
            k = j + 1
            while k < len(B) and B[k]["type"] != "table": k += 1
            B.insert(k + 1, blk)
        print(f"placement: {cap[:-1]} moved {where} {anchor[:-1]}")

def main():
    model = {"chapters": [], "appendices": []}
    for n, f in CHAPTERS:
        model["chapters"].append(parse_file(os.path.join(ROOT, f), f, "chapter", n))
    for L, f in APPENDICES:
        model["appendices"].append(parse_file(os.path.join(ROOT, f), os.path.basename(f), "appendix", L))
    # references in global order; drop sources whose only aliases are Appendix D's own list
    used = [k for k in order]
    reflist = []
    bykey = {r["key"]: r for r in refs}
    for k in used:
        reflist.append({"n": global_num[k], "key": k, "entry": bykey[k]["entry"], "status": bykey[k]["status"]})
    uncited = [r["key"] for r in refs if r["key"] not in global_num and not all(os.path.basename(a[0]) == "appendix_d.md" for a in r["aliases"])]
    apply_placement(model)
    model["references"] = reflist
    model["uncited_sources"] = uncited
    json.dump(model, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # summary
    for c in model["chapters"] + model["appendices"]:
        nb = len(c["blocks"]); caps = [b for b in c["blocks"] if b["type"] == "caption"]
        figs = [b for b in caps if b["kind"] == "Figure"]; tabs = [b for b in caps if b["kind"] == "Table"]
        heads = [b for b in c["blocks"] if b["type"] == "heading"]
        print(f"{c['kind']} {c['id']}: '{c['title']}' blocks={nb} headings={len(heads)} figs={len(figs)} tables={len(tabs)} tables_actual={sum(1 for b in c['blocks'] if b['type']=='table')}")
    print("references cited:", len(reflist), "| uncited sources:", uncited)

if __name__ == "__main__":
    main()
