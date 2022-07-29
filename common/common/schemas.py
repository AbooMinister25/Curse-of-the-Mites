from typing import Literal

from pydantic import BaseModel


class MessageBase(BaseModel):
    """Base schema for a message"""

    type: str


class ChatMessage(MessageBase):
    """Sent by the client when they wish to chat with the rest of the server."""

    player_name: str
    chat_message: str


class InitializePlayer(MessageBase):
    """Sent by the client when they want to initialize a player"""

    username: str


class PlayerSchema(BaseModel):
    """Represents the JSON for a player"""

    uid: int
    name: str
    allowed_actions: set[str]


class RegistrationSuccessful(MessageBase):
    """Sent by the server when the player successfully registers."""

    player: PlayerSchema


class ActionNoTargetRequest(BaseModel):
    """Request sent by the client when they want to do an action without a target."""

    type: Literal["action"]
    action: str
    target: int
    player: int  # The player that's trying to perform the action.


class ActionWithTargetRequest(BaseModel):
    """Request sent by the client when they want to do an action with a target."""

    type: Literal["action"]
    action: str
    player: int  # The player that's trying to perform the action.
