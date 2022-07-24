from server.game_components.actions.action import Action

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

all_actions = {
    "bite": Action("bite", 0, 5, 5, 100),
    "stomp": Action("stomp", 10, 5, 15, 70),
    "spit": Action("spit", 25, 15, 50, 30),
    "eat_berry": Action("eat", 5, -5, -10, 100),
}
