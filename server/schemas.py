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