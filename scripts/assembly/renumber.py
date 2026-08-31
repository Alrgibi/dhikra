#!/usr/bin/env python3
"""renumber.py -- after the cut: map old Chapter 5 section/table/figure numbers to the new ones across every source,
plus the handful of Chapter 3/4/6 and appendix renumberings. Reports every dropped-object reference it finds."""
import re, glob, sys
ROOT = "/home/claude/work/src/docs/chapters/"
FILES = sorted(glob.glob(ROOT + "chapter*.md")) + sorted(glob.glob(ROOT + "appendix_*.md")) + [ROOT + "_pending/appendix_b.md", "/home/claude/work/build/front.py"]

SEC = {"5.9.1": "5.14", "5.14": "5.13.1", "5.15": "5.13.2", "5.16": "5.13.2", "5.17": "5.13.1", "5.18": "5.13.3",
       "5.19": "5.13.2", "5.20": "5.13.3", "5.21": "5.16", "5.22": "5.16", "5.23": "5.13.2", "5.24": "5.14",
       "5.25": "5.15", "5.26": "5.14", "5.26.1": "5.14.1", "5.27": "5.10.1", "5.28": "5.16", "5.29": "5.16", "5.30": "5.16"}
TAB = {"5.1": "5.1", "5.2": "5.2", "5.3": "5.3", "5.5": "5.4", "5.6": "5.5", "5.8": "5.6", "5.9": "5.7", "5.10": "5.8",
       "5.11": "5.9", "5.12": "5.10", "5.13": "5.11", "5.14": "5.12", "5.15": "5.13", "5.16": "5.14", "5.20": "5.15",
       "5.18": "5.16", "5.19": "5.17", "5.25": "5.18"}
FIG = {"5.1": "5.1", "5.2": "5.2", "5.3": "5.3", "5.11": "5.4", "5.14": "5.5", "4.3": "4.2", "4.1": "4.1", "3.2": "3.1"}
DROPPED_TAB = {"5.4", "5.7", "5.17", "5.21", "5.22", "5.23", "5.24"}
DROPPED_FIG = {"5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10", "5.12", "5.13", "4.2", "3.1"}
problems = []
for path in FILES:
    t = open(path, encoding="utf-8").read(); orig = t
    name = path.split("/")[-1]
    # a. tables / figures → placeholders
    def tab(m):
        n = m.group(1)
        if n in TAB: return "Table (⟦T" + TAB[n] + "⟧)"
        if n in DROPPED_TAB: problems.append((name, "dropped table referenced: Table (%s)" % n))
        return m.group(0)
    t = re.sub(r"Table \((5\.\d+)\)", tab, t)
    def fig(m):
        n = m.group(1)
        if n in FIG: return "Figure (⟦F" + FIG[n] + "⟧)"
        if n in DROPPED_FIG: problems.append((name, "dropped figure referenced: Figure (%s)" % n))
        return m.group(0)
    t = re.sub(r"Figure \((5\.\d+|4\.\d+|3\.\d+)\)", fig, t)
    # b. bare Chapter 5 section tokens (headings included), not preceded by a letter/digit/dot (so N5.14 and 0.5.x are untouched)
    def sec(m):
        n = m.group(0)
        return SEC.get(n, n)
    t = re.sub(r"(?<![\w.])5\.\d+(?:\.\d+)?(?![\d.])", sec, t)
    t = t.replace("N5.", "5.")
    # c. restore placeholders
    t = t.replace("⟦T", "").replace("⟦F", "").replace("⟧", "")
    # d. other renumberings
    t = t.replace("Table (H.1)) ", "Table (H.1)) ")  # no-op guard
    if name == "chapter5.md": t = t.replace("(Appendix H, Table (H.1))", "(Appendix H, Table (H.3))")
    if name == "appendix_f.md": t = t.replace("6.1.1", "6.1")
    if name == "appendix_j.md": t = t.replace("the reproduction of section 3.9.2 was performed", "the reproduction of section 3.9.1 was performed")
    if t != orig:
        open(path, "w", encoding="utf-8").write(t); print("renumbered", name)
for p in problems: print("!!", p)
# leftover range references that need a human eye
for path in FILES:
    t = open(path, encoding="utf-8").read()
    for m in re.finditer(r"sections 5\.[\d.]+ (?:to|and) 5\.[\d.]+", t):
        print("check range:", path.split("/")[-1], m.group(0))
