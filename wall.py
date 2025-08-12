import random
from enums import Winds, Dragons
from utils import format_tile_name

# Constants
COPIES = 4

DEAD_WALL_SIZE = 14
KAN_DRAW_WALL_SIZE = 4


class Wall():
    def __init__(self):
        self.wall: list[str] = []
        self.dead_wall: list[str] = []
        self.kan_draw_stack: list[str] = []
        self.dora_indicators: list[dict] = [] # {'tile': isRevealed:bool}, i.e. {'5M': True}
        self.ura_dora_indicators: list[str] = [] # This one is only a list since it only matters if they are in riichi.

    def setup_walls(self, game_state) -> None:
        self.setup_main_wall(game_state)
        self.setup_dead_wall()

    def draw_tile(self, wall: list[str] | None = None) -> str:
        """Draw one tile from a given wall.
        \n If no wall is given it will default to the main wall."""
        return self.draw_tiles(1, wall)[0]

    def append_tile_to_wall(self, value: int, suit: int | str, wall: list[str] | None = None) -> None:
        if wall == None:
            wall = self.wall

        wall.append(format_tile_name(value, suit))

    def draw_tiles(self, amount, wall: list[str] | None = None) -> list[str]:
        """Draw tiles from a given wall.
        \n If no wall is given it will default to the main wall."""
        if wall == None:
            wall = self.wall

        if amount >= 1:
            tiles = wall[:amount]
            del wall[:amount]
        else:
            tiles = wall[amount:]
            del wall[amount:]

        return tiles

    def setup_dead_wall(self) -> None:
        # Dead wall setup.
        self.dead_wall = self.draw_tiles(-DEAD_WALL_SIZE)
        self.kan_draw_stack = self.dead_wall[:KAN_DRAW_WALL_SIZE]

        self.dora_indicators.append({self.dead_wall[KAN_DRAW_WALL_SIZE]: True})

        for i in range(KAN_DRAW_WALL_SIZE + 1, DEAD_WALL_SIZE):
            offset = i - (KAN_DRAW_WALL_SIZE + 1)
            if offset % 2 == 0:
                self.ura_dora_indicators.append(self.dead_wall[i])
            else:
                self.dora_indicators.append({self.dead_wall[i]: False})

    def setup_main_wall(self, game_state) -> None:
        wall  = self.wall

        # Main wall setup.
        for copy in range(COPIES):
            for suit in range(1, 4):
                for value in range(1, 10):
                    # Only keep 1's and 9's from characters if it's 3 player.
                    if game_state.is_three_player:
                        if suit == 1 and value not in (1, 9):
                            continue
                    
                    # Remove one copy of five to make it a red five later.
                    if copy == 0 and value == 5:
                        continue
                    
                    self.append_tile_to_wall(value, suit)

            for wind in Winds:
                self.append_tile_to_wall(wind.value, "Z")

            for dragon in Dragons:
                self.append_tile_to_wall(dragon.value, "Z")

        # Add red fives.
        for suit in range(1, 4):
            if game_state.is_three_player and suit == 1:
                continue
            
            self.append_tile_to_wall(0, suit)

        random.shuffle(wall)