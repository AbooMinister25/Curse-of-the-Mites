import random
import time
from asyncio import Queue

from common.schemas import WIN, LevelUpNotification, RoomChangeUpdate

if __name__ == "__main__":
    from game_objects import (
        ActionDict,
        BaseRoom,
        DeathDict,
        FleeDict,
        LeftLower,
        LeftTop,
        Mob,
        MovementDict,
        Player,
        RightLower,
        RightTop,
        RoomActionDict,
        RoughSide,
        SpidersDen,
        TopOfLeaf,
        Wall,
        raw_map,
    )
else:
    from game_components.game_objects import (
        ActionDict,
        BaseRoom,
        DeathDict,
        FleeDict,
        LeftLower,
        LeftTop,
        Mob,
        MovementDict,
        Player,
        RightLower,
        RightTop,
        RoomActionDict,
        RoughSide,
        SpidersDen,
        TopOfLeaf,
        Wall,
        raw_map,
    )

ROOMS_MAP = {
    "rs": RoughSide,
    "wall": Wall,
    "ll": LeftLower,
    "rl": RightLower,
    "rt": RightTop,
    "lt": LeftTop,
    "sd": SpidersDen,
    "tol": TopOfLeaf,
}


class InvalidRoomError(Exception):
    pass


OUT_QUEUE = (
    ActionDict
    | DeathDict
    | MovementDict
    | RoomActionDict
    | FleeDict
    | RoomChangeUpdate
    | LevelUpNotification
    | WIN
    | int
)


class Game:
    players: dict[int, Player]
    mobs: dict[int, Mob]
    rooms: dict[int, BaseRoom]
    start_time: int

    def __init__(self):
        self.out_queue: Queue[OUT_QUEUE] = Queue()
        self.players = {}
        self.mobs = {}
        self.rooms = {}
        self.build_map()
        self.spawn_mobs()
        self.start_time = round(time.time() * 1000)

    def get_room_at(self, x: int, y: int) -> BaseRoom | None:
        temp = None
        for room in self.rooms.values():
            if room.get_map_location() == (x, y):
                temp = room
                break
        return temp

    def get_room(self, _uid: int) -> BaseRoom | None:
        return self.rooms.get(_uid)

    def get_player(self, _uid: int) -> Player | None:
        return self.players.get(_uid)

    def get_mob(self, _uid: int) -> Mob | None:
        return self.mobs.get(_uid)

    def spawn_mobs(self) -> None:

        for room in self.rooms.values():
            if room.get_map_location() == (15, 24):
                # this is spawn location for player. Dont add a mob here
                continue
            if room.get_map_location() == (15, 23):
                # this is one north of spawn. This lets a player see a mob right away
                # but its WEAK. This lets a player learn the game in a safe environment
                # this acts as a tutorial without being EA handhold-y
                m = Mob("Mite", ["annoy"], self)
                self.add_mob(m, room.display_x, room.display_y)
                continue
            if isinstance(room, Wall):
                continue
            if isinstance(room, SpidersDen):
                # Sting will be difficult, the also dont have annoy, so they are going to hit hard
                m = Mob("Spider", ["sting", "eat_berry", "nibble"], self)
                self.add_mob(m, room.display_x, room.display_y)
                continue
            chance_to_spawn = random.randint(0, 100)

            # if there are too many mobs, make this magic number lower
            if chance_to_spawn < 25:
                m = Mob("Mite", ["nibble", "eat_berry", "stomp", "annoy"], self)
                self.add_mob(m, room.display_x, room.display_y)

    def build_map(self) -> None:
        largest_x = 0
        largest_y = 0
        for room_data in raw_map:
            try:
                temp = ROOMS_MAP[room_data["type"]](
                    _display_x=room_data["x"], _display_y=room_data["y"]
                )
            except KeyError:
                raise InvalidRoomError(f"Unknown room type {room_data['type']}")

            if room_data["x"] > largest_x:
                largest_x = room_data["x"]
            if room_data["y"] > largest_y:
                largest_y = room_data["y"]

            self.rooms[temp.uid] = temp

        for y in range(largest_y + 1):
            for x in range(largest_x + 1):
                current_room = None
                for room in self.rooms.values():
                    if room.get_map_location() == (x, y):
                        current_room = room
                        break
                if current_room is not None:
                    directions: dict[str, None | BaseRoom] = {
                        "north": None,
                        "east": None,
                        "south": None,
                        "west": None,
                    }

                    for room in self.rooms.values():
                        if room.get_map_location() == (
                            current_room.display_x,
                            current_room.display_y - 1,
                        ):
                            directions["north"] = room
                            continue
                        if room.get_map_location() == (
                            current_room.display_x,
                            current_room.display_y + 1,
                        ):
                            directions["south"] = room
                            continue
                        if room.get_map_location() == (
                            current_room.display_x - 1,
                            current_room.display_y,
                        ):
                            directions["west"] = room
                            continue
                        if room.get_map_location() == (
                            current_room.display_x + 1,
                            current_room.display_y,
                        ):
                            directions["east"] = room
                            continue
                    current_room.set_links(directions)

    def add_player(self, player: Player, target_x: int, target_y: int) -> bool:
        room = self.get_room_at(target_x, target_y)
        assert room

        if not room.can_entity_step:
            return False

        if player.uid not in self.players:
            self.players[player.uid] = player

        room.add_player(player)
        return True

    def move_player(self, player: Player, direction: str) -> bool:
        if direction not in ("north", "east", "west", "south"):
            return False

        player_moved = False

        from_room = player.in_room
        to_go = from_room.get_links()[direction]

        if to_go is not None and to_go.can_entity_step:
            from_room.remove_player(player)
            to_go.add_player(player)
            player_moved = True

        return player_moved

    def add_mob(self, mob: Mob, target_x: int, target_y: int) -> bool:
        room = self.get_room_at(target_x, target_y)
        assert room
        assert room.can_entity_step

        self.mobs[mob.uid] = mob
        room.add_mob(mob)
        return True

    async def update(self):
        """One tick of the game!"""
        # Update mobs.
        for mob_uid in self.mobs:
            self.mobs[mob_uid].update()

        # Update players.
        for player_uid in self.players:
            player = self.players[player_uid]
            action_performed = player.update()

            if player.won:
                win = {
                    "type": WIN(type="WIN"),
                    "uid": player_uid,
                }
                await self.out_queue.put(win)
            elif player.level_past_tick < player.level:
                level_up = {
                    "type": LevelUpNotification(
                        type="level_up",
                        times_leveled=(player.level - player.level_past_tick),
                        current_level=player.level,
                    ),
                    "uid": player_uid,
                }
                await self.out_queue.put(level_up)
            player.level_past_tick = player.level

            match action_performed:
                case list():
                    if len(action_performed) == 0:
                        await self.out_queue.put({"no_target": player_uid})
                    for action in action_performed:
                        await self.out_queue.put(action)
                case dict():
                    await self.out_queue.put(action_performed)
                case _:
                    await self.out_queue.put({"no_action": action_performed})

        # Handle events in rooms.
        for room_uid in self.rooms:
            for event in self.rooms[room_uid].events:
                await self.out_queue.put(event)
            self.rooms[
                room_uid
            ].events = (
                []
            )  # If an event was missed for whatever reason... to bad... it's a feature!

    def clean_the_dead(self) -> list[int]:
        ## First the mobs.
        mobs_to_pop = []
        for mob_uid in self.mobs:
            mob = self.mobs[mob_uid]

            if not mob.alive:
                room = mob.in_room

                if mob_uid in room.mob_combatants:
                    room.mob_combatants.remove(mob_uid)

                room.remove_mob(mob)
                mobs_to_pop.append(mob_uid)

        for mob_uid in mobs_to_pop:
            self.mobs.pop(mob_uid)

        ## Then the players.
        players_to_pop = []
        for player_uid in self.players:
            player = self.players[player_uid]

            if not player.alive:
                room = player.in_room

                if player_uid in room.player_combatants:
                    room.player_combatants.remove(player_uid)

                room.remove_player(player)
                players_to_pop.append(player_uid)

        for player_uid in players_to_pop:
            self.players.pop(player_uid)

        return players_to_pop  # Their connections will need to be deleted.


if __name__ == "__main__":
    # required
    g = Game()

    # adding a player to a specific room
    A = Player("xyf", ["bite", "spit"], g)
    temp = g.get_room_at(1, 1)
    assert temp, "no room at (1, 1)"
    temp.add_player(A)

    # adding a mob
    a = Mob("anta", ["bite"])
    temp = g.get_room_at(1, 1)
    assert temp, "no room at (1, 1)"
    temp.add_mob(a)

    # adding a mob to a map location
    b = Mob("antb", ["bite"])
    g.add_mob(b, 1, 1)

    """
    # testing entity combat
    print(temp)
    result = A.commit_action("bite", a)
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")

    print(temp)
    result = A.commit_action("spit")
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")
    print(temp)
    """
    """
    # testing player updating.
    A.add_command_to_queue("bite", a)
    result = A.update()
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")
    print(temp)
    A.add_command_to_queue("spit")
    result = A.update()
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")
    print(temp)
    """

    # Test movements.
    print("~~~~~~~~~~~")
    A5 = Player("A5Rocks", ["bite", "spit"], g)
    g.add_player(A5, 1, 1)
    print(g.get_room_at(1, 1).get_players())
    A5.add_command_to_queue("east", None)
    g.update()
    print(A5.command_queue)
    print(g.get_room_at(1, 1).get_players())
