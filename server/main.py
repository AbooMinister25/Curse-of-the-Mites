import asyncio
import json

import websockets
from game_components.game import Game
from game_components.game_objects import Player
from mess_up_actions import MessedPlayer
from websockets.exceptions import InvalidMessage
from websockets.legacy.server import WebSocketServerProtocol

from common.schemas import (
    CLIENT_REQUEST,
    ActionNoTargetRequest,
    ActionResponse,
    ActionWithTargetRequest,
    ChatMessage,
    InitializePlayer,
    PlayerSchema,
    RegistrationSuccessful,
)
from common.serialization import deserialize_client_request

TIME_BETWEEN_ROUNDS = 10  # Seconds between each round.

connections: dict[
    int, WebSocketServerProtocol
] = {}  # Player UID as key and connection as value.
messed_players: dict[int, MessedPlayer] = {}
game = Game()


def deserialize(message: str | bytes) -> CLIENT_REQUEST:
    return deserialize_client_request(json.loads(message))


async def initialize_player(connection: WebSocketServerProtocol) -> Player:
    """Initializes a player in the game, and returns the initialized player."""
    event = deserialize(await connection.recv())

    if not isinstance(event, InitializePlayer):
        raise InvalidMessage("Expected an `init` message.")

    username = event.username
    player = Player(username, ["spit", "bite"], game)

    game.add_player(player, 1, 1)

    messed_players[player.uid] = MessedPlayer(player)

    return player


async def register(websocket: WebSocketServerProtocol) -> None:
    """Adds a player's connections to connections and removes them when they disconnect."""
    registered_player = await initialize_player(websocket)

    registration_response = RegistrationSuccessful(
        type="registration_successful",
        player=PlayerSchema(
            uid=registered_player.uid,
            name=registered_player.name,
            allowed_actions=set(registered_player.allowed_actions),
        ),
    )

    await websocket.send(registration_response.json())
    connections[registered_player.uid] = websocket

    try:
        await handler(websocket)
    finally:
        del connections[registered_player.uid]


async def handler(websocket: WebSocketServerProtocol) -> None:
    async for message in websocket:
        event = deserialize(message)
        match event:
            case ChatMessage():
                websockets.broadcast(connections.values(), event.json())
            case ActionWithTargetRequest():
                await handle_action_with_target(event, websocket)
            case ActionNoTargetRequest():
                await handle_action_without_target(event, websocket)
            case _:
                raise NotImplementedError(f"Unknown event {event!r}")


async def handle_action_with_target(
    req: ActionWithTargetRequest, ws: WebSocketServerProtocol
):
    action = messed_players[req.player].actions.get(req.action)
    assert action

    if action.requires_target:
        result = game.get_player(req.player).add_command_to_queue(
            req.action, req.target
        )
        response = ActionResponse(type="action_response", response=result.message)
    elif action is not None:
        response = ActionResponse(
            type="action_response",
            response=f"{req.action} doesn't take any targets!",
        )
    else:
        response = ActionResponse(
            type="action_response", response=f"You can't {req.action}!"
        )

    await ws.send(response.json())


async def handle_action_without_target(
    req: ActionNoTargetRequest, ws: WebSocketServerProtocol
):
    action = messed_players[req.player].actions.get(req.action)
    assert action

    response = None
    if not action.requires_target:
        result = game.get_player(req.player).add_command_to_queue(req.action)
        response = ActionResponse(type="action_response", response=result.message)
    elif action is not None:
        response = ActionResponse(
            type="action_response",
            response=f"{req.action} needs a target!",
        )
    else:
        response = ActionResponse(
            type="action_response", response=f"You can't {req.action}!"
        )

    await ws.send(response.json())


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
