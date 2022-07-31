from __future__ import annotations

import functools
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


P = typing.ParamSpec("P")
R = typing.TypeVar("R")


def enforce_initialization(
    func: typing.Callable[typing.Concatenate[Console, P], typing.Awaitable[str]]
) -> typing.Callable[typing.Concatenate[Console, P], typing.Awaitable[str]]:
    """Simple wrapper that makes sure the player is registered before doing certain actions."""

    @functools.wraps(func)
    async def wrapper(self: Console, *args: P.args, **kwargs: P.kwargs) -> str:
        if self.main_app.initialized:
            return await func(self, *args, **kwargs)
        else:
            return "You must register before doing this action."

    return wrapper


class ConsoleLog(Widget):
    HELP_MESSAGE = "Type `/help` to view all available commands. Use up/down keys to navigate the logs."
    REGISTER_MESSAGE = (
        "Type `/register [USERNAME]` to enter the game with your username."
    )
    ACTIONS_MESSAGE = "Actions are prefixed with !, use them to control your bug."

    console_log: list[str] = [HELP_MESSAGE, REGISTER_MESSAGE, ACTIONS_MESSAGE]
    full_log: list[str] = [HELP_MESSAGE, REGISTER_MESSAGE, ACTIONS_MESSAGE]
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

    def get_display_logs(self) -> list[str]:
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
        "actions": "Actions are prefixed with !, use them to control your bug.",
    }

    mouse_over = Reactive(False)
    message = ""
    console_log: list[str] = []
    out: ConsoleLog = ConsoleLog()

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
        if self.main_app.is_dead:
            return  # Sorry, no inputs for you!

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
            case ["!move", direction]:
                if direction in ["north", "south", "east", "west"]:
                    log_display = await self.handle_movement(direction)
                else:
                    log_display = f"{direction} isn't a direction!"
            case [("!flee" | "!nvm" | "!clear") as action]:
                log_display = await self.handle_action_without_target(action)
            case [action, target] if self.message.startswith("!"):
                log_display = await self.handle_action_with_target(action, target)
            case [action] if self.message.startswith("!"):
                log_display = await self.handle_action_without_target(action)
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

    @enforce_initialization
    async def handle_action_with_target(self, action: str, target: str) -> str:
        target_uid = self.get_target(target)

        if target:
            message = {
                "type": "action",
                "action": action[1:],
                "target": target_uid,
                "player": self.main_app.uid,
            }
            await self.main_app.websocket.send(json.dumps(message))
            return ""
        else:
            return "That target doesn't exist!"

    @enforce_initialization
    async def handle_action_without_target(self, action: str) -> str:
        message = {"type": "action", "action": action[1:], "player": self.main_app.uid}
        await self.main_app.websocket.send(json.dumps(message))
        return ""

    @enforce_initialization
    async def handle_movement(self, direction: str) -> str:
        message = {"type": "move", "direction": direction, "player": self.main_app.uid}
        await self.main_app.websocket.send(json.dumps(message))
        return ""

    def get_target(self, target_name: str) -> int | None:
        """Gets a target name and then returns the target's UID.

        Returns None if the target name doesn't exist.
        """
        return (
            1  # TODO: this doesn't feel like an UID. TODO: Check if the target exists.
        )


def display_help(all_commands: dict[str, str]) -> str:
    """Returns a string with information about all available commands."""
    ret = ""

    for k, v in all_commands.items():
        ret += f"{k}: {v}\n"

    return ret[:-1]  # Ignore the last "\n".
