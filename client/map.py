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


STORY: list[str] = [
    "CURSE OF THE MITES",
    "This forest is plagued by Confusing Bugs!",
    "A pesky species of mites that infects other bugs and scrambles their brains...",
    "Your only hope as a caterpillar is to grow into a butterfly and escape the forest!",
    "(just kill a bunch of stuff and you'll be fine)",
]

DEATH: list[str] = [
    "YOU DIED.",
    "Press `ctrl+c` if you wish to leave this limbo.",
    "I know... it's a feature don't worry",
]


def WIN(name: str) -> list[str]:
    return [
        "`You became a beautiful butterfly and won!!!`",
        f"{name}: really, just like that?",
        "`Yup`.",
        f"{name}: just kill 5 mobs and win?",
        "`Mhmhm`",
        f"{name}: No metamorphosis? No coocoon? Nada?",
        "Well you see... you're a very special kind of butterfly... You're a `fyyachure` butterfly ;)",
        "Anyways... if you want more of a challenge try killing the 5 spiders I guess.",
    ]


class Map(Widget):

    grid = Reactive(make_map_grid())

    def __init__(self, main_app: "GameInterface", name: str | None = None):
        self.main_app = main_app
        super().__init__(name)

    def render(self) -> Panel:
        if self.main_app.lost:
            return Panel(
                Align.center("\n".join(DEATH), vertical="middle"),
                border_style="green",
                title="GAME OVER.",
            )
        if self.main_app.won:
            return Panel(
                Align.center("\n".join(WIN(self.main_app.name)), vertical="middle"),
                border_style="green",
                title="CONGRATS.",
            )
        if not self.main_app.initialized:
            return Panel(
                Align.center("\n".join(STORY), vertical="middle"),
                border_style="green",
                title="The Story.",
            )
        return Panel(
            Padding(Align.center(self.grid, vertical="middle")),
            border_style="green",
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
