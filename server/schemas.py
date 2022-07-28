from game_components.game_objects import Player
from pydantic import BaseModel
from typing_extensions import Literal


class Event(BaseModel):
    type: str


class ChatEvent(Event):
    """Sent by the client when they wish to chat with the rest of the server."""

    type: Literal["chat"]
    chat_message: str


class RequestEvent(BaseModel):
    """Sent by either the server or client to ask for some information"""

    type: Literal["init"]
    data: str


class RegistrationSuccess(BaseModel):
    """Sent by the server when the player successfully registers."""

    type: Literal["registration_successful"]
    data: dict

    def __init__(__pydantic_self__, player: Player) -> None:
        """We don't want to send ALL the information about the player."""
        init_data = {"type": "registration_successful"}

        data = {}
        data["uid"] = player.uid
        data["name"] = player.name
        # Don't send the full actions information, only it's names.
        data["allowed_actions"] = set(player.allowed_actions.keys())

        init_data["data"] = data
        super().__init__(**init_data)
