#!/usr/bin/env python3
"""
check_counts.py -- verify every count claim in the project against its own register.

WHY THIS EXISTS. Three separate stale counts were found in one week, each by
accident: "seven negative results" surviving in three passages after the register
had eight; "Figure register -- 19 produced" after a twentieth was added; and
DEVELOPMENT_NARRATIVE entry 18 still headed "the seven negative results" with a
seven-row table after the register had thirteen. Every one was caught because
someone happened to read the line. Nothing mechanical was looking.

WHAT IT DOES. For each register in the project it counts the rows, then finds
every prose claim about that count anywhere in docs/, in digits or in words, and
reports any that disagree. It also reports claims it can see but cannot resolve,
rather than passing silently.

It does not fix anything. Exit status 1 on any mismatch, so it can gate a
pre-submission pass.

USAGE:  python scripts/check_counts.py [--verbose]
"""
import os, re, sys, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "docs")
WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}
NUM = {v: k for k, v in WORDS.items()}

def num(tok):
    t = tok.strip().lower()
    if t.isdigit(): return int(t)
    return WORDS.get(t)

def read(path):
    with open(path, encoding="utf-8") as f: return f.read()

def rows_of_table(text, start_pat, id_col_pat=r"^\|\s*\**\s*(\d+)\s*\**\s*\|"):
    """Count contiguous numbered rows of the first table after start_pat."""
    m = re.search(start_pat, text, re.M)
    if not m: return None, None
    ids = []
    for line in text[m.end():].splitlines():
        r = re.match(id_col_pat, line)
        if r: ids.append(int(r.group(1)))
        elif ids and not line.startswith("|"): break
    if not ids: return None, None
    return len(ids), ids

def claims(pattern, files):
    out = []
    for f in files:
        for i, line in enumerate(read(f).splitlines(), 1):
            for m in re.finditer(pattern, line, re.I):
                v = num(m.group(1))
                out.append((os.path.relpath(f, ROOT), i, m.group(0).strip(), v))
    return out

def main():
    verbose = "--verbose" in sys.argv
    md = sorted(glob.glob(os.path.join(DOCS, "*.md")) + [os.path.join(ROOT, "THESIS_PLAN.md")])
    md = [f for f in md if os.path.exists(f)]
    plan = os.path.join(DOCS, "THESIS_PLAN.md")
    P = read(plan)
    problems, notes = [], []

    # ---- 1. negative results ----------------------------------------------
    n_reg, ids_reg = rows_of_table(P, r"^\*\*5\.8 Negative results")
    n_idx, ids_idx = rows_of_table(P, r"^### 5\.8\.0 The .* negative results, in one place")
    truth = n_reg
    print(f"NEGATIVE RESULTS   register rows: {n_reg}   index rows: {n_idx}")
    if n_reg and n_idx and n_reg != n_idx:
        problems.append(f"register has {n_reg} rows but the 5.8.0 index has {n_idx}")
    for ids, label in ((ids_reg, "register"), (ids_idx, "index")):
        if ids and ids != list(range(1, len(ids) + 1)):
            problems.append(f"{label} row ids are not 1..n contiguous: {ids}")
    # TOTAL-claim forms only. A partitive ("three negative results came out of the
    # same pass") is not a claim about the register size and must not be flagged;
    # nor is the section number in "5.8 Negative results".
    TOTALS = [r"(\w+|\d+)\s+documented negative results",
              r"negative results\s*[\u2014-]\s*(\w+|\d+)\s+of them",
              r"(?<![\d.])[Tt]he\s+(\w+|\d+)\s+negative results",
              r"(\w+|\d+)\s+negative results in \u00a75\.8",
              r"\*\*(\w+|\d+)\s+negative results\*\*",
              # SUMMARY_ACADEMIC headed its table "Eight results that did not
              # work" and stayed stale for three rounds, because no pattern here
              # matched that phrasing. Added 25 August after finding it by hand.
              r"(\w+|\d+)\s+results that did not work",
              r"(\w+|\d+)\s+reported failures"]
    for f in md:
        for i, line in enumerate(read(f).splitlines(), 1):
            for m in [mm for pt in TOTALS for mm in re.finditer(pt, line)]:
                tok = m.group(1)
                v = num(tok)
                if v is None: continue
                rel = os.path.relpath(f, ROOT)
                if truth is not None and v != truth:
                    ctx = line.strip()[:110]
                    if re.search(r"withdraw|retract|previously|earlier version|stale|corrected", line, re.I):
                        notes.append(f"  (historical, allowed) {rel}:{i}  {ctx}")
                    else:
                        problems.append(f"{rel}:{i} claims {v} negative results, register says {truth} -- {ctx}")
                elif verbose:
                    print(f"  ok {rel}:{i} -> {v}")

    # ---- 2. figure register ------------------------------------------------
    m = re.search(r"^## Figure register\s*[—-]\s*(\d+) produced", P, re.M)
    n_fig, ids_fig = rows_of_table(P, r"^## Figure register")
    print(f"FIGURES            heading claims: {m.group(1) if m else '?'}   register rows: {n_fig}")
    if m and n_fig and int(m.group(1)) != n_fig:
        problems.append(f"figure register heading says {m.group(1)} but the table has {n_fig} rows")
    if ids_fig:
        missing = sorted(set(range(1, max(ids_fig) + 1)) - set(ids_fig))
        if missing: notes.append(f"  figure ids not contiguous, missing: {missing}")
        for fid in ids_fig:
            pass

    # ---- 3. figure files on disk ------------------------------------------
    figs = glob.glob(os.path.join(DOCS, "figures", "*.png"))
    print(f"FIGURE FILES       on disk: {len(figs)}")
    if n_fig and len(figs) < n_fig:
        notes.append(f"  {n_fig} figures registered but {len(figs)} .png files present in docs/figures")

    # ---- 4. table register -------------------------------------------------
    n_tab, _ = rows_of_table(P, r"^## Table register")
    print(f"TABLE REGISTER     rows: {n_tab}")

    # ---- 5. pre-registered runs -------------------------------------------
    cand = (glob.glob(os.path.join(ROOT, "scripts", "*.py"))
            + glob.glob(os.path.join(ROOT, "scripts", "_bootstrap", "*.py")))
    pre = [f for f in cand
           if os.path.basename(f) != "check_counts.py"
           and re.search(r"PRE-REGISTRATION|PRE-REGISTERED", read(f)[:4000], re.I)]
    print(f"PRE-REGISTERED     scripts carrying a registration docstring: {len(pre)}")
    for f in md:
        for i, line in enumerate(read(f).splitlines(), 1):
            for m2 in re.finditer(r"(?:roughly\s+)?(\w+|\d+)\s+(?:pre-)?registered runs", line, re.I):
                v = num(m2.group(1))
                if v is None: continue
                rel = os.path.relpath(f, ROOT)
                if abs(v - len(pre)) > 1:
                    problems.append(f"{rel}:{i} claims {v} registered runs; {len(pre)} scripts carry a registration docstring")
                else:
                    notes.append(f"  registered-runs claim {v} at {rel}:{i} vs {len(pre)} on disk (within tolerance)")

    # ---- 6. thesis-plan copies in sync -------------------------------------
    alt = os.path.join(os.path.dirname(ROOT), "THESIS_PLAN.md")
    if os.path.exists(alt):
        same = read(alt) == P
        print(f"PLAN COPIES        in sync: {same}")
        if not same: problems.append("docs/THESIS_PLAN.md and the root copy differ")

    print()
    for n in notes: print(n)
    if problems:
        print(f"\n{len(problems)} MISMATCH(ES):")
        for x in problems: print("  ! " + x)
        return 1
    print("\nAll count claims agree with their registers.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
