from enum import Enum

# region Tile enums
class Suits(Enum):
    MAN = 1
    '''Characters.'''
    CHARACTERS = 1 # alias

    PIN = 2
    '''Circles.'''
    CIRCLES = 2 # alias

    SOU = 3
    '''Bamboo.'''
    BAMBOO = 3 # alias

class Winds(Enum):
    TON = 1
    '''East wind.'''
    EAST = 1 # alias

    NAN = 2
    '''South wind.'''
    SOUTH = 2 # alias

    SHAA = 3
    '''West wind.'''
    WEST = 3 # alias

    PEI = 4
    '''North wind.'''
    NORTH = 4 # alias

class Dragons(Enum):
    HAKU = 5
    '''White dragon.'''
    WHITE = 5 # alias

    HATSU = 6
    '''Green dragon'''
    GREEN = 6 # alias

    CHUN = 7
    '''Red dragon.'''
    RED = 7 # alias
# endregion

class Calls(Enum):
    NONE = 0
    CHII = 1
    PON = 2
    OPEN_KAN = 3
    CLOSED_KAN = 4
    ADDED_KAN = 5
    KITA = 6

class Melds(Enum):
    NONE = 0

    MINJUN = 1
    '''Open sequence.'''
    OPEN_SEQUENCE = 1 # alias

    ANJUN = 2
    '''Closed sequence.'''
    CLOSED_SEQUENCE = 2 # alias

    MINKOU = 3
    '''Open triplet.'''
    OPEN_TRIPLET = 3 # alias

    ANKOU = 4
    '''Closed triplet.'''
    CLOSED_TRIPLET = 4 # alias

    DAIMINKAN = 5
    '''Open quad.'''
    OPEN_QUAD = 5 # alias

    ANKAN = 6
    '''Closed quad.'''
    CLOSED_QUAD = 6 # alias

    SHOUMINKAN = 7
    '''Added quad.'''
    ADDED_QUAD = 7 # alias

class Furiten(Enum):
    NONE = 0
    DISCARD = 1
    TEMPORARY = 2
    PERMANENT = 3