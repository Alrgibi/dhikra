import re
P="/home/claude/work/src/docs/chapters/appendix_e.md"; t=open(P,encoding='utf-8').read()
def sub1(old,new):
    global t; assert t.count(old)==1,(old[:60],t.count(old)); t=t.replace(old,new)
# E.1: table cells shorter
for old,new in [("| 68 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |","| 68 | passed |"),("| 88 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |","| 88 | passed |"),("| 134 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |","| 134 | passed |"),("| 32 | ok — 8.3 s, speech 6.2 s, SNR 37.6 dB |","| 32 | passed |")]: sub1(old,new)
sub1("Every recording passed the gate: the synthetic sample runs 8.3 seconds with 6.2 seconds of speech, a signal-to-noise ratio of 37.6 dB and a clipped fraction of 0.0002, against the minima of the quality-gate table in section 4.5.",
     "Every recording passed the gate — the synthetic sample runs 8.3 seconds with 6.2 seconds of speech, a signal-to-noise ratio of 37.6 dB and a clipped fraction of 0.0002 — against the minima of Table (4.3).")
# E.2
sub1(' and states which task the result came from: "The screening result is computed from the picture-description task only. That is the sole task in the training corpus that included healthy controls, and it is the task on which this model was externally validated. The story-recall and procedural-discourse tasks are administered first and recorded, but do not contribute to this result: they carry more signal for MILD impairment, and scoring them would require a new validation study rather than a new setting."',
     ' and states that the result is computed from the picture-description task only, the sole task with healthy controls in the training corpus and the one on which the model was externally evaluated, the discourse tasks being recorded but contributing nothing to it.')
# E.4: drop the 'Outside range' column, mark the one flag in the value
lines=t.split("\n"); out=[]; in_e3=False
for ln in lines:
    if ln.startswith("| Group | Indicator | Value | Reference | Outside range | Meaning printed on the report |"):
        out.append("| Group | Indicator | Value | Reference | Meaning printed on the report |"); in_e3=True; continue
    if in_e3 and ln.startswith("|---|---|---|---|---|---|"):
        out.append("|---|---|---|---|---|"); continue
    if in_e3 and ln.startswith("|"):
        cells=[c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells)==6:
            g,i,v,r,o,m=cells
            if o=="yes": v=v+" (outside range)"
            out.append(f"| {g} | {i} | {v} | {r} | {m} |"); continue
    if in_e3 and not ln.startswith("|"): in_e3=False
    out.append(ln)
t="\n".join(out)
sub1("Table (E.3) reproduces the 19 indicators as printed, grouped as the report groups them, with the plain-language meaning the report attaches to each. 1 of the 19 fell outside its reference range: pitch variation, at 0.028 against a floor of 0.1. That flag is an artefact of the input, not a finding — the synthesised sample recording has an almost constant fundamental frequency by construction — and it illustrates the profile doing what it is for: reporting a measurement the score does not use, so that the operator can see it.",
     "Table (E.3) reproduces the 19 indicators as printed, with the plain-language meaning the report attaches to each. One fell outside its reference range, pitch variation at 0.028 against a floor of 0.1 — an artefact of the synthesised input, whose fundamental frequency is almost constant by construction, and an illustration of the profile reporting a measurement the score does not use.")
# E.5: drop the long quoted corpus note (and with it the inline citation inside the platform's text)
sub1('Verbal fluency counted 32 animal names with 0 repetitions and 0 unrecognised words; the report attaches the corpus note — "In the Pitt dementia cohort, animal counts fell steadily with severity: 9.4 on average at MMSE 26-30, 6.6 at 16-20, and 2.7 below 11 (r = 0.40 with MMSE, n = 207). For orientation, a normative study of 4,387 cognitively unimpaired adults aged 30-91 reports a mean of about 20 animals in 60 seconds, SD about 5 (Karstens et al., J Int Neuropsychol Soc 30(4):389-401, 2023). Age moderates this more strongly than education, so the figure is not a cut-off and must not be read as one." — and the orientation note that ends: "No validated Libyan-Arabic norm exists, so this figure is context for the operator and does NOT affect the screening result."',
     'Verbal fluency counted 32 animal names with 0 repetitions and 0 unrecognised words; the report attaches a corpus note giving the training cohort\'s counts by severity band and a published normative mean for orientation, and ends: "No validated Libyan-Arabic norm exists, so this figure is context for the operator and does NOT affect the screening result."')
# E.6: the stimulus caveat is quoted in full in section 4.5
sub1('Two texts appear on every screening-score report, and both were present here. The stimulus-substitution caveat of section 4.3.1 reads: "The picture shown is not the picture this model was calibrated on. The original belongs to a published test and cannot be redistributed, so an equivalent scene drawn for this project is used instead. Every item the scorer looks for is present in it, but the two pictures are not interchangeable, and the effect of the substitution on real speakers has never been measured. If this picture costs a speaker even one of the items the original would have prompted, roughly one healthy recording in eight would move from a negative screen to a positive one. Weigh this score accordingly until the substitution has been checked on a local sample." And the disclaimer',
     'Two texts appear on every screening-score report, and both were present here: the stimulus-substitution caveat quoted in full in section 4.5, and the disclaimer')
t=re.sub(r"\n{3,}","\n\n",t); open(P,'w',encoding='utf-8').write(t)
print('E', len(re.findall(r"\S+", re.sub(r"\|", " ", t))))
