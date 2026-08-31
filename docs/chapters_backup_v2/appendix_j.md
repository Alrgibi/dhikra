# Appendix J — Software And Reproducibility

This appendix records where the software lives, what it needs to run, how the figures in this thesis are regenerated from the committed record, and which parts of that record cannot be redistributed. No source code is reproduced here; the repository is the record, and this appendix is its map. Figure (J.1) carries the repository address as a scannable code, and Table (J.1) states the identity of the submitted version.

## J.1 Repository And Version

The project is a single directory tree, `dhikra/`, under the address in Table (J.1). The submitted version is identified by the frozen model's checksum rather than by a commit identifier, because the model is the one artefact that must not change: every performance figure in Chapters 3 and 5 was produced by the file whose checksum is given, and a reader who obtains a copy with a different checksum has a different instrument.

**Table (J.1) : Identity of the submitted software**

| Item | Value |
|---|---|
| Repository address | [REPOSITORY URL] |
| Model card version | `2.0-lu-locked` (Appendix C) |
| Frozen screening model | `models/dhikra_model.pkl`, MD5 `5aa20272bffb6d18be92b444b46d8368` |
| Library the model is pinned to | scikit-learn 1.8.0 |
| Interpreter the platform was verified on | Python 3.11, clean machine, `pip install -r requirements.txt` only |

**Figure (J.1) : The repository address as a scannable code; the address in Table (J.1) is the text it encodes.**

## J.2 Structure Of The Repository

Table (J.2) lists the top-level directories and what each holds. The separation matters for reproducibility: `models/` holds the frozen artefacts, `results/` holds every number the thesis cites, `src/` holds the library the platform and the analysis scripts share, and `scripts/` holds the drivers that produced `results/` from the corpora.

**Table (J.2) : Top-level structure of the repository**

| Path | Contents |
|---|---|
| `src/dhikra/` | The library: corpus parsing, the acoustic, linguistic, information-unit and semantic feature extractors, the Arabic linguistic engine, the model wrapper, the quality gate, the risk-adjustment chain, the stimuli and the report generator |
| `app/` | The assessment platform of Chapter 4: the server, its templates and static files |
| `models/` | The frozen screening model, the acoustic model and the severity model |
| `results/` | Every result file the thesis cites, one owner per number (`docs/NUMBERS.md`); `results/reconstruction/` holds the post-lock recomputations and the tombstone of the one-shot external evaluation; `results/_superseded/` holds the pre-lock files they replace |
| `scripts/` | The corpus builders, the development and reconstruction drivers, the figure and number generators, `preflight.py` (the export gate) and `assembly/` (the scripts that built this document) |
| `docs/` | The plan, the number register, the exposure timeline, the pilot protocol, the figures and the chapter sources |
| `data/` | The synthetic sample and the saved demonstration session of Appendix E; no corpus recording is stored here |
| `future_work/` | Implemented and deliberately unwired components, including the pause-and-timing module (section 6.3) |
| `README.md`, `RUN_THE_APP.md`, `START_WINDOWS.bat`, `START_MAC.command` | The project summary, the run guide and the one-click launchers |

## J.3 Environment

The dependencies are listed in `requirements.txt`; one pin is load-bearing and is commented as such in the file. The frozen model is a pickled scikit-learn object built under version 1.8.0, and scikit-learn does not guarantee that a model pickled under one version loads under another, so the library is pinned to the model rather than the model rebuilt for the library — rebuilding it would require a new external evaluation, which the spent corpus cannot provide. Two spaCy language models are installed separately, `en_core_web_sm` and `en_core_web_md`; the second supplies the word vectors behind nine of the sixty-four features, and section 4.5.1 records what happens when it is absent. Automatic transcription is optional: when no recogniser is installed the platform asks for a typed transcript, which is how the reference corpora were produced.

## J.4 Reproduction

Table (J.3) gives the reproduction path in the order it runs. The corpora are obtained from DementiaBank under its membership agreement and are never part of the repository; the paths to the local copies are declared in `corpus_paths.json`. The one step that cannot be repeated is the external evaluation: `results/reconstruction/LU_ONESHOT_EXECUTED` is the tombstone that blocks a second run, and the reproduction of section 3.9.2 was performed under a protocol permitting one execution and no decision.

**Table (J.3) : Reproduction path**

| Step | Command or script | Produces |
|---|---|---|
| Install | `pip install -r requirements.txt`, then `python -m spacy download en_core_web_sm` and `en_core_web_md` | The pinned environment |
| Run the platform | `python app/server.py`, or a one-click launcher | The assessment platform at `http://127.0.0.1:5000` |
| Build the feature matrices | `scripts/build_pitt_cookie.py`, `scripts/build_delaware.py`, `scripts/build_lu.py` (parse only, locked) | Per-corpus feature tables from the DementiaBank transcripts |
| Extract acoustic measures | `scripts/extract_audio_features.py` | The acoustic feature table |
| Development statistics | `scripts/train_development.py`, which re-implements the 987-recording development pipeline from the committed feature tables and compares its output field by field against `results/summary/CURRENT_development_stats.json` | The development statistics of section 5.1 |
| Post-lock reconstructions | The scripts named in each result file's provenance field, for example `scripts/rdi_english_probe.py`, `scripts/repeat_sampling_analysis.py`, `scripts/control_threshold_precision.py` | `results/reconstruction/*.json` |
| Figures and the number register | `scripts/make_figures_partA.py`, `make_figures_extra.py`, `make_figure_rdi.py`, `make_figure_genre.py`; `scripts/make_numbers_doc.py` | `docs/figures/*.png`, `docs/NUMBERS.md` |
| The export gate | `scripts/preflight.py` | Blocks any export that quotes a number without its interval or a claim the gate forbids |
| This document | `scripts/assembly/build.sh` | `Dhikra_thesis.docx` and its page-number pass |
| Demonstration session | `scripts/appendix_e_session.py` | The saved session and report of Appendix E |

## J.5 Required External Datasets

Three DementiaBank corpora are required: Pittsburgh (Cookie Theft picture descriptions; 548 development recordings after exclusion), Delaware (five tasks; 439 picture-description recordings in the development pool and the 288-participant multi-task set of section 5.25) and Lu (the locked external test set; 53 participants after the exclusion of one aphasia case). The Wisconsin Longitudinal Study data support the prospective analysis reported as negative result 1 (section 5.8). Access to each is by application to the holding organisation under its own agreement, and the corpus builders read the transcripts from the paths in `corpus_paths.json`.

## J.6 What Cannot Be Redistributed

The corpora and any derivative that could reconstruct a participant's speech are excluded from the repository: recordings and transcripts alike, from every corpus. The Cookie Theft picture belongs to a published test and is not redistributed; the platform shows the scene drawn for this project instead, with the consequence measured in section 4.3.1. The committed feature matrices are per-recording summary statistics and are retained because the reconstructions of Chapter 5 run from them; they contain no words. The Arabic pilot's 24 recordings are not part of the repository; only their result files are (`results/arabic_pilot/`).
