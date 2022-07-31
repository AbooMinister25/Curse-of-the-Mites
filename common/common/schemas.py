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


class RoomChangeUpdate(MessageBase[Literal["room_change"]]):
    """Message sent by the server after an entity enters or leaves a room."""

    room_uid: int
    entity_uid: int
    entity_name: str
    enters: bool  # If False then it's leaving.


class MapUpdate(MessageBase[Literal["map_update"]]):
    """Sent by the server to update the client on the details of the map"""

    map: list[ExportedData]
    entities: list[RoomChangeUpdate]


class RegistrationSuccessful(MessageBase[Literal["registration_successful"]]):
    """Sent by the server when the player successfully registers."""

    player: PlayerSchema
    map: MapUpdate


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


class ActionUpdateMessage(MessageBase[Literal["update"]]):
    """Message sent by the server after a game ticks.

    It contains a message to be displayed about the result of the player's queued action.
    """

    message: str


class MovementUpdateMessage(MessageBase[Literal["movement_update"]]):
    """Message sent to the player after they try to move."""

    message: str
    map_update: MapUpdate | None


class RoomInformationMessage(MessageBase[Literal["room_info"]]):
    """Message sent to a player that's entering a new room."""

    entities: list[RoomChangeUpdate]


class LevelUpNotification(MessageBase[Literal["level_up"]]):
    """Message sent by the server to a player that levels up."""

    times_leveled: int  # In case a player levels up more than once.
    current_level: int


class DEATH(MessageBase[Literal["DEATH"]]):
    """Too bad! You died.

    Sent to the player when they get an ice cream :P
    """


class WIN(MessageBase[Literal["WIN"]]):
    """Congrats! You win."""


CLIENT_REQUEST = (
    ChatMessage
    | InitializePlayer
    | ActionNoTargetRequest
    | ActionWithTargetRequest
    | MovementRequest
)

SERVER_RESPONSE = (
    RegistrationSuccessful
    | LevelUpNotification
    | ActionResponse
    | ChatMessage
    | ActionUpdateMessage
    | RoomChangeUpdate
    | DEATH
    | WIN
    | MapUpdate
    | MovementUpdateMessage
)
MESSAGE = CLIENT_REQUEST | SERVER_RESPONSE
