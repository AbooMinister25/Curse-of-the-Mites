from server.game_components.data.data import raw_map
from server.game_components.rooms.type_of_rooms import Hall, Wall


class Game:
    players: list
    mobs: list
    rooms: list

    def __init__(self):
        self.players = []
        self.mobs = []
        self.rooms = []


if __name__ == "__main__":
    g = Game()
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
    # print(largest_x,largest_y)
    for y in range(largest_y + 1):
        for x in range(largest_x + 1):
            # print((x,y),end = " ")
            for room in g.rooms:
                if room.get_map_location() == (x, y):
                    print(room.get_display()["display_char"], end="")
        print()
