from __future__ import annotations

import typing

from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget

if typing.TYPE_CHECKING:
    from main import GameInterface


class AvailableCommands(Widget):
    """Shows the available commands the player can make"""

    MOVE_COMMANDS_MESSAGE: list[str] = [
        "!move (or use numpad keys)",
        "(north | south | east | west)",
    ]
    SPECIAL_COMMANDS: list[str] = ["!flee", "!nvm", "!clear"]
    available_commands: Reactive[list[str]] = Reactive(
        MOVE_COMMANDS_MESSAGE + SPECIAL_COMMANDS + []
    )

    def __init__(self, main_app: GameInterface, name: str | None = None):
        self.main_app = main_app
        super().__init__(name)

    def render(self) -> Panel:
        if not self.main_app.initialized:
            return Panel(
                Padding(Align.left("/register [USERNAME]")),
                border_style="green",
                title="Register to play!",
            )
        return Panel(
            Padding(Align.left("\n".join(self.available_commands))),
            border_style="green",
            title="Allowed Moves",
        )

    def add_commands(self, commands: set[str]) -> None:
        """Adds the given commands to our list of available commands"""
        self.available_commands.extend(commands)
