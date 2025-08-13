from enum import Enum
from typing import TypeVar

# Constants
En = TypeVar('En', bound=Enum)


def send_message(message:str) -> None:
    """Send a message to the console."""
    print(f"\n{message}")


def send_input(_input:str) -> str:
    """Send an input prompt to the console and return the user's input."""
    return input(f"\n{_input}")


def sort_tiles(tiles: list[str]):
    """Sort tiles based on their value and suit.
    \n M (Manzu) < P (Pinzu) < S (Souzu) < Z (Honor tiles).
    \n 5 is treated as 0 for sorting purposes."""
    return sorted(tiles, key=sort_key)


def extract_tile_values(tile: str) -> tuple[int, str]:
    """Extract numeric value and suit from a tile string.
    \n Example: '5M' -> (5, 'M'), '1Z' -> (1, 'Z')."""
    value: int = int(tile[0])
    suit: str = tile[1]
    return value, suit


def extract_tile_list_values(tiles: list[str]) -> tuple[list[int], list[str]]:
    """Extract numeric values and suits from tile list."""
    tiles = sort_tiles(tiles)
    values: list[int] = []
    suits: list[str] = []

    for tile in tiles:
        value, suit = extract_tile_values(tile)
        suits.append(suit)
        values.append(value)

    return values, suits


def is_number_tile(tile: str) -> bool:
    """Check if a tile is a number tile (Manzu, Pinzu, Souzu).
    \n Returns True for tiles like '1M', '5P', '9S'."""
    _, suit = extract_tile_values(tile)
    if suit in ['M', 'P', 'S']:
        return True
    else:
        return False


def is_terminal_tile(tile: str) -> bool:
    """Check if a tile is a terminal tile (1 or 9 of any suit).
    \n Returns True for tiles like '1M', '9P', '9S'."""
    value, _ = extract_tile_values(tile)
    if is_number_tile(tile):
        if value in (1, 9):
            return True
        else:
            return False
    else:
        return False


def get_next_enum(current: En) -> En:
    """Get the next enum member in a circular manner.
    \n If the current enum is the last one, it wraps around to the first."""
    enum_class = current.__class__           # Get the enum class
    members = list(enum_class)               # Get all members
    index = members.index(current)           # Find current member
    next_index = (index + 1) % len(members)  # Wrap around
    return members[next_index]


def get_prev_enum(current: En) -> En:
    """Get the previous enum member in a circular manner.
    \n If the current enum is the first one, it wraps around to the last."""
    enum_class = current.__class__
    members = list(enum_class)
    index = members.index(current)
    prev_index = (index - 1) % len(members)
    return members[prev_index]


def format_tile_name(value: int, suit: int | str) -> str:
    """Format a tile name based on its value and suit.
    \n Example: 5, 1 -> '5M', 1, 'Z' -> '1Z'."""
    if suit == 1:
        return f"{value}M"
    elif suit == 2:
        return f"{value}P"
    elif suit == 3:
        return f"{value}S"
    else:
        return f"{value}Z"


def sort_key(tile: str) -> tuple[int, int]:
    """Key function for sorting tiles.
    \n Returns a tuple of (suit_index, value) for sorting purposes.
    \n M (Manzu) < P (Pinzu) < S (Souzu) < Z (Honor tiles)."""

    value, suit = extract_tile_values(tile)

    if value == 0: value = 5

    if suit == 'M':
        return (0, value)
    elif suit == 'P':
        return (1, value)
    elif suit == 'S':
        return (2, value)
    else:
        return (3, value)