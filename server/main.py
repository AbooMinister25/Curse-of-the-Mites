import asyncio
import json

import websockets
from websockets.exceptions import InvalidMessage

from game_components.game import Game
from game_components.game_objects import Player
from schemas import ChatEvent, RequestEvent

connections = set()
game = Game()


async def initialize_player(connection):
    """Initializes a player in the game"""
    init = RequestEvent(type="init", data="Provide a username")
    await connection.send(init.json())

    message = await connection.recv()
    event = RequestEvent.parse_obj(json.loads(message))

    if event.type != "init":
        raise InvalidMessage("Expected an `init` message.")

    username = event.data
    print(message)
    player = Player(username, ["spit", "bite"])
    game.add_player(player, 1, 1)


async def register(websocket):
    """Adds a player's connections to connections and removes them when they disconnect."""
    await initialize_player(websocket)
    connections.add(websocket)

    try:
        await handler(websocket)
    finally:
        connections.remove(websocket)


async def handler(websocket):
    async for message in websocket:
        event = json.loads(message)
        print(event)  # TODO: remove this later.
        match event["type"]:
            case "chat":
                response = ChatEvent(type="chat", chat_message=event["chat_message"])
                websockets.broadcast(connections, response.json())


async def main():
    async with websockets.serve(register, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
