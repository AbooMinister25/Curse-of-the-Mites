import json

from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget
from websockets.legacy.client import WebSocketClientProtocol


class AvailableCommands(Widget):
    """Shows the available commands the player can make"""

    mouse_over = Reactive(False)
    available_commands: Reactive[list[str]] = Reactive([])

    def __init__(self, main_app, name: str | None = None):
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

    async def refresh_commands(self) -> None:
        """Refreshes the available commands list by fetching data from the server"""
        data = json.dumps({"type": "request", "data": "commands"})
        await self.main_app.websocket.send(data)
        message = await self.main_app.websocket.recv()
        message = json.loads(message)

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
