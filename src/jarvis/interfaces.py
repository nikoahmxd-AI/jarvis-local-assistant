"""Ports for input and intelligence adapters added in later milestones."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class InputEvent:
    text: str
    source: str = "text"


class SpeechToText(Protocol):
    def listen(self) -> InputEvent: ...


class TextToSpeech(Protocol):
    def speak(self, text: str) -> None: ...


class GestureRecognizer(Protocol):
    def recognize(self) -> InputEvent | None: ...


class LanguageModel(Protocol):
    def interpret(self, text: str) -> str: ...

