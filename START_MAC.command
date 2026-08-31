#!/bin/bash
# ============================================================
#   Dhikra Assessment Platform - Mac / Linux one-click launcher
#   Double-click this file (Mac) or run:  bash START_MAC.command
# ============================================================
cd "$(dirname "$0")"

echo ""
echo " ============================================================"
echo "   DHIKRA - Assessment Platform"
echo " ============================================================"
echo ""

# ---- find Python ----
PY=""
command -v python3 >/dev/null 2>&1 && PY=python3
[ -z "$PY" ] && command -v python >/dev/null 2>&1 && PY=python

if [ -z "$PY" ]; then
  echo " [X] Python is not installed."
  echo ""
  echo "     Mac:   install from https://www.python.org/downloads/"
  echo "     Linux: sudo apt install python3 python3-pip"
  echo ""
  read -p "Press Enter to close..."
  exit 1
fi
echo " [1/4] Python found: $($PY --version)"

# ---- install packages ----
echo " [2/4] Installing required packages (first time takes a few minutes)..."
$PY -m pip install --upgrade pip --quiet 2>/dev/null
$PY -m pip install -r requirements.txt --quiet 2>/dev/null \
  || $PY -m pip install -r requirements.txt --quiet --break-system-packages
if [ $? -ne 0 ]; then
  echo ""
  echo " [X] Package installation failed. Check your internet connection."
  read -p "Press Enter to close..."
  exit 1
fi

# ---- English language model ----
echo " [3/4] Setting up the English language model..."
# BOTH are needed: _sm supplies the grammar, _md the word vectors that nine of
# the model's sixty-four measurements are computed from. Without _md the app
# still runs and still prints a score, but those nine are silently replaced by
# training averages. This launcher used to install only _sm. Fixed 2026-08-26.
$PY -m spacy download en_core_web_sm --quiet >/dev/null 2>&1
$PY -m spacy download en_core_web_md --quiet >/dev/null 2>&1
$PY -c "import spacy;spacy.load('en_core_web_md')" >/dev/null 2>&1 || \
  echo " [!] The word-vector model did not install. The app will still start, but the report will say nine measurements were substituted." 

# ---- launch ----
echo " [4/4] Starting the platform..."
echo ""
echo " ============================================================"
echo "   Opening in your browser: http://127.0.0.1:5000"
echo "   Keep THIS WINDOW OPEN while you use the app."
echo "   To stop: press Ctrl+C, or close this window."
echo " ============================================================"
echo ""

( sleep 3 && (open http://127.0.0.1:5000 2>/dev/null || xdg-open http://127.0.0.1:5000 2>/dev/null) ) &
$PY app/server.py

echo ""
echo " The platform has stopped."
read -p "Press Enter to close..."
