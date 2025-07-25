import random
from enums import Winds, Dragons
from utils import format_tile_name
from typing import List, Dict, Optional

# Constants
COPIES = 4

DEAD_WALL_SIZE = 14
KAN_DRAW_WALL_SIZE = 4

class Wall():
    def __init__(self):
        self.wall: List[str] = []
        self.dead_wall: List[str] = []
        self.kan_draw_stack: List[str] = []
        self.dora_indicators: List[Dict] = [] # {'tile': isRevealed:bool}, i.e. {'5M': True}
        self.ura_dora_indicators: List[str] = [] # This one is only a list since it only matters if they are in riichi

    def draw_tiles(self, amount: int, wall: Optional[List[str]] = None) -> List[str]:
        if wall == None:
            wall = self.wall

        if amount >= 1:
            tiles = wall[:amount]
            del wall[:amount]

        else:
            tiles = wall[amount:]
            del wall[amount:]

        return tiles

    def setup_walls(self, game_state):
        wall  = self.wall

        def append_tile_to_wall(value: int, suit: int | str) -> None:
            wall.append(format_tile_name(value, suit))

        # Main wall setup
        for copy in range(COPIES):
            for suit in range(1, 4):
                for value in range(1, 10):

                    if game_state.is_three_player:
                        if suit == 1 and value not in (1, 9):
                            continue
                    
                    if copy == 0 and value == 5:
                        continue
                
                    append_tile_to_wall(value, suit)
            
            for wind in Winds:
                append_tile_to_wall(wind.value, "Z")

            for dragon in Dragons:
                append_tile_to_wall(dragon.value, "Z")

        for suit in range(1, 4):
            if game_state.is_three_player and suit == 1:
                continue
            
            append_tile_to_wall(0, suit)
        
        random.shuffle(wall)

        # Dead wall setup
        self.dead_wall = self.draw_tiles(-DEAD_WALL_SIZE)
        self.kan_draw_stack = self.dead_wall[:KAN_DRAW_WALL_SIZE]

        self.dora_indicators.append({self.dead_wall[4]: True})

        for i in range(KAN_DRAW_WALL_SIZE + 1, DEAD_WALL_SIZE):
            offset = i - (KAN_DRAW_WALL_SIZE + 1)
            if offset % 2 == 0:
                self.ura_dora_indicators.append(self.dead_wall[i])
            else:
                self.dora_indicators.append({self.dead_wall[i]: False})