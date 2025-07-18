import random
from typing import List, Tuple, Optional
from enums import Suits, Winds, Dragons, Melds
from models import GameState

# Constants
COPIES = 4
TILE_NUMBER_MIN = 1
TILE_NUMBER_MAX = 9

def format_tile(suit: int, value: int) -> str:
    if suit == 1:
        return f"{value}M"
    elif suit == 2:
        return f"{value}P"
    else:
        return f"{value}S"

def parse_tile(tile: str) -> Tuple[str, int]:
    value = int(tile[0])
    suit = tile[1]
    return suit, value

def sort_tiles(tiles: List[str]) -> List[str]:
    def tile_sort_key(tile: str) -> tuple:
        suit, raw_value = parse_tile(tile)
        value = 5 if raw_value == 0 else raw_value  # Treat '0' as '5' for sorting

        if suit == 'M':  # Man
            return Suits.MAN.value, value
        elif suit == 'P':  # Pin
            return Suits.PIN.value, value
        elif suit == 'S':  # Sou
            return Suits.SOU.value, value
        elif suit == 'Z':  # Honor tiles
            if 1 <= value <= 4:  # Winds
                return 4, Winds(value).value
            else:  # Dragons
                return 5, Dragons(value).value
        else:
            raise ValueError(f"Unknown tile suit: {tile}")

    return sorted(tiles, key=tile_sort_key)

def get_dora(game_state: GameState) -> List[str]:
    dora_values = []
    dora_indicators = game_state.dora_indicators

    def loop_back(max_val: int, val: int, min_val: int = 1) -> int:
        if val + 1 < max_val:
            return val + 1
        else:
            return min_val

    for tile in dora_indicators:
        suit, value = parse_tile(tile)
        if suit in ("M", "P", "S"):
            dora_value = loop_back(10, value)
            dora_values.append(f"{dora_value}{suit}")
        elif value <= 4:
            dora_value = loop_back(5, value)
            dora_values.append(f"{dora_value}Z")
        else:
            dora_value = loop_back(8, value, 5)
            dora_values.append(f"{dora_value}Z")

    return dora_values

def find_melds(tiles) -> Optional[Melds]:
    if len(tiles) < 3:
        return Melds.NONE
        
    values = []
    suits = []

    for tile in tiles:
        suit, value = parse_tile(tile)
        values.append(value)
        suits.append(suit)

    # If they suits aren't the same then we can't have a meld (except for sequences which need same suit)
    if len(set(suits)) != 1:
        return Melds.NONE
    
    # Check for quads (4 identical tiles)
    if len(tiles) == 4 and len(set(values)) == 1:
        return Melds.CLOSED_QUAD  # TODO: We need to check for the discard type to determine open vs closed
    
    # Check for triplets (3 identical tiles)
    elif len(tiles) == 3 and len(set(values)) == 1:
        return Melds.CLOSED_TRIPLET  # TODO: We need to check for the discard type to determine open vs closed
    
    # Check for sequences (3 consecutive tiles in same suit)
    elif len(tiles) == 3 and suits[0] in ('M', 'P', 'S'):
        sorted_values = sorted(values)
        if sorted_values[1] == sorted_values[0] + 1 and sorted_values[2] == sorted_values[1] + 1:
            return Melds.CLOSED_SEQUENCE  # TODO: We need to check for the discard type to determine open vs closed
    
    return Melds.NONE

def generate_tiles(game_state: GameState) -> List[str]:
    tiles = []

    for copy in range(COPIES):
        # While I would like to use the enum, this system works better for skipping the red 5 and the man tiles if in 3P.
        for suit in range(1, 4):
            for tile_number in range(TILE_NUMBER_MIN, TILE_NUMBER_MAX + 1):

                # Suit 1 is man tiles, and we only keep the terminals, skipping the rest.
                if game_state.player_count == 3 and suit == 1 and tile_number not in (1, 9):
                    continue

                # We skip one copy of a five to make it a red five later.
                if tile_number == 5 and copy == 0:
                    continue

                tiles.append(format_tile(suit, tile_number))

        for wind in Winds:
            tiles.append(f"{wind.value}Z")

        for dragon in Dragons:
            tiles.append(f"{dragon.value}Z")

    # Red fives are re-added as value 0
    for suit in range(1, 4):
        # Skip red 5 man in 3 player game
        if game_state.player_count == 3 and suit == 1:
            continue
        tiles.append(format_tile(suit, 0))

    random.shuffle(tiles)
    return tiles