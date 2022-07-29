import asyncio
import json

import websockets
from game_components.game import Game
from game_components.game_objects import Player
from mess_up_actions import MessedPlayer
from schemas import (
    ActionNoTargetRequest,
    ActionWithTargetRequest,
    ChatMessage,
    InitializePlayer,
    PlayerSchema,
    RegistrationSuccessful,
)
from websockets.exceptions import InvalidMessage
from websockets.legacy.server import WebSocketServerProtocol

TIME_BETWEEN_ROUNDS = 10  # Seconds between each round.

connections: dict[
    int, WebSocketServerProtocol
] = {}  # Player UID as key and connection as value.
messed_players: dict[int, MessedPlayer] = {}
game = Game()


async def initialize_player(connection: WebSocketServerProtocol) -> Player:
    """Initializes a player in the game, and returns the initialized player."""
    message = await connection.recv()
    event = InitializePlayer.parse_obj(json.loads(message))

    if event.type != "init":
        raise InvalidMessage("Expected an `init` message.")

    username = event.username
    print(message)  # TODO: remove this later.
    player = Player(username, ["spit", "bite"])

    game.add_player(player, 1, 1)

    messed_players[player.uid] = MessedPlayer(player)

    return player


async def register(websocket: WebSocketServerProtocol) -> None:
    """Adds a player's connections to connections and removes them when they disconnect."""
    registered_player = await initialize_player(websocket)

    player_schema = PlayerSchema(
        uid=registered_player.uid,
        name=registered_player.name,
        allowed_actions=set(registered_player.allowed_actions),
    )
    registration_response = RegistrationSuccessful(
        type="registration_successful", player=player_schema
    )

    await websocket.send(registration_response.json())
    connections[registered_player.uid] = websocket

    try:
        await handler(websocket)
    finally:
        del connections[registered_player.uid]


async def handler(websocket: WebSocketServerProtocol) -> None:
    async for message in websocket:
        event = json.loads(message)
        print(event)  # TODO: remove this later.

        match event:
            case {
                "type": "chat",
                "player_name": player_name,
                "chat_message": chat_message,
            }:
                response = ChatMessage(
                    type="chat",
                    player_name=player_name,
                    chat_message=chat_message,
                )

                websockets.broadcast(connections.values(), response.json())
            case {"type": "action", "target": _}:
                event_unpacked = ActionWithTargetRequest(**event)
                await handle_action_with_target(event_unpacked, websocket)
            case {"type": "action"}:
                event_unpacked = ActionNoTargetRequest(**event)
                await handle_action_without_target(event_unpacked, websocket)
            case _:
                raise NotImplementedError(f"unknown event type `{event['type']}`")


async def handle_action_with_target(
    req: ActionWithTargetRequest, ws: WebSocketServerProtocol
):
    action = messed_players[req.player].actions.get(req.action)
    assert action

    if action.requires_target:
        # TODO: actually do something with the action.
        response = {
            "type": "action_response",
            "response": f"Got it! So you want to {action.name}!",
        }
    elif action is not None:
        response = {
            "type": "action_response",
            "response": f"{req.action} doesn't take any targets!",
        }
    else:
        response = {"type": "action_response", "response": f"You can't {req.action}!"}

    await ws.send(json.dumps(response))


async def handle_action_without_target(
    req: ActionNoTargetRequest, ws: WebSocketServerProtocol
):
    action = messed_players[req.player].actions.get(req.action)
    assert action

    if not action.requires_target:
        # TODO: actually do something with the action.
        response = {
            "type": "action_response",
            "response": f"Got it! So you want to {action.name}!",
        }
    elif action is not None:
        response = {
            "type": "action_response",
            "response": f"{req.action} needs a target!",
        }
    else:
        response = {"type": "action_response", "response": f"You can't {req.action}!"}

    await ws.send(json.dumps(response))


async def websocket_handling() -> None:
    async with websockets.serve(register, "localhost", 8765):
        await asyncio.Future()  # run forever


async def game_loop():
    """Here we run each tick of the game."""
    while True:
        await asyncio.sleep(TIME_BETWEEN_ROUNDS)
        # HANDLING EACH TICK GOES HERE.


async def main() -> None:
    await asyncio.gather(websocket_handling(), game_loop())


asyncio.run(main())
