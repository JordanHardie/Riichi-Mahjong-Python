from enum import Enum
from typing import List, TypeVar

# Constants
En = TypeVar('En', bound=Enum)


def send_message(message:str) -> None:
    print(f"\n{message}")


def send_input(_input:str) -> str:
    return input(f"\n{_input}")


def sort_tiles(tiles: List[str]):
    return sorted(tiles, key=sort_key)


def extract_tile_values(tile: str) -> tuple:
    value: int = int(tile[0])
    suit: str = tile[1]
    return value, suit


def is_number_tile(tile: str) -> bool:
    _, suit = extract_tile_values(tile)
    if suit in ['M', 'P', 'S']:
        return True
    else:
        return False


def is_terminal_tile(tile: str) -> bool:
    value, _ = extract_tile_values(tile)
    if is_number_tile(tile):
        if value in (1, 9):
            return True
        else:
            return False
    else:
        return False


def get_next_enum(current: En) -> En:
    enum_class = current.__class__           # Get the enum class
    members = list(enum_class)               # Get all members
    index = members.index(current)           # Find current member
    next_index = (index + 1) % len(members)  # Wrap around
    return members[next_index]


def get_prev_enum(current: En) -> En:
    enum_class = current.__class__
    members = list(enum_class)
    index = members.index(current)
    prev_index = (index - 1) % len(members)
    return members[prev_index]


def format_tile_name(value: int, suit: int | str) -> str:
    if suit == 1:
        return f"{value}M"
    elif suit == 2:
        return f"{value}P"
    elif suit == 3:
        return f"{value}S"
    else:
        return f"{value}Z"


def sort_key(tile: str) -> tuple[int, int]:
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