"""
asr.py
------
Speech-to-text for the assessment platform.

DESIGN: PLUGGABLE WITH A HONEST FALLBACK
Automatic transcription uses Whisper, which handles Arabic (including Quranic
recitation) and English well. Whisper downloads its model weights on first use,
which requires an internet connection on the machine running the platform.

If Whisper is unavailable, the platform does NOT fail and does NOT invent a
transcript. It falls back to OPERATOR TRANSCRIPTION -- the person administering
the assessment types what was said. This is not a workaround bolted on: human
transcription is how the DementiaBank reference corpus itself was built, and it
produces higher-quality text than any ASR system. The acoustic analysis is
completely unaffected either way, because it measures the audio signal directly
and never needs words.

MODEL CHOICE
  'small'  -- good Arabic quality, ~500MB, reasonable on a laptop  (default)
  'medium' -- better Arabic, ~1.5GB, slower
  'base'   -- fastest, weaker on Arabic
Arabic dialect note: Whisper is trained mostly on Modern Standard Arabic, so
Libyan dialectal speech will transcribe imperfectly. The operator can always
correct the transcript before analysis -- and SHOULD, for research-grade data.
"""
from __future__ import annotations
import os
import shutil
import subprocess
import tempfile

_MODEL = None
_MODEL_NAME = None


def whisper_available() -> bool:
    """True if the whisper package is importable (weights may still need a download)."""
    try:
        import whisper  # noqa: F401
        return True
    except Exception:
        return False


def _find_ffmpeg() -> str | None:
    """
    Locate an ffmpeg binary.

    Installing ffmpeg by hand is the single biggest setup obstacle on Windows,
    so a pip-installable bundled binary (imageio-ffmpeg) is accepted as a
    fallback. This means `pip install imageio-ffmpeg` is enough -- no manual
    download, no PATH editing.
    """
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def ffmpeg_available() -> bool:
    return _find_ffmpeg() is not None


def convert_to_wav(src_path: str, dst_path: str | None = None,
                   sample_rate: int = 16000) -> str:
    """
    Convert any browser-recorded audio (webm/ogg/mp4) to 16 kHz mono WAV.

    Browsers record with MediaRecorder, which produces webm/ogg rather than
    WAV, so this normalisation step sits between the browser and the analysis
    engines. Requires ffmpeg.
    """
    if dst_path is None:
        dst_path = os.path.splitext(src_path)[0] + ".wav"
    exe = _find_ffmpeg()
    if exe is None:
        raise RuntimeError(
            "ffmpeg not found. Easiest fix:  pip install imageio-ffmpeg  "
            "(or install ffmpeg system-wide) so browser recordings can be "
            "converted to WAV.")
    cmd = [exe, "-y", "-i", src_path, "-ac", "1", "-ar", str(sample_rate),
           "-vn", dst_path]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0 or not os.path.exists(dst_path):
        raise RuntimeError(f"ffmpeg conversion failed: {proc.stderr.decode()[:400]}")
    return dst_path


def _backend() -> str | None:
    """
    Which transcription backend is installed.

    'faster-whisper' is preferred: it is a re-implementation of the same
    Whisper models that runs on CPU without PyTorch, so installing it downloads
    tens of megabytes instead of the multi-gigabyte PyTorch stack. Accuracy is
    equivalent because the model weights are the same.
    """
    try:
        import faster_whisper  # noqa: F401
        return "faster-whisper"
    except Exception:
        pass
    try:
        import whisper  # noqa: F401
        return "openai-whisper"
    except Exception:
        return None


def whisper_available() -> bool:
    return _backend() is not None


def _load_audio(wav_path: str):
    """
    Read a 16 kHz mono WAV into a float32 numpy array.

    WHY THIS MATTERS: openai-whisper normally loads audio by shelling out to an
    `ffmpeg` command on the system PATH. This project installs ffmpeg through
    pip (imageio-ffmpeg), which is NOT on the PATH -- so whisper would fail even
    though the platform's own conversion works fine. Loading the audio here and
    passing an array sidesteps that entirely, and means no separate ffmpeg
    installation is ever required.
    """
    import numpy as np
    import soundfile as sf
    audio, sr = sf.read(wav_path, dtype="float32")
    if audio.ndim > 1:                       # stereo -> mono
        audio = audio.mean(axis=1)
    if sr != 16000:                          # whisper expects 16 kHz
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    return np.ascontiguousarray(audio, dtype="float32")


def load_model(name: str = "small"):
    """Load (and cache) a transcription model. Downloads weights on first call."""
    global _MODEL, _MODEL_NAME
    backend = _backend()
    if _MODEL is not None and _MODEL_NAME == (backend, name):
        return _MODEL
    if backend == "faster-whisper":
        from faster_whisper import WhisperModel
        _MODEL = WhisperModel(name, device="cpu", compute_type="int8")
    elif backend == "openai-whisper":
        import whisper
        _MODEL = whisper.load_model(name)
    else:
        raise RuntimeError("no transcription backend installed")
    _MODEL_NAME = (backend, name)
    return _MODEL


def transcribe(wav_path: str, lang: str = "ar", model_name: str = "small") -> dict:
    """
    Transcribe an audio file.

    Returns
    -------
    {
      'text'      : str    the transcript ('' if unavailable)
      'available' : bool   whether automatic transcription actually ran
      'engine'    : str    backend + model, or 'unavailable'
      'message'   : str    human-readable explanation for the operator
    }

    The caller must handle available=False by asking the operator to type the
    transcript. The platform never fabricates text.
    """
    backend = _backend()
    if backend is None:
        return {
            "text": "", "available": False, "engine": "unavailable",
            "message": ("Automatic transcription is not installed. Install it with:  "
                        "pip install faster-whisper   (small download, recommended) "
                        "or  pip install openai-whisper  (large). Internet is needed "
                        "the first time only, to fetch the model. Meanwhile please "
                        "type the transcript below - acoustic analysis has already "
                        "run on the recording and is unaffected."),
        }
    try:
        audio = _load_audio(wav_path)
        model = load_model(model_name)
        if backend == "faster-whisper":
            segments, _info = model.transcribe(audio, language=lang, beam_size=5)
            text = " ".join(seg.text for seg in segments).strip()
        else:
            result = model.transcribe(audio, language=lang, fp16=False)
            text = (result.get("text") or "").strip()
        return {
            "text": text, "available": True,
            "engine": f"{backend}-{model_name}",
            "message": ("Transcribed automatically. Please review and correct before "
                        "analysing - dialectal Arabic is often imperfect, and the "
                        "word-level measures are computed from this text."),
        }
    except Exception as e:
        return {
            "text": "", "available": False, "engine": "error",
            "message": (f"Automatic transcription failed ({type(e).__name__}: "
                        f"{str(e)[:160]}). Please type the transcript below."),
        }
