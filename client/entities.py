from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget


class Entities(Widget):
    mouse_over = Reactive(False)
    entities: Reactive[dict[int, str]] = Reactive({})

    def render(self) -> Panel:
        return Panel(
            Padding(
                Align.left("\n".join(list(self.entities.values())), vertical="top")
            ),
            border_style="green" if self.mouse_over else "blue",
            title="Entities",
        )

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
