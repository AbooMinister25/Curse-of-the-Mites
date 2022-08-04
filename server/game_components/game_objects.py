from __future__ import annotations

import hashlib
import random
import time
import typing
from abc import ABC, abstractmethod  # abstract classes

from common.schemas import MapUpdate, RoomChangeUpdate

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
    {"y": 7, "x": 14, "type": "wall"},
    {"y": 7, "x": 15, "type": "tol"},
    {"y": 7, "x": 16, "type": "rs"},
    {"y": 7, "x": 17, "type": "wall"},
    {"y": 7, "x": 19, "type": "wall"},
    {"y": 7, "x": 20, "type": "wall"},
    {"y": 7, "x": 21, "type": "wall"},
    {"y": 7, "x": 22, "type": "wall"},
    {"y": 7, "x": 23, "type": "wall"},
    {"y": 7, "x": 24, "type": "wall"},
    {"y": 7, "x": 25, "type": "wall"},
    {"y": 8, "x": 14, "type": "wall"},
    {"y": 8, "x": 15, "type": "tol"},
    {"y": 8, "x": 16, "type": "rs"},
    {"y": 8, "x": 17, "type": "wall"},
    {"y": 8, "x": 19, "type": "wall"},
    {"y": 8, "x": 20, "type": "rt"},
    {"y": 8, "x": 21, "type": "rt"},
    {"y": 8, "x": 22, "type": "rt"},
    {"y": 8, "x": 23, "type": "rt"},
    {"y": 8, "x": 24, "type": "rt"},
    {"y": 8, "x": 25, "type": "rt"},
    {"y": 8, "x": 26, "type": "wall"},
    {"y": 8, "x": 27, "type": "wall"},
    {"y": 8, "x": 28, "type": "wall"},
    {"y": 9, "x": 2, "type": "wall"},
    {"y": 9, "x": 3, "type": "wall"},
    {"y": 9, "x": 4, "type": "wall"},
    {"y": 9, "x": 5, "type": "wall"},
    {"y": 9, "x": 6, "type": "wall"},
    {"y": 9, "x": 7, "type": "wall"},
    {"y": 9, "x": 8, "type": "wall"},
    {"y": 9, "x": 9, "type": "wall"},
    {"y": 9, "x": 10, "type": "wall"},
    {"y": 9, "x": 11, "type": "wall"},
    {"y": 9, "x": 12, "type": "wall"},
    {"y": 9, "x": 14, "type": "wall"},
    {"y": 9, "x": 15, "type": "tol"},
    {"y": 9, "x": 16, "type": "rs"},
    {"y": 9, "x": 17, "type": "wall"},
    {"y": 9, "x": 18, "type": "wall"},
    {"y": 9, "x": 19, "type": "wall"},
    {"y": 9, "x": 20, "type": "tol"},
    {"y": 9, "x": 21, "type": "tol"},
    {"y": 9, "x": 22, "type": "tol"},
    {"y": 9, "x": 23, "type": "tol"},
    {"y": 9, "x": 24, "type": "tol"},
    {"y": 9, "x": 25, "type": "tol"},
    {"y": 9, "x": 26, "type": "tol"},
    {"y": 9, "x": 27, "type": "tol"},
    {"y": 9, "x": 28, "type": "wall"},
    {"y": 10, "x": 2, "type": "wall"},
    {"y": 10, "x": 3, "type": "sd"},
    {"y": 10, "x": 4, "type": "tol"},
    {"y": 10, "x": 5, "type": "tol"},
    {"y": 10, "x": 6, "type": "tol"},
    {"y": 10, "x": 7, "type": "tol"},
    {"y": 10, "x": 8, "type": "tol"},
    {"y": 10, "x": 9, "type": "tol"},
    {"y": 10, "x": 10, "type": "tol"},
    {"y": 10, "x": 11, "type": "tol"},
    {"y": 10, "x": 12, "type": "wall"},
    {"y": 10, "x": 13, "type": "wall"},
    {"y": 10, "x": 14, "type": "wall"},
    {"y": 10, "x": 15, "type": "tol"},
    {"y": 10, "x": 16, "type": "rs"},
    {"y": 10, "x": 17, "type": "wall"},
    {"y": 10, "x": 18, "type": "rt"},
    {"y": 10, "x": 19, "type": "tol"},
    {"y": 10, "x": 20, "type": "tol"},
    {"y": 10, "x": 21, "type": "wall"},
    {"y": 10, "x": 22, "type": "wall"},
    {"y": 10, "x": 23, "type": "wall"},
    {"y": 10, "x": 24, "type": "wall"},
    {"y": 10, "x": 25, "type": "wall"},
    {"y": 10, "x": 26, "type": "wall"},
    {"y": 10, "x": 27, "type": "sd"},
    {"y": 10, "x": 28, "type": "wall"},
    {"y": 11, "x": 2, "type": "wall"},
    {"y": 11, "x": 3, "type": "wall"},
    {"y": 11, "x": 4, "type": "wall"},
    {"y": 11, "x": 5, "type": "wall"},
    {"y": 11, "x": 6, "type": "wall"},
    {"y": 11, "x": 7, "type": "wall"},
    {"y": 11, "x": 8, "type": "wall"},
    {"y": 11, "x": 9, "type": "lt"},
    {"y": 11, "x": 10, "type": "lt"},
    {"y": 11, "x": 11, "type": "tol"},
    {"y": 11, "x": 12, "type": "tol"},
    {"y": 11, "x": 13, "type": "tol"},
    {"y": 11, "x": 14, "type": "wall"},
    {"y": 11, "x": 15, "type": "tol"},
    {"y": 11, "x": 16, "type": "rs"},
    {"y": 11, "x": 17, "type": "wall"},
    {"y": 11, "x": 18, "type": "tol"},
    {"y": 11, "x": 19, "type": "tol"},
    {"y": 11, "x": 20, "type": "wall"},
    {"y": 11, "x": 21, "type": "wall"},
    {"y": 11, "x": 26, "type": "wall"},
    {"y": 11, "x": 27, "type": "wall"},
    {"y": 11, "x": 28, "type": "wall"},
    {"y": 12, "x": 8, "type": "wall"},
    {"y": 12, "x": 9, "type": "wall"},
    {"y": 12, "x": 10, "type": "wall"},
    {"y": 12, "x": 11, "type": "wall"},
    {"y": 12, "x": 12, "type": "wall"},
    {"y": 12, "x": 13, "type": "tol"},
    {"y": 12, "x": 14, "type": "tol"},
    {"y": 12, "x": 15, "type": "tol"},
    {"y": 12, "x": 16, "type": "rs"},
    {"y": 12, "x": 17, "type": "tol"},
    {"y": 12, "x": 18, "type": "tol"},
    {"y": 12, "x": 19, "type": "wall"},
    {"y": 12, "x": 20, "type": "wall"},
    {"y": 13, "x": 12, "type": "wall"},
    {"y": 13, "x": 13, "type": "wall"},
    {"y": 13, "x": 14, "type": "lt"},
    {"y": 13, "x": 15, "type": "tol"},
    {"y": 13, "x": 16, "type": "rs"},
    {"y": 13, "x": 17, "type": "tol"},
    {"y": 13, "x": 18, "type": "wall"},
    {"y": 13, "x": 19, "type": "wall"},
    {"y": 14, "x": 13, "type": "wall"},
    {"y": 14, "x": 14, "type": "wall"},
    {"y": 14, "x": 15, "type": "tol"},
    {"y": 14, "x": 16, "type": "tol"},
    {"y": 14, "x": 17, "type": "tol"},
    {"y": 14, "x": 18, "type": "wall"},
    {"y": 15, "x": 6, "type": "wall"},
    {"y": 15, "x": 7, "type": "wall"},
    {"y": 15, "x": 8, "type": "wall"},
    {"y": 15, "x": 9, "type": "wall"},
    {"y": 15, "x": 10, "type": "wall"},
    {"y": 15, "x": 11, "type": "wall"},
    {"y": 15, "x": 12, "type": "wall"},
    {"y": 15, "x": 14, "type": "wall"},
    {"y": 15, "x": 15, "type": "tol"},
    {"y": 15, "x": 16, "type": "tol"},
    {"y": 15, "x": 17, "type": "wall"},
    {"y": 15, "x": 20, "type": "wall"},
    {"y": 15, "x": 21, "type": "wall"},
    {"y": 15, "x": 22, "type": "wall"},
    {"y": 15, "x": 23, "type": "wall"},
    {"y": 15, "x": 24, "type": "wall"},
    {"y": 15, "x": 25, "type": "wall"},
    {"y": 15, "x": 26, "type": "wall"},
    {"y": 15, "x": 27, "type": "wall"},
    {"y": 16, "x": 2, "type": "wall"},
    {"y": 16, "x": 3, "type": "wall"},
    {"y": 16, "x": 4, "type": "wall"},
    {"y": 16, "x": 5, "type": "wall"},
    {"y": 16, "x": 6, "type": "wall"},
    {"y": 16, "x": 7, "type": "ll"},
    {"y": 16, "x": 8, "type": "ll"},
    {"y": 16, "x": 9, "type": "ll"},
    {"y": 16, "x": 10, "type": "ll"},
    {"y": 16, "x": 11, "type": "ll"},
    {"y": 16, "x": 12, "type": "wall"},
    {"y": 16, "x": 13, "type": "wall"},
    {"y": 16, "x": 14, "type": "wall"},
    {"y": 16, "x": 15, "type": "tol"},
    {"y": 16, "x": 16, "type": "tol"},
    {"y": 16, "x": 17, "type": "wall"},
    {"y": 16, "x": 18, "type": "wall"},
    {"y": 16, "x": 19, "type": "wall"},
    {"y": 16, "x": 20, "type": "wall"},
    {"y": 16, "x": 21, "type": "rl"},
    {"y": 16, "x": 22, "type": "rl"},
    {"y": 16, "x": 23, "type": "rl"},
    {"y": 16, "x": 24, "type": "rl"},
    {"y": 16, "x": 25, "type": "rl"},
    {"y": 16, "x": 26, "type": "rl"},
    {"y": 16, "x": 27, "type": "wall"},
    {"y": 16, "x": 28, "type": "wall"},
    {"y": 16, "x": 29, "type": "wall"},
    {"y": 16, "x": 30, "type": "wall"},
    {"y": 17, "x": 2, "type": "wall"},
    {"y": 17, "x": 3, "type": "sd"},
    {"y": 17, "x": 4, "type": "tol"},
    {"y": 17, "x": 5, "type": "tol"},
    {"y": 17, "x": 6, "type": "tol"},
    {"y": 17, "x": 7, "type": "tol"},
    {"y": 17, "x": 8, "type": "tol"},
    {"y": 17, "x": 9, "type": "tol"},
    {"y": 17, "x": 9, "type": "tol"},
    {"y": 17, "x": 10, "type": "tol"},
    {"y": 17, "x": 11, "type": "tol"},
    {"y": 17, "x": 12, "type": "tol"},
    {"y": 17, "x": 13, "type": "tol"},
    {"y": 17, "x": 14, "type": "ll"},
    {"y": 17, "x": 15, "type": "tol"},
    {"y": 17, "x": 16, "type": "tol"},
    {"y": 17, "x": 17, "type": "wall"},
    {"y": 17, "x": 18, "type": "wall"},
    {"y": 17, "x": 19, "type": "rl"},
    {"y": 17, "x": 20, "type": "rl"},
    {"y": 17, "x": 21, "type": "rl"},
    {"y": 17, "x": 22, "type": "rl"},
    {"y": 17, "x": 23, "type": "tol"},
    {"y": 17, "x": 24, "type": "tol"},
    {"y": 17, "x": 25, "type": "tol"},
    {"y": 17, "x": 26, "type": "tol"},
    {"y": 17, "x": 27, "type": "rl"},
    {"y": 17, "x": 28, "type": "rl"},
    {"y": 17, "x": 29, "type": "rl"},
    {"y": 17, "x": 30, "type": "wall"},
    {"y": 17, "x": 31, "type": "wall"},
    {"y": 18, "x": 2, "type": "wall"},
    {"y": 18, "x": 3, "type": "wall"},
    {"y": 18, "x": 4, "type": "wall"},
    {"y": 18, "x": 5, "type": "wall"},
    {"y": 18, "x": 6, "type": "wall"},
    {"y": 18, "x": 7, "type": "wall"},
    {"y": 18, "x": 8, "type": "wall"},
    {"y": 18, "x": 9, "type": "wall"},
    {"y": 18, "x": 10, "type": "wall"},
    {"y": 18, "x": 11, "type": "wall"},
    {"y": 18, "x": 12, "type": "wall"},
    {"y": 18, "x": 13, "type": "tol"},
    {"y": 18, "x": 14, "type": "tol"},
    {"y": 18, "x": 15, "type": "tol"},
    {"y": 18, "x": 16, "type": "tol"},
    {"y": 18, "x": 17, "type": "tol"},
    {"y": 18, "x": 18, "type": "tol"},
    {"y": 18, "x": 19, "type": "tol"},
    {"y": 18, "x": 20, "type": "tol"},
    {"y": 18, "x": 21, "type": "tol"},
    {"y": 18, "x": 22, "type": "tol"},
    {"y": 18, "x": 23, "type": "tol"},
    {"y": 18, "x": 24, "type": "rl"},
    {"y": 18, "x": 25, "type": "rl"},
    {"y": 18, "x": 26, "type": "tol"},
    {"y": 18, "x": 27, "type": "tol"},
    {"y": 18, "x": 28, "type": "tol"},
    {"y": 18, "x": 29, "type": "tol"},
    {"y": 18, "x": 30, "type": "tol"},
    {"y": 18, "x": 31, "type": "wall"},
    {"y": 19, "x": 13, "type": "wall"},
    {"y": 19, "x": 14, "type": "tol"},
    {"y": 19, "x": 15, "type": "tol"},
    {"y": 19, "x": 16, "type": "tol"},
    {"y": 19, "x": 17, "type": "wall"},
    {"y": 19, "x": 18, "type": "wall"},
    {"y": 19, "x": 19, "type": "wall"},
    {"y": 19, "x": 20, "type": "wall"},
    {"y": 19, "x": 21, "type": "wall"},
    {"y": 19, "x": 22, "type": "wall"},
    {"y": 19, "x": 23, "type": "wall"},
    {"y": 19, "x": 24, "type": "wall"},
    {"y": 19, "x": 25, "type": "wall"},
    {"y": 19, "x": 26, "type": "wall"},
    {"y": 19, "x": 27, "type": "wall"},
    {"y": 19, "x": 28, "type": "wall"},
    {"y": 19, "x": 29, "type": "wall"},
    {"y": 19, "x": 30, "type": "tol"},
    {"y": 19, "x": 31, "type": "wall"},
    {"y": 20, "x": 13, "type": "wall"},
    {"y": 20, "x": 14, "type": "tol"},
    {"y": 20, "x": 15, "type": "tol"},
    {"y": 20, "x": 16, "type": "wall"},
    {"y": 20, "x": 29, "type": "wall"},
    {"y": 20, "x": 30, "type": "sd"},
    {"y": 20, "x": 31, "type": "wall"},
    {"y": 21, "x": 13, "type": "wall"},
    {"y": 21, "x": 14, "type": "wall"},
    {"y": 21, "x": 15, "type": "tol"},
    {"y": 21, "x": 16, "type": "wall"},
    {"y": 21, "x": 29, "type": "wall"},
    {"y": 21, "x": 30, "type": "wall"},
    {"y": 21, "x": 31, "type": "wall"},
    {"y": 22, "x": 14, "type": "wall"},
    {"y": 22, "x": 15, "type": "tol"},
    {"y": 22, "x": 16, "type": "wall"},
    {"y": 23, "x": 14, "type": "wall"},
    {"y": 23, "x": 15, "type": "tol"},
    {"y": 23, "x": 16, "type": "wall"},
    {"y": 24, "x": 14, "type": "wall"},
    {"y": 24, "x": 15, "type": "tol"},
    {"y": 24, "x": 16, "type": "wall"},
    {"y": 25, "x": 14, "type": "wall"},
    {"y": 25, "x": 15, "type": "wall"},
    {"y": 25, "x": 16, "type": "wall"},
]

mobs = []


class Entity(ABC):
    __number_of_entities: int = 0
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
        Entity.__number_of_entities += 1
        now = time.time_ns()
        m = hashlib.sha256()
        data = (
            f"{self.name},{str(now)},{str(_allowed_actions)}{self.__number_of_entities}"
        )
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
    def update(self, actions: list[ActionDict] | None = None):
        if self.mana > self.max_mana:
            self.mana = self.max_mana
        if self.health > self.max_health:
            self.health = self.max_health

        self.enforce_aliveness()

        self._send_updates_to_the_room(actions)
        pass

    def _send_updates_to_the_room(self, actions: list[ActionDict]) -> None:
        """Adds to the list of updates that must be sent to players in the room."""
        assert self.in_room

        if actions is not None:
            for action in actions:
                # Only send successful actions to avoid spamming.
                if action["cast"] and action["hit"]:
                    full_update: RoomActionDict = {
                        "type": "room_action",
                        "room": self.in_room,
                        "action": action,
                    }
                    self.in_room.events.append(full_update)

        if not self.alive:
            # Avoids sending a "player died" message right after a "player won" message.
            # ... even tho it's quite funny.
            if not (isinstance(self, Player) and self.won):
                self.in_room.events.append(
                    {"room_of_death": self.in_room, "deceased": self}
                )

    def enforce_aliveness(self) -> None:
        # Makes sure a winning player doesn't "revive" when we are trying to clean it.
        self.alive = self.health > 0 and self.alive


class Mob(Entity):
    def update(self):
        self.mana += 4
        self.health += random.randint(1, 2)

        self.enforce_aliveness()

        if not self.alive:
            # Level up every player that was part of the combat (even if maybe they didn't do much).
            for player_uid in self.in_room.player_combatants:
                player = self.game.get_player(player_uid)
                if player is not None:
                    player.level_up()

        actions = self._handle_combat()
        super().update(actions=actions)
        pass

    def __init__(self, _name: str, _allowed_actions: list[str], game: Game):
        self.game = game
        super().__init__(_name, _allowed_actions)

    def _handle_combat(self) -> list[ActionDict] | None:
        """Allows the mob to act if it is in combat."""
        res = None

        if (self.alive) and (self.uid in self.in_room.mob_combatants):
            if len(self.in_room.player_combatants) == 0:
                # There are no players left to fight, so stop fighting.
                self.in_room.mob_combatants.remove(self.uid)
                self.in_combat = False
            else:
                res = self._act_in_combat()

        return res

    def _act_in_combat(self) -> list[ActionDict]:
        # TODO MOBS CHOSE ACTIONS BASED ON AVAILABLE MANA
        action_choice = random.choice(list(self.allowed_actions.values()))
        if action_choice.requires_target:
            target_choice = random.choice(list(self.in_room.player_combatants))
            res = self.commit_action(
                action_choice.name, self.game.get_player(target_choice)
            )
        else:
            res = self.commit_action(action_choice.name)

        return res


class Player(Entity):
    level: int
    level_past_tick: int
    command_queue: list[dict[str, Entity | None]]

    def __init__(self, _name: str, _allowed_actions: list[str], game: Game):
        super().__init__(_name, _allowed_actions)
        self.level_past_tick = 0
        self.level = 0
        self.won = False
        self.command_queue = []
        self.game = game

    def update(self) -> list[ActionDict] | FleeDict | MovementDict | int:
        """Updates the player for one tick.

        Executes the next action in the players queue.
        Returns a list of ActionDicts if the player did something and None if they didn't
        """
        self.mana += 7
        self.health += random.randint(1, 3)

        result = self.uid  # If we didn't do anything, return our UID anyways.

        if len(self.command_queue) > 0:
            next_command = self.command_queue.pop()
            result = self._do(next_command)

        if isinstance(result, list):
            self._start_combats_in_room(result)
            super().update(actions=result)
        else:
            super().update()

        self._check_combat_end()
        return result

    def _do(
        self, command: CommandDict
    ) -> list[ActionDict] | MovementDict | FleeDict | None:
        movement_commands = ["north", "east", "south", "west"]

        result = None
        if command["command"] in movement_commands:
            result = self._handle_movement(command)
        elif command["command"] == "flee":
            result = self._try_fleeing()
        else:
            result = self.commit_action(command["command"], command["target"])

        return result

    def _handle_movement(self, command) -> MovementDict:
        reason = None
        valid_move = False
        map_rs = None
        if self.in_combat:
            reason = "combat"
        else:
            valid_move = self.game.move_player(self, command["command"])
            if valid_move:
                map_rooms = [room.export() for room in self.game.rooms.values()]
                rc_update = self._create_room_change_update_list()
                map_rs = MapUpdate(
                    type="map_update",
                    map=map_rooms,
                    entities=rc_update,
                )
        result = {
            "player": self.uid,
            "direction": command["command"],
            "success": valid_move,
            "reason": reason,
            "map_update": map_rs,
        }

        return result

    def _create_room_change_update_list(self) -> list[RoomChangeUpdate]:
        room = self.in_room

        mobs = {mob for mob in room.get_mobs()}
        players = {player for player in room.get_players()}
        all_entities: set[Entity] = mobs | players

        room_change = [
            RoomChangeUpdate(
                type="room_change",
                room_uid=self.in_room.uid,
                entity_uid=entity.uid,
                entity_name=entity.name,
                enters=True,
            )
            for entity in all_entities
        ]

        return room_change

    def _start_combats_in_room(self, actions: list[ActionDict]) -> None:
        """Makes sure combats start in the current room if needed."""
        for action in actions:
            # Only start combat with mobs.
            target = self.game.get_mob(action["target"])
            if (
                (target is not None)
                and (action["cast"])
                and (all_actions[action["name"]])
            ):
                self.in_room.player_combatants.add(self.uid)
                self.in_room.mob_combatants.add(target.uid)
                self.in_combat = True

    def _check_combat_end(self) -> None:
        """Ends combat automatically if there's no mobs left that want to fight."""
        if self.in_combat:
            # If you're engaged in combat and there's still mob combatants in the room,
            # then you don't exit combat automatically.
            self.in_combat = len(self.in_room.mob_combatants) > 0

    def _try_fleeing(self) -> FleeDict:
        FLEEING_CHANCE = 35  # Percent
        success = False
        was_in_combat = self.in_combat
        if was_in_combat:
            success = random.randint(1, 100) <= FLEEING_CHANCE
            self.in_combat = not success

        if success:
            self.in_room.player_combatants.remove(self.uid)

        return {"player": self.uid, "fled": success, "combat": was_in_combat}

    def level_up(self):
        self.level += 1

        if self.level >= 5:
            self.won = True
            self.alive = False  # This make sure we get cleaned from the game :)

    def add_command_to_queue(
        self, _command: str, _target: Entity | None = None
    ) -> bool:
        """
        Adds a command to the player queue if it's valid.

        :param _command: flee, north, east, south, west, one of the skills, clear, nvm
        :param _target: Entity to be targeted or None.
        :return:
        """
        validity = self._check_command_validity(_command, _target)

        if validity:
            event = {"command": _command, "target": _target}
            self.command_queue.insert(0, event)

        return validity

    def _check_command_validity(
        self, _command: str, _target: Entity | None = None
    ) -> bool:
        """
        Checks that a command is valid.

        :param _command: flee, north, east, south, west, one of the skills, clear, nvm
        :param _target: Entity to be targeted or None.
        :return:
        """
        directions = ["north", "east", "south", "west", "flee"]

        if _command in self.allowed_actions:
            # make sure actions that need a target get a target
            if self.allowed_actions[_command].requires_target and _target is None:
                return False
            elif (
                not self.allowed_actions[_command].requires_target
            ) and _target is not None:
                return False

        match _command:
            case "clear":
                self.command_queue = []
                # We did something but there's nothing to queue, so we return false.
                return False
            case "nvm":
                self.command_queue = self.command_queue[:-1]
                # We did something but there's nothing to queue, so we return false.
                return False
            case _:
                return _command in directions or _command in self.allowed_actions


class TargetsError(Exception):
    """Exception raised when you try to perform an action with an incorrect number of targets."""

    def __init__(self, action_name: str, needs_target: bool) -> None:
        s = "requires" if needs_target else "doesn't require"
        self.message = f"{action_name} {s} a target"

    def __str__(self) -> str:
        return self.message


class Action:
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
        self.causes_combat = _causes_combat

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
            "name": self.name,
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
    "nibble": Action(
        _name="nibble",
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
    "eat_berry": Action("eat_berry", 5, -5, -10, 100, False, False, False),
    "annoy": Action("annoy", 0, 1, 1, 100, True, False, True),
    "sing": Action(
        _name="sing",
        _cost=10,
        _min_damage=-2,
        _max_damage=-15,
        _hit_percentage=100,
        _area_of_effect=False,
        _requires_target=True,
        _causes_combat=False,
    ),
    "sting": Action(
        _name="sting",
        _cost=25,
        _min_damage=20,
        _max_damage=70,
        _hit_percentage=35,
        _area_of_effect=False,
        _requires_target=True,
        _causes_combat=True,
    ),
    "offer_berry": Action(
        _name="offer_berry",
        _cost=10,
        _min_damage=-10,
        _max_damage=-20,
        _hit_percentage=60,
        _area_of_effect=False,
        _requires_target=True,
        _causes_combat=False,
    ),
}


class BaseRoom(ABC):
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

    mob_combatants: set[int]
    player_combatants: set[int]

    events: list[RoomActionDict | RoomChangeUpdate | DeathDict]

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
        self.__description = _description
        self.__color = _color
        self.events = []
        self.__linked_rooms = _linked_rooms
        self.__display_char = _display_char
        self.__mobs = []
        self.__players = []
        self.display_x = _display_x
        self.display_y = _display_y

        self.events = []
        self.mob_combatants = set()
        self.player_combatants = set()

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

    def add_player(self, player: Player):
        """
        Add player to room

        :param _player: player object to add
        :return:
        """
        player.in_room = self
        self.__players.append(player)

        self.events.append(
            RoomChangeUpdate(
                type="room_change",
                room_uid=self.uid,
                entity_uid=player.uid,
                entity_name=player.name,
                enters=True,
            )
        )

    def remove_player(self, player: Player):
        player.in_room = None
        self.__players.remove(player)

        self.events.append(
            RoomChangeUpdate(
                type="room_change",
                room_uid=self.uid,
                entity_uid=player.uid,
                entity_name=player.name,
                enters=False,
            )
        )

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


class Tile(typing.TypedDict):
    x: int
    y: int
    type: str


class ActionDict(typing.TypedDict):
    name: str
    caster: int
    target: int
    hit: bool
    dmg: int
    cast: bool


class MovementDict(typing.TypedDict):
    player: int
    direction: str
    success: bool
    reason: str | None
    map_update: MapUpdate | None


class CommandDict(typing.TypedDict):
    command: str
    target: Entity


class DisplayDict(typing.TypedDict):
    color: tuple[int, int, int]
    display_char: str


class DisplayExport(typing.TypedDict):
    color: tuple[int, int, int]
    display_x: int
    display_y: int
    title: str
    description: str
    north: BaseRoom | None
    east: BaseRoom | None
    south: BaseRoom | None
    west: BaseRoom | None


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


class RoomActionDict(typing.TypedDict):
    type: str
    room: BaseRoom
    action: ActionDict


class FleeDict(typing.TypedDict):
    player: int
    fled: bool
    combat: bool


class DeathDict(typing.TypedDict):
    room_of_death: BaseRoom
    deceased: Entity
