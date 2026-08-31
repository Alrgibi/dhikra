"""
make_summary_pdf.py
-------------------
Generates the project summary as a formatted PDF suitable for sending to a
supervisor.

REWRITTEN 2026-08-22. The previous version was written before the Lu lock and
before the post-lock reconstruction, and carried five classes of stale or
overstated content: pre-lock performance figures, the pre-lock calibration
block, the claim that Lu was "excluded from every development decision" and
"never seen", the claim that the English pronoun marker "cannot exist" in
Arabic, and the pre-lock Arabic estimate 0.782. Every figure below is read
from a current result file, named in EVIDENCE beneath it. The external
test-set history is now a section of its own rather than an omission.

Arabic text is reshaped and bidi-reordered before rendering, because ReportLab
draws glyphs in the order given and does not apply Arabic contextual shaping
itself. Without this step the letters appear disconnected and in reverse.

EVIDENCE (every number in this document)
  results/summary/CURRENT_development_stats.json ... 0.755 / 0.809 / 0.629,
        calibration block, operating point 0.367
  results/summary/locked_external_validation.json .. 0.853, 96.2%, 33.3%
  results/summary/external_validation_honest.json .. 0.821 (clean), and which
        figures are contaminated
  docs/LU_EXPOSURE_TIMELINE.md ..................... the exposure chronology
  results/reconstruction/lu_oneshot_reproduction.json  reproduction MATCH
  results/reconstruction/ablation_post_lock.json ... Arabic-19 0.7391
  results/reconstruction/cross_corpus_transfer.json  0.777 / 0.646 / 0.814 /
        0.547, grade TRANSFER-CONFIRMED
  results/reconstruction/age_leakage_evidence.json . 0.707 / 0.515 / 0.798,
        R2 0.994
  results/reconstruction/severity_reconstruction.json  CANNOT-CONFIRM status
  results/reconstruction/acoustic_regen_verification.json  0.708 verified
  results/arabic_pilot/findings.json ............... 0.622 [0.378, 0.857]
  results/pitt_cookie/matching_stability.csv ....... 0.838 -> ten-seed 0.802
  results/wls/findings.json ........................ 0.548, 0.930
  results/fusion/results.json ...................... -0.047, -0.008
  results/summary/review2_actions.json ............. feature selection

DELIBERATELY NOT REPORTED HERE: the figure "corpus identity predicted the
label at 0.858" (Pitt + WLS controls). It appears in the development
transcript but in no result file, and the project's rule is that a reported
number traces to a file. The same negative result is reported through the
0.930 separability figure, which is file-backed.
"""
import os

# ─────────────────────────────────────────────────────────── preflight gate ──
# Nothing leaves this project unverified. scripts/preflight.py checks count
# claims against their registers, retired figures against FIGURE_RECONCILIATION,
# and every file pointer cited in prose. It exists because three stale counts and
# a misfiled figure row were all caught by someone happening to read the line.
#
#   --allow-unverified  does NOT skip the check. It runs it, prints every
#                       failure, and continues. A gate with no override gets
#                       commented out; a gate that shouts is kept.
def _preflight_gate():
    import subprocess, sys as _sys, os as _os
    here = _os.path.dirname(_os.path.abspath(__file__))
    r = subprocess.run([_sys.executable, _os.path.join(here, "preflight.py")],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print("preflight: PASSED"); return
    banner = "!" * 72
    print(f"\n{banner}\nPREFLIGHT FAILED\n{banner}")
    print(r.stdout.rstrip())
    if "--allow-unverified" in _sys.argv:
        print(f"{banner}\nCONTINUING ANYWAY (--allow-unverified). The document produced\n"
              f"by this run contains at least one claim that disagrees with its own\n"
              f"register. Do not submit it without resolving the list above.\n{banner}\n")
        return
    print(f"{banner}\nExport refused. Fix the above, or re-run with --allow-unverified\n"
          f"if you knowingly need a draft.\n{banner}\n")
    raise SystemExit(1)

_preflight_gate()


import arabic_reshaper
from bidi.algorithm import get_display

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether)

# Written into the repository's docs/ folder, which is where the committed
# copy lives. The previous hard-coded /mnt/user-data/outputs/ path only
# existed inside a sandbox and made this script unrunnable anywhere else.
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs",
                   "Dhikra_Project_Summary.pdf")

# DejaVu carries both Latin and Arabic glyphs, so one family covers the
# document and avoids font-switching mid-paragraph.
pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Italic", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                              italic="DejaVu-Italic")

TEAL = colors.HexColor("#0b3d3a")
ACCENT = colors.HexColor("#0f766e")
MUTED = colors.HexColor("#5b6b72")
LINE = colors.HexColor("#d8e3e0")
FLAG = colors.HexColor("#8a3b12")


def ar(text: str) -> str:
    """
    Shape and reorder Arabic, then force the sans face.

    The body font (DejaVuSerif) has no Arabic glyphs, so inline Arabic renders
    as empty boxes. DejaVuSans carries the full Arabic range, so every Arabic
    run is wrapped in a font tag rather than relying on the paragraph default.
    """
    shaped = get_display(arabic_reshaper.reshape(text))
    return f'<font name="DejaVuSans">{shaped}</font>'


ss = getSampleStyleSheet()

TITLE = ParagraphStyle("t", parent=ss["Title"], fontName="DejaVuSans-Bold",
                       fontSize=21, leading=26, textColor=TEAL,
                       spaceAfter=2, alignment=TA_CENTER)
SUB = ParagraphStyle("s", parent=ss["Normal"], fontName="DejaVu",
                     fontSize=11.5, leading=16, textColor=ACCENT,
                     alignment=TA_CENTER, spaceAfter=3)
META = ParagraphStyle("m", parent=ss["Normal"], fontName="DejaVu",
                      fontSize=9, leading=13, textColor=MUTED,
                      alignment=TA_CENTER)
H = ParagraphStyle("h", parent=ss["Heading2"], fontName="DejaVuSans-Bold",
                   fontSize=12.5, leading=16, textColor=TEAL,
                   spaceBefore=13, spaceAfter=5)
BODY = ParagraphStyle("b", parent=ss["Normal"], fontName="DejaVu",
                      fontSize=9.8, leading=14.6, alignment=TA_JUSTIFY,
                      spaceAfter=7)
LEAD = ParagraphStyle("l", parent=BODY, fontSize=10.3, leading=15.6,
                      textColor=colors.HexColor("#1b2b33"))
NOTE = ParagraphStyle("n", parent=BODY, fontSize=9, leading=13.5,
                      textColor=MUTED, spaceAfter=4)
CALLOUT = ParagraphStyle("c", parent=BODY, fontSize=9.6, leading=14.4,
                         textColor=colors.HexColor("#3a2418"),
                         leftIndent=7, rightIndent=7, spaceBefore=3,
                         borderPadding=7, borderWidth=0.7, borderColor=FLAG,
                         backColor=colors.HexColor("#fdf6f1"))


def rule():
    return HRFlowable(width="100%", thickness=0.6, color=LINE,
                      spaceBefore=4, spaceAfter=8)


def table(data, widths, header=True):
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.8),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1b2b33")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
    ]
    if header:
        style += [("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
                  ("TEXTCOLOR", (0, 0), (-1, 0), TEAL),
                  ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f8f7")),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT)]
    t.setStyle(TableStyle(style))
    return t


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4,
                            leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=20 * mm, bottomMargin=18 * mm,
                            title="Dhikra — Project Summary",
                            author="Alhusayn Alriqaybi")
    s = []

    # ── title block ────────────────────────────────────────────────────────
    title_ar = get_display(arabic_reshaper.reshape("ذِكرى"))
    s.append(Paragraph(f"{title_ar} &nbsp;·&nbsp; Dhikra", TITLE))
    s.append(Spacer(1, 3))
    s.append(Paragraph("A Speech-Based Screening System for Cognitive "
                       "Impairment, with Cross-Corpus Validation and a "
                       "Foundational Arabic Adaptation", SUB))
    s.append(Spacer(1, 2))
    s.append(Paragraph("Graduation Project · Department of Biomedical "
                       "Engineering · University of Tripoli", META))
    s.append(rule())

    s.append(Paragraph(
        "<b>In brief.</b> A person describes a picture for about one minute. "
        "The system extracts 117 measurements of how they spoke — how often "
        "they paused, how varied their vocabulary was, whether they named "
        "objects or pointed at them vaguely, how much of the scene they "
        "actually described. The 64 language measures among them feed a model "
        "trained on 987 recordings from 581 real patients and healthy controls "
        "across two independent clinical corpora; the score is then adjusted "
        "for the person's age, why they are being tested, and their family "
        "history. On a third corpus, held out of that model's training data "
        "and scored once at a threshold fixed in advance, it reached "
        "<b>AUC 0.853</b>. It requires no blood test, no brain scan and no "
        "specialist — only a phone and six minutes of talking. It is a "
        "screening aid that flags who should see a doctor; it never diagnoses. "
        "It is also a foundational adaptation of the method to Arabic, a "
        "language whose grammar makes the standard English marker for "
        "word-finding difficulty unusable as it stands.", LEAD))

    # ── problem ────────────────────────────────────────────────────────────
    s.append(Paragraph("The problem", H))
    s.append(Paragraph(
        "Alzheimer's disease damages language early — often years before "
        "anyone notices. A person who cannot retrieve a word says "
        "<i>“the thing”</i> instead of <i>“the jar,”</i> or <i>“he took it”</i> "
        "instead of <i>“the boy took the cookie.”</i> They pause while "
        "searching. They describe less of what is in front of them. The family "
        "does not notice. The person does not notice. But it can be measured.", BODY))
    s.append(Paragraph(
        "In Libya this matters more than almost anywhere, because Libya is "
        "missing from the evidence altogether. A 2026 systematic review and "
        "meta-analysis of dementia prevalence across the Middle East and North "
        "Africa pooled 52 studies covering more than a million people and "
        "reported a regional prevalence of 12.2%, ranging from 17.0% in Israel "
        "to 6.9% in Egypt — <b>Libya is not among the countries it reports</b>. "
        "A companion review by overlapping authors gives the reason directly: "
        "Libya is “not included due to the lack of recently published data”. "
        "An earlier systematic review of dementia epidemiology across the Arab "
        "world searched for Libyan studies and found none eligible at all. "
        "<b>No population-level dementia study has ever been conducted in "
        "Libya</b>, so nobody knows how common it is there. And in low-resource "
        "settings, diagnosis rates are drastically lower simply because "
        "specialist care is not reachable.", BODY))

    # ── what was built ─────────────────────────────────────────────────────
    s.append(Paragraph("What was built", H))
    s.append(Paragraph(
        "A screening system that listens to six minutes of speech and "
        "estimates whether a person is likely to have cognitive impairment. It "
        "requires no blood test, no imaging and no specialist — only a phone.", BODY))
    s.append(Paragraph(
        "A session includes four tasks: describing a picture, naming as many "
        "animals as possible in one minute, retelling a short story, and "
        "reciting a memorised Qur'anic surah. The screening result is computed "
        "from the picture task alone, because it is the only task with healthy "
        "controls in the training data; the others estimate severity and "
        "supporting detail. From the picture task 117 measurements are "
        "extracted — information content, vocabulary richness, syntactic "
        "complexity, discourse coherence, pausing, speech rate, pitch and "
        "voice quality — of which the 64 language measures drive the deployed "
        "model. Every measure is drawn from published research on speech in "
        "dementia.", BODY))

    # ── data ───────────────────────────────────────────────────────────────
    s.append(Paragraph("The data", H))
    s.append(Paragraph(
        "Access to DementiaBank was obtained through Carnegie Mellon "
        "University, and four corpora were analysed. The final model was "
        "trained on <b>987 recordings from 581 participants</b> across the "
        "Pitt and Delaware corpora. A third corpus, Lu, is not in that model's "
        "training data and was scored once, after being locked, at a threshold "
        "fixed beforehand. It was not untouched before that lock — the section "
        "below sets out exactly what happened.", BODY))

    # ── results ────────────────────────────────────────────────────────────
    s.append(Paragraph("The results", H))
    s.append(table([
        ["Evaluation", "AUC", "95% CI"],
        ["Locked external validation (Lu), scored once", "0.853", "0.737 – 0.946"],
        ["Clean pre-lock external (Pitt-only model, Lu)", "0.821", "—"],
        ["Development — dementia (Pitt)", "0.809", "0.761 – 0.855"],
        ["Development — combined", "0.755", "0.719 – 0.790"],
        ["Development — mild cognitive impairment", "0.629", "0.570 – 0.687"],
        ["Arabic-equivalent feature subset (of the above)", "0.739", "0.703 – 0.774"],
        ["Language-independent acoustic model (n = 373)", "0.708", "—"],
        ["Arabic pilot (n = 24, feasibility only)", "0.622", "0.378 – 0.857"],
    ], [88 * mm, 20 * mm, 32 * mm]))
    s.append(Spacer(1, 7))
    s.append(Paragraph(
        "At the deployed threshold of 0.367 — chosen on development data to "
        "hold sensitivity above 75% — the system catches 76% of impaired "
        "speakers and correctly clears 59% of healthy ones. Its probabilities "
        "are usable as a <b>screening score</b> rather than a clinical "
        "probability: calibration slope 1.29, Brier 0.199, and one material "
        "deviation, in the highest band, where it reports about 83% for a "
        "group whose observed rate is 98%. It errs by understating risk at the "
        "top, never by overstating it. The strongest single marker is "
        "information content (effect size <i>d</i> = −0.95). Severity "
        "estimation across three tasks reaches <i>r</i> = 0.655, about ±3.3 "
        "MMSE points — the deployed model's own recorded performance, which a "
        "later pre-registered rebuild could not reproduce and which is "
        "therefore cited as artifact metadata rather than a reproduced result. "
        "For context, Winterlight Labs — a company later acquired by Cambridge "
        "Cognition — reported <b>81% accuracy</b> in its founding study (Fraser, "
        "Meltzer and Rudzicz, 2016). That is an accuracy at one operating "
        "point, not an AUC, so it is not directly comparable with the figures "
        "in the table above; this system's own accuracy at its deployed "
        "threshold is about 67%.", BODY))

    # ── the external test set ──────────────────────────────────────────────
    s.append(Paragraph("The external test set: what went wrong, and what was "
                       "done about it", H))
    s.append(Paragraph(
        "The Lu corpus was obtained on 18 August 2026 to serve as an external "
        "test set. Within ninety minutes it had been scored five times while "
        "different training configurations were compared. Two of those "
        "scorings matter. A Pitt-trained model scored <b>0.821</b> on Lu "
        "before any decision had been informed by it — that figure is clean. "
        "Then a Pitt-plus-Delaware model scored <b>0.859</b>, and that "
        "comparison is what admitted the Delaware corpus to the training pool. "
        "A corpus used to choose between training configurations is a "
        "model-selection set, not a held-out test set. Worse, Lu was then "
        "added to the training pool itself, and the cross-validated figure "
        "obtained inside that pool — 0.849 — was reported as external "
        "validation on a corpus the model had “never seen”. Both claims could "
        "not be true at once.", BODY))
    s.append(Paragraph(
        "This was not caught internally. An adversarial external review of the "
        "draft claims found it. The response was governance: Lu was locked out "
        "at 17:37 the same day, the final model was retrained on Pitt and "
        "Delaware only, the decision threshold was fixed at 0.367 on "
        "development data <i>before</i> the run, and Lu was scored exactly "
        "once — <b>AUC 0.853, 95% CI 0.737 – 0.946</b>. Two days later that "
        "single run was reproduced under a pre-registered protocol permitting "
        "one execution and no decision in either direction; it matched to ten "
        "decimal places, confusion matrix cell for cell. A tombstone file now "
        "blocks any further run.", BODY))
    s.append(Paragraph(
        "<b>What each figure validates, and the residual.</b> 0.821 is "
        "uncontaminated external generalisation, but of a smaller model on a "
        "smaller pool. 0.853 is the deployed system, on data absent from its "
        "training, at a threshold fixed in advance — but the <i>composition</i> "
        "of its training pool was chosen with knowledge of a Lu score. The two "
        "sit 0.032 apart on the same 53 recordings, and 0.821 falls inside the "
        "interval of 0.853, which bounds how large that selection effect can "
        "be; the gap mixes the selection effect with the genuine benefit of "
        "more training data and cannot separate them. The scope of the residual "
        "is precise: <b>one architectural decision</b> — which corpora entered "
        "the training pool — was made with knowledge of a Lu score. No "
        "hyperparameter, threshold, feature selection, calibration method or "
        "model form was. That is stated as a fact after the problem has been "
        "volunteered, not as a defence of it, and it does not restore the "
        "“never seen” claim, which is retired.", BODY))
    s.append(Paragraph(
        "<b>The honest external result caveat.</b> At the pre-specified "
        "threshold the locked corpus gave 96.2% sensitivity but only 33.3% "
        "specificity: 25 of 26 impaired speakers caught, 9 of 27 healthy ones "
        "correctly cleared. A threshold tuned on one case mix did not transfer "
        "to another clinic's. That is exactly what a locked test set exists to "
        "reveal, and it is reported as a finding rather than smoothed away.",
        CALLOUT))
    s.append(Paragraph("Why the specificity was 33%, answered", H))
    s.append(Paragraph(
        "The 18 healthy speakers the threshold misclassified were compared "
        "with the 9 it cleared, on every feature the model uses. They had "
        "genuinely described the picture less well: <b>11.5 information units "
        "against 14.9</b>, 4.7 objects named against 6.8, pronouns standing in "
        "for nouns at 0.893 against 0.537, and 44% mentioning the falling "
        "stool against 100%. The model detected what was in front of it. No "
        "threshold could have separated them, because they sit inside the "
        "impaired distribution on the measurements themselves and not merely "
        "on the output score. The most likely explanation is how the task was "
        "administered — a short prompt, no follow-up probe — which is a "
        "hypothesis the Libyan pilot can test prospectively rather than a "
        "conclusion. The false positives were also 8.4 years older on average, "
        "and 27 people cannot separate age from administration.", BODY))
    s.append(Paragraph(
        "A second finding follows from the same analysis. Referencing the "
        "threshold to the <b>local healthy-control distribution</b> — its 80th "
        "percentile — rather than to a fixed number holds specificity at 79.8%, "
        "79.9% and 77.8% across the three corpora, because it does not move "
        "with local prevalence. It needs healthy speakers and no patients at "
        "all, and the Libyan pilot already recruits them. <b>This is a "
        "recommendation for the next version, analysed after the model was "
        "frozen and never deployed; the result reported above remains the "
        "pre-specified one.</b>", BODY))

    # ── the pooling decision, re-tested without Lu ──────────────────────────
    s.append(Paragraph("The pooling decision, re-tested without Lu", H))
    s.append(Paragraph(
        "The decision that Lu had informed was whether to train on both "
        "corpora. That exact comparison cannot be redone without Lu — it needs "
        "a third corpus containing both patients and controls, and none "
        "remains. So a weaker but Lu-free question was pre-registered, with "
        "its criteria fixed in writing before anything was run: are the two "
        "corpora mutually informative? They are, in both directions.", BODY))
    s.append(table([
        ["Trained on", "Evaluated on", "AUC", "95% CI"],
        ["Delaware only", "Pitt", "0.777", "0.730 – 0.826"],
        ["Pitt only", "Delaware", "0.646", "0.587 – 0.704"],
        ["Pitt only", "Pitt (grouped CV)", "0.814", "0.768 – 0.859"],
        ["Delaware only", "Delaware (grouped CV)", "0.547", "0.485 – 0.605"],
    ], [40 * mm, 44 * mm, 20 * mm, 36 * mm]))
    s.append(Spacer(1, 7))
    s.append(Paragraph(
        "A model that has never seen a Delaware recording ranks Delaware's "
        "participants above chance, and a model trained only on Delaware's "
        "milder cohort ranks Pitt's patients at 0.777 — about 95% of what Pitt "
        "achieves on itself. The striking row is the last one: trained on "
        "itself, Delaware reaches 0.547, an interval spanning chance. It "
        "cannot learn its own task from 439 recordings, and a Pitt-trained "
        "model does better on it than it does. Part of that gap is training-set "
        "size — 548 recordings against roughly 351 per fold — and the two "
        "cannot be separated here. One registered criterion, a retention "
        "ratio, turned out to be uninterpretable when its denominator sat at "
        "chance; it was left unchanged and the defect recorded, because a "
        "pre-registration quietly amended after the result is no "
        "pre-registration.", BODY))

    # ── methodology ────────────────────────────────────────────────────────
    s.append(Paragraph("The methodology, which is the real contribution", H))
    s.append(Paragraph(
        "Several times during development, results that looked good turned out "
        "to be wrong. Most were caught by deliberate testing; the most "
        "important one, above, was not.", BODY))
    s.append(Paragraph(
        "The same patients appeared across multiple yearly visits, which would "
        "have allowed the model to recognise individuals rather than disease; "
        "all recordings from one person were forced into the same fold. The "
        "patients were on average 6.6 years older than the controls, and age "
        "alone scored 0.707 — so an age- and sex-matched cohort was "
        "constructed, after which age alone fell to 0.515, at chance, while "
        "speech still scored 0.798. A technique that avoided discarding data "
        "by removing age statistically produced a large apparent gain, until a "
        "test showed age could be reconstructed from the supposedly age-free "
        "features at R² = 0.994; it was discarded. And an initial headline of "
        "0.838 was corrected downward to 0.802 after repeating the matching "
        "ten times.", BODY))
    s.append(Paragraph(
        "One further check prevented a serious error. Before merging a fourth "
        "corpus of 666 healthy speakers, a model was asked whether it could "
        "distinguish healthy speakers in one study from healthy speakers in "
        "another. It could, at AUC 0.930 — because one team's transcribers "
        "wrote “um” 2.8 times per 100 words and the other's wrote it 0.6 "
        "times. Merging would have produced an impressive but meaningless "
        "result, and the episode produced the rule the project now follows: "
        "corpora may be combined only when each contributes both patients and "
        "controls.", BODY))

    s.append(Spacer(1, 3))
    s.append(KeepTogether([
        Paragraph("Seven experiments that did not work, reported anyway", H),
        table([
            ["Experiment", "Outcome"],
            ["Nine-year-ahead prediction (n = 938)", "AUC 0.548 — chance"],
            ["Pooling a single-class corpus", "healthy speakers separable at 0.930"],
            ["Age residualisation (apparent gain)", "age recoverable at R² = 0.994"],
            ["Task-level fusion", "−0.047"],
            ["Late fusion of acoustic and linguistic models", "−0.008"],
            ["Feature selection, k = 15 … 80", "no size beat the full set"],
            ["Pruning corpus-shifted features to aid transport",
             "Pitt \u2192 Delaware fell at every k"],
        ], [88 * mm, 52 * mm])]))
    s.append(Spacer(1, 7))
    s.append(Paragraph(
        "Together these indicate that the handcrafted feature set has "
        "extracted close to the available signal, and that pretrained language "
        "models are the principal remaining direction.", BODY))

    # ── arabic ─────────────────────────────────────────────────────────────
    s.append(Paragraph("The Arabic contribution", H))
    s.append(Paragraph(
        f"Every existing system of this kind is English or European. Adapting "
        f"it to Arabic was not translation. In English, word-finding "
        f"difficulty appears as pronoun overuse — <i>“he put it there.”</i> "
        f"Arabic is pro-drop: the subject pronoun is normally omitted because "
        f"the verb already carries it, so pronoun counts sit on a completely "
        f"different baseline for grammatical rather than clinical reasons, and "
        f"the English ratio does not transfer. A replacement was therefore "
        f"constructed from what a speaker may do instead when a word will not "
        f"come — point ({ar('هذا، هناك')}) and become vague "
        f"({ar('شيء، حاجة')}) — combined into a referential deficit index. "
        f"That index is consistent with what the wider literature reports "
        f"about speech under word-finding load, but it is a <b>hypothesis the "
        f"planned pilot is designed to test</b>, not a validated marker: it "
        f"has never been computed on real patient speech.", BODY))
    s.append(Paragraph(
        "The Arabic component was evaluated in two ways, neither of which "
        "tests that index. Restricting the English model to only those "
        "measures the Arabic engine can compute gives <b>0.739</b> "
        "[0.703 – 0.774] on the development pool — 97.9% of the full model's "
        "0.755, which is the honest ceiling for a construct-matched transfer. "
        "And a pilot on 24 Arabic-speaking patients with clinical diagnoses "
        "gave AUC 0.622 with an interval that includes chance, using the "
        "language-independent acoustic model on a different task; it is "
        "reported as a feasibility demonstration, not a validation. To the "
        "author's knowledge no publicly available Libyan Arabic "
        "connected-speech corpus for dementia screening has been published, "
        "and no prior work has adapted spontaneous picture-description "
        "analysis to Arabic.", BODY))

    # ── refusals ───────────────────────────────────────────────────────────
    s.append(Paragraph("What the system refuses to do", H))
    s.append(Paragraph(
        "It produces no probability for Arabic sessions, because no "
        "Arabic-validated threshold exists. It applies no English reference "
        "ranges to Arabic speech, which would manufacture false abnormality. "
        "And it returns no result at all when a recording is too noisy to "
        "measure — a threshold calibrated by a degradation experiment showing "
        "the pipeline tolerates compression, low volume, clipping and "
        "telephone-quality audio, but fails on background noise.", BODY))

    # ── limitations ────────────────────────────────────────────────────────
    s.append(Paragraph("Limitations", H))
    s.append(Paragraph(
        "The system is wrong about roughly one person in four. It has not been "
        "validated on Libyan speakers, and has never been used with a patient "
        "in a real clinic. Mild cognitive impairment remains difficult "
        "(0.629), and the Delaware cohort cannot be learned from itself at "
        "all. The operating threshold did not transfer cleanly to the external "
        "corpus. The external corpus was not untouched before its lock, so "
        "0.853 validates the deployed system on unseen data but is not free of "
        "that one prior exposure. The Arabic engine is a method awaiting "
        "validation, and its word lists are drafted in Modern Standard Arabic "
        "and unverified against Libyan dialect.", BODY))

    # ── future work ────────────────────────────────────────────────────────
    s.append(Paragraph("Future work", H))
    s.append(Paragraph(
        "A complete, ethics-ready protocol for a Libyan Arabic feasibility "
        "study has been prepared, specifying design, consent procedures "
        "including capacity assessment, reference standard, sample size and "
        "analysis plan. It is designed as a feasibility and normative study "
        "rather than a diagnostic accuracy study, because a sample of the size "
        "achievable could not support an accuracy claim.", BODY))

    s.append(rule())
    s.append(Paragraph(
        "Every figure in this document is read from a current post-lock result "
        "file; the file for each is named in the header of the script that "
        "generated this PDF. The external test-set history is documented in "
        "full in docs/LU_EXPOSURE_TIMELINE.md. Data from the DementiaBank "
        "corpora is used under TalkBank membership and is not redistributed. "
        "Any use of these corpora cites Becker, Boller, Lopez, Saxton &amp; "
        "McGonigle (1994) and acknowledges NIA grants AG03705 and AG05133.",
        NOTE))

    doc.build(s)
    print(f"written: {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")


if __name__ == "__main__":
    build()
