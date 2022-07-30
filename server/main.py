import asyncio
import json

import websockets
from game_components.game import Game
from game_components.game_objects import ActionDict, Player
from mess_up_actions import MessedPlayer
from websockets.exceptions import InvalidMessage
from websockets.legacy.server import WebSocketServerProtocol

from common.schemas import (
    CLIENT_REQUEST,
    ActionNoTargetRequest,
    ActionResponse,
    ActionUpdateMessage,
    ActionWithTargetRequest,
    ChatMessage,
    InitializePlayer,
    MovementRequest,
    PlayerSchema,
    RegistrationSuccessful,
)
from common.serialization import deserialize_client_request

TIME_BETWEEN_ROUNDS = 6  # Seconds between each round.

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
            case MovementRequest():
                await handle_movement(event, websocket)
            case _:
                raise NotImplementedError(f"Unknown event {event!r}")


async def handle_action_with_target(
    req: ActionWithTargetRequest, ws: WebSocketServerProtocol
):
    action = messed_players[req.player].actions.get(req.action)

    if action is None:
        response = ActionResponse(
            type="action_response", response=f"You can't {req.action}!"
        )
    elif action.requires_target:
        game.get_player(req.player).add_command_to_queue(req.action, req.target)
        response = ActionResponse(
            type="action_response", response="Added action to queue."
        )
    else:
        response = ActionResponse(
            type="action_response",
            response=f"{req.action} doesn't take any targets!",
        )

    await ws.send(response.json())


async def handle_action_without_target(
    req: ActionNoTargetRequest, ws: WebSocketServerProtocol
):
    action = messed_players[req.player].actions.get(req.action)

    response = None
    if action is None:
        response = ActionResponse(
            type="action_response", response=f"You can't {req.action}!"
        )
    elif not action.requires_target:
        game.get_player(req.player).add_command_to_queue(req.action)
        response = ActionResponse(
            type="action_response", response="Added action to queue."
        )
    else:
        response = ActionResponse(
            type="action_response",
            response=f"{req.action} needs a target!",
        )

    await ws.send(response.json())


async def handle_movement(req: MovementRequest, ws: WebSocketServerProtocol):
    direction = messed_players[req.player].directions[req.direction]
    game.get_player(req.player).add_command_to_queue(direction)

    response = ActionResponse(type="action_response", response="Added move to queue.")

    await ws.send(response.json())


async def websocket_handling() -> None:
    async with websockets.serve(register, "localhost", 8765):
        await asyncio.Future()  # run forever


async def game_loop():
    """Here we run each tick of the game."""
    while True:
        await asyncio.sleep(TIME_BETWEEN_ROUNDS)
        # HANDLING EACH TICK GOES HERE.
        await game.update()

        await send_updates(game.out_queue)


async def send_updates(out_queue: asyncio.Queue):
    """Sends all the events in the queue to their respective players."""
    while not out_queue.empty():
        action = await out_queue.get()
        update: ActionUpdateMessage()
        player_uid: int
        match action:
            case {"caster": uid}:
                player_uid = uid
                update = ActionUpdateMessage(
                    type="update", message=get_action_update_message(action)
                )
            case {"player": uid, "direction": direction, "success": success}:
                player_uid = uid
                succeed = "succeed!" if success else "fail!"
                update = ActionUpdateMessage(
                    type="update",
                    message=f"You try moving {direction}... and {succeed}",
                )
            case int():
                player_uid = action
                update = ActionUpdateMessage(
                    type="update",
                    message="Time passes by, but you didn't do anything this round!",
                )
        player_connection = connections.get(player_uid)
        if player_connection is not None:
            await player_connection.send(update.json())
        # else: player disconnected.


def get_action_update_message(action: ActionDict) -> str:
    """A big mess to get a proper message for the action!"""
    target = game.get_mob(action["target"]) or game.get_player(action["target"])
    target_name = "yourself" if action["target"] == action["caster"] else target.name
    assert target

    tried = "attack" if action["dmg"] > 0 else "heal"
    health_affected = abs(action["dmg"])

    if not action["cast"]:
        message = f"You tried {tried}ing {target_name} but you don't have mana!"
    else:
        if action["hit"]:
            message = f"You {tried} for {health_affected} hit points!"
        else:
            message = f"You tried {tried}ing {target_name} but missed!"

    return message


async def main() -> None:
    await asyncio.gather(websocket_handling(), game_loop())


asyncio.run(main())
