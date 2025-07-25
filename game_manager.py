import random
from wall import Wall
from utils import *
from typing import List, Dict
from enums import Winds, Furiten

class GameState():
    def __init__(self) -> None:
        self.wall = Wall()
        self.tiles_left: int = 69
        self.is_three_player: bool = False

        self.repeats: int = 0
        self.kan_count: int = 0
        self.riichi_bets: List[Winds] = [] # List of players who have riichi'd.

        self.turn_number: int = 0
        self.round_number: int = 0

        self.players: List[Player] = []
        self.current_player: Winds = Winds.EAST
        self.previous_player: Winds = Winds.EAST
        self.current_round_wind: Winds = Winds.EAST

class Player():
    def __init__(self) -> None:
        self.seat: Winds = Winds.EAST
        self.points: int = 25000

        self.drawn_tile: str = ""
        self.hand: List[str] = []
        self.calls: List[Dict] = []
        self.discard_pile: List[str] = []

        self.tenpai: bool = False
        self.furiten_status: Furiten = Furiten.NONE

def setup_game() -> None:
    player_count = int(send_input("How many players?: "))

    while player_count not in (3, 4):
        send_message("Please try again!")
        player_count = int(send_input("How many players?: "))

    game_state = GameState()

    winds = [Winds.EAST, Winds.SOUTH, Winds.WEST, Winds.NORTH]
    random.shuffle(winds)

    if player_count == 3:
        game_state.is_three_player = True
        winds.remove(Winds.NORTH)

    wall = game_state.wall
    wall.setup_walls(game_state)

    for _ in range(player_count):
        player = Player()
        player.seat = winds.pop(0)

        player.hand = wall.draw_tiles(13)

        if player.seat == Winds.EAST:
            player.drawn_tile = str(wall.draw_tiles(1))

        game_state.players.append(player)

    game_state.tiles_left = len(wall.wall)