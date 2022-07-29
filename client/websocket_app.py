import asyncio
from typing import Any

import websockets
from rich.console import Console
from textual.app import App
from textual.driver import Driver
from websockets.legacy.client import WebSocketClientProtocol


class WebsocketApp(App):
    """A textual app meant to allow sending and receiving websocket messages."""

    def __init__(
        self,
        websocket: WebSocketClientProtocol,
        screen: bool = True,
        driver_class: type[Driver] | None = None,
        log: str = "",
        log_verbosity: int = 1,
        title: str = "Textual Application",
    ):
        self.websocket = websocket
        super().__init__(screen, driver_class, log, log_verbosity, title)

    async def handle_messages(self):
        """This method is meant to be overriden in order to handle receiving messages from a websocket."""
        await asyncio.Future()

    @classmethod
    def run(
        cls,
        console: Console | None = None,
        screen: bool = True,
        driver: type[Driver] | None = None,
        **kwargs: Any,
    ):
        """Run the app.

        Args:
            console (Console, optional): Console object. Defaults to None.
            screen (bool, optional): Enable application mode. Defaults to True.
            driver (type[Driver], optional): Driver class or None for default. Defaults to None.
        """
        # TODO: Allow connecting to a specific websocket port.
        async def run_app() -> None:
            async with websockets.connect("ws://localhost:8765") as websocket:
                app = cls(
                    screen=screen, driver_class=driver, websocket=websocket, **kwargs
                )

                # Using gather allows our TUI and our message receiving to happen concurrently.
                await asyncio.gather(app.process_messages(), app.handle_messages())

        asyncio.run(run_app())
