import typing
from dataclasses import dataclass

from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

if typing.TYPE_CHECKING:
    from main import GameInterface


@dataclass
class RenderData:
    color: tuple[int, int, int]
    x: int
    y: int
    players: list


def make_map_grid() -> Table:
    map_grid = Table.grid()

    for _ in range(50):
        map_grid.add_column()

    for _ in range(30):
        map_grid.add_row(*("▆ " for _ in range(50)))

    return map_grid


class Map(Widget):
    mouse_over = Reactive(False)
    grid = Reactive(make_map_grid())

    def __init__(self, main_app: "GameInterface", name: str | None = None):
        self.main_app = main_app
        super().__init__(name)

    def render(self) -> Panel:
        return Panel(
            Padding(Align.center(self.grid, vertical="middle")),
            border_style="green" if self.mouse_over else "blue",
            title="Map",
        )

    def render_from(self, tiles: list[RenderData]) -> None:
        """Renders the map using the given tiles"""
        map_grid = Table.grid()

        for _ in range(35):
            map_grid.add_column()

        for i in range(30):
            usable_tiles = [tile for tile in tiles if tile.y == i]
            display: list[Text] = []

            for y in range(35):
                for tile in usable_tiles:
                    if tile.x == y:
                        for player in tile.players:
                            display.append(
                                Text(
                                    "@ ",
                                    "yellow"
                                    if player["uid"] == self.main_app.uid
                                    else "blue",
                                )
                            )
                            break
                        else:
                            display.append(
                                Text(
                                    "▆ ",
                                    f"rgb({','.join((str(i) for i in tile.color))})",
                                )
                            )
                        break
                else:
                    display.append(Text("▆ "))

            map_grid.add_row(*display)

        self.grid = map_grid

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
