from enum import Enum

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

class CallTypes(Enum):
    PON = 1
    CHII = 2
    OPEN_KAN = 3
    CLOSED_KAN = 4
    ADDED_KAN = 5
    KITA = 6

class Melds(Enum):
    NONE = 0
    OPEN_TRIPLET = 1
    """Minkou."""
    CLOSED_TRIPLET = 2
    """Ankou."""
    OPEN_SEQUENCE = 3
    """Minjun."""
    CLOSED_SEQUENCE = 4
    """Anjun."""
    OPEN_QUAD = 5
    """Daiminkan"""
    CLOSED_QUAD = 6
    """Ankan."""
    ADDED_QUAD = 7
    """Shouminkan"""