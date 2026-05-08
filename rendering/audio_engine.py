"""
Audio Engine — background music selection and mixing.
Downloads royalty-free tracks; falls back to procedurally generated jingle.
"""

import os
import math
import wave
import struct
import logging
import requests

logger = logging.getLogger(__name__)

MUSIC_DIR = "assets/music"

TRACKS = [
    {"name": "carefree",  "url": "https://archive.org/download/kevin-macleod-carefree/Carefree.mp3"},
    {"name": "quirky",    "url": "https://archive.org/download/kevin-macleod-quirky/Quirky.mp3"},
]


def _download(url: str, path: str) -> bool:
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(32768):
                f.write(chunk)
        return os.path.getsize(path) > 5000
    except Exception as e:
        logger.warning(f"Music download failed: {e}")
        if os.path.exists(path):
            os.remove(path)
        return False


def _generate_jingle(path: str, duration: float = 60.0) -> str:
    sr     = 44100
    n      = int(duration * sr)
    notes  = {
        "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
        "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25,
        "G3": 196.00, "B3": 246.94,
    }
    melody = ["C4","E4","G4","E4","C5","G4","E4","D4",
              "F4","A4","C5","A4","F4","E4","G4","C4"]
    bass   = ["C4","C4","F4","F4","G3","G3","C4","C4",
              "F4","F4","C4","C4","G3","G3","C4","C4"]

    bpm  = 130
    beat = sr * 60 // bpm
    nlen = int(beat * 0.85)
    audio = [0.0] * n

    for i in range(n // beat + 1):
        mel = melody[i % len(melody)]
        bas = bass[i % len(bass)]
        start, end = i * beat, min(i * beat + nlen, n)
        seg_n = end - start
        for s in range(seg_n):
            t   = s / sr
            env = 1.0
            if s < 200:       env = s / 200
            elif s > seg_n - 500: env = (seg_n - s) / 500
            val  = 0.25 * math.sin(2 * math.pi * notes[mel] * t)
            val += 0.08 * math.sin(4 * math.pi * notes[mel] * t)
            val += 0.15 * math.sin(2 * math.pi * notes[bas] * t)
            idx = start + s
            if idx < n:
                audio[idx] += val * env

    wav_path = path.replace(".mp3", ".wav")
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for s in audio:
            wf.writeframes(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))))

    logger.info(f"Generated fallback jingle: {wav_path}")
    return wav_path


def get_music_track() -> str | None:
    os.makedirs(MUSIC_DIR, exist_ok=True)

    for fname in os.listdir(MUSIC_DIR):
        fpath = os.path.join(MUSIC_DIR, fname)
        if fname.endswith((".mp3", ".wav")) and os.path.getsize(fpath) > 5000:
            logger.info(f"Using cached music: {fname}")
            return fpath

    for track in TRACKS:
        path = os.path.join(MUSIC_DIR, f"{track['name']}.mp3")
        if _download(track["url"], path):
            return path

    fallback = os.path.join(MUSIC_DIR, "jingle.wav")
    return _generate_jingle(fallback)
