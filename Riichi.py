import random
from enum import Enum
from typing import List, Optional, Dict, TypeVar

# Generic type for enums
T = TypeVar('T', bound=Enum)

# Constants
COPIES = 4
HAND_SIZE = 13
TILE_NUMBER_MIN = 1
TILE_NUMBER_MAX = 9

DEAD_WALL_SIZE = 14
DORA_INDICATOR_INDEX = 5

class DiscardType(Enum):
    TEDASHI = 1
    """Tedashi refers to discarding a tile already in the hand."""

    TSUMOGIRI = 2
    """Tsumogiri refers to discarding the tile just drawn."""

class Suits(Enum):
    MAN = 1
    """Characters / numbers / manzu"""
    PIN = 2
    """Circles / wheels / pinzu"""
    SOU = 3
    """Bamboo / sticks / souzu"""

class Winds(Enum):
    EAST = 1
    SOUTH = 2
    WEST = 3
    NORTH = 4

class Dragons(Enum):
    WHITE = 5
    GREEN = 6
    RED = 7

class Furiten(Enum):
    NONE = 0
    DISCARD = 1
    TEMPORARY = 2
    PERMANENT = 3

class GameState:
    def __init__(self):
        self.wall: List[str] = []
        self.dead_wall: List[str] = []
        self.dora: List[str] = []
        self.dora_indicators: List[str] = []

        self.players: List[Player] = []
        self.player_count: int = 4

        self.turn: int = 0
        self.round: int = 0
        self.wind: Winds = Winds.EAST
        self.current_player: Winds = Winds.EAST

class Player:
    def __init__(self):
        self.points: int = 25000
        self.seat: Winds = Winds.EAST

        self.hand: List[str] = []
        self.calls: List[str] = []
        self.discards: List[Dict[str, DiscardType]] = []
        self.drawn_tile: List[str] = []

        self.yaku: List[str] = []
        self.tenpai: bool = False
        self.menzenchin: bool = True
        """If menzenchin is true, then the hand is closed."""
        self.furiten: Furiten = Furiten.NONE

def increment_turn(game_state: GameState) -> None:
    game_state.turn += 1

def increment_round(game_state: GameState) -> None:
    game_state.round += 1

def discard_tile(player: Player, tile: str, discard_type: DiscardType) -> None:
    player.discards.append({tile: discard_type})

    # If the player discards a tile in their hand its replaced with the drawn tile.
    if discard_type == DiscardType.TEDASHI:
        if tile in player.hand:
            player.hand.remove(tile)
            if player.drawn_tile:
                player.hand.append(player.drawn_tile[0])
                player.hand = sort_tiles(player.hand)

    # If the player discard the tile they just drew then we just remove the drawn tile.
    # However in the case of tedashi, we still need to remove the drawn tile to make room for the next one.
    # Hence, we always remove the drawn tile.
    # We access it as a list because the tedashi tile to discard might not match the drawn tile.
    # There's only ever one drawn tile (Or should be).
    if player.drawn_tile:
        player.drawn_tile.remove(player.drawn_tile[0])

def send_message(message: str) -> None:
    print("")
    print(message)

def input_message(message: str) -> str:
    print("")
    result = input(message)
    return result

def next_enum(_enum: T) -> T:
    members = list(type(_enum))
    index = members.index(_enum)
    return members[(index + 1) % len(members)]

def format_tile(suit: int, value: int) -> str:
    if suit == 1:
        return f"{value}M"
    elif suit == 2:
        return f"{value}P"
    else:
        return f"{value}S"

def draw_tiles_from_wall(wall: List[str], amount: int) -> List[str]:
    if amount >= 0:
        tiles = wall[:amount]
        del wall[:amount]
    else:
        tiles = wall[amount:]
        del wall[amount:]
    return tiles

def get_current_player(game_state: GameState) -> Optional[Player]:
    players = game_state.players
    current_player = None

    for player in players:
        if player.seat == game_state.current_player:
            current_player = player
            break

    return current_player

def sort_tiles(tiles: List[str]) -> List[str]:
    def tile_sort_key(tile: str) -> tuple:
        try:
            raw_value = int(tile[0])
            value = 5 if raw_value == 0 else raw_value  # Treat '0' as '5' for sorting
            suit = tile[1]

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
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid tile format: {tile}") from e

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
        try:
            value = int(tile[0])
            suit = tile[1]
            if suit in ("M", "P", "S"):
                dora_value = loop_back(10, value)
                dora_values.append(f"{dora_value}{suit}")
            elif value <= 4:
                dora_value = loop_back(5, value)
                dora_values.append(f"{dora_value}Z")
            else:
                dora_value = loop_back(8, value, 5)
                dora_values.append(f"{dora_value}Z")
        except (ValueError, IndexError):
            continue

    return dora_values

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

def initialize_game(game_state: GameState) -> None:
    while True:
        try:
            amount_of_players = int(input_message("How many players?: "))
            if amount_of_players in (3, 4):
                break
            else:
                send_message("Please enter 3 or 4 players.")
        except ValueError:
            send_message("Please enter a valid number.")

    game_state.player_count = amount_of_players

    game_state.wall = generate_tiles(game_state)
    game_state.dead_wall = draw_tiles_from_wall(game_state.wall, -DEAD_WALL_SIZE)

    # Fix: dora_indicators should be a list, not a single tile
    if len(game_state.dead_wall) > DORA_INDICATOR_INDEX:
        game_state.dora_indicators = [game_state.dead_wall[DORA_INDICATOR_INDEX]]
    else:
        game_state.dora_indicators = []

    winds = [Winds.EAST, Winds.SOUTH, Winds.WEST, Winds.NORTH]
    random.shuffle(winds)

    if amount_of_players == 3:
        winds.remove(Winds.NORTH)

    for _player in range(amount_of_players):
        player = Player()
        seat_wind = random.choice(winds)
        player.seat = seat_wind
        winds.remove(seat_wind)

        player.hand = draw_tiles_from_wall(game_state.wall, HAND_SIZE)
        player.hand = sort_tiles(player.hand)

        game_state.players.append(player)

def run_game() -> None:
    game_state = GameState()

    initialize_game(game_state)

    while game_state.round <= 8:
        display_hand = ""
        current_player = get_current_player(game_state)

        if current_player is None:
            send_message("Error: No current player found")
            break

        # Check if wall is empty
        if not game_state.wall:
            send_message("Wall is empty - game ends")
            break

        current_player.drawn_tile = draw_tiles_from_wall(game_state.wall, 1)
        increment_turn(game_state)

        if current_player.seat == Winds.EAST:
            for i, tile in enumerate(current_player.hand):
                if i != len(current_player.hand) - 1:
                    display_hand += f"{tile}, "
                else:
                    display_hand += f"{tile}"

            if current_player.drawn_tile:
                display_hand += f" | {current_player.drawn_tile[0]}"

            send_message(display_hand)
            while True:
                tile_to_discard = str(input_message("What will you discard?: "))
                tile_to_discard = tile_to_discard.upper()

                if current_player.drawn_tile and tile_to_discard == current_player.drawn_tile[0]:
                    discard_tile(current_player, tile_to_discard, DiscardType.TSUMOGIRI)
                    break
                elif tile_to_discard in current_player.hand:
                    discard_tile(current_player, tile_to_discard, DiscardType.TEDASHI)
                    break
                else:
                    send_message("Invalid tile. Please try again.")

        else:
            if current_player.drawn_tile:
                discard_tile(current_player, current_player.drawn_tile[0], DiscardType.TSUMOGIRI)

        game_state.current_player = next_enum(game_state.current_player)

if __name__ == "__main__":
    run_game()