from rich import box
from rich.layout import Layout
from rich.panel import Panel
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget


class ConsoleLog(Widget):
    console_log: list[str] = []
    full_log: list[str] = []
    reverse_log: Reactive[bool] = Reactive(False)

    def render(self) -> Panel:
        if len(self.console_log) > 7:
            self.console_log.pop(0)

        display_log = (
            self.console_log
            if not self.reverse_log
            else list(reversed(self.console_log))
        )

        return Panel(
            "\n".join(display_log),
            border_style="white",
            box=box.SQUARE,
        )

    def add_log(self, log: str) -> None:
        self.console_log.append(log)
        self.full_log.append(log)
        self.refresh()


class Console(Widget):
    """A textual widget that allows the user to type."""

    # This is the key textual registers when you press the DEL button.
    DELETE_KEY = "ctrl+h"

    mouse_over = Reactive(False)
    message = ""
    console_log: list[str] = []
    out: ConsoleLog = ConsoleLog()

    def render(self) -> Panel:
        message_panel = Panel(
            self.message,
            border_style="white",
            box=box.SQUARE,
        )

        display = Layout()
        display.split_column(
            Layout(self.out, name="console", ratio=3),
            Layout(message_panel, name="message"),
        )

        return Panel(
            display,
            border_style="green" if self.mouse_over else "blue",
            title="Console",
        )

    def on_key(self, event: events.Key):
        key = event.key
        match key:
            case "enter":
                if self.message:
                    result = self.handle_message(self.message)
                    self.out.add_log(result)
                    # self.console_log.append(self.message)
                self.message = ""
            case self.DELETE_KEY:
                self.message = self.message[:-1]
            case _ if "ctrl" in key:
                # Special keys (DEL, tab, etc.), are registered with a "ctrl" in front, we want to ignore them.
                pass
            case _ if key in {"up", "down", "right", "left"}:
                # Arrow keys
                pass
            case _:
                self.message += key

        self.refresh()

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def handle_message(self, message: str) -> str:
        """Handles input from the user.

        Takes the message that the user entered and decides if it's a valid command and how to handle it.
        Returns the message that should be displayed in the log.
        """
        command = message.casefold()  # Let's have a case insensitive console :)

        log_display = ""
        if command == "/console_reverse":
            self.out.reverse_log = not self.out.reverse_log
            log_display = "Console output reversed."
        else:
            log_display = "Invalid command."

        return log_display
