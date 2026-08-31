"""
make_summary_pdf_ar.py
----------------------
Arabic (RTL) edition of the project summary.

REWRITTEN 2026-08-22, mirroring make_summary_pdf.py. The previous version was
written before the Lu lock and carried the same five classes of stale or
overstated content: pre-lock figures, the pre-lock calibration block, the
claim that Lu was reserved untouched and "never seen"
(لم يرها النموذج قط / استُبعدت عمداً من كل قرارات التطوير), the claim that the
English pronoun marker cannot exist in Arabic
(لا يمكن أن يوجد المؤشر الإنجليزي فيها), and the pre-lock Arabic estimate
0.782. Every figure is now read from a current post-lock result file; the
evidence list is the one in make_summary_pdf.py, which this document mirrors
section for section. The figure "0.858" is likewise omitted here: it appears
in the development transcript but in no result file.

THREE THINGS THIS HAS TO GET RIGHT

 1. SHAPING. Arabic letters change form depending on their neighbours.
    ReportLab draws glyphs exactly as given and applies no contextual shaping,
    so every string is passed through arabic_reshaper first or the letters
    appear disconnected.

 2. BIDIRECTIONAL ORDER. Arabic runs right to left while numbers and Latin
    terms inside it run left to right. The Unicode bidi algorithm resolves
    this, and get_display applies it. Verified: "AUC 0.853" stays readable
    inside an Arabic sentence.

 3. NO INLINE MARKUP. Reordering moves ReportLab's <b> and <i> tags along with
    the text, producing broken markup. Arabic paragraphs are therefore plain
    text, and emphasis is carried by paragraph-level styles instead.

Tables are built with their columns reversed so the first logical column sits
on the right, which is where an Arabic reader begins.
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
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether)

# Written into the repository's docs/ folder, which is where the committed
# copy lives. The previous hard-coded /mnt/user-data/outputs/ path only
# existed inside a sandbox and made this script unrunnable anywhere else.
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs",
                   "Dhikra_Project_Summary_Arabic.pdf")

pdfmetrics.registerFont(TTFont("AR", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("AR-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

TEAL = colors.HexColor("#0b3d3a")
ACCENT = colors.HexColor("#0f766e")
MUTED = colors.HexColor("#5b6b72")
LINE = colors.HexColor("#d8e3e0")


from reportlab.pdfbase.pdfmetrics import stringWidth

# Usable text width, minus a safety margin. ReportLab measures the reordered
# string slightly differently from the pre-wrap measurement, and without the
# margin it re-wraps the last word of every line onto a line of its own.
AVAIL = (A4[0] - 44 * mm) * 0.94


def A(text: str) -> str:
    """Shape and bidi-reorder a SHORT Arabic string (headings, table cells)."""
    return get_display(arabic_reshaper.reshape(text))


def A_wrap(text: str, style, width: float = None) -> str:
    """
    Shape and reorder a multi-line Arabic paragraph.

    Bidi reordering must be applied PER LINE. Applying it to a whole paragraph
    reverses the entire string, so when ReportLab then wraps it the lines come
    out in reverse order -- the last line of the paragraph appears first. The
    text is therefore wrapped here, line by line, and each line is reordered
    independently before being joined with explicit breaks.
    """
    width = width or AVAIL
    words, lines, cur = text.split(), [], []
    for w in words:
        trial = " ".join(cur + [w])
        if (stringWidth(arabic_reshaper.reshape(trial), style.fontName,
                        style.fontSize) <= width) or not cur:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return "<br/>".join(A(l) for l in lines)


ss = getSampleStyleSheet()
TITLE = ParagraphStyle("t", parent=ss["Title"], fontName="AR-Bold", fontSize=21,
                       leading=27, textColor=TEAL, alignment=TA_CENTER, spaceAfter=2)
SUB = ParagraphStyle("s", parent=ss["Normal"], fontName="AR", fontSize=11.5,
                     leading=19, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=3)
META = ParagraphStyle("m", parent=ss["Normal"], fontName="AR", fontSize=9,
                      leading=15, textColor=MUTED, alignment=TA_CENTER)
H = ParagraphStyle("h", parent=ss["Heading2"], fontName="AR-Bold", fontSize=12.5,
                   leading=19, textColor=TEAL, alignment=TA_RIGHT,
                   spaceBefore=13, spaceAfter=5)
BODY = ParagraphStyle("b", parent=ss["Normal"], fontName="AR", fontSize=10,
                      leading=19, alignment=TA_RIGHT, spaceAfter=7,
                      wordWrap="RTL")
LEAD = ParagraphStyle("l", parent=BODY, fontSize=10.4, leading=20,
                      textColor=colors.HexColor("#1b2b33"))
NOTE = ParagraphStyle("n", parent=BODY, fontSize=8.8, leading=16,
                      textColor=MUTED, spaceAfter=4)
FLAG = colors.HexColor("#8a3b12")
CALLOUT = ParagraphStyle("c", parent=BODY, fontSize=9.6, leading=18,
                         textColor=colors.HexColor("#3a2418"),
                         leftIndent=7, rightIndent=7, spaceBefore=3,
                         borderPadding=7, borderWidth=0.7, borderColor=FLAG,
                         backColor=colors.HexColor("#fdf6f1"))


def rule():
    return HRFlowable(width="100%", thickness=0.6, color=LINE,
                      spaceBefore=4, spaceAfter=8)


def rtl_table(rows, widths):
    """Build a table with columns reversed, so reading starts on the right."""
    data = [[Paragraph(A(c), ParagraphStyle(
        "c", fontName="AR-Bold" if i == 0 else "AR", fontSize=9, leading=15,
        alignment=TA_RIGHT, textColor=TEAL if i == 0 else colors.HexColor("#1b2b33")))
        for c in reversed(r)] for i, r in enumerate(rows)]
    t = Table(data, colWidths=list(reversed(widths)), hAlign="RIGHT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f8f7")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
    ]))
    return t


def P(text, style=BODY):
    """Headings and short lines need no wrapping; body text does."""
    if style in (H, META):
        return Paragraph(A(text), style)
    if style is SUB:
        # centred but multi-line, so it still needs per-line reordering
        return Paragraph(A_wrap(text, style, AVAIL * 0.82), style)
    if style is CALLOUT:
        # the box has its own indents and padding, so it wraps narrower
        return Paragraph(A_wrap(text, style, AVAIL - 34), style)
    return Paragraph(A_wrap(text, style), style)


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4,
                            leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=20 * mm, bottomMargin=18 * mm,
                            title="ذِكرى — ملخص المشروع",
                            author="الحسين الرقيبي")
    s = []

    s.append(Paragraph(f"{A('ذِكرى')} &nbsp;·&nbsp; Dhikra", TITLE))
    s.append(Spacer(1, 3))
    s.append(P("نظامٌ للفحص المبكر للاختلال المعرفي اعتماداً على تحليل الكلام، "
               "مع تحقُّقٍ عبر مدوَّنات متعددة وتكييفٍ تأسيسي للغة العربية", SUB))
    s.append(Spacer(1, 2))
    s.append(P("مشروع تخرّج · قسم الهندسة الطبية الحيوية · جامعة طرابلس", META))
    s.append(rule())

    s.append(P(
        "باختصار: يَصِف الشخص صورةً لمدة دقيقة تقريباً، فيستخرج النظام مئةً "
        "وسبع عشرة خاصية من خصائص كلامه: عدد وقفاته ومُددها، ومدى ثراء "
        "مفرداته، وهل سمَّى الأشياء بأسمائها أم أشار إليها إشارةً مبهمة، وكم "
        "وصف فعلاً من تفاصيل المشهد. ومنها تُغذِّي القياساتُ اللغوية الأربعة "
        "والستون نموذجاً دُرِّب على 987 تسجيلاً من 581 مشاركاً بين مرضى "
        "حقيقيين وأصحّاء، من مدوَّنتين سريريتين مستقلتين، ثم تُعدَّل النتيجة "
        "وفق عمر الشخص وسبب إجراء الفحص وتاريخه العائلي. وعلى مدوَّنةٍ ثالثة "
        "ليست ضمن بيانات تدريب هذا النموذج، قُيِّم عليها مرةً واحدة بعتبةٍ "
        "حُدِّدت سلفاً، بلغ النظام مساحةً تحت المنحنى (AUC) قدرها 0.853. لا "
        "يحتاج النظام إلى تحليل دم ولا تصوير دماغي ولا طبيبٍ مختص، بل إلى "
        "هاتفٍ وستِّ دقائق من الحديث. وهو أداة فحصٍ مبدئي تُنبِّه إلى من ينبغي "
        "أن يراجع الطبيب، ولا يُشخِّص أبداً. وهو كذلك تكييفٌ تأسيسي لهذه "
        "المنهجية للغة العربية، وهي لغةٌ يجعل نحوُها المؤشرَ الإنجليزي "
        "المعياري لصعوبة استحضار الكلمات غير قابلٍ للنقل كما هو.", LEAD))

    s.append(P("المشكلة", H))
    s.append(P(
        "يُصيب مرض الزهايمر اللغةَ في مراحله المبكرة، وغالباً قبل سنوات من "
        "انتباه أحد. فالشخص الذي يعجز عن استحضار كلمة يقول «هذا الشيء» بدلاً من "
        "«البرطمان»، ويقول «أخذه» بدلاً من «أخذ الولد قطعة الحلوى». يتوقف "
        "باحثاً عن الكلمة، ويصف أقل مما يراه أمامه. لا تنتبه الأسرة، ولا ينتبه "
        "هو نفسه. غير أنّ ذلك كلَّه قابل للقياس.", BODY))
    s.append(P(
        "وفي ليبيا تحديداً تزداد أهمية هذا الأمر، لأنّ ليبيا غائبة عن الأدلة "
        "أصلاً. فقد جمعت مراجعةٌ منهجية وتحليلٌ بَعدي صدرا عام 2026 حول انتشار "
        "الخرف في الشرق الأوسط وشمال أفريقيا 52 دراسة شملت أكثر من مليون شخص، "
        "وأبلغا عن انتشارٍ إقليمي قدره 12.2%، يتراوح بين 17.0% في إسرائيل و6.9% "
        "في مصر — وليبيا ليست من البلدان التي أوردتها. وتذكر مراجعةٌ مرافقة "
        "لباحثين مشتركين السببَ صراحةً: لم تُدرَج ليبيا بسبب غياب بيانات منشورة "
        "حديثة. كما بحثت مراجعةٌ منهجية أسبق عن دراسات ليبية في وبائيات الخرف "
        "عبر العالم العربي فلم تجد أيّ دراسةٍ مؤهَّلة. ولم تُجرَ في ليبيا قط "
        "دراسةٌ سكانية عن الخرف، فلا أحد يعرف كم ينتشر فيها. كما أنّ معدلات "
        "التشخيص في البيئات محدودة الموارد أدنى بكثير، لأنّ الرعاية التخصصية "
        "ببساطة غير متاحة.", BODY))

    s.append(P("ما الذي بُني", H))
    s.append(P(
        "نظام فحصٍ يستمع إلى ستِّ دقائق من الكلام ويُقدِّر احتمال وجود اختلال "
        "معرفي لدى الشخص، دون الحاجة إلى تحليل دم أو تصوير أو طبيبٍ مختص، بل "
        "إلى هاتف فحسب.", BODY))
    s.append(P(
        "تتضمن الجلسة أربع مهام: وصف صورة، وذكر أكبر عدد ممكن من أسماء "
        "الحيوانات في دقيقة واحدة، وإعادة سرد قصة قصيرة، وتلاوة سورة محفوظة من "
        "القرآن الكريم. وتُحسَب نتيجة الفحص من مهمة وصف الصورة وحدها، لأنها "
        "المهمة الوحيدة التي تتوفر لها مجموعة ضابطة من الأصحّاء في بيانات "
        "التدريب؛ أما البقية فتُقدِّر شدة الحالة والتفاصيل المساندة. ومن مهمة "
        "وصف الصورة تُستخرَج مئة وسبع عشرة قياساً: محتوى المعلومات، وثراء "
        "المفردات، والتعقيد النحوي، وترابط الخطاب، والوقفات، وسرعة الكلام، "
        "وطبقة الصوت، وجودته؛ ومنها القياسات اللغوية الأربعة والستون التي "
        "يقوم عليها النموذج المنشور. وكل قياسٍ منها مستمدٌّ من أبحاث منشورة "
        "حول الكلام في الخرف.", BODY))

    s.append(P("البيانات", H))
    s.append(P(
        "حُصِل على صلاحية الوصول إلى قاعدة DementiaBank عبر جامعة كارنيجي "
        "ميلون، وحُلِّلت أربع مدوَّنات. ودُرِّب النموذج النهائي على 987 تسجيلاً "
        "من 581 مشاركاً من مدوَّنتَي Pitt وDelaware. أمّا المدوَّنة الثالثة Lu "
        "فليست ضمن بيانات تدريب هذا النموذج، وقُيِّم عليها مرةً واحدة بعد "
        "إغلاقها، بعتبةٍ حُدِّدت سلفاً. غير أنها لم تكن سليمةً من كل مساس قبل "
        "ذلك الإغلاق، والقسم أدناه يبيِّن بالضبط ما الذي جرى.", BODY))

    s.append(P("النتائج", H))
    s.append(rtl_table([
        ["التقييم", "AUC", "فاصل الثقة 95%"],
        ["التحقق الخارجي المغلق (Lu)، مرة واحدة", "0.853", "0.737 – 0.946"],
        ["الرقم الخارجي النظيف قبل الإغلاق (نموذج Pitt)", "0.821", "—"],
        ["التطوير — الخرف (Pitt)", "0.809", "0.761 – 0.855"],
        ["التطوير — مجتمعاً", "0.755", "0.719 – 0.790"],
        ["التطوير — الاختلال المعرفي الخفيف", "0.629", "0.570 – 0.687"],
        ["المجموعة المكافئة عربياً (من الخصائص نفسها)", "0.739", "0.703 – 0.774"],
        ["النموذج الصوتي المستقل عن اللغة (373)", "0.708", "—"],
        ["التجربة العربية (24 مشاركاً، جدوى فقط)", "0.622", "0.378 – 0.857"],
    ], [80 * mm, 22 * mm, 38 * mm]))
    s.append(Spacer(1, 8))
    s.append(P(
        "عند عتبة التشغيل المعتمدة 0.367 — وقد اختيرت على بيانات التطوير "
        "لإبقاء الحساسية فوق 75% — يكتشف النظام 76% من المصابين ويُبرِّئ بشكل "
        "صحيح 59% من الأصحّاء. وتصلح مخرجاته درجةَ فحصٍ مبدئي لا احتمالاً "
        "سريرياً: ميل المعايرة 1.29، ودرجة براير 0.199، وانحرافٌ جوهري واحد في "
        "الشريحة العليا حيث يُعطي نحو 83% لفئةٍ نسبتها الملاحَظة 98%؛ أي أنه "
        "يُقلِّل من تقدير الخطر في الأعلى ولا يبالغ فيه أبداً. وأقوى مؤشر منفرد "
        "هو محتوى المعلومات، بحجم أثرٍ قدره d = −0.95. ويبلغ تقدير شدة الحالة "
        "عبر ثلاث مهام r = 0.655 بدقةٍ تعادل ±3.3 من درجات اختبار MMSE، وهو "
        "الأداء المسجَّل داخل النموذج المنشور نفسه؛ وقد عجزت إعادة بناءٍ "
        "مُسجَّلة سلفاً عن استنساخه، فيُذكَر بوصفه بياناً وصفياً للنموذج لا "
        "نتيجةً أُعيد إنتاجها. وللمقارنة، فإنّ شركة Winterlight Labs — التي "
        "استحوذت عليها لاحقاً Cambridge Cognition — أبلغت عن دقة تصنيفٍ قدرها "
        "81% في دراستها التأسيسية. وهي دقةٌ عند نقطة تشغيلٍ واحدة لا مساحةٌ "
        "تحت المنحنى، فلا تُقارَن مباشرةً بأرقام الجدول أعلاه؛ ودقة هذا "
        "النظام عند عتبته المعتمدة تبلغ نحو 67%.", BODY))

    s.append(P("مجموعة الاختبار الخارجية: ما الذي حدث، وما الذي فُعِل", H))
    s.append(P(
        "حُصِل على مدوَّنة Lu في 18 أغسطس 2026 لتكون مجموعة اختبار خارجية. وفي "
        "غضون تسعين دقيقة كانت قد قُيِّمت عليها خمس مرات أثناء المقارنة بين "
        "تشكيلات تدريب مختلفة. ومن تلك التقييمات اثنان لهما أثر: فقد سجَّل "
        "نموذجٌ مُدرَّب على Pitt وحدها 0.821 على Lu قبل أن يكون أيُّ قرار قد "
        "استُرشد بها، وهذا الرقم نظيف. ثم سجَّل نموذج Pitt وDelaware معاً "
        "0.859، وتلك المقارنة بعينها هي ما أدخل مدوَّنة Delaware إلى مجموعة "
        "التدريب. والمدوَّنة التي تُستعمل للاختيار بين تشكيلات التدريب تصير "
        "مجموعةَ اختيارٍ للنموذج لا مجموعةَ اختبارٍ محجوزة. والأسوأ أنّ Lu "
        "أُضيفت بعد ذلك إلى مجموعة التدريب نفسها، ثم أُبلغ عن الرقم المُستخرَج "
        "بالتحقق المتقاطع داخل تلك المجموعة — 0.849 — بوصفه تحققاً خارجياً على "
        "مدوَّنةٍ «لم يرها النموذج قط». ولا يمكن أن يصحّ الأمران معاً.", BODY))
    s.append(P(
        "ولم يُكتشف هذا داخلياً، بل كشفته مراجعةٌ خارجية نقدية للادعاءات "
        "المكتوبة. وكان الردّ حوكمةً: أُغلقت Lu في الساعة 17:37 من اليوم نفسه، "
        "وأُعيد تدريب النموذج النهائي على Pitt وDelaware فقط، وثُبِّتت عتبة "
        "القرار عند 0.367 على بيانات التطوير قبل التشغيل، ثم قُيِّمت Lu مرةً "
        "واحدة بالضبط: AUC 0.853 بفاصل ثقة 95% من 0.737 إلى 0.946. وبعد "
        "يومين أُعيد إنتاج ذلك التشغيل المنفرد وفق بروتوكول مُسجَّل سلفاً يسمح "
        "بتنفيذٍ واحد ولا يترتب عليه أي قرار في أي اتجاه، فطابق النتيجة إلى "
        "عشر خانات عشرية، ومصفوفةَ الالتباس خليةً خلية. ويمنع ملف شاهدٍ الآن "
        "أي تشغيل لاحق.", BODY))
    s.append(P(
        "ماذا يثبت كل رقم، وما المتبقي: الرقم 0.821 تعميمٌ خارجي غير ملوَّث، "
        "لكنه لنموذجٍ أصغر على مجموعةٍ أصغر. والرقم 0.853 هو النظام المنشور، "
        "على بياناتٍ غائبة عن تدريبه، بعتبةٍ ثُبِّتت سلفاً، ولمرةٍ واحدة — "
        "غير أنّ تركيب مجموعة تدريبه اختير بمعرفةٍ برقمٍ من Lu. ويفصل بين "
        "الرقمين 0.032 على التسجيلات الثلاثة والخمسين نفسها، ويقع 0.821 داخل "
        "فاصل ثقة 0.853، وهذا يضع حداً أعلى لحجم أثر الاختيار؛ على أنّ هذا "
        "الفارق يخلط أثر الاختيار بالفائدة الحقيقية لزيادة بيانات التدريب ولا "
        "يفصل بينهما. ونطاق المتبقي محدَّد بدقة: قرارٌ معماري واحد — أيّ "
        "المدوَّنات تدخل مجموعة التدريب — اتُّخذ بمعرفةٍ برقمٍ من Lu. ولم يُتخذ "
        "على هذا النحو أيُّ ضبطٍ لمعامل، ولا عتبة، ولا انتقاء خصائص، ولا طريقة "
        "معايرة، ولا صيغة نموذج. ويُذكر هذا بوصفه واقعةً بعد الإفصاح عن "
        "المشكلة، لا دفاعاً عنها، وهو لا يُعيد ادعاء «لم يرها النموذج قط»، "
        "وذلك الادعاء متروك نهائياً.", BODY))
    s.append(P(
        "التحفظ الصريح على النتيجة الخارجية: عند العتبة المحدَّدة سلفاً أعطت "
        "المدوَّنة المغلقة حساسية 96.2% ونوعية 33.3% فقط، أي 25 من 26 مصاباً "
        "اكتُشفوا، و9 من 27 سليماً بُرِّئوا بشكل صحيح. فعتبةٌ ضُبطت على مزيج "
        "حالاتٍ معيَّن لم تنتقل إلى عيادةٍ أخرى. وهذا بالضبط ما تُنشأ مجموعة "
        "الاختبار المغلقة لكشفه، وقد أُبلغ عنه بوصفه نتيجةً لا أن يُطمس.",
        CALLOUT))

    s.append(P("لماذا كانت النوعية 33%؟ الجواب", H))
    s.append(P(
        "قُورن الثمانية عشر سليماً الذين أخطأت العتبة في تصنيفهم بالتسعة الذين "
        "بُرِّئوا صحيحاً، على كل خاصية يستعملها النموذج. وتبيَّن أنهم وصفوا "
        "الصورة وصفاً أفقر فعلاً: 11.5 وحدة معلومات مقابل 14.9، و4.7 "
        "أشياء مسمَّاة مقابل 6.8، ونسبة الضمائر إلى الأسماء 0.893 مقابل 0.537، "
        "وذكر 44% منهم سقوط الكرسي مقابل 100%. فالنموذج التقط ما كان أمامه "
        "حقاً. ولا يمكن لأي عتبة أن تفصلهم، لأنهم يقعون داخل توزيع المصابين على "
        "القياسات نفسها لا على درجة المخرَج وحدها. والتفسير الأرجح هو طريقة "
        "إدارة المهمة — تعليمات قصيرة ولا استقصاء تالٍ — وهذه فرضية تستطيع "
        "التجربة الليبية اختبارها مستقبلاً، لا نتيجة مقرَّرة. كما كان هؤلاء أكبر "
        "سناً بـ 8.4 سنوات في المتوسط، و27 شخصاً لا يكفون لفصل أثر العمر عن "
        "أثر الإدارة.", BODY))
    s.append(P(
        "وتتبع النتيجةَ نفسَها نتيجةٌ ثانية. فإسناد العتبة إلى توزيع الأصحّاء "
        "المحليين — أي إلى المئين الثمانين منه — بدلاً من رقم ثابت يُبقي "
        "النوعية عند 79.8% و79.9% و77.8% في المدوَّنات الثلاث، لأنها لا تتحرك "
        "بتغيُّر الانتشار المحلي. وهي تحتاج متحدثين أصحّاء ولا تحتاج مرضى "
        "البتة، والتجربة الليبية تجنّدهم أصلاً. وهذه توصيةٌ للنسخة التالية، "
        "حُلِّلت بعد تجميد النموذج ولم تُنشر قط؛ والنتيجة المذكورة أعلاه تبقى هي "
        "النتيجة المحدَّدة سلفاً.", BODY))

    s.append(P("قرار الدمج، مُعاداً اختباره دون Lu", H))
    s.append(P(
        "كان القرار الذي استُرشد فيه بـ Lu هو التدريب على المدوَّنتين معاً. "
        "وتلك المقارنة بعينها لا يمكن إعادتها دون Lu، لأنها تحتاج مدوَّنةً "
        "ثالثة تضم مرضى وأصحّاء معاً، ولم تبقَ واحدة. فسُجِّل سلفاً سؤالٌ أضعف "
        "لكنه خالٍ من Lu، وثُبِّتت معاييره كتابةً قبل أي تشغيل: هل تحمل "
        "المدوَّنتان معلوماتٍ متبادلة عن بعضهما؟ نعم، وفي الاتجاهين.", BODY))
    s.append(rtl_table([
        ["التدريب على", "التقييم على", "AUC", "فاصل الثقة 95%"],
        ["Delaware وحدها", "Pitt", "0.777", "0.730 – 0.826"],
        ["Pitt وحدها", "Delaware", "0.646", "0.587 – 0.704"],
        ["Pitt وحدها", "Pitt (تحقق مُجمَّع)", "0.814", "0.768 – 0.859"],
        ["Delaware وحدها", "Delaware (تحقق مُجمَّع)", "0.547", "0.485 – 0.605"],
    ], [36 * mm, 40 * mm, 20 * mm, 34 * mm]))
    s.append(Spacer(1, 8))
    s.append(P(
        "فنموذجٌ لم يرَ تسجيلاً واحداً من Delaware يرتِّب مشاركيها فوق مستوى "
        "الصدفة، ونموذجٌ دُرِّب على فئة Delaware الأخف وحدها يرتِّب مرضى Pitt "
        "عند 0.777، أي نحو 95% مما تبلغه Pitt على نفسها. والصف اللافت هو "
        "الأخير: فحين تُدرَّب Delaware على نفسها تبلغ 0.547 بفاصلٍ يشمل مستوى "
        "الصدفة؛ أي أنها لا تستطيع تعلُّم مهمتها من 439 تسجيلاً، وأنّ نموذجاً "
        "مُدرَّباً على Pitt أفضل عليها منها على نفسها. وجزءٌ من هذا الفارق يعود "
        "إلى حجم بيانات التدريب — 548 تسجيلاً مقابل نحو 351 لكل طية — ولا "
        "يمكن الفصل بين العاملين هنا. كما تبيَّن أنّ أحد المعايير المُسجَّلة "
        "سلفاً، وهو نسبة احتفاظ، غير قابل للتفسير حين يقع مقامه عند مستوى "
        "الصدفة؛ فتُرك كما هو وسُجِّل الخلل، لأنّ تسجيلاً مسبقاً يُعدَّل بهدوء "
        "بعد ظهور النتيجة ليس تسجيلاً مسبقاً.", BODY))

    s.append(P("المنهجية، وهي الإسهام الحقيقي", H))
    s.append(P(
        "مراتٍ عدة خلال التطوير ظهرت نتائج بدت جيدة ثم تبيَّن أنها خاطئة. "
        "واكتُشف أكثرها باختبارٍ مقصود، أما أهمها — الوارد أعلاه — فلم يُكتشف "
        "كذلك.", BODY))
    s.append(P(
        "فقد تكرر ظهور المرضى أنفسهم عبر زيارات سنوية متعددة، ما كان سيتيح "
        "للنموذج أن يتعرَّف على الأشخاص لا على المرض؛ فأُلزِمت جميع تسجيلات "
        "الشخص الواحد بالبقاء في المجموعة نفسها. وكان المرضى أكبر سناً من "
        "الأصحّاء بمقدار 6.6 سنة في المتوسط، وبلغت دقة العمر وحده 0.707؛ لذلك "
        "بُنيت مجموعة مُطابَقة في العمر والجنس، فانخفضت دقة العمر وحده إلى "
        "0.515 أي عند مستوى الصدفة، بينما ظلَّ الكلام عند 0.798. كما أعطت "
        "تقنيةٌ تتفادى إهدار البيانات بإزالة أثر العمر إحصائياً مكسباً ظاهرياً "
        "كبيراً، إلى أن أظهر اختبارٌ أنّ العمر يمكن إعادة بنائه من الخصائص التي "
        "يُفترض أنها خالية منه بمعامل تحديد R² = 0.994، فاستُبعدت. وصُحِّحت "
        "نتيجةٌ أولية قدرها 0.838 نزولاً إلى 0.802 بعد تكرار المطابقة عشر "
        "مرات.", BODY))
    s.append(P(
        "وحال اختبارٌ آخر دون وقوع خطأ جسيم. فقبل دمج مدوَّنة رابعة تضم 666 "
        "متحدثاً سليماً، سُئل النموذج عمّا إذا كان قادراً على التمييز بين "
        "الأصحّاء في دراسةٍ والأصحّاء في دراسةٍ أخرى. وقد استطاع ذلك بدقة 0.930، "
        "لأنّ مُفرِّغي إحدى الدراستين كتبوا كلمة «أم» 2.8 مرة لكل مئة كلمة "
        "بينما كتبها الآخرون 0.6 مرة. ولو تمَّ الدمج لأنتج نتيجةً مُبهرة "
        "وعديمة المعنى؛ ومن تلك الواقعة خرجت القاعدة التي يتبعها المشروع "
        "الآن: لا تُدمج المدوَّنات إلا إذا أسهمت كلٌّ منها بالمرضى والأصحّاء "
        "معاً.", BODY))

    s.append(Spacer(1, 3))
    s.append(KeepTogether([
        P("سبع تجارب لم تنجح، وقد أُبلغ عنها رغم ذلك", H),
        rtl_table([
            ["التجربة", "النتيجة"],
            ["التنبؤ قبل تسع سنوات (938 مشاركاً)", "AUC 0.548 — مستوى الصدفة"],
            ["دمج مدوَّنة أحادية الفئة", "الأصحّاء قابلون للفصل عند 0.930"],
            ["إزالة أثر العمر (مكسب ظاهري)", "العمر قابل للاسترجاع R² = 0.994"],
            ["الدمج على مستوى المهام", "−0.047"],
            ["الدمج المتأخر للنموذجين الصوتي واللغوي", "−0.008"],
            ["انتقاء الخصائص، k = 15 … 80", "لم يتفوق أي حجم على المجموعة الكاملة"],
            ["استبعاد الخصائص المتأثرة بالمدوَّنة لتحسين الانتقال", "تراجع Pitt → Delaware عند كل k"],
        ], [78 * mm, 62 * mm])]))
    s.append(Spacer(1, 8))
    s.append(P(
        "وتشير هذه النتائج مجتمعةً إلى أنّ مجموعة الخصائص المصمَّمة يدوياً قد "
        "استخرجت ما يقارب كل الإشارة المتاحة، وأنّ النماذج اللغوية المُدرَّبة "
        "مسبقاً هي الاتجاه الرئيس المتبقي.", BODY))

    s.append(P("الإسهام العربي", H))
    s.append(P(
        "جميع الأنظمة القائمة من هذا النوع إنجليزية أو أوروبية. ولم يكن تكييفها "
        "للعربية ترجمةً. ففي الإنجليزية تظهر صعوبة استحضار الكلمات في صورة "
        "إفراطٍ في استعمال الضمائر، كقول «he put it there». أمّا العربية فلغةٌ "
        "حاذفة للضمير: إذ يُحذف ضمير الفاعل عادةً لأنّ الفعل يحمله أصلاً، ومن "
        "ثمّ تقع أعداد الضمائر فيها على أساسٍ مختلف تماماً لأسبابٍ نحوية لا "
        "سريرية، فلا تنتقل النسبة الإنجليزية إليها كما هي. فبُني بديلٌ عنه مما "
        "قد يفعله المتحدث حين تعييه الكلمة: الإشارة (هذا، هناك) والإبهام (شيء، "
        "حاجة)، مجموعَين في مؤشرٍ سُمِّي مؤشر القصور الإحالي. وهذا المؤشر "
        "متسقٌ مع ما تُبلغ عنه الأدبيات في لغاتٍ أخرى عن الكلام تحت ضغط "
        "استحضار الكلمة، لكنه فرضيةٌ صُمِّمت التجربة الليبية المقترحة "
        "لاختبارها، لا مؤشراً مُتحقَّقاً منه: فلم يُحسَب قط على كلام مرضى "
        "حقيقيين.", BODY))
    s.append(P(
        "وقُيِّم المكوِّن العربي بطريقتين، وليس فيهما اختبارٌ لذلك المؤشر. "
        "أولاهما حصر النموذج الإنجليزي في القياسات التي يستطيع المحرك العربي "
        "حسابها وحدها، وأعطى 0.739 بفاصل 0.703 – 0.774 على مجموعة التطوير، أي "
        "97.9% من 0.755 التي يبلغها النموذج الكامل، وهو السقف الأمين لأي نقلٍ "
        "مُطابَق البنية. والثانية تجربةٌ استطلاعية على 24 مريضاً ناطقاً "
        "بالعربية لديهم تشخيصات سريرية، وأعطت 0.622 بفاصل ثقةٍ يشمل مستوى "
        "الصدفة، باستعمال النموذج الصوتي المستقل عن اللغة على مهمةٍ مختلفة؛ "
        "وقد أُبلغ عنها بوصفها إثبات جدوى لا تحقُّقاً. وعلى حدّ علم الباحث لم "
        "تُنشر أي مدوَّنة كلامٍ متصل متاحة للعموم بالعربية الليبية لفحص الخرف، "
        "ولم يسبق لعملٍ أن كيَّف تحليل وصف الصور العفوي للغة العربية.", BODY))

    s.append(P("ما يرفض النظام فعله", H))
    s.append(P(
        "لا يُعطي النظام أيَّ احتمال في الجلسات العربية، لعدم وجود عتبةٍ "
        "مُتحقَّق منها للعربية. ولا يطبِّق النطاقات المرجعية الإنجليزية على "
        "الكلام العربي، لأنّ ذلك يصنع شذوذاً وهمياً. ولا يُصدر أيَّ نتيجة حين "
        "يكون التسجيل أكثر ضجيجاً من أن يُقاس، وفق عتبةٍ عُوِيرت بتجربة تدهورٍ "
        "أظهرت أنّ المنظومة تحتمل الضغط وانخفاض مستوى الصوت والقطع وجودة الهاتف، "
        "لكنها تفشل أمام ضجيج الخلفية.", BODY))

    s.append(P("حدود الدراسة", H))
    s.append(P(
        "يُخطئ النظام في نحو شخصٍ من كل أربعة. ولم يُتحقَّق منه على متحدثين "
        "ليبيين، ولم يُستخدم قط مع مريضٍ في عيادة حقيقية. ويظل الاختلال "
        "المعرفي الخفيف صعباً (0.629)، بل إنّ فئة Delaware لا يمكن تعلُّمها من "
        "نفسها أصلاً. ولم تنتقل عتبة التشغيل بسلاسة إلى المدوَّنة الخارجية. "
        "ولم تكن المدوَّنة الخارجية سليمةً من كل مساس قبل إغلاقها، فالرقم "
        "0.853 يُثبت أداء النظام المنشور على بياناتٍ لم يرها، لكنه ليس خالياً "
        "من ذلك المساس السابق الواحد. والمحرك العربي منهجٌ ينتظر التحقُّق، "
        "وقوائم كلماته مكتوبة بالعربية الفصحى ولم تُراجَع على اللهجة الليبية.",
        BODY))

    s.append(P("العمل المستقبلي", H))
    s.append(P(
        "أُعِدَّ بروتوكول كامل جاهز لعرضه على لجنة الأخلاقيات لدراسة جدوى "
        "بالعربية الليبية، يحدِّد التصميم وإجراءات الموافقة بما فيها تقييم "
        "الأهلية، والمعيار المرجعي، وحجم العينة، وخطة التحليل. وقد صُمِّم "
        "بوصفه دراسة جدوى ومعايير طبيعية لا دراسة دقةٍ تشخيصية، لأنّ عينةً "
        "بالحجم الممكن بلوغه لا تكفي لدعم ادعاءٍ بالدقة.", BODY))

    s.append(rule())
    s.append(P(
        "كل رقمٍ في هذه الوثيقة مقروءٌ من ملف نتائج حالي لاحقٍ للإغلاق، وملفُ "
        "كل رقمٍ مذكور في ترويسة السكربت الذي وَلَّد هذه الوثيقة. وتاريخ "
        "مجموعة الاختبار الخارجية موثَّق بالكامل في "
        "docs/LU_EXPOSURE_TIMELINE.md. وتُستخدم بيانات مدوَّنات DementiaBank "
        "بموجب عضوية TalkBank ولا يُعاد توزيعها. وأي استخدام لهذه المدوَّنات "
        "يستشهد بـ Becker وBoller وLopez وSaxton وMcGonigle (1994) ويشكر "
        "منحتَي المعهد الوطني للشيخوخة AG03705 وAG05133.", NOTE))

    doc.build(s)
    print(f"written: {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")


if __name__ == "__main__":
    build()
