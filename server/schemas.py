from pydantic import BaseModel
from typing_extensions import Literal


class Event(BaseModel):
    type: str

    def __init__(**kwargs):
        pass


class ChatEvent(Event):
    """Sent by the client when they wish to chat with the rest of the server."""

    type: Literal["chat"]
    chat_message: str
