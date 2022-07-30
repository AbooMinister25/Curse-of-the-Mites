from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from textual.reactive import Reactive
from textual.widget import Widget

# TILES = [
#     (0, 0, Text("▆")),
#     (1, 0, Text("▆")),
#     (2, 0, Text("▆")),
#     (3, 0, Text("▆")),
#     (4, 0, Text("▆")),
#     (5, 0, Text("▆")),
#     (6, 0, Text("▆")),
#     (7, 0, Text("▆")),
#     (8, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
#     (0, 0, Text("▆")),
# ]


class RenderData:
    color: tuple[int, int, int]
    x: int
    y: int


def make_map_grid() -> Table:
    map_grid = Table.grid()

    for _ in range(50):
        map_grid.add_column()

    for _ in range(30):
        map_grid.add_row(*("▆ " for _ in range(50)))

    return map_grid


# def blocks_from_tile(tiles: list[RenderData]) -> None:
#     blocks = []


class Map(Widget):
    mouse_over = Reactive(False)
    grid = Reactive(make_map_grid())

    def render(self) -> Panel:
        return Panel(
            Padding(Align.center(self.grid, vertical="middle")),
            border_style="green" if self.mouse_over else "blue",
            title="Map",
        )

    def render_from(self, tiles: list[RenderData]) -> None:
        """Renders the map using the given tiles"""
        map_grid = Table.grid()

        for _ in range(50):
            map_grid.add_column()

        for _ in range(30):
            ...

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
