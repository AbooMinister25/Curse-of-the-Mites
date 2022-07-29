import time

from game_components.game_objects import (
    BaseRoom,
    Combat,
    Hall,
    Mob,
    Player,
    Wall,
    raw_map,
)


class Game:
    players: dict[int, Player]
    mobs: dict[int, Mob]
    rooms: dict[int, BaseRoom]
    combats: list[Combat]
    start_time: int

    def __init__(self):
        self.players = {}
        self.mobs = {}
        self.rooms = {}
        self.combats = []
        self.build_map()
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

    def build_map(self) -> None:
        largest_x = 0
        largest_y = 0
        for room_data in raw_map:
            temp = None
            if room_data["type"] == "hall":
                temp = Hall(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "wall":
                temp = Wall(_display_x=room_data["x"], _display_y=room_data["y"])
            if room_data["x"] > largest_x:
                largest_x = room_data["x"]
            if room_data["y"] > largest_y:
                largest_y = room_data["y"]
            assert temp, "unknown room type"
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
        for room in self.rooms.values():
            if room.can_entity_step:
                if room.get_map_location() == (target_x, target_y):
                    room.add_player(player)
                    return True
        else:
            return False

    def move_player(self, _player: Player | int, direction: str) -> bool:
        if direction not in ("north", "east", "west", "south"):
            return False
        player_moved = False
        if isinstance(_player, int):
            if self.players[_player]:
                _player = self.players[_player]

        if isinstance(_player, Player):
            # print("HERE")
            for room in self.rooms.values():
                if _player in room.get_players():
                    # print(_player)
                    # print(room.get_players())
                    to_go = room.get_links()[direction]
                    # print("ROOM TO GO TO")
                    # print(to_go)
                    # print("=======")
                    if to_go is not None:
                        if to_go.can_entity_step:
                            room.remove_player(_player)
                            to_go.add_player(_player)
                            player_moved = True
                    break
        return player_moved

    def add_mob(self, mob: Mob, target_x: int, target_y: int) -> bool:
        for room in self.rooms.values():
            if room.can_entity_step:
                if room.get_map_location() == (target_x, target_y):
                    room.add_mob(mob)
                    return True
        else:
            return False

    def update(self):
        # REDUCE COMBATS
        reduce_combats_done = False
        while not reduce_combats_done:
            for i, _e in enumerate(self.combats):
                hit = False
                for j, _f in enumerate(self.combats):
                    if i != j:
                        result = _e.combine(_f)
                        if result is not None:
                            self.combats.remove(result)
                            break
                if hit:
                    break
            else:
                reduce_combats_done = True

        for room in self.rooms.values():
            for player in room.get_players():
                actions = player.update()
                assert actions is not None, "returned `None` for actions"
                # this wont work at all.
                set([action for action in actions])


if __name__ == "__main__":
    # required
    g = Game()

    # adding a player to a specific room
    A = Player("xyf", ["bite", "spit"])
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

    # Test Combats
    #
    # c = Mob("antc", ["bite"])
    # g.add_mob(c, 1, 1)
    # # adding a player to a map location
    # B = Player("aboo", ["stomp", "spit"])
    # g.add_player(B, 1, 1)
    # d = Mob("antd",['eat_berry','bite','stomp'])
    # g.add_mob(d,1,1)
    # C = Player("baut",['eat_berry','bite','spit'])
    # combata = Combat([A, a], temp)
    # combatb = Combat([B, b, c], temp)
    # combatc = Combat([d, C], temp)
    # g.combats.append(combata)
    # g.combats.append(combatb)
    # g.combats.append(combatc)
    # for i,combat in enumerate(g.combats):
    #     print(i,combat)
    # combatb.add_to_combat(A)
    # combata.add_to_combat(d)
    # g.update()
    # for i,combat in enumerate(g.combats):
    #     print(i,combat)
