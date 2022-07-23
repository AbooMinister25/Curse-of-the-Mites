import hashlib
from abc import ABC  # abstract classes

from server.game_components.entitiies.mob import Mob
from server.game_components.entitiies.player import Player


class BaseRoom(ABC):
    __title = None
    __description = None
    __linked_rooms = None
    __mobs = None
    __players = None
    __display_char = None
    __color = None
    uid = None
    number = 0
    __display_x = None
    __display_y = None
    can_entity_step = None

    def __init__(
        self,
        _title: str,
        _display_char: str,
        _color: tuple[int, int, int],
        _description: str,
        _linked_rooms: dict,
        _display_x: int,
        _display_y: int,
    ):
        """
        Base Room

        :param _title: Title of room.
        :param _display_char: display character of room.
        :param _color: color of tile (0-255,0-255,0-255) rgb.
        :param _description: description for room.
        :param _linked_rooms: dict of linked rooms, req keys are north, east, south and west.
        None if the rooms are not set.
        """
        data = (
            f"{_title}{_description}{_linked_rooms['north']}{_linked_rooms['east']}"
            f"{_linked_rooms['south']}{_linked_rooms['west']}"
        )
        m = hashlib.sha256()
        m.update(data.encode())
        self.uid = int(m.hexdigest(), 16)
        self.__title = _title
        self.__color = _color
        self.__linked_rooms = _linked_rooms
        self.__display_char = _display_char
        self.__mobs = []
        self.__players = []
        self.__display_x = _display_x
        self.__display_y = _display_y

        BaseRoom.number += 1

    def get_display(self) -> dict:
        """:return: dictionary of `color` and `display_char` for building map"""
        return {"color": self.__color, "display_char": self.__display_char}

    def show_mobs(self) -> str:
        """:return: get string of mobs in room"""
        ret = ""
        for mob in self.__mobs:
            ret += f"{str(mob)}\n"
        return ret

    def show_players(self) -> str:
        """:return: get string of players in room"""
        ret = ""
        for player in self.__players:
            ret += f"{str(player)}\n"
        return ret

    def add_player(self, _player: Player):
        """
        Add player to room

        :param _player: player object to add
        :return:
        """
        self.__players.append(_player)

    def add_mob(self, _mob: Mob):
        """
        Add mob to room

        :param _mob: mob object to add
        :return:
        """
        self.__mobs.append(_mob)

    def get_map_location(self):
        return self.__display_x, self.__display_y
