from __future__ import annotations

import hashlib
import time
from abc import ABC  # abstract classes

from server.game_components.actions.action import Action
from server.game_components.data.data import all_actions
from server.game_components.rooms.basic_room import BaseRoom


class Entity(ABC):
    health: int
    mana: int
    alive: bool
    uid: int
    in_combat: bool
    name: str
    allowed_actions: dict[str, Action]

    def __init__(self, _name, _allowed_actions: list[str], _health=100, _mana=100):
        self.health = _health
        self.mana = _mana
        self.alive = True
        now = time.time_ns()
        m = hashlib.sha256()
        m.update(now)
        self.uid = int(m.hexdigest(), 16)
        self.in_combat = False
        self.name = _name
        temp = {}
        for _action in _allowed_actions:
            temp[_action] = all_actions[_action]

        self.allowed_actions = temp

    def commit_action(self, _action: str, target: Entity | list[Entity]):
        return self.allowed_actions[_action].action(self, target)

    def move(self, _direction: str, _map: list[BaseRoom]):
        pass

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.uid[0:4]} ({self.health},{self.mana}) {self.__class__.__name__}"
