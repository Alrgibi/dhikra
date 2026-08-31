"""
app.py — ذِكرى live demo server
--------------------------------
Runs the REAL feature-extraction engines behind a web interface. Type or paste
a transcript (English or Arabic), optionally upload a .wav, and see every
feature the pipeline computes, live.

    pip install flask
    python scripts/app.py
    # open http://127.0.0.1:5000

This is the "real" demo: nothing is pre-baked, every number is computed on the
spot by the same code used for the thesis. (A self-contained HTML version that
needs no install WAS provided as dhikra_demo.html; it was moved to archive/ on
2026-08-23 because it renders plausible-looking results from a hardcoded snapshot
alongside the real application, which is a demonstration liability now that the
app runs. It was powered by a snapshot of
this engine's output.)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from flask import Flask, request, jsonify, Response
from dhikra.linguistic_features import extract_linguistic_features
from dhikra.linguistic_features_ar import (extract_linguistic_features_ar,
                                           recitation_fidelity)

app = Flask(__name__)

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>ذِكرى — live demo</title>
<style>
 body{font-family:system-ui,Arial;max-width:900px;margin:2rem auto;padding:0 1rem;color:#1a2b3c}
 h1{color:#0f766e} textarea{width:100%;height:120px;font-size:1rem;padding:.5rem}
 button{background:#0f766e;color:#fff;border:0;padding:.6rem 1.2rem;border-radius:6px;cursor:pointer;font-size:1rem}
 .row{display:flex;gap:1rem;align-items:center;margin:1rem 0}
 table{border-collapse:collapse;width:100%;margin-top:1rem}
 td,th{border:1px solid #ddd;padding:.4rem .6rem;text-align:left;font-size:.9rem}
 th{background:#f0fdfa}
</style></head><body>
<h1>ذِكرى — live feature extraction</h1>
<p>Type or paste a transcript. The real engine analyses it on the spot.</p>
<div class="row">
 <label>Language:
  <select id="lang"><option value="en">English</option><option value="ar">Arabic</option></select>
 </label>
 <button onclick="analyze()">Analyse</button>
</div>
<textarea id="txt" placeholder="Paste a picture-description transcript here..."></textarea>
<div id="out"></div>
<script>
async function analyze(){
 const r = await fetch('/analyze',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({text:document.getElementById('txt').value,lang:document.getElementById('lang').value})});
 const d = await r.json();
 let h='<table><tr><th>feature</th><th>value</th></tr>';
 for(const k in d){h+=`<tr><td>${k}</td><td>${typeof d[k]==='number'?d[k].toFixed(3):d[k]}</td></tr>`}
 document.getElementById('out').innerHTML=h+'</table>';
}
</script></body></html>"""


@app.route("/")
def index():
    return Response(PAGE, mimetype="text/html")


@app.route("/analyze", methods=["POST"])
def analyze():
    body = request.get_json(force=True)
    text = body.get("text", "")
    lang = body.get("lang", "en")
    if not text.strip():
        return jsonify({"error": "empty text"})
    if lang == "ar":
        feats = extract_linguistic_features_ar(text)
    else:
        feats = extract_linguistic_features(text)
    return jsonify(feats)


@app.route("/recite", methods=["POST"])
def recite():
    body = request.get_json(force=True)
    return jsonify(recitation_fidelity(body.get("text", "")))


if __name__ == "__main__":
    print("ذِكرى demo running -> http://127.0.0.1:5000")
    app.run(debug=False, port=5000)
