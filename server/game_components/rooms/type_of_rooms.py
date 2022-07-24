from basic_room import BaseRoom


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
