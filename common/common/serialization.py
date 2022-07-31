# serialize schemas from dictionaries
import typing

from .schemas import (
    CLIENT_REQUEST,
    DEATH,
    SERVER_RESPONSE,
    WIN,
    ActionNoTargetRequest,
    ActionResponse,
    ActionUpdateMessage,
    ActionWithTargetRequest,
    ChatMessage,
    InitializePlayer,
    LevelUpNotification,
    MapUpdate,
    MovementRequest,
    MovementUpdateMessage,
    RegistrationSuccessful,
    RoomChangeUpdate,
)

SERVER_RESPONSE_TYPES: dict[str, type[SERVER_RESPONSE]] = {}


def deserialize_client_request(event: dict[str, typing.Any]) -> CLIENT_REQUEST:
    match event:
        case {"type": "chat"}:
            return ChatMessage(**event)
        case {"type": "action", "target": _}:
            return ActionWithTargetRequest(**event)
        case {"type": "action"}:
            return ActionNoTargetRequest(**event)
        case {"type": "init"}:
            return InitializePlayer(**event)
        case {"type": "move"}:
            return MovementRequest(**event)
        case _:
            raise NotImplementedError(f"unknown event type `{event['type']}`")


def deserialize_server_response(event: dict[str, typing.Any]) -> SERVER_RESPONSE:
    match event:
        case {"type": "chat"}:
            return ChatMessage(**event)
        case {"type": "registration_successful"}:
            return RegistrationSuccessful(**event)
        case {"type": "action_response"}:
            return ActionResponse(**event)
        case {"type": "map_update"}:
            return MapUpdate(**event)
        case {"type": "update"}:
            return ActionUpdateMessage(**event)
        case {"type": "room_change"}:
            return RoomChangeUpdate(**event)
        case {"type": "DEATH"}:
            return DEATH(**event)
        case {"type": "WIN"}:
            return WIN(**event)
        case {"type": "level_up"}:
            return LevelUpNotification(**event)
        case {"type": "movement_update"}:
            return MovementUpdateMessage(**event)
        case _:
            raise NotImplementedError(f"unknown event type `{event['type']}`")


__all__ = ("deserialize_client_request", "deserialize_server_response")
