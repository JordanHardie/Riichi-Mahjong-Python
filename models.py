from typing import Dict, List
from enums import Winds, Furiten, DiscardType, CallTypes

class GameState:
    def __init__(self):
        self.wall: List[str] = []
        self.dead_wall: List[str] = []
        self.dora: List[str] = []
        self.dora_indicators: List[str] = []

        self.players: List['Player'] = []
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
        self.calls: List[dict] = [] # Structure: {"tiles": [tile_list], "call_type": CallTypes, "called_from": Winds, "called_tile": str}
        self.called_tiles: List[str] = []  # All tiles that have been called (for quick lookup)
        self.discards: List[Dict[str, DiscardType]] = []
        self.drawn_tile: str = ""  # Changed from List[str] to str since there's only one drawn tile

        self.yaku: List[str] = []
        self.tenpai: bool = False
        self.menzenchin: bool = True
        """If menzenchin is true, then the hand is closed."""
        self.furiten: Furiten = Furiten.NONE