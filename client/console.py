from rich.panel import Panel
from rich.align import Align
from rich.padding import Padding
from rich.table import Table

from textual.reactive import Reactive
from textual.widget import Widget


class Console(Widget):
    mouse_over = Reactive(False)

    def render(self) -> Panel:
        return Panel(
            Padding(Align.center("blah", vertical="middle")),
            border_style="green" if self.mouse_over else "blue",
            title="Console",
        )

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
        