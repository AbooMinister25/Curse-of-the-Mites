from rich import box
from rich.layout import Layout
from rich.panel import Panel
from textual.reactive import Reactive
from textual.widget import Widget


class Console(Widget):
    """A textual widget that allows the user to type."""

    # This is the key textual registers when you press the DEL button.
    DELETE_KEY = "ctrl+h"

    mouse_over = Reactive(False)
    message = ""
    console_log: list[str] = []

    def render(self) -> Panel:
        # display = self.console_log + [self.message]

        message_panel = Panel(
            self.message,
            border_style="white",
            box=box.SQUARE,
        )
        console_panel = Panel(
            "\n".join(self.console_log),
            border_style="white",
            box=box.SQUARE,
        )

        # display = Layout(Group(console_panel, message_panel))
        display = Layout()
        display.split_column(
            Layout(console_panel, name="console", ratio=10),
            Layout(message_panel, name="message"),
        )

        return Panel(
            display,
            border_style="green" if self.mouse_over else "blue",
            title="Console",
        )

    def on_key(self, event):
        key = event.key
        match key:
            case "enter":
                if self.message:
                    self.console_log.append(self.message)
                self.message = ""
            case self.DELETE_KEY:
                self.message = self.message[:-1]
            case _ if "ctrl" in key:
                # Special keys (DEL, tab, etc.), are registered with a "ctrl" in front, we want to ignore them.
                pass
            case _:
                self.message += key

        self.refresh()

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
