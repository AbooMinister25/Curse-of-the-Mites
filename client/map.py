from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from textual.reactive import Reactive
from textual.widget import Widget


def make_map_grid() -> Table:
    map_grid = Table.grid(expand=True)

    for _ in range(30):
        map_grid.add_row("▆ " * 50)

    return map_grid


class Map(Widget):
    mouse_over = Reactive(False)
    grid = Reactive(make_map_grid())

    def render(self) -> Panel:
        return Panel(
            Padding(Align.center(self.grid, vertical="middle")),
            border_style="green" if self.mouse_over else "blue",
            title="Map",
        )

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
