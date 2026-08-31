#!/usr/bin/env python3
"""harvest.py -- read the rendered PDF, find the page of every bookmarked item, write pages.json
   (printed page numbers: Roman for the front matter, Arabic from the Chapter 1 title page)."""
import json, re, sys, pymupdf
pdf = sys.argv[1]; out = sys.argv[2]
MODEL = json.load(open("/home/claude/work/build/model.json", encoding="utf-8"))
FRONT = json.load(open("/home/claude/work/build/front.json", encoding="utf-8"))
d = pymupdf.open(pdf)
texts = [p.get_text() for p in d]
lines = [[l.strip() for l in t.splitlines()] for t in texts]
def roman(n):
    vals = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
    s = ""
    for v, r in vals:
        while n >= v: s += r; n -= v
    return s
# physical index of the Chapter 1 title page
ch1 = next(i for i, L in enumerate(lines) if len([x for x in L if x]) <= 3 and "Chapter 1" in L)
def printed(i):
    return roman(i + 1) if i < ch1 else str(i + 1)   # continuous Arabic numbering carrying the physical position
pages = {}
def find_line(pred, start=0):
    for i in range(start, len(lines)):
        for l in lines[i]:
            if pred(l): return i
    return None
# front matter titles
for key, title in [("fm_dedication","Dedication"),("fm_ack","Acknowledgement"),("fm_abstract","Abstract"),("fm_contents","Table of Contents"),("fm_figures","Index of Figures"),("fm_tables","Index of Tables"),("fm_terms","Index of Scientific Terms"),("fm_abbr","Index of Abbreviations"),("fm_symbols","Index of Symbols"),("fm_appendices","Index of Appendices")]:
    i = find_line(lambda l, t=title: l == t)
    if i is not None: pages[key] = printed(i)
i = find_line(lambda l: l == "الملخص" or "الملخص" in l)
if i is not None: pages["fm_abstract_ar"] = printed(i)
i = find_line(lambda l: l == "References", start=ch1)
if i is not None: pages["references"] = printed(i)
# chapter / appendix title pages, headings, captions
pos = ch1
def norm(s): return re.sub(r"\s+", " ", s).strip()
for c in MODEL["chapters"] + MODEL["appendices"]:
    label = f"Chapter {c['id']}" if c["kind"] == "chapter" else f"Appendix {c['id']}"
    i = find_line(lambda l, L=label: l == L, start=pos)
    if i is None: print("!! title page not found", label); continue
    pages[("ch_" if c["kind"] == "chapter" else "app_") + str(c["id"])] = printed(i); pos = i
    for b in c["blocks"]:
        if b["type"] == "heading":
            target = norm(f"{b['number']} {b['text']}")
            j = None
            for k in range(pos, len(lines)):
                joined = norm(" ".join(lines[k]))
                if target in joined: j = k; break
            if j is None: print("!! heading not found", target[:60]); continue
            pages["h_" + b["number"].replace(".", "_")] = printed(j); pos = j
        elif b["type"] == "caption":
            prefix = f"{b['kind']} ({b['chapter']}.{b['n']}):"
            j = None
            for k in range(pos, len(lines)):
                if any(l.startswith(prefix) for l in lines[k]): j = k; break
            if j is None: print("!! caption not found", prefix); continue
            pages[f"c_{b['kind']}_{b['chapter']}_{b['n']}"] = printed(j); pos = j
json.dump(pages, open(out, "w"), indent=1)
# chapter page counts (title page through the page before the next section start)
starts = []
for c in MODEL["chapters"]:
    starts.append((f"Chapter {c['id']}", int(pages[f"ch_{c['id']}"])))
starts.append(("References", int(pages["references"])))
for a in MODEL["appendices"]:
    starts.append((f"Appendix {a['id']}", int(pages[f"app_{a['id']}"])))
starts.append(("END", len(d) + 1))
print(f"physical pages {len(d)}; front matter {ch1} pages (I–{roman(ch1)}); body pages {len(d) - ch1}")
for (n, s), (_, e) in zip(starts, starts[1:]):
    print(f"  {n:14s} pages {s:4d}–{e-1:4d}  = {e - s:3d}")
print("items located:", len(pages))
