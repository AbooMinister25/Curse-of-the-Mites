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
    players: list[Player]
    mobs: list[Mob]
    rooms: list[BaseRoom]
    combats: list[Combat]

    def __init__(self):
        self.players = []
        self.mobs = []
        self.rooms = []
        self.combats = []
        self.build_map()

    def get_room_at(self, x, y) -> BaseRoom | None:
        temp = None
        for room in self.rooms:
            if room.get_map_location() == (x, y):
                temp = room
                break
        return temp

    def get_room(self, _uid: int) -> BaseRoom | None:
        temp = None
        for room in self.rooms:
            if room.uid == _uid:
                return room
        return temp

    def get_player(self, _uid: int) -> Player | None:
        temp = None
        for player in self.players:
            if player.uid == _uid:
                return player
        return temp

    def get_mob(self, _uid: int) -> Mob | None:
        temp = None
        for mob in self.mobs:
            if mob.uid == _uid:
                return mob
        return temp

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
            self.rooms.append(temp)

        for y in range(largest_y + 1):
            for x in range(largest_x + 1):
                current_room = None
                for room in self.rooms:
                    if room.get_map_location() == (x, y):
                        current_room = room
                        break
                if current_room is not None:
                    directions = {
                        "north": None,
                        "east": None,
                        "south": None,
                        "west": None,
                    }

                    for room in self.rooms:
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

    def add_player(self, player: Player, target_x, target_y) -> bool:
        for room in self.rooms:
            if room.can_entity_step:
                if room.get_map_location() == (target_x, target_y):
                    room.add_player(player)
                    return True
        else:
            return False

    def move_player(self, _player: Player | int, direction: str) -> bool:
        assert direction in ("north", "east", "west", "south")
        player_moved = False
        if isinstance(_player, int):
            for player in self.players:
                if player.uid == _player:
                    _player = player
                    break

        if isinstance(_player, Player):
            # print("HERE")
            for room in self.rooms:
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

    def add_mob(self, mob: Mob, target_x, target_y) -> bool:
        for room in self.rooms:
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


if __name__ == "__main__":
    # required
    g = Game()

    # adding a player to a specific room
    A = Player("xyf", ["bite", "spit"])
    temp = g.get_room_at(1, 1)
    temp.add_player(A)

    # adding a mob
    a = Mob("anta", ["bite"])
    temp = g.get_room_at(1, 1)
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
