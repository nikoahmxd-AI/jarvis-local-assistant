# Jarvis (local-first assistant starter)

A Windows-first Python assistant starter with a local Ollama chat model, optional offline speech input, local Windows speech output, optional webcam gesture recognition, explicit online reference lookup, and a small confirmation-gated app launcher.

## What it can do

- Chat with a local Ollama model (default: `qwen3.5:4b`).
- Optional offline microphone transcription with faster-whisper.
- Speak replies using the Windows SAPI voice installed on the PC.
- Optional webcam hand-gesture recognition using MediaPipe Tasks.
- Explicit `search <topic>` online Wikipedia lookup.
- Open only Notepad or Calculator, after a typed confirmation.

This is a starter project, not a general-purpose autonomous computer controller. The model cannot execute shell commands or choose arbitrary applications. Camera and microphone are accessed only after their matching commands.

## Requirements

- Windows 10/11
- Python 3.11 or newer
- Ollama for Windows
- Internet only for downloading Ollama/model/dependencies and for `search` commands

## Quick start (PowerShell)

1. Install Ollama and Python 3.11+.
2. Download the model once:

   ```powershell
   ollama pull qwen3.5:4b
   ```

3. In this repository folder, install the Python package and start Ollama if it is not already running:

   ```powershell
   py -m pip install -e .
   ollama serve
   ```

   Keep `ollama serve` running in a separate terminal. In another terminal:

   ```powershell
   $env:JARVIS_MODEL_URL = 'http://127.0.0.1:11434'
   $env:JARVIS_MODEL_NAME = 'qwen3.5:4b'
   py -m jarvis
   ```

Type `help` for commands and `quit` to exit. For a smaller/faster model, pull another Ollama model and set `JARVIS_MODEL_NAME` to its exact tag.

## Optional voice and gesture features

Install optional packages only if you want those features:

```powershell
py -m pip install numpy sounddevice faster-whisper opencv-python mediapipe
```

The voice command expects a local Whisper model directory at `assets\whisper-small`. Gesture mode expects `assets\gesture_recognizer.task`. These large model assets are intentionally not committed to GitHub; download them from their official project sources and place them at those paths. Then set `JARVIS_ASSETS` to the repository root if launching from another directory.

- `voice` records up to seven seconds and transcribes locally.
- `speak <text>` speaks the provided text using Windows SAPI.
- `gesture` opens the webcam preview; an open palm selects Notepad and a Victory gesture selects Calculator. Both still require keyboard confirmation. Press Q/Esc to exit.

## Safety and privacy

- Model and desktop server communication is restricted to localhost by the client.
- Model output is never executed as a command.
- OS actions are explicitly allowlisted and ask for confirmation.
- Microphone and webcam access is opt-in through commands.
- `search` sends the query to Wikipedia; ordinary chat stays local.

## Repository contents

This repository contains source code only. It excludes bundled Python/Ollama runtimes, model weights, Whisper/MediaPipe assets, logs, caches, and personal machine data. Each user downloads the runtime and assets separately.

## License

No license has been selected. Add a license before inviting others to reuse, modify, or redistribute this code.

