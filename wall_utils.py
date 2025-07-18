from typing import List, Tuple, Optional
from models import GameState, Player

def draw_tiles_from_wall(wall: List[str], amount: int) -> List[str]:
    if amount >= 0:
        tiles = wall[:amount]
        del wall[:amount]
    else:
        tiles = wall[amount:]
        del wall[amount:]
    return tiles

def get_last_discarded_tile(game_state: GameState) -> Tuple[Optional[str], Optional[Player]]:
    """Get the last discarded tile and the player who discarded it."""
    last_tile = None
    last_player = None
    
    for player in game_state.players:
        if player.discards:
            last_tile = list(player.discards[-1].keys())[0]
            last_player = player
    
    return last_tile, last_player