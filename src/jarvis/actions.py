"""Action registry and confirmation boundary.

OS integrations must be registered here; model or input adapters cannot call
arbitrary shell commands directly.
"""

from dataclasses import dataclass
import subprocess
import sys
from typing import Callable


@dataclass(frozen=True)
class Action:
    name: str
    description: str
    run: Callable[[], str]
    requires_confirmation: bool = True


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, action: Action) -> None:
        if action.name in self._actions:
            raise ValueError(f"Action already registered: {action.name}")
        self._actions[action.name] = action

    def get(self, name: str) -> Action | None:
        return self._actions.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._actions))


def execute_with_confirmation(action: Action, confirm: Callable[[str], bool]) -> str:
    if action.requires_confirmation and not confirm(action.description):
        return "Cancelled."
    return action.run()


def desktop_actions() -> ActionRegistry:
    """Return the small, explicit set of safe Windows app launch actions."""
    registry = ActionRegistry()
    if sys.platform != "win32":
        return registry

    def register_app(name: str, executable: str, description: str) -> None:
        registry.register(
            Action(
                name=name,
                description=description,
                run=lambda exe=executable, label=name: _launch_windows_app(exe, label),
                requires_confirmation=True,
            )
        )

    register_app("notepad", "notepad.exe", "Open Notepad")
    register_app("calculator", "calc.exe", "Open Calculator")
    return registry


def _launch_windows_app(executable: str, label: str) -> str:
    subprocess.Popen([executable], shell=False)
    return f"Opening {label}."


def match_app_request(text: str, registry: ActionRegistry) -> Action | None:
    """Match only direct, known phrases; never infer an executable from model text."""
    command = " ".join(text.casefold().strip().split())
    phrases = {
        "notepad": ("open notepad", "launch notepad", "notepad open pannu", "notepad ah open pannu"),
        "calculator": (
            "open calculator",
            "open calc",
            "launch calculator",
            "calculator open pannu",
            "calculator ah open pannu",
        ),
    }
    for action_name, accepted in phrases.items():
        if command in accepted:
            return registry.get(action_name)
    return None

