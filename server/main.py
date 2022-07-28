import asyncio
import json

import websockets
from game_components.game import Game
from game_components.game_objects import Player
from schemas import ChatEvent, RegistrationSuccess, RequestEvent
from websockets.exceptions import InvalidMessage

TIME_BETWEEN_ROUNDS = 10  # Seconds between each round.

connections = {}
game = Game()


async def initialize_player(connection) -> Player:
    """Initializes a player in the game, and returns the initialized player."""
    message = await connection.recv()
    event = RequestEvent.parse_obj(json.loads(message))

    if event.type != "init":
        raise InvalidMessage("Expected an `init` message.")

    username = event.data
    print(message)
    player = Player(username, ["spit", "bite"])
    game.add_player(player, 1, 1)
    return player


async def register(websocket):
    """Adds a player's connections to connections and removes them when they disconnect."""
    registered_player = await initialize_player(websocket)

    registration_response = RegistrationSuccess(registered_player)
    await websocket.send(registration_response.json())

    connections[registered_player.uid] = websocket

    try:
        await handler(websocket)
    finally:
        del connections[registered_player.uid]


async def handler(websocket):
    async for message in websocket:
        event = json.loads(message)
        print(event)  # TODO: remove this later.
        match event:
            case {
                "type": "chat",
                "player_name": player_name,
                "chat_message": chat_message,
            }:
                response = ChatEvent(
                    type="chat", player_name=player_name, chat_message=chat_message
                )
                websockets.broadcast(connections.values(), response.json())


async def websocket_handling():
    async with websockets.serve(register, "localhost", 8765):
        await asyncio.Future()  # run forever


async def game_loop():
    """Here we run each tick of the game."""
    while True:
        await asyncio.sleep(TIME_BETWEEN_ROUNDS)
        # HANDLING EACH TICK GOES HERE.


async def main():
    await asyncio.gather(websocket_handling(), game_loop())


asyncio.run(main())
