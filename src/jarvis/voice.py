"""Optional offline microphone input using sounddevice and faster-whisper."""

from __future__ import annotations

import os
import tempfile
import wave


def listen_once(seconds: int = 7) -> str:
    try:
        import numpy as np
        import sounddevice as sd
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("Offline voice packages are missing. See README setup notes.") from exc

    sample_rate = 16000
    print(f"Listening for up to {seconds} seconds... speak now (Ctrl+C to cancel).")
    audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    if np.max(np.abs(audio)) < 80:
        return ""
    asset_root = os.environ.get("JARVIS_ASSETS", os.getcwd())
    model_path = os.path.join(asset_root, "assets", "whisper-small")
    if not os.path.isdir(model_path):
        raise RuntimeError("Offline Whisper model is not bundled in assets\\whisper-small.")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name
    try:
        with wave.open(audio_path, "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(sample_rate)
            output.writeframes(audio.tobytes())
        model = WhisperModel(model_path, device="cpu", compute_type="int8", cpu_threads=4)
        segments, info = model.transcribe(audio_path, beam_size=2, vad_filter=True)
        recognized = " ".join(segment.text.strip() for segment in segments).strip()
        print(f"Detected speech language: {info.language}")
        return recognized
    finally:
        try:
            os.unlink(audio_path)
        except OSError:
            pass


def speak_local(text: str) -> None:
    """Use the installed Windows SAPI voice locally; no audio is sent online."""
    if os.name != "nt":
        print("Local speech output is available on Windows only.")
        return
    import subprocess

    # Text crosses as base64 so quotes/newlines cannot become PowerShell code.
    import base64
    payload = base64.b64encode(text.encode("utf-16le")).decode("ascii")
    script = (
        "$t=[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('" + payload + "'));"
        "$s=New-Object -ComObject SAPI.SpVoice; [void]$s.Speak($t)"
    )
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

