from game_components.rooms.basic_room import BaseRoom


class Wall(BaseRoom):
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
        super().__init__(
            _title="Wall",
            _display_char="#",
            _color=(0, 0, 0),
            _description="How are you reading this",
            _linked_rooms={"north": None, "east": None, "south": None, "west": None},
            _display_x=_display_x,
            _display_y=_display_y,
        )
        self.can_entity_step = False


class Hall(BaseRoom):
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
        super().__init__(
            _title="The hallway",
            _display_char=" ",
            _color=(0, 0, 0),
            _description="It's a hallway",
            _linked_rooms={"north": None, "east": None, "south": None, "west": None},
            _display_x=_display_x,
            _display_y=_display_y,
        )
        self.can_entity_step = True
