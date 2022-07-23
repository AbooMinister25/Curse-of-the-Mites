import hashlib
import time
from abc import ABC  # abstract classes


class Entity(ABC):
    health = None
    mana = None
    alive = None
    uid = None

    def __init__(self, _health=100, _mana=100):
        self.health = _health
        self.mana = _mana
        self.alive = True
        now = time.time_ns()
        m = hashlib.sha256()
        m.update(now)
        self.uid = int(m.hexdigest(), 16)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.uid[0:4]} ({self.health},{self.mana}) {self.__class__.__name__}"
