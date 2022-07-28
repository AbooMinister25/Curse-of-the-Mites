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

    mouse_over = Reactive(False)
    available_commands: Reactive[list[str]] = Reactive(
        ["north", "east", "south", "west", "flee"]
    )

    def __init__(self, main_app: GameInterface, name: str | None = None):
        self.main_app = main_app
        super().__init__(name)

    def render(self) -> Panel:
        return Panel(
            Padding(
                Align.center("\n".join(self.available_commands), vertical="middle")
            ),
            border_style="green" if self.mouse_over else "blue",
            title="Allowed Moves",
        )

    def add_commands(self, commands: list[str]) -> None:
        """Adds the given commands to our list of available commands"""
        self.available_commands.extend(commands)

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
