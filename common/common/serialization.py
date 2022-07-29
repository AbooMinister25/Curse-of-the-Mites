# serialize schemas from dictionaries
import typing

from .schemas import (
    CLIENT_REQUEST,
    SERVER_RESPONSE,
    ActionNoTargetRequest,
    ActionResponse,
    ActionWithTargetRequest,
    ChatMessage,
    InitializePlayer,
    RegistrationSuccessful,
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
        case _:
            raise NotImplementedError(f"unknown event type `{event['type']}`")


__all__ = ("deserialize_client_request", "deserialize_server_response")
