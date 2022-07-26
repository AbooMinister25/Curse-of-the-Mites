from game_objects import BaseRoom, Hall, Mob, Player, Wall, raw_map


class Game:
    players: list[Player]
    mobs: list[Mob]
    rooms: list[BaseRoom]

    def __init__(self):
        self.players = []
        self.mobs = []
        self.rooms = []

    def get_room_at(self, x, y) -> BaseRoom | None:
        temp = None
        for room in self.rooms:
            if room.get_map_location() == (x, y):
                temp = room
                break
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
            g.rooms.append(temp)

        for y in range(largest_y + 1):
            for x in range(largest_x + 1):
                current_room = None
                for room in g.rooms:
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

                    for room in g.rooms:
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


if __name__ == "__main__":
    g = Game()
    g.build_map()
    p = Player("xyf", ["bite", "spit"])
    start_room = g.get_room_at(1, 1)
    start_room.add_player(p)

    d = Player("aboo", ["stomp", "spit"])
    g.add_player(d, 2, 1)

    a = Mob("anta", ["bite"])
    next_room = g.get_room_at(2, 1)
    next_room.add_mob(a)
    a = Mob("antb", ["bite"])
    next_room.add_mob(a)
    print("START")
    print(start_room)
    print(next_room)
    print("MOVE")
    g.move_player(p, "east")
    print(start_room)
    print(next_room)
