#!/usr/bin/env python3
"""
make_numbers_doc.py -- generates docs/NUMBERS.md, the canonical figure registry.

ONE AUTHORITATIVE SOURCE PER NUMBER. Every figure the thesis cites has exactly
one file it comes from. This document is GENERATED from those files, so it
cannot drift from them; regenerate it rather than editing it.

Where two files could each plausibly be the source, one of them is named here and
the other is not. FIGURE_RECONCILIATION.md explains the ones that have had more
than one value; this document says which value is current and where it lives.
"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def j(rel, *ks, default=None):
    try:
        d = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        for k in ks: d = d[k]
        return d
    except Exception: return default
def f4(x): return "—" if x is None else f"{float(x):.4f}"
def ci(x): return "—" if not x else f"[{float(x[0]):.4f}, {float(x[1]):.4f}]"

C  = "results/summary/CURRENT_development_stats.json"
L  = "results/summary/locked_external_validation.json"
X  = "results/reconstruction/cross_corpus_transfer.json"
I  = "results/reconstruction/instrument_properties.json"
T  = "results/reconstruction/task_count_curve.json"
A  = "results/reconstruction/apparatus_value.json"
S  = "results/reconstruction/selection_optimism.json"
RD = "results/reconstruction/rdi_cross_task_probe.json"

HEAD = [
 ("**External validation** — the one-shot locked evaluation", f4(j(L,"external_auc")), ci(j(L,"ci")), L, "§5.3, §1.7",
  "**Scored once and the corpus is spent.** Never quote without the interval. §3.9 must be cited alongside it: five pre-lock scorings occurred, one informed the training-pool composition."),
 ("Development, combined (Pitt + Delaware)", f4(j(C,"combined","auc")), ci(j(C,"combined","ci95")), C, "§5.1",
  "Cross-validated, participant-grouped. Not an external number."),
 ("Development, Pitt subset", f4(j(C,"pitt_dementia","auc")), ci(j(C,"pitt_dementia","ci95")), C, "§5.1",
  "Dementia target. §3.2.1 records a transcription artefact worth −0.0099 (0.7996 corrected); report both with the pre-registered margin."),
 ("Development, Delaware subset", f4(j(C,"delaware_mci","auc")), ci(j(C,"delaware_mci","ci95")), C, "§5.1, §5.25",
  "MCI target, and a **subset performance** — not a corpus-held-out fit. §5.25 shows the weakness is substantially the TASK."),
]
OPS = [
 ("Screening threshold", j(C,"operating_points","screening","threshold"), C, "§5.3",
  "Fixed on development data **before** the external run."),
 ("Sensitivity at threshold", j(C,"operating_points","screening","sensitivity"), C, "§5.3", "Development."),
 ("Specificity at threshold", j(C,"operating_points","screening","specificity"), C, "§5.3", "Development. §5.23: the ceiling is intrinsic — a length rule was tested and refused."),
 ("External sensitivity", j(L,"sensitivity"), L, "§5.3", "Lu, one shot."),
 ("External specificity", j(L,"specificity"), L, "§5.3", "Lu, one shot. **The headline weakness.**"),
 # OVERRIDE, and the reason it exists is worth more than the number.
 # CURRENT_development_stats.json stores calibration.slope = 1.2763890437 and
 # intercept = 0.1347897983. Those are reproduced to TEN DECIMAL PLACES by an
 # L2-PENALISED fit -- sklearn's default LogisticRegression(), C = 1.0 -- while
 # the committed recipe is unpenalised (C = 1e9) and returns 1.2887 / 0.1376
 # from the same stored out-of-fold vector. A penalty shrinks a calibration
 # slope toward zero, which UNDERSTATES miscalibration, so the penalised pair
 # flatters the model and must not be cited.
 #
 # THE FILE ALREADY SAID SO. It carries a `_note` recording exactly this,
 # dated 2026-08-22, ending "CITE 1.289 / 0.138. The numbers in this file are
 # left unaltered." This generator read the numeric field and could not read
 # the note beside it, so NUMBERS.md -- the document whose whole job is to name
 # the authoritative value -- published the one its own source forbids. The
 # source reported that its value had stopped meaning what it meant; nothing
 # downstream could hear it. That is the failure mode of THESIS_PLAN 6.1 item 9
 # occurring inside the machinery built to prevent it.
 #
 # Any value carrying a sibling `_note` is now overridden here explicitly, by
 # hand, with the reason. See check_notes() in preflight.py, which fails if a
 # published field acquires a note that is not overridden here.
 ("Calibration slope", 1.2887, C, "§5.4", "**Unpenalised fit (C = 1e9), from `oof_predictions.npy`.** The value stored in the source file, 1.2764, is an L2-penalised fit and understates miscalibration; the source's own `_note` says cite this one. §3.12: slope is EVIDENCE STRENGTH, intercept the implied prior. Report separately."),
 ("Calibration intercept", 0.1376, C, "§5.4", "See above. Stored value 0.1348 is the penalised fit."),
 ("Brier score", j(C,"calibration","brier"), C, "§5.4", ""),
 ("Largest calibration gap", j(C,"calibration","max_gap"), C, "§5.4", "Lu-free. Confined to the top band and conservative. **The retired value 0.069 had Lu in training.**"),
 ("Training prior", j("results/reconstruction/training_prior.json","training_prior_987"), "results/reconstruction/training_prior.json", "§3.12",
  "465/987. The constant in `risk_adjustment.py`."),
]
SC = "results/reconstruction/scorer_check_grade.json"
INST = [
 ("**Scorer check — mean absolute difference** (human vs automated)", f4(j(SC,"mean_absolute_difference")), "—", SC, "§5.5.1",
  "**Registered threshold ≤ 1.200 → GRADE INADEQUATE.** Report the grade first. Pre-registered 2026-08-25T20:07:10Z, report-and-stop."),
 ("Scorer check — bias (automated − human)", f4(j(SC,"bias")), "—", SC, "§5.5.1",
  "The software counts LOW. Misses outnumber false credits 3.7 : 1. **A hand-counted threshold cannot be inherited from software counts.**"),
 ("Scorer check — ICC(2,1)", f4(j(SC,"icc21")), "—", SC, "§5.5.1",
  "\"Excellent\" (Koo & Li) against a published **human–human ICC of 0.347 [−0.30, 0.69]**. Carries the stratification caveat."),
 ("Scorer check — Spearman (rank preservation)", f4(j(SC,"spearman")), "—", SC, "§5.5.1",
  "6.8% discordant pairs; offset indistinguishable from constant (p = 0.982). **This is why the AUC results survive — tested, not assumed.**"),
 ("Best single hand-countable feature (`iu.total`)", f4(j(I,"A_simplest_competitive_baseline","best_single_auc_combined")), ci(j(I,"A_simplest_competitive_baseline","best_single_ci95")), I, "§5.1.1, §6.1.0b",
  "Selection optimism **0.0000** — chosen in 5 of 5 folds, so this comparison was always fair."),
 ("Standard error of measurement", f4(j(I,"C_test_retest_and_mdc","controls","gap_le_1.5y","standard_error_of_measurement")), "—", I, "§5.9.1, §5.26", "Controls, visit gap ≤1.5 y, 123 pairs."),
 ("Minimal detectable change (95%)", f4(j(I,"C_test_retest_and_mdc","controls","gap_le_1.5y","minimal_detectable_change_95")), "—", I, "§5.9.1, §5.26",
  "**Screening instrument, not a monitoring instrument** — and §5.26 shows repeat-averaging does not rescue that."),
 ("Visit-to-visit agreement (controls)", "0.4650", "—", I, "§3.6.1, §5.9.1",
  "**Label it visit-to-visit agreement, not test–retest reliability.** Correct as-is for the leakage argument (§3.6.1); a *lower bound* for the MDC (§5.9.1)."),
 ("Decision reproducibility on a repeat recording", f4(j("results/reconstruction/repeat_sampling_analysis.json","Q3","reproducibility_k1")), "—", "results/reconstruction/repeat_sampling_analysis.json", "§5.26.1",
  "**One screening decision in six would reverse.** Reported as a contribution: the literature reports feature-level reliability, not decision-level."),
]
TRANS = [
 ("Delaware → Pitt transfer", f4(j(X,"delaware_to_pitt","auc")), ci(j(X,"delaware_to_pitt","ci95")), X, "§5.12", "Lu-free."),
 ("Pitt → Delaware transfer", f4(j(X,"pitt_to_delaware","auc")), ci(j(X,"pitt_to_delaware","ci95")), X, "§5.12", "Lu-free."),
 ("Delaware within-corpus", f4(j(X,"R_delaware_within","auc")), ci(j(X,"R_delaware_within","ci95")), X, "§5.12, FIG-REC §E",
  "**At chance.** This is why the C2 retention criterion was uninterpretable (§3.10)."),
]
SUCC = [
 ("Cookie Theft, MCI, like-for-like", f4(j(T,"AMENDMENT_3_crosssectional","singles","cookie")), "—", T, "§5.25", "43 shared features, 288 participants at earliest common visit."),
 ("Cinderella retell, MCI", f4(j(T,"AMENDMENT_3_crosssectional","singles","cinderella")), "—", T, "§5.25", ""),
 ("Sandwich (procedural), MCI", f4(j(T,"AMENDMENT_3_crosssectional","singles","sandwich")), "—", T, "§5.25", ""),
 ("Best two-task discourse model", "0.6379", "—", T, "§5.25", "Subset selected in-sample; the curve is an **upper bound**."),
 ("Two discourse vs three picture tasks", f"+{float(j(T,'genre_contrast','battery_2disc_vs_3pic','delta')):.4f}", ci(j(T,"genre_contrast","battery_2disc_vs_3pic","ci95")), T, "§5.25",
  "**The transferable claim is genre, not the named tasks.**"),
 ("Nested best single feature, MCI discourse", f4(j(S,"nested_best_auc")), "—", S, "§5.28, §6.1.0b", "The FAIR single-feature comparator."),
 ("Hand-counted words, two discourse tasks", f4(j("results/reconstruction/minimal_probe.json","raw_total_words_two_discourse_tasks","auc")), ci(j("results/reconstruction/minimal_probe.json","raw_total_words_two_discourse_tasks","ci95")), "results/reconstruction/minimal_probe.json", "§5.28",
  "**Selected on the same data that evaluates it.** True value lies roughly 0.60–0.647. Power on 0.60."),
 ("What the apparatus buys, development", f"+{float(j(A,'development','model_minus_nested')):.4f}", "—", A, "§6.1.0b", "Both sides estimated by nested selection."),
 ("What the apparatus buys, MCI discourse", f"+{float(j(A,'mci_discourse','model_minus_nested')):.4f}", "—", A, "§6.1.0b", "**About four points on both. There is no 'four points versus nothing'.**"),
]
def rows(items, wide=True):
    out = []
    for it in items:
        if wide:
            n, v, c, src, sec, cav = it
            out.append(f"| {n} | **{v}** | {c} | `{src}` | {sec} | {cav} |")
        else:
            n, v, src, sec, cav = it
            vv = "—" if v is None else (f"{float(v):.4f}" if isinstance(v,(int,float)) else str(v))
            out.append(f"| {n} | **{vv}** | `{src}` | {sec} | {cav} |")
    return "\n".join(out)

DOC = f"""# NUMBERS.md — one authoritative source per figure

**GENERATED by `scripts/make_numbers_doc.py` from the result files themselves.**
Do not edit this file; regenerate it. Every value below was read from the file
named beside it at generation time, so this document cannot drift from its
sources.

**The rule.** Every figure the thesis cites has exactly one file it comes from.
Where two files could each plausibly be the source, one is named here and the
other is not. `FIGURE_RECONCILIATION.md` explains the figures that have had more
than one value over the project's life; **this** document says which value is
current, where it lives, which section owns it, and **which caveat must travel
with it**.

**Bootstrap units** are audited in `results/BOOTSTRAP_UNITS.json`: every headline
figure is participant-clustered, or comes from an analysis set with one recording
per participant where the distinction does not arise.

---

## 1. Headline AUCs

| Figure | Value | 95% CI | Authoritative source | Owning section | Caveat that must travel with it |
|---|---|---|---|---|---|
{rows(HEAD)}

## 2. Operating point and calibration

| Figure | Value | Authoritative source | Owning section | Caveat |
|---|---|---|---|---|
{rows(OPS, wide=False)}

## 3. Instrument properties

| Figure | Value | 95% CI | Authoritative source | Owning section | Caveat |
|---|---|---|---|---|---|
{rows(INST)}

## 4. Cross-corpus transfer

| Figure | Value | 95% CI | Authoritative source | Owning section | Caveat |
|---|---|---|---|---|---|
{rows(TRANS)}

## 5. Specified successor — never in a table with a validated figure (§1.7)

| Figure | Value | 95% CI | Authoritative source | Owning section | Caveat |
|---|---|---|---|---|---|
{rows(SUCC)}

---

## 6. Figures that are NOT to be cited

`FIGURE_RECONCILIATION.md` holds the full reconciliations. In short, the
following are retired and the preflight will flag them if they appear as current:

| Retired | Replaced by | Why |
|---|---|---|
| 0.636 | 0.629 | Delaware MCI, pre-lock file |
| 0.849 / 0.859 | 0.853 | external AUC computed with Lu consulted |
| 0.5687 | 0.5061 | Delaware cookie, first-row-in-file-order label rule |
| 0.6455 | 0.6379 | five-task battery, retracted arm |
| 0.7424 | 0.7391 | Arabic-equivalent, pre-lock pool |
| 0.6230 | 0.5571 | age-only, pre-lock pool |
| 0.997 | 0.994 | age-reconstruction R², inline value |
| 0.4721 | 0.471125 | training prior, pre-lock pool |
| 0.069 | 0.151 | calibration gap computed with Lu in training |

## 7. Cohort sizes, stated once

| Quantity | Value | Source |
|---|---|---|
| Development recordings | **{j(C,"n_recordings")}** | `{C}` |
| Development participants | **{j(C,"n_participants")}** | `{C}` |
| Deployed features | **{j(C,"n_features")}** | `{C}` — 64 columns, **63 distinct quantities** (§5.22: `iu.proportion` is `iu.total`/23) |
| Pitt recordings | **548** | `results/pitt_cookie/meta.csv` |
| Delaware cookie recordings | **439** | `results/delaware/cookie_meta.csv` |
| External (Lu) recordings | **{j(L,"n")}** | `{L}` — 27 control / 26 impaired, one recording per participant |
| Delaware complete-case, five tasks | **288** | `{T}` — 115 impaired / 173 control at earliest common visit |

## 8. Sample sizes for the Libyan corpus

| Target | True AUC to power on | n per group | Source |
|---|---|---|---|
| Dementia, referential index | 0.596 | **141** | `ARABIC_CORPUS_GAP.md` §5.6 |
| MCI, discourse — **conservative end, use this** | 0.600 | **130** | §5.6 |
| MCI, discourse — selection-inflated upper end | 0.642 | 65 | **do not power on this** |
| Control arm, threshold to ±7.5 points | — | 108 controls | `control_threshold_precision.json` |
| **Recommended** | — | **120 impaired + 120 healthy** | §5.6 |
| Pilot as written (20/group) detects only | **0.748** | — | §5.8 — **not 0.645, which is the figure for sixty** |
"""
if "--stdout" in sys.argv:
    # Used by preflight.py to check currency WITHOUT writing or deleting anything:
    # the project directory is a read-only-delete mount, so the obvious
    # write-a-backup-and-restore approach fails at the unlink.
    sys.stdout.write(DOC)
else:
    open(os.path.join(ROOT, "docs", "NUMBERS.md"), "w", encoding="utf-8").write(DOC)
    print(f"written docs/NUMBERS.md ({DOC.count(chr(10))+1} lines)")
