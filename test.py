import random
from typing import Dict, List, Tuple, Any
from flask import Flask, request, jsonify

MAP_SIZE = random.randint(20, 25)
TERRAINS = ["plains", "ocean", "desert", "river", "mountains"]
POWER_TYPES = ["WINDMILL", "SOLAR_PANELS", "GEOTHERMAL", "DAM"]

app = Flask(__name__)

# Game State
game_map: List[List[str]] = []
factories: Dict[int, Dict[str, Any]] = {}
bots: Dict[int, Dict[str, Any]] = {}
power_plants: List[Dict[str, Any]] = {}


def generate_map():
    """Generate a random game map with different terrain types."""
    global game_map
    game_map = [[random.choice(TERRAINS) for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]


def find_valid_factory_locations():
    """Find valid locations to place factories on the map."""
    center = MAP_SIZE // 2
    half_size = MAP_SIZE // 2
    valid_locations = [
        (x, y) for x in range(center - half_size, center + half_size)
        for y in range(center - half_size, center + half_size)
        if game_map[x][y] == "plains"
    ]
    return valid_locations


def place_factories():
    """Place factories at valid locations."""
    valid_locations = find_valid_factory_locations()
    for i in range(min(3, len(valid_locations))):  # Limit factories
        x, y = valid_locations.pop(random.randint(0, len(valid_locations) - 1))
        factories[i] = {"id": i, "location": (x, y), "warehouse": {}}


def get_adjacent_cells(x: int, y: int) -> List[Tuple[int, int]]:
    """Get adjacent cells in 4 directions."""
    return [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]


@app.route('/init', methods=['POST'])
def init_game():
    """Initialize the game world."""
    generate_map()
    place_factories()
    return jsonify({"message": "Game initialized", "map_size": MAP_SIZE}), 200


@app.route('/agent/<int:factory_id>/build', methods=['POST'])
def build_bot(factory_id: int):
    """Allow a factory to build an engineer bot."""
    if factory_id not in factories:
        return jsonify({"error": "Factory not found"}), 404

    factory = factories[factory_id]
    x, y = factory["location"]
    build_spot = random.choice(get_adjacent_cells(x, y))

    bot_id = len(bots)
    bots[bot_id] = {"id": bot_id, "location": build_spot, "energy": 100}

    return jsonify({"message": "Engineer bot built", "bot_id": bot_id}), 200


@app.route('/agent/<int:bot_id>/action', methods=['GET'])
def bot_action(bot_id: int):
    """Decide and return action for the engineer bot."""
    if bot_id not in bots:
        return jsonify({"error": "Bot not found"}), 404

    bot = bots[bot_id]
    action = random.choice([
        {"type": "MOVE", "params": {"d_loc": [random.randint(-1, 1), random.randint(-1, 1)]}},
        {"type": "EXPLORE", "params": {}},
        {"type": "DEPLOY",
         "params": {"power_type": "SOLAR_PANELS", "d_loc": [random.randint(-1, 1), random.randint(-1, 1)]}}
    ])

    return jsonify(action), 200


@app.route('/map', methods=['GET'])
def get_map():
    """Return the game map."""
    return jsonify({"map": game_map}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
