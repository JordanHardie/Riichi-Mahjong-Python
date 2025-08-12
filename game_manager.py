import random
from utils import *
from wall import Wall
from enums import Calls, Winds, Furiten, DiscardType

HAND_SIZE = 13


class DiscardedTile():
    def __init__(self) -> None:
        self.tile: str = ''
        self.discarded_by: Winds = Winds.EAST
        self.discard_type: DiscardType = DiscardType.TSUMOGIRI


class CalledTile():
    def __init__(self) -> None:
        self.tiles: list[str] = []
        self.call_type: Calls = Calls.NONE
        self.called_from: Winds = Winds.EAST
        self.discard_type: DiscardType = DiscardType.TEDASHI


class Player():
    def __init__(self) -> None:
        self.seat: Winds = Winds.EAST
        self.points: int = 25000

        self.drawn_tile: str = ""
        self.hand: list[str] = []
        self.calls: list[CalledTile] = []
        self.discard_pile: list[DiscardedTile] = []

        self.tenpai: bool = False
        self.is_in_riichi: bool = False
        self.furiten_status: Furiten = Furiten.NONE


class GameState():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, 'initialized'):
            return
        self.initialized = True

        self.wall = Wall()
        self.tiles_left: int = 69
        self.is_three_player: bool = False

        self.repeats: int = 0
        self.kan_count: int = 0
        self.riichi_bets: int = 0

        self.turn_number: int = 0
        self.round_number: int = 0

        self.players: list[Player] = []
        self.current_player: Winds = Winds.EAST
        self.previous_player: Winds = Winds.EAST
        self.current_round_wind: Winds = Winds.EAST

    def get_current_player(self) -> Player:
        for player in self.players:
            if player.seat == self.current_player:
                return player
        raise ValueError(f"No player found with seat {self.current_player}")

game_state = GameState()


def setup_game() -> None:
    player_count = int(send_input("How many players?: "))

    while player_count not in (3, 4):
        send_message("Please try again!")
        player_count = int(send_input("How many players?: "))

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

        player.hand = wall.draw_tiles(HAND_SIZE)
        player.hand = sort_tiles(player.hand)

        game_state.players.append(player)

    game_state.tiles_left = len(wall.wall)