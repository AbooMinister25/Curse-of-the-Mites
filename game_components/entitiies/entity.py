from abc import ABC, abstractmethod  # abstract classes
import hashlib


class Entity(ABC):
    health = None
    mana = None

    def __init__(self, _health=100, _mana=100):
        self.health = _health
        self.mana = _mana
