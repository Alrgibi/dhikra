# results/_superseded/ — quarantined outputs. NON-CITABLE.

Nothing in this folder may be cited in the thesis or any report. Files
are kept (never deleted) so the record of what was tried survives; they
are quarantined because their provenance cannot meet the project's rule
that every reported number trace to a script and an output file.

## development/  (moved here from results/development/, 2026-08-21)

- `fusion.json` — a feature-FAMILY fusion experiment (branch AUCs for
  linguistic / information / semantic families plus a family-level late
  fusion, baseline 0.7539…).
- `task_fusion.json` — an early task-level fusion vs concatenation run
  (n = 288).

**Why non-citable:**
1. **No committed producer.** No script in the repository writes these
   files (`development_experiments.py` writes `experiments.json`, which
   does not exist).
2. **The code is lost.** The runs were inline; the Claude data export
   strips tool-use blocks, so the generating code survives nowhere
   (`archive/dhikra_full_transcript.md`).
3. **The pool is unverifiable.** `fusion.json` carries no dataset or
   lock-state stamp, and its baseline cannot be tied to a known matrix.
   Timeline evidence places both files in the pre-lock window of
   18 Aug 2026 (17:36–17:40).

**What supersedes them:** `results/fusion/results.json` — the post-lock,
Lu-free rerun (18 Aug 2026, 17:54) whose values `review2_actions.json`
cites verbatim (task fusion 0.638 vs concatenation 0.684; late fusion
0.830 vs pooled 0.838). Cite that file only.

## ablation_pre_lock.json  (moved here from results/summary/ablation.json, 2026-08-21)

The original ablation table, computed 18 Aug 2026 at ~17:17 — **before
the 17:37 Lu lock** — on the pre-lock pool. Settled as pre-lock beyond
inference: its "all features, final ensemble" row equals the pre-lock
combined AUC (`final_by_population.json`) to 16 digits. Superseded by
`results/reconstruction/ablation_post_lock.json`, recomputed on the
locked 987-recording development set with the verified final pipeline.

Reference: docs/DEVELOPMENT_NARRATIVE.md (appendix), docs/RECONSTRUCTION.md.
