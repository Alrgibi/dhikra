#!/usr/bin/env bash
# build.sh -- rebuild Dhikra_thesis.docx from the markdown sources (two passes for index page numbers), then the two-page summary.
# Needs: node + the `docx` npm package, python3 with markdown-it-py, pymupdf, python-docx, qrcode, pillow; LibreOffice (soffice).
# Paths inside parse.py/render.js/front.py/make_qr.py/revlib.py/renumber.py point at /home/claude/work/...; set ROOT there to this repository first.
# ONE-SHOT SCRIPTS -- already applied to docs/chapters/*.md and kept only as the record of what changed; NEVER run them again
# (each asserts the pre-edit text and fails on the edited sources): revise.py..revise5.py (the review pass, from chapters_backup_v1),
# cut_ch5.py, trim_ch5.py, cut_ch3.py, cut_ch3b.py, cut_ch4.py, cut_ch6.py, cut_ch6b.py, cut_ch12.py, cut_ch1.py, cut_appE.py,
# cut_appF.py, renumber.py and every cut2_*.py (the page-budget pass, from chapters_backup_v2). ASSEMBLY_NOTES.md section 5 has the order.
set -e
cd "$(dirname "$0")"
python3 make_qr.py                    # Appendix J QR code from build_config.json (repo_url)
python3 parse.py
python3 front.py                      # pass 1: index pages unknown
node render.js thesis.docx && python3 postpack.py thesis.docx
soffice --headless --convert-to pdf thesis.docx
python3 harvest.py thesis.pdf pages.json
python3 front.py --pages pages.json   # pass 2: real page numbers
node render.js thesis.docx && python3 postpack.py thesis.docx
soffice --headless --convert-to pdf thesis.docx
python3 harvest.py thesis.pdf pages2.json
python3 ../check_docx.py thesis.docx
python3 measure.py thesis.docx        # the revision-pass class counts
python3 unitblank.py                  # pages per unit and the blank tail of each unit's last page
node render_summary.js ../../docs/summary/Dhikra_project_summary.md summary.docx   # the two-page summary
soffice --headless --convert-to pdf summary.docx
