import random
from abc import ABC  # abstract classes

from server.game_components.entities.entity import Entity


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
        if _max_damage < _min_damage:
            raise ValueError("max dmg must be greater than min dmg")
        if _min_damage > _max_damage:
            raise ValueError("min dmg must be less than max dmg")
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
        FOR EXAMPLE:
            hit - false
            dmg - 1000
            cast - true
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

                return [{"hit": hit, "dmg": dmg, "cast": cast}]
            else:
                return [{"hit": hit, "dmg": dmg, "cast": cast}]
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
                    action_list.append({"hit": hit, "dmg": dmg, "cast": cast})
                else:
                    action_list.append({"hit": hit, "dmg": dmg, "cast": cast})


if __name__ == "__main__":
    pass
