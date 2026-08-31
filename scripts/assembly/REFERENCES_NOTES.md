# Merged reference list — assembly notes

Companion to `references.json` (62 unique sources). Built 28 August 2026 from the chapter-local lists and the project's verified-citation records; every existing file was read only.

## 1. Sources read, and where they actually live

- Chapter lists: `docs/chapters/chapter1.md` … `chapter6.md` (run-in "References Cited In This Chapter" paragraphs); appendix lists `appendix_d.md` §D.4, `appendix_h.md` §H.10, `appendix_i.md`; the in-text citations of `appendix_g.md` ([2, 3], Chapter 3 numbering) and `appendix_h.md` ([4]–[12] Chapter 3 numbering, [13]–[14] local).
- `appendix_a.md`, `appendix_c.md`, `appendix_e.md`, `appendix_f.md`: no bracketed citations (see §6 for two unnumbered mentions). `appendix_b.md` (identical byte-for-byte to `bundle2/docs/chapters/_pending/appendix_b.md`; there is no `docs/chapters/_pending/`): no reference list; cites five sources inline in author-year form (§6).
- Records: `docs/WRITING_FINDINGS.md` findings 22, 39, 43 (the log there ends at 44); findings 54, 55, 59, 63, 73 are in `/home/claude/work/verify/NEW_FINDINGS.md`; `docs/chapters/handover.md`; the verification reports are at `/home/claude/work/verify/chapter{1,2,3,4,5A,5B,6}.md` (not `docs/chapters/_verify/`); `docs/THESIS_PLAN.md` §1–§2.5 and §3.7; `docs/DESIGN_RATIONALE.md` §1–§5 and its citation-status table; `docs/ARABIC_CORPUS_GAP.md` (Ding et al. DOI); `results/reconstruction/relative_threshold_rules.json` (the decision-curve reference field).

## 2. Counts

| Quantity | Count |
|---|---|
| Numbered entries in the local lists | 78 (ch1 6, ch2 19, ch3 12, ch4 9, ch5 11, ch6 6, App. D 3, App. H 11 — nine reproduced from Chapter 3 plus two local — App. I 1) |
| (file, local number) aliases resolved | 80 (the 78 above plus Appendix G's [2] and [3], which have no local list) |
| Unique sources | **62** |
| Status: `verified` (rests on a project record) | 27 |
| Status: `web-verified-this-session` (decisive elements from a publisher/Crossref/PubMed read on 28 Aug — the verifiers' or mine) | 33 |
| Status: `initials-unverified` | 2 (MacWhinney 2000; Goodglass and Kaplan 1983) |

Every alias in the JSON maps to exactly one item, and every citation number used in any chapter or appendix body has an item (checked mechanically).

## 3. Merge decisions (16 aliases collapsed into 7 items)

| Item | Aliases merged | Basis |
|---|---|---|
| `peledcohen2025_tacl_review` | chapter1 [5] = chapter2 [4] | identical entries |
| `luz2021_adress_editorial` | chapter2 [11] = chapter6 [3] | identical entries |
| `rabaya2026_arabic_moca` | chapter2 [13] = chapter5 [5] = chapter6 [5] | same article; Chapter 5 abbreviates the journal |
| `kabalan2025_arabic_cognitive_tools` | chapter2 [16] = chapter6 [6] | identical entries |
| `yorkston1980_connected_speech` | chapter3 [2] = chapter4 [8] = appendix_g [2] | identical; Appendix G follows Chapter 3's numbering (verify/chapter3.md row 12) |
| `nicholas1993_ciu` | chapter3 [3] = chapter4 [9] = appendix_g [3] | as above |
| Chapter 3 [4]–[12] | = appendix_h [4]–[12] | Appendix H.10 reproduces Chapter 3's entries under the same numbers |

Every other pair was checked by author + year + title; no further duplicates exist. Hanley and McNeil is **not** cited in Chapter 6 any more — the citation moved to Appendix I with the corpus specification (finding 41), so its only numbered alias is Appendix I [1] (Appendix B names it inline).

## 4. Completions and changes, entry by entry

Entries not listed here are carried from the local list unchanged apart from house formatting (§7).

| Item | What was completed or changed | From |
|---|---|---|
| Sedighi 2026 | DOI 10.1002/alz.71109 added | finding 43 |
| Dajani 2026 | first-author initial "I." added (was surname-only) | finding 43 / verify ch1 row 7 |
| Peled-Cohen & Reichart | vol. 13, pp. 1204–1244, DOI 10.1162/tacl.a.35 added (local entries had year only) | finding 55 (vol., DOI); Crossref (pages) |
| Fahmy & Nordheim Alme | DOI added | plan 290–293 |
| Snowdon 1996 | DOI added | plan §2.1 |
| Fraser, Meltzer, Rudzicz | initials K. C. / J. A. / F.; DOI | verify ch2 row 14; plan §2.2 |
| Guo et al. 2021 | initials Y. / C. / C. / S. / T.; DOI | verify ch2 row 14; plan §2.3 |
| Latif et al. 2025 | DOI added | plan §2.3.1 |
| **Niemelä et al.** | **re-cited as the journal version**: *Applied Computing and Intelligence*, vol. 6, no. 1, pp. 89–114, 2026, doi:10.3934/aci.2026006, with arXiv:2502.03484 kept in parentheses. The chapter cites "arXiv, 2025" but quotes v3/journal figures | finding 73(d); Crossref |
| Luz et al. 2021 editorial | initials; DOI | verify ch2 row 14 |
| Ablimit et al. 2022 | initials; Singapore; pp. 6472–6476; DOI 10.1109/ICASSP43922.2022.9747167 | verify ch2 row 14; Crossref |
| Rabaya et al. 2026 | full initials; DOI | plan §2.5; finding 22 |
| Dabbabi; MohmedShareif; Kabalan; Taiebine ×2; Rauniyar | DOIs added; *Revista de Logopedia, Foniatría y Audiología* written with diacritics | plan §2.5 |
| MacWhinney 2000 | non-IEEE parenthetical "(TalkBank / DementiaBank; membership agreement.)" dropped | — |
| Mitchell et al. 2014 | author list confirmed; DOI 10.1111/acps.12336 | Crossref |
| Pike et al. 2022 | **second author corrected to M. G. Cavuoto** (chapter: "M. J."); DOI added | Crossref |
| **Ronner et al.** | invented title and "F." replaced by the verified title, five authors, vol. 9, no. 1, art. BJGPO.2024.0065; "n = 651" dropped | finding 63 |
| **Blane et al.** | invented title replaced; "n = 313" dropped; "J. Blane et al." (13 authors) | finding 63 |
| **Börsch-Supan et al.** | invented title replaced; four authors named; "n = 47,773" dropped | finding 63 |
| NHS England audit | rewritten as a web source with URL, year 2020 (upload path) and a descriptive sentence | web search; verify ch3 row 3 |
| Manly et al. 2022 | full subtitle ("… the 2016 … Protocol project"); pp. 1242–1249 (was "p. 1242"); DOI | Crossref + PubMed |
| Cannon-Albright et al. 2019 | DOI added; nine authors confirmed | Crossref + PubMed |
| Petersen et al. 2018 (App. H [13]) | full title; 13 authors confirmed; DOI; parenthetical dropped | Crossref + PubMed |
| Alzheimer's Association 2024 (App. H [14]) | cited as the journal publication: *Alzheimer's and Dementia*, vol. 20, no. 5, pp. 3708–3821, doi:10.1002/alz.13809; parenthetical dropped | Crossref |
| Grinsztajn et al. | initials L. / E. / G.; NeurIPS proceedings form (vol. 35) | verify ch4 row 1 |
| Niculescu-Mizil & Caruana | initials A. / R.; pp. 625–632; DOI | Crossref |
| Vyhnalek et al. | "M."; no. 4, pp. 1397–1409; DOI | verify ch4 row 3; Crossref |
| Morris et al. 1989 | "J. C."; published title with "Part I."; no. 9, pp. 1159–1165; DOI | Crossref + PubMed |
| Tombaugh, Kozak, Rees | initials T. N. / J. / L.; DOI | Crossref |
| Jacobsen et al. 2015 | all six authors' initials; pp. 2438–2450; DOI | verify ch4 row 6; Crossref |
| Cox; Miller et al.; Koo & Li | initials, issue numbers and page ranges | verify ch5A row 21 |
| **Steyerberg** | place corrected New York → **Cham**; "E. W." added | finding 73(e); verify ch5A row 20 |
| Hu et al. 2017 | initials C. / D. / X. / M. / L. / H.; DOI | DESIGN_RATIONALE citation table |
| Vickers & Elkin | initials A. J. / E. B.; DOI | Crossref |
| van den Berg et al. | "R. L. van den Berg et al." (18 authors); DOI | Crossref |
| Jafari, Andrew, Rockwood | initials Z. / M. K. / K. J.; DOI | Crossref |
| Albertin & Martinelli | initials G. / E.; pp. 13–19; Pisa, Italy; CEUR-WS vol. 3878 (noted, not printed) | ACL Anthology 2024.clicit-1.3 |
| Bittner et al. | initials D. / C. / J.; DOI | Crossref |
| **Luz et al. 2024 (TAUKADIAL)** | author order corrected (… Lanzi, **Chang, Chou, Liu**); initials; pp. 947–951; DOI | verify ch6 row 8; Crossref |
| Ding et al. 2024 | DOI 10.1007/s10462-024-10961-6 | ARABIC_CORPUS_GAP.md |
| **PROCESS-2** | placeholder replaced by "M. Pahar et al., 'PROCESS-2: a benchmark speech corpus for early cognitive impairment detection,' arXiv:2605.14888, 2026" | verify ch6 row 8 |
| Collins; Sounderajah; Moons (App. D) | "first author et al." (local form listed four names then et al.); "art." before article numbers | — |

## 5. Lookups made (25 of 25)

Crossref `api.crossref.org` unless stated. 1 Niculescu-Mizil & Caruana (DOI) · 2 Morris 1989 · 3 Tombaugh 1999 · 4 Jacobsen 2015 · 5 Vyhnalek 2022 (DOI) · 6 van den Berg 2024 · 7 Jafari 2025 · 8 Bittner 2022 · 9 Vickers & Elkin 2006 · 10 Mitchell 2014 · 11 Pike 2022 · 12 Manly 2022 · 13 Cannon-Albright 2019 · 14 PubMed esearch (Manly, Cannon-Albright, Morris PMIDs) · 15 PubMed esummary (their pages and full titles) · 16 Petersen 2018 · 17 Alzheimer's Association 2024 · 18 PubMed esummary Petersen 2018 (author list) · 19 Ablimit 2022 · 20 Luz 2024 · 21 TACL DOI 10.1162/TACL.a.35 · 22 Niemelä journal version · 23 web search Albertin & Martinelli · 24 ACL Anthology page 2024.clicit-1.3 · 25 web search NHS England audit URL. No DOI was guessed: each printed DOI is either in a project record or was read from one of these lookups.

## 6. Not completed, or flagged for the author

- **Goodglass and Kaplan 1983** — left surname-only (`initials-unverified`). No record holds the initials, the verifier did not search it, and the cap was reached first. Complete from the title page ("2nd ed." rests on the verifier's canonical note).
- **MacWhinney 2000** — no verification record anywhere in the project; the initial rests on the chapter draft (`initials-unverified`).
- **WHO fact sheet** — the page's own date is not in the record; insert it before "accessed Aug. 2026" after reading the page.
- **NHS England audit** — the PDF's named authors were not read; corporate author used; year 2020 inferred from the upload path `/2020/04/`.
- **Blane et al.** and **Börsch-Supan et al.** — article numbers 7765 / 14024 were carried from the chapter; the verifier did not re-check them and neither did I.
- **Grinsztajn et al.** — NeurIPS page range not in the record; entry printed without pages (arXiv:2207.08815 is in DESIGN_RATIONALE §3 if a locator is wanted).
- **Steyerberg** — subtitle not in the record; omitted.
- **Taiebine & El Alaoui Faris 2026** — the plan records the title with a trailing ellipsis; the printed title may be truncated.
- **Petersen et al. 2018** — Crossref and PubMed now carry "[RETIRED]" in the title: the AAN has retired this guideline. The citation remains the correct source of Table (H.1)'s MCI bands, but the thesis may want to say so.
- **Format gate** — the merged list introduces "I. Dajani" and "I. Trancoso" (both left surname-only in the chapters for exactly this reason) and keeps "US" in the Manly title; the pronoun scan needs those exemptions (finding 42 already excludes "US" by case).

## 7. House formatting applied to every entry

No serial comma ("X, Y and Z" — the chapters' and the caller's form; the exemplar's own entry has ", and", a one-regex change if the author prefers it). Straight double quotes (the docx pass can curl them). Sentence-case titles. Journal names written in full (abbreviations such as *J. Speech Hear. Disord.*, *Sci. Rep.*, *JAMA Neurol.*, *Med. Decis. Making* expanded); "&" rendered "and" in *Alzheimer's and Dementia* and *Alzheimer's Research and Therapy* per the chapter-wide house form (verify ch1; verify ch5B row 14). "art." before article numbers throughout (the local lists mixed "art. e71109" and bare "e078378"). En-dashes in all page ranges. Conference form "in *Proc. …*, YEAR, pp." and book form "*Title*, Nth ed. City: Publisher, YEAR" as the caller specified. DOIs printed as "doi:…" at the end of the entry only where sourced (§4). Conference acronyms IC_ASET and ATSIP kept as the record holds them rather than expanded.

Alias numbers are integers except Appendix D's, which are the strings "D1", "D2", "D3" as that appendix labels them; Appendix H's reproduced entries appear as `["appendix_h.md", 4]` … `[…, 12]` beside their Chapter 3 aliases. The JSON carries one optional extra field, `unnumbered_mentions`, on four items only (Sedighi, Dajani, El-Metwally, Hanley–McNeil): the places where Appendix B cites them inline without a number, so the assembler can convert those to [n] if the protocol is renumbered.

## 8. Things that look wrong in the local lists or their in-text use (reported, not fixed)

1. **Chapter 2 scaffolding note** says [3], [8], [11], [12], [13] are surname-only "as the verified-citation record holds them" — for [13] the record already held the full initials (plan §2.5). **Chapter 5's** note says [5], [6] and [8]–[11] "were verified against the published articles" and only [1]–[4], [7] are surname-only — in fact all eleven Chapter 5 entries are surname-only (verify ch5B row 14). **Chapter 6's** note omits [5] from its surname-only list. All three notes are removed at assembly anyway.
2. **Chapter 3**'s scaffolding paragraph repeats its first sentence (lines 652–654).
3. **Appendix G** cites [2, 3] with no local list and no statement that its numbering follows Chapter 3 (Appendix H carries that statement); resolved by the merged list.
4. **Chapter 3 [7], [8], [11]** and their Appendix H.10 copies carry invented titles, a wrong initial and non-IEEE "n = …" annotations (finding 63) — superseded by the merged entries.
5. **Chapter 2 [10]** locates a 2025 arXiv preprint whose v1 does not contain the figures the chapter quotes (finding 73d); **Chapter 5 [3]** had the wrong place of publication (73e); **Chapter 6 [1]** listed the last three authors in the wrong order; **Chapter 6 [4]** was an authorless placeholder — all corrected above.
6. In-text use that does not match the entry's content (findings 56, 59; verify ch2 rows 11–13, ch6 row 9): chapter2.md line 11 attaches Fraser et al. [3] to the sentence naming Novoic, Canary Speech and ki:elements; line 21 cites Guo et al. [8] for the field's external-validation record (belongs to [4]); Table (2.2) row 1 cites Luz 2020 [7] for "ADReSS challenge submissions 0.85–0.95" (the editorial [11] holds the submissions, and nothing cited reaches 0.95); line 82 adds a clause to Kabalan et al. [16] that the review does not say; chapter6.md line 79 lets Ding et al. [2] cover the Framingham access-process sentence, which is the project's own check.
7. **Chapter 2 quotations** attributed to the TACL review [4] may not be verbatim (finding 55: "mostly" / "24%" / "advanced to a real-world application" vs the preprint's "largely" / "29%" / "deployed in real-world applications"); the author must check the published PDF.
8. **Unnumbered citations elsewhere** — candidates for numbered entries if the author wants them: chapter6.md line 106 cites "talkbank.org/dementia/access, retrieved August 2026" inline (verify ch6 row 8 recommends a written-out web entry: TalkBank, "DementiaBank access," https://talkbank.org/dementia/access, accessed Aug. 2026, plus a descriptive sentence); appendix_b.md line 244 cites "Rahman & El Gaafary, 2009" (the Arabic MoCA validation) — in no list anywhere in the thesis, and not verified by any record; appendix_a.md line 36 credits idea density to "Turner and Greene, 1977" (DESIGN_RATIONALE verified it as A. Turner and E. Greene, *The Construction and Use of a Propositional Text Base*, Tech. Rep. 63, Institute for the Study of Intellectual Behavior, University of Colorado, Boulder, 1977); appendix_e.md line 72 quotes the platform's own report text, which embeds "Karstens et al., J Int Neuropsychol Soc 30(4):389-401, 2023" (DESIGN_RATIONALE records it; it is inside a verbatim quotation, so it needs no list entry unless the faculty objects to an uncited reference in quoted text).
9. **Appendix B** cites in author-year brackets ("[Sedighi et al., *Alzheimer's & Dementia*, 22(1):e71109, 2026]"), a different convention from the thesis's [n]; if the appendix is reproduced verbatim from the protocol this is a style inconsistency the assembler should rule on.
10. Faculty rule on citation placement (end of paragraph) is breached thesis-wide by mid-paragraph groups (finding 74a) — not a list matter, noted so it is not rediscovered.
