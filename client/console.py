from __future__ import annotations

import json
import typing

from rich import box
from rich.layout import Layout
from rich.panel import Panel
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

if typing.TYPE_CHECKING:
    from main import GameInterface


class ConsoleLog(Widget):
    HELP_MESSAGE = "Type `/help` to view all available commands. Use up/down keys to navigate the logs."
    REGISTER_MESSAGE = (
        "Type `/register [USERNAME]` to enter the game with your username."
    )

    console_log: list[str] = [HELP_MESSAGE, REGISTER_MESSAGE]
    full_log: list[str] = [HELP_MESSAGE, REGISTER_MESSAGE]
    reverse_log: Reactive[bool] = Reactive(False)
    scroll: Reactive[int] = Reactive(0)

    def render(self) -> Panel:
        if len(self.console_log) > 7:
            self.console_log.pop(0)

        display_log = self.get_display_logs()

        return Panel(
            "\n".join(display_log),
            border_style="white",
            box=box.SQUARE,
        )

    def add_log(self, log: str) -> None:
        self.console_log.append(log)
        self.full_log.append(log)
        self.refresh()

    def get_display_logs(self) -> str:
        """Returns the logs to be displayed, reversed and/or scrolled if necesary."""
        MAX_LOGS = 7

        display_log = self.console_log

        total_scroll_upper = MAX_LOGS + 1 + self.scroll

        if self.scroll:
            # Shift everything "up".
            display_log = ["You're viewing old messages."] + self.full_log[
                -total_scroll_upper : -self.scroll
            ]
        if self.reverse_log:
            display_log = list(reversed(display_log))

        return display_log

    def scroll_towards_new(self) -> None:
        """Moves the scroll towards the newer logs."""
        if self.scroll > 0:
            self.scroll -= 1

    def scroll_towards_old(self) -> None:
        """Moves the scroll towards the older logs."""
        if self.scroll < len(self.full_log):
            self.scroll += 1


class Console(Widget):
    """A textual widget that allows the user to type."""

    # This is the key textual registers when you press the DEL button.
    DELETE_KEY = "ctrl+h"

    ALL_COMMANDS = {
        "/register [USERNAME]": "Use this command to set your username and join the game.",
        "/reverse_console": "Reverses the way console logs are displayed.",
    }

    mouse_over = Reactive(False)
    message = ""
    console_log: list[str] = []
    out: ConsoleLog = ConsoleLog()

    initialized: bool = False

    def __init__(self, main_app: GameInterface, name: str | None = None) -> None:
        self.main_app = main_app
        super().__init__(name)

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

    async def on_key(self, event: events.Key):
        key = event.key
        match key:
            case "enter":
                if self.message:
                    result = await self.handle_message()
                    if result:
                        self.out.add_log(result)
                    # self.console_log.append(self.message)
                self.message = ""
            case self.DELETE_KEY:
                self.message = self.message[:-1]
            case "up":
                (
                    self.out.scroll_towards_old()
                    if not self.out.reverse_log
                    else self.out.scroll_towards_new()
                )
            case "down":
                (
                    self.out.scroll_towards_new()
                    if not self.out.reverse_log
                    else self.out.scroll_towards_old()
                )
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

    async def handle_message(self) -> str:
        """Handles input from the user.

        Takes the message that the user entered and decides if it's a valid command and how to handle it.
        Returns the message that should be displayed in the log.
        """
        log_display = ""

        match self.message.split():
            case ["/help"]:
                log_display = display_help(self.ALL_COMMANDS)
            case ["/reverse_console"]:
                self.out.reverse_log = not self.out.reverse_log
                log_display = "Console output reversed."
            case ["/register", username]:
                log_display = await self.register(username)
            case _ if self.message[0] == "/":
                log_display = f"Invalid command. {self.out.HELP_MESSAGE}"
            case _:
                # Treat commands without a leading slash as "chat" commands.
                log_display = await self.send_chat_message()

        return log_display

    async def register(self, username: str) -> str:
        """Sends an init request to the server to initialize our player."""
        request = {"type": "init", "username": username}
        await self.main_app.websocket.send(json.dumps(request))
        self.initialized = True

        return ""

    @staticmethod
    def enforce_initialization(func):
        """Simple wrapper that makes sure the player is registered before doing certain actions."""

        async def wrapper(self: Console, *args, **kwargs) -> str:
            if self.initialized:
                return await func(self, *args, **kwargs)
            else:
                return "You must register before doing this action."

        return wrapper

    @enforce_initialization
    async def send_chat_message(self) -> str:
        response = json.dumps(
            {
                "type": "chat",
                "player_name": self.main_app.name,
                "chat_message": self.message,
            }
        )
        await self.main_app.websocket.send(response)
        return ""


def display_help(all_commands: dict) -> str:
    """Returns a string with information about all available commands."""
    ret = ""

    for k, v in all_commands.items():
        ret += f"{k}: {v}\n"

    return ret[:-1]  # Ignore the last "\n".
