@echo off
REM ============================================================
REM   Dhikra Assessment Platform - Windows one-click launcher
REM   Just double-click this file.
REM ============================================================
title Dhikra Assessment Platform
cd /d "%~dp0"

echo.
echo  ============================================================
echo    DHIKRA - Assessment Platform
echo  ============================================================
echo.

REM ---- find Python ----
set PY=
where py >nul 2>&1 && set PY=py
if "%PY%"=="" ( where python >nul 2>&1 && set PY=python )

if "%PY%"=="" (
  echo  [X] Python is not installed.
  echo.
  echo      1. Go to  https://www.python.org/downloads/
  echo      2. Download Python for Windows and run the installer
  echo      3. IMPORTANT: tick "Add Python to PATH" on the first screen
  echo      4. Finish the install, then double-click this file again
  echo.
  pause
  exit /b 1
)
echo  [1/4] Python found.

REM ---- install packages ----
echo  [2/4] Installing required packages (first time takes a few minutes)...
%PY% -m pip install --upgrade pip --quiet
%PY% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
  echo.
  echo  [X] Package installation failed. Check your internet connection.
  pause
  exit /b 1
)

REM ---- English language models ----
REM  BOTH are needed. en_core_web_sm supplies the grammar; en_core_web_md
REM  supplies the word vectors that nine of the model's sixty-four measurements
REM  are computed from. Without _md the app still runs and still prints a
REM  score, but those nine are silently replaced by training averages. The
REM  launcher used to install only _sm. Corrected 26 August 2026.
echo  [3/4] Setting up the English language models (two downloads, ~40 MB)...
%PY% -m spacy download en_core_web_sm --quiet >nul 2>&1
%PY% -m spacy download en_core_web_md --quiet >nul 2>&1
%PY% -c "import spacy;spacy.load('en_core_web_md')" >nul 2>&1
if errorlevel 1 (
  echo  [!] The word-vector model did not install. The app will still start,
  echo      but the report will say that nine measurements were substituted.
)

REM ---- launch ----
echo  [4/4] Starting the platform...
echo.
echo  ============================================================
echo    Opening in your browser: http://127.0.0.1:5000
echo    Keep THIS BLACK WINDOW OPEN while you use the app.
echo    To stop: close this window, or press Ctrl+C.
echo  ============================================================
echo.

start "" http://127.0.0.1:5000
%PY% app\server.py

echo.
echo  The platform has stopped.
pause
