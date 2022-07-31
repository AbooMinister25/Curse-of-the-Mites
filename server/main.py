import asyncio
import json

import websockets
from game_components.game import Game
from game_components.game_objects import (
    ActionDict,
    BaseRoom,
    Entity,
    FleeDict,
    MovementDict,
    Player,
    RoomActionDict,
)
from mess_up_actions import NO_SHUFFLE, MessedPlayer
from websockets.exceptions import InvalidMessage
from websockets.legacy.server import WebSocketServerProtocol

from common.schemas import (
    CLIENT_REQUEST,
    DEATH,
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
    PlayerSchema,
    RegistrationSuccessful,
    RoomChangeUpdate,
)
from common.serialization import deserialize_client_request

TIME_BETWEEN_ROUNDS = 6  # Seconds between each round.

connections: dict[
    int, WebSocketServerProtocol
] = {}  # Player UID as key and connection as value.
messed_players: dict[int, MessedPlayer] = {}


def deserialize(message: str | bytes) -> CLIENT_REQUEST:
    return deserialize_client_request(json.loads(message))


async def initialize_player(connection: WebSocketServerProtocol) -> Player:
    """Initializes a player in the game, and returns the initialized player."""
    event = deserialize(await connection.recv())

    if not isinstance(event, InitializePlayer):
        raise InvalidMessage("Expected an `init` message.")

    username = event.username
    player = Player(
        username, ["spit", "bite", "eat_berry", "sing", "stomp", "offer_berry"], game
    )

    game.add_player(player, 15, 24)
    messed_players[player.uid] = MessedPlayer(player)

    return player


async def register(websocket: WebSocketServerProtocol) -> None:
    """Adds a player's connections to connections and removes them when they disconnect."""
    registered_player = await initialize_player(websocket)

    map_rooms = [room.export() for room in game.rooms.values()]
    rc_update = (
        registered_player._create_room_change_update_list()
    )  # TODO this isn't private anymore.
    map_update = MapUpdate(type="map_update", map=map_rooms, entities=rc_update)

    registration_response = RegistrationSuccessful(
        type="registration_successful",
        player=PlayerSchema(
            uid=registered_player.uid,
            name=registered_player.name,
            allowed_actions=set(registered_player.allowed_actions),
        ),
        map=map_update,
    )

    await websocket.send(registration_response.json())
    connections[registered_player.uid] = websocket

    try:
        await handler(websocket)
    finally:
        player = game.get_player(registered_player.uid)
        assert player  # Shouldn't ever be None, so its probably fine to stick an assert here
        player.alive = False

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
        target = game.get_mob(req.target)

        if target is not None:
            game.get_player(req.player).add_command_to_queue(action.name, target)
            response = ActionResponse(
                type="action_response", response="Added action to queue."
            )
        else:
            response = ActionResponse(
                type="action_response",
                response="Whatever you were trying to hit is no longer there! (feature)",
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
    if req.action in NO_SHUFFLE:
        game.get_player(req.player).add_command_to_queue(req.action)
        response = ActionResponse(
            type="action_response", response=get_no_shuffle_response(req.action)
        )
    elif action is None:
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


def get_no_shuffle_response(action: str) -> str:
    message = "Added action to queue."
    if action == "nvm":
        message = "Cleared last action from your queue."
    elif action == "clear":
        message = "Cleared your entire movement queue."

    return message


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

        players_to_clean = game.clean_the_dead()

        for player_uid in players_to_clean:
            if player_uid in connections:
                connections.pop(player_uid)


async def send_updates(out_queue: asyncio.Queue):
    """Sends all the events in the queue to their respective players."""
    while not out_queue.empty():
        action = await out_queue.get()
        update: ActionUpdateMessage()
        player_uids: int | set
        match action:
            case RoomChangeUpdate():
                room = game.get_room(action.room_uid)
                player_uids = get_room_update_uids(room, action.entity_uid)
                update = action
            case {"type": (LevelUpNotification() as notif), "uid": uid}:
                player_uids = uid
                update = notif
            case {"type": (WIN() as win), "uid": player_uid}:
                player_uids = await get_win_update_uids(player_uid, win)
                player_name = game.get_player(player_uid).name
                update = ActionUpdateMessage(
                    type="update",
                    message=f"`{player_name}` became a beautiful butterfly and won!",
                )
            case {"caster": uid}:
                player_uids = uid
                update = ActionUpdateMessage(
                    type="update", message=get_action_update_message(action)
                )
            case {"player": uid, "direction": _}:
                # TODO
                player_uids = uid
                map_rs = action["map_update"]
                update = MovementUpdateMessage(
                    type="movement_update",
                    message=get_movement_message(action),
                    map_update=map_rs,
                )
            case {"player": uid, "fled": _}:
                player_uids = uid
                update = ActionUpdateMessage(
                    type="update",
                    message=get_fleeing_message(action),
                )
                pass
            case {"type": "room_action", "room": room}:
                player_uids = get_room_update_uids(room, action["action"]["caster"])
                update = ActionUpdateMessage(
                    type="update", message=get_room_update_message(action)
                )
            case {"no_target": uid}:
                player_uids = uid
                # We don't tell the player what they tried to do.
                # That way they can't go to an empty room to test no-target skills... Totally a feature.
                update = ActionUpdateMessage(
                    type="update",
                    message="You tried doing something in this room... but there's nothing to hit!",
                )
            case {"no_action": uid}:
                player_uids = uid
                update = ActionUpdateMessage(
                    type="update",
                    message="Time passes by, but you didn't do anything this round!",
                )
            case {"room_of_death": room, "deceased": deceased}:
                player_uids = await get_death_update_uids(room, deceased)
                update = ActionUpdateMessage(
                    type="update", message=f"`{deceased.name}` died!"
                )
            case _:
                # We should probably raise an error here... but it's gonna be fine.
                # Ignoring errors lead to more features ;)
                continue

        match player_uids:
            case int():
                # Send to a single player.
                player_connection = connections.get(player_uids)
                if player_connection is not None:
                    await player_connection.send(update.json())
                # else: player disconnected.
            case set():
                # Broadcast to multiple players.
                player_connections = {
                    connections.get(player_uid)
                    for player_uid in player_uids
                    if connections.get(player_uid) is not None
                }
                websockets.broadcast(player_connections, update.json())


def get_movement_message(move: MovementDict) -> str:
    result = "but there's a wall there!"
    if move["success"]:
        result = "and succeed!"
    elif move["reason"] is not None:
        result = "but you can't move while fighting!"

    return f"You try moving {move['direction']}... {result}"


def get_fleeing_message(fleeing: FleeDict) -> str:
    message = "You tried fleeing but you aren't in combat!"
    if fleeing["fled"]:
        message = "You fled combat!"
    elif fleeing["combat"]:
        message = "You tried fleeing but failed!"

    return message


def get_action_update_message(action: ActionDict) -> str:
    """
    This is the message to be displayed to the player that cast this action.

    A big mess to get a proper message for the action!
    """
    target = game.get_mob(action["target"]) or game.get_player(action["target"])
    target_name = "yourself" if action["target"] == action["caster"] else target.name
    assert target

    tried = "attack" if action["dmg"] > 0 else "heal"
    health_affected = abs(action["dmg"])

    with_ = f"with `{action['name']}`"

    if not action["cast"]:
        message = (
            f"You tried {tried}ing {with_} `{target_name}` but you don't have mana!"
        )
    else:
        if action["hit"]:
            message = f"You {tried}ed `{target_name}` {with_} for {health_affected} hit points!"
        else:
            message = f"You tried {tried}ing `{target_name}` {with_} but missed!"

    return message


def get_room_update_uids(room: BaseRoom, caster_uid: int) -> set:
    """Returns the uids of every player in the room except the caster."""
    players = room.get_players()
    uids = {player.uid for player in players if player.uid != caster_uid}

    return uids


async def get_death_update_uids(room: BaseRoom, deceased: Entity) -> set:
    if isinstance(deceased, Player):
        # We must handle the deceased with a bit more care.
        await handle_dead_player_with_care(deceased.uid)
        # If a player died then tell the entire server!
        return {
            player_uid
            for player_uid in connections.keys()
            if player_uid != deceased.uid
        }
    else:
        # If a mob died, only tell the players in the room.
        return {player.uid for player in room.get_players()}


async def handle_dead_player_with_care(player_uid: int):
    """Properly notifies the client of it's death."""
    tactful_message = DEATH(type="DEATH")
    deceased_connection = connections.get(player_uid)

    if deceased_connection is not None:
        await deceased_connection.send(tactful_message.json())


async def get_win_update_uids(winner_uid: int, win: WIN) -> set[int]:
    winner_connection = connections.get(winner_uid)
    if winner_connection is not None:
        await winner_connection.send(win.json())

    # If a player won then tell the entire server!
    return {player_uid for player_uid in connections.keys() if player_uid != winner_uid}


def get_room_update_message(room_action: RoomActionDict) -> str:
    """This is the message to be displayed to the players in the action that this room happened."""
    action: ActionDict = room_action["action"]

    caster = game.get_player(action["caster"]) or game.get_mob(action["caster"])
    caster_name = caster.name
    target = game.get_mob(action["target"]) or game.get_player(action["target"])
    target_name = "themselves" if action["target"] == action["caster"] else target.name

    did = "attacked" if action["dmg"] > 0 else "healed"
    health_affected = abs(action["dmg"])

    message = f"{caster_name} {did} `{target_name}` for {health_affected} hit points!"

    return message


async def main() -> None:
    await asyncio.gather(websocket_handling(), game_loop())


if __name__ == "__main__":
    game = Game()
    asyncio.run(main())
