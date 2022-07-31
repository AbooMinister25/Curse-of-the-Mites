import json
from typing import Optional

from available_commands import AvailableCommands
from console import Console
from entities import Entities
from map import Map, RenderData
from websocket_app import WebsocketApp

from common.schemas import (
    DEATH,
    WIN,
    ActionResponse,
    ActionUpdateMessage,
    ChatMessage,
    LevelUpNotification,
    MovementUpdateMessage,
    RegistrationSuccessful,
    RoomChangeUpdate,
)
from common.serialization import deserialize_server_response


class GameInterface(WebsocketApp):
    """Textual MUD client"""

    name: Optional[str] = None
    uid: Optional[int] = None
    initialized: bool = False
    won: bool = False
    lost: bool = False

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
        self.map = Map(main_app=self, name="Map")

        self.entities = Entities()

        grid.place(
            map_area=self.map,
            entities_area=self.entities,
            events_area=self.console_widget,
            available_commands_area=self.available_commands_widget,
        )

    async def handle_messages(self):
        """Allows receiving messages from a websocket and handling them."""
        async for message in self.websocket:
            if self.won or self.lost:
                continue  # No message processing for you.

            event = deserialize_server_response(json.loads(message))
            match event:
                case ChatMessage():
                    self.console_widget.out.add_log(
                        f"{event.player_name}: {event.chat_message}"
                    )
                case RegistrationSuccessful():
                    self.initialized = True
                    self.name = event.player.name
                    self.uid = event.player.uid
                    self.available_commands_widget.add_commands(
                        event.player.allowed_actions
                    )
                    self.available_commands_widget.refresh()

                    self.console_widget.name = self.name
                    self.console_widget.out.add_log(
                        f"Correctly registered as {self.name}"
                    )
                    self.console_widget.refresh()

                    tiles = [
                        RenderData(room["color"], room["x"], room["y"], room["players"])
                        for room in event.map.map
                    ]

                    self.map.render_from(tiles)
                    self.map.refresh()

                    self._handle_room_change(event.map.entities)
                case MovementUpdateMessage():
                    self.console_widget.out.add_log(event.message)

                    map_update = event.map_update
                    if map_update is not None:
                        tiles = [
                            RenderData(
                                room["color"], room["x"], room["y"], room["players"]
                            )
                            for room in map_update.map
                        ]
                        self.console_widget.out.add_log(
                            map_update.entities[-1].entity_name
                        )
                        self._handle_room_change(map_update.entities)

                        self.map.render_from(tiles)
                        self.map.refresh()
                    self.available_commands_widget.refresh()
                case ActionResponse():
                    self.console_widget.out.add_log(event.response)
                case ActionUpdateMessage():
                    self.console_widget.out.add_log(event.message)
                case RoomChangeUpdate():
                    e_or_l = "entered" if event.enters else "left"
                    self.console_widget.out.add_log(
                        f"`{event.entity_name}` {e_or_l} the room!"
                    )
                    self._handle_rc_updates(
                        [
                            event,
                        ]
                    )
                case LevelUpNotification():
                    leveled = (
                        "!"
                        if event.times_leveled == 1
                        else f" {event.times_leveled} times!"
                    )
                    message = f"You leveled up{leveled} You are now level {event.current_level}"
                    self.console_widget.out.add_log(message)
                case DEATH():
                    # TODO: more properly display the death.
                    self.initialized = False
                    self.lost = True
                    self.map.refresh()
                    self.console_widget.message = ""
                    self.console_widget.out.console_log = []
                    self.console_widget.out.full_log = (
                        self.console_widget.out.console_log
                    )
                case WIN():
                    self.initialized = False
                    self.won = True  # A happy kind of game over :)
                    self.map.refresh()
                    self.console_widget.message = ""
                    self.console_widget.out.console_log = []
                    self.console_widget.out.full_log = (
                        self.console_widget.out.console_log
                    )
                case _:
                    raise NotImplementedError(f"Unknown event {event!r}")

            self.console_widget.refresh()

    def _handle_room_change(self, rc_updates: list[RoomChangeUpdate]) -> None:
        self.entities.entities = (
            {}
        )  # All the mobs from the room we left aren't here anymore.

        self._handle_rc_updates(rc_updates)

    def _handle_rc_updates(self, rc_updates: list[RoomChangeUpdate]) -> None:
        for rc in rc_updates:
            if rc.enters:
                if not rc.entity_uid == self.uid:
                    self.entities.entities[rc.entity_uid] = rc.entity_name
            else:
                if rc.entity_uid in self.entities.entities:
                    del self.entities.entities[rc.entity_uid]

        self.entities.refresh()


try:
    GameInterface.run(log="textual.log")
except ConnectionRefusedError:
    print("Make sure there's a server running before trying to run the client.")
