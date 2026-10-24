"""Optional loopback-only client for a local llama.cpp-compatible server."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class LocalModel:
    def __init__(
        self,
        base_url: str,
        model_name: str = "qwen3.5:0.8b",
        timeout_seconds: float = 240,
    ) -> None:
        parsed = urlsplit(base_url)
        host = (parsed.hostname or "").casefold()
        is_loopback = host == "localhost" or host == "::1" or host.startswith("127.")
        if parsed.scheme != "http" or not is_loopback or parsed.username or parsed.password:
            raise ValueError("The model URL must be plain HTTP on localhost/127.x/::1.")
        self.endpoint = base_url.rstrip("/") + "/api/chat"
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self._messages: list[dict[str, str]] = []

    def reply(self, user_text: str) -> str | None:
        payload = {
            "model": self.model_name,
            "think": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a helpful and accurate assistant running locally. "
                        "Answer in the same language as the latest user message: English for English, "
                        "conversational Tamil/Tanglish for Tamil/Tanglish. Keep answers clear and concise; "
                        "say when you are uncertain. You may answer and explain, but cannot control the computer. "
                        "Never claim you performed an action."
                    ),
                },
                *self._messages[-8:],
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.4,
            "options": {"num_ctx": 2048, "num_predict": 384},
            "stream": False,
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
            answer = result["message"]["content"].strip()
            if answer:
                self._messages.extend(
                    ({"role": "user", "content": user_text}, {"role": "assistant", "content": answer})
                )
                self._messages = self._messages[-8:]
                return answer
            return None
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
            return None

