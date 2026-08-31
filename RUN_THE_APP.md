# Running the ذِكرى (Dhikra) Assessment Platform

**Everything below was executed end to end on 26 August 2026** — clean machine,
nothing pre-installed, Python 3.11, `pip install -r requirements.txt` only. The
app booted, served a session, scored a transcript and produced a report. Where
this file says something happens, it was watched happening.

---

## 0. The one-click way (try this first)

- **Windows:** double-click **`START_WINDOWS.bat`**
- **Mac / Linux:** double-click **`START_MAC.command`**, or run `bash START_MAC.command`

The launcher finds Python, installs everything, downloads both language models,
opens your browser at `http://127.0.0.1:5000`, and leaves a black window open.
**Keep that window open** — closing it stops the app.

If it works, stop reading. Section 4 is the failure table if it doesn't.

---

## 1. The typed way, from a fresh terminal

Nothing is remembered between sessions except what is on disk. These are the
commands, in order.

### Windows (PowerShell or Command Prompt)

```
cd "C:\Users\PC\Desktop\Dhikra Cowork\dhikra"
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m spacy download en_core_web_sm
py -m spacy download en_core_web_md
py app\server.py
```

### Mac / Linux

```
cd ~/Desktop/"Dhikra Cowork"/dhikra
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
python3 -m spacy download en_core_web_md
python3 app/server.py
```

Then open **http://127.0.0.1:5000** in Chrome, Edge or Firefox.

**The first two `pip` lines need internet and take 3–10 minutes.** After that the
app runs with the network switched off, permanently. Nothing is uploaded, ever.

---

## 2. What a correct start looks like

```
  empirical ranges     : 16 loaded from the control group
==================================================================
  ذِكرى Assessment Platform
==================================================================
  ffmpeg available     : True
  vector model (md)    : True
  auto-transcription   : False  (operator will type transcripts)
  trained model        : True  (n=987, AUC=0.755)
  sessions saved to    : .../data/sessions
------------------------------------------------------------------
  open  ->  http://127.0.0.1:5000
==================================================================
```

**Read those four lines before every real session.** Each one is a thing that can
be silently wrong:

| Line | If it says `False` |
|---|---|
| `ffmpeg available` | Audio cannot be converted. Recording will fail. `pip install imageio-ffmpeg`. |
| `vector model (md)` | **The app still runs and still prints a score, but nine of the sixty-four measurements behind it were not computed** — they are replaced by training averages. The report says so. Fix with `python -m spacy download en_core_web_md`. |
| `auto-transcription` | Normal and fine. It means you type the transcripts yourself, which is how the reference corpus was built. Optional: `pip install faster-whisper`. |
| `trained model` | No probability will be shown at all, only the indicator profile. `models/dhikra_model.pkl` is missing or would not load — see §4. |

---

## 3. Administering one session (about six minutes)

1. **Setup** — participant code, age, sex, education, language. Age and education
   are recorded because both move speech measures independently of cognition.
2. **Consent** — read the on-screen points aloud. Do not skip this.
3. **Tasks**, in the order the app gives them. Hand the device over; they talk.
   - Story recall (90 s) — read the story aloud **once**, then record the retelling
   - Procedural discourse (90 s) — "tell me how you make tea"; no stimulus needed
   - Picture description (90 s) — **this is the only task the score comes from**
   - Verbal fluency (60 s) — "name as many animals as you can"
   - Quran recitation (60 s) — Arabic sessions only; operator picks a known surah
4. **Transcripts** — review and correct them. Word-level measures depend on this.
5. **Report** — screening band, every indicator against its reference range with
   a plain-language explanation, recitation accuracy, task dissociation, and any
   caveats that apply.

Sessions are saved to `data/sessions/*.json`.

**Let silences stand.** Pauses are part of what is being measured. Do not prompt
with example words during fluency.

---

## 4. When it fails

| What you see | What it means | What to do |
|---|---|---|
| `'py' is not recognized` / `python: command not found` | Python is not installed or not on PATH | Install from python.org and **tick "Add Python to PATH"** on the first installer screen. Then reopen the terminal — an already-open one will not see it. |
| `No module named flask` | Requirements not installed, or installed into a different Python | Re-run the `pip install -r requirements.txt` line **with the same command name** you use to run the app (`py` with `py`, `python3` with `python3`). |
| `Address already in use` / `Port 5000 is in use` | The app is already running in another window | Close the other black window. On Mac, System Settings → General → AirDrop & Handoff → turn off **AirPlay Receiver**, which takes port 5000. |
| Browser says "can't reach this page" | The server window closed, or you typed `localhost:5000` with `https://` | Use exactly `http://127.0.0.1:5000`. Check the black window is still open. |
| Microphone never turns on | Browsers only allow microphone access on `localhost` or over HTTPS | Use `127.0.0.1`, not the machine's network address. If you host it elsewhere you need HTTPS. |
| `vector model (md) : False` | `en_core_web_md` is missing | `py -m spacy download en_core_web_md`. Until then every report carries a caveat saying nine measurements were substituted. **Do not ignore it.** |
| `! could not load trained model: ...` | Almost always a **scikit-learn version mismatch** | `requirements.txt` pins `scikit-learn==1.8.0` for exactly this reason: the model file is a pickle built under that version and the library does not guarantee cross-version loading. Run `py -m pip install "scikit-learn==1.8.0"` and restart. The model is frozen and cannot be rebuilt — the library is pinned to it, not the other way round. |
| `ffmpeg available : False` | The bundled converter is missing | `py -m pip install imageio-ffmpeg`. You do **not** need to install ffmpeg by hand; the pip package carries its own binary. (An older version of this file said otherwise. It was wrong.) |
| Recording works but the transcript box is empty | Whisper is not installed | Expected. Type the transcript. |
| Report shows `mode: indicator_profile` and no probability | Working as designed | One of: Arabic session, a non-kitchen picture, or no model loaded. The app refuses to print a number it cannot justify. |
| Report says the picture is not the one the model was calibrated on | Working as designed | This caveat is on **every** English score. See THESIS_PLAN §4.3.1. |

**If pip fails with SSL or proxy errors:** you are behind a filtered network. Run
the two `pip install` lines once on any machine with open internet, in the same
folder, then copy the whole folder across. After first install the app needs no
network at all.

---

## 5. Two operating modes

| Mode | When | What it shows |
|---|---|---|
| **Indicator profile** | Arabic sessions, a non-validated stimulus, or no model attached | How many measured indicators fall outside reference ranges, and which, with direction and meaning. **No probability**, because none would be honest. |
| **Screening score** | `models/dhikra_model.pkl` present, English session, kitchen picture | The same report plus a calibrated probability, its threshold, and every caveat that applies to it. |

Switching modes needs no code change — `report.attach_model()` does it.

---

## 6. Stopping it

Close the black window, or press **Ctrl+C** in it. Sessions already saved to
`data/sessions/` are not affected.
