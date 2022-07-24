from data.data import raw_map
from entities.mob import Mob
from entities.player import Player
from rooms.basic_room import BaseRoom
from rooms.type_of_rooms import Hall, Wall


class Game:
    players: list[Player]
    mobs: list[Mob]
    rooms: list[BaseRoom]

    def __init__(self):
        self.players = []
        self.mobs = []
        self.rooms = []

    def get_map(self, player_x, player_y) -> str:
        largest_x = 0
        largest_y = 0
        ret = ""
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
                for room in g.rooms:
                    if room.get_map_location() == (player_x, player_y):
                        ret += "@"
                    if room.get_map_location() == (x, y):
                        ret += room.get_display()["display_char"]
            ret += "\n"
        return ret

    def add_player(self, player: Player, target_x, target_y) -> bool:
        for room in self.rooms:
            if room.can_entity_step:
                if room.get_map_location() == (target_x, target_y):
                    room.add_player(player)
                    return True
        else:
            return False

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
