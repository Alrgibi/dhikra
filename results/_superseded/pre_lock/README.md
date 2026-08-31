# results/_superseded/pre_lock/ — quarantined 22 August 2026

**Nothing in this folder is citable.** Every file here was computed before the
Lu corpus was locked out (2026-08-18T17:37), and most of them on the
**1,040-recording / 634-participant pool that included Lu**. They are kept
because they are the record of what was believed at the time, and because
several published figures trace back to them.

They were moved here because each one sat in `results/summary/` looking exactly
like a current result file, with no date, no pool, and no provenance — three of
them were advertised in the README as key result files. Each now carries a
`_SUPERSEDED` block at the top of the JSON stating why. **No number in any file
was altered by the quarantine**; that was verified by hashing the non-string
payload before and after.

## What is here, and what replaces it

| File | The problem | Cite this instead |
|---|---|---|
| `calibration.json` | max_gap **0.0688**, `verdict: "probability"` | `CURRENT_development_stats.json → calibration`: slope 1.276, intercept 0.135, Brier 0.199, **max_gap 0.151**, and the output is a **screening score** |
| `operating_points.json` | screening threshold **0.383**; its sens/spec resolve to 370/491 and 322/549 — the 1,040 pool | `CURRENT_development_stats.json → operating_points`: **0.367**, 0.757 sens, 0.588 spec |
| `bootstrap_ci.json` | n **1040**, and a row literally named `"Dementia (Pitt+Lu)"` | combined 0.755 [0.719, 0.790] n=987; Pitt 0.809 [0.761, 0.855]; Delaware MCI 0.629 [0.570, 0.687] |
| `final_by_population.json` | publishes **Lu 0.849** as a population result | `locked_external_validation.json`: **0.853**. `external_validation_honest.json` states 0.849 must never be reported as external validation |
| `specialist_vs_blended.json` | three-corpus (Lu-inclusive) training pool | no post-lock analogue exists; do not report |
| `leave_one_corpus_out.json` | its Lu row **is exposure event E4** — one of the five pre-lock Lu scorings that informed the Delaware decision | `results/reconstruction/cross_corpus_transfer.json` — the Lu-free replacement |
| `all_findings.json` | `deployed_model` n=1040 at threshold 0.38; MCI 0.636; Arabic 0.782/0.805; `auc_speech_only` 0.804 is actually the text+acoustic mean; `age_adjustment_gain` reports the improvement later shown to **be** age leakage | `CURRENT_development_stats.json`, `ablation_post_lock.json`, `age_leakage_evidence.json` |

## One correction this quarantine forces elsewhere

`HANDOFF.md` §5 lists `summary/leave_one_corpus_out.json` under **"UNAFFECTED —
different analyses, still valid"**. That classification is wrong: the file
contains a Lu scoring, and that scoring is on the record as having informed a
training-pool decision. Corrected in HANDOFF on 2026-08-22.

## The sibling folder

`results/_superseded/development/` holds the pre-lock fusion variants
(`fusion.json`, `task_fusion.json`) quarantined on 2026-08-21, and
`results/_superseded/ablation_pre_lock.json` the pre-lock ablation. Same rule:
non-citable, kept for the record.
