#!/usr/bin/env python3
"""revlib.py -- shared helper for the revision scripts. Every replacement asserts its count
on the SOURCE OF RECORD (docs/chapters/*.md, _pending/appendix_b.md, front.py)."""
import re
ROOT = "/home/claude/work/src/docs/chapters/"
FILES = {f: ROOT + f for f in ["chapter1.md","chapter2.md","chapter3.md","chapter4.md","chapter5.md","chapter6.md",
        "appendix_a.md","appendix_c.md","appendix_d.md","appendix_e.md","appendix_f.md","appendix_g.md","appendix_h.md","appendix_i.md"]}
FILES["appendix_b.md"] = ROOT + "_pending/appendix_b.md"
FILES["front.py"] = "/home/claude/work/build/front.py"
TXT = {k: open(v, encoding="utf-8").read() for k, v in FILES.items()}
LOG = []

def ws(s):
    return r"\s+".join(re.escape(w) for w in s.split())

def rep(f, old, new, n=1, regex=False):
    t = TXT[f]
    pat = old if regex else ws(old)
    found = len(re.findall(pat, t, re.S))
    assert found == n, f"{f}: expected {n} of {old[:80]!r}, found {found}"
    TXT[f] = re.sub(pat, lambda m: new, t, flags=re.S)
    LOG.append((f, old[:70], new[:70], n))

def count(f, pat, regex=False):
    return len(re.findall(pat if regex else ws(pat), TXT[f], re.S))

def write(tag=""):
    for k, v in FILES.items():
        open(v, "w", encoding="utf-8").write(TXT[k])
    print(f"{tag}{len(LOG)} replacements applied")
    for f, a, b, n in LOG:
        print(f"  {f:16s} ×{n}  {a!r} → {b!r}")
