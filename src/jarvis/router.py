"""Small deterministic router for fixed local commands."""

from datetime import datetime


def respond(text: str) -> str:
    command = text.strip().casefold()
    if command in {"hi", "hello", "hey", "vanakkam"}:
        return "Vanakkam! Jarvis foundation ready. Try 'help'."
    if command in {"time", "what time is it", "neram"}:
        return f"Local time: {datetime.now().astimezone().strftime('%I:%M %p')}"
    if command in {"help", "?"}:
        return "Commands: help, time, voice (offline mic), speak <text>, gesture (camera), search <query> (online), open Notepad, open Calculator, quit. App launches ask before running."
    return "I don't have that capability connected yet. This starter won't guess or run laptop commands."

