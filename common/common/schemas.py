from typing import Generic, Literal, TypedDict, TypeVar

from pydantic import BaseModel

Type = TypeVar("Type", bound=str)


class MessageBase(BaseModel, Generic[Type]):
    """Base schema for a message"""

    type: Type


class ChatMessage(MessageBase[Literal["chat"]]):
    """Sent by the client (or server) when they wish to chat with the rest of the server."""

    player_name: str
    chat_message: str


class InitializePlayer(MessageBase[Literal["init"]]):
    """Sent by the client when they want to initialize a player"""

    username: str


class PlayerSchema(BaseModel):
    """Represents the JSON for a player"""

    uid: int
    name: str
    allowed_actions: set[str]


class ExportedData(TypedDict):
    uid: int
    color: tuple[int, int, int]
    display_char: str
    x: int
    y: int
    title: str
    description: str
    mobs: list
    players: list
    exits: list


class RegistrationSuccessful(MessageBase[Literal["registration_successful"]]):
    """Sent by the server when the player successfully registers."""

    player: PlayerSchema
    map: list[ExportedData]


class ActionNoTargetRequest(MessageBase[Literal["action"]]):
    """Request sent by the client when they want to do an action without a target."""

    action: str
    player: int  # The player that's trying to perform the action.


class ActionWithTargetRequest(MessageBase[Literal["action"]]):
    """Request sent by the client when they want to do an action with a target."""

    action: str
    target: int
    player: int  # The player that's trying to perform the action.


class MovementRequest(MessageBase[Literal["move"]]):
    """Request sent by the client when they want to move."""

    direction: str
    player: int


class ActionResponse(MessageBase[Literal["action_response"]]):
    """Response to an action which the client sent."""

    response: str


class MapUpdate(MessageBase[Literal["map_update"]]):
    """Sent by the server to update the client on the details of the map"""

    map: list[ExportedData]


CLIENT_REQUEST = (
    ChatMessage
    | InitializePlayer
    | ActionNoTargetRequest
    | ActionWithTargetRequest
    | MovementRequest
)
SERVER_RESPONSE = RegistrationSuccessful | ActionResponse | ChatMessage | MapUpdate
MESSAGE = CLIENT_REQUEST | SERVER_RESPONSE
