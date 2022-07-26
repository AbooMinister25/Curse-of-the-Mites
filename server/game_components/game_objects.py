from __future__ import annotations

import hashlib
import random
import time
from abc import ABC  # abstract classes

raw_map = [
    {"x": 0, "y": 0, "type": "wall"},
    {"x": 1, "y": 0, "type": "wall"},
    {"x": 2, "y": 0, "type": "wall"},
    {"x": 3, "y": 0, "type": "wall"},
    {"x": 0, "y": 1, "type": "wall"},
    {"x": 1, "y": 1, "type": "hall"},
    {"x": 2, "y": 1, "type": "hall"},
    {"x": 3, "y": 1, "type": "wall"},
    {"x": 0, "y": 2, "type": "wall"},
    {"x": 1, "y": 2, "type": "wall"},
    {"x": 2, "y": 2, "type": "wall"},
    {"x": 3, "y": 2, "type": "wall"},
]

mobs = []


class Entity(ABC):
    health: int
    max_health: int
    mana: int
    max_mana: int
    alive: bool
    uid: int
    in_combat: bool
    name: str
    allowed_actions: dict[str, Action]

    def __init__(self, _name, _allowed_actions: list[str], _health=100, _mana=100):
        self.health = _health
        self.max_health = _health
        self.mana = _mana
        self.max_mana = _mana
        self.alive = True

        self.in_combat = False
        self.name = _name
        temp = {}
        for _action in _allowed_actions:
            temp[_action] = all_actions[_action]

        self.allowed_actions = temp

        now = time.time_ns()
        m = hashlib.sha256()
        data = f"{self.name},{str(now)},{str(_allowed_actions)}"
        m.update(data.encode())
        self.uid = int(m.hexdigest(), 16)

    def commit_action(self, _action: str, target: Entity | list[Entity]):
        return self.allowed_actions[_action].action(self, target)

    def move(self, _direction: str, _map: list[BaseRoom]):
        pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        status = f"({self.health}/{self.max_health},{self.mana}/{self.max_mana})"
        moves = f"{[str(e) for e in self.allowed_actions.keys()]}"
        return f"{str(self.uid)[0:4]} {status} {self.__class__.__name__} {self.name} {moves}"


class Mob(Entity):
    def __init__(self, _name, _allowed_actions: list[str]):
        super().__init__(_name, _allowed_actions)


class Player(Entity):
    experience: int
    level: int

    def __init__(self, _name, _allowed_actions: list[str]):
        super().__init__(_name, _allowed_actions)


class Action(ABC):
    __cost: int
    __min_damage: int
    __max_damage: int
    __hit_percentage: int
    name: str

    def __init__(
        self,
        _name: str,
        _cost: int,
        _min_damage: int,
        _max_damage: int,
        _hit_percentage: int,
    ):
        """
        Make an action

        :param _name: name of action
        :param _cost: cost in mana
        :param _min_damage: minimal damage
        :param _max_damage: maximum damage
        :param _hit_percentage: how often should it hit
        """
        if _hit_percentage > 100 or _hit_percentage < 0:
            raise ValueError("hit % must be valid % (0-100) inclusive")
        if _min_damage > _max_damage:
            temp = _max_damage
            _max_damage = _min_damage
            _min_damage = temp

        self.__min_damage = _min_damage
        self.__max_damage = _max_damage
        self.__cost = _cost
        self.__hit_percentage = _hit_percentage
        self.name = _name

    def action(self, caster: Entity, target: list[Entity] | Entity) -> list[dict]:
        """
        Perform an action

        This is the combat of the game. It can handle single and multiple targets.
        correct usage of number of targets is NOT taken into account.
        This "deals damage" to the target if it hits and already takes into account cost
        for each element in the list:
            hit - did the action hit the target
            cast - was the spell cast or not
            dmg - how much dmg would have occurred or did occur.
            caster - the caster uid
            target - the target uid
        FOR EXAMPLE:
            hit - false
            dmg - 1000
            cast - true
            caster - the caster uid
            target - the target uid
            the spell did cast but did not hit, it WOULD HAVE done 1000 dmg BUT DIDN'T

        :param caster: the caster
        :param target: the target(s)
        :return: its a list of what happened. Single target attacks still return a list of dicts
        """
        hit = False
        cast = False
        if caster.mana >= self.__cost:
            caster.mana -= self.__cost
            cast = True

        if isinstance(target, Entity):
            dmg = random.randint(self.__min_damage, self.__max_damage)
            if cast:
                hit_check = random.randint(0, 100)
                if hit_check <= self.__hit_percentage:
                    hit = True
                if hit:
                    target.health -= dmg

                return [
                    {
                        "caster": caster.uid,
                        "target": target.uid,
                        "hit": hit,
                        "dmg": dmg,
                        "cast": cast,
                    }
                ]
            else:
                return [
                    {
                        "caster": caster.uid,
                        "target": target.uid,
                        "hit": hit,
                        "dmg": dmg,
                        "cast": cast,
                    }
                ]
        elif isinstance(target, list):
            action_list = []
            for entity in target:
                dmg = random.randint(self.__min_damage, self.__max_damage)
                if cast:
                    hit_check = random.randint(0, 100)
                    if hit_check <= self.__hit_percentage:
                        hit = True
                    if hit:
                        entity.health -= dmg
                    action_list.append(
                        {
                            "caster": caster.uid,
                            "target": entity.uid,
                            "hit": hit,
                            "dmg": dmg,
                            "cast": cast,
                        }
                    )
                else:
                    action_list.append(
                        {
                            "caster": caster.uid,
                            "target": entity.uid,
                            "hit": hit,
                            "dmg": dmg,
                            "cast": cast,
                        }
                    )
            return action_list


all_actions = {
    "bite": Action("bite", 0, 5, 5, 100),
    "stomp": Action("stomp", 10, 5, 15, 70),
    "spit": Action("spit", 25, 15, 50, 30),
    "eat_berry": Action("eat", 5, -5, -10, 100),
}


class BaseRoom(ABC):
    __title: str
    __description: str
    __linked_rooms: dict[str, BaseRoom | None]
    __mobs: list[Mob]
    __players: list[Player]
    __display_char: str
    __color: tuple[int, int, int]
    uid: int
    number = 0
    display_x: int
    display_y: int
    can_entity_step: bool

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
        self.display_x = _display_x
        self.display_y = _display_y

        BaseRoom.number += 1

    def get_display(self) -> dict:
        """:return: dictionary of `color` and `display_char` for building map"""
        return {"color": self.__color, "display_char": self.__display_char}

    def set_links(self, links: dict):
        self.__linked_rooms = links

    def get_links(self) -> dict[str, BaseRoom]:
        return self.__linked_rooms

    def show_mobs(self) -> str:
        """:return: get string of mobs in room"""
        ret = ""
        for mob in self.__mobs:
            ret += f"{str(mob)}\n"
        return ret

    def set_room(self, direction, room_to_add: BaseRoom):
        self.__linked_rooms[direction] = room_to_add

    def show_players(self) -> str:
        """:return: get string of players in room"""
        ret = ""
        for player in self.__players:
            ret += f"{str(player)}\n"
        return ret

    def get_players(self) -> list[Player]:
        return self.__players

    def add_player(self, _player: Player):
        """
        Add player to room

        :param _player: player object to add
        :return:
        """
        self.__players.append(_player)

    def remove_player(self, _player: Player):
        self.__players.remove(_player)

    def add_mob(self, _mob: Mob):
        """
        Add mob to room

        :param _mob: mob object to add
        :return:
        """
        self.__mobs.append(_mob)

    def get_map_location(self):
        return self.display_x, self.display_y

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = f"({self.display_x},{self.display_y}) {self.__class__.__name__}\n"
        ret += "Players\n"
        for i, player in enumerate(self.__players):
            ret += f"\t{i} {player}\n"
        ret += "Mobs\n"
        for i, mob in enumerate(self.__mobs):
            ret += f"\t{i} {mob}\n"
        ret += "Links\n"
        for k, v in self.__linked_rooms.items():
            if v is not None:
                ret += f"\t{k}\t({v.display_x},{v.display_y}) {v.__class__.__name__}\n"
        return ret


class Wall(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "It's a wall",
        _display_char: str = "#",
        _color: tuple[int, int, int] = (0, 0, 0),
        _description: str = "How are you reading this",
        _linked_rooms: dict = None,
    ):
        if _linked_rooms is None:
            _linked_rooms = {"north": None, "east": None, "south": None, "west": None}
        super().__init__(
            _title=_title,
            _display_char=_display_char,
            _color=_color,
            _description=_description,
            _linked_rooms=_linked_rooms,
            _display_x=_display_x,
            _display_y=_display_y,
        )
        self.can_entity_step = False


class Hall(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "The hallway",
        _display_char: str = " ",
        _color: tuple[int, int, int] = (0, 0, 0),
        _description: str = "It's a hallway",
        _linked_rooms: dict = None,
    ):
        if _linked_rooms is None:
            _linked_rooms = {"north": None, "east": None, "south": None, "west": None}
        super().__init__(
            _title=_title,
            _display_char=_display_char,
            _color=_color,
            _description=_description,
            _linked_rooms=_linked_rooms,
            _display_x=_display_x,
            _display_y=_display_y,
        )
        self.can_entity_step = True
