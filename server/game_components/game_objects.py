from __future__ import annotations

import hashlib
import random
import time
import typing
from abc import ABC, abstractmethod  # abstract classes

if typing.TYPE_CHECKING:
    from game import Game

raw_map: list[Tile] = [
    {"y": 1, "x": 14, "type": "wall"},
    {"y": 1, "x": 15, "type": "wall"},
    {"y": 1, "x": 16, "type": "wall"},
    {"y": 2, "x": 14, "type": "wall"},
    {"y": 2, "x": 15, "type": "sd"},
    {"y": 2, "x": 16, "type": "wall"},
    {"y": 3, "x": 14, "type": "wall"},
    {"y": 3, "x": 15, "type": "tol"},
    {"y": 3, "x": 16, "type": "wall"},
    {"y": 3, "x": 17, "type": "wall"},
    {"y": 4, "x": 14, "type": "wall"},
    {"y": 4, "x": 15, "type": "tol"},
    {"y": 4, "x": 16, "type": "rs"},
    {"y": 4, "x": 17, "type": "wall"},
    {"y": 5, "x": 14, "type": "wall"},
    {"y": 5, "x": 15, "type": "tol"},
    {"y": 5, "x": 16, "type": "rs"},
    {"y": 5, "x": 17, "type": "wall"},
    {"y": 6, "x": 14, "type": "wall"},
    {"y": 6, "x": 15, "type": "tol"},
    {"y": 6, "x": 16, "type": "rs"},
    {"y": 6, "x": 17, "type": "wall"},
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
    in_room: BaseRoom | None

    def __init__(
        self,
        _name: str,
        _allowed_actions: list[str],
        _health: int = 100,
        _mana: int = 100,
    ):
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
        self.in_room = None
        self.allowed_actions = temp

        now = time.time_ns()
        m = hashlib.sha256()
        data = f"{self.name},{str(now)},{str(_allowed_actions)}"
        m.update(data.encode())
        self.uid = int(m.hexdigest(), 16)

    def commit_action(self, _action: str, target: Entity | None = None):
        return self.allowed_actions[_action].action(self, target)

    def __repr__(self):
        return str(self)

    def __str__(self):
        status = f"({self.health}/{self.max_health},{self.mana}/{self.max_mana})"
        moves = f"{[str(e) for e in self.allowed_actions.keys()]}"
        return f"{str(self.uid)[0:4]} {status} {self.__class__.__name__} {self.name} {moves}"

    @abstractmethod
    def update(self):
        if self.mana > self.max_mana:
            self.mana = self.max_mana
        if self.health > self.max_health:
            self.health = self.max_health
        pass


class Mob(Entity):
    def update(self):
        self.mana += 7
        self.health += random.randint(1, 3)
        super().update()
        pass

    def __init__(self, _name: str, _allowed_actions: list[str]):
        super().__init__(_name, _allowed_actions)


class AddCommandResult(typing.NamedTuple):
    success: bool
    message: str


class Player(Entity):
    level: int
    command_queue: list[dict[str, Entity | None]]

    def __init__(self, _name: str, _allowed_actions: list[str], game: Game):
        super().__init__(_name, _allowed_actions)
        self.level = 0
        self.command_queue = []
        self.game = game

    def update(self) -> list[ActionDict] | MovementDict | None:
        """Updates the player for one tick.

        Executes the next action in the players queue.
        Returns a list of ActionDicts if the player did something and None if they didn't
        """
        self.mana += 10
        self.health += random.randint(1, 5)

        result = None

        if len(self.command_queue) > 0:
            next_command = self.command_queue.pop()
            result = self._do(next_command)

        super().update()

        return result

    def _do(self, command: CommandDict) -> list[ActionDict] | MovementDict | None:
        movement_commands = ["north", "east", "south", "west"]

        result = None
        # TODO: Tell the player "HEY, YOU DID THIS THING"
        if command["command"] in movement_commands:
            valid_move = self.game.move_player(self, command["command"])
            result = {
                "player": self.uid,
                "direction": command["command"],
                "success": valid_move,
            }
        elif command["command"] == "flee":
            pass  # TODO: IMPLEMENT FLEEING.
        else:
            result = self.commit_action(command["command"], command["target"])

        return result

    def send_events_to_player(self):
        for event in self.events:
            # TODO: SEND EVENTS TO THE PLAYER
            pass

    def add_command_to_queue(
        self, _command: str, _target: Entity | None = None
    ) -> AddCommandResult:
        """
        Adds a command to the player queue if it's valid.

        :param _command: flee, north, east, south, west, one of the skills, clear, nvm
        :param _target: Entity to be targeted or None.
        :return:
        """
        validity = self._check_command_validity(_command, _target)

        if validity.success:
            event = {"command": _command, "target": _target}
            self.command_queue.insert(0, event)

        return validity

    def _check_command_validity(
        self, _command: str, _target: Entity | None = None
    ) -> AddCommandResult:
        """
        Checks that a command is valid.

        :param _command: flee, north, east, south, west, one of the skills, clear, nvm
        :param _target: Entity to be targeted or None.
        :return:
        """
        directions = ["north", "east", "south", "west"]

        if _command == "flee":
            # you tried to flee but you aren't in combat. idiot.
            if not self.in_combat:
                return AddCommandResult(
                    False, "Silly, don't try to flee if you aren't in combat!"
                )
            else:
                return AddCommandResult(True, "Added fleeing to your queue!")
        if _command in directions:
            # you tried to move but you are in combat. STOP.
            if self.in_combat:
                return AddCommandResult(
                    False, "Don't just move like that when you're fighting!"
                )
            else:
                return AddCommandResult(True, f"Moving {_command} added to your queue.")
        if _command in self.allowed_actions:
            # make sure actions that need a target get a target
            if self.allowed_actions[_command].requires_target and _target is None:
                return AddCommandResult(False, f"{_command} requires a target!")
            elif (
                not self.allowed_actions[_command].requires_target
            ) and _target is not None:
                return AddCommandResult(False, f"{_command} doesn't require a target!")
        match _command:
            case "clear":
                self.command_queue = []
                return AddCommandResult(True, "Your queue was erased!")
            case "nvm":
                self.command_queue = self.command_queue[:-1]
                return AddCommandResult(True, "Last command of the queue erased!")
            case _ if _command in self.allowed_actions:
                return AddCommandResult(True, f"{_command} added to your queue.")
            case _:
                return AddCommandResult(False, f"You can't do {_command}!")


class TargetsError(Exception):
    """Exception raised when you try to perform an action with an incorrect number of targets."""

    def __init__(self, action_name: str, needs_target: bool) -> None:
        s = "requires" if needs_target else "doesn't require"
        self.message = f"{action_name} {s} a target"

    def __str__(self) -> str:
        return self.message


class Action(ABC):
    __cost: int
    __min_damage: int
    __max_damage: int
    __hit_percentage: int
    name: str
    area_of_effect: bool
    requires_target: bool

    def __init__(
        self,
        _name: str,
        _cost: int,
        _min_damage: int,
        _max_damage: int,
        _hit_percentage: int,
        _area_of_effect: bool,
        _requires_target: bool,
        _causes_combat: bool,
    ):
        """
        Make an action

        :param _causes_combat: does this effect cause combat
        :param _name: name of action
        :param _cost: cost in mana
        :param _min_damage: minimal damage
        :param _max_damage: maximum damage
        :param _hit_percentage: how often should it hit
        :param _area_of_effect: hits every entity in the room.
        :param _requires_target: indicates if it needs to have a target
        """
        if _hit_percentage > 100 or _hit_percentage < 0:
            raise ValueError("hit % must be valid % (0-100) inclusive")
        if _min_damage > _max_damage:
            temp = _max_damage
            _max_damage = _min_damage
            _min_damage = temp
        self.area_of_effect = _area_of_effect
        self.requires_target = _requires_target
        self.__min_damage = _min_damage
        self.__max_damage = _max_damage
        self.__cost = _cost
        self.__hit_percentage = _hit_percentage
        self.name = _name

    def action(self, _caster: Entity, _target: Entity | None) -> list[ActionDict]:
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

        :param _caster: the caster
        :param _target: the target(s)
        :return: its a list of what happened. Single target attacks still return a list of dicts
        """
        action_list: list[ActionDict] = []

        cast = _caster.mana >= self.__cost
        if cast:
            _caster.mana -= self.__cost

        if _target is None:
            if self.requires_target:
                raise TargetsError(self.name, self.requires_target)
            action_list = self._no_target_action(cast, _caster)
        else:
            if not self.requires_target:
                raise TargetsError(self.name, self.requires_target)
            action_list.append(self._action_with_target(cast, _caster, _target))

        return action_list

    def _no_target_action(self, cast: bool, caster: Entity) -> list[ActionDict]:
        """Returns the results for either an AOE action or a self targeted action."""
        action_list: list[ActionDict] = []
        if self.area_of_effect:
            assert caster.in_room
            # Add all entities in the room to the targets.
            targets: list[Entity] = []
            for mob in caster.in_room.get_mobs():
                targets.append(mob)
            for player in caster.in_room.get_players():
                # Don't add the casting player to the targets!
                if player.uid != caster.uid:
                    targets.append(player)

            for entity in targets:
                result = self._action_with_target(cast, caster, entity)
                action_list.append(result)
        else:
            # Self targeted action.
            target = caster
            action_list.append(self._action_with_target(cast, caster, target))

        return action_list

    def _action_with_target(
        self, cast: bool, caster: Entity, target: Entity
    ) -> ActionDict:
        dmg = random.randint(self.__min_damage, self.__max_damage)
        hit_check = random.randint(0, 100)
        hit = hit_check <= self.__hit_percentage

        result = {
            "caster": caster.uid,
            "target": target.uid,
            "hit": hit,
            "dmg": dmg,
            "cast": cast,
        }

        if cast and hit:
            Action._perform_action(result, target)

        return result

    @staticmethod
    def _perform_action(action: ActionDict, target: Entity) -> None:
        target.health -= action["dmg"]


all_actions = {
    "bite": Action(
        _name="bite",
        _cost=0,
        _min_damage=5,
        _max_damage=5,
        _hit_percentage=100,
        _area_of_effect=False,
        _requires_target=True,
        _causes_combat=True,
    ),
    "stomp": Action("stomp", 15, 5, 15, 70, False, True, True),
    "spit": Action("spit", 25, 15, 50, 30, True, False, True),
    "eat_berry": Action("eat", 5, -5, -10, 100, False, False, False),
}


class BaseRoom(ABC):
    events: list[object]
    __title: str
    __description: str
    __linked_rooms: dict[str, None | BaseRoom]
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
        _linked_rooms: dict[str, None | BaseRoom],
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
            f"{_display_x}{_title}{_description}{_linked_rooms['north']}{_linked_rooms['east']}"
            f"{_display_y}{_linked_rooms['south']}{_linked_rooms['west']}"
        )
        m = hashlib.sha256()
        m.update(data.encode())
        self.uid = int(m.hexdigest(), 16)
        self.__title = _title
        self.__color = _color
        self.events = []
        self.__linked_rooms = _linked_rooms
        self.__display_char = _display_char
        self.__mobs = []
        self.__players = []
        self.display_x = _display_x
        self.display_y = _display_y

        BaseRoom.number += 1

    def get_display(self) -> DisplayDict:
        """:return: dictionary of `color` and `display_char` for building map"""
        return {"color": self.__color, "display_char": self.__display_char}

    def export(self) -> ExportedData:
        _mobs: list[MobData] = []
        for mob in self.__mobs:
            _mobs.append(
                {
                    "uid": mob.uid,
                    "name": mob.name,
                    "health": mob.health,
                    "max_health": mob.max_health,
                }
            )
        _players: list[PlayerData] = []
        for player in self.__players:
            _players.append(
                {
                    "uid": player.uid,
                    "name": player.name,
                    "health": player.health,
                    "max_health": player.max_health,
                }
            )
        _exits: list[ExitData] = []
        for _dir, room in self.__linked_rooms.items():
            if room is not None:
                _exits.append(
                    {
                        "direction": _dir,
                        "title": room.__title,
                        "uid": room.uid,
                        "can_entity_step": room.can_entity_step,
                    }
                )
        return {
            "uid": self.uid,
            "color": self.__color,
            "display_char": self.__display_char,
            "x": self.display_x,
            "y": self.display_y,
            "title": self.__title,
            "description": self.__description,
            "mobs": _mobs,
            "players": _players,
            "exits": _exits,
        }

    def set_links(self, links: dict[str, None | BaseRoom]):
        self.__linked_rooms = links

    def get_links(self) -> dict[str, None | BaseRoom]:
        return self.__linked_rooms

    def show_mobs(self) -> str:
        """:return: get string of mobs in room"""
        ret = ""
        for mob in self.__mobs:
            ret += f"{str(mob)}\n"
        return ret

    def set_room(self, direction: str, room_to_add: BaseRoom):
        self.__linked_rooms[direction] = room_to_add

    def show_players(self) -> str:
        """:return: get string of players in room"""
        ret = ""
        for player in self.__players:
            ret += f"{str(player)}\n"
        return ret

    def get_players(self) -> list[Player]:
        return self.__players

    def get_mobs(self) -> list[Mob]:
        return self.__mobs

    def add_player(self, _player: Player):
        """
        Add player to room

        :param _player: player object to add
        :return:
        """
        _player.in_room = self
        self.__players.append(_player)

    def remove_player(self, _player: Player):
        _player.in_room = None
        self.__players.remove(_player)

    def add_mob(self, _mob: Mob):
        """
        Add mob to room

        :param _mob: mob object to add
        :return:
        """
        _mob.in_room = self
        self.__mobs.append(_mob)

    def remove_mob(self, _mob: Mob):
        _mob.in_room = None
        self.__mobs.remove(_mob)

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
        _color: tuple[int, int, int] = (0, 102, 0),
        _description: str = "How are you reading this",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class TopOfLeaf(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "Top of the leaf",
        _display_char: str = ".",
        _color: tuple[int, int, int] = (0, 204, 0),
        _description: str = "A nice bit of leaf.",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class LeftLower(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "A Shaded Leaf",
        _display_char: str = "\\",
        _color: tuple[int, int, int] = (0, 102, 51),
        _description: str = "A nice bit of leaf.",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class RoughSide(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "The Rough Side",
        _display_char: str = "*",
        _color: tuple[int, int, int] = (76, 153, 0),
        _description: str = "A nice bit of leaf.",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class LeftTop(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "Sunny Left",
        _display_char: str = "/",
        _color: tuple[int, int, int] = (51, 255, 51),
        _description: str = "The vista of the sun in the distance is beautiful from this view.",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class SpidersDen(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "The Den of a Spider",
        _display_char: str = "X",
        _color: tuple[int, int, int] = (153, 0, 0),
        _description: str = "Carcasses of past catapillers crunch under your feet.",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class RightTop(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "Shaded Right Side",
        _display_char: str = "|",
        _color: tuple[int, int, int] = (0, 102, 51),
        _description: str = "Shadows from the left side fall at your feet. It's tough to see in front of you.",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class RightLower(BaseRoom):
    def __init__(
        self,
        _display_x: int,
        _display_y: int,
        _title: str = "Deeply Shaded Right Side",
        _display_char: str = "-",
        _color: tuple[int, int, int] = (0, 51, 25),
        _description: str = """This part of the leaf is all in shadow.
        It's nearly impossible to see in front of you.""",
        _linked_rooms: dict[str, None | BaseRoom] | None = None,
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


class Combat:
    participants: list[Entity]
    participants_uids: set[int]
    acted_this_round: list[Entity]
    players: list[Player]
    mobs: list[Mob]
    done: bool
    room: BaseRoom
    uid: int

    def __init__(self, _participants: list[Entity], _room: BaseRoom):
        self.participants = _participants
        self.participants_uids = set()
        self.players = []
        self.mobs = []
        self.room = _room
        self.done = False

        for entity in self.participants:
            self.participants_uids.add(entity.uid)
            if isinstance(entity, Player):
                self.players.append(entity)
            if isinstance(entity, Mob):
                self.mobs.append(entity)

        combat_hash = hashlib.sha256()
        data = f"{self.participants_uids}"
        combat_hash.update(str(time.time_ns()).encode())
        combat_hash.update(data.encode())
        self.uid = int(combat_hash.hexdigest(), 16)

    def remove_from_combat(self, entity: Entity):
        self.participants_uids.remove(entity.uid)
        self.participants.remove(entity)
        if isinstance(entity, Player):
            self.players.remove(entity)
        if isinstance(entity, Mob):
            self.mobs.remove(entity)

    def __add_mob_to_combat(self, _mob: Mob):
        if _mob.uid not in self.participants_uids:
            self.participants_uids.add(_mob.uid)
            self.participants.append(_mob)
            self.mobs.append(_mob)

    def __add_player_to_combat(self, _player: Player):
        if _player.uid not in self.participants_uids:
            self.participants_uids.add(_player.uid)
            self.participants.append(_player)
            self.players.append(_player)

    def add_to_combat(self, _participants: list[Entity] | Entity):
        if isinstance(_participants, Entity):
            if isinstance(_participants, Player):
                self.__add_player_to_combat(_participants)
            if isinstance(_participants, Mob):
                self.__add_mob_to_combat(_participants)

        if isinstance(_participants, list):
            for entity in _participants:
                if isinstance(entity, Player):
                    self.__add_player_to_combat(entity)
                if isinstance(entity, Mob):
                    self.__add_mob_to_combat(entity)

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = ""
        for player in self.players:
            ret += f"P{str(player.uid)[:4]} "
        for mob in self.mobs:
            ret += f"M{str(mob.uid)[:4]} "
        return ret

    def combine(self, other: Combat) -> Combat | None:
        combat_to_delete = None
        if self.room.uid == other.room.uid:
            if len(self.participants_uids.intersection(other.participants_uids)) != 0:
                destroy = None
                keep = None
                if self.uid > other.uid:
                    combat_to_delete = other
                    keep = self
                    destroy = other
                if self.uid < other.uid:
                    combat_to_delete = self
                    keep = other
                    destroy = self

                assert keep, "combining with same entity?"
                assert destroy, "combining with same entity?"
                keep.add_to_combat(destroy.participants)

        return combat_to_delete


class Tile(typing.TypedDict):
    x: int
    y: int
    type: str


class ActionDict(typing.TypedDict):
    caster: int
    target: int
    hit: bool
    dmg: int
    cast: bool


class MovementDict(typing.TypedDict):
    player: int
    direction: str
    success: bool


class CommandDict(typing.TypedDict):
    command: str
    target: Entity


class DisplayDict(typing.TypedDict):
    color: tuple[int, int, int]
    display_char: str


class ExportedData(typing.TypedDict):
    uid: int
    color: tuple[int, int, int]
    display_char: str
    x: int
    y: int
    title: str
    description: str
    mobs: list[MobData]
    players: list[PlayerData]
    exits: list[ExitData]


class MobData(typing.TypedDict):
    uid: int
    name: str
    health: int
    max_health: int


class PlayerData(typing.TypedDict):
    uid: int
    name: str
    health: int
    max_health: int


class ExitData(typing.TypedDict):
    direction: str
    title: str
    uid: int
    can_entity_step: bool
