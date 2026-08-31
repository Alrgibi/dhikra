#!/usr/bin/env python3
"""
front.py -- writes build/front.json: cover, verse, dedication, acknowledgement,
abstracts, chapter titles and the seven indices. Pass 1 writes page "0" for
every index entry; pass 2 (front.py --pages build/pages.json) fills the page
numbers measured from the rendered PDF.

Everything the author alone can supply is a bracketed placeholder — the
document is not finished until those are replaced.
"""
import json, re, sys
MODEL = json.load(open("/home/claude/work/build/model.json", encoding="utf-8"))
pages = {}
if len(sys.argv) > 2 and sys.argv[1] == "--pages":
    pages = json.load(open(sys.argv[2], encoding="utf-8"))
P = lambda key: pages.get(key, "0")

CHAPTER_TITLES = {"1": "General Introduction", "2": "Literature Review", "3": "Methodology",
                  "4": "System Design", "5": "Results And Discussion", "6": "Conclusion And Future Work"}

cover = {
    "division": "[DIVISION — e.g. Medical Instrumentation Division]",
    "title_lines": ["Dhikra (ذِكرى)",
                    "A Speech-Based Screening System For Cognitive Impairment",
                    "With Cross-Corpus Validation And A Foundational Arabic Adaptation"],
    "student": "[STUDENT FULL NAME]",
    "registration": "[REGISTRATION NUMBER]",
    "supervisor": "[SUPERVISOR NAME AND ACADEMIC TITLE]",
    "semester": "[SEMESTER — e.g. Spring 2025/2026]",
}

verse = {
    "basmala": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "text": "﴿ وَذَكِّرْ فَإِنَّ الذِّكْرَىٰ تَنفَعُ الْمُؤْمِنِينَ ﴾",
    "ref": "سورة الذاريات، الآية 55",
}

dedication = [
    "To my parents, whose patience made this work possible; to my teachers in the Department of Biomedical Engineering, who taught that the right question matters more than the answer; and to every family in Libya caring for someone whose memory is fading, and doing so without the instruments this work hopes one day to provide.",
    
]

acknowledgement = [
    "Thanks are due first to [SUPERVISOR NAME AND ACADEMIC TITLE], whose supervision of this project is gratefully acknowledged, and to the staff of the Department of Biomedical Engineering, Faculty of Engineering, University of Tripoli.",
    "The English speech corpora used in this project were obtained through DementiaBank, a shared database of the TalkBank project. The Pittsburgh corpus was collected with the support of National Institute on Aging grants AG03705 and AG05133, and its use here follows the TalkBank membership agreement; the Delaware and Lu corpora were used under the same agreement. The Wisconsin Longitudinal Study data were used for the prospective analysis reported in Chapter 5. None of these corpora leaves the project, and none is reproduced in this document.",
    "The Libyan pathway described in Chapter 6 was shaped by the willingness of a national patient organisation to discuss recruitment feasibility and cultural acceptability; that engagement is acknowledged without attributing to it any review, assessment or endorsement of the work.",
    
]

abstract_en = [
    "Cognitive impairment is under-recognised where memory-clinic infrastructure is thin, and Libya has no population-level dementia prevalence study. Connected speech degrades early in the disease and can be recorded with a telephone, so a family member or health worker could administer a speech-based screen. This project built and evaluated such an instrument, Dhikra, under a validation discipline the field has rarely applied: participant-grouped cross-validation, pre-registered analyses with grades fixed in advance, one locked external evaluation, and every negative result reported.",
    "Dhikra extracts 117 speech and language measures across five families. Its externally evaluated English screening model uses a frozen 64-feature transcript-derived subset of linguistic, information-content and discourse-semantic measures; 53 acoustic measures support a separate language-independent pathway. The screening model, a calibrated soft-voting ensemble over that subset, was trained on 987 one-minute picture descriptions from 581 participants of two DementiaBank corpora. Development discrimination was AUC 0.7550 [0.7192, 0.7902], 0.8095 [0.7612, 0.8552] for the dementia target and 0.6291 [0.5703, 0.6868] for mild cognitive impairment, the target where the picture-description architecture performs weakly and connected discourse proved the more promising genre. Scored once on a third corpus at a threshold fixed in advance, the frozen English screening model reached external AUC 0.8533 [0.7371, 0.9458], sensitivity 96.2%, specificity 33.3%; the corpus was excluded from the training data of the final model and from every modelling decision after the lock. Before the lock, five exploratory scorings occurred, one of which informed the decision to include Delaware in the development pool.  Subsequent threshold-transport analysis recovered external specificity to 77.8% by control-referenced thresholding — a post-hoc methodological contribution, not preregistered, not deployed, and requiring prospective validation. Fifteen further hypotheses were tested and found negative; three changed the design.",
    "The Arabic arm is a method awaiting validation: an Arabic linguistic engine verified on constructed examples, an acoustic language-independent model whose 24-recording pilot gave AUC 0.622 [0.378, 0.857] as a feasibility result only, a culturally adapted task battery, an ethics-ready pilot protocol and a specification of the corpus a Libyan validation requires. The instrument has never been used with a patient. What the thesis claims is an English-validated screening method, culturally adapted for Libyan validation, with its evidence graded component by component.",
]

abstract_ar_title = "الملخص"
abstract_ar = [
    "يبقى الضعف المعرفي دون تشخيص في الأماكن التي تفتقر إلى عيادات الذاكرة، ولا توجد في ليبيا أي دراسة لانتشار الخرف على مستوى السكان. يتدهور الكلام المتصل في مرحلة مبكرة من المرض ويمكن تسجيله بهاتف، مما يجعله مرشحاً لأداة فحص يستطيع أحد أفراد الأسرة أو عامل صحي إجراءها. بنى هذا المشروع أداةً من هذا النوع، «ذِكرى»، وقيّمها وفق انضباط في التحقق نادراً ما طُبِّق في هذا المجال: تحقق متقاطع مجمَّع حسب المشارك، وتحليلات مسجَّلة مسبقاً بدرجات محددة قبل التنفيذ، وتقييم خارجي واحد مقفل، ونشر كل نتيجة سلبية.",
    "تستخرج «ذِكرى» 117 مقياساً للكلام واللغة عبر خمس عائلات؛ ويستخدم نموذج الفحص الإنجليزي المقيَّم خارجياً مجموعة فرعية مجمَّدة من 64 سمة مستخرجة من النص، بينما تدعم 53 مقياساً صوتياً مساراً منفصلاً مستقلاً عن اللغة. دُرِّب نموذج الفحص، وهو نموذج تجميعي معايَر بالتصويت الناعم على تلك المجموعة الفرعية المستخرجة من وصف صورة لمدة دقيقة واحدة، على 987 تسجيلاً من 581 مشاركاً في مجموعتين من DementiaBank. بلغت قدرة التمييز في مرحلة التطوير مساحة تحت المنحنى 0.7550 [0.7192، 0.7902]، و0.8095 [0.7612، 0.8552] لهدف الخرف، و0.6291 [0.5703، 0.6868] للضعف المعرفي البسيط، وهو الهدف الذي تضعف فيه بنية وصف الصورة المنشورة، والذي تبيّن أن الخطاب المتصل هو نوع الاستثارة الأكثر وعداً له. وعند تقييم نموذج الفحص الإنجليزي المجمَّد مرة واحدة على مجموعة ثالثة عند عتبة حُدِّدت مسبقاً، كان الأداء الخارجي المقفل: مساحة تحت المنحنى 0.8533 [0.7371، 0.9458]، وحساسية 96.2%، ونوعية 33.3%؛ وقد استُبعدت هذه المجموعة من بيانات تدريب النموذج النهائي ومن كل قرار نمذجة بعد الإقفال؛ وقبل الإقفال جرت خمسة تقييمات استكشافية، أثّر أحدها في قرار ضمّ مجموعة ديلاوير إلى مجموعة التطوير. وقد استعاد تحليلٌ لاحق لنقل العتبة النوعيةَ الخارجية إلى 77.8% عبر عتبة مرجعية بالضوابط — وهي مساهمة منهجية لاحقة، غير مسجَّلة مسبقاً، وغير منشورة للاستخدام، وتتطلب تحققاً استباقياً. واختُبرت خمس عشرة فرضية أخرى فتبيّن أنها سلبية، غيّرت ثلاث منها التصميم.",
    "أما الشق العربي فهو منهج في انتظار التحقق: محرك لغوي عربي جرى التحقق منه على أمثلة مبنية فقط، ونموذج صوتي مستقل عن اللغة أعطى في تجربة أولية من 24 تسجيلاً مساحة تحت المنحنى 0.622 [0.378، 0.857] بوصفها نتيجة جدوى لا أكثر، وبطارية مهام مكيَّفة ثقافياً، وبروتوكول جدوى جاهز للجنة الأخلاقيات، ومواصفة كاملة للمدونة التي يتطلبها التحقق الليبي. لم تُستخدم الأداة قط مع مريض. ما تدّعيه هذه الرسالة هو منهج فحص متحقَّق منه بالإنجليزية، مكيَّف ثقافياً للتحقق الليبي، مع تصنيف أدلته مكوِّناً مكوِّناً.",
]

terms = [
    ["Area under the receiver-operating-characteristic curve", "The probability that a randomly chosen impaired recording receives a higher screening score than a randomly chosen healthy one; 0.5 is chance and 1.0 is perfect discrimination."],
    ["Calibration", "The agreement between the screening score and the observed proportion of impaired speakers at that score, summarised by a slope and an intercept."],
    ["Confidence interval", "The range within which the true value of a figure is expected to lie with the stated probability, here always 95%."],
    ["Control-referenced threshold", "A screening threshold set at a chosen percentile of the healthy group's scores in the deployment cohort, so that it reads no impairment labels."],
    ["Corpus", "A collection of speech recordings and transcripts collected under one protocol."],
    ["Cross-validation, participant-grouped", "An evaluation in which every recording of a participant is kept in the same fold, so no speaker appears in both training and test data."],
    ["Decision-curve analysis", "A method expressing the value of acting on a screening result as a net benefit across the probabilities at which a decision-maker would act."],
    ["Dementia", "A syndrome of acquired cognitive decline beyond ordinary ageing that interferes with daily function; Alzheimer's disease is its most common cause."],
    ["Discourse-semantic feature", "A measure of how a description holds together across utterances, computed from distributional word vectors."],
    ["External validation", "The evaluation of a frozen model on a corpus collected by other investigators and excluded from its training."],
    ["Feature", "One numeric measurement computed from a recording or its transcript; the deployed model uses 64."],
    ["Information unit", "One of the 23 canonical people, objects, places and actions in the picture; the count is the strongest single marker."],
    ["Likelihood ratio", "The factor by which a screening score multiplies the prior odds of impairment."],
    ["Lock", "The moment after which the external corpus entered no decision and the model, features and threshold were frozen."],
    ["Mild cognitive impairment", "Measurable cognitive decline greater than expected for age that does not yet interfere with independence; the harder screening target."],
    ["Minimal detectable change", "The smallest change in a repeated measurement that exceeds the measurement error at 95% confidence."],
    ["Negative result", "A pre-specified hypothesis that was tested and not supported; fifteen are reported in Chapter 5."],
    ["Operating threshold", "The fixed screening-score cut-off, 0.367, above which a recording is flagged for referral."],
    ["Picture description", "The task in which a participant describes a drawn scene for about one minute; the only task the screening score is computed from."],
    ["Pre-registration", "Fixing the criterion, the grade words and the interpretation of an analysis in a committed file before the analysis is run."],
    ["Referential deficit index", "A measure of vague reference — pronouns and empty nouns standing where names would be — proposed as the Arabic replacement marker."],
    ["Screening", "Flagging people whose speech resembles that of diagnosed patients so they can be referred for assessment; not diagnosis."],
    ["Sensitivity", "The proportion of impaired speakers the instrument flags at the operating threshold."],
    ["Specificity", "The proportion of healthy speakers the instrument does not flag at the operating threshold."],
    ["Standard error of measurement", "The expected difference between two recordings of the same unchanged speaker, expressed in score units."],
    ["Transcript", "The written form of a recording, typed by the operator or produced by automatic transcription."],
]

abbreviations = [
    ["AD", "Alzheimer's Disease"],
    ["ADReSS", "Alzheimer's Dementia Recognition through Spontaneous Speech (the 2020 challenge)"],
    ["ADReSSo", "Alzheimer's Dementia Recognition through Spontaneous Speech only (the 2021 challenge)"],
    ["AI", "Artificial Intelligence"],
    ["AUC", "Area Under the receiver-operating-characteristic Curve"],
    ["BMJ", "British Medical Journal"],
    ["CHAT", "Codes for the Human Analysis of Transcripts (the TalkBank transcription format)"],
    ["CI", "Confidence Interval"],
    ["GP", "General Practitioner"],
    ["ICC", "Intraclass Correlation Coefficient"],
    ["ILSE", "Interdisciplinary Longitudinal Study of Adult Development and Aging"],
    ["LOSO", "Leave-One-Subject-Out cross-validation"],
    ["LR", "Likelihood Ratio"],
    ["MCI", "Mild Cognitive Impairment"],
    ["MDC", "Minimal Detectable Change"],
    ["MENA", "Middle East and North Africa"],
    ["MMSE", "Mini-Mental State Examination"],
    ["MoCA", "Montreal Cognitive Assessment"],
    ["NHS", "National Health Service"],
    ["NLP", "Natural Language Processing"],
    ["NPV", "Negative Predictive Value"],
    ["PPV", "Positive Predictive Value"],
    ["PROBAST+AI", "Prediction model Risk Of Bias Assessment Tool, artificial-intelligence extension"],
    ["RDI", "Referential Deficit Index"],
    ["ROC", "Receiver Operating Characteristic"],
    ["RR", "Relative Risk"],
    ["SD", "Standard Deviation"],
    ["SEM", "Standard Error of Measurement"],
    ["SHARE-HCAP", "Survey of Health, Ageing and Retirement in Europe, Harmonized Cognitive Assessment Protocol"],
    ["SNR", "Signal-to-Noise Ratio"],
    ["STARD-AI", "Standards for Reporting of Diagnostic Accuracy Studies, artificial-intelligence extension"],
    ["TAUKADIAL", "The 2024 multilingual (English and Chinese) connected-speech cognitive-assessment challenge"],
    ["TRIPOD+AI", "Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis, artificial-intelligence extension"],
    ["WHO", "World Health Organization"],
]

symbols = [
    ["AUC", "area under the receiver-operating-characteristic curve"],
    ["[a, b]", "a 95% confidence interval from a to b"],
    ["n", "number of recordings or participants, as stated"],
    ["k", "number of information units displaced, or number of tasks, as stated"],
    ["d", "standardised mean difference (Cohen's d)"],
    ["g", "Hedges' g, the small-sample-corrected standardised mean difference"],
    ["r", "Pearson correlation coefficient"],
    ["ρ", "Spearman rank correlation coefficient"],
    ["R²", "coefficient of determination"],
    ["p", "probability value of a statistical test, or, as p(x), a predicted probability"],
    ["α", "significance level of a test"],
    ["Δ", "difference between two figures"],
    ["π₀", "prior probability of impairment in the training pool (0.4711)"],
    ["LR(x)", "likelihood ratio contributed by a speech score x"],
    ["SEM", "standard error of measurement"],
    ["MDC95", "minimal detectable change at 95% confidence"],
    ["×", "multiplication, as in a referral multiplier of ×2.5"],
    ["→", "transfer direction, as in Pittsburgh → Delaware"],
]

# ---------- indices ----------
def first_sentence(text, limit=400, short=60, tolerate=62):
    """the caption's title: its first sentence; when that is longer than `tolerate` characters it is cut back to a
    clause boundary before `short` characters (dash, colon or semicolon first, then a comma, then a function word),
    so that an index entry takes one line"""
    body = re.sub(r"^(Figure|Table) \([^)]*\):\s*", "", text)
    m = re.search(r"\.(\s|$)", body)
    s = body[:m.start()] if m and m.start() < limit else body[:limit].rstrip()
    if len(s) > tolerate:
        for seps in ([" — ", ": ", "; "], [", "], [" and ", " that ", " with ", " against ", " for ", " of ", " by ", " under ", " between ", " in ", " on "]):
            cut = max(s.rfind(sep, 0, short) for sep in seps)
            if cut >= 18:
                s = s[:cut].rstrip(); break
    return s

contents = [
    {"text": "Dedication", "page": P("fm_dedication"), "bookmark": "fm_dedication", "indent": 0, "bold": True},
    {"text": "Acknowledgement", "page": P("fm_ack"), "bookmark": "fm_ack", "indent": 0, "bold": True},
    {"text": "Abstract", "page": P("fm_abstract"), "bookmark": "fm_abstract", "indent": 0, "bold": True},
    {"text": "Abstract in Arabic", "page": P("fm_abstract_ar"), "bookmark": "fm_abstract_ar", "indent": 0, "bold": True},
    {"text": "Table of Contents", "page": P("fm_contents"), "bookmark": "fm_contents", "indent": 0, "bold": True},
    {"text": "Index of Figures", "page": P("fm_figures"), "bookmark": "fm_figures", "indent": 0, "bold": True},
    {"text": "Index of Tables", "page": P("fm_tables"), "bookmark": "fm_tables", "indent": 0, "bold": True},
    {"text": "Index of Scientific Terms", "page": P("fm_terms"), "bookmark": "fm_terms", "indent": 0, "bold": True},
    {"text": "Index of Abbreviations", "page": P("fm_abbr"), "bookmark": "fm_abbr", "indent": 0, "bold": True},
    {"text": "Index of Symbols", "page": P("fm_symbols"), "bookmark": "fm_symbols", "indent": 0, "bold": True},
    {"text": "Index of Appendices", "page": P("fm_appendices"), "bookmark": "fm_appendices", "indent": 0, "bold": True},
]
figs, tabs, apps = [], [], []
for c in MODEL["chapters"]:
    contents.append({"text": f"Chapter {c['id']}  {CHAPTER_TITLES[str(c['id'])]}", "page": P(f"ch_{c['id']}"), "bookmark": f"ch_{c['id']}", "indent": 0, "bold": True})
    for b in c["blocks"]:
        if b["type"] == "heading":
            bid = "h_" + b["number"].replace(".", "_")
            contents.append({"text": f"{b['number']}  {b['text']}", "page": P(bid), "bookmark": bid, "indent": 360 if b["level"] == 2 else 720, "bold": False})
        elif b["type"] == "caption":
            bid = f"c_{b['kind']}_{b['chapter']}_{b['n']}"
            (figs if b["kind"] == "Figure" else tabs).append({"text": f"{b['kind']} ({b['chapter']}.{b['n']})  {first_sentence(b['text'])}", "page": P(bid), "bookmark": bid})
contents.append({"text": "References", "page": P("references"), "bookmark": "references", "indent": 0, "bold": True})
for a in MODEL["appendices"]:
    contents.append({"text": f"Appendix {a['id']}  {a['title']}", "page": P(f"app_{a['id']}"), "bookmark": f"app_{a['id']}", "indent": 0, "bold": True})
    apps.append({"text": f"Appendix {a['id']}  {a['title']}", "page": P(f"app_{a['id']}"), "bookmark": f"app_{a['id']}"})
    for b in a["blocks"]:
        if b["type"] == "heading":
            bid = "h_" + b["number"].replace(".", "_")
            contents.append({"text": f"{b['number']}  {b['text']}", "page": P(bid), "bookmark": bid, "indent": 360 if b["level"] == 2 else 720, "bold": False})
        elif b["type"] == "caption":
            bid = f"c_{b['kind']}_{b['chapter']}_{b['n']}"
            (figs if b["kind"] == "Figure" else tabs).append({"text": f"{b['kind']} ({b['chapter']}.{b['n']})  {first_sentence(b['text'])}", "page": P(bid), "bookmark": bid})

front = {"cover": cover, "verse": verse, "dedication": dedication, "acknowledgement": acknowledgement,
         "abstract_en": abstract_en, "abstract_ar_title": abstract_ar_title, "abstract_ar": abstract_ar,
         "chapter_titles": CHAPTER_TITLES,
         "indices": {"contents": contents, "figures": figs, "tables": tabs, "terms": terms,
                     "abbreviations": abbreviations, "symbols": symbols, "appendices": apps}}
json.dump(front, open("/home/claude/work/build/front.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("front.json:", len(contents), "contents lines,", len(figs), "figures,", len(tabs), "tables,", len(apps), "appendices; pages known:", len(pages))
