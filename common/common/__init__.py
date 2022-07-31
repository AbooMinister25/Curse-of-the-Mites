"""Shared schema code!"""
from .schemas import (
    CLIENT_REQUEST,
    MESSAGE,
    SERVER_RESPONSE,
    ActionNoTargetRequest,
    ActionResponse,
    ActionWithTargetRequest,
    ChatMessage,
    InitializePlayer,
    MapUpdate,
    PlayerSchema,
    RegistrationSuccessful,
)
from .serialization import deserialize_client_request, deserialize_server_response

__all__ = (
    # schemas.py
    "CLIENT_REQUEST",
    "MESSAGE",
    "SERVER_RESPONSE",
    "ActionNoTargetRequest",
    "ActionResponse",
    "ActionWithTargetRequest",
    "ChatMessage",
    "InitializePlayer",
    "PlayerSchema",
    "RegistrationSuccessful",
    "MapUpdate",
    # serialization.py
    "deserialize_client_request",
    "deserialize_server_response",
)
