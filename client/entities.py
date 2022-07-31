from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget


class Entities(Widget):
    entities: Reactive[dict[int, str]] = Reactive({})

    def render(self) -> Panel:
        return Panel(
            Padding(
                Align.left("\n".join(list(self.entities.values())), vertical="top")
            ),
            border_style="green",
            title="Entities",
        )
