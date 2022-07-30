import json
from typing import Optional

from available_commands import AvailableCommands
from console import Console
from entities import Entities
from map import Map
from websocket_app import WebsocketApp

from common.schemas import (
    ActionResponse,
    ActionUpdateMessage,
    ChatMessage,
    RegistrationSuccessful,
)
from common.serialization import deserialize_server_response


class GameInterface(WebsocketApp):
    """Textual MUD client"""

    name: Optional[str] = None
    uid: Optional[int] = None
    initialized: bool = False

    async def on_mount(self) -> None:
        grid = await self.view.dock_grid(edge="left", name="left")

        grid.add_column(fraction=1, name="left")
        grid.add_column(fraction=2, name="center")
        grid.add_column(fraction=1, name="right")

        grid.add_row(fraction=1, name="top", min_size=2)
        grid.add_row(fraction=1, name="middle")
        grid.add_row(fraction=1, name="bottom")

        grid.add_areas(
            map_area="left-start|center-end,top-start|middle-end",
            entities_area="right,top-start|middle-end",
            events_area="left-start|center-end,bottom",
            available_commands_area="right,bottom",
        )

        self.console_widget = Console(main_app=self, name="Console")
        self.available_commands_widget = AvailableCommands(
            main_app=self, name="Available Commands"
        )

        grid.place(
            map_area=Map(),
            entities_area=Entities(),
            events_area=self.console_widget,
            available_commands_area=self.available_commands_widget,
        )

    async def handle_messages(self):
        """Allows receiving messages from a websocket and handling them."""
        async for message in self.websocket:
            event = deserialize_server_response(json.loads(message))
            match event:
                case ChatMessage():
                    self.console_widget.out.add_log(
                        f"{event.player_name}: {event.chat_message}"
                    )
                    self.console_widget.refresh()
                case RegistrationSuccessful():
                    self.initialized = True
                    self.name = event.player.name
                    self.uid = event.player.uid
                    self.available_commands_widget.add_commands(
                        event.player.allowed_actions
                    )
                    self.console_widget.name = self.name
                    self.console_widget.out.add_log(
                        f"Correctly registered as {self.name}"
                    )
                    self.console_widget.refresh()
                case ActionResponse():
                    self.console_widget.out.add_log(event.response)
                    self.console_widget.refresh()
                case ActionUpdateMessage():
                    self.console_widget.out.add_log(event.message)
                    self.console_widget.refresh()
                case _:
                    raise NotImplementedError(f"Unknown event {event!r}")


try:
    GameInterface.run(log="textual.log")
except ConnectionRefusedError:
    print("Make sure there's a server running before trying to run the client.")
