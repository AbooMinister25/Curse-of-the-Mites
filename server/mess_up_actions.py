"""This is (one of) our bug(s)!"""
import copy
import random
import typing

from game_components.game_objects import Action, Player

K = typing.TypeVar("K")
V = typing.TypeVar("V")

NO_SHUFFLE = ["nvm", "clear", "flee"]  # It would be funny tho.


class MessedPlayer:
    """Class for storing the messed inputs of a player.

    How to use:
    When the client tries to do something like `move north` do:
    `self.directions["north"]` and that'll return a messed up direction that the server should execute instead.
    """

    def __init__(self, player: Player) -> None:
        self.player = player
        self.actions = _mess_up_actions(player)
        self.directions = _mess_up_directions()

    def mess_up_again(self):
        """In case we want to reshuffle the players actions."""
        self.actions = _mess_up_actions(self.player)
        self.directions = _mess_up_directions()


def _mess_up_directions() -> dict[str, str]:
    """Takes the direction strings and assigns them to a different direction."""
    directions = ["north", "east", "south", "west"]
    shuffled_directions = copy.copy(directions)
    random.shuffle(shuffled_directions)

    return dict(zip(directions, shuffled_directions))


def _mess_up_actions(player: Player) -> dict[str, Action]:
    """Takes the action strings a player can do and assigns them to a different action."""
    require_target: dict[str, Action] = {}
    no_target: dict[str, Action] = {}

    for name, action in player.allowed_actions.items():
        if action.requires_target:
            require_target[name] = action
        else:
            no_target[name] = action

    # We don't really care about sharing a dict. But we don't want a non-target action to be
    # called with a target or viceversa.
    return shuffled_dict(require_target) | shuffled_dict(no_target)


def shuffled_dict(dict_: dict[K, V]) -> dict[K, V]:
    """Return a dict with its keys and values shuffled around."""
    shuffled_keys = list(dict_)
    random.shuffle(shuffled_keys)
    shuffled_values = list(dict_.values())
    random.shuffle(shuffled_values)

    return dict(zip(shuffled_keys, shuffled_values))
